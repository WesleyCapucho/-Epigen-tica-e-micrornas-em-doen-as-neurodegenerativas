#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | PyMOL renders of the four deposited structures that sit in the mechanism schematic of the
     meta-analysis manuscript (its Fig. 7: how a microRNA represses a target, how the AD and PD
     axes end in an aggregated protein, how the signal reaches a blood test). The coordinates
     are the ones archived in data/raw/structures_2026/:

         6N4O   human Argonaute2 holding miR-122, seed paired to a target        panel a
         4D8C   human BACE1 with an inhibitor in the active site                  panel b
         5OQV   amyloid-beta(1-42) fibril, cryo-EM, seen down its axis            panel b
         6CU7   alpha-synuclein fibril, cryo-EM (rod polymorph), down its axis    panel c

     What they are for, and what they are not. They illustrate the molecules at the steps of the
     two axes. They test no hypothesis and they are not a result. Each render is drawn on the tint
     of the panel it will sit in, so that no frame shows around it, with one flat colour per
     family of molecule: the blue of AD, the orange of PD, grey for the common machinery, purple
     for the microRNA (the palette of scripts/44; it is written out here because
     scripts/_viz_style.py imports matplotlib, which the PyMOL interpreter does not have).

     Provenance is read, not remembered. The title, method, resolution and primary citation of
     each structure are re-read from its coordinate file and compared with
     results/tables/structure_figure_provenance.json, which scripts/13 wrote; the catalytic dyad
     of BACE1 and the two protofilaments of each fibril are taken from that file too (scripts/13
     found them by sequence motif and by proximity, and by the distance between chain centroids)
     and the render stops if the structure in hand disagrees. Nothing is written to results/tables.

     The order of the renders matters. The views of AGO2 and BACE1 depend on the camera the
     previous render left behind (the same script run in another order gave other, equally
     valid views of the same two molecules), so the order below is part of the method: the two
     fibrils first, side views included, then AGO2, then BACE1. The side views are not used in
     the figure; they are drawn because they leave the camera where the AGO2 view starts from.
     Run in this order, in one session, the script gives the four images that went into Fig. 7,
     pixel for pixel.

     Needs PyMOL 3.1.0 and runs headless (no window). The figure was drawn with the conda-forge
     build in a Python 3.11 environment; on Windows the DLL folders of that environment are added
     below. Ray tracing at surface_quality 1 and antialias 1 takes about three minutes; higher
     settings take many times longer. The result is written to
     results/figures/structures/mirna_mechanism/renders/, with renders.json (versions, input and
     output hashes); scripts/43 crops them and scripts/44 draws the figure.

PT | Renders do PyMOL das quatro estruturas depositadas que entram no esquema de mecanismo do
     manuscrito da meta-analise (sua Fig. 7: como um microRNA reprime um alvo, como os eixos da
     DA e da DP terminam numa proteina agregada, como o sinal chega a um exame de sangue). As
     coordenadas sao as arquivadas em data/raw/structures_2026/ (lista acima).

     Para que servem e para que nao servem. Ilustram as moleculas nos passos dos dois eixos. Nao
     testam hipotese e nao sao resultado. Cada render e desenhado sobre o tom do painel onde vai
     ficar, para que nenhuma moldura apareca em volta, com uma cor chapada por familia de
     molecula: o azul da DA, o laranja da DP, cinza para a maquinaria comum, roxo para o microRNA
     (a paleta do scripts/44; esta escrita aqui porque scripts/_viz_style.py importa o
     matplotlib, que o interpretador do PyMOL nao tem).

     A proveniencia e lida, nao lembrada. Titulo, metodo, resolucao e citacao primaria de cada
     estrutura sao relidos do proprio arquivo de coordenadas e comparados com
     results/tables/structure_figure_provenance.json, que o scripts/13 escreveu; a diade
     catalitica da BACE1 e os dois protofilamentos de cada fibrila tambem vem desse arquivo
     (o scripts/13 os achou por motivo de sequencia e por proximidade, e pela distancia entre
     centroides de cadeia) e o render para se a estrutura em maos discorda. Nada e escrito em
     results/tables.

     A ordem dos renders importa. As vistas da AGO2 e da BACE1 dependem da camera que o render
     anterior deixou (o mesmo script rodado em outra ordem deu outras vistas, igualmente
     validas, das mesmas duas moleculas), entao a ordem abaixo faz parte do metodo: as duas
     fibrilas primeiro, vistas laterais incluidas, depois a AGO2, depois a BACE1. As vistas
     laterais nao entram na figura; sao desenhadas porque deixam a camera onde a vista da AGO2
     comeca. Rodado nessa ordem, numa sessao so, o script da as quatro imagens que entraram na
     Fig. 7, pixel a pixel.

     Precisa do PyMOL 3.1.0 e roda sem janela. A figura foi feita com a build do conda-forge num
     ambiente Python 3.11; no Windows as pastas de DLL desse ambiente sao adicionadas abaixo. O
     ray tracing com surface_quality 1 e antialias 1 leva uns tres minutos; ajustes mais altos
     levam muitas vezes mais. O resultado vai para results/figures/structures/mirna_mechanism/
     renders/, com renders.json (versoes, hashes de entrada e de saida); o scripts/43 recorta e
     o scripts/44 desenha a figura.

    python scripts/42_mirna_mechanism_renders.py        # with the interpreter that has PyMOL
"""

import hashlib
import importlib.util
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

# EN/PT: conda keeps PyMOL's DLLs (glew, freetype, libpng, libxml2, netcdf) in Library\bin | o conda guarda as DLLs do PyMOL em Library\bin
if sys.platform == "win32":
    _base = os.path.dirname(sys.executable)
    for _d in (os.path.join(_base, "Library", "bin"), os.path.join(_base, "Library", "mingw-w64", "bin"),
               os.path.join(_base, "Library", "usr", "bin")):
        if os.path.isdir(_d):
            os.add_dll_directory(_d)

STRUCT_DIR = "data/raw/structures_2026"
OUT_ROOT = "results/figures/structures/mirna_mechanism"
OUT_DIR = f"{OUT_ROOT}/renders"
LOG = f"{OUT_ROOT}/renders.json"
PROV13 = "results/tables/structure_figure_provenance.json"
W = 1800                      # EN/PT: canvas in px; the crops are placed at about 600 dpi or more | tela em px
H = int(W * 0.75)

# EN/PT: the order is part of the method (see the docstring) | a ordem faz parte do metodo (ver o docstring)
ORDER = ("abeta42", "asyn", "ago2", "bace1")

# EN/PT: the palette of scripts/44 (lettering and molecules share the hues); the three bg_* tints are those of the
#        panels the renders sit in | a paleta do scripts/44; os tres bg_* sao os tons dos paineis
PAL = {
    "ad_dark": "#1c5cab", "ad_mid": "#5b93d6", "ad_light": "#9fc0ea",
    "pd_dark": "#b8400f", "pd_mid": "#e07b4a", "pd_light": "#f0a983",
    "grey_surf": "#dcdbd7", "grey_cart": "#9d9c97", "grey_dark": "#4a4a48",
    "mirna": "#6a3d9a", "seed": "#c2185b", "dyad": "#a61c1c",
    "bg_grey": "#f4f3f0", "bg_ad": "#e8f0fa", "bg_pd": "#fbece4",
}


def rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]


def load_module(name, filename):
    """EN/PT: import a numbered script (scripts/13) by path, as scripts/39 does | importa um script numerado pelo caminho."""
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, filename))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def style_common(cmd, bg):
    cmd.bg_color(bg)
    cmd.set("ray_opaque_background", 1)
    cmd.set("antialias", 1)
    cmd.set("ray_trace_mode", 0)
    cmd.set("ambient", 0.30)
    cmd.set("specular", 0.15)
    cmd.set("cartoon_fancy_helices", 1)
    cmd.set("cartoon_transparency", 0.0)
    cmd.set("surface_quality", 1)
    cmd.set("hash_max", 220)
    cmd.set("depth_cue", 0)
    cmd.set("ray_shadows", 0)
    cmd.set("cartoon_oval_length", 1.1)
    cmd.set("cartoon_oval_width", 0.35)


def save(cmd, name):
    out = os.path.join(OUT_DIR, name)
    cmd.png(out, width=W, height=H, dpi=300, ray=1)
    print("  wrote", out.replace(os.sep, "/"))


def render_ago2(cmd):
    """EN/PT: Argonaute2 (surface) holding the guide (purple, seed in magenta) paired to the target (grey)."""
    cmd.delete("all")
    cmd.load(os.path.join(STRUCT_DIR, "6N4O.pdb"), "ago2")
    style_common(cmd, "bg_grey")
    cmd.hide("everything")
    cmd.show("surface", "ago2 and chain A and polymer.protein")
    cmd.color("grey_surf", "ago2 and chain A")
    cmd.set("transparency", 0.55, "ago2 and chain A")
    cmd.show("cartoon", "ago2 and chain C+D")
    cmd.show("sticks", "ago2 and chain C+D")
    cmd.set("stick_radius", 0.26, "ago2 and chain C+D")
    cmd.set("cartoon_tube_radius", 0.6, "ago2 and chain C+D")
    cmd.set("cartoon_ring_mode", 3, "ago2 and chain C+D")
    cmd.set("cartoon_ring_finder", 1)
    cmd.set("cartoon_nucleic_acid_mode", 4)
    # EN/PT: one flat colour per strand, all atoms: `util.cnc` would turn the phosphorus (and so the backbone) orange
    cmd.color("mirna", "ago2 and chain C")                   # guide
    cmd.color("grey_dark", "ago2 and chain D")               # target
    cmd.color("seed", "ago2 and chain C and resi 2-8")       # seed, nucleotides 2-8
    cmd.orient("ago2 and chain C+D")
    cmd.turn("y", 12)
    cmd.zoom("ago2", 3, complete=1)
    save(cmd, "ago2.png")


def render_bace1(cmd, s13, prov):
    """EN/PT: BACE1 chain A (cartoon in a translucent surface) with the inhibitor and the catalytic aspartates."""
    cmd.delete("all")
    cmd.load(os.path.join(STRUCT_DIR, "4D8C.cif"), "asu")
    style_common(cmd, "bg_ad")
    cmd.create("bace1", "asu and chain A and (polymer.protein or resn BXD)")
    cmd.delete("asu")
    cmd.hide("everything")
    sel = "bace1 and chain A"
    cmd.show("cartoon", f"{sel} and polymer.protein")
    cmd.color("ad_dark", f"{sel} and polymer.protein")
    cmd.show("surface", f"{sel} and polymer.protein")
    cmd.set("surface_color", "ad_light", f"{sel} and polymer.protein")
    cmd.set("transparency", 0.6, sel)
    lig = f"{sel} and resn BXD"
    cmd.show("sticks", lig)
    cmd.color("grey_dark", lig)
    cmd.set("stick_radius", 0.28, lig)
    # EN/PT: the catalytic aspartyl dyad, found by proximity to the inhibitor here and required to be the one
    #        scripts/13 found by the DTGS and DSGT motifs | a diade catalitica, achada aqui por proximidade
    #        com o inibidor e obrigada a ser a que o scripts/13 achou pelos motivos DTGS e DSGT
    cmd.select("dyad", f"byres ({sel} and resn ASP and polymer.protein within 5 of ({lig}))")
    near = {"l": []}
    cmd.iterate("dyad and name CA", "l.append(int(resi))", space=near)
    recorded = prov["4D8C"]["catalytic_dyad_resi_in_this_deposition"]
    if sorted(near["l"]) != sorted(recorded.values()):
        sys.exit(f"EN/PT: BACE1 dyad by proximity {sorted(near['l'])} differs from scripts/13: {recorded}")
    cmd.show("sticks", "dyad and not hydro")
    cmd.color("dyad", "dyad")
    cmd.set("stick_radius", 0.3, "dyad")
    cmd.orient(lig)
    cmd.zoom(sel, 3, complete=1)
    s13.open_clip(cmd)
    save(cmd, "bace1.png")
    return recorded


def render_fibril(cmd, prov, pdb_id, name, c1, c2, bg):
    """EN/PT: the fibril down its axis, one colour per protofilament, then from the side (the camera leaves from there)."""
    cmd.delete("all")
    cmd.load(os.path.join(STRUCT_DIR, f"{pdb_id}.cif"), "fib")
    style_common(cmd, bg)
    cmd.hide("everything")
    cmd.show("cartoon", "fib")
    cmd.set("cartoon_flat_sheets", 0)
    split = prov[pdb_id]["chain_split"]
    groups = [split["protofilament_1"], split["protofilament_2"]]
    if sorted(c for g in groups for c in g) != sorted(cmd.get_chains("fib")):
        sys.exit(f"EN/PT: {pdb_id} chains {sorted(cmd.get_chains('fib'))} are not the protofilaments of scripts/13: {groups}")
    cmd.color(c1, "fib and chain " + "+".join(groups[0]))
    cmd.color(c2, "fib and chain " + "+".join(groups[1]))
    cmd.orient("fib")
    cmd.zoom("fib", 4, complete=1)
    save(cmd, f"{name}_axis.png")
    cmd.turn("x", 90)
    cmd.zoom("fib", 4, complete=1)
    save(cmd, f"{name}_side.png")
    return groups


def main():
    if not os.path.exists(PROV13):
        sys.exit(f"EN/PT: missing {PROV13}; it is a committed table of the repository (scripts/13 writes it)")
    s13 = load_module("s13", "13_structure_figures.py")
    prov = json.load(open(PROV13, encoding="utf-8"))

    # EN/PT: re-read every coordinate file and compare it with the record of scripts/13 | rele cada arquivo e compara
    inputs = {}
    for pdb_id, spec in s13.EXPECT.items():
        path = os.path.join(STRUCT_DIR, spec["file"])
        if not os.path.exists(path):
            sys.exit(f"EN/PT: missing {path}")
        p = s13.read_provenance(pdb_id, path)
        if not re.search(spec["must_match"], p["title"], re.I):
            sys.exit(f"EN/PT: {pdb_id} title does not mention '{spec['must_match']}': {p['title']!r}")
        for k in ("title", "method", "resolution_angstrom", "doi", "pmid"):
            if p.get(k) != prov[pdb_id].get(k):
                sys.exit(f"EN/PT: {pdb_id} {k}: file {p.get(k)!r} vs scripts/13 {prov[pdb_id].get(k)!r}")
        inputs[pdb_id] = dict(file=spec["file"], sha256=sha256(path), title=p["title"], method=p["method"],
                              resolution_angstrom=p["resolution_angstrom"])

    os.makedirs(OUT_DIR, exist_ok=True)
    import pymol
    pymol.finish_launching(["pymol", "-qc"])
    from pymol import cmd
    for k, v in PAL.items():
        cmd.set_color(k, rgb(v))

    version = cmd.get_version()[0]
    print("=" * 78)
    print("EN | Mechanism schematic: structure renders | PT | Esquema de mecanismo: renders de estrutura")
    print("=" * 78)
    print(f"PyMOL {version} | order {', '.join(ORDER)} | canvas {W} x {H} px")
    log = {
        "_note_en": "Illustration of four deposited structures; not a result. Rendered in the order given, in one session: "
                    "the views of AGO2 and BACE1 depend on the camera left by the render before them.",
        "_note_pt": "Ilustracao de quatro estruturas depositadas; nao e resultado. Renderizado na ordem dada, numa sessao so: "
                    "as vistas da AGO2 e da BACE1 dependem da camera deixada pelo render anterior.",
        "pymol_version": version, "canvas_px": [W, H], "render_order": list(ORDER), "inputs": inputs,
    }
    for target in ORDER:
        t0 = time.time()
        if target == "abeta42":
            log["abeta42_protofilaments"] = render_fibril(cmd, prov, "5OQV", "abeta42", "ad_dark", "ad_mid", "bg_ad")
        elif target == "asyn":
            log["asyn_protofilaments"] = render_fibril(cmd, prov, "6CU7", "asyn", "pd_dark", "pd_mid", "bg_pd")
        elif target == "ago2":
            render_ago2(cmd)
        elif target == "bace1":
            log["bace1_catalytic_dyad_resi"] = render_bace1(cmd, s13, prov)
        print(f"  {target} done in {time.time() - t0:.0f} s", flush=True)

    log["outputs_sha256"] = {f: sha256(os.path.join(OUT_DIR, f)) for f in sorted(os.listdir(OUT_DIR)) if f.endswith(".png")}
    with open(LOG, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(log, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"EN/PT -> {LOG}")
    cmd.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
