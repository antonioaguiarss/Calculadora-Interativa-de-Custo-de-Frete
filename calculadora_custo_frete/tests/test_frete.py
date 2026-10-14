import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from frete import calcular_frete, carregar_regras

class TestCalculadoraFrete(unittest.TestCase):
    def setUp(self):
        self.regras = carregar_regras()

    def test_resultado_positivo(self):
        r = calcular_frete(500, 350, "Rodoviário", "Geral", regras=self.regras)
        self.assertGreater(r["total_estimado_brl"], 0)

    def test_peso_taxavel_considera_cubagem(self):
        r = calcular_frete(100, 10, "Rodoviário", "Geral", volume_m3=2, regras=self.regras)
        self.assertEqual(r["peso_taxavel_kg"], 400)

    def test_desconto_reduz_total(self):
        sem = calcular_frete(1000, 500, "Rodoviário", "Geral", desconto_pct=0, regras=self.regras)
        com = calcular_frete(1000, 500, "Rodoviário", "Geral", desconto_pct=10, regras=self.regras)
        self.assertLess(com["total_estimado_brl"], sem["total_estimado_brl"])

    def test_peso_invalido(self):
        with self.assertRaises(ValueError):
            calcular_frete(0, 100, "Rodoviário", "Geral", regras=self.regras)

    def test_modal_carga_sem_regra(self):
        with self.assertRaises(ValueError):
            calcular_frete(100, 100, "Modal inexistente", "Geral", regras=self.regras)

if __name__ == "__main__":
    unittest.main()
