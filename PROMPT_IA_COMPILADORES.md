# Especificação dos Prompts: Projeto Compilador Tático de Futebol

> **Disciplina:** Compiladores (2026_2)  
> **Estratégia de Arquitetura:** Divisão em **dois prompts especializados**:  
> * **Prompt 1:** Engenharia de Dados & Modelagem Espacial do Campo (StatsBomb + Grid Cartesiano de 11 Zonas).  
> * **Prompt 2 (OFICIAL PARA A PROFESSORA):** Compilador/Tradutor Dirigido pela Sintaxe em Python com PLY (*ply.lex* e *ply.yacc*).

---

## Modelo Espacial do Campo: As 11 Zonas Táticas

Integrando o plano cartesiano do StatsBomb ($X \in [0, 120]$ e $Y \in [0, 80]$) com a divisão tática em 3 faixas verticais, 3 faixas horizontais e 2 zonas nobres (grandes áreas):

```
 0 (Lateral Superior / Esquerda)                    80 (Lateral Inferior / Direita)
 ┌───────────────────────┬─────────────────────────┬───────────────────────┐ 120 (Ataque)
 │  Ataque Esquerdo      │  [GRANDE ÁREA ATAQUE]   │  Ataque Direito       │
 │  (Ponta Esquerda)     │  Ataque Central         │  (Ponta Direita)      │
 ├───────────────────────┼─────────────────────────┼───────────────────────┤ 80
 │  Meio-Campo Esquerdo  │  Meio-Campo Central     │  Meio-Campo Direito   │
 │                       │  (Círculo Central)      │                       │
 ├───────────────────────┼─────────────────────────┼───────────────────────┤ 40
 │  Defesa Esquerda      │  Defesa Central         │  Defesa Direita       │
 │  (Lateral Esquerda)   │  [GRANDE ÁREA DEFESA]   │  (Lateral Direita)    │
 └───────────────────────┴─────────────────────────┴───────────────────────┘ 0 (Defesa)
```

### Regras Cartesianas de Delimitação das Zonas:
1. **Grande Área de Ataque (Prioridade 1):** $102.0 \le X \le 120.0$ e $18.0 \le Y \le 62.0$ (Zona crítica de finalização).
2. **Grande Área de Defesa (Prioridade 1):** $0.0 \le X \le 18.0$ e $18.0 \le Y \le 62.0$ (Zona crítica do goleiro/zaga).
3. **Ataque Esquerdo:** $80.0 \le X \le 120.0$ e $0.0 \le Y < 25.0$.
4. **Ataque Central:** $80.0 \le X < 102.0$ e $25.0 \le Y \le 55.0$ (fora da grande área).
5. **Ataque Direito:** $80.0 \le X \le 120.0$ e $55.0 < Y \le 80.0$.
6. **Meio-Campo Esquerdo:** $40.0 \le X < 80.0$ e $0.0 \le Y < 25.0$.
7. **Meio-Campo Central:** $40.0 \le X < 80.0$ e $25.0 \le Y \le 55.0$ (Círculo central).
8. **Meio-Campo Direito:** $40.0 \le X < 80.0$ e $55.0 < Y \le 80.0$.
9. **Defesa Esquerda:** $0.0 \le X < 40.0$ e $0.0 \le Y < 25.0$.
10. **Defesa Central:** $18.0 < X < 40.0$ e $25.0 \le Y \le 55.0$ (fora da grande área defensiva).
11. **Defesa Direita:** $0.0 \le X < 40.0$ e $55.0 < Y \le 80.0$.

---

## 📦 PROMPT 1: Módulo de Dados & Grid Espacial do Campo
*(Utilizado internamente pela dupla para gerar o extrator do StatsBomb e o resolvedor de coordenadas)*

```text
Atue como um Engenheiro de Dados e Desenvolvedor Python especializado em Sports Analytics.

Preciso de um módulo Python autônomo ('campo_statsbomb.py') que realiza duas tarefas:

1. MODELAGEM GEOMÉTRICA DO CAMPO EM 11 ZONAS TÁTICAS:
   O campo utiliza o sistema de coordenadas 120x80 do StatsBomb (X de 0.0 a 120.0, Y de 0.0 a 80.0).
   Implemente a função `identificar_zona(x: float, y: float) -> str` que classifica qualquer ponto (X, Y) em uma das 11 zonas:
   - "Grande Area de Ataque": X no intervalo [102, 120] e Y no intervalo [18, 62] (alta prioridade);
   - "Grande Area de Defesa": X no intervalo [0, 18] e Y no intervalo [18, 62] (alta prioridade);
   - "Ataque Esquerdo": X >= 80 e Y < 25;
   - "Ataque Central": X >= 80, X < 102 e 25 <= Y <= 55;
   - "Ataque Direito": X >= 80 e Y > 55;
   - "Meio-Campo Esquerdo": 40 <= X < 80 e Y < 25;
   - "Meio-Campo Central": 40 <= X < 80 e 25 <= Y <= 55;
   - "Meio-Campo Direito": 40 <= X < 80 e Y > 55;
   - "Defesa Esquerda": X < 40 e Y < 25;
   - "Defesa Central": 18 < X < 40 e 25 <= Y <= 55;
   - "Defesa Direita": X < 40 e Y > 55.

2. EXTRAÇÃO E FORMATAÇÃO DE LANCES DO STATSBOMB (statsbombpy):
   Implemente a função `extrair_lance_para_dsl(match_id: int, minuto_inicio: int, segundo_inicio: int, minuto_fim: int, segundo_fim: int) -> str`:
   - Baixa os eventos da partida via `statsbombpy.sb.events(match_id=match_id)`;
   - Filtra os eventos de 'Pass' e 'Shot' ocorridos no intervalo de tempo especificado;
   - Converte os dados brutos (jogadores, coordenadas de origem e destino, tempo) em uma string de código formatada rigorosamente na sintaxe da Linguagem Tática (DSL):
     Exemplo de saída gerada:
     LANCE [14:20 - 14:35] {
         PASSE "Luka Modrić" (25.4, 40.2) -> "Mateo Kovačić" (38.2, 42.1);
         PASSE "Mateo Kovačić" (38.2, 42.1) -> "Ivan Perišić" (85.0, 18.5);
         FINALIZACAO "Andrej Kramarić" (108.5, 39.8) RESULTADO GOL;
     }

Gere o código Python completo, documentado e com testes unitários embutidos.
```

---

## 🎓 PROMPT 2: O Compilador / Tradutor Dirigido pela Sintaxe (PLY)
*(PROMPT OFICIAL PARA APRESENTAR À PROFESSORA ATÉ 16/10 E CITAR NO VÍDEO FINAL)*

```text
Atue como um Engenheiro Especialista em Compiladores e Teoria de Linguagens Formais.

Preciso desenvolver um Compilador/Tradutor Dirigido pela Sintaxe (Syntax-Directed Translator) em Python utilizando o gerador de analisadores PLY (Python Lex-Yacc: ply.lex e ply.yacc).

O objetivo do compilador é receber a descrição textual e estruturada de lances de futebol (composta por timestamps, identificadores de jogadores e coordenadas cartesianas no padrão 120x80 do StatsBomb) e traduzir esses dados brutos em uma narrativa tática em linguagem natural, classificando o tipo de passe, direção e zonas do campo.

Você deve projetar a solução obedecendo com rigor aos seguintes requisitos formais da teoria de compiladores:

1. DEFINIÇÃO LÉXICA (ply.lex):
   - Defina os tokens e expressões regulares (regex) claras para:
     * TEMPO: padrão para timestamps e intervalos (ex: [14:20] ou [14:20 - 14:35]);
     * COORDENADA: tuplas de floats ou inteiros (ex: (25.4, 40.2) ou (38, 42));
     * JOGADOR: strings delimitadas por aspas, com suporte a acentuação e UTF-8 (ex: "Luka Modrić");
     * PALAVRAS-CHAVE: LANCE, PASSE, FINALIZACAO, RESULTADO, GOL, FORA, DEFESA, FASE;
     * DELIMITADORES E OPERADORES: '->', ':', ';', '{', '}'.
   - Implemente descarte de espaços em branco (t_ignore) e função de tratamento de erros léxicos (t_error) com rastreamento de linha e coluna.

2. GRAMÁTICA LIVRE DE CONTEXTO E PARSER (ply.yacc):
   - Crie uma Gramática Livre de Contexto (GLC) em formato BNF estrito.
   - CUIDADOS FORMAIS COM A GRAMÁTICA:
     * Utilize recursão à esquerda (left-recursion) para listas de comandos e sequências de passes, garantindo eficiência na pilha do analisador LALR(1) do PLY e evitando estouro de pilha.
     * Elimine qualquer ambiguidade sintática, assegurando zero conflitos de Shift/Reduce ou Reduce/Reduce.
     * REQUISITO FORMAL DE AUTO-INCORPORAÇÃO (Self-Embedding): Para justificar matematicamente que a linguagem é verdadeiramente Livre de Contexto (Chomsky Tipo 2) e não meramente regular, incorpore suporte a blocos aninhados recursivos (exemplo: um LANCE ou FASE tática pode conter blocos subordinados delimitados por chaves: Bloco -> '{' SequenciaAcoes '}', onde SequenciaAcoes pode conter recursivamente novos Blocos aninhados ou passos atômicos).
   - Defina a função p_error(p) com mensagens claras indicando a linha, coluna e token inesperado.

3. TRADUÇÃO DIRIGIDA PELA SINTAXE (SDT) E AÇÕES SEMÂNTICAS:
   - Associe ações semânticas diretamente a cada produção gramatical através do array 'p' do PLY:
     * Mapeamento Cartesiano em 11 Zonas: Mapeie as coordenadas para as 11 zonas do campo (Grande Área de Ataque [X: 102-120, Y: 18-62], Grande Área de Defesa [X: 0-18, Y: 18-62], Ataque/Meio/Defesa Esquerdo, Central e Direito).
     * Cálculo Vetorial: Calcule a distância euclidiana sqrt((x2 - x1)^2 + (y2 - y1)^2) e as variações delta_x e delta_y.
     * Classificação Semântica do Passe:
       - Passe Curto: dist <= 15m;
       - Passe Médio: 15m < dist <= 30m;
       - Lançamento: dist > 30m;
       - Cruzamento: origem em corredor lateral (Y < 25 ou Y > 55) com destino à Grande Área de Ataque.
     * Vetor Direcional: Classifique se o passe foi "para frente" (delta_x > 0), "recuo" (delta_x < 0) ou "inversão lateral".
   - Repasse os atributos sintetizados ao longo da árvore gramatical até a raiz para gerar o relatório consolidado do lance em linguagem natural.

4. ARTEFATOS FORMAIS E DOCUMENTAÇÃO OBRIGATÓRIA:
   - Forneça a TABELA DE PRODUÇÕES E AÇÕES SEMÂNTICAS (SDT) mapeando cada regra gramatical à sua respectiva ação de cálculo/tradução.
   - Apresente um exemplo de sentença válida aceita pela gramática e desenhe textualmente:
     a) A ÁRVORE DE DERIVAÇÃO SINTÁTICA (Parse Tree pura);
     b) A ÁRVORE DE DERIVAÇÃO ANOTADA (Annotated Parse Tree), exibindo os atributos semânticos calculados em cada nó (distância, zonas, classificação).
   - Comente amplamente o código-fonte, sinalizando onde foram criadas as regras léxicas, regras gramaticais e ações semânticas.

5. MODULARIDADE DE EXECUÇÃO:
   - O código deve permitir dois modos de execução:
     a) Leitura direta de arquivo (.txt / .match) via terminal;
     b) Execução recebendo uma string em memória (para integração com a API do StatsBomb).

Gere o código Python completo, funcional e robusto com o PLY, acompanhado da explicação detalhada de cada módulo.
```
