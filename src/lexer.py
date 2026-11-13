# -*- coding: utf-8 -*-
"""
Módulo de Análise Léxica (ply.lex) do Compilador Tático de Futebol.
Reconhece tokens de timestamps, coordenadas cartesianas, jogadores em UTF-8,
palavras-chave da DSL e delimitadores, mantendo rastreamento de linha e coluna.
"""

import ply.lex as lex

# Palavras reservadas da Linguagem Tática (DSL)
reserved = {
    'LANCE': 'LANCE',
    'FASE': 'FASE',
    'POSSE': 'POSSE',
    'TROCA_POSSE': 'TROCA_POSSE',
    'PASSE': 'PASSE',
    'FINALIZACAO': 'FINALIZACAO',
    'RESULTADO': 'RESULTADO',
    'GOL': 'GOL',
    'DEFESA': 'DEFESA',
    'FORA': 'FORA',
    'TRAVE': 'TRAVE',
}

# Lista completa de tokens exportada para o ply.yacc
tokens = [
    'TEMPO',
    'JOGADOR',
    'NUM',
    'SETA',
] + list(reserved.values())

# Símbolos literais de um único caractere usados diretamente na gramática BNF
literals = ['[', ']', '-', '{', '}', '(', ')', ',', ';']

# Expressão regular para o operador de transição de passe (->)
t_SETA = r'->'

# Ignora espaços, tabulações e retorno de carro
t_ignore = ' \t\r'


def t_TEMPO(t):
    r'\d{1,3}:\d{2}'
    return t


def t_NUM(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value)
    return t


def t_JOGADOR(t):
    r'"[^"\n]+"'
    # Remove as aspas mantendo suporte total a caracteres acentuados UTF-8
    t.value = t.value[1:-1]
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    if t.type == 'ID':
        col = encontrar_coluna(t.lexer.lexdata, t)
        raise SyntaxError(
            f"Erro Léxico: Palavra-chave ou identificador desconhecido '{t.value}' "
            f"(linha {t.lineno}, coluna {col})."
        )
    return t


def t_COMMENT(t):
    r'\#.*'
    pass  # Ignora comentários iniciados por '#'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def encontrar_coluna(texto_entrada: str, token) -> int:
    """Calcula a coluna exata (1-based) de um token na linha atual."""
    inicio_linha = texto_entrada.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - inicio_linha) + 1


def t_error(t):
    col = encontrar_coluna(t.lexer.lexdata, t)
    caractere_ilegal = t.value[0]
    raise SyntaxError(
        f"Erro Léxico: Caractere ilegal '{caractere_ilegal}' "
        f"(linha {t.lexer.lineno}, coluna {col})."
    )


def criar_lexer(**kwargs):
    """Instancia e retorna um novo analisador léxico do PLY."""
    return lex.lex(**kwargs)
