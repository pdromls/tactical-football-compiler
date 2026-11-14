# -*- coding: utf-8 -*-
"""
Módulo Semântico e Geométrico (Ambiente SDT) do Compilador Tático.
[NOVO] Código de usuário criado para o trabalho (não existe no exemplo base do PLY).

Implementa o mapeamento espacial do campo 120x80 da StatsBomb em 11 zonas táticas,
cálculos vetoriais (distância euclidiana, Delta X, Delta Y), classificação de passes,
rastreamento de posse por equipe, perspectiva de campo por time e síntese do relatório.

REFERENCIAL DE COORDENADAS (POR TIME)
-------------------------------------
Toda coordenada da DSL está no referencial do TIME QUE EXECUTA A AÇÃO, igual à
StatsBomb: X = 0 é a linha de fundo da própria defesa e X = 120 é o gol adversário.
Por isso o "Ataque" do Brasil é a "Defesa" da Croácia. O mesmo ponto físico visto
pelo adversário é obtido por uma rotação de 180 graus:

        espelhar(x, y) = (120 - x, 80 - y)

Ex.: "Ataque Esquerdo" (Croácia) == "Defesa Direita" (Brasil).
"""

import math

# [NOVO] Dimensões oficiais do campo StatsBomb
COMPRIMENTO_CAMPO = 120.0
LARGURA_CAMPO = 80.0

# [NOVO] Limiares únicos usados por TODO o projeto (compilador e extrator)
LIMIAR_MEIO_CAMPO = 40.0   # X < 40: Defesa | 40 <= X < 80: Meio-Campo
LIMIAR_ATAQUE = 80.0       # X >= 80: Ataque
LIMIAR_DIRECAO_X = 2.0     # |dX| <= 2 m: passe sem progressão
LIMIAR_INVERSAO_Y = 20.0   # |dY| >= 20 m sem progressão: inversão lateral


def identificar_zona(x: float, y: float) -> str:
    """
    Mapeia (X, Y) no referencial do time que executa a ação para uma das 11 zonas.

    Prioridade 1: Grande Área de Ataque (X em [102,120], Y em [18,62])
                  Grande Área de Defesa (X em [0,18],   Y em [18,62])
    Prioridade 2: Setor (Defesa X<40 | Meio-Campo 40<=X<80 | Ataque X>=80)
                  x Corredor (Esquerdo Y<25 | Central 25<=Y<=55 | Direito Y>55)
    """
    if 102.0 <= x <= 120.0 and 18.0 <= y <= 62.0:
        return "Grande Área de Ataque"
    if 0.0 <= x <= 18.0 and 18.0 <= y <= 62.0:
        return "Grande Área de Defesa"

    if y < 25.0:
        corredor_masc, corredor_fem = "Esquerdo", "Esquerda"
    elif y <= 55.0:
        corredor_masc, corredor_fem = "Central", "Central"
    else:
        corredor_masc, corredor_fem = "Direito", "Direita"

    if x >= LIMIAR_ATAQUE:
        return f"Ataque {corredor_masc}"
    if x >= LIMIAR_MEIO_CAMPO:
        return f"Meio-Campo {corredor_masc}"
    return f"Defesa {corredor_fem}"


def com_preposicao(zona: str) -> str:
    """[NOVO] Concordância: 'na Defesa Central' / 'na Grande Área', mas 'no Ataque' / 'no Meio-Campo'."""
    return f"no {zona}" if zona.startswith(("Ataque", "Meio-Campo")) else f"na {zona}"


def espelhar(coord: tuple) -> tuple:
    """[NOVO] Converte uma coordenada para o referencial do time adversário (rotação 180°)."""
    return (round(COMPRIMENTO_CAMPO - coord[0], 2), round(LARGURA_CAMPO - coord[1], 2))


def zona_para_adversario(coord: tuple) -> str:
    """[NOVO] Zona em que o MESMO ponto físico fica para o time adversário."""
    return identificar_zona(*espelhar(coord))


def eh_corredor_lateral(coord: tuple) -> bool:
    """Verifica se a coordenada está num corredor lateral (Y < 25 ou Y > 55)."""
    return coord[1] < 25.0 or coord[1] > 55.0


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
    Classifica o passe e sua direção vetorial:
      - Cruzamento: origem no setor de ataque (X >= 80) E corredor lateral
                    (Y < 25 ou Y > 55) E destino na Grande Área de Ataque
      - Passe curto: dist <= 15m | Passe médio: 15m < dist <= 30m | Lançamento longo: > 30m
    Retorna a tupla (classificacao, direcao).
    """
    dx = coord_dest[0] - coord_orig[0]
    dy = coord_dest[1] - coord_orig[1]

    # [MODIFICADO] Correção: antes um passe da Defesa Esquerda para a grande área
    # adversária virava "Cruzamento". Agora a origem precisa estar no setor de ataque.
    if (
        coord_orig[0] >= LIMIAR_ATAQUE
        and eh_corredor_lateral(coord_orig)
        and zona_dest == "Grande Área de Ataque"
    ):
        return ("Cruzamento", "para a Grande Área de Ataque")

    if dist <= 15.0:
        tipo = "Passe curto"
    elif dist <= 30.0:
        tipo = "Passe médio"
    else:
        tipo = "Lançamento longo"

    # [MODIFICADO] Antes bastava o destino estar no Ataque, e um toque de lado
    # (dX = +1 m) dentro do setor ofensivo virava "para o ataque".
    if dx >= 25.0 or (dx > LIMIAR_DIRECAO_X and "Ataque" in zona_dest):
        direcao = "para o ataque"
    elif dx > LIMIAR_DIRECAO_X:
        direcao = "para frente"
    elif dx < -LIMIAR_DIRECAO_X:
        direcao = "para trás (recuo)"
    elif abs(dy) >= LIMIAR_INVERSAO_Y:
        direcao = "em inversão lateral"
    else:
        direcao = "lateral"

    return (tipo, direcao)


def tempo_para_segundos(tempo_str: str) -> int:
    """Converte string 'MM:SS' em total de segundos."""
    minutos, segundos = map(int, tempo_str.split(':'))
    # [NOVO] O léxico aceita \d{2} nos segundos; aqui a semântica exige 00..59
    if segundos >= 60:
        raise ValueError(
            f"Erro Semântico: Tempo '{tempo_str}' inválido (segundos devem estar entre 00 e 59)."
        )
    return minutos * 60 + segundos


def segundos_para_tempo(total_seg: int) -> str:
    """Converte total de segundos em string 'MM:SS'."""
    return f"{total_seg // 60:02d}:{total_seg % 60:02d}"


# ==============================================================================
# [NOVO] Rótulos hierárquicos (FASE / jogadas táticas recursivas)
# ==============================================================================

def anotar_rotulo(acoes: list, campo: str, rotulo: str) -> list:
    """Prefixa o rótulo do bloco externo em cada ação: 'Externo > Interno'."""
    resultado = []
    for acao in acoes:
        copia = dict(acao)
        copia[campo] = f"{rotulo} > {copia[campo]}" if copia.get(campo) else rotulo
        resultado.append(copia)
    return resultado


def apenas_passes(acoes: list) -> list:
    return [a for a in acoes if a["tipo_acao"] == "PASSE"]


def validar_jogada_uma_equipe(nome_jogada: str, acoes: list) -> None:
    """
    [NOVO] Uma jogada tática (TABELA, TRIANGULACAO, CONTRA_ATAQUE) pertence a UMA
    equipe: não pode conter TROCA_POSSE nem ações de times diferentes. Sem esta
    regra, um CONTRA_ATAQUE com troca de posse somaria coordenadas de referenciais
    diferentes (o ataque de um time é a defesa do outro).
    """
    if any(a["tipo_acao"] == "TROCA_POSSE" for a in acoes):
        raise ValueError(
            f"Erro Semântico: {nome_jogada} não pode conter TROCA_POSSE "
            "(uma jogada tática pertence a uma única equipe)."
        )
    equipes = {a["equipe"] for a in acoes if a.get("equipe")}
    if len(equipes) > 1:
        raise ValueError(
            f"Erro Semântico: {nome_jogada} mistura ações de equipes diferentes "
            f"({', '.join(sorted(equipes))})."
        )


def validar_tabela(jogador_a: str, jogador_b: str, acoes: list) -> None:
    """[NOVO] TABELA A B: os 2 primeiros passes devem ser A -> B e B -> A."""
    if jogador_a == jogador_b:
        raise ValueError(
            f"Erro Semântico: TABELA exige dois jogadores diferentes (recebeu \"{jogador_a}\" duas vezes)."
        )
    validar_jogada_uma_equipe("TABELA", acoes)
    passes = apenas_passes(acoes)
    if (
        len(passes) < 2
        or (passes[0]["autor"], passes[0]["receptor"]) != (jogador_a, jogador_b)
        or (passes[1]["autor"], passes[1]["receptor"]) != (jogador_b, jogador_a)
    ):
        raise ValueError(
            f"Erro Semântico: TABELA \"{jogador_a}\" \"{jogador_b}\" exige o passe "
            f"{jogador_a} -> {jogador_b} seguido de {jogador_b} -> {jogador_a}."
        )


def validar_triangulacao(acoes: list) -> None:
    """[NOVO] TRIANGULACAO: >= 3 passes envolvendo exatamente 3 jogadores distintos."""
    validar_jogada_uma_equipe("TRIANGULACAO", acoes)
    passes = apenas_passes(acoes)
    envolvidos = {p["autor"] for p in passes} | {p["receptor"] for p in passes}
    if len(passes) < 3 or len(envolvidos) != 3:
        raise ValueError(
            "Erro Semântico: TRIANGULACAO exige pelo menos 3 passes entre exatamente "
            f"3 jogadores (encontrados {len(passes)} passes e {len(envolvidos)} jogadores)."
        )


def validar_contra_ataque(acoes: list) -> float:
    """[NOVO] CONTRA_ATAQUE: avanço em X >= 40 m usando no máximo 6 passes."""
    validar_jogada_uma_equipe("CONTRA_ATAQUE", acoes)
    passes = apenas_passes(acoes)
    if not passes:
        raise ValueError("Erro Semântico: CONTRA_ATAQUE precisa de pelo menos um passe.")
    avanco = passes[-1]["coord_dest"][0] - passes[0]["coord_orig"][0]
    if avanco < 40.0 or len(passes) > 6:
        raise ValueError(
            f"Erro Semântico: CONTRA_ATAQUE exige avanço >= 40 m em até 6 passes "
            f"(avanço = {avanco:.1f} m, passes = {len(passes)})."
        )
    return avanco


# ==============================================================================
# Síntese do relatório (ação semântica da raiz <Lance>)
# ==============================================================================

def _zona_com_perspectiva(zona: str, coord: tuple, equipe, adversario) -> str:
    """[NOVO] 'Ataque Esquerdo (Croatia) = Defesa Direita (Brazil)'."""
    if not equipe:
        return zona
    texto = f"{zona} ({equipe})"
    if adversario:
        texto += f" = {zona_para_adversario(coord)} ({adversario})"
    return texto


def gerar_relatorio_final(intervalo: dict, confronto, acoes: list) -> dict:
    """
    Ação semântica da raiz (<Lance>): sintetiza o relatório textual completo,
    rastreando a equipe com a posse, trocas de posse e a perspectiva de campo
    de cada time (o campo de ataque de um é o campo de defesa do outro).
    """
    t_ini = intervalo["inicio_seg"]
    duracao = intervalo["duracao_seg"]

    acoes_bola = [a for a in acoes if a["tipo_acao"] in ("PASSE", "FINALIZACAO")]
    n_acoes_bola = len(acoes_bola)

    # [NOVO] Equipes do confronto: declaradas no cabeçalho ou inferidas pelas posses
    if confronto:
        equipes_confronto = list(confronto)
    else:
        equipes_confronto = []
        for a in acoes:
            eq = a.get("equipe") or a.get("nova_equipe")
            if eq and eq not in equipes_confronto:
                equipes_confronto.append(eq)

    def adversario_de(equipe):
        if equipe and len(equipes_confronto) == 2 and equipe in equipes_confronto:
            return equipes_confronto[1 - equipes_confronto.index(equipe)]
        return None

    linhas_acoes = []
    avisos = []
    equipe_atual = None
    trocas_de_posse = 0
    equipes_participantes = []
    ultimo_timestamp = segundos_para_tempo(t_ini)
    troca_pendente = None   # (equipe_que_perdeu, equipe_que_recuperou, timestamp)
    equipe_esperada = None  # [NOVO] equipe anunciada pelo último TROCA_POSSE
    ultima_bola = None      # última ação de bola (para checar continuidade)
    idx_bola = 0

    def anunciar_troca(perdeu, recuperou, ts, acao_recuperacao):
        nonlocal trocas_de_posse
        trocas_de_posse += 1
        local = ""
        if acao_recuperacao is not None:
            c = acao_recuperacao["coord_orig"]
            # Mesmo ponto físico nas duas perspectivas
            local = (
                f"\n    Local da recuperação: {identificar_zona(*c)} ({recuperou}) = "
                f"{zona_para_adversario(c)} ({perdeu})"
            )
        linhas_acoes.append(
            "    ------------------------------------------------------------------\n"
            f"    >> TROCA DE POSSE (~{ts}): {perdeu} perdeu a posse -> {recuperou} recuperou a bola <<"
            f"{local}\n"
            "    ------------------------------------------------------------------"
        )

    for acao in acoes:
        tipo_acao = acao["tipo_acao"]

        if tipo_acao == "TROCA_POSSE":
            nova_eq = acao["nova_equipe"]
            equipe_esperada = nova_eq
            if equipe_atual and equipe_atual != nova_eq:
                troca_pendente = (equipe_atual, nova_eq, ultimo_timestamp)
            equipe_atual = nova_eq
            if nova_eq not in equipes_participantes:
                equipes_participantes.append(nova_eq)
            continue

        # [MODIFICADO] Horário estimado por interpolação linear (a DSL não traz o
        # tempo de cada ação). Exibido com '~' para não parecer um dado real.
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

            # [NOVO] Depois de TROCA_POSSE "Y", a próxima ação de bola tem de ser de Y
            if equipe_esperada is not None and equipe_acao != equipe_esperada:
                raise ValueError(
                    f"Erro Semântico: TROCA_POSSE \"{equipe_esperada}\" seguida de uma ação "
                    f"de \"{equipe_acao}\" ({acao['autor']})."
                )
            equipe_esperada = None

            if troca_pendente and troca_pendente[1] == equipe_acao:
                anunciar_troca(troca_pendente[0], equipe_acao, troca_pendente[2], acao)
                troca_pendente = None
            elif equipe_atual is not None and equipe_acao != equipe_atual:
                anunciar_troca(equipe_atual, equipe_acao, timestamp_str, acao)
                troca_pendente = None
            elif equipe_atual is None:
                linhas_acoes.append(f"--- POSSE INICIAL: {equipe_acao} ---")
            equipe_atual = equipe_acao

        adversario = adversario_de(equipe_atual)
        acao["adversario"] = adversario
        acao["zona_orig_adversario"] = zona_para_adversario(acao["coord_orig"]) if adversario else None

        # [NOVO] Aviso semântico de continuidade: dentro da mesma posse, quem age
        # deveria ser quem recebeu o passe anterior (não aborta a compilação, pois
        # dados reais têm conduções/disputas que não viram eventos da DSL).
        if (
            ultima_bola is not None
            and ultima_bola["tipo_acao"] == "PASSE"
            and ultima_bola.get("equipe") == acao.get("equipe")
            and not ultima_bola["receptor"].startswith("Passe Interceptado")
            and ultima_bola["receptor"] != acao["autor"]
        ):
            avisos.append(
                f"Aviso Semântico (ação {idx_bola}): {ultima_bola['receptor']} recebeu a bola, "
                f"mas a próxima ação é de {acao['autor']}."
            )
        ultima_bola = acao

        tag_equipe = f" [{equipe_atual}]" if equipe_atual else ""
        rotulos = []
        if acao.get("fase"):
            rotulos.append(f"Fase: {acao['fase']}")
        if acao.get("jogada"):
            rotulos.append(f"Jogada: {acao['jogada']}")
        prefixo = "".join(f" [{r}]" for r in rotulos)

        if tipo_acao == "PASSE":
            origem = _zona_com_perspectiva(acao["zona_orig"], acao["coord_orig"], equipe_atual, adversario)
            destino = _zona_com_perspectiva(acao["zona_dest"], acao["coord_dest"], equipe_atual, adversario)
            linhas_acoes.append(
                f"[{idx_bola}] ~{timestamp_str}{tag_equipe}{prefixo} - {acao['autor']} -> {acao['receptor']}: "
                f"{acao['classificacao']} {acao['direcao']} ({acao['distancia']:.1f}m).\n"
                f"    Origem: {origem}\n"
                f"    Destino: {destino}"
            )
        elif tipo_acao == "FINALIZACAO":
            local = _zona_com_perspectiva(acao["zona_orig"], acao["coord_orig"], equipe_atual, adversario)
            rebote = f" (rebote #{acao['tentativa'] - 1})" if acao.get("tentativa", 1) > 1 else ""
            linhas_acoes.append(
                f"[{idx_bola}] ~{timestamp_str}{tag_equipe}{prefixo} - {acao['autor']}: "
                f"Finalização{rebote} {com_preposicao(local)}!\n"
                f"    Desfecho: {acao['desfecho']}"
            )

    if troca_pendente:  # TROCA_POSSE no fim do lance, sem ação posterior
        anunciar_troca(troca_pendente[0], troca_pendente[1], troca_pendente[2], None)

    # Síntese do resumo da construção tática
    if n_acoes_bola > 0:
        primeira, ultima = acoes_bola[0], acoes_bola[-1]
        eq_ini = f" ({primeira['equipe']})" if primeira.get("equipe") else ""
        eq_fim = f" ({ultima['equipe']})" if ultima.get("equipe") else ""
        zona_inicial = f"{primeira['zona_orig']}{eq_ini}"
        info_trocas = (
            f" Houve {trocas_de_posse} troca(s) de posse de bola no período."
            if trocas_de_posse > 0 else ""
        )
        if ultima["tipo_acao"] == "FINALIZACAO":
            resumo = (
                f"Progressão vertical iniciando {com_preposicao(zona_inicial)} e culminando "
                f"em {ultima['desfecho'].rstrip('!')}{eq_fim}.{info_trocas}"
            )
        else:
            resumo = (
                f"Progressão tática iniciando {com_preposicao(zona_inicial)} e avançando até "
                f"{ultima['zona_dest']}{eq_fim} ({n_acoes_bola} ações registradas).{info_trocas}"
            )
    else:
        resumo = "Nenhuma ação tática registrada no intervalo."

    cabecalho_confronto = (
        f"Confronto: {equipes_confronto[0]} x {equipes_confronto[1]} "
        "(zonas no referencial de quem executa a ação)\n"
        if len(equipes_confronto) == 2 else ""
    )
    bloco_avisos = ("\n\nAVISOS SEMÂNTICOS:\n" + "\n".join(avisos)) if avisos else ""

    relatorio_texto = (
        "======================================================================\n"
        "               RELATÓRIO TÁTICO DO LANCE (SAÍDA DO COMPILADOR)\n"
        "======================================================================\n"
        f"Tempo: {intervalo['inicio']} a {intervalo['fim']} (Duração: {duracao} segundos; "
        "horários por ação são estimados '~')\n"
        f"{cabecalho_confronto}\n"
        "SEQUÊNCIA DE AÇÕES TRADUZIDAS:\n"
        + "\n".join(linhas_acoes)
        + bloco_avisos
        + "\n\nRESUMO DA CONSTRUÇÃO:\n"
        + f"{resumo}\n"
        + "======================================================================"
    )

    return {
        "intervalo": intervalo,
        "confronto": equipes_confronto,
        "acoes": acoes_bola,
        "trocas_de_posse": trocas_de_posse,
        "equipes": equipes_participantes,
        "avisos": avisos,
        "resumo": resumo,
        "texto": relatorio_texto,
    }
