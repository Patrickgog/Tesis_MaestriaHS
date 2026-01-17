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

# Importaciones de módulos refactorizados
from ui.tabs_modules.data_input import render_data_input_tab
from ui.tabs_modules.analysis import render_analysis_tab
from ui.tabs_modules.theory import render_theory_tab
from ui.tabs_modules.tables import render_tables_tab
from ui.tabs_modules.json_viewer import render_json_tab
from ui.tabs_modules.developer import render_questions_tab
from ui.tabs_modules.simulation import render_simulation_tab
from ui.tabs_modules.optimization import render_optimization_tab
from ui.tabs_modules.diameter_selection_ui import render_diameter_selection_tab
from ui.tabs_modules.common import render_footer, render_reports_tab, render_ai_tab, fix_mixed_types_in_dataframe, calcular_caudal_por_bomba

# Imports originales (para compatibilidad si algo escapó)
from ui.ai_module import render_ai_question_response
from ui.transient_tab import render_transient_tab as render_transient_simulation_tab
from ui.transients import render_transient_tab
from ui.html_generator import generate_html_report

# Re-exportar funciones helper para mantener compatibilidad si otros módulos las importaban de aquí
# (Aunque lo ideal es que importen de common, pero por seguridad visual/funcional)

def render_main_tabs():
    """Renderiza las pestañas principales de la aplicación"""
    
    # Crear pestañas
    # Verificar si el análisis transientes está habilitado
    transient_enabled = st.session_state.get('transient_analysis_enabled', False)
    
    # Verificar si la IA está habilitada
    ai_enabled = st.session_state.get('ai_enabled', False)
    
    # Verificar si el visualizador Json está habilitado
    json_enabled = st.session_state.get('json_viewer_enabled', False)
    
    # Verificar si los Informes están habilitados
    informes_enabled = st.session_state.get('informes_enabled', False)
    
    # Verificar si la Simulación está habilitada
    simulation_enabled = st.session_state.get('simulation_enabled', False)
    
    # Verificar si Teoría está habilitada
    theory_enabled = st.session_state.get('theory_enabled', False)
    
    # Verificar si Tablas está habilitada
    tables_enabled = st.session_state.get('tables_enabled', False)
    
    # Verificar si la Optimización IA está habilitada
    optimization_enabled = st.session_state.get('optimization_enabled', False)
    
    # Verificar si la Selección de Diámetros está habilitada
    selection_enabled = st.session_state.get('selection_enabled', False)
    
    # Construir lista de pestañas dinámicamente
    tabs_list = ["Datos de Entrada", "Análisis de Curvas"]
    
    # Agregar pestañas opcionales según estado
    if theory_enabled:
        tabs_list.append("Teoría y Fundamentos")
    if tables_enabled:
        tabs_list.append("Tablas")
    
    # Agregar pestañas opcionales según estado
    if transient_enabled:
        tabs_list.append("🔄 Transientes")
    if ai_enabled:
        tabs_list.append("🤖 Análisis IA")
    if json_enabled:
        tabs_list.append("📋 Resumen")
    if informes_enabled:
        tabs_list.append("📄 Reportes")
    if simulation_enabled:
        tabs_list.append("📈 Simulación Operativa")
    if optimization_enabled:
        tabs_list.append("🎯 Optimización IA")
    if selection_enabled:
        tabs_list.append("📏 Selección de Diámetros")
    if st.session_state.get('developer_mode', False):
        tabs_list.append("📝 Preguntas")
    
    # Crear las pestañas
    tabs = st.tabs(tabs_list)
    
    # Mapear índices de pestañas
    tab_index = 0
    tab1 = tabs[tab_index]; tab_index += 1  # Datos de Entrada
    tab2 = tabs[tab_index]; tab_index += 1  # Análisis de Curvas
    
    # Variables para pestañas opcionales
    tab_theory = None
    tab_tables = None
    tab_transient = None
    tab_ai = None
    tab_json = None
    tab_informes = None
    tab_simulation = None
    tab_optimization = None
    tab_selection = None
    tab_preguntas = None
    
    # Asignar pestañas opcionales según están habilitadas
    if theory_enabled:
        tab_theory = tabs[tab_index]; tab_index += 1
    if tables_enabled:
        tab_tables = tabs[tab_index]; tab_index += 1
    
    if transient_enabled:
        tab_transient = tabs[tab_index]; tab_index += 1
    if ai_enabled:
        tab_ai = tabs[tab_index]; tab_index += 1
    if json_enabled:
        tab_json = tabs[tab_index]; tab_index += 1
    if informes_enabled:
        tab_informes = tabs[tab_index]; tab_index += 1
    if simulation_enabled:
        tab_simulation = tabs[tab_index]; tab_index += 1
    if optimization_enabled:
        tab_optimization = tabs[tab_index]; tab_index += 1
    if selection_enabled:
        tab_selection = tabs[tab_index]; tab_index += 1
    if st.session_state.get('developer_mode', False):
        tab_preguntas = tabs[tab_index]; tab_index += 1
    
    with tab1:
        render_data_input_tab()
    
    with tab2:
        render_analysis_tab()
    
    # Pestaña de Teoría (solo visible si está habilitada)
    if theory_enabled and tab_theory:
        with tab_theory:
            render_theory_tab()
    
    # Pestaña de Tablas (solo visible si está habilitada)
    if tables_enabled and tab_tables:
        with tab_tables:
            render_tables_tab()
    
    # Pestaña de Transientes (solo visible si está habilitada)
    if transient_enabled and tab_transient:
        with tab_transient:
            render_transient_tab()
    
    # Pestaña de Análisis IA (solo visible si está habilitada)
    if ai_enabled and tab_ai:
        with tab_ai:
            render_ai_tab()
    
    # Pestaña de Json (solo visible si está habilitada)
    if json_enabled and tab_json:
        with tab_json:
            render_json_tab()
    
    # Pestaña de Reportes (solo visible si está habilitada)
    if informes_enabled and tab_informes:
        with tab_informes:
            render_reports_tab()
    
    # Pestaña de Simulación Operativa (solo visible si está habilitada)
    if simulation_enabled and tab_simulation:
        with tab_simulation:
            render_simulation_tab()
    
    # Pestaña de Optimización IA (solo visible si está habilitada)
    if optimization_enabled and tab_optimization:
        with tab_optimization:
            render_optimization_tab()

    # Pestaña de Selección de Diámetros (solo visible si está habilitada)
    if selection_enabled and tab_selection:
        with tab_selection:
            render_diameter_selection_tab()
    
    # Pestaña de Preguntas (solo visible en modo desarrollador)
    if st.session_state.get('developer_mode', False) and tab_preguntas:
        with tab_preguntas:
            render_questions_tab()

    # Footer global para todas las pestañas
    render_footer()

# Re-export de save_questions_to_json si es necesario (está en developer.py ahora)
from ui.tabs_modules.developer import save_questions_to_json, render_tema_questions
