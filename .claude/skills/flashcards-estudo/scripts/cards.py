#!/usr/bin/env python3
"""Flashcards de estudo pessoal (estilo Notion).

  cards.py validar  ARQ.tsv
  cards.py preview  ARQ.tsv [--titulo "..."]        -> ARQ.html e ARQ.pdf (Chrome/Edge headless)
  cards.py anki     ARQ.tsv --materia "Matéria" --assunto "Assunto" [--deck "..."] [--modelo "..."]

Baralho e tipo de nota: flags > `perfil.md` ("Baralho Anki", "Tipo de nota Anki") > padrão
("Revisão em voz alta::{materia}::{assunto}" e "Revisão em voz alta - Pergunta", criado se não existir).

`anki` fala direto com o add-on anki-mcp (http://127.0.0.1:3141/, ou ANKI_MCP_URL). Guarda os ids das notas em
ARQ.anki.json, alinhados às linhas do TSV: na primeira vez cria as notas; depois só atualiza os campos, então
editar a frente de um card no TSV e rodar de novo corrige a mesma nota (sem duplicar, sem perder o histórico).
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

MODELO_PADRAO = "Revisão em voz alta - Pergunta"
DECK_PADRAO = "Revisão em voz alta::{materia}::{assunto}"
CAMPOS = ["Pergunta", "Fundamento", "Matéria", "Assunto", "Identificação", "Mais"]
CSS_NOTA = ".card{font-family:-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;font-size:17px;color:#37352F;" \
           "background:#fff;text-align:left;max-width:720px;margin:0 auto;padding:12px;}"
WRAPPER = '<div style="font-family:-apple-system,'
RE_EMOJI = re.compile("[☀-➿\U0001F300-\U0001FAFF]")
RE_PEDE_NUMERO = re.compile(
    r"fundamentos?\s+lega(l|is)|qual\s+(o\s+)?(artigo|dispositivo|par[aá]grafo|inciso|al[ií]nea)|"
    r"(em|por)\s+qual\s+(artigo|dispositivo)|quais\s+(os\s+)?(artigos|dispositivos)|"
    r"(o\s+que|que)\s+(disp[õo]e|diz|estabelece|prev[eê])\s+(a|o)\s+(s[uú]mula|tema|art\.?|artigo|lei)\b|"
    r"qual\s+(a\s+)?s[uú]mula|qual\s+(o\s+)?tema\b|n[uú]mero\s+d[oa]\s+(artigo|s[uú]mula|lei|tema)",
    re.I,
)
RE_VAGA = re.compile(r"qual\s+(é\s+)?o\s+entendimento\s+(sobre|acerca)|^\s*(fale|explique|discorra)\b", re.I)
RE_PRESSUPOE = re.compile(r"^\s*(em\s+que\s+(condi[çc][õo]es?|hip[óo]teses?|casos?)|quando)\b.*\bpode", re.I)


def ler(tsv: Path) -> list[list[str]]:
    linhas = []
    for l in tsv.read_text(encoding="utf-8").splitlines():
        if l.strip() and not l.startswith("#"):
            partes = l.split("\t")
            if len(partes) != 3:
                sys.exit(f"linha com {len(partes)} colunas (esperado 3): {l[:80]}")
            linhas.append(partes)
    return linhas


def validar_card(n: int, frente: str, verso: str) -> tuple[list[str], list[str]]:
    e, a = [], []
    if "<" in frente or ">" in frente:
        e.append("frente com HTML")
    if RE_EMOJI.search(frente):
        e.append("frente com emoji")
    if RE_PEDE_NUMERO.search(frente):
        e.append("frente exige decorar número; pergunte o conteúdo")
    if RE_VAGA.search(frente):
        e.append("pergunta vaga (\"qual o entendimento sobre\", \"fale/explique\")")
    if RE_PRESSUPOE.search(frente):
        a.append("frente parece pressupor a resposta (\"em que condição ... pode\"); prefira \"X pode ...?\"")
    if len(frente) > 400:
        a.append(f"frente com {len(frente)} caracteres: é caso concreto? só se a resposta depender de reconhecer fatos")
    for campo, txt in (("frente", frente), ("verso", verso)):
        if "—" in txt or "–" in txt:
            e.append(f"travessão na {campo}")
    if not verso.startswith(WRAPPER) or not verso.rstrip().endswith("</div>"):
        e.append("verso sem o wrapper <div style=\"font-family:...\">...</div>")
    if '<hr style="' not in verso:
        e.append("verso sem <hr> após a resposta direta")
    if "background:#FDF3C0" not in verso:
        e.append("verso sem grifo amarelo")
    for tag in ("p", "ul", "ol", "li", "table"):
        if re.search(rf"<{tag}>", verso):
            e.append(f"<{tag}> sem style inline")
    if re.search(r"<strong>|<br>\s*<br>|background-color:\s*yellow", verso, re.I):
        e.append("marcação proibida (<strong>, <br><br> ou background-color: yellow)")
    grifos = re.findall(r'<span style="background:#FDF3C0[^"]*">(.*?)</span>', verso)
    if len(grifos) > 2:
        a.append(f"{len(grifos)} grifos amarelos (máx. 2)")
    for g in grifos:
        if len(re.sub(r"<[^>]+>", " ", g).split()) > 10:
            e.append("grifo amarelo longo demais (alvo 2 a 7 palavras)")
        if "<b>" not in g:
            e.append("grifo amarelo sem <b>")
    if len(re.findall(r"border-radius:6px;padding:10px 12px", verso)) > 1:
        e.append("mais de 1 callout")
    vis = len(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", verso)).strip())
    if vis > 2000:
        e.append(f"verso longo demais ({vis} caracteres visíveis)")
    elif vis < 300:
        a.append(f"verso curto ({vis} caracteres visíveis; alvo 500 a 1.500)")
    return [f"card {n}: {x}" for x in e], [f"card {n}: {x}" for x in a]


def cmd_validar(tsv: Path) -> bool:
    linhas = ler(tsv)
    erros, avisos = [], []
    frentes = set()
    for n, (f, v, _t) in enumerate(linhas, 1):
        e, a = validar_card(n, f, v)
        erros += e
        avisos += a
        if f in frentes:
            erros.append(f"card {n}: frente duplicada")
        frentes.add(f)
    for x in avisos:
        print("aviso:", x)
    for x in erros:
        print("ERRO:", x)
    print(f"{tsv.name}: {len(linhas)} cards · {len(erros)} erro(s) · {len(avisos)} aviso(s)")
    return not erros


# ---------- Anki (add-on anki-mcp via HTTP) ----------
URL = os.environ.get("ANKI_MCP_URL", "http://127.0.0.1:3141/")
_id = [0]


def _rpc(metodo, params):
    _id[0] += 1
    req = urllib.request.Request(
        URL, data=json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": metodo, "params": params}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    txt = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    dados = [json.loads(l[5:]) for l in txt.splitlines() if l.startswith("data:")] or [json.loads(txt)]
    return dados[-1]


def _tool(nome, args):
    r = _rpc("tools/call", {"name": nome, "arguments": args})
    if "error" in r:
        raise RuntimeError(r["error"])
    texto = "".join(c.get("text", "") for c in r["result"].get("content", []))
    if r["result"].get("isError"):
        raise RuntimeError(texto)
    return json.loads(texto) if texto.strip()[:1] in "{[" else texto


def ident(frente: str) -> str:
    h = hashlib.sha256(frente.encode("utf-8")).hexdigest()[:16]
    return "-".join(h[i:i + 4] for i in range(0, 16, 4))


def perfil(chave: str) -> str | None:
    """Lê "- **<chave>:** valor" do perfil.md mais próximo (diretório atual ou acima)."""
    for pasta in [Path.cwd(), *Path.cwd().parents]:
        arq = pasta / "perfil.md"
        if arq.exists():
            m = re.search(rf"\*\*{re.escape(chave)}:\*\*\s*([^<\n]+)", arq.read_text(encoding="utf-8"))
            return m.group(1).strip() if m and m.group(1).strip() else None
    return None


def garantir_modelo(modelo: str) -> None:
    nomes = _tool("model_names", {})
    nomes = nomes.get("modelNames", nomes) if isinstance(nomes, dict) else nomes
    if modelo in nomes:
        return
    if modelo != MODELO_PADRAO:
        sys.exit(f'tipo de nota "{modelo}" não existe no Anki; corrija o perfil.md ou use --modelo')
    _tool("create_model", {"model_name": modelo, "in_order_fields": CAMPOS, "css": CSS_NOTA, "card_templates": [
        {"Name": "Pergunta", "Front": "{{Pergunta}}", "Back": "{{FrontSide}}<hr id=answer>{{Fundamento}}"}]})
    print(f'tipo de nota "{modelo}" criado no Anki')


def cmd_anki(tsv: Path, materia: str, assunto: str, deck: str | None, modelo: str | None) -> None:
    if not cmd_validar(tsv):
        sys.exit("corrija os erros antes de enviar")
    deck = (deck or perfil("Baralho Anki") or DECK_PADRAO).format(materia=materia, assunto=assunto)
    modelo = modelo or perfil("Tipo de nota Anki") or MODELO_PADRAO
    linhas = ler(tsv)
    mapa_arq = tsv.with_suffix(".anki.json")
    mapa = json.loads(mapa_arq.read_text(encoding="utf-8")) if mapa_arq.exists() else {"deck": deck, "ids": []}
    try:
        _rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                            "clientInfo": {"name": "flashcards-estudo", "version": "1"}})
    except OSError:
        sys.exit(f"Anki fechado ou add-on anki-mcp fora do ar ({URL}). Abra o Anki e rode de novo, ou importe o TSV "
                 "à mão: Arquivo > Importar, separador Tab, permitir HTML, campo 3 = Tags.")
    garantir_modelo(modelo)
    try:
        _tool("create_deck", {"deck_name": deck})
    except RuntimeError as e:
        if "exist" not in str(e).lower():
            raise
    ids = mapa["ids"]
    novos = 0
    for i, (f, v, tags) in enumerate(linhas):
        campos = {"Pergunta": f, "Fundamento": v, "Identificação": ident(f)}
        if i < len(ids) and ids[i]:
            _tool("update_note_fields", {"id": ids[i], "fields": campos})
            continue
        r = _tool("add_notes", {"deck_name": deck, "model_name": modelo, "tags": tags.split(),
                                "notes": [{"fields": {**campos, "Matéria": materia, "Assunto": assunto, "Mais": ""}}]})
        nid = (r.get("results") or [{}])[0].get("note_id")
        if not nid:
            sys.exit(f"card {i + 1} não foi criado: {r}")
        ids.append(nid) if i >= len(ids) else ids.__setitem__(i, nid)
        novos += 1
    mapa.update(deck=deck, ids=ids)
    mapa_arq.write_text(json.dumps(mapa, ensure_ascii=False, indent=1), encoding="utf-8")
    info = _tool("notes_info", {"notes": ids[:len(linhas)]})
    ok = sum(1 for n, (f, v, _t) in zip(info["notes"], linhas)
             if n["fields"]["Pergunta"]["value"] == f and n["fields"]["Fundamento"]["value"] == v)
    print(f"Anki: {novos} criado(s), {len(linhas) - novos} atualizado(s) · {ok}/{len(linhas)} idênticos ao TSV · deck {deck}")
    if len(ids) > len(linhas):
        print(f"aviso: {len(ids) - len(linhas)} nota(s) antigas além do fim do TSV continuam no Anki (ids {ids[len(linhas):]})")


# ---------- Preview em PDF ----------
CSS = """@page{size:A4;margin:14mm 12mm 16mm}body{font-family:'Segoe UI',Helvetica,Arial,sans-serif;color:#1F1F1F;margin:0}
header{border-bottom:3px solid #B62CA2;padding-bottom:10px;margin-bottom:16px}h1{font-size:22px;color:#00673A;margin:0 0 4px}header p{margin:0;color:#5F6368;font-size:12px}
.card{border:1px solid #E4E6E8;border-radius:8px;padding:14px 16px 10px;margin:0 0 14px;break-inside:avoid}
.num{display:inline-block;background:#B62CA2;color:#fff;font-size:11px;font-weight:600;padding:2px 8px;border-radius:10px;margin-bottom:10px}
.lado{margin-bottom:10px}.rot{font-size:10px;letter-spacing:.09em;text-transform:uppercase;font-weight:700;margin-bottom:4px}.rot-f{color:#00673A}.rot-v{color:#B62CA2}
.frente{font-size:15px;line-height:1.5}.verso{border-left:3px solid #E9E9E7;padding-left:12px}.tags{font-size:10px;color:#8A8F94;border-top:1px dashed #EFEFEF;padding-top:6px}"""


def cmd_preview(tsv: Path, titulo: str | None) -> None:
    linhas = ler(tsv)
    titulo = titulo or tsv.stem
    cards = "".join(
        f'<section class="card"><span class="num">Card {n:02d}</span>'
        f'<div class="lado"><div class="rot rot-f">Frente</div><div class="frente">{html.escape(f, quote=False)}</div></div>'
        f'<div class="lado"><div class="rot rot-v">Verso</div><div class="verso">{v}</div></div>'
        f'<div class="tags">{html.escape(t)}</div></section>'
        for n, (f, v, t) in enumerate(linhas, 1))
    doc = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{html.escape(titulo)}</title>'
           f'<style>{CSS}</style></head><body><header><h1>{html.escape(titulo)}</h1><p>{len(linhas)} cards</p></header>'
           f'{cards}</body></html>')
    arq_html = tsv.with_suffix(".html")
    arq_html.write_text(doc, encoding="utf-8")
    arq_pdf = tsv.with_suffix(".pdf")
    for nav in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "google-chrome", "chromium"):
        try:
            subprocess.run([nav, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            f"--print-to-pdf={arq_pdf.resolve()}", arq_html.resolve().as_uri()],
                           check=True, capture_output=True, timeout=120)
            print(f"preview: {arq_html.name} e {arq_pdf.name}")
            return
        except (OSError, subprocess.SubprocessError):
            continue
    print(f"preview: {arq_html.name} (sem Chrome/Edge para gerar o PDF)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validar"); v.add_argument("tsv", type=Path)
    a = sub.add_parser("anki"); a.add_argument("tsv", type=Path)
    a.add_argument("--materia", required=True); a.add_argument("--assunto", required=True)
    a.add_argument("--deck"); a.add_argument("--modelo")
    p = sub.add_parser("preview"); p.add_argument("tsv", type=Path); p.add_argument("--titulo")
    args = ap.parse_args()
    if args.cmd == "validar":
        sys.exit(0 if cmd_validar(args.tsv) else 1)
    if args.cmd == "anki":
        cmd_anki(args.tsv, args.materia, args.assunto, args.deck, args.modelo)
    else:
        cmd_preview(args.tsv, args.titulo)


if __name__ == "__main__":
    main()
