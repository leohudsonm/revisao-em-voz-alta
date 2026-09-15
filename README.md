# Revisão em voz alta

Revisão ativa para concursos com o **Claude Code**: você anexa seu material, o Claude faz perguntas,
você **responde falando** (ditado), ele corrige, guarda seu desempenho e, no fim, gera um **PDF de revisão só com
as suas lacunas** e **flashcards** para o Anki.

Funciona para qualquer cargo, tribunal ou banca, em dois modos:

| | Discursiva | Objetiva |
|---|---|---|
| O que treina | **produzir** conteúdo (doutrina, jurisprudência, interpretação, caso concreto, sentença) | **reconhecer** a alternativa correta e desmontar pegadinhas |
| Como responde | fala livremente, como um brainstorm de prova | letra (ou certo/errado) + grau de certeza |
| Como é corrigido | rubrica oculta de pontos com peso; só conteúdo, nunca a forma | gabarito, erro de cada distratora, tipo de erro (conteúdo, leitura, pegadinha, chute) |
| Skill | `revisao-discursiva-oral` | `revisao-objetiva` |

No fim de qualquer sessão, a skill `analise-desempenho-revisao` consolida o histórico, gera o PDF e os flashcards.

## Instalação
1. Tenha o [Claude Code](https://claude.com/claude-code) e o Python 3.10+.
2. Baixe/clone esta pasta e abra-a no Claude Code.
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. (Opcional) Copie `perfil.exemplo.md` para `perfil.md` e preencha. Se não fizer, o Claude pergunta na primeira sessão.

## Como usar
1. Coloque o material (PDF, DOCX, TXT ou MD) em qualquer lugar e diga, por exemplo:
   > Quero uma revisão discursiva do arquivo `estudos/usucapiao.pdf`, 10 perguntas.

   ou
   > Faça 10 questões objetivas estilo FGV sobre o material de improbidade.
2. Ative o ditado (no app, o botão de microfone; ou o ditado do sistema: **Win + H** no Windows, **Fn Fn** no Mac)
   e responda falando. Não se preocupe com a estrutura: só o conteúdo é avaliado.
3. Comandos durante a sessão: **pular**, **repetir**, **mais difícil**, **mais fácil**, **encerrar**.
   Dois modos opcionais (configure em `perfil.md` ou peça durante a sessão):
   - **Correção no final ("modo prova")**: nenhuma nota ou comentário durante a sessão; tudo é corrigido no fechamento.
   - **Avaliação em segundo plano**: um subagente corrige e registra cada resposta enquanto a próxima pergunta já aparece.
4. Ao encerrar, você recebe:
   - `sessoes/<data>_<tema>/revisao.pdf`: o material dirigido às suas lacunas;
   - `sessoes/<data>_<tema>/flashcards.tsv`: importe no Anki (Arquivo → Importar; separador Tab; permitir HTML; 3º campo = Tags);
   - o painel atualizado em `desempenho/painel.md`.

Tem questões e espelhos de provas anteriores? Coloque em `banco/`: as skills usam como base de perguntas e rubricas.

## Dashboard
`dashboard/index.html` mostra o histórico em cinco abas:
- **Visão geral:** tempo, sessões, nota média, revisões atrasadas, sequência de dias, calendário de constância, estudo semanal e cartões por disciplina.
- **Disciplinas:** evolução das notas (discursiva e objetiva) e tabela de tópicos com lacunas e erros.
- **Pauta de revisões:** atrasadas, hoje, próximos 7 dias e programadas.
- **Histórico:** todas as sessões, com duração estimada e notas por tópico.
- **Lacunas e erros:** ranking de lacunas, erros conceituais, tipos de erro nas objetivas e calibragem da certeza.

Ao encerrar cada sessão, `scripts/sessao.py` regenera `dashboard/dados.js`. No Claude Code com Artifacts, o painel é
republicado no mesmo link, e cada publicação fica como uma versão. Sem Artifacts, basta abrir `dashboard/index.html`
no navegador. Sem histórico ainda, o painel mostra **dados de exemplo** fictícios (`dados.exemplo.js`), marcados como tal.

## Como o histórico fica barato (tokens)
Ler um histórico longo antes de cada sessão sairia caro. Por isso:
- **Um script é dono do histórico.** `scripts/sessao.py` grava tudo em `desempenho/estado.json`, que o Claude **não lê**.
- **Na abertura, o Claude lê só o `painel.md`**: uma tabela de até 80 linhas, reescrita a cada sessão, com nível,
  tendência, próxima revisão e lacuna-chave de cada tópico.
- **O detalhe de um tópico** (lacunas abertas, erros já cometidos, cards já feitos) só é carregado quando esse
  tópico entra na sessão.
- **O material é processado uma vez** (`texto.md` + `indice.md`); depois, lê-se só o trecho do tópico da vez.
- Os registros brutos das sessões nunca são relidos em sessões futuras.
- Tópicos dominados há mais de 60 dias saem do painel automaticamente.

## Como o desempenho é medido
- **Nível do tópico (0–10)**: média ponderada entre a nota da sessão (60%) e o nível anterior (40%).
- **Tendência**: ↑ ↓ = comparando a sessão com o nível anterior (mostra se a revisão surtiu efeito).
- **Próxima revisão**: nota < 5 → 1 dia; 5–7 → 3 dias; 7–9 → 7 dias; ≥ 9 duas vezes → 21 dias.
- **Objetivas**: acerto com certeza vale 10, com dúvida 6, chute 2, erro 0. Acertar chutando é lacuna.

Detalhes: `.claude/skills/analise-desempenho-revisao/references/formato-desempenho.md`.

## Estrutura
```
CLAUDE.md                     regras gerais (carregadas automaticamente)
.claude/skills/               as 3 skills e seus guias (rubrica, estilos de banca, modelo do PDF)
scripts/sessao.py             abertura, sessões, registro, métricas, consolidação, flashcards
scripts/extrair_material.py   PDF/DOCX/TXT → texto.md + índice
scripts/gerar_pdf.py          revisao.md → revisao.pdf
perfil.exemplo.md             modelo do seu perfil
materiais/ banco/ sessoes/ desempenho/   seus dados (fora do git)
```

## Privacidade
`perfil.md`, `materiais/`, `banco/`, `sessoes/` e `desempenho/` estão no `.gitignore`: seus dados e materiais
não vão para o repositório se você fizer um fork.

## Limites
- As perguntas e correções são geradas por IA. Referências de julgados e súmulas devem ser conferidas; o Claude é
  instruído a não inventar números e a sinalizar incertezas.
- PDFs escaneados (sem texto) precisam ser lidos página a página pelo Claude ou passar por OCR antes.
