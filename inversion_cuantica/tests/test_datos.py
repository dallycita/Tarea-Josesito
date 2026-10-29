import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import datos  # noqa: E402


def serie(valores):
    fechas = pd.date_range("2024-01-01", periods=len(valores), freq="MS")
    return pd.Series(valores, index=fechas, name="PRUEBA")


# Rendimientos: +10 %, −10 %, 0 %, +20 %
PRECIOS = serie([100.0, 110.0, 99.0, 99.0, 118.8])


def test_p_sube():
    # 2 de 4 meses subió (el 0 % cuenta como "no subió")
    assert datos.calcular_estadisticas(PRECIOS)["p_sube"] == pytest.approx(0.5)


def test_subida_y_bajada_promedio():
    est = datos.calcular_estadisticas(PRECIOS)
    assert est["subida_prom"] == pytest.approx(0.15)
    assert est["bajada_prom"] == pytest.approx(-0.05)
    assert est["escenario_sube"] == pytest.approx(115.0)
    assert est["escenario_baja"] == pytest.approx(95.0)


def test_peor_caida():
    # De 110 a 99: −10 %
    assert datos.peor_caida(PRECIOS) == pytest.approx(-0.10)


def test_crecimiento_de_100():
    est = datos.calcular_estadisticas(PRECIOS, monto=100)
    assert est["crec_total"] == pytest.approx(118.8)
    # Con menos de 13 meses, "hace 1 año" es el inicio de la serie
    assert est["crec_1a"] == pytest.approx(118.8)
    assert datos.serie_crecimiento(PRECIOS, 500).iloc[-1] == pytest.approx(594.0)


def test_crecimiento_1_anio_con_serie_larga():
    # 25 meses: sube 1 % cada mes
    p = serie(list(100 * 1.01 ** np.arange(25)))
    est = datos.calcular_estadisticas(p, monto=100)
    assert est["crec_1a"] == pytest.approx(100 * 1.01 ** 12)
    assert est["retorno_anual"] == pytest.approx(1.01 ** 12 - 1)
    assert est["p_sube"] == 1.0
    assert est["peor_caida"] == pytest.approx(0.0)


def test_semaforo():
    assert datos.semaforo(0.10) == "verde"
    assert datos.semaforo(0.30) == "amarillo"
    assert datos.semaforo(0.55) == "rojo"


def test_de_cada_diez():
    assert datos.de_cada_diez(0.62) == 6
    assert datos.de_cada_diez(0.66) == 7


def sin_internet(*args, **kwargs):
    raise ConnectionError("sin internet")


def usar_carpeta_temporal(monkeypatch, carpeta):
    monkeypatch.setattr(datos.config, "CARPETA_CACHE", carpeta)
    monkeypatch.setattr(datos.config, "ARCHIVO_PRECIOS", carpeta / "precios.csv")
    monkeypatch.setattr(datos.config, "ARCHIVO_PRECIOS_INFO", carpeta / "precios_info.json")
    monkeypatch.setattr(datos, "descargar_yfinance", sin_internet)
    monkeypatch.delenv("FMP_API_KEY", raising=False)


def test_sin_internet_usa_datos_guardados(monkeypatch, tmp_path):
    usar_carpeta_temporal(monkeypatch, tmp_path)
    datos.guardar_cache(pd.DataFrame({"PRUEBA": PRECIOS}), "Yahoo Finance")
    precios, info = datos.obtener_precios(forzar=True, tickers=["PRUEBA"])
    assert info["desde_cache"] is True
    assert len(precios) == 5


def test_sin_internet_y_sin_datos_da_error_claro(monkeypatch, tmp_path):
    usar_carpeta_temporal(monkeypatch, tmp_path)
    with pytest.raises(ConnectionError):
        datos.obtener_precios(tickers=["PRUEBA"])
