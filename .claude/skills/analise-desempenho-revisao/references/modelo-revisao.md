# Modelo do `revisao.md` (vira PDF com `scripts/gerar_pdf.py`)

Use apenas os elementos abaixo: o conversor entende este subconjunto de Markdown.

```markdown
---
titulo: Revisão dirigida — <Tema da sessão>
subtitulo: Material montado a partir das suas lacunas
data: <AAAA-MM-DD>
material: <nome do material-base>
modo: Discursiva | Objetiva
perfil: <cargo · banca>
---

# Seu desempenho nesta sessão

| Tópico | Nota | Nível anterior | Tendência | Próxima revisão |
|---|---|---|---|---|
| Usucapião | 5,0 | 7,0 | caiu | 2026-09-15 |

**Onde você foi melhor:** <1–3 linhas>

**Onde você foi pior:** <1–3 linhas>

> [!ATENCAO] Erros conceituais desta sessão: <lista curta, só se houver>

---

# Lacunas prioritárias

## 1. <Tópico> — <lacuna em forma de título>

**O que faltou na sua resposta:** <1–2 frases, sem repetir a pergunta inteira>

<Conteúdo explicado de forma completa e objetiva: conceito, requisitos, correntes, posição dos tribunais,
exemplos. Baseie-se no trecho do material-base; complete com lei e jurisprudência consolidadas.>

- <requisito/elemento 1>
- <requisito/elemento 2>

> [!FUNDAMENTO] <artigos, súmulas, teses — só referências seguras; se incerto: "conferir referência">

> [!DICA] <discursiva: como escrever o ponto na prova — a frase-núcleo que o espelho procura>

> [!PROVA] <objetiva: como a banca costuma cobrar e qual a pegadinha>

> [!ATENCAO] <erro conceitual cometido e a versão correta, se houver>

## 2. <Tópico> — <lacuna>
...

---

# Pontos fortes (manter)
- <tópico: o que você já domina, em 1 linha>

# Rumos para a próxima revisão
1. <ação concreta, ex.: refazer 3 perguntas sobre X em 2026-09-15>
2. <ação>
3. <ação>
```

## Regras de redação
- **Só lacunas.** Não reescreva o material inteiro; aprofunde apenas o que a pessoa não entregou ou errou.
- Ordem das lacunas = ordem de prioridade dada por `metricas`.
- Cada lacuna deve ser estudável sozinha em 3–5 minutos (≈150–400 palavras).
- Discursiva: sempre o quadro `[!DICA]`. Objetiva: sempre o quadro `[!PROVA]`. Sessão mista: os dois quando couber.
- Linguagem de manual de revisão: direta, frases curtas, termos técnicos precisos.
- Não use emojis (a fonte do PDF pode não ter). Tendência por extenso: "subiu", "caiu", "estável", "novo".
- `---` sozinho em uma linha = quebra de página.
