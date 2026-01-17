# Pestañas principales de la aplicación

import streamlit as st
import pandas as pd
import numpy as np
import json
import io
import math
import os
import plotly.graph_objects as go
from scipy.optimize import fsolve
from typing import Dict, Any
from ui.ai_module import render_ai_question_response
from ui.transient_tab import render_transient_tab as render_transient_simulation_tab
from ui.transients import render_transient_tab
from ui.html_generator import generate_html_report
from ui.tabs_modules.common import render_footer

def calculate_smart_axes(q_op, val_op, val_static=0, val_max_data=10, tipo_grafico="hq", q_max_curve=None, val_max_curve=None):
    """
    Calcula rangos inteligentes para los ejes de los gráficos basándose en el punto de operación
    y los valores máximos reales de las curvas.
    
    Args:
        q_op: Caudal de operación
        val_op: Valor de operación (altura, potencia, rendimiento, NPSH)
        val_static: Valor estático (para H-Q)
        val_max_data: Valor máximo de datos (fallback)
        tipo_grafico: Tipo de gráfico ("hq", "potencia", "rendimiento", "npsh")
        q_max_curve: Caudal máximo de la curva (opcional)
        val_max_curve: Valor máximo de la curva (opcional)
    """
    # Eje X: Usar el máximo de la curva si está disponible, sino centrar en operación
    if q_max_curve and q_max_curve > 0:
        x_max = q_max_curve * 1.05  # Solo 5% de margen para que ocupe casi todo el área
    elif q_op and q_op > 0:
        x_max = q_op * 1.4  # Reducido de 1.6 a 1.4 para mejor ajuste
    else:
        x_max = val_max_data * 1.1 if val_max_data > 0 else 5.0
    
    x_range = [0, x_max]
    
    # Eje Y: Depende del tipo de gráfico y usa valores máximos reales
    if tipo_grafico == "hq":
        # Altura Dinámica: Desde un poco menos de la estática hasta un poco más del máximo
        y_min = val_static * 0.95 if val_static > 0 else 0
        if val_max_curve and val_max_curve > 0:
            y_max = val_max_curve * 1.05  # Solo 5% de margen
        else:
            y_max = max(val_op * 1.2, val_static * 1.1) if val_op > 0 else 100.0
        y_range = [y_min, y_max]
    elif tipo_grafico == "rendimiento":
        # Rendimiento: Ajustar al máximo real de la curva o BEP
        if val_max_curve and val_max_curve > 0:
            y_max = min(100.0, val_max_curve * 1.05)  
        else:
            y_max = min(100.0, max(val_op * 1.1, 80.0)) if val_op > 0 else 100.0
        y_range = [0, y_max]
    elif tipo_grafico == "potencia":
        # Potencia: Ajustar al máximo real de la curva
        if val_max_curve and val_max_curve > 0:
            y_max = val_max_curve * 1.05  # Solo 5% de margen
        else:
            y_max = val_op * 1.2 if val_op > 0 else 50.0
        y_range = [0, y_max]
    elif tipo_grafico == "npsh":
        # NPSH: Ajustar al máximo real de la curva
        if val_max_curve and val_max_curve > 0:
            y_max = val_max_curve * 1.1  # 10% de margen para NPSH (para que no toque el borde superior bruscamente)
        else:
            y_max = max(val_op * 2.0, 10.0) if val_op > 0 else 15.0
        y_range = [0, y_max]
    else:
        y_range = None
        
    return x_range, y_range

def render_analysis_tab():
    """Renderiza la pestaña de análisis de curvas"""
    from core.calculations import get_display_unit_label
    from ui.visualization import (
        create_hq_curve_plot,
        create_efficiency_curve_plot,
        create_power_curve_plot,
        create_npsh_curve_plot,
        create_vfd_analysis_plot,
        create_comprehensive_analysis_plot,
        create_results_table
    )
    
    # Procesar flag de reset de ejes de gráficos
    if st.session_state.get('_reset_graph_axes', False):
        # Limpiar valores existentes
        for key in ['graph_x_min', 'graph_x_max', 'graph_x_step', 'graph_y_min', 'graph_y_max']:
            if key in st.session_state:
                del st.session_state[key]
        del st.session_state['_reset_graph_axes']
        st.rerun()

    # Procesar flag de reset de ejes VFD
    if st.session_state.get('_reset_vfd_axes', False):
        for key in ['graph_vfd_x_min', 'graph_vfd_x_max', 'graph_vfd_y_min', 'graph_vfd_y_max']:
            if key in st.session_state:
                del st.session_state[key]
        del st.session_state['_reset_vfd_axes']
        st.rerun()
    
    from core.calculations import (
        process_curve_data,
        find_operating_point,
        calculate_adt_for_multiple_flows,
        convert_flow_unit,
        interpolar_propiedad
    )
    from core.curves import calculate_bep, calculate_efficiency_zone, interpolate_curve_value
    from core.system_head import generate_system_curve_points
    # --- Parámetros base ---
    n_bombas = st.session_state.get('num_bombas', 1)
    caudal_nominal_total = st.session_state.get('caudal_lps', 0)
    caudal_nominal = caudal_nominal_total / n_bombas if n_bombas > 0 else caudal_nominal_total
    
    # Inicializar listas de puntos para evitar NameError
    puntos_sistema = []
    puntos_bomba = []
    puntos_rend = []
    puntos_pot = []
    puntos_npsh = []
    interseccion = None
    power_op = 0
    op_npsh = 0
    op_rend = 0
    bep_q = 0
    bep_eta = 0
    rpm_percentage = st.session_state.get('rpm_percentage', 100.0)
    
    
    curva_mode = st.session_state.get('curva_mode_sidebar', 'Excel')
    if curva_mode == "Excel":
        st.subheader("1. Gráfico de Curvas desde Excel")
        st.info("Los datos de las curvas se cargan automáticamente desde el archivo Excel en la pestaña 'Datos del Proyecto'. Los gráficos se generan automáticamente con los datos cargados.")
        
        # Obtener datos de las curvas desde session_state
        curva_inputs = st.session_state.get('curva_inputs', {})
        ajuste_tipo = st.session_state.get('ajuste_tipo', 'Lineal')
        
        # Procesar datos de curvas si están disponibles
        if curva_inputs:
            st.success("✅ Datos de curvas cargados desde Excel")
            
            # Mostrar resumen de datos cargados
            curva_labels = {
                'bomba': 'Bomba H-Q',
                'rendimiento': 'Rendimiento',
                'potencia': 'Potencia', 
                'npsh': 'NPSH'
            }
            
            # Crear columnas dinámicamente según el número de curvas
            num_curvas = len(curva_labels)
            col_resumen = st.columns(num_curvas)
            
            for i, (curva_key, label) in enumerate(curva_labels.items()):
                if i < len(col_resumen):  # Verificar que el índice esté dentro del rango
                    with col_resumen[i]:
                        puntos = curva_inputs.get(curva_key, [])
                        st.metric(label, f"{len(puntos)} puntos")
        else:
            st.warning("⚠️ No hay datos de curvas cargados. Por favor, carga un archivo Excel en la pestaña 'Datos del Proyecto'.")
    else:
        st.subheader("6. Gráfico de Curvas 100% RPM")
        curva_inputs = st.session_state.get('curva_inputs', {})
        ajuste_tipo = st.session_state.get('ajuste_tipo', 'Lineal')

        # --- PRE-CALCULATIONS FOR 100% RPM ---
        interseccion = None
        
        # Procesar puntos de la bomba desde textarea con conversión de unidades
        puntos_bomba = []
        unidad_caudal = st.session_state.get('flow_unit', 'L/s')
        
        for curva_key in ['bomba', 'rendimiento', 'potencia', 'npsh']:
            textarea_content = st.session_state.get(f'textarea_{curva_key}', '')
            if textarea_content:
                lines = textarea_content.strip().split('\n')
                puntos = []
                for line in lines:
                    if line.strip():
                        try:
                            vals = [v for v in line.replace(';', ' ').replace('\t', ' ').split() if v]
                            if len(vals) >= 2:
                                x = float(vals[0])
                                y = float(vals[1])
                                
                                # Convertir caudal a L/s para cálculos internos
                                if unidad_caudal == 'm³/h':
                                    x = x / 3.6  # m³/h a L/s
                                
                                puntos.append([x, y])
                        except:
                            continue
                
                if curva_key == 'bomba':
                    puntos_bomba = puntos
                curva_inputs[curva_key] = puntos
        
        # No need to redefine caudal_nominal here as it's now at the top
        # Obtener puntos del sistema desde textarea_sistema o curva_inputs
        puntos_sistema = []
        
        # Primero intentar leer desde textarea_sistema
        if 'textarea_sistema' in st.session_state and st.session_state['textarea_sistema']:
            try:
                # Procesar el contenido del textarea
                texto_curva = st.session_state['textarea_sistema']
                lines = [line.strip() for line in texto_curva.splitlines() if line.strip()]
                
                for line in lines:
                    vals = [v for v in line.replace(';', ' ').replace('\t', ' ').split() if v]
                    if len(vals) == 2:
                        try:
                            x = float(vals[0])
                            y = float(vals[1])
                            
                            # Convertir caudal a L/s para cálculos internos
                            if unidad_caudal == 'm³/h':
                                x = x / 3.6  # m³/h a L/s
                            
                            puntos_sistema.append((x, y))
                        except Exception:
                            pass
            except Exception as e:
                st.warning(f"Error procesando puntos del sistema desde textarea: {e}")
        
        # Si no hay puntos en textarea, intentar desde curva_inputs
        if not puntos_sistema and 'sistema' in curva_inputs and curva_inputs['sistema']:
            puntos_sistema = curva_inputs['sistema']
        
        # Si aún no hay puntos, calcular automáticamente
        if not puntos_sistema:
            try:
                # Generar caudales para calcular la curva del sistema
                # Usar un rango representativo basado en el caudal nominal
                q_max = (caudal_nominal_total or 10.0) * 1.5
                flows = np.linspace(0, q_max, 20).tolist()
                flow_unit = st.session_state.get('flow_unit', 'L/s')
                
                # Obtener parámetros del sistema estandarizados
                system_params = {
                    'long_succion': st.session_state.get('long_succion', 10.0),
                    'diam_succion_m': st.session_state.get('diam_succion_mm', 200.0) / 1000.0,
                    'mat_succion': st.session_state.get('mat_succion', 'PVC'),
                    'otras_perdidas_succion': st.session_state.get('otras_perdidas_succion', 0.0),
                    'accesorios_succion': st.session_state.get('accesorios_succion', []),
                    'long_impulsion': st.session_state.get('long_impulsion', 500.0),
                    'diam_impulsion_m': st.session_state.get('diam_impulsion_mm', 150.0) / 1000.0,
                    'mat_impulsion': st.session_state.get('mat_impulsion', 'PVC'),
                    'otras_perdidas_impulsion': st.session_state.get('otras_perdidas_impulsion', 0.0),
                    'accesorios_impulsion': st.session_state.get('accesorios_impulsion', []),
                    'altura_succion': st.session_state.get('altura_succion_input', 1.65),
                    'altura_descarga': st.session_state.get('altura_descarga', 80.0),
                    'bomba_inundada': st.session_state.get('bomba_inundada', False),
                    'metodo_calculo': st.session_state.get('metodo_calculo', 'Hazen-Williams'),
                    'temp_liquido': st.session_state.get('temp_liquido', 20.0),
                    'C_succion': st.session_state.get('coeficiente_hazen_succion', 150),
                    'C_impulsion': st.session_state.get('coeficiente_hazen_impulsion', 150)
                }
                
                from core.calculations import calculate_adt_for_multiple_flows
                resultados_adt = calculate_adt_for_multiple_flows(flows, flow_unit, system_params)
                
                if resultados_adt:
                    # En el gráfico de análisis comparamos con UNA BOMBA INDIVIDUAL
                    puntos_sistema = []
                    for i, r in enumerate(resultados_adt):
                        # Escalar eje X: Caudal Total / N bombas
                        q_indiv = flows[i] / n_bombas if n_bombas > 0 else flows[i]
                        puntos_sistema.append((q_indiv, r['adt_total']))
            except Exception as e:
                st.warning(f"Error calculando curva del sistema en Análisis: {e}")

    # --- CÁLCULO CENTRALIZADO DE INTERSECCIÓN (100% RPM) ---
    interseccion = None
    if len(puntos_sistema) >= 2 and curva_inputs.get('bomba') and len(curva_inputs['bomba']) >= 2:
        try:
            x_sis = np.array([pt[0] for pt in puntos_sistema])
            y_sis = np.array([pt[1] for pt in puntos_sistema])
            x_bom = np.array([pt[0] for pt in curva_inputs['bomba']])
            y_bom = np.array([pt[1] for pt in curva_inputs['bomba']])
            
            grado = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
            coef_sis_calc = np.polyfit(x_sis, y_sis, grado)
            coef_bom_calc = np.polyfit(x_bom, y_bom, grado)
            
            # Calcular coeficientes de rendimiento, potencia y NPSH si hay datos
            coef_rend = None
            if 'rendimiento' in curva_inputs and len(curva_inputs['rendimiento']) >= 2:
                x_rend = np.array([pt[0] for pt in curva_inputs['rendimiento']])
                y_rend = np.array([pt[1] for pt in curva_inputs['rendimiento']])
                coef_rend = np.polyfit(x_rend, y_rend, grado)
            
            coef_pot = None
            if 'potencia' in curva_inputs and len(curva_inputs['potencia']) >= 2:
                x_pot = np.array([pt[0] for pt in curva_inputs['potencia']])
                y_pot = np.array([pt[1] for pt in curva_inputs['potencia']])
                coef_pot = np.polyfit(x_pot, y_pot, grado)
            
            coef_npsh = None
            if 'npsh' in curva_inputs and len(curva_inputs['npsh']) >= 2:
                x_npsh = np.array([pt[0] for pt in curva_inputs['npsh']])
                y_npsh = np.array([pt[1] for pt in curva_inputs['npsh']])
                coef_npsh = np.polyfit(x_npsh, y_npsh, grado)
            
            x_max_comun = max(x_sis.max(), x_bom.max())
            x_end_range = x_max_comun * 2.0
            
            def intersection_func_base(q):
                return np.polyval(coef_bom_calc, q) - np.polyval(coef_sis_calc, q)
            
            initial_guesses = np.linspace(0, x_max_comun, 20)
            for guess in initial_guesses:
                q_int, = fsolve(intersection_func_base, guess)
                h_int = np.polyval(coef_sis_calc, q_int)
                if 0 <= q_int <= x_end_range and h_int >= 0:
                    interseccion = (q_int, h_int)
                    st.session_state['interseccion'] = interseccion
                    break
        except Exception as e:
            pass
    
    # --- Sección 1: Gráficos a 100% RPM ---

    # Configuración de Zona de Eficiencia (movido fuera de las columnas para alineación)
    st.markdown("**Configuración de Zona de Eficiencia**")
    col_eff_min, col_eff_max, _ = st.columns(3)
    with col_eff_min:
        st.number_input(
            "Mínimo (% BEP):",
            min_value=50.0,
            max_value=80.0,
            value=st.session_state.get('zona_eff_min', 65.0),
            step=5.0,
            key="zona_eff_min",
            help="Porcentaje mínimo del BEP para la zona de eficiencia"
        )
    with col_eff_max:
        st.number_input(
            "Máximo (% BEP):",
            min_value=100.0,
            max_value=150.0,
            value=st.session_state.get('zona_eff_max', 115.0),
            step=5.0,
            key="zona_eff_max",
            help="Porcentaje máximo del BEP para la zona de eficiencia"
        )

    # Línea divisoria
    st.markdown("---")

    # CSS para hacer columnas independientes usando flexbox
    st.markdown("""
    <style>
    /* Hacer que el contenedor de columnas use display: flex con align-items: flex-start */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        align-items: flex-start !important;
        gap: 1rem;
    }
    /* Cada columna debe mantener su posición */
    div[data-testid="stHorizontalBlock"] > div {
        flex-shrink: 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- PRE-CÁLCULOS DE GRÁFICOS (100% RPM) ---
    # Calculamos todos los coeficientes y puntos críticos aquí para que estén disponibles en cualquier columna
    puntos_rend = curva_inputs.get('rendimiento', [])
    puntos_pot = curva_inputs.get('potencia', [])
    puntos_npsh = curva_inputs.get('npsh', [])
    
    coef_rend = None
    bep_q = 0
    bep_eta = 0
    zona_min = 0
    zona_max = 0
    
    if len(puntos_rend) >= 2:
        x_vals_r = np.array([pt[0] for pt in puntos_rend])
        y_vals_r = np.array([pt[1] for pt in puntos_rend])
        grado_rend = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
        coef_rend = np.polyfit(x_vals_r, y_vals_r, grado_rend)
        
        # Calcular BEP
        x_fit_r = np.linspace(x_vals_r.min(), max(x_vals_r.max(), (caudal_nominal or 0)*1.2), 500)
        y_fit_r = np.polyval(coef_rend, x_fit_r)
        idx_bep = np.argmax(y_fit_r)
        bep_q = x_fit_r[idx_bep]
        bep_eta = y_fit_r[idx_bep]
        
        # Calcular zonas de eficiencia
        z_eff_min = st.session_state.get('zona_eff_min', 65.0) / 100.0
        z_eff_max = st.session_state.get('zona_eff_max', 115.0) / 100.0
        zona_min = bep_q * z_eff_min
        zona_max = bep_q * z_eff_max

    # Coeficientes para Potencia y NPSH (si existen)
    coef_pot = None
    if len(puntos_pot) >= 2:
        x_p = np.array([pt[0] for pt in puntos_pot])
        y_p = np.array([pt[1] for pt in puntos_pot])
        grado_p = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
        coef_pot = np.polyfit(x_p, y_p, grado_p)

    coef_npsh = None
    if len(puntos_npsh) >= 2:
        x_n = np.array([pt[0] for pt in puntos_npsh])
        y_n = np.array([pt[1] for pt in puntos_npsh])
        grado_n = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
        coef_npsh = np.polyfit(x_n, y_n, grado_n)

    # Layout de 3 columnas para los gráficos y el resumen
    col1, col2, col3 = st.columns([0.35, 0.35, 0.30])

    # --- Columna 3: Resumen y Comentarios ---
    with col3:
        # --- Expander de Personalización de Gráficos ---
        # El expander de personalización manual ha sido eliminado en favor del autoajuste inteligente
        
        with st.expander("📊 Resumen y Comentarios Técnicos - 100% RPM", expanded=False):
            st.markdown("### 📈 **Resumen de Resultados**")
            
            if interseccion:
                q_op, h_op = interseccion
                
                puntos_rend = curva_inputs.get('rendimiento', [])
                eff_op = 0
                if len(puntos_rend) >= 2:
                    x_rend = np.array([pt[0] for pt in puntos_rend])
                    y_rend = np.array([pt[1] for pt in puntos_rend])
                    eff_op = np.interp(q_op, x_rend, y_rend)
                
                puntos_pot = curva_inputs.get('potencia', [])
                power_op = 0
                if len(puntos_pot) >= 2:
                    x_pot = np.array([pt[0] for pt in puntos_pot])
                    y_pot = np.array([pt[1] for pt in puntos_pot])
                    power_op = np.interp(q_op, x_pot, y_pot)
                
                puntos_npsh = curva_inputs.get('npsh', [])
                npsh_op = 0
                if len(puntos_npsh) >= 2:
                    x_npsh = np.array([pt[0] for pt in puntos_npsh])
                    y_npsh = np.array([pt[1] for pt in puntos_npsh])
                    npsh_op = np.interp(q_op, x_npsh, y_npsh)
                
                # Guardar los resultados del punto de operación en el estado de la sesión
                st.session_state['caudal_operacion'] = q_op
                st.session_state['altura_operacion'] = h_op
                st.session_state['eficiencia_operacion'] = eff_op
                st.session_state['potencia_operacion'] = power_op
                st.session_state['npsh_requerido'] = npsh_op
                
                # Calcular margen de NPSH
                npsh_disponible = st.session_state.get('npshd_mca', 0.0)
                if npsh_disponible > 0 and npsh_op > 0:
                    margen_npsh = npsh_disponible - npsh_op
                    st.session_state['npsh_margen'] = margen_npsh
                
                # Mostrar en unidades correctas
                unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                if unidad_caudal == 'm³/h':
                    caudal_display = q_op * 3.6
                    unidad_display = "m³/h"
                else:
                    caudal_display = q_op
                    unidad_display = "L/s"
                
                # Información de bombas en paralelo
                n_bombas = st.session_state.get('num_bombas', 1)
                if n_bombas > 1:
                    # q_op es el caudal de UNA bomba (según las curvas ingresadas)
                    # El caudal total del sistema es q_op × n_bombas
                    q_total_sistema = q_op * n_bombas
                    if unidad_caudal == 'm³/h':
                        q_total_display = q_total_sistema * 3.6
                    else:
                        q_total_display = q_total_sistema
                    power_total = power_op * n_bombas
                    
                    st.info(f"🔄 **Sistema con {n_bombas} bombas en paralelo**")
                    st.markdown(f"""
                    **Punto de Operación por Bomba Individual:**
                    - **Caudal por Bomba:** {caudal_display:.2f} {unidad_display}
                    - **Altura:** {h_op:.2f} m
                    - **Eficiencia:** {eff_op:.1f}%
                    - **Potencia por Bomba:** {power_op:.2f} HP
                    - **NPSH Requerido:** {npsh_op:.2f} m
                    
                    **Sistema Total ({n_bombas} bombas):**
                    - **Caudal Total del Sistema:** {q_total_display:.2f} {unidad_display}
                    - **Potencia Total del Sistema:** {power_total:.2f} HP
                    """)
                else:
                    st.markdown(f"""
                    **Punto de Operación:**
                    - **Caudal:** {caudal_display:.2f} {unidad_display}
                    - **Altura:** {h_op:.2f} m
                    - **Eficiencia:** {eff_op:.1f}%
                    - **Potencia:** {power_op:.2f} HP
                    - **NPSH Requerido:** {npsh_op:.2f} m
                    """)
                
                # Análisis de NPSH con criterio estándar de la industria
                npsh_disponible = st.session_state.get('npshd_mca', 0)
                if len(puntos_npsh) >= 2: # Mostrar análisis si hay datos para la curva NPSH
                    st.markdown("### 🔍 **Análisis de NPSH (100% RPM)**")
                    
                    # Criterio estándar de la industria (API, ASME)
                    margen_seguridad_industria = 1.2 * npsh_op
                    cumple_criterio_industria = npsh_disponible >= margen_seguridad_industria
                    condicion_basica = npsh_disponible > npsh_op
                    
                    st.markdown(f"""
                    **Criterio de Diseño Estándar de la Industria (API/ASME):**
                    
                    **1. Condición de Diseño (NPSH_A > NPSH_R):**
                    - **NPSH Disponible (NPSH_A):** {npsh_disponible:.2f} m.c.a.
                    - **NPSH Requerido (NPSH_R):** {npsh_op:.2f} m.c.a.
                    - **Diferencia:** {npsh_disponible - npsh_op:+.2f} m.c.a.
                    
                    **2. Margen de Seguridad (Regla del 1.2 · NPSH_R):**
                    - **Margen Mínimo Requerido:** {margen_seguridad_industria:.2f} m.c.a.
                    - **Margen Disponible:** {npsh_disponible - margen_seguridad_industria:+.2f} m.c.a.
                    """)
                    
                    # Evaluación según criterios
                    if condicion_basica:
                        if cumple_criterio_industria:
                            st.success("✅ **Diseño Robusto:** Cumple criterio estándar de la industria. NPSH_A ≥ 1.2×NPSH_R. Sin riesgo de cavitación.")
                            st.info("💡 **Recomendación:** Diseño apropiado para operación continua sin restricciones.")
                        else:
                            st.warning("⚠️ **Diseño Marginal:** NPSH_A > NPSH_R pero < 1.2×NPSH_R. Riesgo de cavitación intermitente.")
                            st.warning("⚠️ **Recomendación:** Monitorear condiciones de operación. Considerar aumentar NPSH_A o reducir NPSH_R.")
                    else:
                        st.error("❌ **Diseño Inseguro:** NPSH_A < NPSH_R. Alto riesgo de cavitación.")
                        st.error("❌ **Recomendación:** Rediseñar sistema para aumentar NPSH_A o cambiar bomba con menor NPSH_R.")
                    
                    # Análisis adicional
                    porcentaje_margen = ((npsh_disponible - npsh_op) / npsh_op) * 100
                    st.markdown(f"""
                    **Análisis Adicional:**
                    - **Margen de Seguridad:** {porcentaje_margen:.1f}% sobre NPSH_R
                    - **Factor de Seguridad:** {npsh_disponible/npsh_op:.2f}
                    """)
                    
                    # Recomendaciones específicas
                    if cumple_criterio_industria:
                        st.markdown("""
                        **✅ Condiciones de Operación Aceptables:**
                        - Variaciones de temperatura: ✅ Aceptable
                        - Variaciones de altitud: ✅ Aceptable  
                        - Variaciones de flujo: ✅ Aceptable
                        - Operación continua: ✅ Recomendada
                        """)
                    elif condicion_basica:
                        st.markdown("""
                        **⚠️ Condiciones de Operación Limitadas:**
                        - Variaciones de temperatura: ⚠️ Monitorear
                        - Variaciones de altitud: ⚠️ Monitorear
                        - Variaciones de flujo: ⚠️ Monitorear
                        - Operación continua: ⚠️ Con precaución
                        """)
                    else:
                        st.markdown("""
                        **❌ Condiciones de Operación No Recomendadas:**
                        - Variaciones de temperatura: ❌ No recomendado
                        - Variaciones de altitud: ❌ No recomendado
                        - Variaciones de flujo: ❌ No recomendado
                        - Operación continua: ❌ No recomendado
                        """)
                
                st.markdown("### 🔧 **Comentarios Técnicos**")
                if eff_op >= 80:
                    st.success("✅ **Eficiencia Excelente:** La bomba opera en zona de alta eficiencia (>80%)")
                elif eff_op >= 70:
                    st.info("ℹ️ **Eficiencia Buena:** La bomba opera en zona de eficiencia aceptable (70-80%)")
                else:
                    st.warning("⚠️ **Eficiencia Baja:** La bomba opera en zona de baja eficiencia (<70%)")
                
                npsh_disponible = st.session_state.get('npshd_mca', 0)
                if npsh_disponible > 0:
                    margen_npsh = npsh_disponible - npsh_op
                    if margen_npsh >= 1.0:
                        st.success(f"✅ **NPSH Adecuado:** Margen de seguridad de {margen_npsh:.2f} m")
                    elif margen_npsh >= 0.5:
                        st.info(f"ℹ️ **NPSH Aceptable:** Margen de seguridad de {margen_npsh:.2f} m")
                    else:
                        st.error(f"❌ **NPSH Insuficiente:** Margen de seguridad de {margen_npsh:.2f} m")
                
                if power_op > 0:
                    st.info(f"ℹ️ **Potencia Requerida:** {power_op:.2f} HP en el punto de operación")
                
                if len(puntos_rend) >= 2:
                    x_rend = np.array([pt[0] for pt in puntos_rend])
                    y_rend = np.array([pt[1] for pt in puntos_rend])
                    grado_rend = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
                    coef_rend = np.polyfit(x_rend, y_rend, grado_rend)
                    x_fit = np.linspace(x_rend.min(), x_rend.max(), 100)
                    y_fit = np.polyval(coef_rend, x_fit)
                    idx_bep = np.argmax(y_fit)
                    bep_q = x_fit[idx_bep]
                    bep_eta = y_fit[idx_bep]
                    
                    # Calcular H en el BEP (interpolar desde curva H-Q)
                    if len(puntos_bomba) >= 2:
                        x_bom_bep = np.array([pt[0] for pt in puntos_bomba])
                        y_bom_bep = np.array([pt[1] for pt in puntos_bomba])
                        grado_bom = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
                        coef_bom_bep = np.polyfit(x_bom_bep, y_bom_bep, grado_bom)
                        bep_h = np.polyval(coef_bom_bep, bep_q)
                    else:
                        bep_h = 0
                    
                    # GUARDAR BEP EN SESSION_STATE para usar en expander de Allievi
                    st.session_state['bep_q_100'] = float(bep_q)
                    st.session_state['bep_h_100'] = float(bep_h)
                    st.session_state['bep_eta_100'] = float(bep_eta)
                    
                    st.markdown("### 🎯 **Análisis de BEP (Best Efficiency Point)**")
                    # Mostrar en unidades correctas
                    unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                    if unidad_caudal == 'm³/h':
                        bep_q_display = bep_q * 3.6
                        bep_q_min = bep_q * 0.65 * 3.6
                        bep_q_max = bep_q * 1.15 * 3.6
                        unidad_display = "m³/h"
                    else:
                        bep_q_display = bep_q
                        bep_q_min = bep_q * 0.65
                        bep_q_max = bep_q * 1.15
                        unidad_display = "L/s"
                    
                    st.markdown(f"""
                    - **BEP Caudal:** {bep_q_display:.2f} {unidad_display}
                    - **BEP Eficiencia:** {bep_eta:.1f}%
                    - **Zona de Eficiencia:** {st.session_state.get('zona_eff_min', 65.0):.0f}-{st.session_state.get('zona_eff_max', 115.0):.0f}% del BEP ({bep_q_min:.1f} - {bep_q_max:.1f} {unidad_display})
                    """)
                    zona_eff_min = st.session_state.get('zona_eff_min', 65.0) / 100.0
                    zona_eff_max = st.session_state.get('zona_eff_max', 115.0) / 100.0
                    if q_op >= bep_q * zona_eff_min and q_op <= bep_q * zona_eff_max:
                        st.success(f"✅ **Operación en Zona Eficiente:** El punto de operación está dentro de la zona de eficiencia ({st.session_state.get('zona_eff_min', 65.0):.0f}-{st.session_state.get('zona_eff_max', 115.0):.0f}% del BEP)")
                    else:
                        st.warning("⚠️ **Operación fuera de Zona Eficiente:** El punto de operación está fuera de la zona de eficiencia recomendada")
                
                st.markdown("### 💡 **Recomendaciones**")
                st.markdown("""
                - Verificar que la bomba seleccionada cubra el rango de operación requerido
                - Considerar el factor de seguridad en el diseño
                - Evaluar la posibilidad de operación en paralelo si se requiere mayor caudal
                - Monitorear la eficiencia durante la operación
                - Operar preferiblemente dentro de la zona de eficiencia (65-115% del BEP)
                """)
            else:
                st.warning("⚠️ No se pudo determinar el punto de operación")

    # --- COLUMNA 1: H-Q y Potencia ---
    with col1:
        # 1. Curva H-Q
        st.markdown("**Curva del Sistema y Curva de la Bomba (H-Q)**")
        fig_hq = go.Figure()
        
        # Obtener datos de la bomba
        puntos_bomba = curva_inputs.get('bomba', [])
        if len(puntos_sistema) >= 2 and len(puntos_bomba) >= 2:
            x_max_bom = np.array([pt[0] for pt in puntos_bomba]).max()
            x_end_range = max(x_max_bom, interseccion[0] * 1.25) if interseccion else x_max_bom * 1.2
            x_ext = np.linspace(0, x_end_range, 500)
            
            # Recalcular coef_bom localmente para evitar problemas de visibilidad
            grado = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
            coef_bom = np.polyfit(np.array([pt[0] for pt in puntos_bomba]), np.array([pt[1] for pt in puntos_bomba]), grado)
            coef_sis = np.polyfit(np.array([pt[0] for pt in puntos_sistema]), np.array([pt[1] for pt in puntos_sistema]), grado)
            
            y_sis_fit = np.polyval(coef_sis, x_ext)
            y_bom_fit = np.polyval(coef_bom, x_ext)
            
            unidad_caudal = st.session_state.get('flow_unit', 'L/s')
            x_ext_disp = x_ext * 3.6 if unidad_caudal == 'm³/h' else x_ext
            
            # Zona de eficiencia en H-Q
            if coef_rend is not None:
                x_zona = np.linspace(zona_min, zona_max, 50)
                y_zona = np.polyval(coef_bom, x_zona)
                x_zona_disp = x_zona * 3.6 if unidad_caudal == 'm³/h' else x_zona
                fig_hq.add_trace(go.Scatter(
                    x=np.concatenate([x_zona_disp, x_zona_disp[::-1]]),
                    y=np.concatenate([y_zona, np.zeros_like(y_zona)]),
                    fill='toself', fillcolor='rgba(0, 255, 0, 0.2)', line=dict(color='rgba(0, 255, 0, 0.8)', width=2),
                    name="Zona de Eficiencia", showlegend=True
                ))

            fig_hq.add_trace(go.Scatter(x=x_ext_disp, y=y_sis_fit, mode='lines', name='Curva del Sistema', line=dict(color='red')))
            fig_hq.add_trace(go.Scatter(x=x_ext_disp, y=y_bom_fit, mode='lines', name='Curva de la Bomba', line=dict(color='blue')))
            
            if interseccion:
                q_disp = interseccion[0] * 3.6 if unidad_caudal == 'm³/h' else interseccion[0]
                fig_hq.add_trace(go.Scatter(x=[q_disp], y=[interseccion[1]], mode='markers+text', name='Punto de Operación', marker=dict(color='orange', size=10, symbol='star'), text=["Punto de Operación"], textposition="top right"))
            
            if coef_rend is not None:
                bep_q_disp = bep_q * 3.6 if unidad_caudal == 'm³/h' else bep_q
                bep_h = np.polyval(coef_bom, bep_q)
                fig_hq.add_trace(go.Scatter(x=[bep_q_disp], y=[bep_h], mode='markers+text', name='BEP', marker=dict(color='darkgreen', size=8, symbol='diamond'), text=[f"BEP: {bep_q_disp:.1f}"], textposition="top right"))

            # Calcular rangos inteligentes (Escalado Automático)
            q_op_val = interseccion[0] if interseccion else (puntos_bomba[0][0] if puntos_bomba else 0)
            h_op_val = interseccion[1] if interseccion else (puntos_bomba[0][1] if puntos_bomba else 0)
            h_static = st.session_state.get('altura_estatica_total', 0)
            
            # Obtener rangos base del motor de escalado
            smart_x, smart_y = calculate_smart_axes(
                q_op_val, h_op_val, h_static, x_max_bom, 
                tipo_grafico="hq",
                q_max_curve=x_max_bom,
                val_max_curve=np.array([pt[1] for pt in puntos_bomba]).max()
            )
            
            # Ajustar eje X a la unidad de visualización
            if unidad_caudal == 'm³/h':
                smart_x = [v * 3.6 for v in smart_x]

            x_range_hq = smart_x
            y_range_hq = smart_y
            
            fig_hq.update_layout(
                xaxis_title=f"Caudal (Q) [{get_display_unit_label(unidad_caudal)}]",
                yaxis_title="Altura (H) [m]",
                xaxis=dict(range=x_range_hq, showgrid=True) if x_range_hq else dict(showgrid=True),
                yaxis=dict(range=y_range_hq, showgrid=True) if y_range_hq else dict(showgrid=True),
                legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=40, b=80),
                hovermode='x unified'
            )
            st.plotly_chart(fig_hq, use_container_width=True, key="hq_100_chart_v2")
            
            # Capturar gráfico para reportes
            try:
                from ui.reports import capturar_grafico_plotly
                if capturar_grafico_plotly(fig_hq, 'grupo_100', 'hq_100'):
                    st.session_state['hq_100_capturado'] = True
            except Exception as e:
                pass

            if interseccion:
                caudal_val = interseccion[0] * 3.6 if unidad_caudal == 'm³/h' else interseccion[0]
                u_disp = "m³/h" if unidad_caudal == 'm³/h' else "L/s"
                st.markdown(f"""<div style="background-color: #e6f3ff; padding: 10px; border-radius: 5px; border-left: 4px solid #0066cc;"><strong>Punto de Operación:</strong><br><strong>Caudal (Q):</strong> {caudal_val:.2f} {u_disp}<br><strong>Altura (H):</strong> {interseccion[1]:.2f} m</div>""", unsafe_allow_html=True)

        # 2. Curva de Potencia
        st.markdown("---")
        st.markdown("**Curva de Potencia (PBHP-Q)**")
        fig_pot = go.Figure()
        if coef_pot is not None:
            x_max_p = np.array([pt[0] for pt in puntos_pot]).max()
            x_end_p = max(x_max_p, interseccion[0] * 1.25) if interseccion else x_max_p * 1.2
            x_ext_p = np.linspace(0, x_end_p, 500)
            y_fit_p = np.polyval(coef_pot, x_ext_p)
            
            unidad_caudal = st.session_state.get('flow_unit', 'L/s')
            x_ext_p_disp = x_ext_p * 3.6 if unidad_caudal == 'm³/h' else x_ext_p
            
            # Zona de eficiencia en Potencia
            if coef_rend is not None:
                x_zona_p = np.linspace(zona_min, zona_max, 50)
                y_zona_p = np.polyval(coef_pot, x_zona_p)
                x_zona_p_disp = x_zona_p * 3.6 if unidad_caudal == 'm³/h' else x_zona_p
                fig_pot.add_trace(go.Scatter(
                    x=np.concatenate([x_zona_p_disp, x_zona_p_disp[::-1]]),
                    y=np.concatenate([y_zona_p, np.zeros_like(y_zona_p)]),
                    fill='toself', fillcolor='rgba(0, 255, 0, 0.2)', line=dict(color='rgba(0, 255, 0, 0.8)', width=2),
                    name="Zona de Eficiencia", showlegend=True
                ))

            fig_pot.add_trace(go.Scatter(x=x_ext_p_disp, y=y_fit_p, mode='lines', name='Potencia (ajustada)', line=dict(color='orange')))
            
            if interseccion:
                op_pot = np.polyval(coef_pot, interseccion[0])
                q_disp = interseccion[0] * 3.6 if unidad_caudal == 'm³/h' else interseccion[0]
                fig_pot.add_trace(go.Scatter(x=[q_disp], y=[op_pot], mode='markers+text', name='Potencia Op.', marker=dict(color='orange', size=8, symbol='star'), text=[f"{op_pot:.1f} HP"], textposition="top right"))

            # Calcular rangos inteligentes
            q_op_val = interseccion[0] if interseccion else 0
            pot_op_val = np.polyval(coef_pot, q_op_val) if q_op_val > 0 else 0
            smart_x_pot, smart_y_pot = calculate_smart_axes(
                q_op_val, pot_op_val, 0, x_max_p, 
                tipo_grafico="potencia",
                q_max_curve=x_max_p,
                val_max_curve=np.array([pt[1] for pt in puntos_pot]).max()
            )
            
            if unidad_caudal == 'm³/h':
                smart_x_pot = [v * 3.6 for v in smart_x_pot]

            x_range_pot = smart_x_pot
            y_range_pot = smart_y_pot
            
            fig_pot.update_layout(
                xaxis_title=f"Caudal (Q) [{get_display_unit_label(unidad_caudal)}]",
                yaxis_title="Potencia [HP]",
                xaxis=dict(range=x_range_pot, showgrid=True) if x_range_pot else dict(showgrid=True),
                yaxis=dict(showgrid=True),
                legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=40, b=80)
            )
            st.plotly_chart(fig_pot, use_container_width=True, key="pot_100_chart_v2")
            
            # Capturar gráfico para reportes
            try:
                from ui.reports import capturar_grafico_plotly
                if capturar_grafico_plotly(fig_pot, 'grupo_100', 'potencia_100'):
                    st.session_state['pot_100_capturado'] = True
            except Exception as e:
                pass
            
            # Caja de información del punto de operación
            if interseccion:
                op_pot_val = np.polyval(coef_pot, interseccion[0])
                caudal_val = interseccion[0] * 3.6 if unidad_caudal == 'm³/h' else interseccion[0]
                u_disp = "m³/h" if unidad_caudal == 'm³/h' else "L/s"
                st.markdown(f"""<div style="background-color: #e6f3ff; padding: 10px; border-radius: 5px; border-left: 4px solid #0066cc;"><strong>Punto de Operación:</strong><br><strong>Caudal (Q):</strong> {caudal_val:.2f} {u_disp}<br><strong>Potencia:</strong> {op_pot_val:.2f} HP</div>""", unsafe_allow_html=True)

    # --- COLUMNA 2: Rendimiento y NPSH ---
    with col2:
        # 1. Curva de Rendimiento
        st.markdown("**Curva de Rendimiento (η-Q)**")
        fig_rend = go.Figure()
        if coef_rend is not None:
            x_max_r = np.array([pt[0] for pt in puntos_rend]).max()
            x_end_r = max(x_max_r, interseccion[0] * 1.25) if interseccion else x_max_r * 1.2
            x_ext_r = np.linspace(0, x_end_r, 500)
            y_fit_r = np.polyval(coef_rend, x_ext_r)
            
            unidad_caudal = st.session_state.get('flow_unit', 'L/s')
            x_ext_r_disp = x_ext_r * 3.6 if unidad_caudal == 'm³/h' else x_ext_r
            
            # Zona de eficiencia
            x_zona_r = np.linspace(zona_min, zona_max, 50)
            y_zona_r = np.polyval(coef_rend, x_zona_r)
            x_zona_r_disp = x_zona_r * 3.6 if unidad_caudal == 'm³/h' else x_zona_r
            fig_rend.add_trace(go.Scatter(
                x=np.concatenate([x_zona_r_disp, x_zona_r_disp[::-1]]),
                y=np.concatenate([y_zona_r, np.zeros_like(y_zona_r)]),
                fill='toself', fillcolor='rgba(0, 255, 0, 0.2)', line=dict(color='rgba(0, 255, 0, 0.8)', width=2),
                name="Zona de Eficiencia", showlegend=True
            ))

            fig_rend.add_trace(go.Scatter(x=x_ext_r_disp, y=y_fit_r, mode='lines', name='Rendimiento', line=dict(color='green')))
            
            bep_q_disp = bep_q * 3.6 if unidad_caudal == 'm³/h' else bep_q
            fig_rend.add_trace(go.Scatter(x=[bep_q_disp], y=[bep_eta], mode='markers+text', name='BEP', marker=dict(color='darkgreen', size=8, symbol='diamond'), text=[f"BEP: {bep_eta:.1f}%"], textposition="top right"))

            if interseccion:
                op_rend = np.polyval(coef_rend, interseccion[0])
                q_disp = interseccion[0] * 3.6 if unidad_caudal == 'm³/h' else interseccion[0]
                fig_rend.add_trace(go.Scatter(x=[q_disp], y=[op_rend], mode='markers+text', name='Rendimiento Op.', marker=dict(color='orange', size=8, symbol='star'), text=[f"{op_rend:.1f}%"], textposition="top right"))

            # Calcular rangos inteligentes
            q_op_val = interseccion[0] if interseccion else bep_q
            rend_op_val = np.polyval(coef_rend, q_op_val) if q_op_val > 0 else bep_eta
            smart_x_rend, smart_y_rend = calculate_smart_axes(
                q_op_val, rend_op_val, 0, x_max_r, 
                tipo_grafico="rendimiento",
                q_max_curve=x_max_r,
                val_max_curve=np.array([pt[1] for pt in puntos_rend]).max()
            )
            
            if unidad_caudal == 'm³/h':
                smart_x_rend = [v * 3.6 for v in smart_x_rend]

            x_range_rend = smart_x_rend
            y_range_rend = smart_y_rend
            
            fig_rend.update_layout(
                xaxis_title=f"Caudal (Q) [{get_display_unit_label(unidad_caudal)}]",
                yaxis_title="Rendimiento [%]",
                xaxis=dict(range=x_range_rend, showgrid=True) if x_range_rend else dict(showgrid=True),
                yaxis=dict(showgrid=True),
                legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=40, b=80)
            )
            st.plotly_chart(fig_rend, use_container_width=True, key="rend_100_chart_v2")
            
            # Capturar gráfico para reportes
            try:
                from ui.reports import capturar_grafico_plotly
                if capturar_grafico_plotly(fig_rend, 'grupo_100', 'rendimiento_100'):
                    st.session_state['rend_100_capturado'] = True
            except Exception as e:
                pass
            
            # Caja de información del punto de operación
            if interseccion:
                op_rend_val = np.polyval(coef_rend, interseccion[0])
                caudal_val = interseccion[0] * 3.6 if unidad_caudal == 'm³/h' else interseccion[0]
                u_disp = "m³/h" if unidad_caudal == 'm³/h' else "L/s"
                st.markdown(f"""<div style="background-color: #e6f3ff; padding: 10px; border-radius: 5px; border-left: 4px solid #0066cc;"><strong>Punto de Operación:</strong><br><strong>Caudal (Q):</strong> {caudal_val:.2f} {u_disp}<br><strong>Rendimiento:</strong> {op_rend_val:.1f}%</div>""", unsafe_allow_html=True)

        # 2. Curva de NPSH
        st.markdown("---")
        st.markdown("**Curva de NPSH Requerido (NPSHR-Q)**")
        fig_npsh = go.Figure()
        if coef_npsh is not None:
            x_max_n = np.array([pt[0] for pt in puntos_npsh]).max()
            x_end_n = max(x_max_n, interseccion[0] * 1.25) if interseccion else x_max_n * 1.2
            x_ext_n = np.linspace(0, x_end_n, 500)
            y_fit_n = np.polyval(coef_npsh, x_ext_n)
            
            unidad_caudal = st.session_state.get('flow_unit', 'L/s')
            x_ext_n_disp = x_ext_n * 3.6 if unidad_caudal == 'm³/h' else x_ext_n
            
            # Zona de eficiencia en NPSH
            if coef_rend is not None:
                x_zona_n = np.linspace(zona_min, zona_max, 50)
                y_zona_n = np.polyval(coef_npsh, x_zona_n)
                x_zona_n_disp = x_zona_n * 3.6 if unidad_caudal == 'm³/h' else x_zona_n
                fig_npsh.add_trace(go.Scatter(
                    x=np.concatenate([x_zona_n_disp, x_zona_n_disp[::-1]]),
                    y=np.concatenate([y_zona_n, np.zeros_like(y_zona_n)]),
                    fill='toself', fillcolor='rgba(0, 255, 0, 0.2)', line=dict(color='rgba(0, 255, 0, 0.8)', width=2),
                    name="Zona de Eficiencia", showlegend=True
                ))

            fig_npsh.add_trace(go.Scatter(x=x_ext_n_disp, y=y_fit_n, mode='lines', name='NPSH (ajustada)', line=dict(color='purple')))
            
            if interseccion:
                op_npsh = np.polyval(coef_npsh, interseccion[0])
                q_disp = interseccion[0] * 3.6 if unidad_caudal == 'm³/h' else interseccion[0]
                fig_npsh.add_trace(go.Scatter(x=[q_disp], y=[op_npsh], mode='markers+text', name='NPSH Op.', marker=dict(color='orange', size=8, symbol='star'), text=[f"{op_npsh:.1f} m"], textposition="top right"))

            # Calcular rangos inteligentes
            q_op_val = interseccion[0] if interseccion else 0
            npsh_op_val = np.polyval(coef_npsh, q_op_val) if q_op_val > 0 else 0
            smart_x_npsh, smart_y_npsh = calculate_smart_axes(
                q_op_val, npsh_op_val, 0, x_max_n, 
                tipo_grafico="npsh",
                q_max_curve=x_max_n,
                val_max_curve=np.array([pt[1] for pt in puntos_npsh]).max()
            )
            
            if unidad_caudal == 'm³/h':
                smart_x_npsh = [v * 3.6 for v in smart_x_npsh]

            x_range_npsh = smart_x_npsh
            y_range_npsh = smart_y_npsh
            
            fig_npsh.update_layout(
                xaxis_title=f"Caudal (Q) [{get_display_unit_label(unidad_caudal)}]",
                yaxis_title="NPSH [m]",
                xaxis=dict(range=x_range_npsh, showgrid=True) if x_range_npsh else dict(showgrid=True),
                yaxis=dict(showgrid=True),
                legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=40, b=80)
            )
            st.plotly_chart(fig_npsh, use_container_width=True, key="npsh_100_chart_v2")
            
            # Capturar gráfico para reportes
            try:
                from ui.reports import capturar_grafico_plotly
                if capturar_grafico_plotly(fig_npsh, 'grupo_100', 'npsh_100'):
                    st.session_state['npsh_100_capturado'] = True
            except Exception as e:
                pass
            
            # Caja de información del punto de operación
            if interseccion:
                op_npsh_val = np.polyval(coef_npsh, interseccion[0])
                caudal_val = interseccion[0] * 3.6 if unidad_caudal == 'm³/h' else interseccion[0]
                u_disp = "m³/h" if unidad_caudal == 'm³/h' else "L/s"
                st.markdown(f"""<div style="background-color: #e6f3ff; padding: 10px; border-radius: 5px; border-left: 4px solid #0066cc;"><strong>Punto de Operación:</strong><br><strong>Caudal (Q):</strong> {caudal_val:.2f} {u_disp}<br><strong>NPSH:</strong> {op_npsh_val:.2f} m</div>""", unsafe_allow_html=True)
    
    # --- SECCIÓN VFD ---
    if caudal_nominal > 0 and len(puntos_rend) >= 2:
        st.markdown("---")
        st.markdown("#### ⚙️ Análisis de Variador (VFD)")
        
        # Inicializar rpm_percentage si no existe
        if 'rpm_percentage' not in st.session_state:
            st.session_state['rpm_percentage'] = 75.0
        
        # Funciones de sincronización
        def sync_from_slider():
            st.session_state['rpm_percentage'] = st.session_state['rpm_slider_analysis']
        
        def sync_from_number():
            st.session_state['rpm_percentage'] = st.session_state['rpm_number_analysis']

        # Función para iterar RPM hasta alcanzar el caudal nominal
        def auto_iterate_rpm():
            # Usar caudal nominal por bomba (ya calculado al inicio)
            target_q = caudal_nominal
            if target_q <= 0:
                st.error("❌ Caudal nominal inválido. Verifica que hayas definido un caudal de diseño.")
                return
            
            # Obtener datos base
            curva_inputs = st.session_state.get('curva_inputs', {})
            puntos_bomba = curva_inputs.get('bomba', [])
            
            if len(puntos_bomba) < 2:
                st.error("❌ Se requiere la curva de la bomba (mínimo 2 puntos)")
                return
            
            # Obtener puntos del sistema - Intentar desde múltiples fuentes
            puntos_sistema_raw = []
            
            # Método 1: Desde textarea_sistema
            if 'textarea_sistema' in st.session_state and st.session_state['textarea_sistema']:
                try:
                    texto_curva = st.session_state['textarea_sistema']
                    lines = [line.strip() for line in texto_curva.splitlines() if line.strip()]
                    unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                    
                    for line in lines:
                        vals = [v for v in line.replace(';', ' ').replace('\t', ' ').split() if v]
                        if len(vals) == 2:
                            try:
                                x = float(vals[0])
                                y = float(vals[1])
                                # Convertir a L/s si es necesario
                                if unidad_caudal == 'm³/h':
                                    x = x / 3.6
                                puntos_sistema_raw.append((x, y))
                            except:
                                pass
                except:
                    pass
            
            # Método 2: Desde curva_inputs
            if not puntos_sistema_raw and 'sistema' in curva_inputs:
                puntos_sistema_raw = curva_inputs.get('sistema', [])
            
            # Método 3: Calcular desde parámetros del sistema
            if not puntos_sistema_raw:
                try:
                    from core.system_head import calculate_adt_for_multiple_flows
                    flows = np.linspace(0, target_q * 2, 20).tolist()
                    flow_unit = st.session_state.get('flow_unit', 'L/s')
                    
                    system_params = {
                        'h_estatica': st.session_state.get('h_estatica', 50.0),
                        'long_succion': st.session_state.get('long_succion', 10.0),
                        'diam_succion_m': st.session_state.get('diam_succion', 200.0) / 1000.0,
                        'C_succion': st.session_state.get('C_succion', 150),
                        'accesorios_succion': st.session_state.get('accesorios_succion', []),
                        'otras_perdidas_succion': 0.0,
                        'long_impulsion': st.session_state.get('long_impulsion', 100.0),
                        'diam_impulsion_m': st.session_state.get('diam_impulsion', 150.0) / 1000.0,
                        'C_impulsion': st.session_state.get('C_impulsion', 150),
                        'accesorios_impulsion': st.session_state.get('accesorios_impulsion', []),
                        'otras_perdidas_impulsion': 0.0
                    }
                    
                    adt_values = calculate_adt_for_multiple_flows(flows, flow_unit, system_params)
                    if adt_values:
                        puntos_sistema_raw = [(flows[i], adt_values[i]) for i in range(len(flows)) if adt_values[i] is not None]
                except Exception as e:
                    st.error(f"❌ Error calculando curva del sistema: {str(e)}")
                    return
            
            if len(puntos_sistema_raw) < 2:
                st.error("❌ Se requiere la curva del sistema (mínimo 2 puntos). Define la curva del sistema o los parámetros hidráulicos.")
                return
            
            # Calcular coeficientes del sistema
            x_s = np.array([pt[0] for pt in puntos_sistema_raw])
            y_s = np.array([pt[1] for pt in puntos_sistema_raw])
            grado = 1 if st.session_state.get('ajuste_tipo', 'Lineal') == "Lineal" else 2
            coef_sis_local = np.polyfit(x_s, y_s, grado)
            
            # Calcular coeficientes bomba base (100% RPM)
            x_b = np.array([pt[0] for pt in puntos_bomba])
            y_b = np.array([pt[1] for pt in puntos_bomba])
            coef_bom_base = np.polyfit(x_b, y_b, grado)
            
            # Búsqueda binaria
            low = 50.0
            high = 100.0
            best_rpm = 100.0
            tolerance = 0.1  # Tolerancia de 0.1 L/s
            
            with st.spinner(f'🔄 Calculando RPM óptimo para Q = {target_q:.2f} L/s...'):
                for iteration in range(25):  # Aumentar iteraciones
                    mid = (low + high) / 2
                    ratio = mid / 100.0
                    
                    # Coeficientes bomba escalados (Leyes de afinidad)
                    if grado == 2:
                        a, b, c = coef_bom_base
                        coef_mid = [a, b * ratio, c * (ratio**2)]
                    else:
                        a, b = coef_bom_base
                        coef_mid = [a, b * ratio]
                    
                    # Intersección
                    def f_int(q): return np.polyval(coef_mid, q) - np.polyval(coef_sis_local, q)
                    try:
                        q_int, = fsolve(f_int, target_q)
                        
                        # Verificar si alcanzamos el objetivo
                        if abs(q_int - target_q) < tolerance:
                            best_rpm = mid
                            break
                        
                        if q_int < target_q:
                            low = mid
                        else:
                            high = mid
                        best_rpm = mid
                    except:
                        low = mid
            
            # Actualizar solo rpm_percentage - los widgets se sincronizarán en el rerun
            st.session_state['rpm_percentage'] = round(best_rpm, 2)
            
            # Mostrar mensaje de éxito
            st.success(f"✅ RPM calculado: {best_rpm:.2f}% para alcanzar Q = {target_q:.2f} L/s por bomba")

        col_v1, col_v2, col_v3 = st.columns([0.65, 0.15, 0.20])
        with col_v1:
            st.slider(
                "Porcentaje de RPM (%)",
                min_value=50.0,
                max_value=100.0,
                value=float(st.session_state['rpm_percentage']),
                step=0.1,
                help="Ajusta la velocidad de la bomba para ver el desplazamiento de la curva.",
                key="rpm_slider_analysis",
                on_change=sync_from_slider
            )
        
        with col_v2:
            st.number_input(
                "Ajuste",
                min_value=50.0,
                max_value=100.0,
                value=float(st.session_state['rpm_percentage']),
                step=0.01,
                format="%.2f",
                key="rpm_number_analysis",
                on_change=sync_from_number
            )
        
        with col_v3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🎯 Calc. RPM Objetivo", help="Busca automáticamente el % de RPM para alcanzar el caudal nominal", use_container_width=True):
                auto_iterate_rpm()
                st.rerun()
        
        # El valor final a usar en los cálculos
        rpm_percentage = st.session_state['rpm_percentage']
    if caudal_nominal > 0:
        # 1. Derivar coeficientes VFD analíticamente
        # η = RPM% / 100
        eta = rpm_percentage / 100.0
        
        coef_bom_vfd = None
        # Recalcular coeficientes de la bomba base usando ajuste_tipo actual
        # Esto asegura que las curvas VFD se regeneren correctamente al cambiar el tipo de ajuste
        curva_inputs = st.session_state.get('curva_inputs', {})
        puntos_bomba = curva_inputs.get('bomba', [])
        
        if len(puntos_bomba) >= 2:
            try:
                x_bom = np.array([pt[0] for pt in puntos_bomba])
                y_bom = np.array([pt[1] for pt in puntos_bomba])
                grado = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
                coef_bom_base = np.polyfit(x_bom, y_bom, grado)
                
                # Aplicar leyes de afinidad según el grado del polinomio
                if len(coef_bom_base) == 4:  # Cúbico (3er grado)
                    a, b, c, d = coef_bom_base
                    coef_bom_vfd = np.array([a, b * eta, c * (eta**2), d * (eta**3)])
                elif len(coef_bom_base) == 3:  # Cuadrático (2do grado)
                    a, b, c = coef_bom_base
                    coef_bom_vfd = np.array([a, b * eta, c * (eta**2)])
                elif len(coef_bom_base) == 2:  # Lineal
                    a, b = coef_bom_base
                    coef_bom_vfd = np.array([a, b * eta])
            except Exception as e:
                # Si hay error, continuar sin VFD
                pass

        coef_rend_vfd = None
        if coef_rend is not None:
            if len(coef_rend) == 4:  # Cúbico (3er grado)
                a, b, c, d = coef_rend
                coef_rend_vfd = np.array([a / (eta**3), b / (eta**2), c / eta, d])
            elif len(coef_rend) == 3:  # Cuadrático (2do grado)
                a, b, c = coef_rend
                coef_rend_vfd = np.array([a / (eta**2), b / eta, c])
            elif len(coef_rend) == 2:  # Lineal
                a, b = coef_rend
                coef_rend_vfd = np.array([a / eta, b])

        coef_pot_vfd = None
        if coef_pot is not None:
            if len(coef_pot) == 4:  # Cúbico (3er grado)
                a, b, c, d = coef_pot
                coef_pot_vfd = np.array([a * eta, b * (eta**2), c * (eta**3), d * (eta**4)])
            elif len(coef_pot) == 3:  # Cuadrático (2do grado)
                a, b, c = coef_pot
                coef_pot_vfd = np.array([a * eta, b * (eta**2), c * (eta**3)])
            elif len(coef_pot) == 2:  # Lineal
                a, b = coef_pot
                coef_pot_vfd = np.array([a * (eta**2), b * (eta**3)])

        coef_npsh_vfd = None
        if coef_npsh is not None:
            if len(coef_npsh) == 4:  # Cúbico (3er grado)
                a, b, c, d = coef_npsh
                coef_npsh_vfd = np.array([a, b * eta, c * (eta**2), d * (eta**3)])
            elif len(coef_npsh) == 3:  # Cuadrático (2do grado)
                a, b, c = coef_npsh
                coef_npsh_vfd = np.array([a, b * eta, c * (eta**2)])
            elif len(coef_npsh) == 2:  # Lineal
                a, b = coef_npsh
                coef_npsh_vfd = np.array([a, b * eta])

        # 2. Punto de Intersección VFD
        interseccion_vfd = None
        if coef_bom_vfd is not None and coef_sis is not None:
            def f_vfd(q): return np.polyval(coef_bom_vfd, q) - np.polyval(coef_sis, q)
            try:
                q_start = interseccion[0] * eta if interseccion else caudal_nominal * 0.8
                q_int, = fsolve(f_vfd, q_start)
                h_int = np.polyval(coef_bom_vfd, q_int)
                if q_int > 0:
                    interseccion_vfd = (q_int, h_int)
            except:
                interseccion_vfd = None

        # 3. BEP y Zona de Eficiencia VFD
        bep_q_vfd = 0
        bep_eta_vfd = 0
        zona_min_v = 0
        zona_max_v = 0
        if coef_rend_vfd is not None:
            curva_inputs = st.session_state.get('curva_inputs', {})
            puntos_bomba = curva_inputs.get('bomba', [[0,0], [10,0]])
            x_max_bom_base = np.array([pt[0] for pt in puntos_bomba]).max()
            x_pts_scan = np.linspace(0, x_max_bom_base * 1.5, 1000)
            y_rend_scan = np.polyval(coef_rend_vfd, x_pts_scan)
            idx_bep_v = np.argmax(y_rend_scan)
            bep_q_vfd = x_pts_scan[idx_bep_v]
            bep_eta_vfd = y_rend_scan[idx_bep_v]
            
            # Calcular H en el BEP de VFD usando curva base escalada
            # Usar leyes de afinidad: Q ∝ N, H ∝ N²
            factor_rpm_vfd = rpm_percentage / 100.0
            x_bom_base = np.array([pt[0] for pt in puntos_bomba])
            y_bom_base = np.array([pt[1] for pt in puntos_bomba])
            grado_bom_base = 1 if st.session_state.get('ajuste_tipo', 'Cuadrática') == "Lineal" else 2
            coef_bom_base = np.polyfit(x_bom_base, y_bom_base, grado_bom_base)
            # Interpolar H en la curva base para el Q equivalente
            q_equiv_base = bep_q_vfd / factor_rpm_vfd
            h_equiv_base = np.polyval(coef_bom_base, q_equiv_base)
            bep_h_vfd = h_equiv_base * (factor_rpm_vfd ** 2)
            
            # GUARDAR BEP VFD EN SESSION_STATE para usar en expander de Allievi
            st.session_state['bep_q_vfd'] = float(bep_q_vfd)
            st.session_state['bep_h_vfd'] = float(bep_h_vfd)
            st.session_state['bep_eta_vfd'] = float(bep_eta_vfd)
            z_min_p = st.session_state.get('zona_eff_min', 65.0) / 100.0
            z_max_p = st.session_state.get('zona_eff_max', 115.0) / 100.0
            zona_min_v = bep_q_vfd * z_min_p
            zona_max_v = bep_q_vfd * z_max_p

        # 4. Rango de visualización para gráficos VFD (Autoajustable)
        q_op_ref = interseccion_vfd[0] if interseccion_vfd else bep_q_vfd
        # El límite físico de la bomba escalado por las leyes de afinidad (eta = rpm_ratio)
        q_limit_vfd = x_max_bom_base * eta if 'x_max_bom_base' in locals() else q_op_ref * 1.5
        
        # El rango será el máximo entre el límite físico y el 140% del punto de operación
        x_max_plot_v = max(q_op_ref * 1.4, bep_q_vfd * 1.2, q_limit_vfd, 1.0)
        x_ext_v = np.linspace(0, x_max_plot_v, 500)
        u_flow = st.session_state.get('flow_unit', 'L/s')
        x_disp_v = x_ext_v * 3.6 if u_flow == 'm³/h' else x_ext_v

        # Layout de 3 columnas para VFD (Restaurado según solicitud del usuario)
        col_vfd1, col_vfd2, col_vfd3 = st.columns([0.35, 0.35, 0.30])
        
        with col_vfd1:
            # --- 1. Gráfico H-Q VFD ---
            st.markdown(f"**Curva del Sistema y Bomba ({rpm_percentage:.2f}% RPM)**")
            fig_vfd = go.Figure()
            if coef_bom_vfd is not None and coef_sis is not None:
                y_sis_v = np.polyval(coef_sis, x_ext_v)
                y_bom_v = np.polyval(coef_bom_vfd, x_ext_v)
                if coef_rend_vfd is not None:
                    x_z = np.linspace(zona_min_v, zona_max_v, 50)
                    y_z = np.polyval(coef_bom_vfd, x_z)
                    x_z_disp = x_z * 3.6 if u_flow == 'm³/h' else x_z
                    fig_vfd.add_trace(go.Scatter(x=np.concatenate([x_z_disp, x_z_disp[::-1]]), y=np.concatenate([y_z, np.zeros_like(y_z)]), fill='toself', fillcolor='rgba(0, 255, 0, 0.1)', line=dict(color='rgba(0, 255, 0, 0.5)', width=1), name="Zona de Eficiencia", showlegend=True))
                fig_vfd.add_trace(go.Scatter(x=x_disp_v, y=y_sis_v, mode='lines', name='Sistema', line=dict(color='red')))
                fig_vfd.add_trace(go.Scatter(x=x_disp_v, y=y_bom_v, mode='lines', name=f'Bomba ({rpm_percentage:.1f}%)', line=dict(color='blue')))
                if interseccion_vfd:
                    q_i_disp = interseccion_vfd[0] * 3.6 if u_flow == 'm³/h' else interseccion_vfd[0]
                    fig_vfd.add_trace(go.Scatter(x=[q_i_disp], y=[interseccion_vfd[1]], mode='markers+text', name='Op. VFD', marker=dict(color='orange', size=10, symbol='star'), text=["Op. VFD"], textposition="top right"))
                
                # Calcular rangos inteligentes VFD con valores máximos de curva
                q_op_vfd = interseccion_vfd[0] if interseccion_vfd else (bep_q_vfd if bep_q_vfd > 0 else 0)
                h_op_vfd = interseccion_vfd[1] if interseccion_vfd else (np.polyval(coef_bom_vfd, bep_q_vfd) if bep_q_vfd > 0 else 0)
                h_static_vfd = st.session_state.get('altura_estatica_total', 0)
                
                # Usar solo el máximo de la bomba, no del sistema (que puede ser muy alto)
                smart_x_vfd, smart_y_vfd = calculate_smart_axes(
                    q_op_vfd, h_op_vfd, h_static_vfd, x_ext_v.max(), 
                    tipo_grafico="hq",
                    q_max_curve=x_ext_v.max(),
                    val_max_curve=y_bom_v.max()  # Solo bomba, no sistema
                )
                if u_flow == 'm³/h':
                    smart_x_vfd = [v * 3.6 for v in smart_x_vfd]

                # Usar rangos inteligentes directamente
                x_range_vfd = smart_x_vfd
                y_range_vfd = smart_y_vfd
                
                fig_vfd.update_layout(
                    xaxis_title=f"Q [{get_display_unit_label(u_flow)}]",
                    yaxis_title="H [m]",
                    xaxis=dict(range=x_range_vfd),
                    yaxis=dict(range=y_range_vfd) if y_range_vfd else dict(autorange=True),
                    legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
                    margin=dict(t=40, b=80)
                )
                st.plotly_chart(fig_vfd, use_container_width=True, key="vfd_hq_chart_v_fin")
                if interseccion_vfd:
                    u_d = "m³/h" if u_flow == 'm³/h' else "L/s"
                    st.markdown(f"""<div style="background-color: #e6f3ff; padding: 10px; border-radius: 5px; border-left: 4px solid #0066cc;"><strong>Punto de Operación:</strong><br><strong>Caudal (Q):</strong> {q_i_disp:.2f} {u_d}<br><strong>Altura (H):</strong> {interseccion_vfd[1]:.2f} m</div>""", unsafe_allow_html=True)

            # --- 2. Gráfico Potencia VFD ---
            st.markdown("**Potencia (PBHP-Q) VFD**")
            fig_pot_v = go.Figure()
            if coef_pot_vfd is not None:
                y_pot_v = np.polyval(coef_pot_vfd, x_ext_v)
                if coef_rend_vfd is not None:
                    x_z_p = np.linspace(zona_min_v, zona_max_v, 50)
                    y_z_p = np.polyval(coef_pot_vfd, x_z_p)
                    x_z_disp_p = x_z_p * 3.6 if u_flow == 'm³/h' else x_z_p
                    fig_pot_v.add_trace(go.Scatter(x=np.concatenate([x_z_disp_p, x_z_disp_p[::-1]]), y=np.concatenate([y_z_p, np.zeros_like(y_z_p)]), fill='toself', fillcolor='rgba(0, 255, 0, 0.1)', line=dict(color='rgba(0, 255, 0, 0.5)', width=1), name="Zona de Eficiencia", showlegend=True))
                fig_pot_v.add_trace(go.Scatter(x=x_disp_v, y=y_pot_v, mode='lines', name='Potencia VFD', line=dict(color='orange')))
                if interseccion_vfd:
                    p_op_v = np.polyval(coef_pot_vfd, interseccion_vfd[0])
                    fig_pot_v.add_trace(go.Scatter(x=[q_i_disp], y=[p_op_v], mode='markers+text', name='Pot. Op.', marker=dict(color='orange', size=8, symbol='star'), text=[f"{p_op_v:.1f} HP"], textposition="top right"))
                
                # Calcular rangos inteligentes con valores máximos de curva
                q_op_vfd = interseccion_vfd[0] if interseccion_vfd else 0
                pot_op_vfd = np.polyval(coef_pot_vfd, q_op_vfd) if q_op_vfd > 0 else 0
                smart_x_pot_v, smart_y_pot_v = calculate_smart_axes(
                    q_op_vfd, pot_op_vfd, 0, x_ext_v.max(), 
                    tipo_grafico="potencia",
                    q_max_curve=x_ext_v.max(),
                    val_max_curve=y_pot_v.max()
                )
                
                if u_flow == 'm³/h':
                    smart_x_pot_v = [v * 3.6 for v in smart_x_pot_v]

                # Usar rangos inteligentes directamente
                x_range_pot_vfd = smart_x_pot_v
                y_range_pot_vfd = smart_y_pot_v
                
                fig_pot_v.update_layout(
                    xaxis_title=f"Q [{get_display_unit_label(u_flow)}]",
                    yaxis_title="Potencia [HP]",
                    xaxis=dict(range=x_range_pot_vfd),
                    yaxis=dict(range=y_range_pot_vfd) if y_range_pot_vfd else dict(autorange=True),
                    legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
                    margin=dict(t=40, b=80)
                )
                st.plotly_chart(fig_pot_v, use_container_width=True, key="vfd_pot_chart_v_fin")
                if interseccion_vfd:
                    st.markdown(f"""<div style="background-color: #e6f3ff; padding: 10px; border-radius: 5px; border-left: 4px solid #0066cc;"><strong>Punto de Operación:</strong><br><strong>Caudal (Q):</strong> {q_i_disp:.2f} {get_display_unit_label(u_flow)}<br><strong>Potencia:</strong> {p_op_v:.2f} HP</div>""", unsafe_allow_html=True)

            with col_vfd2:
                # --- 3. Gráfico Rendimiento VFD ---
                st.markdown(f"**Rendimiento (η-Q) VFD**")
                fig_rend_v = go.Figure()
                if coef_rend_vfd is not None:
                    y_rend_v = np.polyval(coef_rend_vfd, x_ext_v)
                    x_z_r = np.linspace(zona_min_v, zona_max_v, 50)
                    y_z_r = np.polyval(coef_rend_vfd, x_z_r)
                    x_z_disp_r = x_z_r * 3.6 if u_flow == 'm³/h' else x_z_r
                    fig_rend_v.add_trace(go.Scatter(x=np.concatenate([x_z_disp_r, x_z_disp_r[::-1]]), y=np.concatenate([y_z_r, np.zeros_like(y_z_r)]), fill='toself', fillcolor='rgba(0, 255, 0, 0.1)', line=dict(color='rgba(0, 255, 0, 0.5)', width=1), name="Zona de Eficiencia", showlegend=True))
                    fig_rend_v.add_trace(go.Scatter(x=x_disp_v, y=y_rend_v, mode='lines', name='Rendimiento VFD', line=dict(color='green')))
                    bep_q_d_v = bep_q_vfd * 3.6 if u_flow == 'm³/h' else bep_q_vfd
                    fig_rend_v.add_trace(go.Scatter(x=[bep_q_d_v], y=[bep_eta_vfd], mode='markers+text', name='BEP VFD', marker=dict(color='darkgreen', size=8, symbol='diamond'), text=[f"BEP: {bep_eta_vfd:.1f}%"], textposition="top right"))
                    if interseccion_vfd:
                        r_op_v = np.polyval(coef_rend_vfd, interseccion_vfd[0])
                        fig_rend_v.add_trace(go.Scatter(x=[q_i_disp], y=[r_op_v], mode='markers+text', name='Rend. Op.', marker=dict(color='orange', size=8, symbol='star'), text=[f"{r_op_v:.1f}%"], textposition="top right"))
                    
                    # Calcular rangos inteligentes con valores máximos de curva
                    q_op_vfd = interseccion_vfd[0] if interseccion_vfd else bep_q_vfd
                    rend_op_vfd = np.polyval(coef_rend_vfd, q_op_vfd) if q_op_vfd > 0 else bep_eta_vfd
                    smart_x_rend_v, smart_y_rend_v = calculate_smart_axes(
                        q_op_vfd, rend_op_vfd, 0, x_ext_v.max(), 
                        tipo_grafico="rendimiento",
                        q_max_curve=x_ext_v.max(),
                        val_max_curve=y_rend_v.max()
                    )
                    
                    if u_flow == 'm³/h':
                        smart_x_rend_v = [v * 3.6 for v in smart_x_rend_v]

                    # Usar rangos inteligentes directamente
                    x_range_rend_vfd = smart_x_rend_v
                    y_range_rend_vfd = smart_y_rend_v
                    
                    fig_rend_v.update_layout(
                        xaxis_title=f"Q [{get_display_unit_label(u_flow)}]",
                        yaxis_title="Rendimiento [%]",
                        xaxis=dict(range=x_range_rend_vfd),
                        yaxis=dict(range=y_range_rend_vfd) if y_range_rend_vfd else dict(autorange=True),
                        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
                        margin=dict(t=40, b=80)
                    )
                    st.plotly_chart(fig_rend_v, use_container_width=True, key="vfd_rend_chart_v_final")
                    if interseccion_vfd:
                        st.markdown(f"""<div style="background-color: #e6f3ff; padding: 10px; border-radius: 5px; border-left: 4px solid #0066cc;"><strong>Punto de Operación:</strong><br><strong>Caudal (Q):</strong> {q_i_disp:.2f} {get_display_unit_label(u_flow)}<br><strong>Rendimiento:</strong> {r_op_v:.1f}%</div>""", unsafe_allow_html=True)

                # --- 4. Gráfico NPSH VFD ---
                st.markdown("**NPSH Requerido (NPSHR-Q) VFD**")
                fig_npsh_v = go.Figure()
                if coef_npsh_vfd is not None:
                    y_npsh_v = np.polyval(coef_npsh_vfd, x_ext_v)
                    fig_npsh_v.add_trace(go.Scatter(x=x_disp_v, y=y_npsh_v, mode='lines', name='NPSH VFD', line=dict(color='purple')))
                    if coef_rend_vfd is not None:
                        y_z_n = np.polyval(coef_npsh_vfd, x_z_r)
                        fig_npsh_v.add_trace(go.Scatter(x=np.concatenate([x_z_disp_r, x_z_disp_r[::-1]]), y=np.concatenate([y_z_n, np.zeros_like(y_z_n)]), fill='toself', fillcolor='rgba(0, 255, 0, 0.1)', line=dict(color='rgba(0, 255, 0, 0.5)', width=1), name="Zona de Eficiencia", showlegend=True))
                    if interseccion_vfd:
                        n_op_v = np.polyval(coef_npsh_vfd, interseccion_vfd[0])
                        fig_npsh_v.add_trace(go.Scatter(x=[q_i_disp], y=[n_op_v], mode='markers+text', name='NPSH Op.', marker=dict(color='orange', size=8, symbol='star'), text=[f"{n_op_v:.1f} m"], textposition="top right"))
                    
                    # Calcular rangos inteligentes con valores máximos de curva
                    q_op_vfd = interseccion_vfd[0] if interseccion_vfd else 0
                    npsh_op_vfd = np.polyval(coef_npsh_vfd, q_op_vfd) if q_op_vfd > 0 else 0
                    smart_x_npsh_v, smart_y_npsh_v = calculate_smart_axes(
                        q_op_vfd, npsh_op_vfd, 0, x_ext_v.max(), 
                        tipo_grafico="npsh",
                        q_max_curve=x_ext_v.max(),
                        val_max_curve=y_npsh_v.max()
                    )
                    
                    if u_flow == 'm³/h':
                        smart_x_npsh_v = [v * 3.6 for v in smart_x_npsh_v]

                    # Usar rangos inteligentes directamente
                    x_range_npsh_vfd = smart_x_npsh_v
                    y_range_npsh_vfd = smart_y_npsh_v
                    
                    fig_npsh_v.update_layout(
                        xaxis_title=f"Q [{get_display_unit_label(u_flow)}]",
                        yaxis_title="NPSH [m]",
                        xaxis=dict(range=x_range_npsh_vfd),
                        yaxis=dict(range=y_range_npsh_vfd) if y_range_npsh_vfd else dict(autorange=True),
                        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
                        margin=dict(t=40, b=80)
                    )
                    st.plotly_chart(fig_npsh_v, use_container_width=True, key="vfd_npsh_chart_v_final")
                    if interseccion_vfd:
                        st.markdown(f"""<div style="background-color: #e6f3ff; padding: 10px; border-radius: 5px; border-left: 4px solid #0066cc;"><strong>Punto de Operación:</strong><br><strong>Caudal (Q):</strong> {q_i_disp:.2f} {get_display_unit_label(u_flow)}<br><strong>NPSH:</strong> {n_op_v:.2f} m</div>""", unsafe_allow_html=True)

        with col_vfd3:
            # El expander de personalización VFD ha sido eliminado en favor del autoajuste inteligente
            
            with st.expander(f"📊 Resumen y Comentarios Técnicos - VFD ({rpm_percentage:.2f}% RPM)", expanded=False):
                st.markdown("### 📈 **Resumen de Resultados**")
                
                if interseccion_vfd:
                    qv, hv = interseccion_vfd
                    ev = np.polyval(coef_rend_vfd, qv) if coef_rend_vfd is not None else 0
                    pv = np.polyval(coef_pot_vfd, qv) if coef_pot_vfd is not None else 0
                    nv = np.polyval(coef_npsh_vfd, qv) if coef_npsh_vfd is not None else 0
                    
                    # Guardar resultados VFD
                    st.session_state['vfd_results'] = {'q_op_vfd':qv, 'h_op_vfd':hv, 'eff_vfd':ev, 'power_vfd_hp':pv, 'npsh_vfd':nv, 'rpm_percentage':rpm_percentage}
                    
                    # Mostrar en unidades correctas
                    qd_v = qv * 3.6 if u_flow == 'm³/h' else qv
                    ud_v = "m³/h" if u_flow == 'm³/h' else "L/s"
                    
                    # Información de bombas en paralelo
                    nb_v = st.session_state.get('num_bombas', 1)
                    if nb_v > 1:
                        q_total_vfd = qv * nb_v
                        q_total_display_vfd = q_total_vfd * 3.6 if u_flow == 'm³/h' else q_total_vfd
                        power_total_vfd = pv * nb_v
                        
                        st.info(f"🔄 **Sistema con {nb_v} bombas en paralelo**")
                        st.markdown(f"""
                        **Punto de Operación por Bomba Individual:**
                        - **Caudal por Bomba:** {qd_v:.2f} {ud_v}
                        - **Altura:** {hv:.2f} m
                        - **Eficiencia:** {ev:.1f}%
                        - **Potencia por Bomba:** {pv:.2f} HP
                        - **NPSH Requerido:** {nv:.2f} m
                        
                        **Sistema Total ({nb_v} bombas):**
                        - **Caudal Total del Sistema:** {q_total_display_vfd:.2f} {ud_v}
                        - **Potencia Total del Sistema:** {power_total_vfd:.2f} HP
                        """)
                    else:
                        st.markdown(f"""
                        **Punto de Operación:**
                        - **Caudal:** {qd_v:.2f} {ud_v}
                        - **Altura:** {hv:.2f} m
                        - **Eficiencia:** {ev:.1f}%
                        - **Potencia:** {pv:.2f} HP
                        - **NPSH Requerido:** {nv:.2f} m
                        """)
                    
                    # Análisis de NPSH VFD
                    nd_v = st.session_state.get('npshd_mca', 0)
                    if nd_v > 0 and coef_npsh_vfd is not None:
                        st.markdown("### 🔍 **Análisis de NPSH (VFD)**")
                        
                        # Criterio estándar de la industria
                        margen_seguridad_vfd = 1.2 * nv
                        cumple_criterio_vfd = nd_v >= margen_seguridad_vfd
                        condicion_basica_vfd = nd_v > nv
                        
                        st.markdown(f"""
                        **Criterio de Diseño Estándar de la Industria (API/ASME):**
                        
                        **1. Condición de Diseño (NPSH_A > NPSH_R):**
                        - **NPSH Disponible (NPSH_A):** {nd_v:.2f} m.c.a.
                        - **NPSH Requerido (NPSH_R):** {nv:.2f} m.c.a.
                        - **Diferencia:** {nd_v - nv:+.2f} m.c.a.
                        
                        **2. Margen de Seguridad (Regla del 1.2 · NPSH_R):**
                        - **Margen Mínimo Requerido:** {margen_seguridad_vfd:.2f} m.c.a.
                        - **Margen Disponible:** {nd_v - margen_seguridad_vfd:+.2f} m.c.a.
                        """)
                        
                        if condicion_basica_vfd:
                            if cumple_criterio_vfd:
                                st.success("✅ **Diseño Robusto:** Cumple criterio estándar de la industria. NPSH_A ≥ 1.2×NPSH_R. Sin riesgo de cavitación.")
                            else:
                                st.warning("⚠️ **Diseño Marginal:** NPSH_A > NPSH_R pero < 1.2×NPSH_R. Riesgo de cavitación intermitente.")
                        else:
                            st.error("❌ **Diseño Inseguro:** NPSH_A < NPSH_R. Alto riesgo de cavitación.")
                    
                    # Comentarios Técnicos
                    st.markdown("### 🔧 **Comentarios Técnicos**")
                    if ev >= 80:
                        st.success("✅ **Eficiencia Excelente:** La bomba opera en zona de alta eficiencia (>80%)")
                    elif ev >= 70:
                        st.info("ℹ️ **Eficiencia Buena:** La bomba opera en zona de eficiencia aceptable (70-80%)")
                    else:
                        st.warning("⚠️ **Eficiencia Baja:** La bomba opera en zona de baja eficiencia (<70%)")
                    
                    # Análisis de BEP VFD
                    if coef_rend_vfd is not None:
                        st.markdown("### 🎯 **Análisis de BEP (Best Efficiency Point) VFD**")
                        bep_q_display_vfd = bep_q_vfd * 3.6 if u_flow == 'm³/h' else bep_q_vfd
                        bep_q_min_vfd = bep_q_vfd * 0.65 * (3.6 if u_flow == 'm³/h' else 1)
                        bep_q_max_vfd = bep_q_vfd * 1.15 * (3.6 if u_flow == 'm³/h' else 1)
                        
                        st.markdown(f"""
                        - **BEP Caudal:** {bep_q_display_vfd:.2f} {ud_v}
                        - **BEP Eficiencia:** {bep_eta_vfd:.1f}%
                        - **Zona de Eficiencia:** {st.session_state.get('zona_eff_min', 65.0):.0f}-{st.session_state.get('zona_eff_max', 115.0):.0f}% del BEP ({bep_q_min_vfd:.1f} - {bep_q_max_vfd:.1f} {ud_v})
                        """)
                        
                        zona_eff_min_pct = st.session_state.get('zona_eff_min', 65.0) / 100.0
                        zona_eff_max_pct = st.session_state.get('zona_eff_max', 115.0) / 100.0
                        if qv >= bep_q_vfd * zona_eff_min_pct and qv <= bep_q_vfd * zona_eff_max_pct:
                            st.success(f"✅ **Operación en Zona Eficiente:** El punto de operación está dentro de la zona de eficiencia ({st.session_state.get('zona_eff_min', 65.0):.0f}-{st.session_state.get('zona_eff_max', 115.0):.0f}% del BEP)")
                        else:
                            st.warning("⚠️ **Operación fuera de Zona Eficiente:** El punto de operación está fuera de la zona de eficiencia recomendada")
                    
                    # Ahorro energético
                    if interseccion and power_op > 0:
                        ahorro_hp = power_op - pv
                        ahorro_pct = (ahorro_hp / power_op) * 100
                        if ahorro_hp > 0:
                            st.markdown("### 💰 **Ahorro Energético**")
                            st.success(f"**Ahorro de Potencia:** {ahorro_hp:.2f} HP ({ahorro_pct:.1f}%)")
                            st.info(f"**Potencia a 100% RPM:** {power_op:.2f} HP → **Potencia VFD:** {pv:.2f} HP")
                    
                    # Recomendaciones
                    st.markdown("### 💡 **Recomendaciones**")
                    st.markdown("""
                    - Verificar que la bomba seleccionada cubra el rango de operación requerido
                    - Monitorear la eficiencia durante la operación con VFD
                    - Operar preferiblemente dentro de la zona de eficiencia (65-115% del BEP)
                    - Considerar el ahorro energético al usar VFD
                    """)
                else:
                    st.warning("⚠️ No se pudo determinar el punto de operación VFD")
    else:
        st.warning("⚠️ No se ha definido un caudal nominal en el diseño")
    
    # --- Sección 8: Tablas ---
    st.markdown("---")
    st.subheader("8. Tablas")
    
    # Layout 3 columnas: 35-35-30%
    col_tablas1, col_tablas2, col_tablas3 = st.columns([0.35, 0.35, 0.30])
    
    # Columna 1: Tablas de gráficos a 100% RPM
    with col_tablas1:
        with st.expander("Tablas de gráficos a 100% RPM", expanded=False):
            # Información de las tablas
            st.markdown("**Información de las tablas a 100% RPM:**")
            
            # Inputs para Q min y Q max
            col_q_min, col_q_max = st.columns(2)
            
            with col_q_min:
                caudal_diseno = st.session_state.get('caudal_lps', 51.0)
                q_min_100 = st.number_input(
                    "Q min (L/s):", 
                    min_value=0.0, 
                    max_value=1000.0, 
                    value=0.0,
                    step=0.1,
                    key="q_min_100_tab2",
                    help="Caudal mínimo para la tabla"
                )
            
            with col_q_max:
                q_max_100 = st.number_input(
                    "Q max (L/s):", 
                    min_value=0.1, 
                    max_value=1000.0, 
                    value=caudal_diseno,
                    step=0.1,
                    key="q_max_100_tab2",
                    help="Caudal máximo para la tabla"
                )
            
            # Calcular paso automático basado en Q max
            if q_max_100 < 10:
                paso_auto_100 = 0.25
            elif q_max_100 < 20:
                paso_auto_100 = 1.0
            elif q_max_100 < 40:
                paso_auto_100 = 2.5
            elif q_max_100 < 100:
                paso_auto_100 = 5.0
            else:
                paso_auto_100 = 10.0
            
            # Campo para definir el paso del caudal (con valor automático)
            paso_caudal_100 = st.number_input(
                "Paso del caudal (L/s):", 
                min_value=0.1, 
                max_value=50.0, 
                value=paso_auto_100,
                step=0.1,
                key="paso_caudal_100_tab2",
                help=f"Define el incremento entre cada punto de la tabla a 100% RPM (Automático: {paso_auto_100} L/s)"
            )
        
            # === MENSAJE INFORMATIVO PARA ALLIEVI ===
            # Calcular Q objetivo para H≈0 (solo informativo)
            try:
                curva_inputs_temp = st.session_state.get('curva_inputs', {})
                puntos_bomba_temp = curva_inputs_temp.get('bomba', [])
                
                if len(puntos_bomba_temp) >= 2:
                    x_bom_temp = np.array([pt[0] for pt in puntos_bomba_temp])
                    y_bom_temp = np.array([pt[1] for pt in puntos_bomba_temp])
                    
                    if np.all(np.isfinite(x_bom_temp)) and np.all(np.isfinite(y_bom_temp)):
                        ajuste_tipo_temp = st.session_state.get('ajuste_tipo', 'Cuadrática (2do grado)')
                        grado_temp = 1 if ajuste_tipo_temp == "Lineal" else 2 if ajuste_tipo_temp == "Cuadrática (2do grado)" else 3
                        coef_temp = np.polyfit(x_bom_temp, y_bom_temp, grado_temp)
                        
                        # Resolver H ≈ 0
                        if grado_temp == 2:
                            a, b, c = coef_temp[0], coef_temp[1], coef_temp[2] # Corrected order for polyfit output
                            discriminante = b**2 - 4*a*c
                            if discriminante >= 0 and a != 0:
                                q1 = (-b + np.sqrt(discriminante)) / (2*a)
                                q2 = (-b - np.sqrt(discriminante)) / (2*a)
                                q_para_h_cero = max(q1, q2) if q1 > 0 or q2 > 0 else q_max_100 * 1.5
                            else:
                                q_para_h_cero = q_max_100 * 1.5
                        else: # Linear or Cubic (simplified for linear, cubic might need numerical solver)
                            q_para_h_cero = -coef_temp[-1] / coef_temp[-2] if len(coef_temp) >= 2 and coef_temp[-2] != 0 else q_max_100 * 1.5
                        
                        # Mostrar mensaje informativo
                        st.info(f"💡 **Para Allievi (método 'Curvas por Puntos'):** Para cubrir desde Q=0 hasta H≈0, ajustar **Q max ≈ {q_para_h_cero:.2f} L/s**")
            except Exception as e:
                # st.error(f"Error calculating Q for H≈0: {e}") # For debugging
                pass
            
            st.markdown("---")
            
            # Obtener datos de las curvas a 100% RPM
            curva_inputs = st.session_state.get('curva_inputs', {})
            ajuste_tipo = st.session_state.get('ajuste_tipo', 'Cuadrática (2do grado)')
            
            # Usar Q max (ya ajustado si extrapolación está activa)
            caudal_max_tabla_100 = q_max_100
            punto_operacion_100 = st.session_state.get('interseccion', [0])[0] if st.session_state.get('interseccion') else 0
            
            # Generar caudales para las tablas usando Q min y Q max
            caudales_tabla_100 = np.arange(q_min_100, caudal_max_tabla_100 + paso_caudal_100, paso_caudal_100)
            
            # Crear 4 columnas para las tablas
            tab_col1_100, tab_col2_100, tab_col3_100 = st.columns([0.35, 0.35, 0.30])
            tab_col4_100, tab_col5_100, tab_col6_100 = st.columns([0.35, 0.35, 0.30])
            
            # Tabla 1: Curva de la Bomba (H-Q) a 100% RPM
            with tab_col1_100:
                st.markdown("**Curva de la Bomba (H-Q) a 100% RPM**")
                
                puntos_bomba = curva_inputs.get('bomba', [])
                
                if len(puntos_bomba) >= 2:
                    # Usar curvas originales directamente
                    n_bombas = st.session_state.get('num_bombas', 1)
                    x_bom = np.array([pt[0] for pt in puntos_bomba])
                    y_bom = np.array([pt[1] for pt in puntos_bomba])
                    
                    if np.all(np.isfinite(x_bom)) and np.all(np.isfinite(y_bom)):
                        grado = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
                        coef_bom = np.polyfit(x_bom, y_bom, grado)
                        
                        # Calcular valores para la tabla
                        alturas = np.polyval(coef_bom, caudales_tabla_100)
                        
                        # Crear DataFrame con unidades correctas
                        unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                        unidad_display = get_display_unit_label(unidad_caudal)
                        
                        if unidad_caudal == 'm³/h':
                            caudales_display = np.round(caudales_tabla_100 * 3.6, 3)
                        else:
                            caudales_display = np.round(caudales_tabla_100, 3)
                        
                        df_bomba_100 = pd.DataFrame({
                            f'Caudal ({unidad_display})': caudales_display,
                            'Altura (m)': np.round(alturas, 3)
                        })
                        
                        # Marcar punto de operación (solo para visualización)
                        if punto_operacion_100 > 0:
                            idx_op = np.argmin(np.abs(caudales_tabla_100 - punto_operacion_100))
                            if idx_op < len(df_bomba_100):
                                # Crear una copia para mostrar con ⭐
                                df_bomba_100_display = df_bomba_100.copy()
                                # Convertir a string ANTES de agregar el emoji
                                df_bomba_100_display = df_bomba_100_display.astype(str)
                                df_bomba_100_display.loc[idx_op, 'Altura (m)'] = f"⭐ {df_bomba_100_display.loc[idx_op, 'Altura (m)']}"
                                st.dataframe(df_bomba_100_display, height=300, use_container_width=True)
                            else:
                                st.dataframe(df_bomba_100, height=300, use_container_width=True)
                        else:
                            st.dataframe(df_bomba_100, height=300, use_container_width=True)
                        
                        # Guardar para Excel
                        st.session_state['df_bomba_100'] = df_bomba_100
                    else:
                        st.warning("Datos de bomba no válidos")
                else:
                    st.info("No hay datos de bomba disponibles")
            
            # Tabla 2: Curva de Rendimiento (η-Q) a 100% RPM
            with tab_col2_100:
                st.markdown("**Curva de Rendimiento (η-Q) a 100% RPM**")
                
                puntos_rendimiento = curva_inputs.get('rendimiento', [])
                
                if len(puntos_rendimiento) >= 2:
                    x_rend = np.array([pt[0] for pt in puntos_rendimiento])
                    y_rend = np.array([pt[1] for pt in puntos_rendimiento])
                    
                    if np.all(np.isfinite(x_rend)) and np.all(np.isfinite(y_rend)):
                        grado = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
                        coef_rend = np.polyfit(x_rend, y_rend, grado)
                        
                        # Calcular valores para la tabla
                        rendimientos = np.polyval(coef_rend, caudales_tabla_100)
                        
                        # Crear DataFrame con unidades correctas
                        unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                        unidad_display = get_display_unit_label(unidad_caudal)
                        
                        if unidad_caudal == 'm³/h':
                            caudales_display = np.round(caudales_tabla_100 * 3.6, 3)
                        else:
                            caudales_display = np.round(caudales_tabla_100, 3)
                        
                        df_rendimiento_100 = pd.DataFrame({
                            f'Caudal ({unidad_display})': caudales_display,
                            'Rendimiento (%)': np.round(rendimientos, 3)
                        })
                        
                        # Marcar punto de operación (solo para visualización)
                        if punto_operacion_100 > 0:
                            idx_op = np.argmin(np.abs(caudales_tabla_100 - punto_operacion_100))
                            if idx_op < len(df_rendimiento_100):
                                # Crear una copia para mostrar con ⭐
                                df_rendimiento_100_display = df_rendimiento_100.copy()
                                # Convertir a string ANTES de agregar el emoji
                                df_rendimiento_100_display = df_rendimiento_100_display.astype(str)
                                df_rendimiento_100_display.loc[idx_op, 'Rendimiento (%)'] = f"⭐ {df_rendimiento_100_display.loc[idx_op, 'Rendimiento (%)']}"
                                st.dataframe(df_rendimiento_100_display, height=300, use_container_width=True)
                            else:
                                st.dataframe(df_rendimiento_100, height=300, use_container_width=True)
                        else:
                            st.dataframe(df_rendimiento_100, height=300, use_container_width=True)
                        
                        # Guardar para Excel
                        st.session_state['df_rendimiento_100'] = df_rendimiento_100
                    else:
                        st.warning("Datos de rendimiento no válidos")
                else:
                    st.info("No hay datos de rendimiento disponibles")
            
            # Tabla 3: Curva de Potencia (PBHP-Q) a 100% RPM
            with tab_col3_100:
                st.markdown("**Curva de Potencia (PBHP-Q) a 100% RPM**")
                
                puntos_potencia = curva_inputs.get('potencia', [])
                
                if len(puntos_potencia) >= 2:
                    x_pot = np.array([pt[0] for pt in puntos_potencia])
                    y_pot = np.array([pt[1] for pt in puntos_potencia])
                    
                    if np.all(np.isfinite(x_pot)) and np.all(np.isfinite(y_pot)):
                        grado = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
                        coef_pot = np.polyfit(x_pot, y_pot, grado)
                        
                        # Calcular valores para la tabla
                        potencias = np.polyval(coef_pot, caudales_tabla_100)
                        
                        # Crear DataFrame con unidades correctas
                        unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                        unidad_display = get_display_unit_label(unidad_caudal)
                        
                        if unidad_caudal == 'm³/h':
                            caudales_display = np.round(caudales_tabla_100 * 3.6, 3)
                        else:
                            caudales_display = np.round(caudales_tabla_100, 3)
                        
                        df_potencia_100 = pd.DataFrame({
                            f'Caudal ({unidad_display})': caudales_display,
                            'Potencia (HP)': np.round(potencias, 3)
                        })
                        
                        # Marcar punto de operación (solo para visualización)
                        if punto_operacion_100 > 0:
                            idx_op = np.argmin(np.abs(caudales_tabla_100 - punto_operacion_100))
                            if idx_op < len(df_potencia_100):
                                # Crear una copia para mostrar con ⭐
                                df_potencia_100_display = df_potencia_100.copy()
                                # Convertir a string ANTES de agregar el emoji
                                df_potencia_100_display = df_potencia_100_display.astype(str)
                                df_potencia_100_display.loc[idx_op, 'Potencia (HP)'] = f"⭐ {df_potencia_100_display.loc[idx_op, 'Potencia (HP)']}"
                                st.dataframe(df_potencia_100_display, height=300, use_container_width=True)
                            else:
                                st.dataframe(df_potencia_100, height=300, use_container_width=True)
                        else:
                            st.dataframe(df_potencia_100, height=300, use_container_width=True)
                        
                        # Guardar para Excel
                        st.session_state['df_potencia_100'] = df_potencia_100
                    else:
                        st.warning("Datos de potencia no válidos")
                else:
                    st.info("No hay datos de potencia disponibles")
            
            # Tabla 4: Curva de NPSH (NPSHR-Q) a 100% RPM
            with tab_col4_100:
                st.markdown("**Curva de NPSH (NPSHR-Q) a 100% RPM**")
                
                puntos_npsh = curva_inputs.get('npsh', [])
                
                if len(puntos_npsh) >= 2:
                    x_npsh = np.array([pt[0] for pt in puntos_npsh])
                    y_npsh = np.array([pt[1] for pt in puntos_npsh])
                    
                    if np.all(np.isfinite(x_npsh)) and np.all(np.isfinite(y_npsh)):
                        grado = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
                        coef_npsh = np.polyfit(x_npsh, y_npsh, grado)
                        
                        # Calcular valores para la tabla
                        npsh_values = np.polyval(coef_npsh, caudales_tabla_100)
                        
                        # Crear DataFrame con unidades correctas
                        unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                        unidad_display = get_display_unit_label(unidad_caudal)
                        
                        if unidad_caudal == 'm³/h':
                            caudales_display = np.round(caudales_tabla_100 * 3.6, 3)
                        else:
                            caudales_display = np.round(caudales_tabla_100, 3)
                        
                        df_npsh_100 = pd.DataFrame({
                            f'Caudal ({unidad_display})': caudales_display,
                            'NPSH (m)': np.round(npsh_values, 3)
                        })
                        
                        # Marcar punto de operación (solo para visualización)
                        if punto_operacion_100 > 0:
                            idx_op = np.argmin(np.abs(caudales_tabla_100 - punto_operacion_100))
                            if idx_op < len(df_npsh_100):
                                # Crear una copia para mostrar con ⭐
                                df_npsh_100_display = df_npsh_100.copy()
                                # Convertir a string ANTES de agregar el emoji
                                df_npsh_100_display = df_npsh_100_display.astype(str)
                                df_npsh_100_display.loc[idx_op, 'NPSH (m)'] = f"⭐ {df_npsh_100_display.loc[idx_op, 'NPSH (m)']}"
                                st.dataframe(df_npsh_100_display, height=300, use_container_width=True)
                            else:
                                st.dataframe(df_npsh_100, height=300, use_container_width=True)
                        else:
                            st.dataframe(df_npsh_100, height=300, use_container_width=True)
                        
                        # Guardar para Excel
                        st.session_state['df_npsh_100'] = df_npsh_100
                    else:
                        st.warning("Datos de NPSH no válidos")
                else:
                    st.info("No hay datos de NPSH disponibles")
            
            # Tabla 5: Curva del Sistema (H-Q) a 100% RPM
            with tab_col5_100:
                st.markdown("**Curva del Sistema (H-Q) a 100% RPM**")
                
                # Obtener puntos del sistema desde textarea_sistema primero
                puntos_sistema = []
                unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                
                # Primero intentar leer desde textarea_sistema
                if 'textarea_sistema' in st.session_state and st.session_state['textarea_sistema']:
                    try:
                        # Procesar el contenido del textarea
                        texto_curva = st.session_state['textarea_sistema']
                        lines = [line.strip() for line in texto_curva.splitlines() if line.strip()]
                        
                        for line in lines:
                            vals = [v for v in line.replace(';', ' ').replace('\t', ' ').split() if v]
                            if len(vals) == 2:
                                try:
                                    x = float(vals[0])
                                    y = float(vals[1])
                                    
                                    # Convertir caudal a L/s para cálculos internos
                                    if unidad_caudal == 'm³/h':
                                        x = x / 3.6  # m³/h a L/s
                                    
                                    puntos_sistema.append((x, y))
                                except Exception:
                                    pass
                    except Exception as e:
                        st.warning(f"Error procesando puntos del sistema desde textarea: {e}")
                
                # Si no hay puntos en textarea, intentar desde curva_inputs
                if not puntos_sistema and 'sistema' in curva_inputs and curva_inputs['sistema']:
                    puntos_sistema = curva_inputs['sistema']
                
                # Si aún no hay puntos, calcular automáticamente
                if not puntos_sistema:
                    try:
                        # Generar caudales para calcular la curva del sistema
                        flows = np.linspace(0, 200, 20).tolist()  # 0 a 200 L/s
                        flow_unit = st.session_state.get('flow_unit', 'L/s')
                        
                        # Obtener parámetros del sistema
                        system_params = {
                            'h_estatica': st.session_state.get('h_estatica', 50.0),
                            'long_succion': st.session_state.get('long_succion', 10.0),
                            'diam_succion_m': st.session_state.get('diam_succion', 200.0) / 1000.0,
                            'C_succion': st.session_state.get('C_succion', 150),
                            'accesorios_succion': st.session_state.get('accesorios_succion', []),
                            'otras_perdidas_succion': 0.0,
                            'long_impulsion': st.session_state.get('long_impulsion', 100.0),
                            'diam_impulsion_m': st.session_state.get('diam_impulsion', 150.0) / 1000.0,
                            'C_impulsion': st.session_state.get('C_impulsion', 150),
                            'accesorios_impulsion': st.session_state.get('accesorios_impulsion', []),
                            'otras_perdidas_impulsion': 0.0
                        }
                        
                        from core.system_head import calculate_adt_for_multiple_flows
                        adt_values = calculate_adt_for_multiple_flows(flows, flow_unit, system_params)
                        
                        if adt_values:
                            puntos_sistema = [(flows[i], adt_values[i]) for i in range(len(flows)) if adt_values[i] is not None]
                        else:
                            puntos_sistema = []
                    except Exception as e:
                        st.warning(f"Error calculando curva del sistema: {e}")
                        puntos_sistema = []

                if len(puntos_sistema) >= 2:
                    x_sis = np.array([pt[0] for pt in puntos_sistema])
                    y_sis = np.array([pt[1] for pt in puntos_sistema])
                    
                    if np.all(np.isfinite(x_sis)) and np.all(np.isfinite(y_sis)):
                        # Ajustar el grado del polinomio según el número de puntos disponibles
                        grado_deseado = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
                        # El grado no puede ser mayor que (número de puntos - 1)
                        grado = min(grado_deseado, len(x_sis) - 1)
                        
                        coef_sis = np.polyfit(x_sis, y_sis, grado)
                        
                        # Calcular valores para la tabla
                        alturas_sistema = np.polyval(coef_sis, caudales_tabla_100)
                        
                        # Crear DataFrame
                        df_sistema_100 = pd.DataFrame({
                            'Caudal (L/s)': np.round(caudales_tabla_100, 3),
                            'Altura (m)': np.round(alturas_sistema, 3)
                        })
                        
                        # Marcar punto de operación (solo para visualización)
                        if punto_operacion_100 > 0:
                            idx_op = np.argmin(np.abs(caudales_tabla_100 - punto_operacion_100))
                            if idx_op < len(df_sistema_100):
                                # Crear una copia para mostrar con ⭐
                                df_sistema_100_display = df_sistema_100.copy()
                                # Convertir a string ANTES de agregar el emoji
                                df_sistema_100_display = df_sistema_100_display.astype(str)
                                df_sistema_100_display.loc[idx_op, 'Altura (m)'] = f"⭐ {df_sistema_100_display.loc[idx_op, 'Altura (m)']}"
                                st.dataframe(df_sistema_100_display, height=300, use_container_width=True)
                            else:
                                st.dataframe(df_sistema_100, height=300, use_container_width=True)
                        else:
                            st.dataframe(df_sistema_100, height=300, use_container_width=True)
                        
                        # Guardar para Excel
                        st.session_state['df_sistema_100'] = df_sistema_100
                    else:
                        st.warning("Datos del sistema no válidos")
                else:
                    st.info("No hay datos del sistema disponibles")
            
            # Botón único para descargar todas las tablas a 100% RPM
            st.markdown("---")
            if st.button("📥 Descargar Todas las Tablas 100% RPM", key="download_all_100rpm", type="primary"):
                try:
                    # Crear buffer para el archivo Excel
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        # Obtener información de las tablas
                        interseccion = st.session_state.get('interseccion', None)
                        punto_operacion = interseccion[0] if interseccion else 0
                        total_puntos = len(caudales_tabla_100)
                        rango_caudal = f"0 a {caudales_tabla_100[-1]:.1f} L/s"
                        
                        # Hoja H-Q (Bomba)
                        if 'df_bomba_100' in st.session_state:
                            df_bomba = st.session_state['df_bomba_100'].copy()
                            # Agregar ecuación solo en la primera fila (C2)
                            if 'coef_bom' in locals():
                                df_bomba.loc[0, 'Ecuación'] = f"H = {coef_bom[0]:.6f}*Q² + {coef_bom[1]:.6f}*Q + {coef_bom[2]:.6f}" if len(coef_bom) > 2 else f"H = {coef_bom[0]:.6f}*Q + {coef_bom[1]:.6f}"
                            # Agregar información solo en la primera fila (D2)
                            unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                            unidad_display = get_display_unit_label(unidad_caudal)
                            if unidad_caudal == 'm³/h':
                                paso_display = paso_caudal_100 * 3.6
                                punto_op_display = punto_operacion * 3.6
                            else:
                                paso_display = paso_caudal_100
                                punto_op_display = punto_operacion
                            df_bomba.loc[0, 'Información'] = f"Rango: {rango_caudal}, Paso: {paso_display:.2f} {unidad_display}, Total: {total_puntos} puntos, Punto operación: {punto_op_display:.2f} {unidad_display}, Ajuste: {ajuste_tipo}"
                            df_bomba.to_excel(writer, sheet_name='H-Q', index=False)
                        
                        # Hoja Efficiency
                        if 'df_rendimiento_100' in st.session_state:
                            df_rend = st.session_state['df_rendimiento_100'].copy()
                            if 'coef_rend' in locals():
                                df_rend.loc[0, 'Ecuación'] = f"η = {coef_rend[0]:.6f}*Q² + {coef_rend[1]:.6f}*Q + {coef_rend[2]:.6f}" if len(coef_rend) > 2 else f"η = {coef_rend[0]:.6f}*Q + {coef_rend[1]:.6f}"
                            unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                            unidad_display = get_display_unit_label(unidad_caudal)
                            if unidad_caudal == 'm³/h':
                                paso_display = paso_caudal_100 * 3.6
                                punto_op_display = punto_operacion * 3.6
                            else:
                                paso_display = paso_caudal_100
                                punto_op_display = punto_operacion
                            df_rend.loc[0, 'Información'] = f"Rango: {rango_caudal}, Paso: {paso_display:.2f} {unidad_display}, Total: {total_puntos} puntos, Punto operación: {punto_op_display:.2f} {unidad_display}, Ajuste: {ajuste_tipo}"
                            df_rend.to_excel(writer, sheet_name='Efficiency', index=False)
                        
                        # Hoja Power
                        if 'df_potencia_100' in st.session_state:
                            df_pot = st.session_state['df_potencia_100'].copy()
                            if 'coef_pot' in locals():
                                df_pot.loc[0, 'Ecuación'] = f"P = {coef_pot[0]:.6f}*Q² + {coef_pot[1]:.6f}*Q + {coef_pot[2]:.6f}" if len(coef_pot) > 2 else f"P = {coef_pot[0]:.6f}*Q + {coef_pot[1]:.6f}"
                            unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                            unidad_display = get_display_unit_label(unidad_caudal)
                            if unidad_caudal == 'm³/h':
                                paso_display = paso_caudal_100 * 3.6
                                punto_op_display = punto_operacion * 3.6
                            else:
                                paso_display = paso_caudal_100
                                punto_op_display = punto_operacion
                            df_pot.loc[0, 'Información'] = f"Rango: {rango_caudal}, Paso: {paso_display:.2f} {unidad_display}, Total: {total_puntos} puntos, Punto operación: {punto_op_display:.2f} {unidad_display}, Ajuste: {ajuste_tipo}"
                            df_pot.to_excel(writer, sheet_name='Power', index=False)
                        
                        # Hoja NPSH
                        if 'df_npsh_100' in st.session_state:
                            df_npsh = st.session_state['df_npsh_100'].copy()
                            if 'coef_npsh' in locals():
                                df_npsh.loc[0, 'Ecuación'] = f"NPSH = {coef_npsh[0]:.6f}*Q² + {coef_npsh[1]:.6f}*Q + {coef_npsh[2]:.6f}" if len(coef_npsh) > 2 else f"NPSH = {coef_npsh[0]:.6f}*Q + {coef_npsh[1]:.6f}"
                            unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                            unidad_display = get_display_unit_label(unidad_caudal)
                            if unidad_caudal == 'm³/h':
                                paso_display = paso_caudal_100 * 3.6
                                punto_op_display = punto_operacion * 3.6
                            else:
                                paso_display = paso_caudal_100
                                punto_op_display = punto_operacion
                            df_npsh.loc[0, 'Información'] = f"Rango: {rango_caudal}, Paso: {paso_display:.2f} {unidad_display}, Total: {total_puntos} puntos, Punto operación: {punto_op_display:.2f} {unidad_display}, Ajuste: {ajuste_tipo}"
                            df_npsh.to_excel(writer, sheet_name='NPSH', index=False)
                        
                        # Hoja H-Q_sistema
                        if 'df_sistema_100' in st.session_state:
                            df_sis = st.session_state['df_sistema_100'].copy()
                            if 'coef_sis' in locals():
                                df_sis.loc[0, 'Ecuación'] = f"H = {coef_sis[0]:.6f}*Q² + {coef_sis[1]:.6f}*Q + {coef_sis[2]:.6f}" if len(coef_sis) > 2 else f"H = {coef_sis[0]:.6f}*Q + {coef_sis[1]:.6f}"
                            df_sis.loc[0, 'Información'] = f"Rango: {rango_caudal}, Paso: {paso_caudal_100} L/s, Total: {total_puntos} puntos, Punto operación: {punto_operacion:.2f} L/s, Ajuste: {ajuste_tipo}"
                            df_sis.to_excel(writer, sheet_name='H-Q_sistema', index=False)
                    
                    # Preparar archivo para descarga
                    output.seek(0)
                    excel_data = output.getvalue()
                    
                    # Descargar archivo
                    st.download_button(
                        label="💾 Descargar Curvas_Bomba_100RPM.xlsx",
                        data=excel_data,
                        file_name="Curvas_Bomba_100RPM.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_curvas_100rpm"
                    )
                    
                    st.success("✅ Archivo Excel generado exitosamente")
                    
                except Exception as e:
                    st.error(f"❌ Error al generar archivo Excel: {e}")
    
    # Columna 2: Tablas de gráficos VFD
    with col_tablas2:
        with st.expander(f"Tablas de gráficos a {rpm_percentage:.2f}% RPM", expanded=False):
            # Información de las tablas
            st.markdown(f"**Información de las tablas a {rpm_percentage:.2f}% RPM:**")
            
            # Inputs para Q min y Q max
            col_q_min_vdf, col_q_max_vdf = st.columns(2)
            
            with col_q_min_vdf:
                caudal_diseno = st.session_state.get('caudal_lps', 51.0)
                q_min_vdf = st.number_input(
                    "Q min (L/s):", 
                    min_value=0.0, 
                    max_value=1000.0, 
                    value=0.0,
                    step=0.1,
                    key="q_min_vdf_tab2",
                    help="Caudal mínimo para la tabla VDF"
                )
            
            with col_q_max_vdf:
                q_max_vdf = st.number_input(
                    "Q max (L/s):", 
                    min_value=0.1, 
                    max_value=1000.0, 
                    value=caudal_diseno,
                    step=0.1,
                    key="q_max_vdf_tab2",
                    help="Caudal máximo para la tabla VDF"
                )
            
            # Calcular paso automático basado en Q max
            if q_max_vdf < 10:
                paso_auto_vdf = 0.25
            elif q_max_vdf < 20:
                paso_auto_vdf = 1.0
            elif q_max_vdf < 40:
                paso_auto_vdf = 2.5
            elif q_max_vdf < 100:
                paso_auto_vdf = 5.0
            else:
                paso_auto_vdf = 10.0
            
            # Campo para definir el paso del caudal (con valor automático)
            paso_caudal_vdf = st.number_input(
                "Paso del caudal (L/s):", 
                min_value=0.1, 
                max_value=50.0, 
                value=paso_auto_vdf, 
                step=0.1,
                key="paso_caudal_vdf_tab2",
                help=f"Define el incremento entre cada punto de la tabla a {rpm_percentage:.2f}% RPM (Automático: {paso_auto_vdf} L/s)"
            )
            
            # === MENSAJE INFORMATIVO PARA ALLIEVI (VFD) ===
            # Calcular Q objetivo para H≈0 (solo informativo)
            try:
                curva_inputs_temp_vfd = st.session_state.get('curva_inputs', {})
                puntos_bomba_temp_vfd = curva_inputs_temp_vfd.get('bomba', [])
                
                if len(puntos_bomba_temp_vfd) >= 2 and rpm_percentage < 100:
                    # Escalar puntos de bomba según % RPM (usando leyes de afinidad)
                    factor_rpm = rpm_percentage / 100.0
                    x_bom_vfd = np.array([pt[0] * factor_rpm for pt in puntos_bomba_temp_vfd])
                    y_bom_vfd = np.array([pt[1] * (factor_rpm ** 2) for pt in puntos_bomba_temp_vfd])
                    
                    if np.all(np.isfinite(x_bom_vfd)) and np.all(np.isfinite(y_bom_vfd)):
                        ajuste_tipo_vfd = st.session_state.get('ajuste_tipo', 'Cuadrática (2do grado)')
                        grado_vfd = 1 if ajuste_tipo_vfd == "Lineal" else 2 if ajuste_tipo_vfd == "Cuadrática (2do grado)" else 3
                        coef_vfd = np.polyfit(x_bom_vfd, y_bom_vfd, grado_vfd)
                        
                        # Resolver H ≈ 0
                        if grado_vfd == 2:
                            a, b, c = coef_vfd[0], coef_vfd[1], coef_vfd[2]
                            discriminante = b**2 - 4*a*c
                            if discriminante >= 0 and a != 0:
                                q1 = (-b + np.sqrt(discriminante)) / (2*a)
                                q2 = (-b - np.sqrt(discriminante)) / (2*a)
                                q_para_h_cero_vfd = max(q1, q2) if q1 > 0 or q2 > 0 else q_max_vdf * 1.5
                            else:
                                q_para_h_cero_vfd = q_max_vdf * 1.5
                        else:
                            q_para_h_cero_vfd = -coef_vfd[-1] / coef_vfd[-2] if len(coef_vfd) >= 2 and coef_vfd[-2] != 0 else q_max_vdf * 1.5
                        
                        # Mostrar mensaje informativo
                        st.info(f"💡 **Para Allievi (método 'Curvas por Puntos'):** Para cubrir desde Q=0 hasta H≈0 a {rpm_percentage:.2f}% RPM, ajustar **Q max ≈ {q_para_h_cero_vfd:.2f} L/s**")
            except:
                pass
            
            st.markdown("---")
            
            # Actualizar el valor automático cuando cambie Q max
            if st.session_state.get("q_max_vdf_tab2", caudal_diseno) != q_max_vdf:
                st.session_state["q_max_vdf_tab2"] = q_max_vdf
                st.rerun()
            
            # Calcular caudal máximo para las tablas VFD
            # Calcular caudal máximo para las tablas VDF
            interseccion_vfd = st.session_state.get('interseccion', None)
            if interseccion_vfd:
                caudal_max_tabla_vfd = interseccion_vfd[0] * 1.3 * (rpm_percentage / 100.0)
            else:
                caudal_max_tabla_vfd = 100.0 * (rpm_percentage / 100.0)
            
            # Generar caudales para las tablas VDF usando Q min y Q max del usuario
            caudales_tabla_vfd = np.arange(q_min_vdf, q_max_vdf + paso_caudal_vdf, paso_caudal_vdf)
            
            # Crear 4 columnas para las tablas VFD
            tab_col1_vfd, tab_col2_vfd, tab_col3_vfd = st.columns([0.35, 0.35, 0.30])
            tab_col4_vfd, tab_col5_vfd, tab_col6_vfd = st.columns([0.35, 0.35, 0.30])
            
            # Tabla 1: Curva de la Bomba (H-Q) VFD
            with tab_col1_vfd:
                st.markdown(f"**Curva de la Bomba (H-Q) a {rpm_percentage:.2f}% RPM**")
                
                puntos_bomba = curva_inputs.get('bomba', [])
                
                if len(puntos_bomba) >= 2:
                    # Usar curvas originales directamente VFD
                    n_bombas = st.session_state.get('num_bombas', 1)
                    x_bom = np.array([pt[0] for pt in puntos_bomba])
                    y_bom = np.array([pt[1] for pt in puntos_bomba])
                    
                    if np.all(np.isfinite(x_bom)) and np.all(np.isfinite(y_bom)):
                        grado = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
                        coef_bom = np.polyfit(x_bom, y_bom, grado)
                        
                        # Aplicar leyes de afinidad para VFD
                        rpm_ratio = rpm_percentage / 100.0
                        caudales_vfd = caudales_tabla_vfd / rpm_ratio  # Convertir a 100% RPM
                        alturas_vfd = np.polyval(coef_bom, caudales_vfd) * (rpm_ratio ** 2)  # Aplicar ley de afinidad
                        
                        # Crear DataFrame con unidades correctas
                        unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                        unidad_display = get_display_unit_label(unidad_caudal)
                        
                        if unidad_caudal == 'm³/h':
                            caudales_display = np.round(caudales_tabla_vfd * 3.6, 3)
                        else:
                            caudales_display = np.round(caudales_tabla_vfd, 3)
                        
                        df_bomba_vfd = pd.DataFrame({
                            f'Caudal ({unidad_display})': caudales_display,
                            'Altura (m)': np.round(alturas_vfd, 3)
                        })
                        
                        st.dataframe(df_bomba_vfd, height=300, use_container_width=True)
                        
                        # Guardar para Excel
                        st.session_state['df_bomba_vfd'] = df_bomba_vfd
                    else:
                        st.warning("Datos de bomba no válidos")
                else:
                    st.info("No hay datos de bomba disponibles")
            
            # Tabla 2: Curva de Rendimiento (η-Q) VFD
            with tab_col2_vfd:
                st.markdown(f"**Curva de Rendimiento (η-Q) a {rpm_percentage:.2f}% RPM**")
                
                puntos_rendimiento = curva_inputs.get('rendimiento', [])
                
                if len(puntos_rendimiento) >= 2:
                    x_rend = np.array([pt[0] for pt in puntos_rendimiento])
                    y_rend = np.array([pt[1] for pt in puntos_rendimiento])
                    
                    if np.all(np.isfinite(x_rend)) and np.all(np.isfinite(y_rend)):
                        grado = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
                        coef_rend = np.polyfit(x_rend, y_rend, grado)
                        
                        # Aplicar leyes de afinidad para VFD
                        rpm_ratio = rpm_percentage / 100.0
                        caudales_vfd = caudales_tabla_vfd / rpm_ratio  # Convertir a 100% RPM
                        rendimientos_vfd = np.polyval(coef_rend, caudales_vfd)  # El rendimiento se mantiene aproximadamente igual
                        
                        # Crear DataFrame con unidades correctas
                        unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                        unidad_display = get_display_unit_label(unidad_caudal)
                        
                        if unidad_caudal == 'm³/h':
                            caudales_display = np.round(caudales_tabla_vfd * 3.6, 3)
                        else:
                            caudales_display = np.round(caudales_tabla_vfd, 3)
                        
                        df_rendimiento_vfd = pd.DataFrame({
                            f'Caudal ({unidad_display})': caudales_display,
                            'Rendimiento (%)': np.round(rendimientos_vfd, 3)
                        })
                        
                        st.dataframe(df_rendimiento_vfd, height=300, use_container_width=True)
                        
                        # Guardar para Excel
                        st.session_state['df_rendimiento_vfd'] = df_rendimiento_vfd
                    else:
                        st.warning("Datos de rendimiento no válidos")
                else:
                    st.info("No hay datos de rendimiento disponibles")
            
            # Tabla 3: Curva de Potencia (PBHP-Q) VFD
            with tab_col3_vfd:
                st.markdown(f"**Curva de Potencia (PBHP-Q) a {rpm_percentage:.2f}% RPM**")
                
                puntos_potencia = curva_inputs.get('potencia', [])
                
                if len(puntos_potencia) >= 2:
                    x_pot = np.array([pt[0] for pt in puntos_potencia])
                    y_pot = np.array([pt[1] for pt in puntos_potencia])
                    
                    if np.all(np.isfinite(x_pot)) and np.all(np.isfinite(y_pot)):
                        grado = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
                        coef_pot = np.polyfit(x_pot, y_pot, grado)
                        
                        # Aplicar leyes de afinidad para VFD
                        rpm_ratio = rpm_percentage / 100.0
                        caudales_vfd = caudales_tabla_vfd / rpm_ratio  # Convertir a 100% RPM
                        potencias_vfd = np.polyval(coef_pot, caudales_vfd) * (rpm_ratio ** 3)  # Aplicar ley de afinidad
                        
                        # Crear DataFrame con unidades correctas
                        unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                        unidad_display = get_display_unit_label(unidad_caudal)
                        
                        if unidad_caudal == 'm³/h':
                            caudales_display = np.round(caudales_tabla_vfd * 3.6, 3)
                        else:
                            caudales_display = np.round(caudales_tabla_vfd, 3)
                        
                        df_potencia_vfd = pd.DataFrame({
                            f'Caudal ({unidad_display})': caudales_display,
                            'Potencia (HP)': np.round(potencias_vfd, 3)
                        })
                        
                        st.dataframe(df_potencia_vfd, height=300, use_container_width=True)
                        
                        # Guardar para Excel
                        st.session_state['df_potencia_vfd'] = df_potencia_vfd
                    else:
                        st.warning("Datos de potencia no válidos")
                else:
                    st.info("No hay datos de potencia disponibles")
            
            # Tabla 4: Curva de NPSH (NPSHR-Q) VFD
            with tab_col4_vfd:
                st.markdown(f"**Curva de NPSH (NPSHR-Q) a {rpm_percentage:.2f}% RPM**")
                
                puntos_npsh = curva_inputs.get('npsh', [])
                
                if len(puntos_npsh) >= 2:
                    x_npsh = np.array([pt[0] for pt in puntos_npsh])
                    y_npsh = np.array([pt[1] for pt in puntos_npsh])
                    
                    if np.all(np.isfinite(x_npsh)) and np.all(np.isfinite(y_npsh)):
                        grado = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
                        coef_npsh = np.polyfit(x_npsh, y_npsh, grado)
                        
                        # Aplicar leyes de afinidad para VFD
                        rpm_ratio = rpm_percentage / 100.0
                        caudales_vfd = caudales_tabla_vfd / rpm_ratio  # Convertir a 100% RPM
                        npsh_vfd = np.polyval(coef_npsh, caudales_vfd) * (rpm_ratio ** 2)  # Aplicar ley de afinidad
                        
                        # Crear DataFrame con unidades correctas
                        unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                        unidad_display = get_display_unit_label(unidad_caudal)
                        
                        if unidad_caudal == 'm³/h':
                            caudales_display = np.round(caudales_tabla_vfd * 3.6, 3)
                        else:
                            caudales_display = np.round(caudales_tabla_vfd, 3)
                        
                        df_npsh_vfd = pd.DataFrame({
                            f'Caudal ({unidad_display})': caudales_display,
                            'NPSH (m)': np.round(npsh_vfd, 3)
                        })
                        
                        st.dataframe(df_npsh_vfd, height=300, use_container_width=True)
                        
                        # Guardar para Excel
                        st.session_state['df_npsh_vfd'] = df_npsh_vfd
                    else:
                        st.warning("Datos de NPSH no válidos")
                else:
                    st.info("No hay datos de NPSH disponibles")
            
            # Tabla 5: Curva del Sistema (H-Q) VFD
            with tab_col5_vfd:
                st.markdown(f"**Curva del Sistema (H-Q) a {rpm_percentage:.2f}% RPM**")
                
                # Obtener puntos del sistema desde textarea_sistema primero
                puntos_sistema_vfd = []
                unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                
                # Primero intentar leer desde textarea_sistema
                if 'textarea_sistema' in st.session_state and st.session_state['textarea_sistema']:
                    try:
                        # Procesar el contenido del textarea
                        texto_curva = st.session_state['textarea_sistema']
                        lines = [line.strip() for line in texto_curva.splitlines() if line.strip()]
                        
                        for line in lines:
                            vals = [v for v in line.replace(';', ' ').replace('\t', ' ').split() if v]
                            if len(vals) == 2:
                                try:
                                    x = float(vals[0])
                                    y = float(vals[1])
                                    
                                    # Convertir caudal a L/s para cálculos internos
                                    if unidad_caudal == 'm³/h':
                                        x = x / 3.6  # m³/h a L/s
                                    
                                    puntos_sistema_vfd.append((x, y))
                                except Exception:
                                    pass
                    except Exception as e:
                        st.warning(f"Error procesando puntos del sistema desde textarea: {e}")
                
                # Si no hay puntos en textarea, intentar desde curva_inputs
                if not puntos_sistema_vfd and 'sistema' in curva_inputs and curva_inputs['sistema']:
                    puntos_sistema_vfd = curva_inputs['sistema']
                
                # Si aún no hay puntos, calcular automáticamente
                if not puntos_sistema_vfd:
                    try:
                        # Generar caudales para calcular la curva del sistema
                        flows = np.linspace(0, 200, 20).tolist()  # 0 a 200 L/s
                        flow_unit = st.session_state.get('flow_unit', 'L/s')
                        
                        # Obtener parámetros del sistema
                        system_params = {
                            'h_estatica': st.session_state.get('h_estatica', 50.0),
                            'long_succion': st.session_state.get('long_succion', 10.0),
                            'diam_succion_m': st.session_state.get('diam_succion', 200.0) / 1000.0,
                            'C_succion': st.session_state.get('C_succion', 150),
                            'accesorios_succion': st.session_state.get('accesorios_succion', []),
                            'otras_perdidas_succion': 0.0,
                            'long_impulsion': st.session_state.get('long_impulsion', 100.0),
                            'diam_impulsion_m': st.session_state.get('diam_impulsion', 150.0) / 1000.0,
                            'C_impulsion': st.session_state.get('C_impulsion', 150),
                            'accesorios_impulsion': st.session_state.get('accesorios_impulsion', []),
                            'otras_perdidas_impulsion': 0.0
                        }
                        
                        from core.system_head import calculate_adt_for_multiple_flows
                        adt_values = calculate_adt_for_multiple_flows(flows, flow_unit, system_params)
                        
                        if adt_values:
                            puntos_sistema_vfd = [(flows[i], adt_values[i]) for i in range(len(flows)) if adt_values[i] is not None]
                        else:
                            puntos_sistema_vfd = []
                    except Exception as e:
                        st.warning(f"Error calculando curva del sistema: {e}")
                        puntos_sistema_vfd = []

                if len(puntos_sistema_vfd) >= 2:
                    x_sis = np.array([pt[0] for pt in puntos_sistema_vfd])
                    y_sis = np.array([pt[1] for pt in puntos_sistema_vfd])
                    
                    if np.all(np.isfinite(x_sis)) and np.all(np.isfinite(y_sis)):
                        # Ajustar el grado del polinomio según el número de puntos disponibles
                        grado_deseado = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
                        # El grado no puede ser mayor que (número de puntos - 1)
                        grado = min(grado_deseado, len(x_sis) - 1)
                        
                        coef_sis = np.polyfit(x_sis, y_sis, grado)
                        
                        # Calcular valores para la tabla (el sistema no cambia con VFD)
                        alturas_sistema_vfd = np.polyval(coef_sis, caudales_tabla_vfd)
                        
                        # Crear DataFrame con unidades correctas
                        unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                        unidad_display = get_display_unit_label(unidad_caudal)
                        
                        if unidad_caudal == 'm³/h':
                            caudales_display = np.round(caudales_tabla_vfd * 3.6, 3)
                        else:
                            caudales_display = np.round(caudales_tabla_vfd, 3)
                        
                        df_sistema_vfd = pd.DataFrame({
                            f'Caudal ({unidad_display})': caudales_display,
                            'Altura (m)': np.round(alturas_sistema_vfd, 3)
                        })
                        
                        st.dataframe(df_sistema_vfd, height=300, use_container_width=True)
                        
                        # Guardar para Excel
                        st.session_state['df_sistema_vfd'] = df_sistema_vfd
                    else:
                        st.warning("Datos del sistema no válidos")
                else:
                    st.info("No hay datos del sistema disponibles")
            
            # Botón único para descargar todas las tablas VFD
            st.markdown("---")
            if st.button(f"📥 Descargar Todas las Tablas {rpm_percentage:.2f}% RPM", key="download_all_vfd", type="primary"):
                try:
                    # Crear buffer para el archivo Excel
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        # Obtener información de las tablas
                        interseccion_vfd = st.session_state.get('interseccion_vfd', None)
                        punto_operacion_vfd = interseccion_vfd[0] if interseccion_vfd else 0
                        total_puntos_vfd = len(caudales_tabla_vfd)
                        rango_caudal_vfd = f"0 a {caudales_tabla_vfd[-1]:.1f} L/s"
                        
                        # Hoja H-Q (Bomba VFD)
                        if 'df_bomba_vfd' in st.session_state:
                            df_bomba_vfd = st.session_state['df_bomba_vfd'].copy()
                            # Agregar ecuación solo en la primera fila (C2)
                            if 'coef_bom_vfd' in locals():
                                df_bomba_vfd.loc[0, 'Ecuación'] = f"H = {coef_bom_vfd[0]:.6f}*Q² + {coef_bom_vfd[1]:.6f}*Q + {coef_bom_vfd[2]:.6f}" if len(coef_bom_vfd) > 2 else f"H = {coef_bom_vfd[0]:.6f}*Q + {coef_bom_vfd[1]:.6f}"
                            # Agregar información solo en la primera fila (D2)
                            df_bomba_vfd.loc[0, 'Información'] = f"Rango: {rango_caudal_vfd}, Paso: {paso_caudal_vdf} L/s, Total: {total_puntos_vfd} puntos, Punto operación: {punto_operacion_vfd:.2f} L/s, Ajuste: {ajuste_tipo}, RPM: {rpm_percentage:.2f}%"
                            df_bomba_vfd.to_excel(writer, sheet_name='H-Q', index=False)
                        
                        # Hoja Efficiency
                        if 'df_rendimiento_vfd' in st.session_state:
                            df_rend_vfd = st.session_state['df_rendimiento_vfd'].copy()
                            if 'coef_rend_vfd' in locals():
                                df_rend_vfd.loc[0, 'Ecuación'] = f"η = {coef_rend_vfd[0]:.6f}*Q² + {coef_rend_vfd[1]:.6f}*Q + {coef_rend_vfd[2]:.6f}" if len(coef_rend_vfd) > 2 else f"η = {coef_rend_vfd[0]:.6f}*Q + {coef_rend_vfd[1]:.6f}"
                            df_rend_vfd.loc[0, 'Información'] = f"Rango: {rango_caudal_vfd}, Paso: {paso_caudal_vdf} L/s, Total: {total_puntos_vfd} puntos, Punto operación: {punto_operacion_vfd:.2f} L/s, Ajuste: {ajuste_tipo}, RPM: {rpm_percentage:.2f}%"
                            df_rend_vfd.to_excel(writer, sheet_name='Efficiency', index=False)
                        
                        # Hoja Power
                        if 'df_potencia_vfd' in st.session_state:
                            df_pot_vfd = st.session_state['df_potencia_vfd'].copy()
                            if 'coef_pot_vfd' in locals():
                                df_pot_vfd.loc[0, 'Ecuación'] = f"P = {coef_pot_vfd[0]:.6f}*Q² + {coef_pot_vfd[1]:.6f}*Q + {coef_pot_vfd[2]:.6f}" if len(coef_pot_vfd) > 2 else f"P = {coef_pot_vfd[0]:.6f}*Q + {coef_pot_vfd[1]:.6f}"
                            df_pot_vfd.loc[0, 'Información'] = f"Rango: {rango_caudal_vfd}, Paso: {paso_caudal_vdf} L/s, Total: {total_puntos_vfd} puntos, Punto operación: {punto_operacion_vfd:.2f} L/s, Ajuste: {ajuste_tipo}, RPM: {rpm_percentage:.2f}%"
                            df_pot_vfd.to_excel(writer, sheet_name='Power', index=False)
                        
                        # Hoja NPSH
                        if 'df_npsh_vfd' in st.session_state:
                            df_npsh_vfd = st.session_state['df_npsh_vfd'].copy()
                            if 'coef_npsh_vfd' in locals():
                                df_npsh_vfd.loc[0, 'Ecuación'] = f"NPSH = {coef_npsh_vfd[0]:.6f}*Q² + {coef_npsh_vfd[1]:.6f}*Q + {coef_npsh_vfd[2]:.6f}" if len(coef_npsh_vfd) > 2 else f"NPSH = {coef_npsh_vfd[0]:.6f}*Q + {coef_npsh_vfd[1]:.6f}"
                            df_npsh_vfd.loc[0, 'Información'] = f"Rango: {rango_caudal_vfd}, Paso: {paso_caudal_vdf} L/s, Total: {total_puntos_vfd} puntos, Punto operación: {punto_operacion_vfd:.2f} L/s, Ajuste: {ajuste_tipo}, RPM: {rpm_percentage:.2f}%"
                            df_npsh_vfd.to_excel(writer, sheet_name='NPSH', index=False)
                        
                        # Hoja H-Q_sistema
                        if 'df_sistema_vfd' in st.session_state:
                            df_sis_vfd = st.session_state['df_sistema_vfd'].copy()
                            if 'coef_sis_vfd' in locals():
                                df_sis_vfd.loc[0, 'Ecuación'] = f"H = {coef_sis_vfd[0]:.6f}*Q² + {coef_sis_vfd[1]:.6f}*Q + {coef_sis_vfd[2]:.6f}" if len(coef_sis_vfd) > 2 else f"H = {coef_sis_vfd[0]:.6f}*Q + {coef_sis_vfd[1]:.6f}"
                            df_sis_vfd.loc[0, 'Información'] = f"Rango: {rango_caudal_vfd}, Paso: {paso_caudal_vdf} L/s, Total: {total_puntos_vfd} puntos, Punto operación: {punto_operacion_vfd:.2f} L/s, Ajuste: {ajuste_tipo}, RPM: {rpm_percentage:.2f}%"
                            df_sis_vfd.to_excel(writer, sheet_name='H-Q_sistema', index=False)
                    
                    # Preparar archivo para descarga
                    output.seek(0)
                    excel_data = output.getvalue()
                    
                    # Descargar archivo
                    st.download_button(
                        label=f"💾 Descargar Curvas_Bomba_{rpm_percentage:.2f}RPM.xlsx",
                        data=excel_data,
                        file_name=f"Curvas_Bomba_{rpm_percentage:.2f}RPM.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_curvas_vfd"
                    )
                    
                    st.success("✅ Archivo Excel generado exitosamente")
                    
                except Exception as e:
                    st.error(f"❌ Error al generar archivo Excel: {e}")
    
    


