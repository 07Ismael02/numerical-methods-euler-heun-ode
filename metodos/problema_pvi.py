"""Official IVP, analytic reference and comparison orchestration."""
import math
from dataclasses import asdict
from .euler import euler
from .heun import heun
from .validaciones import ErrorValidacion, finito, validar


def pendiente(x, y):
    x, y = finito(x, "x"), finito(y, "y")
    if x == 0 or y == 0:
        raise ErrorValidacion("No se puede evaluar f(x,y): x e y deben ser distintos de cero.")
    return finito(x / y - y / x, "f(x,y)")


def constante(x0, y0):
    try:
        return finito(x0**2 * (y0**2 - x0**2 / 2), "Constante C")
    except OverflowError:
        raise ErrorValidacion("Los parámetros exceden el rango de cálculo de la solución exacta.") from None


def exacta(x, c, signo=1):
    if x == 0:
        raise ErrorValidacion("La solución exacta no está definida en x = 0.")
    try:
        radicando = finito(x**2 / 2 + c / x**2, "Radicando de la solución exacta")
    except (OverflowError, ZeroDivisionError):
        raise ErrorValidacion("La escala de los parámetros impide evaluar la solución exacta.") from None
    if radicando <= 0:
        raise ErrorValidacion("No existe una solución real con y ≠ 0 en todo el intervalo solicitado.")
    return math.copysign(math.sqrt(radicando), signo)


def errores(verdadero, aproximado):
    absoluto = finito(abs(verdadero - aproximado), "Error absoluto")
    relativo = finito(absoluto / abs(verdadero) * 100, "Error relativo porcentual")
    return {"absoluto": absoluto, "relativo_porcentual": relativo}


def resolver(datos):
    p = validar(datos)
    c = constante(p.x0, p.y0)
    # x has fixed sign: x^4/2+C is monotonic on the interval, so checking
    # both endpoints proves positivity throughout (not just at sampled nodes).
    exacta(p.x0, c, p.y0)
    verdadero = exacta(p.x_final, c, p.y0)

    def campo(x, y):
        if y == 0 or (y > 0) != (p.y0 > 0):
            raise ErrorValidacion("Un paso o predictor alcanza o atraviesa y = 0. Reduce h.")
        return pendiente(x, y)

    resultados = {}
    for nombre, metodo in (("euler", euler), ("heun", heun)):
        resultado = metodo(campo, p)
        campo(p.x_final, resultado["valor"])
        resultado["errores"] = errores(verdadero, resultado["valor"])
        resultados[nombre] = resultado
    a = resultados["euler"]["errores"]["absoluto"]
    b = resultados["heun"]["errores"]["absoluto"]
    mejor = "empate" if a == b else ("Euler" if a < b else "Heun")
    curva = [{"x": p.x0 + (p.x_final - p.x0) * i / 300,
              "y": exacta(p.x0 + (p.x_final - p.x0) * i / 300, c, p.y0)}
             for i in range(301)]
    return {"estado": "ok", "parametros": asdict(p), "constante": c,
            "valor_exacto": verdadero, **resultados, "mas_preciso": mejor,
            "grafica": {"exacta": curva, "euler": resultados["euler"]["puntos"],
                        "heun": resultados["heun"]["puntos"]}}