# -*- coding: utf-8 -*-
"""
[NOVO] Script auxiliar da documentação (não faz parte do compilador).
Gera as figuras das árvores de derivação anotadas (estilo quadro da professora)
para a gramática ATUAL (31 produções). Os valores das anotações são calculados
com as próprias funções de src/semantico.py, para nunca divergirem do compilador.

Uso (na raiz do projeto):
    python docs/gerar_arvores.py
Saídas:
    docs/arvore_estilo_professora.png   (Passe simples + Finalização)
    docs/arvore_recursiva.png           (TABELA + passe encadeado + rebote)
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.semantico import identificar_zona, calcular_distancia, classificar_passe  # noqa: E402
from src.compilador import CompiladorTatico  # noqa: E402

COR_NT = "#1f4e79"
COR_ANOT = "#0b5d3b"
COR_ORDEM = "#b22222"


class No:
    def __init__(self, rotulo, filhos=None, regra=None, anot=None, lexval=None, terminal=False):
        self.rotulo = rotulo
        self.filhos = filhos or []
        self.regra = regra
        self.anot = anot
        self.lexval = lexval
        self.terminal = terminal
        self.ordem = None
        self.x = self.y = 0.0


def T(rotulo, lexval=None):
    return No(rotulo, lexval=lexval, terminal=True)


def N(rotulo, regra, anot, *filhos):
    return No(rotulo, list(filhos), regra=regra, anot=anot)


def coord(x, y, nome="<Coordenada>", resumida=False, anot=None):
    anot = anot or f"val=({x:g}, {y:g})"
    if resumida:
        return N(nome, 27, anot, T(f"( {x:g} , {y:g} )"))
    return N(nome, 27, anot, T("("), T("NUM", f"{x:g}"), T(","), T("NUM", f"{y:g}"), T(")"))


def info_passe(c1, c2):
    d = calcular_distancia(c1, c2)
    z1, z2 = identificar_zona(*c1), identificar_zona(*c2)
    tipo, direc = classificar_passe(d, c1, c2, z1, z2)
    return d, z1, z2, tipo, direc


# ----------------------------------------------------------------------------
# Layout e desenho
# ----------------------------------------------------------------------------

def numerar_pos_ordem(no, cont=None):
    cont = cont if cont is not None else [0]
    for f in no.filhos:
        numerar_pos_ordem(f, cont)
    if not no.terminal:
        cont[0] += 1
        no.ordem = cont[0]
    return cont[0]


def medidas(no):
    """(largura do rótulo, largura da anotação à direita) em unidades do eixo x."""
    anot = max((len(l) for l in (no.anot or "").split("\n")), default=0)
    return len(no.rotulo) * 0.18 + 0.4, anot * 0.13 + 0.6


def largura_subarvore(no):
    if no.terminal:
        texto = max(no.rotulo, no.lexval or "", key=len)
        no.larg = max(1.1, len(texto) * 0.17 + 0.4)
        return no.larg
    no.soma = sum(largura_subarvore(f) for f in no.filhos)
    rot, anot = medidas(no)
    # O nó fica centralizado sobre os filhos e a anotação ocupa só o lado DIREITO.
    no.recuo = max(0.0, rot / 2 - no.soma / 2)
    no.larg = max(no.soma + no.recuo, no.recuo + no.soma / 2 + rot / 2 + anot)
    return no.larg


def posicionar(no, x0, prof):
    no.y = -prof
    if not no.filhos:
        no.x = x0 + no.larg / 2
        return
    x = x0 + no.recuo
    for f in no.filhos:
        posicionar(f, x, prof + 1)
        x += f.larg
    no.x = (no.filhos[0].x + no.filhos[-1].x) / 2


def layout(no):
    largura_subarvore(no)
    posicionar(no, 0.0, 0)
    return no.larg


def profundidade(no):
    return 1 + max((profundidade(f) for f in no.filhos), default=0)


def desenhar(no, ax, esc_x, esc_y):
    px, py = no.x * esc_x, no.y * esc_y
    for f in no.filhos:
        ax.plot([px, f.x * esc_x], [py - 0.18, f.y * esc_y + 0.18], color="#222", lw=1.0, zorder=1)
        desenhar(f, ax, esc_x, esc_y)
    if no.terminal:
        ax.text(px, py, no.rotulo, ha="center", va="center", fontsize=9, fontweight="bold", zorder=3)
        if no.lexval is not None:
            ax.plot([px, px], [py - 0.2, py - 0.55], ls="--", color="#222", lw=1.0)
            ax.text(px, py - 0.72, f'"{no.lexval}"' if not no.lexval.replace(".", "").isdigit() else no.lexval,
                    ha="center", va="center", fontsize=8, style="italic")
    else:
        ax.text(px, py, no.rotulo, ha="center", va="center", fontsize=9.5, fontweight="bold", zorder=3,
                bbox=dict(boxstyle="round,pad=0.35", fc="#fffdf5", ec=COR_NT, lw=1.6))
        ax.text(px - 0.42 * esc_x, py + 0.32, str(no.ordem), ha="center", va="center", fontsize=8,
                color="white", fontweight="bold", zorder=4,
                bbox=dict(boxstyle="square,pad=0.2", fc=COR_ORDEM, ec=COR_ORDEM))
        if no.anot:
            meia_larg = len(no.rotulo) * 0.085 * esc_x + 0.3
            ax.text(px + meia_larg, py + 0.05, no.anot, ha="left", va="center", fontsize=7.5,
                    color=COR_ANOT, fontweight="bold", zorder=3,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))


def passos(no, saida=None):
    saida = saida if saida is not None else []
    for f in no.filhos:
        passos(f, saida)
    if not no.terminal:
        anot = (no.anot or "").replace("\n", " | ")
        saida.append(f"{no.ordem:2d}: [#{no.regra:<2}] {no.rotulo:<20} => {anot}")
    return saida


def gerar(raiz, sentenca, titulo, arquivo, saida_compilador=None, nota=None):
    numerar_pos_ordem(raiz)
    n_folhas = layout(raiz)
    prof = profundidade(raiz)
    esc_x, esc_y = 1.0, 1.55
    lista_passos = passos(raiz)

    larg = max(16, n_folhas * esc_x * 0.52)
    alt_arvore = prof * esc_y * 0.62 + 2
    alt_painel = 0.19 * len(lista_passos) + 1.2
    fig = plt.figure(figsize=(larg, alt_arvore + alt_painel))
    frac = alt_arvore / (alt_arvore + alt_painel)
    ax = fig.add_axes([0.01, 1 - frac, 0.98, frac - 0.06])
    ax.axis("off")
    desenhar(raiz, ax, esc_x, esc_y)
    ax.set_xlim(-1, n_folhas * esc_x)
    ax.set_ylim(-prof * esc_y - 0.5, 0.8)

    fig.text(0.5, 0.995, titulo, ha="center", va="top", fontsize=15, fontweight="bold")
    fig.text(0.5, 0.995 - 0.35 / (alt_arvore + alt_painel), "Sentença de entrada:  " + sentenca,
             ha="center", va="top", fontsize=10.5, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.4", fc="#eef3fa", ec=COR_NT))

    cab = "PASSO A PASSO DAS REGRAS SEMÂNTICAS (pós-ordem, [#n] = produção da Tabela SDT):"
    texto_passos = cab + "\n" + "\n".join(lista_passos)
    if nota:
        texto_passos += "\n\n" + nota
    fig.text(0.015, (alt_painel - 0.2) / (alt_arvore + alt_painel), texto_passos, ha="left", va="top",
             family="monospace", fontsize=8.5,
             bbox=dict(boxstyle="round,pad=0.5", fc="#f7f9fb", ec=COR_NT))
    if saida_compilador:
        fig.text(0.985, (alt_painel - 0.2) / (alt_arvore + alt_painel), saida_compilador, ha="right", va="top",
                 family="monospace", fontsize=8, multialignment="left",
                 bbox=dict(boxstyle="round,pad=0.5", fc="#eef7ee", ec=COR_ANOT))
    fig.savefig(arquivo, dpi=130)
    plt.close(fig)
    print("gerado:", arquivo)


# ----------------------------------------------------------------------------
# Figura 1: estilo do quadro da professora
# ----------------------------------------------------------------------------

def figura_professora():
    c1, c2, c3 = (25.0, 40.0), (108.0, 40.0), (108.0, 40.0)
    d, z1, z2, tipo, direc = info_passe(c1, c2)
    z3 = identificar_zona(*c3)
    raiz = N("<Lance>", 1, "Lance.relatorio = gerar_relatorio(...)",
        T("LANCE"),
        N("<IntervaloTempo>", 4, "val=(14:20, 14:35, 15s)",
          T("["), T("TEMPO", "14:20"), T("-"), T("TEMPO", "14:35"), T("]")),
        N("<Confronto>", 3, "val=None", T("ε")),
        N("<Bloco>", 5, "Bloco.lista=[P1, F1]",
          T("{"),
          N("<SequenciaAcoes>", 8, "S2.lista = S1.lista + E2.lista",
            N("<SequenciaAcoes>₁", 9, "S1.lista=[P1]",
              N("<ElementoTatico>", 10, "E1.lista=[P1]",
                N("<AcaoAtomica>", 16, "A1.lista=[P1]",
                  N("<Passe>", 20, "lista=Cadeia.passes=[P1]",
                    T("PASSE"), T("JOGADOR", "Modrić"),
                    coord(*c1, nome="<Coordenada>₁", anot="C1=(25, 40)"),
                    N("<CadeiaPasse>", 21,
                      f"herda autor=Modrić, orig=C1\nP1: {tipo} ({d:.1f}m)\n{z1} -> {z2}",
                      T("SETA", "->"), T("JOGADOR", "Kramarić"),
                      coord(*c2, nome="<Coordenada>₂", anot="C2=(108, 40)"))),
                  T(";")))),
            N("<ElementoTatico>", 10, "E2.lista=[F1]",
              N("<AcaoAtomica>", 17, "A2.lista=[F1]",
                N("<Finalizacao>", 23, f"F1: {z3}, GOL!",
                  T("FINALIZACAO"), T("JOGADOR", "Kramarić"),
                  coord(*c3, anot="C3=(108, 40)"),
                  T("RESULTADO"),
                  N("<Desfecho>", 28, 'val="GOL!"', T("GOL"))),
                T(";")))),
          T("}")))
    sentenca = 'LANCE [ 14:20 - 14:35 ] { PASSE "Modrić" (25, 40) -> "Kramarić" (108, 40) ; FINALIZACAO "Kramarić" (108, 40) RESULTADO GOL ; }'
    res = CompiladorTatico().compilar_texto(sentenca.replace("[ ", "[").replace(" ]", "]"))
    saida = "SAÍDA FINAL DO COMPILADOR (atributo sintetizado na raiz):\n" + res["texto"]
    nota = ("Atributo HERDADO: em <CadeiaPasse> (#21) o autor (JOGADOR) e a origem (C1)\n"
            "vêm dos irmãos à esquerda, lidos na pilha do PLY como p[-2] e p[-1].")
    gerar(raiz, sentenca, "ÁRVORE DE DERIVAÇÃO ANOTADA E EXECUÇÃO SEMÂNTICA (SDT)",
          RAIZ / "docs" / "arvore_estilo_professora.png", saida, nota)


# ----------------------------------------------------------------------------
# Figura 2: recursividade (TABELA + passe encadeado + rebote)
# ----------------------------------------------------------------------------

def figura_recursiva():
    a, b, c = (50.0, 40.0), (60.0, 46.0), (72.0, 38.0)
    d1, *_r1 = info_passe(a, b)
    d2, *_r2 = info_passe(b, c)
    s1, s2 = (105.0, 40.0), (110.0, 36.0)
    raiz = N("<Lance>", 1, "Lance.relatorio",
        T("LANCE"),
        N("<IntervaloTempo>", 4, "(10:00, 10:12, 12s)",
          T("["), T("TEMPO", "10:00"), T("-"), T("TEMPO", "10:12"), T("]")),
        N("<Confronto>", 3, "None", T("ε")),
        N("<Bloco>", 5, "[P1, P2, F1, F2]",
          T("{"),
          N("<SequenciaAcoes>", 8, "S.lista = S₁ + E₂",
            N("<SequenciaAcoes>₁", 9, "[P1, P2]",
              N("<ElementoTatico>", 12, "[P1, P2]",
                N("<Jogada>", 13, "valida Modrić->Kovačić,\nKovačić->Modrić; rótulo Tabela",
                  T("TABELA"), T("JOGADOR", "Modrić"), T("JOGADOR", "Kovačić"), T("{"),
                  N("<SequenciaAcoes>", 9, "[P1, P2]",
                    N("<ElementoTatico>", 10, "[P1, P2]",
                      N("<AcaoAtomica>", 16, "[P1, P2]",
                        N("<Passe>", 20, "[P1, P2]",
                          T("PASSE"), T("JOGADOR", "Modrić"),
                          coord(*a, resumida=True),
                          N("<CadeiaPasse>", 22, f"P2: Kovačić->Modrić {d2:.1f}m\npasses=[P1, P2]",
                            N("<CadeiaPasse>₁", 21, f"herda Modrić,(50,40)\nP1: ->Kovačić {d1:.1f}m",
                              T("SETA"), T("JOGADOR", "Kovačić"), coord(*b, resumida=True)),
                            T("SETA"), T("JOGADOR", "Modrić"), coord(*c, resumida=True))),
                        T(";")))),
                  T("}")))),
            N("<ElementoTatico>", 10, "[F1, F2]",
              N("<AcaoAtomica>", 17, "[F1, F2]",
                N("<Finalizacao>", 24, "[F1(tent.1), F2(tent.2)]",
                  T("FINALIZACAO"), T("JOGADOR", "Modrić"), coord(*s1, resumida=True),
                  T("RESULTADO"),
                  N("<DesfechoParcial>", 25, '"DEFESA DO GOLEIRO!"', T("DEFESA")),
                  T("REBOTE"),
                  N("<Finalizacao>₁", 23, f"[F2] {identificar_zona(*s2)}, GOL!",
                    T("FINALIZACAO"), T("JOGADOR", "Kramarić"), coord(*s2, resumida=True),
                    T("RESULTADO"), N("<Desfecho>", 28, '"GOL!"', T("GOL")))),
                T(";")))),
          T("}")))
    sentenca = ('LANCE [10:00 - 10:12] { TABELA "Modrić" "Kovačić" { PASSE "Modrić" (50, 40) -> "Kovačić" (60, 46) '
                '-> "Modrić" (72, 38) ; } FINALIZACAO "Modrić" (105, 40) RESULTADO DEFESA REBOTE '
                'FINALIZACAO "Kramarić" (110, 36) RESULTADO GOL ; }')
    CompiladorTatico().compilar_texto(sentenca)  # garante que a sentença é aceita
    nota = ("Subárvores de <Coordenada> (#27) resumidas como '( x , y )' para caber na figura.\n"
            "Recursão: <Jogada> contém <SequenciaAcoes> (auto-incorporação); <CadeiaPasse> é recursiva\n"
            "à ESQUERDA (#22); <Finalizacao> é recursiva à DIREITA via REBOTE (#24).")
    gerar(raiz, sentenca, "ÁRVORE ANOTADA COM ELEMENTO TÁTICO E AÇÕES ATÔMICAS RECURSIVAS",
          RAIZ / "docs" / "arvore_recursiva.png", None, nota)


if __name__ == "__main__":
    figura_professora()
    figura_recursiva()
