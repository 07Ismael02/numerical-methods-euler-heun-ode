import unittest
from decimal import Decimal, localcontext
from metodos.heun import heun
from metodos.problema_pvi import pendiente, resolver
from metodos.validaciones import PREDETERMINADOS, Parametros, validar, ErrorValidacion


class HeunTests(unittest.TestCase):
    def setUp(self):
        self.r = heun(pendiente, validar(PREDETERMINADOS))

    def test_official_result(self):
        self.assertAlmostEqual(self.r["valor"], 1.775806670950786, places=14)

    def test_predictors(self):
        self.assertAlmostEqual(self.r["traza"][0]["predictor"], 1.85, places=14)
        self.assertAlmostEqual(self.r["traza"][1]["predictor"], 1.759384187290956, places=14)

    def test_correctors(self):
        self.assertAlmostEqual(self.r["traza"][0]["y_siguiente"], 1.8706388206388207, places=14)
        self.assertAlmostEqual(self.r["traza"][1]["y_siguiente"], 1.775806670950786, places=14)

    def test_final_slopes(self):
        self.assertAlmostEqual(self.r["traza"][0]["k2"], -1.087223587223587, places=14)
        self.assertAlmostEqual(self.r["traza"][1]["k2"], -.7840966602820462, places=14)

    def test_high_precision_decimal_reference(self):
        with localcontext() as ctx:
            ctx.prec = 60
            x, y, h = Decimal(1), Decimal(2), Decimal("0.1")
            for _ in range(2):
                a = x / y - y / x
                z = y + h * a
                b = (x + h) / z - z / (x + h)
                y += h * (a + b) / 2
                x += h
            self.assertAlmostEqual(self.r["valor"], float(y), places=14)

    def test_two_steps_three_nodes(self):
        self.assertEqual(len(self.r["traza"]), 2)
        self.assertEqual(len(self.r["puntos"]), 3)

    def test_linear_derivative_exact_integral(self):
        r = heun(lambda x, y: x, Parametros(1, 2, 2, .1, 10))
        self.assertAlmostEqual(r["valor"], 3.5, places=13)

    def test_autonomous_stability_polynomial(self):
        r = heun(lambda x, y: y, Parametros(0, 1, 1, .1, 10))
        self.assertAlmostEqual(r["valor"], (1 + .1 + .1**2 / 2)**10, places=13)

    def test_distinguishes_midpoint_method(self):
        # y'=y², one step: Heun=1.1105 whereas midpoint=1.11025.
        r = heun(lambda x, y: y*y, Parametros(0, 1, .1, .1, 1))
        self.assertAlmostEqual(r["valor"], 1.1105, places=14)
        self.assertGreater(abs(r["valor"] - 1.11025), .0002)

    def test_second_order_convergence(self):
        errors = [resolver(dict(PREDETERMINADOS, h=h))["heun"]["errores"]["absoluto"] for h in (.025, .0125)]
        self.assertGreater(errors[0] / errors[1], 3.8)
        self.assertLess(errors[0] / errors[1], 4.4)

    def test_zero_predictor_rejected(self):
        with self.assertRaises(ErrorValidacion):
            heun(pendiente, Parametros(1, 2, 1 + 4/3, 4/3, 1))

    def test_corrected_value_used_next(self):
        self.assertEqual(self.r["traza"][1]["y"], self.r["traza"][0]["y_siguiente"])