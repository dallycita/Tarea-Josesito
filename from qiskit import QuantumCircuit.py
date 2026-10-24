from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

# Creamos un circuito con un qubit.
circuito = QuantumCircuit(1)

# Preparamos probabilidades iguales para 0 y 1.
circuito.h(0)

# Añadimos la medición.
circuito.measure_all()

# Simulamos 1000 preparaciones y mediciones.
simulador = StatevectorSampler(seed=7)
trabajo = simulador.run([circuito], shots=1000)

# Contamos los ceros y los unos.
conteos = trabajo.result()[0].data.meas.get_counts()
print(conteos)
bajadas = conteos.get("0", 0)
subidas = conteos.get("1", 0)
total = bajadas + subidas

print(f"La acción bajó a $98 en {bajadas} mediciones.")
print(f"La acción subió a $102 en {subidas} mediciones.")
print(f"Porcentaje de bajadas: {100 * bajadas / total:.1f}%")
print(f"Porcentaje de subidas: {100 * subidas / total:.1f}%")

from getpass import getpass
from qiskit_ibm_runtime import QiskitRuntimeService

# Pedimos la clave sin mostrarla en pantalla.
import subprocess

ventana = '''
display dialog "Pega tu API key de IBM:" default answer "" with hidden answer buttons {"Cancelar", "Conectar"} default button "Conectar"
text returned of result
'''

clave = subprocess.run(
    ["osascript", "-e", ventana],
    capture_output=True,
    text=True,
    check=True
).stdout.strip()

# Este es el identificador de tu instancia.
crn = "crn:v1:bluemix:public:quantum-computing:us-east:a/94a6e1d61dc345cc90c624608c85c8de:2621a1a6-a8bd-439d-b01e-4b173840ea63::"

# Conectamos con IBM.
servicio = QiskitRuntimeService(
    channel="ibm_quantum_platform",
    token=clave,
    instance=crn
)
del clave

print("Conexión con IBM establecida.")

# Consultamos las computadoras disponibles.
maquinas = servicio.backends(operational=True, simulator=False)

print("Computadoras disponibles:")
for maquina in maquinas:
    print(maquina.name)
    from qiskit_ibm_runtime import SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# 1. Elegimos una computadora real disponible.
maquina = servicio.least_busy(
    operational=True,
    simulator=False,
    min_num_qubits=1
)
print("Usaremos:", maquina.name)

# 2. Traducimos nuestro circuito a las instrucciones de esa máquina.
traductor = generate_preset_pass_manager(
    backend=maquina,
    optimization_level=1
)
circuito_ibm = traductor.run(circuito)

# 3. Enviamos el circuito para realizar 1000 mediciones reales.
muestreador = SamplerV2(mode=maquina)
trabajo_ibm = muestreador.run([circuito_ibm], shots=1000)

print("ID del trabajo:", trabajo_ibm.job_id())
print("Esperando el resultado de IBM...")

# 4. Recuperamos y contamos los resultados.
conteos_ibm = trabajo_ibm.result()[0].data.meas.get_counts()

bajadas_ibm = conteos_ibm.get("0", 0)
subidas_ibm = conteos_ibm.get("1", 0)
total_ibm = bajadas_ibm + subidas_ibm

print("\nRESULTADOS DE LA COMPUTADORA REAL DE IBM")
print(f"Bajadas: {bajadas_ibm} ({100*bajadas_ibm/total_ibm:.1f}%)")
print(f"Subidas: {subidas_ibm} ({100*subidas_ibm/total_ibm:.1f}%)")