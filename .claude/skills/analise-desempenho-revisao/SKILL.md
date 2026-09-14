---
name: analise-desempenho-revisao
description: Fecha uma sessão de revisão (discursiva ou objetiva). Consolida o desempenho no histórico enxuto (painel e arquivos de tópico, via script), analisa onde a pessoa foi melhor e pior, gera um PDF de revisão dirigido SÓ às lacunas — com base no material de estudo usado — e cria flashcards das lacunas importantes (TSV importável no Anki). Use quando a pessoa disser "encerrar", "fechar a sessão", "analisar meu desempenho", "gerar o material de revisão/PDF", "flashcards das lacunas", ou ao fim do plano de uma sessão das skills revisao-discursiva-oral e revisao-objetiva.
---

# Análise de desempenho e material de revisão

Ordem obrigatória: **consolidar → analisar → PDF → flashcards → resumo no chat.**
Consolidar primeiro garante que o histórico é salvo mesmo se algo falhar depois.

## 1. Consolidar (script, sem reescrever nada à mão)
1. Descubra a sessão (a atual; ou a mais recente com `consolidada: false`, que o `abrir` lista).
2. `python scripts/sessao.py metricas sessoes/<sessão>` → guarde a saída: é a base da análise
   (nota por tópico, nível anterior, tendência, lacunas priorizadas).
3. `python scripts/sessao.py consolidar sessoes/<sessão>` → atualiza `estado.json`, reescreve `painel.md`
   (limitado a 80 linhas), os arquivos de tópico e marca a sessão como consolidada.
   Regras aplicadas pelo script: ver `references/formato-desempenho.md`.

Se for uma consolidação de **sessão antiga pendente** disparada na abertura de outra sessão, pare aqui
(sem PDF nem cards) e volte para a sessão nova.

## 2. Analisar
Com a saída de `metricas` (não releia o `sessao.jsonl` inteiro, a menos que precise do enunciado de uma questão):
- **Pontos fortes**: tópicos com nota ≥ 8 e lacunas superadas (a revisão anterior funcionou).
- **Pontos fracos**: tópicos com nota < 6, erros conceituais, lacunas recorrentes (2x ou mais).
- **Efeito das revisões**: compare nota da sessão × nível anterior (↑ ↓ =) e diga se a revisão surtiu efeito.
- **Objetivas**: separe erro de conteúdo × leitura × pegadinha × chute; muitos erros de leitura pedem
  treino de técnica, não de conteúdo.
- **Prioridades**: use a lista "Prioridade de lacunas" (importância × déficit × recorrência). Pegue as 5 a 8 primeiras.

## 3. PDF de revisão dirigido
1. Para cada lacuna prioritária, busque o conteúdo no **material-base**: localize o tópico em
   `materiais/<slug>/indice.md` e leia só as linhas correspondentes de `texto.md`. Complete com lei, súmulas e
   jurisprudência consolidadas que você conheça com segurança (sem inventar números; sinalize "conferir").
2. Escreva `sessoes/<sessão>/revisao.md` seguindo **exatamente** `references/modelo-revisao.md`.
   Princípio: **só o que falta**. Não resuma o que a pessoa já domina; pontos fortes ocupam poucas linhas.
3. `python scripts/gerar_pdf.py sessoes/<sessão>/revisao.md` → `revisao.pdf`.
   Se o `reportlab` não estiver instalado, entregue o `.md` e oriente `pip install -r requirements.txt`.

## 4. Flashcards (só lacunas importantes)
1. Leia a seção "Flashcards já gerados" dos arquivos de tópico envolvidos (`python scripts/sessao.py topico ...`)
   para não repetir.
2. Regras: **1 lacuna autônoma = 1 card**; importância ≥ 2 ou recorrente; erros conceituais sempre viram card.
   Frente = pergunta direta que exige a lembrança ativa (não "fale sobre X"). Verso = resposta curta (até ~60
   palavras) + fundamento. Nada de card sobre o que a pessoa já acertou com certeza.
3. Grave `sessoes/<sessão>/flashcards.tsv` (UTF-8, separado por TAB, sem cabeçalho, 3 colunas):
   `frente<TAB>verso<TAB>tags`. Tags separadas por espaço, incluindo **obrigatoriamente**
   `<slug-da-disciplina>::<slug-do-tópico>` (minúsculas, sem acento, hífens; ex.: `direito-civil::usucapiao`)
   e `revisao-voz-alta`. Quebras de linha dentro do verso: use `<br>`.
4. `python scripts/sessao.py cards sessoes/<sessão>` → remove duplicados e registra os cards no histórico.
5. **Anki (opcional)**: se houver uma ferramenta de Anki conectada nesta sessão (MCP ou AnkiConnect), ofereça
   enviar os cards para o deck `Revisão em voz alta::<Disciplina>`; se não houver, oriente a importação:
   Anki → Arquivo → Importar → `flashcards.tsv` → separador Tab, permitir HTML, campo 3 = Tags.

## 5. Entrega no chat
Envie o PDF e o TSV (use a ferramenta de envio de arquivos, se existir) e escreva um resumo curto:
```
**Sessão <tema>** — <n> perguntas · nota média <x>
**Melhor:** <tópicos e por quê>
**Pior:** <tópicos e lacunas centrais>
**Revisões anteriores:** <surtiram efeito? ↑↓=>
**Rumos:** <3 ações concretas e datas das próximas revisões (do painel)>
Arquivos: revisao.pdf · flashcards.tsv (<k> cards)
```
