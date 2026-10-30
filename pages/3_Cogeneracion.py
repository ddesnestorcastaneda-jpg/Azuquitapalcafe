import streamlit as st

from utils import (configurar_pagina, encabezado, requerir, invalidar, tabla,
                   descarga_excel, descarga_png, PAGINAS)
from core.m3_cogeneracion import calcular_m3

configurar_pagina("Cogeneración")
encabezado(3, "Cogeneración",
           "Ciclo Rankine con caldera de bagazo y turbina de contrapresión (Cali, 0.90 bar).")
requerir("m1", "m2")

m1 = st.session_state["m1"]
m2 = st.session_state["m2"]
st.markdown(
    f"**Datos recibidos:** bagazo {m1['f_bagazo']:.1f} t/h (módulo 1) · "
    f"vapor de proceso {m2['total_vapor_th']:.2f} t/h y consumo eléctrico {m2['total_kwh']:,.0f} kWh/h (módulo 2)."
)

if st.button("Calcular módulo 3", type="primary"):
    with st.spinner("Calculando ciclo de cogeneración..."):
        st.session_state["m3"] = calcular_m3(m1, m2)
    invalidar("m3")
    st.rerun()

r = st.session_state.get("m3")
if r is None:
    st.info("Pulse «Calcular módulo 3» para ver los resultados.")
    st.stop()

st.subheader(f"Resultados para {r['tch']:.1f} TCH")
c = st.columns(5)
c[0].metric("Bagazo disponible", f"{r['m_bagazo_disponible_th']:.2f} t/h")
c[1].metric("Bagazo en caldera", f"{r['m_bagazo_requerido_th']:.2f} t/h")
c[2].metric("Superávit de bagazo", f"{r['m_bagazo_disponible_th'] - r['m_bagazo_requerido_th']:.2f} t/h")
c[3].metric("Generación bruta", f"{r['w_electrico_bruto_kwh']:,.0f} kWh/h")
c[4].metric("Excedente a la red", f"{r['excedente_red_kwh']:,.0f} kWh/h")

tab_graf, tab_tablas = st.tabs(["Dashboard termodinámico", "Tablas"])
with tab_graf:
    st.pyplot(r["fig_dashboard"], use_container_width=True)
    descarga_png(r["fig_dashboard"], "m3_dashboard_rankine.png", "m3_png")
with tab_tablas:
    st.markdown("**Bases de cogeneración y balance de biomasa**")
    tabla(r["df_explicacion"])
    st.markdown("**Balance seccionado del ciclo Rankine**")
    tabla(r["df_rankine"])
    descarga_excel({"Cogeneracion": r["df_explicacion"], "Rankine": r["df_rankine"]},
                   "m3_cogeneracion.xlsx", "m3_xlsx")

st.divider()
st.page_link(PAGINAS["m4"], label="Siguiente: módulo 4 · Huella de carbono y costos")
