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
from ui.ai_module import render_ai_question_response
from ui.transient_tab import render_transient_tab as render_transient_simulation_tab
from ui.transients import render_transient_tab
from ui.html_generator import generate_html_report

def render_questions_tab():
    """Renderiza la pestaña de gestión de preguntas de IA (solo para desarrolladores)"""
    
    st.title("📝 Gestión de Preguntas de IA")
    st.markdown("**Modo Desarrollador** - Edita las preguntas que se hacen a la IA")
    
    # Lista de temas disponibles
    temas = ["Succion", "Impulsion", "Ajuste_Curvas", "NPSH_Disponible", 
             "Motor_Bomba", "Altura_Dinamica", "Curvas_100_RPM", "Curvas_VDF", "Desarrollador"]
    
    # Crear subpestañas para cada tema
    if temas:
        tema_tabs = st.tabs(temas)
        
        for i, tema in enumerate(temas):
            with tema_tabs[i]:
                render_tema_questions(tema)

def render_tema_questions(tema: str):
    """Renderiza las preguntas editables para un tema específico"""
    
    import json
    import os
    
    st.subheader(f"📋 Preguntas para: {tema}")
    
    # Ruta del archivo JSON del tema
    json_path = os.path.join("temas_ai", f"{tema}.json")
    
    # Cargar preguntas existentes
    try:
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                preguntas = data.get("preguntas", [])
        else:
            preguntas = []
            st.warning(f"Archivo {json_path} no encontrado. Se creará uno nuevo.")
    except Exception as e:
        st.error(f"Error al cargar {json_path}: {e}")
        preguntas = []
    
    # Mostrar número de preguntas actuales
    st.info(f"📊 **Total de preguntas:** {len(preguntas)}")
    
    # Formulario para agregar nueva pregunta
    with st.expander("➕ Agregar Nueva Pregunta", expanded=False):
        with st.form(key=f"add_question_{tema}"):
            nueva_pregunta = st.text_area(
                "Nueva pregunta:",
                placeholder="Escribe aquí la nueva pregunta para la IA...",
                height=100,
                key=f"new_question_{tema}"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Agregar Pregunta", use_container_width=True):
                    if nueva_pregunta.strip():
                        preguntas.append(nueva_pregunta.strip())
                        if save_questions_to_json(tema, preguntas):
                            st.success("✅ Pregunta agregada correctamente")
                            st.rerun()
                        else:
                            st.error("❌ Error al guardar la pregunta")
                    else:
                        st.error("❌ La pregunta no puede estar vacía")
            
            with col2:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    pass
    
    # Mostrar preguntas existentes en cuadros editables
    if preguntas:
        st.markdown("---")
        st.markdown("### 📝 Preguntas Existentes")
        
        for i, pregunta in enumerate(preguntas):
            with st.container():
                st.markdown(f"**Pregunta {i+1}:**")
                
                # Textarea editable para cada pregunta
                edited_pregunta = st.text_area(
                    f"Editar pregunta {i+1}:",
                    value=pregunta,
                    height=80,
                    key=f"edit_question_{tema}_{i}",
                    label_visibility="collapsed"
                )
                
                # Botones de acción para cada pregunta
                col1, col2, col3 = st.columns([1, 1, 4])
                
                with col1:
                    if st.button("💾 Guardar", key=f"save_{tema}_{i}"):
                        if edited_pregunta.strip() and edited_pregunta != pregunta:
                            preguntas[i] = edited_pregunta.strip()
                            if save_questions_to_json(tema, preguntas):
                                st.success("✅ Pregunta actualizada")
                                st.rerun()
                            else:
                                st.error("❌ Error al guardar")
                        elif not edited_pregunta.strip():
                            st.error("❌ La pregunta no puede estar vacía")
                        else:
                            st.info("ℹ️ No hay cambios para guardar")
                
                with col2:
                    if st.button("🗑️ Eliminar", key=f"delete_{tema}_{i}"):
                        if len(preguntas) > 1:  # No permitir eliminar si solo queda una
                            preguntas.pop(i)
                            if save_questions_to_json(tema, preguntas):
                                st.success("✅ Pregunta eliminada")
                                st.rerun()
                            else:
                                st.error("❌ Error al eliminar")
                        else:
                            st.warning("⚠️ No se puede eliminar la última pregunta")
                
                st.markdown("---")
    else:
        st.info("📝 No hay preguntas para este tema. Usa el formulario de arriba para agregar la primera pregunta.")

def save_questions_to_json(tema: str, preguntas: list) -> bool:
    """Guarda las preguntas en el archivo JSON del tema"""
    import json
    import os
    
    try:
        # Crear directorio si no existe
        os.makedirs("temas_ai", exist_ok=True)
        
        # Preparar datos
        data = {
            "tema": tema,
            "preguntas": preguntas
        }
        
        # Guardar archivo
        json_path = os.path.join("temas_ai", f"{tema}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        return True
    except Exception as e:
        st.error(f"Error al guardar {tema}.json: {e}")
        return False

