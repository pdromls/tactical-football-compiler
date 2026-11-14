# -*- coding: utf-8 -*-
"""
Pacote do Compilador / Tradutor Tático de Futebol Dirigido pela Sintaxe (PLY).
[NOVO] Arquivo inteiro criado para este trabalho (não existe no exemplo calc do PLY).
"""

from .compilador import CompiladorTatico
from .semantico import identificar_zona, calcular_distancia, classificar_passe

__all__ = [
    "CompiladorTatico",
    "identificar_zona",
    "calcular_distancia",
    "classificar_passe",
]
