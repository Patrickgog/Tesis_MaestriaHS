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
from ui.tabs_modules.common import calcular_caudal_por_bomba


def render_data_input_tab():
    """Renderiza la pestaña de datos de entrada completa basada en app.py"""
    # from ui.sidebar import render_sidebar  # ELIMINADO: Ya no se usa aquí
    from ui.accessories import render_accessories_panel
    from data.project_manager import (
        save_project_state, load_project_state, load_project_from_upload,
        export_project_summary, validate_project_data
    )
    from ui.ai_module import generar_datos_json, guardar_json_resultados
    import os
    from core.calculations import (
        calcular_hf_hazen_williams, convert_flow_unit, interpolar_propiedad,
        calculate_adt_for_multiple_flows, process_curve_data, get_pead_data,
        get_pead_espesor, calculate_diametro_interno_pead, get_hierro_ductil_data,
        get_hierro_ductil_diametros_disponibles, calculate_diametro_interno_hierro_ductil,
        get_hierro_fundido_data, get_hierro_fundido_diametros_disponibles,
        get_pvc_data, get_pvc_series_disponibles, get_pvc_diametros_disponibles, calculate_diametro_interno_pvc,
        seleccionar_motor_estandar, calcular_potencia_motor, get_display_unit_label, convert_curve_data_to_display_unit
    )
    # Importar módulo de cálculos hidráulicos (D arcy-Weisbach)
    from core.hydraulics import calcular_perdidas_darcy_weisbach
    # Importar módulo de base de datos de bombas comerciales
    from data.pump_database import (
        load_pump_database, filter_pumps_by_requirements, 
        convert_pump_to_textarea_format, get_pump_summary_info
    )
    from config.constants import HAZEN_WILLIAMS_C, ACCESORIOS_DATA, PEAD_DATA, HIERRO_DUCTIL_DATA, HIERRO_FUNDIDO_DATA, PVC_DATA
    from utils.sync_manager import sync_pipe_data
    
    def create_on_change_callback(section_suffix):
        def callback():
            # Disparar sincronización automática
            sync_pipe_data(section_suffix, 'data_input')
            
            # These are the keys of the widgets themselves
            widget_keys_to_delete = [
                f'diam_externo_{section_suffix}',
                f'serie_{section_suffix}',
                f'clase_hierro_{section_suffix}',
                f'dn_{section_suffix}',
                f'clase_hierro_fundido_{section_suffix}',
                f'dn_hierro_fundido_{section_suffix}',
                f'tipo_union_pvc_{section_suffix}',
                f'serie_pvc_{section_suffix}_nombre',
                f'dn_pvc_{section_suffix}',
            ]
            # Also delete the index keys used to set the selectbox index
            index_keys_to_delete = [
                f'diam_externo_{section_suffix}_index',
                f'serie_{section_suffix}_index',
                f'clase_hierro_{section_suffix}_index',
                f'dn_{section_suffix}_index',
                f'clase_hierro_fundido_{section_suffix}_index',
                f'dn_hierro_fundido_{section_suffix}_index',
                f'tipo_union_pvc_{section_suffix}_index',
                f'serie_pvc_{section_suffix}_nombre_index',
                f'dn_pvc_{section_suffix}_index',
            ]

            for key in widget_keys_to_delete + index_keys_to_delete:
                if key in st.session_state:
                    del st.session_state[key]
        return callback

    def clear_downstream_calculations():
        """
        Invalida valores calculados del punto de operación cuando cambian parámetros de diseño.
        Esto asegura que el análisis IA use siempre los valores de la sesión actual.
        """
        calculated_keys = [
            'caudal_operacion', 'altura_operacion', 'interseccion',
            'eficiencia_operacion', 'potencia_operacion', 
            'npsh_requerido', 'npsh_margen'
        ]
        for key in calculated_keys:
            if key in st.session_state:
                del st.session_state[key]

    # Renderizar sidebar (solo en tab1) - ELIMINADO: Ya se llama desde main.py
    # render_sidebar()  # COMENTADO para evitar duplicación

    def callback_seleccionar_bomba(bomba_data, marca):
        """Callback para cargar curvas de bomba sin conflicto de session_state"""
        try:
            flow_unit = st.session_state.get('flow_unit', 'L/s')
            curvas_texto = convert_pump_to_textarea_format(bomba_data, flow_unit)
            
            # Actualizar session state con las curvas
            for curva_key, texto in curvas_texto.items():
                st.session_state[f'textarea_{curva_key}'] = texto
            
            # Guardar info de la bomba
            st.session_state['bomba_url'] = bomba_data.get('url_ficha_tecnica', '')
            st.session_state['bomba_nombre'] = bomba_data['modelo']
            st.session_state['bomba_descripcion'] = (
                f"Bomba {marca} - Serie {bomba_data['serie']} - "
                f"{bomba_data['potencia_hp']} HP ({bomba_data['potencia_kw']} kW) - "
                f"{bomba_data['etapas']} etapas - {bomba_data['rpm']} RPM\n"
                f"Código: {bomba_data['codigo']}\n"
                f"Tipo: {bomba_data['tipo_bomba']}\n"
                f"Material: {bomba_data['material_impulsor']}"
            )
            
            # Mensaje persistente y limpieza
            st.session_state['search_message'] = ("success", f"✅ Curvas de {bomba_data['modelo']} cargadas exitosamente. Revisa la Sección 4.")
            st.session_state.pop('bombas_compatibles', None)
            st.session_state.pop('search_triggered', None)
            
        except Exception as e:
            st.session_state['search_message'] = ("error", f"Error al cargar curvas: {e}")
    
    # Inicializar valores por defecto si no existen
    defaults = {
        'proyecto': '',
        'diseno': '',
        'caudal_lps': 51.0,
        'caudal_m3h': 183.6,
        'elevacion_sitio': 450.0,
        'altura_succion_input': 1.65,
        'bomba_inundada': False,
        'altura_descarga': 80.0,
        'num_bombas': 1,
        'long_succion': 10.0,
        'diam_succion_mm': 200.0,
        'mat_succion': list(HAZEN_WILLIAMS_C.keys())[0],
        'otras_perdidas_succion': 0.0,
        'accesorios_succion': [],
        'long_impulsion': 500.0,
        'diam_impulsion_mm': 150.0,
        'mat_impulsion': list(HAZEN_WILLIAMS_C.keys())[0],
        'otras_perdidas_impulsion': 0.0,
        'accesorios_impulsion': [],
        'temp_liquido': 20.0,
        'densidad_liquido': 1.0,
        'presion_barometrica_calculada': 0.0
    }
    
    # Siempre asegurar que los valores por defecto estén disponibles
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    
    # SINCRONIZACIÓN AUTOMÁTICA DE DIÁMETROS
    # Esta función asegura que diam_succion_mm y diam_impulsion_mm reflejen
    # los valores calculados desde los datos específicos del material
    def sync_diameters_from_material_data():
        """Sincroniza diam_succion_mm y diam_impulsion_mm con los datos específicos del material"""
        # Sincronizar Succión
        mat_suc = st.session_state.get('mat_succion', 'PVC')
        
        if mat_suc in ["PEAD", "HDPE (Polietileno)"]:
            diam_ext = st.session_state.get('diam_externo_succion', None)
            serie = st.session_state.get('serie_succion', None)
            if diam_ext and serie:
                try:
                    di_calc = calculate_diametro_interno_pead(diam_ext, serie)
                    if di_calc and di_calc > 0:
                        st.session_state['diam_succion_mm'] = di_calc
                except:
                    pass
        
        elif mat_suc == "PVC":
            tipo_union = st.session_state.get('tipo_union_pvc_succion', None)
            serie_pvc = st.session_state.get('serie_pvc_succion_nombre', None)
            dn_pvc = st.session_state.get('dn_pvc_succion', None)
            if tipo_union and serie_pvc and dn_pvc:
                try:
                    di_calc = calculate_diametro_interno_pvc(tipo_union, serie_pvc, dn_pvc)
                    if di_calc and di_calc > 0:
                        st.session_state['diam_succion_mm'] = di_calc
                except:
                    pass
        
        elif mat_suc == "Hierro Dúctil":
            clase = st.session_state.get('clase_hierro_succion', None)
            dn = st.session_state.get('dn_succion', None)
            if clase and dn:
                try:
                    di_calc = calculate_diametro_interno_hierro_ductil(clase, dn)
                    if di_calc and di_calc > 0:
                        st.session_state['diam_succion_mm'] = di_calc
                except:
                    pass
        
        elif mat_suc == "Hierro Fundido":
            clase_hf = st.session_state.get('clase_hierro_fundido_succion', None)
            dn_hf = st.session_state.get('dn_hierro_fundido_succion', None)
            if clase_hf and dn_hf:
                try:
                    data = get_hierro_fundido_data(clase_hf, dn_hf)
                    if data and 'di_mm' in data:
                        st.session_state['diam_succion_mm'] = data['di_mm']
                except:
                    pass
        
        # Sincronizar Impulsión
        mat_imp = st.session_state.get('mat_impulsion', 'PVC')
        
        if mat_imp in ["PEAD", "HDPE (Polietileno)"]:
            diam_ext = st.session_state.get('diam_externo_impulsion', None)
            serie = st.session_state.get('serie_impulsion', None)
            if diam_ext and serie:
                try:
                    di_calc = calculate_diametro_interno_pead(diam_ext, serie)
                    if di_calc and di_calc > 0:
                        st.session_state['diam_impulsion_mm'] = di_calc
                except:
                    pass
        
        elif mat_imp == "PVC":
            tipo_union = st.session_state.get('tipo_union_pvc_impulsion', None)
            serie_pvc = st.session_state.get('serie_pvc_impulsion_nombre', None)
            dn_pvc = st.session_state.get('dn_pvc_impulsion', None)
            if tipo_union and serie_pvc and dn_pvc:
                try:
                    di_calc = calculate_diametro_interno_pvc(tipo_union, serie_pvc, dn_pvc)
                    if di_calc and di_calc > 0:
                        st.session_state['diam_impulsion_mm'] = di_calc
                except:
                    pass
        
        elif mat_imp == "Hierro Dúctil":
            clase = st.session_state.get('clase_hierro_impulsion', None)
            dn = st.session_state.get('dn_impulsion', None)
            if clase and dn:
                try:
                    di_calc = calculate_diametro_interno_hierro_ductil(clase, dn)
                    if di_calc and di_calc > 0:
                        st.session_state['diam_impulsion_mm'] = di_calc
                except:
                    pass
        
        elif mat_imp == "Hierro Fundido":
            clase_hf = st.session_state.get('clase_hierro_fundido_impulsion', None)
            dn_hf = st.session_state.get('dn_hierro_fundido_impulsion', None)
            if clase_hf and dn_hf:
                try:
                    data = get_hierro_fundido_data(clase_hf, dn_hf)
                    if data and 'di_mm' in data:
                        st.session_state['diam_impulsion_mm'] = data['di_mm']
                except:
                    pass
    
    # Ejecutar sincronización automática
    sync_diameters_from_material_data()
    
    def get_current_system_params():
        """Obtiene un diccionario unificado de parámetros del sistema desde el session_state."""
        # Asegurar sincronización con los selectores detallados si existen
        s_di = st.session_state.get('diam_succion_mm', 200.0)
        i_di = st.session_state.get('diam_impulsion_mm', 150.0)
        
        return {
            'long_succion': st.session_state.get('long_succion', 10.0),
            'diam_succion_m': s_di / 1000.0,
            'mat_succion': st.session_state.get('mat_succion', 'PVC'),
            'C_succion': st.session_state.get('coeficiente_hazen_succion', 150),
            'accesorios_succion': st.session_state.get('accesorios_succion', []),
            'otras_perdidas_succion': st.session_state.get('otras_perdidas_succion', 0.0),
            
            'long_impulsion': st.session_state.get('long_impulsion', 500.0),
            'diam_impulsion_m': i_di / 1000.0,
            'mat_impulsion': st.session_state.get('mat_impulsion', 'PVC'),
            'C_impulsion': st.session_state.get('coeficiente_hazen_impulsion', 150),
            'accesorios_impulsion': st.session_state.get('accesorios_impulsion', []),
            'otras_perdidas_impulsion': st.session_state.get('otras_perdidas_impulsion', 0.0),
            
            'altura_succion': st.session_state.get('altura_succion_input', 1.65),
            'altura_descarga': st.session_state.get('altura_descarga', 80.0),
            'bomba_inundada': st.session_state.get('bomba_inundada', False),
            'metodo_calculo': st.session_state.get('metodo_calculo', 'Hazen-Williams'),
            'temp_liquido': st.session_state.get('temp_liquido', 20.0)
        }
    
    
    
    # Información del proyecto
    col1, col2, col3 = st.columns([0.35, 0.35, 0.3])
    
    with col1:
        st.text_input(
            "PROYECTO", 
            key="proyecto", 
            help="Nombre del proyecto."
        )
    
    with col2:
        st.text_input(
            "DISEÑO", 
            key="diseno", 
            help="Nombre del diseño."
        )
    
    with col3:
        pass
    
    # Cálculos de presión
    temperatura_c = st.session_state.get('temp_liquido', 20.0)
    densidad_liquido = st.session_state.get('densidad_liquido', 1.0)
    
    # Función para calcular presión de vapor
    def calcular_presion_vapor_mca(temp_input):
        temp_C = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
        vapor_agua_mca = [0.06, 0.09, 0.12, 0.17, 0.25, 0.33, 0.44, 0.58, 0.76, 0.98, 1.25, 1.61, 2.03, 2.56, 3.20, 3.96, 4.85, 5.93, 7.18, 8.62, 10.33]
        return interpolar_propiedad(temp_input, temp_C, vapor_agua_mca)

    presion_vapor = calcular_presion_vapor_mca(temperatura_c)

    # Cálculo presión barométrica
    from core.calculations import calcular_presion_atmosferica_mca
    elevacion = st.session_state.get('elevacion_sitio', 450.0)
    densidad_agua = densidad_liquido * 1000  # g/cm³ a kg/m³
    G = 9.81
    gamma = densidad_agua * G
    presion_barometrica = calcular_presion_atmosferica_mca(elevacion, gamma)
    st.session_state['presion_barometrica_calculada'] = presion_barometrica

    st.header("Configuración de Parámetros del Sistema")
    st.subheader("1. Condiciones de Operación")
    
    col1, col2, col3 = st.columns([0.25, 0.25, 0.5])
    
    with col1:
        unidad_caudal = st.session_state.get('flow_unit', 'L/s')  # Mantener L/s por defecto
        if unidad_caudal == 'L/s':
            caudal_lps = st.number_input(
                "Caudal de Diseño (L/s)",
                value=st.session_state.get('caudal_lps', 51.0),
                min_value=0.1,
                step=0.1,
                key="caudal_lps",
                on_change=clear_downstream_calculations,
                help="Caudal requerido en litros por segundo para el sistema."
            )
            st.text_input("Caudal en m³/h", value=f"{caudal_lps * 3.6:.2f}", disabled=True)
            # Actualizar caudal_m3h
            st.session_state['caudal_m3h'] = caudal_lps * 3.6
        else:
            caudal_m3h = st.number_input(
                "Caudal de Diseño (m³/h)",
                value=st.session_state.get('caudal_m3h', 183.6),
                min_value=0.1,
                step=0.1,
                key="caudal_m3h",
                on_change=clear_downstream_calculations,
                help="Caudal requerido en metros cúbicos por hora para el sistema."
            )
            st.text_input("Caudal en L/s", value=f"{caudal_m3h / 3.6:.2f}", disabled=True)
            # Actualizar caudal_lps
            st.session_state['caudal_lps'] = caudal_m3h / 3.6
        
        st.number_input(
            "Elevación del sitio (Cota eje bomba) (m)",
            value=st.session_state.get('elevacion_sitio', 450.0),
            min_value=0.0,
            format="%.2f",
            key="elevacion_sitio",
            help="Cota del eje de la bomba. Esta es la elevación de referencia del sistema."
        )
        st.number_input(
            "Altura de Succión (m)", 
            value=st.session_state.get('altura_succion_input', 2.0), 
            min_value=0.0,
            step=0.01,
            on_change=clear_downstream_calculations,
            help="Distancia vertical desde el NIVEL DEL AGUA (superficie libre) hasta el eje de la bomba.", 
            key="altura_succion_input"
        )
        st.checkbox(
            "Bomba debajo del tanque (inundada)", 
            value=st.session_state.get('bomba_inundada', False), 
            help="Marcar si el nivel del agua está ARRIBA del eje de la bomba. Desmarcar si está DEBAJO.", 
            key="bomba_inundada"
        )
        st.number_input(
            "Altura de Descarga (m)", 
            value=st.session_state.get('altura_descarga', 80.0), 
            min_value=0.0,
            step=0.01,
            on_change=clear_downstream_calculations,
            help="Distancia vertical desde el eje de la bomba hasta el punto de entrega.", 
            key="altura_descarga"
        )
        num_bombas_input = st.number_input(
            "Número de Bombas en Paralelo", 
            value=st.session_state.get('num_bombas', 1), 
            min_value=1, 
            step=1, 
            help="Define cuántas bombas idénticas operan en paralelo.", 
            key="num_bombas"
        )
        
        # Advertencia importante sobre selección de bomba
        if num_bombas_input > 1:
            caudal_diseno = st.session_state.get('caudal_lps', 51.0)
            caudal_por_bomba = calcular_caudal_por_bomba(caudal_diseno, num_bombas_input)
            
            st.warning(f"""
            ⚠️ **IMPORTANTE: Selección de Bomba para Sistema en Paralelo**
            
            Con **{num_bombas_input} bombas** en paralelo, cada bomba debe manejar:
            - **Caudal por bomba: {caudal_por_bomba:.2f} L/s**
            - **Altura: Igual a la ADT del sistema**
            
            **📋 Pasos a seguir:**
            1. Busca en el catálogo una bomba que entregue **{caudal_por_bomba:.2f} L/s** a la altura requerida
            2. Ingresa las curvas características de ESA bomba específica (H-Q, Rendimiento, Potencia, NPSH)
            3. La app calculará el punto de operación para cada bomba individual
            4. El sistema total entregará: **{caudal_diseno:.2f} L/s** ({num_bombas_input} × {caudal_por_bomba:.2f} L/s)
            
            ⚠️ **NO uses las curvas de una bomba para {caudal_diseno:.2f} L/s**. Usa las curvas de una bomba para **{caudal_por_bomba:.2f} L/s**.
            """)
        
        # Datos del sistema
        st.markdown("---")
        st.markdown("**📊 Datos del Sistema:**")
        
        # Usar valores precalculados del session_state
        altura_succion_val = st.session_state.get('altura_succion_input', 2.0)
        bomba_inundada_val = st.session_state.get('bomba_inundada', False)
        long_succion_val = st.session_state.get('long_succion', 10.0)
        long_impulsion_val = st.session_state.get('long_impulsion', 150.0)
        
        # Calcular Altura de Succión Estática (Hs)
        if bomba_inundada_val:
            altura_succion_estatica = +altura_succion_val  # Positiva
        else:
            altura_succion_estatica = -altura_succion_val  # Negativa
        
        # Obtener altura de descarga
        altura_descarga_val = st.session_state.get('altura_descarga', 80.0)
        
        # Calcular Altura Estática Total
        z_descarga = altura_descarga_val
        z_nivel_agua = altura_succion_estatica
        altura_estatica_total_calc = z_descarga - z_nivel_agua
        
        st.markdown(f"- **Altura Succión Estática (Hs):** {altura_succion_estatica:.2f} m {'(+Positiva)' if altura_succion_estatica > 0 else '(-Negativa)'}")
        st.markdown(f"- **Altura Estática Total:** {altura_estatica_total_calc:.2f} m")
        st.markdown(f"- **Longitud Total Tuberías:** {long_succion_val + long_impulsion_val:.1f} m")
        st.markdown("- **ADT:** Ver sección Resumen del Sistema abajo ⬇️")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botones de gestión de proyecto (Descarga y Guardado como)
        st.markdown("**Gestión del Proyecto**")
        
        # Botones principales de exportación
        col_btn3, col_btn4 = st.columns(2)

        with col_btn3:
            # Generar nombre de archivo para descarga
            proyecto_name = st.session_state.get('proyecto', 'proyecto').replace(' ', '_')
            filename = f"Sistemas de Bombeo_{proyecto_name}.json"
            
            # Usar generar_datos_json para asegurar que se descarga el estado completo
            project_data_to_download = generar_datos_json()

            st.download_button(
                label="📥 Descargar Proyecto",
                data=json.dumps(project_data_to_download, indent=4, ensure_ascii=False),
                file_name=filename,
                mime="application/json",
                help="Descarga el proyecto actual como un archivo JSON.",
                use_container_width=True
            )
        
        with col_btn4:
            if st.button("💾 Guardar Como...", help="Permite guardar el proyecto con un nombre personalizado.", use_container_width=True):
                st.session_state['show_custom_save'] = True
        
        # Información sobre el entorno
        st.info("💻 **Modo Local:** Los proyectos se guardan en archivos locales y en la sesión.")
        
        # Modal para guardar con nombre personalizado
        if st.session_state.get('show_custom_save', False):
            with st.expander("💾 Guardar Proyecto con Nombre Personalizado", expanded=True):
                custom_filename = st.text_input(
                    "Nombre del archivo (sin extensión):",
                    value=f"{st.session_state.get('proyecto', 'proyecto')}_{st.session_state.get('diseno', 'diseno')}",
                    help="Ingresa el nombre del archivo sin la extensión .json"
                )
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if custom_filename.strip():
                        filename = f"{custom_filename.strip()}.json"
                        # Generar datos actualizados para descarga
                        project_data_custom = generar_datos_json()
                        
                        st.download_button(
                            label="📥 Confirmar y Descargar",
                            data=json.dumps(project_data_custom, indent=4, ensure_ascii=False),
                            file_name=filename,
                            mime="application/json",
                            key="confirm_custom_download",
                            use_container_width=True,
                            on_click=lambda: st.session_state.update({'show_custom_save': False})
                        )
                    else:
                        st.error("❌ Por favor ingresa un nombre válido para el archivo")
                
                with col_cancel:
                    if st.button("❌ Cancelar", key="custom_save_cancel"):
                        st.session_state['show_custom_save'] = False
        
        # Cargar proyecto desde archivo
        st.markdown("---")
        uploaded_file = st.file_uploader(
            "📂 Cargar Proyecto JSON", 
            type=["json"], 
            key="file_uploader_json_config",
            help="Selecciona un archivo JSON de proyecto para cargar todos los datos guardados previamente."
        )
        
        if uploaded_file is not None:
            file_identifier = f"{uploaded_file.name}_{uploaded_file.size}"
            if st.session_state.get('last_uploaded_file_id') != file_identifier:
                try:
                    if load_project_from_upload(uploaded_file):
                        st.session_state['last_uploaded_file_id'] = file_identifier
                        st.success("✅ Proyecto cargado correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al cargar el proyecto")
                except Exception as e:
                    st.error(f"❌ Error al cargar el archivo: {e}")
    
    with col3:
        st.markdown("**📐 Diagrama Esquemático del Sistema**")
        
        # Obtener parámetros para el diagrama
        altura_succion = st.session_state.get('altura_succion_input', 2.0)
        nivel_agua = st.session_state.get('nivel_agua_tanque', 1.59)
        altura_descarga = st.session_state.get('altura_descarga', 80.0)
        bomba_inundada = st.session_state.get('bomba_inundada', False)
        long_succion = st.session_state.get('long_succion', 10.0)
        long_impulsion = st.session_state.get('long_impulsion', 150.0)
        diam_succion = st.session_state.get('diam_succion_mm', 61.4)
        diam_impulsion = st.session_state.get('diam_impulsion_mm', 40.8)
        
        # Calcular elevaciones con extensión de tubería
        # Check DESACTIVADO: bomba SOBRE tanque (tanque debajo, elev negativa)
        # Check ACTIVADO: bomba DEBAJO tanque (tanque arriba, elev positiva)
        
        # Extensión adicional de tubería vertical (metros)
        extension_tuberia = 3.0  # 3 metros adicionales de tubería vertical
        
        if bomba_inundada:
            # Bomba inundada: tanque ARRIBA del eje
            elev_tanque_suc = altura_succion + extension_tuberia
            nivel_agua_abs = elev_tanque_suc + nivel_agua
        else:
            # Bomba en aspiración: tanque DEBAJO del eje
            elev_tanque_suc = -(altura_succion + extension_tuberia)
            nivel_agua_abs = elev_tanque_suc + nivel_agua
        
        elev_tanque_desc = altura_descarga
        
        # Crear el diagrama SVG con mayor ancho
        svg_width = 800  # Aumentado a 800 para mejor integración
        svg_height = 700
        
        # Escala: convertir coordenadas del usuario (0-20) a píxeles
        escala = 35  # 35 píxeles por unidad
        offset_x = 120  # Mayor margen para centrar mejor
        offset_y = 50  # Margen superior
        
        # Función para convertir coordenadas del usuario a píxeles
        def coord_x(x):
            return offset_x + (x * escala)
        
        def coord_y(y):
            return offset_y + (y * escala)
        
        # Colores
        color_agua = "#4A90E2"
        color_tanque = "#34495E"
        color_tuberia = "#7F8C8D"
        color_bomba = "#E74C3C"
        color_nivel = "#3498DB"
        
        # Determinar posiciones según el check
        # Check DESACTIVADO: eje en y=9, tanque succión DEBAJO
        # Check ACTIVADO: eje en y=13, tanque succión ARRIBA, descarga MÁS ARRIBA
        if bomba_inundada:
            # Eje de bomba más abajo
            y_eje_bomba = 13
            # Tanque succión ARRIBA del eje (más angosto: 1.5 unidades)
            x_tanque_suc = 0.75
            y_tanque_suc_top = 6
            y_tanque_suc_bottom = 9
            y_tub_vert_suc_start = 9
            # Tanque descarga MÁS ARRIBA (más angosto: 1.5 unidades)
            y_tanque_desc_top = 0
            y_tanque_desc_bottom = 3
            # Tubería llega al nivel del agua (30% del tanque)
            y_impulsion_vert_end = y_tanque_desc_top + (y_tanque_desc_bottom - y_tanque_desc_top) * 0.3
        else:
            # Eje de bomba normal
            y_eje_bomba = 9
            # Tanque succión DEBAJO del eje (más angosto: 1.5 unidades)
            x_tanque_suc = 0.75
            y_tanque_suc_top = 14
            y_tanque_suc_bottom = 17
            y_tub_vert_suc_start = 14
            # Tanque descarga arriba normal (más angosto: 1.5 unidades)
            y_tanque_desc_top = 0
            y_tanque_desc_bottom = 3
            # Tubería llega al nivel del agua (30% del tanque)
            y_impulsion_vert_end = y_tanque_desc_top + (y_tanque_desc_bottom - y_tanque_desc_top) * 0.3
        
        # Construir SVG con coordenadas corregidas y eje variable
        svg_content = f'''<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
<rect width="{svg_width}" height="{svg_height}" fill="#F8F9FA"/>
<line x1="0" y1="{coord_y(y_eje_bomba)}" x2="{svg_width}" y2="{coord_y(y_eje_bomba)}" stroke="#BDC3C7" stroke-width="1" stroke-dasharray="5,5"/>
<text x="10" y="{coord_y(y_eje_bomba) - 5}" fill="#7F8C8D" font-size="11">Eje Bomba (0.00 m)</text>
<g id="tanque_succion">
<rect x="{coord_x(x_tanque_suc)}" y="{coord_y(y_tanque_suc_top)}" width="{coord_x(1.5)}" height="{coord_y(y_tanque_suc_bottom) - coord_y(y_tanque_suc_top)}" fill="{color_tanque}" stroke="#2C3E50" stroke-width="2"/>
<rect x="{coord_x(x_tanque_suc) + 5}" y="{coord_y(y_tanque_suc_top) + (coord_y(y_tanque_suc_bottom) - coord_y(y_tanque_suc_top)) * 0.3}" width="{coord_x(1.5) - 10}" height="{(coord_y(y_tanque_suc_bottom) - coord_y(y_tanque_suc_top)) * 0.7}" fill="{color_agua}" opacity="0.6"/>
<line x1="{coord_x(x_tanque_suc)}" y1="{coord_y(y_tanque_suc_top) + (coord_y(y_tanque_suc_bottom) - coord_y(y_tanque_suc_top)) * 0.3}" x2="{coord_x(x_tanque_suc + 1.5)}" y2="{coord_y(y_tanque_suc_top) + (coord_y(y_tanque_suc_bottom) - coord_y(y_tanque_suc_top)) * 0.3}" stroke="{color_nivel}" stroke-width="2"/>
<text x="{coord_x(x_tanque_suc + 0.75)}" y="{coord_y(y_tanque_suc_top) - 5}" text-anchor="middle" fill="{color_tanque}" font-size="13" font-weight="bold">Tanque Succión</text>
<text x="{coord_x(x_tanque_suc + 1.5) + 15}" y="{coord_y(y_tanque_suc_top) + (coord_y(y_tanque_suc_bottom) - coord_y(y_tanque_suc_top)) * 0.3 + 5}" fill="white" font-size="12" font-weight="bold">h = {nivel_agua:.2f} m</text>
<text x="{coord_x(x_tanque_suc + 1.5) + 15}" y="{coord_y(y_tanque_suc_bottom) + 15}" fill="white" font-size="11" font-weight="bold">Fondo: {elev_tanque_suc:.2f} m</text>
</g>
<g id="tuberia_succion">
<line x1="{coord_x(1.5)}" y1="{coord_y(y_tub_vert_suc_start)}" x2="{coord_x(1.5)}" y2="{coord_y(y_eje_bomba)}" stroke="{color_tuberia}" stroke-width="5"/>
<line x1="{coord_x(1.5)}" y1="{coord_y(y_eje_bomba)}" x2="{coord_x(4.6)}" y2="{coord_y(y_eje_bomba)}" stroke="{color_tuberia}" stroke-width="5"/>
<text x="{coord_x(1.5) + 10}" y="{(coord_y(y_tub_vert_suc_start) + coord_y(y_eje_bomba)) / 2}" fill="{color_tuberia}" font-size="11">L = {long_succion:.1f} m</text>
<text x="{coord_x(1.5) + 10}" y="{(coord_y(y_tub_vert_suc_start) + coord_y(y_eje_bomba)) / 2 + 16}" fill="{color_tuberia}" font-size="11">Ø {diam_succion:.1f} mm</text>
<text x="{coord_x(1.5) - 65}" y="{(coord_y(y_tub_vert_suc_start) + coord_y(y_eje_bomba)) / 2 + 5}" fill="{color_tuberia}" font-size="11" font-weight="bold">H = {altura_succion:.1f}m</text>
</g>
<g id="bomba">
<rect x="{coord_x(4.6)}" y="{coord_y(y_eje_bomba) - 15}" width="{coord_x(0.8)}" height="30" rx="5" fill="{color_bomba}" stroke="#C0392B" stroke-width="2"/>
<circle cx="{coord_x(5)}" cy="{coord_y(y_eje_bomba)}" r="12" fill="{color_bomba}" stroke="#C0392B" stroke-width="2"/>
<path d="M {coord_x(5)} {coord_y(y_eje_bomba) - 6} L {coord_x(5)} {coord_y(y_eje_bomba) + 6} M {coord_x(5) - 3} {coord_y(y_eje_bomba) + 3} L {coord_x(5)} {coord_y(y_eje_bomba) + 6} L {coord_x(5) + 3} {coord_y(y_eje_bomba) + 3}" stroke="white" stroke-width="2" fill="none"/>
<text x="{coord_x(5)}" y="{coord_y(y_eje_bomba) + 30}" text-anchor="middle" fill="{color_bomba}" font-size="12" font-weight="bold">BOMBA</text>
</g>
<g id="tuberia_impulsion">
<line x1="{coord_x(5.5)}" y1="{coord_y(y_eje_bomba)}" x2="{coord_x(10)}" y2="{coord_y(y_eje_bomba)}" stroke="{color_tuberia}" stroke-width="5"/>
<line x1="{coord_x(10)}" y1="{coord_y(y_eje_bomba)}" x2="{coord_x(10)}" y2="{coord_y(y_impulsion_vert_end)}" stroke="{color_tuberia}" stroke-width="5"/>
<line x1="{coord_x(10)}" y1="{coord_y(y_impulsion_vert_end)}" x2="{coord_x(13.5)}" y2="{coord_y(y_impulsion_vert_end)}" stroke="{color_tuberia}" stroke-width="5"/>
<text x="{coord_x(10) - 65}" y="{(coord_y(y_eje_bomba) + coord_y(y_impulsion_vert_end)) / 2 - 8}" fill="{color_tuberia}" font-size="11">L = {long_impulsion:.1f} m</text>
<text x="{coord_x(10) - 65}" y="{(coord_y(y_eje_bomba) + coord_y(y_impulsion_vert_end)) / 2 + 8}" fill="{color_tuberia}" font-size="11">Ø {diam_impulsion:.1f} mm</text>
<text x="{coord_x(10) + 10}" y="{(coord_y(y_eje_bomba) + coord_y(y_impulsion_vert_end)) / 2}" fill="{color_tuberia}" font-size="11">H = {altura_descarga:.1f} m</text>
</g>
<g id="tanque_descarga">
<rect x="{coord_x(13.75)}" y="{coord_y(y_tanque_desc_top)}" width="{coord_x(1.5)}" height="{coord_y(y_tanque_desc_bottom) - coord_y(y_tanque_desc_top)}" fill="{color_tanque}" stroke="#2C3E50" stroke-width="2"/>
<rect x="{coord_x(13.75) + 5}" y="{coord_y(y_tanque_desc_top) + (coord_y(y_tanque_desc_bottom) - coord_y(y_tanque_desc_top)) * 0.3}" width="{coord_x(1.5) - 10}" height="{(coord_y(y_tanque_desc_bottom) - coord_y(y_tanque_desc_top)) * 0.7}" fill="{color_agua}" opacity="0.6"/>
<line x1="{coord_x(13.75)}" y1="{coord_y(y_tanque_desc_top) + (coord_y(y_tanque_desc_bottom) - coord_y(y_tanque_desc_top)) * 0.3}" x2="{coord_x(13.75 + 1.5)}" y2="{coord_y(y_tanque_desc_top) + (coord_y(y_tanque_desc_bottom) - coord_y(y_tanque_desc_top)) * 0.3}" stroke="{color_nivel}" stroke-width="2"/>
<text x="{coord_x(13.75 + 0.75)}" y="{coord_y(y_tanque_desc_top) - 5}" text-anchor="middle" fill="{color_tanque}" font-size="13" font-weight="bold">Tanque Descarga</text>
<text x="{coord_x(13.75 + 1.5) + 15}" y="{coord_y(y_impulsion_vert_end) + 5}" fill="white" font-size="11" font-weight="bold">+{altura_descarga:.1f} m</text>
</g>
<g id="leyenda">
<text x="10" y="22" fill="#2C3E50" font-size="15" font-weight="bold">Sistema de Bombeo</text>
<text x="10" y="42" fill="#2C3E50" font-size="13" font-weight="bold">{"Bomba Inundada" if bomba_inundada else "Bomba en Aspiración"}</text>
</g>
</svg>'''
        
        st.markdown(svg_content, unsafe_allow_html=True)
        
        # Guardar el SVG para el PDF
        # Convertir SVG a imagen usando matplotlib
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            from io import BytesIO
            import base64
            
            # Crear figura para el diagrama
            fig_diagrama, ax = plt.subplots(figsize=(10, 8))
            ax.axis('off')
            
            # Agregar el SVG como texto (simplificado para el PDF)
            # En lugar de renderizar SVG complejo, crear una representación visual básica
            ax.text(0.5, 0.95, "Sistema de Bombeo", ha='center', va='top', 
                   fontsize=16, fontweight='bold', transform=ax.transAxes)
            ax.text(0.5, 0.90, f"{'Bomba Inundada' if bomba_inundada else 'Bomba en Aspiración'}", 
                   ha='center', va='top', fontsize=12, transform=ax.transAxes)
            
            # Dibujar representación simplificada
            if bomba_inundada:
                # Tanque succión arriba
                rect_suc = patches.Rectangle((0.1, 0.6), 0.15, 0.2, linewidth=2, 
                                            edgecolor='#34495E', facecolor='#4A90E2', alpha=0.6)
                ax.add_patch(rect_suc)
                ax.text(0.175, 0.82, 'Tanque\nSucción', ha='center', va='center', fontsize=10)
                
                # Bomba en el medio
                circle_bomba = patches.Circle((0.5, 0.5), 0.05, linewidth=2, 
                                             edgecolor='#C0392B', facecolor='#E74C3C')
                ax.add_patch(circle_bomba)
                ax.text(0.5, 0.42, 'BOMBA', ha='center', va='top', fontsize=10, fontweight='bold')
                
                # Tanque descarga arriba
                rect_desc = patches.Rectangle((0.75, 0.75), 0.15, 0.2, linewidth=2, 
                                             edgecolor='#34495E', facecolor='#4A90E2', alpha=0.6)
                ax.add_patch(rect_desc)
                ax.text(0.825, 0.97, 'Tanque\nDescarga', ha='center', va='center', fontsize=10)
                
                # Tuberías
                ax.plot([0.175, 0.175, 0.45], [0.6, 0.5, 0.5], linewidth=3, color='#7F8C8D')
                ax.plot([0.55, 0.825, 0.825], [0.5, 0.5, 0.75], linewidth=3, color='#7F8C8D')
                
                # Etiquetas
                ax.text(0.12, 0.55, f'Hs={altura_succion:.1f}m', fontsize=9, color='#7F8C8D')
                ax.text(0.88, 0.62, f'Hd={altura_descarga:.1f}m', fontsize=9, color='#7F8C8D')
            else:
                # Tanque succión abajo
                rect_suc = patches.Rectangle((0.1, 0.1), 0.15, 0.2, linewidth=2, 
                                            edgecolor='#34495E', facecolor='#4A90E2', alpha=0.6)
                ax.add_patch(rect_suc)
                ax.text(0.175, 0.05, 'Tanque\nSucción', ha='center', va='top', fontsize=10)
                
                # Bomba en el medio
                circle_bomba = patches.Circle((0.5, 0.5), 0.05, linewidth=2, 
                                             edgecolor='#C0392B', facecolor='#E74C3C')
                ax.add_patch(circle_bomba)
                ax.text(0.5, 0.42, 'BOMBA', ha='center', va='top', fontsize=10, fontweight='bold')
                
                # Tanque descarga arriba
                rect_desc = patches.Rectangle((0.75, 0.75), 0.15, 0.2, linewidth=2, 
                                             edgecolor='#34495E', facecolor='#4A90E2', alpha=0.6)
                ax.add_patch(rect_desc)
                ax.text(0.825, 0.97, 'Tanque\nDescarga', ha='center', va='center', fontsize=10)
                
                # Tuberías
                ax.plot([0.175, 0.175, 0.45], [0.3, 0.5, 0.5], linewidth=3, color='#7F8C8D')
                ax.plot([0.55, 0.825, 0.825], [0.5, 0.5, 0.75], linewidth=3, color='#7F8C8D')
                
                # Etiquetas
                ax.text(0.12, 0.4, f'Hs={altura_succion:.1f}m', fontsize=9, color='#7F8C8D')
                ax.text(0.88, 0.62, f'Hd={altura_descarga:.1f}m', fontsize=9, color='#7F8C8D')
            
            # Línea de referencia (eje bomba)
            ax.axhline(y=0.5, color='#BDC3C7', linestyle='--', linewidth=1, alpha=0.5)
            ax.text(0.02, 0.51, 'Eje Bomba (0.00 m)', fontsize=9, color='#7F8C8D')
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            
            # Guardar en session_state
            st.session_state['diagrama_esquematico_fig'] = fig_diagrama
            plt.close(fig_diagrama)  # Cerrar para liberar memoria
            
        except Exception as e:
            # Si hay error, al menos guardar los parámetros
            st.session_state['diagrama_esquematico_params'] = {
                'altura_succion': altura_succion,
                'altura_descarga': altura_descarga,
                'bomba_inundada': bomba_inundada,
                'long_succion': long_succion,
                'long_impulsion': long_impulsion
            }
    
    st.markdown("---")

    # Secciones 2 y 3 en tres columnas 35-35-30%
    col_suc, col_imp, col_empty = st.columns([0.35, 0.35, 0.3])
    
    # --- Función Auxiliar para Migración ---
    def migrate_diameter(prefix, target_mat, target_di):
        """Intenta sincronizar los selectores detallados con el material y DI importados."""
        # 1. Ajustar material principal
        st.session_state[f'mat_{prefix}'] = target_mat
        
        # 2. Lógica de emparejamiento por material
        if target_mat in ["PEAD", "HDPE (Polietileno)"]:
            best_ext = PEAD_DATA[0]["diametro_nominal_mm"]
            min_diff = 999
            for item in PEAD_DATA:
                # Probar con una serie estándar (ej: s10) para comparar DI
                if "s10" in item and item["s10"]["espesor_mm"]:
                    di_est = item["diametro_nominal_mm"] - 2 * item["s10"]["espesor_mm"]
                    diff = abs(di_est - target_di)
                    if diff < min_diff:
                        min_diff = diff
                        best_ext = item["diametro_nominal_mm"]
            st.session_state[f'diam_externo_{prefix}'] = best_ext
            st.session_state[f'diam_externo_{prefix}_index'] = [i["diametro_nominal_mm"] for i in PEAD_DATA].index(best_ext)
            
        elif target_mat == "PVC":
            # Usar unión elastomérica por defecto para la búsqueda
            series = ["s20", "s16", "s12_5", "s10", "s8", "s6_3"]
            best_dn = 110
            min_diff = 999
            for s in series:
                d_list = get_pvc_diametros_disponibles("union_elastomerica", s)
                for dn in d_list:
                    data = get_pvc_data("union_elastomerica", s, dn)
                    if data:
                        di_pvc = data["de_mm"] - (data["espesor_min_mm"] + data["espesor_max_mm"])
                        diff = abs(di_pvc - target_di)
                        if diff < min_diff:
                            min_diff = diff
                            best_dn = dn
            st.session_state[f'dn_pvc_{prefix}'] = best_dn
            # Los índices se recalcularán en el renderizado
            
        elif target_mat == "Hierro Dúctil":
            d_list = get_hierro_ductil_diametros_disponibles("c40")
            best_dn = d_list[0] if d_list else 100
            min_diff = 999
            for dn in d_list:
                data = get_hierro_ductil_data("c40", dn)
                if data:
                    di_h = data["de_mm"] - 2 * data["espesor_nominal_mm"]
                    diff = abs(di_h - target_di)
                    if diff < min_diff:
                        min_diff = diff
                        best_dn = dn
            st.session_state[f'dn_{prefix}'] = best_dn

        elif target_mat == "Hierro Fundido":
            d_list = get_hierro_fundido_diametros_disponibles("clase_150")
            best_dn = d_list[0] if d_list else 100
            min_diff = 999
            for dn in d_list:
                data = get_hierro_fundido_data("clase_150", dn)
                if data:
                    diff = abs(data["di_mm"] - target_di)
                    if diff < min_diff:
                        min_diff = diff
                        best_dn = dn
            st.session_state[f'dn_hierro_fundido_{prefix}'] = best_dn
            
        else:
            # Material genérico
            st.session_state[f'diam_{prefix}_mm'] = target_di

    with col_suc:
        st.subheader("2. Tubería y Accesorios de Succión")
        
        
        # Indicador de sincronización automática
        from utils.sync_manager import render_sync_indicator
        render_sync_indicator('succion')



        st.number_input(
            "Longitud Tubería (m)",
            value=st.session_state.get('long_succion', 10.0),
            min_value=0.0,
            step=0.01,
            key="long_succion",
            help="Longitud total de la tubería de succión desde la fuente hasta la bomba."
        )
        # Material de succión
        mat_succion_options = list(HAZEN_WILLIAMS_C.keys())
        current_mat_succion = st.session_state.get('mat_succion', mat_succion_options[0])
        # Validar que el material actual existe en las opciones
        if current_mat_succion not in mat_succion_options:
            current_mat_succion = mat_succion_options[0]
            st.session_state['mat_succion'] = current_mat_succion
        mat_succion_index = mat_succion_options.index(current_mat_succion)
        
        on_mat_succion_change = create_on_change_callback('succion')
        mat_succion = st.selectbox(
            "Material Tubería",
            options=mat_succion_options,
            index=mat_succion_index,
            key="mat_succion",
            help="Selecciona el material de la tubería de succión.",
            on_change=on_mat_succion_change
        )
        
        # Configuración específica para PEAD/HDPE
        if mat_succion in ["PEAD", "HDPE (Polietileno)"]:
            # Diámetro externo para PEAD
            diametros_pead = [item["diametro_nominal_mm"] for item in PEAD_DATA]
            
            # Validar que hay datos disponibles
            if not diametros_pead:
                st.error("No hay datos de tuberías PEAD disponibles. Verifique el archivo pead_data.json")
                return
            
            diam_externo_succion = st.selectbox(
                "Diámetro Externo (mm)",
                options=diametros_pead,
                index=st.session_state.get('diam_externo_succion_index', 0),
                key="diam_externo_succion",
                help="Selecciona el diámetro externo de la tubería PEAD."
            )
            
            # Guardar el índice actual solo si diam_externo_succion no es None
            if diam_externo_succion is not None:
                try:
                    st.session_state['diam_externo_succion_index'] = diametros_pead.index(diam_externo_succion)
                except ValueError:
                    # Si no se encuentra el valor, usar el índice por defecto
                    st.session_state['diam_externo_succion_index'] = 0
            
            # Obtener datos de la tubería PEAD seleccionada
            pead_data_succion = get_pead_data(diam_externo_succion)
            if pead_data_succion:
                # Series disponibles para este diámetro
                series_disponibles = []
                if pead_data_succion is not None:
                    for serie_key in ["s12_5", "s10", "s8", "s6_3", "s5", "s4"]:
                        if serie_key in pead_data_succion and pead_data_succion[serie_key]["espesor_mm"] is not None:
                            series_disponibles.append(serie_key)
                
                if series_disponibles:
                    # Índice seguro para serie_succion
                    safe_serie_succion_index = st.session_state.get('serie_succion_index', 0)
                    if safe_serie_succion_index >= len(series_disponibles):
                        safe_serie_succion_index = 0
                    
                    serie_succion = st.selectbox(
                        "Serie del Tubo",
                        options=series_disponibles,
                        index=safe_serie_succion_index,
                        key="serie_succion",
                        help="Selecciona la serie del tubo PEAD."
                    )
                    # Guardar el índice actual
                    if serie_succion is not None:
                        try:
                            st.session_state['serie_succion_index'] = series_disponibles.index(serie_succion)
                        except ValueError:
                            st.session_state['serie_succion_index'] = 0
                    
                    # Obtener espesor, presión y calcular diámetro interno
                    if serie_succion is not None and serie_succion in pead_data_succion:
                        espesor_succion = pead_data_succion[serie_succion]["espesor_mm"]
                        presion_succion = pead_data_succion[serie_succion]["presion_mpa"]
                        sdr_succion = pead_data_succion[serie_succion]["sdr"]
                        st.session_state['espesor_succion'] = espesor_succion
                        st.session_state['presion_nominal_succion'] = presion_succion
                        st.session_state['sdr_succion'] = sdr_succion
                    else:
                        espesor_succion = None
                        presion_succion = None
                        sdr_succion = None
                    diam_interno_succion = calculate_diametro_interno_pead(diam_externo_succion, espesor_succion)
                    st.session_state['diam_interno_succion'] = diam_interno_succion
                    
                    st.info(f"**Espesor de pared:** {espesor_succion} mm")
                    st.info(f"**SDR:** {sdr_succion}")
                    st.info(f"**Presión nominal de trabajo:** {presion_succion} MPa")
                    if diam_interno_succion is not None:
                        st.info(f"**Diámetro interno calculado:** {diam_interno_succion:.1f} mm")
                        # Guardar el diámetro interno calculado en session_state
                        st.session_state['diam_succion_mm'] = diam_interno_succion
                    else:
                        st.info("**Diámetro interno calculado:** No disponible")
                else:
                    st.warning("No hay series disponibles para este diámetro.")
            else:
                st.error("Error al cargar datos de tubería PEAD.")
        elif mat_succion == "Hierro Dúctil":
            # Configuración específica para Hierro Dúctil
            clases_hierro = ["C40", "C30", "C25", "C20"]
            clase_hierro_succion = st.selectbox(
                "Clase de Presión",
                options=clases_hierro,
                index=st.session_state.get('clase_hierro_succion_index', 0),
                key="clase_hierro_succion",
                help="Selecciona la clase de presión para la tubería de hierro dúctil."
            )
            # Guardar el índice actual
            if clase_hierro_succion is not None:
                try:
                    st.session_state['clase_hierro_succion_index'] = clases_hierro.index(clase_hierro_succion)
                except ValueError:
                    st.session_state['clase_hierro_succion_index'] = 0
            
            # Diámetros disponibles para la clase seleccionada
            if clase_hierro_succion is not None:
                diametros_hierro = get_hierro_ductil_diametros_disponibles(clase_hierro_succion.lower())
            else:
                diametros_hierro = []
            if diametros_hierro:
                # Índice seguro para dn_succion
                safe_dn_succion_index = st.session_state.get('dn_succion_index', 0)
                if safe_dn_succion_index >= len(diametros_hierro):
                    safe_dn_succion_index = 0
                    
                dn_succion = st.selectbox(
                    "Diámetro Nominal (DN mm)",
                    options=diametros_hierro,
                    index=safe_dn_succion_index,
                    key="dn_succion",
                    help="Selecciona el diámetro nominal de la tubería de hierro dúctil."
                )
                # Guardar el índice actual
                if dn_succion is not None:
                    try:
                        st.session_state['dn_succion_index'] = diametros_hierro.index(dn_succion)
                    except ValueError:
                        st.session_state['dn_succion_index'] = 0
                
                # Obtener datos de la tubería
                if clase_hierro_succion is not None:
                    tuberia_hierro = get_hierro_ductil_data(clase_hierro_succion.lower(), dn_succion)
                else:
                    tuberia_hierro = None
                if tuberia_hierro:
                    st.session_state['espesor_succion'] = tuberia_hierro["espesor_nominal_mm"]
                    diametro_interno = calculate_diametro_interno_hierro_ductil(
                        tuberia_hierro["de_mm"], 
                        tuberia_hierro["espesor_nominal_mm"]
                    )
                    st.session_state['diam_interno_succion'] = diametro_interno
                    if diametro_interno is not None:
                        st.session_state['diam_succion_mm'] = diametro_interno
                    
                    # Mostrar información calculada
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**DE (mm):** {tuberia_hierro['de_mm']}")
                        st.info(f"**Espesor Nominal (mm):** {tuberia_hierro['espesor_nominal_mm']}")
                    with col2:
                        st.info(f"**DI (mm):** {diametro_interno:.1f}")
                        st.info(f"**PFA (bar):** {tuberia_hierro['pfa_bar']}")
                        st.info(f"**PMA (bar):** {tuberia_hierro['pma_bar']}")
                else:
                    st.warning("No se encontraron datos para esta combinación de clase y diámetro")
            else:
                st.warning("No hay diámetros disponibles para esta clase")
        elif mat_succion == "Hierro Fundido":
            # Configuración específica para Hierro Fundido
            clases_hierro_fundido = ["Clase 150", "Clase 125", "Clase 100"]
            clase_hierro_fundido_succion = st.selectbox(
                "Clase de Presión",
                options=clases_hierro_fundido,
                index=st.session_state.get('clase_hierro_fundido_succion_index', 0),
                key="clase_hierro_fundido_succion",
                help="Selecciona la clase de presión para la tubería de hierro fundido."
            )
            # Guardar el índice actual
            if clase_hierro_fundido_succion is not None:
                try:
                    st.session_state['clase_hierro_fundido_succion_index'] = clases_hierro_fundido.index(clase_hierro_fundido_succion)
                except ValueError:
                    st.session_state['clase_hierro_fundido_succion_index'] = 0
            
            # Mapear clase a clave del JSON
            if clase_hierro_fundido_succion is not None:
                clase_key = clase_hierro_fundido_succion.lower().replace(" ", "_")
            else:
                clase_key = "c40"  # Valor por defecto
            
            # Diámetros disponibles para la clase seleccionada
            diametros_hierro_fundido = get_hierro_fundido_diametros_disponibles(clase_key)
            if diametros_hierro_fundido:
                # Índice seguro para dn_hierro_fundido_succion
                safe_dn_hf_succion_index = st.session_state.get('dn_hierro_fundido_succion_index', 0)
                if safe_dn_hf_succion_index >= len(diametros_hierro_fundido):
                    safe_dn_hf_succion_index = 0

                dn_hierro_fundido_succion = st.selectbox(
                    "Diámetro Nominal (DN mm)",
                    options=diametros_hierro_fundido,
                    index=safe_dn_hf_succion_index,
                    key="dn_hierro_fundido_succion",
                    help="Selecciona el diámetro nominal de la tubería de hierro fundido."
                )
                # Guardar el índice actual
                if dn_hierro_fundido_succion is not None:
                    try:
                        st.session_state['dn_hierro_fundido_succion_index'] = diametros_hierro_fundido.index(dn_hierro_fundido_succion)
                    except ValueError:
                        st.session_state['dn_hierro_fundido_succion_index'] = 0
                
                # Obtener datos de la tubería
                tuberia_hierro_fundido = get_hierro_fundido_data(clase_key, dn_hierro_fundido_succion)
                if tuberia_hierro_fundido:
                    st.session_state['espesor_succion'] = tuberia_hierro_fundido["espesor_mm"]
                    # Usar el DI directamente de la tabla
                    diametro_interno = tuberia_hierro_fundido["di_mm"]
                    st.session_state['diam_interno_succion'] = diametro_interno
                    if diametro_interno is not None:
                        st.session_state['diam_succion_mm'] = diametro_interno
                    
                    # Mostrar información calculada
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**DE (mm):** {tuberia_hierro_fundido['de_mm']}")
                        st.info(f"**Espesor (mm):** {tuberia_hierro_fundido['espesor_mm']}")
                    with col2:
                        st.info(f"**DI (mm):** {diametro_interno}")
                        st.info(f"**P. Trabajo (bar):** {tuberia_hierro_fundido['pfa_bar']}")
                        st.info(f"**P. Máxima (bar):** {tuberia_hierro_fundido['pma_bar']}")
                else:
                    st.warning("No se encontraron datos para esta combinación de clase y diámetro")
            else:
                st.warning("No hay diámetros disponibles para esta clase")
        elif mat_succion == "PVC":
            # Configuración específica para PVC
            tipos_union_pvc = ["Unión Sellado Elastomérico (Unión R)", "Unión Espiga Campana"]
            tipo_union_pvc_succion = st.selectbox(
                "Tipo de Unión",
                options=tipos_union_pvc,
                index=st.session_state.get('tipo_union_pvc_succion_index', 0),
                key="tipo_union_pvc_succion",
                help="Selecciona el tipo de unión para la tubería PVC."
            )
            # Guardar el índice actual
            if tipo_union_pvc_succion is not None:
                try:
                    st.session_state['tipo_union_pvc_succion_index'] = tipos_union_pvc.index(tipo_union_pvc_succion)
                except ValueError:
                    st.session_state['tipo_union_pvc_succion_index'] = 0
            
            # Mapear tipo de unión a clave del JSON
            if tipo_union_pvc_succion == "Unión Sellado Elastomérico (Unión R)":
                tipo_union_key = "union_elastomerica"
            else:
                tipo_union_key = "union_espiga_campana"
            
            # Series disponibles para el tipo de unión seleccionado
            series_pvc = get_pvc_series_disponibles(tipo_union_key)
            if series_pvc:
                # Mapear series a nombres legibles
                series_nombres = []
                for serie_key in series_pvc:
                    if serie_key == "s20":
                        series_nombres.append("Serie S 20.0 (Presión: 0.63 MPa)")
                    elif serie_key == "s16":
                        series_nombres.append("Serie S 16.0 (Presión: 0.80 MPa)")
                    elif serie_key == "s12_5":
                        series_nombres.append("Serie S 12.5 (Presión: 1.00 MPa)")
                    elif serie_key == "s10":
                        series_nombres.append("Serie S 10.0 (Presión: 1.25 MPa)")
                    elif serie_key == "s8":
                        series_nombres.append("Serie S 8.0 (Presión: 1.60 MPa)")
                    elif serie_key == "s6_3":
                        series_nombres.append("Serie S 6.3 (Presión: 2.00 MPa)")
                
                # Índice seguro para serie_pvc_succion_nombre_index
                safe_serie_pvc_suc_index = st.session_state.get('serie_pvc_succion_nombre_index', 0)
                if safe_serie_pvc_suc_index >= len(series_nombres):
                    safe_serie_pvc_suc_index = 0

                serie_pvc_succion_nombre = st.selectbox(
                    "Serie del Tubo",
                    options=series_nombres,
                    index=safe_serie_pvc_suc_index,
                    key="serie_pvc_succion_nombre",
                    help="Selecciona la serie del tubo PVC."
                )
                # Guardar el índice actual
                if serie_pvc_succion_nombre is not None:
                    try:
                        st.session_state['serie_pvc_succion_nombre_index'] = series_nombres.index(serie_pvc_succion_nombre)
                    except ValueError:
                        st.session_state['serie_pvc_succion_nombre_index'] = 0
                
                # Mapear nombre de serie a clave
                if serie_pvc_succion_nombre is not None:
                    try:
                        serie_pvc_succion_key = series_pvc[series_nombres.index(serie_pvc_succion_nombre)]
                    except ValueError:
                        serie_pvc_succion_key = series_pvc[0]  # Usar el primer valor disponible
                else:
                    serie_pvc_succion_key = series_pvc[0]  # Usar el primer valor disponible
                
                # Diámetros disponibles para la serie seleccionada
                diametros_pvc = get_pvc_diametros_disponibles(tipo_union_key, serie_pvc_succion_key)
                if diametros_pvc:
                    # Índice seguro para dn_pvc_succion_index
                    safe_dn_pvc_suc_index = st.session_state.get('dn_pvc_succion_index', 0)
                    if safe_dn_pvc_suc_index >= len(diametros_pvc):
                        safe_dn_pvc_suc_index = 0

                    dn_pvc_succion = st.selectbox(
                        "Diámetro Nominal (DN mm)",
                        options=diametros_pvc,
                        index=safe_dn_pvc_suc_index,
                        key="dn_pvc_succion",
                        help="Selecciona el diámetro nominal de la tubería PVC."
                    )
                    # Guardar el índice actual
                    if dn_pvc_succion is not None:
                        try:
                            st.session_state['dn_pvc_succion_index'] = diametros_pvc.index(dn_pvc_succion)
                        except ValueError:
                            st.session_state['dn_pvc_succion_index'] = 0
                    
                    # Obtener datos de la tubería
                    tuberia_pvc = get_pvc_data(tipo_union_key, serie_pvc_succion_key, dn_pvc_succion)
                    if tuberia_pvc:
                        # Calcular diámetro interno
                        st.session_state['espesor_succion'] = (tuberia_pvc['espesor_max_mm'] + tuberia_pvc['espesor_min_mm']) / 2
                        diametro_interno = calculate_diametro_interno_pvc(
                            tuberia_pvc["de_mm"], 
                            tuberia_pvc["espesor_min_mm"], 
                            tuberia_pvc["espesor_max_mm"]
                        )
                        st.session_state['diam_interno_succion'] = diametro_interno
                        if diametro_interno is not None:
                            st.session_state['diam_succion_mm'] = diametro_interno
                        
                        # Mostrar información calculada
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"**DE (mm):** {tuberia_pvc['de_mm']}")
                            st.info(f"**Espesor (mm):** {(tuberia_pvc['espesor_max_mm'] + tuberia_pvc['espesor_min_mm']) / 2:.1f}")
                        with col2:
                            st.info(f"**DI (mm):** {diametro_interno:.1f}")
                            st.info(f"**Presión (MPa):** {tuberia_pvc['presion_mpa']}")
                    else:
                        st.warning("No se encontraron datos para esta combinación")
                else:
                    st.warning("No hay diámetros disponibles para esta serie")
            else:
                st.warning("No hay series disponibles para este tipo de unión")
        else:
            # Para otros materiales, usar diámetro interno directamente
            st.number_input(
                "Diámetro Interno (mm)",
                value=st.session_state.get('diam_succion_mm', 200.0),
                min_value=1.0,
                step=0.01,
                key="diam_succion_mm",
                help="Diámetro interno de la tubería de succión en milímetros."
            )
        c_succion = HAZEN_WILLIAMS_C.get(mat_succion, None)
        if c_succion:
            st.markdown(f"<span style='color:#888888'><b>C (coeficiente Hazen-Williams) para {mat_succion}: {c_succion}</b></span>", unsafe_allow_html=True)
        
        st.number_input(
            "Otras Pérdidas en Succión (m)",
            value=st.session_state.get('otras_perdidas_succion', 0.0),
            key="otras_perdidas_succion",
            help="Pérdidas adicionales en la succión por accesorios, válvulas, etc."
        )
    
        # Mostrar accesorios de succión
        st.markdown("**Accesorios en Succión**")
        if st.session_state.get('accesorios_succion'):
            st.markdown("<div style='background-color:#f5f5f5;padding:4px;border-radius:4px;font-weight:bold;display:flex;'>"
                        "<div style='width:50%;'>Tipo</div>"
                        "<div style='width:25%;text-align:center;'>Cantidad</div>"
                        "<div style='width:25%;text-align:center;'>Le/D</div>"
                        "<div style='width:10%;text-align:center;'></div>"
                        "</div>", unsafe_allow_html=True)
            delete_succion = []
            for i, acc in enumerate(st.session_state['accesorios_succion']):
                lc_d_val = acc.get('lc_d', 'N/A')
                bg = '#ffffff' if i % 2 == 0 else '#eeeeee'
                cols = st.columns([2, 1, 1, 0.5])
                cols[0].markdown(f"<div style='background-color:{bg};padding:4px;border-radius:4px;'>{acc['tipo']}</div>", unsafe_allow_html=True)
                cols[1].markdown(f"<div style='background-color:{bg};padding:4px;border-radius:4px;text-align:center;'>{acc['cantidad']}</div>", unsafe_allow_html=True)
                cols[2].markdown(f"<div style='background-color:{bg};padding:4px;border-radius:4px;text-align:center;'>{lc_d_val}</div>", unsafe_allow_html=True)
                delete_succion.append(cols[3].checkbox("🗑️", key=f"del_s_chk_{i}", label_visibility="collapsed"))
            
            if st.button("Eliminar seleccionados de Succión"):
                for idx in reversed(range(len(delete_succion))):
                    if delete_succion[idx]:
                        st.session_state.accesorios_succion.pop(idx)
        else:
            st.info("No hay accesorios de succión seleccionados.")
    
    with col_imp:
        st.subheader("3. Tubería y Accesorios de Impulsión")
        
        # Indicador de sincronización automática
        from utils.sync_manager import render_sync_indicator
        render_sync_indicator('impulsion')

        st.number_input(
            "Longitud Tubería (m)",
            value=st.session_state.get('long_impulsion', 500.0),
            min_value=0.0,
            step=0.01,
            key="long_impulsion",
            help="Longitud total de la tubería de impulsión desde la bomba hasta el punto de entrega."
        )
        # Material de impulsión
        mat_impulsion_options = list(HAZEN_WILLIAMS_C.keys())
        current_mat_impulsion = st.session_state.get('mat_impulsion', mat_impulsion_options[0])
        # Validar que el material actual existe en las opciones
        if current_mat_impulsion not in mat_impulsion_options:
            current_mat_impulsion = mat_impulsion_options[0]
            st.session_state['mat_impulsion'] = current_mat_impulsion
        mat_impulsion_index = mat_impulsion_options.index(current_mat_impulsion)
        
        on_mat_impulsion_change = create_on_change_callback('impulsion')
        mat_impulsion = st.selectbox(
            "Material Tubería",
            options=mat_impulsion_options,
            index=mat_impulsion_index,
            key="mat_impulsion",
            help="Selecciona el material de la tubería de impulsión.",
            on_change=on_mat_impulsion_change
        )
        
        # Configuración específica para PEAD/HDPE
        if mat_impulsion in ["PEAD", "HDPE (Polietileno)"]:
            # Diámetro externo para PEAD
            diametros_pead = [item["diametro_nominal_mm"] for item in PEAD_DATA]
            
            # Validar que hay datos disponibles
            if not diametros_pead:
                st.error("No hay datos de tuberías PEAD disponibles. Verifique el archivo pead_data.json")
                return
            
            diam_externo_impulsion = st.selectbox(
                "Diámetro Externo (mm)",
                options=diametros_pead,
                index=st.session_state.get('diam_externo_impulsion_index', 0),
                key="diam_externo_impulsion",
                help="Selecciona el diámetro externo de la tubería PEAD."
            )
            
            # Guardar el índice actual solo si diam_externo_impulsion no es None
            if diam_externo_impulsion is not None:
                try:
                    st.session_state['diam_externo_impulsion_index'] = diametros_pead.index(diam_externo_impulsion)
                except ValueError:
                    # Si no se encuentra el valor, usar el índice por defecto
                    st.session_state['diam_externo_impulsion_index'] = 0
            
            # Obtener datos de la tubería PEAD seleccionada
            pead_data_impulsion = get_pead_data(diam_externo_impulsion)
            if pead_data_impulsion:
                # Series disponibles para este diámetro
                series_disponibles = []
                if pead_data_impulsion is not None:
                    for serie_key in ["s12_5", "s10", "s8", "s6_3", "s5", "s4"]:
                        if serie_key in pead_data_impulsion and pead_data_impulsion[serie_key]["espesor_mm"] is not None:
                            series_disponibles.append(serie_key)
                
                if series_disponibles:
                    # Índice seguro para serie_impulsion
                    safe_serie_impulsion_index = st.session_state.get('serie_impulsion_index', 0)
                    if safe_serie_impulsion_index >= len(series_disponibles):
                        safe_serie_impulsion_index = 0
                        
                    serie_impulsion = st.selectbox(
                        "Serie del Tubo",
                        options=series_disponibles,
                        index=safe_serie_impulsion_index,
                        key="serie_impulsion",
                        help="Selecciona la serie del tubo PEAD."
                    )
                    # Guardar el índice actual
                    if serie_impulsion is not None:
                        try:
                            st.session_state['serie_impulsion_index'] = series_disponibles.index(serie_impulsion)
                        except ValueError:
                            st.session_state['serie_impulsion_index'] = 0
                    
                    # Obtener espesor, presión y calcular diámetro interno
                    if serie_impulsion is not None and serie_impulsion in pead_data_impulsion:
                        espesor_impulsion = pead_data_impulsion[serie_impulsion]["espesor_mm"]
                        presion_impulsion = pead_data_impulsion[serie_impulsion]["presion_mpa"]
                        sdr_impulsion = pead_data_impulsion[serie_impulsion]["sdr"]
                        st.session_state['espesor_impulsion'] = espesor_impulsion
                        st.session_state['presion_nominal_impulsion'] = presion_impulsion
                        st.session_state['sdr_impulsion'] = sdr_impulsion
                    else:
                        espesor_impulsion = None
                        presion_impulsion = None
                        sdr_impulsion = None
                    diam_interno_impulsion = calculate_diametro_interno_pead(diam_externo_impulsion, espesor_impulsion)
                    st.session_state['diam_interno_impulsion'] = diam_interno_impulsion
                    
                    st.info(f"**Espesor de pared:** {espesor_impulsion} mm")
                    st.info(f"**SDR:** {sdr_impulsion}")
                    st.info(f"**Presión nominal de trabajo:** {presion_impulsion} MPa")
                    if diam_interno_impulsion is not None:
                        st.info(f"**Diámetro interno calculado:** {diam_interno_impulsion:.1f} mm")
                        # Guardar el diámetro interno calculado en session_state
                        st.session_state['diam_impulsion_mm'] = diam_interno_impulsion
                    else:
                        st.info("**Diámetro interno calculado:** No disponible")
                else:
                    st.warning("No hay series disponibles para este diámetro.")
            else:
                st.error("Error al cargar datos de tubería PEAD.")
        elif mat_impulsion == "Hierro Dúctil":
            # Configuración específica para Hierro Dúctil
            clases_hierro = ["C40", "C30", "C25", "C20"]
            clase_hierro_impulsion = st.selectbox(
                "Clase de Presión",
                options=clases_hierro,
                index=st.session_state.get('clase_hierro_impulsion_index', 0),
                key="clase_hierro_impulsion",
                help="Selecciona la clase de presión para la tubería de hierro dúctil."
            )
            # Guardar el índice actual
            if clase_hierro_impulsion is not None:
                try:
                    st.session_state['clase_hierro_impulsion_index'] = clases_hierro.index(clase_hierro_impulsion)
                except ValueError:
                    st.session_state['clase_hierro_impulsion_index'] = 0
            
            # Diámetros disponibles para la clase seleccionada
            if clase_hierro_impulsion is not None:
                diametros_hierro = get_hierro_ductil_diametros_disponibles(clase_hierro_impulsion.lower())
            else:
                diametros_hierro = []
            if diametros_hierro:
                # Índice seguro para dn_impulsion
                safe_dn_impulsion_index = st.session_state.get('dn_impulsion_index', 0)
                if safe_dn_impulsion_index >= len(diametros_hierro):
                    safe_dn_impulsion_index = 0
                    
                dn_impulsion = st.selectbox(
                    "Diámetro Nominal (DN mm)",
                    options=diametros_hierro,
                    index=safe_dn_impulsion_index,
                    key="dn_impulsion",
                    help="Selecciona el diámetro nominal de la tubería de hierro dúctil."
                )
                # Guardar el índice actual
                if dn_impulsion is not None:
                    try:
                        st.session_state['dn_impulsion_index'] = diametros_hierro.index(dn_impulsion)
                    except ValueError:
                        st.session_state['dn_impulsion_index'] = 0
                
                # Obtener datos de la tubería
                if clase_hierro_impulsion is not None:
                    tuberia_hierro = get_hierro_ductil_data(clase_hierro_impulsion.lower(), dn_impulsion)
                else:
                    tuberia_hierro = None
                if tuberia_hierro:
                    st.session_state['espesor_impulsion'] = tuberia_hierro["espesor_nominal_mm"]
                    diametro_interno = calculate_diametro_interno_hierro_ductil(
                        tuberia_hierro["de_mm"], 
                        tuberia_hierro["espesor_nominal_mm"]
                    )
                    st.session_state['diam_interno_impulsion'] = diametro_interno
                    if diametro_interno is not None:
                        st.session_state['diam_impulsion_mm'] = diametro_interno
                    
                    # Mostrar información calculada
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**DE (mm):** {tuberia_hierro['de_mm']}")
                        st.info(f"**Espesor Nominal (mm):** {tuberia_hierro['espesor_nominal_mm']}")
                    with col2:
                        st.info(f"**DI (mm):** {diametro_interno:.1f}")
                        st.info(f"**PFA (bar):** {tuberia_hierro['pfa_bar']}")
                        st.info(f"**PMA (bar):** {tuberia_hierro['pma_bar']}")
                else:
                    st.warning("No se encontraron datos para esta combinación de clase y diámetro")
            else:
                st.warning("No hay diámetros disponibles para esta clase")
        elif mat_impulsion == "Hierro Fundido":
            # Configuración específica para Hierro Fundido
            clases_hierro_fundido = ["Clase 150", "Clase 125", "Clase 100"]
            clase_hierro_fundido_impulsion = st.selectbox(
                "Clase de Presión",
                options=clases_hierro_fundido,
                index=st.session_state.get('clase_hierro_fundido_impulsion_index', 0),
                key="clase_hierro_fundido_impulsion",
                help="Selecciona la clase de presión para la tubería de hierro fundido."
            )
            # Guardar el índice actual
            if clase_hierro_fundido_impulsion is not None:
                try:
                    st.session_state['clase_hierro_fundido_impulsion_index'] = clases_hierro_fundido.index(clase_hierro_fundido_impulsion)
                except ValueError:
                    st.session_state['clase_hierro_fundido_impulsion_index'] = 0
            
            # Mapear clase a clave del JSON
            if clase_hierro_fundido_impulsion is not None:
                clase_key = clase_hierro_fundido_impulsion.lower().replace(" ", "_")
            else:
                clase_key = "c40"  # Valor por defecto
            
            # Diámetros disponibles para la clase seleccionada
            diametros_hierro_fundido = get_hierro_fundido_diametros_disponibles(clase_key)
            if diametros_hierro_fundido:
                # Índice seguro para dn_hierro_fundido_impulsion
                safe_dn_hf_impulsion_index = st.session_state.get('dn_hierro_fundido_impulsion_index', 0)
                if safe_dn_hf_impulsion_index >= len(diametros_hierro_fundido):
                    safe_dn_hf_impulsion_index = 0

                dn_hierro_fundido_impulsion = st.selectbox(
                    "Diámetro Nominal (DN mm)",
                    options=diametros_hierro_fundido,
                    index=safe_dn_hf_impulsion_index,
                    key="dn_hierro_fundido_impulsion",
                    help="Selecciona el diámetro nominal de la tubería de hierro fundido."
                )
                # Guardar el índice actual
                if dn_hierro_fundido_impulsion is not None:
                    try:
                        st.session_state['dn_hierro_fundido_impulsion_index'] = diametros_hierro_fundido.index(dn_hierro_fundido_impulsion)
                    except ValueError:
                        st.session_state['dn_hierro_fundido_impulsion_index'] = 0
                
                # Obtener datos de la tubería
                tuberia_hierro_fundido = get_hierro_fundido_data(clase_key, dn_hierro_fundido_impulsion)
                if tuberia_hierro_fundido:
                    st.session_state['espesor_impulsion'] = tuberia_hierro_fundido["espesor_mm"]
                    # Usar el DI directamente de la tabla
                    diametro_interno = tuberia_hierro_fundido["di_mm"]
                    st.session_state['diam_interno_impulsion'] = diametro_interno
                    if diametro_interno is not None:
                        st.session_state['diam_impulsion_mm'] = diametro_interno
                    
                    # Mostrar información calculada
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**DE (mm):** {tuberia_hierro_fundido['de_mm']}")
                        st.info(f"**Espesor (mm):** {tuberia_hierro_fundido['espesor_mm']}")
                    with col2:
                        st.info(f"**DI (mm):** {diametro_interno}")
                        st.info(f"**P. Trabajo (bar):** {tuberia_hierro_fundido['pfa_bar']}")
                        st.info(f"**P. Máxima (bar):** {tuberia_hierro_fundido['pma_bar']}")
                else:
                    st.warning("No se encontraron datos para esta combinación de clase y diámetro")
            else:
                st.warning("No hay diámetros disponibles para esta clase")
        elif mat_impulsion == "PVC":
            # Configuración específica para PVC
            tipos_union_pvc = ["Unión Sellado Elastomérico (Unión R)", "Unión Espiga Campana"]
            tipo_union_pvc_impulsion = st.selectbox(
                "Tipo de Unión",
                options=tipos_union_pvc,
                index=st.session_state.get('tipo_union_pvc_impulsion_index', 0),
                key="tipo_union_pvc_impulsion",
                help="Selecciona el tipo de unión para la tubería PVC."
            )
            # Guardar el índice actual
            if tipo_union_pvc_impulsion is not None:
                try:
                    st.session_state['tipo_union_pvc_impulsion_index'] = tipos_union_pvc.index(tipo_union_pvc_impulsion)
                except ValueError:
                    st.session_state['tipo_union_pvc_impulsion_index'] = 0
            
            # Mapear tipo de unión a clave del JSON
            if tipo_union_pvc_impulsion == "Unión Sellado Elastomérico (Unión R)":
                tipo_union_key = "union_elastomerica"
            else:
                tipo_union_key = "union_espiga_campana"
            
            # Series disponibles para el tipo de unión seleccionado
            series_pvc = get_pvc_series_disponibles(tipo_union_key)
            if series_pvc:
                # Mapear series a nombres legibles
                series_nombres = []
                for serie_key in series_pvc:
                    if serie_key == "s20":
                        series_nombres.append("Serie S 20.0 (Presión: 0.63 MPa)")
                    elif serie_key == "s16":
                        series_nombres.append("Serie S 16.0 (Presión: 0.80 MPa)")
                    elif serie_key == "s12_5":
                        series_nombres.append("Serie S 12.5 (Presión: 1.00 MPa)")
                    elif serie_key == "s10":
                        series_nombres.append("Serie S 10.0 (Presión: 1.25 MPa)")
                    elif serie_key == "s8":
                        series_nombres.append("Serie S 8.0 (Presión: 1.60 MPa)")
                    elif serie_key == "s6_3":
                        series_nombres.append("Serie S 6.3 (Presión: 2.00 MPa)")
                
                # Índice seguro para serie_pvc_impulsion_nombre
                safe_serie_pvc_imp_index = st.session_state.get('serie_pvc_impulsion_nombre_index', 0)
                if safe_serie_pvc_imp_index >= len(series_nombres):
                    safe_serie_pvc_imp_index = 0

                serie_pvc_impulsion_nombre = st.selectbox(
                    "Serie del Tubo",
                    options=series_nombres,
                    index=safe_serie_pvc_imp_index,
                    key="serie_pvc_impulsion_nombre",
                    help="Selecciona la serie del tubo PVC."
                )
                # Guardar el índice actual
                if serie_pvc_impulsion_nombre is not None:
                    try:
                        st.session_state['serie_pvc_impulsion_nombre_index'] = series_nombres.index(serie_pvc_impulsion_nombre)
                    except ValueError:
                        st.session_state['serie_pvc_impulsion_nombre_index'] = 0
                
                # Mapear nombre de serie a clave
                if serie_pvc_impulsion_nombre is not None:
                    try:
                        serie_pvc_impulsion_key = series_pvc[series_nombres.index(serie_pvc_impulsion_nombre)]
                    except ValueError:
                        serie_pvc_impulsion_key = series_pvc[0]  # Usar el primer valor disponible
                else:
                    serie_pvc_impulsion_key = series_pvc[0]  # Usar el primer valor disponible
                
                # Diámetros disponibles para la serie seleccionada
                diametros_pvc = get_pvc_diametros_disponibles(tipo_union_key, serie_pvc_impulsion_key)
                if diametros_pvc:
                    # Índice seguro para dn_pvc_impulsion
                    safe_dn_pvc_imp_index = st.session_state.get('dn_pvc_impulsion_index', 0)
                    if safe_dn_pvc_imp_index >= len(diametros_pvc):
                        safe_dn_pvc_imp_index = 0

                    dn_pvc_impulsion = st.selectbox(
                        "Diámetro Nominal (DN mm)",
                        options=diametros_pvc,
                        index=safe_dn_pvc_imp_index,
                        key="dn_pvc_impulsion",
                        help="Selecciona el diámetro nominal de la tubería PVC."
                    )
                    # Guardar el índice actual
                    if dn_pvc_impulsion is not None:
                        try:
                            st.session_state['dn_pvc_impulsion_index'] = diametros_pvc.index(dn_pvc_impulsion)
                        except ValueError:
                            st.session_state['dn_pvc_impulsion_index'] = 0
                    
                    # Obtener datos de la tubería
                    tuberia_pvc = get_pvc_data(tipo_union_key, serie_pvc_impulsion_key, dn_pvc_impulsion)
                    if tuberia_pvc:
                        # Calcular diámetro interno
                        st.session_state['espesor_impulsion'] = (tuberia_pvc['espesor_max_mm'] + tuberia_pvc['espesor_min_mm']) / 2
                        diametro_interno = calculate_diametro_interno_pvc(
                            tuberia_pvc["de_mm"], 
                            tuberia_pvc["espesor_min_mm"], 
                            tuberia_pvc["espesor_max_mm"]
                        )
                        st.session_state['diam_interno_impulsion'] = diametro_interno
                        if diametro_interno is not None:
                            st.session_state['diam_impulsion_mm'] = diametro_interno
                        
                        # Mostrar información calculada
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"**DE (mm):** {tuberia_pvc['de_mm']}")
                            st.info(f"**Espesor (mm):** {(tuberia_pvc['espesor_max_mm'] + tuberia_pvc['espesor_min_mm']) / 2:.1f}")
                        with col2:
                            st.info(f"**DI (mm):** {diametro_interno:.1f}")
                            st.info(f"**Presión (MPa):** {tuberia_pvc['presion_mpa']}")
                    else:
                        st.warning("No se encontraron datos para esta combinación")
                else:
                    st.warning("No hay diámetros disponibles para esta serie")
            else:
                st.warning("No hay series disponibles para este tipo de unión")
        else:
            # Para otros materiales, usar diámetro interno directamente
            st.number_input(
                "Diámetro Interno (mm)",
                value=st.session_state.get('diam_impulsion_mm', 150.0),
                min_value=1.0,
                step=0.01,
                key="diam_impulsion_mm",
                help="Diámetro interno de la tubería de impulsión en milímetros."
            )
        c_impulsion = HAZEN_WILLIAMS_C.get(mat_impulsion, None)
        if c_impulsion:
            st.markdown(f"<span style='color:#888888'><b>C (coeficiente Hazen-Williams) para {mat_impulsion}: {c_impulsion}</b></span>", unsafe_allow_html=True)
        
        st.number_input(
            "Otras Pérdidas en Impulsión (m)",
            value=st.session_state.get('otras_perdidas_impulsion', 0.0),
            key="otras_perdidas_impulsion",
            help="Pérdidas adicionales en la impulsión por accesorios, válvulas, etc."
        )
    
        # Mostrar accesorios de impulsión
        st.markdown("**Accesorios en Impulsión**")
        if st.session_state.get('accesorios_impulsion'):
            st.markdown("<div style='background-color:#f5f5f5;padding:4px;border-radius:4px;font-weight:bold;display:flex;'>"
                        "<div style='width:50%;'>Tipo</div>"
                        "<div style='width:25%;text-align:center;'>Cantidad</div>"
                        "<div style='width:25%;text-align:center;'>Le/D</div>"
                        "<div style='width:10%;text-align:center;'></div>"
                        "</div>", unsafe_allow_html=True)
            delete_impulsion = []
            for i, acc in enumerate(st.session_state['accesorios_impulsion']):
                lc_d_val = acc.get('lc_d', 'N/A')
                bg = '#ffffff' if i % 2 == 0 else '#eeeeee'
                cols = st.columns([2, 1, 1, 0.5])
                cols[0].markdown(f"<div style='background-color:{bg};padding:4px;border-radius:4px;'>{acc['tipo']}</div>", unsafe_allow_html=True)
                cols[1].markdown(f"<div style='background-color:{bg};padding:4px;border-radius:4px;text-align:center;'>{acc['cantidad']}</div>", unsafe_allow_html=True)
                cols[2].markdown(f"<div style='background-color:{bg};padding:4px;border-radius:4px;text-align:center;'>{lc_d_val}</div>", unsafe_allow_html=True)
                delete_impulsion.append(cols[3].checkbox("🗑️", key=f"del_i_chk_{i}", label_visibility="collapsed"))
            
            if st.button("Eliminar seleccionados de Impulsión"):
                for idx in reversed(range(len(delete_impulsion))):
                    if delete_impulsion[idx]:
                        st.session_state.accesorios_impulsion.pop(idx)
        else:
            st.info("No hay accesorios de impulsión seleccionados.")
    
    with col_empty:
        # Panel de Accesorios
        with st.expander("🔵 Seleccionar Accesorios para Succión", expanded=False):
            render_accessories_panel("Succión", "accesorios_succion")
        
        st.markdown("---")
        
        with st.expander("🔴 Seleccionar Accesorios para Impulsión", expanded=False):
            render_accessories_panel("Impulsión", "accesorios_impulsion")
    
    st.markdown("---")
    
    # Curvas de Bomba según modo seleccionado
    curva_mode = st.session_state.get('curva_mode_sidebar', 'Excel')
    
    if curva_mode == "Excel":
        st.subheader("4. Curvas de Bomba por Excel")
        st.markdown("Arrastra y suelta el archivo Excel con las curvas de la bomba.")
        uploaded_pump_file_tab1 = st.file_uploader(
            "Cargar archivo Excel con curvas (H-Q, Power, Efficiency, NPSH)",
            type=['xlsx'],
            key="uploaded_pump_file_tab1",
            help="Carga un archivo Excel con las curvas de la bomba."
        )
        
        if uploaded_pump_file_tab1 is None:
            st.info("Por favor, cargue un archivo Excel con las curvas de la bomba para comenzar el análisis.")
            st.warning(
                "El archivo Excel debe contener las siguientes hojas:\n"
                "- H-Q\n"
                "- Power\n"
                "- Efficiency\n"
                "- NPSH\n\n"
                "Cada hoja debe tener encabezados en la fila 1 y datos a partir de la fila 2:\n"
                "1. Caudal (Q) en m³/h\n"
                "2. Valor (Altura en m, Potencia en kW, Eficiencia en %, NPSH en m)"
            )
        else:
            # Procesar archivo Excel
            from data.excel_processor import load_excel_to_session_state
            
            # Verificar si ya se procesó este archivo
            file_id = f"{uploaded_pump_file_tab1.name}_{uploaded_pump_file_tab1.size}"
            if st.session_state.get('last_excel_file_id') != file_id:
                st.session_state['last_excel_file_id'] = file_id
                load_excel_to_session_state(uploaded_pump_file_tab1)
            else:
                st.success(f"✅ Archivo Excel ya procesado: {uploaded_pump_file_tab1.name}")
    else:
        st.subheader("4. Ajuste de Curvas Características (3 puntos)")
        st.markdown("Ingresa los puntos para cada curva en formato x y, separados por espacio, coma o punto y coma. Ejemplo: 10 20; 15,25; 20 30")
        
        # Mostrar información sobre sincronización con ADT
        if 'adt_caudales_personalizados' in st.session_state:
            caudales_adt = st.session_state.adt_caudales_personalizados
            st.info(f"🔄 **Sincronización Activa:** Los puntos de la Curva del Sistema se calculan automáticamente usando los caudales personalizados: {caudales_adt[0]:.1f}, {caudales_adt[1]:.1f}, {caudales_adt[2]:.1f} L/s")
        
        curva_names = [
            ("Curva del Sistema (H-Q)", "sistema"),
            ("Curva de la Bomba (H-Q)", "bomba"),
            ("Curva de Rendimiento (η-Q)", "rendimiento"),
            ("Curva de Potencia (PBHP-Q)", "potencia"),
            ("Curva de NPSH Requerido (NPSHR-Q)", "npsh")
        ]
        curva_cols = st.columns(5)
        for idx, (curva_label, curva_key) in enumerate(curva_names):
            with curva_cols[idx]:
                st.markdown(f"**{curva_label}**")
                
                # Para la Curva del Sistema (H-Q), mostrar valores de ADT calculados automáticamente
                if curva_key == "sistema":
                    try:
                        # Usar caudales personalizados de ADT si existen, sino usar valores por defecto
                        if 'adt_caudales_personalizados' in st.session_state:
                            flows = st.session_state.adt_caudales_personalizados
                        else:
                            flows = [0, st.session_state.get('caudal_lps', 51.0), 70]
                        
                        flow_unit = st.session_state.get('flow_unit', 'L/s')
                        
                        # Obtener parámetros del sistema unificados
                        system_params = get_current_system_params()
                        n_bombas = st.session_state.get('num_bombas', 1)
                        
                        # --- CÁLCULO DE PUNTOS DE LA CURVA DEL SISTEMA ---
                        # Usar caudales personalizados de ADT si existen (siempre en L/s internamente)
                        if 'adt_caudales_personalizados' in st.session_state:
                            flows_total = st.session_state.adt_caudales_personalizados
                        else:
                            flows_total = [0, st.session_state.get('caudal_lps', 51.0), st.session_state.get('caudal_lps', 51.0) * 1.3]
                        
                        # IMPORTANTE: Forzamos 'L/s' para el motor porque los puntos están en esa unidad.
                        resultados_adt = calculate_adt_for_multiple_flows(flows_total, 'L/s', system_params)
                        
                        if resultados_adt:
                            valores_adt = []
                            unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                            unidad_display = get_display_unit_label(unidad_caudal)
                            
                            for i, r in enumerate(resultados_adt):
                                # Caudal TOTAL en la unidad seleccionada
                                caudal_total_disp = flows_total[i]
                                if unidad_caudal == 'm³/h' and flow_unit == 'L/s':
                                    caudal_total_disp = flows_total[i] * 3.6
                                elif unidad_caudal == 'L/s' and flow_unit == 'm³/h':
                                    caudal_total_disp = flows_total[i] / 3.6
                                
                                # DIVIDIR POR N BOMBAS para el eje X de la curva del sistema
                                caudal_por_bomba = caudal_total_disp / n_bombas if n_bombas > 0 else caudal_total_disp
                                
                                valores_adt.append(f"{caudal_por_bomba:.2f} {r['adt_total']:.2f}")
                            
                            valores_texto = "\n".join(valores_adt)
                            
                            puntos_str = st.text_area(
                                f"Puntos x y para {curva_label}",
                                value=valores_texto,
                                key=f"textarea_{curva_key}",
                                help=f"Puntos calculados automáticamente (Caudal por Bomba ({unidad_display}) vs ADT Total (m)). Método: {system_params['metodo_calculo']}"
                            )
                            st.info(f"💡 **Curva compensada para {n_bombas} bombas** (Total / {n_bombas})")
                        else:
                            puntos_str = st.text_area(
                                f"Puntos x y para {curva_label}",
                                value="",
                                key=f"textarea_{curva_key}"
                            )
                    except Exception as e:
                        st.warning(f"Error calculando valores de ADT: {e}")
                        puntos_str = st.text_area(
                            f"Puntos x y para {curva_label}",
                            value="",
                            key=f"textarea_{curva_key}"
                        )
                else:
                    # Para curvas de la bomba, mostrar valores según la unidad seleccionada
                    unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                    unidad_display = get_display_unit_label(unidad_caudal)
                    
                    # Obtener valores actuales del textarea
                    current_value = st.session_state.get(f'textarea_{curva_key}', '')
                    
                    puntos_str = st.text_area(
                        f"Puntos x y para {curva_label}",
                        value=current_value,
                        key=f"textarea_{curva_key}",
                        help=f"Ingresa los puntos en formato x y, separados por espacio, coma o punto y coma. Caudal en {unidad_display}"
                    )
    
    # Exportar Datos a Excel y Bomba Seleccionada en 2 columnas
    st.markdown("---")
    
    col_export, col_bomba = st.columns([0.50, 0.50])
    
    with col_export:
        with st.expander("📊 Exportar Datos a Excel", expanded=False):
            col1, col2, col3, col4, col5 = st.columns([0.20, 0.20, 0.20, 0.20, 0.20])
            
            with col1:
                st.markdown("**Exportación de Curvas**")
                st.markdown("Exporta los datos de las curvas características a un archivo Excel con múltiples hojas.")
                
                if st.button("📅 Exportar Curvas a Excel", type="primary", key="export_curves_tab1"):
                    try:
                        # Procesar datos de curvas antes de exportar
                        curva_inputs = {}
                        unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                        
                        for curva_key in ['bomba', 'rendimiento', 'potencia', 'npsh']:
                            textarea_content = st.session_state.get(f'textarea_{curva_key}', '')
                            if textarea_content:
                                lines = textarea_content.strip().split('\n')
                                puntos = []
                                for line in lines:
                                    if line.strip():
                                        try:
                                            if ';' in line:
                                                parts = line.split(';')
                                            elif ',' in line:
                                                parts = line.split(',')
                                            else:
                                                parts = line.split()
                                            
                                            if len(parts) >= 2:
                                                x = float(parts[0].strip())
                                                y = float(parts[1].strip())
                                                
                                                # Convertir caudal a L/s para cálculos internos
                                                if unidad_caudal == 'm³/h':
                                                    x = x / 3.6  # m³/h a L/s
                                                
                                                puntos.append([x, y])
                                        except:
                                            continue
                                curva_inputs[curva_key] = puntos
                        
                        output = io.BytesIO()
                        
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            sheet_mapping = {
                                'bomba': 'H-Q',
                                'rendimiento': 'Efficiency', 
                                'potencia': 'Power',
                                'npsh': 'NPSH'
                            }
                            
                            for curva_key, sheet_name in sheet_mapping.items():
                                puntos_curva = curva_inputs.get(curva_key, [])
                                
                                if len(puntos_curva) >= 2:
                                    caudales_lps = np.array([pt[0] for pt in puntos_curva])
                                    caudales_m3h = caudales_lps * 3.6
                                    valores = np.array([pt[1] for pt in puntos_curva])
                                    
                                    # Obtener unidad de caudal para las columnas
                                    unidad_caudal = st.session_state.get('flow_unit', 'L/s')
                                    unidad_display = get_display_unit_label(unidad_caudal)
                                    
                                    if curva_key == 'bomba':
                                        df = pd.DataFrame({
                                            f'Caudal (Q) en {unidad_display}': caudales_m3h if unidad_caudal == 'm³/h' else caudales_lps,
                                            'Valor (Altura en m)': valores
                                        })
                                    elif curva_key == 'rendimiento':
                                        df = pd.DataFrame({
                                            f'Caudal (Q) en {unidad_display}': caudales_m3h if unidad_caudal == 'm³/h' else caudales_lps,
                                            'Valor (Eficiencia en %)': valores
                                        })
                                    elif curva_key == 'potencia':
                                        valores_kw = valores * 0.7457
                                        df = pd.DataFrame({
                                            f'Caudal (Q) en {unidad_display}': caudales_m3h if unidad_caudal == 'm³/h' else caudales_lps,
                                            'Valor (Potencia en kW)': valores_kw
                                        })
                                    elif curva_key == 'npsh':
                                        df = pd.DataFrame({
                                            f'Caudal (Q) en {unidad_display}': caudales_m3h if unidad_caudal == 'm³/h' else caudales_lps,
                                            'Valor (NPSH en m)': valores
                                        })
                                    
                                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                                else:
                                    df_empty = pd.DataFrame({'Mensaje': ['No hay datos disponibles']})
                                    df_empty.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        output.seek(0)
                        st.download_button(
                            label="📥 Descargar Archivo Excel",
                            data=output.getvalue(),
                            file_name="curvas_caracteristicas.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        st.success("✅ Archivo Excel generado exitosamente")
                        
                    except Exception as e:
                        st.error(f"Error al generar archivo Excel: {e}")
            
            with col2:
                st.markdown("**Exportación de Reporte Completo**")
                st.markdown("Exporta todos los inputs, resultados y datos de curvas a un único archivo Excel.")
                
                # Usar un botón normal que al ser presionado, prepara y ofrece la descarga
                if st.button("📊 Generar Reporte Completo en Excel", type="primary", key="export_reporte_tab1"):
                    try:
                        from data.export import create_comprehensive_excel_report
                        
                        # Generar el archivo Excel mejorado en memoria
                        excel_output = create_comprehensive_excel_report(st.session_state)
                        
                        # Guardar en session_state para que el botón de descarga aparezca
                        st.session_state.excel_report_data = excel_output.getvalue()
                        st.session_state.excel_report_generated = True
                        
                    except Exception as e:
                        st.error(f"Error al generar el reporte: {e}")
                        st.session_state.excel_report_generated = False

                # Mostrar el botón de descarga solo si el reporte ha sido generado
                if st.session_state.get('excel_report_generated', False):
                    st.download_button(
                        label="📥 Descargar Reporte Excel",
                        data=st.session_state.excel_report_data,
                        file_name="Reporte_Analisis_Bombeo.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    st.success("✅ ¡Reporte listo para descargar!")
            
            with col3:
                st.markdown("**Información Curvas**")
                st.info("""
                - H-Q: Altura vs caudal
                - Efficiency: Eficiencia
                - Power: Potencia
                - NPSH: NPSH requerido
                """)
            
            with col4:
                st.markdown("**Información Reporte**")
                st.info("""
                - Resumen: Parámetros
                - Succión: Cálculos
                - Impulsión: Cálculos
                """)
            
            with col5:
                st.markdown("**Estado**")
                if st.session_state.get('excel_report_generated', False):
                    st.success("✅ Reporte listo")
                else:
                    st.info("⏳ Sin generar")
    
    with col_bomba:
        with st.expander("🔧 Bomba Seleccionada", expanded=False):
            st.markdown("**Información de la bomba seleccionada para este proyecto:**")
            
            col1, col2, col3, col4, col5 = st.columns([0.20, 0.20, 0.20, 0.20, 0.20])
            
            with col1:
                bomba_url = st.text_input(
                    "URL de la bomba:",
                    value=st.session_state.get('bomba_url', ''),
                    placeholder="https://ejemplo.com/bomba",
                    help="Ingresa la URL del sitio web donde se encuentra la información de la bomba"
                )
                
                bomba_nombre = st.text_input(
                    "Nombre de la bomba:",
                    value=st.session_state.get('bomba_nombre', ''),
                    placeholder="Ej: Bomba Centrífuga ABC-123",
                    help="Nombre o modelo de la bomba seleccionada"
                )
                
                bomba_descripcion = st.text_area(
                    "Descripción:",
                    value=st.session_state.get('bomba_descripcion', ''),
                    placeholder="Descripción técnica de la bomba...",
                    help="Descripción técnica o características principales de la bomba"
                )
            
            with col2:
                st.markdown("**Acciones:**")
                
                # Guardar datos en session_state
                if st.button("💾 Guardar Información", type="primary"):
                    st.session_state['bomba_url'] = bomba_url
                    st.session_state['bomba_nombre'] = bomba_nombre
                    st.session_state['bomba_descripcion'] = bomba_descripcion
                    st.success("✅ Información de bomba guardada!")
                
                # Botón para abrir URL si existe
                if bomba_url and bomba_url.startswith(('http://', 'https://')):
                    st.markdown(f"""
                    <a href="{bomba_url}" target="_blank" style="text-decoration: none;">
                        <button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%;">
                            🌐 Abrir Sitio Web
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("**Estado:**")
                
                # Mostrar información guardada
                if bomba_nombre:
                    st.success(f"✅ {bomba_nombre[:30]}")
                
                if bomba_url:
                    st.info("🔗 URL guardada")
                
                if bomba_descripcion:
                    st.info(f"📝 {len(bomba_descripcion)} caracteres")
            
            # col4 y col5 vacías
    
    st.markdown("---")
    
    # --- Catálogo de Bombas Comerciales (Prediseño) ---
    expander_bomba_abierto = st.session_state.get('bombas_compatibles') is not None
    with st.expander("🏭 Catálogo de Bombas Comerciales (Prediseño)", expanded=expander_bomba_abierto):
        st.markdown("""
        **Herramienta de Prediseño**: Selecciona bombas comerciales (Grundfos, Ebara) basadas en tus 
        requerimientos de caudal y altura. Esta es una herramienta de prediseño inicial; 
        siempre valida la selección final con catálogos oficiales del fabricante.
        """)
        
        col_marca, col_criterios = st.columns([0.25, 0.75])
        
        with col_marca:
            # Selector de marca
            marca_bomba = st.selectbox(
                "Marca:",
                options=["Grundfos", "Ebara", "KSB", "Pedrollo"],
                index=0,
                key="marca_bomba_comercial",
                help="Selecciona el fabricante de bombas"
            )
            
            # Mostrar link a catálogo
            if marca_bomba == "Grundfos":
                url_catalogo = "https://product-selection.grundfos.com/"
            elif marca_bomba == "Ebara":
                url_catalogo = "https://www.pumpsebara.com/es"
            elif marca_bomba == "KSB":
                url_catalogo = "https://www.ksb.com/es-ec"
            else: # Pedrollo
                url_catalogo = "https://www.pedrollo.com/es"
            
            st.markdown(f"[📘 Ver Catálogo Online]({url_catalogo})")
            st.caption(f"Catálogo completo de {marca_bomba}")
        
        with col_criterios:
            col_q, col_h, col_margen = st.columns(3)
            
            # --- Sincronización Reactiva de Caudal y Altura ---
            # Obtener valores actuales del proyecto
            n_bombas = st.session_state.get('num_bombas', 1)
            q_total_proyecto = st.session_state.get('caudal_lps', 51.0)
            adt_total_proyecto = st.session_state.get('adt_total', 100.0)
            q_calculado_por_bomba = q_total_proyecto / n_bombas if n_bombas > 0 else q_total_proyecto
            
            # Detectar si el caudal total, el número de bombas o la ADT ha cambiado
            last_q_total = st.session_state.get('_last_catalog_q_total', 0.0)
            last_n_bombas = st.session_state.get('_last_catalog_n_bombas', 0)
            last_adt_total = st.session_state.get('_last_catalog_adt_total', 0.0)
            
            if q_total_proyecto != last_q_total or n_bombas != last_n_bombas or adt_total_proyecto != last_adt_total:
                # Actualizar los valores de los widgets en session_state
                st.session_state['caudal_diseno_bomba'] = q_calculado_por_bomba
                st.session_state['altura_diseno_bomba'] = adt_total_proyecto
                
                # Guardar estados actuales para próxima comparación
                st.session_state['_last_catalog_q_total'] = q_total_proyecto
                st.session_state['_last_catalog_n_bombas'] = n_bombas
                st.session_state['_last_catalog_adt_total'] = adt_total_proyecto
            
            with col_q:
                caudal_diseno = st.number_input(
                    "Caudal de Diseño POR BOMBA (L/s)",
                    value=st.session_state.get('caudal_diseno_bomba', q_calculado_por_bomba),
                    min_value=0.1,
                    step=0.1,
                    key="caudal_diseno_bomba",
                    help="Caudal de diseño de una sola bomba. Para sistemas en paralelo, busca una bomba que maneje su fracción del flujo total."
                )
                if n_bombas > 1:
                    st.info(f"💡 Buscando 1 de {n_bombas} bombas ({q_total_proyecto:.2f} L/s total)")
            
            with col_h:
                altura_diseno = st.number_input(
                    "Altura Total (m)",
                    value=st.session_state.get('altura_diseno_bomba', adt_total_proyecto),
                    min_value=1.0,
                    step=1.0,
                    key="altura_diseno_bomba",
                    help="Altura dinámica total del sistema"
                )
            
            with col_margen:
                margen = st.slider(
                    "Margen (%)",
                    min_value=10,
                    max_value=50,
                    value=20,
                    step=5,
                    key="margen_bomba",
                    help="Margen de tolerancia para el filtrado de bombas compatibles"
                )
        
        # Botón de búsqueda
        col_btn, col_info = st.columns([0.3, 0.7])
        
        with col_btn:
            buscar_clicked = st.button("🔍 Buscar Bombas", type="primary", use_container_width=True)
        
        with col_info:
            st.caption(f"Buscando bombas para: Q = {caudal_diseno:.1f} L/s, H = {altura_diseno:.1f} m (±{margen}%)")
        
        if buscar_clicked:
            try:
                # Cargar base de datos
                db = load_pump_database(marca_bomba)
                
                # Filtrar bombas
                bombas_compatibles = filter_pumps_by_requirements(
                    db, caudal_diseno, altura_diseno, margen
                )
                
                # Guardar en session state
                st.session_state['bombas_compatibles'] = bombas_compatibles
                st.session_state['marca_bomba_seleccionada'] = marca_bomba
                st.session_state['search_triggered'] = True
                
                if bombas_compatibles:
                    st.session_state['search_message'] = ("success", f"✅ Se encontraron {len(bombas_compatibles)} bombas compatibles de {marca_bomba}")
                else:
                    st.session_state['search_message'] = ("warning", "⚠️ No se encontraron bombas compatibles con estos criterios. Intenta ampliar el margen (%) o revisar los parámetros de caudal y altura.")
                
                st.rerun()
            except Exception as e:
                st.error(f"Error al buscar bombas: {e}")
        
        # Mostrar mensaje persistente si existe
        if st.session_state.get('search_message'):
            msg_type, msg_text = st.session_state['search_message']
            if msg_type == "success":
                st.success(msg_text)
            elif msg_type == "warning":
                st.warning(msg_text)
            elif msg_type == "error":
                st.error(msg_text)
        
        # Mostrar resultados si existen
        if st.session_state.get('bombas_compatibles'):
            bombas_list = st.session_state['bombas_compatibles']
            marca_actual = st.session_state.get('marca_bomba_seleccionada', 'Desconocida')
            
            st.markdown("---")
            st.markdown(f"### 📋 Bombas {marca_actual} Compatibles ({len(bombas_list)})")
            
            if len(bombas_list) == 0:
                st.info("No hay bombas compatibles. Intenta ampliar el margen o ajustar los parámetros.")
            else:
                for idx, bomba in enumerate(bombas_list):
                    with st.container():
                        # Encabezado con modelo y tipo
                        col_header, col_score = st.columns([0.8, 0.2])
                        
                        with col_header:
                            tipo_icono = "↕️" if "Vertical" in bomba.get('tipo_bomba', '') else "↔️"
                            st.markdown(f"**{tipo_icono} {bomba['modelo']}** - {bomba['serie']}")
                        
                        with col_score:
                            # Score de ajuste (menor es mejor)
                            score = bomba.get('_score', 0)
                            if score < 0.15:
                                badge = "🟢 Excelente"
                            elif score < 0.30:
                                badge = "🟡 Bueno"
                            else:
                                badge = "🟠 Aceptable"
                            st.caption(badge)
                        
                        # Información técnica en columnas
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Potencia", f"{bomba['potencia_hp']} HP", 
                                     f"{bomba['potencia_kw']} kW")
                        
                        with col2:
                            q_min, q_max = bomba['rango_caudal_optimo_lps']
                            st.metric("Q óptimo (L/s)", f"{q_min:.1f} - {q_max:.1f}")
                        
                        with col3:
                            if isinstance(bomba['rango_altura_optima_m'], list):
                                h_min, h_max = bomba['rango_altura_optima_m']
                                st.metric("H óptima (m)", f"{h_min:.0f} - {h_max:.0f}")
                            else:
                                h_opt = bomba['rango_altura_optima_m']
                                st.metric("H óptima (m)", f"≈ {h_opt:.0f}")
                        
                        with col4:
                            st.metric("Etapas / RPM", f"{bomba['etapas']} / {bomba['rpm']}")
                        
                        # Fila de detalles adicionales
                        with st.expander("📋 Ver especificaciones completas", expanded=False):
                            col_esp1, col_esp2 = st.columns(2)
                            
                            with col_esp1:
                                st.markdown(f"""
                                **Código:** {bomba['codigo']}  
                                **Tipo:** {bomba['tipo_bomba']}  
                                **Material:** {bomba['material_impulsor']}  
                                **Peso:** {bomba['peso_kg']} kg  
                                """)
                            
                            with col_esp2:
                                st.markdown(f"""
                                **Temp. máx:** {bomba['temperatura_max_c']}°C  
                                **Presión máx:** {bomba['presion_max_bar']} bar  
                                **Costo estimado:** ${bomba['costo_estimado_usd']:,.0f} USD  
                                **Categoría:** {bomba.get('_categoria', 'N/A')}  
                                """)
                        
                        # Botones de acción
                        col_btn1, col_btn2, col_btn3 = st.columns([0.3, 0.3, 0.4])
                        
                        with col_btn1:
                            st.button(
                                f"✅ Usar Curvas", 
                                key=f"usar_bomba_{idx}", 
                                use_container_width=True,
                                on_click=callback_seleccionar_bomba,
                                args=(bomba, marca_actual)
                            )
                        
                        with col_btn2:
                            # Link a ficha técnica
                            ficha_url = bomba.get('url_ficha_tecnica', '')
                            if ficha_url:
                                st.markdown(
                                    f'<a href="{ficha_url}" target="_blank">'
                                    f'<button style="width:100%; background-color:#4CAF50; color:white; '
                                    f'padding:8px; border:none; border-radius:4px; cursor:pointer;">'
                                    f'📄 Ficha Técnica</button></a>',
                                    unsafe_allow_html=True
                                )
                            else:
                                st.button("📄 Ficha Técnica", disabled=True, use_container_width=True)
                        
                        with col_btn3:
                            st.caption(f"Ajuste: {(1-score)*100:.1f}% compatible")
                        
                        st.markdown("---")
                
                # Botón para limpiar resultados
                if st.button("🗑️ Limpiar Resultados de Búsqueda"):
                    st.session_state.pop('bombas_compatibles', None)
                    st.session_state.pop('marca_bomba_seleccionada', None)
                    st.session_state.pop('search_message', None)
                    st.session_state.pop('search_triggered', None)
                    st.rerun()
    
    st.markdown("---")
    
    # --- Resultados de Cálculos Hidráulicos ---
    st.subheader("5. Resultados de Cálculos Hidráulicos")
    
    # Realizar cálculos básicos para mostrar resultados
    n_bombas = st.session_state.get('num_bombas', 1)
    q_total_lps = st.session_state.get('caudal_lps', 51.0)
    q_individual_lps = q_total_lps / n_bombas if n_bombas > 0 else q_total_lps
    caudal_m3s_design = convert_flow_unit(q_individual_lps, 'L/s', 'm³/s')
    diam_succion_m = st.session_state.get('diam_succion_mm', 200.0) / 1000.0
    diam_impulsion_m = st.session_state.get('diam_impulsion_mm', 150.0) / 1000.0
    
    # Cálculos de succión
    area_succion = math.pi * (diam_succion_m / 2)**2
    if caudal_m3s_design > 0 and area_succion > 0:
        vel_succion = caudal_m3s_design / area_succion
    else:
        vel_succion = 0.0
    st.session_state['velocidad_succion'] = vel_succion
    
    # --- UNIFICACIÓN DE MOTOR DE CÁLCULO ---
    # Preparar parámetros para el motor centralizado
    system_params = get_current_system_params()
    
    # Calcular ADT para el punto de diseño (Caudal TOTAL para pérdidas en tubería común)
    res_diseno = calculate_adt_for_multiple_flows([q_total_lps], 'L/s', system_params)[0]
    
    # Sincronizar estados desde el motor central
    st.session_state['hf_primaria_succion'] = res_diseno['hf_primaria_succion']
    st.session_state['hf_secundaria_succion'] = res_diseno['hf_secundaria_succion']
    st.session_state['perdida_total_succion'] = res_diseno['perdida_succion']
    
    st.session_state['hf_primaria_impulsion'] = res_diseno['hf_primaria_impulsion']
    st.session_state['hf_secundaria_impulsion'] = res_diseno['hf_secundaria_impulsion']
    st.session_state['perdida_total_impulsion'] = res_diseno['perdida_impulsion']
    
    st.session_state['altura_estatica_total'] = res_diseno['altura_estatica_total']
    st.session_state['perdidas_totales_sistema'] = res_diseno['perdida_succion'] + res_diseno['perdida_impulsion']
    st.session_state['adt_total'] = res_diseno['adt_total']

    # --- RECALCULAR LONGITUDES EQUIVALENTES PARA VISUALIZACIÓN ---
    le_total_succion = 0
    for acc in st.session_state.get('accesorios_succion', []):
        le_over_d = float(acc.get('lc_d', 10))
        le_total_succion += le_over_d * acc.get('cantidad', 1) * diam_succion_m
    st.session_state['le_total_succion'] = le_total_succion

    le_total_impulsion = 0
    for acc in st.session_state.get('accesorios_impulsion', []):
        le_over_d = float(acc.get('lc_d', 10))
        le_total_impulsion += le_over_d * acc.get('cantidad', 1) * diam_impulsion_m
    st.session_state['le_total_impulsion'] = le_total_impulsion

    # Recuperar valores para visualización
    hf_primaria_succion = st.session_state['hf_primaria_succion']
    hf_secundaria_succion = st.session_state['hf_secundaria_succion']
    perdida_total_succion = st.session_state['perdida_total_succion']
    
    hf_primaria_impulsion = st.session_state['hf_primaria_impulsion']
    hf_secundaria_impulsion = st.session_state['hf_secundaria_impulsion']
    perdida_total_impulsion = st.session_state['perdida_total_impulsion']
    
    # Velocidad de impulsión (no calculada por calculate_adt_for_multiple_flows, se mantiene)
    area_impulsion = math.pi * (diam_impulsion_m / 2)**2
    if caudal_m3s_design > 0 and area_impulsion > 0:
        vel_impulsion = caudal_m3s_design / area_impulsion
    else:
        vel_impulsion = 0.0
    st.session_state['velocidad_impulsion'] = vel_impulsion

    # Alturas dinámicas de succión e impulsión (se recalculan para visualización)
    altura_dinamica_succion = st.session_state.get('altura_succion_input', 1.65) + perdida_total_succion
    st.session_state['altura_dinamica_succion'] = altura_dinamica_succion
    
    altura_dinamica_impulsion = st.session_state.get('altura_descarga', 80.0) + perdida_total_impulsion
    st.session_state['altura_dinamica_impulsion'] = altura_dinamica_impulsion
    
    # --- NPSH DISPONIBLE ---
    # Presión de vapor y barométrica (ya calculadas o recuperar)
    temperatura_c = st.session_state.get('temp_liquido', 20.0)
    presion_barometrica = st.session_state.get('presion_barometrica_calculada', 0)
    presion_vapor = calcular_presion_vapor_mca(temperatura_c) # Recalcular para asegurar frescura
    st.session_state['presion_vapor_calculada'] = presion_vapor
    
    # Obtener parámetros
    altura_succion = st.session_state.get('altura_succion_input', 2.0)  # Distancia desde nivel agua hasta eje
    bomba_inundada = st.session_state.get('bomba_inundada', False)
    
    # Calcular altura neta (hn)
    # altura_succion = distancia desde superficie libre del agua hasta eje de bomba
    if bomba_inundada:
        # Nivel agua ARRIBA del eje (positivo)
        altura_neta = +altura_succion
    else:
        # Nivel agua DEBAJO del eje (negativo)
        altura_neta = -altura_succion
    
    # Fórmula unificada de NPSH
    # NPSHd = Pa + hn - hf_suc - Pv
    npshd_mca = presion_barometrica + altura_neta - perdida_total_succion - presion_vapor
    st.session_state['npshd_mca'] = npshd_mca
    st.session_state['altura_neta_succion'] = altura_neta
    
    # Calcular margen de NPSH si hay NPSH requerido disponible
    npsh_requerido = st.session_state.get('npsh_requerido', 0.0)
    if npsh_requerido > 0:
        margen_npsh = npshd_mca - npsh_requerido
        st.session_state['npsh_margen'] = margen_npsh
    else:
        st.session_state['npsh_margen'] = 0.0
    
    # Altura dinámica total
    # Altura Estática Total (geodésica)
    # H_est = Z_descarga - Z_nivel_agua
    altura_succion_val = st.session_state.get('altura_succion_input', 2.0)
    bomba_inundada_val = st.session_state.get('bomba_inundada', False)
    if bomba_inundada_val:
        z_nivel_agua = +altura_succion_val
    else:
        z_nivel_agua = -altura_succion_val
    z_descarga = st.session_state.get('altura_descarga', 80.0)
    altura_estatica_total = z_descarga - z_nivel_agua
    st.session_state['altura_estatica_total'] = altura_estatica_total

    perdidas_totales_sistema = perdida_total_succion + perdida_total_impulsion
    st.session_state['perdidas_totales_sistema'] = perdidas_totales_sistema

    # ADT = H_estática + Σhf
    adt_total = altura_estatica_total + perdidas_totales_sistema
    st.session_state['adt_total'] = adt_total
    
    col1, col2, col3, col4, col5 = st.columns([0.20, 0.20, 0.20, 0.20, 0.20])
    
    with col1:
        st.markdown("#### Resultados de Succión")
        st.metric("Velocidad en Succión", f"{vel_succion:.2f} m/s")
        if 0.6 <= vel_succion <= 0.9:
            st.success("✅ Velocidad óptima (0.6-0.9 m/s)")
        elif vel_succion < 0.6:
            st.warning("⚠️ Velocidad baja. **Disminuya el diámetro** en succión")
        else:  # vel_succion > 0.9
            st.error("❌ Velocidad excesiva. **Aumente el diámetro** en succión")
        
        st.metric("Pérdida Primaria", f"{hf_primaria_succion:.2f} m")
        st.metric("Pérdida Secundaria", f"{hf_secundaria_succion:.2f} m")
        st.metric("Long. Equiv. Accesorios", f"{le_total_succion:.2f} m")
        st.markdown(f"""
        <div style='background-color: #e8f4fd; padding: 10px; border-radius: 8px; border-left: 4px solid #1f77b4; margin: 10px 0;'>
            <h4 style='margin: 0; color: #1f77b4;'>Pérdida Total en Succión: {perdida_total_succion:.2f} m</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background-color: #e8f4fd; padding: 10px; border-radius: 8px; border-left: 4px solid #1f77b4; margin: 10px 0;'>
            <h4 style='margin: 0; color: #1f77b4;'>Altura Dinámica de Succión: {altura_dinamica_succion:.2f} m</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Resultados de Impulsión")
        st.metric("Velocidad en Impulsión", f"{vel_impulsion:.2f} m/s")
        if 1.0 <= vel_impulsion <= 2.5:
            st.success("✅ Velocidad óptima (1.0-2.5 m/s)")
        elif vel_impulsion < 1.0:
            st.warning("⚠️ Velocidad baja. **Disminuya el diámetro** en impulsión")
        else:  # vel_impulsion > 2.5
            st.error("❌ Velocidad excesiva. **Aumente el diámetro** en impulsión")
        
        st.metric("Pérdida Primaria", f"{hf_primaria_impulsion:.2f} m")
        st.metric("Pérdida Secundaria", f"{hf_secundaria_impulsion:.2f} m")
        st.metric("Long. Equiv. Accesorios", f"{le_total_impulsion:.2f} m")
        st.markdown(f"""
        <div style='background-color: #d1ecf1; padding: 10px; border-radius: 8px; border-left: 4px solid #0c5460; margin: 10px 0;'>
            <h4 style='margin: 0; color: #0c5460;'>Pérdida Total en Impulsión: {perdida_total_impulsion:.2f} m</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Cálculo de Altura Dinámica de Impulsión
        altura_dinamica_impulsion = st.session_state.get('altura_descarga', 80.0) + perdida_total_impulsion
        st.markdown(f"""
        <div style='background-color: #d1ecf1; padding: 10px; border-radius: 8px; border-left: 4px solid #0c5460; margin: 10px 0;'>
            <h4 style='margin: 0; color: #0c5460;'>Altura Dinámica de Impulsión: {altura_dinamica_impulsion:.2f} m</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("#### Cálculo de NPSH Disponible")
        
        # Leer los valores actuales del estado de la sesión
        bomba_inundada_actual = st.session_state.get('bomba_inundada', False)
        altura_succion_actual = st.session_state.get('altura_succion_input', 1.65)
        nivel_agua_actual = st.session_state.get('nivel_agua_tanque', 1.59)
        altura_neta_actual = st.session_state.get('altura_neta_succion', 0)
        npshd_mca_actual = st.session_state.get('npshd_mca', 0)
        
        # Indicador del estado de la bomba con geometría
        if bomba_inundada_actual:
            elev_tanque_display = altura_succion_actual
            nivel_agua_display = elev_tanque_display + nivel_agua_actual
            st.info(f"🔵 **Estado:** Bomba inundada (debajo del fondo del tanque)")
            st.markdown(f"📐 **Geometría:** Fondo tanque a +{elev_tanque_display:.2f}m, Nivel agua a +{nivel_agua_display:.2f}m")
        else:
            elev_tanque_display = -altura_succion_actual
            nivel_agua_display = elev_tanque_display + nivel_agua_actual
            if altura_neta_actual >= 0:
                st.info(f"🔵 **Estado:** Bomba sobre el fondo del tanque (agua ARRIBA del eje)")
            else:
                st.warning(f"⚠️ **Estado:** Bomba en aspiración (agua DEBAJO del eje)")
            st.markdown(f"📐 **Geometría:** Fondo tanque a {elev_tanque_display:.2f}m, Nivel agua a {nivel_agua_display:.2f}m")
        
        st.markdown("**Parámetros del cálculo (todos en m.c.a.):**")
        st.markdown(f"- **Presión Barométrica (Pa):** {presion_barometrica:.2f} m.c.a. (Elevación: {st.session_state.get('elevacion_sitio', 450.0):.0f} m)")
        st.markdown(f"- **Altura Neta (hn):** {altura_neta_actual:.2f} m.c.a. (nivel agua - eje bomba)")
        st.markdown(f"- **Pérdida en la Succión (hg):** {perdida_total_succion:.2f} m.c.a.")
        st.markdown(f"- **Presión de Vapor (Pv):** {presion_vapor:.2f} m.c.a. (Temp: {temperatura_c:.1f}°C)")
        
        # Mostrar fórmula unificada
        st.markdown("**Fórmula (Unificada):**")
        st.markdown("NPSHd = Pa + hn - hg - Pv")
        st.markdown(f"**Cálculo:** {presion_barometrica:.2f} + ({altura_neta_actual:.2f}) - {perdida_total_succion:.2f} - {presion_vapor:.2f} = {npshd_mca_actual:.2f} m.c.a.")
        
        st.markdown(f"""
        <div style='background-color: #d4edda; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; margin: 10px 0; text-align: center;'>
            <h2 style='margin: 0; color: #155724; font-size: 1.8rem; font-weight: bold;'>NPSH Disponible: {npshd_mca_actual:.2f} m.c.a.</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("#### Cálculo del Motor de la Bomba")
        
        # Obtener datos del punto de operación
        caudal_diseno = st.session_state.get('caudal_lps', 51.0)
        altura_total = adt_total
        
        # Cálculo de potencia hidráulica
        densidad_agua = 1000  # kg/m³
        gravedad = 9.81  # m/s²
        caudal_m3s = caudal_diseno / 1000  # Convertir L/s a m³/s
        
        # Obtener número de bombas en paralelo
        n_bombas = st.session_state.get('num_bombas', 1)
        
        # Calcular potencia hidráulica por bomba individual
        potencia_hidraulica_individual_kw = (densidad_agua * gravedad * caudal_m3s * altura_total) / 1000
        st.session_state['potencia_hidraulica_kw'] = potencia_hidraulica_individual_kw
        
        potencia_hidraulica_individual_hp = potencia_hidraulica_individual_kw / 0.7457
        st.session_state['potencia_hidraulica_hp'] = potencia_hidraulica_individual_hp
        
        eficiencia_bomba = 0.75  # 75% eficiencia típica
        
        # Calcular potencia del motor por bomba
        potencia_motor_individual_kw = potencia_hidraulica_individual_kw / eficiencia_bomba
        potencia_motor_individual_hp = potencia_motor_individual_kw / 0.7457
        
        # Guardar en session_state (es por bomba)
        st.session_state['potencia_motor_kw'] = potencia_motor_individual_kw
        st.session_state['potencia_motor_hp'] = potencia_motor_individual_hp
        
        factor_seguridad = 1.20
        
        # Aplicar factor de seguridad a cada bomba individual
        potencia_motor_final_kw = potencia_motor_individual_kw * factor_seguridad
        st.session_state['potencia_motor_final_kw'] = potencia_motor_final_kw
        
        potencia_motor_final_hp = potencia_motor_individual_hp * factor_seguridad
        st.session_state['potencia_motor_final_hp'] = potencia_motor_final_hp
        
        # Potencia total del sistema (todas las bombas)
        potencia_hidraulica_total_kw = potencia_hidraulica_individual_kw * n_bombas
        potencia_hidraulica_total_hp = potencia_hidraulica_individual_hp * n_bombas
        
        potencia_total_sistema_kw = potencia_motor_final_kw * n_bombas
        potencia_total_sistema_hp = potencia_motor_final_hp * n_bombas
        
        from core.calculations import seleccionar_motor_estandar
        motor_seleccionado = seleccionar_motor_estandar(potencia_motor_final_hp)
        st.session_state['motor_seleccionado'] = motor_seleccionado
        
        # Mostrar banner si hay bombas en paralelo
        if n_bombas > 1:
            st.info(f"🔄 **Sistema con {n_bombas} bombas en paralelo**")
        
        st.markdown("**Parámetros del cálculo:**")
        st.markdown(f"- **Caudal Total:** {q_total_lps:.2f} L/s")
        if n_bombas > 1:
            st.markdown(f"- **Caudal por Bomba:** {q_individual_lps:.2f} L/s")
        st.markdown(f"- **Número de bombas:** {n_bombas}")
        st.markdown(f"- **Altura total (ADT):** {altura_total:.2f} m")
        st.markdown(f"- **Densidad del agua:** {densidad_agua} kg/m³")
        st.markdown(f"- **Gravedad:** {gravedad} m/s²")
        st.markdown(f"- **Eficiencia de la bomba:** {eficiencia_bomba*100:.0f}%")
        st.markdown(f"- **Factor de seguridad:** {factor_seguridad}")
        
        st.markdown("**Fórmula de potencia hidráulica:**")
        st.markdown("P_h = (ρ × g × Q × H) / 1000")
        st.markdown(f"**Cálculo:** ({densidad_agua} × {gravedad} × {caudal_m3s:.3f} × {altura_total:.2f}) / 1000 = {potencia_hidraulica_total_kw:.2f} kW")
        
        st.markdown("**Potencia del motor:**")
        if n_bombas > 1:
            st.markdown(f"P_motor_total = P_h / η_bomba × F.S. = {potencia_total_sistema_kw:.2f} kW")
            st.markdown(f"P_motor_individual = P_motor_total / {n_bombas} = {potencia_motor_final_kw:.2f} kW por bomba")
        else:
            st.markdown("P_motor = P_h / η_bomba × F.S.")
            st.markdown(f"**Cálculo:** {potencia_hidraulica_total_kw:.2f} / {eficiencia_bomba} × {factor_seguridad} = {potencia_motor_final_kw:.2f} kW")
        
        st.markdown(f"""
        <div style='background-color: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 10px 0; text-align: center;'>
            <h3 style='margin: 0; color: #856404; font-size: 1.4rem; font-weight: bold;'>Potencia Hidráulica Total: {potencia_hidraulica_total_kw:.2f} kW ({potencia_hidraulica_total_hp:.2f} HP)</h3>
            <p style='margin: 5px 0; color: #856404;'>({n_bombas} bombas × {potencia_hidraulica_individual_hp:.2f} HP/bomba)</p>
        </div>
        """, unsafe_allow_html=True)
        
        if n_bombas > 1:
            st.markdown(f"""
            <div style='background-color: #d1ecf1; padding: 15px; border-radius: 8px; border-left: 4px solid #0c5460; margin: 10px 0; text-align: center;'>
                <h2 style='margin: 0; color: #0c5460; font-size: 1.6rem; font-weight: bold;'>Potencia por Bomba: {potencia_motor_final_kw:.2f} kW ({potencia_motor_final_hp:.2f} HP)</h2>
                <p style='margin: 5px 0; color: #0c5460;'><strong>Potencia Total del Sistema: {potencia_total_sistema_kw:.2f} kW ({potencia_total_sistema_hp:.2f} HP)</strong></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='background-color: #d1ecf1; padding: 15px; border-radius: 8px; border-left: 4px solid #0c5460; margin: 10px 0; text-align: center;'>
                <h2 style='margin: 0; color: #0c5460; font-size: 1.6rem; font-weight: bold;'>Potencia del Motor: {potencia_motor_final_kw:.2f} kW ({potencia_motor_final_hp:.2f} HP)</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Motor Estándar Seleccionado
        st.markdown("---")
        st.markdown("#### 🔧 Motor Estándar Seleccionado")
        
        # Mostrar motor seleccionado automáticamente
        if motor_seleccionado:
            if n_bombas > 1:
                costo_total = motor_seleccionado['costo_estimado_usd'] * n_bombas
                peso_total = motor_seleccionado['peso_kg'] * n_bombas
                st.markdown(f"""
                <div style='background-color: #d4edda; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; margin: 10px 0;'>
                    <h3 style='margin: 0; color: #155724; font-size: 1.4rem; font-weight: bold;'>
                        Motor por Bomba: {motor_seleccionado['potencia_hp']:.2f} HP ({motor_seleccionado['potencia_kw']:.2f} kW)
                    </h3>
                    <p style='margin: 5px 0; color: #155724; font-size: 1.1rem;'>
                        <strong>⚡ Cantidad de Motores: {n_bombas} unidades</strong>
                    </p>
                    <p style='margin: 5px 0; color: #155724;'>
                        <strong>Eficiencia:</strong> {motor_seleccionado['eficiencia_porcentaje']}% | 
                        <strong>Factor de Potencia:</strong> {motor_seleccionado['factor_potencia']} | 
                        <strong>RPM:</strong> {motor_seleccionado['rpm_estandar']}
                    </p>
                    <p style='margin: 5px 0; color: #155724;'>
                        <strong>Corriente Nominal:</strong> {motor_seleccionado['corriente_nominal_a']} A | 
                        <strong>Tensión:</strong> {motor_seleccionado['tension_nominal_v']} V | 
                        <strong>Fases:</strong> {motor_seleccionado['fases']}
                    </p>
                    <p style='margin: 5px 0; color: #155724;'>
                        <strong>Aplicación:</strong> {motor_seleccionado['aplicacion']}
                    </p>
                    <p style='margin: 5px 0; color: #155724;'>
                        <strong>Costo por Motor:</strong> ${motor_seleccionado['costo_estimado_usd']} USD | 
                        <strong>Costo Total:</strong> ${costo_total:.2f} USD
                    </p>
                    <p style='margin: 5px 0; color: #155724;'>
                        <strong>Peso por Motor:</strong> {motor_seleccionado['peso_kg']} kg | 
                        <strong>Peso Total:</strong> {peso_total:.2f} kg
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background-color: #d4edda; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; margin: 10px 0;'>
                    <h3 style='margin: 0; color: #155724; font-size: 1.4rem; font-weight: bold;'>
                        Motor: {motor_seleccionado['potencia_hp']:.2f} HP ({motor_seleccionado['potencia_kw']:.2f} kW)
                    </h3>
                    <p style='margin: 5px 0; color: #155724;'>
                        <strong>Eficiencia:</strong> {motor_seleccionado['eficiencia_porcentaje']}% | 
                        <strong>Factor de Potencia:</strong> {motor_seleccionado['factor_potencia']} | 
                        <strong>RPM:</strong> {motor_seleccionado['rpm_estandar']}
                    </p>
                    <p style='margin: 5px 0; color: #155724;'>
                        <strong>Corriente Nominal:</strong> {motor_seleccionado['corriente_nominal_a']} A | 
                        <strong>Tensión:</strong> {motor_seleccionado['tension_nominal_v']} V | 
                        <strong>Fases:</strong> {motor_seleccionado['fases']}
                    </p>
                    <p style='margin: 5px 0; color: #155724;'>
                        <strong>Aplicación:</strong> {motor_seleccionado['aplicacion']}
                    </p>
                    <p style='margin: 5px 0; color: #155724;'>
                        <strong>Costo Estimado:</strong> ${motor_seleccionado['costo_estimado_usd']} USD | 
                        <strong>Peso:</strong> {motor_seleccionado['peso_kg']} kg
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No se pudo seleccionar un motor estándar para la potencia calculada.")
    
    with col5:
        st.markdown("### 📊 Resumen del Sistema")
        st.metric("Altura Estática Total", f"{altura_estatica_total:.2f} m", help="Altura de Succión + Altura de Descarga")
        st.metric("Pérdidas Totales", f"{perdida_total_succion + perdida_total_impulsion:.2f} m", help="Suma de todas las pérdidas")
        st.markdown(f"""
        <div style='background-color: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 10px 0; text-align: center;'>
            <h2 style='margin: 0; color: #856404; font-size: 1.8rem; font-weight: bold;'>🎯 Altura Dinámica Total (ADT): {adt_total:.2f} m</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # --- EXPLICACIÓN TÉCNICA DETALLADA ---
        with st.expander("📚 Explicación Técnica de Cálculos Hidráulicos", expanded=False):
            st.markdown("### Memoria de Cálculo Hidráulico")
            
            # 1. Altura Estática
            st.markdown("#### 1. Altura Estática Total ($H_e$)")
            if system_params['bomba_inundada']:
                st.latex(r"H_e = Z_{descarga} - Z_{succión} = " + f"{system_params['altura_descarga']:.2f} - {system_params['altura_succion']:.2f} = {altura_estatica_total:.2f} \\text{{ m}}")
            else:
                st.latex(r"H_e = Z_{descarga} - (-Z_{succión}) = " + f"{system_params['altura_descarga']:.2f} - (-{system_params['altura_succion']:.2f}) = {altura_estatica_total:.2f} \\text{{ m}}")
            
            # 2. Pérdidas por Fricción
            st.markdown(f"#### 2. Pérdidas por Fricción - Método: {system_params['metodo_calculo']}")
            if system_params['metodo_calculo'] == 'Hazen-Williams':
                st.markdown("**Ecuación de Hazen-Williams:**")
                st.latex(r"h_f = 10.67 \cdot L_{total} \cdot \left( \frac{Q}{C} \right)^{1.852} \cdot D^{-4.87}")
                st.markdown(f"*C_succión: {system_params['C_succion']}, C_impulsión: {system_params['C_impulsion']}*")
            else:
                st.markdown("**Ecuación de Darcy-Weisbach:**")
                st.latex(r"h_f = f \cdot \frac{L_{total}}{D} \cdot \frac{v^2}{2g}")
                st.markdown(f"*Cálculo teórico basado en el número de Reynolds y la rugosidad absoluta del material.*")
            
            # 3. Pérdidas Secundarias (Accesorios)
            st.markdown("#### 3. Pérdidas en Accesorios (Secundarias)")
            st.markdown("Se utiliza el método de la **Longitud Equivalente ($L_e$)**:")
            st.latex(r"L_{total} = L_{tubería} + \sum \left( \frac{L_e}{D} \cdot D_{interno} \right)")
            
            # 4. ADT Final
            st.markdown("#### 4. Altura Dinámica Total ($ADT$)")
            st.latex(r"ADT = H_e + \sum h_{f,succión} + \sum h_{f,impulsión}")
            st.latex(f"ADT = {altura_estatica_total:.2f} + {perdida_total_succion:.2f} + {perdida_total_impulsion:.2f} = {adt_total:.2f} \\text{{ m}}")
            
            st.info("💡 **Nota:** Todos los cálculos se realizan utilizando el caudal total del sistema para determinar las pérdidas en las tuberías comunes.")
        
        # Tabla de ADT para múltiples caudales
        st.markdown("### 📈 ADT para Diferentes Caudales")
        
        # Inicializar caudales personalizados en session_state si no existen
        if 'adt_caudales_personalizados' not in st.session_state:
            st.session_state.adt_caudales_personalizados = [0, st.session_state.get('caudal_lps', 51.0), 70]
        
        # Permitir al usuario personalizar los caudales
        with st.expander("⚙️ Personalizar Caudales para ADT", expanded=False):
            st.markdown("**Ingrese los 3 caudales para calcular ADT:**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                caudal_1 = st.number_input(
                    "Caudal 1 (L/s)", 
                    min_value=0.0, 
                    max_value=1000.0, 
                    value=float(st.session_state.adt_caudales_personalizados[0]),
                    step=0.1,
                    key="adt_caudal_1"
                )
            
            with col2:
                caudal_2 = st.number_input(
                    "Caudal 2 (L/s)", 
                    min_value=0.0, 
                    max_value=1000.0, 
                    value=float(st.session_state.adt_caudales_personalizados[1]),
                    step=0.1,
                    key="adt_caudal_2"
                )
            
            with col3:
                caudal_3 = st.number_input(
                    "Caudal 3 (L/s)", 
                    min_value=0.0, 
                    max_value=1000.0, 
                    value=float(st.session_state.adt_caudales_personalizados[2]),
                    step=0.1,
                    key="adt_caudal_3"
                )
            
            # Botón para actualizar caudales
            if st.button("🔄 Actualizar Tabla ADT", type="primary"):
                st.session_state.adt_caudales_personalizados = [caudal_1, caudal_2, caudal_3]
                # Limpiar el text-area del sistema para forzar recálculo
                if 'textarea_sistema' in st.session_state:
                    del st.session_state['textarea_sistema']
                st.success("✅ Caudales actualizados! Los puntos de la Curva del Sistema se sincronizarán automáticamente.")
                st.rerun()
            
            # Botón para resetear a valores por defecto
            if st.button("🔄 Resetear a Valores por Defecto"):
                caudal_diseno = st.session_state.get('caudal_lps', 51.0)
                st.session_state.adt_caudales_personalizados = [0, caudal_diseno, 70]
                # Limpiar el text-area del sistema para forzar recálculo
                if 'textarea_sistema' in st.session_state:
                    del st.session_state['textarea_sistema']
                st.success("✅ Valores reseteados! Los puntos de la Curva del Sistema se sincronizarán automáticamente.")
                st.rerun()
        
        try:
            # Usar caudales personalizados
            flows = st.session_state.adt_caudales_personalizados
            flow_unit = st.session_state.get('flow_unit', 'L/s')
            
            # Obtener parámetros del sistema unificados
            system_params = get_current_system_params()
            
            resultados_adt = calculate_adt_for_multiple_flows(flows, 'L/s', system_params)
            
            # Crear DataFrame para la tabla
            df_adt = pd.DataFrame(resultados_adt)
            df_adt['Caudal (L/s)'] = df_adt['caudal_lps'].astype(int)
            df_adt['Caudal (m³/h)'] = df_adt['caudal_m3h'].round(1)
            df_adt['Pérdidas Succión (m)'] = df_adt['perdida_succion'].round(2)
            df_adt['Pérdidas Impulsión (m)'] = df_adt['perdida_impulsion'].round(2)
            df_adt['ADT Total (m)'] = df_adt['adt_total'].round(2)
            
            # Mostrar tabla según la unidad seleccionada
            unidad_caudal = st.session_state.get('flow_unit', 'L/s')
            if unidad_caudal == 'm³/h':
                # Mostrar solo m³/h cuando está seleccionado
                st.dataframe(
                    df_adt[['Caudal (m³/h)', 'Pérdidas Succión (m)', 'Pérdidas Impulsión (m)', 'ADT Total (m)']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                # Mostrar ambas columnas cuando está en L/s
                st.dataframe(
                    df_adt[['Caudal (L/s)', 'Caudal (m³/h)', 'Pérdidas Succión (m)', 'Pérdidas Impulsión (m)', 'ADT Total (m)']],
                    use_container_width=True,
                    hide_index=True
                )
            
            # Información adicional
            st.info("💡 **Nota:** La ADT aumenta con el caudal debido a las pérdidas por fricción que son proporcionales al cuadrado de la velocidad.")
            
        except Exception as e:
            st.error(f"Error calculando ADT para múltiples caudales: {e}")
    
    # ============================================================================
    # VISUALIZACIÓN DE PARÁMETROS DARCY-WEISBACH
    # ============================================================================
    if st.session_state.get('metodo_calculo') == 'Darcy-Weisbach':
        st.markdown("---")
        st.markdown("### 📐 Parámetros Darcy-Weisbach")
        
        col_suc, col_imp = st.columns(2)
        
        with col_suc:
            st.markdown("#### 🔵 Succión")
            
            # Pérdidas Primarias
            detalles_prim = st.session_state.get('detalles_calc_succion_primaria', {})
            if detalles_prim and detalles_prim.get('metodo') == 'Darcy-Weisbach':
                st.markdown("**Pérdidas Primarias:**")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Reynolds", f"{detalles_prim.get('Re', 0):.0f}")
                    st.metric("Régimen", detalles_prim.get('regimen', 'N/A'))
                    st.metric("Factor f", f"{detalles_prim.get('f', 0):.6f}")
                with col_b:
                    st.metric("Rugosidad ε (mm)", f"{detalles_prim.get('epsilon', 0)*1000:.4f}")
                    st.metric("Viscosidad ν (×10⁻⁶ m²/s)", f"{detalles_prim.get('nu', 0)*1e6:.3f}")
                    st.metric("Velocidad (m/s)", f"{detalles_prim.get('V', 0):.2f}")
                
                # Interpretación del régimen para SUCCIÓN
                st.info("""
                **Interpretación del Régimen de Flujo**:
                - **Re < 2,000**: Flujo Laminar (poco común en sistemas de bombeo)
                - **2,000 < Re < 4,000**: Zona de Transición (interpolación entre laminar y turbulento)
                - **Re > 4,000**: Flujo Turbulento (típico en sistemas de bombeo de agua)
                
                **Factor de Fricción (f)**:
                - Laminar: f = 64/Re (inversamente proporcional a Reynolds)
                - Turbulento: Calculado por Swamee-Jain (depende de Re y rugosidad ε/D)
                """)
        
        with col_imp:
            st.markdown("#### 🔴 Impulsión")
            
            # Pérdidas Primarias
            detalles_prim = st.session_state.get('detalles_calc_impulsion_primaria', {})
            if detalles_prim and detalles_prim.get('metodo') == 'Darcy-Weisbach':
                st.markdown("**Pérdidas Primarias:**")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Reynolds", f"{detalles_prim.get('Re', 0):.0f}")
                    st.metric("Régimen", detalles_prim.get('regimen', 'N/A'))
                    st.metric("Factor f", f"{detalles_prim.get('f', 0):.6f}")
                with col_b:
                    st.metric("Rugosidad ε (mm)", f"{detalles_prim.get('epsilon', 0)*1000:.4f}")
                    st.metric("Viscosidad ν (×10⁻⁶ m²/s)", f"{detalles_prim.get('nu', 0)*1e6:.3f}")
                    st.metric("Velocidad (m/s)", f"{detalles_prim.get('V', 0):.2f}")
                
                # Interpretación del régimen para IMPULSIÓN
                st.info("""
                **Interpretación del Régimen de Flujo**:
                - **Re < 2,000**: Flujo Laminar (poco común en sistemas de bombeo)
                - **2,000 < Re < 4,000**: Zona de Transición (interpolación entre laminar y turbulento)
                - **Re > 4,000**: Flujo Turbulento (típico en sistemas de bombeo de agua)
                
                **Factor de Fricción (f)**:
                - Laminar: f = 64/Re (inversamente proporcional a Reynolds)
                - Turbulento: Calculado por Swamee-Jain (depende de Re y rugosidad ε/D)
                """)

 
