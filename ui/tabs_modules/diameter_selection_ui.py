import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import json
import os
import math
from core.diameter_selection import PipeDiameterAnalyzer
from core.hydraulics import obtener_rugosidad_absoluta, obtener_viscosidad_cinematica
from core.calculations import interpolar_propiedad
from ui.tabs_modules.common import render_footer
from ui.tabs_modules.diameter_selection_docs import render_technical_documentation

def calcular_presion_vapor_mca_local(temp_input):
    temp_C = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
    vapor_agua_mca = [0.06, 0.09, 0.12, 0.17, 0.25, 0.33, 0.44, 0.58, 0.76, 0.98, 1.25, 1.61, 2.03, 2.56, 3.20, 3.96, 4.85, 5.93, 7.18, 8.62, 10.33]
    return interpolar_propiedad(temp_input, temp_C, vapor_agua_mca)

def detectar_asintota_tecnica(diametros, valores, umbral_pendiente=0.04):
    """Detecta el 'codo' de la curva donde la variable se estabiliza (asíntota hidráulica)"""
    if len(diametros) < 4: return None
    
    # Calcular pendientes normalizadas para comparar tasas de cambio
    y = np.array(valores)
    x = np.array(diametros)
    norm_y = (y - np.min(y)) / (np.max(y) - np.min(y) if np.max(y) != np.min(y) else 1)
    
    # Pendiente: d(norm_y)/dx
    pendientes = np.abs(np.diff(norm_y) / np.diff(x))
    
    # El punto donde la pendiente deja de ser "drástica"
    for i, p in enumerate(pendientes):
        if p < umbral_pendiente:
            return x[i]
    return x[-1]

def interpretar_punto_grafico(tipo, valor, asintota, is_suc, meta=None, di_especifico=0):
    """Genera diagnóstico técnico profundo con soluciones reales, definiciones y referencia al punto específico"""
    msg = ""
    status = "info" # info, success, warning, error
    
    # Colores para el fondo de la nota
    bg_colors = {
        "success": "#d1e7dd", "warning": "#fff3cd", "error": "#f8d7da", "info": "#cfe2ff"
    }
    
    # Prefijo con el punto específico
    ref_punto = f"🔍 <b>Para el diámetro de {di_especifico:.1f} mm:</b> " if di_especifico > 0 else ""

    if tipo == "velocidad":
        v_min, v_max = (0.6, 0.9) if is_suc else (1.0, 2.5)
        def_v = "<br>💡 <i>La velocidad define la capacidad de transporte. Un exceso erosiona la tubería, un defecto acumula sedimentos.</i>"
        asintota_msg = ""
        if asintota and di_especifico > asintota:
            asintota_msg = "<br>🛡️ <b>Estabilidad:</b> Se encuentra en la zona robusta de la curva (derecha de la asíntota)."
        elif asintota and di_especifico <= asintota:
            asintota_msg = "<br>🚨 <b>Zona Crítica:</b> Pequeños cambios en el caudal dispararán la velocidad de forma inestable."

        if valor < v_min:
            msg = f"{ref_punto}Velocidad de <b>{valor:.2f} m/s</b> es insuficiente. {def_v} 💡 <b><i>Disminuya el diámetro.</i></b> {asintota_msg}"
            status = "warning"
        elif valor > v_max:
            msg = f"{ref_punto}Velocidad de <b>{valor:.2f} m/s</b> es excesiva. {def_v} 💡 <b><i>Aumente el diámetro.</i></b> {asintota_msg}"
            status = "error"
        else:
            msg = f"{ref_punto}Velocidad de <b>{valor:.2f} m/s</b> es óptima. {def_v} {asintota_msg}"
            status = "success"
        
    elif tipo == "perdidas":
        # Criterio de Zona Roja (Analogía del Tacómetro)
        def_h = "<br>💡 <i>Las pérdidas totales ($H_L$) crecen exponencialmente con el caudal. Un diseño resiliente evita la 'Zona Roja' (curva parabólica).</i>"
        
        # El umbral exponencial lo definimos por el gradiente J > 16-20 m/km o por la asíntota de diseño
        gradiente_pt = (valor / (di_especifico/1000.0) ) * 1000 if di_especifico > 0 else 0 # Simplificación m/km
        
        # Verificamos si estamos en el 75% de la capacidad de la zona lineal
        if asintota and di_especifico < asintota:
            msg = f"{ref_punto}Pérdidas de <b>{valor:.2f} m</b> están en la 🚨 <b>Zona Roja</b>. El sistema es extremadamente frágil ante aumentos de caudal. {def_h} 💡 <i>Aumente el diámetro para operar en la zona lineal.</i>"
            status = "error"
        elif asintota and di_especifico < asintota * 1.25: # Margen de seguridad del 75% (D_lin = 1.25 * D_crit aprox)
             msg = f"{ref_punto}Pérdidas de <b>{valor:.2f} m</b> controladas, pero con ⚠️ <b>Margen Reducido</b>. Está cerca de la zona exponencial. {def_h}"
             status = "warning"
        else:
            msg = f"{ref_punto}Pérdidas de <b>{valor:.2f} m</b> en 🛡️ <b>Zona Robusta</b>. El sistema tiene capacidad de maniobra ante picos de demanda. {def_h}"
            status = "success"
                 
    elif tipo == "presion":
        # Meta viene en MPa
        pn = meta if meta else 1.0 # Default 1.0 MPa si no hay meta
        def_p = "<br>💡 <i>La presión interna debe ser soportada por las paredes de la tubería para evitar roturas. El diseño debe considerar no solo la presión operativa, sino también la estática, de prueba y los transitorios (ariete).</i>"
        if valor > pn * 0.8:
            msg = f"{ref_punto}Presión de <b>{valor:.3f} MPa</b> excede el 80% de la PN ({pn:.2f} MPa). {def_p} 💡 <i>Use mayor Serie/RDE para soportar el golpe de ariete y la presión de prueba.</i>"
            status = "error"
        else:
            msg = f"{ref_punto}Presión de <b>{valor:.3f} MPa</b> segura frente a PN {pn:.2f} MPa. {def_p}"
            status = "success"

    elif tipo == "npsh":
        margen = valor - (meta if meta else 0)
        def_n = "<br>💡 <i>NPSH Disp: Energía disponible en la succión para evitar la ebullición del agua (cavitación).</i>"
        if margen < 0.5:
            msg = f"{ref_punto}Margen crítico de <b>{margen:.2f} m</b>. {def_n} 💡 <i>¡Cavitación inminente! Aumente diámetro.</i>"
            status = "error"
        elif margen < 1.0:
            msg = f"{ref_punto}Margen de <b>{margen:.2f} m</b> ajustado. {def_n}"
            status = "warning"
        else:
            msg = f"{ref_punto}Margen de <b>{margen:.2f} m</b> asegura estabilidad. {def_n}"
            status = "success"

    elif tipo == "gradiente":
        j = valor # m/km
        def_j = "<br>💡 <i>El Gradiente J es el 'impuesto' energético: pérdidas por cada km. Cifras > 20 m/km indican diseños costosos en OPEX.</i>"
        if j > 20:
             msg = f"{ref_punto}Gradiente de <b>{j:.2f} m/km</b> es ineficiente. {def_j}"
             status = "error"
        elif j > 15:
             msg = f"{ref_punto}Gradiente de <b>{j:.2f} m/km</b> es elevado. {def_j}"
             status = "warning"
        else:
             msg = f"{ref_punto}Gradiente de <b>{j:.2f} m/km</b> es excelente (Rango Gold). {def_j}"
             status = "success"

    elif tipo == "friccion":
        if valor < 0:
            msg = f"<b>Aviso:</b> Active <b>Darcy-Weisbach</b> para ver el Factor f dinámico para {di_especifico:.1f} mm."
            status = "info"
        else:
            msg = f"{ref_punto}Factor f = <b>{valor:.4f}</b>. Define la rugosidad relativa en régimen turbulento."
            status = "success"

    elif tipo == "reynolds":
        def_re = "<br>💡 <i>Reynolds indica la estabilidad del régimen de flujo. Valores > 4000 aseguran transporte turbulento pleno.</i>"
        msg = f"{ref_punto}Reynolds de <b>{int(valor):,}</b> en régimen <b>{meta}</b>. {def_re}"
        status = "success" if valor > 4000 else "warning"

    elif tipo == "sumergencia":
        def_s = "<br>💡 <i>Evita la entrada de aire. A niveles menores, la bomba succiona aire y pierde eficiencia.</i>"
        msg = f"{ref_punto}Sumergencia mínima de <b>{valor:.2f} m</b> requerida. {def_s}"
        status = "info"

    elif tipo == "capex":
        msg = f"{ref_punto}Costo de inversión proyectado en <b>${valor:.2f}</b>. Representa la compra inicial de materiales."
        status = "info"

    elif tipo == "opex":
        msg = f"{ref_punto}Costo energético de <b>${valor:.2f}/año</b>. Refleja el gasto eléctrico por vencer la fricción."
        status = "info"

    bg = bg_colors.get(status, "#cfe2ff")
    border = "#86b7fe" if status == "info" else "#badbcc" if status == "success" else "#ffecb5" if status == "warning" else "#f5c2c7"
    
    html = f"""<div style="padding:15px; border-left: 6px solid {border}; background-color:{bg}; border-radius:8px; margin-bottom:25px; font-size:0.9rem; color:#111; line-height:1.4;">
        {msg}
    </div>"""
    return html, status

def cargar_diametros_comerciales(material_key):
    """Carga diámetros internos reales desde los archivos JSON"""
    base_path = r"c:\Users\psciv\OneDrive\Desktop\PYTHON\App_bombeo\app_bombeo_modulos\data_tablas"
    diametros = []
    try:
        mat_key = material_key.upper()
        if "PVC" in mat_key:
            with open(os.path.join(base_path, "pvc_data.json"), 'r') as f:
                data = json.load(f)
            series = data.get("pvc_tuberias", {}).get("union_elastomerica", {}).get("series", {})
            for s_name, s_data in series.items():
                for pipe in s_data.get("tuberias", []):
                    di = float(pipe['de_mm']) - 2 * float(pipe['espesor_min_mm'])
                    diametros.append((f"PVC {s_name.upper()} DN{pipe['dn_mm']}", di))
                    
        elif "PEAD" in mat_key or "HDPE" in mat_key:
            with open(os.path.join(base_path, "pead_data.json"), 'r') as f:
                data = json.load(f)
            for pipe in data.get("pead_tuberias", []):
                dn = pipe['diametro_nominal_mm']
                s_data = pipe.get("s5", {}) 
                if s_data.get("espesor_mm"):
                    di = float(dn) - 2 * float(s_data['espesor_mm'])
                    diametros.append((f"HDPE SDR11 DN{dn}", di))

        elif "HIERRO" in mat_key or "DUCTIL" in mat_key:
            with open(os.path.join(base_path, "hierro_ductil_data.json"), 'r') as f:
                data = json.load(f)
            pipes = data.get("hierro_ductil", {}).get("c40", {}).get("tuberias", [])
            for pipe in pipes:
                di = float(pipe['de_mm']) - 2 * float(pipe['espesor_nominal_mm'])
                diametros.append((f"HF C40 DN{pipe['dn_mm']}", di))
    except: pass
    return sorted(list(set(diametros)), key=lambda x: x[1])

def render_diameter_selection_tab():
    st.header("📏 Selección Técnica de Diámetros")
    
    # 1. Datos Globales de Sesión
    n_bombas = st.session_state.get('num_bombas', 1)
    q_total_lps = st.session_state.get('caudal_lps', 51.0)
    q_lps_sess = q_total_lps / n_bombas if n_bombas > 0 else q_total_lps
    h_suc_input = st.session_state.get('altura_succion_input', 2.0)
    bomba_inundada = st.session_state.get('bomba_inundada', False)
    h_est_suc = h_suc_input if bomba_inundada else -h_suc_input
    h_est_imp = st.session_state.get('altura_descarga', 80.0)
    temp = st.session_state.get('temp_liquido', 20.0)
    p_baro = st.session_state.get('presion_barometrica_calculada', 10.33)
    p_vap = calcular_presion_vapor_mca_local(temp)
    nps_req = st.session_state.get('npsh_requerido', 3.0)
    
    # 2. Configuración Global (Slicer y otros)
    with st.expander("🛠️ Parámetros Globales (Sincronizados)", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        if n_bombas > 1:
            c1.metric("Caudal Global", f"{q_total_lps:.2f} L/s")
            c1.metric("Caudal por Bomba", f"{q_lps_sess:.2f} L/s")
        else:
            c1.metric("Caudal de Diseño", f"{q_lps_sess:.2f} L/s")
        
        # Callback para sincronizar presión atmosférica con session_state
        def sync_p_atm():
            st.session_state['presion_barometrica_calculada'] = st.session_state['p_atm_input']
        
        p_atm = c2.number_input("P. Atms (mca)", 
                                value=float(p_baro), 
                                step=0.1, 
                                key='p_atm_input',
                                on_change=sync_p_atm,
                                help="Presión atmosférica. Los cambios se sincronizan con Análisis de Curvas.")
        nr = c3.number_input("NPSH Req (m)", value=float(nps_req), step=0.1)
        d_min, d_max = c4.select_slider("Rango Gráficos (mm)", options=[20, 25, 32, 40, 50, 63, 75, 90, 110, 125, 140, 160, 180, 200, 225, 250, 280, 315, 355, 400, 450, 500, 560, 630, 700], value=(32, 355))

    # Definir pestañas dinámicamente según el modo desarrollador
    tab_titles = ["💧 Análisis de Succión", "🚀 Análisis de Impulsión"]
    dev_mode = st.session_state.get('developer_mode', False)
    
    if dev_mode:
        tab_titles.append("📈 Análisis de Pérdidas")
    
    tab_titles.append("📚 Guía Técnica")
    
    tabs = st.tabs(tab_titles)
    
    # Asignar pestañas a variables
    t_suc = tabs[0]
    t_imp = tabs[1]
    
    if dev_mode:
        t_perd = tabs[2]
        t_doc = tabs[3]
    else:
        t_perd = None
        t_doc = tabs[2]
    
    # --- SUCCIÓN ---
    with t_suc:
        mat_suc_sess = st.session_state.get('mat_succion', 'PVC')
        long_suc_sess = st.session_state.get('long_succion', 10.0)
        le_suc_sess = st.session_state.get('le_total_succion', 0.0)
        render_analysis_section(q_lps_sess, p_atm, temp, p_vap, nr, long_suc_sess, h_est_suc, mat_suc_sess, le_suc_sess, (d_min, d_max), is_suc=True)
    
    # --- IMPULSIÓN ---
    with t_imp:
        mat_imp_sess = st.session_state.get('mat_impulsion', 'Hierro Ductil')
        long_imp_sess = st.session_state.get('long_impulsion', 100.0)
        le_imp_sess = st.session_state.get('le_total_impulsion', 0.0)
        render_analysis_section(q_lps_sess, p_atm, temp, p_vap, nr, long_imp_sess, h_est_imp, mat_imp_sess, le_imp_sess, (d_min, d_max), is_suc=False)

    # --- ANÁLISIS DE PÉRDIDAS (RESILIENCIA) ---
    if dev_mode and t_perd:
        with t_perd:
            render_loss_analysis_tab(q_lps_sess, p_atm, temp, p_vap, nr)
    
    # --- DOCUMENTACIÓN TÉCNICA ---
    with t_doc:
        # Recopilar datos para la guía técnica (usamos impulsión por defecto para análisis si existe)
        render_technical_documentation()
        

def render_analysis_section(q_sess_lps, p_atm, temp, p_vap, nr, length_sess, h_est, mat_sess, le_sess_m, dn_range, is_suc):
    prefix = "suc" if is_suc else "imp"
    
    # Obtener método de cálculo y coeficiente C de la sesión
    metodo_calculo = st.session_state.get('metodo_calculo', 'Darcy-Weisbach')
    from config.constants import HAZEN_WILLIAMS_C
    c_hazen = HAZEN_WILLIAMS_C.get(mat_sess, 150.0)
    
    # --- Layout Principal: Gráficos (Izq) vs Punto (Der) ---
    # Al usar [0.8, 0.2], los sub-gráficos en 2 columnas dentro de main_col tendrán el 40% cada uno.
    main_col, side_col = st.columns([0.8, 0.2])
    
    with side_col:
        # Placeholder para el título dinámico (Evita UnboundLocalError)
        point_title = st.empty()
        
        # --- BOTÓN DE IA (Sincronización) ---
        ga_data = st.session_state.get('ga_results')
        if ga_data:
            if st.button("🤖 Sincronizar con Óptimo IA", use_container_width=True, key=f"btn_sync_ia_{prefix}"):
                best_ind = ga_data['best_ind'] # [mat_s_idx, dn_s_idx, mat_d_idx, dn_d_idx]
                if is_suc:
                    st.session_state['diam_succion_mm'] = 110 # Fallback o lógica real si catalog_dn existe
                    # En realidad, el optimizador usa catalog_dn: [50, 63, 75, 90, 110, 125, 140, 160, 200, 250, 315, 400, 500, 630]
                    cat_ga = [50, 63, 75, 90, 110, 125, 140, 160, 200, 250, 315, 400, 500, 630]
                    st.session_state['diam_succion_mm'] = float(cat_ga[best_ind[1]])
                    st.info(f"✅ Succión ajustada a {cat_ga[best_ind[1]]} mm (Óptimo IA)")
                else:
                    cat_ga = [50, 63, 75, 90, 110, 125, 140, 160, 200, 250, 315, 400, 500, 630]
                    st.session_state['diam_impulsion_mm'] = float(cat_ga[best_ind[3]])
                    st.info(f"✅ Impulsión ajustada a {cat_ga[best_ind[3]]} mm (Óptimo IA)")
                st.rerun()
        else:
            with st.expander("🤖 ¿Cómo interviene la IA?", expanded=False):
                st.write("""
                La IA (Algoritmo Genético) analiza miles de combinaciones para encontrar el **costo mínimo total** (Inversión + 20 años de Energía).
                
                **¿Cómo ver su intervención?**
                1. Ve a la pestaña **🎯 Optimización IA** y presiona 'Ejecutar Optimización'.
                2. Regresa aquí y verás el marcador verde ✳️ en las gráficas.
                3. Usa el botón **Sincronizar** para aplicar automáticamente esos diámetros a tu diseño.
                """)

        # Parámetros de Punto (Sincronizados proactivamente para bombas en paralelo)
        # Task: Si cambia num_bombas o caudal nominal, resetear q_pt_suc/imp al caudal por bomba
        q_target_divided = float(q_sess_lps)
        q_current_val = st.session_state.get(f"q_pt_{prefix}", 0.0)
        
        # Si hay una discrepancia significativa (más del 1%), actualizamos
        if abs(q_current_val - q_target_divided) > 0.01:
            st.session_state[f"q_pt_{prefix}"] = q_target_divided

        q_lps = st.number_input("Caudal de Análisis [L/s]", value=q_target_divided, key=f"q_pt_{prefix}")
        q_m3s = q_lps / 1000.0
        
        
        # --- SELECCIÓN DE MATERIAL (Unificada con data_input.py) ---
        mat_options = list(HAZEN_WILLIAMS_C.keys())
        
        # Sincronización proactiva con la sesión
        mat_target = mat_sess if mat_sess else mat_options[0]
        mat_sess_upper = str(mat_target).upper()
        
        # Encontrar índice del material actual
        idx_mat = 0
        for i, m in enumerate(mat_options):
            if m.upper() == mat_sess_upper or mat_sess_upper in m.upper():
                idx_mat = i
                break
        
        mat = st.selectbox(
            "Material de Tubería", 
            options=mat_options, 
            index=idx_mat, 
            key=f"mat_sel_{prefix}",
            help="Selecciona el material de la tubería"
        )
        
        # Actualizar C si cambia el material
        c_hazen_punto = HAZEN_WILLIAMS_C.get(mat, 150.0)
        
        # --- OPCIÓN PARA USAR DIÁMETRO EXPORTADO ---
        diam_exportado = st.session_state.get('diam_succion_mm' if is_suc else 'diam_impulsion_mm', None)
        usar_exportado = False
        
        if diam_exportado and diam_exportado > 0:
            usar_exportado = st.checkbox(
                f"✅ Usar diámetro exportado ({diam_exportado:.1f} mm)",
                value=True,
                key=f"use_exported_{prefix}",
                help="Usa el diámetro exportado desde la pestaña de Datos de Entrada"
            )
        
        # --- SELECCIÓN ESPECÍFICA POR MATERIAL ---
        di_eval = 100.0  # Valor por defecto
        tipo_union_key = None
        serie_key = None
        dn_value = None
        diam_externo_value = None
        clase_value = None
        
        # Si se usa el diámetro exportado, se sobrescribirá di_eval al final
        # Mostrar advertencia si se está usando el diámetro exportado
        if usar_exportado:
            st.warning("⚠️ Los selectores de material/serie/DN se ignoran mientras el checkbox esté marcado. El análisis usa el diámetro exportado.")
        
        # ========== PVC ==========
        if mat == "PVC":
            from config.constants import PVC_DATA
            from core.calculations import get_pvc_series_disponibles, get_pvc_diametros_disponibles, get_pvc_data, calculate_diametro_interno_pvc
            
            # Tipo de Unión
            tipos_union_display = [
                "Unión Sellado Elastomérico (Unión R)",
                "Unión Encolada (Unión E)"
            ]
            # Obtener índice guardado o usar 0 por defecto
            idx_tipo_union = st.session_state.get(f'tipo_union_pvc_{prefix}_index', 0)
            if idx_tipo_union >= len(tipos_union_display):
                idx_tipo_union = 0
            
            tipo_union = st.selectbox(
                "Tipo de Unión",
                options=tipos_union_display,
                index=idx_tipo_union,
                key=f"tipo_union_pvc_{prefix}_analysis",
                help="Tipo de unión de la tubería PVC"
            )
            
            # Guardar índice seleccionado
            st.session_state[f'tipo_union_pvc_{prefix}_index'] = tipos_union_display.index(tipo_union)
            
            # Mapear a clave interna
            tipo_union_key = "union_elastomerica" if "Elastomérico" in tipo_union else "union_encolada"
            
            # Serie del Tubo
            series_pvc = get_pvc_series_disponibles(tipo_union_key)
            if series_pvc:
                # Formatear nombres de series - EXACTAMENTE como data_input.py
                series_nombres = []
                for serie_key_item in series_pvc:
                    if serie_key_item == "s20":
                        series_nombres.append("Serie S 20.0 (Presión: 0.63 MPa)")
                    elif serie_key_item == "s16":
                        series_nombres.append("Serie S 16.0 (Presión: 0.80 MPa)")
                    elif serie_key_item == "s12_5":
                        series_nombres.append("Serie S 12.5 (Presión: 1.00 MPa)")
                    elif serie_key_item == "s10":
                        series_nombres.append("Serie S 10.0 (Presión: 1.25 MPa)")
                    elif serie_key_item == "s8":
                        series_nombres.append("Serie S 8.0 (Presión: 1.60 MPa)")
                    elif serie_key_item == "s6_3":
                        series_nombres.append("Serie S 6.3 (Presión: 2.00 MPa)")
                
                # Obtener índice guardado o usar 0 por defecto
                idx_serie = st.session_state.get(f'serie_pvc_{prefix}_nombre_index', 0)
                if idx_serie >= len(series_nombres):
                    idx_serie = 0
                
                serie_pvc_nombre = st.selectbox(
                    "Serie del Tubo",
                    options=series_nombres,
                    index=idx_serie,
                    key=f"serie_pvc_{prefix}_analysis",
                    help="Serie del tubo PVC"
                )
                
                # Guardar índice seleccionado
                st.session_state[f'serie_pvc_{prefix}_nombre_index'] = series_nombres.index(serie_pvc_nombre)
                
                # Mapear nombre a clave
                serie_idx = series_nombres.index(serie_pvc_nombre)
                serie_key = series_pvc[serie_idx]
                
                # Diámetros disponibles
                diametros_pvc = get_pvc_diametros_disponibles(tipo_union_key, serie_key)
                if diametros_pvc:
                    # Obtener índice guardado o usar 0 por defecto
                    idx_dn = st.session_state.get(f'dn_pvc_{prefix}_index', 0)
                    if idx_dn >= len(diametros_pvc):
                        idx_dn = 0
                    
                    dn_pvc = st.selectbox(
                        "Diámetro Nominal (DN mm)",
                        options=diametros_pvc,
                        index=idx_dn,
                        key=f"dn_pvc_{prefix}_analysis",
                        help="Diámetro nominal de la tubería PVC"
                    )
                    
                    # Guardar índice seleccionado
                    st.session_state[f'dn_pvc_{prefix}_index'] = diametros_pvc.index(dn_pvc)
                    dn_value = dn_pvc
                    
                    # Obtener datos y calcular DI
                    tuberia_pvc = get_pvc_data(tipo_union_key, serie_key, dn_pvc)
                    if tuberia_pvc:
                        di_eval = calculate_diametro_interno_pvc(
                            tuberia_pvc["de_mm"],
                            tuberia_pvc["espesor_min_mm"],
                            tuberia_pvc["espesor_max_mm"]
                        )
                        
                        # Mostrar información
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"**DE (mm):** {tuberia_pvc['de_mm']}")
                            st.info(f"**DI (mm):** {di_eval:.1f}")
                        with col2:
                            st.info(f"**Espesor (mm):** {(tuberia_pvc['espesor_max_mm'] + tuberia_pvc['espesor_min_mm']) / 2:.1f}")
                            st.info(f"**Presión (MPa):** {tuberia_pvc['presion_mpa']}")
                    else:
                        st.warning("No se encontraron datos para esta combinación")
                        di_eval = st.number_input("Diámetro Interno (mm)", value=100.0, key=f"di_fallback_pvc_{prefix}")
                else:
                    st.warning("No hay diámetros disponibles para esta serie")
                    di_eval = st.number_input("Diámetro Interno (mm)", value=100.0, key=f"di_fallback_pvc2_{prefix}")
            else:
                st.warning("No hay series disponibles para este tipo de unión")
                di_eval = st.number_input("Diámetro Interno (mm)", value=100.0, key=f"di_fallback_pvc3_{prefix}")
        
        # ========== PEAD/HDPE ==========
        elif mat in ["PEAD", "HDPE (Polietileno)"]:
            from config.constants import PEAD_DATA
            from core.calculations import get_pead_data, get_pead_espesor
            
            # Diámetro Externo
            diametros_pead = [item["diametro_nominal_mm"] for item in PEAD_DATA]
            if diametros_pead:
                # Obtener índice guardado o usar 0 por defecto
                idx_diam_ext = st.session_state.get(f'diam_externo_{prefix}_index', 0)
                if idx_diam_ext >= len(diametros_pead):
                    idx_diam_ext = 0
                
                diam_externo = st.selectbox(
                    "Diámetro Externo (mm)",
                    options=diametros_pead,
                    index=idx_diam_ext,
                    key=f"diam_externo_{prefix}_analysis",
                    help="Diámetro externo de la tubería PEAD"
                )
                
                # Guardar índice seleccionado
                st.session_state[f'diam_externo_{prefix}_index'] = diametros_pead.index(diam_externo)
                diam_externo_value = diam_externo
                
                # Serie
                pead_data = get_pead_data(diam_externo)
                if pead_data:
                    series_disponibles = []
                    for serie_key_item in ["s12_5", "s10", "s8", "s6_3", "s5", "s4"]:
                        if serie_key_item in pead_data and pead_data[serie_key_item]["espesor_mm"] is not None:
                            series_disponibles.append(serie_key_item)
                    
                    if series_disponibles:
                        # Obtener índice guardado o usar 0 por defecto
                        idx_serie = st.session_state.get(f'serie_{prefix}_index', 0)
                        if idx_serie >= len(series_disponibles):
                            idx_serie = 0
                        
                        serie = st.selectbox(
                            "Serie del Tubo",
                            options=series_disponibles,
                            index=idx_serie,
                            key=f"serie_{prefix}_analysis",
                            help="Serie del tubo PEAD"
                        )
                        
                        # Guardar índice seleccionado
                        st.session_state[f'serie_{prefix}_index'] = series_disponibles.index(serie)
                        serie_key = serie
                        
                        # Calcular DI
                        espesor = get_pead_espesor(diam_externo, serie)
                        if espesor:
                            di_eval = diam_externo - 2 * espesor
                            
                            # Mostrar información
                            col1, col2 = st.columns(2)
                            with col1:
                                st.info(f"**DE (mm):** {diam_externo}")
                                st.info(f"**DI (mm):** {di_eval:.1f}")
                            with col2:
                                st.info(f"**Espesor (mm):** {espesor:.1f}")
                                st.info(f"**Serie:** {serie.upper()}")
                        else:
                            st.warning("No se pudo calcular el espesor")
                            di_eval = st.number_input("Diámetro Interno (mm)", value=100.0, key=f"di_fallback_pead_{prefix}")
                    else:
                        st.warning("No hay series disponibles")
                        di_eval = st.number_input("Diámetro Interno (mm)", value=100.0, key=f"di_fallback_pead2_{prefix}")
                else:
                    st.warning("No se encontraron datos para este diámetro")
                    di_eval = st.number_input("Diámetro Interno (mm)", value=100.0, key=f"di_fallback_pead3_{prefix}")
            else:
                st.warning("No hay diámetros PEAD disponibles")
                di_eval = st.number_input("Diámetro Interno (mm)", value=100.0, key=f"di_fallback_pead4_{prefix}")
        
        # ========== HIERRO DUCTIL ==========
        elif "Hierro Ductil" in mat:
            from config.constants import HIERRO_DUCTIL_DATA
            from core.calculations import get_hierro_ductil_diametros_disponibles, get_hierro_ductil_data, calculate_diametro_interno_hierro_ductil
            
            # Clase
            clases_display = ["Clase 40", "Clase 30", "Clase 25"]
            # Obtener índice guardado o usar 0 por defecto
            idx_clase = st.session_state.get(f'clase_hierro_{prefix}_index', 0)
            if idx_clase >= len(clases_display):
                idx_clase = 0
            
            clase = st.selectbox(
                "Clase de Presión",
                options=clases_display,
                index=idx_clase,
                key=f"clase_hierro_{prefix}_analysis",
                help="Clase de presión del hierro dúctil"
            )
            
            # Guardar índice seleccionado
            st.session_state[f'clase_hierro_{prefix}_index'] = clases_display.index(clase)
            clase_value = clase
            
            # Mapear a clave interna
            clase_key = clase.lower().replace(" ", "_")
            
            # DN
            diametros_hd = get_hierro_ductil_diametros_disponibles(clase_key)
            if diametros_hd:
                # Obtener índice guardado o usar 0 por defecto
                idx_dn = st.session_state.get(f'dn_{prefix}_index', 0)
                if idx_dn >= len(diametros_hd):
                    idx_dn = 0
                
                dn = st.selectbox(
                    "Diámetro Nominal (DN mm)",
                    options=diametros_hd,
                    index=idx_dn,
                    key=f"dn_{prefix}_analysis",
                    help="Diámetro nominal del hierro dúctil"
                )
                
                # Guardar índice seleccionado
                st.session_state[f'dn_{prefix}_index'] = diametros_hd.index(dn)
                dn_value = dn
                
                # Calcular DI
                data_hd = get_hierro_ductil_data(clase_key, dn)
                if data_hd:
                    di_eval = calculate_diametro_interno_hierro_ductil(data_hd["de_mm"], data_hd["espesor_nominal_mm"])
                    
                    # Mostrar información
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**DE (mm):** {data_hd['de_mm']}")
                        st.info(f"**DI (mm):** {di_eval:.1f}")
                    with col2:
                        st.info(f"**Espesor (mm):** {data_hd['espesor_nominal_mm']}")
                        st.info(f"**Clase:** {clase}")
                else:
                    st.warning("No se encontraron datos")
                    di_eval = st.number_input("Diámetro Interno (mm)", value=100.0, key=f"di_fallback_hd_{prefix}")
            else:
                st.warning("No hay diámetros disponibles")
                di_eval = st.number_input("Diámetro Interno (mm)", value=100.0, key=f"di_fallback_hd2_{prefix}")
        
        # ========== HIERRO FUNDIDO ==========
        elif "Hierro Fundido" in mat:
            from config.constants import HIERRO_FUNDIDO_DATA
            from core.calculations import get_hierro_fundido_diametros_disponibles, get_hierro_fundido_data
            
            # Clase
            clases_display = ["Clase 150", "Clase 200", "Clase 250"]
            # Obtener índice guardado o usar 0 por defecto
            idx_clase_hf = st.session_state.get(f'clase_hierro_fundido_{prefix}_index', 0)
            if idx_clase_hf >= len(clases_display):
                idx_clase_hf = 0
            
            clase = st.selectbox(
                "Clase de Presión",
                options=clases_display,
                index=idx_clase_hf,
                key=f"clase_hierro_fundido_{prefix}_analysis",
                help="Clase de presión del hierro fundido"
            )
            
            # Guardar índice seleccionado
            st.session_state[f'clase_hierro_fundido_{prefix}_index'] = clases_display.index(clase)
            clase_value = clase
            
            # Mapear a clave interna
            clase_key = clase.lower().replace(" ", "_")
            
            # DN
            diametros_hf = get_hierro_fundido_diametros_disponibles(clase_key)
            if diametros_hf:
                # Obtener índice guardado o usar 0 por defecto
                idx_dn_hf = st.session_state.get(f'dn_hierro_fundido_{prefix}_index', 0)
                if idx_dn_hf >= len(diametros_hf):
                    idx_dn_hf = 0
                
                dn = st.selectbox(
                    "Diámetro Nominal (DN mm)",
                    options=diametros_hf,
                    index=idx_dn_hf,
                    key=f"dn_hierro_fundido_{prefix}_analysis",
                    help="Diámetro nominal del hierro fundido"
                )
                
                # Guardar índice seleccionado
                st.session_state[f'dn_hierro_fundido_{prefix}_index'] = diametros_hf.index(dn)
                dn_value = dn
                
                # Calcular DI
                data_hf = get_hierro_fundido_data(clase_key, dn)
                if data_hf:
                    di_eval = data_hf["de_mm"] - 2 * data_hf["espesor_nominal_mm"]
                    
                    # Mostrar información
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**DE (mm):** {data_hf['de_mm']}")
                        st.info(f"**DI (mm):** {di_eval:.1f}")
                    with col2:
                        st.info(f"**Espesor (mm):** {data_hf['espesor_nominal_mm']}")
                        st.info(f"**Clase:** {clase}")
                else:
                    st.warning("No se encontraron datos")
                    di_eval = st.number_input("Diámetro Interno (mm)", value=100.0, key=f"di_fallback_hf_{prefix}")
            else:
                st.warning("No hay diámetros disponibles")
                di_eval = st.number_input("Diámetro Interno (mm)", value=100.0, key=f"di_fallback_hf2_{prefix}")
        
        # ========== OTROS MATERIALES ==========
        else:
            # Para otros materiales, usar diámetro interno directamente
            dn_actual_sess = st.session_state.get('diam_succion_mm' if is_suc else 'diam_impulsion_mm', 100.0)
            di_eval = st.number_input(
                "Diámetro Interno (mm)",
                value=float(dn_actual_sess),
                min_value=1.0,
                step=0.1,
                key=f"di_otros_{prefix}_analysis",
                help="Diámetro interno de la tubería en milímetros"
            )
        
        # OVERRIDE: Si el usuario marcó el checkbox para usar el diámetro exportado, sobrescribir di_eval
        if usar_exportado and diam_exportado:
            di_eval = float(diam_exportado)
            st.success(f"✅ Usando diámetro exportado: {di_eval:.1f} mm")
        
        l_eval = st.number_input("Longitud de Tubería (m)", value=float(length_sess), key=f"len_pt_{prefix}")
        le_m_input = st.number_input("Long. Equiv. Accesorios (m)", value=float(le_sess_m), format="%.2f", key=f"le_m_pt_{prefix}")
        
        
        # Actualizar el título dinámico con la configuración completa
        if mat == "PVC" and dn_value:
            dn_label_display = f"PVC {tipo_union.split('(')[1].strip(')')} {serie_pvc_nombre.split('(')[0].strip()} DN{dn_value}"
        elif mat in ["PEAD", "HDPE (Polietileno)"] and diam_externo_value:
            dn_label_display = f"HDPE DE{diam_externo_value} {serie_key.upper() if serie_key else ''}"
        elif "Hierro Ductil" in mat and dn_value:
            dn_label_display = f"Hierro Dúctil {clase_value} DN{dn_value}"
        elif "Hierro Fundido" in mat and dn_value:
            dn_label_display = f"Hierro Fundido {clase_value} DN{dn_value}"
        else:
            dn_label_display = f"{mat} DI {di_eval:.1f} mm"
        
        point_title.subheader(f"📍 Análisis: {dn_label_display}")
        
        # Cálculos de Punto e Interpretación
        le_d_calc = le_m_input / (di_eval / 1000.0) if di_eval > 0 else 0
        analyzer = PipeDiameterAnalyzer(
            fluid_props={'density': 1000.0, 'viscosity': obtener_viscosidad_cinematica(temp), 'vapor_pressure': p_vap},
            operating_conditions={'flow_rate': q_m3s, 'temperature': temp, 'atmospheric_pressure': p_atm, 'npsh_required': nr, 'static_head': h_est},
            pipe_params={'length': l_eval, 'absolute_roughness': obtener_rugosidad_absoluta(mat), 'le_over_d': le_d_calc},
            calculation_method=metodo_calculo,
            hazen_c=c_hazen_punto
        )

        df_point = analyzer.analyze_range([di_eval], is_suction=is_suc)
        pt = df_point.iloc[0].to_dict()
        
        # Guardar para la guía técnica
        res_key = f"last_pt_res_{prefix}"
        st.session_state[res_key] = pt
        st.session_state[f"last_pt_di_{prefix}"] = di_eval
        st.session_state[f"last_pt_mat_{prefix}"] = mat
        
        # Dashboard de Resultados (Envolvente)
        p_mpa = pt['pressure_kpa'] / 1000.0
        p_static_mpa = h_est * 0.00981
        p_surge_pt = (350 if any(m in mat.upper() for m in ["PVC", "PEAD", "HDPE"]) else 1100) * pt['velocity'] / 9.81 * 0.00981
        pn_ref = st.session_state.get('presion_nominal_succion' if is_suc else 'presion_nominal_impulsion', 1.0)
        p_test_pt = pn_ref * 1.5
        
        st.markdown(f"""
        <div style='background-color: #f8fbff; padding: 18px; border-radius: 12px; border: 1.5px solid #b8daff; margin-top: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
            <h4 style='color: #004085; margin: 0 0 15px 0; font-size: 1.15rem; border-bottom: 2px solid #b8daff; padding-bottom: 8px;'>
                📊 Resumen (DN {di_eval:.1f} mm) - Envolvente de Presiones
            </h4>
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.9rem;'>
                <div style='background: white; padding: 8px; border-radius: 6px; border: 1px solid #eef;'>🚀 <b>V:</b> {pt['velocity']:.2f} m/s</div>
                <div style='background: white; padding: 8px; border-radius: 6px; border: 1px solid #eef;'>📏 <b>Le:</b> {le_m_input:.2f} m</div>
                <div style='background: #fdf2f2; padding: 8px; border-radius: 6px; border: 1px solid #ecc;'>📉 <b>hf:</b> {pt['h_primary']:.3f} m</div>
                <div style='background: #f2fdf5; padding: 8px; border-radius: 6px; border: 1px solid #cee;'>📈 <b>Ha:</b> {h_est} m</div>
                <div style='background: #fff; padding: 8px; border-radius: 6px; border: 1px solid #eef;'>⚖️ <b>P. Estática:</b> {p_static_mpa:.3f} MPa</div>
                <div style='background: #fff; padding: 8px; border-radius: 6px; border: 1px solid #eef;'>🛡️ <b>P. Prueba:</b> {p_test_pt:.3f} MPa</div>
            </div>
            <div style='margin-top: 12px; padding: 10px; background: {"#d4edda" if (is_suc and (pt['npsh_available'] - nr) > 0.5) else "#fff3cd"}; border-radius: 8px; border: 1px solid #bee5eb; text-align: center;'>
                <span style='font-size: 1.05rem; font-weight: bold; color: #004085;'>
                    {('💎 NPSH Disp: ' + f"{pt['npsh_available']:.2f} m") if is_suc else ('🚩 P. Op + Ariete: ' + f"{p_mpa + p_surge_pt:.3f} MPa")}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        
        # --- BOTÓN DE MIGRACIÓN DE DIÁMETROS (COMPLETO) ---
        st.markdown("---")
        if st.button(f"📥 Migrar Configuración Completa a {'Succión' if is_suc else 'Impulsión'}", 
                    use_container_width=True, 
                    key=f"btn_migrate_{prefix}",
                    help="Transfiere el material, tipo, serie y diámetro seleccionado a la pestaña de entrada"):
            
            # Usar claves temporales para evitar conflicto con widgets
            # data_input.py leerá estas claves al inicializar
            prefix_key = 'suc' if is_suc else 'imp'
            
            # Guardar configuración en claves temporales
            st.session_state[f'_migrated_{prefix_key}_mat'] = mat
            st.session_state[f'_migrated_{prefix_key}_di'] = float(di_eval)
            
            # Configuración específica por material
            if mat == "PVC" and tipo_union_key and serie_key and dn_value:
                st.session_state[f'_migrated_{prefix_key}_tipo_union'] = tipo_union
                st.session_state[f'_migrated_{prefix_key}_serie_nombre'] = serie_pvc_nombre
                st.session_state[f'_migrated_{prefix_key}_dn'] = dn_value
                msg = f"PVC {tipo_union.split('(')[1].strip(')')} {serie_pvc_nombre.split('(')[0].strip()} DN{dn_value}"
            
            elif mat in ["PEAD", "HDPE (Polietileno)"] and diam_externo_value and serie_key:
                st.session_state[f'_migrated_{prefix_key}_diam_externo'] = diam_externo_value
                st.session_state[f'_migrated_{prefix_key}_serie'] = serie_key
                msg = f"HDPE DE{diam_externo_value} {serie_key.upper()}"
            
            elif "Hierro Ductil" in mat and clase_value and dn_value:
                st.session_state[f'_migrated_{prefix_key}_clase'] = clase_value
                st.session_state[f'_migrated_{prefix_key}_dn'] = dn_value
                msg = f"Hierro Dúctil {clase_value} DN{dn_value}"
            
            elif "Hierro Fundido" in mat and clase_value and dn_value:
                st.session_state[f'_migrated_{prefix_key}_clase_fundido'] = clase_value
                st.session_state[f'_migrated_{prefix_key}_dn_fundido'] = dn_value
                msg = f"Hierro Fundido {clase_value} DN{dn_value}"
            
            else:
                msg = f"{mat} DI {di_eval:.1f} mm"
            
            # Marcar que hay una migración pendiente
            st.session_state[f'_migration_pending_{prefix_key}'] = True
            
            st.success(f"✅ Configuración guardada: {msg}")
            st.info("💡 Ve a la pestaña 'Datos de Entrada' para aplicar los cambios con el botón '📥 Importar desde Selección de Diámetros'")
        
        st.markdown("---")
            
        with st.expander("📝 Interpretación Técnica del Análisis", expanded=True):
            # Análisis de Velocidad
            v_min, v_max = (0.6, 0.9) if is_suc else (1.0, 2.5)
            if v_min <= pt['velocity'] <= v_max: 
                st.success(f"✅ **Velocidad Óptima:** Rango ideal ({v_min}-{v_max} m/s).")
            elif pt['velocity'] > v_max: 
                st.warning(f"⚠️ **Velocidad Alta (> {v_max} m/s):** Riesgo de erosión.")
            else: 
                st.warning(f"⚠️ **Velocidad Baja (< {v_min} m/s):** Riesgo de sedimentación.")
            
            # Análisis de Cavitación / Presión
            if is_suc:
                margen = pt['npsh_available'] - nr
                if margen >= 0.5: st.success(f"✅ **Margen NPSH:** {margen:.2f} m (Seguro).")
                elif margen >= 0: st.warning(f"⚠️ **Margen Crítico:** {margen:.2f} m.")
                else: st.error(f"❌ **CAVITACIÓN:** Margen negativo ({margen:.2f} m).")
            else:
                p_mpa = pt['pressure_kpa'] / 1000.0
                p_ariete_total = p_mpa + p_surge_pt
                # Obtener PN de la sesión de forma proactiva
                pn_sess = st.session_state.get('presion_nominal_impulsion', 1.0)
                
                if p_ariete_total < pn_sess * 0.8: 
                    st.success(f"✅ **Diseño Seguro:** P. Operativa + Ariete ({p_ariete_total:.3f} MPa) es inferior al 80% de la PN ({pn_sess} MPa).")
                else: 
                    st.error(f"❌ **Riesgo por Transitorios:** La presión total con ariete ({p_ariete_total:.3f} MPa) supera los límites de seguridad de la tubería PN {pn_sess}.")
                
                st.info(f"💡 **Criterio de Prueba:** La presión de estanqueidad sugerida es de **{p_test_pt:.3f} MPa**.")

    with main_col:
        # Gráficos de Tendencia - UNIFICACIÓN DE PARÁMETROS
        d_list = [d for d in [32, 40, 50, 63, 75, 90, 110, 125, 140, 160, 180, 200, 225, 250, 280, 315, 355, 400, 450, 500, 560, 630] if dn_range[0] <= d <= dn_range[1]]
        
        # Sincronización proactiva: usamos los mismos valores que el punto para la curva
        analyzer_trends = PipeDiameterAnalyzer(
            fluid_props={'density': 1000.0, 'viscosity': obtener_viscosidad_cinematica(temp), 'vapor_pressure': p_vap},
            operating_conditions={'flow_rate': q_m3s, 'temperature': temp, 'atmospheric_pressure': p_atm, 'npsh_required': nr, 'static_head': h_est},
            pipe_params={'length': l_eval, 'absolute_roughness': obtener_rugosidad_absoluta(mat), 'le_over_d': le_d_calc},
            calculation_method=metodo_calculo,
            hazen_c=c_hazen_punto
        )
        df = analyzer_trends.analyze_range(d_list, is_suction=is_suc)

        # Matriz de Gráficos (2 columnas - layout 35%-35%-30%)
        dn_actual = st.session_state.get('diam_succion_mm' if is_suc else 'diam_impulsion_mm', 0.0)
        
        # Helper para encontrar valores en el DF por cercanía a un diámetro
        def get_val(df_in, di_target, col):
            if abs(di_eval - di_target) < 0.1: return pt[col]
            return df_in.iloc[(df_in['di_mm']-di_target).abs().argsort()[:1]][col].values[0]

        # Centralizar marcadores "Diseño Actual"
        v_actual = get_val(df, dn_actual, 'velocity')
        h_actual = get_val(df, dn_actual, 'friction_loss')
        p_actual = get_val(df, dn_actual, 'pressure_kpa')
        n_actual = get_val(df, dn_actual, 'npsh_available')
        re_actual = get_val(df, dn_actual, 'reynolds')
        f_actual = get_val(df, dn_actual, 'friction_factor')
        j_actual = get_val(df, dn_actual, 'hydraulic_gradient') * 1000
        s_actual = get_val(df, dn_actual, 'submergence_min')
        c_actual = get_val(df, dn_actual, 'capex')
        o_actual = get_val(df, dn_actual, 'energy_cost_annual')

        # Centralizar marcadores "IA Optimal"
        di_ia, v_ia, h_ia, p_ia, n_ia, re_ia, f_ia, j_ia, s_ia, c_ia, o_ia = [None]*11
        if ga_data:
            cat_ga = [50, 63, 75, 90, 110, 125, 140, 160, 200, 250, 315, 400, 500, 630]
            di_ia = float(cat_ga[ga_data['best_ind'][1 if is_suc else 3]])
            v_ia = get_val(df, di_ia, 'velocity')
            h_ia = get_val(df, di_ia, 'friction_loss')
            p_ia = get_val(df, di_ia, 'pressure_kpa')
            n_ia = get_val(df, di_ia, 'npsh_available')
            re_ia = get_val(df, di_ia, 'reynolds')
            f_ia = get_val(df, di_ia, 'friction_factor')
            j_ia = get_val(df, di_ia, 'hydraulic_gradient') * 1000
            s_ia = get_val(df, di_ia, 'submergence_min')
            c_ia = get_val(df, di_ia, 'capex')
            o_ia = get_val(df, di_ia, 'energy_cost_annual')

        # Criterios de Presión (Golpe de Ariete y Otros)
        def calc_surge(v_val, material):
            # Celeridad aproximada (m/s)
            a = 350 if any(m in material.upper() for m in ["PVC", "PEAD", "HDPE", "POLIET"]) else 1100
            return (a * v_val) / 9.81 * 0.00981 # MPa
        
        df['p_mpa'] = df['pressure_kpa'] / 1000.0
        df['p_static_mpa'] = h_est * 0.00981 # Aproximación rápida 1 mca = 0.00981 MPa
        df['p_surge_delta'] = df.apply(lambda row: calc_surge(row['velocity'], mat), axis=1)
        df['p_total_surge'] = df['p_mpa'] + df['p_surge_delta']
        
        # Presión de Prueba (1.5 * Operativa o 1.5 * PN)
        pn_ref = st.session_state.get('presion_nominal_succion' if is_suc else 'presion_nominal_impulsion', 1.0)
        df['p_test'] = pn_ref * 1.5
        
        # Presión de Vapor (Solo para Succión - Límite Inferior)
        p_vap_gauge_mpa = (p_vap - p_atm) * 0.00981
        
        def apply_style(fig, title, y_label, asintota=None):
            fig.update_layout(
                title=dict(text=f"<b>{title}</b>", x=0.5, xanchor='center', font=dict(size=18, color='#111')),
                xaxis=dict(
                    title=dict(
                        text="Diámetro Interno (mm)", 
                        font=dict(size=14)
                    ),
                    tickfont=dict(size=12),
                    showgrid=True,  # Mostrar líneas verticales de cuadrícula
                    gridwidth=1,
                    gridcolor='LightGray'
                ),
                yaxis=dict(
                    title=dict(
                        text=y_label, 
                        font=dict(size=14)
                    ),
                    tickfont=dict(size=12),
                    showgrid=True,  # Mostrar líneas horizontales de cuadrícula
                    gridwidth=1,
                    gridcolor='LightGray'
                ),
                height=600,  # Cambiado a 600 para gráficos cuadrados
                width=600,   # Agregado width para gráficos cuadrados
                margin=dict(l=80, r=80, t=80, b=120),
                legend=dict(
                    orientation="h", 
                    yanchor="top", y=-0.25, 
                    xanchor="center", x=0.5, 
                    font=dict(size=12),
                    bgcolor="rgba(255,255,255,0.8)"
                ),
                hovermode="x unified", 
                template="plotly_white",
                font=dict(family="Inter, sans-serif")
            )
            if asintota:
                fig.add_vline(x=asintota, line_dash="dot", line_color="#888", 
                              annotation_text="Límite Técnico", annotation_position="top right")

        # FILA 1: Velocidad y Pérdidas
        row1_c1, row1_c2 = st.columns(2)
        
        # 1. Velocidad
        asint_v = detectar_asintota_tecnica(df['di_mm'].values, df['velocity'].values)
        fv = go.Figure()
        fv.add_trace(go.Scatter(x=df['di_mm'], y=df['velocity'], mode='lines', name='Tendencia (PROYECTO)', line=dict(color='#007bff', width=2.5)))
        # PUNTO ANALIZADO (ESTRELLA ROJA)
        fv.add_trace(go.Scatter(x=[di_eval], y=[pt['velocity']], mode='markers', name='Análisis Manual', marker=dict(size=13, color='red', symbol='star', line=dict(color='black', width=1.5))))
        # DISEÑO ACTUAL (DIAMANTE AZUL)
        fv.add_trace(go.Scatter(x=[dn_actual], y=[v_actual], mode='markers', name='Diseño Actual', marker=dict(size=11, color='cyan', symbol='diamond', line=dict(color='black', width=1.5))))
        # INDICADOR IA (Óptimo Genético)
        if ga_data:
            fv.add_trace(go.Scatter(x=[di_ia], y=[v_ia], mode='markers', name='Óptimo IA (AG)', marker=dict(size=14, color='lime', symbol='star-diamond', line=dict(color='green', width=2))))

        vmin, vmax = (0.6, 0.9) if is_suc else (1.0, 2.5)
        # Agregar líneas horizontales con etiquetas para límites de velocidad
        fv.add_hline(y=vmax, line_dash="dash", line_color="#dc3545", 
                     annotation_text=f"Límite superior: {vmax} m/s", 
                     annotation_position="right")
        fv.add_hline(y=vmin, line_dash="dash", line_color="#28a745",
                     annotation_text=f"Límite inferior: {vmin} m/s",
                     annotation_position="right")
        # Agregar línea vertical solo para el diámetro correspondiente (succión o impulsión)
        if is_suc:
            diam_ref = st.session_state.get('diam_succion_mm', None)
            if diam_ref and diam_ref > 0:
                fv.add_vline(x=diam_ref, line_dash="dash", line_color="blue",
                            annotation_text=f"Succión: {diam_ref:.0f} mm",
                            annotation_position="top")
        else:
            diam_ref = st.session_state.get('diam_impulsion_mm', None)
            if diam_ref and diam_ref > 0:
                fv.add_vline(x=diam_ref, line_dash="dash", line_color="red",
                            annotation_text=f"Impulsión: {diam_ref:.0f} mm",
                            annotation_position="top")
        
        apply_style(fv, "Velocidad vs Diámetro", "v (m/s)", asintota=asint_v)
        row1_c1.plotly_chart(fv, use_container_width=True, key=f"chart_v_{prefix}")
        
        v_msg, v_stat = interpretar_punto_grafico("velocidad", pt['velocity'], asint_v, is_suc, meta=di_eval, di_especifico=di_eval)
        row1_c1.markdown(v_msg, unsafe_allow_html=True)

        # 2. Pérdidas
        asint_h = detectar_asintota_tecnica(df['di_mm'].values, df['friction_loss'].values)
        fh = go.Figure()
        fh.add_trace(go.Scatter(x=df['di_mm'], y=df['friction_loss'], mode='lines', name='Pérdidas (PROY)', line=dict(color='#fd7e14', width=2.5)))
        
        # Sombreado de Zona Roja (Pérdidas Exponenciales)
        if asint_h:
            fh.add_vrect(x0=df['di_mm'].min(), x1=asint_h, fillcolor="red", opacity=0.1, layer="below", line_width=0, annotation_text="ZONA ROJA")
            fh.add_vline(x=asint_h * 1.25, line_dash="dash", line_color="orange", annotation_text="Margen 75%")

        fh.add_trace(go.Scatter(x=[di_eval], y=[pt['friction_loss']], mode='markers', name='Análisis Manual', marker=dict(size=13, color='red', symbol='star', line=dict(color='black', width=1.5))))
        fh.add_trace(go.Scatter(x=[dn_actual], y=[h_actual], mode='markers', name='Diseño Actual', marker=dict(size=11, color='cyan', symbol='diamond', line=dict(color='black', width=1.5))))
        if ga_data:
            fh.add_trace(go.Scatter(x=[di_ia], y=[h_ia], mode='markers', name='Óptimo IA (AG)', marker=dict(size=14, color='lime', symbol='star-diamond', line=dict(color='green', width=2))))
        
        # Agregar línea vertical solo para el diámetro correspondiente
        if is_suc:
            diam_ref = st.session_state.get('diam_succion_mm', None)
            if diam_ref and diam_ref > 0:
                fh.add_vline(x=diam_ref, line_dash="dash", line_color="blue",
                            annotation_text=f"Succión: {diam_ref:.0f} mm",
                            annotation_position="top")
        else:
            diam_ref = st.session_state.get('diam_impulsion_mm', None)
            if diam_ref and diam_ref > 0:
                fh.add_vline(x=diam_ref, line_dash="dash", line_color="red",
                            annotation_text=f"Impulsión: {diam_ref:.0f} mm",
                            annotation_position="top")
        
        apply_style(fh, "Pérdidas Totales (m)", "h (m)", asintota=asint_h)
        row1_c2.plotly_chart(fh, use_container_width=True, key=f"chart_h_{prefix}")
        
        h_msg, h_stat = interpretar_punto_grafico("perdidas", pt['friction_loss'], asint_h, is_suc, meta=di_eval, di_especifico=di_eval)
        row1_c2.markdown(h_msg, unsafe_allow_html=True)

        # FILA 2: Presión y NPSH/Reynolds
        row2_c1, row2_c2 = st.columns(2)
        
        # 3. Presión (Envolvente Técnica)
        fp = go.Figure()
        
        # Serie Dinámica (Presión de Trabajo) - Línea Gruesa y Vibrante
        fp.add_trace(go.Scatter(x=df['di_mm'], y=df['p_mpa'], mode='lines', name='P. Operativa', line=dict(color='#d63384', width=4)))
        
        # ELIMINADO: Serie Transitorios (Golpe de Ariete) - Solicitado por usuario
        # fp.add_trace(go.Scatter(x=df['di_mm'], y=df['p_total_surge'], mode='lines', name='P. + Ariete', line=dict(color='#fd7e14', width=2, dash='dash')))
        
        # Línea de Presión Estática (Caudal 0) - Azul Profundo
        fp.add_trace(go.Scatter(x=df['di_mm'], y=[df['p_static_mpa'].iloc[0]]*len(df), mode='lines', name='P. Estática', line=dict(color='#0056b3', width=1.5, dash='dot')))
        
        # Línea de Presión de Prueba (1.5 * PN) - Verde Bosque
        fp.add_trace(go.Scatter(x=df['di_mm'], y=df['p_test'], mode='lines', name='P. Prueba (1.5*PN)', line=dict(color='#198754', width=1.5, dash='dot')))
        
        if is_suc:
            # Línea de Presión de Vapor (Cavitación) - Rojo Alerta
            fp.add_trace(go.Scatter(x=df['di_mm'], y=[p_vap_gauge_mpa]*len(df), mode='lines', name='P. Vapor (Límite)', line=dict(color='#dc3545', width=2, dash='longdash')))

        # Puntos de Referencia
        fp.add_trace(go.Scatter(x=[di_eval], y=[pt['pressure_kpa'] / 1000.0], mode='markers', name='Análisis Manual', marker=dict(size=12, color='red', symbol='star', line=dict(color='black', width=1))))
        fp.add_trace(go.Scatter(x=[dn_actual], y=[p_actual / 1000.0], mode='markers', name='Diseño Actual', marker=dict(size=10, color='cyan', symbol='diamond', line=dict(color='black', width=1))))

        # Líneas de PN
        if is_suc:
            pn_val = st.session_state.get('presion_nominal_succion', 0.5)
        else:
            pn_val = st.session_state.get('presion_nominal_impulsion', 1.0)
            
        fp.add_hline(y=pn_val, line_dash="dash", line_color="#dc3545", annotation_text=f"PN {pn_val:.1f} MPa")
        fp.add_hline(y=pn_val*0.8, line_dash="dot", line_color="#dee2e6", annotation_text="Límite 80% PN")
        
        # Rango Inteligente de Y: No mostrar los picos teóricos absurdos (ej. 400 MPa) de diámetros minúsculos
        # Limitamos a 2.0 * presión nominal o 2.0 * presión operativa máxima en el punto de diseño
        y_max_limit = max(pn_val * 1.6, abs(p_actual/1000.0)*2.0, 0.5)
        y_min_limit = min(df['p_mpa'].min()*1.2, p_vap_gauge_mpa*1.5 if is_suc else 0)
        
        apply_style(fp, "Riesgo de Cavitación", "P (MPa)", asintota=detectar_asintota_tecnica(df['di_mm'], df['p_mpa']))
        fp.update_layout(yaxis=dict(range=[y_min_limit, y_max_limit], tickformat=".2f"))
        
        # Agregar línea vertical solo para el diámetro correspondiente
        if is_suc:
            diam_ref = st.session_state.get('diam_succion_mm', None)
            if diam_ref and diam_ref > 0:
                fp.add_vline(x=diam_ref, line_dash="dash", line_color="blue",
                            annotation_text=f"Succión: {diam_ref:.0f} mm",
                            annotation_position="top")
        else:
            diam_ref = st.session_state.get('diam_impulsion_mm', None)
            if diam_ref and diam_ref > 0:
                fp.add_vline(x=diam_ref, line_dash="dash", line_color="red",
                            annotation_text=f"Impulsión: {diam_ref:.0f} mm",
                            annotation_position="top")
        
        row2_c1.plotly_chart(fp, use_container_width=True, key=f"chart_p_{prefix}")
        
        p_msg, p_stat = interpretar_punto_grafico("presion", pt['pressure_kpa'] / 1000.0, None, is_suc, meta=pn_val, di_especifico=di_eval)
        row2_c1.markdown(p_msg, unsafe_allow_html=True)

        # 4. NPSH / Reynolds
        if is_suc:
            asint_n = detectar_asintota_tecnica(df['di_mm'].values, df['npsh_available'].values)
            fn = go.Figure()
            fn.add_trace(go.Scatter(x=df['di_mm'], y=df['npsh_available'], mode='lines', name='NPSH Disp (PROY)', line=dict(color='#20c997', width=2.5)))
            fn.add_trace(go.Scatter(x=[di_eval], y=[pt['npsh_available']], mode='markers', name='Análisis Manual', marker=dict(size=13, color='red', symbol='star', line=dict(color='black', width=1.5))))
            fn.add_trace(go.Scatter(x=[dn_actual], y=[n_actual], mode='markers', name='Diseño Actual', marker=dict(size=11, color='cyan', symbol='diamond', line=dict(color='black', width=1.5))))
            if ga_data:
                fn.add_trace(go.Scatter(x=[di_ia], y=[n_ia], mode='markers', name='Óptimo IA (AG)', marker=dict(size=14, color='lime', symbol='star-diamond', line=dict(color='green', width=2))))
            apply_style(fn, "Seguridad NPSH", "NPSH (m)", asintota=asint_n)
            row2_c2.plotly_chart(fn, use_container_width=True, key=f"chart_npsh_{prefix}")
            n_msg, n_stat = interpretar_punto_grafico("npsh", pt['npsh_available'], asint_n, is_suc, meta=nr, di_especifico=di_eval)
            row2_c2.markdown(n_msg, unsafe_allow_html=True)
        else:
            asint_r = detectar_asintota_tecnica(df['di_mm'].values, df['reynolds'].values)
            fr = go.Figure()
            fr.add_trace(go.Scatter(x=df['di_mm'], y=df['reynolds'], mode='lines', name='Reynolds (PROY)', line=dict(color='#6f42c1', width=2.5)))
            fr.add_trace(go.Scatter(x=[di_eval], y=[pt['reynolds']], mode='markers', name='Análisis Manual', marker=dict(size=13, color='red', symbol='star', line=dict(color='black', width=1.5))))
            fr.add_trace(go.Scatter(x=[dn_actual], y=[re_actual], mode='markers', name='Diseño Actual', marker=dict(size=11, color='cyan', symbol='diamond', line=dict(color='black', width=1.5))))
            if ga_data:
                fr.add_trace(go.Scatter(x=[di_ia], y=[re_ia], mode='markers', name='Óptimo IA (AG)', marker=dict(size=14, color='lime', symbol='star-diamond', line=dict(color='green', width=2))))
            # Agregar líneas horizontales para límites de régimen
            fr.add_hline(y=2300, line_dash="dash", line_color="red",
                        annotation_text="Laminar/Transición (Re=2300)",
                        annotation_position="right")
            fr.add_hline(y=4000, line_dash="dash", line_color="orange",
                        annotation_text="Transición/Turbulento (Re=4000)",
                        annotation_position="right")
            
            # Agregar línea vertical solo para el diámetro correspondiente
            if is_suc:
                diam_ref = st.session_state.get('diam_succion_mm', None)
                if diam_ref and diam_ref > 0:
                    fr.add_vline(x=diam_ref, line_dash="dash", line_color="blue",
                                annotation_text=f"Succión: {diam_ref:.0f} mm",
                                annotation_position="top")
            else:
                diam_ref = st.session_state.get('diam_impulsion_mm', None)
                if diam_ref and diam_ref > 0:
                    fr.add_vline(x=diam_ref, line_dash="dash", line_color="red",
                                annotation_text=f"Impulsión: {diam_ref:.0f} mm",
                                annotation_position="top")
            
            apply_style(fr, "Régimen de Flujo (Reynolds)", "Re", asintota=asint_r)
            # Configurar escala logarítmica en eje Y
            fr.update_yaxes(type='log')
            row2_c2.plotly_chart(fr, use_container_width=True, key=f"chart_re_{prefix}")
            re_msg, re_stat = interpretar_punto_grafico("reynolds", pt['reynolds'], asint_r, is_suc, meta=pt['regime'], di_especifico=di_eval)
            row2_c2.markdown(re_msg, unsafe_allow_html=True)

        # FILA 3: Factor de Fricción y Gradiente Hidráulico
        row3_c1, row3_c2 = st.columns(2)
        
        # 5. Factor de Fricción
        asint_f = detectar_asintota_tecnica(df['di_mm'].values, df['friction_factor'].values)
        ff = go.Figure()
        ff.add_trace(go.Scatter(x=df['di_mm'], y=df['friction_factor'], mode='lines', name='Factor f (PROY)', line=dict(color='#ffc107', width=2.5)))
        ff.add_trace(go.Scatter(x=[di_eval], y=[pt['friction_factor']], mode='markers', name='Análisis Manual', marker=dict(size=13, color='red', symbol='star', line=dict(color='black', width=1.5))))
        ff.add_trace(go.Scatter(x=[dn_actual], y=[f_actual], mode='markers', name='Diseño Actual', marker=dict(size=11, color='cyan', symbol='diamond', line=dict(color='black', width=1.5))))
        if ga_data:
            ff.add_trace(go.Scatter(x=[di_ia], y=[f_ia], mode='markers', name='Óptimo IA (AG)', marker=dict(size=14, color='lime', symbol='star-diamond', line=dict(color='green', width=2))))
        
        # Agregar línea vertical solo para el diámetro correspondiente
        if is_suc:
            diam_ref = st.session_state.get('diam_succion_mm', None)
            if diam_ref and diam_ref > 0:
                ff.add_vline(x=diam_ref, line_dash="dash", line_color="blue",
                            annotation_text=f"Succión: {diam_ref:.0f} mm",
                            annotation_position="top")
        else:
            diam_ref = st.session_state.get('diam_impulsion_mm', None)
            if diam_ref and diam_ref > 0:
                ff.add_vline(x=diam_ref, line_dash="dash", line_color="red",
                            annotation_text=f"Impulsión: {diam_ref:.0f} mm",
                            annotation_position="top")
        
        apply_style(ff, "Factor de Fricción (f)", "f", asintota=asint_f)
        row3_c1.plotly_chart(ff, use_container_width=True, key=f"chart_f_{prefix}")
        
        darcy_active = metodo_calculo == 'Darcy-Weisbach'
        f_msg, f_stat = interpretar_punto_grafico("friccion", pt['friction_factor'] if darcy_active else -1, asint_f, is_suc, di_especifico=di_eval)
        row3_c1.markdown(f_msg, unsafe_allow_html=True)

        # 6. Gradiente Hidráulico
        asint_j = detectar_asintota_tecnica(df['di_mm'].values, (df['hydraulic_gradient']*1000).values)
        fg = go.Figure()
        fg.add_trace(go.Scatter(x=df['di_mm'], y=df['hydraulic_gradient']*1000, mode='lines', name='J (PROY)', line=dict(color='#6610f2', width=2.5)))
        fg.add_trace(go.Scatter(x=[di_eval], y=[pt['hydraulic_gradient']*1000], mode='markers', name='Análisis Manual', marker=dict(size=13, color='red', symbol='star', line=dict(color='black', width=1.5))))
        fg.add_trace(go.Scatter(x=[dn_actual], y=[j_actual], mode='markers', name='Diseño Actual', marker=dict(size=11, color='cyan', symbol='diamond', line=dict(color='black', width=1.5))))
        if ga_data:
            fg.add_trace(go.Scatter(x=[di_ia], y=[j_ia], mode='markers', name='Óptimo IA (AG)', marker=dict(size=14, color='lime', symbol='star-diamond', line=dict(color='green', width=2))))
        
        # Agregar línea vertical solo para el diámetro correspondiente
        if is_suc:
            diam_ref = st.session_state.get('diam_succion_mm', None)
            if diam_ref and diam_ref > 0:
                fg.add_vline(x=diam_ref, line_dash="dash", line_color="blue",
                            annotation_text=f"Succión: {diam_ref:.0f} mm",
                            annotation_position="top")
        else:
            diam_ref = st.session_state.get('diam_impulsion_mm', None)
            if diam_ref and diam_ref > 0:
                fg.add_vline(x=diam_ref, line_dash="dash", line_color="red",
                            annotation_text=f"Impulsión: {diam_ref:.0f} mm",
                            annotation_position="top")
        
        apply_style(fg, "Gradiente Hidráulico (J)", "J (m/km)", asintota=asint_j)
        row3_c2.plotly_chart(fg, use_container_width=True, key=f"chart_j_{prefix}")
        j_msg, j_stat = interpretar_punto_grafico("gradiente", pt['hydraulic_gradient']*1000, asint_j, is_suc, di_especifico=di_eval)
        row3_c2.markdown(j_msg, unsafe_allow_html=True)

        # FILA 4: Sumergencia/CAPEX y Costo Energético/Reynolds
        row4_c1, row4_c2 = st.columns(2)
        
        # 7. Sumergencia / Inversión
        if is_suc:
            fs = go.Figure()
            fs.add_trace(go.Scatter(x=df['di_mm'], y=df['submergence_min'], mode='lines', name='S min (PROY)', line=dict(color='#17a2b8', width=2.5)))
            fs.add_trace(go.Scatter(x=[di_eval], y=[pt['submergence_min']], mode='markers', name='Análisis Manual', marker=dict(size=13, color='red', symbol='star', line=dict(color='black', width=1.5))))
            fs.add_trace(go.Scatter(x=[dn_actual], y=[s_actual], mode='markers', name='Diseño Actual', marker=dict(size=11, color='cyan', symbol='diamond', line=dict(color='black', width=1.5))))
            if ga_data:
                fs.add_trace(go.Scatter(x=[di_ia], y=[s_ia], mode='markers', name='Óptimo IA (AG)', marker=dict(size=14, color='lime', symbol='star-diamond', line=dict(color='green', width=2))))
            apply_style(fs, "Sumergencia Mínima", "S (m)")
            row4_c1.plotly_chart(fs, use_container_width=True, key=f"chart_sumer_{prefix}")
            s_msg, s_stat = interpretar_punto_grafico("sumergencia", pt['submergence_min'], None, is_suc, di_especifico=di_eval)
            row4_c1.markdown(s_msg, unsafe_allow_html=True)
        else:
            fe = go.Figure()
            fe.add_trace(go.Scatter(x=df['di_mm'], y=df['capex'], mode='lines', name='Inversión (PROY)', line=dict(color='#20c997', width=2.5)))
            fe.add_trace(go.Scatter(x=[di_eval], y=[pt['capex']], mode='markers', name='Análisis Manual', marker=dict(size=13, color='red', symbol='star', line=dict(color='black', width=1.5))))
            fe.add_trace(go.Scatter(x=[dn_actual], y=[c_actual], mode='markers', name='Diseño Actual', marker=dict(size=11, color='cyan', symbol='diamond', line=dict(color='black', width=1.5))))
            if ga_data:
                fe.add_trace(go.Scatter(x=[di_ia], y=[c_ia], mode='markers', name='Óptimo IA (AG)', marker=dict(size=14, color='lime', symbol='star-diamond', line=dict(color='green', width=2))))
            apply_style(fe, "Inversión Relativa (CAPEX)", "CAPEX")
            row4_c1.plotly_chart(fe, use_container_width=True, key=f"chart_capex_{prefix}")
            c_msg, c_stat = interpretar_punto_grafico("capex", pt['capex'], None, is_suc, di_especifico=di_eval)
            row4_c1.markdown(c_msg, unsafe_allow_html=True)

        # 8. OPEX
        if not is_suc: 
            fo = go.Figure()
            fo.add_trace(go.Scatter(x=df['di_mm'], y=df['energy_cost_annual'], mode='lines', name='Costo Anual (PROY)', line=dict(color='#dc3545', width=2.5)))
            fo.add_trace(go.Scatter(x=[di_eval], y=[pt['energy_cost_annual']], mode='markers', name='Análisis Manual', marker=dict(size=13, color='red', symbol='star', line=dict(color='black', width=1.5))))
            fo.add_trace(go.Scatter(x=[dn_actual], y=[o_actual], mode='markers', name='Diseño Actual', marker=dict(size=11, color='cyan', symbol='diamond', line=dict(color='black', width=1.5))))
            if ga_data:
                fo.add_trace(go.Scatter(x=[di_ia], y=[o_ia], mode='markers', name='Óptimo IA (AG)', marker=dict(size=14, color='lime', symbol='star-diamond', line=dict(color='green', width=2))))
            apply_style(fo, "Gasto Energético (OPEX)", "USD/año")
            row4_c2.plotly_chart(fo, use_container_width=True, key=f"chart_energy_{prefix}")
            o_msg, o_stat = interpretar_punto_grafico("opex", pt['energy_cost_annual'], None, is_suc, di_especifico=di_eval)
            row4_c2.markdown(o_msg, unsafe_allow_html=True)
        else:
            fr_suc = go.Figure()
            fr_suc.add_trace(go.Scatter(x=df['di_mm'], y=df['reynolds'], mode='lines', name='Reynolds (PROY)', line=dict(color='#6f42c1', width=2.5)))
            fr_suc.add_trace(go.Scatter(x=[di_eval], y=[pt['reynolds']], mode='markers', name='Análisis Manual', marker=dict(size=13, color='red', symbol='star', line=dict(color='black', width=1.5))))
            fr_suc.add_trace(go.Scatter(x=[dn_actual], y=[re_actual], mode='markers', name='Diseño Actual', marker=dict(size=11, color='cyan', symbol='diamond', line=dict(color='black', width=1.5))))
            if ga_data:
                fr_suc.add_trace(go.Scatter(x=[di_ia], y=[re_ia], mode='markers', name='Óptimo IA (AG)', marker=dict(size=14, color='lime', symbol='star-diamond', line=dict(color='green', width=2))))
            
            # Agregar líneas horizontales para límites de régimen
            fr_suc.add_hline(y=2300, line_dash="dash", line_color="red",
                        annotation_text="Laminar/Transición (Re=2300)",
                        annotation_position="right")
            fr_suc.add_hline(y=4000, line_dash="dash", line_color="orange",
                        annotation_text="Transición/Turbulento (Re=4000)",
                        annotation_position="right")
            
            # Agregar línea vertical solo para el diámetro correspondiente
            diam_ref = st.session_state.get('diam_succion_mm', None)
            if diam_ref and diam_ref > 0:
                fr_suc.add_vline(x=diam_ref, line_dash="dash", line_color="blue",
                            annotation_text=f"Succión: {diam_ref:.0f} mm",
                            annotation_position="top")
            
            apply_style(fr_suc, "Régimen de Flujo (Reynolds)", "Re")
            # Configurar escala logarítmica en eje Y
            fr_suc.update_yaxes(type='log')
            row4_c2.plotly_chart(fr_suc, use_container_width=True, key=f"chart_re_suc_{prefix}")
            re_msg, re_stat = interpretar_punto_grafico("reynolds", pt['reynolds'], None, is_suc, meta=pt['regime'], di_especifico=di_eval)
            row4_c2.markdown(re_msg, unsafe_allow_html=True)

def render_loss_analysis_tab(q_design_lps_sess, p_atm, temp, p_vap, nr):
    st.subheader("📈 Análisis de Vulnerabilidad: Control de Pérdidas")
    
    col_input, col_chart = st.columns([0.25, 0.75])
    
    with col_input:
        st.info("💡 Herramienta de simulación: Varía el Caudal, Diámetro o Material para ver cómo se comporta la resiliencia del sistema.")
        
        tipo_tramo = st.radio("Tramo base", ["Impulsión", "Succión"], key="loss_tab_tipo")
        is_suc = tipo_tramo == "Succión"
        prefix_sess = "suc" if is_suc else "imp"
        
        # --- CONTROLES INTERACTIVOS ---
        # 1. Caudal Interactivo (Slider de 0 a 3x Q_diseño)
        q_limit = float(max(q_design_lps_sess * 2, 10.0))
        q_sim = st.slider("Caudal de Simulación (L/s)", 0.0, q_limit, float(q_design_lps_sess), step=0.5, key="q_sim_loss")
        
        # 2. Material Interactivo
        options_mat = ["PVC", "HDPE (Polietileno)", "Hierro Ductil", "Hierro Fundido"]
        mat_sess = st.session_state.get(f'mat_sel_{prefix_sess}', options_mat[0])
        idx_mat = 0
        mat_sess_upper = str(mat_sess).upper()
        if "PVC" in mat_sess_upper: idx_mat = 0
        elif "PEAD" in mat_sess_upper or "HDPE" in mat_sess_upper: idx_mat = 1
        elif "HIERRO" in mat_sess_upper and "DUCTIL" in mat_sess_upper: idx_mat = 2
        elif "HIERRO" in mat_sess_upper and "FUNDIDO" in mat_sess_upper: idx_mat = 3
        
        mat_sim = st.selectbox("Material Interactivo", options_mat, index=idx_mat, key="mat_sim_loss")
        
        # 3. Diámetro Interactivo
        db = cargar_diametros_comerciales(mat_sim)
        dn_actual_sess = st.session_state.get(f'last_pt_di_{prefix_sess}', 100.0)
        
        idx_dn = -1
        if db:
            for i, d in enumerate(db): 
                if abs(float(d[1]) - float(dn_actual_sess)) < 0.5: 
                    idx_dn = i
                    break
            options_dn = [f"{d[0]} (DI: {d[1]:.1f} mm)" for d in db] + ["🛠️ Personalizado"]
            if idx_dn == -1: idx_dn = len(options_dn) - 1
            
            sel_dn_label = st.selectbox("Diámetro Interactivo", options_dn, index=idx_dn, key="dn_sim_loss")
            if "Personalizado" in sel_dn_label:
                di_sim = st.number_input("DI Personalizado (mm)", value=float(dn_actual_sess), key="di_cust_loss")
            else:
                di_sim = db[options_dn.index(sel_dn_label)][1]
        else:
            di_sim = st.number_input("DI Interactivo (mm)", value=float(dn_actual_sess), key="di_man_loss")

        # 4. Longitud y Accesorios (Sincronizados)
        length = st.session_state.get(f'len_pt_{prefix_sess}', 100.0)
        le_m = st.session_state.get(f'le_m_pt_{prefix_sess}', 0.0)
        h_est = st.session_state.get('h_suc_input', 2.0) if (is_suc and st.session_state.get('bomba_inundada', False)) else (st.session_state.get('altura_descarga', 80.0) if not is_suc else -st.session_state.get('h_suc_input', 2.0))
        
        st.markdown("---")
        st.markdown("""
        **Guía de Colores:**
        - 🟢 **Zona Lineal:** Eficiencia máxima.
        - 🟠 **Límite 75%:** Margen de seguridad.
        - 🔴 **Zona Roja:** Pérdidas exponenciales.
        """)

    with col_chart:
        # Algoritmo de Detección de Zona Roja (Transición Lineal -> Parabólica)
        q_max_graph = max(q_sim * 2.5, 50.0)
        q_range = np.linspace(0.1, q_max_graph, 60)
        le_d_calc = le_m / (di_sim / 1000.0) if di_sim > 0 else 0
        
        analyzer = PipeDiameterAnalyzer(
            fluid_props={'density': 1000.0, 'viscosity': obtener_viscosidad_cinematica(temp), 'vapor_pressure': p_vap},
            operating_conditions={'flow_rate': q_sim/1000.0, 'temperature': temp, 'atmospheric_pressure': p_atm, 'npsh_required': nr, 'static_head': h_est},
            pipe_params={'length': length, 'absolute_roughness': obtener_rugosidad_absoluta(mat_sim), 'le_over_d': le_d_calc},
            calculation_method=st.session_state.get('metodo_calculo', 'Darcy-Weisbach'),
            hazen_c=150
        )
        
        losses = []
        for q in q_range:
            analyzer.ops['flow_rate'] = q / 1000.0
            res = analyzer.analyze_range([di_sim], is_suction=is_suc)
            losses.append(res.iloc[0]['friction_loss'])
            
        losses = np.array(losses)
        
        # Detección matemática: Donde la pendiente (1era derivada) empieza a aumentar rápido (2da derivada)
        slopes = np.gradient(losses, q_range)
        acceleration = np.gradient(slopes, q_range)
        
        # El "Codo" es donde la aceleración de pérdidas supera un umbral relativo
        # O donde la pérdida se desvía un X% de la proyección lineal inicial
        # Usamos un criterio de sensibilidad: donde la pendiente es 2.2 veces la inicial
        idx_crit = 0
        for i, s in enumerate(slopes):
            if s > slopes[0] * 2.5: # Criterio de "Zona Roja"
                idx_crit = i
                break
        q_crit = q_range[idx_crit] if idx_crit > 0 else q_range[-1]
        
        # 1. Gráfico Principal: Caudal vs Pérdidas
        fq = go.Figure()
        fq.add_trace(go.Scatter(x=q_range, y=losses, mode='lines', name='Curva de Pérdidas', line=dict(color='#007bff', width=3.5)))
        
        # Marcador Q Simulado
        y_sim = np.interp(q_sim, q_range, losses)
        fq.add_trace(go.Scatter(x=[q_sim], y=[y_sim], mode='markers+text', 
                                name='Punto Simulado', text=[f"📍 {q_sim:.1f} L/s"], textposition="top center",
                                marker=dict(size=14, color='red', symbol='star', line=dict(color='black', width=1))))
        
        # Sombrear Zona Roja con Interpretación de Detección
        fq.add_vrect(x0=q_crit, x1=q_range[-1], fillcolor="red", opacity=0.15, layer="below", line_width=0, 
                    annotation_text="ZONA ROJA (FRÁGIL)", annotation_position="top left")
        
        # Margen del 75%
        q_margin = q_crit * 0.75
        fq.add_vline(x=q_margin, line_dash="dash", line_color="orange", annotation_text="Margen 75% (Seguridad)")
        
        fq.update_layout(
            title=f"<b>Gráfico Caudal vs Pérdidas (Simulación)</b><br><span style='font-size:12px; color:#666;'>Material: {mat_sim} | DI: {di_sim:.1f} mm</span>",
            xaxis_title="Caudal (L/s)", yaxis_title="Pérdida de Carga (m)",
            template="plotly_white", height=500,
            hovermode="x unified",
            margin=dict(t=100)
        )
        st.plotly_chart(fq, use_container_width=True)
        
        # Diagnóstico de Resiliencia Dinámico
        resiliencia_pct = (q_crit / q_sim) * 100 if q_sim > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Punto de Inflexión", f"{q_crit:.1f} L/s", delta="Zona Crítica", delta_color="inverse")
        c2.metric("Margen de Seguridad", f"{q_margin:.1f} L/s", delta="Límite 75%")
        c3.metric("Resiliencia Actual", f"{resiliencia_pct:.0f}%", delta="Capacidad de Crecimiento")

        if q_sim >= q_crit:
            st.error(f"🚨 **VULNERABILIDAD ALTA:** El caudal de {q_sim:.1f} L/s opera en la **Zona Roja**. Cualquier demanda extra disparará las pérdidas sin control.")
        elif q_sim >= q_margin:
            st.warning(f"⚠️ **DISEÑO AJUSTADO:** Operas por encima del margen de seguridad del 75%. El sistema tiene poca flexibilidad ante aumentos inesperados.")
        else:
            st.success(f"✅ **DISEÑO ROBUSTO:** Operas en la zona lineal segura. Tienes un margen del {resiliencia_pct-100:.0f}% antes de que la tubería se vuelva 'frágil'.")

        # 2. Comparativa Interactiva (Cambio de Diámetro)
        st.markdown("---")
        st.subheader("⚖️ Impacto del Tamaño en la Estabilidad")
        st.write("Mira cómo las curvas se aplanan y la 'Zona Roja' se aleja al aumentar el diámetro.")
        
        # Seleccionamos rangos comerciales alrededor del actual para comparar
        dn_list_comp = sorted([d[1] for d in db if abs(d[1]-di_sim) < 100][:3])
        if di_sim not in dn_list_comp: dn_list_comp.append(di_sim)
        dn_list_comp = sorted(dn_list_comp)
        
        fc = go.Figure()
        for d in dn_list_comp:
            l_comp = []
            for q in q_range:
                analyzer.ops['flow_rate'] = q / 1000.0
                analyzer.pipe['le_over_d'] = le_m / (d/1000.0) if d > 0 else 0
                res = analyzer.analyze_range([d], is_suction=is_suc)
                l_comp.append(res.iloc[0]['friction_loss'])
            
            is_active = abs(d - di_sim) < 0.1
            fc.add_trace(go.Scatter(x=q_range, y=l_comp, mode='lines', 
                                    name=f"DI {d:.1f} mm {'(Actual)' if is_active else ''}",
                                    line=dict(width=4 if is_active else 2, dash=None if is_active else 'dot')))
            
        fc.update_layout(title="<b>Comparativa de Curvas de Ineficiencia</b>", xaxis_title="Caudal (L/s)", yaxis_title="Pérdida (m)", template="plotly_white", height=450)
        st.plotly_chart(fc, use_container_width=True)
