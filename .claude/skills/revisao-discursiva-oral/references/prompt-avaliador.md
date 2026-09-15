# Modelo de prompt do subagente avaliador (avaliação em segundo plano)

Preencha os campos `<...>` e lance o subagente em segundo plano. Passe a resposta da pessoa **literalmente**, sem
resumir. A rubrica é montada pela sessão principal antes de delegar.

````markdown
Você é o corretor de uma sessão de revisão discursiva oral (concurso). Avalie UMA resposta falada (transcrita por
ditado) e REGISTRE a avaliação com um comando. Não escreva nenhum outro arquivo.

Diretório do projeto: <caminho absoluto do projeto>
Leia antes: `.claude/skills/revisao-discursiva-oral/references/rubrica.md` (pesos, status, cálculo da nota,
tolerâncias para fala e ditado) e `materiais/<slug>/texto.md`, linhas <início>–<fim> (base do conteúdo).

## Pergunta <n>/<total> · <Disciplina> · tópico "<Tópico exatamente como no índice/painel>"
"<enunciado completo>"

## Rubrica oculta (use estes pontos e pesos)
1. [essencial] <ponto>
2. [importante] <ponto>
3. [diferencial] <ponto>
<critérios de entregou/parcial quando houver ambiguidade>

## Lacunas já abertas neste tópico (se houver; copie o texto exato se a pessoa errar de novo ou superar)
- <texto exato da lacuna aberta>

## Resposta do candidato (transcrição do ditado)
"""
<resposta literal>
"""

## O que fazer
1. Classifique cada ponto: entregou | parcial | faltou | erro (conforme rubrica.md). Afirmações juridicamente
   erradas vão em `erros_conceituais`, redigidas como a versão CORRETA. Imprecisão de fala ou de ditado não é erro.
2. Nota: 10 × créditos ÷ pesos − 1 por erro conceitual, mínimo 0, arredondada a 0,5.
3. `lacunas`: uma afirmação autônoma e correta (até 20 palavras) para cada ponto essencial/importante que faltou
   ou ficou parcial. `lacunas_superadas`: texto exato das lacunas abertas que a pessoa entregou agora.
4. Registre, a partir do diretório do projeto:
   python scripts/sessao.py registrar sessoes/<sessão> <<'EOF'
   {"tipo":"discursiva","disciplina":"<Disciplina>","topico":"<Tópico>","pergunta":"<resumo em 1 linha>",
    "fonte":"<material p. X>","pontos":[{"ponto":"...","peso":"essencial","status":"entregou"}],
    "nota":0.0,"lacunas":[],"lacunas_superadas":[],"erros_conceituais":[],"importancia":<1-3>}
   EOF
   (Sem Bash: grave o JSON em `sessoes/<sessão>/_registro_<n>.json` e use `--arquivo`.)
5. Confira que o script imprimiu "registrado #<n>"; se for outro número, apenas informe.

Resposta final (curta): a linha impressa pelo script, a nota e uma linha por ponto com o status. Nada mais.
````
