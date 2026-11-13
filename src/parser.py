# -*- coding: utf-8 -*-
"""
Módulo de Análise Sintática e Tradução Dirigida pela Sintaxe (ply.yacc).
Implementa a Gramática Livre de Contexto (BNF) com:
  1. Recursão à esquerda em <SequenciaAcoes> (eficiência de pilha O(1) no LALR);
  2. Auto-incorporação (Self-Embedding) em <Bloco> -> '{' <SequenciaAcoes> '}'
     para comprovação formal de Linguagem Livre de Contexto (Chomsky Tipo 2);
  3. Ações semânticas S-atribuídas via array 'p' do PLY.
"""

import ply.yacc as yacc
from .lexer import tokens, encontrar_coluna  # noqa: F401
from .semantico import (
    identificar_zona,
    calcular_distancia,
    classificar_passe,
    tempo_para_segundos,
    gerar_relatorio_final,
)


# ==============================================================================
# PRODUÇÕES GRAMATICAIS BNF E REGRAS SEMÂNTICAS (SDT)
# ==============================================================================

def p_lance(p):
    """Lance : LANCE IntervaloTempo Bloco"""
    p[0] = gerar_relatorio_final(p[2], p[3])


def p_intervalo_tempo(p):
    """IntervaloTempo : '[' TEMPO '-' TEMPO ']'"""
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
    p[0] = p[2]


def p_bloco_fase_nomeada(p):
    """Bloco : FASE JOGADOR '{' SequenciaAcoes '}'"""
    nome_fase = p[2]
    acoes_bloco = []
    for acao in p[4]:
        copia = dict(acao)
        if copia.get("fase"):
            copia["fase"] = f"{nome_fase} > {copia['fase']}"
        else:
            copia["fase"] = nome_fase
        acoes_bloco.append(copia)
    p[0] = acoes_bloco


def p_bloco_posse_equipe(p):
    """Bloco : POSSE JOGADOR '{' SequenciaAcoes '}'"""
    nome_equipe = p[2]
    acoes_bloco = []
    for acao in p[4]:
        copia = dict(acao)
        if not copia.get("equipe"):
            copia["equipe"] = nome_equipe
        acoes_bloco.append(copia)
    p[0] = acoes_bloco


def p_sequencia_acoes_recursiva(p):
    """SequenciaAcoes : SequenciaAcoes ElementoTatico"""
    # Recursão à esquerda: reduz imediatamente sem crescer a pilha LALR
    p[0] = p[1] + p[2]


def p_sequencia_acoes_base(p):
    """SequenciaAcoes : ElementoTatico"""
    p[0] = p[1]


def p_elemento_tatico_atomico(p):
    """ElementoTatico : AcaoAtomica"""
    p[0] = [p[1]]


def p_elemento_tatico_bloco(p):
    """ElementoTatico : Bloco"""
    # Propriedade de Auto-Incorporação (Self-Embedding): Bloco =>+ '{' Bloco '}'
    p[0] = p[1]


def p_acao_atomica_passe(p):
    """AcaoAtomica : Passe ';'"""
    p[0] = p[1]


def p_acao_atomica_finalizacao(p):
    """AcaoAtomica : Finalizacao ';'"""
    p[0] = p[1]


def p_acao_atomica_troca_posse(p):
    """AcaoAtomica : TrocaPosse ';'"""
    p[0] = p[1]


def p_troca_posse(p):
    """TrocaPosse : TROCA_POSSE JOGADOR"""
    p[0] = {
        "tipo_acao": "TROCA_POSSE",
        "nova_equipe": p[2],
    }


def p_passe(p):
    """Passe : PASSE JOGADOR Coordenada SETA JOGADOR Coordenada"""
    c_orig = p[3]
    c_dest = p[6]
    dist = calcular_distancia(c_orig, c_dest)
    z_orig = identificar_zona(c_orig[0], c_orig[1])
    z_dest = identificar_zona(c_dest[0], c_dest[1])
    classificacao, direcao = classificar_passe(dist, c_orig, c_dest, z_orig, z_dest)

    p[0] = {
        "tipo_acao": "PASSE",
        "autor": p[2],
        "receptor": p[5],
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


def p_finalizacao(p):
    """Finalizacao : FINALIZACAO JOGADOR Coordenada RESULTADO Desfecho"""
    c_orig = p[3]
    z_orig = identificar_zona(c_orig[0], c_orig[1])
    p[0] = {
        "tipo_acao": "FINALIZACAO",
        "autor": p[2],
        "coord_orig": c_orig,
        "zona_orig": z_orig,
        "zona_dest": z_orig,
        "desfecho": p[5],
    }


def p_coordenada(p):
    """Coordenada : '(' NUM ',' NUM ')'"""
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
    if p:
        col = encontrar_coluna(p.lexer.lexdata, p)
        raise SyntaxError(
            f"Erro Sintático: Token inesperado '{p.value}' (tipo {p.type}) "
            f"na linha {p.lineno}, coluna {col}."
        )
    else:
        raise SyntaxError(
            "Erro Sintático: Fim inesperado da entrada (EOF). Verifique chaves '}' ou ';' ausentes."
        )


def criar_parser(**kwargs):
    """Instancia e retorna o analisador sintático LALR(1) do PLY."""
    return yacc.yacc(write_tables=False, debug=False, **kwargs)
