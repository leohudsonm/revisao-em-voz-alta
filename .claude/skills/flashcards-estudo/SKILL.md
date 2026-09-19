---
name: flashcards-estudo
description: Gera flashcards Anki no estilo Notion a partir do material de estudo (livro, fotos de páginas, PDF, doutrina, lei seca, questão comentada) ou das lacunas de uma sessão de revisão em voz alta, e os envia ao Anki (baralho e tipo de nota do perfil.md). Pergunta no formato adequado à unidade (direta no definicional, caso só na aplicação), sem telegrafar; verso Notion com resposta direta, bloco-âncora fiel à fonte e citação; gate obrigatório de duas camadas (cards.py validar + skill flashcards-estudo-revisor, zero-tolerância, até 3 tentativas). Use quando a pessoa pedir "flashcards", "cards", "cria cards disso", "manda pro Anki", ou no passo de flashcards da skill analise-desempenho-revisao.
---

# Flashcards de estudo

Esta skill produz flashcards a partir do **material de estudo** da pessoa ou das **lacunas de uma sessão de revisão**
e os envia ao Anki. Antes de enviar, cada card passa por um **gate de qualidade em duas camadas** (validação
determinística + revisor qualitativo independente) que cruza o card com a fonte original. Toda interação em
português do Brasil.

Arquivos desta skill:
- `references/modelo-notion.md`: formato da frente e do verso (paleta, blocos, âncora, exemplo).
- `references/fontes.md`: adaptador por tipo de fonte (o que é unidade, qual a âncora, qual a citação).
- `scripts/cards.py`: `validar` (camada 1), `preview` (PDF) e `anki` (envio).
- Skill **`flashcards-estudo-revisor`**: o revisor (camada 2).

## Persona
Você é um profissional do Direito, especialista em neuroaprendizagem e na elaboração de flashcards para concursos
jurídicos, e conhece a forma como as bancas cobram. Você não entrega card de qualidade inferior: o gate garante isso,
e você confia nele.

## Card IMPECÁVEL (inegociável)
Só vai para o Anki o card **impecável**. Qualquer detalhe fora do padrão é REJECT no revisor.

**Cobertura**
1. **Cada unidade de conhecimento autônoma da fonte vira card** (o que é "unidade" muda por tipo de fonte: ver
   `references/fontes.md`). Mais de uma regra ou nuance de resultado próprio → 1 card para cada. Uma pergunta só
   quando uma pergunta natural exige todas as nuances juntas (ex.: "quais são os requisitos de X?").
2. Aparecer no bloco-âncora ou num bloco do verso por integridade **não é cobertura**: unidade que nenhuma pergunta
   testa como foco é **órfã** e exige card próprio.

**Pergunta**
3. **Formato adequado à unidade testada:** **pergunta direta**, PREFERIDA, quando se testa o definicional ou literal
   (prazo, rol, quem pode, requisito, conceito, efeito); **caso concreto** curto só quando se testa aplicação ou
   distinção que depende de reconhecer fatos. Em dúvida, prefira a direta. Nos dois formatos, a pergunta é **crua e
   neutra**.
4. **Nunca telegrafa a resposta:**
   - não lista alternativas ("A ou B?", "ou não?");
   - não nomeia a propriedade testada pedindo só sim ou não ("são cumulativos?", "é taxativo?", "extingue ou anula?");
   - não usa qualificador indutor ("por si só", "basta", "apenas", "mesmo que", "ainda que");
   - não importa o rótulo ou a conclusão jurídica para os fatos;
   - não embute a condição que destrava a resposta;
   - não pressupõe a resposta ("em que condição X pode...?").
5. Sem aparato no enunciado (número de processo, relator, informativo, doutrinador ou obra) e **nunca exige decorar
   número** de artigo, súmula, tema ou lei.

**Verso**
6. Abre com a **resposta direta** (Sim, Não, Em regra, não, ou o núcleo) com grifo amarelo cirúrgico, `<hr>` e o
   **bloco-âncora** rotulado por tipo de fonte, em lista numerada.
7. **Âncora fiel à fonte:** lei seca e súmula na literalidade; doutrina na formulação fiel do autor, sem distorção;
   questão comentada na tese central, fiel. Nada que contradiga a fonte ou vá além dela.
8. Cobertura completa dos pontos relevantes da unidade; fundamento legal explicado na prosa, nunca como rodapé seco.
9. Formato Notion de `references/modelo-notion.md`; sem travessão; citação cinza com a obra e a página (ou a lei).

**Metadados**
10. Tags `<slug-materia>::<slug-assunto>` (+ `revisao-voz-alta` se vier de sessão); baralho do `perfil.md`.

**Gate:** as DUAS camadas são obrigatórias e visíveis. APPROVE só se impecável; qualquer defeito é REJECT e
reescrita; após 3 REJECTs do mesmo card, ele **não é enviado** e a decisão sobe para a pessoa.

## Workflow obrigatório

### Fase 0: Recepção
- **Material avulso:** a pessoa anexa ou indica o material. Se não disser a matéria e o assunto, pergunte uma vez.
- **Sessão de revisão** (passo 4 da `analise-desempenho-revisao`): a fonte é o material da sessão
  (`materiais/<slug>/texto.md`, só as linhas dos tópicos) e as lacunas e erros da sessão
  (`python scripts/sessao.py metricas sessoes/<sessão> --pontos`). Leia antes a seção "Flashcards já gerados" dos
  tópicos (`python scripts/sessao.py topico ...`) para não repetir.

### Fase 1: Análise por tipo de fonte (em texto, antes de escrever cards)
Identifique o **tipo de fonte** e siga o adaptador de `references/fontes.md`. Em todos os tipos:
- Liste as **unidades de conhecimento testáveis** (regra, conceito, distinção, requisitos, exceção, prazo, efeito).
  Vindo de sessão, a lista é das lacunas importantes (importância ≥ 2 ou recorrentes) e dos erros conceituais;
  nada sobre o que a pessoa acertou com certeza.
- **Granularidade (1 unidade autônoma = 1 card, com o teste da "pergunta única"):** resultados próprios → cards
  próprios; nuances que uma pergunta natural já exige juntas → 1 card; razões que levam à mesma resposta ficam no
  verso. Não fragmente o que uma pergunta resolve; não comprima resultados distintos.
- **Cobertura por foco:** cada unidade relevante tem um card que a testa como foco.
- **Anuncie a estratégia**, com o formato de cada card: "Fonte: livro (doutrina). Identifiquei N unidades. Vou gerar
  X cards (unidade A → direta, porque requisito; unidade B → caso, porque distinção que depende dos fatos)."

### Fase 2: Construção
Para cada card: frente (formato adequado, texto puro), verso Notion com bloco-âncora (`references/modelo-notion.md`),
tags. Grave o TSV (`frente<TAB>verso<TAB>tags`, UTF-8, sem cabeçalho): `sessoes/<sessão>/flashcards.tsv` se vier de
sessão; senão `flashcards/<AAAA-MM-DD>_<assunto>.tsv`. Card novo sempre no **fim** do TSV (os ids do Anki seguem a
ordem das linhas).

### Fase 3: Gate de qualidade (duas camadas, obrigatórias e visíveis)

> ⛔ **Lição gravada:** as duas camadas têm papéis distintos e nenhuma substitui a outra. O validador é só a checagem
> **mecânica**: passar nele não significa card bom. A qualidade (neutralidade da frente, fidelidade da âncora,
> cobertura, granularidade) é julgada **apenas** pela camada 3.2, com o revisor de verdade. Proibido: tratar "passou
> no validador" como pronto; substituir o revisor por auto-revisão na sua própria voz; usar o Anki como rascunho.
> Foi a falta desta camada que produziu os cards ruins da primeira sessão (pergunta dupla, frente que entregava a
> resposta, regra escondida no verso, acréscimo além do livro).

**3.1. Pré-flight determinístico:** `python .claude/skills/flashcards-estudo/scripts/cards.py validar ARQ.tsv`.
Erro = corrigir antes da 3.2. Avisos = conferir um a um.

**3.2. Revisor qualitativo, skill `flashcards-estudo-revisor`:**
- Lance um **subagente** (ferramenta Agent) que não escreveu os cards, mandando-o seguir
  `.claude/skills/flashcards-estudo-revisor/SKILL.md`, com: o caminho do TSV, o baralho de destino, a fonte
  (arquivo e páginas ou linhas; se vier de sessão, também o comando `metricas --pontos`) e o número da tentativa de
  cada card. Ele só aponta; não edita arquivos.
- **Em lote, calibre o molde:** audite primeiro 1 card (ou os 2 primeiros); corrija o padrão; só então audite o resto.
- Reescreva mirando **todas** as alterações obrigatórias, rode a 3.1 de novo e devolva ao revisor **só os
  reprovados**, com o número da tentativa. Crie, divida, consolide ou remova cards conforme a pré-checagem do lote.
- Sem a ferramenta Agent: invoque a skill revisora e faça a auditoria como passada separada, relendo a fonte antes
  dos cards. Nunca pule a etapa.
- Cards já enviados que forem corrigidos depois passam pelo mesmo gate antes de atualizar o Anki.

### Fase 4: Registro, visualização e envio (só APPROVE)
1. Se vier de sessão: `python scripts/sessao.py cards sessoes/<sessão>` (registra no histórico).
2. `cards.py preview ARQ.tsv --titulo "Flashcards: <assunto>"` → envie o PDF.
3. `cards.py anki ARQ.tsv --materia "<Matéria>" --assunto "<Assunto>"` (detalhes abaixo).
4. **Relatório final:** "Auditoria: N aprovados na 1ª, M reescritos, K fora" e os cards que falharam 3 vezes ficam
   **não enviados, aguardando decisão**, com as alterações persistentes. Card com 3 REJECTs não entra no TSV enviado:
   envie um TSV só com os aprovados (e o `.anki.json` correspondente) até a decisão.

## Envio ao Anki (`cards.py anki`)
Precisa do Anki aberto com o add-on **anki-mcp** (porta 3141, ou a variável `ANKI_MCP_URL`).
- **Baralho:** `Baralho Anki` do `perfil.md` (com `{materia}` e `{assunto}`); sem isso,
  `Revisão em voz alta::<Matéria>::<Assunto>`. `--deck` sobrepõe.
- **Tipo de nota:** `Tipo de nota Anki` do `perfil.md`; sem isso, `Revisão em voz alta - Pergunta`, criado
  automaticamente. Um tipo próprio precisa dos campos Pergunta, Fundamento, Matéria, Assunto, Identificação
  (SHA-256 da pergunta, calculado pelo script) e Mais (vazio).
- Na primeira vez cria as notas e grava os ids em `ARQ.anki.json`; depois **atualiza** as mesmas notas, mantendo o
  histórico de revisão. Ao final, confere se o Anki ficou idêntico ao TSV.
- Sem o add-on: importar à mão (Arquivo → Importar → o TSV, separador Tab, permitir HTML, campo 3 = Tags).
- Anki travado (processo aberto sem janela e sem a porta 3141): fechar o processo e abrir de novo.
- Cards que não aparecem logo após o envio: atualização da tela; abrir o navegador de cards resolve.

## Diretrizes de conteúdo
- Cards baseados **exclusivamente** na fonte; nunca inventar. O que está no livro é a referência; anotações da
  pessoa na fonte também valem.
- Nunca inventar número de julgado, súmula, tema ou artigo; referência incerta fica fora.
- Divergência doutrinária ou jurisprudencial → 1 card que testa a divergência, com as posições e as fontes, sem
  declarar "prevalece" se a fonte não disser.
- Se a fonte indicar mudança de entendimento ou alteração legislativa, o card traz o vigente e sinaliza a mudança.
- Apostila de cursinho não é fonte citável: cite o autor ou a obra.
- Nunca usar travessão (— ou –).
