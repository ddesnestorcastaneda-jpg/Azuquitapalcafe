import streamlit as st

from utils import configurar_pagina, PAGINAS

configurar_pagina("Inicio")

st.title("Simulador de ingenio azucarero")
st.caption("Balance de materia · energía · cogeneración · huella de carbono y costos")
st.divider()

st.markdown(
    """
El simulador se ejecuta **módulo por módulo**. Cada módulo se calcula con un botón, muestra sus
resultados al terminar y deja habilitado el siguiente, que toma sus datos directamente del anterior.

1. **Balance de materia:** diagrama de bloques, balance por etapa e indicadores de composición.
2. **Balance energético:** consumo eléctrico (kWh) y de vapor de proceso (t/h) por equipo.
3. **Cogeneración:** ciclo Rankine con bagazo, generación y excedente eléctrico.
4. **Huella de carbono y costos:** emisiones del proceso, con comparativa opcional frente a gas natural o carbón.
"""
)

st.info(
    "Si recalcula un módulo, los resultados de los módulos siguientes se borran "
    "para evitar mezclar cifras de corridas distintas."
)

st.page_link(PAGINAS["m1"], label="Comenzar con el módulo 1 · Balance de materia")

with st.expander("Alcance y supuestos"):
    st.markdown(
        """
- **Alcance de la huella:** desde la molienda (módulo 1) en adelante. No incluye cosecha, recolección ni transporte de la caña.
- **CO₂ del bagazo:** se trata como biogénico neutro (solo se contabilizan CH₄ y N₂O), según el criterio IPCC.
- **Factores de emisión:** valores por defecto IPCC 2006; verifíquelos si los usará en un reporte formal.
- **Precios:** los valores iniciales son de referencia y se ajustan en el módulo 4.
- **Ubicación del ciclo de vapor:** Cali, presión atmosférica 0.90 bar.
"""
    )
