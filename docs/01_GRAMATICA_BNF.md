# Especificação Formal da Gramática Livre de Contexto (BNF)

**Disciplina:** Compiladores (2026_2)  
**Projeto:** Tradutor Tático de Futebol Dirigido pela Sintaxe (StatsBomb 120x80)  
**Gerador de Analisadores:** PLY (`ply.lex` e `ply.yacc` — LALR(1))

---

## 1. Definição Formal da Gramática $G$

A linguagem formal de descrição de lances táticos é definida pela quádrupla $G = (V, \Sigma, P, S)$, onde:

* **Conjunto de Variáveis / Não-Terminais ($V$):**
  $$V = \{ \langle\text{Lance}\rangle, \langle\text{IntervaloTempo}\rangle, \langle\text{Bloco}\rangle, \langle\text{SequenciaAcoes}\rangle, \langle\text{ElementoTatico}\rangle, \langle\text{AcaoAtomica}\rangle, \langle\text{Passe}\rangle, \langle\text{Finalizacao}\rangle, \langle\text{Coordenada}\rangle, \langle\text{Desfecho}\rangle \}$$

* **Alfabeto de Símbolos Terminais / Tokens ($\Sigma$):**
  $$\Sigma = \{ \textbf{LANCE}, \textbf{FASE}, \textbf{PASSE}, \textbf{FINALIZACAO}, \textbf{RESULTADO}, \textbf{GOL}, \textbf{DEFESA}, \textbf{FORA}, \textbf{TRAVE}, \textbf{TEMPO}, \textbf{JOGADOR}, \textbf{NUM}, \texttt{'['}, \texttt{']'}, \texttt{'-'}, \texttt{'\{'}, \texttt{'\}'}, \texttt{'('}, \texttt{')'}, \texttt{','}, \texttt{'->'}, \texttt{';'} \}$$

* **Símbolo Inicial ($S$):**
  $$S = \langle\text{Lance}\rangle$$

---

## 2. Regras de Produção ($P$) em Notação BNF Estrita

```bnf
<Lance>          ::= LANCE <IntervaloTempo> <Bloco>

<IntervaloTempo> ::= '[' TEMPO '-' TEMPO ']'

<Bloco>          ::= '{' <SequenciaAcoes> '}'
                   | FASE JOGADOR '{' <SequenciaAcoes> '}'
                   | POSSE JOGADOR '{' <SequenciaAcoes> '}'

<SequenciaAcoes> ::= <SequenciaAcoes> <ElementoTatico>
                   | <ElementoTatico>

<ElementoTatico> ::= <AcaoAtomica>
                   | <Bloco>

<AcaoAtomica>    ::= <Passe> ';'
                   | <Finalizacao> ';'
                   | <TrocaPosse> ';'

<TrocaPosse>     ::= TROCA_POSSE JOGADOR

<Passe>          ::= PASSE JOGADOR <Coordenada> '->' JOGADOR <Coordenada>

<Finalizacao>    ::= FINALIZACAO JOGADOR <Coordenada> RESULTADO <Desfecho>

<Coordenada>     ::= '(' NUM ',' NUM ')'

<Desfecho>       ::= GOL
                   | DEFESA
                   | FORA
                   | TRAVE
```

---

## 3. Especificação Léxica dos Terminais (`ply.lex`)

| Token Terminal | Expressão Regular (Regex) | Exemplo de Lexema | Valor Atribuído (`t.value`) |
| :--- | :--- | :--- | :--- |
| `TEMPO` | `\d{1,3}:\d{2}` | `14:20`, `90:05` | String `"14:20"` |
| `NUM` | `\d+(\.\d+)?` | `25.4`, `108.5`, `40` | `float(t.value)` |
| `JOGADOR` | `"[^"\n]+"` | `"Luka Modrić"` | String UTF-8 sem aspas |
| `SETA` (`'->'`) | `->` | `->` | String `"->"` |
| Palavras Reservadas | `[a-zA-Z_][a-zA-Z_0-9]*` | `LANCE`, `PASSE`, `FINALIZACAO`, `RESULTADO`, `GOL`, `DEFESA`, `FORA`, `TRAVE`, `FASE` | Nome do token reservado |
| Literais | `[\[\]\-\{\}\(\),;]` | `[`, `]`, `-`, `{`, `}`, `(`, `)`, `,`, `;` | Próprio caractere ASCII |

---

## 4. Justificativas Teóricas Formais

### 4.1 Recursão à Esquerda em Analisadores Ascendentes LALR(1)

Na regra de produção que define a lista de ações do lance:

```bnf
<SequenciaAcoes> ::= <SequenciaAcoes> <ElementoTatico>
                   | <ElementoTatico>
```

Optou-se deliberadamente pela **recursão direta à esquerda** em vez da recursão à direita.
* **Justificativa para o `ply.yacc`:** O gerador `ply.yacc` constrói um analisador sintático ascendente (*bottom-up*) do tipo **LALR(1)** (*Lookahead LR*). Em um parser *shift-reduce*, a recursão à esquerda permite que cada $\langle\text{ElementoTatico}\rangle$ lido seja reduzido imediatamente (`reduce`) ao topo da pilha, mantendo a profundidade da pilha de estados constante em $O(1)$, independentemente do número $N$ de passes da partida.
* Caso fosse empregada recursão à direita ($\langle\text{SequenciaAcoes}\rangle ::= \langle\text{ElementoTatico}\rangle \ \langle\text{SequenciaAcoes}\rangle$), o autômato precisaria empilhar (`shift`) todos os $N$ eventos na pilha antes de realizar a primeira redução no final do bloco, exigindo espaço $O(N)$ na pilha de análise e podendo causar estouro de pilha (*Stack Overflow*) em sequências longas.

### 4.2 Propriedade de Auto-Incorporação (*Self-Embedding*) e Classificação de Chomsky (Tipo 2)

Para provar matematicamente que a linguagem gerada por $G$ é **estritamente Livre de Contexto (Tipo 2 na Hierarquia de Chomsky)** e **não é uma Linguagem Regular (Tipo 3)**, demonstramos que $G$ possui a propriedade de **Auto-Incorporação (*Self-Embedding*)** não-degenerada.

> **Definição Formal:** Uma Gramática Livre de Contexto $G = (V, \Sigma, P, S)$ apresenta auto-incorporação se e somente se existe uma variável $A \in V$ tal que:
> $$A \Rightarrow^+ \alpha A \beta$$
> onde $\alpha, \beta \in (V \cup \Sigma)^+$ (isto é, $\alpha \neq \varepsilon$ e $\beta \neq \varepsilon$).

**Demonstração em nossa gramática:**
Tomando o não-terminal $A = \langle\text{Bloco}\rangle$, temos a seguinte sequência de derivações em três passos:

1. $\langle\text{Bloco}\rangle \Rightarrow \texttt{'\{'} \ \langle\text{SequenciaAcoes}\rangle \ \texttt{'\}'}$ *(pela Produção 3)*
2. $\texttt{'\{'} \ \langle\text{SequenciaAcoes}\rangle \ \texttt{'\}'} \Rightarrow \texttt{'\{'} \ \langle\text{ElementoTatico}\rangle \ \texttt{'\}'}$ *(pela Produção 5)*
3. $\texttt{'\{'} \ \langle\text{ElementoTatico}\rangle \ \texttt{'\}'} \Rightarrow \texttt{'\{'} \ \langle\text{Bloco}\rangle \ \texttt{'\}'}$ *(pela Produção 7)*

Portanto:
$$\langle\text{Bloco}\rangle \Rightarrow^+ \texttt{'\{'} \ \langle\text{Bloco}\rangle \ \texttt{'\}'}$$

onde $\alpha = \texttt{'\{'} \in \Sigma^+$ e $\beta = \texttt{'\}'} \in \Sigma^+$, ambos não-vazios.

**Significado Semântico e Conclusão:**
No domínio tático do futebol, essa estrutura permite agrupar **subfases táticas hierárquicas** arbitrariamente aninhadas dentro de um lance (por exemplo, um bloco de `"Saída de Bola"` que contém um sub-bloco de `"Triangulação sob Pressão"` `{ ... { ... } ... }`). Como o reconhecimento do balanceamento exato de delimitadores aninhados $\{^n \ \dots \ \}^n$ para $n \ge 1$ arbitrário viola o Lema do Bombeamento para Linguagens Regulares, conclui-se que a linguagem exige um **Autômato com Pilha (PDA)** e pertence estritamente à classe das **Linguagens Livres de Contexto (Chomsky Tipo 2)**.
