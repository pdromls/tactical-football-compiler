# Tabela de Tradução Dirigida pela Sintaxe (SDT) e Regras Semânticas

**Disciplina:** Compiladores (2026_2)  
**Projeto:** Tradutor Tático de Futebol Dirigido pela Sintaxe (StatsBomb 120x80)  
**Classificação da SDT:** Definição **S-Atribuída** (todos os atributos são *sintetizados* das folhas até a raiz, avaliados durante as reduções *bottom-up* do parser LALR(1)).

---

## 1. Modelo Espacial Cartesiano: As 11 Zonas do Campo (StatsBomb 120x80)

O campo oficial no padrão StatsBomb possui dimensões $X \in [0.0, 120.0]$ (comprimento: defesa $\rightarrow$ ataque) e $Y \in [0.0, 80.0]$ (largura: esquerda $\rightarrow$ direita).

```text
 0.0 (Corredor Esquerdo)                             80.0 (Corredor Direito)
 ┌───────────────────────┬─────────────────────────┬───────────────────────┐ 120.0 (Linha de Fundo Ataque)
 │  Ataque Esquerdo      │  [GRANDE ÁREA ATAQUE]   │  Ataque Direito       │
 │  (Y < 25)             │  X:[102,120] Y:[18,62]  │  (Y > 55)             │
 │                       │  Ataque Central         │                       │
 ├───────────────────────┼─────────────────────────┼───────────────────────┤ 80.0
 │  Meio-Campo Esquerdo  │  Meio-Campo Central     │  Meio-Campo Direito   │
 │  (40 <= X < 80)       │  (25 <= Y <= 55)        │  (40 <= X < 80)       │
 ├───────────────────────┼─────────────────────────┼───────────────────────┤ 40.0
 │  Defesa Esquerda      │  Defesa Central         │  Defesa Direita       │
 │  (X < 40)             │  [GRANDE ÁREA DEFESA]   │  (X < 40)             │
 │                       │  X:[0,18]    Y:[18,62]  │                       │
 └───────────────────────┴─────────────────────────┴───────────────────────┘ 0.0 (Linha de Fundo Defesa)
```

### Função Semântica de Mapeamento de Zona: $\text{zona}(x, y)$

Avaliada com prioridade estrita para as Grandes Áreas:

1. **Prioridade Máxima (Zonas Críticas):**
   * Se $102.0 \le x \le 120.0$ e $18.0 \le y \le 62.0 \implies \text{"Grande Área de Ataque"}$
   * Se $0.0 \le x \le 18.0$ e $18.0 \le y \le 62.0 \implies \text{"Grande Área de Defesa"}$
2. **Setor de Ataque ($x \ge 80.0$):**
   * $y < 25.0 \implies \text{"Ataque Esquerdo"}$
   * $25.0 \le y \le 55.0 \implies \text{"Ataque Central"}$
   * $y > 55.0 \implies \text{"Ataque Direito"}$
3. **Setor de Meio-Campo ($40.0 \le x < 80.0$, ou $x \ge 38.0$ na faixa de transição central):**
   * $y < 25.0 \implies \text{"Meio-Campo Esquerdo"}$
   * $25.0 \le y \le 55.0 \implies \text{"Meio-Campo Central"}$
   * $y > 55.0 \implies \text{"Meio-Campo Direito"}$
4. **Setor de Defesa ($x < 40.0$):**
   * $y < 25.0 \implies \text{"Defesa Esquerda"}$
   * $25.0 \le y \le 55.0 \implies \text{"Defesa Central"}$
   * $y > 55.0 \implies \text{"Defesa Direita"}$

---

## 2. Funções Vetoriais e de Classificação Tática

Para dois pontos $C_1 = (x_1, y_1)$ e $C_2 = (x_2, y_2)$:

* **Variações Escalares:** $\Delta X = x_2 - x_1$ e $\Delta Y = y_2 - y_1$
* **Distância Euclidiana:**
  $$\text{dist}(C_1, C_2) = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$$
* **Classificação do Passe $\text{classificarPasse}(d, z_{orig}, z_{dest}, \Delta X)$:**
  1. **Cruzamento (Alta Prioridade):** Se $z_{orig}$ pertence a qualquer corredor lateral ($Y < 25$ ou $Y > 55$) **e** $z_{dest} = \text{"Grande Área de Ataque"}$, retorna `("Cruzamento", "para a Grande Área")`.
  2. **Passe Curto:** Se $d \le 15.0\text{m}$, retorna `"Passe curto"`.
  3. **Passe Médio:** Se $15.0\text{m} < d \le 30.0\text{m}$, retorna `"Passe médio"`.
  4. **Lançamento Longo:** Se $d > 30.0\text{m}$, retorna `"Lançamento longo"`.
* **Vetor Direcional $\text{dir}(\Delta X, \Delta Y, z_{dest})$:**
  * Se $\Delta X \ge 25.0$ ou `"Ataque"` $\in z_{dest} \implies \text{"para o ataque"}$
  * Senão, se $\Delta X > 3.0 \implies \text{"para frente"}$
  * Senão, se $\Delta X < -3.0 \implies \text{"para trás (recuo)"}$
  * Caso contrário ($|\Delta X| \le 3.0$ e $|\Delta Y| > 15.0$) $\implies \text{"em inversão lateral"}$ (ou `"lateral"`).

---

## 3. Tabela Formal de Tradução Dirigida pela Sintaxe (SDT)

Na implementação com `ply.yacc`, cada símbolo do lado esquerdo da produção corresponde a `p[0]`, e os símbolos do lado direito correspondem a `p[1]`, `p[2]`, ..., `p[n]`.

| # | Produção Gramatical (BNF) | Ação / Regra Semântica Associada |
| :-: | :--- | :--- |
| **1** | `<Lance> ::= LANCE <IntervaloTempo> <Bloco>` | `<Lance>.relatorio = formatar_relatorio(<IntervaloTempo>.val, <Bloco>.acoes)`<br>*(No PLY: `p[0] = gerar_relatorio_final(p[2], p[3])`)* |
| **2** | `<IntervaloTempo> ::= '[' TEMPO_1 '-' TEMPO_2 ']'` | `<IntervaloTempo>.val = { "inicio": TEMPO_1.lexval, "fim": TEMPO_2.lexval, "duracao_seg": seg(TEMPO_2.lexval) - seg(TEMPO_1.lexval) }`<br>*(No PLY: `p[0] = calc_intervalo(p[2], p[4])`)* |
| **3** | `<Bloco> ::= '{' <SequenciaAcoes> '}'` | `<Bloco>.acoes = <SequenciaAcoes>.lista`<br>*(No PLY: `p[0] = p[2]`)* |
| **4** | `<Bloco> ::= FASE JOGADOR '{' <SequenciaAcoes> '}'` | `<Bloco>.acoes = anotar_fase(JOGADOR.lexval, <SequenciaAcoes>.lista)`<br>*(No PLY: `p[0] = anotar_fase(p[2], p[4])`)* |
| **5** | `<Bloco> ::= POSSE JOGADOR '{' <SequenciaAcoes> '}'` | `<Bloco>.acoes = anotar_posse_equipe(JOGADOR.lexval, <SequenciaAcoes>.lista)`<br>*(Define a equipe detentora da posse e o referencial das 11 zonas)* |
| **6** | `<SequenciaAcoes> ::= <SequenciaAcoes>_1 <ElementoTatico>` | `<SequenciaAcoes>.lista = <SequenciaAcoes>_1.lista + <ElementoTatico>.lista`<br>*(No PLY: `p[0] = p[1] + p[2]` — acumulação recursiva à esquerda)* |
| **7** | `<SequenciaAcoes> ::= <ElementoTatico>` | `<SequenciaAcoes>.lista = <ElementoTatico>.lista`<br>*(No PLY: `p[0] = p[1]`)* |
| **8** | `<ElementoTatico> ::= <AcaoAtomica>` | `<ElementoTatico>.lista = [ <AcaoAtomica>.info ]`<br>*(No PLY: `p[0] = [p[1]]`)* |
| **9** | `<ElementoTatico> ::= <Bloco>` | `<ElementoTatico>.lista = <Bloco>.acoes`<br>*(No PLY: `p[0] = p[1]` — sintetiza sub-blocos aninhados por auto-incorporação)* |
| **10** | `<AcaoAtomica> ::= <Passe> ';'` | `<AcaoAtomica>.info = <Passe>.info`<br>*(No PLY: `p[0] = p[1]`)* |
| **11** | `<AcaoAtomica> ::= <Finalizacao> ';'` | `<AcaoAtomica>.info = <Finalizacao>.info`<br>*(No PLY: `p[0] = p[1]`)* |
| **12** | `<AcaoAtomica> ::= <TrocaPosse> ';'` | `<AcaoAtomica>.info = <TrocaPosse>.info`<br>*(No PLY: `p[0] = p[1]`)* |
| **13** | `<TrocaPosse> ::= TROCA_POSSE JOGADOR` | `<TrocaPosse>.info = { "tipo_acao": "TROCA_POSSE", "nova_equipe": JOGADOR.lexval }`<br>*(Registra a inversão de posse e do referencial espacial do campo)* |
| **14** | `<Passe> ::= PASSE JOGADOR_1 <Coordenada>_1 '->' JOGADOR_2 <Coordenada>_2` | $d = \text{dist}(\langle\text{Coordenada}\rangle_1.\text{val}, \langle\text{Coordenada}\rangle_2.\text{val})$<br>$\Delta X = \langle\text{Coordenada}\rangle_2.x - \langle\text{Coordenada}\rangle_1.x$<br>$\Delta Y = \langle\text{Coordenada}\rangle_2.y - \langle\text{Coordenada}\rangle_1.y$<br>$z_o = \text{zona}(\langle\text{Coordenada}\rangle_1.x, \langle\text{Coordenada}\rangle_1.y)$<br>$z_d = \text{zona}(\langle\text{Coordenada}\rangle_2.x, \langle\text{Coordenada}\rangle_2.y)$<br>$(\text{tipo}, \text{dir}) = \text{classificarPasse}(d, z_o, z_d, \Delta X)$<br>`<Passe>.info = { "tipo_acao": "PASSE", "autor": JOGADOR_1.lexval, "receptor": JOGADOR_2.lexval, "coord_orig": <Coordenada>_1.val, "coord_dest": <Coordenada>_2.val, "distancia": round(d, 1), "zona_orig": z_o, "zona_dest": z_d, "classificacao": tipo, "direcao": dir }` |
| **15** | `<Finalizacao> ::= FINALIZACAO JOGADOR <Coordenada> RESULTADO <Desfecho>` | $z_o = \text{zona}(\langle\text{Coordenada}\rangle.x, \langle\text{Coordenada}\rangle.y)$<br>`<Finalizacao>.info = { "tipo_acao": "FINALIZACAO", "autor": JOGADOR.lexval, "coord_orig": <Coordenada>.val, "zona_orig": z_o, "zona_dest": z_o, "desfecho": <Desfecho>.val }` |
| **16** | `<Coordenada> ::= '(' NUM_1 ',' NUM_2 ')'` | Verifica $0 \le \text{NUM}_1 \le 120$ e $0 \le \text{NUM}_2 \le 80$;<br>`<Coordenada>.x = float(NUM_1.lexval)`<br>`<Coordenada>.y = float(NUM_2.lexval)`<br>`<Coordenada>.val = (float(NUM_1.lexval), float(NUM_2.lexval))` |
| **17** | `<Desfecho> ::= GOL` | `<Desfecho>.val = "GOL!"` |
| **18** | `<Desfecho> ::= DEFESA` | `<Desfecho>.val = "DEFESA DO GOLEIRO!"` |
| **19** | `<Desfecho> ::= FORA` | `<Desfecho>.val = "PARA FORA!"` |
| **20** | `<Desfecho> ::= TRAVE` | `<Desfecho>.val = "NA TRAVE!"` |
