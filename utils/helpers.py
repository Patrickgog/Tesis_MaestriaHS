# Funciones auxiliares y utilidades

import streamlit as st
import json
import os
from typing import Dict, Any

def initialize_state():
    """Inicializa el estado de la aplicación"""
    if 'init_done' not in st.session_state:
        loaded_state = load_state()
        # Solo inicializar valores que no existen
        defaults = {
            'static_head': loaded_state.get('static_head', 10.0),
            'pipe_length': loaded_state.get('pipe_length', 1000.0),
            'selected_material_name': loaded_state.get('selected_material_name', "PVC"),
            'flow_unit': loaded_state.get('flow_unit', 'L/s'),
            'col1_width': loaded_state.get('col1_width', 25),
            'col2_width': loaded_state.get('col2_width', 25),
            'col3_width': loaded_state.get('col3_width', 25),
            'col4_width': loaded_state.get('col4_width', 25),
            'font_size_title': loaded_state.get('font_size_title', 18),
            'font_size_axis': loaded_state.get('font_size_axis', 15),
            'init_done': True,
            'calibration_points': loaded_state.get('calibration_points', None),
            'digitalized_points': loaded_state.get('digitalized_points', []),
            'cal1_pixel_x': loaded_state.get('cal1_pixel_x', None),
            'cal1_pixel_y': loaded_state.get('cal1_pixel_y', None),
            'cal2_pixel_x': loaded_state.get('cal2_pixel_x', None),
            'cal2_pixel_y': loaded_state.get('cal2_pixel_y', None),
            'cal1_real_x': loaded_state.get('cal1_real_x', None),
            'cal1_real_y': loaded_state.get('cal1_real_y', None),
            'cal2_real_x': loaded_state.get('cal2_real_x', None),
            'cal2_real_y': loaded_state.get('cal2_real_y', None),
            'uploaded_image_bytes': loaded_state.get('uploaded_image_bytes', None),
            'proyecto': loaded_state.get('proyecto', ''),
            'diseno': loaded_state.get('diseno', ''),
            'h_estatica': loaded_state.get('h_estatica', 50.0),
            'caudal_nominal': loaded_state.get('caudal_nominal', 50.0),
            'npshd': loaded_state.get('npshd', 5.0),
            'ajuste_tipo': loaded_state.get('ajuste_tipo', 'Cuadrática (2do grado)'),
            'curva_mode': loaded_state.get('curva_mode', '3 puntos'),
            'temperatura_c': loaded_state.get('temperatura_c', 20.0),
            'densidad_liquido': loaded_state.get('densidad_liquido', 1.0),
            'presion_vapor': loaded_state.get('presion_vapor', 0.023),
            'long_succion': loaded_state.get('long_succion', 10.0),
            'diam_succion': loaded_state.get('diam_succion', 200.0),
            'mat_succion': loaded_state.get('mat_succion', 'PVC'),
            'long_impulsion': loaded_state.get('long_impulsion', 100.0),
            'diam_impulsion': loaded_state.get('diam_impulsion', 150.0),
            'mat_impulsion': loaded_state.get('mat_impulsion', 'PVC'),
            'accesorios_succion': loaded_state.get('accesorios_succion', []),
            'accesorios_impulsion': loaded_state.get('accesorios_impulsion', []),
            'curva_inputs': loaded_state.get('curva_inputs', {}),
            'rpm_percentage': loaded_state.get('rpm_percentage', 75.0),
            'paso_caudal_vfd': loaded_state.get('paso_caudal_vfd', 5.0),
            'metodo_calculo': loaded_state.get('metodo_calculo', 'Darcy-Weisbach')
        }
        
        # Aplicar valores por defecto
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        
        # Inicializar estado del módulo de IA
        initialize_ai_state()

def load_state() -> Dict[str, Any]:
    """Carga el estado desde un archivo JSON"""
    try:
        if os.path.exists('app_state.json'):
            with open('app_state.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error cargando estado: {e}")
    return {}

def save_state():
    """Guarda el estado actual en un archivo JSON"""
    try:
        # Crear una copia del estado sin funciones y objetos no serializables
        state_to_save = {}
        for key, value in st.session_state.items():
            if key not in ['init_done', 'uploaded_image_bytes']:  # Excluir claves problemáticas
                try:
                    json.dumps(value)  # Test si es serializable
                    state_to_save[key] = value
                except (TypeError, ValueError):
                    continue
        
        with open('app_state.json', 'w', encoding='utf-8') as f:
            json.dump(state_to_save, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando estado: {e}")

def format_number(value: float, decimals: int = 2) -> str:
    """Formatea un número con el número de decimales especificado"""
    return f"{value:.{decimals}f}"

def validate_curve_data(curve_data: list) -> bool:
    """Valida que los datos de la curva sean válidos"""
    if not curve_data or len(curve_data) < 2:
        return False
    
    for point in curve_data:
        if len(point) != 2 or not isinstance(point[0], (int, float)) or not isinstance(point[1], (int, float)):
            return False
        if point[0] < 0 or point[1] < 0:
            return False
    
    return True

def get_curve_summary(curve_data: list, curve_name: str) -> str:
    """Genera un resumen de los datos de la curva"""
    if not validate_curve_data(curve_data):
        return f"❌ {curve_name}: Datos inválidos"
    
    x_values = [point[0] for point in curve_data]
    y_values = [point[1] for point in curve_data]
    
    return f"✅ {curve_name}: {len(curve_data)} puntos, Q: {min(x_values):.1f}-{max(x_values):.1f} L/s, {curve_name.split()[0]}: {min(y_values):.1f}-{max(y_values):.1f}"

def initialize_ai_state():
    """Inicializa el estado de sesión para el módulo de IA"""
    ai_defaults = {
        'api_key': None,
        'ai_enabled': False,
        'selected_question': None,
        'selected_tema': None,
        'model': None,
        'selected_model': 'gemini-2.5-flash',
        'ai_response': None,
        'ai_response_generated': False
    }
    
    for key, value in ai_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value