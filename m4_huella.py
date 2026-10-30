"""
MÓDULO 4: HUELLA DE CARBONO Y COSTOS (ALCANCE: DESDE EL MÓDULO 1 EN ADELANTE).
Excluye cosecha, recolección y transporte de la caña.

Criterios:
- CO2 del bagazo = biogénico neutro (solo se contabilizan CH4 y N2O).
- Electricidad propia = 0 emisiones (Alcance 2 solo si hay déficit eléctrico).
- Comparativa: el gas natural o el carbón sustituyen TODO el bagazo de la caldera
  y el bagazo liberado se vende.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ------------------------------------------------------------------------------
# PARÁMETROS Y FACTORES DE EMISIÓN (EDITABLES)
# Factores por defecto IPCC 2006, Vol. 2, Tabla 2.2 (combustión estacionaria,
# industrias de la energía), en kg de gas por TJ de energía del combustible.
# Verifíquelos contra la fuente oficial si los usará en un reporte formal.
# ------------------------------------------------------------------------------
FE = {
    "Bagazo":      {"co2": 100000.0, "ch4": 30.0, "n2o": 4.0, "biogenico": True},   # Biomasa sólida primaria
    "Gas natural": {"co2": 56100.0,  "ch4": 1.0,  "n2o": 0.1, "biogenico": False},
    "Carbón":      {"co2": 94600.0,  "ch4": 1.0,  "n2o": 1.5, "biogenico": False},  # Otro carbón bituminoso
}
GWP_CH4 = 28.0     # IPCC AR5, 100 años
GWP_N2O = 265.0    # IPCC AR5, 100 años

PCI_CARBON_KJKG = 25800.0     # kJ/kg (IPCC, valor por defecto)
KJ_POR_MMBTU = 1055055.85     # kJ por MMBtu
FE_RED_KG_KWH = 0.13          # kg CO2e/kWh, REFERENCIAL: solo se usa si hay déficit eléctrico


def _emisiones(combustible, e_tj_h):
    """Emisiones en kg/h para una energía de combustible en TJ/h."""
    f = FE[combustible]
    co2 = e_tj_h * f["co2"]
    ch4 = e_tj_h * f["ch4"] * GWP_CH4     # kg CO2e/h
    n2o = e_tj_h * f["n2o"] * GWP_N2O     # kg CO2e/h
    if f["biogenico"]:
        return {"co2_fosil": 0.0, "co2_bio": co2, "ch4": ch4, "n2o": n2o}
    return {"co2_fosil": co2, "co2_bio": 0.0, "ch4": ch4, "n2o": n2o}


def calcular_m4(m1, m2, m3, comparar, comb_alt, p_bag, p_el, p_gas, p_car):
    """
    m1, m2, m3 : diccionarios de resultados de los módulos anteriores.
    comparar   : True/False. comb_alt: 'Gas natural' o 'Carbón' (si comparar).
    Precios: p_bag (USD/t bagazo), p_el (USD/MWh), p_gas (USD/MMBtu), p_car (USD/t).
    """
    tch_actual = float(m1["tch"])
    q_kw = m3["q_combustion_kw"]
    e_tj_h = q_kw * 3600.0 / 1.0e9      # TJ/h de energía térmica en la caldera
    disp = m3["m_bagazo_disponible_th"]
    req = m3["m_bagazo_requerido_th"]
    exc = m3["excedente_red_kwh"]
    azucar = m1["f_azucar_final"]
    vapor = m2["total_vapor_th"]

    grid_co2e = max(-exc, 0.0) * FE_RED_KG_KWH   # solo si hay déficit eléctrico
    ing_el = exc / 1000.0 * p_el                 # USD/h (negativo si es compra)

    escenarios = []

    # --- Escenario base: bagazo ---
    em = _emisiones("Bagazo", e_tj_h)
    escenarios.append({
        "nombre": "Base\n(Bagazo)", "nombre_tabla": "Base: Bagazo", "comb": "Bagazo",
        "consumo": f"{req:,.2f} t/h bagazo", "color": "#2ECC71", **em,
        "red": grid_co2e, "costo_comb": 0.0,
        "ing_bag": (disp - req) * p_bag, "ing_el": ing_el
    })

    # --- Escenario alterno: sustituye todo el bagazo y se vende el bagazo liberado ---
    if comparar:
        em2 = _emisiones(comb_alt, e_tj_h)
        if comb_alt == "Gas natural":
            cant = q_kw * 3600.0 / KJ_POR_MMBTU
            costo = cant * p_gas
            consumo = f"{cant:,.1f} MMBtu/h gas"
            color = "#3498DB"
        else:
            cant = q_kw * 3600.0 / PCI_CARBON_KJKG / 1000.0
            costo = cant * p_car
            consumo = f"{cant:,.2f} t/h carbón"
            color = "#7F8C8D"
        escenarios.append({
            "nombre": f"Sustitución\n({comb_alt})", "nombre_tabla": f"Sustitución: {comb_alt}", "comb": comb_alt,
            "consumo": consumo, "color": color, **em2,
            "red": grid_co2e, "costo_comb": costo,
            "ing_bag": disp * p_bag, "ing_el": ing_el
        })

    for e in escenarios:
        e["total"] = e["co2_fosil"] + e["ch4"] + e["n2o"] + e["red"]
        e["ingresos"] = max(e["ing_bag"], 0) + max(e["ing_el"], 0)
        e["compras"] = max(-e["ing_bag"], 0) + max(-e["ing_el"], 0)
        e["costos"] = e["costo_comb"] + e["compras"]
        e["neto"] = e["ing_bag"] + e["ing_el"] - e["costo_comb"]
        e["kg_t_cana"] = e["total"] / tch_actual
        e["kg_t_azucar"] = e["total"] / azucar
        e["neto_t_azucar"] = e["neto"] / azucar

    # --------------------------------------------------------------------------
    # TABLAS
    # --------------------------------------------------------------------------
    df_emis = pd.DataFrame([{
        "Escenario": e["nombre_tabla"],
        "Combustible en caldera": e["consumo"],
        "CO₂ fósil (kg CO₂e/h)": round(e["co2_fosil"], 1),
        "CH₄ (kg CO₂e/h)": round(e["ch4"], 1),
        "N₂O (kg CO₂e/h)": round(e["n2o"], 1),
        "Electricidad de red (kg CO₂e/h)": round(e["red"], 1),
        "HUELLA TOTAL (kg CO₂e/h)": round(e["total"], 1),
        "kg CO₂e / t caña": round(e["kg_t_cana"], 2),
        "kg CO₂e / t azúcar": round(e["kg_t_azucar"], 2),
        "CO₂ biogénico, no contabilizado (kg/h)": round(e["co2_bio"], 1)
    } for e in escenarios])

    df_eco = pd.DataFrame([{
        "Escenario": e["nombre_tabla"],
        "Costo combustible comprado (USD/h)": round(e["costo_comb"], 2),
        "Ingreso/Compra de bagazo (USD/h)": round(e["ing_bag"], 2),
        "Ingreso/Compra de electricidad (USD/h)": round(e["ing_el"], 2),
        "BALANCE NETO (USD/h)": round(e["neto"], 2),
        "Balance neto (USD / t azúcar)": round(e["neto_t_azucar"], 2)
    } for e in escenarios])

    # --------------------------------------------------------------------------
    # GRÁFICAS
    # --------------------------------------------------------------------------
    n = len(escenarios)
    x = np.arange(n)
    etiquetas = [e["nombre"] for e in escenarios]
    colores = [e["color"] for e in escenarios]

    fig, axs = plt.subplots(2, 3, figsize=(22, 12))
    fig.suptitle(f"HUELLA DE CARBONO Y COSTOS DEL PROCESO ({tch_actual:.1f} TCH, DESDE EL MÓDULO 1)",
                 fontsize=16, fontweight="bold", color="black")

    # 1. Emisiones apiladas por gas
    ax = axs[0, 0]
    base = np.zeros(n)
    capas = [("co2_fosil", "CO₂ fósil", "#C0392B"), ("ch4", "CH₄ (CO₂e)", "#F39C12"),
             ("n2o", "N₂O (CO₂e)", "#8E44AD"), ("red", "Electricidad de red", "#16A085")]
    for clave, nombre, col in capas:
        vals = np.array([e[clave] for e in escenarios])
        if vals.sum() > 0:
            ax.bar(x, vals, bottom=base, color=col, edgecolor="black", label=nombre, width=0.55)
            base = base + vals
    for i, e in enumerate(escenarios):
        ax.text(i, e["total"] * 1.02, f"{e['total']:,.0f}", ha="center", fontweight="bold", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas, fontweight="bold")
    ax.set_ylabel("kg CO₂e / h", fontweight="bold")
    ax.set_ylim(0, max(base.max(), 1) * 1.15)
    ax.set_title("Emisiones totales por gas (Alcance 1)", fontsize=12, fontweight="bold")
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    ax.legend(fontsize=9)

    # 2. Intensidad por tonelada de caña
    ax = axs[0, 1]
    vals = [e["kg_t_cana"] for e in escenarios]
    ax.bar(x, vals, color=colores, edgecolor="black", width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v * 1.02, f"{v:,.2f}", ha="center", fontweight="bold", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas, fontweight="bold")
    ax.set_ylabel("kg CO₂e / t caña", fontweight="bold")
    ax.set_ylim(0, max(max(vals), 1e-9) * 1.15)
    ax.set_title("Huella por tonelada de caña molida", fontsize=12, fontweight="bold")
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)

    # 3. Intensidad por tonelada de azúcar
    ax = axs[0, 2]
    vals = [e["kg_t_azucar"] for e in escenarios]
    ax.bar(x, vals, color=colores, edgecolor="black", width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v * 1.02, f"{v:,.1f}", ha="center", fontweight="bold", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas, fontweight="bold")
    ax.set_ylabel("kg CO₂e / t azúcar", fontweight="bold")
    ax.set_ylim(0, max(max(vals), 1e-9) * 1.15)
    ax.set_title("Huella por tonelada de azúcar producida", fontsize=12, fontweight="bold")
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)

    # 4. Balance económico (ingresos arriba, costos abajo, neto en rombo)
    ax = axs[1, 0]
    bag_pos = np.array([max(e["ing_bag"], 0) for e in escenarios])
    el_pos = np.array([max(e["ing_el"], 0) for e in escenarios])
    costo_comb = np.array([e["costo_comb"] for e in escenarios])
    compras = np.array([e["compras"] for e in escenarios])
    ax.bar(x, bag_pos, color="#2ECC71", edgecolor="black", width=0.55, label="Ingreso venta de bagazo")
    ax.bar(x, el_pos, bottom=bag_pos, color="#F1C40F", edgecolor="black", width=0.55, label="Ingreso venta de electricidad")
    if costo_comb.sum() > 0:
        ax.bar(x, -costo_comb, color="#E74C3C", edgecolor="black", width=0.55, label="Costo de combustible")
    if compras.sum() > 0:
        ax.bar(x, -compras, bottom=-costo_comb, color="#E67E22", edgecolor="black", width=0.55, label="Compras (bagazo/electricidad)")
    netos = [e["neto"] for e in escenarios]
    ax.plot(x, netos, linestyle="none", marker="D", markersize=10, color="black", zorder=5, label="Balance neto")
    for i, v in enumerate(netos):
        ax.text(i + 0.32, v, f"{v:,.0f}", ha="left", va="center", fontweight="bold", fontsize=10)
    ax.axhline(0, color="black", lw=1.5)
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas, fontweight="bold")
    ax.set_xlim(-0.6, n - 0.4)
    ax.set_ylabel("USD / h", fontweight="bold")
    ax.set_title("Balance económico por escenario", fontsize=12, fontweight="bold")
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    ax.legend(fontsize=8.5)

    # 5. Resultado neto por tonelada de azúcar
    ax = axs[1, 1]
    vals = [e["neto_t_azucar"] for e in escenarios]
    ax.bar(x, vals, color=colores, edgecolor="black", width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v, f"{v:,.1f}", ha="center", va="bottom" if v >= 0 else "top", fontweight="bold", fontsize=10)
    ax.axhline(0, color="black", lw=1.5)
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas, fontweight="bold")
    ax.set_ylabel("USD / t azúcar", fontweight="bold")
    ax.set_title("Balance neto por tonelada de azúcar", fontsize=12, fontweight="bold")
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)

    # 6. Tarjeta de indicadores
    ax = axs[1, 2]
    ax.axis("off")
    b0 = escenarios[0]
    kpi = (
        f"  INDICADORES CLAVE\n"
        f"  ------------------------------------------------\n\n"
        f"  Energía térmica en caldera : {q_kw/1000:,.2f} MWth\n"
        f"  Vapor de proceso (Mód. 2)  : {vapor:,.2f} t/h\n"
        f"  Azúcar producida (Mód. 1)  : {azucar:,.2f} t/h\n\n"
        f"  HUELLA BASE (BAGAZO)       : {b0['total']:,.0f} kg CO₂e/h\n"
        f"  Intensidad / t vapor       : {b0['total']/vapor:,.2f} kg CO₂e/t\n"
        f"  CO₂ biogénico (no contado) : {b0['co2_bio']:,.0f} kg/h\n"
    )
    if comparar:
        b1 = escenarios[1]
        factor = b1["total"] / b0["total"] if b0["total"] > 0 else float("nan")
        kpi += (
            f"\n  HUELLA {comb_alt.upper()}: {b1['total']:,.0f} kg CO₂e/h\n"
            f"  Aumento vs. base           : {b1['total']-b0['total']:+,.0f} kg CO₂e/h\n"
            f"                               (x{factor:,.1f})\n"
            f"  Δ balance neto vs. base    : {b1['neto']-b0['neto']:+,.0f} USD/h\n"
        )
    ax.text(0.02, 0.5, kpi, fontsize=11, fontweight="bold", va="center", family="monospace",
            bbox=dict(boxstyle="round,pad=1", fc="#F4F6F7", ec="#2C3E50", lw=2))

    fig.tight_layout()
    plt.close(fig)

    aviso = None
    if exc < 0:
        aviso = (f"El ingenio queda con déficit eléctrico ({-exc:,.0f} kWh/h): se contabiliza energía de red "
                 f"con {FE_RED_KG_KWH} kg CO₂e/kWh (valor referencial).")

    return {
        "tch": tch_actual,
        "comparar": comparar,
        "comb_alt": comb_alt,
        "precios": {"bagazo": p_bag, "electricidad": p_el, "gas": p_gas, "carbon": p_car},
        "escenarios": escenarios,
        "df_emis": df_emis,
        "df_eco": df_eco,
        "fig": fig,
        "aviso": aviso
    }
