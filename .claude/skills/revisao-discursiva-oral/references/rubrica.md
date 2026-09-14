# Rubrica oculta: como pontuar a resposta falada

A rubrica é montada **antes** de fazer a pergunta e **não** é mostrada à pessoa até a correção.
Ela imita o espelho de correção das bancas: uma lista de pontos, cada um com peso.

## 1. Montagem
- De 3 a 6 pontos por pergunta (ou item).
- Cada ponto é **uma ideia verificável**: conceito, requisito, distinção, corrente, tese de tribunal, dispositivo,
  consequência prática, solução do caso.
- Pesos:
  | Peso | Valor | O que é |
  |---|---|---|
  | essencial | 3 | sem ele a resposta não responde à pergunta; costuma valer a maior fatia no espelho |
  | importante | 2 | esperado de um candidato bem preparado |
  | diferencial | 1 | o que separa a resposta boa da excelente: corrente minoritária relevante, evolução jurisprudencial, crítica doutrinária, visão sistêmica |
- Ao menos 1 essencial por pergunta, e no máximo 1 diferencial para cada 3 pontos.
- Se houver espelho real no `banco/`, a rubrica **segue o espelho** (converta os pontos dele nesses pesos).

## 2. Status de cada ponto
| Status | Crédito | Quando |
|---|---|---|
| ✅ entregou | 100% | a ideia foi dita de forma correta e suficiente, mesmo sem o número do artigo |
| ◐ parcial | 50% | tangenciou, faltou o elemento que torna o ponto completo, ou disse o requisito sem a consequência |
| ❌ faltou | 0% | não apareceu |
| ⚠️ erro conceitual | 0% e −1 ponto na nota final (mínimo 0) | afirmou algo juridicamente errado sobre o ponto |

- Citar o dispositivo, súmula ou tese **não é obrigatório** para "entregou", salvo quando a pergunta pede
  expressamente a posição de um tribunal ou o fundamento legal. Mas, se a pessoa citar **errado**, registre como erro conceitual.
- Contradição interna (disse certo e depois o contrário) = parcial.
- Resposta correta, mas fora do que foi perguntado, não pontua.

## 3. Nota
`nota = 10 × (soma dos créditos) ÷ (soma dos pesos)` − 1 por erro conceitual; arredonde para 0,5.

Exemplo: pontos essencial (3) entregou, essencial (3) faltou, importante (2) parcial →
créditos 3 + 0 + 1 = 4 de 8 → nota 5,0.

## 4. Tolerâncias por ser resposta falada
- Ordem, estrutura, introdução e conclusão: **não avaliar**.
- Repetições, hesitações, frases incompletas: não avaliar se a ideia foi transmitida.
- Erros do ditado: palavras foneticamente próximas de um termo jurídico correto contam como o termo correto
  ("prescrição intercorrente" transcrita como "prescrição inter corrente"). Número de artigo transcrito de forma
  estranha: interprete pelo contexto.
- Na dúvida entre erro de ditado e erro de conteúdo, dê o benefício e **mencione** a dúvida em meia linha.

## 5. Transformar a correção em registro
- `pontos`: todos, com `peso` e `status` (entregou | parcial | faltou | erro).
- `lacunas`: um item para cada ponto **faltou** ou **parcial** de peso essencial/importante, redigido como a
  afirmação correta e completa (o que a pessoa deveria ter dito). Diferencial que faltou só vira lacuna se for
  tema de alta incidência.
- `erros_conceituais`: a versão correta da afirmação errada.
