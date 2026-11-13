# -*- coding: utf-8 -*-
"""
Módulo Semântico e Geométrico (Ambiente SDT) do Compilador Tático.
Implementa o mapeamento espacial do campo 120x80 da StatsBomb em 11 zonas táticas,
cálculos vetoriais (distância euclidiana, Delta X, Delta Y), classificação de passes,
rastreamento de posse de bola por equipe e síntese do relatório tático.
"""

import math


def identificar_zona(x: float, y: float, estrito_40: bool = False) -> str:
    """
    Mapeia uma coordenada cartesiana (X, Y) no padrão StatsBomb (120x80)
    para uma das 11 zonas táticas do campo (referencial da equipe com a posse).

    Prioridade 1 (Alta Prioridade):
      - Grande Área de Ataque: X em [102, 120] e Y em [18, 62]
      - Grande Área de Defesa: X em [0, 18] e Y em [18, 62]
    Prioridade 2 (Divisão Longitudinal X e Transversal Y):
      - Ataque: X >= 80
      - Meio-Campo: 40 <= X < 80 (ou X >= 38 na zona central de transição se estrito_40=False)
      - Defesa: X < 40
      - Corredores Laterais/Central: Esquerdo (Y < 25), Central (25 <= Y <= 55), Direito (Y > 55)
    """
    # 1. Alta prioridade: Grandes Áreas
    if 102.0 <= x <= 120.0 and 18.0 <= y <= 62.0:
        return "Grande Área de Ataque"
    if 0.0 <= x <= 18.0 and 18.0 <= y <= 62.0:
        return "Grande Área de Defesa"

    # 2. Definição do corredor transversal (Eixo Y: 0 a 80)
    if y < 25.0:
        corredor_masc = "Esquerdo"
        corredor_fem = "Esquerda"
    elif y <= 55.0:
        corredor_masc = "Central"
        corredor_fem = "Central"
    else:
        corredor_masc = "Direito"
        corredor_fem = "Direita"

    # 3. Definição do setor longitudinal (Eixo X: 0 a 120)
    limiar_meio = 40.0 if estrito_40 else 38.0
    if x >= 80.0:
        return f"Ataque {corredor_masc}"
    elif x >= limiar_meio:
        return f"Meio-Campo {corredor_masc}"
    else:
        return f"Defesa {corredor_fem}"


def eh_corredor_lateral(zona_orig: str) -> bool:
    """Verifica se a zona de origem pertence a um corredor lateral (Esquerdo/Direito)."""
    return any(lat in zona_orig for lat in ("Esquerdo", "Esquerda", "Direito", "Direita"))


def calcular_distancia(c1: tuple, c2: tuple) -> float:
    """Calcula a distância euclidiana entre c1=(x1, y1) e c2=(x2, y2)."""
    return math.hypot(c2[0] - c1[0], c2[1] - c1[1])


def classificar_passe(
    dist: float,
    coord_orig: tuple,
    coord_dest: tuple,
    zona_orig: str,
    zona_dest: str,
) -> tuple:
    """
    Classifica o passe e sua direção vetorial com base nas regras semânticas:
      - Cruzamento: origem lateral (Y < 25 ou Y > 55) e destino na Grande Área de Ataque
      - Passe curto: dist <= 15m
      - Passe médio: 15m < dist <= 30m
      - Lançamento longo: dist > 30m
    Retorna a tupla (classificacao, direcao).
    """
    dx = coord_dest[0] - coord_orig[0]
    dy = coord_dest[1] - coord_orig[1]

    # Regra prioritária: Cruzamento para a Grande Área
    if eh_corredor_lateral(zona_orig) and zona_dest == "Grande Área de Ataque":
        return ("Cruzamento", "para a Grande Área de Ataque")

    # Classificação por distância euclidiana
    if dist <= 15.0:
        tipo = "Passe curto"
    elif dist <= 30.0:
        tipo = "Passe médio"
    else:
        tipo = "Lançamento longo"

    # Classificação direcional baseada em Delta X e Delta Y
    if dx >= 25.0 or "Ataque" in zona_dest:
        direcao = "para o ataque"
    elif dx > 2.0:
        direcao = "para frente"
    elif dx < -2.0:
        direcao = "para trás (recuo)"
    elif abs(dy) >= 20.0:
        direcao = "em inversão lateral"
    else:
        direcao = "lateral"

    return (tipo, direcao)


def tempo_para_segundos(tempo_str: str) -> int:
    """Converte string 'MM:SS' em total de segundos."""
    minutos, segundos = map(int, tempo_str.split(':'))
    return minutos * 60 + segundos


def segundos_para_tempo(total_seg: int) -> str:
    """Converte total de segundos em string 'MM:SS'."""
    minutos = total_seg // 60
    segundos = total_seg % 60
    return f"{minutos:02d}:{segundos:02d}"


def gerar_relatorio_final(intervalo: dict, acoes: list) -> dict:
    """
    Ação semântica da raiz (<Lance>): sintetiza o relatório textual completo,
    rastreando a equipe com a posse da bola, trocas de posse e o referencial
    de zonas táticas de cada time.
    """
    t_ini = intervalo["inicio_seg"]
    duracao = intervalo["duracao_seg"]

    # Separa ações reais de bola (PASSE / FINALIZACAO) para contagem e interpolação
    acoes_bola = [a for a in acoes if a["tipo_acao"] in ("PASSE", "FINALIZACAO")]
    n_acoes_bola = len(acoes_bola)

    linhas_acoes = []
    equipe_atual = None
    trocas_de_posse = 0
    equipes_participantes = []
    ultimo_timestamp = segundos_para_tempo(t_ini)
    troca_ja_anunciada_para = None
    idx_bola = 0

    for acao in acoes:
        tipo_acao = acao["tipo_acao"]

        # Caso 1: Comando explícito de TROCA_POSSE na DSL
        if tipo_acao == "TROCA_POSSE":
            nova_eq = acao["nova_equipe"]
            if equipe_atual and equipe_atual != nova_eq:
                linhas_acoes.append(
                    f"    ------------------------------------------------------------------\n"
                    f"    >> TROCA DE POSSE ({ultimo_timestamp}): {equipe_atual} perdeu a posse -> "
                    f"{nova_eq} recuperou a bola <<\n"
                    f"    ------------------------------------------------------------------"
                )
                trocas_de_posse += 1
                troca_ja_anunciada_para = nova_eq
            equipe_atual = nova_eq
            if nova_eq not in equipes_participantes:
                equipes_participantes.append(nova_eq)
            continue

        # Caso 2: Ação de bola (PASSE ou FINALIZACAO)
        if n_acoes_bola > 1:
            t_estimado = int(t_ini + (duracao * idx_bola) // (n_acoes_bola - 1))
        else:
            t_estimado = t_ini

        timestamp_str = segundos_para_tempo(t_estimado)
        ultimo_timestamp = timestamp_str
        idx_bola += 1
        acao["ordem"] = idx_bola
        acao["timestamp"] = timestamp_str

        equipe_acao = acao.get("equipe") or equipe_atual
        if equipe_acao:
            acao["equipe"] = equipe_acao
            if equipe_acao not in equipes_participantes:
                equipes_participantes.append(equipe_acao)

            # Se mudou de equipe sem ter passado por um TROCA_POSSE explícito antes
            if (
                equipe_atual is not None
                and equipe_acao != equipe_atual
                and troca_ja_anunciada_para != equipe_acao
            ):
                linhas_acoes.append(
                    f"    ------------------------------------------------------------------\n"
                    f"    >> TROCA DE POSSE ({timestamp_str}): {equipe_atual} perdeu a posse -> "
                    f"{equipe_acao} recuperou a bola <<\n"
                    f"    ------------------------------------------------------------------"
                )
                trocas_de_posse += 1

            # Se é o primeiro toque de uma posse identificada, exibe cabeçalho da posse
            if equipe_atual is None:
                linhas_acoes.append(f"--- POSSE INICIAL: {equipe_acao} ---")

            equipe_atual = equipe_acao
            troca_ja_anunciada_para = None

        tag_equipe = f" [{equipe_atual}]" if equipe_atual else ""
        sufixo_zona = f" ({equipe_atual})" if equipe_atual else ""
        prefixo_fase = f" [Fase: {acao['fase']}]" if acao.get("fase") else ""

        if tipo_acao == "PASSE":
            linhas_acoes.append(
                f"[{idx_bola}] {timestamp_str}{tag_equipe}{prefixo_fase} - {acao['autor']}: "
                f"{acao['classificacao']} {acao['direcao']} ({acao['distancia']:.1f}m).\n"
                f"    Origem: {acao['zona_orig']}{sufixo_zona} -> "
                f"Destino: {acao['zona_dest']}{sufixo_zona}."
            )
        elif tipo_acao == "FINALIZACAO":
            linhas_acoes.append(
                f"[{idx_bola}] {timestamp_str}{tag_equipe}{prefixo_fase} - {acao['autor']}: "
                f"Finalização na {acao['zona_orig']}{sufixo_zona}!\n"
                f"    Desfecho: {acao['desfecho']}"
            )

    # Síntese do resumo da construção tática
    if n_acoes_bola > 0:
        primeira = acoes_bola[0]
        ultima = acoes_bola[-1]
        eq_ini = f" ({primeira['equipe']})" if primeira.get("equipe") else ""
        eq_fim = f" ({ultima['equipe']})" if ultima.get("equipe") else ""
        zona_inicial = f"{primeira['zona_orig']}{eq_ini}"

        info_trocas = (
            f" Houve {trocas_de_posse} troca(s) de posse de bola no período."
            if trocas_de_posse > 0
            else ""
        )

        if ultima["tipo_acao"] == "FINALIZACAO":
            desfecho_limpo = ultima["desfecho"].rstrip("!")
            resumo = (
                f"Progressão vertical iniciando na {zona_inicial} e culminando "
                f"em {desfecho_limpo}{eq_fim}.{info_trocas}"
            )
        else:
            resumo = (
                f"Progressão tática iniciando na {zona_inicial} e avançando até "
                f"{ultima['zona_dest']}{eq_fim} ({n_acoes_bola} ações registradas).{info_trocas}"
            )
    else:
        resumo = "Nenhuma ação tática registrada no intervalo."

    relatorio_texto = (
        "======================================================================\n"
        "               RELATÓRIO TÁTICO DO LANCE (SAÍDA DO COMPILADOR)\n"
        "======================================================================\n"
        f"Tempo: {intervalo['inicio']} a {intervalo['fim']} (Duração: {duracao} segundos)\n\n"
        "SEQUÊNCIA DE AÇÕES TRADUZIDAS:\n"
        + "\n".join(linhas_acoes)
        + "\n\nRESUMO DA CONSTRUÇÃO:\n"
        + f"{resumo}\n"
        + "======================================================================"
    )

    return {
        "intervalo": intervalo,
        "acoes": acoes_bola,
        "trocas_de_posse": trocas_de_posse,
        "equipes": equipes_participantes,
        "resumo": resumo,
        "texto": relatorio_texto,
    }
