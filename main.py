# -*- coding: utf-8 -*-
"""
Ponto de entrada principal (CLI) do Compilador/Tradutor Tático de Futebol.
Suporta 3 modos de operação:
  1. Demonstração em memória (sem argumentos);
  2. Leitura de arquivo em disco (.txt / .match);
  3. Extração ao vivo de uma partida do StatsBomb (--match-id, --inicio, --fim)
     seguida da compilação automática pelo PLY!

Exemplos de uso:
  python main.py
  python main.py exemplos/lance_croacia.txt
  python main.py exemplos/lance_aninhado_fase.txt --tokens
  python main.py exemplos/lance_recursivo.txt        (jogadas e ações recursivas)
  python main.py exemplos/lance_troca_posse.txt      (perspectiva de campo por equipe)
  python main.py --match-id 3869253 --inicio 116:30 --fim 116:50 --mostrar-dsl
"""

import argparse
import sys
from src.compilador import CompiladorTatico
from src.campo_statsbomb import extrair_lance_para_dsl


EXEMPLO_MEMORIA = """LANCE [14:20 - 14:35] {
    PASSE "Luka Modrić" (25.4, 40.2) -> "Mateo Kovačić" (38.2, 42.1);
    PASSE "Mateo Kovačić" (38.2, 42.1) -> "Andrej Kramarić" (85.0, 18.5);
    FINALIZACAO "Andrej Kramarić" (108.5, 39.8) RESULTADO GOL;
}"""


def _parse_mm_ss(tempo_str: str) -> tuple[int, int]:
    partes = tempo_str.strip().split(":")
    if len(partes) != 2:
        raise ValueError(f"Formato de tempo inválido '{tempo_str}'. Use MM:SS (ex: 14:20).")
    return int(partes[0]), int(partes[1])


def main():
    # Garante saída UTF-8 no terminal Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser_cli = argparse.ArgumentParser(
        description="Compilador / Tradutor Dirigido pela Sintaxe (SDT) - Futebol StatsBomb 120x80"
    )
    parser_cli.add_argument(
        "arquivo",
        nargs="?",
        help="Caminho opcional para um arquivo de entrada (.txt / .match).",
    )
    parser_cli.add_argument(
        "--match-id",
        type=int,
        help="ID da partida no StatsBomb (ex: 3869253 para Croácia x Brasil na Copa 2022).",
    )
    parser_cli.add_argument(
        "--inicio",
        type=str,
        default="14:20",
        help="Tempo inicial no formato MM:SS quando usado com --match-id (padrão: 14:20).",
    )
    parser_cli.add_argument(
        "--fim",
        type=str,
        default="14:35",
        help="Tempo final no formato MM:SS quando usado com --match-id (padrão: 14:35).",
    )
    parser_cli.add_argument(
        "--mostrar-dsl",
        action="store_true",
        help="Exibe o código-fonte intermediário gerado na DSL antes do relatório compilado.",
    )
    parser_cli.add_argument(
        "--tokens",
        action="store_true",
        help="Exibe a lista de tokens reconhecidos pelo Analisador Léxico (ply.lex).",
    )
    args = parser_cli.parse_args()

    compilador = CompiladorTatico()

    try:
        if args.match_id is not None:
            min_ini, seg_ini = _parse_mm_ss(args.inicio)
            min_fim, seg_fim = _parse_mm_ss(args.fim)
            codigo_fonte = extrair_lance_para_dsl(
                match_id=args.match_id,
                minuto_inicio=min_ini,
                segundo_inicio=seg_ini,
                minuto_fim=min_fim,
                segundo_fim=seg_fim,
            )
        elif args.arquivo:
            with open(args.arquivo, "r", encoding="utf-8") as f:
                codigo_fonte = f.read()
        else:
            codigo_fonte = EXEMPLO_MEMORIA

        if args.mostrar_dsl:
            print("=" * 70)
            print("               CÓDIGO GERADO NA LINGUAGEM FORMAL (DSL)")
            print("=" * 70)
            print(codigo_fonte)
            print()

        if args.tokens:
            print("=" * 70)
            print("               TOKENS RECONHECIDOS PELO PLY.LEX")
            print("=" * 70)
            for tok in compilador.tokenizar(codigo_fonte):
                print(f"Linha {tok.lineno:02d} | Tipo: {tok.type:<12} | Valor: {tok.value}")
            print()

        resultado = compilador.compilar_texto(codigo_fonte)
        print(resultado["texto"])

    except (SyntaxError, ValueError, FileNotFoundError) as erro:
        print(f"\n[ERRO DE COMPILAÇÃO] {erro}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
