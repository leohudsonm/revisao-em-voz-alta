---
name: flashcards-estudo
description: Cria flashcards de estudo no estilo Notion a partir de um material (livro, fotos de páginas, PDF, resumo, aula) ou das lacunas de uma sessão de revisão, valida o formato, submete todos os cards a uma auditoria final por revisor independente, gera um PDF de visualização e envia para o Anki (baralho e tipo de nota do perfil.md). Use quando a pessoa pedir "flashcards", "cards", "cria cards disso", "manda pro Anki", ou no passo de flashcards da skill analise-desempenho-revisao.
---

# Flashcards de estudo

Formato completo, com paleta, blocos e exemplo: `references/modelo-notion.md` (leia antes de escrever os cards).
Auditoria final obrigatória: `references/revisor.md` (passo 6). Nenhum card vai para o Anki sem aprovação.
Script: `python .claude/skills/flashcards-estudo/scripts/cards.py {validar|preview|anki}` (no Windows, `py` se
`python` não existir).

## 1. Fonte e fidelidade
- Identifique a fonte e leia **só a parte** que vai virar card (páginas, tópico do `indice.md`, lacunas da sessão).
- **A fonte é a referência.** O que está no livro ou material está certo: não acrescente afirmação externa que o
  contradiga ou vá além dele. Anotações da pessoa na fonte também valem.
- Nunca invente número de julgado, súmula, tema ou artigo. Na dúvida sobre a referência, deixe-a fora da citação.

## 2. Selecionar o que vira card
- **1 regra autônoma = 1 card.** Se uma regra só aparece "de carona" no verso de outro card, ela ganha card próprio.
- Priorize o que cai em prova e o que a pessoa errou ou não lembrou. Nada de card sobre obviedade ou curiosidade.
- Vindo de sessão de revisão: só lacunas importantes (importância ≥ 2 ou recorrentes) e erros conceituais (estes
  com callout 🚫). Nada sobre o que a pessoa acertou com certeza.

## 3. Escrever: as regras da frente que mais importam
1. **Pergunta direta por padrão**, sem introdução de caso concreto. Caso só quando a resposta depende de
   reconhecer fatos; aí, curto e com quesito neutro. Em dúvida, direta.
2. **Neutra: não entrega nem pressupõe a resposta.** "Em que condição X pode ser atingido?" → "X pode ser atingido?".
   Não embutir na pergunta a crítica, o requisito ou a consequência cobrados.
3. **Nunca exige decorar número** de artigo, súmula, tema ou lei; números só no verso.
4. **A frente puxa tudo o que o verso cobra**; o verso responde exatamente a pergunta e só aprofunda.
5. Nada de pergunta vaga ("Qual o entendimento sobre X?", "Fale sobre X").

## 4. Conferir antes de validar
Leia cada frente **sozinha**, como quem vai revisar no Anki amanhã:
- Dá para responder sem ter visto o verso? A pergunta é inequívoca?
- Ela sugere a resposta (sim/não, condição, alternativa)?
- Tem regra no verso que a pergunta não provoca? → novo card.
- Tudo no verso bate com a fonte?

## 5. Gravar e validar (checagem mecânica)
1. Grave o TSV (UTF-8, TAB, sem cabeçalho): `frente<TAB>verso<TAB>tags`, com a tag `<slug-materia>::<slug-assunto>`
   (e `revisao-voz-alta`, se vier de sessão). Local: `sessoes/<sessão>/flashcards.tsv` se vier de sessão; senão,
   `flashcards/<AAAA-MM-DD>_<assunto>.tsv`.
2. `cards.py validar ARQ.tsv` → corrija até zerar os erros; leia os avisos (pressupor resposta, frente longa).

## 6. Auditoria final (obrigatória, antes de mostrar e de enviar)
Passar no validador **não** é estar pronto: ele só confere o formato. A qualidade é julgada por um **revisor
independente**, seguindo `references/revisor.md` (padrão impecável, APPROVE ou REJECT por card).
1. Lance um **subagente** (ferramenta Agent) que não participou da redação, com: o caminho do TSV, o de
   `references/revisor.md` e `references/modelo-notion.md`, o baralho de destino e a **fonte** (arquivo e
   páginas ou linhas do material; se vier de sessão, também `python scripts/sessao.py metricas sessoes/<sessão> --pontos`).
   Peça o veredito de todos os cards e a pré-checagem do lote. Ele só aponta; não edita arquivos.
   Sem a ferramenta Agent, faça a auditoria como uma passada separada, relendo a fonte antes dos cards e
   preenchendo a tabela do revisor para cada card; nunca pule a etapa.
2. Reescreva os cards reprovados atacando **todas** as alterações obrigatórias, rode `cards.py validar` de novo e
   devolva ao revisor **só os reprovados**, com o número da tentativa. Crie, divida, consolide ou remova cards
   conforme a pré-checagem do lote.
3. Card com **3 REJECTs** fica fora do TSV e do Anki; mostre à pessoa o impasse.
4. Registre o resultado em uma linha no chat: "Auditoria: N aprovados na 1ª, M reescritos, K fora".
5. Só depois: se vier de sessão, `python scripts/sessao.py cards sessoes/<sessão>` (registra no histórico) e
   `cards.py preview ARQ.tsv --titulo "Flashcards: <assunto>"` → envie o PDF para a pessoa ver.

Cards já enviados que forem corrigidos depois (a pedido da pessoa) passam pela mesma auditoria antes de atualizar
o Anki.

## 7. Enviar para o Anki (só cards aprovados na auditoria)
Precisa do Anki aberto com o add-on **anki-mcp** (porta 3141, ou a variável `ANKI_MCP_URL`).
- `cards.py anki ARQ.tsv --materia "<Matéria>" --assunto "<Assunto>"`
  - **Baralho:** `Baralho Anki` do `perfil.md` (com `{materia}` e `{assunto}`); sem isso,
    `Revisão em voz alta::<Matéria>::<Assunto>`. `--deck` sobrepõe.
  - **Tipo de nota:** `Tipo de nota Anki` do `perfil.md`; sem isso, `Revisão em voz alta - Pergunta`, criado
    automaticamente. Um tipo próprio precisa ter os campos Pergunta, Fundamento, Matéria, Assunto, Identificação e Mais.
  - Na primeira vez cria as notas e grava os ids em `ARQ.anki.json`; depois **atualiza** as mesmas notas (corrigir
    um card = editar o TSV e rodar de novo; o histórico de revisão no Anki é mantido). Card novo vai no **fim** do TSV.
  - Ao final, confere se o Anki ficou idêntico ao TSV.
- Sem o add-on: importar à mão (Arquivo → Importar → o TSV, separador Tab, permitir HTML, campo 3 = Tags).
- Cards que não aparecem logo após o envio: é atualização da tela do Anki; abrir o navegador de cards resolve.
