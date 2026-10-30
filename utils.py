"""Utilidades compartidas por todas las páginas de la app."""
import io

import pandas as pd
import streamlit as st

# Orden y nombres de los módulos (la clave es la que se guarda en session_state)
MODULOS = [
    ("m1", "1 · Balance de materia"),
    ("m2", "2 · Balance energético"),
    ("m3", "3 · Cogeneración"),
    ("m4", "4 · Huella de carbono y costos"),
]
PAGINAS = {
    "m1": "pages/1_Balance_de_Materia.py",
    "m2": "pages/2_Balance_Energetico.py",
    "m3": "pages/3_Cogeneracion.py",
    "m4": "pages/4_Huella_y_Costos.py",
}


def configurar_pagina(titulo):
    """Configuración de página y panel de estado en la barra lateral.
    Debe ser lo primero que se llama en cada página."""
    st.set_page_config(
        page_title=f"{titulo} | Simulador azucarero",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    with st.sidebar:
        st.markdown("**Estado del proceso**")
        for clave, nombre in MODULOS:
            marca = "●" if clave in st.session_state else "○"
            st.markdown(f"{marca}&nbsp; {nombre}")
        st.caption("● calculado   ○ pendiente")
        if "m1" in st.session_state:
            st.caption(f"Base de cálculo: {st.session_state['m1']['tch']:.1f} TCH")


def invalidar(desde):
    """Borra los resultados de los módulos posteriores a `desde`
    (para que nunca queden cifras de una corrida anterior)."""
    claves = [c for c, _ in MODULOS]
    for k in claves[claves.index(desde) + 1:]:
        st.session_state.pop(k, None)


def requerir(*claves):
    """Bloquea la página si falta el resultado de algún módulo previo."""
    nombres = dict(MODULOS)
    for c in claves:
        if c not in st.session_state:
            st.warning(f"Este módulo necesita los resultados de «{nombres[c]}». Calcúlelo primero.")
            st.page_link(PAGINAS[c], label=f"Ir a {nombres[c]}")
            st.stop()


def encabezado(numero, titulo, descripcion):
    st.title(f"Módulo {numero} · {titulo}")
    st.caption(descripcion)
    st.divider()


def descarga_excel(tablas, nombre_archivo, key):
    """tablas: dict {nombre_hoja: DataFrame}"""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for hoja, df in tablas.items():
            df.to_excel(writer, sheet_name=hoja[:31], index=False)
    st.download_button(
        "Descargar tablas (Excel)", buf.getvalue(), file_name=nombre_archivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=key,
    )


def descarga_png(fig, nombre_archivo, key, etiqueta="Descargar gráfica (PNG)"):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    st.download_button(etiqueta, buf.getvalue(), file_name=nombre_archivo, mime="image/png", key=key)


def tabla(df):
    st.dataframe(df, use_container_width=True, hide_index=True)
