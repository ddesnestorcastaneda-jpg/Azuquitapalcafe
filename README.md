# Simulador de ingenio azucarero (Streamlit)

Cuatro módulos que se calculan en cadena, uno por página:

1. Balance de materia (`core/m1_balance.py`)
2. Balance energético (`core/m2_energia.py`)
3. Cogeneración (`core/m3_cogeneracion.py`)
4. Huella de carbono y costos (`core/m4_huella.py`)

## Ejecutar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cómo funciona

- Cada página tiene su botón de cálculo y muestra resultados al terminar.
- Los módulos 2, 3 y 4 quedan bloqueados hasta que existan los resultados de los anteriores.
- Los resultados se guardan en `st.session_state` (`m1`, `m2`, `m3`, `m4`).
- Si se recalcula un módulo, se borran los resultados de los siguientes.
- La carpeta `core/` contiene solo cálculo y gráficas (sin interfaz); las páginas en `pages/` solo muestran.

## Ajustes frecuentes

- Factores de emisión, GWP y poder calorífico del carbón: parte superior de `core/m4_huella.py`.
- Precios iniciales: campos del formulario en `pages/4_Huella_y_Costos.py`.
- Tema: `.streamlit/config.toml`.

## Despliegue

Streamlit Community Cloud: subir esta carpeta a un repositorio de GitHub y elegir `app.py` como archivo principal.
