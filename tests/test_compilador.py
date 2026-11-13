# -*- coding: utf-8 -*-
"""
Suíte de Testes Automatizados do Compilador Tático de Futebol.
Valida:
  1. Mapeamento Cartesiano das 11 Zonas do Campo StatsBomb (120x80);
  2. Classificação de Passes (Curto, Médio, Lançamento, Cruzamento);
  3. Análise Léxica e Sintática com PLY;
  4. Auto-Incorporação (Blocos aninhados recursivamente - Chomsky Tipo 2);
  5. Detecção de Erros Léxicos, Sintáticos e Semânticos.
"""

import unittest
from src.compilador import CompiladorTatico
from src.semantico import identificar_zona, calcular_distancia


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
            PASSE "Mateo Kovačić" (38.2, 42.1) -> "Ivan Perišić" (85.0, 18.5);
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
        self.assertEqual(a1["zona_dest"], "Meio-Campo Central")

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


if __name__ == "__main__":
    unittest.main()
