#!/usr/bin/env python3
"""Converte o material de revisão (Markdown simples) em PDF.

Uso:
    python scripts/gerar_pdf.py sessoes/<sessão>/revisao.md [--saida arquivo.pdf]

Markdown suportado (ver .claude/skills/analise-desempenho-revisao/references/modelo-revisao.md):
    --- bloco de capa --- (titulo, subtitulo, data, material, modo, perfil)
    # / ## / ###          títulos
    parágrafos, listas "- " e "1. ", **negrito**, *itálico*, `código`
    tabelas com pipes    | a | b |
    > [!ATENCAO] texto    quadro vermelho  (erro conceitual / pegadinha)
    > [!DICA] texto       quadro verde     (como escrever na prova / macete)
    > [!FUNDAMENTO] texto quadro azul      (lei, súmula, tese, doutrina)
    > [!PROVA] texto      quadro âmbar     (como a banca cobra)
    > texto               citação simples
    ---                   quebra de página (fora da capa)
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (KeepTogether, ListFlowable, ListItem, PageBreak, Paragraph,
                                    SimpleDocTemplate, Spacer, Table, TableStyle)
except ImportError:
    sys.exit("ERRO: reportlab não instalado. Rode: pip install -r requirements.txt "
             "(o revisao.md continua disponível para leitura).")

# ---------------------------------------------------------------- fontes (com fallback portátil)
CANDIDATAS = [
    ("DejaVuSans", ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/Library/Fonts/DejaVuSans.ttf"],
     ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/Library/Fonts/DejaVuSans-Bold.ttf"]),
    ("Arial", ["C:/Windows/Fonts/arial.ttf", "/Library/Fonts/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"],
     ["C:/Windows/Fonts/arialbd.ttf", "/Library/Fonts/Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"]),
    ("LiberationSans", ["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"],
     ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]),
]


ITALICOS = {
    "DejaVuSans": ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", "/Library/Fonts/DejaVuSans-Oblique.ttf"],
    "Arial": ["C:/Windows/Fonts/ariali.ttf", "/Library/Fonts/Arial Italic.ttf", "/System/Library/Fonts/Supplemental/Arial Italic.ttf"],
    "LiberationSans": ["/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"],
}


def registrar_fonte() -> tuple[str, str]:
    for nome, regs, bolds in CANDIDATAS:
        reg = next((p for p in regs if Path(p).exists()), None)
        bold = next((p for p in bolds if Path(p).exists()), None)
        if reg and bold:
            try:
                pdfmetrics.registerFont(TTFont(nome, reg))
                pdfmetrics.registerFont(TTFont(nome + "-Bold", bold))
                ital = next((p for p in ITALICOS.get(nome, []) if Path(p).exists()), None)
                italico = nome
                if ital:
                    pdfmetrics.registerFont(TTFont(nome + "-Italic", ital))
                    italico = nome + "-Italic"
                pdfmetrics.registerFontFamily(nome, normal=nome, bold=nome + "-Bold",
                                              italic=italico, boldItalic=nome + "-Bold")
                return nome, nome + "-Bold"
            except Exception:
                continue
    return "Helvetica", "Helvetica-Bold"


FONTE, FONTE_B = registrar_fonte()

# Emojis e símbolos que as fontes comuns não desenham: troca por texto.
SUBSTITUICOES = {
    "✅": "[ENTREGOU]", "◐": "[PARCIAL]", "❌": "[FALTOU]", "⚠️": "[ERRO]", "⚠": "[ERRO]",
    "↑": "(subiu)", "↓": "(caiu)", "→": "->", "⏰": "", "📌": "", "💡": "", "🎯": "", "📚": "",
    "\u200d": "", "\ufe0f": "",
}

COR_PRIMARIA = colors.HexColor("#1F3A5F")
QUADROS = {
    "ATENCAO": ("Atenção", colors.HexColor("#FDECEA"), colors.HexColor("#C0392B")),
    "DICA": ("Como escrever na prova", colors.HexColor("#E8F6EF"), colors.HexColor("#1E8449")),
    "FUNDAMENTO": ("Fundamento", colors.HexColor("#EAF2FB"), colors.HexColor("#2E6DA4")),
    "PROVA": ("Como a banca cobra", colors.HexColor("#FEF5E7"), colors.HexColor("#B9770E")),
}


def limpar(txt: str) -> str:
    for a, b in SUBSTITUICOES.items():
        txt = txt.replace(a, b)
    return txt


def inline(txt: str) -> str:
    txt = html.escape(limpar(txt), quote=False)
    txt = re.sub(r"`([^`]+)`", r'<font face="Courier">\1</font>', txt)
    txt = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", txt)
    txt = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", txt)
    return txt


def estilos():
    base = getSampleStyleSheet()
    s = {
        "corpo": ParagraphStyle("corpo", parent=base["BodyText"], fontName=FONTE, fontSize=10.5, leading=15, spaceAfter=6),
        "h1": ParagraphStyle("h1", fontName=FONTE_B, fontSize=17, leading=22, textColor=COR_PRIMARIA, spaceBefore=10, spaceAfter=8),
        "h2": ParagraphStyle("h2", fontName=FONTE_B, fontSize=13.5, leading=18, textColor=COR_PRIMARIA, spaceBefore=12, spaceAfter=6),
        "h3": ParagraphStyle("h3", fontName=FONTE_B, fontSize=11.5, leading=15, textColor=colors.HexColor("#333333"), spaceBefore=8, spaceAfter=4),
        "citacao": ParagraphStyle("citacao", fontName=FONTE, fontSize=10, leading=14, leftIndent=12, textColor=colors.HexColor("#555555"), spaceAfter=6),
        "capa_t": ParagraphStyle("capa_t", fontName=FONTE_B, fontSize=26, leading=32, alignment=TA_CENTER, textColor=COR_PRIMARIA),
        "capa_s": ParagraphStyle("capa_s", fontName=FONTE, fontSize=14, leading=20, alignment=TA_CENTER, textColor=colors.HexColor("#444444")),
        "capa_m": ParagraphStyle("capa_m", fontName=FONTE, fontSize=11, leading=17, alignment=TA_CENTER, textColor=colors.HexColor("#666666")),
        "celula": ParagraphStyle("celula", fontName=FONTE, fontSize=9, leading=12),
        "celula_h": ParagraphStyle("celula_h", fontName=FONTE_B, fontSize=9, leading=12, textColor=colors.white),
        "quadro_t": ParagraphStyle("quadro_t", fontName=FONTE_B, fontSize=10, leading=13, spaceAfter=2),
        "quadro": ParagraphStyle("quadro", fontName=FONTE, fontSize=10, leading=14),
    }
    return s


def capa(meta: dict, S) -> list:
    fl = [Spacer(1, 6 * cm), Paragraph(inline(meta.get("titulo", "Revisão dirigida")), S["capa_t"]), Spacer(1, 0.6 * cm)]
    if meta.get("subtitulo"):
        fl += [Paragraph(inline(meta["subtitulo"]), S["capa_s"]), Spacer(1, 1.5 * cm)]
    for campo, rotulo in (("material", "Material"), ("modo", "Modo"), ("perfil", "Perfil"), ("data", "Data")):
        if meta.get(campo):
            fl.append(Paragraph(f"<b>{rotulo}:</b> {inline(meta[campo])}", S["capa_m"]))
    fl.append(PageBreak())
    return fl


def quadro(tipo: str, linhas: list[str], S, largura: float):
    rotulo, fundo, borda = QUADROS[tipo]
    titulo = ParagraphStyle("qt", parent=S["quadro_t"], textColor=borda)
    conteudo = [Paragraph(rotulo, titulo)] + [Paragraph(inline(l), S["quadro"]) for l in linhas if l.strip()]
    t = Table([[conteudo]], colWidths=[largura])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fundo),
        ("LINEBEFORE", (0, 0), (0, -1), 3, borda),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return KeepTogether([t, Spacer(1, 8)])


def tabela(linhas: list[str], S, largura: float):
    rows = []
    for l in linhas:
        if re.match(r"^\s*\|?\s*:?-{2,}", l):
            continue
        cels = [c.strip() for c in l.strip().strip("|").split("|")]
        rows.append(cels)
    if not rows:
        return None
    ncol = max(len(r) for r in rows)
    dados = []
    for i, r in enumerate(rows):
        r = r + [""] * (ncol - len(r))
        estilo = S["celula_h"] if i == 0 else S["celula"]
        dados.append([Paragraph(inline(c), estilo) for c in r])
    t = Table(dados, colWidths=[largura / ncol] * ncol, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COR_PRIMARIA),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F6F8")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9D1D9")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return KeepTogether([t, Spacer(1, 10)])


def lista(itens: list[str], numerada: bool, S):
    return ListFlowable(
        [ListItem(Paragraph(inline(i), S["corpo"]), leftIndent=14) for i in itens],
        bulletType="1" if numerada else "bullet", start=1 if numerada else None,
        bulletFontName=FONTE, bulletFontSize=9, leftIndent=14,
    )


def converter(md: str, S, largura: float) -> list:
    linhas = md.splitlines()
    fl: list = []
    i = 0
    if linhas and linhas[0].strip() == "---":
        meta, i = {}, 1
        while i < len(linhas) and linhas[i].strip() != "---":
            if ":" in linhas[i]:
                k, v = linhas[i].split(":", 1)
                meta[k.strip().lower()] = v.strip()
            i += 1
        i += 1
        fl += capa(meta, S)

    paragrafo: list[str] = []

    def fechar_paragrafo():
        if paragrafo:
            fl.append(Paragraph(inline(" ".join(paragrafo)), S["corpo"]))
            paragrafo.clear()

    while i < len(linhas):
        l = linhas[i]
        s = l.strip()
        if not s:
            fechar_paragrafo(); i += 1; continue
        if s == "---":
            fechar_paragrafo(); fl.append(PageBreak()); i += 1; continue
        m = re.match(r"^(#{1,3})\s+(.*)", s)
        if m:
            fechar_paragrafo()
            fl.append(Paragraph(inline(m.group(2)), S[f"h{len(m.group(1))}"]))
            i += 1; continue
        if s.startswith("|"):
            fechar_paragrafo()
            bloco = []
            while i < len(linhas) and linhas[i].strip().startswith("|"):
                bloco.append(linhas[i]); i += 1
            t = tabela(bloco, S, largura)
            if t:
                fl.append(t)
            continue
        if s.startswith(">"):
            fechar_paragrafo()
            bloco = []
            while i < len(linhas) and linhas[i].strip().startswith(">"):
                bloco.append(linhas[i].strip()[1:].strip()); i += 1
            m = re.match(r"^\[!(\w+)\]\s*(.*)", bloco[0])
            tipo = m.group(1).upper().replace("Ç", "C").replace("Ã", "A") if m else None
            if m and tipo in QUADROS:
                fl.append(quadro(tipo, [m.group(2)] + bloco[1:], S, largura))
            else:
                fl.append(Paragraph(inline(" ".join(bloco)), S["citacao"]))
            continue
        if re.match(r"^[-*]\s+", s) or re.match(r"^\d+[.)]\s+", s):
            fechar_paragrafo()
            numerada = bool(re.match(r"^\d+[.)]\s+", s))
            itens = []
            padrao = r"^\d+[.)]\s+" if numerada else r"^[-*]\s+"
            while i < len(linhas) and re.match(padrao, linhas[i].strip()):
                itens.append(re.sub(padrao, "", linhas[i].strip())); i += 1
                while i < len(linhas) and linhas[i].startswith(("  ", "\t")) and linhas[i].strip() \
                        and not re.match(padrao, linhas[i].strip()):
                    itens[-1] += " " + linhas[i].strip(); i += 1
            fl.append(lista(itens, numerada, S))
            continue
        paragrafo.append(s)
        i += 1
    fechar_paragrafo()
    return fl


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONTE, 8)
    canvas.setFillColor(colors.HexColor("#888888"))
    if doc.page > 1:
        canvas.drawString(2 * cm, 1.2 * cm, "Revisão em voz alta · material dirigido às lacunas")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"{doc.page}")
    canvas.restoreState()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("markdown")
    ap.add_argument("--saida")
    args = ap.parse_args()
    origem = Path(args.markdown)
    if not origem.exists():
        sys.exit(f"ERRO: não encontrado: {origem}")
    saida = Path(args.saida) if args.saida else origem.with_suffix(".pdf")
    S = estilos()
    doc = SimpleDocTemplate(str(saida), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm, title="Revisão dirigida")
    largura = A4[0] - 4 * cm
    doc.build(converter(origem.read_text(encoding="utf-8"), S, largura), onFirstPage=rodape, onLaterPages=rodape)
    print(f"PDF gerado: {saida} (fonte: {FONTE})")


if __name__ == "__main__":
    main()
