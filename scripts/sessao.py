#!/usr/bin/env python3
"""Gerencia sessões e desempenho do projeto "Revisão em voz alta".

A fonte da verdade do desempenho é `desempenho/estado.json`, que só este script lê e escreve.
A partir dele são gerados os arquivos que o Claude lê, curtos e de tamanho limitado:

    desempenho/painel.md                         (lido na abertura de toda sessão)
    desempenho/topicos/<disciplina>/<topico>.md  (lido só quando o tópico entra na sessão)
    desempenho/arquivo.md                        (tópicos dominados e antigos; não é lido na abertura)

Comandos:
    abrir                         resumo de abertura: perfil, pendências, revisões vencidas, painel
    nova --modo M --tema T [--material SLUG]   cria sessoes/AAAA-MM-DD_<tema>/
    registrar SESSAO [--json J | --arquivo F]  acrescenta pergunta(s) corrigida(s) (JSON via stdin, --json ou arquivo)
    metricas SESSAO [--pontos]    métricas da sessão por tópico, com nível anterior e projeção
    consolidar SESSAO             atualiza estado.json e regenera painel e arquivos de tópico
    cards SESSAO                  remove flashcards duplicados do TSV e registra os novos
    topico DISCIPLINA TOPICO      mostra o arquivo de detalhe do tópico
    exportar [--exemplo]          gera dashboard/dados.js (ou dados.exemplo.js) para o dashboard
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
SESSOES = RAIZ / "sessoes"
MATERIAIS = RAIZ / "materiais"
DESEMP = RAIZ / "desempenho"
ESTADO = DESEMP / "estado.json"
PAINEL = DESEMP / "painel.md"
ARQUIVO = DESEMP / "arquivo.md"
TOPICOS = DESEMP / "topicos"

LIMITE_LINHAS_PAINEL = 80
DIAS_PARA_ARQUIVAR = 60
MAX_HISTORICO = 10
MAX_LACUNAS_ABERTAS = 12
MAX_SUPERADAS = 5
MAX_ERROS = 8
PALAVRAS_LACUNA_CHAVE = 12

NOTA_OBJETIVA = {"certeza": 10.0, "duvida": 6.0, "chute": 2.0}


# ---------------------------------------------------------------- utilitários
def hoje() -> str:
    return dt.date.today().isoformat()


def slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t or "sem-nome"


def chave(disciplina: str, topico: str) -> str:
    return f"{slug(disciplina)}::{slug(topico)}"


STOPWORDS = set("a o as os de da do das dos e em no na nos nas um uma uns umas por para com sem que se ao aos "
                "ou é e sua seu suas seus pelo pela pelos pelas como mais menos entre sobre".split())


def termos(texto: str) -> set[str]:
    return {w[:6] for w in slug(texto).split("-") if w and w not in STOPWORDS}


def mesmo_texto(a: str, b: str) -> bool:
    """Equivalência tolerante a paráfrases curtas (mesmos termos-chave, em qualquer ordem)."""
    sa, sb = slug(a), slug(b)
    if sa == sb or (len(sa) > 15 and sa in sb) or (len(sb) > 15 and sb in sa):
        return True
    ta, tb = termos(a), termos(b)
    if len(ta) < 3 or len(tb) < 3:
        return False
    return len(ta & tb) / len(ta | tb) >= 0.6


def erro(msg: str) -> None:
    print(f"ERRO: {msg}", file=sys.stderr)
    sys.exit(1)


def ler_json(caminho: Path, padrao):
    if not caminho.exists():
        return padrao
    return json.loads(caminho.read_text(encoding="utf-8"))


def gravar_json(caminho: Path, dados) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def carregar_estado() -> dict:
    return ler_json(ESTADO, {"versao": 1, "topicos": {}, "sessoes_consolidadas": []})


def pasta_sessao(arg: str) -> Path:
    p = Path(arg)
    if not p.is_absolute():
        p = (SESSOES / arg) if (SESSOES / arg).exists() else (RAIZ / arg)
    if not (p / "meta.json").exists():
        erro(f"sessão não encontrada (sem meta.json): {arg}")
    return p


def ler_registros(pasta: Path) -> list[dict]:
    arq = pasta / "sessao.jsonl"
    if not arq.exists():
        return []
    return [json.loads(l) for l in arq.read_text(encoding="utf-8").splitlines() if l.strip()]


def data_sessao(meta: dict) -> str:
    return (meta.get("criada_em") or hoje())[:10]


def somar_dias(data_iso: str, dias: int) -> str:
    return (dt.date.fromisoformat(data_iso) + dt.timedelta(days=dias)).isoformat()


def media(valores: list[float]) -> float | None:
    return round(sum(valores) / len(valores), 1) if valores else None


# ---------------------------------------------------------------- regras de desempenho
def normalizar_certeza(c: str) -> str:
    c = slug(c)
    if c.startswith("cert"):
        return "certeza"
    if c.startswith("duv"):
        return "duvida"
    if c.startswith("chu"):
        return "chute"
    erro(f"certeza inválida: {c!r} (use certeza | duvida | chute)")
    return ""


def nota_do_registro(r: dict) -> float:
    return float(r["nota"])


def dias_ate_proxima(nota_sessao: float, historico: list[dict]) -> int:
    if nota_sessao < 5:
        return 1
    if nota_sessao < 7:
        return 3
    if nota_sessao < 9:
        return 7
    anterior = historico[-2]["nota"] if len(historico) >= 2 else None
    return 21 if anterior is not None and anterior >= 9 else 7


def tendencia(nota_sessao: float, nivel_anterior: float | None) -> str:
    if nivel_anterior is None:
        return "novo"
    d = nota_sessao - nivel_anterior
    return "↑" if d >= 0.5 else "↓" if d <= -0.5 else "="


def novo_nivel(nota_sessao: float, nivel_anterior: float | None) -> float:
    if nivel_anterior is None:
        return round(nota_sessao, 1)
    return round(0.6 * nota_sessao + 0.4 * nivel_anterior, 1)


def lacuna_chave(t: dict) -> str:
    abertas = sorted(t["lacunas_abertas"], key=lambda l: (-l.get("importancia", 1), -l.get("vezes", 1)))
    if not abertas:
        return "—"
    palavras = abertas[0]["texto"].split()
    txt = " ".join(palavras[:PALAVRAS_LACUNA_CHAVE])
    return txt + ("…" if len(palavras) > PALAVRAS_LACUNA_CHAVE else "")


# ---------------------------------------------------------------- renderização
def celula(txt) -> str:
    return str(txt).replace("|", "/").replace("\n", " ")


def render_painel(estado: dict) -> None:
    ativos = [t for t in estado["topicos"].values() if not t.get("arquivado")]
    arquivados = [t for t in estado["topicos"].values() if t.get("arquivado")]
    ativos.sort(key=lambda t: (t["proxima"], t["nivel"]))
    ref = hoje()

    cab = [
        "# Painel de desempenho",
        f"_Gerado por `scripts/sessao.py` em {ref}. Não editar à mão. "
        "Detalhe de cada tópico: `python scripts/sessao.py topico \"<disciplina>\" \"<tópico>\"`._",
        "",
        f"Tópicos ativos: {len(ativos)} · Arquivados (dominados): {len(arquivados)} · "
        f"Sessões consolidadas: {len(estado['sessoes_consolidadas'])} · "
        f"Revisões vencidas: {sum(1 for t in ativos if t['proxima'] <= ref)}",
        "",
        "| Disciplina | Tópico | Nível | Tend. | Última | Próxima | Lacuna-chave |",
        "|---|---|---|---|---|---|---|",
    ]
    vagas = LIMITE_LINHAS_PAINEL - len(cab) - 2
    linhas = []
    for t in ativos[:vagas]:
        prox = f"**{t['proxima']}**" if t["proxima"] <= ref else t["proxima"]
        linhas.append(
            f"| {celula(t['disciplina'])} | {celula(t['topico'])} | {t['nivel']:.1f} | {t['tendencia']} "
            f"| {t['ultima']} | {prox} | {celula(lacuna_chave(t))} |"
        )
    rodape = []
    if len(ativos) > vagas:
        rodape = ["", f"_+{len(ativos) - vagas} tópicos menos urgentes omitidos para manter o painel curto._"]
    DESEMP.mkdir(parents=True, exist_ok=True)
    PAINEL.write_text("\n".join(cab + linhas + rodape) + "\n", encoding="utf-8")

    arq = ["# Arquivo: tópicos dominados", "_Nível ≥ 9 e sem revisão há mais de "
           f"{DIAS_PARA_ARQUIVAR} dias. Voltam ao painel automaticamente se forem revisados._", ""]
    for t in sorted(arquivados, key=lambda t: (t["disciplina"], t["topico"])):
        arq.append(f"- {t['disciplina']} · {t['topico']} · nível {t['nivel']:.1f} · última {t['ultima']}")
    ARQUIVO.write_text("\n".join(arq) + "\n", encoding="utf-8")


def caminho_topico(t: dict) -> Path:
    return TOPICOS / slug(t["disciplina"]) / f"{slug(t['topico'])}.md"


def render_topico(t: dict) -> None:
    notas = " | ".join(f"{h['data']}: {h['nota']:.1f} ({h['modo'][:4]})" for h in t["historico"][-5:])
    L = [
        f"# {t['topico']} — {t['disciplina']}",
        "_Gerado por `scripts/sessao.py`. Não editar à mão._",
        "",
        f"- Nível: {t['nivel']:.1f} ({t['tendencia']}) · Sessões: {t['sessoes']} · "
        f"Última: {t['ultima']} · Próxima: {t['proxima']}",
        f"- Últimas notas: {notas or '—'}",
        "",
        "## Lacunas abertas (perguntar de novo; copie o texto exato em `lacunas_superadas` quando o ponto for entregue)",
    ]
    abertas = sorted(t["lacunas_abertas"], key=lambda l: (-l.get("importancia", 1), -l.get("vezes", 1)))
    L += [f"- [imp {l.get('importancia', 1)} · {l.get('vezes', 1)}x] {l['texto']}" for l in abertas] or ["- nenhuma"]
    L += ["", "## Erros conceituais já cometidos"]
    L += [f"- ({e['data']}) {e['texto']}" for e in t["erros_conceituais"]] or ["- nenhum"]
    L += ["", "## Lacunas superadas recentemente"]
    L += [f"- ({s['data']}) {s['texto']}" for s in t["lacunas_superadas"]] or ["- nenhuma"]
    L += ["", f"## Flashcards já gerados ({len(t['cards'])}) — não repetir"]
    L += [f"- {c['frente'][:90]}" for c in t["cards"]] or ["- nenhum"]
    p = caminho_topico(t)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(L) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- comandos
def cmd_abrir(_args) -> None:
    ref = hoje()
    print(f"# Abertura — {ref}")
    perfil = RAIZ / "perfil.md"
    print(f"- Perfil: {'OK (perfil.md)' if perfil.exists() else 'AUSENTE → fazer onboarding e criar perfil.md a partir de perfil.exemplo.md'}")

    pendentes = []
    if SESSOES.exists():
        for m in sorted(SESSOES.glob("*/meta.json")):
            meta = ler_json(m, {})
            if not meta.get("consolidada"):
                n = len(ler_registros(m.parent))
                pendentes.append(f"{m.parent.name} ({n} registros)")
    print(f"- Sessões não consolidadas: {', '.join(pendentes) if pendentes else 'nenhuma'}")
    if pendentes:
        print("  → rodar `python scripts/sessao.py consolidar <sessão>` em cada uma ANTES de começar "
              "(sessões com 0 registros podem ser apagadas).")

    mats = []
    if MATERIAIS.exists():
        for d in sorted(p for p in MATERIAIS.iterdir() if p.is_dir()):
            idx = d / "indice.md"
            mats.append(f"{d.name} (índice: {'sim' if idx.exists() else 'NÃO'})")
    print(f"- Materiais processados: {', '.join(mats) if mats else 'nenhum'}")

    estado = carregar_estado()
    vencidas = [t for t in estado["topicos"].values() if not t.get("arquivado") and t["proxima"] <= ref]
    vencidas.sort(key=lambda t: (t["proxima"], t["nivel"]))
    if vencidas:
        print(f"- Revisões vencidas ({len(vencidas)}): " + "; ".join(
            f"{t['disciplina']} · {t['topico']} (nível {t['nivel']:.1f})" for t in vencidas[:10]))
    else:
        print("- Revisões vencidas: nenhuma")
    print()
    print(PAINEL.read_text(encoding="utf-8") if PAINEL.exists() else "_Sem histórico ainda: primeira sessão._")


def cmd_nova(args) -> None:
    if args.modo not in {"discursiva", "objetiva", "mista"}:
        erro("modo deve ser discursiva | objetiva | mista")
    base = f"{hoje()}_{slug(args.tema)[:50]}"
    pasta, i = SESSOES / base, 2
    while pasta.exists():
        pasta, i = SESSOES / f"{base}-{i}", i + 1
    pasta.mkdir(parents=True)
    meta = {
        "id": pasta.name,
        "criada_em": dt.datetime.now().isoformat(timespec="seconds"),
        "modo": args.modo,
        "tema": args.tema,
        "material": args.material,
        "consolidada": False,
        "consolidada_em": None,
    }
    gravar_json(pasta / "meta.json", meta)
    (pasta / "sessao.jsonl").touch()
    print(f"sessão criada: sessoes/{pasta.name}")


def validar_registro(r: dict) -> dict:
    for campo in ("tipo", "disciplina", "topico", "pergunta"):
        if not str(r.get(campo, "")).strip():
            erro(f"campo obrigatório ausente: {campo}")
    r.setdefault("lacunas", [])
    r.setdefault("lacunas_superadas", [])
    r.setdefault("erros_conceituais", [])
    r["importancia"] = int(r.get("importancia", 2))
    if r["importancia"] not in (1, 2, 3):
        erro("importancia deve ser 1, 2 ou 3")
    for campo in ("lacunas", "lacunas_superadas", "erros_conceituais"):
        if not isinstance(r[campo], list):
            erro(f"{campo} deve ser uma lista de textos")
    if r["tipo"] == "discursiva":
        if "nota" not in r:
            erro("discursiva exige 'nota' (0 a 10)")
        r["nota"] = float(r["nota"])
        if not 0 <= r["nota"] <= 10:
            erro("nota fora de 0..10")
        r.setdefault("pontos", [])
    elif r["tipo"] == "objetiva":
        for campo in ("resposta", "gabarito", "certeza"):
            if not str(r.get(campo, "")).strip():
                erro(f"objetiva exige '{campo}'")
        r["certeza"] = normalizar_certeza(r["certeza"])
        r["acertou"] = slug(r["resposta"]) == slug(r["gabarito"])
        r["nota"] = NOTA_OBJETIVA[r["certeza"]] if r["acertou"] else 0.0
    else:
        erro("tipo deve ser discursiva | objetiva")
    return r


def cmd_registrar(args) -> None:
    pasta = pasta_sessao(args.sessao)
    if args.arquivo:
        bruto = Path(args.arquivo).read_text(encoding="utf-8")
    else:
        bruto = args.json if args.json else sys.stdin.read()
    try:
        dados = json.loads(bruto)
    except json.JSONDecodeError as e:
        erro(f"JSON inválido: {e}")
    itens = dados if isinstance(dados, list) else [dados]
    arq = pasta / "sessao.jsonl"
    n = len(ler_registros(pasta))
    with arq.open("a", encoding="utf-8") as f:
        for r in itens:
            r = validar_registro(r)
            n += 1
            r["n"] = n
            r["registrado_em"] = dt.datetime.now().isoformat(timespec="seconds")
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            extra = f" · {'acertou' if r['acertou'] else 'errou'} ({r['certeza']})" if r["tipo"] == "objetiva" else ""
            print(f"registrado #{n}: {r['disciplina']} · {r['topico']} · nota {r['nota']:.1f}{extra}")


def agrupar(registros: list[dict]) -> dict[str, list[dict]]:
    grupos: dict[str, list[dict]] = {}
    for r in registros:
        grupos.setdefault(chave(r["disciplina"], r["topico"]), []).append(r)
    return grupos


def cmd_metricas(args) -> None:
    pasta = pasta_sessao(args.sessao)
    meta = ler_json(pasta / "meta.json", {})
    regs = ler_registros(pasta)
    if not regs:
        erro("sessão sem registros")
    estado = carregar_estado()
    print(f"# Métricas — {meta['id']} ({meta['modo']}, tema: {meta['tema']})")
    notas = [r["nota"] for r in regs]
    print(f"- Perguntas: {len(regs)} · Nota média geral: {media(notas)}")
    obj = [r for r in regs if r["tipo"] == "objetiva"]
    if obj:
        chutes = sum(1 for r in obj if r["acertou"] and r["certeza"] == "chute")
        print(f"- Objetivas: {sum(r['acertou'] for r in obj)}/{len(obj)} acertos · acertos por chute: {chutes}")
        tipos: dict[str, int] = {}
        for r in obj:
            if r.get("tipo_erro"):
                tipos[r["tipo_erro"]] = tipos.get(r["tipo_erro"], 0) + 1
        if tipos:
            print("- Tipos de erro: " + ", ".join(f"{k}: {v}" for k, v in tipos.items()))
    resumo = []
    for k, rs in agrupar(regs).items():
        ns = media([r["nota"] for r in rs])
        ant = estado["topicos"].get(k, {}).get("nivel")
        resumo.append((ns, k, rs, ant))
    resumo.sort(key=lambda x: x[0])
    print("\n## Por tópico (pior → melhor)")
    for ns, k, rs, ant in resumo:
        d, t = rs[0]["disciplina"], rs[0]["topico"]
        print(f"\n### {d} · {t}")
        print(f"- Nota da sessão: {ns} · nível anterior: {ant if ant is not None else '—'} · "
              f"nível após consolidar: {novo_nivel(ns, ant)} · tendência: {tendencia(ns, ant)}")
        for r in rs:
            lac = "; ".join(r["lacunas"]) or "—"
            print(f"- #{r['n']} [{r['tipo'][:4]} · imp {r['importancia']} · nota {r['nota']:.1f}] {r['pergunta'][:110]}")
            if getattr(args, "pontos", False):
                if r["tipo"] == "objetiva":
                    print(f"  resposta {r['resposta']} ({r['certeza']}) · gabarito {r['gabarito']} · "
                          f"{'acertou' if r['acertou'] else 'errou'}{' · ' + r['tipo_erro'] if r.get('tipo_erro') else ''}")
                for p in r.get("pontos", []):
                    print(f"  [{p.get('status', '?')}] ({p.get('peso', '?')}) {p.get('ponto', '')}")
            print(f"  lacunas: {lac}")
            if r["erros_conceituais"]:
                print(f"  ERROS CONCEITUAIS: {'; '.join(r['erros_conceituais'])}")
            if r["lacunas_superadas"]:
                print(f"  superou: {'; '.join(r['lacunas_superadas'])}")
    print("\n## Prioridade de lacunas (importância × déficit × recorrência)")
    prio = []
    for r in regs:
        for lac in r["lacunas"]:
            t = estado["topicos"].get(chave(r["disciplina"], r["topico"]), {})
            vezes = 1 + sum(1 for l in t.get("lacunas_abertas", []) if mesmo_texto(l["texto"], lac))
            score = r["importancia"] * (10 - r["nota"]) * vezes
            prio.append((score, vezes, r, lac))
    prio.sort(key=lambda x: -x[0])
    for score, vezes, r, lac in prio[:15]:
        rec = f" · recorrente ({vezes}x)" if vezes > 1 else ""
        print(f"- [{score:.0f}] {r['disciplina']} · {r['topico']}: {lac}{rec}")
    if not prio:
        print("- nenhuma lacuna registrada")


def cmd_consolidar(args) -> None:
    pasta = pasta_sessao(args.sessao)
    meta = ler_json(pasta / "meta.json", {})
    estado = carregar_estado()
    if meta["id"] in estado["sessoes_consolidadas"]:
        print(f"sessão {meta['id']} já consolidada; nada a fazer.")
        return
    regs = ler_registros(pasta)
    if not regs:
        erro("sessão sem registros; nada a consolidar (pode apagar a pasta)")
    data = data_sessao(meta)

    for k, rs in agrupar(regs).items():
        ns = media([r["nota"] for r in rs])
        t = estado["topicos"].get(k) or {
            "disciplina": rs[0]["disciplina"], "topico": rs[0]["topico"], "nivel": None, "tendencia": "novo",
            "sessoes": 0, "ultima": data, "proxima": data, "historico": [], "lacunas_abertas": [],
            "lacunas_superadas": [], "erros_conceituais": [], "cards": [], "arquivado": False,
        }
        ant = t["nivel"]
        t["tendencia"] = tendencia(ns, ant)
        t["nivel"] = novo_nivel(ns, ant)
        t["sessoes"] += 1
        t["ultima"] = data
        t["arquivado"] = False
        tipos = {r["tipo"] for r in rs}
        modo = tipos.pop() if len(tipos) == 1 else "mista"
        t["historico"] = (t["historico"] + [{"data": data, "nota": ns, "modo": modo, "sessao": meta["id"]}])[-MAX_HISTORICO:]
        t["proxima"] = somar_dias(data, dias_ate_proxima(ns, t["historico"]))

        for r in rs:
            for sup in r["lacunas_superadas"]:
                antes = len(t["lacunas_abertas"])
                t["lacunas_abertas"] = [l for l in t["lacunas_abertas"] if not mesmo_texto(l["texto"], sup)]
                if len(t["lacunas_abertas"]) < antes:
                    t["lacunas_superadas"].append({"texto": sup, "data": data})
            for lac in r["lacunas"]:
                existente = next((l for l in t["lacunas_abertas"] if mesmo_texto(l["texto"], lac)), None)
                if existente:
                    existente["vezes"] = existente.get("vezes", 1) + 1
                    existente["importancia"] = max(existente.get("importancia", 1), r["importancia"])
                    existente["texto"] = lac
                else:
                    t["lacunas_abertas"].append({"texto": lac, "desde": data, "vezes": 1, "importancia": r["importancia"]})
            for e in r["erros_conceituais"]:
                if not any(mesmo_texto(x["texto"], e) for x in t["erros_conceituais"]):
                    t["erros_conceituais"].append({"texto": e, "data": data})

        if len(t["lacunas_abertas"]) > MAX_LACUNAS_ABERTAS:
            t["lacunas_abertas"].sort(key=lambda l: (-l.get("importancia", 1), -l.get("vezes", 1), l.get("desde", "")))
            t["lacunas_abertas"] = t["lacunas_abertas"][:MAX_LACUNAS_ABERTAS]
        t["lacunas_superadas"] = t["lacunas_superadas"][-MAX_SUPERADAS:]
        t["erros_conceituais"] = t["erros_conceituais"][-MAX_ERROS:]
        estado["topicos"][k] = t

    limite = somar_dias(hoje(), -DIAS_PARA_ARQUIVAR)
    for t in estado["topicos"].values():
        if t["nivel"] >= 9 and t["ultima"] < limite:
            t["arquivado"] = True

    estado["sessoes_consolidadas"].append(meta["id"])
    gravar_json(ESTADO, estado)
    render_painel(estado)
    for k in agrupar(regs):
        render_topico(estado["topicos"][k])
    meta["consolidada"] = True
    meta["consolidada_em"] = dt.datetime.now().isoformat(timespec="seconds")
    gravar_json(pasta / "meta.json", meta)

    print(f"consolidada: {meta['id']}")
    for k in agrupar(regs):
        t = estado["topicos"][k]
        print(f"- {t['disciplina']} · {t['topico']}: nível {t['nivel']:.1f} ({t['tendencia']}) · próxima {t['proxima']}")
    n_linhas = len(PAINEL.read_text(encoding="utf-8").splitlines())
    print(f"painel.md: {n_linhas} linhas (limite {LIMITE_LINHAS_PAINEL})")
    print(f"dashboard: {exportar().relative_to(RAIZ).as_posix()} atualizado")


def cmd_cards(args) -> None:
    pasta = pasta_sessao(args.sessao)
    tsv = pasta / "flashcards.tsv"
    if not tsv.exists():
        erro("flashcards.tsv não encontrado na sessão")
    estado = carregar_estado()
    manter, duplicados, sem_topico = [], [], []
    tocados = set()
    for linha in tsv.read_text(encoding="utf-8").splitlines():
        if not linha.strip() or linha.startswith("#"):
            manter.append(linha)
            continue
        partes = linha.split("\t")
        if len(partes) < 3:
            erro(f"linha sem 3 colunas (frente, verso, tags): {linha[:80]}")
        frente, tags = partes[0], partes[2]
        k = next((tg for tg in tags.split() if "::" in tg and tg in estado["topicos"]), None)
        if not k:
            sem_topico.append(frente[:60])
            manter.append(linha)
            continue
        t = estado["topicos"][k]
        existente = next((c for c in t["cards"] if mesmo_texto(c["frente"], frente)), None)
        if existente and existente["sessao"] != pasta.name:
            duplicados.append(frente[:60])
            continue
        if not existente:
            t["cards"].append({"frente": frente, "sessao": pasta.name})
            tocados.add(k)
        manter.append(linha)
    tsv.write_text("\n".join(manter) + "\n", encoding="utf-8")
    gravar_json(ESTADO, estado)
    for k in tocados:
        render_topico(estado["topicos"][k])
    exportar()
    total = sum(1 for l in manter if l.strip() and not l.startswith("#"))
    print(f"flashcards.tsv: {total} cards · duplicados removidos: {len(duplicados)}")
    for d in duplicados:
        print(f"  - duplicado: {d}")
    if sem_topico:
        print("AVISO: cards sem tag disciplina::topico reconhecida (consolide a sessão antes, "
              "e use a tag exata `slug-disciplina::slug-topico`):")
        for s in sem_topico:
            print(f"  - {s}")


# ---------------------------------------------------------------- exportação para o dashboard
DASHBOARD = RAIZ / "dashboard"


def ler_perfil() -> dict:
    p = RAIZ / "perfil.md"
    if not p.exists():
        return {}
    campos = {"cargo-alvo": "cargo", "orgao-tribunal": "orgao", "banca-provavel": "banca",
              "fase-atual": "fase", "data-da-prova": "data_prova"}
    perfil = {}
    for linha in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*-\s*\*\*(.+?):\*\*\s*(.*)", linha)
        if m and slug(m.group(1)) in campos:
            valor = re.sub(r"<!--.*?-->", "", m.group(2)).strip()
            perfil[campos[slug(m.group(1))]] = valor
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", perfil.get("data_prova", "")):
        perfil.pop("data_prova", None)
    return perfil


def duracao_minutos(regs: list[dict]) -> int:
    horarios = sorted(dt.datetime.fromisoformat(r["registrado_em"]) for r in regs if r.get("registrado_em"))
    if not horarios:
        return 0
    gaps = [(b - a).total_seconds() / 60 for a, b in zip(horarios, horarios[1:])]
    uteis = sorted(g for g in gaps if g <= 30)
    mediana = uteis[len(uteis) // 2] if uteis else 4.0
    return max(1, round(sum(uteis) + mediana))


def montar_dados() -> dict:
    estado = carregar_estado()
    sessoes, series, ordem_disc = [], {}, []
    calib = {c: {"n": 0, "acertos": 0} for c in NOTA_OBJETIVA}
    for m in sorted(SESSOES.glob("*/meta.json")) if SESSOES.exists() else []:
        meta = ler_json(m, {})
        regs = ler_registros(m.parent)
        if not meta.get("consolidada") or not regs:
            continue
        data = data_sessao(meta)
        obj = [r for r in regs if r["tipo"] == "objetiva"]
        tipos: dict[str, int] = {}
        for r in obj:
            calib[r["certeza"]]["n"] += 1
            calib[r["certeza"]]["acertos"] += int(r["acertou"])
            if r.get("tipo_erro"):
                tipos[r["tipo_erro"]] = tipos.get(r["tipo_erro"], 0) + 1
        por_topico = []
        for k, rs in agrupar(regs).items():
            d = rs[0]["disciplina"]
            if d not in ordem_disc:
                ordem_disc.append(d)
            ns = media([r["nota"] for r in rs])
            tps = {r["tipo"] for r in rs}
            modo = tps.pop() if len(tps) == 1 else "mista"
            series.setdefault(k, []).append({"data": data, "nota": ns, "modo": modo})
            por_topico.append({"disciplina": d, "topico": rs[0]["topico"], "nota": ns, "n": len(rs)})
        sessoes.append({
            "id": meta["id"], "data": data, "tema": meta.get("tema", ""), "modo": meta.get("modo", ""),
            "duracao_min": duracao_minutos(regs), "n": len(regs), "nota": media([r["nota"] for r in regs]),
            "obj_total": len(obj), "obj_acertos": sum(int(r["acertou"]) for r in obj),
            "chutes": sum(1 for r in obj if r["acertou"] and r["certeza"] == "chute"),
            "tipos_erro": tipos, "topicos": por_topico,
        })
    topicos = []
    for k, t in estado["topicos"].items():
        if t["disciplina"] not in ordem_disc:
            ordem_disc.append(t["disciplina"])
        topicos.append({
            "disciplina": t["disciplina"], "topico": t["topico"], "nivel": t["nivel"], "tendencia": t["tendencia"],
            "ultima": t["ultima"], "proxima": t["proxima"], "sessoes": t["sessoes"], "arquivado": t.get("arquivado", False),
            "lacunas": [{"texto": l["texto"], "vezes": l.get("vezes", 1), "importancia": l.get("importancia", 1)}
                        for l in t["lacunas_abertas"]],
            "erros": t["erros_conceituais"], "cards": len(t["cards"]),
            "serie": series.get(k, [{"data": h["data"], "nota": h["nota"], "modo": h["modo"]} for h in t["historico"]]),
        })
    return {"gerado_em": dt.datetime.now().isoformat(timespec="minutes"), "exemplo": False, "perfil": ler_perfil(),
            "disciplinas": ordem_disc, "sessoes": sessoes, "topicos": topicos, "calibragem": calib}


def dados_exemplo() -> dict:
    """Histórico fictício (8 semanas) para demonstração. O conteúdo das lacunas é juridicamente correto."""
    import random
    rnd = random.Random(7)
    base = {
        "Direito Civil": {
            "Usucapião": ["Usucapião familiar: 2 anos, imóvel urbano de até 250 m² e abandono do lar pelo ex-cônjuge (art. 1.240-A do CC)"],
            "Prescrição e decadência": ["Prazo prescricional geral é de 10 anos (art. 205 do CC); reparação civil prescreve em 3 anos (art. 206, § 3º, V)"],
            "Responsabilidade civil": ["Responsabilidade objetiva pela atividade de risco: art. 927, parágrafo único, do CC"],
        },
        "Processo Civil": {
            "Tutela provisória": ["Tutela antecipada antecedente estabiliza se a decisão não for impugnada (art. 304 do CPC); revisão em 2 anos"],
            "Honorários": ["Honorários contra a Fazenda Pública seguem as faixas percentuais do art. 85, § 3º, do CPC"],
        },
        "Direito Penal": {
            "Dosimetria": ["Na 2ª fase, atenuantes não levam a pena abaixo do mínimo legal (Súmula 231 do STJ)"],
            "Roubo": ["Roubo com emprego de arma branca: majorante do art. 157, § 2º, VII, do CP (Lei 13.964/2019)"],
        },
        "Processo Penal": {
            "Prisão preventiva": ["Necessidade da preventiva revisada a cada 90 dias (art. 316, parágrafo único, do CPP)"],
            "Nulidades": ["Não há nulidade sem demonstração de prejuízo (art. 563 do CPP)"],
        },
    }
    erros = {"Prisão preventiva": "Prisão preventiva não tem prazo máximo fixado em lei",
             "Dosimetria": "Maus antecedentes e reincidência não podem valorar o mesmo fato em fases distintas"}
    hoje_d = dt.date.today()
    inicio = hoje_d - dt.timedelta(days=55)
    pares = [(d, t) for d in base for t in base[d]]
    habilidade = {p: rnd.uniform(3.0, 6.0) for p in pares}
    sessoes, series = [], {}
    calib = {"certeza": {"n": 0, "acertos": 0}, "duvida": {"n": 0, "acertos": 0}, "chute": {"n": 0, "acertos": 0}}
    dia = inicio
    while dia <= hoje_d:
        if rnd.random() < 0.62:
            modo = rnd.choice(["discursiva", "discursiva", "objetiva"])
            escolhidos = rnd.sample(pares, rnd.randint(2, 3))
            por_topico, notas, tipos, obj_total, obj_acertos, chutes = [], [], {}, 0, 0, 0
            for (d, t) in escolhidos:
                habilidade[(d, t)] = min(9.6, habilidade[(d, t)] + rnd.uniform(0.1, 0.55))
                n = rnd.randint(2, 4)
                ns = round(max(0, min(10, habilidade[(d, t)] + rnd.uniform(-1.6, 1.2))) * 2) / 2
                notas += [ns] * n
                por_topico.append({"disciplina": d, "topico": t, "nota": ns, "n": n})
                series.setdefault((d, t), []).append({"data": dia.isoformat(), "nota": ns, "modo": modo})
                if modo == "objetiva":
                    for _ in range(n):
                        c = rnd.choices(["certeza", "duvida", "chute"], [5, 3, 1])[0]
                        ok = rnd.random() < {"certeza": 0.86, "duvida": 0.55, "chute": 0.4}[c]
                        calib[c]["n"] += 1; calib[c]["acertos"] += int(ok)
                        obj_total += 1; obj_acertos += int(ok); chutes += int(ok and c == "chute")
                        if not ok:
                            te = rnd.choice(["conteudo", "conteudo", "leitura", "pegadinha"])
                            tipos[te] = tipos.get(te, 0) + 1
            tema = escolhidos[0][0]
            sessoes.append({"id": f"{dia.isoformat()}_exemplo", "data": dia.isoformat(), "tema": tema, "modo": modo,
                            "duracao_min": rnd.randint(22, 75), "n": len(notas), "nota": media(notas),
                            "obj_total": obj_total, "obj_acertos": obj_acertos, "chutes": chutes,
                            "tipos_erro": tipos, "topicos": por_topico})
        dia += dt.timedelta(days=1)
    topicos = []
    for (d, t) in pares:
        s = series.get((d, t), [])
        if not s:
            continue
        nivel = s[0]["nota"]
        for p in s[1:]:
            nivel = round(0.6 * p["nota"] + 0.4 * nivel, 1)
        ant = s[-2]["nota"] if len(s) > 1 else None
        ultima = s[-1]["data"]
        prox = somar_dias(ultima, dias_ate_proxima(s[-1]["nota"], [{"nota": x["nota"]} for x in s]))
        abertas = [] if nivel >= 8.5 else [{"texto": x, "vezes": rnd.randint(1, 3), "importancia": rnd.choice([2, 3])} for x in base[d][t]]
        topicos.append({"disciplina": d, "topico": t, "nivel": nivel, "tendencia": tendencia(s[-1]["nota"], ant),
                        "ultima": ultima, "proxima": prox, "sessoes": len(s), "arquivado": False, "lacunas": abertas,
                        "erros": [{"texto": erros[t], "data": s[0]["data"]}] if t in erros else [],
                        "cards": rnd.randint(0, 4), "serie": s})
    return {"gerado_em": dt.datetime.now().isoformat(timespec="minutes"), "exemplo": True,
            "perfil": {"cargo": "Juiz de Direito Substituto", "orgao": "Tribunal de Justiça", "banca": "FGV",
                       "fase": "2ª fase", "data_prova": (hoje_d + dt.timedelta(days=47)).isoformat()},
            "disciplinas": list(base), "sessoes": sessoes, "topicos": topicos, "calibragem": calib}


def exportar(exemplo: bool = False) -> Path:
    DASHBOARD.mkdir(parents=True, exist_ok=True)
    dados = dados_exemplo() if exemplo else montar_dados()
    destino = DASHBOARD / ("dados.exemplo.js" if exemplo else "dados.js")
    var = "DADOS_EXEMPLO" if exemplo else "DADOS"
    destino.write_text(f"window.{var} = {json.dumps(dados, ensure_ascii=False)};\n", encoding="utf-8")
    return destino


def cmd_exportar(args) -> None:
    destino = exportar(args.exemplo)
    print(f"dados do dashboard: {destino.relative_to(RAIZ).as_posix()} ({destino.stat().st_size // 1024 + 1} KB)")


def cmd_topico(args) -> None:
    estado = carregar_estado()
    t = estado["topicos"].get(chave(args.disciplina, args.topico))
    if not t:
        print(f"Sem histórico para {args.disciplina} · {args.topico} (tópico novo).")
        return
    p = caminho_topico(t)
    if not p.exists():
        render_topico(t)
    print(p.read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("abrir").set_defaults(f=cmd_abrir)
    p = sub.add_parser("nova")
    p.add_argument("--modo", required=True)
    p.add_argument("--tema", required=True)
    p.add_argument("--material")
    p.set_defaults(f=cmd_nova)
    p = sub.add_parser("registrar")
    p.add_argument("sessao")
    p.add_argument("--json")
    p.add_argument("--arquivo", help="lê o JSON de um arquivo (útil no PowerShell)")
    p.set_defaults(f=cmd_registrar)
    for nome, f in (("metricas", cmd_metricas), ("consolidar", cmd_consolidar), ("cards", cmd_cards)):
        p = sub.add_parser(nome)
        p.add_argument("sessao")
        if nome == "metricas":
            p.add_argument("--pontos", action="store_true", help="inclui o status de cada ponto (correção no fechamento)")
        p.set_defaults(f=f)
    p = sub.add_parser("exportar")
    p.add_argument("--exemplo", action="store_true", help="gera dashboard/dados.exemplo.js com histórico fictício")
    p.set_defaults(f=cmd_exportar)
    p = sub.add_parser("topico")
    p.add_argument("disciplina")
    p.add_argument("topico")
    p.set_defaults(f=cmd_topico)
    args = ap.parse_args()
    args.f(args)


if __name__ == "__main__":
    main()
