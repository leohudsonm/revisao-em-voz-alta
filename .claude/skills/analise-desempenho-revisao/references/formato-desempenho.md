# Como o desempenho é medido e guardado

Tudo abaixo é executado por `scripts/sessao.py`. Este arquivo existe para explicar as regras (e para quem quiser ajustá-las no código).

## Arquivos
| Arquivo | Quem lê | Tamanho |
|---|---|---|
| `desempenho/estado.json` | só o script | cresce devagar (histórico limitado por tópico) |
| `desempenho/painel.md` | Claude, na abertura de toda sessão | máx. 80 linhas |
| `desempenho/topicos/<disciplina>/<topico>.md` | Claude, só quando o tópico entra na sessão | ~20–50 linhas |
| `desempenho/arquivo.md` | ninguém por padrão | lista de tópicos dominados |
| `sessoes/<id>/sessao.jsonl` | só `metricas`/`consolidar` da própria sessão | 1 linha por pergunta |

## Registro de uma pergunta (`sessao.jsonl`)
Campos comuns: `tipo` (discursiva|objetiva), `disciplina`, `topico`, `pergunta`, `lacunas[]`,
`lacunas_superadas[]`, `erros_conceituais[]`, `importancia` (1–3). Opcionais: `subtopico`, `fonte`, `enunciado`.
- Discursiva: `nota` (0–10) e `pontos[{ponto, peso, status}]`.
- Objetiva: `resposta`, `gabarito`, `certeza` (certeza|duvida|chute), `tipo_erro`, `banca`.
  O script calcula `acertou` e `nota`: certeza 10 · dúvida 6 · chute 2 · erro 0.

## Nota da sessão por tópico
Média das notas das perguntas daquele tópico na sessão.

## Nível do tópico (0–10)
- Primeira vez: nível = nota da sessão.
- Depois: `nível = 0,6 × nota da sessão + 0,4 × nível anterior` (dá peso ao mais recente sem apagar a história).

## Tendência
Compara a nota da sessão com o nível anterior: diferença ≥ +0,5 → ↑; ≤ −0,5 → ↓; senão =. Primeira vez → "novo".

## Próxima revisão (repetição espaçada simples)
| Nota da sessão | Próxima revisão |
|---|---|
| < 5 | 1 dia |
| 5 a 6,9 | 3 dias |
| 7 a 8,9 | 7 dias |
| ≥ 9 | 7 dias; 21 dias se a sessão anterior do tópico também foi ≥ 9 |

## Lacunas
- Novas lacunas entram em "abertas"; se já existir uma equivalente, soma `vezes` (recorrência).
- Texto em `lacunas_superadas` remove a lacuna aberta equivalente e a registra como superada.
- Máximo de 12 lacunas abertas por tópico (ficam as de maior importância e recorrência).
- Lacuna-chave do painel = a aberta de maior importância e recorrência, cortada em 12 palavras.

## Arquivamento
Tópico com nível ≥ 9 e sem revisão há mais de 60 dias sai do painel e vai para `arquivo.md`.
Se voltar a ser perguntado, retorna automaticamente.

## Prioridade das lacunas no PDF
`importância × (10 − nota da pergunta) × recorrência`.
