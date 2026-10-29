"""
TODOS los textos que ve el usuario, en lenguaje sencillo.

Regla: ningún término técnico aparece sin su explicación al lado o en un
tooltip (ayuda que se ve al pasar el mouse por el signo "?").
"""

# ---------------------------------------------------------------------------
# Formato de números
# ---------------------------------------------------------------------------
def dinero(x, decimales=0):
    """1234.5 → "$1,235" """
    signo = "-" if x < 0 else ""
    return f"{signo}${abs(x):,.{decimales}f}"


def dinero_md(x, decimales=0):
    """
    Igual que dinero(), pero para textos con formato (markdown).
    Streamlit toma el texto entre dos signos $ como una fórmula matemática,
    así que se escribe \\$ para que se vea el signo normal.
    """
    return dinero(x, decimales).replace("$", "\\$")


def pct(x, decimales=1):
    """0.125 → "12.5 %" """
    return f"{100 * x:.{decimales}f} %"


def fecha(f):
    """Fecha corta en español: 25 oct 2026"""
    meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    return f"{f.day} {meses[f.month - 1]} {f.year}"


def fecha_hora(f):
    return f"{fecha(f)}, {f:%H:%M}"


# ---------------------------------------------------------------------------
# Generales
# ---------------------------------------------------------------------------
TITULO_APP = "Inversión cuántica para todos"

MENSAJE_CENTRAL = (
    "Este programa muestra cómo se han comportado estas empresas y usa una computadora "
    "cuántica para representar y medir esas probabilidades. **No adivina el futuro ni es "
    "una recomendación de inversión.**"
)

AVISO_PIE = "Esto describe el pasado. No es una recomendación de inversión ni una predicción."

PIE_CURSO = "Proyecto del curso Teoría de Inversión · UVG · Prof. Mario A. Cuevas"

SECCIONES = {
    "inicio": "Inicio",
    "empresas": "Las 10 empresas",
    "ibm": "Pregúntale a IBM",
    "paseo": "¿Y si el mercado fuera cuántico?",
    "como": "¿Cómo funciona?",
}

MARCA_NOMBRE = "Inversión Cuántica"
MARCA_CURSO = "Teoría de Inversión · UVG"

MENU_TITULO = "Recorrido"
MENU_MONTO = "Tu monto de ejemplo"
MENU_MONTO_AYUDA = "Este monto se usa en toda la app para los ejemplos («si hubieras puesto…»)."

GLOSARIO_TITULO = "Glosario rápido"
GLOSARIO = [
    ("Acción", "Un pedacito de una empresa. Si a la empresa le va bien, suele subir de precio."),
    ("Volatilidad", "Qué tanto sube y baja un precio. En la app es el semáforo."),
    ("Índice de Sharpe", "Ganancia por cada unidad de susto: cuánto ganó comparado con cuánto se movió."),
    ("Peor caída (drawdown)", "Lo más que bajó desde su punto más alto."),
    ("Qubit", "El «bit cuántico»: puede estar en baja y sube a la vez hasta que se mide."),
    ("Medición", "Mirar el qubit. En ese momento da un solo resultado: 0 (baja) o 1 (sube)."),
]

BOTON_ANTERIOR = "Anterior"
BOTON_SIGUIENTE = "Siguiente: {titulo}"

# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------
DATOS_FECHA = "Precios mensuales de {fuente}, del {inicio} al {fin}. Descargados el {descarga}."
DATOS_DESDE_CACHE = "Sin conexión: usando datos guardados el {descarga}."
DATOS_BOTON_ACTUALIZAR = "Actualizar datos"
DATOS_ACTUALIZANDO = "Descargando precios…"
DATOS_ERROR = (
    "No se pudieron conseguir los precios y no hay datos guardados. "
    "Revisa tu conexión a internet y presiona «Actualizar datos». Detalle: {error}"
)

# ---------------------------------------------------------------------------
# Inicio
# ---------------------------------------------------------------------------
INICIO_ETIQUETA = "Precios reales hasta el {fin}"
INICIO_DESTACADO = "convenido"
CINTA_TITULO = "Cuánto cambió cada empresa en el último año"
INICIO_TITULO = "¿Dónde ha convenido invertir?"
INICIO_SUBTITULO = (
    "Las 10 empresas más grandes de Wall Street, vistas con una computadora cuántica"
)
INICIO_QUE_HAY = "Qué vas a encontrar"
INICIO_PASOS = [
    ("1", "Mira cómo les fue a las empresas",
     "Usamos los precios reales de los últimos 5 años, explicados con ejemplos de dinero.",
     "Ver las empresas"),
    ("2", "Pregúntale a una computadora cuántica real",
     "Convertimos lo que pasó en probabilidades y se las damos a una máquina de IBM para que las mida.",
     "Ir a IBM"),
    ("3", "Descubre qué cambia si el mercado fuera cuántico",
     "Comparamos el azar de una moneda normal con el «azar cuántico», donde los caminos se suman y se cancelan.",
     "Probar el experimento"),
]
INICIO_MONTO = "¿Cuánto te imaginas invirtiendo?"
INICIO_MONTO_AYUDA = (
    "Elige un monto. Todos los ejemplos de la app se calculan con él. "
    "También puedes cambiarlo después en el panel de la izquierda."
)
INICIO_BOTON = "Empezar el recorrido"

# ---------------------------------------------------------------------------
# Las 10 empresas
# ---------------------------------------------------------------------------
EMPRESAS_TITULO = "Las 10 empresas"
EMPRESAS_TABS = ["Tarjetas", "Comparar en gráficas", "Tabla completa"]
DESTACADAS_TITULO = "Lo más destacado"

KPI_CRECIO = "Más creció (5 años)"
KPI_CRECIO_DELTA = "{monto} → {valor}"
KPI_TRANQUILA = "Más tranquila"
KPI_TRANQUILA_DELTA = "se movió {vol} al año"
KPI_MESES = "Más meses al alza"
KPI_MESES_DELTA = "{n} de cada 10 meses"
KPI_SHARPE = "Mejor ganancia/susto"
KPI_SHARPE_DELTA = "índice de Sharpe {valor:.2f}"

EMPRESAS_INTRO = (
    "Así les fue en los últimos 5 años a las empresas más grandes de Wall Street. "
    "Toca **«Ver ficha»** en cualquier empresa para ver todos sus datos."
)

ORDEN_ETIQUETA = "Ordenar por"
ORDEN_OPCIONES = {
    "sharpe": "Ganancia/susto",
    "gano": "Más ganó",
    "tranquila": "Más tranquila",
}
ORDEN_AYUDA = (
    "«Ganancia por cada unidad de susto» compara lo que ganó una empresa con cuánto subía y "
    "bajaba su precio por el camino. Los expertos le dicen «índice de Sharpe»."
)

# (ícono, palabra, color de la etiqueta)
SEMAFORO = {
    "verde": (":material/check_circle:", "Tranquila", "green"),
    "amarillo": (":material/swap_vert:", "Normal", "orange"),
    "rojo": (":material/bolt:", "Muy movida", "red"),
}
SEMAFORO_LEYENDA = "Estabilidad:"
SEMAFORO_AYUDA_CORTA = (
    "Qué tanto sube y baja el precio de un mes a otro. «Tranquila» = cambios pequeños; "
    "«Muy movida» = saltos grandes en ambas direcciones. Los expertos le dicen «volatilidad»."
)
SEMAFORO_AYUDA = SEMAFORO_AYUDA_CORTA + " Esta empresa se movió en promedio {vol} al año."

NIVEL_SHARPE = {"baja": "Baja", "media": "Media", "alta": "Alta"}

ETIQUETA_TOP = "Top 3"

# Tarjeta corta de cada empresa
TARJETA_1A = "Si hubieras puesto {monto} hace 1 año, hoy tendrías"
BOTON_VER_FICHA = "Ver ficha"

# Ficha completa (ventana que se abre al tocar «Ver ficha»)
FICHA_TITULO = "Ficha de la empresa"
FICHA_MESES = "Meses en que subió"
FICHA_MESES_VALOR = "{n} de cada 10"
FICHA_ANUAL = "Ganancia promedio al año"
FICHA_ANUAL_PERDIO = "Pérdida promedio al año"
FICHA_CAIDA = "En su peor momento, {monto} valían"
FICHA_SHARPE = "Ganancia por cada unidad de susto"
FICHA_VOLATILIDAD = "Cuánto se movió al año"
TARJETA_ANUAL_AYUDA = (
    "Promedio de los 5 años, como si hubiera crecido lo mismo cada año. "
    "Los expertos le dicen «rendimiento anual»."
)
TARJETA_CAIDA_AYUDA = (
    "La mayor caída desde el precio más alto que había tenido hasta el más bajo que vino "
    "después. Los expertos le dicen «drawdown máximo»."
)

DETALLE_GRAFICA = "Cómo habrían crecido {monto} puestos hace 5 años"

BARRAS_TITULO = "¿Cuánto valdrían hoy {monto} puestos hace 5 años?"
BARRAS_LINEA = "Lo que pusiste"

RIESGO_TITULO = "Ganancia contra susto"
RIESGO_NOTA = (
    "Cada punto es una empresa. Más arriba = ganó más cada año. Más a la derecha = su precio "
    "subía y bajaba más (más susto). Lo ideal es estar arriba y a la izquierda."
)
RIESGO_EJE_X = "Qué tanto se movió al año (volatilidad)"
RIESGO_EJE_Y = "Ganancia promedio al año"

TABLA_COLUMNAS = {
    "nombre": "Empresa",
    "semaforo": "Estabilidad",
    "p_sube": "Meses que subió",
    "retorno_anual": "Ganancia/año",
    "volatilidad": "Movimiento/año",
    "peor_caida": "Peor caída",
    "crec_total": "Hoy valen tus {monto}",
    "sharpe": "Ganancia/susto",
}

# ---------------------------------------------------------------------------
# Pregúntale a IBM
# ---------------------------------------------------------------------------
IBM_TITULO = "Pregúntale a IBM"
IBM_SUBTITULO = (
    "Una computadora cuántica mide las probabilidades de que cada empresa suba. "
    "**Simúlalo al instante** o **envíalo a una máquina real de IBM**, y compara el "
    "resultado con los datos."
)
IBM_EXPLICACION = "¿Qué está pasando aquí? Explicación en 3 pasos"
IBM_PASOS = [
    ("1", "Un qubit por empresa",
     "Cada empresa es un qubit: puede estar en «baja» y «sube» a la vez hasta que se mide."),
    ("2", "Lo preparamos con datos reales",
     "Lo giramos para que la probabilidad de «sube» sea la misma que tuvo la empresa en el pasado."),
    ("3", "Lo medimos {shots} veces",
     "Contamos cuántas veces salió «sube» y lo comparamos con los datos."),
]
IBM_QUBIT_AYUDA = (
    "Qubit = «bit cuántico». Un bit normal es 0 o 1. Un qubit puede estar en una mezcla "
    "de los dos (eso se llama «superposición») hasta que se mide: en ese momento da 0 o 1."
)

SIM_TITULO = "En tu computadora"
SIM_ETIQUETA = "Instantáneo"
SIM_TEXTO = "Imita a una computadora cuántica perfecta, sin ruido. Ideal para probar."
BOTON_SIMULAR = "Simular de nuevo"
SIMULACION_HECHA = "Simulación número {n}: {shots} mediciones hechas en tu computadora."
SIMULACION_AYUDA = "Cada vez que simulas salen números un poco distintos: así es el azar."

IBM_TARJETA_TITULO = "En IBM Quantum (máquina real)"
IBM_TARJETA_TEXTO = (
    "El circuito viaja a una computadora cuántica de verdad. Entra a una fila y puede tardar "
    "de segundos a horas; no hace falta esperar con la página abierta."
)
IBM_ETIQUETA_SIN_CONFIGURAR = "Sin configurar"
IBM_ETIQUETA_EN_FILA = "Trabajo en fila"
IBM_ETIQUETA_GUARDADO = "Resultado guardado"
IBM_ETIQUETA_LISTA = "Lista para enviar"
BOTON_ENVIAR = "Enviar a IBM"
BOTON_REVISAR = "Revisar si ya terminó"
IBM_ENVIANDO = "Conectando con IBM y enviando el circuito…"
IBM_ENVIADO = "Trabajo enviado a **{maquina}**. Puede tardar desde segundos hasta varios minutos si hay fila."
IBM_PENDIENTE = "Trabajo enviado a **{maquina}** el {fecha}. Estado: **{estado}**"
IBM_ESTADO_SIN_REVISAR = "sin revisar todavía"
IBM_NO_CONFIGURADO = "La conexión con IBM no está configurada. Sigue el paso del README."
IBM_ULTIMO = "Último resultado real: **{maquina}**, {fecha}."
IBM_SIN_RESULTADO = "Todavía no hay resultados de IBM guardados."
IBM_PROBS_DISTINTAS = (
    "Ese trabajo se envió con los datos de ese día; las probabilidades pueden diferir un poco "
    "de las actuales."
)
IBM_LISTO = "¡Listo! IBM terminó y el resultado quedó guardado."
IBM_TERMINO_MAL = "El trabajo no se completó ({estado}). Puedes enviarlo de nuevo."

KPI_DIF_SIM = "Simulación vs. datos"
KPI_DIF_IBM = "IBM real vs. datos"
KPI_PUNTOS = "{x:.1f} puntos"
KPI_SIN_IBM = "Sin resultado"
KPI_DIF_AYUDA = (
    "Diferencia promedio entre el % de «sube» medido y el % de los datos. "
    "Mientras más cerca de 0, más se parecen."
)
IBM_TABS = ["Resultados por empresa", "Lectura financiera"]

FUENTE_DATOS = "Datos del pasado"
FUENTE_SIM = "Simulación"
FUENTE_IBM = "IBM real"

GRAFICA_IBM_TITULO = "¿Cuántas veces salió «sube»? (de cada 100 mediciones)"
GRAFICA_IBM_EJE = "Veces que salió «sube» (%)"

LECTURA_TITULO = "Lectura financiera: ¿cuánto valdrían {base} dentro de un mes?"
LECTURA_INTRO = (
    "Cada empresa tiene dos escenarios sacados de su historia: cuánto bajaba en promedio "
    "cuando bajaba y cuánto subía en promedio cuando subía. El precio esperado mezcla los "
    "dos escenarios según cuántas veces salió «sube»:"
)
LECTURA_FORMULA = r"\text{precio esperado} = f \times \text{sube} + (1 - f) \times \text{baja}"
LECTURA_COLUMNAS = {
    "empresa": "Empresa",
    "escenarios": "De {base} podría pasar a…",
    "datos": "Esperado (datos)",
    "sim": "Esperado (simulación)",
    "ibm": "Esperado (IBM real)",
}
LECTURA_ESCENARIOS = "{baja} o {sube}"
LECTURA_CONCLUSION = (
    "Los tres números se parecen: la computadora cuántica reproduce la distribución que le "
    "dimos. Eso no significa que sepa qué va a pasar."
)
NOTA_DIFERENCIAS = (
    "Las pequeñas diferencias vienen del azar y de las imperfecciones de la máquina real."
)

# ---------------------------------------------------------------------------
# ¿Y si el mercado fuera cuántico?
# ---------------------------------------------------------------------------
PASEO_TITULO = "¿Y si el mercado fuera cuántico?"
PASEO_CONTROLES = "Ajusta el experimento"
PASEO_VECES = "×{veces:.1f} comparado con la moneda normal"
PASEO_INTRO = (
    "Imagina un precio que cada día sube o baja un escalón, como si se lanzara una moneda. "
    "Comparamos dos versiones de ese juego: con una **moneda normal** y con una **moneda "
    "cuántica**."
)
PASEO_PASOS = "Número de pasos (días)"
PASEO_MONEDA = "Moneda inicial"
PASEO_MONEDAS = {
    "simetrica": "Equilibrada (no favorece a ningún lado)",
    "sesgada": "Inclinada (empieza «apuntando» a la baja)",
}
PASEO_MONEDA_AYUDA = (
    "Es el estado inicial de la moneda cuántica. Equilibrada = (|0⟩ + i|1⟩)/√2. "
    "Inclinada = |0⟩. En la moneda normal no cambia nada."
)
PASEO_OBSERVAR = "Observar en cada paso"
PASEO_OBSERVAR_AYUDA = (
    "Mirar la moneda cada día obliga a que tenga un resultado definido. "
    "Así se pierde la «memoria» cuántica y el juego vuelve a ser como el normal."
)
PASEO_CLASICO = "Moneda normal (clásico)"
PASEO_CUANTICO = "Moneda cuántica"
PASEO_CUANTICO_OBS = "Moneda cuántica, observada cada paso"
PASEO_EJE_X = "Escalones arriba (+) o abajo (−) del precio inicial"
PASEO_EJE_Y = "Probabilidad"
PASEO_EXPLICACION = (
    "En el modelo clásico, lo más probable es quedar cerca de donde empezaste. En el modelo "
    "cuántico, los caminos se interfieren: algunos se refuerzan y otros se cancelan, y el "
    "precio se reparte hacia los extremos. **Influye lo que ocurre y también lo que pudo ocurrir.**"
)
PASEO_EXPLICACION_OBS = (
    "Con «Observar en cada paso» activado, la curva cuántica cae justo encima de la clásica: "
    "observar en cada etapa hace que el sistema pierda la memoria y se comporte como el caso "
    "clásico (Guía Cuántica, «Secuencias de observación»)."
)
PASEO_NOTA = (
    "Esta sección es un **cálculo exacto del modelo cuántico** hecho en tu computadora, no una "
    "ejecución en IBM. Un paseo de 100 pasos necesita un circuito demasiado largo para las "
    "máquinas actuales: el ruido lo destruiría. Fuente de la idea: Orrell, *Quantum Economics "
    "and Finance* (diapositiva «Métodos cuánticos (III)»)."
)
PASEO_METRICA_CLASICO = "Qué tan lejos suele terminar (moneda normal)"
PASEO_METRICA_CUANTICO = "Qué tan lejos suele terminar (moneda cuántica)"
PASEO_METRICA_AYUDA = "Distancia típica al punto de partida, en escalones (desviación estándar)."

# ---------------------------------------------------------------------------
# ¿Cómo funciona?
# ---------------------------------------------------------------------------
COMO_TITULO = "¿Cómo funciona?"
COMO_SUBTITULO = "Lo que pasa por dentro del programa, explicado paso a paso."
COMO_TABS = ["El circuito", "Paso a paso", "Conceptos de la Guía", "Límites honestos"]
COMO_CIRCUITO = "El circuito que se envía a IBM"
COMO_CIRCUITO_NOTA = (
    "Cada línea horizontal es un qubit (una empresa, de arriba hacia abajo en el orden de la "
    "lista). La caja **Ry** es la rotación que lo prepara y el símbolo del medidor es la medición."
)
COMO_PASOS_TITULO = "Paso a paso"
COMO_PASOS = [
    ("Preparar", "Cada qubit empieza en |0⟩ («baja»)."),
    ("Rotar", "Lo giramos un ángulo θ = 2·arcsin(√p), donde p es la fracción de meses en que "
              "la empresa subió. Así la probabilidad de medir «sube» queda exactamente en p."),
    ("Medir", "Al medir, el qubit deja de estar «a la vez» en baja y sube y da un solo resultado: "
              "0 (baja) o 1 (sube)."),
    ("Repetir", "Hacemos eso {shots} veces y contamos cuántas salió «sube». No son {shots} días "
                "de bolsa: son {shots} repeticiones del mismo experimento."),
]
COMO_EJEMPLO = (
    "Ejemplo con **{nombre}**: subió {pct_sube} de los meses, así que θ = 2·arcsin(√{p:.3f}) "
    "= {theta:.3f} radianes ({grados:.1f}°)."
)
COMO_TABLA_TITULO = "Conceptos de la Guía Cuántica en el programa"
COMO_TABLA_COLUMNAS = ("Concepto de la Guía Cuántica", "Dónde aparece en el programa")
COMO_TABLA = [
    ("Ket |ψ⟩ y superposición",
     "El qubit de cada empresa antes de medir: |ψ⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩, «baja» y «sube» a la vez."),
    ("Regla de Born (|a|², |b|²)",
     "La probabilidad de medir «sube» es |sin(θ/2)|² = p. Por eso θ = 2·arcsin(√p)."),
    ("Espacio de estado (determinista) vs. espacio de medición (aleatorio)",
     "La rotación Ry siempre es la misma (determinista); los resultados de las 1,000 mediciones son aleatorios."),
    ("Postulado de proyección / colapso",
     "Cada medición equivale a «cerrar una transacción»: el estado colapsa a un único resultado."),
    ("Valor esperado ⟨s⟩ que no es un resultado posible",
     "El precio esperado (p. ej. {ejemplo}) cuando solo existen dos escenarios: ninguna medición da ese precio."),
    ("Interferencia y trayectorias de Feynman",
     "El paseo cuántico: los caminos se suman o se cancelan y el precio se reparte hacia los extremos."),
    ("Pérdida de memoria al observar en etapas intermedias",
     "La casilla «Observar en cada paso»: el paseo cuántico vuelve a la campana clásica."),
]
COMO_LIMITES_TITULO = "Límites honestos"
COMO_LIMITES = [
    "**No predice.** Solo describe lo que ya pasó y mide esas mismas probabilidades.",
    "**Los datos son del pasado.** Que una empresa haya subido 6 de cada 10 meses no dice nada "
    "seguro sobre el próximo mes.",
    "**No hay ventaja cuántica.** Este problema también se puede calcular fácilmente en una "
    "computadora normal; usamos IBM para mostrar cómo se representa y se mide una distribución.",
    "**Mercados eficientes.** Según la Hipótesis de Mercados Eficientes (y Malkiel, *Un paseo "
    "aleatorio por Wall Street*), los precios ya incorporan la información disponible, así que "
    "los patrones pasados no garantizan ganancias futuras.",
    "**Simplificación.** Cada empresa se mide por separado (sin relación entre ellas) y cada mes "
    "se reduce a dos escenarios: sube o baja.",
]
