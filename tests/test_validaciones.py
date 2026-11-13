import unittest
from metodos.validaciones import validar, PREDETERMINADOS, ErrorValidacion
from metodos.problema_pvi import resolver


class ValidationTests(unittest.TestCase):
    def bad(self, **kwargs):
        with self.assertRaises(ErrorValidacion):
            validar(dict(PREDETERMINADOS, **kwargs))

    def test_zero_step(self): self.bad(h=0)
    def test_negative_step(self): self.bad(h=-.1)
    def test_backward_interval(self): self.bad(x_final=.5)
    def test_empty_interval(self): self.bad(x_final=1)
    def test_noninteger_steps(self): self.bad(h=.03)
    def test_zero_x(self): self.bad(x0=0)
    def test_zero_y(self): self.bad(y0=0)
    def test_crosses_zero_x(self): self.bad(x0=-1)
    def test_too_many_steps(self): self.bad(h=1e-9)
    def test_step_exceeds_interval(self): self.bad(h=1)

    def test_booleans_rejected_every_field(self):
        for key in PREDETERMINADOS:
            with self.subTest(key=key): self.bad(**{key: True})

    def test_nonfinite_every_field(self):
        for key in PREDETERMINADOS:
            for value in (float("nan"), float("inf"), float("-inf")):
                with self.subTest(key=key, value=value): self.bad(**{key: value})

    def test_wrong_types(self):
        for value in ("1", None, [], {}):
            with self.subTest(value=value): self.bad(y0=value)

    def test_payload_shape(self):
        for payload in ([], None, {}, dict(PREDETERMINADOS, extra=1)):
            with self.subTest(payload=payload), self.assertRaises(ErrorValidacion): validar(payload)

    def test_float_step_tolerance(self):
        self.assertEqual(validar(PREDETERMINADOS).pasos, 2)

    def test_overflow_constant(self):
        with self.assertRaises(ErrorValidacion): resolver(dict(PREDETERMINADOS, y0=1e300))

    def test_underflow_scale(self):
        with self.assertRaises(ErrorValidacion):
            resolver({"x0": 1e-200, "y0": 2, "x_final": 2e-200, "h": 1e-200})

    def test_huge_integer(self): self.bad(y0=10**500)

    def test_maximum_grid(self):
        p = validar(dict(PREDETERMINADOS, x_final=2, h=.0001))
        self.assertEqual(p.pasos, 10000)