#!/usr/bin/env node
/*
 * Gera o DOCX do material de revisão a partir do revisao.md (mesmo layout do PDF).
 *
 * Uso:    node scripts/gerar_docx.js sessoes/<sessão>/revisao.md [saida.docx]
 * Prefira: python scripts/gerar_material.py sessoes/<sessão>/revisao.md   (DOCX e PDF)
 *
 * Fontes: Open Sans e Bebas Neue (assets/fonts; instale no sistema para ver no Word, senão ele usa substitutas).
 * Marcações: as mesmas de scripts/gerar_pdf.py (ver references/modelo-revisao.md).
 */
'use strict';
const fs = require('fs');
const path = require('path');
let docx;
try {
  docx = require('docx');
} catch (e) {
  console.error('ERRO: biblioteca "docx" não encontrada. Rode "npm install" na pasta do projeto.');
  process.exit(1);
}
const {
  AlignmentType, BorderStyle, Document, Footer, HeightRule, Packer, PageBreak, PageNumber, Paragraph,
  ShadingType, Table, TableCell, TableOfContents, TableRow, TextRun, VerticalAlign, WidthType, HeadingLevel,
} = docx;

// ---------------------------------------------------------------- identidade visual
const FONTE = 'Open Sans';
const ROTULO = 'Bebas Neue';
const COR = {
  verde: '00673A', verdeCapa: '118742', magenta: 'B62CA2', texto: '1F1F1F', cinza: '5F6368', quadroTexto: '333333',
};
const QUADROS = {
  ATENCAO: { rotulo: 'ATENÇÃO', cor: 'B62CA2', fundo: 'FBEFF9' },
  DICA: { rotulo: 'COMO ESCREVER NA PROVA', cor: '00673A', fundo: 'EAF4EE' },
  FUNDAMENTO: { rotulo: 'FUNDAMENTO', cor: '1F5F8B', fundo: 'EAF1F7' },
  PROVA: { rotulo: 'COMO A BANCA COBRA', cor: 'B9770E', fundo: 'FDF4E6' },
};
const ROTULOS = { 'Entregou:': '00673A', 'Parcial:': 'B9770E', 'Faltou:': 'C0392B', 'Erro conceitual:': 'C0392B' };

const A4 = { w: 11906, h: 16838 };
const MARGEM_X = 1418;
const CORPO = A4.w - 2 * MARGEM_X;
const RECUO_BLOCO = 794; // 1,4 cm
const SEM = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const SEM_BORDAS = { top: SEM, bottom: SEM, left: SEM, right: SEM };

// ---------------------------------------------------------------- texto inline
function runs(texto, base = {}) {
  const out = [];
  const re = /(\*\*(.+?)\*\*|==(.+?)==|(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*]))/g;
  let ultimo = 0;
  let m;
  const push = (t, extra = {}) => { if (t) out.push(new TextRun({ text: t, font: FONTE, ...base, ...extra })); };
  while ((m = re.exec(texto)) !== null) {
    push(texto.slice(ultimo, m.index));
    if (m[2] !== undefined) push(m[2], ROTULOS[m[2]] ? { bold: true, color: ROTULOS[m[2]] } : { bold: true });
    else if (m[3] !== undefined) push(m[3], { bold: true, color: COR.magenta });
    else if (m[4] !== undefined) push(m[4], { italics: true });
    ultimo = re.lastIndex;
  }
  push(texto.slice(ultimo));
  return out;
}

const par = (texto, opts = {}) => new Paragraph({
  children: runs(texto, { size: opts.size || 21, color: opts.color || COR.texto, bold: opts.bold }),
  spacing: { after: opts.after ?? 140, line: opts.line || 300 },
  alignment: opts.alignment || AlignmentType.JUSTIFIED,
  keepNext: opts.keepNext,
});

// ---------------------------------------------------------------- blocos
function capa(meta) {
  const brancoTexto = (t, size, bold) => new TextRun({ text: t, font: FONTE, size, bold, color: 'FFFFFF' });
  const conteudo = [
    new Paragraph({ spacing: { before: 900, after: 300 }, children: [brancoTexto(meta.titulo || 'Revisão dirigida', 60, true)] }),
  ];
  if (meta.subtitulo) conteudo.push(new Paragraph({ spacing: { after: 200 }, children: [brancoTexto(meta.subtitulo, 28)] }));
  return [
    new Table({
      width: { size: CORPO, type: WidthType.DXA },
      columnWidths: [CORPO],
      rows: [new TableRow({
        height: { value: 12600, rule: HeightRule.EXACT },
        children: [new TableCell({
          width: { size: CORPO, type: WidthType.DXA },
          borders: SEM_BORDAS,
          shading: { type: ShadingType.CLEAR, color: 'auto', fill: COR.verdeCapa },
          margins: { left: 600, right: 600, top: 400 },
          children: conteudo,
        })],
      })],
    }),
    new Paragraph({
      spacing: { before: 360, after: 80 },
      children: [new TextRun({
        text: ` ${[meta.modo, meta.data].filter(Boolean).join(' · ') || 'Revisão dirigida'} `,
        font: FONTE, size: 18, bold: true, color: 'FFFFFF', shading: { type: ShadingType.CLEAR, color: 'auto', fill: COR.magenta },
      })],
    }),
    ...[meta.perfil, meta.material].filter(Boolean).map((t) => new Paragraph({
      spacing: { after: 40 }, children: [new TextRun({ text: t, font: FONTE, size: 17, color: COR.cinza })],
    })),
    new Paragraph({ children: [new PageBreak()] }),
    new Paragraph({ spacing: { after: 360 }, children: [new TextRun({ text: 'Sumário', font: FONTE, size: 68, bold: true, color: COR.verde })] }),
    new TableOfContents('Sumário', { hyperlink: true, headingStyleRange: '1-2' }),
    new Paragraph({ children: [new PageBreak()] }),
  ];
}

function titulo(nivel, texto) {
  const cfg = { 1: [40, COR.verde], 2: [27, COR.verde], 3: [23, COR.texto] }[nivel];
  return new Paragraph({
    heading: [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3][nivel - 1],
    keepNext: true,
    spacing: { before: nivel === 1 ? 240 : 280, after: nivel === 1 ? 240 : 140 },
    children: runs(texto, { size: cfg[0], bold: true, color: cfg[1] }),
  });
}

function blocoComFilete(filhos, cor, fundo) {
  const larg = CORPO - RECUO_BLOCO;
  return [
    new Table({
      width: { size: larg, type: WidthType.DXA },
      columnWidths: [larg],
      indent: { size: RECUO_BLOCO, type: WidthType.DXA },
      rows: [new TableRow({
        cantSplit: true,
        children: [new TableCell({
          width: { size: larg, type: WidthType.DXA },
          shading: fundo ? { type: ShadingType.CLEAR, color: 'auto', fill: fundo } : undefined,
          margins: { top: fundo ? 120 : 20, bottom: fundo ? 140 : 20, left: 220, right: 200 },
          borders: { top: SEM, bottom: SEM, right: SEM, left: { style: BorderStyle.SINGLE, size: 36, color: cor } },
          children: filhos,
        })],
      })],
    }),
    new Paragraph({ spacing: { after: 160 }, children: [] }),
  ];
}

function quadro(tipo, linhas) {
  const q = QUADROS[tipo];
  const filhos = [new Paragraph({
    spacing: { after: 40 }, keepNext: true,
    children: [new TextRun({ text: q.rotulo, font: ROTULO, size: 30, color: q.cor })],
  })];
  linhas.filter((l) => l.trim()).forEach((l, i, arr) => filhos.push(new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: i === arr.length - 1 ? 0 : 60, line: 288 },
    children: runs(l, { size: 20, color: COR.quadroTexto }),
  })));
  return blocoComFilete(filhos, q.cor, q.fundo);
}

function enunciado(texto) {
  return blocoComFilete([new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 0, line: 288 },
    children: runs(texto, { size: 20, bold: true, color: COR.cinza }),
  })], COR.magenta, null);
}

function tabela(linhas, tituloTab) {
  const rows = linhas
    .filter((l) => !/^\s*\|?\s*:?-{2,}/.test(l))
    .map((l) => l.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim()));
  if (!rows.length) return [];
  const ncol = Math.max(...rows.map((r) => r.length));
  const total = Math.round(CORPO * 0.92);
  const base = Math.floor(total / ncol);
  const larguras = Array(ncol).fill(base);
  larguras[ncol - 1] += total - base * ncol;
  const borda = { style: BorderStyle.SINGLE, size: 6, color: COR.magenta };
  const out = [];
  if (tituloTab) out.push(par(`**${tituloTab}**`, { alignment: AlignmentType.CENTER, size: 20, after: 100, keepNext: true }));
  out.push(new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: larguras,
    alignment: AlignmentType.CENTER,
    rows: rows.map((r, i) => new TableRow({
      tableHeader: i === 0,
      cantSplit: true,
      children: Array.from({ length: ncol }, (_, j) => new TableCell({
        width: { size: larguras[j], type: WidthType.DXA },
        borders: { top: borda, bottom: borda, left: borda, right: borda },
        verticalAlign: VerticalAlign.CENTER,
        shading: i === 0 ? { type: ShadingType.CLEAR, color: 'auto', fill: COR.magenta } : undefined,
        margins: { top: 80, bottom: 80, left: 110, right: 110 },
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 0, line: 264 },
          children: runs(r[j] || '', { size: 19, bold: i === 0, color: i === 0 ? 'FFFFFF' : COR.texto }),
        })],
      })),
    })),
  }));
  out.push(new Paragraph({ spacing: { after: 200 }, children: [] }));
  return out;
}

function rodape(meta) {
  const texto = 'Revisão em voz alta' + (meta.titulo ? ` · ${meta.titulo.split(':').slice(-1)[0].trim()}` : '');
  const quadradoLarg = 460;
  return new Footer({
    children: [new Table({
      width: { size: CORPO, type: WidthType.DXA },
      columnWidths: [CORPO - quadradoLarg, quadradoLarg],
      rows: [new TableRow({
        height: { value: 460, rule: HeightRule.EXACT },
        children: [
          new TableCell({
            width: { size: CORPO - quadradoLarg, type: WidthType.DXA }, borders: SEM_BORDAS, verticalAlign: VerticalAlign.CENTER,
            children: [new Paragraph({ children: [new TextRun({ text: texto, font: FONTE, size: 16, color: COR.cinza })] })],
          }),
          new TableCell({
            width: { size: quadradoLarg, type: WidthType.DXA }, borders: SEM_BORDAS, verticalAlign: VerticalAlign.CENTER,
            shading: { type: ShadingType.CLEAR, color: 'auto', fill: COR.magenta },
            children: [new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [new TextRun({ children: [PageNumber.CURRENT], font: FONTE, size: 22, bold: true, color: 'FFFFFF' })],
            })],
          }),
        ],
      })],
    })],
  });
}

// ---------------------------------------------------------------- conversão
function converter(md) {
  const linhas = md.split(/\r?\n/);
  const out = [];
  const meta = {};
  let i = 0;
  if (linhas[0] && linhas[0].trim() === '---') {
    i = 1;
    while (i < linhas.length && linhas[i].trim() !== '---') {
      const k = linhas[i].indexOf(':');
      if (k > 0) meta[linhas[i].slice(0, k).trim().toLowerCase()] = linhas[i].slice(k + 1).trim();
      i++;
    }
    i++;
  }
  out.push(...capa(meta));
  let paragrafo = [];
  let tituloTab = null;
  const fechar = () => { if (paragrafo.length) { out.push(par(paragrafo.join(' '))); paragrafo = []; } };

  while (i < linhas.length) {
    const s = linhas[i].trim();
    if (!s) { fechar(); i++; continue; }
    if (s === '---') { fechar(); out.push(new Paragraph({ children: [new PageBreak()] })); i++; continue; }
    let m = s.match(/^(#{1,3})\s+(.*)/);
    if (m) { fechar(); out.push(titulo(m[1].length, m[2])); i++; continue; }
    m = s.match(/^\*\*((?:Quadro|Tabela) \d+\..*)\*\*$/);
    if (m && linhas[i + 1] && linhas[i + 1].trim().startsWith('|')) { fechar(); tituloTab = m[1]; i++; continue; }
    if (s.startsWith('|')) {
      fechar();
      const bloco = [];
      while (i < linhas.length && linhas[i].trim().startsWith('|')) bloco.push(linhas[i++]);
      out.push(...tabela(bloco, tituloTab));
      tituloTab = null;
      continue;
    }
    if (s.startsWith('>')) {
      fechar();
      const bloco = [];
      while (i < linhas.length && linhas[i].trim().startsWith('>')) bloco.push(linhas[i++].trim().slice(1).trim());
      m = bloco[0].match(/^\[!(\w+)\]\s*(.*)/);
      const tipo = m ? m[1].toUpperCase() : null;
      if (tipo && QUADROS[tipo]) out.push(...quadro(tipo, [m[2], ...bloco.slice(1)]));
      else out.push(...enunciado(bloco.join(' ')));
      continue;
    }
    const numerada = /^\d+[.)]\s+/.test(s);
    if (numerada || /^[-*]\s+/.test(s)) {
      fechar();
      const padrao = numerada ? /^\d+[.)]\s+/ : /^[-*]\s+/;
      while (i < linhas.length && padrao.test(linhas[i].trim())) {
        // Sem marcadores no material: cada item vira um parágrafo justificado (numerados mantêm o número).
        const num = numerada ? linhas[i].trim().match(/^\d+/) : null;
        let item = linhas[i].trim().replace(padrao, '');
        i++;
        while (i < linhas.length && /^(\s{2,}|\t)/.test(linhas[i]) && linhas[i].trim() && !padrao.test(linhas[i].trim())) {
          item += ' ' + linhas[i].trim();
          i++;
        }
        out.push(par(num ? `**${num[0]}.** ${item}` : item));
      }
      continue;
    }
    paragrafo.push(s);
    i++;
  }
  fechar();
  return { out, meta };
}

function main() {
  const [, , entrada, saidaArg] = process.argv;
  if (!entrada) {
    console.error('Uso: node scripts/gerar_docx.js <revisao.md> [saida.docx]');
    process.exit(1);
  }
  const md = fs.readFileSync(entrada, 'utf8');
  const { out, meta } = converter(md);
  const saida = saidaArg || entrada.replace(/\.md$/i, '.docx');
  const doc = new Document({
    creator: 'Revisão em voz alta',
    title: meta.titulo || 'Revisão dirigida',
    features: { updateFields: true },
    styles: {
      default: { document: { run: { font: FONTE, size: 21, color: COR.texto } } },
      paragraphStyles: [
        { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
          run: { font: FONTE, size: 40, bold: true, color: COR.verde }, paragraph: { outlineLevel: 0 } },
        { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
          run: { font: FONTE, size: 27, bold: true, color: COR.verde }, paragraph: { outlineLevel: 1 } },
        { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
          run: { font: FONTE, size: 23, bold: true, color: COR.texto }, paragraph: { outlineLevel: 2 } },
      ],
    },
    sections: [{
      properties: {
        page: { size: { width: A4.w, height: A4.h }, margin: { top: 1304, bottom: 1474, left: MARGEM_X, right: MARGEM_X } },
        titlePage: true,
      },
      footers: { default: rodape(meta), first: new Footer({ children: [new Paragraph({ children: [] })] }) },
      children: out,
    }],
  });
  Packer.toBuffer(doc).then((buf) => {
    fs.writeFileSync(saida, buf);
    console.log(`DOCX gerado: ${path.normalize(saida)}`);
  });
}

main();
