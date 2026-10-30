import streamlit as st

from utils import (configurar_pagina, encabezado, requerir, invalidar, tabla,
                   descarga_excel, PAGINAS)
from core.m2_energia import calcular_m2

configurar_pagina("Balance energético")
encabezado(2, "Balance energético",
           "Consumo eléctrico real (kWh) y vapor de proceso (t/h) por equipo.")
requerir("m1")

m1 = st.session_state["m1"]
st.markdown(f"**Datos recibidos del módulo 1:** {m1['tch']:.1f} TCH de caña.")

if st.button("Calcular módulo 2", type="primary"):
    with st.spinner("Calculando balance energético..."):
        st.session_state["m2"] = calcular_m2(m1)
    invalidar("m2")
    st.rerun()

r = st.session_state.get("m2")
if r is None:
    st.info("Pulse «Calcular módulo 2» para ver los resultados.")
    st.stop()

st.subheader(f"Resultados para {r['tch']:.1f} TCH")
c = st.columns(3)
c[0].metric("Trabajo eléctrico total", f"{r['total_kwh']:,.0f} kWh/h")
c[1].metric("Consumo específico", f"{r['kwh_por_t']:.2f} kWh/t caña")
c[2].metric("Vapor de escape total", f"{r['total_vapor_th']:.2f} t/h")

st.markdown("**Tabla 1 · Consumo de trabajo eléctrico real por equipo**")
tabla(r["df_electrico"])
st.markdown("**Tabla 2 · Consumo de vapor de proceso por equipo térmico**")
tabla(r["df_termico"])
descarga_excel({"Electrico": r["df_electrico"], "Termico": r["df_termico"]},
               "m2_balance_energetico.xlsx", "m2_xlsx")

st.divider()
st.page_link(PAGINAS["m3"], label="Siguiente: módulo 3 · Cogeneración")
