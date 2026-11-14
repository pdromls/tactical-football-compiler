# Produções Gramaticais e Regras Semânticas (Tabela SDT para a apresentação)

**Disciplina:** Compiladores (2026_2)  
**Projeto:** Tradutor Tático de Lances de Futebol (Padrão Cartesiano StatsBomb 120x80)  
**Gerador:** PLY (`ply.lex` + `ply.yacc`, LALR(1), 0 conflitos)

* **Não-terminais (V):** \<Lance\>, \<Confronto\>, \<IntervaloTempo\>, \<Bloco\>, \<SequenciaAcoes\>, \<ElementoTatico\>, \<Jogada\>, \<AcaoAtomica\>, \<TrocaPosse\>, \<Passe\>, \<CadeiaPasse\>, \<Finalizacao\>, \<DesfechoParcial\>, \<Coordenada\>, \<Desfecho\>
* **Terminais (Σ):** LANCE, VS, FASE, POSSE, TROCA_POSSE, PASSE, FINALIZACAO, RESULTADO, REBOTE, GOL, DEFESA, FORA, TRAVE, TABELA, TRIANGULACAO, CONTRA_ATAQUE, TEMPO, JOGADOR, NUM, SETA ("->"), "[", "]", "-", "{", "}", "(", ")", ",", ";"
* **Tipo de SDT:** S-atribuída, com um atributo herdado em #21 (portanto **L-atribuída**).

## O que há de recursivo (correção pedida pela professora)

| Recursão | Produções | Tipo | Regra semântica própria |
| :--- | :--- | :--- | :--- |
| Elementos táticos recursivos | #13 TABELA, #14 TRIANGULACAO, #15 CONTRA_ATAQUE (+ #5–#7 blocos) | auto-incorporação (podem conter uns aos outros) | cada uma **valida** o próprio conteúdo |
| Passe encadeado `A -> B -> C` | #20–#22 | ação atômica recursiva à **esquerda** | o portador da bola passa de um elo ao outro (atributo herdado em #21) |
| Finalização com rebote | #24 | ação atômica recursiva à **direita** | numera as tentativas; o desfecho final é o do chute mais interno |

## Tabela

| # | Produção (BNF) | Regra semântica (notação SDT) | Implementação no ply.yacc (`src/parser.py`) |
| :-: | :--- | :--- | :--- |
| **1** | \<Lance\> → **LANCE** \<IntervaloTempo\> \<Confronto\> \<Bloco\> | Verifica: toda equipe de `Bloco.lista` ∈ `Confronto.val` (se declarado).<br>Lance.relatorio = gerar_relatorio(IntervaloTempo.val, Confronto.val, Bloco.lista) | `p[0] = gerar_relatorio_final(p[2], p[3], p[4])` |
| **2** | \<Confronto\> → **JOGADOR₁** **VS** **JOGADOR₂** | Verifica JOGADOR₁ ≠ JOGADOR₂.<br>Confronto.val = (JOGADOR₁.lexval, JOGADOR₂.lexval) | `p[0] = (p[1], p[3])` |
| **3** | \<Confronto\> → ε | Confronto.val = nulo (equipes inferidas das posses) | `p[0] = None` |
| **4** | \<IntervaloTempo\> → '[' **TEMPO₁** '-' **TEMPO₂** ']' | Verifica segundos de cada TEMPO em 00..59 e seg(TEMPO₂) ≥ seg(TEMPO₁).<br>IntervaloTempo.val = {ini, fim, duracao = seg(TEMPO₂) − seg(TEMPO₁)} | `p[0] = {"inicio": p[2], "fim": p[4], "duracao_seg": ...}` |
| **5** | \<Bloco\> → '{' \<SequenciaAcoes\> '}' | Bloco.lista = SequenciaAcoes.lista | `p[0] = p[2]` |
| **6** | \<Bloco\> → **FASE** **JOGADOR** '{' \<SequenciaAcoes\> '}' | Bloco.lista = rotular(SequenciaAcoes.lista, "fase", JOGADOR.lexval) *(rótulo hierárquico "Externa > Interna")* | `p[0] = anotar_rotulo(p[4], "fase", p[2])` |
| **7** | \<Bloco\> → **POSSE** **JOGADOR** '{' \<SequenciaAcoes\> '}' | Para cada ação sem equipe: acao.equipe = JOGADOR.lexval *(as coordenadas do bloco estão no referencial desta equipe)* | laço que preenche `copia["equipe"] = p[2]` |
| **8** | \<SequenciaAcoes\> → \<SequenciaAcoes\>₁ \<ElementoTatico\> | SequenciaAcoes.lista = SequenciaAcoes₁.lista + ElementoTatico.lista | `p[0] = p[1] + p[2]` |
| **9** | \<SequenciaAcoes\> → \<ElementoTatico\> | SequenciaAcoes.lista = ElementoTatico.lista | `p[0] = p[1]` |
| **10** | \<ElementoTatico\> → \<AcaoAtomica\> | ElementoTatico.lista = AcaoAtomica.lista | `p[0] = p[1]` |
| **11** | \<ElementoTatico\> → \<Bloco\> | ElementoTatico.lista = Bloco.lista *(auto-incorporação)* | `p[0] = p[1]` |
| **12** | \<ElementoTatico\> → \<Jogada\> | ElementoTatico.lista = Jogada.lista | `p[0] = p[1]` |
| **13** | \<Jogada\> → **TABELA** **JOGADOR₁** **JOGADOR₂** '{' \<SequenciaAcoes\> '}' | Verifica: JOGADOR₁ ≠ JOGADOR₂; uma única equipe e sem TROCA_POSSE dentro; 1º passe = JOGADOR₁→JOGADOR₂ e 2º passe = JOGADOR₂→JOGADOR₁; senão **erro semântico**.<br>Jogada.lista = rotular(SequenciaAcoes.lista, "jogada", "Tabela A/B") | `validar_tabela(p[2], p[3], p[5])`<br>`p[0] = anotar_rotulo(p[5], "jogada", ...)` |
| **14** | \<Jogada\> → **TRIANGULACAO** '{' \<SequenciaAcoes\> '}' | envolvidos = {autores} ∪ {receptores} dos passes.<br>Verifica: uma única equipe e sem TROCA_POSSE dentro; nº passes ≥ 3 e \|envolvidos\| = 3; senão **erro semântico**.<br>Jogada.lista = rotular(..., "Triangulação") | `validar_triangulacao(p[3])` |
| **15** | \<Jogada\> → **CONTRA_ATAQUE** '{' \<SequenciaAcoes\> '}' | avanco = x_dest(último passe) − x_orig(primeiro passe).<br>Verifica: uma única equipe e sem TROCA_POSSE dentro (senão o avanço somaria referenciais diferentes); avanco ≥ 40 m e nº passes ≤ 6; senão **erro semântico**.<br>Jogada.lista = rotular(..., "Contra-ataque (+avanco m)") | `avanco = validar_contra_ataque(p[3])` |
| **16** | \<AcaoAtomica\> → \<Passe\> ';' | AcaoAtomica.lista = Passe.lista | `p[0] = p[1]` |
| **17** | \<AcaoAtomica\> → \<Finalizacao\> ';' | AcaoAtomica.lista = Finalizacao.lista | `p[0] = p[1]` |
| **18** | \<AcaoAtomica\> → \<TrocaPosse\> ';' | AcaoAtomica.lista = [ TrocaPosse.info ] | `p[0] = [p[1]]` |
| **19** | \<TrocaPosse\> → **TROCA_POSSE** **JOGADOR** | TrocaPosse.info = {tipo: TROCA_POSSE, nova_equipe: JOGADOR.lexval} *(muda o referencial das coordenadas seguintes; na raiz, verifica que a próxima ação de bola é dessa equipe)* | `p[0] = {"tipo_acao": "TROCA_POSSE", ...}` |
| **20** | \<Passe\> → **PASSE** **JOGADOR** \<Coordenada\> \<CadeiaPasse\> | Passe.lista = CadeiaPasse.passes | `p[0] = p[4]["passes"]` |
| **21** | \<CadeiaPasse\> → **SETA** **JOGADOR** \<Coordenada\> | **Atributos herdados:** CadeiaPasse.autor_h = JOGADOR(irmão em #20), CadeiaPasse.orig_h = Coordenada(irmã em #20).<br>P = montar_passe(autor_h, orig_h, JOGADOR.lexval, Coordenada.val)<br>CadeiaPasse.passes = [P]; .ultimo = JOGADOR.lexval; .ultima_coord = Coordenada.val | `autor, c_orig = p[-2], p[-1]` *(lidos na pilha, como `$0` no Bison)* |
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


> Detalhes das funções `identificar_zona`, `classificar_passe` e da perspectiva por equipe (`espelhar`): ver `02_TABELA_SDT.md`.
