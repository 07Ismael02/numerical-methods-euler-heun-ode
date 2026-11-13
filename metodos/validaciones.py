"""Input and floating-point guards for forward fixed-step integration."""
import math
from dataclasses import dataclass

MAX_PASOS = 10000
PREDETERMINADOS = {"x0": 1.0, "y0": 2.0, "x_final": 1.2, "h": 0.1}


class ErrorValidacion(ValueError):
    """A domain or input error suitable for displaying to the student."""


def finito(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ErrorValidacion(f"{nombre} debe ser un número, no texto ni booleano.")
    try:
        numero = float(valor)
    except (OverflowError, ValueError):
        raise ErrorValidacion(f"{nombre} está fuera del rango numérico permitido.") from None
    if not math.isfinite(numero):
        raise ErrorValidacion(f"{nombre} debe ser finito.")
    return numero


@dataclass(frozen=True)
class Parametros:
    x0: float
    y0: float
    x_final: float
    h: float
    pasos: int


def validar(datos):
    if not isinstance(datos, dict):
        raise ErrorValidacion("Envía un objeto JSON con x0, y0, x_final y h.")
    if set(datos) != set(PREDETERMINADOS):
        raise ErrorValidacion("Se requieren exactamente x0, y0, x_final y h.")
    x0, y0, xf, h = (finito(datos[k], k) for k in PREDETERMINADOS)
    if x0 == 0 or xf == 0 or y0 == 0:
        raise ErrorValidacion("El dominio requiere x ≠ 0 e y ≠ 0.")
    if x0 < 0 < xf:
        raise ErrorValidacion("El intervalo no puede atravesar x = 0.")
    if h <= 0:
        raise ErrorValidacion("El tamaño de paso h debe ser positivo.")
    if xf <= x0:
        raise ErrorValidacion("x objetivo debe ser mayor que x inicial.")
    n = finito((xf - x0) / h, "Número de pasos")
    if n < 1 or n > MAX_PASOS:
        raise ErrorValidacion(f"Elige un paso que produzca entre 1 y {MAX_PASOS} iteraciones.")
    pasos = round(n)
    if not math.isclose(n, pasos, rel_tol=1e-12, abs_tol=1e-9):
        raise ErrorValidacion("El intervalo debe contener un número entero de pasos h.")
    if x0 + h == x0 or xf - h == xf:
        raise ErrorValidacion("h es demasiado pequeño para representar los nodos con precisión.")
    return Parametros(x0, y0, xf, h, pasos)


def nodo(p, i):
    # Avoid cumulative addition drift; the last label is the requested endpoint.
    return p.x_final if i == p.pasos else p.x0 + i * p.h