# Adaptador de fonte: como analisar cada tipo de material

O chassi (frente, verso, gate) é o mesmo para todos. O que muda é a **Fase 1 (análise)**: o que conta como
"unidade de conhecimento testável", qual é a **âncora** (o bloco fiel à fonte, em lista numerada, logo após o `<hr>`)
e qual é a **citação** final.

Regras transversais:
- A fonte é a referência. A âncora não pode contradizer a fonte nem ir além dela.
- Autor e obra são citáveis; apostila de cursinho não é: cite o autor ou a obra.
- **Formato da pergunta:** direta por padrão, em todos os tipos. Caso concreto só quando a unidade é de aplicação ou
  distinção e a resposta depende de reconhecer os fatos; nunca como enfeite de uma pergunta que seria direta.

---

## 1. Livro ou doutrina
**Fonte típica:** capítulo de manual, fotos de páginas, PDF, resumo do autor. Traz conceito, natureza jurídica,
requisitos, efeitos, distinções, correntes, julgados comentados.

**Unidade testável:** cada regra, conceito, distinção, requisito ou exceção autônoma. Exemplos:
- uma **distinção** ("desconsideração x imputação direta") → 1 card que pergunta a diferença;
- **requisitos** de um instituto → 1 card ("quais são os requisitos de X?"), com a natureza cumulativa ou
  alternativa na resposta, nunca na pergunta;
- **correntes divergentes** → 1 card sobre a divergência, com as posições e quem as sustenta;
- **exceção** relevante → card próprio se tem resultado autônomo;
- **julgado comentado pelo autor** → a tese que o autor extrai dele.

**Âncora:** rótulo `📚 <b>Doutrina:</b>`. Cada item é a **formulação fiel** da lição (próxima da literalidade
quando for definição consagrada), atribuída ao autor quando for opinião dele ("Para o autor, ...").
Julgado citado pelo autor pode entrar como `⚖️ <b>Tese do julgado:</b>`, com a ementa fiel.

**Citação:** `(Autor, Obra, p. X)`, somada aos dispositivos e julgados usados no verso.

**Cuidado:** a pergunta cobra compreensão (a regra, o requisito, o efeito), não decoreba de classificação sem função.

---

## 2. Lei seca
**Fonte típica:** artigo, parágrafo ou inciso.

**Unidade testável:** cada comando normativo autônomo. Incisos que são hipóteses independentes → em regra 1 card por
hipótese de resultado próprio; requisitos → 1 card. Prazos, competências, vedações e exceções são unidades fortes.

**Âncora:** rótulo `📜 <b>Dispositivo:</b>`. O item é o **texto verbatim** (aspas preservadas; única adequação: trocar
travessão por pontuação). Qualquer alteração é veto no revisor.

**Citação:** `(Lei nº X/AAAA, art. Y)` ou o código: `(Código Civil, art. 50)`.

**Cuidado:** a pergunta não cobra o número do artigo; cobra a regra. O número fica na âncora e na citação.

---

## 3. Questão comentada
**Fonte típica:** questão com gabarito e comentário (tese central, fundamento, pegadinha).

**Unidade testável:** a **regra que decide a questão**, não a questão em si. A pegadinha, quando relevante, vira o
callout 🚫.

**Âncora:** rótulo `🎯 <b>Tese central:</b>`, com a tese fiel.

**Citação:** `(Banca AAAA, questão comentada; base: dispositivo ou tese)`.

**Cuidado:** o card não reproduz a múltipla escolha nem importa as alternativas; destila a regra numa pergunta direta.

---

## 4. Lacunas de uma sessão de revisão em voz alta
**Fonte típica:** os pontos parciais, faltantes e os erros conceituais registrados na sessão
(`sessao.py metricas --pontos`), ancorados no **material da sessão** (`materiais/<slug>/texto.md`, livro-fonte).

**Unidade testável:** cada lacuna importante (importância ≥ 2 ou recorrente) e cada erro conceitual. A lacuna
orienta o **foco**; o conteúdo do card vem do **material**, não da resposta falada nem do comentário da correção.
Pontos que a pessoa entregou com segurança não viram card, salvo pedido dela.

**Âncora e citação:** herdam do tipo do material (livro → 📚 Doutrina; dispositivo → 📜 Dispositivo).
Erro conceitual cometido na sessão ganha o callout 🚫 Pegadinha.

---

## Resumo

| Tipo | Rótulo da âncora | Item da âncora | Citação |
|---|---|---|---|
| Livro ou doutrina | `📚 Doutrina:` | formulação fiel do autor | `(Autor, Obra, p. X)` |
| Lei seca | `📜 Dispositivo:` | texto verbatim | `(Lei nº X/AAAA, art. Y)` |
| Questão | `🎯 Tese central:` | tese fiel | `(Banca AAAA, questão comentada; base: ...)` |
| Lacuna de sessão | herda do material | herda | herda |

Em todos: grifo amarelo só no **núcleo** da unidade-foco; itens secundários da âncora sem grifo.
