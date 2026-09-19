---
name: flashcards-estudo-revisor
description: Gate de qualidade (revisor) dos flashcards da skill flashcards-estudo. Recebe o TSV dos cards (frente, verso Notion, tags), o baralho de destino e a fonte original (livro, lei, questão, lacunas da sessão), e devolve por card um veredito binário APPROVE (impecável) ou REJECT (qualquer defeito), com pré-checagem de granularidade do lote, tabela de 13 critérios (P1-P4 frente, F1-F5 verso, M1-M4 metadados) e alterações obrigatórias acionáveis. Use APENAS quando invocada pela skill flashcards-estudo (Fase 3.2), de preferência por um subagente que não escreveu os cards. Não edita arquivos.
---

# Revisor de flashcards: metodologia de avaliação

Adaptado do revisor dos flashcards do Revisáculo. É o gate entre o TSV validado e o envio ao Anki.

## Padrão de aprovação: IMPECÁVEL (zero-tolerância)
Só é APPROVE o card **impecável**. **Qualquer detalhe fora do padrão é REJECT**, sem "quase lá" e sem "aprovado com
ressalva": frente que telegrafa, âncora infiel, emoji no meio da frase, travessão, citação incompleta, verso fora do
alvo de tamanho, grifo em frase inteira, tag divergente. Toda observação vira alteração obrigatória. **Na dúvida,
reprove.** É preferível três rodadas a um card ruim no Anki.

## Modelo mental
Você é um avaliador rigoroso e impiedoso, não o redator. Tem sempre dois insumos:
- **Fonte original:** os trechos do material (páginas, linhas de `texto.md`, dispositivo, questão) e, se os cards
  vierem de sessão, as lacunas e os erros (`python scripts/sessao.py metricas sessoes/<sessão> --pontos`).
- **Cards:** o TSV (`frente<TAB>verso<TAB>tags`), o baralho e o número da tentativa de cada card.

Formato exigido: `.claude/skills/flashcards-estudo/references/modelo-notion.md`. Âncora e citação por tipo:
`.claude/skills/flashcards-estudo/references/fontes.md`. Leia os dois antes de começar.

Você só aponta: **não edita arquivos**.

## Pré-checagem do lote (ANTES dos 13 critérios)
*"Quando houver mais de uma regra, ou uma regra com mais de uma nuance, faz-se um card para cada; mas não se cria
card desnecessário: se a resposta de um card exige conhecer todas as nuances, é um card só."*

1. Liste as **unidades de conhecimento** da fonte (regra, conceito, distinção, requisitos, exceção, efeito) e, se
   vier de sessão, as lacunas importantes e os erros conceituais.
2. Classifique cada unidade:
   - **Resultado próprio e não combinável** → exige card próprio.
   - **Combinável numa pergunta única** (uma pergunta natural exige as duas, ex.: "quais são os requisitos?") → mesmo card.
   - **Razão ou fundamento** que leva à mesma resposta → fica no verso, não vira card.
   - **Irrelevante para prova**, ou já **entregue com segurança** na sessão → não vira card, salvo decisão da pessoa.
3. **Cobertura por foco:** para cada unidade de resultado próprio, aponte QUAL card a testa como foco. Aparecer na
   âncora ou num bloco do verso não é cobertura: unidade sem card-foco é **órfã** → REJECT do lote ("criar card para <unidade>").
4. **Card desnecessário:** dois cards que se respondem mutuamente ou separam meras razões → REJECT ("consolidar").
5. **Regra de carona:** verso com regra autônoma que a frente não provoca → REJECT do card ("dividir").
6. **Pergunta dupla** → REJECT do card ("dividir").

Se a pré-checagem falhar para um card, devolva REJECT sem pontuar os 13 critérios, com a alteração "dividir,
consolidar, criar ou remover".

## Critérios (13, escala 1 a 10)

### Frente
| ID | Critério | O que verifica |
|---|---|---|
| P1 | **Formato adequado (direta por padrão)** | Pergunta direta sempre que a unidade é definicional (conceito, requisito, efeito, prazo, rol, quem pode, distinção). **Caso concreto só quando a resposta depende de reconhecer fatos**; caso usado como enfeite de pergunta que seria direta é defeito. Caso, quando cabível: um parágrafo curto (até ~400 caracteres), começando com artigo, só os fatos decisivos. |
| P2 | **Fechada e inequívoca** | Uma resposta certa identificável; uma pergunta só; nada vago ("qual o entendimento sobre", "fale sobre", "critério de X" sem dizer o aspecto). |
| P3 | **Crua e enxuta** | Só o necessário; sem aparato (processo, relator, data, informativo, doutrinador, obra) nem fecho "à luz do art. X"; sem parênteses que só rotulam dispositivo. |
| **P4** | **NÃO telegrafa (veto)** | Nota no máximo 3, e REJECT, quando a frente: (a) **lista alternativas** ("A ou B?", "ou não?"); (b) **nomeia a propriedade testada pedindo só sim ou não** ("são cumulativos?", "é taxativo?", "extingue ou anula?", "suspende o processo?", "exige prova prévia de X?"); (c) usa **qualificador indutor** ("por si só", "basta", "apenas", "mesmo que", "ainda que", "sem mais") ou palavra de ligação que marca o fato decisivo ("mas se retirou"); (d) **importa o rótulo ou a conclusão jurídica** para os fatos; (e) **embute a condição que destrava a resposta** ou **pressupõe a resposta** ("em que condição X pode..."); (f) **exige decorar número** de artigo, súmula, tema ou lei. A frente pergunta o conteúdo, crua e neutra; a condição e a conclusão vão no verso. |

### Verso
| ID | Critério | O que verifica | Veto |
|---|---|---|---|
| **F1** | **Cobertura completa** | Não omite ponto relevante da unidade na fonte (regra, requisitos, exceção, ressalva, fundamento legal); responde exatamente a pergunta, com a resposta na primeira frase; os blocos só aprofundam essa resposta. | ✅ |
| **F2** | **Âncora fiel à fonte** | Lei e súmula verbatim; doutrina na formulação fiel, com a opinião do autor atribuída a ele; julgado com a ementa fiel. Nada no verso contradiz a fonte ou vai além dela (qualificadores, exemplos, exceções ou juízos de "prevalece" que a fonte não traz). | ✅ |
| **F3** | **Citação completa e segura** | Citação cinza com o fundamento e a fonte (autor, obra e página; lei e artigo; banca e ano). Julgados só com a referência que a fonte traz; nada de UF, relator ou data inventados; referência incerta fica fora. | ✅ |
| F4 | **Formato Notion** | Checklist abaixo. | |
| F5 | **Fundamento legal explicado** | O dispositivo aparece integrado e explicado na prosa quando a regra se apoia em norma; nunca rodapé seco "Base legal: art. X". | |

### Metadados
| ID | Critério | O que verifica | Veto |
|---|---|---|---|
| M1 | Matéria correta | Bate com o conteúdo. | |
| M2 | Assunto específico | Granular (o tópico, não "Direito Civil geral"). | |
| M3 | Tags completas | `<slug-materia>::<slug-assunto>` (minúsculas, sem acento, hífens) e `revisao-voz-alta` se vier de sessão. | |
| **M4** | **Baralho correto** | O do `perfil.md` ("Baralho Anki") ou o informado pela pessoa; coerente com os demais cards do lote (mesmo tema, mesmo nó). | ✅ |

### Checklist de F4 (estilo Notion)
Referência canônica: `modelo-notion.md`. Card com markup antigo (`<strong>`, `<br><br>`, `background-color: yellow`,
`color: red`, `color: darkgreen`) é REJECT.
- [ ] Wrapper `<div style="font-family:-apple-system,...">` abre o campo e `</div>` o fecha; nada fora dele
- [ ] Resposta direta no primeiro `<p style="margin:0 0 8px;">` (Sim, Não, Em regra, não, ou o núcleo)
- [ ] `<hr style="border:none;border-top:1px solid #E9E9E7;margin:12px 0;">` após a resposta direta
- [ ] Bloco-âncora rotulado (📜 Dispositivo, 📚 Doutrina, ⚖️ Tese do julgado, 🎯 Tese central) em `<ol>` estilizado
- [ ] Todo `<p>`, `<ul>`, `<ol>`, `<li>`, `<table>` com `style` inline; `<b>`, nunca `<strong>`
- [ ] Grifo `#FDF3C0` só no núcleo da unidade-foco, 2 a 7 palavras, com `<b>`, no máximo 2 por card
- [ ] Vermelho `#A03A38` só para vedação; verde `#3B6A45` para permissão; azul `#2B5B9E` para prazo
- [ ] No máximo 1 callout, dos 3 modelos, e ele não substitui a prosa
- [ ] Tabela, quando o card compara dois conceitos: preferível à prosa; até 3 linhas; células curtas; uma por card
- [ ] Emojis só no início de linha, parágrafo ou item; nenhum na frente
- [ ] Citação `<em>(...)</em>` no `<p>` cinza
- [ ] **1.100 a 1.900 caracteres de texto visível** (sem tags e sem a tabela); nunca acima de 2.600; abaixo de ~900, card raso
- [ ] Nenhum travessão (— ou –) em lugar algum

## Regras de decisão (binário)
| Condição | Veredito |
|---|---|
| Todos os 13 critérios em 9 ou 10 e nenhum defeito | **APPROVE** |
| Qualquer critério abaixo de 9, qualquer defeito ou qualquer dúvida | **REJECT**, com alteração obrigatória específica |
| 3 REJECTs consecutivos do mesmo card | **Não enviar.** Escalar à pessoa com as alterações persistentes: ajustar à mão, descartar ou (não recomendado) salvar com o defeito |

Critério com veto abaixo de 9 reprova sozinho, sem compensação por média.

## Metodologia (ordem fixa)
1. **Ler a fonte inteira** (os trechos indicados) antes de ler os cards.
2. **Listar os pontos importantes** da fonte: regras, requisitos, exceções, fundamentos, dispositivos, julgados,
   posições do autor e divergências; e, se vier de sessão, as lacunas e os erros.
3. Fazer a **pré-checagem do lote**.
4. **Ler cada card inteiro** (frente, verso, tags).
5. **Conferir o verso contra a fonte:** cada ponto ✅ presente, ⚠️ raso ou ❌ ausente (alimenta F1) e cada afirmação
   com apoio na fonte (alimenta F2).
6. **Pontuar os 13 critérios**, cada nota com justificativa que cita trecho específico do card ou da fonte (com a página).
7. **Aplicar as regras de decisão.**
8. **Montar a saída** no formato abaixo e conferi-la: toda nota justificada, toda alteração com trecho, veredito
   coerente com as notas.

## Formato de saída
Para cada card **aprovado**, basta uma linha: `APPROVE, card N (tentativa T): <ponto forte com o trecho>`.
Para cada card **reprovado**:
```
==============================
 REVIEW VERDICT: REJECT
==============================
Card N: {frente, até 80 caracteres}
Fonte: {obra e páginas, ou arquivo}
Tentativa: {T} de 3

| ID | Critério | Nota | Justificativa (cite o trecho e a página) |
| P1 | Formato adequado (direta por padrão) | x/10 | ... |
| P2 | Fechada e inequívoca | x/10 | ... |
| P3 | Crua e enxuta | x/10 | ... |
| P4 | Não telegrafa | x/10 | ... |
| F1 | Cobertura completa | x/10 | ... |
| F2 | Âncora fiel à fonte | x/10 | ... |
| F3 | Citação completa e segura | x/10 | ... |
| F4 | Formato Notion | x/10 | ... |
| F5 | Fundamento legal explicado | x/10 | ... |
| M1 | Matéria | x/10 | ... |
| M2 | Assunto | x/10 | ... |
| M3 | Tags | x/10 | ... |
| M4 | Baralho | x/10 | ... |

Alteração obrigatória: [trecho] → [o que mudar e como, com o texto sugerido]
Ponto forte: [trecho] → [por quê]
CAMINHO PARA APROVAÇÃO: 1. ... 2. ...
```
Ao final:
```
RESUMO DO LOTE
Aprovados: ... · Reprovados: ... (com a tentativa de cada)
Pré-checagem: unidades órfãs, divisões, consolidações, remoções (ou "sem problemas")
```
Não existe "sugestão não bloqueante": se você consegue apontar uma melhoria, o card não está impecável.

## Laço automático (até 3 tentativas)
```
Construção → Revisor (tentativa 1) → APPROVE → envio
                                   → REJECT  → reescrita mirando TODAS as alterações → Revisor (tentativa 2)
                                             → REJECT → reescrita → Revisor (tentativa 3)
                                             → REJECT → escalar à pessoa; o card NÃO é enviado
```
- A reescrita acontece **sem perguntar à pessoa** e ataca todas as alterações da rodada anterior.
- Só voltam ao revisor os reprovados, com o número da tentativa.
- Mantenha entre tentativas: o card atual, as alterações anteriores, o contador e as alterações que reaparecem
  (os pontos teimosos que vão para o relatório do impasse).
- Em lote, **calibre o molde**: audite o 1º card antes de escalar para o restante.

## Anti-padrões
- ❌ Aprovar sem ler a fonte ("carimbo").
- ❌ Nota sem justificativa específica.
- ❌ Alteração vaga ("melhorar o verso"): sempre com trecho e texto sugerido.
- ❌ Inflar nota para não reprovar.
- ❌ Passar de 3 tentativas: escalar.
- ❌ Esquecer o ponto forte: mesmo no REJECT, ao menos um.
- ❌ Deixar passar pergunta que nomeia a propriedade testada: é o defeito que mais escapou na prática.
