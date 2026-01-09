# Módulo de integración de IA para análisis de sistemas de bombeo

import streamlit as st
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from config.settings import AppSettings

# --- INICIO: Bloque de diagnóstico ---
print("--- DIAGNÓSTICO DE ENTORNO ---")
print(f"Python Executable: {sys.executable}")
print("sys.path:")
for path in sys.path:
    print(f"  - {path}")
print("--- FIN: Bloque de diagnóstico ---")
# --- FIN: Bloque de diagnóstico ---

# Importar google.generativeai al nivel del módulo
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    print(f"OK: google-generativeai importado correctamente. Version: {genai.__version__}")
except ImportError as e:
    GEMINI_AVAILABLE = False
    genai = None
    print(f"ERROR: Error al importar google-generativeai: {e}")
except Exception as e:
    GEMINI_AVAILABLE = False
    genai = None
    print(f"ERROR: Error inesperado al importar google-generativeai: {e}")

# Configuración de carpetas
RESULTADOS_DIR = "resultados_para_IA"
TEMAS_DIR = "temas_ai"

# Crear carpetas si no existen
os.makedirs(RESULTADOS_DIR, exist_ok=True)
os.makedirs(TEMAS_DIR, exist_ok=True)


def cargar_preguntas_tema(tema: str) -> List[str]:
    """Carga las preguntas desde el archivo JSON del tema"""
    json_path = os.path.join(TEMAS_DIR, f"{tema}.json")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("preguntas", [])
    except FileNotFoundError:
        st.warning(f"Archivo {json_path} no encontrado.")
        return []
    except json.JSONDecodeError:
        st.error(f"Error al leer el archivo {json_path}. Verifica el formato JSON.")
        return []

def generar_informe_markdown(historial: List[Dict[str, str]]) -> str:
    """Genera un informe en Markdown a partir del historial del chat."""
    md_content = f"""# Análisis IA - Conversación de Desarrollador\n\n**Proyecto:** {st.session_state.get('proyecto', 'N/A')}\n**Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n---\n\n"""
    for item in historial:
        md_content += f"""**{item['tipo'].capitalize()} ({item['timestamp']})**\n\n{item['contenido']}\n\n---\n"""
    return md_content

def generar_informe_html(historial: List[Dict[str, str]]) -> str:
    """Genera un informe en HTML a partir del historial del chat con un estilo limpio y profesional."""
    import re
    import markdown

    # 1. Construir el cuerpo del HTML con la conversación
    html_body = ""
    for item in historial:
        raw_content = item['contenido']

        # --- INICIO DE CORRECCIONES COMPLETAS ---
        # Corrección 1: Asegurar que los marcadores de lista inicien en una nueva línea.
        content_con_saltos = re.sub(r'(?<!^)([*✅⚠️])', r'\n\1', raw_content)

        # Convertir Markdown a HTML
        contenido_html = markdown.markdown(content_con_saltos, extensions=['tables'])

        # Corrección 2: Mapeo de símbolos griegos LaTeX a caracteres Unicode
        greek_symbols = {
            r'\\rho': 'ρ',
            r'\\alpha': 'α',
            r'\\beta': 'β',
            r'\\gamma': 'γ',
            r'\\delta': 'δ',
            r'\\epsilon': 'ε',
            r'\\zeta': 'ζ',
            r'\\eta': 'η',
            r'\\theta': 'θ',
            r'\\iota': 'ι',
            r'\\kappa': 'κ',
            r'\\lambda': 'λ',
            r'\\mu': 'μ',
            r'\\nu': 'ν',
            r'\\xi': 'ξ',
            r'\\pi': 'π',
            r'\\sigma': 'σ',
            r'\\tau': 'τ',
            r'\\upsilon': 'υ',
            r'\\phi': 'φ',
            r'\\chi': 'χ',
            r'\\psi': 'ψ',
            r'\\omega': 'ω',
            r'\\Delta': 'Δ',
            r'\\Gamma': 'Γ',
            r'\\Lambda': 'Λ',
            r'\\Omega': 'Ω',
            r'\\Phi': 'Φ',
            r'\\Pi': 'Π',
            r'\\Sigma': 'Σ',
            r'\\Theta': 'Θ',
            r'\\Upsilon': 'Υ',
            r'\\Xi': 'Ξ',
            r'\\Psi': 'Ψ'
        }

        # Aplicar conversión de símbolos griegos
        for latex_symbol, unicode_char in greek_symbols.items():
            contenido_html = re.sub(latex_symbol, unicode_char, contenido_html)

        # Corrección 3: Eliminar TODOS los símbolos $ de LaTeX y convertir a negritas HTML
        # Patrón para variables simples: $variable$ -> <strong>variable</strong>
        contenido_html = re.sub(r'\$([^$]+)\$', r'<strong>\1</strong>', contenido_html)
        
        # Corrección 4: Convertir marcadores Markdown **texto** a <strong>texto</strong>
        contenido_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', contenido_html)
        
        # Corrección 5: Convertir marcadores Markdown __texto__ a <strong>texto</strong>
        contenido_html = re.sub(r'__(.*?)__', r'<strong>\1</strong>', contenido_html)

        # Corrección 6: Mejorar formato de tablas con bordes HTML
        # Reemplazar tablas Markdown básicas con HTML con bordes
        contenido_html = re.sub(
            r'<table>',
            '<table style="border-collapse: collapse; width: 100%; margin: 1em 0;">',
            contenido_html
        )
        
        # Aplicar estilos a encabezados de tabla
        contenido_html = re.sub(
            r'<th>',
            '<th style="border: 1px solid #ccc; padding: 8px; background-color: #f5f5f5; font-weight: bold;">',
            contenido_html
        )
        
        # Aplicar estilos a celdas de tabla
        contenido_html = re.sub(
            r'<td>',
            '<td style="border: 1px solid #ccc; padding: 8px;">',
            contenido_html
        )

        # Corrección 7: Resaltar palabras clave técnicas importantes (simplificado)
        technical_keywords = [
            'NPSH', 'cavitación', 'eficiencia', 'potencia', 'caudal', 'altura',
            'presión', 'velocidad', 'diámetro', 'longitud', 'pérdidas',
            'fricción', 'bomba', 'motor', 'impulsión', 'succión', 'total',
            'resultado', 'análisis', 'recomendación'
        ]
        
        for keyword in technical_keywords:
            # Resaltar palabras clave que no estén ya dentro de tags <strong>
            pattern = rf'\b({keyword})\b'
            contenido_html = re.sub(pattern, r'<strong>\1</strong>', contenido_html, flags=re.IGNORECASE)

        # Corrección 8: Limpieza completa de caracteres residuales
        # Eliminar comandos LaTeX residuales
        contenido_html = re.sub(r'\\[a-zA-Z]+', '', contenido_html)
        contenido_html = re.sub(r'\{|\}', '', contenido_html)  # Eliminar llaves residuales
        
        # Corrección 9: Limpieza completa de asteriscos residuales
        # Eliminar asteriscos sueltos que quedaron después de la conversión
        contenido_html = re.sub(r'\*+', '', contenido_html)  # Eliminar cualquier secuencia de asteriscos
        
        # Corrección 10: Limpiar elementos HTML malformados
        # Eliminar elementos vacíos o malformados que puedan haber quedado
        contenido_html = re.sub(r'<li>\s*\*+\s*</li>', '', contenido_html)  # Listas con solo asteriscos
        contenido_html = re.sub(r'<p>\s*\*+\s*</p>', '', contenido_html)  # Párrafos con solo asteriscos
        contenido_html = re.sub(r'<td>\s*\*+\s*</td>', '<td></td>', contenido_html)  # Celdas con solo asteriscos
        
        # Corrección 11: Limpiar espacios múltiples y líneas vacías
        contenido_html = re.sub(r'\s+', ' ', contenido_html)  # Múltiples espacios a uno solo
        contenido_html = re.sub(r'>\s+<', '><', contenido_html)  # Espacios entre tags
        
        # Corrección 12: Limpiar elementos de lista malformados
        # Eliminar elementos de lista que solo contienen asteriscos o están vacíos
        contenido_html = re.sub(r'<li>\s*</li>', '', contenido_html)  # Listas vacías
        contenido_html = re.sub(r'<li>\s*\*+\s*</li>', '', contenido_html)  # Listas con asteriscos
        
        # Corrección 13: Limpiar texto residual de Markdown
        # Eliminar patrones residuales de Markdown que puedan haber quedado
        contenido_html = re.sub(r'\*\s*\*', '', contenido_html)  # Asteriscos separados
        contenido_html = re.sub(r'_\s*_', '', contenido_html)  # Guiones bajos separados
        
        # --- FIN DE CORRECCIONES COMPLETAS ---

        if item['tipo'] == 'pregunta':
            html_body += f"""<div class="pregunta">
<h3>Pregunta <span class="timestamp">({item['timestamp']})</span></h3>
<p><strong>{item['contenido']}</strong></p>
</div>"""
        else:
            html_body += f"""<div class="respuesta">
<h4>Análisis Técnico <span class="timestamp">({item['timestamp']})</span></h4>
{contenido_html}
</div>"""

    # 2. Definir la plantilla HTML completa con el CSS
    full_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Análisis IA - Conversación de Desarrollador</title>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.7; color: #333; background-color: #fff; }}
        h1, h2, h3, h4, h5, h6 {{ color: #111; font-weight: 600; margin-top: 2.5em; margin-bottom: 1em; }}
        h1 {{ font-size: 2em; border-bottom: 1px solid #ddd; padding-bottom: 0.4em; }}
        h3 {{ font-size: 1.4em; }}
        h4 {{ font-size: 1.1em; color: #555; font-weight: 700; }}
        p {{ margin-bottom: 1.2em; }}
        ul, ol {{ padding-left: 25px; margin-bottom: 1.2em; }}
        li {{ margin-bottom: 0.6em; }}
        strong, b {{ font-weight: 600; color: #000; }}
        .timestamp {{ font-size: 0.8em; color: #888; font-weight: normal; }}
        .pregunta, .respuesta {{ margin-bottom: 2.5em; padding-bottom: 1.5em; border-bottom: 1px solid #eee; }}
        .pregunta p strong {{ font-size: 1.1em; color: #0056b3; }}
        .MathJax_Display, .latex-block {{ text-align: center; margin: 2em auto !important; padding: 1em; background-color: #f8f9fa; border-radius: 4px; font-size: 1.1em; overflow-x: auto; border: 1px solid #e9ecef; }}
    </style>
</head>
<body>
    <header>
        <h1>Análisis IA</h1>
        <p><strong>Proyecto:</strong> {st.session_state.get('proyecto', 'N/A')} | <strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
    </header>
    <main>
        {html_body}
    </main>
</body>
</html>"""
    return full_html



def generar_datos_json() -> Dict[str, Any]:
    """
    Genera el JSON con los datos actuales de entrada y resultados de la app,
    leyendo directamente desde st.session_state para asegurar consistencia.
    Incluye TODOS los datos: inputs, resultados, curvas, materiales específicos, etc.
    """
    
    # Helper function to get values intelligently from session_state
    def get_session_value(primary_key: str, alternative_keys: list = None, default=0.0):
        """
        Busca un valor en session_state, probando múltiples claves.
        Prioriza valores != 0 para evitar falsos "no datos"
        """
        if alternative_keys is None:
            alternative_keys = []
        
        # Intentar primero con la  clave principal
        value = st.session_state.get(primary_key, None)
        
        # Si es None o 0, buscar en las alternativas
        if (value is None or value == 0 or value == 0.0 or value == ''):
            for alt_key in alternative_keys:
                alt_value = st.session_state.get(alt_key, None)
                if alt_value is not None and alt_value != 0 and alt_value != 0.0 and alt_value != '':
                    return alt_value
        
        # Si encontramos un valor válido en la clave principal, usarlo
        if value is not None:
            return value
            
        # Si todo falló, retornar el default
        return default
    
    
    # --- RECOPILACIÓN COMPLETA DE INPUTS DESDE SESSION_STATE ---
    inputs = {
        # Información del proyecto
        "proyecto": st.session_state.get('proyecto', ''),
        "diseno": st.session_state.get('diseno', ''),
        "proyecto_input_main": st.session_state.get('proyecto_input_main', ''),
        "diseno_input_main": st.session_state.get('diseno_input_main', ''),
        "ajuste_tipo": st.session_state.get('ajuste_tipo', 'Cuadrática (2do grado)'),
        "curva_mode": st.session_state.get('curva_mode', '3 puntos'),
        "flow_unit": st.session_state.get('flow_unit', 'L/s'),
        
        # Condiciones de Operación
        "caudal_diseno_lps": get_session_value('caudal_lps', ['caudal_diseno_lps', 'caudal_nominal'], 0.0),
        "caudal_diseno_m3h": get_session_value('caudal_m3h', ['caudal_diseno_m3h'], 0.0),
        "elevacion_sitio": get_session_value('elevacion_sitio', ['elevacion'], 0.0),
        "altura_succion": get_session_value('altura_succion_input', ['altura_succion', 'h_succion'], 0.0),
        "altura_descarga": get_session_value('altura_descarga', ['h_descarga', 'h_estatica'], 0.0),
        "num_bombas_paralelo": st.session_state.get('num_bombas', 1),
        "bomba_inundada": st.session_state.get('bomba_inundada', False),
        
        # Parámetros físicos y ambientales
        "temperatura": st.session_state.get('temp_liquido', 20.0),
        "densidad_liquido": st.session_state.get('densidad_liquido', 1.0),
        "presion_vapor_calculada": st.session_state.get('presion_vapor_calculada', 0.0),
        "presion_barometrica_calculada": st.session_state.get('presion_barometrica_calculada', 0.0),
        
        # Tubería de Succión - DATOS COMPLETOS
        "succion": {
            "longitud": st.session_state.get('long_succion', 0.0),
            "material": st.session_state.get('mat_succion', ''),
            "diametro_nominal": st.session_state.get('diam_succion_mm', 0.0),
            "diametro_externo": st.session_state.get('diam_externo_succion', 0.0),
            "diametro_interno": st.session_state.get('diam_interno_succion', 0.0),
            "espesor": st.session_state.get('espesor_succion', 0.0),
            "coeficiente_hazen": st.session_state.get('coeficiente_hazen_succion', 0),
            "otras_perdidas": st.session_state.get('otras_perdidas_succion', 0.0),
            "accesorios": st.session_state.get('accesorios_succion', []),
            # Campos específicos de material PEAD
            "serie_pead": st.session_state.get('serie_succion', ''),
            "sdr_pead": st.session_state.get('sdr_succion', 0),
            "presion_nominal_pead": st.session_state.get('presion_nominal_succion', 0.0),
            # Campos específicos de material Hierro Dúctil
            "clase_hierro": st.session_state.get('clase_hierro_succion', ''),
            "dn_hierro": st.session_state.get('dn_succion', ''),
            # Campos específicos de material Hierro Fundido
            "clase_hf": st.session_state.get('clase_hierro_fundido_succion', ''),
            "dn_hf": st.session_state.get('dn_hierro_fundido_succion', ''),
            # Campos específicos de material PVC
            "union_pvc": st.session_state.get('tipo_union_pvc_succion', ''),
            "serie_pvc": st.session_state.get('serie_pvc_succion_nombre', ''),
            "dn_pvc": st.session_state.get('dn_pvc_succion', ''),
        },
        
        # Tubería de Impulsión - DATOS COMPLETOS
        "impulsion": {
            "longitud": st.session_state.get('long_impulsion', 0.0),
            "material": st.session_state.get('mat_impulsion', ''),
            "diametro_nominal": st.session_state.get('diam_impulsion_mm', 0.0),
            "diametro_externo": st.session_state.get('diam_externo_impulsion', 0.0),
            "diametro_interno": st.session_state.get('diam_interno_impulsion', 0.0),
            "espesor": st.session_state.get('espesor_impulsion', 0.0),
            "coeficiente_hazen": st.session_state.get('coeficiente_hazen_impulsion', 0),
            "otras_perdidas": st.session_state.get('otras_perdidas_impulsion', 0.0),
            "accesorios": st.session_state.get('accesorios_impulsion', []),
            # Campos específicos de material PEAD
            "serie_pead": st.session_state.get('serie_impulsion', ''),
            "sdr_pead": st.session_state.get('sdr_impulsion', 0),
            "presion_nominal_pead": st.session_state.get('presion_nominal_impulsion', 0.0),
            # Campos específicos de material Hierro Dúctil
            "clase_hierro": st.session_state.get('clase_hierro_impulsion', ''),
            "dn_hierro": st.session_state.get('dn_impulsion', ''),
            # Campos específicos de material Hierro Fundido
            "clase_hf": st.session_state.get('clase_hierro_fundido_impulsion', ''),
            "dn_hf": st.session_state.get('dn_hierro_fundido_impulsion', ''),
            # Campos específicos de material PVC
            "union_pvc": st.session_state.get('tipo_union_pvc_impulsion', ''),
            "serie_pvc": st.session_state.get('serie_pvc_impulsion_nombre', ''),
            "dn_pvc": st.session_state.get('dn_pvc_impulsion', ''),
        },
        
        # Curvas - DATOS COMPLETOS (puntos y texto)
        "curvas_puntos": {
            "sistema": st.session_state.get('curva_sistema', []),
            "bomba": st.session_state.get('curva_bomba', []),
            "rendimiento": st.session_state.get('curva_eficiencia', []),
            "potencia": st.session_state.get('curva_potencia', []),
            "npsh": st.session_state.get('curva_npsh', [])
        },
        "curvas_texto": {
            "sistema": st.session_state.get('textarea_sistema', ''),
            "bomba": st.session_state.get('textarea_bomba', ''),
            "rendimiento": st.session_state.get('textarea_rendimiento', ''),
            "potencia": st.session_state.get('textarea_potencia', ''),
            "npsh": st.session_state.get('textarea_npsh', '')
        },
        
        # Datos VFD - COMPLETOS
        "vfd": {
            "rpm_percentage": st.session_state.get('rpm_percentage', 75.0),
            "paso_caudal_vfd": st.session_state.get('paso_caudal_vfd', 5.0),
            "curvas_vfd": st.session_state.get('curvas_vfd', {}),
            "caudal_nominal": st.session_state.get('caudal_nominal', st.session_state.get('caudal_lps', 0.0)),
            "caudal_diseno_lps": st.session_state.get('caudal_lps', 0.0),
            "caudal_diseno_m3h": st.session_state.get('caudal_m3h', 0.0),
            "nota": "El caudal nominal VFD es igual al caudal de diseño del sistema"
        },
        
        # Caudales personalizados para ADT
        "adt_caudales_personalizados": st.session_state.get('adt_caudales_personalizados', [0, 51.0, 70]),
        
        # Información de bomba seleccionada - COMPLETA
        "bomba_seleccionada": {
            "url": st.session_state.get('bomba_url', ''),
            "nombre": st.session_state.get('bomba_nombre', ''),
            "descripcion": st.session_state.get('bomba_descripcion', '')
        },
        
        # Motor - DATOS COMPLETOS
        "motor": {
            "tension": st.session_state.get('tension', 0.0),
            "rpm": st.session_state.get('rpm', 0.0)
        },
        
        # Datos adicionales del proyecto
        "curva_inputs": st.session_state.get('curva_inputs', {}),
        "calibration_points": st.session_state.get('calibration_points', None),
        "digitalized_points": st.session_state.get('digitalized_points', []),
        
        # === CAMPOS A NIVEL RAÍZ PARA COMPATIBILIDAD CON load_project_state ===
        # Esto permite que el JSON descargado pueda cargarse correctamente
        "accesorios_succion": st.session_state.get('accesorios_succion', []),
        "accesorios_impulsion": st.session_state.get('accesorios_impulsion', []),
        "long_succion": st.session_state.get('long_succion', 0.0),
        "long_impulsion": st.session_state.get('long_impulsion', 0.0),
        "diam_succion_mm": st.session_state.get('diam_succion_mm', 0.0),
        "diam_impulsion_mm": st.session_state.get('diam_impulsion_mm', 0.0),
        "mat_succion": st.session_state.get('mat_succion', ''),
        "mat_impulsion": st.session_state.get('mat_impulsion', ''),
        "otras_perdidas_succion": st.session_state.get('otras_perdidas_succion', 0.0),
        "otras_perdidas_impulsion": st.session_state.get('otras_perdidas_impulsion', 0.0),
        "caudal_lps": get_session_value('caudal_lps', ['caudal_diseno_lps', 'caudal_nominal'], 0.0),
        "caudal_m3h": get_session_value('caudal_m3h', ['caudal_diseno_m3h'], 0.0),
        "altura_succion_input": st.session_state.get('altura_succion_input', 0.0),
        "altura_descarga": st.session_state.get('altura_descarga', 0.0),
        "elevacion_sitio": st.session_state.get('elevacion_sitio', 0.0),
        "num_bombas": st.session_state.get('num_bombas', 1),
        "bomba_inundada": st.session_state.get('bomba_inundada', False),
        "temp_liquido": st.session_state.get('temp_liquido', 20.0),
        "densidad_liquido": st.session_state.get('densidad_liquido', 1.0),
        "presion_barometrica_calculada": st.session_state.get('presion_barometrica_calculada', 0.0),
        "presion_vapor_calculada": st.session_state.get('presion_vapor_calculada', 0.0),
        "rpm_percentage": st.session_state.get('rpm_percentage', 75.0),
        "curvas_vfd": st.session_state.get('curvas_vfd', {}),
        "caudal_nominal": st.session_state.get('caudal_nominal', 0.0),
        "paso_caudal_vfd": st.session_state.get('paso_caudal_vfd', 5.0),
        "adt_caudales_personalizados": st.session_state.get('adt_caudales_personalizados', []),
        # Datos específicos de materiales - Succión
        "diam_externo_succion": st.session_state.get('diam_externo_succion', None),
        "diam_externo_succion_index": st.session_state.get('diam_externo_succion_index', 0),
        "serie_succion": st.session_state.get('serie_succion', None),
        "serie_succion_index": st.session_state.get('serie_succion_index', 0),
        "clase_hierro_succion": st.session_state.get('clase_hierro_succion', None),
        "clase_hierro_succion_index": st.session_state.get('clase_hierro_succion_index', 0),
        "dn_succion": st.session_state.get('dn_succion', None),
        "dn_succion_index": st.session_state.get('dn_succion_index', 0),
        # Datos específicos de materiales - Impulsión
        "diam_externo_impulsion": st.session_state.get('diam_externo_impulsion', None),
        "diam_externo_impulsion_index": st.session_state.get('diam_externo_impulsion_index', 0),
        "serie_impulsion": st.session_state.get('serie_impulsion', None),
        "serie_impulsion_index": st.session_state.get('serie_impulsion_index', 0),
        "clase_hierro_impulsion": st.session_state.get('clase_hierro_impulsion', None),
        "clase_hierro_impulsion_index": st.session_state.get('clase_hierro_impulsion_index', 0),
        "dn_impulsion": st.session_state.get('dn_impulsion', None),
        "dn_impulsion_index": st.session_state.get('dn_impulsion_index', 0),
        # Datos específicos de materiales - Hierro Fundido Succión
        "clase_hierro_fundido_succion": st.session_state.get('clase_hierro_fundido_succion', None),
        "clase_hierro_fundido_succion_index": st.session_state.get('clase_hierro_fundido_succion_index', 0),
        "dn_hierro_fundido_succion": st.session_state.get('dn_hierro_fundido_succion', None),
        "dn_hierro_fundido_succion_index": st.session_state.get('dn_hierro_fundido_succion_index', 0),
        # Datos específicos de materiales - Hierro Fundido Impulsión
        "clase_hierro_fundido_impulsion": st.session_state.get('clase_hierro_fundido_impulsion', None),
        "clase_hierro_fundido_impulsion_index": st.session_state.get('clase_hierro_fundido_impulsion_index', 0),
        "dn_hierro_fundido_impulsion": st.session_state.get('dn_hierro_fundido_impulsion', None),
        "dn_hierro_fundido_impulsion_index": st.session_state.get('dn_hierro_fundido_impulsion_index', 0),
        # Datos específicos de materiales - PVC Succión
        "tipo_union_pvc_succion": st.session_state.get('tipo_union_pvc_succion', None),
        "tipo_union_pvc_succion_index": st.session_state.get('tipo_union_pvc_succion_index', 0),
        "serie_pvc_succion_nombre": st.session_state.get('serie_pvc_succion_nombre', None),
        "serie_pvc_succion_nombre_index": st.session_state.get('serie_pvc_succion_nombre_index', 0),
        "dn_pvc_succion": st.session_state.get('dn_pvc_succion', None),
        "dn_pvc_succion_index": st.session_state.get('dn_pvc_succion_index', 0),
        # Datos específicos de materiales - PVC Impulsión
        "tipo_union_pvc_impulsion": st.session_state.get('tipo_union_pvc_impulsion', None),
        "tipo_union_pvc_impulsion_index": st.session_state.get('tipo_union_pvc_impulsion_index', 0),
        "serie_pvc_impulsion_nombre": st.session_state.get('serie_pvc_impulsion_nombre', None),
        "serie_pvc_impulsion_nombre_index": st.session_state.get('serie_pvc_impulsion_nombre_index', 0),
        "dn_pvc_impulsion": st.session_state.get('dn_pvc_impulsion', None),
        "dn_pvc_impulsion_index": st.session_state.get('dn_pvc_impulsion_index', 0),
        
        # Textareas de curvas - CRÍTICO para que las curvas se carguen correctamente
        "textarea_bomba": st.session_state.get('textarea_bomba', ''),
        "textarea_rendimiento": st.session_state.get('textarea_rendimiento', ''),
        "textarea_potencia": st.session_state.get('textarea_potencia', ''),
        "textarea_npsh": st.session_state.get('textarea_npsh', ''),
        "textarea_sistema": st.session_state.get('textarea_sistema', ''),
    }
    
    # --- RECOPILACIÓN DE RESULTADOS DESDE SESSION_STATE ---
    # Se leen todos los resultados calculados previamente por la app.
    # NO se recalcula nada para garantizar la consistencia de los datos.
    
    resultados = {
        "succion": {
            "velocidad": st.session_state.get('velocidad_succion', 0.0),
            "perdida_primaria": st.session_state.get('hf_primaria_succion', 0.0),
            "perdida_secundaria": st.session_state.get('hf_secundaria_succion', 0.0),
            "long_equiv_accesorios": st.session_state.get('le_total_succion', 0.0),
            "perdida_total": st.session_state.get('perdida_total_succion', 0.0),
            "altura_dinamica": st.session_state.get('altura_dinamica_succion', 0.0)
        },
        "impulsion": {
            "velocidad": st.session_state.get('velocidad_impulsion', 0.0),
            "perdida_primaria": st.session_state.get('hf_primaria_impulsion', 0.0),
            "perdida_secundaria": st.session_state.get('hf_secundaria_impulsion', 0.0),
            "long_equiv_accesorios": st.session_state.get('le_total_impulsion', 0.0),
            "perdida_total": st.session_state.get('perdida_total_impulsion', 0.0),
            "altura_dinamica": st.session_state.get('altura_dinamica_impulsion', 0.0)
        },
        "npsh": {
            "disponible": st.session_state.get('npshd_mca', 0.0),
            "requerido": st.session_state.get('npsh_requerido', 0.0),
            "margen": st.session_state.get('npsh_margen', 0.0)
        },
        "alturas": {
            "estatica_total": st.session_state.get('altura_estatica_total', 0.0),
            "perdidas_totales": st.session_state.get('perdidas_totales_sistema', 0.0),
            "dinamica_total": st.session_state.get('adt_total', 0.0)
        },
        "motor_bomba": {
            "potencia_hidraulica_kw": st.session_state.get('potencia_hidraulica_kw', 0.0),
            "potencia_hidraulica_hp": st.session_state.get('potencia_hidraulica_hp', 0.0),
            "potencia_motor_kw": st.session_state.get('potencia_motor_kw', 0.0),
            "potencia_motor_hp": st.session_state.get('potencia_motor_hp', 0.0),
            "potencia_motor_final_kw": st.session_state.get('potencia_motor_final_kw', 0.0),
            "potencia_motor_final_hp": st.session_state.get('potencia_motor_final_hp', 0.0),
            "motor_seleccionado": st.session_state.get('motor_seleccionado', {}),
            "corriente_nominal": st.session_state.get('corriente_nominal', 0.0),
        },
        "punto_operacion": {
            "caudal": get_session_value('caudal_operacion', ['interseccion', 'caudal_interseccion', 'Q_operacion'], 0.0),
            "altura": get_session_value('altura_operacion', ['H_operacion', 'altura_interseccion'], 0.0),
            "eficiencia": get_session_value('eficiencia_operacion', ['rendimiento_operacion', 'eta_operacion'], 0.0),
            "potencia": get_session_value('potencia_operacion', ['P_operacion', 'BHP_operacion'], 0.0),
            # Datos de intersección de curvas
            "interseccion": st.session_state.get('interseccion', None),
            "interseccion_texto": st.session_state.get('interseccion_texto', ''),
        },
        "analisis_vdf": {
            # Calcular caudal nominal VFD (usar caudal de diseño como base)
            "caudal_nominal_vdf": st.session_state.get('caudal_nominal_vdf', st.session_state.get('caudal_lps', 0.0)),
            "caudal_diseno_lps": st.session_state.get('caudal_lps', 0.0),
            "caudal_diseno_m3h": st.session_state.get('caudal_m3h', 0.0),
            
            # Calcular potencia ajustada usando leyes de afinidad: P ∝ N³
            "potencia_ajustada": st.session_state.get('potencia_ajustada', 
                st.session_state.get('potencia_motor_final_hp', 0.0) * 
                ((st.session_state.get('rpm_percentage', 100.0) / 100.0) ** 3)),
            
            # Calcular eficiencia ajustada (aproximadamente constante)
            "eficiencia_ajustada": st.session_state.get('eficiencia_ajustada', 
                st.session_state.get('motor_seleccionado', {}).get('eficiencia_porcentaje', 
                st.session_state.get('eficiencia_operacion', 0.0))),
            
            "rpm_porcentaje": st.session_state.get('rpm_percentage', 100.0),
            "potencia_motor_kw": st.session_state.get('potencia_motor_kw', 0.0),
            "potencia_motor_hp": st.session_state.get('potencia_motor_hp', 0.0),
            "potencia_motor_final_hp": st.session_state.get('potencia_motor_final_hp', 0.0),
            "eficiencia_operacion": st.session_state.get('eficiencia_operacion', 0.0),
            
            # Datos adicionales para análisis VFD
            "factor_rpm": st.session_state.get('rpm_percentage', 100.0) / 100.0,
            "nota_calculo": "Potencia ajustada calculada usando leyes de afinidad: P ∝ N³",
            
            # Intersección VFD (si está disponible)
            "interseccion_vfd": st.session_state.get('interseccion_vfd', None),
            "caudal_interseccion_vfd": st.session_state.get('caudal_interseccion_vfd', 0.0),
            "altura_interseccion_vfd": st.session_state.get('altura_interseccion_vfd', 0.0)
        },
        "resumen": {
            "altura_estatica_total": get_session_value('altura_estatica_total', ['h_estatica_total'], 0.0),
            "perdidas_totales": get_session_value('perdidas_totales_sistema', ['hf_total', 'perdidas_totales'], 0.0),
            "altura_dinamica_total": get_session_value('adt_total', ['ADT', 'TDH', 'altura_dinamica_total'], 0.0),
            "caudal_diseno": get_session_value('caudal_lps', ['caudal_diseno_lps', 'caudal_nominal'], 0.0),
            "caudal_diseno_m3h": get_session_value('caudal_m3h', ['caudal_diseno_m3h'], 0.0),
            "num_bombas": st.session_state.get('num_bombas', 1),
            "caudal_nominal_vfd": get_session_value('caudal_nominal_vdf', ['caudal_lps'], 0.0),
            # Punto de operación calculado
            "punto_operacion_Q": st.session_state.get('interseccion', [0, 0])[0] if st.session_state.get('interseccion') else 0.0,
            "punto_operacion_H": st.session_state.get('interseccion', [0, 0])[1] if st.session_state.get('interseccion') and len(st.session_state.get('interseccion', [])) > 1 else 0.0,
            "nota_vfd": "El caudal nominal VFD corresponde al caudal de diseño del sistema"
        }
    }
    
    # --- TABLAS DE GRÁFICOS RPM (DATOS CRÍTICOS PARA EXCEL E INFORMES) ---
    # Función para convertir DataFrame a diccionario serializable
    def dataframe_to_dict(df):
        """Convierte un DataFrame de pandas a un diccionario serializable"""
        if df is None or df.empty:
            return None
        try:
            # Convertir DataFrame a diccionario con orient='records' para mantener estructura
            return {
                "data": df.to_dict('records'),
                "columns": df.columns.tolist(),
                "index": df.index.tolist(),
                "shape": df.shape,
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
            }
        except Exception as e:
            # Si hay error, convertir a string como fallback
            return {"error": f"Error al convertir DataFrame: {str(e)}", "data": str(df)}
    
    # Función para obtener configuración de tablas con valores inteligentes
    def get_table_config(table_type="100"):
        """Obtiene la configuración de las tablas con valores inteligentes por defecto"""
        caudal_diseno = st.session_state.get('caudal_lps', 51.0)
        
        if table_type == "100":
            # Configuración para tablas 100% RPM
            q_min = st.session_state.get('q_min_100_tab2', 0.0)
            q_max = st.session_state.get('q_max_100_tab2', caudal_diseno)
            
            # Calcular paso automático basado en Q max si no está configurado
            if 'paso_caudal_100_tab2' not in st.session_state:
                if q_max < 10:
                    paso_auto = 0.25
                elif q_max < 20:
                    paso_auto = 1.0
                elif q_max < 40:
                    paso_auto = 2.5
                elif q_max < 100:
                    paso_auto = 5.0
                else:
                    paso_auto = 10.0
            else:
                paso_auto = st.session_state.get('paso_caudal_100_tab2', 5.0)
            
            return {
                "q_min_100": q_min,
                "q_max_100": q_max,
                "paso_caudal_100": paso_auto,
                "ajuste_tipo": st.session_state.get('ajuste_tipo', 'Cuadrática (2do grado)'),
                "flow_unit": st.session_state.get('flow_unit', 'L/s'),
                "nota_config": "Valores de configuración de las tablas a 100% RPM"
            }
        else:
            # Configuración para tablas VFD
            q_min = st.session_state.get('q_min_vdf_tab2', 0.0)
            q_max = st.session_state.get('q_max_vdf_tab2', caudal_diseno)
            
            # Calcular paso automático basado en Q max si no está configurado
            if 'paso_caudal_vdf_tab2' not in st.session_state:
                if q_max < 10:
                    paso_auto = 0.25
                elif q_max < 20:
                    paso_auto = 1.0
                elif q_max < 40:
                    paso_auto = 2.5
                elif q_max < 100:
                    paso_auto = 5.0
                else:
                    paso_auto = 10.0
            else:
                paso_auto = st.session_state.get('paso_caudal_vdf_tab2', 5.0)
            
            return {
                "rpm_percentage": st.session_state.get('rpm_percentage', 75.0),
                "q_min_vdf": q_min,
                "q_max_vdf": q_max,
                "paso_caudal_vdf": paso_auto,
                "ajuste_tipo": st.session_state.get('ajuste_tipo', 'Cuadrática (2do grado)'),
                "flow_unit": st.session_state.get('flow_unit', 'L/s'),
                "nota_config": "Valores de configuración de las tablas VFD"
            }
    
    # Incluir todas las tablas de gráficos a 100% RPM y VFD
    tablas_graficos = {
        "tablas_100_rpm": {
            "df_bomba_100": dataframe_to_dict(st.session_state.get('df_bomba_100', None)),
            "df_rendimiento_100": dataframe_to_dict(st.session_state.get('df_rendimiento_100', None)),
            "df_potencia_100": dataframe_to_dict(st.session_state.get('df_potencia_100', None)),
            "df_npsh_100": dataframe_to_dict(st.session_state.get('df_npsh_100', None)),
            "df_sistema_100": dataframe_to_dict(st.session_state.get('df_sistema_100', None)),
            "configuracion": get_table_config("100"),
            "nota": "Tablas de gráficos a 100% RPM para exportación a Excel e informes Word"
        },
        "tablas_vfd_rpm": {
            "df_bomba_vfd": dataframe_to_dict(st.session_state.get('df_bomba_vfd', None)),
            "df_rendimiento_vfd": dataframe_to_dict(st.session_state.get('df_rendimiento_vfd', None)),
            "df_potencia_vfd": dataframe_to_dict(st.session_state.get('df_potencia_vfd', None)),
            "df_npsh_vfd": dataframe_to_dict(st.session_state.get('df_npsh_vfd', None)),
            "df_sistema_vfd": dataframe_to_dict(st.session_state.get('df_sistema_vfd', None)),
            "configuracion": get_table_config("vfd"),
            "nota": f"Tablas de gráficos a {st.session_state.get('rpm_percentage', 75.0):.2f}% RPM para exportación a Excel e informes Word"
        }
    }
    
    # Incluir todos los campos adicionales que podrían estar en session_state
    datos_adicionales = {}
    
    # --- CURVAS EXPLÍCITAS (CRÍTICO PARA IA) ---
    curvas = {
        "curva_bomba": {
            "puntos_hq": st.session_state.get('curva_hq_puntos', st.session_state.get('pump_curve_data', [])),
            "coeficientes_hq": st.session_state.get('coef_hq', st.session_state.get('pump_curve_coeffs', [])),
            "puntos_eficiencia": st.session_state.get('curva_eficiencia_puntos', []),
            "coeficientes_eficiencia": st.session_state.get('coef_eficiencia', []),
            "puntos_potencia": st.session_state.get('curva_potencia_puntos', []),
            "coeficientes_potencia": st.session_state.get('coef_potencia', []),
            "puntos_npsh": st.session_state.get('curva_npsh_puntos', []),
            "coeficientes_npsh": st.session_state.get('coef_npsh', []),
        },
        "curva_sistema": {
            "puntos_adt": st.session_state.get('curva_sistema_puntos', st.session_state.get('adt_resultados', [])),
            "altura_estatica": get_session_value('altura_estatica_total', ['h_estatica_total'], 0.0),
            "coeficientes": st.session_state.get('coef_sistema', []),
        },
        "interseccion": {
            "punto": st.session_state.get('interseccion', None),
            "caudal_lps": st.session_state.get('interseccion', [0])[0] if st.session_state.get('interseccion') else 0.0,
            "altura_m": st.session_state.get('interseccion', [0, 0])[1] if st.session_state.get('interseccion') and len(st.session_state.get('interseccion', [])) > 1 else 0.0,
            "eficiencia_pct": st.session_state.get('eficiencia_interseccion', 0.0),
            "potencia_hp": st.session_state.get('potencia_interseccion', 0.0),
        },
        "curvas_vfd": st.session_state.get('curvas_vfd', {}),
    }
    
    # Recopilar todos los campos de session_state que no estén ya incluidos
    campos_existentes = set()
    
    # Agregar campos de inputs
    for key in inputs.keys():
        if isinstance(inputs[key], dict):
            campos_existentes.update(inputs[key].keys())
        else:
            campos_existentes.add(key)
    
    # Agregar campos de resultados
    for key in resultados.keys():
        if isinstance(resultados[key], dict):
            campos_existentes.update(resultados[key].keys())
        else:
            campos_existentes.add(key)
    
    # --- CAPTURA COMPLETA DE SESSION_STATE ---
    # Incluir TODOS los campos relevantes, no excluir nada importante
    campos_criticos = [
        'caudal_lps', 'caudal_m3h', 'caudal_nominal', 'caudal_por_bomba',
        'altura_estatica_total', 'adt_total', 'ADT', 'TDH',
        'velocidad_succion', 'velocidad_impulsion',
        'hf_primaria_succion', 'hf_primaria_impulsion',
        'hf_secundaria_succion', 'hf_secundaria_impulsion',
        'perdida_total_succion', 'perdida_total_impulsion',
        'npshd_mca', 'npsh_requerido', 'npsh_margen',
        'potencia_hidraulica_kw', 'potencia_hidraulica_hp',
        'potencia_motor_kw', 'potencia_motor_hp',
        'potencia_motor_final_kw', 'potencia_motor_final_hp',
        'motor_seleccionado', 'bomba_seleccionada',
        'eficiencia_operacion', 'rendimiento_bomba',
        'interseccion', 'caudal_operacion', 'altura_operacion',
        'rpm_percentage', 'num_bombas',
        'long_succion', 'long_impulsion',
        'diam_interno_succion', 'diam_interno_impulsion',
        'coeficiente_hazen_succion', 'coeficiente_hazen_impulsion',
        'mat_succion', 'mat_impulsion',
        'curva_inputs', 'pump_curve_data', 'adt_resultados',
    ]
    
    # Capturar campos críticos explícitamente
    for campo in campos_criticos:
        if campo in st.session_state and campo not in campos_existentes:
            value = st.session_state[campo]
            if value is not None:
                try:
                    if hasattr(value, 'to_dict') and hasattr(value, 'columns'):
                        datos_adicionales[campo] = dataframe_to_dict(value)
                    else:
                        import json
                        json.dumps(value)
                        datos_adicionales[campo] = value
                except (TypeError, ValueError):
                    datos_adicionales[campo] = str(value)
    
    # Recopilar campos adicionales de session_state (los que no son críticos pero podrían ser útiles)
    for key, value in st.session_state.items():
        if (key not in campos_existentes and 
            key not in datos_adicionales and
            key not in campos_criticos and
            not key.startswith('_') and
            not key.startswith('FormSubmitter') and
            key not in ['ai_enabled', 'init_done']):
            
            if value is not None:
                try:
                    if hasattr(value, 'to_dict') and hasattr(value, 'columns'):
                        datos_adicionales[key] = dataframe_to_dict(value)
                    else:
                        import json
                        json.dumps(value)
                        datos_adicionales[key] = value
                except (TypeError, ValueError):
                    datos_adicionales[key] = str(value)
    
    # Agregar todos los textareas al nivel raíz (CRÍTICO para carga)
    textareas = {}
    for key in st.session_state:
        if key.startswith('textarea_'):
            textareas[key] = st.session_state[key]
    
    # Build final return including flat textareas
    resultado_final = {
        "inputs": inputs,
        "resultados": resultados,
        "curvas": curvas,  # NUEVO: Curvas explícitas para IA
        "tablas_graficos": tablas_graficos,
        "datos_adicionales": datos_adicionales,
        "metadata": {
            "fecha_generacion": st.session_state.get('fecha_generacion', ''),
            "version_app": "1.0",
            "total_campos": len(campos_existentes) + len(datos_adicionales),
            "campos_session_state": len(st.session_state),
            "nota": "JSON generado con captura completa de session_state para análisis IA preciso"
        }
    }
    
    # Agregar textareas a nivel raíz para compatibilidad con load_project_state
    resultado_final.update(textareas)
    
    # También agregar campos de inputs a nivel raíz para compatibilidad
    for key, value in inputs.items():
        if not isinstance(value, dict) and key not in resultado_final:
            resultado_final[key] = value
    
    return resultado_final


# Función eliminada - ya no se usa JSON, se usan datos directos de st.session_state

def guardar_json_resultados(datos_json: Dict[str, Any]) -> str:
    """Guarda el JSON en la carpeta resultados_para_IA con un nombre fijo"""
    json_path = os.path.join(RESULTADOS_DIR, "resultados_para_IA.json")
    
    # Agregar marca de tiempo
    from datetime import datetime
    datos_json["metadata"]["fecha_generacion"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(datos_json, f, indent=4, ensure_ascii=False)
        return json_path
    except Exception as e:
        st.error(f"Error al guardar JSON: {e}")
        return ""

def configurar_gemini_api(api_key: str, model_name: str = 'gemini-2.5-flash') -> bool:
    """Configura la API de Gemini con la clave proporcionada"""
    if not GEMINI_AVAILABLE:
        st.error("Error: google-generativeai no está instalado. Ejecuta: pip install google-generativeai")
        return False
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        st.session_state.model = model
        st.session_state.selected_model = model_name
        # Guardar la clave API en secrets para persistencia
        st.session_state.api_key = api_key
        return True
    except Exception as e:
        st.error(f"Error configurando API de Gemini: {e}")
        return False

def cargar_api_key_desde_secrets():
    """Carga la primera clave API disponible desde st.secrets o el archivo secrets"""
    try:
        # 1. Intentar desde st.secrets (Streamlit Cloud) - Solo en modo desarrollador
        if AppSettings.SHOW_DEVELOPER_SECTION and 'GEMINI_API_KEY' in st.secrets:
            return st.secrets['GEMINI_API_KEY']
            
        # 2. Intentar desde archivo local (útil para desarrollo local)
        if os.path.exists('secrets'):
            with open('secrets', 'r', encoding='utf-8') as f:
                content = f.read()
                for line in content.split('\n'):
                    if line.startswith('GEMINI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        if api_key:
                            return api_key
        return None
    except Exception:
        return None

def cargar_todas_api_keys_desde_secrets():
    """Carga todas las claves API desde st.secrets y el archivo secrets"""
    api_keys = []
    try:
        # 1. De st.secrets - Solo en modo desarrollador
        if AppSettings.SHOW_DEVELOPER_SECTION and 'GEMINI_API_KEY' in st.secrets:
            api_keys.append(st.secrets['GEMINI_API_KEY'])
            
        # 2. De archivo local
        if os.path.exists('secrets'):
            with open('secrets', 'r', encoding='utf-8') as f:
                content = f.read()
                for line in content.split('\n'):
                    if line.startswith('GEMINI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        if api_key and api_key not in api_keys:
                            api_keys.append(api_key)
    except Exception:
        pass
    return api_keys

def guardar_api_key_en_secrets(api_key: str):
    """Guarda la clave API en el archivo secrets (evita duplicados)"""
    try:
        # Leer contenido actual del archivo secrets
        try:
            with open('secrets', 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            content = ""
        
        # Verificar si la clave ya existe
        existing_keys = cargar_todas_api_keys_desde_secrets()
        if api_key in existing_keys:
            return True  # Ya existe, no hacer nada
        
        # Agregar la nueva clave al final
        if content and not content.endswith('\n'):
            content += '\n'
        content += f'GEMINI_API_KEY={api_key}\n'
        
        # Escribir el archivo actualizado
        with open('secrets', 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        st.error(f"Error guardando API key: {e}")
        return False

def guardar_pregunta_desarrollador(pregunta: str):
    """Guarda una nueva pregunta del desarrollador en el archivo JSON"""
    try:
        json_path = os.path.join(TEMAS_DIR, "Desarrollador.json")
        
        # Cargar el archivo existente
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            # Crear estructura inicial si no existe
            data = {
                "tema": "Desarrollador",
                "descripcion": "Tema especial para desarrolladores que permite realizar cualquier pregunta técnica sobre sistemas de bombeo",
                "preguntas": []
            }
        
        # Verificar si la pregunta ya existe (comparación case-insensitive)
        pregunta_limpia = pregunta.strip()
        preguntas_existentes = [p.lower() for p in data["preguntas"]]
        
        if pregunta_limpia and pregunta_limpia.lower() not in preguntas_existentes:
            data["preguntas"].append(pregunta_limpia)
            
            # Guardar el archivo actualizado
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            return True, "✅ Pregunta guardada para reutilización"
        elif pregunta_limpia.lower() in preguntas_existentes:
            return False, "⚠️ Esta pregunta ya existe en el cuestionario"
        else:
            return False, "⚠️ Pregunta vacía"
    except Exception as e:
        print(f"Error guardando pregunta del desarrollador: {e}")
        return False, f"❌ Error al guardar: {e}"

def cargar_criterios_tecnicos():
    """Carga los criterios técnicos desde el archivo de configuración"""
    try:
        criteria_file = 'config/ai_criteria.json'
        if os.path.exists(criteria_file):
            with open(criteria_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error cargando criterios técnicos: {e}")
    
    # Criterios por defecto si no se puede cargar el archivo
    return {
        "criterios_tecnicos": {
            "velocidades_optimas": {
                "succion": {"min": 0.6, "max": 0.9, "unidad": "m/s"},
                "impulsion": {"min": 1.0, "max": 2.5, "unidad": "m/s"}
            },
            "npsh": {"margen_seguridad_minimo": 0.5, "unidad": "m"},
            "perdidas": {"succion_maxima_porcentaje": 10},
            "eficiencias": {"bomba_tipica_min": 70, "bomba_tipica_max": 85, "unidad": "%"},
            "motor": {"factor_servicio_min": 1.15, "factor_servicio_max": 1.25},
            "formulas": {
                "npsh": "NPSH = Pvapor + Patm - Psucción - Pperdidas",
                "bernoulli": "P1/γ + V1²/2g + Z1 = P2/γ + V2²/2g + Z2 + hf",
                "leyes_afinidad": "Q1/Q2 = N1/N2, H1/H2 = (N1/N2)², P1/P2 = (N1/N2)³"
            }
        }
    }

def render_ai_sidebar():
    """Renderiza el panel de IA en el sidebar, simplificado para configuración."""
    
    # Cargar API key guardada si no está en session_state
    if 'api_key' not in st.session_state or st.session_state.api_key is None:
        saved_api_key = cargar_api_key_desde_secrets()
        if saved_api_key:
            st.session_state.api_key = saved_api_key
            # Configurar el modelo automáticamente con el modelo por defecto
            default_model = st.session_state.get('selected_model', 'gemini-2.5-flash')
            configurar_gemini_api(saved_api_key, default_model)
            # NO mostrar mensaje - solo cargar silenciosamente

    # Panel principal de Análisis IA
    with st.sidebar.expander("🤖 Análisis IA", expanded=False):
        # Verificar disponibilidad de Gemini
        if not GEMINI_AVAILABLE:
            st.error("⚠️ google-generativeai no está instalado.")
            st.info("Para usar el análisis con IA, ejecuta: `pip install google-generativeai`")
            return

        ai_enabled = st.checkbox("Activar Análisis IA", value=st.session_state.get('ai_enabled', False))
        st.session_state.ai_enabled = ai_enabled
        
        if ai_enabled:
            st.info("✅ Análisis IA activado. La pestaña '🤖 Análisis IA' ya está disponible.")
            
            # En la versión pública, pedir el API Key directamente
            if not AppSettings.SHOW_DEVELOPER_SECTION and not st.session_state.get('api_key'):
                st.warning("⚠️ Se requiere una Clave API de Gemini para usar esta función.")
                api_key_public = st.text_input(
                    "Ingresa tu API Key de Gemini:", 
                    type="password",
                    help="Obtén una clave gratis en Google AI Studio (aistudio.google.com)"
                )
                if st.button("Configurar Clave", key="set_public_api_key"):
                    if api_key_public:
                        model_to_use = st.session_state.get('selected_model', 'gemini-2.5-flash')
                        if configurar_gemini_api(api_key_public, model_to_use):
                            st.success("✅ Clave configurada correctamente")
                            st.rerun()
                        else:
                            st.error("❌ Error: Clave inválida o error de conexión")
                    else:
                        st.error("Por favor ingresa una clave")
            
            # Subpanel Configuración API
            with st.expander("⚙️ Configuración Avanzada API", expanded=False):
                # Selector de modelo
                modelos_disponibles = [
                    "gemini-2.5-flash",      # Modelo rápido y económico (recomendado)
                    "gemini-2.0-flash-exp",   # Experimental 2.0
                    "gemini-1.5-flash",       # Flash 1.5 estable
                    "gemini-1.5-flash-8b",    # Flash 1.5 ligero
                    "gemini-1.5-pro",         # Pro 1.5 (mejor calidad)
                ]
                
                modelo_actual = st.session_state.get('selected_model', 'gemini-2.5-flash')
                try:
                    modelo_index = modelos_disponibles.index(modelo_actual)
                except ValueError:
                    modelo_index = 0
                
                selected_model = st.selectbox(
                    "Modelo de IA:",
                    modelos_disponibles,
                    index=modelo_index,
                    help="Selecciona el modelo de Gemini a utilizar."
                )
                
                # Actualizar el modelo si cambió
                if selected_model != modelo_actual and st.session_state.get('api_key'):
                    if configurar_gemini_api(st.session_state.api_key, selected_model):
                        st.success(f"✅ Modelo cambiado a: {selected_model}")
                
                # Mostrar claves API disponibles
                api_keys_disponibles = cargar_todas_api_keys_desde_secrets()
                
                if api_keys_disponibles:
                    st.markdown("**Claves API Disponibles:**")
                    api_key_options = [f"Clave {i+1} (***{key[-4:]})" for i, key in enumerate(api_keys_disponibles)]
                    api_key_options.append("Nueva Clave API")
                    
                    selected_key_option = st.selectbox(
                        "Seleccionar Clave API:",
                        api_key_options,
                        key="api_key_selector"
                    )
                    
                    if selected_key_option != "Nueva Clave API":
                        # Usar clave existente
                        key_index = api_key_options.index(selected_key_option)
                        selected_api_key = api_keys_disponibles[key_index]
                        
                        if st.button("🔄 Usar Clave Seleccionada"):
                            if configurar_gemini_api(selected_api_key, selected_model):
                                st.success(f"✅ Clave API {key_index+1} configurada con modelo: {selected_model}")
                            else:
                                st.error("❌ Error al configurar la clave API")
                    else:
                        # Agregar nueva clave
                        st.markdown("**Agregar Nueva Clave API:**")
                        api_key_input = st.text_input(
                            "Nueva Clave API Gemini", 
                            type="password", 
                            help="Obtén tu clave API desde Google AI Studio."
                        )
                        
                        if st.button("➕ Agregar Nueva Clave"):
                            if api_key_input:
                                if configurar_gemini_api(api_key_input, selected_model):
                                    guardar_api_key_en_secrets(api_key_input)
                                    st.success(f"✅ Nueva clave API agregada y configurada")
                                    st.rerun()
                                else:
                                    st.error("❌ Error al configurar la nueva clave API")
                            else:
                                st.error("Por favor, ingresa una clave válida.")
                else:
                    # No hay claves disponibles, mostrar input normal
                    api_key_input = st.text_input(
                        "Clave API Gemini", 
                        type="password", 
                        help="Obtén tu clave API desde Google AI Studio."
                    )
                    
                    if st.button("Configurar API Key"):
                        if api_key_input:
                            if configurar_gemini_api(api_key_input, selected_model):
                                guardar_api_key_en_secrets(api_key_input)
                                st.success(f"✅ API Key configurada con modelo: {selected_model}")
                                st.rerun()
                            else:
                                st.session_state.api_key = None
                        else:
                            st.error("Por favor, ingresa una clave válida.")
                
                # Botón para limpiar
                if st.button("🗑️ Limpiar Estado"):
                    st.session_state.api_key = None
                    st.session_state.model = None
                    st.success("Estado de API limpiado.")
        else:
            st.info("ℹ️ Activa la casilla para habilitar la pestaña de análisis con IA.")
            


def render_ai_question_response():
    """Renderiza el recuadro de pregunta/respuesta de IA"""
    
    # Asegurar que el historial de chat de desarrollador esté inicializado
    if 'developer_chat_history' not in st.session_state:
        st.session_state.developer_chat_history = []
    
    # Asegurar que selected_question esté inicializado
    if 'selected_question' not in st.session_state:
        st.session_state.selected_question = None
    
    # Verificar condiciones para mostrar el recuadro
    if not st.session_state.ai_enabled:
        return
    
    # Crear contenedor con estilo CSS
    st.markdown(
        """
        <style>
        .ai-container {
            border: 1px solid #ccc;
            padding: 20px;
            border-radius: 10px;
            background-color: #f9f9f9;
            margin-top: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .copy-button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .copy-button:hover {
            background-color: #0056b3;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Layout principal: 3 columnas (35-35-30%)
    col1, col2, col3 = st.columns([0.35, 0.35, 0.30])
    
    # Primera fila: Selección de Análisis
    with col1:
        st.markdown('<div class="ai-container">', unsafe_allow_html=True)
        st.markdown("### 1. Selección de Análisis")
        st.markdown("Selecciona un tema de análisis:")
        
        # Verificar si está en modo desarrollador
        developer_mode = st.session_state.get('developer_mode', False)
        
        # Cargar temas disponibles
        temas_disponibles = []
        try:
            temas_files = [f for f in os.listdir(TEMAS_DIR) if f.endswith('.json')]
            temas_disponibles = [f.replace('.json', '') for f in temas_files]
            
            # Si NO está en modo desarrollador, remover el tema Desarrollador
            if not developer_mode and 'Desarrollador' in temas_disponibles:
                temas_disponibles.remove('Desarrollador')
        except:
            temas_disponibles = []
        
        if temas_disponibles:
            tema_seleccionado = st.selectbox(
                "Tema:",
                temas_disponibles,
                key="tema_selector",
                help="Selecciona el tema de análisis"
            )
            
            # Cargar preguntas del tema seleccionado
            if tema_seleccionado == 'Desarrollador':
                # Para modo desarrollador, mostrar opciones inmediatamente
                st.markdown("---")
                st.markdown("**🔧 Opciones del Desarrollador:**")
                
                # Cargar preguntas guardadas del desarrollador
                preguntas_guardadas = cargar_preguntas_tema('Desarrollador')
                
                if preguntas_guardadas:
                    st.markdown("**Preguntas guardadas:**")
                    pregunta_seleccionada = st.selectbox(
                        "Selecciona una pregunta guardada:",
                        ["Nueva pregunta libre"] + preguntas_guardadas,
                        key="pregunta_desarrollador_guardada"
                    )
                    
                    if pregunta_seleccionada != "Nueva pregunta libre":
                        # Usar pregunta guardada
                        st.session_state.selected_question = {
                            'tema': 'Desarrollador',
                            'pregunta': pregunta_seleccionada
                        }
                        st.success(f"✅ Pregunta seleccionada: {pregunta_seleccionada}")
                    else:
                        # Inicializar contador si no existe
                        if 'pregunta_libre_counter' not in st.session_state:
                            st.session_state.pregunta_libre_counter = 0
                        
                        # Mostrar área de texto para nueva pregunta con key dinámico
                        pregunta_libre = st.text_area(
                            "Pregunta personalizada:",
                            placeholder="Escribe tu pregunta técnica aquí...",
                            height=100,
                            key=f"pregunta_desarrollador_{st.session_state.pregunta_libre_counter}"
                        )
                        
                        # Botón para enviar pregunta
                        if st.button("🚀 Enviar Pregunta", key=f"enviar_pregunta_{st.session_state.pregunta_libre_counter}"):
                            if pregunta_libre.strip():
                                # Guardar la pregunta en el JSON
                                guardado_exitoso, mensaje = guardar_pregunta_desarrollador(pregunta_libre.strip())
                                if guardado_exitoso:
                                    st.success(mensaje)
                                else:
                                    st.warning(mensaje)
                                
                                st.session_state.selected_question = {
                                    'tema': 'Desarrollador',
                                    'pregunta': pregunta_libre.strip()
                                }
                                
                                # Incrementar contador para próxima pregunta
                                st.session_state.pregunta_libre_counter += 1
                                # NO hacer st.rerun() para permitir que se muestre el chat continuo
                                st.info("💡 Pregunta registrada. Presiona '🚀 Enviar Pregunta a IA' abajo para obtener respuesta.")
                            else:
                                st.warning("⚠️ Por favor escribe una pregunta antes de enviar")
                else:
                    # Si no hay preguntas guardadas, mostrar solo área de texto
                    st.info("No hay preguntas guardadas. Escribe una nueva pregunta:")
                    
                    # Inicializar contador si no existe
                    if 'pregunta_libre_counter' not in st.session_state:
                        st.session_state.pregunta_libre_counter = 0
                    
                    pregunta_libre = st.text_area(
                        "Pregunta personalizada:",
                        placeholder="Escribe tu pregunta técnica aquí...",
                        height=100,
                        key=f"pregunta_desarrollador_alt_{st.session_state.pregunta_libre_counter}"
                    )
                    
                    # Botón para enviar pregunta
                    if st.button("🚀 Enviar Pregunta", key=f"enviar_pregunta_alt_{st.session_state.pregunta_libre_counter}"):
                        if pregunta_libre.strip():
                            # Guardar la pregunta en el JSON
                            guardado_exitoso, mensaje = guardar_pregunta_desarrollador(pregunta_libre.strip())
                            if guardado_exitoso:
                                st.success(mensaje)
                            else:
                                st.warning(mensaje)
                            
                            st.session_state.selected_question = {
                                'tema': 'Desarrollador',
                                'pregunta': pregunta_libre.strip()
                            }
                            
                            # Incrementar contador para próxima pregunta
                            st.session_state.pregunta_libre_counter += 1
                            # NO hacer st.rerun() para permitir que se muestre el chat continuo
                            st.info("💡 Pregunta registrada. Presiona '🚀 Enviar Pregunta a IA' abajo para obtener respuesta.")
                        else:
                            st.warning("⚠️ Por favor escribe una pregunta antes de enviar")
            else:
                # Para otros temas, cargar preguntas predefinidas
                preguntas = cargar_preguntas_tema(tema_seleccionado)
                if preguntas:
                    pregunta_seleccionada = st.selectbox(
                        "Pregunta:",
                        preguntas,
                        key="pregunta_selector"
                    )
                    st.session_state.selected_question = {
                        'tema': tema_seleccionado,
                        'pregunta': pregunta_seleccionada
                    }
                else:
                    st.warning("No hay preguntas disponibles para este tema.")
        else:
            st.warning("No hay temas disponibles.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="ai-container">', unsafe_allow_html=True)
        st.markdown("### 2. Pregunta de Análisis")
        
        # Mostrar pregunta seleccionada
        if st.session_state.get('selected_question'):
            pregunta_actual = st.session_state.selected_question.get('pregunta', 'N/A')
            tema_actual = st.session_state.selected_question.get('tema', 'N/A')
            
            st.info(f"**Tema:** {tema_actual}")
            st.info(f"**Pregunta:** {pregunta_actual}")
        else:
            st.info("💡 Selecciona un tema y una pregunta arriba para empezar.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        # Columna vacía (30%)
        pass

    
    # Procesamiento de la pregunta y respuesta
    if st.session_state.get('selected_question'):
        # === INVALIDAR VALORES CALCULADOS OBSOLETOS ANTES DE GENERAR PROMPT ===
        # Esto asegura que el análisis IA SIEMPRE use los valores de diseño actuales
        # en lugar de valores calculados que puedan estar desactualizados
        calculated_keys_to_clear = [
            'caudal_operacion', 'altura_operacion', 'interseccion',
            'eficiencia_operacion', 'potencia_operacion', 
            'npsh_requerido', 'npsh_margen'
        ]
        for key in calculated_keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # === GENERACIÓN EXHAUSTIVA DE TODOS LOS DATOS DEL SISTEMA ===
        
        # Función auxiliar para obtener valores de forma segura CON BÚSQUEDA INTELIGENTE
        def get_value(key, default='N/A', format_str='{:.2f}', alt_keys=None):
            """
            Busca un valor en session_state, probando múltiples claves alternativas.
            Prioriza valores válidos (no None, no 0, no vacío).
            """
            if alt_keys is None:
                alt_keys = []
            
            # Intentar clave principal
            value = st.session_state.get(key, None)
            
            # Si no encontró o es 0/vacío, buscar en alternativas
            if value is None or value == 0 or value == 0.0 or value == '':
                for alt_key in alt_keys:
                    alt_value = st.session_state.get(alt_key, None)
                    if alt_value is not None and alt_value != 0 and alt_value != 0.0 and alt_value != '':
                        value = alt_value
                        break
            
            # Si sigue sin valor, usar default
            if value is None or value == '':
                return str(default)
            
            try:
                if isinstance(value, (int, float)):
                    return format_str.format(value)
                else:
                    return str(value)
            except:
                return str(value)
        
        # 1. INFORMACIÓN BÁSICA DEL PROYECTO
        datos_basicos = f"""
INFORMACIÓN BÁSICA DEL PROYECTO:
- Proyecto: {get_value('proyecto', alt_keys=['proyecto_input_main'])}
- Diseño: {get_value('diseno', alt_keys=['diseno_input_main'])}
- Proyecto Input Main: {get_value('proyecto_input_main')}
- Diseño Input Main: {get_value('diseno_input_main')}
- Elevación del sitio: {get_value('elevacion_sitio', 0, '{:.1f}')} m
- Tipo de ajuste: {get_value('ajuste_tipo')}
- Tipo de ajuste configurado: {get_value('ajuste_tipo_configured')}
- Modo de curva: {get_value('curva_mode')}
- Modo de curva sidebar: {get_value('curva_mode_sidebar')}
- Unidad de flujo: {get_value('flow_unit')}
- Ruta del proyecto actual: {get_value('current_project_path')}
- Inicialización completada: {get_value('init_done', False)}
- Modo desarrollador: {get_value('developer_checkbox', False)}
"""

        # 2. CONDICIONES DE OPERACIÓN COMPLETAS - USO INTELIGENTE DE CLAVES
        condiciones_operacion = f"""
CONDICIONES DE OPERACIÓN:
- Caudal de diseño L/s: {get_value('caudal_lps', 0, '{:.2f}', alt_keys=['caudal_diseno_lps', 'caudal_nominal'])} L/s
- Caudal de diseño m³/h: {get_value('caudal_m3h', 0, '{:.2f}', alt_keys=['caudal_diseno_m3h'])} m³/h
- Caudal de operación (Q): {get_value('caudal_lps', 0, '{:.2f}', alt_keys=['caudal_operacion', 'interseccion'])} L/s
- Altura estática total: {get_value('altura_estatica_total', 0, '{:.2f}', alt_keys=['h_estatica_total', 'static_head'])} m
- Altura dinámica total (ADT): {get_value('adt_total', 0, '{:.2f}', alt_keys=['ADT', 'TDH', 'altura_dinamica_total'])} m
- Altura de operación: {get_value('altura_operacion', 0, '{:.2f}', alt_keys=['H_operacion', 'altura_interseccion'])} m
- Altura estática: {get_value('h_estatica', 0, '{:.2f}')} m
- Altura succión: {get_value('altura_succion', 0, '{:.2f}', alt_keys=['altura_succion_input', 'h_succion'])} m
- Altura succión input: {get_value('altura_succion_input', 0, '{:.2f}')} m
- Altura descarga: {get_value('altura_descarga', 0, '{:.2f}', alt_keys=['h_descarga'])} m
- Número de bombas en paralelo: {get_value('num_bombas_paralelo', 1, '{}', alt_keys=['num_bombas'])}
- Bomba inundada: {get_value('bomba_inundada', False)}
- Cabeza estática: {get_value('static_head', 0, '{:.2f}')} m
"""


        # 3. PARÁMETROS FÍSICOS Y AMBIENTALES COMPLETOS
        parametros_fisicos = f"""
PARÁMETROS FÍSICOS Y AMBIENTALES:
- Temperatura del líquido: {get_value('temp_liquido', 20, '{:.1f}')} °C
- Temperatura: {get_value('temperatura', 20, '{:.1f}')} °C
- Temperatura C: {get_value('temperatura_c', 20, '{:.1f}')} °C
- Densidad del líquido: {get_value('densidad_liquido', 1.0, '{:.3f}')} kg/m³
- Presión de vapor calculada: {get_value('presion_vapor_calculada', 0, '{:.3f}')} m.c.a.
- Presión de vapor: {get_value('presion_vapor', 0, '{:.3f}')} m.c.a.
- Presión barométrica calculada: {get_value('presion_barometrica_calculada', 0, '{:.3f}')} m.c.a.
"""

        # 4. DATOS COMPLETOS DE LA BOMBA
        datos_bomba = f"""
DATOS COMPLETOS DE LA BOMBA:
- Nombre de la bomba: {get_value('bomba_nombre')}
- Descripción de la bomba: {get_value('bomba_descripcion')}
- URL de la bomba: {get_value('bomba_url')}
- Bomba seleccionada: {get_value('bomba_seleccionada')}
- Potencia del motor final kW: {get_value('potencia_motor_final_kw', 0, '{:.2f}')} kW
- Potencia del motor final HP: {get_value('potencia_motor_final_hp', 0, '{:.2f}')} HP
- Potencia hidráulica kW: {get_value('potencia_hidraulica_kw', 0, '{:.2f}')} kW
- Potencia hidráulica HP: {get_value('potencia_hidraulica_hp', 0, '{:.2f}')} HP
- Potencia de operación: {get_value('potencia_operacion', 0, '{:.2f}')} HP
- Eficiencia de operación: {get_value('eficiencia_operacion', 0, '{:.2f}')}%
"""

        # 5. ANÁLISIS NPSH COMPLETO
        analisis_npsh = f"""
ANÁLISIS NPSH COMPLETO:
- NPSH disponible MCA: {get_value('npshd_mca', 0, '{:.2f}')} m
- NPSH disponible: {get_value('npshd', 0, '{:.2f}')} m
- NPSH requerido: {get_value('npsh_requerido', 0, '{:.2f}')} m
- NPSH: {get_value('npsh')}
- Margen NPSH: {get_value('npsh_margen', 0, '{:.2f}')} m
"""

        # 6. DATOS COMPLETOS DE TUBERÍAS
        datos_tuberias = f"""
DATOS COMPLETOS DE TUBERÍAS:
SUCCIÓN:
- Material: {get_value('mat_succion')}
- Diámetro nominal: {get_value('diam_succion_mm', 0, '{:.1f}')} mm
- Diámetro interno: {get_value('diam_interno_succion', 0, '{:.1f}')} mm
- Diámetro externo: {get_value('diam_externo_succion', 0, '{:.1f}')} mm
- Diámetro: {get_value('diam_succion')}
- Longitud: {get_value('long_succion', 0, '{:.1f}')} m
- Espesor: {get_value('espesor_succion', 0, '{:.1f}')} mm
- Coeficiente Hazen-Williams: {get_value('coeficiente_hazen_succion', 0)}
- Velocidad: {get_value('velocidad_succion', 0, '{:.2f}')} m/s
- Pérdida primaria: {get_value('hf_primaria_succion', 0, '{:.2f}')} m
- Pérdida secundaria: {get_value('hf_secundaria_succion', 0, '{:.2f}')} m
- Pérdida total: {get_value('perdida_total_succion', 0, '{:.2f}')} m
- Longitud equivalente total: {get_value('le_total_succion', 0, '{:.2f}')} m
- Otras pérdidas: {get_value('otras_perdidas_succion', 0, '{:.2f}')} m
- Altura dinámica: {get_value('altura_dinamica_succion', 0, '{:.2f}')} m

IMPULSIÓN:
- Material: {get_value('mat_impulsion')}
- Diámetro nominal: {get_value('diam_impulsion_mm', 0, '{:.1f}')} mm
- Diámetro interno: {get_value('diam_interno_impulsion', 0, '{:.1f}')} mm
- Diámetro externo: {get_value('diam_externo_impulsion', 0, '{:.1f}')} mm
- Diámetro: {get_value('diam_impulsion')}
- Longitud: {get_value('long_impulsion', 0, '{:.1f}')} m
- Espesor: {get_value('espesor_impulsion', 0, '{:.1f}')} mm
- Coeficiente Hazen-Williams: {get_value('coeficiente_hazen_impulsion', 0)}
- Velocidad: {get_value('velocidad_impulsion', 0, '{:.2f}')} m/s
- Pérdida primaria: {get_value('hf_primaria_impulsion', 0, '{:.2f}')} m
- Pérdida secundaria: {get_value('hf_secundaria_impulsion', 0, '{:.2f}')} m
- Pérdida total: {get_value('perdida_total_impulsion', 0, '{:.2f}')} m
- Longitud equivalente total: {get_value('le_total_impulsion', 0, '{:.2f}')} m
- Otras pérdidas: {get_value('otras_perdidas_impulsion', 0, '{:.2f}')} m
- Altura dinámica: {get_value('altura_dinamica_impulsion', 0, '{:.2f}')} m
"""

        # 7. DATOS COMPLETOS DE MATERIALES ESPECÍFICOS
        datos_materiales = f"""
DATOS COMPLETOS DE MATERIALES ESPECÍFICOS:
PEAD/HDPE:
- Serie impulsión: {get_value('serie_impulsion')}
- Serie impulsión índice: {get_value('serie_impulsion_index', 0)}
- SDR impulsión: {get_value('sdr_impulsion', 0)}
- Presión nominal impulsión: {get_value('presion_nominal_impulsion', 0, '{:.1f}')} bar
- Serie succión: {get_value('serie_succion')}
- Serie succión índice: {get_value('serie_succion_index', 0)}
- SDR succión: {get_value('sdr_succion', 0)}
- Presión nominal succión: {get_value('presion_nominal_succion', 0, '{:.1f}')} bar

HIERRO DÚCTIL:
- Clase impulsión: {get_value('clase_hierro_impulsion')}
- Clase impulsión índice: {get_value('clase_hierro_impulsion_index', 0)}
- DN impulsión: {get_value('dn_impulsion')}
- DN impulsión índice: {get_value('dn_impulsion_index', 0)}
- Clase succión: {get_value('clase_hierro_succion')}
- Clase succión índice: {get_value('clase_hierro_succion_index', 0)}
- DN succión: {get_value('dn_succion')}
- DN succión índice: {get_value('dn_succion_index', 0)}

HIERRO FUNDIDO:
- Clase impulsión: {get_value('clase_hierro_fundido_impulsion')}
- Clase impulsión índice: {get_value('clase_hierro_fundido_impulsion_index', 0)}
- DN impulsión: {get_value('dn_hierro_fundido_impulsion')}
- DN impulsión índice: {get_value('dn_hierro_fundido_impulsion_index', 0)}
- Clase succión: {get_value('clase_hierro_fundido_succion')}
- Clase succión índice: {get_value('clase_hierro_fundido_succion_index', 0)}
- DN succión: {get_value('dn_hierro_fundido_succion')}
- DN succión índice: {get_value('dn_hierro_fundido_succion_index', 0)}

PVC:
- Tipo unión impulsión: {get_value('tipo_union_pvc_impulsion')}
- Tipo unión impulsión índice: {get_value('tipo_union_pvc_impulsion_index', 0)}
- Serie impulsión: {get_value('serie_pvc_impulsion_nombre')}
- Serie impulsión índice: {get_value('serie_pvc_impulsion_nombre_index', 0)}
- DN impulsión: {get_value('dn_pvc_impulsion')}
- DN impulsión índice: {get_value('dn_pvc_impulsion_index', 0)}
- Tipo unión succión: {get_value('tipo_union_pvc_succion')}
- Tipo unión succión índice: {get_value('tipo_union_pvc_succion_index', 0)}
- Serie succión: {get_value('serie_pvc_succion_nombre')}
- Serie succión índice: {get_value('serie_pvc_succion_nombre_index', 0)}
- DN succión: {get_value('dn_pvc_succion')}
- DN succión índice: {get_value('dn_pvc_succion_index', 0)}

ÍNDICES DE DIÁMETROS EXTERNOS:
- Diámetro externo impulsión índice: {get_value('diam_externo_impulsion_index', 0)}
- Diámetro externo succión índice: {get_value('diam_externo_succion_index', 0)}
"""

        # 8. GENERAR TABLAS DE ACCESORIOS DETALLADAS
        accesorios_impulsion = st.session_state.get('accesorios_impulsion', [])
        tabla_accesorios_impulsion = ""
        if accesorios_impulsion:
            tabla_accesorios_impulsion = "\nACCESORIOS DE IMPULSIÓN:\n"
            tabla_accesorios_impulsion += "| Accesorio | Cantidad | K | Lc/D | Leq (m) |\n"
            tabla_accesorios_impulsion += "|-----------|----------|---|------|----------|\n"
            
            total_leq = 0
            for accesorio in accesorios_impulsion:
                tipo = accesorio.get('tipo', 'N/A')
                cantidad = accesorio.get('cantidad', 1)
                k = accesorio.get('k', 0)
                lc_d = accesorio.get('lc_d', 0)
                diam2_mm = st.session_state.get('diam_interno_impulsion', 40.8)
                
                leq_individual = lc_d * (diam2_mm / 1000)
                leq_total = leq_individual * cantidad
                total_leq += leq_total
                
                tabla_accesorios_impulsion += f"| {tipo} | {cantidad} | {k} | {lc_d} | {leq_individual:.3f} |\n"
            
            tabla_accesorios_impulsion += f"| **TOTAL** | | | | **{total_leq:.3f}** |\n"

        accesorios_succion = st.session_state.get('accesorios_succion', [])
        tabla_accesorios_succion = ""
        if accesorios_succion:
            tabla_accesorios_succion = "\nACCESORIOS DE SUCCIÓN:\n"
            tabla_accesorios_succion += "| Accesorio | Cantidad | K | Lc/D | Leq (m) |\n"
            tabla_accesorios_succion += "|-----------|----------|---|------|----------|\n"
            
            total_leq_succion = 0
            for accesorio in accesorios_succion:
                tipo = accesorio.get('tipo', 'N/A')
                cantidad = accesorio.get('cantidad', 1)
                k = accesorio.get('k', 0)
                lc_d = accesorio.get('lc_d', 0)
                diam2_mm = st.session_state.get('diam_interno_succion', 0)
                
                leq_individual = lc_d * (diam2_mm / 1000)
                leq_total = leq_individual * cantidad
                total_leq_succion += leq_total
                
                tabla_accesorios_succion += f"| {tipo} | {cantidad} | {k} | {lc_d} | {leq_individual:.3f} |\n"
            
            tabla_accesorios_succion += f"| **TOTAL** | | | | **{total_leq_succion:.3f}** |\n"

        # 9. DATOS COMPLETOS DE VFD Y ANÁLISIS TRANSIENTES
        datos_vfd_transientes = f"""
VFD Y ANÁLISIS TRANSIENTES COMPLETOS:
- Porcentaje RPM: {get_value('rpm_percentage', 100, '{:.1f}')}%
- Potencia ajustada: {get_value('potencia_ajustada', 0, '{:.2f}')} HP
- Eficiencia ajustada: {get_value('eficiencia_ajustada', 0, '{:.2f}')}%
- Análisis transientes activado: {get_value('transient_checkbox', False)}
- Celeridad de onda: {get_value('celeridad_onda', 0, '{:.1f}')} m/s
- Longitud de tubería: {get_value('pipe_length', 0, '{:.1f}')} m
- Análisis VDF: {get_value('analisis_vdf')}
- VFD: {get_value('vfd')}
"""

        # 10. DATOS COMPLETOS DE CURVAS Y AJUSTES
        datos_curvas = f"""
DATOS COMPLETOS DE CURVAS Y AJUSTES:
- Puntos de calibración: {get_value('calibration_points')}
- Puntos digitalizados: {get_value('digitalized_points')}
- Curvas puntos: {get_value('curvas_puntos')}
- Curvas texto: {get_value('curvas_texto')}
- Curva inputs: {get_value('curva_inputs')}
- Caudal máximo 100% RPM: {get_value('q_max_100_tab2', 0, '{:.1f}')} L/s
- Caudal mínimo 100% RPM: {get_value('q_min_100_tab2', 0, '{:.1f}')} L/s
- Caudal máximo VFD: {get_value('q_max_vdf_tab2', 0, '{:.1f}')} L/s
- Caudal mínimo VFD: {get_value('q_min_vdf_tab2', 0, '{:.1f}')} L/s
- Paso caudal 100% RPM: {get_value('paso_caudal_100_tab2', 0, '{:.1f}')} L/s
- Paso caudal VFD: {get_value('paso_caudal_vdf_tab2', 0, '{:.1f}')} L/s
- Zona eficiencia máxima: {get_value('zona_eff_max', 0, '{:.1f}')}%
- Zona eficiencia mínima: {get_value('zona_eff_min', 0, '{:.1f}')}%
"""

        # 11. DATOS COMPLETOS DE ADT POR CAUDALES
        datos_adt_caudales = f"""
ALTURA DINÁMICA TOTAL POR CAUDALES:
- ADT Caudal 1: {get_value('adt_caudal_1', 0, '{:.2f}')} m
- ADT Caudal 2: {get_value('adt_caudal_2', 0, '{:.2f}')} m
- ADT Caudal 3: {get_value('adt_caudal_3', 0, '{:.2f}')} m
- ADT Caudales personalizados: {get_value('adt_caudales_personalizados')}
- ADT Total: {get_value('adt_total', 0, '{:.2f}', alt_keys=['ADT', 'TDH', 'altura_dinamica_total'])} m
- Altura Estática Total: {get_value('altura_estatica_total', 0, '{:.2f}', alt_keys=['h_estatica_total', 'static_head'])} m
"""

        # 12. DATOS COMPLETOS DE ALTURAS DINÁMICAS
        datos_alturas_dinamicas = f"""
ALTURAS DINÁMICAS COMPLETAS:
- Altura dinámica impulsión: {get_value('altura_dinamica_impulsion', 0, '{:.2f}')} m
- Altura dinámica succión: {get_value('altura_dinamica_succion', 0, '{:.2f}')} m
- Cabeza estática: {get_value('static_head', 0, '{:.2f}')} m
- Alturas: {get_value('alturas')}
"""

        # 13. DATOS COMPLETOS DE PÉRDIDAS TOTALES
        datos_perdidas = f"""
PÉRDIDAS DE CARGA TOTALES:
- Pérdidas succión: {get_value('perdida_total_succion', 0, '{:.2f}')} m
- Pérdidas impulsión: {get_value('perdida_total_impulsion', 0, '{:.2f}')} m
- Pérdidas totales del sistema: {get_value('perdidas_totales_sistema', 0, '{:.2f}')} m
"""

        # 14. DATOS COMPLETOS DE TEXTAREAS E INFORMACIÓN ADICIONAL
        datos_textareas = f"""
INFORMACIÓN ADICIONAL COMPLETA:
- Textarea bomba: {get_value('textarea_bomba')}
- Textarea NPSH: {get_value('textarea_npsh')}
- Textarea potencia: {get_value('textarea_potencia')}
- Textarea rendimiento: {get_value('textarea_rendimiento')}
- Textarea sistema: {get_value('textarea_sistema')}
"""

        # 15. CONFIGURACIÓN COMPLETA DE GRÁFICOS Y UI
        config_graficos = f"""
CONFIGURACIÓN COMPLETA DE GRÁFICOS Y UI:
- Tamaño fuente eje: {get_value('font_size_axis', 12)}
- Tamaño fuente título: {get_value('font_size_title', 14)}
- Ancho columna 1: {get_value('col1_width', 25)}%
- Ancho columna 2: {get_value('col2_width', 25)}%
- Ancho columna 3: {get_value('col3_width', 25)}%
- Ancho columna 4: {get_value('col4_width', 25)}%
- Tema selector: {get_value('tema_selector')}
- Material seleccionado: {get_value('selected_material_name')}
- Modelo seleccionado: {get_value('selected_model')}
"""

        # 16. DATOS DE INTERSECCIÓN Y PUNTOS DE OPERACIÓN
        # Obtener datos de intersección de forma inteligente
        interseccion_raw = st.session_state.get('interseccion', None)
        caudal_interseccion = 0.0
        altura_interseccion = 0.0
        if interseccion_raw and isinstance(interseccion_raw, (list, tuple)) and len(interseccion_raw) >= 2:
            caudal_interseccion = interseccion_raw[0]
            altura_interseccion = interseccion_raw[1]
        
        datos_interseccion = f"""
DATOS DE INTERSECCIÓN Y PUNTOS DE OPERACIÓN:
- Caudal de Operación (Intersección): {caudal_interseccion:.2f} L/s ({caudal_interseccion * 3.6:.2f} m³/h)
- Altura de Operación (Intersección): {altura_interseccion:.2f} m
- Eficiencia en Punto de Operación: {get_value('eficiencia_operacion', 0, '{:.2f}', alt_keys=['rendimiento_operacion', 'eta_operacion'])}%
- Potencia en Punto de Operación: {get_value('potencia_operacion', 0, '{:.2f}', alt_keys=['P_operacion', 'BHP_operacion'])} HP
- Intersección VFD: {get_value('interseccion_vfd')}
- Punto de operación datos: {get_value('punto_operacion')}
"""

        # 17. DATOS DE MOTOR Y BOMBA DETALLADOS
        datos_motor_bomba = f"""
DATOS DETALLADOS DE MOTOR Y BOMBA:
- Motor: {get_value('motor')}
- Motor bomba: {get_value('motor_bomba')}
"""

        # 18. DATOS DE SISTEMAS COMPLETOS
        datos_sistemas = f"""
DATOS DE SISTEMAS COMPLETOS:
- Succión: {get_value('succion')}
- Impulsión: {get_value('impulsion')}
- Resumen: {get_value('resumen')}
"""

        # 19. DATOS DE PANELES Y CONFIGURACIÓN
        datos_paneles = f"""
DATOS DE PANELES Y CONFIGURACIÓN:
- Panel agregar accesorios impulsión: {get_value('panel_add_accesorios_impulsion', False)}
- Panel agregar accesorios succión: {get_value('panel_add_accesorios_succion', False)}
- Panel cantidad accesorios impulsión: {get_value('panel_cant_accesorios_impulsion', 0)}
- Panel cantidad accesorios succión: {get_value('panel_cant_accesorios_succion', 0)}
- Panel diámetro 2 accesorios impulsión: {get_value('panel_diam2_accesorios_impulsion', 0, '{:.1f}')} mm
- Panel diámetro 2 accesorios succión: {get_value('panel_diam2_accesorios_succion', 0, '{:.1f}')} mm
- Panel selección accesorios impulsión: {get_value('panel_selection_accesorios_impulsion')}
- Panel selección accesorios succión: {get_value('panel_selection_accesorios_succion')}
"""

        # 20. DATOS DE EXPORTACIÓN Y DESCARGA
        datos_exportacion = f"""
DATOS DE EXPORTACIÓN Y DESCARGA:
- Exportar curvas tab1: {get_value('export_curves_tab1', False)}
- Exportar reporte tab1: {get_value('export_reporte_tab1', False)}
- Descargar accesorios: {get_value('download_accesorios', False)}
- Descargar todo 100 RPM: {get_value('download_all_100rpm', False)}
- Descargar todo VFD: {get_value('download_all_vdf', False)}
- Descargar celeridad: {get_value('download_celeridad', False)}
- Descargar celeridad CSV: {get_value('download_celeridad_csv', False)}
- Descargar válvulas: {get_value('download_valvulas', False)}
- Descargar medidores: {get_value('download_medidores', False)}
"""

        # 21. DATOS DE API Y CONFIGURACIÓN TÉCNICA
        datos_api_config = f"""
DATOS DE API Y CONFIGURACIÓN TÉCNICA:
- API Key: {get_value('api_key', 'N/A')}
- Modelo: {get_value('model')}
- Último archivo subido ID: {get_value('last_uploaded_file_id')}
- Configuración file uploader JSON: {get_value('file_uploader_json_config')}
"""

        # COMPILAR TODOS LOS DATOS EXHAUSTIVOS
        datos_sistema = f"""
{datos_basicos}
{condiciones_operacion}
{parametros_fisicos}
{datos_bomba}
{analisis_npsh}
{datos_tuberias}
{datos_materiales}
{tabla_accesorios_impulsion}
{tabla_accesorios_succion}
{datos_vfd_transientes}
{datos_curvas}
{datos_adt_caudales}
{datos_alturas_dinamicas}
{datos_perdidas}
{datos_textareas}
{config_graficos}
{datos_interseccion}
{datos_motor_bomba}
{datos_sistemas}
{datos_paneles}
{datos_exportacion}
{datos_api_config}
        """

        if datos_sistema.strip():
            # Cargar criterios técnicos
            criteria = cargar_criterios_tecnicos()
            criterios_tecnicos = criteria['criterios_tecnicos']
            
            # Crear prompt para IA
            tema_actual = st.session_state.get('selected_question', {}).get('tema', 'N/A')
            pregunta_actual = st.session_state.get('selected_question', {}).get('pregunta', 'N/A')
            
            # Prompt especial para tema Desarrollador
            if tema_actual == "Desarrollador":
                prompt = f"""
Eres un ingeniero hidráulico experto en diseño de sistemas de bombeo con más de 30 años de experiencia. Tu tarea es responder a la pregunta del desarrollador de manera completa, técnica y detallada, utilizando todos los datos proporcionados del sistema.

**INSTRUCCIONES ESPECIALES PARA MODO DESARROLLADOR:**
- Responde de manera exhaustiva y técnica
- Incluye análisis detallados de todos los aspectos del sistema
- Proporciona recomendaciones específicas y prácticas
- Menciona consideraciones de diseño, operación y mantenimiento
- Incluye cálculos y fórmulas cuando sea relevante
- Analiza tanto aspectos positivos como áreas de mejora
- Considera aspectos económicos, técnicos y operacionales

**FORMATO DE LA RESPUESTA:**
1. **Título Principal**: Usa Markdown `#` para el título con el texto exacto de la pregunta (ej. `# Análisis completo del sistema de bombeo`).
2. **Subtítulos**: Usa Markdown `##` para secciones lógicas (ej. `## Análisis del Sistema`, `## Recomendaciones`, `## Consideraciones Técnicas`).
3. **Cuerpo de Texto**: Escribe en párrafos cortos (2-3 líneas) con tamaño de fuente equivalente a 16 px.
4. **Énfasis**: Usa **negritas** para términos clave, resultados importantes o alertas.
5. **Viñetas**: Usa viñetas (`*` en Markdown) para listas de puntos clave, observaciones o sugerencias. Incluye iconos simples como ✅, ⚠️ o 🔍.
6. **Fórmulas**: Presenta cada fórmula centrada en un bloque LaTeX con `$$` (ej. `$$ \\Delta H = \\frac{{a \\cdot \\Delta V}}{{g}} $$`).
7. **Unidades**: Incluye unidades consistentes para todas las cantidades numéricas.
8. **Recomendaciones**: Termina con una sección `## Recomendaciones` con viñetas de acciones prácticas.

**Pregunta del Desarrollador**: {pregunta_actual}

**Datos del Sistema**:
{datos_sistema}
"""
            else:
                # Prompt normal para otros temas
                prompt = f"""
Eres un ingeniero hidráulico experto en diseño de sistemas de bombeo. Tu tarea es analizar los datos proporcionados del sistema a continuación y responder SOLO a la pregunta seleccionada, con una respuesta clara, rigurosa y basada en principios de ingeniería. Sigue estas instrucciones estrictas para el formato de la respuesta:

**CRITERIOS TÉCNICOS IMPORTANTES:**
- Velocidad óptima en SUCCIÓN: {criterios_tecnicos['velocidades_optimas']['succion']['min']} - {criterios_tecnicos['velocidades_optimas']['succion']['max']} {criterios_tecnicos['velocidades_optimas']['succion']['unidad']}
- Velocidad óptima en IMPULSIÓN: {criterios_tecnicos['velocidades_optimas']['impulsion']['min']} - {criterios_tecnicos['velocidades_optimas']['impulsion']['max']} {criterios_tecnicos['velocidades_optimas']['impulsion']['unidad']}
- {criterios_tecnicos['formulas']['npsh']}
- Pérdidas en succión deben ser <{criterios_tecnicos['perdidas']['succion_maxima_porcentaje']}% de la altura total
- Margen de seguridad NPSH > {criterios_tecnicos['npsh']['margen_seguridad_minimo']} {criterios_tecnicos['npsh']['unidad']}
- Eficiencia de bomba típica: {criterios_tecnicos['eficiencias']['bomba_tipica_min']}-{criterios_tecnicos['eficiencias']['bomba_tipica_max']}{criterios_tecnicos['eficiencias']['unidad']}
- Factor de servicio motor: {criterios_tecnicos['motor']['factor_servicio_min']}-{criterios_tecnicos['motor']['factor_servicio_max']}

**FÓRMULAS IMPORTANTES:**
- Bernoulli: {criterios_tecnicos['formulas']['bernoulli']}
- Leyes de afinidad: {criterios_tecnicos['formulas']['leyes_afinidad']}

**FORMATO DE LA RESPUESTA:**
1. **Título Principal**: Usa Markdown `#` para el título con el texto exacto de la pregunta seleccionada (ej. `# ¿Son razonables las pérdidas en succión?`).
2. **Subtítulos**: Usa Markdown `##` para secciones lógicas (ej. `## Análisis`, `## Fórmulas`, `## Recomendaciones`).
3. **Cuerpo de Texto**: Escribe en párrafos cortos (2-3 líneas) con tamaño de fuente equivalente a 16 px (usa Markdown estándar).
4. **Énfasis**: Usa **negritas** para términos clave, resultados importantes o alertas (ej. **Riesgo de cavitación**).
5. **Viñetas**: Usa viñetas (`*` en Markdown) para listas de puntos clave, observaciones o sugerencias. Incluye iconos simples como ✅, ⚠️ o 🔍 al inicio de viñetas para destacar.
6. **Fórmulas**:
   - Presenta cada fórmula centrada en un bloque LaTeX con `$$` (ej. `$$ \\Delta H = \\frac{{a \\cdot \\Delta V}}{{g}} $$`).
   - Asegúrate de que numeradores y denominadores sean claros usando `\\frac` (ej. `\\frac{{a \\cdot \\Delta V}}{{g}}`).
   - Debajo de cada fórmula, incluye una lista de viñetas (`*`) explicando cada término con su significado y unidad (ej. `* \\( a \\): Velocidad de onda, m/s`).
7. **Unidades**: Incluye unidades consistentes para todas las cantidades numéricas (ej. m, m³/h, kW).
8. **Manejo de Datos Faltantes**: Si falta un dato en el JSON, indícalo con **Dato faltante** y sugiere un valor típico si es razonable.
9. **Recomendaciones**: Termina con una sección `## Recomendaciones` con viñetas de acciones prácticas, destacando las más importantes en **negritas**.

**RESTRICCIONES:**
- Responde SOLO a la pregunta seleccionada; no incluyas información adicional ni respondas a otras preguntas.
- No hagas suposiciones no respaldadas por los datos del sistema.
- Usa un tono profesional, técnico y conciso, similar a un informe de ingeniería.
- Asegúrate de que el formato Markdown sea compatible con Streamlit (usa # para títulos, ## para subtítulos, * para viñetas, ** para negritas).
- Usa bloques LaTeX con `$$` para fórmulas centradas y `\\frac` para fracciones.

**Pregunta Seleccionada**: {pregunta_actual}

**Datos del Sistema**:
{datos_sistema}
"""
            
            # Verificar si hay API key y modelo configurado
            if not st.session_state.api_key or not st.session_state.model:
                st.warning("⚠️ Para usar el análisis con IA, primero configura tu clave API en el panel lateral.")
                st.info("1. Activa 'Análisis IA' en el panel lateral")
                st.info("2. Configura tu clave API de Gemini")
                st.info("3. Selecciona una pregunta de análisis")
            else:
                # Botón Enviar Pregunta en 2 columnas (35-35-30%)
                st.markdown("---")
                col_btn1, col_btn2, col_btn3 = st.columns([0.35, 0.35, 0.30])
                
                with col_btn1:
                    # Formulario para enviar pregunta
                    with st.form(key="ai_form"):
                        if st.form_submit_button("🚀 Enviar Pregunta a IA", use_container_width=True):
                            try:
                                with st.spinner("🤖 Analizando con IA..."):
                                    response = st.session_state.model.generate_content(prompt)
                                
                                # Guardar la respuesta en session_state para mostrarla fuera del form
                                st.session_state.ai_response = response.text
                                st.session_state.ai_response_generated = True
                                
                            except Exception as e:
                                st.error(f"❌ **Error al consultar IA:** {e}")
                                st.error("🔧 **Solución:** Verifica que tu clave API sea válida y que tengas conexión a internet.")
                
                with col_btn2:
                    # Estado de la API
                    if st.session_state.get('api_key') and st.session_state.get('model'):
                        st.success("✅ API Configurada correctamente")
                    else:
                        st.error("❌ API No configurada")
                
                with col_btn3:
                    # Columna vacía (30%)
                    pass
                
                # --- INICIO: Bloque de respuesta y chat continuo ---
                if st.session_state.get('ai_response_generated') and st.session_state.get('ai_response'):
                    
                    # Solo en modo desarrollador, añadir al historial
                    tema_actual = st.session_state.get('selected_question', {}).get('tema', '')
                    if tema_actual == 'Desarrollador':
                        # Añadir solo si es una nueva interacción para evitar duplicados en re-runs
                        if 'last_question_added' not in st.session_state or st.session_state.last_question_added != st.session_state.selected_question['pregunta']:
                            st.session_state.developer_chat_history.append({
                                'tipo': 'pregunta',
                                'contenido': st.session_state.selected_question['pregunta'],
                                'timestamp': datetime.now().strftime('%H:%M:%S')
                            })
                            st.session_state.developer_chat_history.append({
                                'tipo': 'respuesta',
                                'contenido': st.session_state.ai_response,
                                'timestamp': datetime.now().strftime('%H:%M:%S')
                            })
                            st.session_state.last_question_added = st.session_state.selected_question['pregunta']

                    # Visualización de la respuesta
                    st.markdown("---")
                    col_resp_full, col_actions = st.columns([0.7, 0.3])
                    with col_resp_full:
                        st.markdown("### 🤖 **Análisis de IA**")
                        st.markdown(f'<div class="ai-response">{st.session_state.ai_response}</div>', unsafe_allow_html=True)
                    
                    # Columna de acciones (copiar, convertir, descargar)
                    with col_actions:
                        st.markdown("### **Acciones**")
                        
                        tema_actual = st.session_state.get('selected_question', {}).get('tema', '')
                        
                        # Botón de Copiar (diferente según modo)
                        if tema_actual == 'Desarrollador':
                            # MODO DESARROLLADOR: Copiar todas las respuestas
                            if st.button("📋 Copiar Todas las Respuestas", use_container_width=True):
                                if st.session_state.get('developer_chat_history'):
                                    # Formatear para Word
                                    texto_completo = "CONVERSACIÓN DE ANÁLISIS IA - MODO DESARROLLADOR\n"
                                    texto_completo += f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                                    texto_completo += "="*70 + "\n\n"
                                    
                                    for item in st.session_state.developer_chat_history:
                                        if item['tipo'] == 'pregunta':
                                            texto_completo += f"PREGUNTA ({item['timestamp']}):\n{item['contenido']}\n\n"
                                        else:
                                            # Limpiar markdown básico
                                            contenido = item['contenido']
                                            import re
                                            contenido = re.sub(r'\*\*(.*?)\*\*', r'\1', contenido)
                                            contenido = re.sub(r'\*(.*?)\*', r'\1', contenido)
                                            contenido = re.sub(r'^#{1,6}\s+', '', contenido, flags=re.MULTILINE)
                                            contenido = re.sub(r'`(.*?)`', r'\1', contenido)
                                            texto_completo += f"RESPUESTA IA ({item['timestamp']}):\n{contenido}\n\n"
                                            texto_completo += "-"*70 + "\n\n"
                                    
                                    st.text_area("Copiar este texto (Ctrl+A, Ctrl+C):", texto_completo, height=300, key="copy_all_dev")
                                    st.info("✅ Listo para pegar en Word")
                                else:
                                    st.warning("No hay conversaciones para copiar")
                        else:
                            # MODO NORMAL: Copiar solo respuesta actual
                            if st.button("📋 Copiar Respuesta Actual", use_container_width=True):
                                # Limpiar markdown
                                contenido = st.session_state.ai_response
                                import re
                                contenido = re.sub(r'\*\*(.*?)\*\*', r'\1', contenido)
                                contenido = re.sub(r'\*(.*?)\*', r'\1', contenido)
                                contenido = re.sub(r'^#{1,6}\s+', '', contenido, flags=re.MULTILINE)
                                contenido = re.sub(r'`(.*?)`', r'\1', contenido)
                                st.text_area("Copiar este texto (Ctrl+A, Ctrl+C):", contenido, height=200, key="copy_current")
                                st.info("✅ Listo para pegar en Word")

                        # EXPORTACIÓN: Disponible para TODOS los temas
                        st.markdown("### **Exportar**")
                        
                        if tema_actual == 'Desarrollador':
                            # MODO DESARROLLADOR: Exportar historial completo
                            if st.button("Convertir a HTML", use_container_width=True):
                                if st.session_state.developer_chat_history:
                                    st.session_state.generated_html = generar_informe_html(st.session_state.developer_chat_history)
                                    st.session_state.html_ready = True
                                else:
                                    st.warning("No hay historial de chat para exportar.")

                            
                            if st.button("Convertir a Markdown", use_container_width=True):
                                if st.session_state.developer_chat_history:
                                    st.session_state.generated_markdown = generar_informe_markdown(st.session_state.developer_chat_history)
                                    st.session_state.md_ready = True
                                else:
                                    st.warning("No hay historial de chat para exportar.")

                            # Botones para DESCARGAR (aparecen después de convertir)
                            if st.session_state.get('html_ready'):
                                st.download_button(
                                    label="Descargar HTML",
                                    data=st.session_state.generated_html,
                                    file_name=f"conversacion_dev_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                    mime="text/html",
                                    use_container_width=True
                                )
                            
                            if st.session_state.get('md_ready'):
                                st.download_button(
                                    label="Descargar Markdown",
                                    data=st.session_state.generated_markdown,
                                    file_name=f"conversacion_dev_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                    mime="text/markdown",
                                    use_container_width=True
                                )

                        # Lógica para otros modos (descarga directa de respuesta única)
                        else:
                            st.markdown("### **Descargar Análisis**")
                            st.download_button(
                                label="Descargar HTML",
                                data=generar_informe_html([{'tipo': 'respuesta', 'contenido': st.session_state.ai_response, 'timestamp': ''}]),
                                file_name=f"analisis_{tema_actual.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                mime="text/html",
                                use_container_width=True
                            )
                            st.download_button(
                                label="Descargar Markdown",
                                data=generar_informe_markdown([{'tipo': 'respuesta', 'contenido': st.session_state.ai_response, 'timestamp': ''}]),
                                file_name=f"analisis_{tema_actual.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                mime="text/markdown",
                                use_container_width=True
                            )


                    # Formulario para chat continuo en modo desarrollador
                    if tema_actual == 'Desarrollador':
                        st.markdown("---")
                        st.markdown("### 🔧 **Chat Continuo**")
                        with st.form(key="developer_follow_up_form"):
                            pregunta_adicional = st.text_area("Siguiente pregunta:", height=100, key="pregunta_adicional")
                            submitted = st.form_submit_button("🚀 Enviar Pregunta Adicional")

                            if submitted and pregunta_adicional.strip():
                                with st.spinner("🤖 Pensando..."):
                                    # Construir prompt con historial
                                    historial_prompt = ""
                                    for msg in st.session_state.developer_chat_history:
                                        historial_prompt += f"{msg['tipo'].capitalize()}: {msg['contenido']}\n\n"
                                    
                                    prompt_contextual = f"""Eres un ingeniero experto. A continuación se presenta un historial de conversación. Responde a la 'Nueva Pregunta' manteniendo el contexto.

--- HISTORIAL ---
{historial_prompt}
--- NUEVA PREGUNTA ---
{pregunta_adicional}
"""
                                    try:
                                        response = st.session_state.model.generate_content(prompt_contextual)
                                        # Actualizar la pregunta seleccionada para que el ciclo se repita
                                        st.session_state.selected_question = {'tema': 'Desarrollador', 'pregunta': pregunta_adicional}
                                        st.session_state.ai_response = response.text
                                        st.session_state.ai_response_generated = True
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error al consultar IA: {e}")

    else:
        # Mostrar estado cuando no hay pregunta seleccionada
        if st.session_state.api_key and st.session_state.model:
            st.success("✅ IA configurada correctamente. Selecciona un tema y una pregunta arriba para comenzar el análisis.")
        else:
            st.warning("⚠️ Configura tu clave API en el panel lateral para usar el análisis con IA.")
