"""
Paseo aleatorio clásico vs. paseo cuántico con moneda de Hadamard
(diapositiva "Métodos cuánticos (III)", Orrell, Quantum Economics and Finance).

Es un cálculo exacto del modelo con numpy; no se ejecuta en IBM.
Las posiciones van de -pasos a +pasos; la posición x está en el índice x + pasos.
"""

import numpy as np
from scipy.stats import binom

# Compuerta de Hadamard (la "moneda cuántica")
HADAMARD = np.array([[1, 1], [1, -1]]) / np.sqrt(2)

# Estado inicial de la moneda: [amplitud de |0⟩, amplitud de |1⟩]
MONEDAS = {
    "simetrica": np.array([1, 1j]) / np.sqrt(2),  # (|0⟩ + i|1⟩)/√2
    "sesgada": np.array([1, 0]),                  # |0⟩
}


def posiciones(pasos):
    return np.arange(-pasos, pasos + 1)


def paseo_clasico(pasos):
    """Cada paso sube o baja 1 con probabilidad 1/2: distribución binomial (campana)."""
    probabilidad = np.zeros(2 * pasos + 1)
    for subidas in range(pasos + 1):
        posicion = 2 * subidas - pasos
        probabilidad[posicion + pasos] = binom.pmf(subidas, pasos, 0.5)
    return probabilidad


def mover(tabla):
    """
    Desplaza según la moneda: columna 0 → una posición a la izquierda,
    columna 1 → una posición a la derecha.
    """
    nueva = np.zeros_like(tabla)
    nueva[:-1, 0] = tabla[1:, 0]
    nueva[1:, 1] = tabla[:-1, 1]
    return nueva


def paseo_cuantico(pasos, moneda="simetrica", observar=False):
    """
    Probabilidad de cada posición después de `pasos` pasos.

    - observar=False: se trabaja con amplitudes, que se suman o se cancelan
      (interferencia).
    - observar=True: se mide la moneda en cada paso. Solo quedan probabilidades
      (|amplitud|²), no hay interferencia y el resultado es el clásico.
    """
    filas = 2 * pasos + 1
    centro = pasos

    if not observar:
        # estado[posición, moneda] = amplitud (número complejo)
        estado = np.zeros((filas, 2), dtype=complex)
        estado[centro] = MONEDAS[moneda]
        for _ in range(pasos):
            estado = estado @ HADAMARD.T   # lanzar la moneda cuántica
            estado = mover(estado)         # dar el paso
        return (np.abs(estado) ** 2).sum(axis=1)

    # Observando cada paso: probabilidades en vez de amplitudes
    hadamard_medida = np.abs(HADAMARD) ** 2      # cada resultado con prob. 1/2
    prob = np.zeros((filas, 2))
    prob[centro] = np.abs(MONEDAS[moneda]) ** 2
    for _ in range(pasos):
        prob = prob @ hadamard_medida.T
        prob = mover(prob)
    return prob.sum(axis=1)


def solo_alcanzables(pasos, clasico, cuantico):
    """
    Quita las posiciones imposibles: con un número par de pasos solo se puede
    terminar en posiciones pares (y con uno impar, en impares).
    """
    x = posiciones(pasos)
    alcanzable = (x + pasos) % 2 == 0
    return x[alcanzable], clasico[alcanzable], cuantico[alcanzable]
