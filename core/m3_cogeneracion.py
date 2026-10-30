"""
MÓDULO 3: COGENERACIÓN, BALANCES Y DIAGRAMA T-s (AJUSTADO A CALI).
Cálculos y gráficas idénticos a la versión de Colab. Los datos de entrada salen
de los módulos 1 y 2 (bagazo, vapor de proceso y consumo eléctrico).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd


def calcular_m3(m1, m2, graficar=True):
    tch_actual = float(m1["tch"])

    # --------------------------------------------------------------------------
    # 1. PARÁMETROS TERMODINÁMICOS REALES Y TABLA IAPWS-IF97 (P_atm Cali = 0.90 bar)
    # --------------------------------------------------------------------------
    # Estado 1: Líquido Saturado (2.7 bar abs / 1.8 bar manométrica @ Cali)
    P1 = 2.70         # bar abs
    T1 = 130.05       # °C
    h1 = 546.31       # kJ/kg
    s1 = 1.6346       # kJ/kg·K (100% Líquido Saturado)

    # Estado 2: Líquido Comprimido (Salida de Bomba @ 45.0 bar abs / 44.1 bar manométrica)
    P2 = 45.00        # bar abs
    eta_bomba = 0.78
    w_bomba = 4.85    # kJ/kg real
    h2 = h1 + w_bomba # 551.16 kJ/kg
    s2 = 1.6390       # kJ/kg·K
    T2 = 131.20       # °C

    # Puntos de ebullición y cambio de fase en Caldera @ 45.0 bar abs
    T_sat_45bar = 257.41       # °C
    s_liq_sat_45bar = 2.8587   # kJ/kg·K (Límite sf @ 45 bar)
    s_vap_sat_45bar = 6.0217   # kJ/kg·K (Límite sg @ 45 bar)

    # Estado 3: Vapor Sobrecalentado (Salida Caldera @ 45.0 bar abs, 430 °C)
    P3 = 45.00        # bar abs
    T3 = 430.00       # °C
    h3 = 3278.40      # kJ/kg
    s3 = 6.8193       # kJ/kg·K

    # Estado 4: Vapor de Escape Turbina (Salida Turbina @ 2.7 bar abs, η_turbina = 82%)
    P4 = 2.70         # bar abs
    T4 = 142.50       # °C (Vapor de escape hacia el proceso)
    h4 = 2752.80      # kJ/kg
    s4 = 7.0850       # kJ/kg·K

    # Límite de entrada al domo durante la condensación en el proceso @ 2.7 bar abs
    s_vap_sat_2_7bar = 7.0269  # kJ/kg·K (sg @ 2.7 bar)

    # --------------------------------------------------------------------------
    # 2. BALANCES MÁSICOS, TÉRMICOS Y COGENERACIÓN
    # --------------------------------------------------------------------------
    # Demandas del Módulo 2 (vapor de escape total requerido por el proceso)
    v_proceso_th = float(m2["total_vapor_th"])
    m_dot_kg_s = (v_proceso_th * 1000.0) / 3600.0

    # Bagazo real del Módulo 1
    m_bagazo_disponible_th = float(m1["f_bagazo"])

    # Potencias y Consumos
    w_bomba_kwh = m_dot_kg_s * w_bomba
    q_caldera_kw = m_dot_kg_s * (h3 - h2)
    q_combustion_kw = q_caldera_kw / 0.80  # η_caldera = 80%

    # PCI Bagazo húmedo (50% humedad) ~7,600 kJ/kg
    m_bagazo_requerido_th = (q_combustion_kw / 7600.0) * 3600.0 / 1000.0

    w_electrico_bruto_kwh = m_dot_kg_s * (h3 - h4) * 0.96 # η_generador = 96%
    q_proceso_kw = m_dot_kg_s * (h4 - h1)  # Calor latente entregado al proceso

    # Consumo eléctrico total del Módulo 2 + trabajo de la bomba de este módulo
    autoconsumo_ingenio_kwh = float(m2["total_kwh"]) + w_bomba_kwh
    excedente_red_kwh = w_electrico_bruto_kwh - autoconsumo_ingenio_kwh

    # --------------------------------------------------------------------------
    # 3. TABLAS DETALLADAS DE RESULTADOS
    # --------------------------------------------------------------------------
    df_explicacion_cogeneracion = pd.DataFrame([
        {"Concepto Clave": "1. Biomasa Útil (Bagazo Módulo 1)", "Valor Obtenido": f"{m_bagazo_disponible_th:.2f} t/h", "Descripción del Balance": "Bagazo real de molienda disponible post-mermas."},
        {"Concepto Clave": "2. Consumo Bagazo en Caldera", "Valor Obtenido": f"{m_bagazo_requerido_th:.2f} t/h", "Descripción del Balance": "Bagazo quemado a 45 bar para cubrir la demanda térmica."},
        {"Concepto Clave": "3. Superávit de Bagazo Libres", "Valor Obtenido": f"{m_bagazo_disponible_th - m_bagazo_requerido_th:.2f} t/h", "Descripción del Balance": "Reserva sobrante para paradas, arranques o venta."},
        {"Concepto Clave": "4. Generación Eléctrica Bruta", "Valor Obtenido": f"{w_electrico_bruto_kwh:.2f} kWh", "Descripción del Balance": "Energía producida por expansión en la turbina de contrapresión."},
        {"Concepto Clave": "5. Excedente Vendible a la Red", "Valor Obtenido": f"{excedente_red_kwh:.2f} kWh", "Descripción del Balance": "Energía neta exportable tras cubrir autoconsumo total."}
    ])

    df_ciclo_rankine = pd.DataFrame([
        {"Componente del Ciclo": "1. Bomba de Agua de Alimentación", "Entrada / Estado": f"Líq. Sat. (2.7 bar, {T1:.1f} °C, s1={s1:.2f})", "Salida / Estado": f"Líq. Comp. (45 bar, {T2:.1f} °C, s2={s2:.2f})", "Trabajo Mec./Eléc. (kWh)": f"{w_bomba_kwh:.2f} kWh (Consumo)", "Calor / Potencia (kWth)": "-", "Métrica de Cogeneración": f"Δh = {w_bomba:.2f} kJ/kg (η = 78%)"},
        {"Componente del Ciclo": "2. Caldera Acuotubular de Bagazo", "Entrada / Estado": f"Agua Alimentación (45 bar, h2={h2:.1f})", "Salida / Estado": f"Vapor Sobrecal. (45 bar, {T3:.0f} °C, s3={s3:.2f})", "Trabajo Mec./Eléc. (kWh)": "-", "Calor / Potencia (kWth)": f"{q_caldera_kw:.1f} kWth", "Métrica de Cogeneración": f"Bagazo: {m_bagazo_requerido_th:.2f} t/h (η = 80%)"},
        {"Componente del Ciclo": "3. Turbina de Contrapresión y Generador", "Entrada / Estado": f"Vapor Sobrecal. (h3={h3:.0f})", "Salida / Estado": f"Vapor de Escape (2.7 bar, {T4:.1f} °C, s4={s4:.2f})", "Trabajo Mec./Eléc. (kWh)": f"{w_electrico_bruto_kwh:.2f} kWh (Generación)", "Calor / Potencia (kWth)": "-", "Métrica de Cogeneración": f"Excedente a Red = {excedente_red_kwh:.2f} kWh"},
        {"Componente del Ciclo": "4. Proceso Azucarero (Condensador)", "Entrada / Estado": f"Vapor de Escape (s4={s4:.2f})", "Salida / Estado": f"Condensado Líq. Sat. (s1={s1:.2f})", "Trabajo Mec./Eléc. (kWh)": "-", "Calor / Potencia (kWth)": f"{q_proceso_kw:.1f} kWth", "Métrica de Cogeneración": f"Vapor Proceso = {v_proceso_th:.2f} t/h"}
    ])

    res = {
        "tch": tch_actual,
        "q_caldera_kw": q_caldera_kw,
        "q_combustion_kw": q_combustion_kw,
        "m_bagazo_requerido_th": m_bagazo_requerido_th,
        "m_bagazo_disponible_th": m_bagazo_disponible_th,
        "w_electrico_bruto_kwh": w_electrico_bruto_kwh,
        "autoconsumo_ingenio_kwh": autoconsumo_ingenio_kwh,
        "excedente_red_kwh": excedente_red_kwh,
        "v_proceso_th": v_proceso_th,
        "w_bomba_kwh": w_bomba_kwh,
        "q_proceso_kw": q_proceso_kw,
        "df_explicacion": df_explicacion_cogeneracion,
        "df_rankine": df_ciclo_rankine
    }

    if not graficar:
        return res

    # --------------------------------------------------------------------------
    # 4. DASHBOARD GRÁFICO (ESQUEMA Y CAMPANA T-s CON PUNTOS REALES IAPWS-IF97)
    # --------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(22, 9.5))
    fig.suptitle(f"DASHBOARD TERMODINÁMICO DE COGENERACIÓN RANKINE ({tch_actual:.1f} TCH - CALI, 0.90 BAR ATM)",
                 fontsize=15, fontweight='bold', color='black')

    # --- ESQUEMA DE EQUIPOS (IZQUIERDA) ---
    ax1.set_xlim(-5, 105)
    ax1.set_ylim(-5, 105)
    ax1.axis('off')
    ax1.set_title("Esquema de Equipos del Ciclo de Potencia y Cogeneración", fontsize=12, fontweight='bold', pad=15)

    ax1.add_patch(patches.Circle((20, 20), radius=7, ec="black", fc="#E5E7EB", lw=2.5))
    ax1.add_patch(patches.Polygon([[15, 15], [15, 25], [25, 20]], closed=True, ec="black", fc="#3B82F6"))
    ax1.text(20, 8, f"1. BOMBA AGUA\nW_in = {w_bomba_kwh:.1f} kWh\n45 bar abs", ha="center", fontweight="bold", fontsize=9)

    ax1.add_patch(patches.FancyBboxPatch((10, 60), 20, 25, boxstyle="round,pad=0.3", ec="black", fc="#FEF3C7", lw=2.5))
    ax1.add_patch(patches.Circle((20, 72.5), radius=5, ec="#D97706", fc="#F59E0B", lw=3))
    ax1.text(20, 90, f"2. CALDERA BAGAZO\nQ_in = {q_caldera_kw:.0f} kWth\nBagazo: {m_bagazo_requerido_th:.1f} t/h", ha="center", fontweight="bold", fontsize=9)

    ax1.add_patch(patches.Polygon([[70, 80], [90, 85], [90, 60], [70, 65]], closed=True, ec="black", fc="#E0E7FF", lw=2.5))
    ax1.text(80, 90, f"3. TURBINA VAPOR\nW_gen = {w_electrico_bruto_kwh:.1f} kWh\nExcedente: {excedente_red_kwh:.1f} kWh", ha="center", fontweight="bold", fontsize=9)

    ax1.add_patch(patches.FancyBboxPatch((70, 10), 20, 22, boxstyle="round,pad=0.3", ec="black", fc="#DCFCE7", lw=2.5))
    y_serp = np.linspace(14, 28, 100)
    x_serp = 80 + 5 * np.sin(y_serp * 2)
    ax1.plot(x_serp, y_serp, color="#16A34A", lw=2.5)
    ax1.text(80, 2, f"4. PROCESO (CONDENSADOR)\nQ_out = {q_proceso_kw:.0f} kWth\nVapor: {v_proceso_th:.1f} t/h", ha="center", fontweight="bold", fontsize=9)

    ax1.annotate("", xy=(20, 58), xytext=(20, 28), arrowprops=dict(arrowstyle="->", color="black", lw=2.5))
    ax1.text(22, 43, f"Agua 45 bar\nh2={h2:.1f} kJ/kg", fontsize=8.5, fontweight="bold")

    ax1.annotate("", xy=(68, 72.5), xytext=(32, 72.5), arrowprops=dict(arrowstyle="->", color="red", lw=2.5))
    ax1.text(50, 76, f"Vapor Sobrecalentado 430°C\nh3={h3:.0f} kJ/kg", ha="center", fontsize=8.5, fontweight="bold", color="red")

    ax1.annotate("", xy=(80, 34), xytext=(80, 58), arrowprops=dict(arrowstyle="->", color="blue", lw=2.5))
    ax1.text(82, 46, f"Vapor Escape 2.7 bar\nh4={h4:.1f} kJ/kg", fontsize=8.5, fontweight="bold", color="blue")

    ax1.annotate("", xy=(28, 20), xytext=(68, 20), arrowprops=dict(arrowstyle="->", color="green", lw=2.5))
    ax1.text(48, 23, f"Condensado Líquido Sat. 130°C\nh1={h1:.1f} kJ/kg", ha="center", fontsize=8.5, fontweight="bold", color="green")

    # --- DIAGRAMA TERMODINÁMICO T-s (DERECHA) ---
    ax2.set_title("Diagrama Termodinámico T-s (Domos y Fases IAPWS-IF97)", fontsize=12, fontweight='bold', pad=15)
    ax2.set_xlabel("Entropía Específica, s (kJ/kg·K)", fontweight='bold')
    ax2.set_ylabel("Temperatura, T (°C)", fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.5)

    # TABLA DEL DOMO DE SATURACIÓN (T °C | sf | sg en kJ/kg·K)
    tabla_sat_iapws = [
        (0.01, 0.0000, 9.1556), (10, 0.1511, 8.8999), (20, 0.2965, 8.6661),
        (30, 0.4368, 8.4520), (40, 0.5724, 8.2555), (50, 0.7038, 8.0748),
        (60, 0.8313, 7.9082), (70, 0.9551, 7.7540), (80, 1.0756, 7.6111),
        (90, 1.1929, 7.4781), (100, 1.3072, 7.3542), (110, 1.4188, 7.2387),
        (120, 1.5279, 7.1296), (130, 1.6346, 7.0269), (140, 1.7392, 6.9299),
        (150, 1.8418, 6.8379), (160, 1.9427, 6.7502), (170, 2.0419, 6.6663),
        (180, 2.1396, 6.5857), (190, 2.2359, 6.5079), (200, 2.3309, 6.4323),
        (220, 2.5178, 6.2861), (240, 2.7015, 6.1437), (250, 2.7927, 6.0730),
        (300, 3.2548, 5.7042), (350, 3.7784, 5.2110)
    ]
    T_tab  = np.array([p[0] for p in tabla_sat_iapws])
    sf_tab = np.array([p[1] for p in tabla_sat_iapws])
    sg_tab = np.array([p[2] for p in tabla_sat_iapws])

    # Interpolación suave (PCHIP conserva la monotonía; si no hay scipy, usa lineal)
    try:
        from scipy.interpolate import PchipInterpolator
        _sf = PchipInterpolator(T_tab, sf_tab)
        _sg = PchipInterpolator(T_tab, sg_tab)
    except Exception:
        _sf = lambda T: np.interp(T, T_tab, sf_tab)
        _sg = lambda T: np.interp(T, T_tab, sg_tab)

    # Zona 350 °C → punto crítico (373.946 °C, 4.412): ley de potencias, cierra el domo redondeado
    T_crit, s_crit = 373.946, 4.4120
    T_a = np.linspace(T_tab[0], 350.0, 400)
    T_b = T_crit - (T_crit - 350.0) * np.linspace(1.0, 0.0, 200)[1:] ** 2
    fr = (T_crit - T_b) / (T_crit - 350.0)
    s_med = s_crit + (4.4947 - s_crit) * fr ** 0.264   # (sf+sg)/2
    s_semi = 0.7163 * fr ** 0.426                       # (sg-sf)/2
    T_domo  = np.concatenate([T_a, T_b])
    sf_domo = np.concatenate([_sf(T_a), s_med - s_semi])
    sg_domo = np.concatenate([_sg(T_a), s_med + s_semi])

    ax2.plot(sf_domo, T_domo, color='black', lw=2.5, label="Límite Líquido Saturado (sf)")
    ax2.plot(sg_domo, T_domo, color='black', lw=2.5, linestyle='--', label="Límite Vapor Saturado (sg)")

    # ----------------------------------------------------------------------
    # TRAYECTORIA DEL CICLO con curvas reales (no rectas entre vértices)
    # ----------------------------------------------------------------------
    K = 273.15
    # 1→2: bomba (casi vertical, compresión del líquido)
    # 2→2a: calentamiento del líquido a 45 bar, sigue la curva sf desplazada
    T_liq = np.linspace(T2, T_sat_45bar, 60)
    s_liq = _sf(T_liq) + (s2 - float(_sf(T2))) * (T_sat_45bar - T_liq) / (T_sat_45bar - T2)
    s_liq = s_liq + (s_liq_sat_45bar - s_liq[-1]) * (T_liq - T2) / (T_sat_45bar - T2)  # cierra exacto en 2a
    # 2a→2b: ebullición isotérmica (línea horizontal)
    # 2b→3: sobrecalentamiento a 45 bar: s = sg + cp·ln(T/Tsat) (curva logarítmica)
    T_sh = np.linspace(T_sat_45bar, T3, 60)
    cp_sh = (s3 - s_vap_sat_45bar) / np.log((T3 + K) / (T_sat_45bar + K))
    s_sh = s_vap_sat_45bar + cp_sh * np.log((T_sh + K) / (T_sat_45bar + K))
    # 3→4: expansión real irreversible (se dibuja como segmento)
    # 4→4a: enfriamiento del vapor de escape a 2.7 bar hasta saturación
    T_ds = np.linspace(T4, T1, 60)
    cp_ds = (s4 - s_vap_sat_2_7bar) / np.log((T4 + K) / (T1 + K))
    s_ds = s_vap_sat_2_7bar + cp_ds * np.log((T_ds + K) / (T1 + K))
    # 4a→1: condensación isotérmica hasta líquido saturado

    s_ciclo_real = np.concatenate([[s1], s_liq, [s_vap_sat_45bar], s_sh, [s4], s_ds, [s1]])
    T_ciclo_real = np.concatenate([[T1], T_liq, [T_sat_45bar], T_sh, [T4], T_ds, [T1]])

    # Sombrear trabajo y dibujar la línea del ciclo
    ax2.plot(s_ciclo_real, T_ciclo_real, color='#DC2626', lw=3, label="Ciclo Rankine Real")
    ax2.fill(s_ciclo_real, T_ciclo_real, color='#FCA5A5', alpha=0.35, label="Trabajo Neto Generado")
    # Vértices del ciclo
    ax2.plot([s1, s2, s_liq_sat_45bar, s_vap_sat_45bar, s3, s4],
             [T1, T2, T_sat_45bar, T_sat_45bar, T3, T4],
             linestyle='none', marker='o', markersize=5, color='#DC2626', zorder=5)
    # Referencia: expansión isentrópica ideal (vertical desde 3 hasta 2.7 bar)
    ax2.plot([s3, s3], [T3, T1], color='gray', lw=1.5, linestyle=':', label="Expansión isentrópica ideal (3→4s)")

    # Resaltar Estado 1 (Verde) y Estado 4 (Azul)
    ax2.plot(s1, T1, marker='o', markersize=10, color='green', zorder=6, label="Estado 1: Líquido Saturado 100%")
    ax2.plot(s4, T4, marker='o', markersize=10, color='blue', zorder=6, label="Estado 4: Vapor de Escape Turbina")

    # Anotaciones claras
    ax2.text(s1 + 0.15, T1 - 45, f"Estado 1 (LÍQUIDO SATURADO)\ns1={s1:.2f}, T={T1:.1f} °C", fontweight='bold', fontsize=8.5, color="green")
    ax2.text(s2 - 1.35, T2 + 40, f"Estado 2 (Líq. Comprimido)\ns2={s2:.2f}, P=45 bar abs", fontweight='bold', fontsize=8.5)
    ax2.text(s3 + 0.1, T3 + 5, f"Estado 3 (Vapor Sobrecal.)\ns3={s3:.2f}, T=430 °C", fontweight='bold', fontsize=8.5, color="red")
    ax2.text(s4 + 0.15, T4 - 5, f"Estado 4 (Vapor Escape)\ns4={s4:.2f}, T={T4:.1f} °C", fontweight='bold', fontsize=8.5, color="blue")

    # Flecha descriptiva de condensación
    ax2.annotate("CONDENSACIÓN EN PROCESO (4 → 1)\n(Cede calor latente y vuelve a Líquido Saturado)",
                 xy=(4.0, T1), xytext=(3.2, 60),
                 arrowprops=dict(arrowstyle="->", color="green", lw=2),
                 fontweight="bold", fontsize=8.5, color="green",
                 bbox=dict(boxstyle="round,pad=0.3", fc="#DCFCE7", ec="#16A34A"))

    ax2.set_xlim(-0.2, 9.4)
    ax2.set_ylim(0, 500)
    ax2.legend(loc="upper left", fontsize=8.5)

    fig.tight_layout()
    plt.close(fig)
    res["fig_dashboard"] = fig
    return res
