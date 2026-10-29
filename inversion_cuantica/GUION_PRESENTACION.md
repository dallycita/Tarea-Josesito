# Guion de presentación (3–5 minutos)

**Inversión cuántica para todos: diez empresas, diez qubits**

> Consejo: antes de la clase, abre la app (`streamlit run app.py`) y ejecuta una vez en IBM real para tener un resultado guardado. Si en clase hay fila larga en IBM, muestra el último resultado guardado. Los números de este guion son de los datos de octubre de 2026 y pueden cambiar un poco al actualizar los precios.

---

### 1. De dónde partimos (30 s) · *Pantalla: Inicio*

"En el primer experimento, «Dos escenarios, un qubit», partí de una acción imaginaria de 100 dólares que podía bajar a 98 o subir a 102. Usé una compuerta Hadamard, que siempre da 50 % y 50 %. En `ibm_marrakesh` obtuve 499 ceros y 501 unos.

Ese experimento tenía dos límites: la acción era inventada y la probabilidad la elegí yo. Si aplicaba Hadamard a diez empresas, las diez salían iguales. Este proyecto corrige las dos cosas."

### 2. Datos reales (1 min) · *Pantalla: Las 10 empresas*

"Tomé las 10 empresas más grandes de Wall Street y descargué sus precios mensuales de los últimos 5 años. Para cada una calculé, en lenguaje simple:

- cuántos meses de cada 10 subió,
- cuánto habrían crecido 100 dólares,
- qué tan movida es (el semáforo, que en finanzas se llama volatilidad),
- y su peor caída.

Por ejemplo, Eli Lilly subió 64 % de los meses y Tesla solo 47 %. Ya no son todas iguales. Ordené las empresas por «ganancia por cada unidad de susto», que es el índice de Sharpe explicado sin jerga."

### 3. Un qubit por empresa (1 min 30 s) · *Pantalla: Pregúntale a IBM*

"Cada empresa es un qubit: |ψ⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩, donde 0 es «baja» y 1 es «sube».

Según la **regla de Born**, la probabilidad de medir 1 es sin²(θ/2). Si quiero que sea igual a la probabilidad real de subir, el ángulo debe ser **θ = 2·arcsin(√p)**. Así reemplacé la Hadamard por una rotación RY con el ángulo de cada empresa.

Los diez qubits van en **un solo circuito**, así IBM mide las diez empresas en un solo trabajo y gasto menos del tiempo gratuito.

La preparación es determinista (**espacio de estado**). Las 1,000 mediciones son aleatorias (**espacio de medición**). Cada medición es como **cerrar una transacción**: el estado colapsa a un solo resultado.

*(Mostrar la gráfica.)* Las barras de los datos, de la simulación y de IBM se parecen. Las diferencias pequeñas vienen del azar y del ruido de la máquina real."

### 4. Lectura financiera (30 s) · *Misma pantalla, pestaña «Lectura financiera»*

"Los 98 y 102 inventados ahora salen de los datos. Por ejemplo, para Nvidia, de 100 dólares podría pasar a unos 90 o a unos 113 en un mes. El precio esperado mezcla los dos escenarios según cuántas veces salió «sube».

Ese promedio, cerca de 104 dólares, **no es un resultado posible**: ninguna medición da 104. Es el **valor esperado ⟨s⟩** de la Guía Cuántica."

### 5. ¿Y si el mercado fuera cuántico? (1 min) · *Pantalla: paseo*

"Esta parte es un cálculo del modelo, no IBM: un paseo de 100 pasos sería demasiado largo para el hardware actual.

Con una moneda normal, el precio suele quedar cerca de donde empezó: la campana. Con una moneda cuántica, los caminos **interfieren**: unos se refuerzan y otros se cancelan, y el precio se va a los extremos. La distancia típica pasa de 10 a 54 escalones. Influye lo que ocurre y también lo que pudo ocurrir.

*(Marcar «Observar en cada paso».)* Si observo en cada paso, la curva cuántica cae justo sobre la clásica. Es lo que dice la Guía en «Secuencias de observación»: **observar en cada etapa hace que el sistema pierda la memoria**."

### 6. Cierre: lo logrado y lo que queda fuera (30 s) · *Pantalla: ¿Cómo funciona?*

"**Logramos:**
- usar datos reales de 10 empresas,
- preparar cada qubit con su probabilidad real mediante la regla de Born,
- medir las 10 en una computadora cuántica real de IBM,
- y mostrar todo en una app que cualquier persona puede usar.

**Queda fuera del alcance:**
- predecir precios o recomendar inversiones,
- las relaciones entre empresas (cada qubit se mide por separado),
- y una ventaja cuántica, porque este problema también se resuelve fácilmente en una computadora normal.

Además, según la Hipótesis de Mercados Eficientes y Malkiel, los patrones del pasado no garantizan ganancias futuras.

El programa muestra cómo se comportaron estas empresas y usa una computadora cuántica para representar y medir esas probabilidades. No adivina el futuro."
