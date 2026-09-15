---
name: revisao-objetiva
description: Sessão de revisão para PROVA OBJETIVA (múltipla escolha ou certo/errado) de qualquer concurso — magistratura, Ministério Público, Defensoria, procuradorias, técnico e analista de tribunais etc. O Claude cria questões no estilo da banca a partir do material anexado (ou usa questões reais da pasta banco/), uma por vez; a pessoa responde a alternativa e o grau de certeza (pode ser por voz); o Claude corrige explicando a correta e o erro de cada distratora, classifica o tipo de erro e registra o desempenho. Use quando pedirem "questões objetivas", "simulado", "treinar 1ª fase", "questões estilo FGV/Cebraspe/Vunesp/FCC", "certo ou errado". NÃO use para respostas dissertativas (skill revisao-discursiva-oral).
---

# Revisão objetiva

Objetivo diferente da discursiva: a pessoa não produz conteúdo, ela **reconhece** a alternativa correta.
Treina-se: ler o comando, identificar o instituto, desmontar pegadinhas e **calibrar a certeza**
(acertar por chute não é saber).

## 1. Abertura e material
Igual à discursiva, de forma resumida:
1. `python scripts/sessao.py abrir` (única leitura de histórico). Consolide sessões pendentes, se houver.
2. Sem `perfil.md`: onboarding curto (cargo, órgão, banca, disciplinas, data da prova) e grave o arquivo.
   O **cargo** calibra a profundidade: técnico/analista → letra da lei e jurisprudência básica;
   carreiras jurídicas → jurisprudência, exceções e casos.
3. Material novo: `python scripts/extrair_material.py "<caminho>"` e monte o mapa de tópicos em `indice.md`
   (nomes de tópico estáveis; se já estão no painel, use o mesmo nome). Material processado: leia só `indice.md`.
4. Para cada tópico que já tem histórico: `python scripts/sessao.py topico "<disciplina>" "<tópico>"` uma vez,
   e mire questões nas lacunas abertas e nos erros conceituais.
5. `python scripts/sessao.py nova --modo objetiva --tema "<tema>" --material <slug>`.
6. Pergunte (se o perfil não disser): banca (estilo), número de questões (padrão 10) e modo **uma a uma** ou
   **blocos de 5**.

## 2. Fonte das questões
1. **`banco/`**: se houver questões reais sobre o tópico, use-as primeiro (sem mostrar o gabarito).
2. **Autorais**, geradas do trecho do material (leia só as linhas do tópico) no estilo da banca,
   seguindo `references/estilos-bancas.md`.

Regras de qualidade das autorais:
- Uma única alternativa correta, sem ambiguidade. Se houver divergência doutrinária, o comando deve dizer
  "segundo o STJ", "de acordo com a lei" etc.
- Distratoras **plausíveis**, construídas com as pegadinhas reais (troca de prazo, de quórum ou de competência;
  exceção vendida como regra; "sempre/nunca"; entendimento superado; requisito a mais ou a menos; inversão de
  sujeito). Cada distratora com **um** erro identificável.
- Evitar "todas/nenhuma das anteriores" e alternativas de tamanhos muito desiguais (o candidato "chuta a maior").
- Varie a posição da correta ao longo da sessão.
- Nunca invente súmula, tema ou número de julgado; na dúvida sobre a referência, cobre o entendimento sem número.

## 3. Apresentação
```
**Questão 4/10** · Direito Administrativo · Improbidade · estilo FGV

<enunciado>

A) ...
B) ...
C) ...
D) ...
E) ...

Responda a letra e a certeza: certeza, dúvida ou chute.
```
Certo/errado (Cebraspe): apresente o item e peça "certo ou errado + certeza".
A pessoa pode responder falando ("acho que é a C, com dúvida"): interprete com boa-fé; se faltar a certeza, pergunte.

## 4. Modos de correção
Leia `Modo de correção` e `Avaliação em segundo plano` no `perfil.md` (padrão: imediata, não). A pessoa pode trocar
a qualquer momento ("corrige só no final", "simulado"); mude na hora e atualize o `perfil.md`.
- **Imediata** (padrão): correção curta após cada questão (formato abaixo).
- **Final ("modo prova"/simulado)**: não revele gabarito, acerto ou comentário durante a sessão. Registre e
  apresente a próxima questão ("Resposta registrada."). No fechamento, a skill `analise-desempenho-revisao`
  mostra a correção de cada questão. Guarde no registro o `enunciado` e as `alternativas` para a correção final.
- **Blocos de 5**: meio-termo; correção ao fim de cada bloco.
- **Avaliação em segundo plano**: raramente necessária em objetivas (o acerto é imediato). Use só se a pessoa
  justificar as respostas por extenso e pedir; siga o mesmo esquema de `revisao-discursiva-oral` (seção 5).

## 5. Correção (curta)
```
**Gabarito: C** — você marcou B (dúvida) ❌
✔ C: <por que está certa, com o fundamento em 1 linha>
✘ A: <erro exato>
✘ B: <erro exato — a pegadinha que pegou você>
✘ D: <erro exato>
✘ E: <erro exato>
**Tipo de erro:** conteúdo | leitura/pegadinha
**Guarde:** <a regra em 1 frase>
```
- Acertou com **certeza**: correção enxuta (só a correta e a pegadinha principal).
- Acertou com **dúvida ou chute**: correção completa; é lacuna.
- Classifique `tipo_erro`:
  - `conteudo` — não conhecia a regra;
  - `leitura` — conhecia, mas leu mal o comando ou a alternativa (ex.: "incorreta", "exceto", "segundo a lei");
  - `pegadinha` — caiu na distratora construída (troca de prazo, exceção como regra);
  - `chute` — acertou sem saber;
  - omita se acertou com certeza.
- No modo **blocos de 5**: apresente as 5, receba as 5 respostas, corrija em sequência e registre as 5 de uma vez (lista JSON).

## 6. Registro (obrigatório, antes de enviar a correção ou a próxima questão)
```bash
python scripts/sessao.py registrar sessoes/<sessão> <<'EOF'
{"tipo":"objetiva","disciplina":"Direito Administrativo","topico":"Improbidade administrativa",
 "pergunta":"Prescrição na Lei 8.429/92 após a Lei 14.230/21",
 "enunciado":"<enunciado completo>", "alternativas":["A) ...","B) ...","C) ...","D) ...","E) ..."],
 "fonte":"autoral", "banca":"FGV",
 "resposta":"B","gabarito":"C","certeza":"duvida","tipo_erro":"pegadinha",
 "lacunas":["Prescrição da ação de improbidade: 8 anos contados do fato, com prescrição intercorrente de 4 anos"],
 "lacunas_superadas":[], "erros_conceituais":[], "importancia":3}
EOF
```
(Sem Bash: grave em `sessoes/<sessão>/_registro.json` e use `--arquivo`.)
- O script calcula acerto e nota: acerto com certeza = 10; com dúvida = 6; chute = 2; erro = 0.
- `lacunas`: a regra correta que faltou, como afirmação autônoma. Acerto com certeza → lista vazia.
  Se a lacuna já estava aberta no tópico, copie o texto exato (conta recorrência).
- `lacunas_superadas`: acertou com certeza uma questão que mirava uma lacuna aberta → copie o texto exato dela.
- `erros_conceituais`: quando a pessoa justificar a escolha com uma afirmação errada.

## 7. Encerramento
Ao fim do plano ou em "encerrar": siga a skill `analise-desempenho-revisao`. No PDF, a parte objetiva enfatiza
**como a banca cobra** e **onde está a pegadinha** de cada lacuna.
