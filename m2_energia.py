"""
MÓDULO 2: ENERGÍA ELÉCTRICA (kWh) Y TÉRMICA (VAPOR).
Cálculos idénticos a la versión de Colab. Recibe los resultados del módulo 1
(solo usa las TCH, como en el original) y devuelve resultados y tablas.
"""
import pandas as pd


def calcular_m2(m1):
    tch_actual = float(m1["tch"])

    # --------------------------------------------------------------------------
    # 1. ESCALADO DE FLUJOS MÁSICOS REALES (BASADO EN EL PRIMER MODELO)
    # --------------------------------------------------------------------------
    f_cana = tch_actual
    f_prep = tch_actual * (1 - 0.002 - 0.003)
    f_imb = tch_actual * 0.28
    f_jugo_ext = tch_actual * 1.0063
    f_lodo = tch_actual * 0.12
    f_jugo_encalado = tch_actual * 1.09
    f_jugo_clarificado = tch_actual * 0.983
    f_meladura = tch_actual * 0.204
    f_masa_cocida = tch_actual * 0.147
    f_azucar_humedo = tch_actual * 0.1085

    # --------------------------------------------------------------------------
    # 2. TRABAJO ELÉCTRICO REAL (kWh)
    # --------------------------------------------------------------------------
    equipos_electricos = [
        {"Equipo / Sección": "1. Mesa de Alimentación", "Materia Entrante (t/h)": f_cana, "Consumo Esp. (kWh/t)": 0.45, "Eficiencia (η)": 0.75},
        {"Equipo / Sección": "2. Picadoras y Desfibrador", "Materia Entrante (t/h)": f_prep, "Consumo Esp. (kWh/t)": 14.50, "Eficiencia (η)": 0.85},
        {"Equipo / Sección": "3. Tándem de Molinos", "Materia Entrante (t/h)": f_prep + f_imb, "Consumo Esp. (kWh/t)": 18.20, "Eficiencia (η)": 0.80},
        {"Equipo / Sección": "4 a 7. Bombas y Agitadores Tratamiento", "Materia Entrante (t/h)": f_jugo_ext, "Consumo Esp. (kWh/t)": 0.65, "Eficiencia (η)": 0.72},
        {"Equipo / Sección": "8 y 9. Filtro Rotatorio y Vacío", "Materia Entrante (t/h)": f_lodo, "Consumo Esp. (kWh/t)": 1.60, "Eficiencia (η)": 0.70},
        {"Equipo / Sección": "10. Bombas de Evaporación y Condensado", "Materia Entrante (t/h)": f_jugo_clarificado, "Consumo Esp. (kWh/t)": 0.85, "Eficiencia (η)": 0.75},
        {"Equipo / Sección": "11 y 12. Agitadores Tachos y Cristalizadores", "Materia Entrante (t/h)": f_meladura, "Consumo Esp. (kWh/t)": 1.20, "Eficiencia (η)": 0.78},
        {"Equipo / Sección": "13. Centrífugas de Cristalización", "Materia Entrante (t/h)": f_masa_cocida, "Consumo Esp. (kWh/t)": 3.20, "Eficiencia (η)": 0.80},
        {"Equipo / Sección": "14 y 15. Secador, Zaranda y Elevadores", "Materia Entrante (t/h)": f_azucar_humedo, "Consumo Esp. (kWh/t)": 1.10, "Eficiencia (η)": 0.82}
    ]

    lista_elec = []
    total_kwh = 0.0

    for eq in equipos_electricos:
        flujo = eq["Materia Entrante (t/h)"]
        c_esp = eq["Consumo Esp. (kWh/t)"]
        eta = eq["Eficiencia (η)"]

        kwh_equipo = (flujo * c_esp) / eta
        total_kwh += kwh_equipo

        lista_elec.append({
            "Equipo / Sección": eq["Equipo / Sección"],
            "Materia Entrante (t/h)": round(flujo, 2),
            "Consumo Esp. Teórico (kWh/t)": c_esp,
            "Eficiencia Real (η)": f"{int(eta*100)}%",
            "Trabajo Eléctrico Real (kWh)": round(kwh_equipo, 2)
        })

    # Fila de TOTALES
    lista_elec.append({
        "Equipo / Sección": "TOTAL CONSUMO ELÉCTRICO DEL INGENIO",
        "Materia Entrante (t/h)": round(f_cana, 2),
        "Consumo Esp. Teórico (kWh/t)": "-",
        "Eficiencia Real (η)": "-",
        "Trabajo Eléctrico Real (kWh)": round(total_kwh, 2)
    })

    df_electrico = pd.DataFrame(lista_elec)

    # --------------------------------------------------------------------------
    # 3. BALANCE TÉRMICO Y VAPOR DE PROCESO (t/h)
    # --------------------------------------------------------------------------
    delta_T_primario = 65 - 30      # 35 °C
    delta_T_secundario = 105 - 65    # 40 °C
    cp_jugo = 3.9                  # kJ/kg°C
    latente_vap = 2180.0           # kJ/kg (Vapor de escape)

    q_primario_kjl = (f_jugo_ext * 1000) * cp_jugo * delta_T_primario
    v_primario_th = q_primario_kjl / latente_vap / 1000

    q_secundario_kjl = (f_jugo_encalado * 1000) * cp_jugo * delta_T_secundario
    v_secundario_th = q_secundario_kjl / latente_vap / 1000

    v_evaporados_totales = tch_actual * 0.7795
    v_evaporadores_th = (v_evaporados_totales * 1000 / 3.8) / 1000

    v_tachos_evap = tch_actual * 0.0566
    v_tachos_th = (v_tachos_evap * 1000 / 0.95) / 1000

    equipos_termicos = [
        {"Equipo Térmico": "Calentadores Primarios", "Materia Entrante (t/h)": f_jugo_ext, "Operación Térmica": "Calentamiento 30°C a 65°C", "Vapor Requerido (t/h)": v_primario_th},
        {"Equipo Térmico": "Calentadores Secundarios", "Materia Entrante (t/h)": f_jugo_encalado, "Operación Térmica": "Calentamiento 65°C a 105°C", "Vapor Requerido (t/h)": v_secundario_th},
        {"Equipo Térmico": "Evaporadores Múltiple Efecto", "Materia Entrante (t/h)": f_jugo_clarificado, "Operación Térmica": "Evaporación de Agua (Cuádruple Efecto)", "Vapor Requerido (t/h)": v_evaporadores_th},
        {"Equipo Térmico": "Tachos al Vacío", "Materia Entrante (t/h)": f_meladura, "Operación Térmica": "Concentración y Cristales al Vacío", "Vapor Requerido (t/h)": v_tachos_th}
    ]

    lista_term = []
    total_vapor_th = 0.0

    for eq in equipos_termicos:
        v_th = eq["Vapor Requerido (t/h)"]
        total_vapor_th += v_th
        kw_termico = (v_th * 1000 * latente_vap) / 3600

        lista_term.append({
            "Equipo / Sección Térmica": eq["Equipo Térmico"],
            "Materia Entrante (t/h)": round(eq["Materia Entrante (t/h)"], 2),
            "Operación Térmica": eq["Operación Térmica"],
            "Vapor de Escape Requerido (t/h)": round(v_th, 2),
            "Potencia Térmica Equivalente (kWth)": round(kw_termico, 2)
        })

    # Fila de TOTALES
    lista_term.append({
        "Equipo / Sección Térmica": "TOTAL VAPOR DE PROCESO",
        "Materia Entrante (t/h)": round(f_cana, 2),
        "Operación Térmica": "Consumo Global de Vapor",
        "Vapor de Escape Requerido (t/h)": round(total_vapor_th, 2),
        "Potencia Térmica Equivalente (kWth)": round((total_vapor_th * 1000 * latente_vap) / 3600, 2)
    })

    df_termico = pd.DataFrame(lista_term)

    return {
        "tch": tch_actual,
        "total_kwh": total_kwh,
        "kwh_por_t": total_kwh / tch_actual,
        "total_vapor_th": total_vapor_th,
        "v_primario_th": v_primario_th,
        "v_secundario_th": v_secundario_th,
        "v_evaporadores_th": v_evaporadores_th,
        "v_tachos_th": v_tachos_th,
        "df_electrico": df_electrico,
        "df_termico": df_termico
    }
