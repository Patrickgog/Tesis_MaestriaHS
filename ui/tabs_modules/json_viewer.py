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



def render_json_tab():
    """Renderiza la pestaña de resumen del proyecto con todos los datos y resultados"""
    # Obtener el nombre del proyecto
    nombre_proyecto = st.session_state.get('proyecto', 'Proyecto')
    if not nombre_proyecto or nombre_proyecto.strip() == '':
        nombre_proyecto = 'Proyecto'
    
    st.title(f"📋 Resumen del Proyecto: {nombre_proyecto}")
    st.markdown("**Datos del Proyecto y Resultados**")
    
    # Función helper para generar tabla de accesorios en Markdown
    def generar_tabla_accesorios_markdown(accesorios_data, titulo):
        if not accesorios_data:
            return f"**{titulo}**: No hay accesorios disponibles."
        
        tabla_md = f"**{titulo}**\n\n"
        tabla_md += "| Tipo | Cantidad | K | Lc/D |\n"
        tabla_md += "|------|----------|---|------|\n"
        
        for acc in accesorios_data:
            tipo = acc.get('tipo', 'N/A')
            cantidad = acc.get('cantidad', 'N/A')
            k = acc.get('k', 'N/A')
            lc_d = acc.get('lc_d', 'N/A')
            tabla_md += f"| {tipo} | {cantidad} | {k} | {lc_d} |\n"
        
        return tabla_md
    
    # Crear sub-pestañas
    json_project_tab = st.tabs(["📄 Resumen Proyecto"])[0]
    
    with json_project_tab:
        st.header("📄 Datos del Proyecto")
        
        # Construir project_data desde session_state en lugar de cargar desde archivo
        # Esto evita problemas de rutas y usa los datos actuales de la sesión
        try:
            # Construir diccionario project_data desde session_state
            project_data = {
                'proyecto': st.session_state.get('proyecto', 'N/A'),
                'diseno': st.session_state.get('diseno', 'N/A'),
                'caudal_diseno_lps': st.session_state.get('caudal_lps', 0),
                'elevacion_sitio': st.session_state.get('elevacion_sitio', 0),
                'altura_succion': st.session_state.get('altura_succion_input', 0),
                'altura_descarga': st.session_state.get('altura_descarga', 0),
                'num_bombas_paralelo': st.session_state.get('num_bombas', 1),
                'bomba_inundada': st.session_state.get('bomba_inundada', False),
                'temperatura': st.session_state.get('temp_liquido', st.session_state.get('temperatura_c', 20)),
                'densidad_liquido': st.session_state.get('densidad_liquido', 1.0),
                'presion_vapor_calculada': st.session_state.get('presion_vapor_calculada', 0),
                'presion_barometrica_calculada': st.session_state.get('presion_barometrica_calculada', 10.33),
                'succion': {
                    'longitud': st.session_state.get('long_succion', 0),
                    'material': st.session_state.get('mat_succion', 'N/A'),
                    'diametro_interno': st.session_state.get('diam_succion_mm', 0),
                    'velocidad': st.session_state.get('velocidad_succion', 0),
                    'perdida_primaria': st.session_state.get('hf_primaria_succion', 0),
                    'perdida_secundaria': st.session_state.get('hf_secundaria_succion', 0),
                    'long_equiv_accesorios': st.session_state.get('le_total_succion', 0),
                    'perdida_total': st.session_state.get('perdida_total_succion', 0),
                    'altura_dinamica': st.session_state.get('altura_dinamica_succion', 0),
                },
                'impulsion': {
                    'longitud': st.session_state.get('long_impulsion', 0),
                    'material': st.session_state.get('mat_impulsion', 'N/A'),
                    'diametro_interno': st.session_state.get('diam_impulsion_mm', 0),
                    'velocidad': st.session_state.get('velocidad_impulsion', 0),
                    'perdida_primaria': st.session_state.get('hf_primaria_impulsion', 0),
                    'perdida_secundaria': st.session_state.get('hf_secundaria_impulsion', 0),
                    'long_equiv_accesorios': st.session_state.get('le_total_impulsion', 0),
                    'perdida_total': st.session_state.get('perdida_total_impulsion', 0),
                    'altura_dinamica': st.session_state.get('altura_dinamica_impulsion', 0),
                },
                'accesorios_succion': st.session_state.get('accesorios_succion', []),
                'accesorios_impulsion': st.session_state.get('accesorios_impulsion', []),
                'curva_inputs': st.session_state.get('curva_inputs', {}),
                'curvas_texto': {
                    'sistema': st.session_state.get('textarea_sistema', ''),
                    'bomba': st.session_state.get('textarea_bomba', ''),
                    'rendimiento': st.session_state.get('textarea_rendimiento', ''),
                    'potencia': st.session_state.get('textarea_potencia', ''),
                    'npsh': st.session_state.get('textarea_npsh', ''),
                },
                'npsh': {
                    'disponible': st.session_state.get('npshd_mca', st.session_state.get('npshd', 0)),
                    'requerido': st.session_state.get('npsh_requerido', 0),
                    'margen': st.session_state.get('npsh_margen', 0),
                },
                'motor_bomba': {
                    'eficiencia_bomba': st.session_state.get('eficiencia_operacion', 0),
                    'factor_seguridad': 1.15,
                    'potencia_hidraulica_kw': st.session_state.get('potencia_hidraulica_kw', 0),
                    'potencia_hidraulica_hp': st.session_state.get('potencia_hidraulica_hp', 0),
                    'potencia_motor_final_kw': st.session_state.get('potencia_motor_final_kw', 0),
                    'potencia_motor_final_hp': st.session_state.get('potencia_motor_final_hp', 0),
                    'motor_seleccionado': st.session_state.get('motor_seleccionado', {}),
                },
                'resumen': {
                    'altura_estatica_total': st.session_state.get('altura_estatica_total', 0),
                    'perdidas_totales': st.session_state.get('perdidas_totales_sistema', 0),
                    'altura_dinamica_total': st.session_state.get('adt_total', 0),
                    'caudal_diseno': st.session_state.get('caudal_lps', 0),
                    'caudal_diseno_m3h': st.session_state.get('caudal_m3h', 0),
                    'num_bombas': st.session_state.get('num_bombas', 1),
                    'caudal_nominal_vdf': st.session_state.get('caudal_nominal', 0),
                },
                'punto_operacion': {
                    'caudal': st.session_state.get('caudal_operacion', 0),
                    'altura': st.session_state.get('altura_operacion', 0),
                    'eficiencia': st.session_state.get('eficiencia_operacion', 0),
                    'potencia': st.session_state.get('potencia_operacion', 0),
                },
                # Análisis VFD
                'vfd': {
                    'rpm_percentage': st.session_state.get('rpm_percentage', 100),
                },
                'analisis_vdf': {
                    'caudal_nominal_vdf': st.session_state.get('caudal_nominal', 0),
                    'caudal_diseno_lps': st.session_state.get('caudal_lps', 0),
                    'potencia_ajustada': st.session_state.get('potencia_ajustada', 0),
                    'eficiencia_ajustada': st.session_state.get('eficiencia_ajustada', 0),
                    'rpm_porcentaje': st.session_state.get('rpm_percentage', 100),
                    'eficiencia_operacion': st.session_state.get('eficiencia_operacion', 0),
                    'interseccion_vfd': st.session_state.get('interseccion_vfd', [0, 0]),
                },
                # Bomba seleccionada
                'bomba_seleccionada': {
                    'nombre': st.session_state.get('bomba_nombre', 'N/A'),
                    'url': st.session_state.get('bomba_url', ''),
                    'descripcion': st.session_state.get('bomba_descripcion', 'N/A'),
                },
            }
            
            # Función helper para convertir DataFrame al formato esperado por tablas_graficos
            def df_to_table_format(df_key):
                df = st.session_state.get(df_key)
                if df is not None and hasattr(df, 'to_dict') and hasattr(df, 'columns'):
                    return {
                        'data': df.to_dict('records'),
                        'columns': df.columns.tolist()
                    }
                return None
            
            # Agregar tablas_graficos con el formato esperado por la sección 8
            project_data['tablas_graficos'] = {
                'tablas_100_rpm': {
                    'df_bomba_100': df_to_table_format('df_bomba_100'),
                    'df_sistema_100': df_to_table_format('df_sistema_100'),
                    'df_rendimiento_100': df_to_table_format('df_rendimiento_100'),
                    'df_potencia_100': df_to_table_format('df_potencia_100'),
                    'df_npsh_100': df_to_table_format('df_npsh_100'),
                    'nota': 'Tablas a 100% RPM'
                },
                'tablas_vfd_rpm': {
                    'df_bomba_vfd': df_to_table_format('df_bomba_vfd'),
                    'df_sistema_vfd': df_to_table_format('df_sistema_vfd'),
                    'df_rendimiento_vfd': df_to_table_format('df_rendimiento_vfd'),
                    'df_potencia_vfd': df_to_table_format('df_potencia_vfd'),
                    'df_npsh_vfd': df_to_table_format('df_npsh_vfd'),
                    'nota': f"Tablas a {st.session_state.get('rpm_percentage', 100)}% RPM"
                }
            }
            
            # PROYECTO Y DISEÑO
            st.markdown("### 📋 PROYECTO")
            st.markdown(f"{project_data.get('proyecto', 'N/A')}")
            
            st.markdown("### 👨‍💻 DISEÑO")
            st.markdown(f"{project_data.get('diseno', 'N/A')}")
            
            # Separador horizontal
            st.markdown("---")
            
            # CONFIGURACIÓN DE PARÁMETROS DEL SISTEMA
            
            # Crear 3 columnas: 33% - 33% - 33% para las primeras 3 secciones
            col1, col2, col3 = st.columns([0.33, 0.33, 0.33])
            
            # --- COLUMNA 1: Condiciones de Operación ---
            with col1:
                st.markdown("### 1. Condiciones de Operación")
                # Tabla de Parámetros Principales
                st.markdown("#### Parámetros Principales")
                
                caudal = project_data.get('caudal_diseno_lps', 'N/A')
                if caudal != 'N/A':
                    caudal = f"{float(caudal):.2f}"
                
                elevacion = project_data.get('elevacion_sitio', 'N/A')
                if elevacion != 'N/A':
                    elevacion = f"{float(elevacion):.2f}"
                
                altura_succion = project_data.get('altura_succion', 'N/A')
                if altura_succion != 'N/A':
                    altura_succion = f"{float(altura_succion):.2f}"
                
                altura_descarga = project_data.get('altura_descarga', 'N/A')
                if altura_descarga != 'N/A':
                    altura_descarga = f"{float(altura_descarga):.2f}"
                
                estado_bomba = "Sí" if project_data.get('bomba_inundada', False) else "No"
                
                tabla_parametros_html = f"""
                <table style="width: 100%; border-collapse: collapse; margin: 10px 0; font-family: Arial, sans-serif;">
                <thead>
                    <tr style="background-color: #f5f5f5;">
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Parámetro</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Dato</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Unidad</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Caudal de Diseño</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{caudal}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">L/s</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Elevación del Sitio</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{elevacion}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Altura de Succión</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{altura_succion}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Altura de Descarga</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{altura_descarga}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Número de Bombas</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{project_data.get('num_bombas_paralelo', 'N/A')}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">-</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Bomba Inundada</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{estado_bomba}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">-</td>
                    </tr>
                </tbody>
                </table>
                """
                
                st.markdown(tabla_parametros_html, unsafe_allow_html=True)
                
                # Tabla de Condiciones del Fluido
                st.markdown("#### Condiciones del Fluido")
                
                temperatura = project_data.get('temperatura', 'N/A')
                if temperatura != 'N/A':
                    temperatura = f"{float(temperatura):.2f}"
                
                densidad = project_data.get('densidad_liquido', 'N/A')
                if densidad != 'N/A':
                    densidad = f"{float(densidad):.2f}"
                
                presion_vapor = project_data.get('presion_vapor_calculada', 'N/A')
                if presion_vapor != 'N/A':
                    presion_vapor = f"{float(presion_vapor):.2f}"
                
                presion_barometrica = project_data.get('presion_barometrica_calculada', 'N/A')
                if presion_barometrica != 'N/A':
                    presion_barometrica = f"{float(presion_barometrica):.2f}"
                
                tabla_fluido_html = f"""
                <table style="width: 100%; border-collapse: collapse; margin: 10px 0; font-family: Arial, sans-serif;">
                <thead>
                    <tr style="background-color: #f5f5f5;">
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Condición</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Dato</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Unidad</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Temperatura</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{temperatura}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">°C</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Densidad</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{densidad}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">g/cm³</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Presión de Vapor</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{presion_vapor}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">m.c.a.</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Presión Barométrica</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{presion_barometrica}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">m.c.a.</td>
                    </tr>
                </tbody>
                </table>
                """
                
                st.markdown(tabla_fluido_html, unsafe_allow_html=True)
                
                # Método de Cálculo de Pérdidas
                st.markdown("#### Método de Cálculo de Pérdidas")
                
                metodo_calculo = st.session_state.get('metodo_calculo', 'Hazen-Williams')
                
                tabla_metodo_html = f"""
                <table style="width: 100%; border-collapse: collapse; margin: 10px 0; font-family: Arial, sans-serif;">
                <thead>
                    <tr style="background-color: #f5f5f5;">
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Parámetro</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Valor</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Método utilizado</td>
                        <td style="border: 1px solid #ddd; padding: 10px; font-weight: bold; color: {'#007bff' if metodo_calculo == 'Darcy-Weisbach' else '#28a745'};">{metodo_calculo}</td>
                    </tr>
                </tbody>
                </table>
                """
                
                st.markdown(tabla_metodo_html, unsafe_allow_html=True)
                
                # Si es Darcy-Weisbach, mostrar parámetros adicionales
                if metodo_calculo == 'Darcy-Weisbach':
                    det_suc = st.session_state.get('detalles_calc_succion_primaria', {})
                    det_imp = st.session_state.get('detalles_calc_impulsion_primaria', {})
                    
                    if det_suc and det_suc.get('metodo') == 'Darcy-Weisbach':
                        st.markdown("**📘 Succión (Darcy-Weisbach)**")
                        st.markdown(f"- Reynolds: {det_suc.get('Re', 0):.0f}")
                        st.markdown(f"- Régimen: {det_suc.get('regimen', 'N/A')}")
                        st.markdown(f"- Factor f: {det_suc.get('f', 0):.6f}")
                    
                    if det_imp and det_imp.get('metodo') == 'Darcy-Weisbach':
                        st.markdown("**📕 Impulsión (Darcy-Weisbach)**")
                        st.markdown(f"- Reynolds: {det_imp.get('Re', 0):.0f}")
                        st.markdown(f"- Régimen: {det_imp.get('regimen', 'N/A')}")
                        st.markdown(f"- Factor f: {det_imp.get('f', 0):.6f}")
            
            # --- COLUMNA 2: Tubería y Accesorios de Succión ---
            with col2:
                st.markdown("### 2. Tubería y Accesorios de Succión")
                if 'succion' in project_data:
                    succion = project_data['succion']
                    
                    # Tabla de Resultados Hidráulicos
                    st.markdown("#### Resultados Hidráulicos")
                    
                    velocidad = succion.get('velocidad', 'N/A')
                    if velocidad != 'N/A':
                        velocidad = f"{float(velocidad):.2f}"
                    
                    perdida_primaria = succion.get('perdida_primaria', 'N/A')
                    if perdida_primaria != 'N/A':
                        perdida_primaria = f"{float(perdida_primaria):.2f}"
                    
                    perdida_secundaria = succion.get('perdida_secundaria', 'N/A')
                    if perdida_secundaria != 'N/A':
                        perdida_secundaria = f"{float(perdida_secundaria):.2f}"
                    
                    long_equiv = succion.get('long_equiv_accesorios', 'N/A')
                    if long_equiv != 'N/A':
                        long_equiv = f"{float(long_equiv):.2f}"
                    
                    perdida_total = succion.get('perdida_total', 'N/A')
                    if perdida_total != 'N/A':
                        perdida_total = f"{float(perdida_total):.2f}"
                    
                    altura_dinamica = succion.get('altura_dinamica', 'N/A')
                    if altura_dinamica != 'N/A':
                        altura_dinamica = f"{float(altura_dinamica):.2f}"
                    
                    tabla_hidraulicos_html = f"""
                    <table style="width: 100%; border-collapse: collapse; margin: 10px 0; font-family: Arial, sans-serif;">
                    <thead>
                        <tr style="background-color: #f5f5f5;">
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Parámetro</th>
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Valor</th>
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Unidad</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Velocidad</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{velocidad}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m/s</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Pérdida Primaria</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{perdida_primaria}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Pérdida Secundaria</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{perdida_secundaria}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Longitud Equivalente Accesorios</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{long_equiv}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Pérdida Total</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{perdida_total}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Altura Dinámica</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{altura_dinamica}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                        </tr>
                    </tbody>
                    </table>
                    """
                    
                    st.markdown(tabla_hidraulicos_html, unsafe_allow_html=True)
                
                # Accesorios de Succión en tabla
                if isinstance(project_data, dict) and 'accesorios_succion' in project_data:
                    accesorios_succion = project_data['accesorios_succion']
                    tabla_succion_md = generar_tabla_accesorios_markdown(accesorios_succion, "Accesorios de Succión")
                    st.markdown(tabla_succion_md)
            
            # --- COLUMNA 3: Tubería y Accesorios de Impulsión ---
            with col3:
                st.markdown("### 3. Tubería y Accesorios de Impulsión")
                if 'impulsion' in project_data:
                    impulsion = project_data['impulsion']
                    
                    # Tabla de Resultados Hidráulicos
                    st.markdown("#### Resultados Hidráulicos")
                    
                    velocidad = impulsion.get('velocidad', 'N/A')
                    if velocidad != 'N/A':
                        velocidad = f"{float(velocidad):.2f}"
                    
                    perdida_primaria = impulsion.get('perdida_primaria', 'N/A')
                    if perdida_primaria != 'N/A':
                        perdida_primaria = f"{float(perdida_primaria):.2f}"
                    
                    perdida_secundaria = impulsion.get('perdida_secundaria', 'N/A')
                    if perdida_secundaria != 'N/A':
                        perdida_secundaria = f"{float(perdida_secundaria):.2f}"
                    
                    long_equiv = impulsion.get('long_equiv_accesorios', 'N/A')
                    if long_equiv != 'N/A':
                        long_equiv = f"{float(long_equiv):.2f}"
                    
                    perdida_total = impulsion.get('perdida_total', 'N/A')
                    if perdida_total != 'N/A':
                        perdida_total = f"{float(perdida_total):.2f}"
                    
                    altura_dinamica = impulsion.get('altura_dinamica', 'N/A')
                    if altura_dinamica != 'N/A':
                        altura_dinamica = f"{float(altura_dinamica):.2f}"
                    
                    tabla_hidraulicos_impulsion_html = f"""
                    <table style="width: 100%; border-collapse: collapse; margin: 10px 0; font-family: Arial, sans-serif;">
                    <thead>
                        <tr style="background-color: #f5f5f5;">
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Parámetro</th>
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Valor</th>
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Unidad</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Velocidad</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{velocidad}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m/s</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Pérdida Primaria</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{perdida_primaria}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Pérdida Secundaria</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{perdida_secundaria}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Longitud Equivalente Accesorios</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{long_equiv}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Pérdida Total</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{perdida_total}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Altura Dinámica</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{altura_dinamica}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                        </tr>
                    </tbody>
                    </table>
                    """
                    
                    st.markdown(tabla_hidraulicos_impulsion_html, unsafe_allow_html=True)
                
                # Accesorios de Impulsión en tabla
                if isinstance(project_data, dict) and 'accesorios_impulsion' in project_data:
                    accesorios_impulsion = project_data['accesorios_impulsion']
                    tabla_impulsion_md = generar_tabla_accesorios_markdown(accesorios_impulsion, "Accesorios de Impulsión")
                    st.markdown(tabla_impulsion_md)
            
            # Separador horizontal
            st.markdown("---")
            
            # 4. Ajuste de Curvas Características (3 puntos)
            st.markdown("### 4. Ajuste de Curvas Características (3 puntos)")
            
            if 'curva_inputs' in project_data:
                curva_inputs = project_data['curva_inputs']
                
                # Crear tabla HTML con todas las curvas en fila (incluyendo Sistema)
                tabla_html = """
                <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                <thead>
                    <tr style="background-color: #f0f0f0;">
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva Bomba (H-Q)</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva Rendimiento (η-Q)</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva Potencia (PBHP-Q)</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva NPSH (NPSHR-Q)</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva del Sistema (H-Q)</th>
                    </tr>
                    <tr style="background-color: #f8f8f8;">
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Q (L/s) | H (m)</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Q (L/s) | η (%)</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Q (L/s) | P (HP)</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Q (L/s) | NPSH (m)</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Q (L/s) | H (m)</th>
                    </tr>
                </thead>
                <tbody>
                """
                
                # Obtener datos de todas las curvas
                bomba_data = curva_inputs.get('bomba', [])
                rendimiento_data = curva_inputs.get('rendimiento', [])
                potencia_data = curva_inputs.get('potencia', [])
                npsh_data = curva_inputs.get('npsh', [])
                
                # Obtener datos del sistema desde curvas_texto
                sistema_data = []
                if 'curvas_texto' in project_data and 'sistema' in project_data['curvas_texto']:
                    sistema_texto = project_data['curvas_texto']['sistema']
                    for linea in sistema_texto.split('\n'):
                        if linea.strip():
                            partes = linea.strip().split()
                            if len(partes) >= 2:
                                sistema_data.append([float(partes[0]), float(partes[1])])
                
                # Determinar el número máximo de filas
                max_rows = max(len(bomba_data), len(rendimiento_data), len(potencia_data), len(npsh_data), len(sistema_data))
                
                for i in range(max_rows):
                    tabla_html += "<tr>"
                    
                    # Curva Bomba
                    if i < len(bomba_data):
                        tabla_html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{bomba_data[i][0]:.2f} | {bomba_data[i][1]:.2f}</td>'
                    else:
                        tabla_html += '<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">-</td>'
                    
                    # Curva Rendimiento
                    if i < len(rendimiento_data):
                        tabla_html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{rendimiento_data[i][0]:.2f} | {rendimiento_data[i][1]:.2f}</td>'
                    else:
                        tabla_html += '<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">-</td>'
                    
                    # Curva Potencia
                    if i < len(potencia_data):
                        tabla_html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{potencia_data[i][0]:.2f} | {potencia_data[i][1]:.2f}</td>'
                    else:
                        tabla_html += '<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">-</td>'
                    
                    # Curva NPSH
                    if i < len(npsh_data):
                        tabla_html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{npsh_data[i][0]:.2f} | {npsh_data[i][1]:.2f}</td>'
                    else:
                        tabla_html += '<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">-</td>'
                    
                    # Curva del Sistema
                    if i < len(sistema_data):
                        tabla_html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{sistema_data[i][0]:.2f} | {sistema_data[i][1]:.2f}</td>'
                    else:
                        tabla_html += '<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">-</td>'
                    
                    tabla_html += "</tr>"
                
                tabla_html += "</tbody></table>"
                st.markdown(tabla_html, unsafe_allow_html=True)
                
                # La tabla del Sistema ya está incluida en la tabla HTML horizontal arriba
            
            # Separador horizontal
            st.markdown("---")
            
            # 5. Resultados de Cálculos Hidráulicos
            st.markdown("### 5. Resultados de Cálculos Hidráulicos")
            
            # Crear 3 columnas: 33% - 33% - 33%
            col1, col2, col3 = st.columns([0.33, 0.33, 0.33])
            
            with col1:
                # Datos de NPSH
                st.markdown("#### Datos de NPSH")
                
                presion_barometrica = project_data.get('presion_barometrica_calculada', 'N/A')
                if presion_barometrica != 'N/A':
                    presion_barometrica = f"{float(presion_barometrica):.2f}"
                
                elevacion = project_data.get('elevacion_sitio', 'N/A')
                if elevacion != 'N/A':
                    elevacion = f"{float(elevacion):.2f}"
                
                perdida_succion = project_data.get('succion', {}).get('perdida_total', 'N/A')
                if perdida_succion != 'N/A':
                    perdida_succion = f"{float(perdida_succion):.2f}"
                
                presion_vapor = project_data.get('presion_vapor_calculada', 'N/A')
                if presion_vapor != 'N/A':
                    presion_vapor = f"{float(presion_vapor):.2f}"
                
                temperatura = project_data.get('temperatura', 'N/A')
                if temperatura != 'N/A':
                    temperatura = f"{float(temperatura):.2f}"
                
                altura_succion = project_data.get('altura_succion', 'N/A')
                if altura_succion != 'N/A':
                    altura_succion = f"{float(altura_succion):.2f}"
                
                # Preparar datos de NPSH
                npsh_disponible = 'N/A'
                npsh_requerido = 'N/A'
                margen_npsh = 'N/A'
                
                if 'npsh' in project_data:
                    npsh = project_data['npsh']
                    npsh_disponible = npsh.get('disponible', 'N/A')
                    if npsh_disponible != 'N/A':
                        npsh_disponible = f"{float(npsh_disponible):.2f}"
                    
                    npsh_requerido = npsh.get('requerido', 'N/A')
                    if npsh_requerido != 'N/A':
                        npsh_requerido = f"{float(npsh_requerido):.2f}"
                    
                    margen_npsh = npsh.get('margen', 'N/A')
                    if margen_npsh != 'N/A':
                        margen_npsh = f"{float(margen_npsh):.2f}"
                
                tabla_npsh_html = f"""
                <table style="width: 100%; border-collapse: collapse; margin: 10px 0; font-family: Arial, sans-serif;">
                <thead>
                    <tr style="background-color: #f5f5f5;">
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Parámetro</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Valor</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Unidad</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Presión Barométrica</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{presion_barometrica}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">m.c.a.</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Elevación</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{elevacion}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Pérdida en la Succión</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{perdida_succion}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">m.c.a.</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Presión de Vapor</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{presion_vapor}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">m.c.a.</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Temperatura</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{temperatura}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">°C</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Altura de Succión</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{altura_succion}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">m.c.a.</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">NPSH Disponible</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{npsh_disponible}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">m.c.a.</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">NPSH Requerido</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{npsh_requerido}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">m.c.a.</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 10px;">Margen NPSH</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">{margen_npsh}</td>
                        <td style="border: 1px solid #ddd; padding: 10px;">m.c.a.</td>
                    </tr>
                </tbody>
                </table>
                """
                
                st.markdown(tabla_npsh_html, unsafe_allow_html=True)
            
            with col2:
                # Motor de la Bomba
                st.markdown("#### Motor de la Bomba")
                if 'motor_bomba' in project_data:
                    motor_bomba = project_data['motor_bomba']
                    
                    # Buscar eficiencia en motor_seleccionado
                    eficiencia = 'N/A'
                    if 'motor_seleccionado' in motor_bomba:
                        eficiencia = motor_bomba['motor_seleccionado'].get('eficiencia_porcentaje', 'N/A')
                    
                    if eficiencia != 'N/A':
                        eficiencia = f"{float(eficiencia):.2f}"
                    
                    # Factor de seguridad
                    factor_seguridad = motor_bomba.get('factor_seguridad', 'N/A')
                    if factor_seguridad != 'N/A':
                        factor_seguridad = f"{float(factor_seguridad):.2f}"
                    
                    potencia_hidraulica_kw = motor_bomba.get('potencia_hidraulica_kw', 'N/A')
                    if potencia_hidraulica_kw != 'N/A':
                        potencia_hidraulica_kw = f"{float(potencia_hidraulica_kw):.2f}"
                    potencia_hidraulica_hp = motor_bomba.get('potencia_hidraulica_hp', 'N/A')
                    if potencia_hidraulica_hp != 'N/A':
                        potencia_hidraulica_hp = f"{float(potencia_hidraulica_hp):.2f}"
                    
                    potencia_motor_kw = motor_bomba.get('potencia_motor_final_kw', 'N/A')
                    if potencia_motor_kw != 'N/A':
                        potencia_motor_kw = f"{float(potencia_motor_kw):.2f}"
                    potencia_motor_hp = motor_bomba.get('potencia_motor_final_hp', 'N/A')
                    if potencia_motor_hp != 'N/A':
                        potencia_motor_hp = f"{float(potencia_motor_hp):.2f}"
                    
                    tabla_motor_html = f"""
                    <table style="width: 100%; border-collapse: collapse; margin: 10px 0; font-family: Arial, sans-serif;">
                    <thead>
                        <tr style="background-color: #f5f5f5;">
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Parámetro</th>
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Valor</th>
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Unidad</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Eficiencia de la bomba</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{eficiencia}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">%</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Factor de seguridad</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{factor_seguridad}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">-</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Potencia Hidráulica</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{potencia_hidraulica_kw} kW ({potencia_hidraulica_hp} HP)</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">kW/HP</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Potencia del Motor</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{potencia_motor_kw} kW ({potencia_motor_hp} HP)</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">kW/HP</td>
                        </tr>
                    </tbody>
                    </table>
                    """
                    
                    st.markdown(tabla_motor_html, unsafe_allow_html=True)
            
            with col3:
                # Motor Estándar Seleccionado
                st.markdown("#### 🔧 Motor Estándar Seleccionado")
                if 'motor_bomba' in project_data and 'motor_seleccionado' in project_data['motor_bomba']:
                    motor_sel = project_data['motor_bomba']['motor_seleccionado']
                    
                    id_motor = motor_sel.get('id', 'N/A')
                    potencia_hp = motor_sel.get('potencia_hp', 'N/A')
                    potencia_kw = motor_sel.get('potencia_kw', 'N/A')
                    rpm = motor_sel.get('rpm_estandar', 'N/A')
                    tension = motor_sel.get('tension', 'N/A')
                    eficiencia = motor_sel.get('eficiencia_porcentaje', 'N/A')
                    if eficiencia != 'N/A':
                        eficiencia = f"{float(eficiencia):.2f}"
                    factor_potencia = motor_sel.get('factor_potencia', 'N/A')
                    if factor_potencia != 'N/A':
                        factor_potencia = f"{float(factor_potencia):.2f}"
                    
                    tabla_motor_estandar_html = f"""
                    <table style="width: 100%; border-collapse: collapse; margin: 10px 0; font-family: Arial, sans-serif;">
                    <thead>
                        <tr style="background-color: #f5f5f5;">
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Parámetro</th>
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Valor</th>
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Unidad</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">ID</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{id_motor}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">-</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Potencia</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{potencia_hp} HP ({potencia_kw} kW)</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">HP/kW</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">RPM</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{rpm}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">rpm</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Tensión</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{tension}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">V</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Eficiencia</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{eficiencia}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">%</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Factor de Potencia</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{factor_potencia}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">-</td>
                        </tr>
                    </tbody>
                    </table>
                    """
                    
                    st.markdown(tabla_motor_estandar_html, unsafe_allow_html=True)
            
            # Separador para nueva subsección
            st.markdown("---")
            
            # Resumen del Sistema (fuera de las columnas anteriores)
            st.markdown("#### 📊 Resumen del Sistema")
            
            # Crear 3 columnas: 33% - 33% - 33%
            col_res1, col_res2, col_res3 = st.columns([0.33, 0.33, 0.33])
            
            with col_res1:
                if 'resumen' in project_data:
                    resumen = project_data['resumen']
                    
                    altura_estatica = resumen.get('altura_estatica_total', 'N/A')
                    if altura_estatica != 'N/A':
                        altura_estatica = f"{float(altura_estatica):.2f}"
                    
                    perdidas_totales = resumen.get('perdidas_totales', 'N/A')
                    if perdidas_totales != 'N/A':
                        perdidas_totales = f"{float(perdidas_totales):.2f}"
                    
                    adt = resumen.get('altura_dinamica_total', 'N/A')
                    if adt != 'N/A':
                        adt = f"{float(adt):.2f}"
                    
                    caudal_diseno = resumen.get('caudal_diseno', 'N/A')
                    if caudal_diseno != 'N/A':
                        caudal_diseno = f"{float(caudal_diseno):.2f}"
                    
                    caudal_m3h = resumen.get('caudal_diseno_m3h', 'N/A')
                    if caudal_m3h != 'N/A':
                        caudal_m3h = f"{float(caudal_m3h):.2f}"
                    
                    num_bombas = resumen.get('num_bombas', 'N/A')
                    caudal_vfd = resumen.get('caudal_nominal_vdf', resumen.get('caudal_diseno', 'N/A'))
                    if caudal_vfd != 'N/A':
                        caudal_vfd = f"{float(caudal_vfd):.2f}"
                    nota_vfd = resumen.get('nota_vfd', 'N/A')
                    
                    tabla_resumen_html = f"""
                    <table style="width: 100%; border-collapse: collapse; margin: 10px 0; font-family: Arial, sans-serif;">
                    <thead>
                        <tr style="background-color: #f5f5f5;">
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Parámetro</th>
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Valor</th>
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Unidad</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Altura Estática Total</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{altura_estatica}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Pérdidas Totales</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{perdidas_totales}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">🎯 Altura Dinámica Total (ADT)</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{adt}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Caudal de Diseño</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{caudal_diseno}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">L/s</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Caudal de Diseño</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{caudal_m3h}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m³/h</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Número de Bombas</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{num_bombas}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">-</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Caudal Nominal VFD</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{caudal_vfd}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">L/s</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Nota VFD</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{nota_vfd}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">-</td>
                        </tr>
                    </tbody>
                    </table>
                    """
                    
                    st.markdown(tabla_resumen_html, unsafe_allow_html=True)
            
            # --- COLUMNA 2: Punto de Operación ---
            with col_res2:
                st.markdown("#### 🎯 Punto de Operación")
                if 'punto_operacion' in project_data:
                    punto_op = project_data['punto_operacion']
                    
                    caudal_op = punto_op.get('caudal', 'N/A')
                    if caudal_op != 'N/A':
                        caudal_op = f"{float(caudal_op):.2f}"
                    
                    altura_op = punto_op.get('altura', 'N/A')
                    if altura_op != 'N/A':
                        altura_op = f"{float(altura_op):.2f}"
                    
                    eficiencia_op = punto_op.get('eficiencia', 'N/A')
                    if eficiencia_op != 'N/A':
                        eficiencia_op = f"{float(eficiencia_op):.2f}"
                    
                    potencia_op = punto_op.get('potencia', 'N/A')
                    if potencia_op != 'N/A':
                        potencia_op = f"{float(potencia_op):.2f}"
                    
                    tabla_punto_op_html = f"""
                    <table style="width: 100%; border-collapse: collapse; margin: 10px 0; font-family: Arial, sans-serif;">
                    <thead>
                        <tr style="background-color: #f5f5f5;">
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Parámetro</th>
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Valor</th>
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Unidad</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Caudal</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{caudal_op}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">L/s</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Altura</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{altura_op}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">m</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Eficiencia</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{eficiencia_op}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">%</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Potencia</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{potencia_op}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">HP</td>
                        </tr>
                    </tbody>
                    </table>
                    """
                    
                    st.markdown(tabla_punto_op_html, unsafe_allow_html=True)
            
            # --- COLUMNA 3: Análisis VFD ---
            with col_res3:
                st.markdown("#### 🔄 Análisis VFD")
                if 'analisis_vdf' in project_data:
                    vdf = project_data['analisis_vdf']
                    
                    caudal_nominal_vdf = vdf.get('caudal_nominal_vdf', 'N/A')
                    if caudal_nominal_vdf != 'N/A':
                        caudal_nominal_vdf = f"{float(caudal_nominal_vdf):.2f}"
                    
                    caudal_diseno_lps = vdf.get('caudal_diseno_lps', 'N/A')
                    if caudal_diseno_lps != 'N/A':
                        caudal_diseno_lps = f"{float(caudal_diseno_lps):.2f}"
                    
                    potencia_ajustada = vdf.get('potencia_ajustada', 'N/A')
                    if potencia_ajustada != 'N/A':
                        potencia_ajustada = f"{float(potencia_ajustada):.2f}"
                    
                    eficiencia_ajustada = vdf.get('eficiencia_ajustada', 'N/A')
                    if eficiencia_ajustada != 'N/A':
                        eficiencia_ajustada = f"{float(eficiencia_ajustada):.2f}"
                    
                    rpm_porcentaje = vdf.get('rpm_porcentaje', 'N/A')
                    if rpm_porcentaje != 'N/A':
                        rpm_porcentaje = f"{float(rpm_porcentaje):.2f}"
                    
                    factor_rpm = vdf.get('factor_rpm', 'N/A')
                    if factor_rpm != 'N/A':
                        factor_rpm = f"{float(factor_rpm):.2f}"
                    
                    eficiencia_operacion = vdf.get('eficiencia_operacion', 'N/A')
                    if eficiencia_operacion != 'N/A':
                        eficiencia_operacion = f"{float(eficiencia_operacion):.2f}"
                    
                    nota_calculo = vdf.get('nota_calculo', 'N/A')
                    
                    tabla_vdf_html = f"""
                    <table style="width: 100%; border-collapse: collapse; margin: 10px 0; font-family: Arial, sans-serif;">
                    <thead>
                        <tr style="background-color: #f5f5f5;">
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Parámetro</th>
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Valor</th>
                            <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Unidad</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Caudal Nominal VDF</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{caudal_nominal_vdf}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">L/s</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Caudal de Diseño</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{caudal_diseno_lps}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">L/s</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Potencia Ajustada</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{potencia_ajustada}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">kW</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Eficiencia Ajustada</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{eficiencia_ajustada}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">%</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">RPM Porcentaje</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{rpm_porcentaje}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">%</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Factor RPM</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{factor_rpm}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">-</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Eficiencia Operación</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{eficiencia_operacion}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">%</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 10px;">Nota Cálculo</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">{nota_calculo}</td>
                            <td style="border: 1px solid #ddd; padding: 10px;">-</td>
                        </tr>
                    </tbody>
                    </table>
                    """
                    
                    st.markdown(tabla_vdf_html, unsafe_allow_html=True)
            
            # Bomba Seleccionada
            st.markdown("#### 🚰 Bomba Seleccionada")
            
            if 'bomba_seleccionada' in project_data:
                bomba_sel = project_data['bomba_seleccionada']
                st.markdown(f"• **Nombre:** {bomba_sel.get('nombre', 'N/A')}")
                st.markdown(f"• **URL:** {bomba_sel.get('url', 'N/A')}")
                st.markdown(f"• **Descripción:** {bomba_sel.get('descripcion', 'N/A')[:200]}...")
            
            # Separador horizontal
            st.markdown("---")
            
            # Gráfico de Curvas 100% RPM
            st.markdown("### 6. Gráfico de Curvas 100% RPM")
            
            # Mostrar punto de operación para 100% RPM
            if 'punto_operacion' in project_data:
                punto_op = project_data['punto_operacion']
                
                # Datos del punto de operación
                caudal_op = punto_op.get('caudal', 'N/A')
                altura_op = punto_op.get('altura', 'N/A')
                eficiencia_op = punto_op.get('eficiencia', 'N/A')
                potencia_op = punto_op.get('potencia', 'N/A')
                
                # Formatear valores
                if caudal_op != 'N/A':
                    caudal_op = f"{float(caudal_op):.2f}"
                if altura_op != 'N/A':
                    altura_op = f"{float(altura_op):.2f}"
                if eficiencia_op != 'N/A':
                    eficiencia_op = f"{float(eficiencia_op):.2f}"
                if potencia_op != 'N/A':
                    potencia_op = f"{float(potencia_op):.2f}"
                
                # Obtener datos de NPSH
                npsh_op = "N/A"
                if 'curva_inputs' in project_data and 'npsh' in project_data['curva_inputs']:
                    npsh_data = project_data['curva_inputs']['npsh']
                    if len(npsh_data) >= 2:
                        punto_npsh = npsh_data[1]  # Segundo punto como punto de operación
                        npsh_op = f"{punto_npsh[1]:.2f}"
                
                # Crear tabla HTML para punto 6 (100% RPM)
                tabla_html_100 = f"""
                <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                <thead>
                    <tr style="background-color: #f0f0f0;">
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva del Sistema y Curva de la Bomba (H-Q)</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva de Rendimiento (η-Q)</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva de Potencia (PBHP-Q)</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva de NPSH Requerido (NPSHR-Q)</th>
                    </tr>
                    <tr style="background-color: #f8f8f8;">
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Punto de Operación</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Punto de Operación</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Punto de Operación</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Punto de Operación</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">
                            <strong>Caudal (Q):</strong> {caudal_op} L/s<br>
                            <strong>Altura (H):</strong> {altura_op} m
                        </td>
                        <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">
                            <strong>Caudal (Q):</strong> {caudal_op} L/s<br>
                            <strong>Rendimiento (η):</strong> {eficiencia_op} %
                        </td>
                        <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">
                            <strong>Caudal (Q):</strong> {caudal_op} L/s<br>
                            <strong>Potencia (PBHP):</strong> {potencia_op} HP
                        </td>
                        <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">
                            <strong>Caudal (Q):</strong> {caudal_op} L/s<br>
                            <strong>NPSHreq:</strong> {npsh_op} m
                        </td>
                    </tr>
                </tbody>
                </table>
                """
                
                st.markdown(tabla_html_100, unsafe_allow_html=True)
            
            # Porcentaje de RPM para curvas VDF
            if 'vfd' in project_data:
                vfd = project_data['vfd']
                st.markdown(f"• **Porcentaje de RPM para curvas VDF:** {vfd.get('rpm_percentage', 'N/A')}%")
            
            # Separador horizontal
            st.markdown("---")
            
            # Gráfico de Curvas VDF
            st.markdown("### 7. Gráfico de Curvas VDF")
            if 'vfd' in project_data:
                vfd = project_data['vfd']
                rpm_percentage = vfd.get('rpm_percentage', 'N/A')
                st.markdown(f"**Porcentaje de RPM para curvas VDF:** {rpm_percentage}%")
                
                # Mostrar punto de operación VDF
                if 'analisis_vdf' in project_data:
                    analisis_vdf = project_data['analisis_vdf']
                    
                    # Datos del punto de operación VDF
                    caudal_vdf = analisis_vdf.get('caudal_diseno_lps', 'N/A')
                    altura_vdf = analisis_vdf.get('interseccion_vfd', ['N/A', 'N/A'])
                    eficiencia_vdf = analisis_vdf.get('eficiencia_operacion', 'N/A')
                    potencia_vdf = analisis_vdf.get('potencia_ajustada', 'N/A')
                    
                    # Formatear valores
                    if caudal_vdf != 'N/A':
                        caudal_vdf = f"{float(caudal_vdf):.2f}"
                    if altura_vdf[1] != 'N/A':
                        altura_vdf = f"{float(altura_vdf[1]):.2f}"
                    else:
                        altura_vdf = "N/A"
                    if eficiencia_vdf != 'N/A':
                        eficiencia_vdf = f"{float(eficiencia_vdf):.2f}"
                    if potencia_vdf != 'N/A':
                        potencia_vdf = f"{float(potencia_vdf):.2f}"
                    
                    # Obtener datos de NPSH VDF
                    npsh_vdf = "N/A"
                    if 'curvas_texto' in project_data and 'npsh' in project_data['curvas_texto']:
                        npsh_texto = project_data['curvas_texto']['npsh']
                        puntos_npsh = []
                        for linea in npsh_texto.split('\n'):
                            if linea.strip():
                                partes = linea.strip().split('\t')
                                if len(partes) >= 2:
                                    puntos_npsh.append([float(partes[0]), float(partes[1])])
                        
                        if len(puntos_npsh) >= 2:
                            punto_npsh_vdf = puntos_npsh[1]  # Segundo punto como punto de operación
                            npsh_vdf = f"{punto_npsh_vdf[1]:.2f}"
                    
                    # Crear tabla HTML para punto 7 (VDF)
                    tabla_html_vdf = f"""
                    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                    <thead>
                        <tr style="background-color: #f0f0f0;">
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva del Sistema y Curva de la Bomba ({rpm_percentage}% RPM)</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva de Rendimiento ({rpm_percentage}% RPM)</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva de Potencia ({rpm_percentage}% RPM)</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva de NPSH Requerido ({rpm_percentage}% RPM)</th>
                        </tr>
                        <tr style="background-color: #f8f8f8;">
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Punto de Operación VDF</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Punto de Operación VDF</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Punto de Operación VDF</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Punto de Operación VDF</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">
                                <strong>Caudal (Q):</strong> {caudal_vdf} L/s<br>
                                <strong>Altura (H):</strong> {altura_vdf} m
                            </td>
                            <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">
                                <strong>Caudal (Q):</strong> {caudal_vdf} L/s<br>
                                <strong>Rendimiento (η):</strong> {eficiencia_vdf} %
                            </td>
                            <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">
                                <strong>Caudal (Q):</strong> {caudal_vdf} L/s<br>
                                <strong>Potencia (PBHP):</strong> {potencia_vdf} HP
                            </td>
                            <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">
                                <strong>Caudal (Q):</strong> {caudal_vdf} L/s<br>
                                <strong>NPSHreq:</strong> {npsh_vdf} m
                            </td>
                        </tr>
                    </tbody>
                    </table>
                    """
                    
                    st.markdown(tabla_html_vdf, unsafe_allow_html=True)
            
            # Separador horizontal
            st.markdown("---")
            
            # --- 8. TABLAS ---
            st.subheader("8. Tablas")
            
            # Verificar si hay datos de tablas_graficos
            tablas_graficos = project_data.get('tablas_graficos', {})
            if not tablas_graficos:
                st.warning("⚠️ No hay datos de tablas_graficos disponibles en el JSON")
                st.info("💡 Las tablas se generan automáticamente durante el cálculo del proyecto")
            else:
                # Función helper para generar tabla Markdown desde DF
                def df_to_markdown(df, title):
                    if df.empty:
                        return f"**{title}**: No hay datos disponibles."
                    md = df.to_markdown(index=False, tablefmt="pipe")
                    return f"### {title}\n{md}"
                
                # Función para reconstruir DF (con fix genérico por si acaso)
                def build_df(df_info):
                    if not df_info or 'data' not in df_info:
                        return pd.DataFrame()
                    try:
                        df = pd.DataFrame(df_info['data'])
                        # Fix genérico (no necesario aquí, pero seguro)
                        for col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        return df
                    except Exception as e:
                        st.error(f"Error reconstruyendo DF: {str(e)}")
                        return pd.DataFrame()
                
                # Función helper para generar tabla HTML horizontal con 5 curvas
                def generar_tabla_horizontal_html(df_bomba, df_rend, df_pot, df_npsh, df_sist, titulo):
                    tabla_html = f"""
                    <h4>{titulo}</h4>
                    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                    <thead>
                        <tr style="background-color: #f0f0f0;">
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva Bomba (H-Q)</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva Rendimiento (η-Q)</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva Potencia (PBHP-Q)</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva NPSH (NPSHR-Q)</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Curva del Sistema (H-Q)</th>
                        </tr>
                        <tr style="background-color: #f8f8f8;">
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Q (L/s) | H (m)</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Q (L/s) | η (%)</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Q (L/s) | P (HP)</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Q (L/s) | NPSH (m)</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Q (L/s) | H (m)</th>
                        </tr>
                    </thead>
                    <tbody>
                    """
                    
                    # Determinar el número máximo de filas
                    max_rows = max(len(df_bomba), len(df_rend), len(df_pot), len(df_npsh), len(df_sist))
                    
                    for i in range(max_rows):
                        tabla_html += "<tr>"
                        
                        # Curva Bomba
                        if i < len(df_bomba) and not df_bomba.empty:
                            tabla_html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{df_bomba.iloc[i, 0]:.2f} | {df_bomba.iloc[i, 1]:.2f}</td>'
                        else:
                            tabla_html += '<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">-</td>'
                        
                        # Curva Rendimiento
                        if i < len(df_rend) and not df_rend.empty:
                            tabla_html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{df_rend.iloc[i, 0]:.2f} | {df_rend.iloc[i, 1]:.2f}</td>'
                        else:
                            tabla_html += '<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">-</td>'
                        
                        # Curva Potencia
                        if i < len(df_pot) and not df_pot.empty:
                            tabla_html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{df_pot.iloc[i, 0]:.2f} | {df_pot.iloc[i, 1]:.2f}</td>'
                        else:
                            tabla_html += '<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">-</td>'
                        
                        # Curva NPSH
                        if i < len(df_npsh) and not df_npsh.empty:
                            tabla_html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{df_npsh.iloc[i, 0]:.2f} | {df_npsh.iloc[i, 1]:.2f}</td>'
                        else:
                            tabla_html += '<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">-</td>'
                        
                        # Curva del Sistema
                        if i < len(df_sist) and not df_sist.empty:
                            tabla_html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{df_sist.iloc[i, 0]:.2f} | {df_sist.iloc[i, 1]:.2f}</td>'
                        else:
                            tabla_html += '<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">-</td>'
                        
                        tabla_html += "</tr>"
                    
                    tabla_html += "</tbody></table>"
                    return tabla_html
                
                # Tablas 100% RPM
                with st.container():
                    st.markdown("**Tablas de gráficos a 100% RPM en cuadros**")
                    tablas_100 = tablas_graficos.get('tablas_100_rpm', {})
                    config_100 = tablas_100.get('configuracion', {})
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"• **Q min (L/s)**: {config_100.get('q_min_100', 0.0)}")
                    with col2:
                        st.markdown(f"• **Q max (L/s)**: {config_100.get('q_max_100', 70.0)}")
                    with col3:
                        st.markdown(f"• **Paso del caudal (L/s)**: {config_100.get('paso_caudal_100', 5.0)}")
                    
                    # Reconstruir DataFrames
                    df_bomba = build_df(tablas_100.get('df_bomba_100'))
                    df_rend = build_df(tablas_100.get('df_rendimiento_100'))
                    df_pot = build_df(tablas_100.get('df_potencia_100'))
                    df_npsh = build_df(tablas_100.get('df_npsh_100'))
                    df_sist = build_df(tablas_100.get('df_sistema_100'))
                    
                    # Generar tabla horizontal HTML
                    tabla_html_100 = generar_tabla_horizontal_html(
                        df_bomba, df_rend, df_pot, df_npsh, df_sist,
                        "📈 Tablas de Gráficos a 100% RPM"
                    )
                    st.markdown(tabla_html_100, unsafe_allow_html=True)
                    
                    if 'nota' in tablas_100:
                        st.markdown(f"*Nota: {tablas_100['nota']}*")
                
                # Tablas VFD
                with st.container():
                    st.markdown("**Tablas de gráficos VDF en cuadros**")
                    tablas_vfd = tablas_graficos.get('tablas_vfd_rpm', {})
                    config_vfd = tablas_vfd.get('configuracion', {})
                    rpm_pct = config_vfd.get('rpm_percentage', 75.0)
                    st.markdown(f"**Porcentaje de RPM para curvas VFD: {rpm_pct}%**")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"• **Q min (L/s)**: {config_vfd.get('q_min_vdf', 0.0)}")
                    with col2:
                        st.markdown(f"• **Q max (L/s)**: {config_vfd.get('q_max_vdf', 70.0)}")
                    with col3:
                        st.markdown(f"• **Paso del caudal (L/s)**: {config_vfd.get('paso_caudal_vfd', 5.0)}")
                    
                    # Reconstruir DFs VFD
                    df_bomba_vfd = build_df(tablas_vfd.get('df_bomba_vfd'))
                    df_rend_vfd = build_df(tablas_vfd.get('df_rendimiento_vfd'))
                    df_pot_vfd = build_df(tablas_vfd.get('df_potencia_vfd'))
                    df_npsh_vfd = build_df(tablas_vfd.get('df_npsh_vfd'))
                    df_sist_vfd = build_df(tablas_vfd.get('df_sistema_vfd'))
                    
                    # Generar tabla horizontal HTML
                    tabla_html_vfd = generar_tabla_horizontal_html(
                        df_bomba_vfd, df_rend_vfd, df_pot_vfd, df_npsh_vfd, df_sist_vfd,
                        f"📈 Tablas de Gráficos VDF a {rpm_pct}% RPM"
                    )
                    st.markdown(tabla_html_vfd, unsafe_allow_html=True)
                    
                    if 'nota' in tablas_vfd:
                        st.markdown(f"*Nota: {tablas_vfd['nota']}*")
            
            # Separador horizontal antes de los botones de descarga
            st.markdown("---")
            
            # BOTONES DE DESCARGA
            st.markdown("### 📥 Descargas")
            col1, col2, col3, col4, col5 = st.columns([20, 20, 20, 20, 20])
            
            with col1:
                # Botón de descarga JSON
                json_str = json.dumps(project_data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📄 Descargar JSON",
                    data=json_str,
                    file_name=f"{nombre_proyecto}_resumen.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col2:
                # Botón de descarga HTML
                html_content = generate_html_report(project_data, nombre_proyecto)
                st.download_button(
                    label="🌐 Descargar HTML",
                    data=html_content,
                    file_name=f"{nombre_proyecto}_resumen.html",
                    mime="text/html",
                    use_container_width=True
                )
            
            # col3, col4, col5 quedan vacías
            
        except Exception as e:
            st.error(f"Error al cargar resumen: {str(e)}")
            st.error(f"Tipo de error: {type(e).__name__}")
            if hasattr(e, 'args') and e.args:
                st.error(f"Detalles del error: {e.args}")
            # Debug: mostrar información adicional
            st.write("**Debug - Información del proyecto:**")
            st.write(f"- Claves disponibles en session_state: {len(list(st.session_state.keys()))} claves")
    

