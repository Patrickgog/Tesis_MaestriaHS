# Punto de entrada principal de la aplicación

import streamlit as st
from config.settings import AppSettings
from ui.tabs import render_main_tabs
from ui.sidebar import render_sidebar, render_common_sidebar_options, render_developer_sidebar
from ui.ai_module import render_ai_sidebar
from utils.helpers import initialize_state

def main():
    """Función principal de la aplicación"""
    
    # Configuración de la página
    st.set_page_config(layout="wide", page_title="Tesis de Maestría Hidrosanitaria")
    
    # Inicializar estado
    initialize_state()
    
    # Título principal
    st.title("Tesis de Maestría Hidrosanitaria")
    st.header("Diseño de Sistemas de Bombeo")
    
    # Determinar si usar layout agrupado (solo para versión pública)
    use_grouped_layout = not AppSettings.SHOW_DEVELOPER_SECTION
    
    # PRIMERO: Mostrar banner de versión AL INICIO DE TODO
    if AppSettings.SHOW_DEVELOPER_SECTION:
        st.sidebar.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 10px; 
                    border-radius: 5px; 
                    text-align: center; 
                    margin-bottom: 15px;">
            <h3 style="color: white; margin: 0;">🔧 MODO DESARROLLADOR</h3>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 10px; 
                    border-radius: 5px; 
                    text-align: center; 
                    margin-bottom: 15px;">
            <h3 style="color: white; margin: 0;">🌐 VERSIÓN PÚBLICA</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # 1. Renderizar panel de IA en sidebar (PRIMERO - siempre visible)
    render_ai_sidebar()
    
    # 2. Renderizar configuración general (siempre visible)
    render_sidebar(use_grouped_layout=use_grouped_layout)
    
    # 3. Renderizar opciones comunes del sidebar (siempre visible para todos los usuarios)
    render_common_sidebar_options(use_grouped_layout=use_grouped_layout)
    
    # 4. Renderizar expander de Desarrollador en sidebar (solo si está habilitado en configuración)
    if AppSettings.SHOW_DEVELOPER_SECTION:
        render_developer_sidebar()
    
    # Renderizar pestañas principales
    render_main_tabs()

if __name__ == "__main__":
    main()
