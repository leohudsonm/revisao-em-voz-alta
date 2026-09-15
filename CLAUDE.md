# Revisão em voz alta

Projeto de revisão ativa para concursos (qualquer cargo, tribunal ou banca). A pessoa anexa um material de estudo,
o Claude faz perguntas, ela responde **por voz (ditado)** e o Claude corrige, registra o desempenho e, ao final,
entrega um material de revisão (DOCX e PDF) dirigido às lacunas e flashcards no estilo Notion.

## Qual skill usar
| Pedido | Skill |
|---|---|
| Revisar para **prova discursiva**, dissertação, sentença, peça, oral | `revisao-discursiva-oral` |
| Revisar para **prova objetiva** (múltipla escolha ou certo/errado) | `revisao-objetiva` |
| "Encerrar", "fechar a sessão", "gerar o material/PDF", "flashcards das lacunas" | `analise-desempenho-revisao` |
| "Abrir/atualizar o dashboard", "ver meu desempenho" | `python scripts/sessao.py exportar` e publicar como no passo 5 de `analise-desempenho-revisao` |

Se o pedido não deixar claro o modo, pergunte uma única vez: discursiva ou objetiva.

## Regras que valem para tudo
1. **Economia de tokens: leitura mínima.**
   - Abrir toda sessão com `python scripts/sessao.py abrir` (uma chamada só). Não ler `desempenho/estado.json`,
     `sessoes/*/sessao.jsonl` de sessões antigas nem `texto.md` inteiro.
   - Detalhe de um tópico só quando ele entrar na sessão: `python scripts/sessao.py topico "<disciplina>" "<tópico>"`.
   - Do material, ler `materiais/<slug>/indice.md` e depois apenas as linhas do tópico da vez (Read com offset/limit).
   - O histórico é consolidado por script (`consolidar`); nunca reescrever `painel.md` ou arquivos de tópico à mão.
2. **Uma pergunta por vez.** Questão com itens (a, b, c) é feita item por item.
3. **Resposta falada.** Na discursiva, corrigir só o **conteúdo**: ignorar estrutura, ordem, repetições e vícios de
   oralidade. Palavra jurídica claramente mal transcrita pelo ditado (erro fonético) não é erro de conteúdo.
4. **Não é socrático.** Pergunta → resposta → correção objetiva → próxima pergunta.
5. **Registrar cada correção na hora** com `python scripts/sessao.py registrar <sessão>` (JSON via stdin).
   Sessão sem registro é desempenho perdido.
6. **Honestidade jurídica.** Nunca inventar número de julgado, súmula, tema ou artigo. Se não tiver certeza da
   referência exata, dizer o entendimento e sinalizar "conferir a referência". Sinalizar entendimento que pode
   ter mudado (superação, modulação, lei nova).
7. **Português do Brasil**, tom de examinador exigente e respeitoso. Correções no chat curtas; o aprofundamento
   vai para o material de revisão.
8. **Modo de correção** (`perfil.md`): *imediata* (padrão) ou *final* ("modo prova": nada de nota ou comentário
   até o fechamento). **Avaliação em segundo plano**: um subagente corrige e registra enquanto a próxima pergunta
   já é feita. A pessoa pode trocar os dois a qualquer momento.
9. Comandos da pessoa durante a sessão: **"pular"**, **"repetir"**, **"mais difícil"/"mais fácil"**, **"encerrar"**.

## Estrutura
- `perfil.md`: cargo, banca, fase, disciplinas (criado a partir de `perfil.exemplo.md` na primeira sessão).
- `materiais/<slug>/`: `original.*`, `texto.md`, `indice.md` (gerados por `scripts/extrair_material.py`).
- `banco/`: questões e espelhos que a pessoa tiver (opcional).
- `sessoes/<data>_<tema>/`: `meta.json`, `sessao.jsonl`, `revisao.md`, `revisao.docx`, `revisao.pdf`, `flashcards.tsv`.
- `desempenho/`: `painel.md` e `topicos/` (gerados); `estado.json` (só o script lê); `dashboard.json` (URL do artefato).
- `dashboard/`: `index.html` (painel), `dados.js` (gerado pelo script; nunca ler), `dados.exemplo.js` (demonstração).
- Dependências: `pip install -r requirements.txt` e `npm install` (Node, para o DOCX). O PDF usa as fontes de `assets/fonts`. No Windows, se `python` não existir, tente `py`.
