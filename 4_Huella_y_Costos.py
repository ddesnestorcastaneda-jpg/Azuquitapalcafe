import streamlit as st

from utils import (configurar_pagina, encabezado, requerir, tabla,
                   descarga_excel, descarga_png)
from core.m1_balance import calcular_m1
from core.m2_energia import calcular_m2
from core.m3_cogeneracion import calcular_m3
from core.m4_huella import calcular_m4

configurar_pagina("Huella de carbono y costos")
encabezado(4, "Huella de carbono y costos",
           "Emisiones del proceso desde el módulo 1 (sin cosecha ni transporte) y balance económico, "
           "con comparativa opcional frente a gas natural o carbón.")
requerir("m1", "m2", "m3")

m1 = st.session_state["m1"]
m2 = st.session_state["m2"]
m3 = st.session_state["m3"]

OPC_DATOS_SI = "Sí, continuar con los datos de los módulos anteriores"
OPC_DATOS_NO = "No, ingresar otra cantidad de TCH"
OPC_COMP_SI = "Sí, comparar con gas natural o carbón"
OPC_COMP_NO = "No, solo huella y costos del proceso con bagazo"

# --- Paso 1: datos base -------------------------------------------------------
st.subheader("1 · Datos base")
base = st.radio("¿Continuar con los datos de los módulos anteriores?",
                [OPC_DATOS_SI, OPC_DATOS_NO], index=None, key="m4_base")
if base is None:
    st.info("Responda para continuar.")
    st.stop()

tch_manual = None
if base == OPC_DATOS_NO:
    tch_manual = st.number_input("Caña molida (TCH)", min_value=1.0, max_value=2000.0,
                                 value=float(m1["tch"]), step=5.0, key="m4_tch")
    st.caption("Los módulos 1 a 3 se recalculan internamente con estas TCH, "
               "sin modificar los resultados guardados.")
else:
    st.caption(f"Se usan los resultados guardados ({m1['tch']:.1f} TCH).")

# --- Paso 2: comparativa ------------------------------------------------------
st.subheader("2 · Comparativa")
comp = st.radio("¿Desea hacer una comparativa?", [OPC_COMP_SI, OPC_COMP_NO],
                index=None, key="m4_comp")
if comp is None:
    st.info("Responda para continuar.")
    st.stop()

comparar = (comp == OPC_COMP_SI)
comb = None
if comparar:
    comb = st.selectbox("Combustible a comparar", ["Gas natural", "Carbón"], index=None,
                        placeholder="Seleccione una opción", key="m4_comb")
    if comb is None:
        st.info("Seleccione el combustible para continuar.")
        st.stop()
    st.caption("El combustible elegido sustituye todo el bagazo de la caldera "
               "y el bagazo liberado se vende.")

# --- Paso 3: precios ----------------------------------------------------------
st.subheader("3 · Precios")
st.caption("Los valores iniciales son de referencia; ajústelos a su caso.")
with st.form("m4_precios"):
    c1, c2 = st.columns(2)
    p_bag = c1.number_input("Bagazo (USD/t)", min_value=0.0, max_value=1000.0, value=12.0, step=1.0)
    p_el = c2.number_input("Electricidad vendida (USD/MWh)", min_value=0.0, max_value=1000.0, value=80.0, step=5.0)
    p_gas, p_car = 8.0, 110.0
    if comparar:
        c3, c4 = st.columns(2)
        p_gas = c3.number_input("Gas natural (USD/MMBtu)", min_value=0.0, max_value=1000.0, value=8.0, step=0.5)
        p_car = c4.number_input("Carbón (USD/t)", min_value=0.0, max_value=2000.0, value=110.0, step=5.0)
    enviar = st.form_submit_button("Calcular huella y costos", type="primary")

if enviar:
    with st.spinner("Calculando huella de carbono y costos..."):
        if base == OPC_DATOS_NO:
            m1x = calcular_m1(tch_manual, graficar=False)
            m2x = calcular_m2(m1x)
            m3x = calcular_m3(m1x, m2x, graficar=False)
        else:
            m1x, m2x, m3x = m1, m2, m3
        st.session_state["m4"] = calcular_m4(m1x, m2x, m3x, comparar, comb, p_bag, p_el, p_gas, p_car)
    st.rerun()

# --- Resultados ---------------------------------------------------------------
r = st.session_state.get("m4")
if r is None:
    st.stop()

st.divider()
etiqueta = f"comparativa con {r['comb_alt']}" if r["comparar"] else "sin comparativa"
st.subheader(f"Resultados para {r['tch']:.1f} TCH · {etiqueta}")
if r["aviso"]:
    st.warning(r["aviso"])

esc = r["escenarios"]
b0 = esc[0]
if r["comparar"]:
    b1 = esc[1]
    c = st.columns(4)
    c[0].metric("Huella base (bagazo)", f"{b0['total']:,.0f} kg CO₂e/h")
    c[1].metric(f"Huella con {r['comb_alt']}", f"{b1['total']:,.0f} kg CO₂e/h",
                delta=f"{b1['total'] - b0['total']:+,.0f} vs. base", delta_color="inverse")
    c[2].metric("Balance neto base", f"{b0['neto']:,.0f} USD/h")
    c[3].metric(f"Balance neto con {r['comb_alt']}", f"{b1['neto']:,.0f} USD/h",
                delta=f"{b1['neto'] - b0['neto']:+,.0f} vs. base")
else:
    c = st.columns(3)
    c[0].metric("Huella total (bagazo)", f"{b0['total']:,.0f} kg CO₂e/h")
    c[1].metric("Intensidad", f"{b0['kg_t_cana']:.2f} kg CO₂e/t caña")
    c[2].metric("Balance neto", f"{b0['neto']:,.0f} USD/h")

st.pyplot(r["fig"], use_container_width=True)

st.markdown("**Tabla 1 · Huella de carbono por escenario**")
tabla(r["df_emis"])
st.markdown("**Tabla 2 · Costos e ingresos por escenario (USD/h)**")
tabla(r["df_eco"])
st.caption("Criterio: el CO₂ del bagazo es biogénico neutro (solo se contabilizan CH₄ y N₂O). "
           "La electricidad propia no genera emisiones.")

d1, d2, _ = st.columns([1, 1, 2])
with d1:
    descarga_excel({"Huella": r["df_emis"], "Costos": r["df_eco"]}, "m4_huella_costos.xlsx", "m4_xlsx")
with d2:
    descarga_png(r["fig"], "m4_huella_costos.png", "m4_png")
