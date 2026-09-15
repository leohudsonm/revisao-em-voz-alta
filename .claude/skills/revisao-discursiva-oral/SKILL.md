---
name: revisao-discursiva-oral
description: Sessão de revisão para PROVA DISCURSIVA (questões dissertativas, sentença cível/criminal, peças, prova oral) com respostas faladas por ditado. O Claude faz uma pergunta por vez a partir do material anexado, corrige só o conteúdo com rubrica de pontos esperados, registra o desempenho e, no fim, chama a análise de desempenho. Use quando a pessoa pedir "revisão discursiva", "me faça perguntas sobre este material", "treinar 2ª fase", "revisar em voz alta", "treinar sentença", ou anexar material pedindo perguntas abertas. NÃO use para questões de múltipla escolha ou certo/errado (skill revisao-objetiva).
---

# Revisão discursiva oral

Objetivo: fazer a pessoa **produzir conteúdo** jurídico de alto nível (doutrina, jurisprudência, interpretação que não
está escrita na lei, aplicação a caso concreto) e medir, ponto a ponto, o que ela entrega e o que falta.
A resposta é **falada**: avalia-se o **conteúdo**, nunca a forma.

## 1. Abertura (barata em tokens)
1. Rode `python scripts/sessao.py abrir`. É a **única** leitura de histórico nesta etapa.
2. Se houver **sessões não consolidadas**, rode `python scripts/sessao.py consolidar <sessão>` em cada uma antes de seguir.
3. Se o perfil estiver **AUSENTE**, faça o onboarding numa única mensagem (cargo e tribunal, banca, fase, se há
   sentença/peça, disciplinas prioritárias, data da prova) e grave `perfil.md` seguindo `perfil.exemplo.md`.
   Se já existir, leia `perfil.md` (é curto).
4. Diga em 2 a 4 linhas o **ponto de partida**: revisões vencidas, tópicos de nível baixo, tendência recente.
   Sem histórico, diga que esta sessão cria a linha de base.

## 2. Material
- **Arquivo novo** (PDF, DOCX, TXT, MD): `python scripts/extrair_material.py "<caminho>"`. Depois, transforme o
  esboço de `materiais/<slug>/indice.md` no mapa definitivo (tabela: disciplina, tópico, subtópicos-chave, linhas
  em `texto.md`, importância 1–3). Para montar o mapa, use os títulos candidatos e leia só trechos por amostragem.
  Use nomes de tópico **estáveis e curtos** (ex.: "Usucapião", "Prisão preventiva"): eles viram a chave do histórico.
  Se o tópico já aparece no painel, reutilize **exatamente** o mesmo nome.
- **Material já processado**: leia só `indice.md`.
- **PDF escaneado** (o script avisa): leia o original pelas páginas necessárias.
- **Sem material** (a pessoa só diz o tema): trabalhe com o conhecimento do modelo e avise que as referências devem
  ser conferidas com mais cuidado.
- **`banco/`**: se tiver arquivos sobre o assunto, use as questões reais e os espelhos como base das perguntas e
  das rubricas.

## 3. Plano da sessão
1. Tamanho: o do perfil (padrão 10; aceite o que a pessoa pedir).
2. Escolha dos tópicos, nesta ordem: (a) tópicos do material com revisão **vencida** ou nível < 6 no painel;
   (b) tópicos de importância 3 ainda sem histórico; (c) demais, variando.
3. Para cada tópico escolhido que já tem histórico, rode `python scripts/sessao.py topico "<disciplina>" "<tópico>"`
   **uma vez** e reserve ao menos uma pergunta que reteste uma **lacuna aberta** ou um **erro conceitual** anterior.
4. Crie a sessão: `python scripts/sessao.py nova --modo discursiva --tema "<tema>" --material <slug>`.
5. Anuncie em uma linha: quantas perguntas e quais tópicos. **Não** revele as perguntas nem as rubricas.

## 4. Como perguntar
- **Uma pergunta por vez**, com cabeçalho: `**Pergunta 3/10** · Direito Civil · Usucapião`.
- Questão com itens: faça **só o item (a)**; corrija; depois o (b), no mesmo cabeçalho (`3b`). Cada item é um registro.
- Nível de prova de carreira: cobrar o que **não** está literal na lei. Varie os tipos (ver `references/padroes-discursivas.md`):
  conceito e natureza jurídica; distinções; correntes doutrinárias; posição do STF/STJ e sua evolução; interpretação
  sistemática de dispositivo; caso concreto com solução fundamentada; e, se o perfil tiver sentença, pontos da peça
  (preliminares, prejudiciais, mérito, dosimetria, dispositivo, consectários).
- Enunciado enxuto, como em prova. Pode pedir "discorra", "diferencie", "resolva o caso", "posicione-se".
- Antes de enviar a pergunta, monte **mentalmente** a rubrica oculta (3 a 6 pontos com peso) conforme
  `references/rubrica.md`. Base: trecho do material (leia só as linhas do tópico), espelho do `banco/`, conhecimento consolidado.
- Adapte: duas notas ≥ 8 seguidas → aumente a dificuldade; duas < 4 → quebre o tema em perguntas menores.

## 5. Modos de correção
Leia `Modo de correção` e `Avaliação em segundo plano` no `perfil.md` (padrão: imediata, não). A pessoa pode
trocar a qualquer momento ("corrige só no final", "pode corrigir agora", "avalia em segundo plano"): mude
na hora e atualize o `perfil.md` para as próximas sessões.

| Modo | Durante a sessão | No fechamento |
|---|---|---|
| **Imediata** (padrão) | correção curta (formato abaixo) + próxima pergunta na mesma mensagem | resumo + PDF |
| **Final ("modo prova")** | **nenhuma** nota, comentário ou dica: registrar e fazer a próxima pergunta ("Resposta registrada." + pergunta) | correção de **cada** pergunta no chat (tabela da skill `analise-desempenho-revisao`) + PDF |

**Avaliação em segundo plano** (combina com os dois modos, mais útil no modo final): assim que a resposta chegar,
lance um subagente em segundo plano (ferramenta de agentes, `run_in_background: true`, modelo rápido) com o
modelo de `references/prompt-avaliador.md` preenchido — pergunta, rubrica oculta, linhas do material e a resposta
**literal**. O subagente corrige e roda o `registrar`; você apresenta a próxima pergunta **imediatamente**, sem
esperar. Regras:
- Monte a rubrica oculta **você mesmo** antes de delegar (é ela que garante a qualidade); o subagente só aplica.
- Quando o aviso de conclusão chegar, **não** mostre a nota no modo final; no máximo "Pergunta N registrada".
- Se o subagente relatar número de registro fora de ordem ou erro, confira com `metricas` no fechamento.
- Não encerre a sessão (Skill 3) enquanto houver avaliação em andamento.
- Sem ferramenta de agentes disponível: avalie você mesmo, em silêncio, e siga.

## 6. Como corrigir (só conteúdo)
Ignore estrutura, ordem, repetição, hesitação e vícios de fala. Termo jurídico evidentemente trocado pelo ditado
("usu capião", "art. mil duzentos e quarenta a") conta como dito corretamente. Resposta genérica que só "tangencia"
o ponto é **parcial**, não entregue.

Formato no chat (curto):
```
**Nota 6,5/10**
✅ <ponto entregue>
◐ <ponto parcial> — faltou: <o quê>
❌ <ponto não entregue> — <conteúdo esperado + fundamento em 1 linha>
⚠️ Erro conceitual: <o que foi dito> → correto: <o que é>
**Para fechar o ponto na prova:** <1 ou 2 frases com o núcleo que o examinador procura>
```
Em seguida, na **mesma mensagem**, a próxima pergunta (fluxo contínuo para quem responde falando).
No modo final, esse formato não aparece durante a sessão: a avaliação é feita e registrada, mas só é mostrada no fechamento.

## 7. Registro (obrigatório, antes de enviar a correção ou a próxima pergunta)
Grave um JSON por pergunta/item. Com Bash:
```bash
python scripts/sessao.py registrar sessoes/<sessão> <<'EOF'
{"tipo":"discursiva","disciplina":"Direito Civil","topico":"Usucapião","subtopico":"Usucapião familiar",
 "pergunta":"Requisitos da usucapião familiar e a natureza do 'abandono do lar'",
 "fonte":"material p. 12",
 "pontos":[{"ponto":"prazo de 2 anos e metragem até 250 m²","peso":"essencial","status":"entregou"},
           {"ponto":"abandono do lar como abandono patrimonial/familiar, não culpa","peso":"essencial","status":"faltou"},
           {"ponto":"imóvel urbano, propriedade dividida com ex-cônjuge","peso":"importante","status":"parcial"}],
 "nota":5.0,
 "lacunas":["Abandono do lar na usucapião familiar é abandono da família e do patrimônio, sem discutir culpa"],
 "lacunas_superadas":[],
 "erros_conceituais":[],
 "importancia":3}
EOF
```
Sem Bash (PowerShell): grave o JSON em `sessoes/<sessão>/_registro.json` e rode
`python scripts/sessao.py registrar sessoes/<sessão> --arquivo sessoes/<sessão>/_registro.json`.

Regras dos campos:
- `lacunas`: cada item é uma **afirmação autônoma do conteúdo que faltou** (até 20 palavras), que sirva de verso de
  flashcard. Nada de "não soube o conceito". Se a lacuna **já estava aberta** no tópico e a pessoa errou de novo,
  copie o texto exato de lá (é assim que o script conta a recorrência).
- `lacunas_superadas`: quando a pessoa entregar um ponto que estava nas **lacunas abertas** do tópico, copie o texto
  **exato** de lá.
- `erros_conceituais`: só afirmações erradas (não omissões), redigidas como a versão correta: "Prisão preventiva
  não tem prazo legal fixo (e não 'máximo de 180 dias')".
- `importancia`: 3 = tema recorrente/central na prova; 2 = relevante; 1 = detalhe.
- Pergunta pulada não é registrada.

## 8. Encerramento
Quando o plano terminar ou a pessoa disser "encerrar": diga "Encerrando e analisando o desempenho" e siga a skill
`analise-desempenho-revisao` para esta sessão. Se a pessoa sair sem encerrar, a próxima abertura consolida.
