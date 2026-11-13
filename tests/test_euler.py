import math
import unittest
from fractions import Fraction
from metodos.euler import euler
from metodos.problema_pvi import pendiente, resolver
from metodos.validaciones import Parametros, PREDETERMINADOS, validar, ErrorValidacion


class EulerTests(unittest.TestCase):
    def setUp(self):
        self.p = validar(PREDETERMINADOS)
        self.r = euler(pendiente, self.p)

    def test_official_result(self):
        self.assertAlmostEqual(self.r["valor"], 1.7412776412776414, places=14)

    def test_first_iteration(self):
        r = self.r["traza"][0]
        self.assertEqual(r["k1"], -1.5)
        self.assertAlmostEqual(r["incremento"], -.15)
        self.assertEqual(r["y_siguiente"], 1.85)

    def test_second_iteration_fraction_reference(self):
        # Exact rational arithmetic, derived by hand from y1=37/20, x1=11/10.
        slope = Fraction(22, 37) - Fraction(37, 22)
        target = Fraction(37, 20) + slope / 10
        self.assertAlmostEqual(self.r["traza"][1]["k1"], float(slope), places=14)
        self.assertAlmostEqual(self.r["valor"], float(target), places=14)

    def test_number_of_steps_and_nodes(self):
        self.assertEqual(len(self.r["traza"]), 2)
        self.assertEqual(len(self.r["puntos"]), 3)
        self.assertEqual(self.r["puntos"][-1]["x"], 1.2)

    def test_constant_derivative_is_exact(self):
        r = euler(lambda x, y: 3, Parametros(1, 2, 2, .1, 10))
        self.assertAlmostEqual(r["valor"], 5, places=13)

    def test_linear_derivative_independent_sum(self):
        # Sum of n left rectangles for y'=x, over [1,2].
        r = euler(lambda x, y: x, Parametros(1, 2, 2, .1, 10))
        self.assertAlmostEqual(r["valor"], 3.45, places=13)

    def test_autonomous_geometric_reference(self):
        r = euler(lambda x, y: y, Parametros(0, 1, 1, .1, 10))
        self.assertAlmostEqual(r["valor"], 1.1**10, places=13)

    def test_first_order_convergence(self):
        errors = [resolver(dict(PREDETERMINADOS, h=h))["euler"]["errores"]["absoluto"] for h in (.025, .0125)]
        self.assertGreater(errors[0] / errors[1], 1.9)
        self.assertLess(errors[0] / errors[1], 2.2)

    def test_nonfinite_slope_rejected(self):
        with self.assertRaises(ErrorValidacion):
            euler(lambda x, y: math.inf, self.p)

    def test_no_intermediate_rounding(self):
        self.assertEqual(self.r["traza"][1]["y"], self.r["traza"][0]["y_siguiente"])
        self.assertNotEqual(self.r["valor"], round(self.r["valor"], 6))