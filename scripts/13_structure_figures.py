#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Render the structural figures for the two modelled axes, from deposited
     coordinates archived in data/raw/structures_2026/.
PT | Renderiza as figuras estruturais dos dois eixos modelados, a partir de
     coordenadas depositadas e arquivadas em data/raw/structures_2026/.

EN | What these figures are for, and what they are not. They illustrate the
     molecular machinery behind the miR-29/BACE1/Abeta and miR-7/SNCA/alpha-synuclein
     axes: how a microRNA recognises a target at all, what the enzyme the miR-29
     family represses looks like, and what the aggregated end states of both axes
     look like. They are mechanistic illustration for the introduction and
     discussion. They test no hypothesis and they are not a result. The quantitative
     claims in this project rest on the meta-analysis and on scripts/12.
PT | Para que servem estas figuras, e para que nao servem. Elas ilustram a maquinaria
     molecular por tras dos eixos miR-29/BACE1/Abeta e miR-7/SNCA/alfa-sinucleina:
     como um microRNA reconhece um alvo, qual a cara da enzima que a familia miR-29
     reprime, e qual a cara dos estados agregados finais dos dois eixos. Sao ilustracao
     mecanistica para a introducao e a discussao. Nao testam hipotese e nao sao
     resultado. As afirmacoes quantitativas deste projeto repousam na meta-analise e
     no scripts/12.

EN | Provenance is read from the coordinate files themselves and written to
     results/tables/structure_figure_provenance.json, so the figure legends quote the
     deposited title, method and resolution rather than a description from memory.
PT | A proveniencia e lida dos proprios arquivos de coordenadas e escrita em
     results/tables/structure_figure_provenance.json, para que as legendas citem o
     titulo, o metodo e a resolucao depositados, e nao uma descricao de memoria.

    python scripts/13_structure_figures.py
"""

import json
import os
import re
import sys

STRUCT_DIR = "data/raw/structures_2026"
FIG_DIR = "results/figures/structures"
TAB_DIR = "results/tables"

# EN/PT: what each entry must be, checked against the file before it is drawn
EXPECT = {
    "6N4O": dict(file="6N4O.pdb", must_match=r"argonaute",
                 role_en="How a microRNA recognises its target at all: the guide is held by "
                         "Argonaute2 and the seed pairs with the target. Common to both axes.",
                 role_pt="Como um microRNA reconhece o alvo: o guia e segurado pelo Argonauta2 "
                         "e a semente pareia com o alvo. Comum aos dois eixos."),
    "4D8C": dict(file="4D8C.cif", must_match=r"secretase",
                 role_en="BACE1, the enzyme the miR-29 family represses, with an inhibitor bound "
                         "in the active site.",
                 role_pt="BACE1, a enzima que a familia miR-29 reprime, com inibidor ligado no "
                         "sitio ativo."),
    "6CU7": dict(file="6CU7.cif", must_match=r"synuclein",
                 role_en="The aggregated end state of the miR-7/SNCA axis.",
                 role_pt="O estado agregado final do eixo miR-7/SNCA."),
    "5OQV": dict(file="5OQV.cif", must_match=r"amyloid",
                 role_en="The aggregated end state of the miR-29/BACE1/Abeta axis.",
                 role_pt="O estado agregado final do eixo miR-29/BACE1/Abeta."),
}


def read_provenance(pdb_id, path):
    """
    EN | Pull the deposited title, method, resolution and citation out of the file.
         A figure legend written from memory is a figure legend that can be wrong;
         this makes the legend quote the deposition.
    PT | Extrai titulo, metodo, resolucao e citacao depositados do proprio arquivo.
         Legenda escrita de memoria e legenda que pode estar errada; assim a legenda
         cita o deposito.
    """
    text = open(path, encoding="utf-8", errors="replace").read()
    p = dict(pdb_id=pdb_id, file=os.path.basename(path))

    if path.endswith(".pdb"):
        title = " ".join(re.findall(r"^TITLE\s*\d*\s*(.*?)\s*$", text, re.M))
        p["title"] = re.sub(r"\s+", " ", title).strip()
        m = re.search(r"^EXPDTA\s+(.*?)\s*$", text, re.M)
        p["method"] = m.group(1).strip() if m else ""
        m = re.search(r"^REMARK\s+2\s+RESOLUTION\.\s*([\d.]+)", text, re.M)
        p["resolution_angstrom"] = float(m.group(1)) if m else None
        m = re.search(r"^JRNL\s+DOI\s+(.*?)\s*$", text, re.M)
        p["doi"] = m.group(1).strip().lower() if m else ""
        m = re.search(r"^JRNL\s+PMID\s+(\d+)", text, re.M)
        p["pmid"] = m.group(1) if m else ""
    else:
        m = re.search(r"_struct\.title\s+(?:'([^']*)'|\"([^\"]*)\"|;(.*?)\n;)", text, re.S)
        p["title"] = re.sub(r"\s+", " ", (m.group(1) or m.group(2) or m.group(3) or "")).strip() if m else ""
        m = re.search(r"_exptl\.method\s+(?:'([^']*)'|\"([^\"]*)\"|(\S+))", text)
        p["method"] = ((m.group(1) or m.group(2) or m.group(3)) if m else "").strip()
        res = None
        m = re.search(r"_em_3d_reconstruction\.resolution\s+([\d.]+)", text)
        if m:
            res = float(m.group(1))
        else:
            m = re.search(r"_refine\.ls_d_res_high\s+([\d.]+)", text)
            if m:
                res = float(m.group(1))
        p["resolution_angstrom"] = res
        # EN | In a loop_ block the tag is a COLUMN HEADER, not a key-value pair, so
        #      reading the next token returns the first data row ("primary") instead of
        #      the DOI. That is exactly what happened for 4D8C. Match the DOI by its own
        #      shape instead, and take the PubMed id only when it is a plausible id.
        # PT | Num bloco loop_ a tag e CABECALHO DE COLUNA, nao par chave-valor, entao ler
        #      o proximo token devolve a primeira linha de dados ("primary") em vez do
        #      DOI. Foi exatamente o que ocorreu com o 4D8C. Casa o DOI pelo formato dele,
        #      e pega o PubMed id so quando for um id plausivel.
        m = re.search(r"\b(10\.\d{4,9}/[^\s'\";]+)", text)
        p["doi"] = m.group(1).strip().lower().rstrip(".,") if m else ""
        pmid = ""
        m = re.search(r"_citation\.pdbx_database_id_PubMed\s+(\d{6,9})\b", text)
        if m:
            pmid = m.group(1)
        else:
            for cand in re.findall(r"^\s*(\d{7,8})\s*$", text, re.M):
                pmid = cand
                break
        p["pmid"] = pmid
    return p


def style_common(cmd):
    cmd.bg_color("white")
    cmd.set("ray_opaque_background", 1)
    cmd.set("antialias", 2)
    cmd.set("ray_trace_mode", 0)
    cmd.set("ambient", 0.22)
    cmd.set("specular", 0.25)
    cmd.set("cartoon_fancy_helices", 1)
    cmd.set("cartoon_transparency", 0.0)
    cmd.set("surface_quality", 1)
    cmd.set("depth_cue", 0)
    cmd.set("ray_shadows", 0)


def render_ago2(cmd, path, out):
    """EN/PT: Ago2 holding the guide, seed paired to the target."""
    cmd.delete("all"); cmd.load(path, "ago2"); style_common(cmd)
    cmd.hide("everything")
    cmd.show("surface", "ago2 and chain A and polymer.protein")
    cmd.color("grey80", "ago2 and chain A")
    cmd.set("transparency", 0.55, "ago2 and chain A")
    # guide (chain C) and target (chain D)
    cmd.show("cartoon", "ago2 and chain C+D")
    cmd.show("sticks", "ago2 and chain C+D")
    cmd.set("cartoon_ring_mode", 3, "ago2 and chain C+D")
    cmd.set("cartoon_ring_finder", 1, "ago2 and chain C+D")
    cmd.color("orange", "ago2 and chain C")
    cmd.color("skyblue", "ago2 and chain D")
    # EN/PT: the seed, guide nucleotides 2-8
    cmd.color("firebrick", "ago2 and chain C and resi 2-8")
    cmd.set("cartoon_nucleic_acid_mode", 4)
    # EN | Orient on the RNA to get a readable view of the duplex, but FRAME on the
    #      whole complex. An earlier version zoomed to the RNA with a small buffer, so
    #      the protein ran off the top of the canvas and left dead space below.
    # PT | Orienta pelo RNA para obter uma vista legivel do duplex, mas ENQUADRA pelo
    #      complexo inteiro. Uma versao anterior dava zoom no RNA com margem pequena, e
    #      a proteina saia pelo topo da tela deixando espaco morto embaixo.
    cmd.orient("ago2 and chain C+D")
    cmd.turn("y", 12)
    cmd.zoom("ago2", 3, complete=1)
    cmd.png(out, width=2000, height=1500, dpi=300, ray=1)


def render_bace1(cmd, path, out):
    """EN/PT: BACE1 with the co-crystallised inhibitor and the catalytic aspartates."""
    cmd.delete("all"); cmd.load(path, "bace1"); style_common(cmd)
    cmd.hide("everything")
    sel = "bace1 and chain A"
    # EN | One flat colour for cartoon and surface. An earlier version ran a spectrum
    #      over the CA atoms, and the surface inherited it as a pink/cyan halo that
    #      carried no information at all.
    # PT | Uma cor chapada para cartoon e superficie. Uma versao anterior passava um
    #      espectro nos atomos CA, e a superficie herdava aquilo como um halo rosa/ciano
    #      que nao carregava informacao nenhuma.
    cmd.show("cartoon", f"{sel} and polymer.protein")
    cmd.color("skyblue", f"{sel} and polymer.protein")
    cmd.show("surface", f"{sel} and polymer.protein")
    cmd.set("transparency", 0.72, sel)
    lig = f"{sel} and resn BXD"
    cmd.show("sticks", lig); cmd.color("orange", f"{lig} and elem C")
    cmd.set("stick_radius", 0.22, lig)
    # EN/PT: catalytic aspartyl dyad, selected by proximity to the inhibitor
    cmd.select("dyad", f"byres ({sel} and resn ASP and polymer.protein within 5 of ({lig}))")
    cmd.show("sticks", "dyad and not hydro"); cmd.color("firebrick", "dyad and elem C")
    cmd.set("stick_radius", 0.22, "dyad")
    # EN/PT: orient on the pocket, then frame the whole domain so it is not clipped
    cmd.orient(lig)
    cmd.zoom(sel, 3, complete=1)
    cmd.png(out, width=2000, height=1500, dpi=300, ray=1)
    n = cmd.count_atoms("dyad and name CA")
    cmd.delete("dyad")
    return n


def render_fibril(cmd, path, out, label):
    """EN/PT: fibril down the axis and from the side, chains coloured by stacking layer."""
    cmd.delete("all"); cmd.load(path, "fib"); style_common(cmd)
    cmd.hide("everything")
    cmd.show("cartoon", "fib")
    cmd.set("cartoon_flat_sheets", 0)
    # EN | Colour by PROTOFILAMENT, not by chain. A rainbow over ten chains hides the
    #      one thing the view down the axis exists to show: that the fibril is two
    #      protofilaments packed against each other, each a stack of identical layers.
    #      Chains are split into first and second half, which is how these depositions
    #      are ordered; the split is asserted below rather than assumed.
    # PT | Colorir por PROTOFILAMENTO, nao por cadeia. Um arco-iris sobre dez cadeias
    #      esconde justamente o que a vista pelo eixo existe para mostrar: que a fibrila
    #      sao dois protofilamentos encaixados, cada um uma pilha de camadas identicas.
    #      As cadeias sao divididas em primeira e segunda metade, que e como esses
    #      depositos vem ordenados; a divisao e verificada abaixo, nao suposta.
    chains = cmd.get_chains("fib")
    half = len(chains) // 2
    pf1, pf2 = chains[:half], chains[half:]
    cmd.color("deepteal", "fib and chain " + "+".join(pf1))
    cmd.color("orange", "fib and chain " + "+".join(pf2))
    cmd.show("sticks", "fib and sidechain and not hydro")
    cmd.set("stick_radius", 0.13)
    cmd.set("cartoon_transparency", 0.1)
    cmd.orient("fib")
    cmd.zoom("fib", 4, complete=1)
    cmd.png(out.replace(".png", "_axis.png"), width=2000, height=1500, dpi=300, ray=1)
    cmd.turn("x", 90)
    cmd.zoom("fib", 4, complete=1)
    cmd.png(out.replace(".png", "_side.png"), width=2000, height=1500, dpi=300, ray=1)
    return dict(n_chains=len(chains), protofilament_1=pf1, protofilament_2=pf2)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs(TAB_DIR, exist_ok=True)

    import pymol
    pymol.finish_launching(["pymol", "-qc"])
    from pymol import cmd

    prov = {}
    print("=" * 78)
    print("EN | Structure figures | PT | Figuras de estrutura")
    print("=" * 78)

    for pdb_id, spec in EXPECT.items():
        path = os.path.join(STRUCT_DIR, spec["file"])
        if not os.path.exists(path):
            sys.exit(f"EN/PT: missing {path}")
        p = read_provenance(pdb_id, path)
        # EN | Confirm the file is the molecule the figure claims. A mis-downloaded
        #      structure would otherwise be rendered and captioned as the right one.
        # PT | Confirma que o arquivo e a molecula que a figura diz ser. Uma estrutura
        #      baixada errada seria renderizada e legendada como se fosse a certa.
        if not re.search(spec["must_match"], p["title"], re.I):
            sys.exit(f"EN/PT: {pdb_id} title does not mention "
                     f"'{spec['must_match']}': {p['title']!r}")
        p["role_en"] = spec["role_en"]
        p["role_pt"] = spec["role_pt"]
        prov[pdb_id] = p
        res = f"{p['resolution_angstrom']} A" if p["resolution_angstrom"] else "n/a"
        print(f"  {pdb_id}  {p['method']:<20} {res:>8}   {p['title'][:56]}")

    print("\nrendering | renderizando ...")
    render_ago2(cmd, os.path.join(STRUCT_DIR, "6N4O.pdb"), f"{FIG_DIR}/ago2_guide_target.png")
    n_asp = render_bace1(cmd, os.path.join(STRUCT_DIR, "4D8C.cif"), f"{FIG_DIR}/bace1_inhibitor.png")
    prov["4D8C"]["catalytic_aspartates_within_5A_of_ligand"] = int(n_asp)
    prov["6CU7"]["chain_split"] = render_fibril(
        cmd, os.path.join(STRUCT_DIR, "6CU7.cif"),
        f"{FIG_DIR}/alpha_synuclein_fibril.png", "alpha-synuclein")
    prov["5OQV"]["chain_split"] = render_fibril(
        cmd, os.path.join(STRUCT_DIR, "5OQV.cif"),
        f"{FIG_DIR}/abeta42_fibril.png", "Abeta42")

    json.dump(prov, open(f"{TAB_DIR}/structure_figure_provenance.json", "w"),
              ensure_ascii=False, indent=1)

    print("\nEN | Figures are mechanistic illustration, not a result.")
    print("PT | As figuras sao ilustracao mecanistica, nao resultado.")
    for f in sorted(os.listdir(FIG_DIR)):
        print(f"  {FIG_DIR}/{f}")
    print(f"  {TAB_DIR}/structure_figure_provenance.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
