"""
Inversión cuántica para todos: la interfaz gráfica.

Abrir con:  streamlit run app.py

Aquí solo va la interfaz. Los cálculos están en datos.py, cuantico.py y paseo.py,
todos los textos en textos.py y el diseño (tarjetas, portada, colores) en estilo.css
y .streamlit/config.toml.
"""

import base64
from datetime import datetime
from io import BytesIO

import matplotlib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import config
import cuantico
import datos
import paseo
import textos as T

matplotlib.use("Agg")  # dibujar el circuito sin abrir ventanas

st.set_page_config(page_title=T.TITULO_APP, page_icon="⚛️", layout="wide")
st.html(config.CARPETA / "estilo.css")

# ---------------------------------------------------------------------------
# Memoria de la sesión (lo que se recuerda entre clic y clic)
# ---------------------------------------------------------------------------
if "monto" not in st.session_state:
    st.session_state.monto = config.MONTO_DEFECTO
# El monto se puede cambiar en dos lugares (Inicio y barra lateral);
# los dos controles siempre muestran el mismo valor.
if "monto_inicio" not in st.session_state:
    st.session_state.monto_inicio = st.session_state.monto
if "monto_lateral" not in st.session_state:
    st.session_state.monto_lateral = st.session_state.monto
if "version_datos" not in st.session_state:
    st.session_state.version_datos = 0
if "n_simulacion" not in st.session_state:
    st.session_state.n_simulacion = 1
if "mensaje_ibm" not in st.session_state:
    st.session_state.mensaje_ibm = None
if "estado_ibm" not in st.session_state:
    st.session_state.estado_ibm = None


def cambiar_monto(control):
    """Se llama al mover un control del monto; copia el valor al otro control."""
    st.session_state.monto = st.session_state[control]
    st.session_state.monto_inicio = st.session_state.monto
    st.session_state.monto_lateral = st.session_state.monto


# ---------------------------------------------------------------------------
# Funciones con caché (Streamlit guarda el resultado para no repetir cálculos)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def cargar_precios(version):
    # version = 0 al abrir la app; sube en 1 cada vez que se presiona "Actualizar datos"
    return datos.obtener_precios(forzar=version > 0)


@st.cache_data(show_spinner=False)
def calcular_resumen(precios, monto):
    return datos.resumen(precios, monto)


@st.cache_data(show_spinner=False)
def simular(probabilidades, semilla):
    circuito = cuantico.construir_circuito(probabilidades)
    return cuantico.simular(circuito, config.SHOTS, semilla)


@st.cache_data(show_spinner=False)
def dibujo_circuito(probabilidades):
    # Estilo oscuro de IBM ("iqp-dark") con el fondo de las tarjetas y las rotaciones en dorado
    estilo = {
        "name": "iqp-dark",
        "backgroundcolor": "#0F1115",
        "displaycolor": {"ry": ["#C9A45C", "#0A0B0E"]},
    }
    figura = cuantico.construir_circuito(probabilidades).draw("mpl", fold=-1, style=estilo)
    imagen = BytesIO()
    figura.savefig(imagen, format="png", dpi=150, bbox_inches="tight", facecolor="#0F1115")
    return imagen.getvalue()


@st.cache_data(show_spinner=False)
def calcular_paseo(pasos, moneda, observar):
    clasico = paseo.paseo_clasico(pasos)
    cuantico_ = paseo.paseo_cuantico(pasos, moneda, observar)
    return paseo.solo_alcanzables(pasos, clasico, cuantico_)


# ---------------------------------------------------------------------------
# Piezas que se repiten
# ---------------------------------------------------------------------------
def dar_estilo(fig, altura=420):
    fig.update_layout(
        height=altura,
        plot_bgcolor="rgba(0,0,0,0)",   # transparente: se ve el fondo de la tarjeta
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=config.FUENTE_GRAFICAS, size=13, color=config.COLOR_TEXTO_SUAVE),
        hoverlabel=dict(bgcolor="#16181E", bordercolor=config.COLOR_DORADO,
                        font=dict(family=config.FUENTE_GRAFICAS, color=config.COLOR_TEXTO)),
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0,
                    font=dict(color=config.COLOR_TEXTO)),
        barcornerradius=5,              # barras con esquinas redondeadas
    )
    fig.update_xaxes(showgrid=False, linecolor=config.COLOR_REJILLA)
    fig.update_yaxes(gridcolor=config.COLOR_REJILLA, zeroline=False)
    return fig


def mostrar_grafica(fig, altura, key):
    # displayModeBar=False quita la barra de botones de plotly para que se vea más limpio
    st.plotly_chart(dar_estilo(fig, altura), key=key, config={"displayModeBar": False})


def encabezado(numero, titulo, subtitulo):
    """Indicador de pasos, título grande y una línea de explicación."""
    # Barra con los 4 pasos: los anteriores en dorado suave, el actual en dorado
    pasos = ""
    for i in range(1, len(PAGINAS)):
        if i < numero:
            clase = "item hecho"
        elif i == numero:
            clase = "item actual"
        else:
            clase = "item"
        pasos += f"<div class='{clase}'><span class='num'>0{i}</span>{PAGINAS[i].title}</div>"
    st.html(f"<div class='pasos'>{pasos}</div>")

    st.title(titulo)
    with st.container(key="subtitulo"):  # el estilo está en estilo.css (.st-key-subtitulo)
        st.markdown(subtitulo)


def paso_numerado(numero, titulo, detalle, key):
    """Tarjeta con un círculo numerado, un título y una explicación corta."""
    with st.container(border=True, key=key, height="stretch"):
        st.html(f"<div class='numero'>{numero}</div>")
        st.markdown(f"**{titulo}**")
        st.caption(detalle)


def botones_navegacion(actual):
    """Botones «Anterior» y «Siguiente» al final de cada sección."""
    st.write("")
    izquierda, derecha = st.columns(2)
    with izquierda:
        anterior = PAGINAS[actual - 1]
        if st.button(T.BOTON_ANTERIOR, icon=":material/arrow_back:", key="anterior"):
            st.switch_page(anterior)
    if actual < len(PAGINAS) - 1:
        siguiente = PAGINAS[actual + 1]
        with derecha.container(horizontal_alignment="right"):
            if st.button(T.BOTON_SIGUIENTE.format(titulo=siguiente.title), type="primary",
                         icon=":material/arrow_forward:", icon_position="right", key="siguiente"):
                st.switch_page(siguiente)


def pie():
    st.html(f"<div class='pie'><span><b>{T.AVISO_PIE}</b></span><span>{T.PIE_CURSO}</span></div>")


def aviso_sin_conexion():
    """Si no hubo internet, avisa que se usan los datos guardados."""
    if info_precios.get("desde_cache"):
        descarga = T.fecha_hora(datetime.fromisoformat(info_precios["fecha_descarga"]))
        st.warning(T.DATOS_DESDE_CACHE.format(descarga=descarga), icon=":material/wifi_off:")


def info_datos():
    """De dónde salen los precios, con el botón para actualizarlos."""
    descarga = T.fecha_hora(datetime.fromisoformat(info_precios["fecha_descarga"]))
    with st.container(horizontal=True, vertical_alignment="center"):
        st.caption(":material/database: " + T.DATOS_FECHA.format(
            fuente=info_precios["fuente"],
            inicio=T.fecha(precios.index[0]),
            fin=T.fecha(precios.index[-1]),
            descarga=descarga,
        ))
        if st.button(T.DATOS_BOTON_ACTUALIZAR, icon=":material/refresh:", type="tertiary"):
            st.session_state.version_datos += 1
            st.rerun()


def escenarios(ticker):
    """Escenarios de baja y subida, escalados al monto elegido."""
    escala = monto / 100
    baja = tabla.loc[ticker, "escenario_baja"] * escala
    sube = tabla.loc[ticker, "escenario_sube"] * escala
    return baja, sube


# ---------------------------------------------------------------------------
# 1. Inicio
# ---------------------------------------------------------------------------
def cinta_cotizaciones():
    """Cinta que se mueve con cuánto cambió cada empresa en el último año."""
    items = ""
    for t in tickers:
        cambio = tabla.loc[t, "crec_1a"] / monto - 1
        if cambio >= 0:
            clase, flecha = "sube", "▲"
        else:
            clase, flecha = "baja", "▼"
        items += (f"<span class='item'><span class='sigla'>{t}</span>"
                  f"<span class='nombre'>{config.NOMBRES[t]}</span>"
                  f"<span class='{clase}'>{flecha} {100 * abs(cambio):.1f} %</span></span>")
    # La lista va dos veces seguidas para que la animación no tenga cortes
    st.html(f"<div class='cinta'><div class='pista'>{items}{items}</div></div>")


def pantalla_inicio():
    # Palabra del título en cursiva dorada
    titulo = T.INICIO_TITULO.replace(T.INICIO_DESTACADO, f"<em>{T.INICIO_DESTACADO}</em>")
    fin = T.fecha(precios.index[-1])
    st.html(
        "<div class='portada'>"
        "<div class='luz dorada'></div><div class='luz azul'></div><div class='rejilla'></div>"
        "<div class='contenido'>"
        f"<div class='etiqueta'><span class='vivo'></span>{T.INICIO_ETIQUETA.format(fin=fin)}</div>"
        f"<div class='titulo'>{titulo}</div>"
        f"<div class='texto'>{T.INICIO_SUBTITULO}</div>"
        "</div></div>"
    )
    st.caption(T.CINTA_TITULO)
    cinta_cotizaciones()

    # Elegir el monto y empezar
    st.write("")
    with st.container(border=True, key="tarjeta_fija_monto"):
        izquierda, derecha = st.columns([3, 2], vertical_alignment="center", gap="large")
        with izquierda:
            st.markdown(f"### {T.INICIO_MONTO}")
            st.caption(T.INICIO_MONTO_AYUDA)
            st.slider(
                T.INICIO_MONTO,
                min_value=config.MONTO_MIN,
                max_value=config.MONTO_MAX,
                step=100,
                format="$%d",
                key="monto_inicio",
                on_change=cambiar_monto,
                args=("monto_inicio",),
                label_visibility="collapsed",
            )
        with derecha:
            if st.button(T.INICIO_BOTON, type="primary", icon=":material/arrow_forward:",
                         icon_position="right", width="stretch"):
                st.switch_page(PAGINAS[1])

    st.write("")
    st.subheader(T.INICIO_QUE_HAY)
    columnas = st.columns(3)
    for i in range(3):
        numero, titulo, detalle, boton = T.INICIO_PASOS[i]
        with columnas[i]:
            with st.container(border=True, key=f"tarjeta_inicio_{i}", height="stretch"):
                st.html(f"<div class='numero'>{numero}</div>")
                st.markdown(f"**{titulo}**")
                st.caption(detalle)
                if st.button(boton, key=f"ir_{i}", type="tertiary",
                             icon=":material/arrow_forward:", icon_position="right"):
                    st.switch_page(PAGINAS[i + 1])

    st.info(T.MENSAJE_CENTRAL, icon=":material/info:")


# ---------------------------------------------------------------------------
# 2. Las 10 empresas
# ---------------------------------------------------------------------------
def indicadores_empresas():
    """Fila de 4 indicadores: las empresas que destacan en algo."""
    crecio = tabla["crec_total"].idxmax()
    tranquila = tabla["volatilidad"].idxmin()
    meses = tabla["p_sube"].idxmax()
    sharpe = tabla["sharpe"].idxmax()

    c1, c2, c3, c4 = st.container(key="indicadores_empresas").columns(4)
    c1.metric(T.KPI_CRECIO, config.NOMBRES[crecio], border=True, delta_arrow="up",
              delta=T.KPI_CRECIO_DELTA.format(monto=T.dinero_md(monto),
                                              valor=T.dinero_md(tabla.loc[crecio, "crec_total"])))
    c2.metric(T.KPI_TRANQUILA, config.NOMBRES[tranquila], border=True, delta_color="off",
              delta_arrow="off",
              delta=T.KPI_TRANQUILA_DELTA.format(vol=T.pct(tabla.loc[tranquila, "volatilidad"], 0)))
    c3.metric(T.KPI_MESES, config.NOMBRES[meses], border=True, delta_color="off", delta_arrow="off",
              delta=T.KPI_MESES_DELTA.format(n=datos.de_cada_diez(tabla.loc[meses, "p_sube"])))
    c4.metric(T.KPI_SHARPE, config.NOMBRES[sharpe], border=True, delta_color="off", delta_arrow="off",
              delta=T.KPI_SHARPE_DELTA.format(valor=tabla.loc[sharpe, "sharpe"]), help=T.ORDEN_AYUDA)


def encabezado_empresa(ticker, destacada):
    """Logo con las siglas, nombre, descripción y etiquetas (semáforo y Top 3)."""
    fila = tabla.loc[ticker]
    icono, palabra, color = T.SEMAFORO[fila["semaforo"]]
    st.html(
        "<div class='empresa'>"
        f"<div class='logo'>{ticker}</div>"
        f"<div><div class='nombre'>{fila['nombre']}</div>"
        f"<div class='descripcion'>{config.DESCRIPCIONES[ticker]}</div></div>"
        "</div>"
    )
    with st.container(horizontal=True, gap="small"):
        st.badge(palabra, icon=icono, color=color,
                 help=T.SEMAFORO_AYUDA.format(vol=T.pct(fila["volatilidad"], 0)))
        if destacada:
            st.badge(T.ETIQUETA_TOP, icon=":material/star:", color="violet", help=T.ORDEN_AYUDA)


@st.dialog(T.FICHA_TITULO, width="large")
def ficha_empresa(ticker, destacada):
    """Ventana con todos los datos de una empresa. Se abre con el botón «Ver ficha»."""
    fila = tabla.loc[ticker]
    encabezado_empresa(ticker, destacada)
    st.write("")

    # Fila 1: lo que tendrías hoy y cuántos meses subió
    c1, c2, c3 = st.columns(3)
    cambio = fila["crec_1a"] / monto - 1
    c1.metric(T.TARJETA_1A.format(monto=T.dinero_md(monto)), T.dinero(fila["crec_1a"]),
              delta=f"{100 * cambio:+.1f} %", border=True)
    c2.metric(T.FICHA_MESES, T.FICHA_MESES_VALOR.format(n=datos.de_cada_diez(fila["p_sube"])),
              border=True)
    if fila["retorno_anual"] >= 0:
        titulo_anual = T.FICHA_ANUAL
    else:
        titulo_anual = T.FICHA_ANUAL_PERDIO
    c3.metric(titulo_anual, T.pct(abs(fila["retorno_anual"])), help=T.TARJETA_ANUAL_AYUDA, border=True)

    # Fila 2: los riesgos
    c1, c2, c3 = st.columns(3)
    c1.metric(T.FICHA_CAIDA.format(monto=T.dinero_md(monto)), T.dinero(monto * (1 + fila["peor_caida"])),
              delta=f"{100 * fila['peor_caida']:.0f} %", help=T.TARJETA_CAIDA_AYUDA, border=True)
    c2.metric(T.FICHA_VOLATILIDAD, T.pct(fila["volatilidad"], 0), help=T.SEMAFORO_AYUDA_CORTA, border=True)
    c3.metric(T.FICHA_SHARPE, T.NIVEL_SHARPE[fila["nivel_sharpe"]], help=T.ORDEN_AYUDA, border=True)

    # Gráfica de los 5 años
    st.markdown(f"##### {T.DETALLE_GRAFICA.format(monto=T.dinero_md(monto))}")
    serie = datos.serie_crecimiento(precios[ticker], monto)
    fig = go.Figure()
    fig.add_scatter(x=serie.index, y=serie.values, mode="lines",
                    line=dict(color=config.COLOR_DORADO, width=2),
                    fill="tozeroy", fillcolor="rgba(201, 164, 92, 0.10)",
                    hovertemplate="%{x|%b %Y}: $%{y:,.0f}<extra></extra>")
    fig.add_hline(y=monto, line_dash="dot", line_color=config.COLOR_TEXTO_SUAVE)
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")
    mostrar_grafica(fig, 300, f"grafica_ficha_{ticker}")


def tarjeta(ticker, destacada):
    """Tarjeta corta: solo lo esencial. El resto está en la ficha."""
    fila = tabla.loc[ticker]
    with st.container(border=True, key=f"tarjeta_empresa_{ticker}", height="stretch"):
        encabezado_empresa(ticker, destacada)

        # Dato principal con la mini gráfica del último año (13 meses = 12 cambios)
        serie = datos.serie_crecimiento(precios[ticker], monto)
        cambio = fila["crec_1a"] / monto - 1
        st.metric(
            T.TARJETA_1A.format(monto=T.dinero_md(monto)),
            T.dinero(fila["crec_1a"]),
            delta=f"{100 * cambio:+.1f} %",
            chart_data=serie.iloc[-13:].round(2).tolist(),
            chart_type="area",
        )
        if st.button(T.BOTON_VER_FICHA, key=f"ficha_{ticker}", icon=":material/open_in_full:",
                     width="stretch"):
            ficha_empresa(ticker, destacada)


def vista_tarjetas():
    # Una sola fila: ordenar (izquierda) y leyenda del semáforo (derecha)
    izquierda, derecha = st.columns(2, vertical_alignment="bottom")
    with izquierda:
        orden = st.segmented_control(T.ORDEN_ETIQUETA, list(T.ORDEN_OPCIONES.keys()),
                                     format_func=T.ORDEN_OPCIONES.get, default="sharpe",
                                     required=True, help=T.ORDEN_AYUDA, key="orden")
    if orden == "sharpe":
        ordenada = tabla.sort_values("sharpe", ascending=False)
    elif orden == "gano":
        ordenada = tabla.sort_values("crec_total", ascending=False)
    else:
        ordenada = tabla.sort_values("volatilidad", ascending=True)

    with derecha.container(horizontal=True, vertical_alignment="center", gap="small",
                           horizontal_alignment="right"):
        st.caption(T.SEMAFORO_LEYENDA)
        for clave in ["verde", "amarillo", "rojo"]:
            icono, palabra, color = T.SEMAFORO[clave]
            st.badge(palabra, icon=icono, color=color)

    # Las 3 con mejor relación ganancia/susto llevan una etiqueta
    mejores = list(tabla.sort_values("sharpe", ascending=False).index[:3])

    # Tarjetas de 3 en 3
    lista = list(ordenada.index)
    for inicio in range(0, len(lista), 3):
        columnas = st.columns(3)
        grupo = lista[inicio:inicio + 3]
        for i in range(len(grupo)):
            with columnas[i]:
                tarjeta(grupo[i], grupo[i] in mejores)


def vista_comparar():
    # Barras: cuánto valdría hoy el monto puesto hace 5 años
    with st.container(border=True, key="tarjeta_fija_barras"):
        st.markdown(f"#### {T.BARRAS_TITULO.format(monto=T.dinero_md(monto))}")
        barras = tabla.sort_values("crec_total")
        etiquetas = [T.dinero(v) for v in barras["crec_total"]]
        fig = go.Figure()
        fig.add_bar(x=barras["crec_total"], y=barras["nombre"], orientation="h",
                    marker_color=config.COLOR_SERIE, text=etiquetas, textposition="outside",
                    textfont=dict(color=config.COLOR_TEXTO),
                    cliponaxis=False, hovertemplate="%{y}: $%{x:,.0f}<extra></extra>")
        fig.add_vline(x=monto, line_dash="dot", line_color=config.COLOR_TEXTO_SUAVE,
                      annotation_text=f"{T.BARRAS_LINEA} ({T.dinero(monto)})", annotation_position="top")
        fig.update_layout(bargap=0.35)
        fig.update_xaxes(tickprefix="$", tickformat=",.0f", showgrid=True, gridcolor=config.COLOR_REJILLA)
        fig.update_yaxes(showgrid=False)
        mostrar_grafica(fig, 440, "barras_empresas")

    # Puntos: ganancia contra susto (riesgo contra rendimiento)
    with st.container(border=True, key="tarjeta_fija_riesgo"):
        st.markdown(f"#### {T.RIESGO_TITULO}")
        st.caption(T.RIESGO_NOTA)
        fig = go.Figure()
        fig.add_scatter(x=100 * tabla["volatilidad"], y=100 * tabla["retorno_anual"],
                        mode="markers+text", text=tickers, textposition="top center",
                        customdata=tabla["nombre"],
                        textfont=dict(color=config.COLOR_TEXTO, family="JetBrains Mono, monospace", size=11),
                        marker=dict(size=13, color=config.COLOR_DORADO, line=dict(color="#0A0B0E", width=2)),
                        hovertemplate="%{customdata}<br>Movimiento: %{x:.0f} %<br>Ganancia: %{y:.1f} %<extra></extra>")
        fig.update_xaxes(title=T.RIESGO_EJE_X, ticksuffix=" %", showgrid=True, gridcolor=config.COLOR_REJILLA)
        fig.update_yaxes(title=T.RIESGO_EJE_Y, ticksuffix=" %")
        mostrar_grafica(fig, 420, "riesgo_empresas")


def vista_tabla():
    nombres = T.TABLA_COLUMNAS
    columna_monto = nombres["crec_total"].format(monto=T.dinero(monto))
    vista = pd.DataFrame({
        nombres["nombre"]: tabla["nombre"],
        nombres["semaforo"]: [T.SEMAFORO[s][1] for s in tabla["semaforo"]],
        nombres["p_sube"]: 100 * tabla["p_sube"],
        nombres["retorno_anual"]: 100 * tabla["retorno_anual"],
        nombres["volatilidad"]: 100 * tabla["volatilidad"],
        nombres["peor_caida"]: 100 * tabla["peor_caida"],
        columna_monto: tabla["crec_total"],
        nombres["sharpe"]: tabla["sharpe"],
    }).sort_values(nombres["sharpe"], ascending=False)

    st.dataframe(
        vista,
        hide_index=True,
        column_config={
            nombres["p_sube"]: st.column_config.ProgressColumn(format="%.0f %%", min_value=0, max_value=100),
            nombres["retorno_anual"]: st.column_config.NumberColumn(format="%.1f %%", help=T.TARJETA_ANUAL_AYUDA),
            nombres["volatilidad"]: st.column_config.NumberColumn(format="%.0f %%", help=T.SEMAFORO_AYUDA_CORTA),
            nombres["peor_caida"]: st.column_config.NumberColumn(format="%.0f %%", help=T.TARJETA_CAIDA_AYUDA),
            columna_monto: st.column_config.NumberColumn(format="$%.0f"),
            nombres["sharpe"]: st.column_config.NumberColumn(format="%.2f", help=T.ORDEN_AYUDA),
        },
    )


def pantalla_empresas():
    encabezado(1, T.EMPRESAS_TITULO, T.EMPRESAS_INTRO)
    aviso_sin_conexion()
    st.markdown(f"##### {T.DESTACADAS_TITULO}")
    indicadores_empresas()
    st.write("")

    pestana_tarjetas, pestana_comparar, pestana_tabla = st.tabs(T.EMPRESAS_TABS)
    with pestana_tarjetas:
        vista_tarjetas()
    with pestana_comparar:
        vista_comparar()
    with pestana_tabla:
        vista_tabla()

    st.write("")
    info_datos()
    botones_navegacion(1)


# ---------------------------------------------------------------------------
# 3. Pregúntale a IBM
# ---------------------------------------------------------------------------
def mostrar_mensaje_ibm():
    if st.session_state.mensaje_ibm is None:
        return
    tipo, mensaje = st.session_state.mensaje_ibm
    if tipo == "exito":
        st.success(mensaje)
    elif tipo == "aviso":
        st.warning(mensaje)
    else:
        st.error(mensaje)


def panel_ibm():
    """Tarjeta de IBM: estado, botón de envío, revisión y último resultado guardado."""
    configurada = cuantico.cuenta_configurada()
    pendiente = cuantico.leer_pendiente()
    ultimo = cuantico.leer_ultimo_resultado()

    st.markdown(f"#### :material/cloud: {T.IBM_TARJETA_TITULO}")
    if not configurada:
        st.badge(T.IBM_ETIQUETA_SIN_CONFIGURAR, icon=":material/link_off:", color="gray")
    elif pendiente is not None:
        st.badge(T.IBM_ETIQUETA_EN_FILA, icon=":material/hourglass_top:", color="orange")
    elif ultimo is not None:
        st.badge(T.IBM_ETIQUETA_GUARDADO, icon=":material/check_circle:", color="green")
    else:
        st.badge(T.IBM_ETIQUETA_LISTA, icon=":material/check:", color="blue")
    st.caption(T.IBM_TARJETA_TEXTO)

    enviar = st.button(T.BOTON_ENVIAR, type="primary", icon=":material/cloud_upload:",
                       disabled=(not configurada) or (pendiente is not None))
    if enviar:
        with st.spinner(T.IBM_ENVIANDO):
            try:
                nuevo = cuantico.enviar_a_ibm(probabilidades)
                st.session_state.mensaje_ibm = ("exito", T.IBM_ENVIADO.format(maquina=nuevo["maquina"]))
                st.session_state.estado_ibm = None
            except cuantico.ErrorIBM as error:
                st.session_state.mensaje_ibm = ("error", str(error))
        st.rerun()

    if not configurada:
        st.info(T.IBM_NO_CONFIGURADO, icon=":material/settings:")

    if pendiente is not None:
        estado = st.session_state.estado_ibm or T.IBM_ESTADO_SIN_REVISAR
        fecha_envio = T.fecha_hora(datetime.fromisoformat(pendiente["fecha_envio"]))
        st.markdown(T.IBM_PENDIENTE.format(maquina=pendiente["maquina"], fecha=fecha_envio, estado=estado))
        if st.button(T.BOTON_REVISAR, icon=":material/sync:", disabled=not configurada):
            try:
                respuesta = cuantico.revisar_trabajo()
                st.session_state.estado_ibm = respuesta["mensaje"]
                if respuesta["estado"] == "DONE":
                    st.session_state.mensaje_ibm = ("exito", T.IBM_LISTO)
                elif respuesta["estado"] in ["ERROR", "CANCELLED"]:
                    st.session_state.mensaje_ibm = ("aviso", T.IBM_TERMINO_MAL.format(estado=respuesta["mensaje"]))
                else:
                    st.session_state.mensaje_ibm = None
            except cuantico.ErrorIBM as error:
                st.session_state.mensaje_ibm = ("error", str(error))
            st.rerun()

    mostrar_mensaje_ibm()

    if ultimo is None:
        st.caption(T.IBM_SIN_RESULTADO)
    else:
        fecha_resultado = T.fecha_hora(datetime.fromisoformat(ultimo["fecha_resultado"]))
        st.markdown(T.IBM_ULTIMO.format(maquina=ultimo["maquina"], fecha=fecha_resultado))
        # Avisar si IBM usó probabilidades distintas a las de hoy
        for t in tickers:
            if abs(ultimo["probabilidades"].get(t, 0) - probabilidades[t]) > 0.005:
                st.caption(T.IBM_PROBS_DISTINTAS)
                break
    return ultimo


def diferencia_promedio(medidas):
    """Diferencia promedio (en puntos de %) entre lo medido y los datos."""
    diferencias = []
    for t in tickers:
        diferencias.append(abs(medidas.get(t, 0) - probabilidades[t]))
    return 100 * sum(diferencias) / len(diferencias)


def pantalla_ibm():
    encabezado(2, T.IBM_TITULO, T.IBM_SUBTITULO)

    # La explicación queda guardada en un desplegable para quien quiera leerla
    with st.expander(T.IBM_EXPLICACION, icon=":material/school:"):
        columnas = st.columns(3)
        for i in range(3):
            numero, titulo, detalle = T.IBM_PASOS[i]
            with columnas[i]:
                paso_numerado(numero, titulo.format(shots=f"{config.SHOTS:,}"), detalle,
                              f"tarjeta_ibm_paso_{i}")
        st.caption(":material/help: " + T.IBM_QUBIT_AYUDA)

    # Dos formas de medir: simulación (instantánea) e IBM (máquina real)
    col_sim, col_ibm = st.columns(2)
    with col_sim:
        with st.container(border=True, key="tarjeta_fija_simulacion", height="stretch"):
            st.markdown(f"#### :material/computer: {T.SIM_TITULO}")
            st.badge(T.SIM_ETIQUETA, icon=":material/bolt:", color="green")
            st.caption(T.SIM_TEXTO)
            if st.button(T.BOTON_SIMULAR, icon=":material/replay:"):
                st.session_state.n_simulacion += 1
            n = st.session_state.n_simulacion
            st.caption(T.SIMULACION_HECHA.format(n=n, shots=f"{config.SHOTS:,}") + " " + T.SIMULACION_AYUDA)
    with col_ibm:
        with st.container(border=True, key="tarjeta_fija_ibm", height="stretch"):
            ultimo = panel_ibm()

    # Cada simulación usa una semilla distinta: la 1ª siempre da lo mismo
    semilla = config.SEMILLA_SIMULACION + st.session_state.n_simulacion - 1
    simulacion = cuantico.conteos_por_empresa(simular(probabilidades, semilla), tickers)
    if ultimo is not None:
        ibm = ultimo["marginales"]
    else:
        ibm = None

    pestana_resultados, pestana_lectura = st.tabs(T.IBM_TABS)

    # Gráfica: datos del pasado / simulación / IBM real
    with pestana_resultados:
        # Indicadores: qué tan parecidos son los resultados a los datos
        m1, m2 = st.columns(2)
        m1.metric(T.KPI_DIF_SIM, T.KPI_PUNTOS.format(x=diferencia_promedio(simulacion)),
                  help=T.KPI_DIF_AYUDA, border=True)
        if ibm is not None:
            m2.metric(T.KPI_DIF_IBM, T.KPI_PUNTOS.format(x=diferencia_promedio(ibm)),
                      help=T.KPI_DIF_AYUDA, border=True)
        else:
            m2.metric(T.KPI_DIF_IBM, T.KPI_SIN_IBM, help=T.KPI_DIF_AYUDA, border=True)
        with st.container(border=True, key="tarjeta_fija_grafica_ibm"):
            st.markdown(f"#### {T.GRAFICA_IBM_TITULO}")
            nombres = [config.NOMBRES[t] for t in tickers]
            fig = go.Figure()
            fig.add_bar(name=T.FUENTE_DATOS, x=nombres, y=[100 * probabilidades[t] for t in tickers],
                        marker_color=config.COLOR_DATOS, hovertemplate="%{x}: %{y:.1f} %")
            fig.add_bar(name=T.FUENTE_SIM, x=nombres, y=[100 * simulacion[t] for t in tickers],
                        marker_color=config.COLOR_SIMULACION, hovertemplate="%{x}: %{y:.1f} %")
            if ibm is not None:
                fig.add_bar(name=T.FUENTE_IBM, x=nombres, y=[100 * ibm.get(t, 0) for t in tickers],
                            marker_color=config.COLOR_IBM, hovertemplate="%{x}: %{y:.1f} %")
            fig.update_traces(marker_line_color="#0F1115", marker_line_width=2)
            fig.update_layout(barmode="group", bargap=0.25)
            fig.update_yaxes(title=T.GRAFICA_IBM_EJE, range=[0, 100], ticksuffix=" %")
            mostrar_grafica(fig, 420, "barras_ibm")
            st.caption(T.NOTA_DIFERENCIAS)

    # Lectura financiera
    with pestana_lectura:
        st.markdown(f"#### {T.LECTURA_TITULO.format(base=T.dinero_md(monto))}")
        st.write(T.LECTURA_INTRO)
        st.latex(T.LECTURA_FORMULA)

        columna_escenarios = T.LECTURA_COLUMNAS["escenarios"].format(base=T.dinero(monto))
        filas = []
        for t in tickers:
            baja, sube = escenarios(t)
            fila = {
                T.LECTURA_COLUMNAS["empresa"]: config.NOMBRES[t],
                columna_escenarios: T.LECTURA_ESCENARIOS.format(baja=T.dinero(baja), sube=T.dinero(sube)),
                T.LECTURA_COLUMNAS["datos"]: T.dinero(cuantico.precio_esperado(probabilidades[t], sube, baja), 2),
                T.LECTURA_COLUMNAS["sim"]: T.dinero(cuantico.precio_esperado(simulacion[t], sube, baja), 2),
            }
            if ibm is not None and t in ibm:
                fila[T.LECTURA_COLUMNAS["ibm"]] = T.dinero(cuantico.precio_esperado(ibm[t], sube, baja), 2)
            filas.append(fila)
        st.dataframe(pd.DataFrame(filas), hide_index=True)
        st.success(T.LECTURA_CONCLUSION, icon=":material/check_circle:")

    botones_navegacion(2)


# ---------------------------------------------------------------------------
# 4. ¿Y si el mercado fuera cuántico?
# ---------------------------------------------------------------------------
def dispersion(x, probabilidad):
    """Distancia típica al punto de partida (desviación estándar)."""
    media = (probabilidad * x).sum()
    varianza = (probabilidad * x ** 2).sum() - media ** 2
    return float(np.sqrt(varianza))


def pantalla_paseo():
    encabezado(3, T.PASEO_TITULO, T.PASEO_INTRO)

    with st.container(border=True, key="tarjeta_fija_controles"):
        st.markdown(f"**:material/tune: {T.PASEO_CONTROLES}**")
        col1, col2, col3 = st.columns([2, 2, 1.3], vertical_alignment="center")
        pasos = col1.slider(T.PASEO_PASOS, config.PASOS_MIN, config.PASOS_MAX, config.PASOS_DEFECTO, step=2)
        moneda = col2.selectbox(T.PASEO_MONEDA, list(T.PASEO_MONEDAS.keys()),
                                format_func=T.PASEO_MONEDAS.get, help=T.PASEO_MONEDA_AYUDA)
        observar = col3.toggle(T.PASEO_OBSERVAR, help=T.PASEO_OBSERVAR_AYUDA)

    x, clasico, cuant = calcular_paseo(pasos, moneda, observar)
    nombre_cuantico = T.PASEO_CUANTICO_OBS if observar else T.PASEO_CUANTICO

    with st.container(border=True, key="tarjeta_fija_grafica_paseo"):
        fig = go.Figure()
        fig.add_scatter(x=x, y=clasico, name=T.PASEO_CLASICO, mode="lines",
                        line=dict(color=config.COLOR_PASEO_CLASICO, width=2, dash="dash"))
        fig.add_scatter(x=x, y=cuant, name=nombre_cuantico, mode="lines",
                        line=dict(color=config.COLOR_PASEO_CUANTICO, width=2),
                        fill="tozeroy", fillcolor="rgba(184, 137, 58, 0.12)")
        fig.update_traces(hovertemplate="%{y:.2%}")
        fig.update_layout(hovermode="x unified")
        fig.update_xaxes(title=T.PASEO_EJE_X)
        fig.update_yaxes(title=T.PASEO_EJE_Y, tickformat=".0%", rangemode="tozero")
        mostrar_grafica(fig, 440, "grafica_paseo")

    d_clasico = dispersion(x, clasico)
    d_cuantico = dispersion(x, cuant)
    m1, m2 = st.columns(2)
    m1.metric(T.PASEO_METRICA_CLASICO, f"{d_clasico:.1f}", help=T.PASEO_METRICA_AYUDA, border=True)
    m2.metric(T.PASEO_METRICA_CUANTICO, f"{d_cuantico:.1f}", help=T.PASEO_METRICA_AYUDA, border=True,
              delta=T.PASEO_VECES.format(veces=d_cuantico / d_clasico), delta_color="off", delta_arrow="off")

    if observar:
        st.success(T.PASEO_EXPLICACION_OBS, icon=":material/visibility:")
    else:
        st.info(T.PASEO_EXPLICACION, icon=":material/lightbulb:")
    st.caption(T.PASEO_NOTA)

    botones_navegacion(3)


# ---------------------------------------------------------------------------
# 5. ¿Cómo funciona?
# ---------------------------------------------------------------------------
def pantalla_como():
    encabezado(4, T.COMO_TITULO, T.COMO_SUBTITULO)

    pestana_circuito, pestana_pasos, pestana_conceptos, pestana_limites = st.tabs(T.COMO_TABS)

    with pestana_circuito:
        with st.container(border=True, key="tarjeta_fija_circuito"):
            st.markdown(f"#### {T.COMO_CIRCUITO}")
            st.image(dibujo_circuito(probabilidades), width=650)
            leyenda = []
            for i in range(len(tickers)):
                leyenda.append(f"q{i} = {config.NOMBRES[tickers[i]]}")
            st.caption(T.COMO_CIRCUITO_NOTA + "  \n" + " · ".join(leyenda))

    # Ejemplo con la primera empresa de la lista
    ticker = tickers[0]
    p = probabilidades[ticker]
    theta = cuantico.angulo(p)

    with pestana_pasos:
        columnas = st.columns(4)
        for i in range(4):
            titulo, detalle = T.COMO_PASOS[i]
            with columnas[i]:
                paso_numerado(i + 1, titulo, detalle.format(shots=f"{config.SHOTS:,}"), f"tarjeta_como_paso_{i}")
        st.info(T.COMO_EJEMPLO.format(nombre=config.NOMBRES[ticker], pct_sube=T.pct(p, 0),
                                      p=p, theta=theta, grados=np.degrees(theta)),
                icon=":material/calculate:")

    with pestana_conceptos:
        baja, sube = escenarios(ticker)
        ejemplo = T.dinero(cuantico.precio_esperado(p, sube, baja), 2) + " en " + config.NOMBRES[ticker]
        concepto, donde = T.COMO_TABLA_COLUMNAS
        filas = []
        for c, d in T.COMO_TABLA:
            filas.append({concepto: c, donde: d.format(ejemplo=ejemplo)})
        st.dataframe(pd.DataFrame(filas), hide_index=True,
                     column_config={concepto: st.column_config.TextColumn(width="medium"),
                                    donde: st.column_config.TextColumn(width="large")})

    with pestana_limites:
        with st.container(border=True, key="tarjeta_fija_limites"):
            for linea in T.COMO_LIMITES:
                st.markdown(f":material/check_small: {linea}")

    botones_navegacion(4)


# ---------------------------------------------------------------------------
# Menú: las 5 secciones de la app
# ---------------------------------------------------------------------------
PAGINAS = [
    st.Page(pantalla_inicio, title=T.SECCIONES["inicio"], icon=":material/home:", default=True),
    st.Page(pantalla_empresas, title=T.SECCIONES["empresas"], icon=":material/apartment:"),
    st.Page(pantalla_ibm, title=T.SECCIONES["ibm"], icon=":material/memory:"),
    st.Page(pantalla_paseo, title=T.SECCIONES["paseo"], icon=":material/shuffle:"),
    st.Page(pantalla_como, title=T.SECCIONES["como"], icon=":material/menu_book:"),
]
# position="hidden": el menú lo dibujamos nosotros en la barra lateral
pagina = st.navigation(PAGINAS, position="hidden")

# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------
# El logo se mete dentro del HTML como texto (base64) para no depender de otro archivo
logo = base64.b64encode((config.CARPETA / "logo.svg").read_bytes()).decode()

with st.sidebar:
    st.html(
        "<div class='marca'>"
        f"<img src='data:image/svg+xml;base64,{logo}' width='42' height='42'>"
        f"<div><div class='nombre'>{T.MARCA_NOMBRE}</div><div class='curso'>{T.MARCA_CURSO}</div></div>"
        "</div>"
    )
    st.html(f"<div class='menu-titulo'>{T.MENU_TITULO}</div>")
    for una_pagina in PAGINAS:
        st.page_link(una_pagina)

    st.html(f"<div class='menu-titulo'>{T.MENU_MONTO}</div>")
    st.slider(
        T.MENU_MONTO,
        min_value=config.MONTO_MIN,
        max_value=config.MONTO_MAX,
        step=100,
        format="$%d",
        key="monto_lateral",
        on_change=cambiar_monto,
        args=("monto_lateral",),
        help=T.MENU_MONTO_AYUDA,
        label_visibility="collapsed",
    )

    with st.expander(T.GLOSARIO_TITULO, icon=":material/menu_book:"):
        for termino, significado in T.GLOSARIO:
            st.markdown(f"**{termino}.** {significado}")

# ---------------------------------------------------------------------------
# Datos que usan todas las pantallas
# ---------------------------------------------------------------------------
monto = st.session_state.monto

try:
    with st.spinner(T.DATOS_ACTUALIZANDO):
        precios, info_precios = cargar_precios(st.session_state.version_datos)
except ConnectionError as error:
    st.error(T.DATOS_ERROR.format(error=error))
    pie()
    st.stop()

tabla = calcular_resumen(precios, monto)
tickers = list(tabla.index)
probabilidades = {}  # ticker → probabilidad de subir
for t in tickers:
    probabilidades[t] = float(tabla.loc[t, "p_sube"])

# ---------------------------------------------------------------------------
# Mostrar la pantalla elegida
# ---------------------------------------------------------------------------
pagina.run()
pie()
