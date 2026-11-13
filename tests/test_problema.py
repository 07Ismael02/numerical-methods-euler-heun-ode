import math
import unittest
from decimal import Decimal, localcontext
from metodos.problema_pvi import constante, exacta, pendiente, resolver
from metodos.validaciones import PREDETERMINADOS, ErrorValidacion


class ProblemaTests(unittest.TestCase):
    def setUp(self):
        self.r = resolver(PREDETERMINADOS)

    def test_exact_value_decimal_reference(self):
        with localcontext() as ctx:
            ctx.prec = 60
            x = Decimal("1.2")
            expected = (x*x/2 + Decimal("3.5")/(x*x)).sqrt()
            self.assertAlmostEqual(self.r["valor_exacto"], float(expected), places=14)

    def test_constant(self):
        self.assertEqual(self.r["constante"], 3.5)

    def test_absolute_errors(self):
        self.assertAlmostEqual(self.r["euler"]["errores"]["absoluto"], .0337027967992283, places=14)
        self.assertAlmostEqual(self.r["heun"]["errores"]["absoluto"], .0008262328739163, places=14)

    def test_relative_errors(self):
        self.assertAlmostEqual(self.r["euler"]["errores"]["relativo_porcentual"], 1.8987700414177011, places=12)
        self.assertAlmostEqual(self.r["heun"]["errores"]["relativo_porcentual"], .04654884393044697, places=12)

    def test_recalculates_constant(self):
        r = resolver(dict(PREDETERMINADOS, y0=3))
        self.assertEqual(r["constante"], 8.5)
        self.assertAlmostEqual(r["valor_exacto"], math.sqrt(.72 + 8.5 / 1.44), places=14)

    def test_negative_initial_condition_symmetry(self):
        r = resolver(dict(PREDETERMINADOS, y0=-2))
        self.assertEqual(r["valor_exacto"], -self.r["valor_exacto"])
        for method in ("euler", "heun"):
            self.assertEqual(r[method]["valor"], -self.r[method]["valor"])
            self.assertEqual(r[method]["errores"], self.r[method]["errores"])

    def test_negative_x_interval(self):
        r = resolver({"x0": -1.2, "y0": -2, "x_final": -1, "h": .1})
        self.assertLess(r["heun"]["valor"], 0)
        self.assertLess(r["valor_exacto"], 0)

    def test_exact_initial_value(self):
        for x, y in ((1, 2), (2, -3), (-2, 3)):
            self.assertAlmostEqual(exacta(x, constante(x, y), y), y)

    def test_analytic_derivative_matches_ode(self):
        # Centered finite differences of the independent analytic reference.
        for x in (1, 1.1, 1.2):
            h = 1e-5
            dy = (exacta(x+h, 3.5) - exacta(x-h, 3.5)) / (2*h)
            self.assertAlmostEqual(dy, pendiente(x, exacta(x, 3.5)), places=8)

    def test_exact_conserved_quantity(self):
        for point in self.r["grafica"]["exacta"]:
            x, y = point["x"], point["y"]
            self.assertAlmostEqual(x*x*y*y - x**4/2, 3.5, places=12)

    def test_nonreal_interval_rejected(self):
        with self.assertRaises(ErrorValidacion):
            resolver({"x0": -2, "y0": .5, "x_final": -1, "h": .1})

    def test_endpoint_zero_exact_rejected(self):
        with self.assertRaises(ErrorValidacion):
            exacta(1, -.5)

    def test_numerical_crossing_rejected(self):
        with self.assertRaisesRegex(ErrorValidacion, "Reduce h"):
            resolver(dict(PREDETERMINADOS, x_final=3, h=2))

    def test_true_domain_division_by_zero(self):
        for x, y in ((0, 2), (1, 0)):
            with self.assertRaises(ErrorValidacion):
                pendiente(x, y)

    def test_heun_more_precise_official(self):
        self.assertEqual(self.r["mas_preciso"], "Heun")

    def test_graph_endpoints(self):
        self.assertEqual(len(self.r["grafica"]["exacta"]), 301)
        self.assertEqual(self.r["grafica"]["exacta"][0], {"x": 1, "y": 2})
        self.assertAlmostEqual(self.r["grafica"]["exacta"][-1]["y"], self.r["valor_exacto"])

    def test_zero_constant_branch(self):
        self.assertAlmostEqual(exacta(2, 0), math.sqrt(2), places=14)
        self.assertAlmostEqual(exacta(2, 0, -1), -math.sqrt(2), places=14)

    def test_full_maximum_grid_calculation(self):
        r = resolver(dict(PREDETERMINADOS, x_final=2, h=.0001))
        self.assertEqual(len(r["euler"]["traza"]), 10000)
        self.assertEqual(len(r["heun"]["puntos"]), 10001)
        self.assertLess(r["heun"]["errores"]["absoluto"], 1e-7)