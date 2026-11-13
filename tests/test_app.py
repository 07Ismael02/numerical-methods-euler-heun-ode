import json
import unittest
from backend.app import create_app
from metodos.validaciones import PREDETERMINADOS


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()

    def test_index(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Una ecuación.", r.get_data(as_text=True))

    def test_valid_request(self):
        r = self.client.post("/api/resolver", json=PREDETERMINADOS)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json["estado"], "ok")
        self.assertAlmostEqual(r.json["heun"]["valor"], 1.775806670950786)
        json.dumps(r.json, allow_nan=False)

    def test_invalid_request(self):
        r = self.client.post("/api/resolver", json=dict(PREDETERMINADOS, h=0))
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json["estado"], "error")

    def test_negative_condition(self):
        r = self.client.post("/api/resolver", json=dict(PREDETERMINADOS, y0=-2))
        self.assertEqual(r.status_code, 200)
        self.assertLess(r.json["valor_exacto"], 0)

    def test_malformed_json(self):
        r = self.client.post("/api/resolver", data="{broken", content_type="application/json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json["estado"], "error")

    def test_json_null(self):
        r = self.client.post("/api/resolver", data="null", content_type="application/json")
        self.assertEqual(r.status_code, 400)

    def test_wrong_content_type(self):
        r = self.client.post("/api/resolver", data="x0=1")
        self.assertEqual(r.status_code, 415)
        self.assertTrue(r.is_json)

    def test_wrong_method(self):
        r = self.client.get("/api/resolver")
        self.assertEqual(r.status_code, 405)
        self.assertTrue(r.is_json)

    def test_css(self):
        r = self.client.get("/static/css/styles.css")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/css", r.content_type)
        r.close()

    def test_javascript(self):
        r = self.client.get("/static/js/app.js")
        self.assertEqual(r.status_code, 200)
        self.assertIn("javascript", r.content_type)
        r.close()

    def test_health(self):
        self.assertEqual(self.client.get("/health").json, {"estado": "ok"})

    def test_boolean_json(self):
        self.assertEqual(self.client.post("/api/resolver", json=dict(PREDETERMINADOS, x0=True)).status_code, 400)

    def test_payload_limit(self):
        r = self.client.post("/api/resolver", data='{"x":"' + 'a'*17000 + '"}', content_type="application/json")
        self.assertEqual(r.status_code, 413)
        self.assertTrue(r.is_json)

    def test_invalid_domain(self):
        r = self.client.post("/api/resolver", json={"x0": -2, "y0": .5, "x_final": -1, "h": .1})
        self.assertEqual(r.status_code, 400)

    def test_nonfinite_json(self):
        r = self.client.post("/api/resolver", data='{"x0":1,"y0":NaN,"x_final":1.2,"h":0.1}', content_type="application/json")
        self.assertEqual(r.status_code, 400)

    def test_security_headers(self):
        r = self.client.get("/")
        self.assertEqual(r.headers["X-Content-Type-Options"], "nosniff")
        self.assertIn("default-src 'self'", r.headers["Content-Security-Policy"])