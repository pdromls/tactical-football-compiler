# -*- coding: utf-8 -*-
"""
Suíte de Testes Automatizados do Compilador Tático de Futebol.
Valida:
  1. Mapeamento Cartesiano das 11 Zonas do Campo StatsBomb (120x80);
  2. Classificação de Passes (Curto, Médio, Lançamento, Cruzamento);
  3. Análise Léxica e Sintática com PLY;
  4. Auto-Incorporação (Blocos aninhados recursivamente - Chomsky Tipo 2);
  5. Detecção de Erros Léxicos, Sintáticos e Semânticos;
  6. [NOVO] Elementos táticos recursivos (TABELA, TRIANGULACAO, CONTRA_ATAQUE);
  7. [NOVO] Ações atômicas recursivas (passe encadeado e finalização com rebote);
  8. [NOVO] Perspectiva de campo por equipe (ataque de um = defesa do outro).
"""

import sys
import unittest
from pathlib import Path

# [NOVO] Permite rodar os testes de qualquer diretório (inclusive de dentro de tests/)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.compilador import CompiladorTatico
from src.semantico import identificar_zona, espelhar, zona_para_adversario, classificar_passe, calcular_distancia

# [NOVO] Caminho absoluto: os testes funcionam de qualquer diretório
EXEMPLOS = Path(__file__).resolve().parent.parent / "exemplos"


class TestCompiladorTatico(unittest.TestCase):
    def setUp(self):
        self.compilador = CompiladorTatico()

    def test_11_zonas_do_campo(self):
        """Testa a delimitação cartesiana exata das 11 zonas táticas."""
        # Grandes Áreas (Prioridade Máxima)
        self.assertEqual(identificar_zona(110.0, 40.0), "Grande Área de Ataque")
        self.assertEqual(identificar_zona(10.0, 40.0), "Grande Área de Defesa")

        # Setor de Ataque (X >= 80)
        self.assertEqual(identificar_zona(90.0, 15.0), "Ataque Esquerdo")
        self.assertEqual(identificar_zona(90.0, 40.0), "Ataque Central")
        self.assertEqual(identificar_zona(90.0, 65.0), "Ataque Direito")

        # Setor de Meio-Campo (40 <= X < 80)
        self.assertEqual(identificar_zona(60.0, 10.0), "Meio-Campo Esquerdo")
        self.assertEqual(identificar_zona(60.0, 40.0), "Meio-Campo Central")
        self.assertEqual(identificar_zona(60.0, 70.0), "Meio-Campo Direito")

        # Setor de Defesa (X < 40, fora da grande área)
        self.assertEqual(identificar_zona(25.0, 10.0), "Defesa Esquerda")
        self.assertEqual(identificar_zona(25.0, 40.0), "Defesa Central")
        self.assertEqual(identificar_zona(25.0, 70.0), "Defesa Direita")

    def test_lance_padrao_croacia(self):
        """Testa a compilação e os atributos sintetizados do lance padrão da Croácia."""
        entrada = """
        LANCE [14:20 - 14:35] {
            PASSE "Luka Modrić" (25.4, 40.2) -> "Mateo Kovačić" (38.2, 42.1);
            PASSE "Mateo Kovačić" (38.2, 42.1) -> "Andrej Kramarić" (85.0, 18.5);
            FINALIZACAO "Andrej Kramarić" (108.5, 39.8) RESULTADO GOL;
        }
        """
        res = self.compilador.compilar_texto(entrada)
        self.assertEqual(res["intervalo"]["duracao_seg"], 15)
        self.assertEqual(len(res["acoes"]), 3)

        # Ação 1: Passe curto para frente
        a1 = res["acoes"][0]
        self.assertEqual(a1["autor"], "Luka Modrić")
        self.assertEqual(a1["classificacao"], "Passe curto")
        self.assertEqual(a1["zona_orig"], "Defesa Central")
        self.assertEqual(a1["zona_dest"], "Defesa Central")  # limiar unificado: X < 40 é Defesa

        # Ação 2: Lançamento longo para o ataque
        a2 = res["acoes"][1]
        self.assertEqual(a2["autor"], "Mateo Kovačić")
        self.assertEqual(a2["classificacao"], "Lançamento longo")
        self.assertEqual(a2["zona_dest"], "Ataque Esquerdo")

        # Ação 3: Finalização na Grande Área de Ataque com GOL
        a3 = res["acoes"][2]
        self.assertEqual(a3["tipo_acao"], "FINALIZACAO")
        self.assertEqual(a3["zona_orig"], "Grande Área de Ataque")
        self.assertEqual(a3["desfecho"], "GOL!")

    def test_auto_incorporacao_e_cruzamento(self):
        """Testa blocos recursivamente aninhados (Chomsky Tipo 2) e regra de Cruzamento."""
        entrada = """
        LANCE [50:00 - 50:10] {
            {
                PASSE "Luka Modrić" (60.0, 40.0) -> "Ivan Perišić" (95.0, 10.0);
                {
                    PASSE "Ivan Perišić" (95.0, 10.0) -> "Andrej Kramarić" (110.0, 40.0);
                }
            }
            FINALIZACAO "Andrej Kramarić" (110.0, 40.0) RESULTADO DEFESA;
        }
        """
        res = self.compilador.compilar_texto(entrada)
        self.assertEqual(len(res["acoes"]), 3)
        cruzamento = res["acoes"][1]
        self.assertEqual(cruzamento["classificacao"], "Cruzamento")
        self.assertEqual(cruzamento["zona_orig"], "Ataque Esquerdo")
        self.assertEqual(cruzamento["zona_dest"], "Grande Área de Ataque")

    def test_erro_sintatico_chaves_desbalanceadas(self):
        """Garante que chaves desbalanceadas disparam SyntaxError no parser LALR."""
        entrada_invalida = """
        LANCE [14:20 - 14:35] {
            PASSE "Luka Modrić" (25.4, 40.2) -> "Mateo Kovačić" (38.2, 42.1);
        """
        with self.assertRaises(SyntaxError):
            self.compilador.compilar_texto(entrada_invalida)

    def test_erro_semantico_coordenada_fora_do_campo(self):
        """Garante que coordenadas fora do limite 120x80 disparam ValueError."""
        entrada_invalida = """
        LANCE [14:20 - 14:35] {
            PASSE "Luka Modrić" (150.0, 40.2) -> "Mateo Kovačić" (38.2, 42.1);
        }
        """
        with self.assertRaises(ValueError):
            self.compilador.compilar_texto(entrada_invalida)

    # ------------------------------------------------------------------
    # [NOVO] Testes da correção: recursividade e perspectiva por equipe
    # ------------------------------------------------------------------

    def test_passe_encadeado_recursivo(self):
        """PASSE A -> B -> C gera 2 passes; o 2º sai de B (atributo herdado/sintetizado)."""
        res = self.compilador.compilar_texto(
            'LANCE [1:00 - 1:10] { PASSE "A" (30, 40) -> "B" (45, 40) -> "C" (70, 30); }'
        )
        a1, a2 = res["acoes"]
        self.assertEqual((a1["autor"], a1["receptor"]), ("A", "B"))
        self.assertEqual((a2["autor"], a2["receptor"]), ("B", "C"))
        self.assertEqual(a2["coord_orig"], (45.0, 40.0))

    def test_finalizacao_com_rebote_recursivo(self):
        """Finalização com rebote (recursão à direita) numera as tentativas."""
        res = self.compilador.compilar_texto(
            'LANCE [1:00 - 1:10] { FINALIZACAO "A" (105, 40) RESULTADO DEFESA REBOTE '
            'FINALIZACAO "B" (110, 38) RESULTADO TRAVE REBOTE '
            'FINALIZACAO "C" (112, 40) RESULTADO GOL; }'
        )
        self.assertEqual([a["tentativa"] for a in res["acoes"]], [1, 2, 3])
        self.assertEqual(res["acoes"][-1]["desfecho"], "GOL!")

    def test_jogadas_recursivas_aninhadas(self):
        """TABELA dentro de CONTRA_ATAQUE: rótulo hierárquico e validação em cada nível."""
        res = self.compilador.compilar_arquivo(EXEMPLOS / "lance_recursivo.txt")
        self.assertIn("Tabela", res["acoes"][2]["jogada"])
        self.assertTrue(res["acoes"][2]["jogada"].startswith("Contra-ataque"))

    def test_erros_semanticos_das_jogadas(self):
        casos = [
            'TABELA "A" "B" { PASSE "A" (50, 40) -> "C" (60, 40); }',
            'TRIANGULACAO { PASSE "A" (50, 40) -> "B" (60, 40) -> "C" (70, 40) -> "D" (75, 40); }',
            'CONTRA_ATAQUE { PASSE "A" (50, 40) -> "B" (60, 40); }',
        ]
        for corpo in casos:
            with self.assertRaises(ValueError):
                self.compilador.compilar_texto(f"LANCE [1:00 - 1:10] {{ {corpo} }}")

    def test_perspectiva_por_equipe(self):
        """O mesmo ponto físico é Ataque para um time e Defesa para o outro."""
        self.assertEqual(espelhar((85.0, 18.5)), (35.0, 61.5))
        self.assertEqual(identificar_zona(85.0, 18.5), "Ataque Esquerdo")
        self.assertEqual(zona_para_adversario((85.0, 18.5)), "Defesa Direita")
        self.assertEqual(zona_para_adversario((110.0, 40.0)), "Grande Área de Defesa")

    def test_confronto_e_troca_de_posse(self):
        res = self.compilador.compilar_arquivo(EXEMPLOS / "lance_troca_posse.txt")
        self.assertEqual(res["confronto"], ["Croatia", "Brazil"])
        self.assertEqual(res["trocas_de_posse"], 1)
        brasil = [a for a in res["acoes"] if a["equipe"] == "Brazil"][0]
        self.assertEqual(brasil["adversario"], "Croatia")
        self.assertIn("Defesa Esquerda (Brazil) = Ataque Direito (Croatia)", res["texto"])

    def test_equipe_fora_do_confronto(self):
        with self.assertRaises(ValueError):
            self.compilador.compilar_texto(
                'LANCE [1:00 - 1:10] "Croatia" VS "Brazil" { POSSE "Argentina" { '
                'PASSE "A" (50, 40) -> "B" (60, 40); } }'
            )

    def test_cruzamento_exige_origem_no_ataque(self):
        """Correção do bug: passe longo da Defesa Esquerda não é cruzamento."""
        c1, c2 = (10.0, 5.0), (105.0, 40.0)
        tipo, _ = classificar_passe(calcular_distancia(c1, c2), c1, c2,
                                    identificar_zona(*c1), identificar_zona(*c2))
        self.assertEqual(tipo, "Lançamento longo")

    def test_aviso_de_continuidade(self):
        res = self.compilador.compilar_texto(
            'LANCE [1:00 - 1:10] { PASSE "A" (30, 40) -> "B" (45, 40); '
            'FINALIZACAO "C" (108, 40) RESULTADO FORA; }'
        )
        self.assertEqual(len(res["avisos"]), 1)

    # ------------------------------------------------------------------
    # [NOVO] Revisão de 13/11: verificações semânticas adicionais
    # ------------------------------------------------------------------

    def test_segundos_invalidos(self):
        with self.assertRaises(ValueError):
            self.compilador.compilar_texto('LANCE [14:75 - 14:80] { PASSE "A" (30, 40) -> "B" (45, 40); }')

    def test_tabela_exige_jogadores_diferentes(self):
        with self.assertRaises(ValueError):
            self.compilador.compilar_texto(
                'LANCE [1:00 - 1:10] { TABELA "A" "A" { PASSE "A" (50, 40) -> "A" (55, 40) -> "A" (60, 40); } }'
            )

    def test_jogada_nao_atravessa_troca_de_posse(self):
        """CONTRA_ATAQUE não pode misturar referenciais de dois times."""
        with self.assertRaises(ValueError):
            self.compilador.compilar_texto(
                'LANCE [1:00 - 1:10] "X" VS "Y" { CONTRA_ATAQUE { '
                'POSSE "X" { PASSE "A" (20, 40) -> "B" (90, 40); } TROCA_POSSE "Y"; '
                'POSSE "Y" { PASSE "C" (30, 40) -> "D" (70, 40); } } }'
            )

    def test_troca_de_posse_inconsistente(self):
        """Depois de TROCA_POSSE "Y", a próxima ação tem de ser de Y."""
        with self.assertRaises(ValueError):
            self.compilador.compilar_texto(
                'LANCE [1:00 - 1:10] "X" VS "Y" { POSSE "X" { PASSE "A" (20, 40) -> "B" (60, 40); } '
                'TROCA_POSSE "Y"; POSSE "X" { PASSE "B" (60, 40) -> "C" (70, 40); } }'
            )


if __name__ == "__main__":
    unittest.main()
