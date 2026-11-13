# -*- coding: utf-8 -*-
"""
Módulo de Análise Léxica (ply.lex) do Compilador Tático de Futebol.
Reconhece tokens de timestamps, coordenadas cartesianas, nomes entre aspas em UTF-8,
palavras-chave da DSL e delimitadores, mantendo rastreamento de linha e coluna.

LEGENDA DAS MARCAÇÕES (exigência do passo 6 do enunciado):
  [NOVO]       -> criado para este trabalho (não existe no exemplo calc do PLY)
  [MODIFICADO] -> adaptado a partir da estrutura do exemplo calc do PLY
  [PLY]        -> estrutura padrão exigida pelo gerador (mantida do exemplo)
"""

import ply.lex as lex

# [NOVO] Palavras reservadas da Linguagem Tática (DSL).
# No exemplo calc não há palavras reservadas; aqui o token ID é reclassificado
# por esta tabela (técnica padrão do PLY para keywords).
reserved = {
    'LANCE': 'LANCE',
    'VS': 'VS',                        # [NOVO] cabeçalho do confronto "A" VS "B"
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
    'REBOTE': 'REBOTE',                # [NOVO] finalização recursiva (rebote)
    'TABELA': 'TABELA',                # [NOVO] elemento tático recursivo
    'TRIANGULACAO': 'TRIANGULACAO',    # [NOVO] elemento tático recursivo
    'CONTRA_ATAQUE': 'CONTRA_ATAQUE',  # [NOVO] elemento tático recursivo
}

# [MODIFICADO] Lista de tokens (no calc: NUMBER, PLUS, MINUS...). Aqui: tokens do futebol.
# Observação: o token JOGADOR representa QUALQUER nome entre aspas (jogador, equipe ou
# nome de fase). Léxicamente são indistinguíveis; o papel é dado pela produção sintática.
tokens = [
    'TEMPO',
    'JOGADOR',
    'NUM',
    'SETA',
] + list(reserved.values())

# [MODIFICADO] Símbolos literais de um caractere usados diretamente na gramática
literals = ['[', ']', '-', '{', '}', '(', ')', ',', ';']

# [NOVO] Operador de transição de passe (->). PLY ordena regras-string pelo tamanho
# da regex, então '->' é testado antes do literal '-'.
t_SETA = r'->'

# [PLY] Ignora espaços, tabulações e retorno de carro
t_ignore = ' \t\r'


def t_TEMPO(t):
    r'\d{1,3}:\d{2}'
    # [NOVO] Definido ANTES de t_NUM para que "14:20" não seja lido como NUM ':' NUM
    return t


def t_NUM(t):
    r'\d+(\.\d+)?'
    # [MODIFICADO] Do calc (inteiros) para reais: coordenadas como 25.4
    t.value = float(t.value)
    return t


def t_JOGADOR(t):
    r'"[^"\n]+"'
    # [NOVO] Remove as aspas mantendo suporte total a caracteres acentuados UTF-8
    t.value = t.value[1:-1]
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    # [NOVO] Identificadores só são válidos se forem palavras reservadas
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
    pass  # [NOVO] Ignora comentários iniciados por '#'


def t_newline(t):
    r'\n+'
    # [PLY] Atualiza o número da linha
    t.lexer.lineno += len(t.value)


def encontrar_coluna(texto_entrada: str, token) -> int:
    """[NOVO] Calcula a coluna exata (1-based) de um token na linha atual."""
    inicio_linha = texto_entrada.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - inicio_linha) + 1


def t_error(t):
    # [MODIFICADO] No calc apenas imprime e pula; aqui aborta com linha e coluna
    col = encontrar_coluna(t.lexer.lexdata, t)
    raise SyntaxError(
        f"Erro Léxico: Caractere ilegal '{t.value[0]}' "
        f"(linha {t.lexer.lineno}, coluna {col})."
    )


def criar_lexer(**kwargs):
    """Instancia e retorna um novo analisador léxico do PLY."""
    return lex.lex(**kwargs)
