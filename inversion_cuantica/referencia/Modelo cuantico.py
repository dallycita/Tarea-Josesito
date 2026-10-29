"""
Módulo para consultar y visualizar la capitalización de mercado de empresas
similares (stock peers) usando la API de Financial Modeling Prep.
"""

import os
import sys
import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt

# Configuración y constantes globales
API_BASE_URL = "https://financialmodelingprep.com/stable/stock-peers"
DEFAULT_API_KEY = os.getenv("FMP_API_KEY", "pVwwaxd6JrWXXWdYvKy1uHIVECcFVk3e")
DEFAULT_SYMBOL = "AAPL"
BILLION = 1_000_000_000  # Factor para convertir a miles de millones


def obtener_pares_mercado(
    symbol: str = DEFAULT_SYMBOL,
    api_key: str = DEFAULT_API_KEY,
    timeout: int = 15,
) -> List[Dict[str, Any]]:
    """
    Obtiene la lista de empresas similares y su capitalización de mercado desde la API de FMP.
    """
    if not api_key:
        raise ValueError(
            "Se requiere una API Key válida. Proporciónala como argumento o en la variable FMP_API_KEY."
        )

    params = {
        "symbol": symbol.strip().upper(),
        "apikey": api_key.strip(),
    }
    url = f"{API_BASE_URL}?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            datos = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        raise ConnectionError(f"Error HTTP devuelto por el servidor: {err}") from err
    except urllib.error.URLError as err:
        if isinstance(err.reason, TimeoutError):
            raise ConnectionError(
                f"La solicitud a la API excedió el tiempo límite ({timeout}s)."
            ) from err
        raise ConnectionError(f"Error de conexión con la API: {err.reason}") from err
    except TimeoutError as err:
        raise ConnectionError(
            f"La solicitud a la API excedió el tiempo límite ({timeout}s)."
        ) from err
    except OSError as err:
        raise ConnectionError(f"Error de conexión con la API: {err}") from err
    except ValueError as json_err:
        raise ValueError(f"No se pudo decodificar la respuesta JSON: {json_err}")

    # Validar formato devuelto por la API
    if isinstance(datos, dict):
        if "Error Message" in datos:
            raise ValueError(f"Error devuelto por la API: {datos['Error Message']}")
        if "error" in datos:
            raise ValueError(f"Error devuelto por la API: {datos['error']}")
        datos = [datos]

    if not isinstance(datos, list):
        raise ValueError(f"Respuesta inesperada de la API. Se esperaba una lista, recibido: {type(datos).__name__}")

    if not datos:
        raise ValueError(f"No se encontraron empresas pares para el símbolo '{symbol}'.")

    return datos


def procesar_datos_capitalizacion(
    datos: List[Dict[str, Any]],
    ordenar_ascendente: bool = True,
) -> Tuple[List[str], List[float], List[str]]:
    """
    Limpia, valida y convierte la capitalización a miles de millones (billions).
    """
    empresas_filtradas = []

    for item in datos:
        nombre = item.get("companyName") or item.get("symbol") or "Desconocido"
        ticker = item.get("symbol", "")
        mkt_cap = item.get("mktCap")

        if mkt_cap is None:
            continue

        try:
            mkt_cap_num = float(mkt_cap)
        except (ValueError, TypeError):
            continue

        cap_en_billones = mkt_cap_num / BILLION
        empresas_filtradas.append({
            "nombre": nombre,
            "ticker": ticker,
            "capitalizacion": cap_en_billones,
        })

    if not empresas_filtradas:
        raise ValueError("No se encontraron registros válidos de capitalización en los datos.")

    # Ordenar por capitalización (menor a mayor para que en barh el mayor quede arriba)
    empresas_filtradas.sort(
        key=lambda x: x["capitalizacion"],
        reverse=not ordenar_ascendente
    )

    nombres = [item["nombre"] for item in empresas_filtradas]
    capitalizaciones = [item["capitalizacion"] for item in empresas_filtradas]
    simbolos = [item["ticker"] for item in empresas_filtradas]

    return nombres, capitalizaciones, simbolos


def generar_grafica(
    nombres: List[str],
    capitalizaciones: List[float],
    simbolos: List[str],
    simbolo_base: str = DEFAULT_SYMBOL,
    archivo_salida: Optional[str] = None,
    mostrar: bool = True,
) -> None:
    """
    Genera y personaliza un gráfico de barras horizontales con los datos de capitalización.
    """
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, ax = plt.subplots(figsize=(13, 7), dpi=100)

    # Barras horizontales
    barras = ax.barh(
        nombres,
        capitalizaciones,
        color="#3B82F6",
        edgecolor="#1D4ED8",
        height=0.65,
    )

    # Etiquetas numéricas en el extremo de cada barra
    max_cap = max(capitalizaciones) if capitalizaciones else 1
    for barra, cap in zip(barras, capitalizaciones):
        ancho = barra.get_width()
        etiqueta = f"${cap:,.1f} B"
        ax.annotate(
            etiqueta,
            xy=(ancho, barra.get_y() + barra.get_height() / 2),
            xytext=(7, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=9,
            fontweight="bold",
            color="#1F2937",
        )

    # Títulos y ejes
    simbolo_fmt = simbolo_base.upper()
    ax.set_title(
        f"Capitalización de Mercado de Empresas Similares a {simbolo_fmt}",
        fontsize=14,
        fontweight="bold",
        pad=18,
    )
    ax.set_xlabel("Capitalización de mercado (miles de millones de USD / Billions)", fontsize=11, labelpad=10)
    ax.set_ylabel("Empresas", fontsize=11, labelpad=10)

    # Margen derecho extra para evitar corte de etiquetas
    ax.set_xlim(0, max_cap * 1.15)
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    plt.tight_layout()

    if archivo_salida:
        plt.savefig(archivo_salida, dpi=300, bbox_inches="tight")
        print(f"💾 Gráfica guardada exitosamente en: {archivo_salida}")

    if mostrar:
        plt.show()

    plt.close(fig)


def main() -> None:
    """Función principal para ejecución desde consola."""
    parser = argparse.ArgumentParser(
        description="Analiza y grafica la capitalización de mercado de empresas similares a un símbolo dado."
    )
    parser.add_argument(
        "-s", "--symbol",
        default=DEFAULT_SYMBOL,
        help=f"Ticker a consultar (por defecto: {DEFAULT_SYMBOL}).",
    )
    parser.add_argument(
        "-k", "--api-key",
        default=DEFAULT_API_KEY,
        help="API Key de Financial Modeling Prep (o usa variable FMP_API_KEY).",
    )
    parser.add_argument(
        "-o", "--output",
        default="capitalizacion_peers.png",
        help="Ruta para guardar la gráfica en imagen.",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="No abrir ventana interactiva (ideal para ejecución desatendida).",
    )

    args = parser.parse_args()

    print(f"🔍 Consultando pares y capitalización para '{args.symbol.upper()}'...")
    try:
        datos = obtener_pares_mercado(symbol=args.symbol, api_key=args.api_key)
        print(f"✅ Se obtuvieron {len(datos)} empresas pares.")

        nombres, capitalizaciones, simbolos = procesar_datos_capitalizacion(datos)
        print(f"📊 Procesados {len(nombres)} registros válidos.")

        print("🎨 Generando gráfica...")
        generar_grafica(
            nombres=nombres,
            capitalizaciones=capitalizaciones,
            simbolos=simbolos,
            simbolo_base=args.symbol,
            archivo_salida=args.output,
            mostrar=not args.no_show,
        )
        print("✨ Proceso finalizado con éxito.")

    except (ConnectionError, ValueError) as err:
        print(f"❌ Error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()