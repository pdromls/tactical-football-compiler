# Tabela de Tradução Dirigida pela Sintaxe (SDT) e Regras Semânticas

**Disciplina:** Compiladores (2026_2)  
**Projeto:** Tradutor Tático de Futebol Dirigido pela Sintaxe (StatsBomb 120 × 80)  
**Numeração:** idêntica a `01_GRAMATICA_BNF.md` e às árvores.

---

## 1. Modelo espacial: as 11 zonas do campo (StatsBomb 120 × 80)

O campo tem `X ∈ [0, 120]` (comprimento, **da própria defesa para o ataque**) e `Y ∈ [0, 80]` (largura, da esquerda para a direita **de quem ataca**).

```text
 Y=0 (Corredor Esquerdo)                              Y=80 (Corredor Direito)
 ┌───────────────────────┬─────────────────────────┬───────────────────────┐ X=120 (gol adversário)
 │  Ataque Esquerdo      │  [GRANDE ÁREA ATAQUE]   │  Ataque Direito       │
 │  (Y < 25)             │  X:[102,120] Y:[18,62]  │  (Y > 55)             │
 │                       │  Ataque Central         │                       │
 ├───────────────────────┼─────────────────────────┼───────────────────────┤ X=80
 │  Meio-Campo Esquerdo  │  Meio-Campo Central     │  Meio-Campo Direito   │
 ├───────────────────────┼─────────────────────────┼───────────────────────┤ X=40
 │  Defesa Esquerda      │  Defesa Central         │  Defesa Direita       │
 │                       │  [GRANDE ÁREA DEFESA]   │                       │
 │                       │  X:[0,18]    Y:[18,62]  │                       │
 └───────────────────────┴─────────────────────────┴───────────────────────┘ X=0 (própria linha de fundo)
```

### Função `identificar_zona(x, y)`: **uma única definição** em `src/semantico.py`

1. **Prioridade máxima:** `102 <= x <= 120` e `18 <= y <= 62` → "Grande Área de Ataque"; `0 <= x <= 18` e `18 <= y <= 62` → "Grande Área de Defesa".
2. **Setor** (eixo X): Defesa `x < 40` · Meio-Campo `40 <= x < 80` · Ataque `x >= 80` (três terços iguais).
3. **Corredor** (eixo Y): Esquerdo `y < 25` · Central `25 <= y <= 55` · Direito `y > 55`.

> Correção aplicada: antes o compilador usava `x >= 38` para o meio-campo e o extrator usava `x >= 40`. Havia 644 pontos do campo (grade de 0,5 m) classificados de forma diferente. Agora o extrator importa a mesma função.

---

## 2. Perspectiva por equipe: o ataque de um é a defesa do outro

As coordenadas estão sempre no **referencial do time que executa a ação** (padrão StatsBomb). Para saber onde o mesmo ponto fica para o adversário:

`espelhar(x, y) = (120 − x, 80 − y)` e `zona_para_adversario(c) = identificar_zona(espelhar(c))`

| Ponto (referencial da Croácia) | Zona para a Croácia | Mesmo ponto para o Brasil | Zona para o Brasil |
| :--- | :--- | :--- | :--- |
| (85, 18.5) | Ataque Esquerdo | (35, 61.5) | Defesa Direita |
| (110, 40) | Grande Área de Ataque | (10, 40) | Grande Área de Defesa |
| (60, 40) | Meio-Campo Central | (60, 40) | Meio-Campo Central |

O relatório imprime cada zona nas duas perspectivas, por exemplo `Ataque Direito (Croatia) = Defesa Esquerda (Brazil)`. Na troca de posse, ele informa o **local da recuperação** para os dois times. Isso exige saber quem é o adversário: vem do cabeçalho `"A" VS "B"` (#2) ou, sem ele, das equipes que aparecem nas posses.

---

## 3. Funções de classificação

Para `C₁ = (x₁, y₁)` e `C₂ = (x₂, y₂)`: `ΔX = x₂ − x₁`, `ΔY = y₂ − y₁`, `d = √(ΔX² + ΔY²)`.

**Tipo do passe** (`classificar_passe`):
1. **Cruzamento:** origem no setor de ataque (`x₁ >= 80`) **e** num corredor lateral (`y₁ < 25` ou `y₁ > 55`) **e** destino na Grande Área de Ataque. *(Correção aplicada: antes não exigia `x₁ >= 80`, e um passe longo da Defesa Esquerda virava "cruzamento".)*
2. **Passe curto:** `d <= 15` m · **Passe médio:** `15 < d <= 30` m · **Lançamento longo:** `d > 30` m.

**Direção:**
* `ΔX >= 25`, **ou** (`ΔX > 2` **e** destino no setor de Ataque) → "para o ataque" *(antes bastava o destino estar no Ataque, e um toque de lado virava "para o ataque")*;
* senão `ΔX > 2` → "para frente"; `ΔX < -2` → "para trás (recuo)";
* senão `|ΔY| >= 20` → "em inversão lateral"; caso contrário → "lateral".

**Verificações semânticas** (abortam a compilação com `ValueError`): coordenada fora de 120×80 (#27), tempo final < inicial (#4), confronto de um time contra ele mesmo (#2), equipe fora do confronto (#1), `TABELA`/`TRIANGULACAO`/`CONTRA_ATAQUE` inconsistentes (#13–#15).

**Avisos semânticos** (não abortam): quebra de continuidade, quando quem age não é quem recebeu o passe anterior da mesma equipe. Nos dados reais há conduções e disputas que não viram eventos da DSL, por isso é aviso e não erro.

**Horários:** a DSL só tem o intervalo do lance. O horário de cada ação é **interpolado** e exibido com `~`.

---

## 4. Tabela de Tradução Dirigida pela Sintaxe (31 produções)

Definição predominantemente **S-atribuída** (atributos sintetizados, avaliados nas reduções *bottom-up*), com **um atributo herdado** em #21. Isso a torna uma definição **L-atribuída**: o atributo herdado depende apenas de irmãos à esquerda, que já estão na pilha do parser LR.

| # | Produção (BNF) | Regra semântica (notação SDT) | Implementação no ply.yacc (`src/parser.py`) |
| :-: | :--- | :--- | :--- |
| **1** | \<Lance\> → **LANCE** \<IntervaloTempo\> \<Confronto\> \<Bloco\> | Verifica: toda equipe de `Bloco.lista` ∈ `Confronto.val` (se declarado).<br>Lance.relatorio = gerar_relatorio(IntervaloTempo.val, Confronto.val, Bloco.lista) | `p[0] = gerar_relatorio_final(p[2], p[3], p[4])` |
| **2** | \<Confronto\> → **JOGADOR₁** **VS** **JOGADOR₂** | Verifica JOGADOR₁ ≠ JOGADOR₂.<br>Confronto.val = (JOGADOR₁.lexval, JOGADOR₂.lexval) | `p[0] = (p[1], p[3])` |
| **3** | \<Confronto\> → ε | Confronto.val = nulo (equipes inferidas das posses) | `p[0] = None` |
| **4** | \<IntervaloTempo\> → '[' **TEMPO₁** '-' **TEMPO₂** ']' | Verifica seg(TEMPO₂) ≥ seg(TEMPO₁).<br>IntervaloTempo.val = {ini, fim, duracao = seg(TEMPO₂) − seg(TEMPO₁)} | `p[0] = {"inicio": p[2], "fim": p[4], "duracao_seg": ...}` |
| **5** | \<Bloco\> → '{' \<SequenciaAcoes\> '}' | Bloco.lista = SequenciaAcoes.lista | `p[0] = p[2]` |
| **6** | \<Bloco\> → **FASE** **JOGADOR** '{' \<SequenciaAcoes\> '}' | Bloco.lista = rotular(SequenciaAcoes.lista, "fase", JOGADOR.lexval) *(rótulo hierárquico "Externa > Interna")* | `p[0] = anotar_rotulo(p[4], "fase", p[2])` |
| **7** | \<Bloco\> → **POSSE** **JOGADOR** '{' \<SequenciaAcoes\> '}' | Para cada ação sem equipe: acao.equipe = JOGADOR.lexval *(as coordenadas do bloco estão no referencial desta equipe)* | laço que preenche `copia["equipe"] = p[2]` |
| **8** | \<SequenciaAcoes\> → \<SequenciaAcoes\>₁ \<ElementoTatico\> | SequenciaAcoes.lista = SequenciaAcoes₁.lista + ElementoTatico.lista | `p[0] = p[1] + p[2]` |
| **9** | \<SequenciaAcoes\> → \<ElementoTatico\> | SequenciaAcoes.lista = ElementoTatico.lista | `p[0] = p[1]` |
| **10** | \<ElementoTatico\> → \<AcaoAtomica\> | ElementoTatico.lista = AcaoAtomica.lista | `p[0] = p[1]` |
| **11** | \<ElementoTatico\> → \<Bloco\> | ElementoTatico.lista = Bloco.lista *(auto-incorporação)* | `p[0] = p[1]` |
| **12** | \<ElementoTatico\> → \<Jogada\> | ElementoTatico.lista = Jogada.lista | `p[0] = p[1]` |
| **13** | \<Jogada\> → **TABELA** **JOGADOR₁** **JOGADOR₂** '{' \<SequenciaAcoes\> '}' | Verifica: 1º passe = JOGADOR₁→JOGADOR₂ e 2º passe = JOGADOR₂→JOGADOR₁; senão **erro semântico**.<br>Jogada.lista = rotular(SequenciaAcoes.lista, "jogada", "Tabela A/B") | `validar_tabela(p[2], p[3], p[5])`<br>`p[0] = anotar_rotulo(p[5], "jogada", ...)` |
| **14** | \<Jogada\> → **TRIANGULACAO** '{' \<SequenciaAcoes\> '}' | envolvidos = {autores} ∪ {receptores} dos passes.<br>Verifica: nº passes ≥ 3 e \|envolvidos\| = 3; senão **erro semântico**.<br>Jogada.lista = rotular(..., "Triangulação") | `validar_triangulacao(p[3])` |
| **15** | \<Jogada\> → **CONTRA_ATAQUE** '{' \<SequenciaAcoes\> '}' | avanco = x_dest(último passe) − x_orig(primeiro passe).<br>Verifica: avanco ≥ 40 m e nº passes ≤ 6; senão **erro semântico**.<br>Jogada.lista = rotular(..., "Contra-ataque (+avanco m)") | `avanco = validar_contra_ataque(p[3])` |
| **16** | \<AcaoAtomica\> → \<Passe\> ';' | AcaoAtomica.lista = Passe.lista | `p[0] = p[1]` |
| **17** | \<AcaoAtomica\> → \<Finalizacao\> ';' | AcaoAtomica.lista = Finalizacao.lista | `p[0] = p[1]` |
| **18** | \<AcaoAtomica\> → \<TrocaPosse\> ';' | AcaoAtomica.lista = [ TrocaPosse.info ] | `p[0] = [p[1]]` |
| **19** | \<TrocaPosse\> → **TROCA_POSSE** **JOGADOR** | TrocaPosse.info = {tipo: TROCA_POSSE, nova_equipe: JOGADOR.lexval} *(muda o referencial das coordenadas seguintes)* | `p[0] = {"tipo_acao": "TROCA_POSSE", ...}` |
| **20** | \<Passe\> → **PASSE** **JOGADOR** \<Coordenada\> \<CadeiaPasse\> | Passe.lista = CadeiaPasse.passes | `p[0] = p[4]["passes"]` |
| **21** | \<CadeiaPasse\> → **SETA** **JOGADOR** \<Coordenada\> | **Atributos herdados:** CadeiaPasse.autor_h = JOGADOR(irmão em #20), CadeiaPasse.orig_h = Coordenada(irmã em #20).<br>P = montar_passe(autor_h, orig_h, JOGADOR.lexval, Coordenada.val)<br>CadeiaPasse.passes = [P]; .ultimo = JOGADOR.lexval; .ultima_coord = Coordenada.val | `autor, c_orig = p[-2], p[-1]` *(lidos na pilha, como `topo-2` no LR)* |
| **22** | \<CadeiaPasse\> → \<CadeiaPasse\>₁ **SETA** **JOGADOR** \<Coordenada\> | P = montar_passe(CadeiaPasse₁.ultimo, CadeiaPasse₁.ultima_coord, JOGADOR.lexval, Coordenada.val)<br>CadeiaPasse.passes = CadeiaPasse₁.passes + [P] | `p[0] = {"passes": p[1]["passes"] + [passe], ...}` |
| — | *montar_passe(A, C₁, B, C₂)* | ΔX = C₂.x − C₁.x; ΔY = C₂.y − C₁.y; d = √(ΔX² + ΔY²)<br>z_o = zona(C₁); z_d = zona(C₂)<br>(tipo, dir) = classificar_passe(d, C₁, C₂, z_o, z_d) | `_montar_passe(...)` |
| **23** | \<Finalizacao\> → **FINALIZACAO** **JOGADOR** \<Coordenada\> **RESULTADO** \<Desfecho\> | Finalizacao.lista = [ {autor, zona(Coordenada), Desfecho.val, tentativa = 1} ] | `p[0] = [_montar_chute(p[2], p[3], p[5])]` |
| **24** | \<Finalizacao\> → **FINALIZACAO** **JOGADOR** \<Coordenada\> **RESULTADO** \<DesfechoParcial\> **REBOTE** \<Finalizacao\>₁ | Finalizacao.lista = [ chute(tentativa = 1) ] + [ c com tentativa + 1 para c ∈ Finalizacao₁.lista ] *(recursão à direita)* | `p[0] = [_montar_chute(...)] + seguintes` |
| **25** | \<DesfechoParcial\> → **DEFESA** | DesfechoParcial.val = "DEFESA DO GOLEIRO!" | `p[0] = "DEFESA DO GOLEIRO!"` |
| **26** | \<DesfechoParcial\> → **TRAVE** | DesfechoParcial.val = "NA TRAVE!" | `p[0] = "NA TRAVE!"` |
| **27** | \<Coordenada\> → '(' **NUM₁** ',' **NUM₂** ')' | Verifica 0 ≤ NUM₁ ≤ 120 e 0 ≤ NUM₂ ≤ 80; senão **erro semântico**.<br>Coordenada.val = (NUM₁.lexval, NUM₂.lexval) | `p[0] = (p[2], p[4])` |
| **28** | \<Desfecho\> → **GOL** | Desfecho.val = "GOL!" | `p[0] = "GOL!"` |
| **29** | \<Desfecho\> → **DEFESA** | Desfecho.val = "DEFESA DO GOLEIRO!" | `p[0] = "DEFESA DO GOLEIRO!"` |
| **30** | \<Desfecho\> → **FORA** | Desfecho.val = "PARA FORA!" | `p[0] = "PARA FORA!"` |
| **31** | \<Desfecho\> → **TRAVE** | Desfecho.val = "NA TRAVE!" | `p[0] = "NA TRAVE!"` |
