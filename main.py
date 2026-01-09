# Punto de entrada principal de la aplicación

import streamlit as st
from config.settings import AppSettings
from ui.tabs import render_main_tabs
from ui.sidebar import render_sidebar, render_developer_sidebar
# from ui.ai_module import render_ai_sidebar  # COMENTADO - Ahora está en sidebar.py
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
    
    # Renderizar panel de IA en sidebar (ahora está en render_developer_sidebar)
    # render_ai_sidebar()  # COMENTADO - Ahora está integrado en sidebar.py
    
    # Renderizar expander de Desarrollador en sidebar (solo si está habilitado en configuración)
    if AppSettings.SHOW_DEVELOPER_SECTION:
        render_developer_sidebar()
    
    # Renderizar pestañas principales
    render_main_tabs()

if __name__ == "__main__":
    main()
