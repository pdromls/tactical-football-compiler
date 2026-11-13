# -*- coding: utf-8 -*-
"""
Módulo Autônomo de Engenharia de Dados e Modelagem Espacial ('campo_statsbomb.py').
Realiza duas responsabilidades principais na arquitetura do Compilador Tático:
  1. Modelagem geométrica do campo (padrão 120x80 da StatsBomb) em 11 zonas táticas;
  2. Extração de eventos reais ('Pass' e 'Shot') de partidas via statsbombpy
     (com cache local em disco e fallback HTTP para o repositório Open Data),
     detectando a equipe detentora da posse e as trocas de posse ('POSSE' e 'TROCA_POSSE')
     e serializando para a gramática formal da Linguagem Tática (DSL).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch
import urllib.request
import warnings
from typing import Any

try:  # funciona como pacote (src.campo_statsbomb) e como script
    from .semantico import identificar_zona as _identificar_zona_semantica
except ImportError:  # pragma: no cover
    from semantico import identificar_zona as _identificar_zona_semantica


# Diretório de cache local para que partidas já baixadas rodem instantaneamente e offline
CACHE_DIR = Path(__file__).resolve().parent.parent / "data_cache"


# ==============================================================================
# 1. MODELAGEM GEOMÉTRICA DO CAMPO EM 11 ZONAS TÁTICAS (STATSBOMB 120x80)
# ==============================================================================

def identificar_zona(x: float, y: float) -> str:
    """
    [MODIFICADO] Antes este módulo tinha uma cópia própria da função com limiar
    X >= 40 para o meio-campo, enquanto o compilador usava X >= 38 (644 pontos do
    campo caíam em zonas diferentes). Agora existe UMA única definição, em
    `semantico.py`; aqui apenas validamos os limites do campo e delegamos.

    As coordenadas da StatsBomb já vêm no referencial do time que executa o
    evento (X = 120 é sempre o gol adversário de quem age).
    """
    x_val, y_val = float(x), float(y)
    if not (0.0 <= x_val <= 120.0 and 0.0 <= y_val <= 80.0):
        raise ValueError(
            f"Coordenada ({x_val}, {y_val}) fora dos limites do campo StatsBomb (120x80)."
        )
    return _identificar_zona_semantica(x_val, y_val)


# ==============================================================================
# 2. EXTRAÇÃO E FORMATAÇÃO DE LANCES DO STATSBOMB PARA A DSL FORMAL
# ==============================================================================

def _mapear_desfecho_finalizacao(shot_outcome: str) -> str:
    """
    Traduz o atributo 'shot_outcome' do StatsBomb para um dos terminais
    válidos da gramática BNF: GOL, DEFESA, TRAVE ou FORA.
    """
    outcome = (shot_outcome or "").strip().upper()
    if outcome == "GOAL":
        return "GOL"
    if outcome in ("SAVED", "SAVED TO POST", "BLOCKED"):
        return "DEFESA"
    if outcome == "POST":
        return "TRAVE"
    return "FORA"


def _eh_valor_valido(val: Any) -> bool:
    """Verifica se um valor vindo de DataFrame/JSON não é None nem NaN."""
    if val is None:
        return False
    if isinstance(val, float) and math.isnan(val):
        return False
    return True


def _obter_eventos_statsbomb(match_id: int) -> list[dict[str, Any]]:
    """
    Obtém os eventos da partida via cache local (se já baixado anteriormente),
    via `statsbombpy.sb.events(match_id=match_id)` ou via JSON oficial do GitHub.
    """
    arquivo_cache = CACHE_DIR / f"match_{int(match_id)}.json"
    if arquivo_cache.exists():
        return json.loads(arquivo_cache.read_text(encoding="utf-8"))

    registros_normalizados: list[dict[str, Any]] = []

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from statsbombpy import sb  # type: ignore

            df_eventos = sb.events(match_id=match_id)

        registros_brutos = (
            df_eventos.to_dict(orient="records")
            if hasattr(df_eventos, "to_dict")
            else list(df_eventos)
        )
        for idx, reg in enumerate(registros_brutos):
            tipo = reg.get("type")
            if tipo not in ("Pass", "Shot"):
                continue
            loc = reg.get("location")
            end_loc = reg.get("pass_end_location")
            registros_normalizados.append(
                {
                    "index": int(reg.get("index", idx)),
                    "minute": int(reg.get("minute", 0)),
                    "second": int(reg.get("second", 0)),
                    "type": str(tipo),
                    "team": str(reg.get("team", "")).strip() if _eh_valor_valido(reg.get("team")) else "",
                    "possession_team": (
                        str(reg.get("possession_team", "")).strip()
                        if _eh_valor_valido(reg.get("possession_team"))
                        else ""
                    ),
                    "player": str(reg.get("player", "")).strip() if _eh_valor_valido(reg.get("player")) else "",
                    "location": list(loc) if isinstance(loc, (list, tuple)) else None,
                    "pass_end_location": list(end_loc) if isinstance(end_loc, (list, tuple)) else None,
                    "pass_recipient": (
                        str(reg.get("pass_recipient", "")).strip()
                        if _eh_valor_valido(reg.get("pass_recipient"))
                        else ""
                    ),
                    "shot_outcome": (
                        str(reg.get("shot_outcome", "")).strip()
                        if _eh_valor_valido(reg.get("shot_outcome"))
                        else ""
                    ),
                }
            )
    except ImportError:
        url = (
            "https://raw.githubusercontent.com/statsbomb/open-data/"
            f"master/data/events/{int(match_id)}.json"
        )
        with urllib.request.urlopen(url, timeout=15) as response:
            dados_json = json.loads(response.read().decode("utf-8"))
        for ev in dados_json:
            tipo = ev.get("type", {}).get("name")
            if tipo not in ("Pass", "Shot"):
                continue
            passe_info = ev.get("pass", {}) if tipo == "Pass" else {}
            shot_info = ev.get("shot", {}) if tipo == "Shot" else {}
            registros_normalizados.append(
                {
                    "index": int(ev.get("index", 0)),
                    "minute": int(ev.get("minute", 0)),
                    "second": int(ev.get("second", 0)),
                    "type": tipo,
                    "team": ev.get("team", {}).get("name", ""),
                    "possession_team": ev.get("possession_team", {}).get("name", ""),
                    "player": ev.get("player", {}).get("name", ""),
                    "location": ev.get("location"),
                    "pass_end_location": passe_info.get("end_location"),
                    "pass_recipient": passe_info.get("recipient", {}).get("name", ""),
                    "shot_outcome": shot_info.get("outcome", {}).get("name", ""),
                }
            )

    # Salva no cache local para que as próximas execuções rodem em < 0.05s e offline
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        arquivo_cache.write_text(
            json.dumps(registros_normalizados, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        pass

    return registros_normalizados


def extrair_lance_para_dsl(
    match_id: int,
    minuto_inicio: int,
    segundo_inicio: int,
    minuto_fim: int,
    segundo_fim: int,
) -> str:
    """
    Baixa os eventos da partida via `statsbombpy.sb.events(match_id=match_id)`,
    filtra os eventos de 'Pass' e 'Shot' ocorridos no intervalo de tempo especificado
    e converte os dados brutos em uma string formatada rigorosamente na sintaxe da DSL.

    Quando os eventos possuem identificação da equipe ('team'), agrupa cada sequência
    em blocos `POSSE "Equipe" { ... }` e insere `TROCA_POSSE "Nova Equipe";` sempre
    que a posse de bola muda de um time para o outro.
    """
    tempo_ini_seg = int(minuto_inicio) * 60 + int(segundo_inicio)
    tempo_fim_seg = int(minuto_fim) * 60 + int(segundo_fim)

    if tempo_fim_seg < tempo_ini_seg:
        raise ValueError("O tempo final do lance não pode ser menor que o tempo inicial.")

    registros = _obter_eventos_statsbomb(match_id)

    # [NOVO] Os dois times da partida (para o cabeçalho "A" VS "B"): o campo de
    # ataque de um é o campo de defesa do outro, e o compilador precisa saber disso.
    equipes_partida: list[str] = []
    for reg in registros:
        eq = reg.get("team")
        if _eh_valor_valido(eq) and str(eq).strip():
            eq = str(eq).strip().replace('"', "'")
            if eq not in equipes_partida:
                equipes_partida.append(eq)

    # Filtra apenas eventos 'Pass' e 'Shot' dentro do intervalo [tempo_ini_seg, tempo_fim_seg]
    eventos_filtrados = []
    for idx_padrao, reg in enumerate(registros):
        tipo = reg.get("type")
        if tipo not in ("Pass", "Shot"):
            continue

        minuto = int(reg.get("minute", 0))
        segundo = int(reg.get("second", 0))
        t_evento = minuto * 60 + segundo

        if tempo_ini_seg <= t_evento <= tempo_fim_seg:
            ordem_original = int(reg.get("index", idx_padrao))
            eventos_filtrados.append((t_evento, ordem_original, reg))

    # Garante ordenação estritamente cronológica
    eventos_filtrados.sort(key=lambda item: (item[0], item[1]))

    # Monta a lista de tuplas (equipe, linha_acao_dsl)
    acoes_formatadas: list[tuple[str, str]] = []
    for _, _, ev in eventos_filtrados:
        tipo = ev.get("type")
        equipe_raw = ev.get("team")
        equipe = (
            str(equipe_raw).strip().replace('"', "'")
            if _eh_valor_valido(equipe_raw) and str(equipe_raw).strip()
            else ""
        )

        jogador = ev.get("player")
        if not _eh_valor_valido(jogador) or not str(jogador).strip():
            jogador = "Jogador Desconhecido"
        else:
            jogador = str(jogador).strip().replace('"', "'")

        loc = ev.get("location")
        if not isinstance(loc, (list, tuple)) or len(loc) < 2:
            continue
        x1, y1 = float(loc[0]), float(loc[1])

        if tipo == "Pass":
            end_loc = ev.get("pass_end_location")
            if not isinstance(end_loc, (list, tuple)) or len(end_loc) < 2:
                continue
            x2, y2 = float(end_loc[0]), float(end_loc[1])

            receptor = ev.get("pass_recipient")
            if not _eh_valor_valido(receptor) or not str(receptor).strip():
                receptor_limpo = "Passe Interceptado / Sem Receptor"
            else:
                receptor_limpo = str(receptor).strip().replace('"', "'")

            linha = (
                f'PASSE "{jogador}" ({x1:.1f}, {y1:.1f}) -> '
                f'"{receptor_limpo}" ({x2:.1f}, {y2:.1f});'
            )
            acoes_formatadas.append((equipe, linha))

        elif tipo == "Shot":
            outcome_bruto = ev.get("shot_outcome", "")
            outcome_str = str(outcome_bruto) if _eh_valor_valido(outcome_bruto) else ""
            desfecho = _mapear_desfecho_finalizacao(outcome_str)

            linha = (
                f'FINALIZACAO "{jogador}" ({x1:.1f}, {y1:.1f}) '
                f'RESULTADO {desfecho};'
            )
            acoes_formatadas.append((equipe, linha))

    # Verifica se os dados possuem informação de equipe para estruturar blocos POSSE e TROCA_POSSE
    tem_equipe = any(eq != "" for eq, _ in acoes_formatadas)

    linhas_codigo_dsl: list[str] = []
    if not tem_equipe:
        for _, linha in acoes_formatadas:
            linhas_codigo_dsl.append(f"    {linha}")
    else:
        equipe_atual: str | None = None
        for eq, linha in acoes_formatadas:
            eq_nome = eq or "Equipe Desconhecida"
            if equipe_atual is None:
                equipe_atual = eq_nome
                linhas_codigo_dsl.append(f'    POSSE "{equipe_atual}" {{')
            elif eq_nome != equipe_atual:
                linhas_codigo_dsl.append("    }")
                linhas_codigo_dsl.append(f'    TROCA_POSSE "{eq_nome}";')
                equipe_atual = eq_nome
                linhas_codigo_dsl.append(f'    POSSE "{equipe_atual}" {{')
            linhas_codigo_dsl.append(f"        {linha}")
        if equipe_atual is not None:
            linhas_codigo_dsl.append("    }")

    ts_inicio = f"{int(minuto_inicio):02d}:{int(segundo_inicio):02d}"
    ts_fim = f"{int(minuto_fim):02d}:{int(segundo_fim):02d}"
    corpo_dsl = "\n".join(linhas_codigo_dsl)

    confronto = (
        f' "{equipes_partida[0]}" VS "{equipes_partida[1]}"'
        if len(equipes_partida) == 2 else ""
    )
    return f"LANCE [{ts_inicio} - {ts_fim}]{confronto} {{\n{corpo_dsl}\n}}"


# ==============================================================================
# 3. TESTES UNITÁRIOS EMBUTIDOS
# ==============================================================================

class TestCampoStatsBomb(unittest.TestCase):
    """Testes unitários embutidos para validação das 11 zonas e do extrator DSL."""

    def test_prioridade_grandes_areas(self):
        self.assertEqual(identificar_zona(102.0, 18.0), "Grande Área de Ataque")
        self.assertEqual(identificar_zona(108.5, 39.8), "Grande Área de Ataque")
        self.assertEqual(identificar_zona(120.0, 62.0), "Grande Área de Ataque")

        self.assertEqual(identificar_zona(0.0, 18.0), "Grande Área de Defesa")
        self.assertEqual(identificar_zona(12.0, 40.0), "Grande Área de Defesa")
        self.assertEqual(identificar_zona(18.0, 62.0), "Grande Área de Defesa")

    def test_zonas_ataque(self):
        self.assertEqual(identificar_zona(85.0, 18.5), "Ataque Esquerdo")
        self.assertEqual(identificar_zona(95.0, 40.0), "Ataque Central")
        self.assertEqual(identificar_zona(110.0, 70.0), "Ataque Direito")

    def test_zonas_meio_campo(self):
        self.assertEqual(identificar_zona(50.0, 10.0), "Meio-Campo Esquerdo")
        self.assertEqual(identificar_zona(40.0, 42.1), "Meio-Campo Central")
        self.assertEqual(identificar_zona(79.9, 60.0), "Meio-Campo Direito")

    def test_zonas_defesa(self):
        self.assertEqual(identificar_zona(20.0, 15.0), "Defesa Esquerda")
        self.assertEqual(identificar_zona(25.4, 40.2), "Defesa Central")
        self.assertEqual(identificar_zona(35.0, 65.0), "Defesa Direita")

    def test_extracao_lance_simples_sem_equipe(self):
        """Simula o retorno de eventos sem campo 'team' para validar formato enxuto."""
        eventos_mock = [
            {
                "index": 1,
                "minute": 14,
                "second": 20,
                "type": "Pass",
                "player": "Luka Modrić",
                "location": [25.4, 40.2],
                "pass_end_location": [38.2, 42.1],
                "pass_recipient": "Mateo Kovačić",
            },
            {
                "index": 2,
                "minute": 14,
                "second": 26,
                "type": "Pass",
                "player": "Mateo Kovačić",
                "location": [38.2, 42.1],
                "pass_end_location": [85.0, 18.5],
                "pass_recipient": "Ivan Perišić",
            },
            {
                "index": 3,
                "minute": 14,
                "second": 35,
                "type": "Shot",
                "player": "Andrej Kramarić",
                "location": [108.5, 39.8],
                "shot_outcome": "Goal",
            },
        ]

        with patch(__name__ + "._obter_eventos_statsbomb", return_value=eventos_mock):
            codigo_dsl = extrair_lance_para_dsl(3869420, 14, 20, 14, 35)

        esperado = (
            "LANCE [14:20 - 14:35] {\n"
            '    PASSE "Luka Modrić" (25.4, 40.2) -> "Mateo Kovačić" (38.2, 42.1);\n'
            '    PASSE "Mateo Kovačić" (38.2, 42.1) -> "Ivan Perišić" (85.0, 18.5);\n'
            '    FINALIZACAO "Andrej Kramarić" (108.5, 39.8) RESULTADO GOL;\n'
            "}"
        )
        self.assertEqual(codigo_dsl, esperado)

    def test_extracao_lance_com_troca_de_posse(self):
        """Verifica se mudanças de 'team' geram blocos POSSE e comandos TROCA_POSSE."""
        eventos_mock = [
            {
                "index": 1,
                "minute": 10,
                "second": 0,
                "type": "Pass",
                "team": "Croatia",
                "player": "Dominik Livaković",
                "location": [6.0, 44.0],
                "pass_end_location": [70.6, 67.5],
                "pass_recipient": "Mario Pašalić",
            },
            {
                "index": 2,
                "minute": 10,
                "second": 8,
                "type": "Pass",
                "team": "Brazil",
                "player": "Marcos Aoás Corrêa",
                "location": [25.9, 43.7],
                "pass_end_location": [39.3, 41.0],
                "pass_recipient": "Carlos Henrique Casimiro",
            },
        ]

        with patch(__name__ + "._obter_eventos_statsbomb", return_value=eventos_mock):
            codigo_dsl = extrair_lance_para_dsl(3869420, 10, 0, 10, 15)

        self.assertIn('LANCE [10:00 - 10:15] "Croatia" VS "Brazil" {', codigo_dsl)
        self.assertIn('POSSE "Croatia"', codigo_dsl)
        self.assertIn('TROCA_POSSE "Brazil";', codigo_dsl)
        self.assertIn('POSSE "Brazil"', codigo_dsl)


if __name__ == "__main__":
    print("=" * 70)
    print("  EXECUTANDO DEMONSTRAÇÃO E TESTES DO MÓDULO 'campo_statsbomb.py'")
    print("=" * 70)
    unittest.main(verbosity=2)
