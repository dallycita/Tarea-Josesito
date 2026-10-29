import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import paseo  # noqa: E402


@pytest.mark.parametrize("pasos", [10, 100, 200])
@pytest.mark.parametrize("moneda", ["simetrica", "sesgada"])
@pytest.mark.parametrize("observar", [False, True])
def test_probabilidades_suman_1(pasos, moneda, observar):
    assert paseo.paseo_cuantico(pasos, moneda, observar).sum() == pytest.approx(1.0)
    assert paseo.paseo_clasico(pasos).sum() == pytest.approx(1.0)


@pytest.mark.parametrize("moneda", ["simetrica", "sesgada"])
def test_observar_en_cada_paso_da_binomial(moneda):
    np.testing.assert_allclose(
        paseo.paseo_cuantico(100, moneda, observar=True), paseo.paseo_clasico(100), atol=1e-12
    )


def test_cuantico_simetrico_es_simetrico_y_se_aleja():
    q = paseo.paseo_cuantico(100, "simetrica")
    np.testing.assert_allclose(q, q[::-1], atol=1e-12)
    x = paseo.posiciones(100)
    # El paseo cuántico se dispersa más que el clásico
    assert (q * x**2).sum() > 5 * (paseo.paseo_clasico(100) * x**2).sum()


def test_sesgada_se_carga_a_un_lado():
    q = paseo.paseo_cuantico(100, "sesgada")
    x = paseo.posiciones(100)
    assert (q * x).sum() < -10  # moneda |0⟩ → se va a la izquierda


def test_paridad():
    x, c, q = paseo.solo_alcanzables(100, paseo.paseo_clasico(100), paseo.paseo_cuantico(100))
    assert np.all(x % 2 == 0)
    assert q.sum() == pytest.approx(1.0)
