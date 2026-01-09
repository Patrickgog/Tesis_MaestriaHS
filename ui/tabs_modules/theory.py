"""
Módulo de Teoría y Fundamentos con Diseño Profesional
Renderiza contenido técnico desde archivos markdown con interfaz dinámica
"""

import streamlit as st
import os
from pathlib import Path

def load_markdown_content(filename):
    """Carga contenido de un archivo markdown"""
    base_path = Path(__file__).parent.parent.parent / "Teoria_Fundamentos"
    file_path = base_path / filename
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"⚠️ Archivo no encontrado: {filename}"
    except Exception as e:
        return f"❌ Error al cargar: {str(e)}"

def render_professional_content(markdown_content, section_color="#F5F5DC"):
    """
    Renderiza contenido markdown con estilo profesional
    
    Args:
        markdown_content: Contenido en formato markdown
        section_color: Color de acento para la sección (beige por defecto)
    """
    
    # CSS personalizado para diseño profesional
    st.markdown(f"""
    <style>
        /* Contenedor principal con efecto hover */
        .theory-container {{
            background: linear-gradient(135deg, #FFFFFF 0%, {section_color} 100%);
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
            transition: all 0.3s ease;
            border-left: 5px solid #D4AF37;
        }}
        
        .theory-container:hover {{
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.12);
            transform: translateY(-2px);
        }}
        
        /* Títulos con línea decorativa */
        .theory-container h1 {{
            color: #2C3E50;
            border-bottom: 3px solid #D4AF37;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        
        .theory-container h2 {{
            color: #34495E;
            margin-top: 25px;
            font-weight: 500;
            position: relative;
            padding-left: 15px;
        }}
        
        .theory-container h2::before {{
            content: "";
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 5px;
            height: 70%;
            background: #D4AF37;
            border-radius: 3px;
        }}
        
        .theory-container h3 {{
            color: #5D6D7E;
            margin-top: 20px;
            font-weight: 500;
        }}
        
        /* Párrafos con mejor legibilidad */
        .theory-container p {{
            color: #2C3E50;
            line-height: 1.8;
            font-size: 1.05em;
            margin: 15px 0;
            text-align: justify;
        }}
        
        /* Listas con iconos personalizados */
        .theory-container ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .theory-container ul li {{
            padding: 8px 0 8px 30px;
            position: relative;
            color: #34495E;
            line-height: 1.6;
        }}
        
        .theory-container ul li::before {{
            content: "▸";
            position: absolute;
            left: 10px;
            color: #D4AF37;
            font-weight: bold;
        }}
        
        /* Código con fondo beige suave */
        .theory-container code {{
            background-color: #FFF8DC;
            color: #C7254E;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        .theory-container pre {{
            background-color: #FFF8DC;
            border-left: 4px solid #D4AF37;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        
        /* Tablas elegantes */
        .theory-container table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .theory-container th {{
            background: linear-gradient(135deg, #D4AF37 0%, #C5A028 100%);
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        .theory-container td {{
            padding: 10px 12px;
            border-bottom: 1px solid #E8E8E8;
            color: #2C3E50;
        }}
        
        .theory-container tr:hover {{
            background-color: #FFF8DC;
            transition: background-color 0.2s ease;
        }}
        
        /* Ecuaciones con fondo destacado */
        .theory-container .math {{
            background-color: #F8F9FA;
            padding: 10px 15px;
            border-radius: 5px;
            margin: 15px 0;
            border-left: 3px solid #D4AF37;
        }}
        
        /* Blockquotes profesionales */
        .theory-container blockquote {{
            border-left: 5px solid #D4AF37;
            background-color: #FFF8DC;
            padding: 15px 20px;
            margin: 20px 0;
            font-style: italic;
            color: #5D6D7E;
            border-radius: 0 5px 5px 0;
        }}
        
        /* Alerts/Notas */
        .theory-container .note {{
            background-color: #E8F4F8;
            border-left: 4px solid #3498DB;
            padding: 12px 15px;
            margin: 15px 0;
            border-radius: 3px;
        }}
        
        .theory-container .warning {{
            background-color: #FFF3CD;
            border-left: 4px solid #FFC107;
            padding: 12px 15px;
            margin: 15px 0;
            border-radius: 3px;
        }}
        
        .theory-container .success {{
            background-color: #D4EDDA;
            border-left: 4px solid #28A745;
            padding: 12px 15px;
            margin: 15px 0;
            border-radius: 3px;
        }}
        
        /* Línea divisoria elegante */
        .theory-cont ainer hr {{
            border: none;
            height: 2px;
            background: linear-gradient(to right, transparent, #D4AF37, transparent);
            margin: 30px 0;
        }}
        
        /* Links con hover effect */
        .theory-container a {{
            color: #3498DB;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-bottom 0.2s ease;
        }}
        
        .theory-container a:hover {{
            border-bottom: 1px solid #3498DB;
        }}
        
        /* Scrollbar personalizado */
        .theory-container::-webkit-scrollbar {{
            width: 8px;
        }}
        
        .theory-container::-webkit-scrollbar-track {{
            background: #F5F5DC;
            border-radius: 10px;
        }}
        
        .theory-container::-webkit-scrollbar-thumb {{
            background: #D4AF37;
            border-radius: 10px;
        }}
        
        .theory-container::-webkit-scrollbar-thumb:hover {{
            background: #C5A028;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Renderizar contenido en contenedor con clase
    st.markdown(f'<div class="theory-container">', unsafe_allow_html=True)
    st.markdown(markdown_content)
    st.markdown('</div>', unsafe_allow_html=True)


def render_theory_tab():
    """Renderiza la pestaña principal de Teoría y Fundamentos con sub-pestañas"""
    
    # Header principal con diseño profesional
    st.markdown("""
    <div style="background: linear-gradient(135deg, #2C3E50 0%, #34495E 100%); 
                padding: 30px; border-radius: 10px; margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h1 style="color: #D4AF37; margin: 0; font-size: 2.2em; font-weight: 600;">
            📚 Teoría y Fundamentos
        </h1>
        <p style="color: #ECF0F1; margin-top: 10px; font-size: 1.1em;">
            Fundamentos técnicos y científicos del diseño de sistemas de bombeo
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Crear sub-pestañas
    subtabs = st.tabs([
        "🏠 Introducción",
        "📝 Datos de Entrada",
        "📈 Análisis de Curvas",
        "⚡ Pérdidas de Carga",
        "💧 Resultados Hidráulicos",
        "🔧 Accesorios",
        "🎯 VFD y Eficiencia"
    ])
    
    # Definir colores para cada sección
    section_colors = {
        0: "#F5F5DC",  # Beige claro
        1: "#FFF8DC",  # Cornsilk
        2: "#FAFAD2",  # Light goldenrod
        3: "#F0E68C",  # Khaki
        4: "#F5DEB3",  # Wheat
        5: "#FFE4B5",  # Moccasin
        6: "#FFDAB9",  # Peach puff
    }
    
    # 1. Introducción
    with subtabs[0]:
        content = load_markdown_content("01_introduccion.md")
        render_professional_content(content, section_colors[0])
        
        # Agregar imagen o diagrama interactivo si existe
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⚙️ Componentes", "5 principales")
        with col2:
            st.metric("📐 Ecuaciones", "Bernoulli + Continuidad")
        with col3:
            st.metric("✅ Validación", "Automática")
    
    # 2. Datos de Entrada
    with subtabs[1]:
        content = load_markdown_content("02_datos_entrada.md")
        render_professional_content(content, section_colors[1])
    
    # 3. Análisis de Curvas
    with subtabs[2]:
        content = load_markdown_content("03_analisis_curvas.md")
        render_professional_content(content, section_colors[2])
    
    # 4. Pérdidas de Carga
    with subtabs[3]:
        content = load_markdown_content("04_perdidas_carga.md")
        render_professional_content(content, section_colors[3])
    
    # 5. Resultados Hidráulicos
    with subtabs[4]:
        content = load_markdown_content("05_resultados_hidraulicos.md")
        render_professional_content(content, section_colors[4])
    
    # 6. Accesorios (placeholder)
    with subtabs[5]:
        st.info("📝 Sección en desarrollo: Cálculo detallado de accesorios y sus coeficientes de pérdida")
    
    # 7. VFD y Eficiencia (placeholder)
    with subtabs[6]:
        st.info("📝 Sección en desarrollo: Análisis detallado de variadores de frecuencia y optimización energética")
    
    # Footer profesional
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #7F8C8D; padding: 20px;">
        <p style="margin: 0; font-size: 0.9em;">
            💡 <em>Esta documentación técnica es parte del Sistema de Diseño de Bombeo</em>
        </p>
        <p style="margin: 5px 0 0 0; font-size: 0.85em;">
            Desarrollado como tesis de Maestría en Ingeniería Hidrosanitaria
        </p>
    </div>
    """, unsafe_allow_html=True)
