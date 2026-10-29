"""
Guarda la cuenta de IBM Quantum en esta computadora. Se corre UNA sola vez:

    python configurar_ibm.py

La clave se guarda en la configuración de Qiskit de tu usuario
(fuera de este proyecto), nunca en un archivo del proyecto.
"""

import os
import sys
from getpass import getpass

from dotenv import load_dotenv
from qiskit_ibm_runtime import QiskitRuntimeService

import config

load_dotenv(config.CARPETA / ".env")

print("Configuración de la conexión con IBM Quantum")
print("--------------------------------------------")

# getpass no muestra lo que escribes (funciona en Mac y en Windows)
clave = getpass("Pega tu API key de IBM (no se verá en pantalla) y presiona Enter: ").strip()
if not clave:
    print("No escribiste ninguna clave. No se guardó nada.")
    sys.exit(1)

instancia = os.getenv("IBM_INSTANCE", "").strip()
if instancia:
    print("Usando el CRN de la instancia que está en el archivo .env")
else:
    instancia = input("Pega el CRN de tu instancia (empieza con 'crn:'): ").strip()
if not instancia:
    print("Falta el CRN de la instancia. No se guardó nada.")
    sys.exit(1)

QiskitRuntimeService.save_account(
    channel="ibm_quantum_platform",
    token=clave,
    instance=instancia,
    set_as_default=True,
    overwrite=True,
)
del clave

print("Probando la conexión…")
try:
    servicio = QiskitRuntimeService()
    maquinas = servicio.backends(operational=True, simulator=False)
except Exception as error:
    print(f"La cuenta se guardó, pero no se pudo conectar con IBM: {error}")
    print("Revisa la clave y el CRN y vuelve a correr este archivo.")
    sys.exit(1)

print("Computadoras cuánticas disponibles:")
for maquina in maquinas:
    print(f"  - {maquina.name} ({maquina.num_qubits} qubits)")
print("\nConexión con IBM guardada correctamente.")
