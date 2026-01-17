import streamlit as st
import json
import os
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False
import pandas as pd
import io

def configure_gemini(api_key=None):
    """Configura Gemini para generación de análisis
    
    Args:
        api_key: API key de Gemini (opcional). Si no se proporciona, intenta leer desde archivo secrets.
    """
    if not GEMINI_AVAILABLE:
        return None
    try:
        # Si no se proporciona API key, intentar leer desde archivo
        if not api_key:
            try:
                with open('secrets', 'r', encoding='utf-8') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if line.startswith('GEMINI_API_KEY='):
                            api_key = line.split('=', 1)[1].strip()
                            break
            except:
                pass
        
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            return model
        return None
    except Exception as e:
        st.error(f"Error configurando Gemini: {e}")
        return None

def generar_analisis_gemini(model, datos_prompt, tema):
    """Genera texto técnico con Gemini basado en datos del proyecto"""
    # (Esta función contendría la lógica completa de prompts)
    if not model:
        return "Análisis no disponible - Error de configuración"
    prompt = f"Analiza el siguiente tema: {tema} con los datos: {datos_prompt}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generando análisis: {str(e)}"

def is_valid_data(data):
    if data is None:
        return False
    if isinstance(data, list):
        return len(data) > 0
    if hasattr(data, 'empty'):
        return not data.empty
    if isinstance(data, str):
        return len(data.strip()) > 0
    return bool(data)

def parse_dataframe_string(df_string):
    """Convierte string de DataFrame a lista de diccionarios"""
    if not isinstance(df_string, str):
        return df_string
    try:
        df = pd.read_csv(io.StringIO(df_string), sep='\s+')
        return df.to_dict('records')
    except:
        return df_string

def extract_data_from_format(data):
    """Extrae datos de diferentes formatos posibles"""
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        return data
    elif isinstance(data, str):
        parsed = parse_dataframe_string(data)
        if isinstance(parsed, list):
            return parsed
    return []