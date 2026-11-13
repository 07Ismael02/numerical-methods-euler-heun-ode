"""HTTP adapter. Run locally with python -m backend.app."""
import os
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from metodos.problema_pvi import resolver
from metodos.validaciones import ErrorValidacion, PREDETERMINADOS


def create_app():
    app = Flask(__name__)
    app.config.update(MAX_CONTENT_LENGTH=16384)
    app.json.ensure_ascii = False

    @app.get("/")
    def inicio():
        return render_template("index.html", defaults=PREDETERMINADOS)

    @app.get("/health")
    def salud():
        return jsonify(estado="ok")

    @app.post("/api/resolver")
    def calcular():
        if not request.is_json:
            return jsonify(estado="error", mensaje="Envía los parámetros como application/json."), 415
        datos = request.get_json()
        try:
            return jsonify(resolver(datos))
        except ErrorValidacion as error:
            return jsonify(estado="error", mensaje=str(error)), 400
        except (OverflowError, ZeroDivisionError):
            return jsonify(estado="error", mensaje="La escala numérica es inválida. Revisa los parámetros."), 400

    @app.errorhandler(HTTPException)
    def error_http(error):
        if request.path.startswith("/api/"):
            mensajes = {400: "El cuerpo JSON no es válido.", 413: "La solicitud es demasiado grande.",
                        404: "Endpoint no encontrado.", 405: "Método HTTP no permitido."}
            return jsonify(estado="error", mensaje=mensajes.get(error.code, error.description)), error.code
        return error

    @app.after_request
    def cabeceras(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; frame-ancestors 'none'"
        return response

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5014")), debug=False)