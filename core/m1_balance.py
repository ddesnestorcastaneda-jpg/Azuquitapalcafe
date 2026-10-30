"""
MÓDULO 1: BALANCE DE MATERIA, INDICADORES Y DASHBOARD ANALÍTICO.
Cálculos y gráficas idénticos a la versión de Colab; solo se eliminó la interfaz
(ipywidgets) para poder usarlo desde Streamlit.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd


def calcular_m1(tch=150.0, graficar=True):
    """Devuelve un diccionario con todos los resultados escalares, el DataFrame
    de balance y (si graficar=True) las figuras del diagrama y del dashboard."""
    tch = float(tch)

    # --------------------------------------------------------------------------
    # A. COMPOSICIÓN Y PARÁMETROS BASE (LITERATURA HUGOT / CHEN & CHOU)
    # --------------------------------------------------------------------------
    brix_cana = 14.0       # % Brix en caña
    fibra_cana = 13.0      # % Fibra en caña
    pol_cana = 12.18       # % Pol en caña (Pureza Jugo Mixto ~87%)

    # --- 1. MESA DE ALIMENTACIÓN ---
    merma_mesa = tch * 0.002
    f1_cana = tch - merma_mesa

    # --- 2. PICADORAS Y DESFIBRADOR ---
    merma_prep = f1_cana * 0.003
    f2_prep = f1_cana - merma_prep

    # --- 3. TÁNDEM DE MOLINOS ---
    f_agua_imb = tch * 0.28   # Imbibición agua (~28% sobre caña)
    merma_molinos = (f2_prep + f_agua_imb) * 0.005 # Derrames / bacteriológico

    # Bagazo (~47.5% fibra, 50% agua, 2.5% Brix)
    f_bagazo = (f2_prep * (fibra_cana / 100.0)) / 0.475
    brix_bagazo_t = f_bagazo * 0.025

    f_jugo_ext = (f2_prep + f_agua_imb) - f_bagazo - merma_molinos
    brix_jugo_ext = (f2_prep * (brix_cana / 100.0)) - brix_bagazo_t
    pol_jugo_ext = (f2_prep * (pol_cana / 100.0)) - (brix_bagazo_t * 0.75)

    # --- 9. FILTRO ROTATORIO DE VACÍO ---
    f_cachaza = tch * 0.035             # Cachaza seca (~3.5%)
    brix_cachaza_t = f_cachaza * 0.015
    pol_cachaza_t = brix_cachaza_t * 0.60

    f_lodo = tch * 0.12                 # Lodos del clarificador
    brix_lodo_t = f_lodo * 0.08
    pol_lodo_t = brix_lodo_t * 0.85

    f_agua_lav_filtro = tch * 0.01
    merma_filtro = f_lodo * 0.003

    f_filtrado = f_lodo + f_agua_lav_filtro - f_cachaza - merma_filtro
    brix_filtrado_t = brix_lodo_t - brix_cachaza_t
    pol_filtrado_t = pol_lodo_t - pol_cachaza_t

    # --- 4, 5, 6, 7. JUGO MIXTO Y PRE-TRATAMIENTO ---
    f_jugo_mixto = f_jugo_ext + f_filtrado
    brix_jugo_mixto_t = brix_jugo_ext + brix_filtrado_t
    pol_jugo_mixto_t = pol_jugo_ext + pol_filtrado_t

    bx_mixto = (brix_jugo_mixto_t / f_jugo_mixto) * 100.0
    pol_mixto = (pol_jugo_mixto_t / f_jugo_mixto) * 100.0
    pureza_mixto = (pol_mixto / bx_mixto) * 100.0

    merma_calentamiento = f_jugo_mixto * 0.002
    f_jugo_encalado = (f_jugo_mixto * 1.002) - merma_calentamiento

    # --- 8. CLARIFICADOR DE JUGO ---
    f_jugo_clarificado = f_jugo_encalado - f_lodo
    brix_clarificado_t = brix_jugo_mixto_t - brix_lodo_t
    pol_clarificado_t = pol_jugo_mixto_t - pol_lodo_t

    bx_clarificado = (brix_clarificado_t / f_jugo_clarificado) * 100.0
    pol_clarificado = (pol_clarificado_t / f_jugo_clarificado) * 100.0
    pureza_clarificado = (pol_clarificado / bx_clarificado) * 100.0

    # --- 10. EVAPORADORES DE MÚLTIPLE EFECTO ---
    bx_meladura = 65.0
    f_meladura = brix_clarificado_t / (bx_meladura / 100.0)
    v_evaporadores = f_jugo_clarificado - f_meladura
    pureza_meladura = pureza_clarificado
    pol_meladura = bx_meladura * (pureza_meladura / 100.0)

    # --- 11 y 12. TACHOS AL VACÍO Y CRISTALIZACIÓN ---
    bx_masa_cocida = 90.0
    f_masa_cocida = brix_clarificado_t / (bx_masa_cocida / 100.0)
    v_tachos = f_meladura - f_masa_cocida
    pureza_masa_cocida = pureza_meladura

    # --- 13, 14, 15. CENTRÍFUGAS, SECADO Y ZARANDA ---
    f_azucar_comercial_teorico = tch * 0.108
    f_azucar_humedo = f_azucar_comercial_teorico / 0.995
    f_melaza = f_masa_cocida - f_azucar_humedo

    v_secador = f_azucar_humedo - f_azucar_comercial_teorico
    merma_polvillo_azucar = f_azucar_comercial_teorico * 0.0015
    f_azucar_final = f_azucar_comercial_teorico - merma_polvillo_azucar

    v_total = v_evaporadores + v_tachos + v_secador
    mermas_totales = merma_mesa + merma_prep + merma_molinos + merma_filtro + merma_calentamiento + merma_polvillo_azucar

    # Purezas clave para el balance fisicoquímico
    pureza_azucar = 99.95
    pureza_melaza = 38.50  # Pureza típica de agotamiento de miel final B/C

    # --------------------------------------------------------------------------
    # B. CÁLCULO DE LOS 4 INDICADORES DE COMPOSICIÓN Y PROCESO
    # --------------------------------------------------------------------------
    caida_pureza = pureza_meladura - pureza_melaza

    recirculacion_mieles_pct = ((f_masa_cocida - f_meladura) / f_meladura) * 100.0 + 32.5

    S = pureza_azucar / 100.0
    J = pureza_meladura / 100.0
    M = pureza_melaza / 100.0
    recuperacion_sjm = (S * (J - M)) / (J * (S - M)) * 100.0

    # --------------------------------------------------------------------------
    # RESULTADOS ESCALARES (para los módulos siguientes)
    # --------------------------------------------------------------------------
    _snapshot = dict(locals())
    res = {k: float(v) for k, v in _snapshot.items()
           if isinstance(v, (int, float, np.floating)) and not isinstance(v, bool) and not k.startswith("_")}

    # --- TABLA COMPLETA DE BALANCES Y COMPOSICIÓN ---
    res["df_balance"] = pd.DataFrame([
        {"Bloque Unitario": "1. Mesa de Alimentación", "Entrada (t/h)": tch, "Salida Principal (t/h)": f1_cana, "Concentración (°Bx)": f"{brix_cana:.1f}°Bx", "Pureza (%)": f"{pureza_mixto:.1f}%", "Merma / Salida (t/h)": f"Merma: {merma_mesa:.2f}"},
        {"Bloque Unitario": "2. Picadoras / Desfibrador", "Entrada (t/h)": f1_cana, "Salida Principal (t/h)": f2_prep, "Concentración (°Bx)": f"{brix_cana:.1f}°Bx", "Pureza (%)": f"{pureza_mixto:.1f}%", "Merma / Salida (t/h)": f"Merma: {merma_prep:.2f}"},
        {"Bloque Unitario": "3. Tándem de Molinos", "Entrada (t/h)": f2_prep + f_agua_imb, "Salida Principal (t/h)": f_jugo_ext, "Concentración (°Bx)": f"{bx_mixto:.1f}°Bx", "Pureza (%)": f"{pureza_mixto:.1f}%", "Merma / Salida (t/h)": f"Bagazo: {f_bagazo:.1f} | Pérd: {merma_molinos:.2f}"},
        {"Bloque Unitario": "4 a 7. Calentamiento / Sulfitación", "Entrada (t/h)": f_jugo_mixto, "Salida Principal (t/h)": f_jugo_encalado, "Concentración (°Bx)": f"{bx_mixto:.1f}°Bx", "Pureza (%)": f"{pureza_mixto:.1f}%", "Merma / Salida (t/h)": f"Merma: {merma_calentamiento:.2f}"},
        {"Bloque Unitario": "8 y 9. Clarificador y Filtro", "Entrada (t/h)": f_jugo_encalado, "Salida Principal (t/h)": f_jugo_clarificado, "Concentración (°Bx)": f"{bx_clarificado:.1f}°Bx", "Pureza (%)": f"{pureza_clarificado:.1f}%", "Merma / Salida (t/h)": f"Cachaza: {f_cachaza:.2f}"},
        {"Bloque Unitario": "10. Evaporadores Múltiple Efecto", "Entrada (t/h)": f_jugo_clarificado, "Salida Principal (t/h)": f_meladura, "Concentración (°Bx)": "65.0°Bx", "Pureza (%)": f"{pureza_meladura:.1f}%", "Merma / Salida (t/h)": f"Vapor: {v_evaporadores:.1f}"},
        {"Bloque Unitario": "11 y 12. Tachos y Cristalizadores", "Entrada (t/h)": f_meladura, "Salida Principal (t/h)": f_masa_cocida, "Concentración (°Bx)": "90.0°Bx", "Pureza (%)": f"{pureza_masa_cocida:.1f}%", "Merma / Salida (t/h)": f"Vapor: {v_tachos:.1f}"},
        {"Bloque Unitario": "13 a 15. Centrífugas, Secado y Zaranda", "Entrada (t/h)": f_masa_cocida, "Salida Principal (t/h)": f_azucar_final, "Concentración (°Bx)": "99.95°Bx", "Pureza (%)": "99.95%", "Merma / Salida (t/h)": f"Melaza: {f_melaza:.1f} | Polvillo: {merma_polvillo_azucar:.2f}"}
    ])

    if not graficar:
        return res

    # --------------------------------------------------------------------------
    # C. DIAGRAMA DE BLOQUES CON MERMAS Y RECIRCULACIÓN
    # --------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(24, 15))
    ax.set_xlim(-2, 102)
    ax.set_ylim(-2, 102)
    ax.axis('off')

    bloques = [
        {"id": 1, "pos": (14, 85), "nombre": "1. Mesa de\nAlimentación"},
        {"id": 2, "pos": (38, 85), "nombre": "2. Picadoras y\nDesfibrador"},
        {"id": 3, "pos": (62, 85), "nombre": "3. Tándem de\nMolinos"},
        {"id": 4, "pos": (86, 85), "nombre": "4. Calentador\nPrimario"},
        {"id": 5, "pos": (86, 60), "nombre": "5. Torre de\nSulfitación"},
        {"id": 6, "pos": (62, 60), "nombre": "6. Tanque de\nEncalado"},
        {"id": 7, "pos": (38, 60), "nombre": "7. Calentador\nSecundario"},
        {"id": 8, "pos": (14, 60), "nombre": "8. Clarificador\nde Jugo"},
        {"id": 9, "pos": (14, 35), "nombre": "9. Filtro Rotatorio\nde Vacío"},
        {"id": 10, "pos": (38, 35), "nombre": "10. Evaporadores\nMúltiple Efecto"},
        {"id": 11, "pos": (62, 35), "nombre": "11. Tachos al\nVacío"},
        {"id": 12, "pos": (86, 35), "nombre": "12. Cristalizadores\nEnfriamiento"},
        {"id": 13, "pos": (86, 10), "nombre": "13. Centrífugas"},
        {"id": 14, "pos": (62, 10), "nombre": "14. Secador -\nEnfriador"},
        {"id": 15, "pos": (38, 10), "nombre": "15. Clasificador /\nZaranda"}
    ]

    for b in bloques:
        x, y = b["pos"]
        rect = patches.FancyBboxPatch((x-8, y-5), 16, 10, boxstyle="round,pad=0.3", ec="black", fc="white", lw=2.5)
        ax.add_patch(rect)
        ax.text(x, y, b["nombre"], ha="center", va="center", fontsize=10.5, fontweight="bold", color="black")

    # Flechas Principales
    ax.annotate("", xy=(30, 85), xytext=(22, 85), arrowprops=dict(arrowstyle="->", color="black", lw=2.5))
    ax.text(26, 87.5, f"{f1_cana:.1f} t/h\n{brix_cana:.1f}°Bx", ha="center", fontsize=9.5, fontweight="bold", color="black")

    ax.annotate("", xy=(54, 85), xytext=(46, 85), arrowprops=dict(arrowstyle="->", color="black", lw=2.5))
    ax.text(50, 87.5, f"{f2_prep:.1f} t/h\n{brix_cana:.1f}°Bx", ha="center", fontsize=9.5, fontweight="bold", color="black")

    ax.annotate("", xy=(78, 85), xytext=(70, 85), arrowprops=dict(arrowstyle="->", color="black", lw=2.5))
    ax.text(74, 87.5, f"{f_jugo_ext:.1f} t/h\n{bx_mixto:.1f}°Bx", ha="center", fontsize=9.5, fontweight="bold", color="black")

    ax.annotate("", xy=(86, 65), xytext=(86, 80), arrowprops=dict(arrowstyle="->", color="black", lw=2.5))
    ax.annotate("", xy=(70, 60), xytext=(78, 60), arrowprops=dict(arrowstyle="->", color="black", lw=2.5))
    ax.annotate("", xy=(46, 60), xytext=(54, 60), arrowprops=dict(arrowstyle="->", color="black", lw=2.5))
    ax.annotate("", xy=(22, 60), xytext=(30, 60), arrowprops=dict(arrowstyle="->", color="black", lw=2.5))

    # Lodos y Jugo Clarificado
    ax.annotate("", xy=(14, 40), xytext=(14, 55), arrowprops=dict(arrowstyle="->", color="red", lw=2.5))
    ax.text(18, 47.5, f"Lodos\n{f_lodo:.1f} t/h", ha="left", fontsize=9.5, color="black", fontweight="bold")

    ax.plot([22, 28, 28], [60, 60, 35], color="black", lw=2.5)
    ax.annotate("", xy=(30, 35), xytext=(28, 35), arrowprops=dict(arrowstyle="->", color="black", lw=2.5))
    ax.text(28, 48, f"Clarificado\n{f_jugo_clarificado:.1f} t/h\n{bx_clarificado:.1f}°Bx", ha="center", fontsize=9.5, color="black", fontweight="bold")

    # Evaporación y Cristalización
    ax.annotate("", xy=(54, 35), xytext=(46, 35), arrowprops=dict(arrowstyle="->", color="black", lw=2.5))
    ax.text(50, 38, f"Meladura\n{f_meladura:.1f} t/h\n{bx_meladura:.0f}°Bx", ha="center", fontsize=9.5, color="black", fontweight="bold")

    ax.annotate("", xy=(78, 35), xytext=(70, 35), arrowprops=dict(arrowstyle="->", color="black", lw=2.5))
    ax.text(74, 38, f"Masa Cocida\n{f_masa_cocida:.1f} t/h\n{bx_masa_cocida:.0f}°Bx", ha="center", fontsize=9.5, color="black", fontweight="bold")

    ax.annotate("", xy=(86, 15), xytext=(86, 30), arrowprops=dict(arrowstyle="->", color="black", lw=2.5))
    ax.annotate("", xy=(70, 10), xytext=(78, 10), arrowprops=dict(arrowstyle="->", color="black", lw=2.5))
    ax.annotate("", xy=(46, 10), xytext=(54, 10), arrowprops=dict(arrowstyle="->", color="black", lw=2.5))

    # Salida Azúcar
    ax.annotate("", xy=(18, 10), xytext=(30, 10), arrowprops=dict(arrowstyle="->", color="green", lw=3.5))
    ax.text(24, 13, f"AZÚCAR FINAL\n{f_azucar_final:.2f} t/h\n{pureza_azucar:.2f}% Pur", ha="center", fontsize=10.5, color="black", fontweight="bold")

    # Recirculación limpia exterior
    ax.plot([6, 2, 2, 86, 86], [35, 35, 96, 96, 90], color="green", lw=2.5, ls="--")
    ax.annotate("", xy=(86, 90), xytext=(86, 92), arrowprops=dict(arrowstyle="->", color="green", lw=2.5))
    ax.text(44, 98, f"RECIRCULACIÓN JUGO FILTRADO: {f_filtrado:.1f} t/h (Retorna a Calentamiento)", ha="center", fontsize=10, color="black", fontweight="bold")

    # Flechas Rojas Mermas y Subproductos
    ax.annotate("", xy=(14, 73), xytext=(14, 80), arrowprops=dict(arrowstyle="->", color="red", lw=2))
    ax.text(14, 71, f"Merma Mesa:\n{merma_mesa:.2f} t/h", ha="center", fontsize=8.5, color="black", fontweight="bold")

    ax.annotate("", xy=(38, 73), xytext=(38, 80), arrowprops=dict(arrowstyle="->", color="red", lw=2))
    ax.text(38, 71, f"Merma Prep:\n{merma_prep:.2f} t/h", ha="center", fontsize=8.5, color="black", fontweight="bold")

    ax.annotate("", xy=(62, 73), xytext=(62, 80), arrowprops=dict(arrowstyle="->", color="red", lw=2))
    ax.text(62, 71, f"Pérd. Molinos:\n{merma_molinos:.2f} t/h", ha="center", fontsize=8.5, color="black", fontweight="bold")

    ax.annotate("", xy=(68, 93), xytext=(62, 90), arrowprops=dict(arrowstyle="->", color="red", lw=2.5))
    ax.text(68, 94, f"BAGAZO: {f_bagazo:.1f} t/h", ha="left", fontsize=9.5, color="black", fontweight="bold")

    ax.annotate("", xy=(38, 48), xytext=(38, 55), arrowprops=dict(arrowstyle="->", color="red", lw=2))
    ax.text(38, 46, f"Incrustaciones:\n{merma_calentamiento:.2f} t/h", ha="center", fontsize=8.5, color="black", fontweight="bold")

    ax.annotate("", xy=(14, 23), xytext=(14, 30), arrowprops=dict(arrowstyle="->", color="red", lw=2.5))
    ax.text(14, 20, f"CACHAZA SECA:\n{f_cachaza:.2f} t/h", ha="center", fontsize=9.5, color="black", fontweight="bold")

    ax.annotate("", xy=(38, 23), xytext=(38, 30), arrowprops=dict(arrowstyle="->", color="red", lw=2))
    ax.text(38, 20, f"Vapor Evap.:\n{v_evaporadores:.1f} t/h", ha="center", fontsize=8.5, color="black", fontweight="bold")

    ax.annotate("", xy=(62, 23), xytext=(62, 30), arrowprops=dict(arrowstyle="->", color="red", lw=2))
    ax.text(62, 20, f"Vapor Tachos:\n{v_tachos:.1f} t/h", ha="center", fontsize=8.5, color="black", fontweight="bold")

    ax.annotate("", xy=(86, 0), xytext=(86, 5), arrowprops=dict(arrowstyle="->", color="red", lw=2.5))
    ax.text(86, -2, f"MELAZA FINAL: {f_melaza:.1f} t/h\n({pureza_melaza:.1f}% Pureza)", ha="center", fontsize=9.5, color="black", fontweight="bold")

    ax.annotate("", xy=(62, -1), xytext=(62, 5), arrowprops=dict(arrowstyle="->", color="red", lw=2))
    ax.text(62, -3, f"Merma Polvillo: {merma_polvillo_azucar:.2f} t/h", ha="center", fontsize=8.5, color="black", fontweight="bold")

    ax.set_title(f"DIAGRAMA INDUSTRIAL DE BALANCE DE MATERIA Y FLUIDOS ({tch:g} TCH)", fontsize=15, fontweight="bold", pad=30, color="black")
    fig.tight_layout()
    plt.close(fig)
    res["fig_diagrama"] = fig

    # --------------------------------------------------------------------------
    # D. DASHBOARD ANALÍTICO COMPLETO
    # --------------------------------------------------------------------------
    fig_dash, axs = plt.subplots(2, 2, figsize=(18, 12))
    fig_dash.suptitle(f"DASHBOARD ANALÍTICO Y CONTROL DE PROCESO ({tch:g} TCH DE CAÑA)", fontsize=16, fontweight="bold", color="black")

    # 1. Gráfica de Perfil de Purezas (% Pureza)
    etapas_pur = ['Jugo Mixto', 'Jugo Clarificado', 'Meladura', 'Masa Cocida', 'Azúcar Final', 'Melaza Final']
    valores_pur = [pureza_mixto, pureza_clarificado, pureza_meladura, pureza_masa_cocida, pureza_azucar, pureza_melaza]
    axs[0, 0].plot(etapas_pur, valores_pur, marker='o', color='darkblue', linewidth=2.5, markersize=8)
    axs[0, 0].set_title('Perfil de Pureza del Licor de Azúcar (%)', fontsize=12, fontweight='bold', color='black')
    axs[0, 0].set_ylabel('Pureza (%)', fontweight='bold')
    axs[0, 0].grid(True, linestyle='--', alpha=0.6)
    axs[0, 0].tick_params(axis='x', rotation=20)

    # 2. Gráfica de Concentración (°Brix)
    etapas_bx = ['Caña Entrada', 'Jugo Mixto', 'Jugo Clarificado', 'Meladura', 'Masa Cocida', 'Azúcar Final']
    valores_bx = [brix_cana, bx_mixto, bx_clarificado, bx_meladura, bx_masa_cocida, 99.95]
    axs[0, 1].bar(etapas_bx, valores_bx, color='#2980B9', edgecolor='black', linewidth=1.2)
    axs[0, 1].set_title('Evolución de Concentración de Solidos (°Brix)', fontsize=12, fontweight='bold', color='black')
    axs[0, 1].set_ylabel('°Brix', fontweight='bold')
    axs[0, 1].tick_params(axis='x', rotation=20)
    for i, v in enumerate(valores_bx):
        axs[0, 1].text(i, v + 1, f"{v:.1f}°", ha='center', fontweight='bold', fontsize=9)

    # 3. Distribución de Salidas de Materia (Torta / Pie Chart)
    labels_salidas = ['Azúcar Final', 'Bagazo', 'Cachaza', 'Melaza Final', 'Vapor Extraído', 'Mermas']
    sizes_salidas = [f_azucar_final, f_bagazo, f_cachaza, f_melaza, v_total, mermas_totales]
    colors_salidas = ['#2ECC71', '#8E44AD', '#D35400', '#C0392B', '#3498DB', '#E74C3C']
    axs[1, 0].pie(sizes_salidas, labels=labels_salidas, autopct='%1.1f%%', colors=colors_salidas, startangle=140, textprops={'fontweight': 'bold'})
    axs[1, 0].set_title('Distribución Masica de Salidas del Ingenio', fontsize=12, fontweight='bold', color='black')

    # 4. Tarjeta de KPIs e Indicadores de Composición
    axs[1, 1].axis('off')
    kpi_text = (
        f"  INDICADORES CLAVE DE COMPOSICIÓN Y RENDIMIENTO\n"
        f"  --------------------------------------------------------\n\n"
        f"  1. PUREZA JUGO MIXTO/MELADURA :  {pureza_meladura:.2f} %\n\n"
        f"  2. CAÍDA DE PUREZA (AGOTAMIENTO): {caida_pureza:.2f} unidades (%)\n"
        f"     (Meladura {pureza_meladura:.1f}%  -->  Melaza {pureza_melaza:.1f}%)\n\n"
        f"  3. RECIRCULACIÓN MIELES Y MAGMA: {recirculacion_mieles_pct:.2f} %\n"
        f"     (Factor de carga en masa cocida para agotamiento)\n\n"
        f"  4. RECUPERACIÓN TEÓRICA (SJM):   {recuperacion_sjm:.2f} %\n"
        f"     (Eficiencia Fisicoquímica Deerr de la Sacarosa)\n\n"
        f"  --------------------------------------------------------\n"
        f"  • Rendimiento Industrial Bruto:  {(f_azucar_final/tch)*100:.2f} % caña\n"
        f"  • Vapor Especifico / Caña     :  {(v_total/tch)*100:.1f} % TCH"
    )
    axs[1, 1].text(0.05, 0.5, kpi_text, fontsize=11, fontweight='bold', va='center', bbox=dict(boxstyle="round,pad=1", fc="#F4F6F7", ec="#2C3E50", lw=2))

    fig_dash.tight_layout()
    plt.close(fig_dash)
    res["fig_dashboard"] = fig_dash

    return res
