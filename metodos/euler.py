"""Explicit Euler, implemented directly from its recurrence."""
from .validaciones import finito, nodo


def euler(f, p):
    y = p.y0
    puntos = [{"x": p.x0, "y": y}]
    traza = []
    for i in range(p.pasos):
        x, xn = nodo(p, i), nodo(p, i + 1)
        k1 = finito(f(x, y), "Pendiente de Euler")
        incremento = finito(p.h * k1, "Incremento de Euler")
        yn = finito(y + incremento, "Resultado de Euler")
        traza.append({"iteracion": i + 1, "x": x, "y": y, "h": p.h,
                      "k1": k1, "incremento": incremento,
                      "x_siguiente": xn, "y_siguiente": yn})
        puntos.append({"x": xn, "y": yn})
        y = yn
    return {"valor": y, "traza": traza, "puntos": puntos}