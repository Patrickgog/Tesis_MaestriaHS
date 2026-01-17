# Procesador de archivos Excel para curvas de bomba

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Any, Tuple, List
import io

def process_excel_curves(uploaded_file) -> Dict[str, Any]:
    """
    Procesa un archivo Excel con curvas de bomba y devuelve los datos estructurados.
    
    Args:
        uploaded_file: Archivo Excel subido por el usuario
    
    Returns:
        Diccionario con los datos de las curvas procesadas
    """
    try:
        # Leer todas las hojas del archivo Excel
        excel_data = pd.read_excel(uploaded_file, sheet_name=None, engine='openpyxl')
        
        # Estructura esperada de las hojas
        expected_sheets = ['H-Q', 'Power', 'Efficiency', 'NPSH']
        processed_data = {
            'success': False,
            'curves': {},
            'errors': [],
            'warnings': []
        }
        
        # Verificar que todas las hojas necesarias existan
        missing_sheets = []
        for sheet_name in expected_sheets:
            if sheet_name not in excel_data:
                missing_sheets.append(sheet_name)
        
        if missing_sheets:
            processed_data['errors'].append(f"Hojas faltantes: {', '.join(missing_sheets)}")
            return processed_data
        
        # Procesar cada hoja
        sheet_mapping = {
            'H-Q': 'bomba',
            'Power': 'potencia', 
            'Efficiency': 'rendimiento',
            'NPSH': 'npsh'
        }
        
        for sheet_name, curve_key in sheet_mapping.items():
            try:
                df = excel_data[sheet_name]
                
                # Verificar que tenga al menos 2 columnas
                if df.shape[1] < 2:
                    processed_data['errors'].append(f"Hoja {sheet_name} debe tener al menos 2 columnas")
                    continue
                
                # Tomar las primeras dos columnas como caudal y valor
                col_flow = df.columns[0]  # Primera columna = caudal
                col_value = df.columns[1]  # Segunda columna = valor
                
                # Limpiar datos: eliminar filas con valores NaN
                df_clean = df[[col_flow, col_value]].dropna()
                
                if len(df_clean) < 2:
                    processed_data['errors'].append(f"Hoja {sheet_name} debe tener al menos 2 filas válidas")
                    continue
                
                # Convertir caudal de m³/h a L/s
                flow_ls = df_clean[col_flow] / 3.6
                values = df_clean[col_value]
                
                # Crear puntos de la curva
                curve_points = []
                for i in range(len(df_clean)):
                    flow_val = float(flow_ls.iloc[i])
                    value_val = float(values.iloc[i])
                    curve_points.append([flow_val, value_val])
                
                # Ordenar por caudal
                curve_points.sort(key=lambda x: x[0])
                
                processed_data['curves'][curve_key] = curve_points
                
                # Crear texto para textarea
                text_lines = []
                for point in curve_points:
                    text_lines.append(f"{point[0]:.2f} {point[1]:.2f}")
                
                processed_data['curves'][f"{curve_key}_textarea"] = "\n".join(text_lines)
                
            except Exception as e:
                processed_data['errors'].append(f"Error procesando hoja {sheet_name}: {str(e)}")
        
        # Si tenemos al menos la curva de la bomba, marcarlo como exitoso
        if 'bomba' in processed_data['curves']:
            processed_data['success'] = True
            processed_data['warnings'].append(f"Archivo procesado exitosamente. Curvas disponibles: {list(sheet_mapping.keys())}")
        else:
            processed_data['errors'].append("No se pudo procesar ninguna curva válida")
        
        return processed_data
        
    except Exception as e:
        return {
            'success': False,
            'curves': {},
            'errors': [f"Error general: {str(e)}"],
            'warnings': []
        }

def create_system_curve_points(caudal_lps: float, system_params: Dict[str, Any]) -> List[Tuple[float, float]]:
    """
    Crea puntos para la curva del sistema basada en los parámetros dados.
    
    Args:
        caudal_lps: Caudal de diseño en L/s
        system_params: Parámetros del sistema
    
    Returns:
        Lista de puntos (caudal, altura) para la curva del sistema
    """
    from core.calculations import calculate_adt_for_multiple_flows
    from config.constants import HAZEN_WILLIAMS_C
    
    # Definir caudales para generar puntos de la curva
    flows = [0, 25, 50, 75, 100, 125, 150, 175, 200]  # L/s
    flows = [f for f in flows if f <= caudal_lps * 2]  # Limitar al doble del caudal de diseño
    
    # Agregar el caudal de diseño si no está incluido
    if caudal_lps not in flows:
        flows.append(caudal_lps)
    flows.sort()
    
    # Preparar parámetros del sistema
    params = {
        'long_succion': system_params.get('long_succion', 10.0),
        'diam_succion_m': system_params.get('diam_succion_mm', 200.0) / 1000.0,
        'mat_succion': system_params.get('mat_succion', 'PVC'),
        'otras_perdidas_succion': system_params.get('otras_perdidas_succion', 0.0),
        'accesorios_succion': system_params.get('accesorios_succion', []),
        'long_impulsion': system_params.get('long_impulsion', 500.0),
        'diam_impulsion_m': system_params.get('diam_impulsion_mm', 150.0) / 1000.0,
        'mat_impulsion': system_params.get('mat_impulsion', 'PVC'),
        'otras_perdidas_impulsion': system_params.get('otras_perdidas_impulsion', 0.0),
        'accesorios_impulsion': system_params.get('accesorios_impulsion', []),
        'altura_succion': system_params.get('altura_succion_input', 1.65),
        'altura_descarga': system_params.get('altura_descarga', 80.0)
    }
    
    # Agregar coeficientes C de Hazen-Williams
    params['C_succion'] = HAZEN_WILLIAMS_C.get(params['mat_succion'], 150)
    params['C_impulsion'] = HAZEN_WILLIAMS_C.get(params['mat_impulsion'], 150)
    
    try:
        resultados_adt = calculate_adt_for_multiple_flows(flows, 'L/s', params)
        
        system_points = []
        for resultado in resultados_adt:
            system_points.append([resultado['caudal_lps'], resultado['adt_total']])
        
        return system_points
        
    except Exception as e:
        # Si hay error, crear una curva simple
        st.warning(f"Error calculando curva del sistema: {e}. Usando curva simple.")
        altura_estatica = params['altura_succion'] + params['altura_descarga']
        return [[0, altura_estatica], [max(flows), altura_estatica + 20]]

def load_excel_to_session_state(uploaded_file) -> bool:
    """
    Carga datos Excel al session_state y actualiza los textareas.
    
    Args:
        uploaded_file: Archivo Excel subido
    
    Returns:
        True si se cargó exitosamente, False en caso contrario
    """
    try:
        # Procesar el archivo Excel
        excel_data = process_excel_curves(uploaded_file)
        
        if not excel_data['success']:
            # Mostrar errores
            for error in excel_data['errors']:
                st.error(f"❌ {error}")
            return False
        
        # Mostrar advertencias
        for warning in excel_data['warnings']:
            st.warning(f"⚠️ {warning}")
        
        # Cargar datos en session_state
        curves = excel_data['curves']
        
        # Actualizar textareas
        for curve_key, textarea_content in curves.items():
            if curve_key.endswith('_textarea'):
                original_key = curve_key.replace('_textarea', '')
                textarea_key = f"textarea_{original_key}"
                st.session_state[textarea_key] = textarea_content
        
        # Crear curva del sistema automáticamente
        caudal_lps = st.session_state.get('caudal_lps', 51.0)
        system_params = {
            'long_succion': st.session_state.get('long_succion', 10.0),
            'diam_succion_mm': st.session_state.get('diam_succion_mm', 200.0),
            'mat_succion': st.session_state.get('mat_succion', 'PVC'),
            'otras_perdidas_succion': st.session_state.get('otras_perdidas_succion', 0.0),
            'accesorios_succion': st.session_state.get('accesorios_succion', []),
            'long_impulsion': st.session_state.get('long_impulsion', 500.0),
            'diam_impulsion_mm': st.session_state.get('diam_impulsion_mm', 150.0),
            'mat_impulsion': st.session_state.get('mat_impulsion', 'PVC'),
            'otras_perdidas_impulsion': st.session_state.get('otras_perdidas_impulsion', 0.0),
            'accesorios_impulsion': st.session_state.get('accesorios_impulsion', []),
            'altura_succion_input': st.session_state.get('altura_succion_input', 1.65),
            'altura_descarga': st.session_state.get('altura_descarga', 80.0)
        }
        
        sistema_points = create_system_curve_points(caudal_lps, system_params)
        
        # Crear texto para curva del sistema
        sistema_lines = []
        for point in sistema_points:
            sistema_lines.append(f"{point[0]:.2f} {point[1]:.2f}")
        sistema_textarea = "\n".join(sistema_lines)
        
        # Cargar curva del sistema en session_state
        st.session_state["textarea_sistema"] = sistema_textarea
        
        # Actualizar inputs específicos de curvas
        # Convertir puntos a la estructura esperada
        curva_inputs = {}
        for curve_key, points in curves.items():
            if not curve_key.endswith('_textarea'):
                curva_inputs[curve_key] = points
        
        # Agregar sistema
        curva_inputs['sistema'] = sistema_points
        
        st.session_state['curva_inputs'] = curva_inputs
        
        st.success(f"✅ Archivo Excel procesado exitosamente: {uploaded_file.name}")
        
        # Mostrar información de las curvs cargadas
        with st.expander("📊 Información de las Curvas Cargadas", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Curvas de la Bomba:**")
                for sheet_name, curve_key in [('H-Q', 'bomba'), ('Power', 'potencia'), ('Efficiency', 'rendimiento'), ('NPSH', 'npsh')]:
                    if curve_key in curves:
                        points = curves[curve_key]
                        st.markdown(f"- **{sheet_name}:** {len(points)} puntos (Caudal: {points[0][0]:.1f} - {points[-1][0]:.1f} L/s)")
            
            with col2:
                st.markdown("**Curva del Sistema:**")
                st.markdown(f"- **Sistema:** {len(sistema_points)} puntos (Caudal: {sistema_points[0][0]:.1f} - {sistema_points[-1][0]:.1f} L/s)")
                st.markdown(f"- **ADT:** {sistema_points[-1][1]:.1f} m (para caudal máximo)")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error procesando archivo Excel: {str(e)}")
        return False
