# Inversión cuántica para todos

Proyecto del curso **Teoría de Inversión** (UVG, Prof. Mario A. Cuevas).

Es una aplicación que muestra cómo se comportaron en los últimos 5 años las 10 empresas más grandes de Wall Street. Después convierte esas probabilidades en qubits y las mide en una **computadora cuántica real de IBM**.

> El programa describe el pasado y mide esas probabilidades. **No adivina el futuro ni es una recomendación de inversión.**

---

## 1. Instalar (una sola vez)

Necesitas **Python 3.10 o superior**. Abre la terminal de VS Code dentro de la carpeta `inversion_cuantica` y escribe:

**Mac**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> Si la terminal muestra `(.venv)` al inicio de la línea, el entorno está activo. Cada vez que abras una terminal nueva, repite solo la línea `source .venv/bin/activate` (Mac) o `.venv\Scripts\activate` (Windows).

## 2. Configurar IBM Quantum (una sola vez)

Sin este paso la app funciona igual (con la simulación), pero no puede enviar trabajos a IBM.

1. Entra a **https://quantum.cloud.ibm.com** con tu cuenta.
2. **API key**: en la página principal (Dashboard), busca el cuadro *API key* y presiona **Create**. Copia la clave y guárdala en un lugar seguro, porque IBM la muestra una sola vez.
3. **CRN de la instancia**: en el menú, entra a **Instances**, abre tu instancia (plan *Open*, el gratuito) y copia el texto **CRN**, que empieza con `crn:v1:bluemix:...`.
4. Copia el archivo `.env.example` con el nombre `.env` y pega el CRN después de `IBM_INSTANCE=`.
5. En la terminal (con el entorno activo) escribe:
   ```bash
   python configurar_ibm.py
   ```
   Pega tu API key cuando te la pida. No se verá en pantalla, y es normal. Si todo sale bien, verás la lista de computadoras disponibles y el mensaje **"Conexión con IBM guardada correctamente"**.

La clave queda guardada en la configuración de Qiskit de tu usuario, **fuera de este proyecto**. Nunca se escribe en ningún archivo de la carpeta.

## 3. Abrir la app

```bash
streamlit run app.py
```

Se abre sola en el navegador (si no, entra a http://localhost:8501). Para cerrarla, presiona `Ctrl + C` en la terminal.

## 4. Cómo se usa

| Sección | Qué hace |
|---|---|
| **Inicio** | Explica el programa y te deja elegir un monto de ejemplo ($100 a $10,000). |
| **Las 10 empresas** | Cómo le fue a cada empresa, con ejemplos de dinero y un semáforo de estabilidad. |
| **Pregúntale a IBM** | Un qubit por empresa. Se simula en tu computadora y se puede enviar a IBM. |
| **¿Y si el mercado fuera cuántico?** | Paseo aleatorio con moneda normal vs. moneda cuántica. |
| **¿Cómo funciona?** | El circuito, los conceptos de la Guía Cuántica y los límites del proyecto. |

### Si IBM tarda

- Al presionar **"Enviar a la computadora cuántica real de IBM"**, el trabajo entra a una **fila**. Puede tardar desde segundos hasta horas, según cuánta gente esté usando las máquinas.
- No hace falta esperar con la página abierta: el número del trabajo queda guardado en `cache/ibm_trabajo_pendiente.json`. Más tarde presiona **"Revisar si ya terminó"**.
- Cuando termina, el resultado se guarda en `cache/ibm_ultimo_resultado.json` y la app lo muestra siempre, **aunque IBM no esté disponible** después.
- El plan gratuito de IBM (*Open*) da **pocos minutos de uso al mes**. Por eso las 10 empresas se miden en un solo trabajo, y conviene no enviar trabajos de más.

### Si no hay internet

Los precios se guardan en `cache/precios.csv`. Si no hay conexión, la app usa esos datos y muestra la fecha en que se descargaron. Con el botón **"Actualizar datos"** se vuelven a descargar.

## 5. Precios de respaldo (opcional)

La fuente principal es Yahoo Finance y no necesita clave. Si falla, la app puede usar **Financial Modeling Prep (FMP)**: crea una clave gratuita en https://site.financialmodelingprep.com y ponla en `.env` después de `FMP_API_KEY=`.

## 6. Pruebas

```bash
pytest
```

Comprueban los cálculos financieros, el orden de los qubits, los límites de probabilidad 0 y 1, el paseo cuántico y qué pasa cuando no hay internet o no hay cuenta de IBM.

## 7. Archivos

| Archivo | Para qué sirve |
|---|---|
| `app.py` | La interfaz (pantallas y botones). |
| `textos.py` | Todos los textos que ve el usuario. |
| `estilo.css` | El diseño: tarjetas blancas, portada, barra lateral. |
| `.streamlit/config.toml` | Colores y tipos de letra de toda la app. |
| `logo.svg` | El logo del átomo de la barra lateral. |
| `config.py` | Empresas, parámetros, colores y umbrales (fácil de editar). |
| `datos.py` | Descarga de precios, datos guardados y cálculos. |
| `cuantico.py` | Circuito, simulación y conexión con IBM. |
| `paseo.py` | Paseo clásico vs. paseo cuántico. |
| `configurar_ibm.py` | Guarda la cuenta de IBM (se corre una vez). |
| `referencia/` | Los dos programas originales, sin cambios. |
| `GUION_PRESENTACION.md` | Guion para exponer en clase. |

## 8. Nota técnica

`requirements.txt` fija **Qiskit 2.4**. Las versiones 2.5 y 2.6 cierran la app con un error de memoria (*Segmentation fault*) en Mac cuando se usan dentro de Streamlit, porque Qiskit se carga en un hilo y se usa en otro. Si en el futuro se actualiza Qiskit, hay que volver a probar `streamlit run app.py` y abrir la sección "Pregúntale a IBM".
