#!/usr/bin/env python3
"""Gera o PDF do material de revisão a partir do revisao.md (layout padrão do projeto).

Uso:
    python scripts/gerar_pdf.py sessoes/<sessão>/revisao.md [--saida arquivo.pdf]
Prefira: python scripts/gerar_material.py sessoes/<sessão>/revisao.md   (DOCX e PDF)

Identidade visual: capa verde, sumário, Open Sans justificada, títulos verdes, destaques em magenta, rótulos dos
quadros em fonte condensada (Bebas Neue), tabelas com cabeçalho magenta e número da página em quadrado magenta.
Fontes em assets/fonts (licença OFL). Guia completo:
.claude/skills/analise-desempenho-revisao/references/modelo-revisao.md

Marcações:
    --- capa ---            titulo, subtitulo, material, modo, perfil, data
    # / ## / ###            títulos (# e ## entram no sumário)
    **negrito**  *itálico*  ==destaque magenta==
    **Entregou:** **Parcial:** **Faltou:** **Erro conceitual:**   rótulos coloridos do feedback
    > texto                 enunciado ou citação (filete magenta)
    > [!ATENCAO] ...        quadro ATENÇÃO
    > [!DICA] ...           quadro COMO ESCREVER NA PROVA
    > [!FUNDAMENTO] ...     quadro FUNDAMENTO
    > [!PROVA] ...          quadro COMO A BANCA COBRA
    **Quadro 1. Título**    título centralizado da tabela seguinte
    | a | b |               tabela
    ---                     quebra de página
Listas viram parágrafos justificados (o material não usa marcadores). Travessões (— –) são recusados.
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
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (CondPageBreak, KeepTogether, PageBreak, Paragraph, Spacer, Table, TableStyle)
    from reportlab.platypus.doctemplate import SimpleDocTemplate
    from reportlab.platypus.tableofcontents import TableOfContents
except ImportError:
    sys.exit("ERRO: reportlab não instalado. Rode: pip install -r requirements.txt")

RAIZ = Path(__file__).resolve().parent.parent
FONTES = RAIZ / "assets" / "fonts"

# ---------------------------------------------------------------- fontes
def registrar_fontes() -> dict:
    arquivos = {
        "OS": "OpenSans-Regular.ttf", "OS-B": "OpenSans-Bold.ttf", "OS-I": "OpenSans-Italic.ttf",
        "OS-BI": "OpenSans-BoldItalic.ttf", "OS-SB": "OpenSans-SemiBold.ttf", "OS-XB": "OpenSans-ExtraBold.ttf",
        "Bebas": "BebasNeue-Regular.ttf",
    }
    if all((FONTES / a).exists() for a in arquivos.values()):
        for nome, arq in arquivos.items():
            pdfmetrics.registerFont(TTFont(nome, str(FONTES / arq)))
        pdfmetrics.registerFontFamily("OS", normal="OS", bold="OS-B", italic="OS-I", boldItalic="OS-BI")
        return {"r": "OS", "b": "OS-B", "sb": "OS-SB", "xb": "OS-XB", "rot": "Bebas"}
    print("AVISO: fontes de assets/fonts ausentes; usando Helvetica.")
    return {"r": "Helvetica", "b": "Helvetica-Bold", "sb": "Helvetica-Bold", "xb": "Helvetica-Bold", "rot": "Helvetica-Bold"}


F = registrar_fontes()

# ---------------------------------------------------------------- paleta
H = colors.HexColor
VERDE, VERDE_ESC, VERDE_CAPA, VERDE_CAPA_ESC = H("#00673A"), H("#005F2B"), H("#118742"), H("#0D6D35")
MAGENTA = H("#B62CA2")
TEXTO, CINZA, CINZA_CLARO = H("#1F1F1F"), H("#5F6368"), H("#8A8F94")

QUADROS = {  # rótulo, cor do filete e do rótulo, fundo
    "ATENCAO": ("ATENÇÃO", MAGENTA, H("#FBEFF9")),
    "DICA": ("COMO ESCREVER NA PROVA", VERDE, H("#EAF4EE")),
    "FUNDAMENTO": ("FUNDAMENTO", H("#1F5F8B"), H("#EAF1F7")),
    "PROVA": ("COMO A BANCA COBRA", H("#B9770E"), H("#FDF4E6")),
}
ROTULOS = {"Entregou:": "#00673A", "Parcial:": "#B9770E", "Faltou:": "#C0392B", "Erro conceitual:": "#C0392B"}

MARGEM_X, MARGEM_TOPO, MARGEM_BASE = 2.5 * cm, 2.3 * cm, 2.6 * cm
LARGURA = A4[0] - 2 * MARGEM_X


def est(nome, **kw):
    base = dict(fontName=F["r"], fontSize=10.5, leading=15.5, textColor=TEXTO)
    base.update(kw)
    return ParagraphStyle(nome, **base)


S = {
    "corpo": est("corpo", alignment=TA_JUSTIFY, spaceAfter=7),
    "h1": est("h1", fontName=F["xb"], fontSize=20, leading=25, textColor=VERDE, spaceBefore=6, spaceAfter=12),
    "h2": est("h2", fontName=F["b"], fontSize=13.5, leading=18, textColor=VERDE, spaceBefore=14, spaceAfter=7),
    "h3": est("h3", fontName=F["b"], fontSize=11.5, leading=15, textColor=TEXTO, spaceBefore=10, spaceAfter=5),
    "enunciado": est("enunciado", fontName=F["sb"], fontSize=10, leading=14.5, textColor=CINZA, alignment=TA_JUSTIFY),
    "quadro_rot": est("quadro_rot", fontName=F["rot"], fontSize=15, leading=16, spaceAfter=3),
    "quadro": est("quadro", fontSize=10, leading=14.5, alignment=TA_JUSTIFY, textColor=H("#333333")),
    "tab_titulo": est("tab_titulo", fontName=F["b"], fontSize=10, leading=13, alignment=TA_CENTER, spaceBefore=4, spaceAfter=5),
    "cel": est("cel", fontSize=9.5, leading=12.5, alignment=TA_CENTER),
    "cel_h": est("cel_h", fontName=F["b"], fontSize=9.5, leading=12.5, alignment=TA_CENTER, textColor=colors.white),
    "sumario_t": est("sumario_t", fontName=F["xb"], fontSize=34, leading=40, textColor=VERDE, spaceAfter=18),
    "toc0": est("toc0", fontName=F["b"], fontSize=12, leading=16, textColor=VERDE, spaceBefore=10, alignment=TA_LEFT),
    "toc1": est("toc1", fontSize=10, leading=14, leftIndent=0, alignment=TA_LEFT),
}

SUBST = {"✅": "", "◐": "", "❌": "", "⚠️": "", "⚠": "", "↑": "subiu", "↓": "caiu", "→": "->", "️": "", "‍": ""}


def inline(txt: str) -> str:
    for a, b in SUBST.items():
        txt = txt.replace(a, b)
    txt = html.escape(txt.strip(), quote=False)
    for rotulo, cor in ROTULOS.items():
        txt = txt.replace(f"**{rotulo}**", f'<font name="{F["b"]}" color="{cor}">{rotulo}</font>')
    txt = re.sub(r"==(.+?)==", rf'<font name="{F["b"]}" color="#B62CA2">\1</font>', txt)
    txt = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", txt)
    txt = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", txt)
    return txt


# ---------------------------------------------------------------- blocos
def barra(conteudo: list, cor, fundo=None, pad_esq=12):
    t = Table([["", conteudo]], colWidths=[4, LARGURA - 4 - 1.4 * cm], hAlign="RIGHT")
    estilo = [
        ("BACKGROUND", (0, 0), (0, 0), cor),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), pad_esq), ("RIGHTPADDING", (1, 0), (1, 0), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 7 if fundo else 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 9 if fundo else 2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    if fundo:
        estilo.append(("BACKGROUND", (1, 0), (1, 0), fundo))
    t.setStyle(TableStyle(estilo))
    return t


def quadro(tipo: str, linhas: list[str]):
    rot, cor, fundo = QUADROS[tipo]
    conteudo = [Paragraph(rot, ParagraphStyle("qr", parent=S["quadro_rot"], textColor=cor))]
    conteudo += [Paragraph(inline(l), S["quadro"]) for l in linhas if l.strip()]
    return KeepTogether([Spacer(1, 3), barra(conteudo, cor, fundo), Spacer(1, 11)])


def enunciado(texto: str):
    return KeepTogether([Spacer(1, 2), barra([Paragraph(inline(texto), S["enunciado"])], MAGENTA), Spacer(1, 10)])


def tabela(linhas: list[str], titulo: str | None):
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in linhas if not re.match(r"^\s*\|?\s*:?-{2,}", l)]
    if not rows:
        return []
    ncol = max(len(r) for r in rows)
    dados = [[Paragraph(inline(c), S["cel_h"] if i == 0 else S["cel"]) for c in (r + [""] * (ncol - len(r)))]
             for i, r in enumerate(rows)]
    larg = LARGURA * 0.92
    t = Table(dados, colWidths=[larg / ncol] * ncol, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), MAGENTA),
        ("GRID", (0, 0), (-1, -1), 0.6, MAGENTA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    fl = [Paragraph(inline(titulo), S["tab_titulo"])] if titulo else []
    return [KeepTogether(fl + [t]), Spacer(1, 12)]


class Titulo(Paragraph):
    """Parágrafo de título que se registra no sumário."""
    def __init__(self, texto, estilo, nivel):
        super().__init__(texto, estilo)
        self.nivel = nivel
        self.texto_limpo = re.sub(r"<[^>]+>", "", texto)


class Documento(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Titulo) and flowable.nivel <= 1:
            self.notify("TOCEntry", (flowable.nivel, flowable.texto_limpo, self.page))


# ---------------------------------------------------------------- capa e rodapé
def desenhar_capa(canvas, meta: dict):
    w, h = A4
    canvas.saveState()
    canvas.setFillColor(VERDE_CAPA)
    canvas.rect(0, 0, w, h - 0.0, stroke=0, fill=1)
    # traçado decorativo: linhas grossas com cantos arredondados
    canvas.setStrokeColor(VERDE_CAPA_ESC)
    canvas.setLineWidth(26)
    canvas.setLineCap(1)
    canvas.setLineJoin(1)
    caminhos = [
        [(-20, h * 0.80), (w * 0.22, h * 0.80), (w * 0.22, h * 0.64), (w * 0.40, h * 0.64), (w * 0.40, h * 0.47)],
        [(w * 0.62, h + 20), (w * 0.62, h * 0.90), (w * 0.86, h * 0.90), (w * 0.86, h * 0.72), (w + 20, h * 0.72)],
        [(w * 0.10, -20), (w * 0.10, h * 0.20), (w * 0.33, h * 0.20), (w * 0.33, h * 0.33), (w * 0.58, h * 0.33)],
        [(w * 0.70, h * 0.18), (w * 0.70, h * 0.42), (w * 0.92, h * 0.42), (w * 0.92, h * 0.58)],
    ]
    for c in caminhos:
        p = canvas.beginPath()
        p.moveTo(*c[0])
        for pt in c[1:]:
            p.lineTo(*pt)
        canvas.drawPath(p, stroke=1, fill=0)
    # faixa de título
    canvas.setFillColor(VERDE_CAPA)
    titulo = meta.get("titulo", "Revisão dirigida")
    estilo_t = ParagraphStyle("capa_t", fontName=F["sb"], fontSize=30, leading=38, textColor=colors.white)
    p = Paragraph(inline(titulo), estilo_t)
    pw, ph = p.wrap(w - 5 * cm, h)
    canvas.rect(2.1 * cm, h - 3.2 * cm - ph - 0.6 * cm, pw + 0.8 * cm, ph + 1.0 * cm, stroke=0, fill=1)
    p.drawOn(canvas, 2.5 * cm, h - 3.2 * cm - ph)
    if meta.get("subtitulo"):
        s = Paragraph(inline(meta["subtitulo"]), ParagraphStyle("capa_s", fontName=F["r"], fontSize=14, leading=19,
                                                                 textColor=colors.white))
        sw, sh = s.wrap(w - 5 * cm, h)
        canvas.rect(2.1 * cm, h - 3.9 * cm - ph - sh - 0.3 * cm, sw + 0.8 * cm, sh + 0.6 * cm, stroke=0, fill=1)
        s.drawOn(canvas, 2.5 * cm, h - 3.9 * cm - ph - sh)
    # rodapé branco com etiqueta magenta e dados da sessão
    canvas.setFillColor(colors.white)
    canvas.rect(0, 0, w, 2.6 * cm, stroke=0, fill=1)
    etiqueta = " · ".join(x for x in (meta.get("modo"), meta.get("data")) if x) or "Revisão dirigida"
    canvas.setFont(F["b"], 9)
    tw = canvas.stringWidth(etiqueta, F["b"], 9)
    canvas.setFillColor(MAGENTA)
    canvas.rect(1.6 * cm, 1.45 * cm, tw + 0.5 * cm, 0.55 * cm, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.drawString(1.85 * cm, 1.63 * cm, etiqueta)
    canvas.setFillColor(CINZA)
    canvas.setFont(F["r"], 8.5)
    for n, info in enumerate(x for x in (meta.get("perfil"), meta.get("material")) if x):
        canvas.drawString(1.6 * cm, (0.95 - 0.42 * n) * cm, info[:120])
    canvas.restoreState()


def rodape_factory(meta: dict):
    texto = "Revisão em voz alta" + (f" · {meta['titulo'].split(':', 1)[-1].strip()}" if meta.get("titulo") else "")

    def rodape(canvas, doc):
        if doc.page == 1:
            desenhar_capa(canvas, meta)
            return
        w, _ = A4
        canvas.saveState()
        canvas.setFont(F["r"], 8)
        canvas.setFillColor(CINZA)
        canvas.drawString(MARGEM_X, 1.25 * cm, texto[:95])
        canvas.setFillColor(MAGENTA)
        canvas.rect(w - MARGEM_X - 0.8 * cm, 0.95 * cm, 0.8 * cm, 0.8 * cm, stroke=0, fill=1)
        canvas.setFillColor(colors.white)
        canvas.setFont(F["b"], 12)
        canvas.drawCentredString(w - MARGEM_X - 0.4 * cm, 1.2 * cm, str(doc.page))
        canvas.restoreState()

    return rodape


# ---------------------------------------------------------------- conversão
def converter(md: str) -> tuple[list, dict]:
    linhas = md.splitlines()
    fl: list = []
    meta: dict = {}
    i = 0
    if linhas and linhas[0].strip() == "---":
        i = 1
        while i < len(linhas) and linhas[i].strip() != "---":
            if ":" in linhas[i]:
                k, v = linhas[i].split(":", 1)
                meta[k.strip().lower()] = v.strip()
            i += 1
        i += 1
    toc = TableOfContents()
    toc.levelStyles = [S["toc0"], S["toc1"]]
    toc.dotsMinLevel = 0
    fl += [Spacer(1, 1), PageBreak(), Paragraph("Sumário", S["sumario_t"]), toc, PageBreak()]

    paragrafo: list[str] = []
    titulo_tab = None

    def fechar():
        if paragrafo:
            fl.append(Paragraph(inline(" ".join(paragrafo)), S["corpo"]))
            paragrafo.clear()

    while i < len(linhas):
        s = linhas[i].strip()
        if not s:
            fechar(); i += 1; continue
        if s == "---":
            fechar(); fl.append(PageBreak()); i += 1; continue
        m = re.match(r"^(#{1,3})\s+(.*)", s)
        if m:
            fechar()
            n = len(m.group(1))
            fl.append(CondPageBreak(3.5 * cm))
            fl.append(Titulo(inline(m.group(2)), S[f"h{n}"], n - 1))
            i += 1; continue
        m = re.match(r"^\*\*((?:Quadro|Tabela) \d+\..*)\*\*$", s)
        if m and i + 1 < len(linhas) and linhas[i + 1].strip().startswith("|"):
            fechar(); titulo_tab = m.group(1); i += 1; continue
        if s.startswith("|"):
            fechar()
            bloco = []
            while i < len(linhas) and linhas[i].strip().startswith("|"):
                bloco.append(linhas[i]); i += 1
            fl += tabela(bloco, titulo_tab)
            titulo_tab = None
            continue
        if s.startswith(">"):
            fechar()
            bloco = []
            while i < len(linhas) and linhas[i].strip().startswith(">"):
                bloco.append(linhas[i].strip()[1:].strip()); i += 1
            m = re.match(r"^\[!(\w+)\]\s*(.*)", bloco[0])
            tipo = m.group(1).upper() if m else None
            if tipo in QUADROS:
                fl.append(quadro(tipo, [m.group(2)] + bloco[1:]))
            else:
                fl.append(enunciado(" ".join(bloco)))
            continue
        numerada = re.match(r"^(\d+)[.)]\s+", s)
        if numerada or re.match(r"^[-*]\s+", s):
            fechar()
            padrao = r"^\d+[.)]\s+" if numerada else r"^[-*]\s+"
            while i < len(linhas) and re.match(padrao, linhas[i].strip()):
                num = re.match(r"^(\d+)", linhas[i].strip())
                item = re.sub(padrao, "", linhas[i].strip()); i += 1
                while (i < len(linhas) and linhas[i].startswith(("  ", "\t")) and linhas[i].strip()
                       and not re.match(padrao, linhas[i].strip())):
                    item += " " + linhas[i].strip(); i += 1
                fl.append(Paragraph(inline(f"**{num.group(1)}.** {item}" if numerada else item), S["corpo"]))
            continue
        paragrafo.append(s)
        i += 1
    fechar()
    return fl, meta


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("markdown")
    ap.add_argument("--saida")
    args = ap.parse_args()
    origem = Path(args.markdown)
    if not origem.exists():
        sys.exit(f"ERRO: não encontrado: {origem}")
    md = origem.read_text(encoding="utf-8")
    ruins = [(n, l) for n, l in enumerate(md.splitlines(), 1) if "—" in l or "–" in l]
    if ruins:
        sys.exit("ERRO: travessão (— ou –) no texto. Troque por vírgula, dois-pontos ou parênteses:\n"
                 + "\n".join(f"  linha {n}: {l.strip()[:90]}" for n, l in ruins[:15]))
    saida = Path(args.saida) if args.saida else origem.with_suffix(".pdf")
    fl, meta = converter(md)
    doc = Documento(str(saida), pagesize=A4, leftMargin=MARGEM_X, rightMargin=MARGEM_X, topMargin=MARGEM_TOPO,
                    bottomMargin=MARGEM_BASE, title=meta.get("titulo", "Revisão dirigida"), author="Revisão em voz alta")
    rodape = rodape_factory(meta)
    doc.multiBuild(fl, onFirstPage=rodape, onLaterPages=rodape)
    print(f"PDF gerado: {saida}")


if __name__ == "__main__":
    main()
