# Especificação Formal da Gramática Livre de Contexto (BNF)

**Disciplina:** Compiladores (2026_2)  
**Projeto:** Tradutor Tático de Futebol Dirigido pela Sintaxe (StatsBomb 120 × 80)  
**Gerador de Analisadores:** PLY (`ply.lex` e `ply.yacc` — LALR(1), **0 conflitos**)

---

## 1. Definição Formal da Gramática G

A linguagem de descrição de lances táticos é definida pela quádrupla `G = (V, Σ, P, S)`:

* **Não-terminais (`V`), 15 símbolos:**
  `V = { <Lance>, <Confronto>, <IntervaloTempo>, <Bloco>, <SequenciaAcoes>, <ElementoTatico>, <Jogada>, <AcaoAtomica>, <TrocaPosse>, <Passe>, <CadeiaPasse>, <Finalizacao>, <DesfechoParcial>, <Coordenada>, <Desfecho> }`

* **Terminais / tokens (`Σ`):**
  * Palavras reservadas: **LANCE, VS, FASE, POSSE, TROCA_POSSE, PASSE, FINALIZACAO, RESULTADO, REBOTE, GOL, DEFESA, FORA, TRAVE, TABELA, TRIANGULACAO, CONTRA_ATAQUE**
  * Tokens com valor: **TEMPO, JOGADOR, NUM, SETA** (`->`)
  * Literais: `[` `]` `-` `{` `}` `(` `)` `,` `;`

* **Símbolo inicial:** `S = <Lance>`

---

## 2. Regras de Produção (P): 31 produções

A numeração é a mesma da **Tabela SDT** (`02_TABELA_SDT.md`) e das árvores.

```bnf
 1  <Lance>           ::= LANCE <IntervaloTempo> <Confronto> <Bloco>
 2  <Confronto>       ::= JOGADOR VS JOGADOR
 3                      | ε
 4  <IntervaloTempo>  ::= '[' TEMPO '-' TEMPO ']'

 5  <Bloco>           ::= '{' <SequenciaAcoes> '}'
 6                      | FASE JOGADOR '{' <SequenciaAcoes> '}'
 7                      | POSSE JOGADOR '{' <SequenciaAcoes> '}'

 8  <SequenciaAcoes>  ::= <SequenciaAcoes> <ElementoTatico>
 9                      | <ElementoTatico>

10  <ElementoTatico>  ::= <AcaoAtomica>
11                      | <Bloco>
12                      | <Jogada>

13  <Jogada>          ::= TABELA JOGADOR JOGADOR '{' <SequenciaAcoes> '}'
14                      | TRIANGULACAO '{' <SequenciaAcoes> '}'
15                      | CONTRA_ATAQUE '{' <SequenciaAcoes> '}'

16  <AcaoAtomica>     ::= <Passe> ';'
17                      | <Finalizacao> ';'
18                      | <TrocaPosse> ';'

19  <TrocaPosse>      ::= TROCA_POSSE JOGADOR

20  <Passe>           ::= PASSE JOGADOR <Coordenada> <CadeiaPasse>
21  <CadeiaPasse>     ::= SETA JOGADOR <Coordenada>
22                      | <CadeiaPasse> SETA JOGADOR <Coordenada>

23  <Finalizacao>     ::= FINALIZACAO JOGADOR <Coordenada> RESULTADO <Desfecho>
24                      | FINALIZACAO JOGADOR <Coordenada> RESULTADO <DesfechoParcial> REBOTE <Finalizacao>
25  <DesfechoParcial> ::= DEFESA
26                      | TRAVE

27  <Coordenada>      ::= '(' NUM ',' NUM ')'

28  <Desfecho>        ::= GOL
29                      | DEFESA
30                      | FORA
31                      | TRAVE
```

### 2.1 Exemplos de sentenças aceitas

```text
LANCE [14:20 - 14:35] {
    PASSE "Luka Modrić" (25.4, 40.2) -> "Mateo Kovačić" (38.2, 42.1);
    PASSE "Mateo Kovačić" (38.2, 42.1) -> "Andrej Kramarić" (85.0, 18.5);
    FINALIZACAO "Andrej Kramarić" (108.5, 39.8) RESULTADO GOL;
}
```

```text
LANCE [62:10 - 62:40] {
  CONTRA_ATAQUE {
    PASSE "Gvardiol" (15.0, 35.0) -> "Brozovic" (32.0, 40.0) -> "Modric" (45.0, 44.0);
    TABELA "Modric" "Kovacic" {
      PASSE "Modric" (45.0, 44.0) -> "Kovacic" (52.0, 50.0) -> "Modric" (60.0, 42.0);
    }
    PASSE "Modric" (60.0, 42.0) -> "Perisic" (92.0, 12.0);
  }
  FINALIZACAO "Perisic" (105.0, 30.0) RESULTADO DEFESA REBOTE
    FINALIZACAO "Kramaric" (110.0, 40.0) RESULTADO TRAVE REBOTE
      FINALIZACAO "Petkovic" (112.0, 38.0) RESULTADO GOL;
}
```

---

## 3. Especificação Léxica dos Terminais (`ply.lex`)

| Token | Expressão regular | Exemplo de lexema | Valor (`t.value`) |
| :--- | :--- | :--- | :--- |
| `TEMPO` | `\d{1,3}:\d{2}` | `14:20`, `116:30` | string `"14:20"` |
| `NUM` | `\d+(\.\d+)?` | `25.4`, `40` | `float` |
| `JOGADOR` | `"[^"\n]+"` | `"Luka Modrić"` | string UTF-8 sem aspas |
| `SETA` | `->` | `->` | `"->"` |
| Reservadas | `[a-zA-Z_][a-zA-Z_0-9]*` + tabela `reserved` | `LANCE`, `VS`, `FASE`, `POSSE`, `TROCA_POSSE`, `PASSE`, `FINALIZACAO`, `RESULTADO`, `REBOTE`, `GOL`, `DEFESA`, `FORA`, `TRAVE`, `TABELA`, `TRIANGULACAO`, `CONTRA_ATAQUE` | nome da palavra |
| Literais | `[ ] - { } ( ) , ;` | `{` | o próprio caractere |
| (ignorados) | `[ \t\r]`, `\n+`, `\#.*` | espaços, quebras, comentários | — |

**Decisões léxicas:**
* `t_TEMPO` é definido **antes** de `t_NUM`. Assim, `14:20` vira um único token, e não `NUM ':' NUM`.
* O PLY ordena as regras definidas por string pelo tamanho da regex. Por isso `->` (SETA) é testado antes do literal `-`.
* Um identificador que não está na tabela `reserved` gera **erro léxico** com linha e coluna.
* **Sobre o nome `JOGADOR`:** o token representa *qualquer nome entre aspas*. Lexicamente, um jogador (`"Modrić"`), uma equipe (`POSSE "Croatia"`) e uma fase (`FASE "Saída de Bola"`) são indistinguíveis. **Quem dá o papel é a produção sintática** em que o token aparece.

---

## 4. Justificativas Teóricas

### 4.1 Recursão à esquerda em analisadores LALR(1)

```bnf
 8  <SequenciaAcoes> ::= <SequenciaAcoes> <ElementoTatico>
22  <CadeiaPasse>    ::= <CadeiaPasse> SETA JOGADOR <Coordenada>
```

Num parser *shift-reduce* (o `ply.yacc` gera LALR(1)), a recursão à esquerda permite reduzir cada elemento assim que ele termina. Para uma sequência **no mesmo nível**, a pilha fica com tamanho constante, independentemente do número `N` de ações. Com recursão à direita, os `N` elementos seriam empilhados antes da primeira redução (pilha `O(N)`).

> A pilha total é `O(d)`, onde `d` é a **profundidade de aninhamento** de blocos e jogadas. O aninhamento é justamente o que exige pilha (Seção 4.3).

### 4.2 Recursão à direita intencional: o rebote

```bnf
24  <Finalizacao> ::= FINALIZACAO JOGADOR <Coordenada> RESULTADO <DesfechoParcial> REBOTE <Finalizacao>
```

Aqui a recursão à direita é escolhida pelo **significado**: o segundo chute só existe por causa do primeiro (a bola voltou da defesa do goleiro ou da trave). A sequência de rebotes é curta na prática, então o custo de pilha `O(k)` é irrelevante. Em troca, a árvore representa a relação causal "chute → rebote → chute".

**Ausência de conflito:** depois de `DEFESA`, o parser decide pelo *lookahead*. Se o próximo token é `;`, reduz para `<Desfecho>` (#29). Se é `REBOTE`, reduz para `<DesfechoParcial>` (#25). Um token de lookahead basta, por isso é LALR(1).

### 4.3 A linguagem é livre de contexto e não é regular (Chomsky Tipo 2)

**(a) Auto-incorporação na gramática.** A variável `<Bloco>` satisfaz `A ⇒⁺ α A β` com `α, β ≠ ε`:

`<Bloco> ⇒(#5) { <SequenciaAcoes> } ⇒(#9) { <ElementoTatico> } ⇒(#11) { <Bloco> }`

O mesmo vale para `<Jogada>`: `<Jogada> ⇒ TABELA J J { <SequenciaAcoes> } ⇒⁺ TABELA J J { <Jogada> }`.

> **Atenção:** auto-incorporação **sozinha não prova** que a linguagem não é regular. O teorema de Chomsky diz o contrário: *se uma GLC não tem auto-incorporação, a linguagem é regular*. A recíproca é falsa. Por exemplo, `S → aSa | a` tem auto-incorporação e gera `a(aa)*`, que é regular. A auto-incorporação mostra que **esta gramática** precisa de pilha. Para afirmar algo sobre **a linguagem**, usamos o argumento (b).

**(b) Prova de que `L(G)` não é regular.** Considere a linguagem regular:

`R = LANCE [T - T] {* PASSE J (N,N) -> J (N,N) ; }*`

1. As linguagens regulares são fechadas sob interseção. Logo, se `L(G)` fosse regular, `L(G) ∩ R` também seria.
2. Pela gramática, as chaves precisam estar balanceadas, então `L(G) ∩ R = { LANCE [T-T] {^n PASSE...; }^n | n >= 1 }`.
3. Aplicando o homomorfismo que apaga todos os símbolos exceto `{` e `}`, obtemos `{ {^n }^n | n >= 1 }`. As linguagens regulares são fechadas sob homomorfismo.
4. `{ {^n }^n }` **não é regular pelo Lema do Bombeamento**. Tome `w = {^p }^p`. Qualquer divisão `w = xyz` com `|xy| <= p`, `|y| >= 1` tem `y` formado só por `{`. Então `xy²z` fica com mais `{` do que `}`, e não pertence à linguagem.
5. Contradição. Portanto `L(G)` **não é regular**. Como `G` é livre de contexto, `L(G)` é **estritamente Tipo 2**: precisa de um **autômato com pilha**.

**Significado no domínio:** a pilha guarda o contexto tático em aberto. Por exemplo, um `CONTRA_ATAQUE` que contém uma `TABELA` que contém um sub-bloco. Ao fechar cada `}`, o parser sabe exatamente qual jogada está sendo concluída e aplica a regra semântica dela.

### 4.4 Precedência e eliminação de ambiguidade

**Por que não há tabela `precedence` no `ply.yacc`:** no exemplo calc, a precedência é necessária porque a gramática de expressões (`expr : expr '+' expr | expr '*' expr`) é **ambígua**, e o PLY usa `precedence` para resolver os conflitos *shift/reduce*. A DSL tática **não tem operadores binários**: cada construção começa com uma palavra reservada (`PASSE`, `FINALIZACAO`, `TABELA`…) ou com um delimitador (`{`), o que já determina qual produção usar.

**Prova de que não é ambígua:** o PLY gera as tabelas LALR(1) com **0 conflitos *shift/reduce* e 0 conflitos *reduce/reduce***. Toda gramática LALR(1) sem conflitos é **não ambígua**, porque cada sentença tem uma única derivação mais à direita. Logo, a precedência não foi necessária.

**Pontos que poderiam gerar ambiguidade e como foram resolvidos:**

| Ponto | Risco | Solução |
| :--- | :--- | :--- |
| `DEFESA` / `TRAVE` em `<Desfecho>` (#29, #31) e em `<DesfechoParcial>` (#25, #26) | conflito *reduce/reduce* | **lookahead**: com `;` reduz para `<Desfecho>`; com `REBOTE` reduz para `<DesfechoParcial>` |
| Lista de ações (#8) | recursão à esquerda × à direita | recursão **à esquerda**, sem ambiguidade e com pilha constante |
| `->` e o literal `-` | ambiguidade **léxica** | o PLY testa as regex por tamanho: `->` (SETA) antes de `-` |
| `14:20` | `TEMPO` ou `NUM ':' NUM` | `t_TEMPO` definido antes de `t_NUM` |
| Palavras reservadas × identificadores | `PASSE` lido como identificador | tabela `reserved` reclassifica o token; identificador desconhecido é **erro léxico** |
| Cabeçalho `<Confronto>` opcional (#3, produção vazia) | conflito com o início de `<Bloco>` | `<Bloco>` nunca começa com `JOGADOR`, então o lookahead decide |

---

## 5. Convenção de coordenadas por equipe (importante para a semântica)

Toda coordenada da DSL está no **referencial do time que executa a ação**, o mesmo padrão da StatsBomb. `X = 0` é a linha de fundo da própria defesa e `X = 120` é o gol adversário. Consequências:

* O **campo de ataque do Brasil é o campo de defesa da Croácia**, e vice-versa.
* O mesmo ponto físico visto pelo adversário é obtido por uma **rotação de 180°**:
  `espelhar(x, y) = (120 − x, 80 − y)`
  Exemplo: `Ataque Esquerdo` da Croácia em `(85, 18.5)` = `Defesa Direita` do Brasil em `(35, 61.5)`.
* **Verificado nos dados reais** (Croácia x Brasil, Copa 2022, `match_id` 3869420): todos os chutes dos dois times têm `X >= 89`, e nas trocas de posse o primeiro evento do time que recupera fica em `≈ (120 − x, 80 − y)` do último passe do time que perdeu. Exemplo: Croácia perde em `(80.0, 26.5)` e o Brasil começa em `(40.1, 53.6)`.
* O cabeçalho opcional `"Croatia" VS "Brazil"` (produção #2) diz ao compilador quem é o adversário de cada time. Assim, o relatório mostra cada zona **nas duas perspectivas** e valida que `POSSE`/`TROCA_POSSE` só citam equipes do confronto.
