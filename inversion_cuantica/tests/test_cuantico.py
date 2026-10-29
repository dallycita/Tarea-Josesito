import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cuantico  # noqa: E402

TICKERS = [f"E{i}" for i in range(10)]


def test_frecuencia_con_p_070():
    qc = cuantico.construir_circuito({"A": 0.7})
    counts = cuantico.simular(qc, shots=20_000, semilla=123)
    f = cuantico.conteos_por_empresa(counts, ["A"])["A"]
    assert 0.68 <= f <= 0.72


def test_orden_de_bits():
    # Solo la empresa índice 2 tiene p = 1
    probs = {t: (1.0 if i == 2 else 0.0) for i, t in enumerate(TICKERS)}
    counts = cuantico.simular(cuantico.construir_circuito(probs), shots=500)
    marginales = cuantico.conteos_por_empresa(counts, TICKERS)
    assert marginales["E2"] == 1.0
    assert all(marginales[t] == 0.0 for t in TICKERS if t != "E2")


def test_orden_de_bits_con_cadena_manual():
    # "100" → qubit 2 = 1, qubits 0 y 1 = 0
    assert cuantico.conteos_por_empresa({"100": 10}, ["a", "b", "c"]) == {"a": 0.0, "b": 0.0, "c": 1.0}


@pytest.mark.parametrize("p", [0.0, 1.0, -0.1, 1.1])
def test_limites_no_fallan(p):
    qc = cuantico.construir_circuito({"A": p})
    counts = cuantico.simular(qc, shots=200)
    f = cuantico.conteos_por_empresa(counts, ["A"])["A"]
    assert f == (1.0 if p >= 1 else 0.0)


def test_precio_esperado():
    assert cuantico.precio_esperado(0.5, 102, 98) == pytest.approx(100)
    assert cuantico.precio_esperado(0.501, 102, 98) == pytest.approx(100.004)


def test_sin_cuenta_de_ibm_da_mensaje_sencillo(monkeypatch):
    monkeypatch.setattr(cuantico, "cuenta_configurada", lambda: False)
    with pytest.raises(cuantico.ErrorIBM, match="no está configurada"):
        cuantico.enviar_a_ibm({"A": 0.5})
