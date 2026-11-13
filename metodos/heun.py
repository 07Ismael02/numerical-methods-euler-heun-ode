"""Heun: Euler predictor followed by one trapezoidal correction."""
from .validaciones import finito, nodo


def heun(f, p):
    y = p.y0
    puntos = [{"x": p.x0, "y": y}]
    traza = []
    for i in range(p.pasos):
        x, xn = nodo(p, i), nodo(p, i + 1)
        k1 = finito(f(x, y), "Pendiente inicial de Heun")
        predictor = finito(y + p.h * k1, "Predictor de Heun")
        k2 = finito(f(xn, predictor), "Pendiente final de Heun")
        incremento = finito(p.h * (k1 / 2 + k2 / 2), "Incremento de Heun")
        yn = finito(y + incremento, "Corrector de Heun")
        traza.append({"iteracion": i + 1, "x": x, "y": y, "h": p.h,
                      "k1": k1, "predictor": predictor, "k2": k2,
                      "incremento": incremento, "x_siguiente": xn, "y_siguiente": yn})
        puntos.append({"x": xn, "y": yn})
        y = yn
    return {"valor": y, "traza": traza, "puntos": puntos}