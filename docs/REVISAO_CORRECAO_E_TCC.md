# Revisão do Trabalho e Correção da Professora

**Data:** 10/11/2026 · **Base:** enunciado da disciplina (PDF local, fora do repositório), `src/`, `docs/`, `exemplos/`, `tests/`

---

## 0. Situação atual

* **Todas as correções foram aplicadas no código e nos documentos** (Seção 1). 18 testes do compilador + 6 do extrator passam. A gramática LALR(1) tem 31 produções e 0 conflitos.
* **Correção da professora implementada** (Seção 2): elementos táticos recursivos (`TABELA`, `TRIANGULACAO`, `CONTRA_ATAQUE`) e ações atômicas recursivas (passe encadeado e finalização com `REBOTE`).
* **Campo por equipe** (Seção 3): o ataque de um time é a defesa do outro. Isso foi verificado nos dados reais da StatsBomb e agora é explícito no compilador.
* **TCC:** a análise, a ideia recomendada e as 5 ideias novas estão em `IDEIAS_TCC_CIENCIA_DE_DADOS.md` (Partes 5 a 7).

---

## 1. Revisão: o que foi encontrado e o que foi feito

| # | Problema encontrado | Situação |
| :-: | :--- | :--- |
| 1 | Passo 6 do enunciado: o código não marcava o que foi criado/modificado | Marcações `[NOVO]`, `[MODIFICADO]`, `[PLY]` em `lexer.py`, `parser.py`, `semantico.py`, `campo_statsbomb.py` (legenda no topo do `lexer.py`) |
| 2 | **Erro teórico:** "tem auto-incorporação, logo não é regular" (implicação falsa; contraexemplo `S → aSa \| a`) | Prova refeita em `01_GRAMATICA_BNF.md` §4.3 (interseção com linguagem regular + homomorfismo + Lema do Bombeamento) |
| 3 | V e Σ sem `TrocaPosse`, `POSSE`, `TROCA_POSSE`; numeração da prova diferente da tabela | Gramática reescrita com 31 produções numeradas igual em todos os docs |
| 4 | "Pilha O(1)" sem ressalva | Agora diz O(d), onde d é a profundidade de aninhamento |
| 5 | Duas `identificar_zona` (limiar 38 × 40; 644 pontos divergentes) | Uma única função em `semantico.py` (X ≥ 40), importada pelo extrator |
| 6 | Limiares de direção diferentes entre docs e código | Docs alinhados (2 m / 20 m) |
| 7 | Bug: passe da Defesa Esquerda para a grande área virava "Cruzamento" | Exige origem no setor de ataque (X ≥ 80); teste novo |
| 8 | Toque de lado no ataque (ΔX = +1 m) virava "para o ataque" | Agora exige ΔX > 2 m |
| 9 | Horários interpolados apresentados como reais | Exibidos como `~62:14`, com nota no cabeçalho |
| 10 | Exemplo da Croácia: Perišić recebe e Kramarić chuta | Exemplo corrigido + **aviso semântico** de continuidade do portador da bola |
| 11 | Token `JOGADOR` usado para fase e equipe | Mantido (as figuras e o prompt já usam esse nome) e justificado: léxicamente é "nome entre aspas", e quem dá o papel é a produção |
| 12 | `POSSE` dizia definir o referencial, mas nada era feito | Implementado de verdade (Seção 3) |

> **Efeito colateral do limiar 40:** no lance da Croácia, Kovačić em (38.2, 42.1) passou a ser `Defesa Central` (antes `Meio-Campo Central`). Os documentos e figuras já estão atualizados.

---

## 2. Correção da professora: recursividade

**Antes:** só `<Bloco>` era recursivo, e só colocava rótulos. `<AcaoAtomica>` era plana.

**Agora:**

| O quê | Produções | Recursão | Semântica própria |
| :--- | :--- | :--- | :--- |
| `TABELA "A" "B" { … }` | #13 | auto-incorporação | valida A→B e depois B→A |
| `TRIANGULACAO { … }` | #14 | auto-incorporação | ≥ 3 passes entre exatamente 3 jogadores |
| `CONTRA_ATAQUE { … }` | #15 | auto-incorporação | avanço ≥ 40 m em ≤ 6 passes |
| `PASSE "A" (…) -> "B" (…) -> "C" (…);` | #20–#22 | ação atômica, à **esquerda** | o portador passa de elo em elo; **atributo herdado** em #21 (`p[-2]`, `p[-1]`), então a SDT é L-atribuída |
| `FINALIZACAO … RESULTADO DEFESA REBOTE FINALIZACAO …` | #24–#26 | ação atômica, à **direita** | tentativas numeradas; o desfecho final é o do chute mais interno |

A sintaxe antiga continua válida. Exemplos: `exemplos/lance_recursivo.txt`. Árvore: `docs/arvore_recursiva.png`.

**Sugestão para o vídeo (7 min):** mostre a execução de `lance_recursivo.txt` e depois um erro semântico ao vivo (por exemplo, trocar a ordem dos passes dentro da `TABELA`). Isso mostra em poucos segundos que a recursão tem **semântica**, e não só sintaxe.

---

## 3. Campo de ataque × campo de defesa por equipe

**Fato verificado nos dados** (Croácia x Brasil, `match_id` 3869420): a StatsBomb grava cada evento **no referencial do time que o executa** (X = 120 é sempre o gol adversário de quem age). Todos os chutes dos dois times têm X ≥ 89. Nas trocas de posse, o mesmo ponto aparece girado 180°: a Croácia perde em (80.0, 26.5) e o Brasil começa em (40.1, 53.6) ≈ (120 − 80.0, 80 − 26.5).

**O que foi implementado:**
* `espelhar(x, y) = (120 − x, 80 − y)` e `zona_para_adversario(c)` em `semantico.py`;
* cabeçalho opcional `LANCE [..] "Croatia" VS "Brazil" { … }` (produções #2/#3); o extrator da StatsBomb já gera esse cabeçalho;
* o relatório mostra cada zona nas duas perspectivas: `Ataque Direito (Croatia) = Defesa Esquerda (Brazil)`;
* na troca de posse, mostra o **local da recuperação** para os dois times;
* **erro semântico** se `POSSE`/`TROCA_POSSE` citar uma equipe fora do confronto;
* exemplo `exemplos/lance_troca_posse.txt` e testes `test_perspectiva_por_equipe`, `test_confronto_e_troca_de_posse`.

**Cuidado ao escrever DSL à mão:** dentro de `POSSE "Brazil" { … }`, as coordenadas são **do Brasil**. Se você copiar coordenadas absolutas de um vídeo (com um único sentido para o campo todo), precisa espelhar as do time que ataca para a esquerda.

---

## 4. TCC

As ideias de TCC (análise crítica das 15 ideias, a ideia recomendada detalhada e as 5 novas ideias, 16 a 20) foram incorporadas ao documento **`IDEIAS_TCC_CIENCIA_DE_DADOS.md`** (Partes 4 a 7).

---

## 5. Segunda revisão (13/11/2026, repositório `pdromls/tactical-football-compiler`)

Revisão completa do repositório na versão v2.0: código, testes, exemplos, documentos e PDFs.

**O que estava certo:**
* gramática com 31 produções e 0 conflitos LALR;
* todos os exemplos rodam;
* a partida inteira Croácia x Brasil compila (0' a 125', 155 trocas de posse).

**Bugs semânticos encontrados com testes de borda (corrigidos, com 4 testes novos):**

| # | Entrada aceita indevidamente | Correção |
| :-: | :--- | :--- |
| 1 | `LANCE [14:75 - 14:80]` (segundos ≥ 60) | erro semântico em #4 |
| 2 | `TABELA "A" "A" { … }` | erro semântico em #13 (exige A ≠ B) |
| 3 | `CONTRA_ATAQUE` contendo `TROCA_POSSE` e passes dos dois times: o avanço somava coordenadas de **referenciais diferentes** | #13–#15 exigem uma única equipe e nenhuma `TROCA_POSSE` dentro da jogada |
| 4 | `TROCA_POSSE "Y"` seguida de `POSSE "X"`: o relatório dizia "Y perdeu → X recuperou" | erro semântico na raiz: a próxima ação de bola tem de ser da equipe anunciada |

**Outros ajustes:**
* concordância no relatório ("**no** Meio-Campo Central", "**no** Ataque Central"; antes saía "na");
* `main.py` trata falha de rede (partida fora de `data_cache/`) com mensagem própria;
* os testes rodam de qualquer diretório (antes dependiam de serem chamados da raiz).

**Documentos corrompidos pela conversão de LaTeX para Unicode (corrigidos):**
* `$0` virou `topo-2` (PROMPT, 02, ENTREGA, MANUAL, IDEIAS, v1/02);
* `\left(` virou `≤ft(`;
* restos de `\frac`, `\mathbf`, `\;\;` (GUIA, PROPOSTA);
* `$` soltos no PROMPT;
* a linguagem regular `R` da prova de não-regularidade (01, §4.3) estava escrita como `{*}` em vez de `{*`.

**Repositório:**
* O PDF do enunciado da professora foi **retirado do repositório público** e incluído no `.gitignore`. A cópia local continua na pasta. Ele ainda existe nos commits antigos (v1.0 e v2.0); para apagá-lo do histórico, é preciso reescrever o histórico e forçar o push.
* `matplotlib` foi adicionado ao `requirements.txt` como dependência opcional (só para `docs/gerar_arvores.py`).
* Ponto em aberto: o gerador de PDFs (`Prova/generate_pdfs.py`) está em `Prova/`, que o `.gitignore` exclui. Quem clonar o repositório não consegue regenerar os PDFs de `docs/`.

---

## 6. Checklist antes do vídeo (25/11)

- [x] Marcar no código o que foi criado/modificado
- [x] Corrigir V, Σ, numeração e a prova de não-regularidade
- [x] Unificar `identificar_zona` e alinhar docs
- [x] Corrigir cruzamento, direção e exemplo da Croácia
- [x] Aplicar a correção da professora (recursividade) + tabela + árvores
- [x] Zonas por equipe (ataque × defesa)
- [x] Regenerar os PDFs da pasta `docs/`
- [ ] Ensaiar o vídeo em 7 min: ideia (1 min) → léxico/gramática (2) → SDT e árvores (2) → execução ao vivo: `lance_recursivo.txt`, `lance_troca_posse.txt` e um erro semântico (2)
