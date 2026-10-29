"""
Descarga de precios históricos, caché local y cálculos financieros.

Las funciones de cálculo reciben precios (pandas) y devuelven resultados,
sin tocar la interfaz.
"""

import json
import os
import warnings
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv

import config

load_dotenv(config.CARPETA / ".env")

FMP_URL_AJUSTADO = "https://financialmodelingprep.com/stable/historical-price-eod/dividend-adjusted"
FMP_URL_NORMAL = "https://financialmodelingprep.com/stable/historical-price-eod/full"
HORAS_VIGENCIA_CACHE = 24


# ---------------------------------------------------------------------------
# Descarga
# ---------------------------------------------------------------------------
def descargar_yfinance(tickers, anios=config.PERIODO_ANIOS):
    """Precios mensuales ajustados de Yahoo Finance, todas las empresas en una llamada."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # yfinance muestra avisos internos que no nos afectan
        try:
            datos = yf.download(tickers, period=f"{anios}y", interval="1mo",
                                auto_adjust=True, progress=False)
        except Exception as error:
            raise ConnectionError(f"No se pudo descargar de Yahoo Finance: {error}")

    if datos is None or datos.empty:
        raise ConnectionError("Yahoo Finance no devolvió datos (¿hay conexión a internet?).")

    precios = datos["Close"]
    for ticker in tickers:
        if ticker not in precios.columns or precios[ticker].dropna().empty:
            raise ValueError(f"Yahoo Finance no devolvió precios para {ticker}.")

    return limpiar(precios[tickers])


def descargar_fmp_una_empresa(ticker, api_key, desde):
    """Precios diarios de FMP. Prueba primero los ajustados y luego los normales."""
    intentos = [(FMP_URL_AJUSTADO, "adjClose"), (FMP_URL_NORMAL, "close")]
    for url, columna in intentos:
        parametros = {"symbol": ticker, "from": desde, "apikey": api_key}
        try:
            respuesta = requests.get(url, params=parametros, timeout=15)
            datos = respuesta.json()
        except requests.Timeout:
            raise ConnectionError("La solicitud a FMP excedió el tiempo límite (15 s).")
        except requests.RequestException as error:
            raise ConnectionError(f"Error de conexión con FMP: {error}")
        except ValueError:
            continue  # la respuesta no era JSON: probar la otra dirección

        if isinstance(datos, dict) and "Error Message" in datos:
            raise ValueError(f"Error devuelto por FMP: {datos['Error Message']}")
        if not isinstance(datos, list) or len(datos) == 0:
            continue

        tabla = pd.DataFrame(datos)
        if columna in tabla.columns:
            serie = pd.Series(tabla[columna].values, index=pd.to_datetime(tabla["date"]))
            return serie.astype(float)

    raise ValueError(f"FMP no devolvió precios para {ticker}.")


def descargar_fmp(tickers, api_key, anios=config.PERIODO_ANIOS):
    """Respaldo: precios diarios de FMP convertidos a un precio por mes."""
    desde = (datetime.now() - timedelta(days=365 * anios + 31)).strftime("%Y-%m-%d")
    columnas = {}
    for ticker in tickers:
        columnas[ticker] = descargar_fmp_una_empresa(ticker, api_key, desde)
    diarios = pd.DataFrame(columnas).sort_index()
    # Último precio de cada mes, con la fecha al inicio del mes (igual que Yahoo)
    mensuales = diarios.resample("MS").last()
    return limpiar(mensuales)


def limpiar(precios):
    precios = precios.copy()
    precios.index = pd.to_datetime(precios.index).tz_localize(None)
    precios.index.name = "fecha"
    precios = precios.sort_index()
    return precios.dropna(how="all")


# ---------------------------------------------------------------------------
# Caché (archivos en la carpeta cache/)
# ---------------------------------------------------------------------------
def guardar_cache(precios, fuente):
    config.CARPETA_CACHE.mkdir(exist_ok=True)
    precios.to_csv(config.ARCHIVO_PRECIOS)
    info = {"fuente": fuente, "fecha_descarga": datetime.now().isoformat(timespec="seconds")}
    config.ARCHIVO_PRECIOS_INFO.write_text(json.dumps(info, indent=2), encoding="utf-8")
    return info


def leer_cache():
    """Devuelve (precios, info) guardados, o (None, None) si no hay nada."""
    if not config.ARCHIVO_PRECIOS.exists():
        return None, None
    precios = pd.read_csv(config.ARCHIVO_PRECIOS, index_col=0, parse_dates=True)
    if config.ARCHIVO_PRECIOS_INFO.exists():
        info = json.loads(config.ARCHIVO_PRECIOS_INFO.read_text(encoding="utf-8"))
    else:
        fecha = datetime.fromtimestamp(config.ARCHIVO_PRECIOS.stat().st_mtime)
        info = {"fuente": "datos guardados", "fecha_descarga": fecha.isoformat(timespec="seconds")}
    return precios, info


def obtener_precios(forzar=False, tickers=config.TICKERS):
    """
    Devuelve (precios, info).

    1. Si los datos guardados son de las últimas 24 horas (y no se pidió
       actualizar), los usa.
    2. Si no, descarga de Yahoo Finance; si falla, intenta con FMP.
    3. Si todo falla, usa los datos guardados aunque sean viejos y lo marca
       con info["desde_cache"] = True.
    """
    cache, info_cache = leer_cache()
    hay_cache = cache is not None and all(t in cache.columns for t in tickers)

    if hay_cache and not forzar:
        antiguedad = datetime.now() - datetime.fromisoformat(info_cache["fecha_descarga"])
        if antiguedad < timedelta(hours=HORAS_VIGENCIA_CACHE):
            info_cache["desde_cache"] = False
            return cache[tickers], info_cache

    errores = []
    try:
        precios = descargar_yfinance(tickers)
        info = guardar_cache(precios, "Yahoo Finance")
        info["desde_cache"] = False
        return precios, info
    except (ConnectionError, ValueError) as error:
        errores.append(str(error))

    api_key = os.getenv("FMP_API_KEY", "").strip()
    if api_key:
        try:
            precios = descargar_fmp(tickers, api_key)
            info = guardar_cache(precios, "Financial Modeling Prep")
            info["desde_cache"] = False
            return precios, info
        except (ConnectionError, ValueError) as error:
            errores.append(str(error))

    if hay_cache:
        info_cache["desde_cache"] = True
        return cache[tickers], info_cache

    raise ConnectionError("No se pudieron descargar los precios. " + " | ".join(errores))


# ---------------------------------------------------------------------------
# Cálculos
# ---------------------------------------------------------------------------
def rendimientos(precios):
    """Cambio de cada mes:  r_t = P_t / P_{t-1} − 1"""
    return precios.dropna().pct_change().dropna()


def peor_caida(precios):
    """Mayor caída desde un pico (número negativo: −0.35 significa −35 %)."""
    p = precios.dropna()
    maximo_hasta_hoy = p.cummax()
    caidas = p / maximo_hasta_hoy - 1
    return float(caidas.min())


def serie_crecimiento(precios, monto=100):
    """Cuánto valdría `monto` invertido al inicio del periodo, mes a mes."""
    p = precios.dropna()
    return monto * p / p.iloc[0]


def semaforo(volatilidad):
    if volatilidad < config.UMBRAL_VERDE:
        return "verde"
    if volatilidad <= config.UMBRAL_ROJO:
        return "amarillo"
    return "rojo"


def nivel_sharpe(sharpe):
    if np.isnan(sharpe) or sharpe < config.SHARPE_MEDIO:
        return "baja"
    if sharpe < config.SHARPE_ALTO:
        return "media"
    return "alta"


def calcular_estadisticas(precios, monto=100, tasa_libre_riesgo=config.TASA_LIBRE_RIESGO):
    """Todas las estadísticas de una empresa a partir de sus precios mensuales."""
    p = precios.dropna()
    if len(p) < 3:
        raise ValueError(f"Muy pocos datos para {precios.name}: se necesitan al menos 3 meses.")

    r = rendimientos(p)
    subidas = r[r > 0]
    bajadas = r[r <= 0]
    n_meses = len(r)

    p_inicial = p.iloc[0]
    p_final = p.iloc[-1]
    if len(p) >= 13:
        p_hace_un_anio = p.iloc[-13]  # 12 meses antes del último precio
    else:
        p_hace_un_anio = p_inicial

    retorno_anual = (p_final / p_inicial) ** (12 / n_meses) - 1
    volatilidad = r.std() * np.sqrt(12)
    if volatilidad > 0:
        sharpe = (retorno_anual - tasa_libre_riesgo) / volatilidad
    else:
        sharpe = float("nan")

    subida_prom = subidas.mean() if len(subidas) > 0 else 0.0
    bajada_prom = bajadas.mean() if len(bajadas) > 0 else 0.0

    return {
        "p_sube": len(subidas) / n_meses,
        "subida_prom": float(subida_prom),
        "bajada_prom": float(bajada_prom),
        "crec_1a": float(monto * p_final / p_hace_un_anio),
        "crec_total": float(monto * p_final / p_inicial),
        "retorno_anual": float(retorno_anual),
        "volatilidad": float(volatilidad),
        "semaforo": semaforo(volatilidad),
        "peor_caida": peor_caida(p),
        "sharpe": float(sharpe),
        "nivel_sharpe": nivel_sharpe(sharpe),
        "escenario_baja": float(100 * (1 + bajada_prom)),
        "escenario_sube": float(100 * (1 + subida_prom)),
    }


def resumen(precios, monto=100):
    """Tabla con una fila por empresa (el índice es el ticker)."""
    filas = {}
    for ticker in precios.columns:
        filas[ticker] = calcular_estadisticas(precios[ticker], monto)
        filas[ticker]["nombre"] = config.NOMBRES.get(ticker, ticker)
    return pd.DataFrame(filas).T.infer_objects()


def de_cada_diez(p):
    """0.62 → 6  ("subió 6 de cada 10 meses")"""
    return int(round(p * 10))


if __name__ == "__main__":
    # Prueba rápida: python datos.py
    precios, info = obtener_precios()
    print(f"Fuente: {info['fuente']} · descargado: {info['fecha_descarga']}")
    tabla = resumen(precios)
    columnas = ["nombre", "p_sube", "subida_prom", "bajada_prom", "retorno_anual",
                "volatilidad", "peor_caida", "sharpe", "crec_1a"]
    pd.set_option("display.width", 160)
    print(tabla[columnas].round(3))
