# Modelo de flashcard (estilo Notion)

Cada linha de `flashcards.tsv` é um card com três colunas separadas por TAB: `frente<TAB>verso<TAB>tags`.
- **Frente:** texto puro, sem HTML e sem emoji.
- **Verso:** HTML inline no estilo Notion, **numa única linha** (sem quebras nem TAB).
- **Tags:** `revisao-voz-alta <slug-disciplina>::<slug-tópico>`.

O script `python scripts/sessao.py cards <sessão>` valida o formato antes de registrar e recusa o arquivo se
houver erro.

## Frente (pergunta)
- Uma pergunta direta que obriga a lembrar a lacuna, ou um caso curto (até ~400 caracteres) terminado em pergunta neutra.
- Não pode sugerir a resposta. Nada de "Fale sobre X" nem "Explique X".
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
| Citação (fundamento legal) | `<p style="margin:12px 0 0;font-size:13px;color:#787774;"><em>(...)</em></p>` |

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
1. **Resposta direta** em 1 ou 2 frases. Abra com `<b>Sim</b>.` ou `<b>Não</b>.` quando a pergunta admitir, e grife em amarelo o núcleo.
2. `<hr>`.
3. **De 1 a 3 blocos curtos**, cada um com emoji no início, título em negrito e 2 a 4 linhas (ou uma lista).
4. **Callout** opcional: 🚫 para erro conceitual cometido na sessão, 🎯 para como cai em prova, 🗝️ para macete.
5. **Citação cinza** com o fundamento: artigos, súmulas, temas e julgados, só referências seguras.

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
`Na desconsideração inversa da personalidade jurídica, qual patrimônio responde por qual dívida, e quais são os requisitos?`

Verso:
```html
<div style="font-family:-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;font-size:16px;line-height:1.5;color:#37352F;">
<p style="margin:0 0 8px;">Os <span style="background:#FDF3C0;padding:1px 3px;border-radius:3px;"><b>bens da pessoa jurídica</b></span> respondem por <b>obrigação pessoal do sócio</b> que ocultou seu patrimônio na sociedade.</p>
<hr style="border:none;border-top:1px solid #E9E9E7;margin:12px 0;">
<p style="margin:0 0 6px;">📋 <b>Requisitos (os mesmos do art. 50 do CC):</b></p>
<ul style="margin:0 0 12px;padding-left:20px;"><li style="margin:0 0 4px;"><span style="color:#3B6A45;"><b>Desvio de finalidade</b></span> (dolo), ou</li><li style="margin:0 0 4px;"><span style="color:#3B6A45;"><b>Confusão patrimonial</b></span> (objetiva)</li></ul>
<p style="margin:0 0 8px;">👪 <b>Uso típico.</b> Fraude à partilha no divórcio ou frustração de alimentos, transferindo bens para a sociedade controlada.</p>
<div style="background:#FBE4E4;border-radius:6px;padding:10px 12px;margin:8px 0;"><p style="margin:0;"><b style="color:#A03A38;">🚫 Pegadinha:</b> atingir o patrimônio <b>do sócio</b> é a desconsideração comum, <span style="color:#A03A38;"><b>não a inversa</b></span>.</p></div>
<p style="margin:12px 0 0;font-size:13px;color:#787774;"><em>(Art. 50, § 3º, do CC; art. 133, § 2º, do CPC)</em></p>
</div>
```
