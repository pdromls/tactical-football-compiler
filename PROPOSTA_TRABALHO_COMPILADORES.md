# Proposta de Trabalho: Tradutor Tático de Lances de Futebol
**Disciplina:** Compiladores (2026_2)  
**Equipe:** Trabalho em Dupla  
**Linguagem de Base:** Python  
**Gerador de Analisadores:** PLY (*Python Lex-Yacc*)  

---

## 1. Visão Geral do Projeto

O objetivo do projeto é desenvolver um **Compilador/Tradutor Dirigido pela Sintaxe** capaz de receber registros estruturados de eventos esportivos (coordenadas cartesianas e toques na bola em um intervalo de tempo de uma partida) e traduzi-los em uma **narrativa tática descritiva e classificada em linguagem natural**.

Em vez de processar dados com condicionais soltas em scripts tradicionais, a solução utiliza a teoria formal de compiladores:
* O campo de futebol é modelado formalmente como um **plano cartesiano zoneado** (tabuleiro de zonas táticas);
* Os toques na bola formam sentenças de uma **linguagem formal de lances**;
* As regras de produção gramatical estruturam as jogadas;
* As **ações semânticas dirigidas pela sintaxe (SDT)** calculam grandezas físicas (distâncias euclidianas, vetores de deslocamento) e mapeiam as zonas para traduzir o que de fato aconteceu no lance (ex: *passe curto para frente*, *lançamento longo*, *inversão lateral*).

---

## 2. Alinhamento com os Requisitos da Disciplina

O projeto atende com precisão a todos os critérios e entregáveis exigidos no regulamento:

```
                  ┌───────────────────────────────────────────┐
                  │             ENTRADA MODULAR               │
                  │  Modo A: Arquivo em disco (.txt / .match) │
                  │  Modo B: Stream em Memória (via StatsBomb)│
                  └─────────────────────┬─────────────────────┘
                                        │
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │         Análise Léxica (ply.lex)          │
                  │       (Regex: Coords, IDs, Tempos)        │
                  └─────────────────────┬─────────────────────┘
                                        │
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │        Análise Sintática (ply.yacc)       │
                  │         (Gramática BNF do Lance)          │
                  └─────────────────────┬─────────────────────┘
                                        │
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │       Análise Semântica (Ações SDT)       │
                  │        (Cálculo de Zonas/Distância)       │
                  └─────────────────────┬─────────────────────┘
                                        │
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │        Saída Traduzida / Relatório        │
                  │        ("Passe curto de A para B")        │
                  └───────────────────────────────────────────┘
```

### 2.1 Análise Léxica (`ply.lex`)
* **Expressões Regulares:** Mapeadas em tokens formais da linguagem:
  * `COORDENADA`: Padrão `r'\(\s*\d+\s*,\s*\d+\s*\)'` (ex: `(25, 40)`).
  * `JOGADOR`: Padrão `r'"[a-zA-ZÀ-ÿ\s]+"'` (ex: `"Modric"`).
  * `TEMPO`: Padrão `r'\[\d{2}:\d{2}\]'` ou intervalos `r'\[\d{2}:\d{2}\s*-\s*\d{2}:\d{2}\]'`.
  * `PALAVRAS_CHAVE`: `PASSE`, `TOQUE`, `PARA`, `LANCE`, `FINALIZACAO`, `RESULTADO`.
  * Operadores e delimitadores: `->`, `:`, etc.

### 2.2 Análise Sintática (`ply.yacc`)
* **Gramática Livre de Contexto (BNF):**
  * Modela a estrutura estrita de um lance válido:
    $$\text{Lance} \rightarrow \text{CabecalhoTempo} \;\; \text{SequenciaPasses} \;\; \text{Fim}$$
    $$\text{SequenciaPasses} \rightarrow \text{SequenciaPasses} \;\; \text{Passo} \;\mid\; \text{Passo}$$
    $$\text{Passo} \rightarrow \text{PASSE} \;\; \text{JOGADOR} \;\; \text{COORD} \;\; \text{"->"} \;\; \text{JOGADOR} \;\; \text{COORD}$$
* **Árvore de Derivação (Parse Tree):** Atende diretamente ao item **4.d** do regulamento, evidenciando como a sentença de entrada se deriva a partir do símbolo inicial da gramática.

### 2.3 Análise Semântica & Tradução Dirigida pela Sintaxe (SDT)
Nas funções do `ply.yacc`, cada redução gramatical executa a ação semântica correspondente:
* **Mapeamento Espacial de Zonas:** Transforma as coordenadas $(X, Y)$ da entrada em quadrantes/zonas do campo (ex: *Zona Defensiva*, *Terço Médio*, *Corredor Lateral*, *Zona de Ataque*).
* **Cálculo Físico-Geométrico:**
  * Distância Euclidiana: $d = \sqrt{(X_2 - X_1)^2 + (Y_2 - Y_1)^2}$
  * Vetor Direcional: Variação $\Delta X$ (avanço ou recuo) e $\Delta Y$ (mudança de corredor).
* **Classificação Qualitativa do Passe:**
  * $d \le 15\text{m}$: Classificado como `PASSE_CURTO`.
  * $15\text{m} < d \le 30\text{m}$: Classificado como `PASSE_MEDIO`.
  * $d > 30\text{m}$: Classificado como `LANCAMENTO`.
* **Árvore de Derivação Anotada:** Decora cada nó com seus atributos semânticos sintetizados (`origem_zona`, `destino_zona`, `distancia`, `classificacao`).

### 2.4 Modularidade da Entrada: Modo Arquivo vs. Modo Memória (Stream)
O compilador foi projetado com arquitetura desacoplada, aceitando a entrada por dois caminhos:
1. **Modo Arquivo em Disco (`.txt` / `.match`):**
   * **Objetivo:** Rigor acadêmico, testes unitários e elaboração dos diagramas estáticos exigidos no trabalho.
   * **Funcionamento:** O usuário ou professor pode rodar via terminal `python tradutor.py exemplo_lance.txt`, facilitando a inspeção da gramática e das árvores de derivação.
2. **Modo Automático em Memória (Stream direto da API/StatsBomb):**
   * **Objetivo:** Experiência integrada e interativa na aplicação/front-end.
   * **Funcionamento:** O usuário apenas seleciona a partida e o intervalo de tempo desejado. O sistema consome a API do StatsBomb, extrai os eventos brutos, serializa-os em tempo de execução como uma string formatada na gramática e injeta diretamente no compilador via `parser.parse(string_em_memoria)` de forma transparente, sem necessidade de manipulação manual de arquivos.

---

## 3. Escopo Incremental: Do MVP à Expansão Futura

Para garantir a entrega no prazo com excelência e sem riscos de atraso, o projeto foi planejado em duas camadas:

```
  ┌──────────────────────────────────────────────────────────────┐
  │                   FASE 1: MVP DO COMPILADOR                  │
  │               (Obrigatório - Garantia da Nota)               │
  │                                                              │
  │  • Gramática focada em passes de Jogador A para Jogador B    │
  │  • Processamento de coordenadas (X, Y)                       │
  │  • Cálculo de distância e direção (para frente / recuo)      │
  │  • Classificação em Passe Curto, Médio ou Lançamento         │
  │  • Mapeamento de Zonas Básicas (Defesa, Meio, Ataque)        │
  │  • Árvores de derivação sintática e anotada                  │
  │  • Tabela SDT completa                                       │
  └──────────────────────────────┬───────────────────────────────┘
                                 │
                                 ▼ (Após o MVP validado)
  ┌──────────────────────────────────────────────────────────────┐
  │                 FASE 2: EXPANSÕES E EVOLUÇÃO                 │
  │                     (Diferenciais Extras)                    │
  │                                                              │
  │  • Inclusão de Cruzamentos (saída lateral -> grande área)    │
  │  • Inclusão de Finalizações e Gols                           │
  │  • Classificação de Jogadas Compostas (ex: Contra-ataque)    │
  │  • Conector com a API aberta da StatsBomb (jogos da Copa)    │
  │  • Interface gráfica/web para seleção de partidas e tempos   │
  └──────────────────────────────────────────────────────────────┘
```

### 3.1 Fase 1: MVP (Foco Estrito na Disciplina)
* Entrada textual simples contendo apenas a sequência de passes com coordenadas.
* Saída traduzida de cada passe:
  > *"Passe curto para frente de Modric para Kovacic, avançando da Zona Defensiva para o Meio-Campo."*
  > *"Lançamento longo de Kovacic para Perisic, avançando do Meio-Campo para o Corredor Esquerdo de Ataque."*
* **Status:** Já cumpre **100% dos requisitos acadêmicos** para nota máxima.

### 3.2 Fase 2: Evolução e Avanços Posteriores
Uma vez que o núcleo da Fase 1 esteja estável e testado, novos recursos podem ser plugados modularmente:
1. **Tipos Complexos de Lances:**
   * **Cruzamento:** Quando a origem é lateral ($Y < 20$ ou $Y > 60$) e o destino é a grande área adversária ($X > 100$).
   * **Finalização:** Registro de chute a gol com atributo booleano de resultado (gol, defesa, fora).
2. **Classificação Tática de Alto Nível:**
   * Regra semântica que analisa o conjunto do lance: se houver 3 passes verticais sucessivos em menos de 10 segundos, anota o lance inteiro como *"Construção de Contra-Ataque Rápido"*.
3. **Consumo de Dados do StatsBomb:**
   * Um conector que consome o banco de dados aberto da StatsBomb (`statsbombpy`), filtra um intervalo de tempo real de uma partida oficial (ex: Copa do Mundo de 2022) e alimenta o compilador automaticamente.
4. **Front-End Interativo:**
   * Tela simples onde o usuário escolhe a partida e os minutos que deseja traduzir, visualizando o relatório e o desenho das jogadas no campo.

---

## 4. Tabela SDT (Exemplo Demonstrativo para Apresentação)

Exemplo da tabela exigida no item **4.c** do PDF (Tradução Dirigida pela Sintaxe):

| Produção Gramatical | Ação Semântica Associada |
| :--- | :--- |
| $\text{Passo} \rightarrow \text{PASSE} \;\; \text{ID}_1 \;\; \text{COORD}_1 \;\; \text{"->"} \;\; \text{ID}_2 \;\; \text{COORD}_2$ | $\Delta X = \text{COORD}_2.x - \text{COORD}_1.x$<br>$\text{dist} = \text{calcular\_distancia}(\text{COORD}_1, \text{COORD}_2)$<br>$\text{tipo} = \text{classificar\_passe}(\text{dist})$<br>$\text{dir} = \text{"para frente" if } \Delta X > 0 \text{ else "recuo"}$<br>$\text{Passo.traducao} = \text{formatar}(\text{ID}_1, \text{tipo}, \text{dir}, \text{ID}_2)$ |
| $\text{SequenciaPasses}_1 \rightarrow \text{SequenciaPasses}_2 \;\; \text{Passo}$ | $\text{SequenciaPasses}_1.\text{lista} = \text{SequenciaPasses}_2.\text{lista} + [\text{Passo.traducao}]$ |
| $\text{Lance} \rightarrow \text{CABECALHO} \;\; \text{SequenciaPasses}$ | $\text{Lance.relatorio} = \text{gerar\_relatorio}(\text{CABECALHO}, \text{SequenciaPasses}.\text{lista})$ |

---

## 5. Divisão de Trabalho em Dupla

A divisão foi balanceada para que ambos tenham domínio conceitual do projeto para as reuniões presenciais e para o vídeo final:

| Responsabilidade | Integrante A | Integrante B |
| :--- | :---: | :---: |
| **Frontend do Compilador** | Responsável principal pela definição dos Tokens, Regex e regras léxicas no `ply.lex`. | Apoio e revisão dos tokens de coordenadas e jogadores. |
| **Sintaxe & Gramática** | Construção das produções BNF no `ply.yacc` e tratamento de precedência/conflitos. | Definição da estrutura de nós e atributos sintáticos. |
| **Semântica & Runtime** | Apoio no repasse de atributos entre produções. | Responsável principal pelas Ações Semânticas (cálculo de distâncias, mapeamento do tabuleiro e classificação). |
| **Teoria & Diagramas** | Criação do desenho da **Árvore de Derivação Sintática**. | Construção da **Tabela SDT** e da **Árvore de Derivação Anotada**. |
| **Casos de Teste** | Criação de entradas com erros léxicos e sintáticos para teste. | Criação de entradas com lances válidos de testes reais. |
| **Apresentação e Vídeo** | Apresentação da parte léxica, sintática e árvore no vídeo. | Apresentação das ações semânticas, SDT e execução ao vivo. |

---

## 6. Cronograma e Próximos Passos Imediatos

* **14/10 (Quarta-feira):** Apresentar esta proposta e a escolha do **PLY (Python)** à professora.
* **16/10 (Sexta-feira):** Baixar e rodar o exemplo base do PLY; submeter o **Prompt de IA** detalhado à professora.
* **Acompanhamentos Semanais:** Participar presencialmente apresentando o avanço do código para garantir os **2,0 pontos** de processo.
* **25/11:** Entrega final da tarefa no Teams (Código fonte comentado + Vídeo de até 7 minutos com execução ao vivo).
