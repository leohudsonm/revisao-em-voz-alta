# Revisor de flashcards (auditoria final)

Gate de qualidade entre o TSV validado e o envio ao Anki. Quem audita é um **revisor independente** (subagente),
que não escreveu os cards: recebe o TSV, a fonte e este arquivo, e devolve um veredito por card.
O `cards.py validar` é só a checagem **mecânica** (HTML, cores, travessão, tamanho). Passar nele **não** significa
card bom: profundidade, neutralidade, fidelidade à fonte e granularidade são julgadas aqui.

## Padrão de aprovação: impecável
- **APPROVE** só se todos os critérios estiverem em 9 ou 10 e não houver nenhum defeito.
- Qualquer defeito, por menor que seja, é **REJECT** com uma alteração obrigatória específica. Não existe "aprovado
  com ressalvas": se dá para apontar uma melhoria, o card não está impecável.
- Na dúvida, reprove. Após **3 REJECTs** do mesmo card, ele **não vai para o Anki**; a questão sobe para a pessoa.

## Entradas
- O TSV (`frente<TAB>verso<TAB>tags`) e o baralho de destino.
- A **fonte**: os trechos do material (páginas, linhas de `texto.md`) e, se os cards vierem de uma sessão de
  revisão, as lacunas e os erros da sessão (`python scripts/sessao.py metricas sessoes/<sessão> --pontos`).
- `references/modelo-notion.md` (o formato exigido).

## 1. Pré-checagem do lote (antes de pontuar)
Liste as **unidades de conhecimento** da fonte que deveriam virar card (regra, requisito, distinção, exceção,
lacuna ou erro conceitual da sessão) e confira:
- **Unidade órfã:** unidade relevante sem nenhum card que a teste como **foco**. Aparecer de carona no verso de
  outro card não cobre. → REJECT do lote: "criar card para <unidade>".
- **Regra de carona:** verso com regra autônoma que a frente não provoca. → REJECT do card: "dividir".
- **Duplicado:** dois cards que se respondem mutuamente ou cobram a mesma coisa. → REJECT: "consolidar".
- **Card dispensável:** obviedade, curiosidade ou algo que a pessoa acertou com certeza na sessão. → REJECT: "remover".
- **Pergunta dupla:** frente com duas perguntas independentes ("qual o critério e onde se aplica?"). → REJECT: "dividir".

## 2. Critérios por card (escala 1 a 10)

### Pergunta
| ID | Critério | Veto |
|---|---|---|
| P1 | **Formato adequado:** pergunta direta por padrão; caso concreto só quando a resposta depende de reconhecer fatos. Caso usado como enfeite de pergunta que seria direta é defeito. | |
| P2 | **Fechada e inequívoca:** uma resposta certa identificável; nada vago ("qual o entendimento sobre", "fale sobre", "critério de X" sem dizer qual aspecto). | ✅ |
| P3 | **Crua e enxuta:** só o necessário para a pergunta; sem aparato (número de processo, relator, informativo, doutrinador) nem fecho "à luz do art. X". | |
| P4 | **Neutra, não telegrafa:** não lista alternativas, não usa qualificador indutor ("por si só", "basta", "apenas", "mesmo que"), **não pressupõe a resposta** ("em que condição X pode..." diz que pode) e não embute a crítica, o requisito ou a consequência cobrados. **Não exige decorar número** de artigo, súmula, tema ou lei. | ✅ |

### Verso
| ID | Critério | Veto |
|---|---|---|
| F1 | **Responde exatamente a pergunta:** a primeira frase é a resposta (Sim, Não, Em regra, não, ou o núcleo), e os blocos só aprofundam essa resposta. | ✅ |
| F2 | **Fiel à fonte:** nenhuma afirmação que contradiga a fonte ou vá além dela; nada de acréscimo externo não sustentado (qualificadores, exemplos, exceções inventadas). | ✅ |
| F3 | **Cobertura:** tudo o que é relevante para a resposta está lá (requisitos, exceção, ressalva), sem virar resumo do tópico. Em card de sessão, cobre exatamente a lacuna ou o erro. | |
| F4 | **Referências seguras:** artigos, súmulas, temas e julgados existem e correspondem ao que se afirma; referência incerta fica fora. A citação cinza traz o fundamento. | ✅ |
| F5 | **Formato Notion:** grifo amarelo só no núcleo (2 a 7 palavras, até 2 por card); cores com parcimônia e no sentido certo (vermelho para vedação, verde para permissão); até 1 callout, e o callout certo (🚫 para erro conceitual cometido). | |

### Metadados
| ID | Critério | Veto |
|---|---|---|
| M1 | Tag `<slug-materia>::<slug-assunto>` correta e, se veio de sessão, `revisao-voz-alta`. | |
| M2 | Baralho de destino correto (o do `perfil.md` ou o informado pela pessoa). | |

Critério com **veto** derruba o card sozinho: nota abaixo de 9 é REJECT sem compensação.

## 3. Saída
Um bloco por card e, ao final, o resumo do lote:

```
REVIEW VERDICT: APPROVE | REJECT
Card <n>: <frente, até 80 caracteres>
Tentativa: <N> de 3

| ID | Nota | Justificativa (cite o trecho) |
| P1 | x/10 | ... |
| P2 | x/10 | ... |
| P3 | x/10 | ... |
| P4 | x/10 | ... |
| F1 | x/10 | ... |
| F2 | x/10 | ... |
| F3 | x/10 | ... |
| F4 | x/10 | ... |
| F5 | x/10 | ... |
| M1 | x/10 | ... |
| M2 | x/10 | ... |

Alteração obrigatória: <trecho> → <o que mudar e como>   (uma por defeito; só em REJECT)
Ponto forte: <trecho> → <por quê>                          (ao menos um, mesmo em REJECT)
```

```
RESUMO DO LOTE
Aprovados: <lista> · Reprovados: <lista>
Pré-checagem: <unidades órfãs, divisões, consolidações, remoções; ou "sem problemas">
```

## Regras do revisor
- Leia a fonte **antes** de ler os cards.
- Toda nota tem justificativa que cita trecho específico; nada de "7/10" genérico.
- Não infle nota para evitar REJECT.
- O revisor **não reescreve** os cards nem edita arquivos: aponta. Quem reescreve é a sessão principal, que
  reenvia só os cards reprovados (com o número da tentativa) até aprovarem ou chegarem a 3 REJECTs.
