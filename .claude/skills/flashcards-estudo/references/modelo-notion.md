# Modelo de flashcard (estilo Notion)

Cada linha do TSV é um card: `frente<TAB>verso<TAB>tags`, UTF-8, sem cabeçalho.
- **Frente:** texto puro, sem HTML e sem emoji.
- **Verso:** HTML inline no estilo Notion, **numa única linha** (sem quebras nem TAB).
- **Tags:** separadas por espaço, com `<slug-materia>::<slug-assunto>` (minúsculas, sem acento, hífens).

`python ~/.claude/skills/flashcards-estudo/scripts/cards.py validar <arquivo.tsv>` confere tudo isto.

## Frente (pergunta)
### Formato: pergunta direta é a regra
- **Pergunta direta** sempre que possível: conceito, requisito, efeito, prazo, rol, quem pode, quem é atingido,
  distinção entre institutos. É mais rápida de ler, o que significa mais cards revisados por sessão.
  **Em dúvida, prefira a direta.**
- **Caso concreto** só quando a resposta exige **reconhecer a situação** nos fatos (subsunção, pegadinha que só
  aparece diante de fatos). Nesse caso: um parágrafo curto (até ~400 caracteres), só os fatos que decidem a
  resposta e o quesito cru e neutro no final. Não use caso como enfeite de uma pergunta que seria direta.
- **Pergunta vaga não é pergunta direta:** "Qual o entendimento sobre X?", "Fale sobre X" e "Explique X" são vedadas.

### Pergunta neutra: a frente não entrega a resposta
- Sem qualificador que induza a resposta e sem listar alternativas ("A ou B?").
- **Não pressupor a resposta.** "Em que condição X pode ser atingido?" já diz que pode: pergunte "X pode ser
  atingido?" e deixe a condição para o verso ("Em regra, não. Só se...").
- Não embutir na pergunta a crítica, a consequência ou o requisito que o card cobra. Errado: "A crítica de que o
  legislador confundiu desconsideração com imputação direta recai sobre quais hipóteses?". Certo: "Qual é a crítica
  da doutrina às hipóteses de desconsideração previstas no CDC?".

### A frente puxa tudo o que o verso cobra
- Se o verso traz uma regra autônoma que a pergunta não provoca (ex.: a responsabilidade do conselho fiscal escondida
  num card sobre "quais sócios são atingidos"), essa regra vira **card próprio**. O verso só aprofunda a resposta da
  pergunta feita.

### Nunca exigir decorar número
- A pergunta cobra o **conteúdo** (regra, requisito, consequência, distinção), nunca "qual artigo", "qual dispositivo",
  "qual o fundamento legal", "o que dispõe a Súmula N" ou "o que diz o Tema N". Números ficam no verso e na citação cinza.
  Errado: "Quais os fundamentos legais da desconsideração inversa?" / "O que dispõe a Súmula 435 do STJ?".
  Certo: "Quais os requisitos da desconsideração inversa?" / "A empresa que deixa de funcionar no domicílio fiscal
  sem comunicar os órgãos competentes gera presunção que autorize o redirecionamento ao sócio-gerente?".
- Texto puro: sem emoji, sem HTML e sem travessão.

## Verso (fundamento)

### Paleta Notion (use só estas cores)
| Uso | Estilo inline |
|---|---|
| Texto base | `color:#37352F` (no wrapper) |
| **Grifo amarelo**: núcleo da resposta (único fundo de destaque) | `<span style="background:#FDF3C0;padding:1px 3px;border-radius:3px;"><b>...</b></span>` |
| Vermelho: vedação, "não", erro | `<span style="color:#A03A38;"><b>...</b></span>` |
| Verde: permissão, requisito | `<span style="color:#3B6A45;"><b>...</b></span>` |
| Azul: prazo, número, referência | `<span style="color:#2B5B9E;"><b>...</b></span>` |
| Separador | `<hr style="border:none;border-top:1px solid #E9E9E7;margin:12px 0;">` |
| Citação (fundamento) | `<p style="margin:12px 0 0;font-size:13px;color:#787774;"><em>(...)</em></p>` |

### Blocos
- Wrapper, sempre o primeiro e o último elemento:
  `<div style="font-family:-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;font-size:16px;line-height:1.5;color:#37352F;">` ... `</div>`
- Parágrafo: `<p style="margin:0 0 8px;">`. Rótulo de bloco: `<p style="margin:0 0 6px;">📋 <b>Título:</b></p>`.
- Listas: `<ul style="margin:0 0 12px;padding-left:20px;"><li style="margin:0 0 4px;">` e
  `<ol style="margin:0 0 12px;padding-left:20px;"><li style="margin:0 0 6px;">`.
- Tabela (opcional, no máximo 1 e até 3 linhas):
  - tabela: `<table style="border-collapse:collapse;width:100%;font-size:14.5px;margin:0 0 12px;">`
  - célula: `border:1px solid #E9E9E7;padding:6px 8px;`
  - cabeçalho: acrescente `background:#F7F6F3;font-weight:600;`
- Callout (opcional, **no máximo 1**), apenas um destes três:
  - 🚫 `<div style="background:#FBE4E4;border-radius:6px;padding:10px 12px;margin:8px 0;"><p style="margin:0;"><b style="color:#A03A38;">🚫 Pegadinha:</b> ...</p></div>`
  - 🎯 `<div style="background:#FBF3DB;border-radius:6px;padding:10px 12px;margin:8px 0;"><p style="margin:0;"><b style="color:#8A6300;">🎯 Dica de prova:</b> ...</p></div>`
  - 🗝️ `<div style="background:#EDF3EC;border-radius:6px;padding:10px 12px;margin:8px 0;"><p style="margin:0;"><b style="color:#3B6A45;">🗝️ Para memorizar:</b> ...</p></div>`

### Ordem do verso
1. **Resposta direta** em 1 ou 2 frases. Abra com `<b>Sim</b>.`, `<b>Não</b>.` ou `<b>Em regra, não.</b>` quando a
   pergunta admitir, e grife em amarelo o núcleo.
2. `<hr>`.
3. **De 1 a 3 blocos curtos**, cada um com emoji no início, título em negrito e 2 a 4 linhas (ou uma lista).
4. **Callout** opcional: 🚫 para confusão comum ou erro já cometido, 🎯 para como cai em prova, 🗝️ para macete.
5. **Citação cinza** com o fundamento: artigos, súmulas, temas, julgados e a obra-fonte, só referências seguras.

### Regras
- **Grifo cirúrgico:** de 2 a 7 palavras, sempre com `<b>` dentro. No máximo 2 grifos amarelos por card. Cores de
  texto só para contraste, com parcimônia.
- **Emojis:** só no início de linha, parágrafo ou item, nunca no meio da frase e nunca na frente. Emojis de apoio:
  💡 raciocínio, 📋 requisitos, ⚖️ consequência, ⚠️ exceção, 🔁 procedimento, 🆚 distinção, 🗓️ prazo, 📌 ponto-chave,
  🏢 empresarial, 🏛️ administrativo, ⛓️ penal, 💰 tributário, 🛒 consumidor, 👪 família, 🌳 ambiental.
- **Proibidos:** travessão (— ou –), `<strong>`, `<br><br>` entre parágrafos, `background-color: yellow`, e qualquer
  `<p>`, `<ul>`, `<ol>`, `<li>` ou `<table>` sem `style`.
- **Tamanho:** de 500 a 1.500 caracteres visíveis no verso.

## Exemplo (uma linha no TSV; aqui quebrado só para leitura)
Frente:
`Os membros do conselho fiscal podem ser atingidos pela desconsideração da personalidade jurídica fundada na teoria menor?`

Verso:
```html
<div style="font-family:-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;font-size:16px;line-height:1.5;color:#37352F;">
<p style="margin:0 0 8px;"><b>Em regra, não.</b> Só se houver indícios de que contribuíram, <span style="background:#FDF3C0;padding:1px 3px;border-radius:3px;"><b>ao menos culposamente e com desvio de função</b></span>, para a prática de atos de administração.</p>
<hr style="border:none;border-top:1px solid #E9E9E7;margin:12px 0;">
<p style="margin:0 0 8px;">💡 <b>Por quê.</b> O conselho fiscal fiscaliza, não administra. A simples condição de conselheiro <span style="color:#A03A38;"><b>não autoriza</b></span> a responsabilização.</p>
<p style="margin:0 0 8px;">⚠️ <b>Mesmo na teoria menor.</b> Ela dispensa prova de abuso, fraude ou confusão patrimonial, mas não alcança quem jamais atuou como gestor.</p>
<div style="background:#FBE4E4;border-radius:6px;padding:10px 12px;margin:8px 0;"><p style="margin:0;"><b style="color:#A03A38;">🚫 Pegadinha:</b> teoria menor não significa que qualquer integrante da sociedade responda.</p></div>
<p style="margin:12px 0 0;font-size:13px;color:#787774;"><em>(Art. 28, § 5º, do CDC; precedente do STJ citado por André Santa Cruz, Manual de Direito Empresarial)</em></p>
</div>
```
