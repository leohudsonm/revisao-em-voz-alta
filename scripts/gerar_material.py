#!/usr/bin/env python3
"""Gera o material de revisão em DOCX e PDF a partir do revisao.md.

Uso:
    python scripts/gerar_material.py sessoes/<sessão>/revisao.md

1. PDF: `scripts/gerar_pdf.py` (reportlab, com as fontes de assets/fonts). É o arquivo de leitura, fiel ao layout.
2. DOCX: `node scripts/gerar_docx.js` (biblioteca docx; instale uma vez com `npm install`), para quem quiser editar.
   Sem Node, o PDF é gerado mesmo assim e o script avisa.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent


def rodar(cmd: list[str]) -> bool:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    saida = (r.stdout or "").strip() or (r.stderr or "").strip()
    if saida:
        print(saida)
    return r.returncode == 0


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Uso: python scripts/gerar_material.py sessoes/<sessão>/revisao.md")
    md = Path(sys.argv[1]).resolve()
    if not md.exists():
        sys.exit(f"ERRO: não encontrado: {md}")

    pdf_ok = rodar([sys.executable, str(RAIZ / "scripts" / "gerar_pdf.py"), str(md), "--saida", str(md.with_suffix(".pdf"))])

    docx_ok = False
    if shutil.which("node"):
        docx_ok = rodar(["node", str(RAIZ / "scripts" / "gerar_docx.js"), str(md), str(md.with_suffix(".docx"))])
    else:
        print("AVISO: Node.js não encontrado; o DOCX não foi gerado (instale o Node e rode `npm install`).")

    if not (pdf_ok or docx_ok):
        sys.exit("ERRO: nenhum arquivo gerado. Instale as dependências (pip install -r requirements.txt; npm install).")


if __name__ == "__main__":
    main()
