# Tabela de Tradução Dirigida pela Sintaxe (SDT) e Regras Semânticas

**Disciplina:** Compiladores (2026_2)  
**Projeto:** Tradutor Tático de Futebol Dirigido pela Sintaxe (StatsBomb 120x80)  
**Classificação da SDT:** Definição **S-Atribuída** (todos os atributos são *sintetizados* das folhas até a raiz, avaliados durante as reduções *bottom-up* do parser LALR(1)).

---

## 1. Modelo Espacial Cartesiano: As 11 Zonas do Campo (StatsBomb 120x80)

O campo oficial no padrão StatsBomb possui dimensões X ∈ [0.0, 120.0] (comprimento: defesa → ataque) e Y ∈ [0.0, 80.0] (largura: esquerda → direita).

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

### Função Semântica de Mapeamento de Zona: zona(x, y)

Avaliada com prioridade estrita para as Grandes Áreas:

1. **Prioridade Máxima (Zonas Críticas):**
   * Se 102.0 ≤ x ≤ 120.0 e 18.0 ≤ y ≤ 62.0 \implies "Grande Área de Ataque"
   * Se topo-2.0 ≤ x ≤ 18.0 e 18.0 ≤ y ≤ 62.0 \implies "Grande Área de Defesa"$
2. **Setor de Ataque (x ≥ 80.0):**
   * y < 25.0 \implies "Ataque Esquerdo"
   * 25.0 ≤ y ≤ 55.0 \implies "Ataque Central"
   * y > 55.0 \implies "Ataque Direito"
3. **Setor de Meio-Campo (40.0 ≤ x < 80.0, ou x ≥ 38.0 na faixa de transição central):**
   * y < 25.0 \implies "Meio-Campo Esquerdo"
   * 25.0 ≤ y ≤ 55.0 \implies "Meio-Campo Central"
   * y > 55.0 \implies "Meio-Campo Direito"
4. **Setor de Defesa (x < 40.0):**
   * y < 25.0 \implies "Defesa Esquerda"
   * 25.0 ≤ y ≤ 55.0 \implies "Defesa Central"
   * y > 55.0 \implies "Defesa Direita"

---

## 2. Funções Vetoriais e de Classificação Tática

Para dois pontos C_1 = (x_1, y_1) e C_2 = (x_2, y_2):

* **Variações Escalares:** ΔX = x_2 - x_1 e ΔY = y_2 - y_1
* **Distância Euclidiana:**
  dist(C_1, C_2) = √((x_2 - x_1)^2 + (y_2 - y_1)^2)
* **Classificação do Passe classificarPasse(d, z_{orig}, z_{dest}, ΔX):**
  1. **Cruzamento (Alta Prioridade):** Se z_{orig} pertence a qualquer corredor lateral (Y < 25 ou Y > 55) **e** z_{dest} = "Grande Área de Ataque", retorna `("Cruzamento", "para a Grande Área")`.
  2. **Passe Curto:** Se d ≤ 15.0m, retorna `"Passe curto"`.
  3. **Passe Médio:** Se 15.0m < d ≤ 30.0m, retorna `"Passe médio"`.
  4. **Lançamento Longo:** Se d > 30.0m, retorna `"Lançamento longo"`.
* **Vetor Direcional dir(ΔX, ΔY, z_{dest}):**
  * Se ΔX ≥ 25.0 ou `"Ataque"` ∈ z_{dest} \implies "para o ataque"
  * Senão, se ΔX > 3.0 \implies "para frente"
  * Senão, se ΔX < -3.0 \implies "para trás (recuo)"
  * Caso contrário (|ΔX| ≤ 3.0 e |ΔY| > 15.0) \implies "em inversão lateral" (ou `"lateral"`).

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
| **14** | `<Passe> ::= PASSE JOGADOR_1 <Coordenada>_1 '->' JOGADOR_2 <Coordenada>_2` | d = dist(<Coordenada>_1.val, <Coordenada>_2.val)<br>ΔX = <Coordenada>_2.x - <Coordenada>_1.x<br>ΔY = <Coordenada>_2.y - <Coordenada>_1.y<br>z_o = zona(<Coordenada>_1.x, <Coordenada>_1.y)<br>z_d = zona(<Coordenada>_2.x, <Coordenada>_2.y)<br>(tipo, dir) = classificarPasse(d, z_o, z_d, ΔX)<br>`<Passe>.info = { "tipo_acao": "PASSE", "autor": JOGADOR_1.lexval, "receptor": JOGADOR_2.lexval, "coord_orig": <Coordenada>_1.val, "coord_dest": <Coordenada>_2.val, "distancia": round(d, 1), "zona_orig": z_o, "zona_dest": z_d, "classificacao": tipo, "direcao": dir }` |
| **15** | `<Finalizacao> ::= FINALIZACAO JOGADOR <Coordenada> RESULTADO <Desfecho>` | z_o = zona(<Coordenada>.x, <Coordenada>.y)<br>`<Finalizacao>.info = { "tipo_acao": "FINALIZACAO", "autor": JOGADOR.lexval, "coord_orig": <Coordenada>.val, "zona_orig": z_o, "zona_dest": z_o, "desfecho": <Desfecho>.val }` |
| **16** | `<Coordenada> ::= '(' NUM_1 ',' NUM_2 ')'` | Verifica topo-2 ≤ NUM_1 ≤ 120 e topo-2 ≤ NUM_2 ≤ 80;<br>`<Coordenada>.x = float(NUM_1.lexval)`<br>`<Coordenada>.y = float(NUM_2.lexval)`<br>`<Coordenada>.val = (float(NUM_1.lexval), float(NUM_2.lexval))` |
| **17** | `<Desfecho> ::= GOL` | `<Desfecho>.val = "GOL!"` |
| **18** | `<Desfecho> ::= DEFESA` | `<Desfecho>.val = "DEFESA DO GOLEIRO!"` |
| **19** | `<Desfecho> ::= FORA` | `<Desfecho>.val = "PARA FORA!"` |
| **20** | `<Desfecho> ::= TRAVE` | `<Desfecho>.val = "NA TRAVE!"` |
