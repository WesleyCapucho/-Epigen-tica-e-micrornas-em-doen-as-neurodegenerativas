// Minimal Markdown -> DOCX converter for the manuscript drafts.
// Handles: headings, paragraphs, bold/italic/code inline, tables, bullet lists,
// ordered reference lists and horizontal rules.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  LevelFormat, convertInchesToTwip,
} = require("docx");

const FONT = "Calibri";
const inFile = process.argv[2];
const outFile = process.argv[3];
const md = fs.readFileSync(inFile, "utf8");

function inlineRuns(text, base = {}) {
  const runs = [];
  // split on **bold**, *italic*, `code`
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) {
      runs.push(new TextRun({ text: text.slice(last, m.index), font: FONT, size: 22, ...base }));
    }
    const tok = m[0];
    if (tok.startsWith("**")) {
      runs.push(new TextRun({ text: tok.slice(2, -2), font: FONT, size: 22, bold: true, ...base }));
    } else if (tok.startsWith("`")) {
      runs.push(new TextRun({ text: tok.slice(1, -1), font: "Consolas", size: 20, ...base }));
    } else {
      runs.push(new TextRun({ text: tok.slice(1, -1), font: FONT, size: 22, italics: true, ...base }));
    }
    last = m.index + tok.length;
  }
  if (last < text.length) {
    runs.push(new TextRun({ text: text.slice(last), font: FONT, size: 22, ...base }));
  }
  return runs.length ? runs : [new TextRun({ text: "", font: FONT, size: 22 })];
}

function cell(text, header, widthPct) {
  return new TableCell({
    width: { size: widthPct, type: WidthType.PERCENTAGE },
    shading: header ? { type: ShadingType.CLEAR, fill: "1F3864" } : undefined,
    margins: { top: 90, bottom: 90, left: 110, right: 110 },
    children: [new Paragraph({
      children: inlineRuns(text.replace(/\*\*/g, ""), {
        bold: header, color: header ? "FFFFFF" : "000000", size: 20,
      }),
    })],
  });
}

const lines = md.split("\n");
const children = [];
let i = 0;

while (i < lines.length) {
  const line = lines[i];

  // table
  if (line.trim().startsWith("|") && lines[i + 1] && /^\s*\|[\s:|-]+\|\s*$/.test(lines[i + 1])) {
    const rows = [];
    const header = line.split("|").slice(1, -1).map((s) => s.trim());
    i += 2;
    const body = [];
    while (i < lines.length && lines[i].trim().startsWith("|")) {
      body.push(lines[i].split("|").slice(1, -1).map((s) => s.trim()));
      i++;
    }
    const nCols = header.length;
    const w = Math.floor(100 / nCols);
    rows.push(new TableRow({ children: header.map((h) => cell(h, true, w)) }));
    for (const r of body) {
      while (r.length < nCols) r.push("");
      rows.push(new TableRow({ children: r.slice(0, nCols).map((c) => cell(c, false, w)) }));
    }
    children.push(new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows }));
    children.push(new Paragraph({ spacing: { after: 180 }, children: [] }));
    continue;
  }

  if (/^---+\s*$/.test(line)) {
    children.push(new Paragraph({
      border: { bottom: { color: "AAAAAA", space: 4, style: BorderStyle.SINGLE, size: 6 } },
      spacing: { after: 200 }, children: [],
    }));
    i++; continue;
  }

  const h = line.match(/^(#{1,4})\s+(.*)$/);
  if (h) {
    const lvl = h[1].length;
    const sizes = { 1: 32, 2: 26, 3: 23, 4: 22 };
    children.push(new Paragraph({
      heading: [null, HeadingLevel.TITLE, HeadingLevel.HEADING_1,
                HeadingLevel.HEADING_2, HeadingLevel.HEADING_3][lvl],
      spacing: { before: lvl === 1 ? 0 : 300, after: 160 },
      alignment: lvl === 1 ? AlignmentType.CENTER : AlignmentType.LEFT,
      children: inlineRuns(h[2], { bold: true, size: sizes[lvl] }),
    }));
    i++; continue;
  }

  const bullet = line.match(/^[-*]\s+(.*)$/);
  if (bullet) {
    children.push(new Paragraph({
      numbering: { reference: "bullets", level: 0 },
      spacing: { after: 90 },
      children: inlineRuns(bullet[1]),
    }));
    i++; continue;
  }

  const num = line.match(/^(\d+)\.\s+(.*)$/);
  if (num) {
    children.push(new Paragraph({
      spacing: { after: 90 },
      indent: { left: convertInchesToTwip(0.32), hanging: convertInchesToTwip(0.32) },
      children: inlineRuns(`${num[1]}. ${num[2]}`, { size: 20 }),
    }));
    i++; continue;
  }

  if (line.trim() === "") { i++; continue; }

  children.push(new Paragraph({
    spacing: { after: 160, line: 300 },
    alignment: AlignmentType.JUSTIFIED,
    children: inlineRuns(line),
  }));
  i++;
}

const doc = new Document({
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: "•",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: convertInchesToTwip(0.3), hanging: convertInchesToTwip(0.18) } } },
      }],
    }],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 } } }, // A4
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(outFile, buf);
  console.log(`wrote ${outFile}`);
});
