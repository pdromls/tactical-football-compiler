# Especificação das Produções Gramaticais e Regras Semânticas (SDT)

**Disciplina:** Compiladores (2026_2)  
**Projeto:** Tradutor Tático de Lances de Futebol (Padrão Cartesiano StatsBomb 120x80)  
**Gerador de Analisadores:** PLY (*Python Lex-Yacc* — **ply.lex** e **ply.yacc**)

---

## 1. Visão Geral da Tradução Dirigida pela Sintaxe (SDT)

O compilador implementa um **Esquema de Tradução S-Atribuído**: todos os atributos são **sintetizados**, fluindo das folhas para a raiz durante as reduções *bottom-up* do analisador sintático LALR(1) do **ply.yacc**.

* **Símbolos Não-Terminais (V):** \<Lance\>, \<IntervaloTempo\>, \<Bloco\>, \<SequenciaAcoes\>, \<ElementoTatico\>, \<AcaoAtomica\>, \<TrocaPosse\>, \<Passe\>, \<Finalizacao\>, \<Coordenada\>, \<Desfecho\>
* **Símbolos Terminais / Tokens (Σ):** **LANCE**, **FASE**, **POSSE**, **TROCA_POSSE**, **PASSE**, **FINALIZACAO**, **RESULTADO**, **GOL**, **DEFESA**, **FORA**, **TRAVE**, **TEMPO**, **JOGADOR**, **NUM**, **SETA** ("->"), "[", "]", "-", "{", "}", "(", ")", ",", ";"

---

## 2. Tabela de Produções e Regras Semânticas (SDT)

Na coluna **Regra Semântica (Notação SDT)** utilizamos a notação clássica de atributos dos slides de *Tradução Dirigida pela Sintaxe* (ex: **X.val**, **X.trad**, **X.lista**), e na coluna à direita mostramos a implementação direta no vetor **p** do **ply.yacc**:

| # | Produção Gramatical (BNF) | Regra Semântica Associada (Notação SDT) | Implementação no ply.yacc (src/parser.py) |
| :-: | :--- | :--- | :--- |
| **1** | \<Lance\> → **LANCE** \<IntervaloTempo\> \<Bloco\> | Lance.relatorio = gerar_relatorio(IntervaloTempo.val, Bloco.lista) | p[0] = gerar_relatorio_final(p[2], p[3]) |
| **2** | \<IntervaloTempo\> → '[' **TEMPO₁** '-' **TEMPO₂** ']' | IntervaloTempo.ini = TEMPO₁.lexval<br>IntervaloTempo.fim = TEMPO₂.lexval<br>IntervaloTempo.duracao = seg(TEMPO₂.lexval) - seg(TEMPO₁.lexval) | p[0] = {"inicio": p[2], "fim": p[4], "duracao_seg": seg_fim - seg_ini} |
| **3** | \<Bloco\> → '{' \<SequenciaAcoes\> '}' | Bloco.lista = SequenciaAcoes.lista | p[0] = p[2] |
| **4** | \<Bloco\> → **FASE** **JOGADOR** '{' \<SequenciaAcoes\> '}' | Bloco.lista = anotar_fase(JOGADOR.lexval, SequenciaAcoes.lista) | p[0] = anotar_fase(p[2], p[4]) |
| **5** | \<Bloco\> → **POSSE** **JOGADOR** '{' \<SequenciaAcoes\> '}' | Bloco.lista = anotar_posse_equipe(JOGADOR.lexval, SequenciaAcoes.lista)<br>*(Define de qual equipe são as zonas de Defesa/Meio/Ataque)* | p[0] = anotar_posse(p[2], p[4]) |
| **6** | \<SequenciaAcoes\> → \<SequenciaAcoes\>₁ \<ElementoTatico\> | SequenciaAcoes.lista = SequenciaAcoes₁.lista + ElementoTatico.lista<br>*(Recursão à esquerda acumulando a lista de ações)* | p[0] = p[1] + p[2] |
| **7** | \<SequenciaAcoes\> → \<ElementoTatico\> | SequenciaAcoes.lista = ElementoTatico.lista | p[0] = p[1] |
| **8** | \<ElementoTatico\> → \<AcaoAtomica\> | ElementoTatico.lista = [ AcaoAtomica.trad ] | p[0] = [p[1]] |
| **9** | \<ElementoTatico\> → \<Bloco\> | ElementoTatico.lista = Bloco.lista<br>*(Auto-incorporação: permite sub-blocos aninhados)* | p[0] = p[1] |
| **10** | \<AcaoAtomica\> → \<Passe\> ';' | AcaoAtomica.trad = Passe.trad | p[0] = p[1] |
| **11** | \<AcaoAtomica\> → \<Finalizacao\> ';' | AcaoAtomica.trad = Finalizacao.trad | p[0] = p[1] |
| **12** | \<AcaoAtomica\> → \<TrocaPosse\> ';' | AcaoAtomica.trad = TrocaPosse.trad | p[0] = p[1] |
| **13** | \<TrocaPosse\> → **TROCA_POSSE** **JOGADOR** | TrocaPosse.trad = { tipo: "TROCA_POSSE", nova_equipe: JOGADOR.lexval } | p[0] = {"tipo_acao": "TROCA_POSSE", "nova_equipe": p[2]} |
| **14** | \<Passe\> → **PASSE** **JOGADOR₁** \<Coordenada\>₁ **SETA** **JOGADOR₂** \<Coordenada\>₂ | ΔX = Coordenada₂.x - Coordenada₁.x<br>ΔY = Coordenada₂.y - Coordenada₁.y<br>d = √(ΔX² + ΔY²)<br>z_orig = identificar_zona(Coordenada₁.x, Coordenada₁.y)<br>z_dest = identificar_zona(Coordenada₂.x, Coordenada₂.y)<br>(tipo, dir) = classificar_passe(d, ΔX, ΔY, z_orig, z_dest)<br>Passe.trad = montar_passe(JOGADOR₁.lexval, JOGADOR₂.lexval, d, z_orig, z_dest, tipo, dir) | dist = calcular_distancia(p[3], p[6])<br>z_orig = identificar_zona(...)<br>z_dest = identificar_zona(...)<br>tipo, dir = classificar_passe(...)<br>p[0] = {...} |
| **15** | \<Finalizacao\> → **FINALIZACAO** **JOGADOR** \<Coordenada\> **RESULTADO** \<Desfecho\> | z_orig = identificar_zona(Coordenada.x, Coordenada.y)<br>Finalizacao.trad = montar_chute(JOGADOR.lexval, z_orig, Desfecho.val) | z_orig = identificar_zona(p[3][0], p[3][1])<br>p[0] = {"tipo_acao": "FINALIZACAO", "autor": p[2], "zona_orig": z_orig, "desfecho": p[5]} |
| **16** | \<Coordenada\> → '(' **NUM₁** ',' **NUM₂** ')' | Verifica 0 ≤ NUM₁.val ≤ 120 e 0 ≤ NUM₂.val ≤ 80;<br>Coordenada.x = NUM₁.val<br>Coordenada.y = NUM₂.val | p[0] = (p[2], p[4]) |
| **17** | \<Desfecho\> → **GOL** | Desfecho.val = "GOL!" | p[0] = "GOL!" |
| **18** | \<Desfecho\> → **DEFESA** | Desfecho.val = "DEFESA DO GOLEIRO!" | p[0] = "DEFESA DO GOLEIRO!" |
| **19** | \<Desfecho\> → **FORA** | Desfecho.val = "PARA FORA!" | p[0] = "PARA FORA!" |
| **20** | \<Desfecho\> → **TRAVE** | Desfecho.val = "NA TRAVE!" | p[0] = "NA TRAVE!" |

---

## 3. Detalhamento das Funções Auxiliares das Regras Semânticas

Detalhamento das funções invocadas nas **Produções #14** e **#15**:

### 3.1. Função identificar_zona(x, y) — Mapeamento Cartesiano (11 Zonas)
Converte qualquer par **(x, y)** do campo **120 x 80** (no referencial da equipe com a posse da bola) em uma das 11 zonas táticas:
* **Grandes Áreas (Prioridade 1):**
  * **102 ≤ x ≤ 120** e **18 ≤ y ≤ 62** → "Grande Área de Ataque"
  * **0 ≤ x ≤ 18** e **18 ≤ y ≤ 62** → "Grande Área de Defesa"
* **Divisão longitudinal (X) × Corredor transversal (Y):**
  * **Setor:** Defesa (**x < 38**), Meio-Campo (**38 ≤ x < 80**), Ataque (**x ≥ 80**).
  * **Corredor:** Esquerdo (**y < 25**), Central (**25 ≤ y ≤ 55**), Direito (**y > 55**).

### 3.2. Função classificar_passe(d, ΔX, ΔY, z_orig, z_dest)
* **Tipo do Passe:**
  * Se **z_orig** pertence a um corredor lateral (**y < 25** ou **y > 55**) **e** **z_dest == "Grande Área de Ataque"** → **Cruzamento**;
  * Senão, se **d ≤ 15m** → **Passe curto**;
  * Senão, se **15m < d ≤ 30m** → **Passe médio**;
  * Senão (**d > 30m**) → **Lançamento longo**.
* **Direção Vetorial:**
  * **ΔX ≥ 25** ou destino no setor de Ataque → "para o ataque";
  * **ΔX > 2** → "para frente";
  * **ΔX < -2** → "para trás (recuo)";
  * **|ΔX| ≤ 2** e **|ΔY| ≥ 20** → "em inversão lateral".
