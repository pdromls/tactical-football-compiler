# Compilador / Tradutor Tático de Futebol (PLY)

**Disciplina:** Compiladores (2026_2) — Ciência da Computação  
**Tecnologias:** Python 3 + PLY (`ply.lex` e `ply.yacc`) + Padrão Cartesiano StatsBomb (120 × 80)

---

## Visão Geral

Este repositório contém a especificação formal e a implementação de um **Compilador/Tradutor Dirigido pela Sintaxe (SDT)** que recebe registros estruturados de lances de uma partida de futebol (timestamps, jogadores e coordenadas cartesianas X, Y no padrão 120 × 80 da StatsBomb) e os traduz para uma **narrativa tática detalhada em linguagem natural**.

**Destaques da versão atual (v2.0 — pós-feedback da professora):**
* **Elementos táticos recursivos** com regra semântica própria: `TABELA`, `TRIANGULACAO`, `CONTRA_ATAQUE` (podem conter uns aos outros);
* **Ações atômicas recursivas:** passe encadeado `PASSE "A" (x,y) -> "B" (x,y) -> "C" (x,y);` (recursão à esquerda, com atributo herdado) e finalização com `REBOTE` (recursão à direita);
* **Campo por equipe:** as coordenadas estão no referencial de quem executa a ação. O relatório mostra cada zona nas duas perspectivas (`Ataque Direito (Croatia) = Defesa Esquerda (Brazil)`), com o cabeçalho opcional `"Croatia" VS "Brazil"`;
* Gramática LALR(1) com **31 produções e 0 conflitos**; 14 testes do compilador + 6 do extrator;
* No código, as marcações `[NOVO]` / `[MODIFICADO]` / `[PLY]` indicam o que foi criado ou adaptado em relação ao exemplo calc do PLY.

---

## Estrutura do Repositório

```text
tactical-football-compiler/
├── docs/                                  # Documentação Formal exigida na disciplina
│   ├── 01_GRAMATICA_BNF.md                # Gramática BNF, Recursão à Esquerda e Prova Chomsky Tipo 2
│   ├── 02_TABELA_SDT.md                   # Modelo das 11 Zonas e Tabela de Tradução Dirigida pela Sintaxe
│   ├── 03_ARVORES_DERIVACAO.md            # Árvores de Derivação Sintática (Pura) e Anotada
│   ├── ENTREGA_PRODUCOES_E_REGRAS_SEMANTICAS.md   # Tabela SDT para a apresentação (31 produções)
│   ├── EXEMPLO_ARVORE_ESTILO_QUADRO_PROFESSORA.md # Árvore numerada [1]..[17]
│   ├── arvore_estilo_professora.png / arvore_recursiva.png
│   ├── gerar_arvores.py                   # Gera as figuras usando as funções do compilador
│   ├── IDEIAS_TCC_CIENCIA_DE_DADOS.md     # Ideias de TCC (20 ideias, triagem e ideia recomendada)
│   ├── REVISAO_CORRECAO_E_TCC.md          # Revisão e correção aplicada
│   └── v1_pre_feedback/                   # Documentação original da v1.0 (20 produções) para comparação
├── src/                                   # Código-fonte modular do Compilador
│   ├── __init__.py
│   ├── lexer.py                           # Analisador Léxico (ply.lex) com suporte UTF-8
│   ├── parser.py                          # Analisador Sintático LALR(1) e Regras SDT (ply.yacc)
│   ├── semantico.py                       # Geometria das 11 Zonas, vetores e gerador de relatórios
│   ├── compilador.py                      # Fachada CompiladorTatico (Modo Arquivo e Modo Memória)
│   └── campo_statsbomb.py                 # Extrator e conversor de partidas da API StatsBomb para a DSL
├── exemplos/                              # Programas de exemplo na linguagem formal (.txt)
│   ├── lance_croacia.txt                  # Lance clássico (Modrić -> Kovačić -> Kramarić, gol)
│   ├── lance_aninhado_fase.txt            # Exemplo de blocos aninhados (Auto-Incorporação) e Cruzamento
│   ├── lance_erro_sintatico.txt           # Exemplo de erro sintático para demonstração do p_error
│   ├── lance_recursivo.txt                # CONTRA_ATAQUE > TABELA, passe encadeado e rebote
│   └── lance_troca_posse.txt              # Confronto "A" VS "B" e zonas nas duas perspectivas
├── tests/                                 # Testes unitários automatizados
│   └── test_compilador.py                 # Validação das 11 zonas, parser, SDT e erros
├── main.py                                # Interface de Linha de Comando (CLI)
├── requirements.txt                       # Dependências do projeto
├── PROPOSTA_TRABALHO_COMPILADORES.md      # Proposta original do trabalho
└── PROMPT_IA_COMPILADORES.md              # Especificação dos prompts do projeto
```

---

## Documentação Teórica e Formal

1. **[Especificação da Gramática BNF (`docs/01_GRAMATICA_BNF.md`)](docs/01_GRAMATICA_BNF.md)**
   * Quádrupla formal `G = (V, Σ, P, S)` e produções em BNF estrita;
   * Recursão à esquerda (lista e passe encadeado) e recursão à direita (rebote) no LALR(1);
   * Auto-incorporação de `<Bloco>`/`<Jogada>` e **prova de não-regularidade** (interseção com linguagem regular + Lema do Bombeamento), logo a linguagem é estritamente Tipo 2.
2. **[Tabela de Tradução Dirigida pela Sintaxe (`docs/02_TABELA_SDT.md`)](docs/02_TABELA_SDT.md)**
   * Mapeamento espacial do campo 120 × 80 nas **11 Zonas Táticas** (com alta prioridade para as Grandes Áreas);
   * Fórmulas vetoriais (`ΔX, ΔY`, distância euclidiana) e regras de classificação de passes (*Curto*, *Médio*, *Lançamento*, *Cruzamento*);
   * Perspectiva de campo por equipe: `(x, y) → (120 − x, 80 − y)`;
   * Tabela das 31 produções × ações semânticas (S-atribuída + um atributo herdado, portanto L-atribuída).
3. **[Árvores de Derivação (`docs/03_ARVORES_DERIVACAO.md`)](docs/03_ARVORES_DERIVACAO.md)**
   * **Árvore de Derivação Sintática (Parse Tree pura)**;
   * **Árvore de Derivação Anotada (Annotated Parse Tree)** com todos os atributos sintetizados passo a passo.

---

## Como Executar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Executar o exemplo padrão em memória
```bash
python main.py
```

### 3. Executar lendo um arquivo `.txt` (Modo Arquivo)
```bash
python main.py exemplos/lance_croacia.txt
python main.py exemplos/lance_aninhado_fase.txt --tokens
python main.py exemplos/lance_recursivo.txt
python main.py exemplos/lance_troca_posse.txt
```

### 3b. Extrair um trecho real da StatsBomb (Croácia x Brasil, Copa 2022)
```bash
python main.py --match-id 3869420 --inicio 2:30 --fim 3:05 --mostrar-dsl
```

### 4. Executar a suíte de testes unitários
```bash
python -m unittest discover -s tests -v
python -m unittest src.campo_statsbomb -v
```
