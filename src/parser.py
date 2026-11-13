# -*- coding: utf-8 -*-
"""
Módulo de Análise Sintática e Tradução Dirigida pela Sintaxe (ply.yacc).
Implementa a Gramática Livre de Contexto (BNF) com:
  1. Recursão à esquerda em <SequenciaAcoes> e <CadeiaPasse> (pilha LALR constante
     para sequências longas);
  2. Auto-incorporação (Self-Embedding) em <Bloco> e <Jogada>:
     <Bloco> =>+ '{' <Bloco> '}'  e  <Jogada> =>+ TABELA A B '{' <Jogada> '}';
  3. Elementos táticos recursivos com regra semântica própria
     (TABELA, TRIANGULACAO, CONTRA_ATAQUE);
  4. Ações atômicas recursivas: passe encadeado (recursão à esquerda, com atributo
     herdado) e finalização com rebote (recursão à direita);
  5. Ações semânticas no vetor 'p' do PLY.

LEGENDA: [NOVO] criado para o trabalho | [MODIFICADO] adaptado do exemplo calc do PLY
         [PLY] estrutura padrão do gerador.
No exemplo calc as produções são expression : expression PLUS term ...; todas as
produções abaixo foram criadas para a linguagem tática.
"""

import ply.yacc as yacc
from .lexer import tokens, encontrar_coluna  # noqa: F401
from .semantico import (
    identificar_zona,
    calcular_distancia,
    classificar_passe,
    tempo_para_segundos,
    gerar_relatorio_final,
    anotar_rotulo,
    validar_tabela,
    validar_triangulacao,
    validar_contra_ataque,
)


# ==============================================================================
# PRODUÇÕES GRAMATICAIS BNF E REGRAS SEMÂNTICAS (SDT)
# ==============================================================================

def p_lance(p):
    """Lance : LANCE IntervaloTempo Confronto Bloco"""
    # [MODIFICADO] Raiz: sintetiza o relatório. Verificação semântica: toda equipe
    # citada em POSSE / TROCA_POSSE precisa pertencer ao confronto declarado.
    confronto = p[3]
    if confronto:
        for acao in p[4]:
            equipe = acao.get("equipe") or acao.get("nova_equipe")
            if equipe and equipe not in confronto:
                raise ValueError(
                    f"Erro Semântico: a equipe '{equipe}' não pertence ao confronto "
                    f"{confronto[0]} x {confronto[1]}."
                )
    p[0] = gerar_relatorio_final(p[2], confronto, p[4])


def p_confronto(p):
    """Confronto : JOGADOR VS JOGADOR"""
    # [NOVO] Declara os dois times. Necessário porque o campo de ataque de um
    # time é o campo de defesa do outro (perspectiva por equipe).
    if p[1] == p[3]:
        raise ValueError(f"Erro Semântico: confronto de '{p[1]}' contra ele mesmo.")
    p[0] = (p[1], p[3])


def p_confronto_vazio(p):
    """Confronto : """
    # [NOVO] Cabeçalho opcional (produção vazia): equipes inferidas das posses
    p[0] = None


def p_intervalo_tempo(p):
    """IntervaloTempo : '[' TEMPO '-' TEMPO ']'"""
    # [NOVO] Converte MM:SS em segundos e valida a ordem temporal
    seg_ini = tempo_para_segundos(p[2])
    seg_fim = tempo_para_segundos(p[4])
    if seg_fim < seg_ini:
        raise ValueError(
            f"Erro Semântico: Tempo final ({p[4]}) anterior ao tempo inicial ({p[2]})."
        )
    p[0] = {
        "inicio": p[2],
        "fim": p[4],
        "inicio_seg": seg_ini,
        "fim_seg": seg_fim,
        "duracao_seg": seg_fim - seg_ini,
    }


def p_bloco_simples(p):
    """Bloco : '{' SequenciaAcoes '}'"""
    # [NOVO] Bloco anônimo (auto-incorporação)
    p[0] = p[2]


def p_bloco_fase_nomeada(p):
    """Bloco : FASE JOGADOR '{' SequenciaAcoes '}'"""
    # [NOVO] Rotula hierarquicamente: "Externa > Interna"
    p[0] = anotar_rotulo(p[4], "fase", p[2])


def p_bloco_posse_equipe(p):
    """Bloco : POSSE JOGADOR '{' SequenciaAcoes '}'"""
    # [NOVO] Define qual equipe executa as ações: as coordenadas do bloco estão no
    # referencial DESSA equipe (X = 120 é o gol adversário dela).
    nome_equipe = p[2]
    acoes_bloco = []
    for acao in p[4]:
        copia = dict(acao)
        if copia["tipo_acao"] != "TROCA_POSSE" and not copia.get("equipe"):
            copia["equipe"] = nome_equipe
        acoes_bloco.append(copia)
    p[0] = acoes_bloco


def p_sequencia_acoes_recursiva(p):
    """SequenciaAcoes : SequenciaAcoes ElementoTatico"""
    # [NOVO] Recursão à esquerda: reduz a cada elemento, sem crescer a pilha LALR
    p[0] = p[1] + p[2]


def p_sequencia_acoes_base(p):
    """SequenciaAcoes : ElementoTatico"""
    p[0] = p[1]


def p_elemento_tatico_atomico(p):
    """ElementoTatico : AcaoAtomica"""
    p[0] = p[1]


def p_elemento_tatico_bloco(p):
    """ElementoTatico : Bloco"""
    # [NOVO] Auto-incorporação: Bloco =>+ '{' Bloco '}'
    p[0] = p[1]


def p_elemento_tatico_jogada(p):
    """ElementoTatico : Jogada"""
    # [NOVO] Elementos táticos recursivos com semântica própria
    p[0] = p[1]


def p_jogada_tabela(p):
    """Jogada : TABELA JOGADOR JOGADOR '{' SequenciaAcoes '}'"""
    # [NOVO] Tabela (1-2): exige A -> B seguido de B -> A
    validar_tabela(p[2], p[3], p[5])
    p[0] = anotar_rotulo(p[5], "jogada", f"Tabela {p[2]}/{p[3]}")


def p_jogada_triangulacao(p):
    """Jogada : TRIANGULACAO '{' SequenciaAcoes '}'"""
    # [NOVO] Triangulação: >= 3 passes entre exatamente 3 jogadores
    validar_triangulacao(p[3])
    p[0] = anotar_rotulo(p[3], "jogada", "Triangulação")


def p_jogada_contra_ataque(p):
    """Jogada : CONTRA_ATAQUE '{' SequenciaAcoes '}'"""
    # [NOVO] Contra-ataque: avanço >= 40 m em até 6 passes (atributo agregado)
    avanco = validar_contra_ataque(p[3])
    p[0] = anotar_rotulo(p[3], "jogada", f"Contra-ataque (+{avanco:.0f}m)")


def p_acao_atomica_passe(p):
    """AcaoAtomica : Passe ';'"""
    p[0] = p[1]


def p_acao_atomica_finalizacao(p):
    """AcaoAtomica : Finalizacao ';'"""
    p[0] = p[1]


def p_acao_atomica_troca_posse(p):
    """AcaoAtomica : TrocaPosse ';'"""
    p[0] = [p[1]]


def p_troca_posse(p):
    """TrocaPosse : TROCA_POSSE JOGADOR"""
    # [NOVO] A partir daqui o referencial de coordenadas passa a ser o da nova equipe
    p[0] = {"tipo_acao": "TROCA_POSSE", "nova_equipe": p[2]}


def _montar_passe(autor, c_orig, receptor, c_dest):
    """[NOVO] Atributos sintetizados de um passe (distância, zonas, tipo, direção)."""
    dist = calcular_distancia(c_orig, c_dest)
    z_orig = identificar_zona(*c_orig)
    z_dest = identificar_zona(*c_dest)
    classificacao, direcao = classificar_passe(dist, c_orig, c_dest, z_orig, z_dest)
    return {
        "tipo_acao": "PASSE",
        "autor": autor,
        "receptor": receptor,
        "coord_orig": c_orig,
        "coord_dest": c_dest,
        "dx": round(c_dest[0] - c_orig[0], 2),
        "dy": round(c_dest[1] - c_orig[1], 2),
        "distancia": round(dist, 1),
        "zona_orig": z_orig,
        "zona_dest": z_dest,
        "classificacao": classificacao,
        "direcao": direcao,
    }


def p_passe(p):
    """Passe : PASSE JOGADOR Coordenada CadeiaPasse"""
    # [MODIFICADO] Ação atômica recursiva: PASSE A (c) -> B (c) -> C (c) ...
    p[0] = p[4]["passes"]


def p_cadeia_passe_base(p):
    """CadeiaPasse : SETA JOGADOR Coordenada"""
    # [NOVO] ATRIBUTO HERDADO: o autor e a origem do 1º passe não estão nesta
    # produção; vêm dos irmãos à esquerda na pilha do parser (p[-2] = JOGADOR,
    # p[-1] = Coordenada de "PASSE JOGADOR Coordenada"). Equivale ao $0 do Bison.
    autor, c_orig = p[-2], p[-1]
    p[0] = {
        "passes": [_montar_passe(autor, c_orig, p[2], p[3])],
        "ultimo": p[2],
        "ultima_coord": p[3],
    }


def p_cadeia_passe_recursiva(p):
    """CadeiaPasse : CadeiaPasse SETA JOGADOR Coordenada"""
    # [NOVO] Recursão à esquerda: o portador da bola é quem recebeu o elo anterior
    anterior = p[1]
    passe = _montar_passe(anterior["ultimo"], anterior["ultima_coord"], p[3], p[4])
    p[0] = {
        "passes": anterior["passes"] + [passe],
        "ultimo": p[3],
        "ultima_coord": p[4],
    }


def _montar_chute(autor, coord, desfecho):
    z_orig = identificar_zona(*coord)
    return {
        "tipo_acao": "FINALIZACAO",
        "autor": autor,
        "coord_orig": coord,
        "zona_orig": z_orig,
        "zona_dest": z_orig,
        "desfecho": desfecho,
        "tentativa": 1,
    }


def p_finalizacao(p):
    """Finalizacao : FINALIZACAO JOGADOR Coordenada RESULTADO Desfecho"""
    p[0] = [_montar_chute(p[2], p[3], p[5])]


def p_finalizacao_rebote(p):
    """Finalizacao : FINALIZACAO JOGADOR Coordenada RESULTADO DesfechoParcial REBOTE Finalizacao"""
    # [NOVO] Recursão à direita: o chute seguinte só existe por causa do anterior.
    # A numeração das tentativas é sintetizada de dentro para fora.
    seguintes = [dict(a, tentativa=a["tentativa"] + 1) for a in p[7]]
    p[0] = [_montar_chute(p[2], p[3], p[5])] + seguintes


def p_desfecho_parcial(p):
    """DesfechoParcial : DEFESA
                       | TRAVE"""
    # [NOVO] Desfechos que permitem rebote. Com lookahead REBOTE reduz aqui;
    # com ';' reduz para <Desfecho> (LALR(1) resolve sem conflito).
    p[0] = {"DEFESA": "DEFESA DO GOLEIRO!", "TRAVE": "NA TRAVE!"}[p[1]]


def p_coordenada(p):
    """Coordenada : '(' NUM ',' NUM ')'"""
    # [NOVO] Verificação semântica dos limites do campo StatsBomb
    x, y = p[2], p[4]
    if not (0.0 <= x <= 120.0 and 0.0 <= y <= 80.0):
        raise ValueError(
            f"Erro Semântico: Coordenada ({x}, {y}) fora dos limites oficiais "
            f"do campo StatsBomb (X: 0..120, Y: 0..80)."
        )
    p[0] = (x, y)


def p_desfecho(p):
    """Desfecho : GOL
                | DEFESA
                | FORA
                | TRAVE"""
    mapa = {
        "GOL": "GOL!",
        "DEFESA": "DEFESA DO GOLEIRO!",
        "FORA": "PARA FORA!",
        "TRAVE": "NA TRAVE!",
    }
    p[0] = mapa[p[1]]


def p_error(p):
    # [MODIFICADO] No calc apenas imprime "Syntax error"; aqui aborta com linha/coluna
    if p:
        col = encontrar_coluna(p.lexer.lexdata, p)
        raise SyntaxError(
            f"Erro Sintático: Token inesperado '{p.value}' (tipo {p.type}) "
            f"na linha {p.lineno}, coluna {col}."
        )
    raise SyntaxError(
        "Erro Sintático: Fim inesperado da entrada (EOF). Verifique chaves '}' ou ';' ausentes."
    )


def criar_parser(**kwargs):
    """[PLY] Instancia e retorna o analisador sintático LALR(1)."""
    return yacc.yacc(write_tables=False, debug=False, **kwargs)
