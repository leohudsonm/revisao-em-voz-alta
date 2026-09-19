# Modelo do flashcard: frente direta e verso no estilo Notion

Adaptado do padrão dos flashcards do Revisáculo (estilo Notion, HTML inline). O que muda aqui é só o que é próprio
deste projeto: **perguntas diretas por padrão** e a âncora por tipo de fonte (livro, lei, questão, lacuna de sessão).

Cada linha do TSV é um card: `frente<TAB>verso<TAB>tags`, UTF-8, sem cabeçalho.
- **Frente:** texto puro, sem HTML, sem emoji, sem travessão.
- **Verso:** HTML inline no estilo Notion, **numa única linha** (sem quebras nem TAB). Nos exemplos abaixo aparece
  quebrado só para leitura.
- **Tags:** separadas por espaço, com `<slug-materia>::<slug-assunto>` (minúsculas, sem acento, hífens) e
  `revisao-voz-alta` se vier de sessão.

`python .claude/skills/flashcards-estudo/scripts/cards.py validar ARQ.tsv` confere a parte mecânica.

---

# FRENTE

## 1. Formato: pergunta direta é a regra
- **Pergunta direta** sempre que possível: conceito, requisito, efeito, prazo, rol, quem pode, quem é atingido,
  distinção entre institutos. Leitura mais rápida = mais cards revisados por sessão. **Em dúvida, prefira a direta.**
- **Caso concreto só quando necessário:** quando a resposta exige **reconhecer a situação** nos fatos (subsunção,
  pegadinha que só aparece diante de fatos). Nesse caso: um parágrafo curto (até ~400 caracteres), começando com
  artigo ("Um sócio...", "Uma sociedade..."), só os fatos que decidem a resposta e o quesito cru e neutro no final.
  Caso usado como enfeite de uma pergunta que seria direta é defeito.
- **Pergunta vaga não é pergunta direta:** "Qual o entendimento sobre X?", "Fale sobre X", "Explique X" e "Qual o
  critério de X?" sem dizer qual aspecto são vedadas.
- **Uma pergunta só.** Frente com duas perguntas independentes ("qual o efeito e qual o prazo?") vira dois cards.

## 2. Neutra: a frente não entrega a resposta (veto)
- **Não nomeia a propriedade testada pedindo só sim ou não.** "São cumulativos?", "O rol é taxativo?", "Extingue ou
  anula?", "Suspende o processo?", "Exige prova prévia de X?": quem lê percebe que a pergunta só existe porque a
  resposta surpreende, e acerta sem saber. Pergunte o **conteúdo**:
  - Errado: "Desvio de finalidade e confusão patrimonial são requisitos cumulativos?" → Certo: "Quais são os
    requisitos da desconsideração pela teoria maior?" (a alternatividade vem na resposta).
  - Errado: "A desconsideração extingue ou anula a pessoa jurídica?" → Certo: "Qual o efeito da desconsideração
    sobre a existência da pessoa jurídica?"
  - Errado: "Todos os sócios podem ser atingidos?" → Certo: "Quais sócios ou administradores podem ser atingidos?"
  - Sim ou não continua permitido quando a pergunta não sugere o lado: "Um administrador que não é sócio pode ser
    atingido pela teoria menor?".
- **Não lista alternativas** ("A ou B?", "ou não?").
- **Sem qualificador indutor:** "por si só", "basta", "apenas", "mesmo que", "ainda que", "sem mais".
- **Não pressupõe a resposta:** "Em que condição X pode ser atingido?" já diz que pode.
- **Não importa o rótulo ou a conclusão jurídica** para os fatos ("o abuso da personalidade praticado por...").
- **Não embute a condição que destrava a resposta** nem a crítica, o requisito ou a consequência cobrados.
- **Palavras de ligação também telegrafam:** "era gerente **mas** se retirou" marca o fato que isenta; use "e depois".

## 3. A frente puxa tudo o que o verso cobra
Se o verso traz uma regra autônoma que a pergunta não provoca (ex.: a responsabilidade do conselho fiscal escondida
num card sobre "quais sócios são atingidos"), essa regra vira **card próprio**. O verso só aprofunda a resposta.

## 4. Sem aparato e sem decoreba de número
- Sem número de processo, relator, informativo, doutrinador ou obra na frente.
- **Nunca exige decorar número** de artigo, súmula, tema ou lei: nada de "qual artigo", "qual o fundamento legal",
  "o que dispõe a Súmula N". Números ficam na âncora, na prosa e na citação.

---

# VERSO (estilo Notion)

> O visual é compacto, mas **o verso continua ensinando o raciocínio**: alvo de **1.100 a 1.900 caracteres de texto
> visível** (sem contar as tags HTML e sem contar a tabela). Acima de 1.900 só com necessidade; nunca acima de 2.600.
> Abaixo de ~900, suspeite de card raso.

## 1. Wrapper obrigatório
Sempre o primeiro caractere do campo; nada fica fora dele, nem a citação:
```html
<div style="font-family:-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;font-size:16px;line-height:1.5;color:#37352F;">
...conteúdo...
</div>
```

## 2. Blocos de texto
| Elemento | Snippet |
|---|---|
| Parágrafo padrão | `<p style="margin:0 0 8px;">...</p>` |
| Rótulo de bloco (emoji + título) | `<p style="margin:0 0 6px;">💡 <b>Título do bloco.</b> texto...</p>` |
| Separador (após a resposta direta) | `<hr style="border:none;border-top:1px solid #E9E9E7;margin:12px 0;">` |
| Lista não ordenada | `<ul style="margin:0 0 12px;padding-left:20px;"><li style="margin:0 0 4px;">...</li></ul>` |
| Lista ordenada (âncora, requisitos, passos) | `<ol style="margin:0 0 12px;padding-left:20px;"><li style="margin:0 0 6px;">...</li></ol>` |
| Negrito | `<b>...</b>` (nunca `<strong>`) |
| Itálico (obras, expressões latinas) | `<i>...</i>` |

Todo `<p>`, `<ul>`, `<ol>`, `<li>` e `<table>` leva `style` inline. **Nunca `<br><br>` entre parágrafos**; `<br>`
isolado só dentro do mesmo parágrafo.

## 3. Grifo cirúrgico e cores
```html
<span style="background:#FDF3C0;padding:1px 3px;border-radius:3px;"><b>núcleo conceitual</b></span>
```
**2 a 7 palavras**, só o núcleo da unidade-foco, **nunca a frase inteira**, sempre com `<b>` dentro; no máximo 2 por
card (um por posição, em card de divergência ou distinção).

| Uso | Snippet |
|---|---|
| Vedação, negativa forte | `<span style="color:#A03A38;"><b>...</b></span>` |
| Permissão, requisito positivo | `<span style="color:#3B6A45;"><b>...</b></span>` |
| Prazo, marco temporal | `<span style="color:#2B5B9E;"><b>...</b></span>` |

Cores servem ao contraste, não para colorir o card. Proibido o markup antigo: `background-color: yellow`,
`color: red`, `color: darkgreen`.

## 4. Bloco-âncora (fiel à fonte, logo após o `<hr>`)
Rótulo por tipo de fonte (ver `fontes.md`) e itens em `<ol>`:
```html
<p style="margin:0 0 6px;">📚 <b>Doutrina:</b></p>
<ol style="margin:0 0 12px;padding-left:20px;">
<li style="margin:0 0 6px;">[formulação fiel do autor; o núcleo da unidade-foco em grifo]</li>
</ol>
```
- `📜 <b>Dispositivo:</b>`: texto da lei **verbatim**.
- `📚 <b>Doutrina:</b>`: formulação fiel da lição; opinião do autor atribuída a ele ("Para o autor, ...").
- `⚖️ <b>Tese do julgado:</b>`: ementa ou tese fiel, quando a fonte traz o julgado.
- `🎯 <b>Tese central:</b>`: tese da questão comentada.
Só o núcleo da unidade-foco recebe grifo; itens secundários entram sem grifo.

## 5. Explicação em prosa
De 1 a 3 blocos curtos, cada um com emoji no início, título em negrito e 2 a 4 linhas, com o dispositivo legal
**integrado e explicado** (dizendo o que a norma estabelece), nunca como rodapé seco. Listas só para conteúdo
genuinamente enumerativo. Sem fonte que explique, não invente: o verso fica mais curto.

## 6. Tabela comparativa (formato preferível quando o card compara)
Quando o objetivo é contrastar dois conceitos (desconsideração x imputação direta; teoria maior x menor; regime antes
x depois da lei nova), a tabela é **preferível à prosa**. Até 3 linhas de critérios, células curtas, uma tabela por
card, e ela **substitui** a prosa daquele ponto. Não conta no orçamento de caracteres.
```html
<table style="border-collapse:collapse;width:100%;font-size:14.5px;margin:0 0 12px;">
<tr><th style="border:1px solid #E9E9E7;padding:6px 8px;background:#F7F6F3;font-weight:600;">Critério</th><th style="border:1px solid #E9E9E7;padding:6px 8px;background:#F7F6F3;font-weight:600;">A</th><th style="border:1px solid #E9E9E7;padding:6px 8px;background:#F7F6F3;font-weight:600;">B</th></tr>
<tr><td style="border:1px solid #E9E9E7;padding:6px 8px;">...</td><td style="border:1px solid #E9E9E7;padding:6px 8px;">...</td><td style="border:1px solid #E9E9E7;padding:6px 8px;">...</td></tr>
</table>
```

## 7. Callout (no máximo UM por card, e só se agregar)
```html
<div style="background:#FBE4E4;border-radius:6px;padding:10px 12px;margin:8px 0;"><p style="margin:0;"><b style="color:#A03A38;">🚫 Pegadinha:</b> ...</p></div>
<div style="background:#FBF3DB;border-radius:6px;padding:10px 12px;margin:8px 0;"><p style="margin:0;"><b style="color:#8A6300;">🎯 Dica de prova:</b> ...</p></div>
<div style="background:#EDF3EC;border-radius:6px;padding:10px 12px;margin:8px 0;"><p style="margin:0;"><b style="color:#3B6A45;">🗝️ Para memorizar:</b> ...</p></div>
```
🚫 para erro conceitual cometido na sessão ou pegadinha de banca. O callout não substitui a prosa.

## 8. Citação final (obrigatória, última linha, dentro do wrapper)
```html
<p style="margin:12px 0 0;font-size:13px;color:#787774;"><em>(Art. 50 do CC; REsp 1.729.554/SP; André Santa Cruz, Manual de Direito Empresarial, pp. 626-627)</em></p>
```
Por tipo: livro → autor, obra e página; lei → lei e artigo; questão → banca, ano e base. Julgados só com a
referência que a fonte traz (sem inventar UF, relator ou data).

## 9. Esqueleto completo
```html
<div style="font-family:-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;font-size:16px;line-height:1.5;color:#37352F;">
<p style="margin:0 0 8px;"><b>Não</b>. [resposta direta em 1-2 frases, com o <span style="background:#FDF3C0;padding:1px 3px;border-radius:3px;"><b>núcleo conceitual</b></span> grifado]</p>
<hr style="border:none;border-top:1px solid #E9E9E7;margin:12px 0;">
<p style="margin:0 0 6px;">📚 <b>Doutrina:</b></p>
<ol style="margin:0 0 12px;padding-left:20px;"><li style="margin:0 0 6px;">[lição fiel da fonte]</li></ol>
<p style="margin:0 0 8px;">💡 <b>Por quê.</b> [prosa de 2 a 4 linhas, com o dispositivo integrado e explicado]</p>
<p style="margin:0 0 8px;">⚠️ <b>Exceção.</b> [se houver]</p>
<div style="background:#FBE4E4;border-radius:6px;padding:10px 12px;margin:8px 0;"><p style="margin:0;"><b style="color:#A03A38;">🚫 Pegadinha:</b> [opcional]</p></div>
<p style="margin:12px 0 0;font-size:13px;color:#787774;"><em>(fundamento; autor, obra, página)</em></p>
</div>
```
A resposta direta abre com `<b>Sim</b>`, `<b>Não</b>`, `<b>Em regra, não.</b>` quando a pergunta admite; nas
perguntas de conteúdo ("quais são", "qual o efeito"), abre com o núcleo da resposta.

## 10. Emojis
Sempre no início da linha, do parágrafo ou do item; nunca no meio da frase; nunca na frente. Temáticos primeiro
(🏢 empresarial, ⛓️ penal, 💰 tributário, 👪 família, 🛒 consumidor, 🌳 ambiental...), explicativos quando o tema é
abstrato (💡 📋 ⚖️ ⚠️ 🔁 🆚 🗓️ 📌). Tabela completa em `emojis.md`.

## 11. Checklist visual rápido
- [ ] Começa com o wrapper e termina com `</div>`
- [ ] Resposta direta no 1º `<p>`, com grifo no núcleo
- [ ] `<hr style="...">` depois da resposta direta
- [ ] Bloco-âncora rotulado, em `<ol>`, fiel à fonte
- [ ] Toda tag de bloco com `style` inline; `<b>`, nunca `<strong>`
- [ ] Grifo `#FDF3C0`, 2 a 7 palavras, com `<b>`
- [ ] No máximo 1 callout e 1 tabela
- [ ] Citação em `<em>(...)</em>` no `<p>` cinza, com a obra e a página
- [ ] 1.100 a 1.900 caracteres visíveis (sem a tabela)
- [ ] Sem travessão, sem markdown, sem `<br><br>`
