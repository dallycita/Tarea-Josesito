"""
Parte cuántica: un qubit por empresa, simulación local y ejecución en IBM.

Estado de cada qubit:  |ψ⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩,  |0⟩ = "baja", |1⟩ = "sube".
Regla de Born:         P(1) = sin²(θ/2) = p_sube   ⇒   θ = 2·arcsin(√p_sube)
"""

import json
from datetime import datetime

import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

import config


class ErrorIBM(Exception):
    """Error de IBM con un mensaje sencillo para mostrar al usuario."""


# ---------------------------------------------------------------------------
# Circuito
# ---------------------------------------------------------------------------
def angulo(p):
    """θ = 2·arcsin(√p). Primero se asegura que p esté entre 0 y 1."""
    p = min(max(float(p), 0.0), 1.0)
    return 2 * np.arcsin(np.sqrt(p))


def construir_circuito(probabilidades):
    """Un qubit por empresa (en el orden del diccionario), rotado con RY(θ) y medido."""
    circuito = QuantumCircuit(len(probabilidades))
    for i, p in enumerate(probabilidades.values()):
        circuito.ry(angulo(p), i)
    circuito.measure_all()
    return circuito


def conteos_por_empresa(conteos, tickers):
    """
    Fracción de veces que salió "1" (sube) en cada qubit por separado.

    Qiskit escribe los resultados al revés: el qubit 0 es el ÚLTIMO carácter
    de la cadena, el qubit 1 el penúltimo, etc. Por eso se usa cadena[-(i + 1)].
    """
    total = sum(conteos.values())
    resultado = {}
    for i, ticker in enumerate(tickers):
        unos = 0
        for cadena, veces in conteos.items():
            if cadena[-(i + 1)] == "1":
                unos += veces
        resultado[ticker] = unos / total if total > 0 else 0.0
    return resultado


def precio_esperado(f, escenario_sube, escenario_baja):
    """f · sube + (1 − f) · baja"""
    return f * escenario_sube + (1 - f) * escenario_baja


# ---------------------------------------------------------------------------
# Simulación en la computadora propia
# ---------------------------------------------------------------------------
def simular(circuito, shots=config.SHOTS, semilla=config.SEMILLA_SIMULACION):
    simulador = StatevectorSampler(seed=semilla)
    resultado = simulador.run([circuito], shots=shots).result()
    return resultado[0].data.meas.get_counts()


# ---------------------------------------------------------------------------
# Computadora cuántica real de IBM
# ---------------------------------------------------------------------------
ESTADOS = {
    "INITIALIZING": "Preparando el envío…",
    "QUEUED": "En fila en IBM…",
    "VALIDATING": "IBM está revisando el circuito…",
    "RUNNING": "Ejecutándose en la computadora cuántica…",
    "DONE": "¡Listo!",
    "ERROR": "IBM reportó un error en el trabajo.",
    "CANCELLED": "El trabajo fue cancelado.",
}


def cuenta_configurada():
    """¿Ya se corrió configurar_ibm.py? (no necesita internet)"""
    try:
        return len(QiskitRuntimeService.saved_accounts()) > 0
    except Exception:
        return False


def mensaje_de_error(error):
    """Convierte un error técnico de IBM en una frase sencilla."""
    texto = str(error).lower()
    if "account" in texto and "not found" in texto:
        return "La conexión con IBM no está configurada. Sigue el paso del README."
    if "connection" in texto or "timeout" in texto or "timed out" in texto or "max retries" in texto:
        return "No hay conexión con IBM. Revisa tu internet e inténtalo de nuevo."
    if "401" in texto or "unauthorized" in texto:
        return "IBM no aceptó la clave guardada. Vuelve a correr configurar_ibm.py."
    if "backend" in texto:
        return "Ahora mismo no hay computadoras cuánticas de IBM disponibles. Prueba más tarde."
    return f"IBM devolvió un error: {error}"


def conectar():
    if not cuenta_configurada():
        raise ErrorIBM("La conexión con IBM no está configurada. Sigue el paso del README.")
    try:
        return QiskitRuntimeService()
    except Exception as error:
        raise ErrorIBM(mensaje_de_error(error))


def guardar_json(ruta, datos):
    config.CARPETA_CACHE.mkdir(exist_ok=True)
    ruta.write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8")


def leer_json(ruta):
    if not ruta.exists():
        return None
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except ValueError:
        return None


def leer_pendiente():
    return leer_json(config.ARCHIVO_IBM_PENDIENTE)


def leer_ultimo_resultado():
    return leer_json(config.ARCHIVO_IBM_RESULTADO)


def enviar_a_ibm(probabilidades, shots=config.SHOTS):
    """Envía el circuito a la máquina menos ocupada y guarda el trabajo como pendiente."""
    servicio = conectar()
    try:
        maquina = servicio.least_busy(operational=True, simulator=False, min_num_qubits=len(probabilidades))
        traductor = generate_preset_pass_manager(backend=maquina, optimization_level=1)
        circuito_ibm = traductor.run(construir_circuito(probabilidades))
        trabajo = SamplerV2(mode=maquina).run([circuito_ibm], shots=shots)
    except Exception as error:
        raise ErrorIBM(mensaje_de_error(error))

    pendiente = {
        "job_id": trabajo.job_id(),
        "maquina": maquina.name,
        "fecha_envio": datetime.now().isoformat(timespec="seconds"),
        "shots": shots,
        "probabilidades": dict(probabilidades),
    }
    guardar_json(config.ARCHIVO_IBM_PENDIENTE, pendiente)
    return pendiente


def revisar_trabajo():
    """
    Pregunta a IBM cómo va el trabajo pendiente.
    Devuelve {"estado": "QUEUED" / "DONE" / ..., "mensaje": texto sencillo}.
    Si ya terminó, guarda el resultado en cache/ibm_ultimo_resultado.json.
    """
    pendiente = leer_pendiente()
    if pendiente is None:
        return {"estado": "NINGUNO", "mensaje": "No hay ningún trabajo enviado a IBM."}

    servicio = conectar()
    try:
        trabajo = servicio.job(pendiente["job_id"])
        estado = str(trabajo.status()).upper()
        if "." in estado:  # algunas versiones devuelven "JobStatus.DONE"
            estado = estado.split(".")[-1]
    except Exception as error:
        raise ErrorIBM(mensaje_de_error(error))

    if estado == "DONE":
        try:
            conteos = trabajo.result()[0].data.meas.get_counts()
        except Exception as error:
            raise ErrorIBM(mensaje_de_error(error))
        tickers = list(pendiente["probabilidades"].keys())
        resultado = {
            "job_id": pendiente["job_id"],
            "maquina": pendiente["maquina"],
            "fecha_envio": pendiente["fecha_envio"],
            "fecha_resultado": datetime.now().isoformat(timespec="seconds"),
            "shots": pendiente["shots"],
            "probabilidades": pendiente["probabilidades"],
            "conteos": conteos,
            "marginales": conteos_por_empresa(conteos, tickers),
        }
        guardar_json(config.ARCHIVO_IBM_RESULTADO, resultado)
        config.ARCHIVO_IBM_PENDIENTE.unlink()

    if estado == "ERROR" or estado == "CANCELLED":
        config.ARCHIVO_IBM_PENDIENTE.unlink()

    return {"estado": estado, "mensaje": ESTADOS.get(estado, estado)}
