#!/usr/bin/env python3
"""Processa um material de estudo UMA VEZ, para que as sessões leiam só o necessário.

Uso:
    python scripts/extrair_material.py CAMINHO_DO_ARQUIVO [--slug nome-curto]

Gera em materiais/<slug>/:
    original.<ext>   cópia do arquivo
    texto.md         texto integral, com marcadores de página  <!-- p. N -->
    indice.md        ESBOÇO do índice: títulos candidatos com página e LINHA do texto.md.
                     O Claude revisa o esboço e o transforma no mapa de tópicos definitivo.

Formatos: .pdf (pypdf), .docx (python-docx), .txt, .md.
PDF escaneado (sem camada de texto) é detectado e informado: nesse caso, leia o PDF
diretamente com o Claude (páginas) ou passe OCR antes.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
MATERIAIS = RAIZ / "materiais"

RE_NUMERADO = re.compile(r"^(\d{1,2}(\.\d{1,2}){0,3}\.?|[IVXLC]{1,6}[.\-–)]|[A-Z][).])\s+\S")
RE_PALAVRA_CHAVE = re.compile(r"^(cap[íi]tulo|t[íi]tulo|se[çc][ãa]o|parte|m[óo]dulo|aula|tema|unidade)\b", re.I)


def slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()[:60] or "material"


def extrair_pdf(caminho: Path) -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.exit("ERRO: instale as dependências: pip install -r requirements.txt")
    leitor = PdfReader(str(caminho))
    return [(pg.extract_text() or "") for pg in leitor.pages]


def extrair_docx(caminho: Path) -> list[str]:
    try:
        import docx
    except ImportError:
        sys.exit("ERRO: instale as dependências: pip install -r requirements.txt")
    d = docx.Document(str(caminho))
    linhas = []
    for par in d.paragraphs:
        txt = par.text.strip()
        if not txt:
            continue
        estilo = (par.style.name or "").lower() if par.style is not None else ""
        m = re.search(r"(heading|t[íi]tulo)\s*(\d)", estilo)
        linhas.append(f"{'#' * min(int(m.group(2)) + 1, 4)} {txt}" if m else txt)
    return ["\n".join(linhas)]


def eh_titulo(linha: str) -> bool:
    s = linha.strip()
    if not (3 <= len(s) <= 90) or s.endswith((",", ";")):
        return False
    if s.startswith("#"):
        return True
    letras = [c for c in s if c.isalpha()]
    caixa_alta = len(letras) >= 4 and sum(c.isupper() for c in letras) / len(letras) > 0.85
    return bool(caixa_alta or RE_NUMERADO.match(s) or RE_PALAVRA_CHAVE.match(s))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arquivo")
    ap.add_argument("--slug")
    args = ap.parse_args()

    origem = Path(args.arquivo).expanduser().resolve()
    if not origem.exists():
        sys.exit(f"ERRO: arquivo não encontrado: {origem}")
    ext = origem.suffix.lower()
    destino = MATERIAIS / (args.slug or slug(origem.stem))
    destino.mkdir(parents=True, exist_ok=True)

    if ext == ".pdf":
        paginas = extrair_pdf(origem)
    elif ext == ".docx":
        paginas = extrair_docx(origem)
    elif ext in (".txt", ".md"):
        paginas = [origem.read_text(encoding="utf-8", errors="replace")]
    else:
        sys.exit("ERRO: formato não suportado (use .pdf, .docx, .txt ou .md)")

    copia = destino / f"original{ext}"
    if origem != copia.resolve():
        shutil.copy2(origem, copia)

    linhas_texto: list[str] = [f"# {origem.stem}", ""]
    candidatos: list[tuple[int, int, str]] = []
    for i, conteudo in enumerate(paginas, start=1):
        if len(paginas) > 1:
            linhas_texto += [f"<!-- p. {i} -->"]
        for linha in conteudo.splitlines():
            linha = linha.rstrip()
            linhas_texto.append(linha)
            if eh_titulo(linha):
                candidatos.append((i, len(linhas_texto), linha.strip().lstrip("# ")))
        linhas_texto.append("")

    (destino / "texto.md").write_text("\n".join(linhas_texto), encoding="utf-8")

    total_chars = sum(len(p) for p in paginas)
    palavras = sum(len(p.split()) for p in paginas)
    escaneado = ext == ".pdf" and total_chars / max(len(paginas), 1) < 200

    idx = [
        f"# Índice — {origem.stem}",
        "",
        "> ESBOÇO GERADO AUTOMATICAMENTE. O Claude deve substituir esta seção pelo mapa de tópicos",
        "> definitivo (formato abaixo) e apagar esta nota.",
        "",
        f"- Arquivo: `{copia.name}` · páginas: {len(paginas)} · palavras: {palavras} · "
        f"tokens estimados do texto integral: ~{int(palavras * 1.6)}",
        "- Texto integral: `texto.md` (leia só as linhas do tópico da vez, com offset/limit).",
        "",
        "## Formato do mapa definitivo",
        "| # | Disciplina | Tópico | Subtópicos-chave | Linhas em texto.md | Importância (1-3) |",
        "|---|---|---|---|---|---|",
        "",
        "## Títulos candidatos detectados (página · linha · texto)",
    ]
    idx += [f"- p. {p} · L{l} · {t}" for p, l, t in candidatos[:400]] or ["- nenhum título detectado"]
    if len(candidatos) > 400:
        idx.append(f"- … +{len(candidatos) - 400} candidatos omitidos")
    (destino / "indice.md").write_text("\n".join(idx) + "\n", encoding="utf-8")

    print(f"material: materiais/{destino.name}")
    print(f"páginas: {len(paginas)} · palavras: {palavras} · títulos candidatos: {len(candidatos)}")
    if escaneado:
        print("AVISO: pouquíssimo texto por página — PDF provavelmente escaneado. "
              "Leia o original direto pelo Claude (por páginas) ou aplique OCR.")


if __name__ == "__main__":
    main()
