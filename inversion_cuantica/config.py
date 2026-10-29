"""
Configuración general del proyecto: empresas, parámetros, colores y umbrales.

Para cambiar una empresa basta con editar la lista EMPRESAS.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Empresas (las 10 más grandes de EE. UU. por valor de mercado, oct. 2026).
# SpaceX se excluye a propósito: acaba de salir a bolsa y casi no tiene
# historial. En su lugar va JPMorgan, que además agrega un banco.
# ---------------------------------------------------------------------------
EMPRESAS = [
    {"ticker": "NVDA", "nombre": "Nvidia", "descripcion": "Chips para computadoras e inteligencia artificial"},
    {"ticker": "AAPL", "nombre": "Apple", "descripcion": "iPhone, Mac y servicios digitales"},
    {"ticker": "GOOGL", "nombre": "Alphabet (Google)", "descripcion": "Google, YouTube y Android"},
    {"ticker": "MSFT", "nombre": "Microsoft", "descripcion": "Windows, Office y servicios en la nube"},
    {"ticker": "AMZN", "nombre": "Amazon", "descripcion": "Tienda en línea y servicios en la nube"},
    {"ticker": "AVGO", "nombre": "Broadcom", "descripcion": "Chips para redes y comunicaciones"},
    {"ticker": "META", "nombre": "Meta", "descripcion": "Facebook, Instagram y WhatsApp"},
    {"ticker": "TSLA", "nombre": "Tesla", "descripcion": "Autos eléctricos y baterías"},
    {"ticker": "LLY", "nombre": "Eli Lilly", "descripcion": "Medicinas (farmacéutica)"},
    {"ticker": "JPM", "nombre": "JPMorgan Chase", "descripcion": "Banco"},
]

TICKERS = [e["ticker"] for e in EMPRESAS]
NOMBRES = {e["ticker"]: e["nombre"] for e in EMPRESAS}
DESCRIPCIONES = {e["ticker"]: e["descripcion"] for e in EMPRESAS}

# ---------------------------------------------------------------------------
# Parámetros de cálculo
# ---------------------------------------------------------------------------
PERIODO_ANIOS = 5            # Años de historia mensual usados en los cálculos
TASA_LIBRE_RIESGO = 0.04     # Aproximación anual de bonos del Tesoro de EE. UU.
SHOTS = 1000                 # Mediciones por ejecución del circuito
SEMILLA_SIMULACION = 7       # Igual que en el experimento original

# Semáforo de estabilidad (volatilidad anual)
UMBRAL_VERDE = 0.25          # menor que esto: "Tranquila"
UMBRAL_ROJO = 0.40           # mayor que esto: "Muy movida"

# Escala simple del índice de Sharpe ("ganancia por cada unidad de susto")
SHARPE_MEDIO = 0.5
SHARPE_ALTO = 1.0

# Monto de ejemplo
MONTO_MIN = 100
MONTO_MAX = 10_000
MONTO_DEFECTO = 100

# Paseo clásico vs. cuántico
PASOS_MIN = 10
PASOS_MAX = 200
PASOS_DEFECTO = 100

# ---------------------------------------------------------------------------
# Colores (el tema oscuro general está en .streamlit/config.toml)
# ---------------------------------------------------------------------------
# Gráficas con varias series: paleta de 3 colores validada para daltonismo
# sobre fondo oscuro (azul zafiro / rosa vino / dorado).
# Las gráficas de una sola serie usan el dorado (COLOR_SERIE).
COLOR_DORADO = "#C9A45C"
COLOR_SERIE = "#B8893A"
COLOR_DATOS = "#3F7FDB"
COLOR_SIMULACION = "#C0567E"
COLOR_IBM = "#B8893A"
COLOR_PASEO_CLASICO = "#3F7FDB"
COLOR_PASEO_CUANTICO = "#B8893A"
COLOR_SUBE = "#3DD68C"       # verde para "subió"
COLOR_BAJA = "#F06A6A"       # rojo para "bajó"
COLOR_TEXTO = "#E8E6E1"
COLOR_TEXTO_SUAVE = "#8B909C"
COLOR_REJILLA = "#1E2128"
FUENTE_GRAFICAS = "Inter, sans-serif"

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
CARPETA = Path(__file__).resolve().parent
CARPETA_CACHE = CARPETA / "cache"
ARCHIVO_PRECIOS = CARPETA_CACHE / "precios.csv"
ARCHIVO_PRECIOS_INFO = CARPETA_CACHE / "precios_info.json"
ARCHIVO_IBM_PENDIENTE = CARPETA_CACHE / "ibm_trabajo_pendiente.json"
ARCHIVO_IBM_RESULTADO = CARPETA_CACHE / "ibm_ultimo_resultado.json"
