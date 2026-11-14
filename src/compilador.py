# -*- coding: utf-8 -*-
"""
Fachada Modular do Compilador Tático de Futebol.
[NOVO] Arquivo inteiro criado para este trabalho (não existe no exemplo calc do PLY).
Permite compilar lances tanto a partir de arquivos em disco (.txt / .match)
quanto a partir de strings em memória (integração com API StatsBomb).
"""

from pathlib import Path
from .lexer import criar_lexer
from .parser import criar_parser


class CompiladorTatico:
    """
    Compilador e Tradutor Dirigido pela Sintaxe (SDT) para a DSL Tática de Futebol.
    """

    def __init__(self):
        # [PLY] lex.lex() e yacc.yacc() constroem o analisador léxico e o LALR(1)
        self.lexer = criar_lexer()
        self.parser = criar_parser()

    def tokenizar(self, codigo_fonte: str) -> list:
        """
        Executa apenas a análise léxica e retorna a lista de tokens reconhecidos.
        Útil para inspeção acadêmica e depuração do ply.lex.
        """
        self.lexer.lineno = 1
        self.lexer.input(codigo_fonte)
        lista_tokens = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            lista_tokens.append(tok)
        return lista_tokens

    def compilar_texto(self, codigo_fonte: str) -> dict:
        """
        Modo B (Stream em Memória): Recebe uma string formatada na DSL tática
        e retorna o dicionário contendo o relatório traduzido e os atributos sintetizados.
        """
        self.lexer.lineno = 1
        return self.parser.parse(codigo_fonte, lexer=self.lexer)

    def compilar_arquivo(self, caminho_arquivo: str | Path) -> dict:
        """
        Modo A (Arquivo em Disco): Lê um arquivo .txt ou .match em UTF-8
        e executa a compilação completa.
        """
        caminho = Path(caminho_arquivo)
        if not caminho.exists():
            raise FileNotFoundError(f"Arquivo de lance não encontrado: {caminho}")
        conteudo = caminho.read_text(encoding="utf-8")
        return self.compilar_texto(conteudo)
