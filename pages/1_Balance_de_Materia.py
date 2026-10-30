import streamlit as st

from utils import (configurar_pagina, encabezado, invalidar, tabla,
                   descarga_excel, descarga_png, PAGINAS)
from core.m1_balance import calcular_m1

configurar_pagina("Balance de materia")
encabezado(1, "Balance de materia",
           "Diagrama de bloques, balance másico por etapa e indicadores de composición y proceso.")

# --- Entrada y cálculo -------------------------------------------------------
col_in, col_btn, _ = st.columns([1, 1, 2])
with col_in:
    tch = st.number_input("Caña molida (TCH)", min_value=1.0, max_value=2000.0,
                          value=150.0, step=5.0, key="m1_tch_input")
with col_btn:
    st.write("")
    st.write("")
    calcular = st.button("Calcular módulo 1", type="primary")

if calcular:
    with st.spinner("Calculando balance de materia..."):
        st.session_state["m1"] = calcular_m1(tch)
    invalidar("m1")
    st.rerun()

# --- Resultados --------------------------------------------------------------
r = st.session_state.get("m1")
if r is None:
    st.info("Defina las TCH y pulse «Calcular módulo 1» para ver los resultados.")
    st.stop()

if abs(r["tch"] - tch) > 1e-9:
    st.warning(f"Los resultados mostrados corresponden a {r['tch']:.1f} TCH. "
               "Pulse «Calcular módulo 1» para actualizarlos con el nuevo valor.")

st.subheader(f"Resultados para {r['tch']:.1f} TCH")
c = st.columns(6)
c[0].metric("Azúcar final", f"{r['f_azucar_final']:.2f} t/h")
c[1].metric("Rendimiento", f"{r['f_azucar_final'] / r['tch'] * 100:.2f} % caña")
c[2].metric("Bagazo", f"{r['f_bagazo']:.1f} t/h")
c[3].metric("Melaza final", f"{r['f_melaza']:.1f} t/h")
c[4].metric("Recuperación SJM", f"{r['recuperacion_sjm']:.2f} %")
c[5].metric("Caída de pureza", f"{r['caida_pureza']:.2f} u")

tab_diag, tab_tabla, tab_dash = st.tabs(["Diagrama de bloques", "Tabla de balance", "Dashboard analítico"])
with tab_diag:
    st.pyplot(r["fig_diagrama"], use_container_width=True)
    descarga_png(r["fig_diagrama"], "m1_diagrama_bloques.png", "m1_png_diag")
with tab_tabla:
    tabla(r["df_balance"])
    descarga_excel({"Balance M1": r["df_balance"]}, "m1_balance_materia.xlsx", "m1_xlsx")
with tab_dash:
    st.pyplot(r["fig_dashboard"], use_container_width=True)
    descarga_png(r["fig_dashboard"], "m1_dashboard.png", "m1_png_dash")

st.divider()
st.page_link(PAGINAS["m2"], label="Siguiente: módulo 2 · Balance energético")
