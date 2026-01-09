# Barra lateral de la aplicación

import streamlit as st
from typing import Dict, Any, List

def render_sidebar():
    """Renderiza la barra lateral con configuración general (solo en tab1)"""
    
    st.sidebar.title("Configuración General")
    
    # Configuración de tipo de ajuste de curva
    with st.sidebar.expander("Tipo de ajuste de curva", expanded=False):
        # Usar valor cargado si existe, sino usar valor por defecto
        default_ajuste = st.session_state.get('_loaded_ajuste_tipo', 'Cuadrática (2do grado)')
        ajuste_options = ["Lineal", "Cuadrática (2do grado)", "Polinomial (3er grado)"]
        default_index = ajuste_options.index(default_ajuste) if default_ajuste in ajuste_options else 1
        
        ajuste_tipo = st.radio(
            "Selecciona el tipo de ajuste:",
            ajuste_options,
            index=default_index,
            key="ajuste_tipo",
            horizontal=False
        )
        
        # Limpiar el valor cargado después de usarlo
        if '_loaded_ajuste_tipo' in st.session_state:
            del st.session_state['_loaded_ajuste_tipo']
        
        # Marcar que se ha configurado el tipo de ajuste
        st.session_state['ajuste_tipo_configured'] = True
    
    # Configuración de modo de curvas de bomba
    with st.sidebar.expander("Modo de Curvas de Bomba", expanded=False):
        # Usar valor cargado si existe, sino usar valor por defecto
        default_curva_mode = st.session_state.get('_loaded_curva_mode', '3 puntos')
        curva_options = ["Excel", "3 puntos"]
        default_curva_index = curva_options.index(default_curva_mode) if default_curva_mode in curva_options else 1
        
        curva_mode = st.radio(
            "Selecciona el modo de ingreso de curvas:", 
            curva_options, 
            key="curva_mode_sidebar", 
            index=default_curva_index, 
            horizontal=True
        )
        
        # Limpiar el valor cargado después de usarlo
        if '_loaded_curva_mode' in st.session_state:
            del st.session_state['_loaded_curva_mode']
    
    # Configuración de parámetros físicos y ambientales
    with st.sidebar.expander("Parámetros físicos y ambientales", expanded=False):
        temperatura_c = st.number_input("Temperatura del líquido (°C)", min_value=0.0, max_value=100.0, value=st.session_state.get('temp_liquido', 20.0), step=0.1, key="temp_liquido")
        densidad_liquido = st.number_input("Densidad del líquido (g/cm³)", min_value=0.5, max_value=2.0, value=st.session_state.get('densidad_liquido', 1.0), step=0.01, key="densidad_liquido")
        
        # Cálculo presión de vapor (solo depende de temperatura)
        def calcular_presion_vapor_mca(temp_input):
            from core.calculations import interpolar_propiedad
            temp_C = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
            vapor_agua_mca = [0.06, 0.09, 0.12, 0.17, 0.25, 0.33, 0.44, 0.58, 0.76, 0.98, 1.25, 1.61, 2.03, 2.56, 3.20, 3.96, 4.85, 5.93, 7.18, 8.62, 10.33]
            return interpolar_propiedad(temp_input, temp_C, vapor_agua_mca)

        presion_vapor = calcular_presion_vapor_mca(temperatura_c)
        st.markdown(f"<b>Presión de vapor calculada:</b> {presion_vapor:.2f} m.c.a.", unsafe_allow_html=True)
        
        # Cálculo presión barométrica (depende de elevación y densidad)
        elevacion = st.session_state.get('elevacion_sitio', 450.0)
        densidad_agua = densidad_liquido * 1000  # g/cm³ a kg/m³
        G = 9.81
        gamma = densidad_agua * G
        from core.calculations import calcular_presion_atmosferica_mca
        presion_barometrica = calcular_presion_atmosferica_mca(elevacion, gamma)
        st.markdown(f"<b>Presión barométrica calculada:</b> {presion_barometrica:.2f} m.c.a.", unsafe_allow_html=True)
        
        # Guardar el valor calculado en session_state para uso en otras secciones
        st.session_state['presion_barometrica_calculada'] = presion_barometrica
        st.session_state['presion_vapor_calculada'] = presion_vapor
    
    # Configuración de unidades
    with st.sidebar.expander("Unidades", expanded=False):
        # Usar valor cargado si existe, sino usar valor por defecto
        default_flow_unit = st.session_state.get('_loaded_flow_unit', 'L/s')  # Mantener L/s por defecto
        flow_options = ['L/s', 'm³/h']
        default_flow_index = flow_options.index(default_flow_unit) if default_flow_unit in flow_options else 0  # Por defecto L/s
        
        # Detectar cambio de unidad
        previous_unit = st.session_state.get('flow_unit', default_flow_unit)
        
        # Inicializar _last_flow_unit si no existe
        if '_last_flow_unit' not in st.session_state:
            st.session_state['_last_flow_unit'] = default_flow_unit
        
        new_unit = st.radio(
            "Unidad de Caudal:", 
            flow_options, 
            key='flow_unit', 
            index=default_flow_index,
            on_change=convert_units_on_change, 
            horizontal=True
        )
        
        # Limpiar el valor cargado después de usarlo
        if '_loaded_flow_unit' in st.session_state:
            del st.session_state['_loaded_flow_unit']
    
# Funciones auxiliares para el sidebar
def save_state():
    """Función placeholder para save_state"""
    pass

def convert_units_on_change():
    """Convierte automáticamente los valores cuando cambia la unidad de caudal"""
    current_unit = st.session_state.get('flow_unit', 'L/s')
    previous_unit = st.session_state.get('_last_flow_unit', 'L/s')
    
    # Si hay un caudal en L/s, convertir a m³/h
    if 'caudal_lps' in st.session_state and current_unit == 'm³/h':
        caudal_lps = st.session_state['caudal_lps']
        caudal_m3h = caudal_lps * 3.6
        st.session_state['caudal_m3h'] = caudal_m3h
    
    # Si hay un caudal en m³/h, convertir a L/s
    elif 'caudal_m3h' in st.session_state and current_unit == 'L/s':
        caudal_m3h = st.session_state['caudal_m3h']
        caudal_lps = caudal_m3h / 3.6
        st.session_state['caudal_lps'] = caudal_lps
    
    # Convertir valores de las curvas características si cambió la unidad
    if current_unit != previous_unit:
        # Lista de todas las curvas que necesitan conversión
        curva_keys = ['sistema', 'bomba', 'rendimiento', 'potencia', 'npsh']
        
        for curva_key in curva_keys:
            textarea_key = f'textarea_{curva_key}'
            if textarea_key in st.session_state:
                current_value = st.session_state[textarea_key]
                if current_value and current_value.strip():
                    try:
                        lines = current_value.strip().split('\n')
                        converted_lines = []
                        for line in lines:
                            if line.strip():
                                # Intentar parsear diferentes formatos: "x y", "x,y", "x;y"
                                vals = line.replace(',', ' ').replace(';', ' ').split()
                                if len(vals) >= 2:
                                    try:
                                        x = float(vals[0])
                                        y = float(vals[1])
                                        
                                        # Convertir x (caudal) según el cambio de unidad
                                        if previous_unit == 'L/s' and current_unit == 'm³/h':
                                            x_converted = x * 3.6  # L/s a m³/h
                                        elif previous_unit == 'm³/h' and current_unit == 'L/s':
                                            x_converted = x / 3.6  # m³/h a L/s
                                        else:
                                            x_converted = x  # Sin cambio
                                        
                                        converted_lines.append(f"{x_converted:.2f} {y:.2f}")
                                    except ValueError:
                                        # Si no se puede convertir, mantener la línea original
                                        converted_lines.append(line)
                                else:
                                    converted_lines.append(line)
                        
                        # Actualizar el valor del textarea
                        st.session_state[textarea_key] = '\n'.join(converted_lines)
                    except Exception:
                        # Si hay error en la conversión, mantener el valor original
                        pass
        
        # Actualizar la unidad anterior
        st.session_state['_last_flow_unit'] = current_unit

def preserve_project_data():
    """Preserva los datos del proyecto antes de cambios en el modo desarrollador"""
    # Lista de claves importantes del proyecto que deben preservarse
    project_keys = [
        'proyecto', 'diseno', 'proyecto_input_main', 'diseno_input_main',
        'caudal_lps', 'caudal_m3h', 'elevacion_sitio', 'altura_succion_input',
        'altura_descarga', 'num_bombas', 'bomba_inundada',
        'long_succion', 'diam_succion_mm', 'mat_succion', 'otras_perdidas_succion', 'accesorios_succion',
        'coeficiente_hazen_succion', 'hf_primaria_succion', 'hf_secundaria_succion', 'perdida_total_succion',
        'long_impulsion', 'diam_impulsion_mm', 'mat_impulsion', 'otras_perdidas_impulsion', 'accesorios_impulsion',
        'coeficiente_hazen_impulsion', 'hf_primaria_impulsion', 'hf_secundaria_impulsion', 'perdida_total_impulsion',
        'temp_liquido', 'densidad_liquido', 'presion_barometrica_calculada', 'presion_vapor_calculada',
        'npshd_mca', 'npsh_requerido', 'npsh_margen',
        'rpm_percentage', 'curvas_vdf', 'caudal_nominal', 'paso_caudal_vfd',
        'bomba_url', 'bomba_nombre', 'bomba_descripcion',
        'tension', 'rpm', 'motor_seleccionado',
        'curva_sistema', 'curva_bomba', 'curva_eficiencia', 'curva_potencia', 'curva_npsh',
        'textarea_sistema', 'textarea_bomba', 'textarea_rendimiento', 'textarea_potencia', 'textarea_npsh',
        'current_project_path', 'curva_inputs', 'calibration_points', 'digitalized_points'
    ]
    
    # Crear backup de datos del proyecto
    if 'project_data_backup' not in st.session_state:
        st.session_state.project_data_backup = {}
    
    # Guardar datos actuales en backup
    for key in project_keys:
        if key in st.session_state:
            st.session_state.project_data_backup[key] = st.session_state[key]

def restore_project_data():
    """Restaura los datos del proyecto desde el backup"""
    if 'project_data_backup' in st.session_state:
        for key, value in st.session_state.project_data_backup.items():
            st.session_state[key] = value

def render_developer_sidebar():
    """Renderiza el expander de Desarrollador en el sidebar (disponible en todas las pestañas)"""
    
    # 1. Resumen Proyecto
    with st.sidebar.expander("📋 Resumen Proyecto", expanded=False):
        if 'json_viewer_enabled' not in st.session_state:
            st.session_state.json_viewer_enabled = False
        
        json_enabled = st.checkbox(
            "Activar Resumen", 
            value=st.session_state.json_viewer_enabled,
            key="json_checkbox",
            help="Activa la pestaña de resumen del proyecto en la interfaz principal"
        )
        
        st.session_state.json_viewer_enabled = json_enabled
        
        if json_enabled:
            st.success("✅ Resumen activado")
        else:
            st.info("ℹ️ Resumen desactivado")
    
    # 2. Reportes
    with st.sidebar.expander("📄 Reportes", expanded=False):
        if 'informes_enabled' not in st.session_state:
            st.session_state.informes_enabled = False
        
        informes_enabled = st.checkbox(
            "Activar Reportes", 
            value=st.session_state.informes_enabled,
            key="informes_checkbox",
            help="Activa la pestaña de Reportes en la interfaz principal"
        )
        
        st.session_state.informes_enabled = informes_enabled
        
        if informes_enabled:
            st.success("✅ Reportes activado")
        else:
            st.info("ℹ️ Reportes desactivado")
    
    # 3. Método de Cálculo de Pérdidas
    with st.sidebar.expander("🧮 Método de Cálculo de Pérdidas", expanded=False):
        # Inicializar si no existe
        if 'metodo_calculo' not in st.session_state:
            st.session_state.metodo_calculo = 'Hazen-Williams'
        
        metodo = st.radio(
            "Seleccione el método:",
            options=['Hazen-Williams', 'Darcy-Weisbach'],
            index=0 if st.session_state.metodo_calculo == 'Hazen-Williams' else 1,
            key='metodo_calculo_selector',
            help="""
            **Hazen-Williams**: Empírico, solo agua a 5-25°C, rápido
            **Darcy-Weisbach**: Teórico universal, más preciso, considera Reynolds y rugosidad
            """
        )
        
        st.session_state.metodo_calculo = metodo
        
        # Indicador visual del método seleccionado
        if metodo == 'Hazen-Williams':
            st.info("📘 **Método Empírico**: Usa coef. C según material")
        else:
            st.success("📐 **Método Teórico**: Calcula factor f (Re + rugosidad)")
            st.caption("⚙️ Requiere temperatura del fluido (ver Parámetros Físicos)")
    
    # 4. Tablas de Configuración
    with st.sidebar.expander("📊 Tablas de Configuración", expanded=False):
        if 'tables_enabled' not in st.session_state:
            st.session_state.tables_enabled = False
        
        tables_enabled = st.checkbox(
            "Activar Tablas", 
            value=st.session_state.tables_enabled,
            key="tables_checkbox",
            help="Activa la pestaña de tablas de configuración del sistema"
        )
        
        st.session_state.tables_enabled = tables_enabled
        
        if tables_enabled:
            st.success("✅ Tablas activadas")
        else:
            st.info("ℹ️ Tablas desactivadas")
    
    # 4. Teoría y Fundamentos
    with st.sidebar.expander("📚 Teoría y Fundamentos", expanded=False):
        if 'theory_enabled' not in st.session_state:
            st.session_state.theory_enabled = False
        
        theory_enabled = st.checkbox(
            "Activar Teoría y Fundamentos", 
            value=st.session_state.theory_enabled,
            key="theory_checkbox",
            help="Activa la pestaña de teoría y fundamentos hidráulicos"
        )
        
        st.session_state.theory_enabled = theory_enabled
        
        if theory_enabled:
            st.success("✅ Teoría activada")
        else:
            st.info("ℹ️ Teoría desactivada")
    
    # 5. Análisis IA
    with st.sidebar.expander("🤖 Análisis IA", expanded=False):
        # Cargar API key guardada si no está en session_state
        if 'api_key' not in st.session_state or st.session_state.api_key is None:
            from ui.ai_module import cargar_api_key_desde_secrets, configurar_gemini_api
            saved_api_key = cargar_api_key_desde_secrets()
            if saved_api_key:
                st.session_state.api_key = saved_api_key
                default_model = st.session_state.get('selected_model', 'gemini-2.5-flash')
                configurar_gemini_api(saved_api_key, default_model)
        
        if 'ai_enabled' not in st.session_state:
            st.session_state.ai_enabled = False
        
        ai_enabled = st.checkbox(
            "Activar Análisis IA", 
            value=st.session_state.ai_enabled,
            key="ai_checkbox",
            help="Activa la pestaña de análisis con inteligencia artificial"
        )
        
        st.session_state.ai_enabled = ai_enabled
        
        if ai_enabled:
            st.success("✅ Análisis IA activado")
            
            # Subpanel Configuración API
            with st.expander("🔑 Configuración API", expanded=False):
                # Importar funciones necesarias
                from ui.ai_module import (
                    configurar_gemini_api, 
                    cargar_todas_api_keys_desde_secrets,
                    guardar_api_key_en_secrets
                )
                
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
                    help="Selecciona el modelo de Gemini a utilizar.",
                    key="model_selector_sidebar"
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
                        key="api_key_selector_sidebar"
                    )
                    
                    if selected_key_option != "Nueva Clave API":
                        # Usar clave existente
                        key_index = api_key_options.index(selected_key_option)
                        selected_api_key = api_keys_disponibles[key_index]
                        
                        if st.button("🔄 Usar Clave Seleccionada", key="use_key_btn_sidebar"):
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
                            help="Obtén tu clave API desde Google AI Studio.",
                            key="new_api_key_input_sidebar"
                        )
                        
                        if st.button("➕ Agregar Nueva Clave", key="add_key_btn_sidebar"):
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
                        help="Obtén tu clave API desde Google AI Studio.",
                        key="api_key_input_sidebar"
                    )
                    
                    if st.button("Configurar API Key", key="config_key_btn_sidebar"):
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
                if st.button("🗑️ Limpiar Estado", key="clear_api_btn_sidebar"):
                    st.session_state.api_key = None
                    st.session_state.model = None
                    st.success("Estado de API limpiado.")
        else:
            st.info("ℹ️ Análisis IA desactivado")
    
    # 5.1 Optimización IA (Genetic Algorithms)
    with st.sidebar.expander("🎯 Optimización IA (GA)", expanded=False):
        if 'optimization_enabled' not in st.session_state:
            st.session_state.optimization_enabled = False
        
        opt_enabled = st.checkbox(
            "Activar Optimización IA", 
            value=st.session_state.optimization_enabled,
            key="optimization_checkbox",
            help="Activa la pestaña de optimización de diámetros mediante Algoritmos Genéticos"
        )
        
        st.session_state.optimization_enabled = opt_enabled
        
        if opt_enabled:
            st.success("✅ Optimización activada")
        else:
            st.info("ℹ️ Optimización desactivada")
            
    # 5.2 Selección de Diámetros (Análisis Técnico)
    with st.sidebar.expander("📏 Selección de Diámetros", expanded=False):
        if 'selection_enabled' not in st.session_state:
            st.session_state.selection_enabled = True
        
        sel_enabled = st.checkbox(
            "Activar Selección Técnica", 
            value=st.session_state.selection_enabled,
            key="selection_checkbox",
            help="Activa la pestaña de análisis detallado de diámetros (NPSH, Pérdidas, Cavitación)"
        )
        
        st.session_state.selection_enabled = sel_enabled
        
        if sel_enabled:
            st.success("✅ Selección activada")
        else:
            st.info("ℹ️ Selección desactivada")
    
    # 6. Desarrollador
    with st.sidebar.expander("👨‍💻 Desarrollador", expanded=False):
        if 'developer_mode' not in st.session_state:
            st.session_state.developer_mode = False
        
        developer_enabled = st.checkbox(
            "Activar Modo Desarrollador", 
            value=st.session_state.developer_mode,
            key="developer_checkbox"
        )
        
        preserve_project_data()
        
        if developer_enabled and not st.session_state.developer_mode:
            password = st.text_input(
                "Contraseña de Desarrollador:", 
                type="password",
                key="developer_password"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Verificar", key="verify_password"):
                    try:
                        correct_password = None
                        
                        # 1. Intentar desde st.secrets (Streamlit Cloud)
                        if 'DEVELOPER_PASSWORD' in st.secrets:
                            correct_password = st.secrets['DEVELOPER_PASSWORD']
                            
                        # 2. Intentar desde archivo local (si existe)
                        if not correct_password:
                            try:
                                with open('secrets', 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    for line in content.split('\n'):
                                        if line.startswith('DEVELOPER_PASSWORD='):
                                            correct_password = line.split('=', 1)[1].strip()
                                            break
                            except FileNotFoundError:
                                pass
                        
                        # 3. Valor por defecto
                        if not correct_password:
                            correct_password = 'patto25'
                        
                        if password == correct_password:
                            st.session_state.developer_mode = True
                            st.success("✅ Modo desarrollador activado")
                            restore_project_data()
                        else:
                            st.error("❌ Contraseña incorrecta")
                    except Exception as e:
                        st.error(f"❌ Error al verificar contraseña: {e}")
            
            with col2:
                if st.button("❌ Cancelar", key="cancel_password"):
                    st.session_state.developer_mode = False
                    restore_project_data()
        
        elif st.session_state.developer_mode:
            st.success("🔓 Modo desarrollador activo")
            if st.button("🔒 Desactivar", key="deactivate_developer"):
                st.session_state.developer_mode = False
                restore_project_data()
    
    # PESTAÑAS DE DESARROLLADOR (solo visibles cuando desarrollador está activo)
    if st.session_state.get('developer_mode', False):
        # 7. Análisis Transientes
        with st.sidebar.expander("🔄 Análisis Transientes", expanded=False):
            if 'transient_analysis_enabled' not in st.session_state:
                st.session_state.transient_analysis_enabled = False
            
            transient_enabled = st.checkbox(
                "Activar Análisis Transientes", 
                value=st.session_state.transient_analysis_enabled,
                key="transient_checkbox",
                help="Activa la pestaña de análisis transientes en la interfaz principal"
            )
            
            st.session_state.transient_analysis_enabled = transient_enabled
            
            if transient_enabled:
                st.success("✅ Análisis transientes activado")
                st.info("💡 La pestaña de transientes estará visible en la interfaz principal")
            else:
                st.info("ℹ️ Análisis transientes desactivado")
        
        # 8. Simulación Operativa
        with st.sidebar.expander("📈 Simulación Operativa", expanded=False):
            if 'simulation_enabled' not in st.session_state:
                st.session_state.simulation_enabled = False
            
            simulation_enabled = st.checkbox(
                "Activar Simulación", 
                value=st.session_state.simulation_enabled,
                key="simulation_checkbox",
                help="Activa la pestaña de simulación dinámica y optimización energética"
            )
            
            st.session_state.simulation_enabled = simulation_enabled
            
            if simulation_enabled:
                st.success("✅ Simulación activada")
                st.info("💡 La pestaña Simulación Operativa estará visible en la interfaz principal")
            else:
                st.info("ℹ️ Simulación desactivada")
    
