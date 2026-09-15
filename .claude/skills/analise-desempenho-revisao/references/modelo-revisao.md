# Modelo do `revisao.md` (vira PDF e DOCX com `scripts/gerar_material.py`)

O material é para **sentar e ler com calma**. O layout é padronizado e aplicado automaticamente pelos geradores:
- **Capa:** verde, com o título em branco e uma etiqueta magenta com o modo e a data.
- **Sumário:** automático, montado a partir dos títulos `#` e `##`.
- **Texto:** Open Sans **justificada**, em parágrafos completos. **Não use marcadores** (bullet points); listas no
  `.md` viram parágrafos.
- **Títulos:** verdes.
- **Destaques:** em **magenta**.
- **Quadros:** rótulo em fonte condensada, filete colorido à esquerda e fundo claro.
- **Tabelas:** cabeçalho magenta.
- **Rodapé:** número da página num quadrado magenta.

Fontes em `assets/fonts` (licença OFL); o PDF já as incorpora. Para ver o DOCX igual no Word, instale as fontes da pasta.

## Elementos
| Marcação | Resultado | Uso |
|---|---|---|
| `---` + campos + `---` no topo | capa e sumário | `titulo`, `subtitulo`, `material`, `modo`, `perfil`, `data` |
| `#`, `##` | títulos verdes, entram no sumário | numere à mão ("1.", "2.3"); nas perguntas, `## Pergunta 1 · Tópico` |
| `###` | subtítulo escuro | uso raro |
| `**negrito**` | negrito | termos técnicos e núcleo da ideia; até 2 ou 3 por parágrafo |
| `==destaque==` | **negrito magenta** | a afirmação central que não pode ser esquecida; **no máximo 1 por parágrafo**, sempre curta (até ~12 palavras) |
| `*itálico*` | itálico | expressões estrangeiras, nomes de obras |
| `> texto` | bloco com filete magenta, texto cinza em seminegrito | **enunciado das perguntas** e trechos literais |
| `**Nota 6,0/10**` | negrito | nota de cada resposta |
| `**Entregou:**` · `**Parcial:**` · `**Faltou:**` · `**Erro conceitual:**` | rótulo **verde · âmbar · vermelho · vermelho** | início de cada parágrafo do feedback |
| `> [!ATENCAO] ...` | quadro **ATENÇÃO** (magenta) | erro conceitual, exceção que derruba a regra, pegadinha |
| `> [!DICA] ...` | quadro **COMO ESCREVER NA PROVA** (verde) | frase-núcleo que o espelho procura (discursiva) |
| `> [!FUNDAMENTO] ...` | quadro **FUNDAMENTO** (azul-petróleo) | artigos, súmulas, temas, julgados (só referências seguras) |
| `> [!PROVA] ...` | quadro **COMO A BANCA COBRA** (âmbar) | forma de cobrança e pegadinha (objetiva) |
| `**Quadro 1. Título**` + tabela | título centralizado e tabela com cabeçalho magenta | desempenho e comparações |
| `---` sozinho no corpo | quebra de página | início de cada parte |

Regras de formatação:
- **Cores:** as únicas são as dos quatro quadros, a dos rótulos do feedback e a magenta dos destaques, enunciados e tabelas.
- **Quadros:** no máximo 2 por lacuna e nunca dois do mesmo tipo seguidos; cada um com 1 a 4 linhas.
- **Pontuação e datas:** sem travessão (— ou –) e sem emojis. Datas em DD/MM/AAAA.

## Estrutura (as quatro partes são obrigatórias, nesta ordem)
```markdown
---
titulo: Revisão dirigida: <tema da sessão>
subtitulo: Material montado a partir das suas lacunas
material: <nome do material-base>
modo: Discursiva | Objetiva
perfil: <cargo · fase>
data: <DD/MM/AAAA>
---

# 1. Seu desempenho nesta sessão

**Quadro 1. Notas da sessão**
| # | Tópico | Nota | Próxima revisão |
|---|---|---|---|
| 1 | Teorias maior e menor | 6,0 | 17/09/2026 |

<Parágrafo com a nota média e a comparação com o nível anterior: a revisão surtiu efeito?>

<Parágrafo "Onde você foi melhor" e parágrafo "Onde você foi pior", em prosa.>

---

# 2. Correção de cada resposta

## Pergunta 1 · <Tópico>

> <enunciado completo, exatamente como foi apresentado>

**Nota 6,0/10**

**Entregou:** <o que a resposta trouxe corretamente, em frase completa>

**Parcial:** <o que foi tocado sem completude e o que faltou para completar>

**Faltou:** <o conteúdo esperado que não apareceu, com o fundamento>

**Erro conceitual:** <o que foi dito> O correto é: <a versão correta>.

> [!DICA] <a frase-núcleo para fechar o ponto na prova>

## Pergunta 2 · <Tópico>
...

---

# 3. Lacunas prioritárias

## 3.1 <Tópico>: <lacuna em forma de título>

<Parágrafo: o que faltou na resposta.>

<Explicação completa, em prosa justificada: conceito, requisitos, correntes, posição dos tribunais, exemplo.
Requisitos e hipóteses vão encadeados no texto ("São dois os requisitos. O primeiro... O segundo..."), e não em
marcadores. Base: trecho do material-base, completado com lei e jurisprudência consolidadas.>

> [!FUNDAMENTO] <artigos, súmulas, temas>

> [!DICA] <discursiva: como escrever o ponto na prova>

## 3.2 <próxima lacuna>
...

---

# 4. Pontos fortes e rumos para a próxima revisão

<Parágrafo com os pontos fortes.>

<Parágrafo com as ações concretas e as datas das próximas revisões.>
```

## Regras da parte 2 (correção de cada resposta)
- **Todas as perguntas** da sessão entram, em ordem, cada uma com o **enunciado completo** e o feedback no mesmo nível
  de detalhe da correção imediata. Isso vale inclusive para perguntas já corrigidas no chat.
- **Um parágrafo por ponto**, começando pelo rótulo. Omita os rótulos que não se aplicam.
- **Objetivas:** depois do enunciado, as alternativas em parágrafos ("A) ..."), seguidas de "**Gabarito:** C. Você
  marcou B (dúvida)", por que a correta está certa, o erro de cada distratora e o tipo de erro.
- **Encerramento de cada pergunta:** um `[!DICA]` (discursiva) ou um `[!PROVA]` (objetiva).

## Regras de redação
- **Só lacunas na parte 3.** Não reescreva o material inteiro; aprofunde o que faltou ou foi dito errado.
- **Ordem** das lacunas: a prioridade dada por `metricas`.
- **Tamanho:** cada lacuna com 3 a 6 minutos de leitura (cerca de 200 a 450 palavras).
- **Estilo:** linguagem de manual de revisão, com termos técnicos precisos e transições claras entre as ideias.
