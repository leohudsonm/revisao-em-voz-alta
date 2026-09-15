---
name: analise-desempenho-revisao
description: Fecha uma sessão de revisão (discursiva ou objetiva). Consolida o desempenho no histórico enxuto (painel e arquivos de tópico, via script), analisa onde a pessoa foi melhor e pior, gera um material de revisão (DOCX e PDF) dirigido SÓ às lacunas, com base no material de estudo usado, e cria flashcards estilo Notion das lacunas importantes (TSV importável no Anki). Use quando a pessoa disser "encerrar", "fechar a sessão", "analisar meu desempenho", "gerar o material de revisão/PDF", "flashcards das lacunas", ou ao fim do plano de uma sessão das skills revisao-discursiva-oral e revisao-objetiva.
---

# Análise de desempenho e material de revisão

Ordem obrigatória: **consolidar → analisar → material (DOCX e PDF) → flashcards → dashboard → resumo no chat.**
Consolidar primeiro garante que o histórico é salvo mesmo se algo falhar depois.

## 1. Consolidar (script, sem reescrever nada à mão)
0. Se houver **avaliações em segundo plano** ainda rodando, espere todas terminarem antes de consolidar.
1. Descubra a sessão (a atual; ou a mais recente com `consolidada: false`, que o `abrir` lista).
2. `python scripts/sessao.py metricas sessoes/<sessão>` (no **modo de correção final**, use `--pontos`, que
   inclui o status de cada ponto, a resposta marcada e o gabarito) → guarde a saída: é a base da análise
   (nota por tópico, nível anterior, tendência, lacunas priorizadas).
3. `python scripts/sessao.py consolidar sessoes/<sessão>` → atualiza `estado.json`, reescreve `painel.md`
   (limitado a 80 linhas), os arquivos de tópico e marca a sessão como consolidada.
   Regras aplicadas pelo script: ver `references/formato-desempenho.md`.

Se for uma consolidação de **sessão antiga pendente** disparada na abertura de outra sessão, pare aqui
(sem material nem cards) e volte para a sessão nova.

## 2. Analisar
Com a saída de `metricas` (não releia o `sessao.jsonl` inteiro, a menos que precise do enunciado de uma questão):
- **Pontos fortes**: tópicos com nota ≥ 8 e lacunas superadas (a revisão anterior funcionou).
- **Pontos fracos**: tópicos com nota < 6, erros conceituais, lacunas recorrentes (2x ou mais).
- **Efeito das revisões**: compare nota da sessão × nível anterior (↑ ↓ =) e diga se a revisão surtiu efeito.
- **Objetivas**: separe erro de conteúdo × leitura × pegadinha × chute; muitos erros de leitura pedem
  treino de técnica, não de conteúdo.
- **Prioridades**: use a lista "Prioridade de lacunas" (importância × déficit × recorrência). Pegue as 5 a 8 primeiras.

## 3. Material de revisão dirigido (DOCX e PDF)
1. Para cada lacuna prioritária, busque o conteúdo no **material-base**: localize o tópico em
   `materiais/<slug>/indice.md` e leia só as linhas correspondentes de `texto.md`. Complete com lei, súmulas e
   jurisprudência consolidadas que você conheça com segurança (sem inventar números; sinalize "conferir").
2. Escreva `sessoes/<sessão>/revisao.md` seguindo **exatamente** `references/modelo-revisao.md`, com as quatro
   partes: desempenho; **correção de cada resposta** (enunciado completo e feedback detalhado, lidos de
   `metricas --pontos`); lacunas prioritárias; pontos fortes e rumos. O texto é **prosa justificada, sem
   marcadores**. Nas lacunas, vale o princípio de **só o que falta**.
3. `python scripts/gerar_material.py sessoes/<sessão>/revisao.md` → `revisao.pdf` (reportlab, fontes embutidas,
   layout padrão com capa, sumário e rodapé) e `revisao.docx` (biblioteca `docx`, Node; `npm install` uma vez).
   Sem Node, sai só o PDF. Se nada for gerado, entregue o `.md` e oriente `pip install -r requirements.txt` e `npm install`.

## 4. Flashcards (só lacunas importantes)
1. Leia a seção "Flashcards já gerados" dos arquivos de tópico envolvidos (`python scripts/sessao.py topico ...`)
   para não repetir.
2. Regras: **1 lacuna autônoma = 1 card**; importância ≥ 2 ou recorrente; erros conceituais sempre viram card
   (com callout 🚫 Pegadinha). Nada de card sobre o que a pessoa já acertou com certeza.
3. **Formato estilo Notion, obrigatório:** siga `references/modelo-flashcard-notion.md`. A frente é texto puro; o
   verso é HTML inline numa única linha (wrapper, resposta direta com grifo amarelo, `<hr>`, blocos com emoji,
   no máximo 1 callout, citação cinza).
4. Grave `sessoes/<sessão>/flashcards.tsv` (UTF-8, separado por TAB, sem cabeçalho, 3 colunas):
   `frente<TAB>verso<TAB>tags`. Tags separadas por espaço, incluindo **obrigatoriamente**
   `<slug-da-disciplina>::<slug-do-tópico>` (minúsculas, sem acento, hífens; ex.: `direito-civil::usucapiao`)
   e `revisao-voz-alta`.
5. `python scripts/sessao.py cards sessoes/<sessão>` → **valida o formato** (recusa o arquivo e aponta os erros),
   remove duplicados e registra os cards no histórico. Corrija até passar.
6. **Anki (opcional)**: se houver uma ferramenta de Anki conectada nesta sessão (MCP ou AnkiConnect), ofereça
   enviar os cards para o deck `Revisão em voz alta::<Disciplina>`; se não houver, oriente a importação:
   Anki → Arquivo → Importar → `flashcards.tsv` → separador Tab, permitir HTML, campo 3 = Tags.

## 5. Atualizar o dashboard
O `consolidar` e o `cards` já regeneram `dashboard/dados.js`; falta só publicar.
- **Ferramenta Artifact disponível:**
  - Leia `desempenho/dashboard.json`.
  - **Sem URL:** publique `dashboard/index.html` com
    `files: {"dados.js": "dashboard/dados.js", "dados.exemplo.js": "dashboard/dados.exemplo.js"}`, favicon `📈` e
    descrição "Painel de desempenho das sessões de revisão". Grave `{"url": "<url>"}` em `desempenho/dashboard.json`.
  - **Com URL:** publique de novo com `url` e o mesmo `files` (mesmo link; cada publicação vira uma versão). Se a
    publicação for recusada por o artefato não ter sido lido nesta conversa, faça `action: "read"` nessa URL e publique de novo.
- **Sem a ferramenta Artifact:** diga que basta abrir `dashboard/index.html` no navegador (os dados já estão atualizados).
- Consolidação de sessão pendente disparada na abertura de outra sessão: **não** publique; a próxima sessão encerrada publica tudo.

## 6. Entrega no chat
**Modo de correção final:** a pessoa ainda não viu nenhuma correção, então o fechamento traz o **feedback completo
de cada pergunta**, no mesmo nível de detalhe da correção imediata. Uma tabela sozinha não basta. Para cada
pergunta, em ordem, repita o **enunciado completo** (campo `enunciado` do registro, que `metricas --pontos` mostra)
e, logo abaixo, a correção:

```
---
**Pergunta 3/8** · Direito Empresarial · Desconsideração inversa
> <enunciado completo, como foi feito na sessão>

**Nota 4,5/10**
✅ <ponto entregue>
◐ <ponto parcial>. Faltou: <o quê>
❌ <ponto não entregue>. <conteúdo esperado e fundamento em 1 ou 2 linhas>
⚠️ Erro conceitual: <o que foi dito> → correto: <o que é>
**Para fechar o ponto na prova:** <1 ou 2 frases com o núcleo que o examinador procura>
```
Nas objetivas, o mesmo formato traz: o enunciado com as alternativas, o gabarito comparado com a resposta e a
certeza declarada, por que a correta está certa, o erro de cada distratora, o tipo de erro e a regra em uma frase
("Guarde:").

Depois de todas as perguntas, mostre uma **tabela-síntese** (# · tópico · nota) e siga para o resumo abaixo.
Perguntas já corrigidas durante a sessão (quando a pessoa mudou de modo no meio) entram só na tabela-síntese.

Envie o PDF, o DOCX e o TSV (use a ferramenta de envio de arquivos, se existir) e escreva um resumo curto:
```
**Sessão <tema>** — <n> perguntas · nota média <x>
**Melhor:** <tópicos e por quê>
**Pior:** <tópicos e lacunas centrais>
**Revisões anteriores:** <surtiram efeito? ↑↓=>
**Rumos:** <3 ações concretas e datas das próximas revisões (do painel)>
Arquivos: revisao.pdf · revisao.docx · flashcards.tsv (<k> cards) · Dashboard: <link ou dashboard/index.html>
```
