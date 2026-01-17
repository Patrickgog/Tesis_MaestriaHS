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
    
    # Renderizar configuración general (siempre visible)
    render_sidebar()
    
    # Renderizar panel de IA en sidebar (siempre visible)
    render_ai_sidebar()
    
    # Renderizar opciones comunes del sidebar (siempre visible para todos los usuarios)
    render_common_sidebar_options()
    
    # Renderizar expander de Desarrollador en sidebar (solo si está habilitado en configuración)
    if AppSettings.SHOW_DEVELOPER_SECTION:
        render_developer_sidebar()
    
    # Renderizar pestañas principales
    render_main_tabs()

if __name__ == "__main__":
    main()
