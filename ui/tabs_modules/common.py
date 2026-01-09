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

def render_footer():
    """Renderiza el pie de página común para todas las pestañas"""
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    st.markdown("""
    <div style='text-align: center; padding: 10px; color: #666; line-height: 1.2;'>
        <h5 style='margin-bottom: 5px;'>MAESTRÍA EN HIDROSANITARIA</h5>
        <p style='margin: 2px 0; font-size: 14px;'><strong>Desarrollador:</strong> Patricio Sarmiento Reinoso</p>
        <p style='margin: 2px 0; font-size: 14px;'><strong>Director:</strong> Aurelio Ochoa García</p>
        <p style='margin: 2px 0; font-size: 14px;'><strong>2025</strong></p>
    </div>
    """, unsafe_allow_html=True)



def fix_mixed_types_in_dataframe(df):
    """
    Función helper para corregir tipos mixtos en DataFrames de accesorios.
    Aplica el fix global para evitar errores de PyArrow con tipos mixtos.
    
    Args:
        df: DataFrame de pandas
    
    Returns:
        DataFrame corregido con tipos consistentes
    """
    if df is None or df.empty:
        return df
    
    # Crear una copia para evitar modificar el DataFrame original
    df_fixed = df.copy()
    
    # FIX GLOBAL: Convertir columnas problemáticas a string para evitar errores de PyArrow
    problematic_columns = ['k', 'K', 'cantidad', 'Cantidad']
    for col in problematic_columns:
        if col in df_fixed.columns:
            # Convertir todos los valores a string, manejando NaN y None
            df_fixed[col] = df_fixed[col].astype(str)
            # Reemplazar 'nan' string con 'N/A' para mejor visualización
            df_fixed[col] = df_fixed[col].replace('nan', 'N/A')
            df_fixed[col] = df_fixed[col].replace('None', 'N/A')
    
    # Opcional: Corrige otras columnas mixtas si las hay (e.g., 'lc_d' si es str)
    numeric_columns = ['lc_d', 'Lc/D', 'lc_d_medio', 'Lc/D Medio']
    for col in numeric_columns:
        if col in df_fixed.columns:
            df_fixed[col] = pd.to_numeric(df_fixed[col], errors='coerce')  # Numérico, NaN si falla
    
    return df_fixed

def calcular_caudal_por_bomba(caudal_total, n_bombas):
    """
    Calcula el caudal que debe manejar cada bomba individual en un sistema paralelo.
    
    Para bombas en paralelo:
    - Cada bomba maneja una fracción del caudal total
    - Todas las bombas trabajan a la misma altura
    
    Args:
        caudal_total: Caudal total del sistema en L/s
        n_bombas: Número de bombas idénticas en paralelo
    
    Returns:
        Caudal que debe manejar cada bomba individual
    """
    if n_bombas <= 0:
        return caudal_total
    
    return caudal_total / n_bombas




def render_reports_tab():
    """Renderiza la pestaña de informes técnicos"""
    from ui.reports import render_reports_tab as render_reports
    render_reports()

def render_ai_tab():
    """Renderiza la pestaña dedicada al análisis con IA"""
    from ui.ai_module import render_ai_question_response
    
    # Verificar si la IA está configurada
    if not st.session_state.get('ai_enabled', False):
        st.warning("⚠️ **Análisis IA no está activado**")
        st.info("Para usar el análisis con IA, activa 'Análisis IA' en el panel lateral y configura tu clave API.")
        return
    
    if not st.session_state.get('api_key') or not st.session_state.get('model'):
        st.warning("⚠️ **Configuración de IA incompleta**")
        st.info("Por favor, configura tu clave API de Gemini en el panel lateral.")
        return
    
    # Renderizar la funcionalidad de pregunta/respuesta
    render_ai_question_response()



