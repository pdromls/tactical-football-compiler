# Compilador / Tradutor Tático de Futebol (PLY)

**Disciplina:** Compiladores (2026_2) — Ciência da Computação  
**Tecnologias:** Python 3 + PLY (`ply.lex` e `ply.yacc`) + Padrão Cartesiano StatsBomb ($120 \times 80$)

---

## 📌 Visão Geral

Este repositório contém a especificação formal e a implementação de um **Compilador/Tradutor Dirigido pela Sintaxe (SDT)** que recebe registros estruturados de lances de uma partida de futebol (timestamps, jogadores e coordenadas cartesianas $X, Y$ no padrão $120 \times 80$ da StatsBomb) e os traduz para uma **narrativa tática detalhada em linguagem natural**.

---

## 📂 Estrutura do Repositório

```text
Trabalho Compiladores/
├── docs/                                  # Documentação Formal exigida na disciplina
│   ├── 01_GRAMATICA_BNF.md                # Gramática BNF, Recursão à Esquerda e Prova Chomsky Tipo 2
│   ├── 02_TABELA_SDT.md                   # Modelo das 11 Zonas e Tabela de Tradução Dirigida pela Sintaxe
│   └── 03_ARVORES_DERIVACAO.md            # Árvores de Derivação Sintática (Pura) e Anotada
├── src/                                   # Código-fonte modular do Compilador
│   ├── __init__.py
│   ├── lexer.py                           # Analisador Léxico (ply.lex) com suporte UTF-8
│   ├── parser.py                          # Analisador Sintático LALR(1) e Regras SDT (ply.yacc)
│   ├── semantico.py                       # Geometria das 11 Zonas, vetores e gerador de relatórios
│   ├── compilador.py                      # Fachada CompiladorTatico (Modo Arquivo e Modo Memória)
│   └── campo_statsbomb.py                 # Extrator e conversor de partidas da API StatsBomb para a DSL
├── exemplos/                              # Programas de exemplo na linguagem formal (.txt)
│   ├── lance_croacia.txt                  # Lance clássico (Modrić -> Kovačić -> Perišić -> Kramarić)
│   ├── lance_aninhado_fase.txt            # Exemplo de blocos aninhados (Auto-Incorporação) e Cruzamento
│   └── lance_erro_sintatico.txt           # Exemplo de erro sintático para demonstração do p_error
├── tests/                                 # Testes unitários automatizados
│   └── test_compilador.py                 # Validação das 11 zonas, parser, SDT e erros
├── main.py                                # Interface de Linha de Comando (CLI)
├── requirements.txt                       # Dependências do projeto
├── PROPOSTA_TRABALHO_COMPILADORES.md      # Proposta original do trabalho
└── PROMPT_IA_COMPILADORES.md              # Especificação dos prompts do projeto
```

---

## 📚 Documentação Teórica e Formal

1. **[Especificação da Gramática BNF (`docs/01_GRAMATICA_BNF.md`)](docs/01_GRAMATICA_BNF.md)**
   * Quádrupla formal $G = (V, \Sigma, P, S)$ e produções em BNF estrita;
   * Explicação da **Recursão à Esquerda** para eficiência $O(1)$ na pilha do analisador LALR(1);
   * Demonstração matemática da **Auto-Incorporação (*Self-Embedding*)** ($\langle\text{Bloco}\rangle \Rightarrow^+ \texttt{'\{'} \ \langle\text{Bloco}\rangle \ \texttt{'\}'}$) provando que a linguagem é Livre de Contexto (Chomsky Tipo 2).
2. **[Tabela de Tradução Dirigida pela Sintaxe (`docs/02_TABELA_SDT.md`)](docs/02_TABELA_SDT.md)**
   * Mapeamento espacial do campo $120 \times 80$ nas **11 Zonas Táticas** (com alta prioridade para as Grandes Áreas);
   * Fórmulas vetoriais ($\Delta X, \Delta Y$, distância euclidiana) e regras de classificação de passes (*Curto*, *Médio*, *Lançamento*, *Cruzamento*);
   * Tabela completa de produções BNF $\times$ ações semânticas S-atribuídas.
3. **[Árvores de Derivação (`docs/03_ARVORES_DERIVACAO.md`)](docs/03_ARVORES_DERIVACAO.md)**
   * **Árvore de Derivação Sintática (Parse Tree pura)**;
   * **Árvore de Derivação Anotada (Annotated Parse Tree)** com todos os atributos sintetizados passo a passo.

---

## 🚀 Como Executar

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
```

### 4. Executar a suíte de testes unitários
```bash
python -m unittest discover -s tests -v
```
