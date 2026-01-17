# Barra lateral de la aplicación

import streamlit as st
from typing import Dict, Any, List

def render_sidebar():
    """Renderiza la barra lateral con configuración general (solo en tab1)"""
    
    # Indicador visual de modo desarrollador
    from config.settings import AppSettings
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
    
    st.sidebar.title("Configuración General")
    
    # Consolidar todos los controles de configuración en un solo expander
    with st.sidebar.expander("📐 Configuración del Sistema", expanded=False):
        # Tipo de ajuste de curva
        st.markdown("**Tipo de ajuste de curva**")
        default_ajuste = st.session_state.get('_loaded_ajuste_tipo', 'Cuadrática (2do grado)')
        ajuste_options = ["Lineal", "Cuadrática (2do grado)", "Polinomial (3er grado)"]
        default_index = ajuste_options.index(default_ajuste) if default_ajuste in ajuste_options else 1
        
        ajuste_tipo = st.radio(
            "Selecciona el tipo de ajuste:",
            ajuste_options,
            index=default_index,
            key="ajuste_tipo",
            horizontal=False,
            label_visibility="collapsed"
        )
        
        if '_loaded_ajuste_tipo' in st.session_state:
            del st.session_state['_loaded_ajuste_tipo']
        st.session_state['ajuste_tipo_configured'] = True
        
        st.markdown("---")
        
        # Modo de Curvas de Bomba
        st.markdown("**Modo de Curvas de Bomba**")
        default_curva_mode = st.session_state.get('_loaded_curva_mode', '3 puntos')
        curva_options = ["Excel", "3 puntos"]
        default_curva_index = curva_options.index(default_curva_mode) if default_curva_mode in curva_options else 1
        
        curva_mode = st.radio(
            "Selecciona el modo de ingreso de curvas:", 
            curva_options, 
            key="curva_mode_sidebar", 
            index=default_curva_index, 
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if '_loaded_curva_mode' in st.session_state:
            del st.session_state['_loaded_curva_mode']
        
        st.markdown("---")
        
        # Unidades de Caudal
        st.markdown("**Unidades de Caudal**")
        default_flow_unit = st.session_state.get('_loaded_flow_unit', 'L/s')
        flow_options = ['L/s', 'm³/h']
        default_flow_index = flow_options.index(default_flow_unit) if default_flow_unit in flow_options else 0
        
        if '_last_flow_unit' not in st.session_state:
            st.session_state['_last_flow_unit'] = default_flow_unit
        
        new_unit = st.radio(
            "Unidad de Caudal:", 
            flow_options, 
            key='flow_unit', 
            index=default_flow_index,
            on_change=convert_units_on_change, 
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if '_loaded_flow_unit' in st.session_state:
            del st.session_state['_loaded_flow_unit']
        
        st.markdown("---")
        
        # Parámetros físicos y ambientales
        st.markdown("**Parámetros físicos y ambientales**")
        temperatura_c = st.number_input(
            "Temperatura del líquido (°C)", 
            min_value=0.0, 
            max_value=100.0, 
            value=st.session_state.get('temp_liquido', 20.0), 
            step=0.1, 
            key="temp_liquido"
        )
        densidad_liquido = st.number_input(
            "Densidad del líquido (g/cm³)", 
            min_value=0.5, 
            max_value=2.0, 
            value=st.session_state.get('densidad_liquido', 1.0), 
            step=0.01, 
            key="densidad_liquido"
        )
        
        # Cálculo presión de vapor
        def calcular_presion_vapor_mca(temp_input):
            from core.calculations import interpolar_propiedad
            temp_C = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
            vapor_agua_mca = [0.06, 0.09, 0.12, 0.17, 0.25, 0.33, 0.44, 0.58, 0.76, 0.98, 1.25, 1.61, 2.03, 2.56, 3.20, 3.96, 4.85, 5.93, 7.18, 8.62, 10.33]
            return interpolar_propiedad(temp_input, temp_C, vapor_agua_mca)

        presion_vapor = calcular_presion_vapor_mca(temperatura_c)
        st.markdown(f"<b>Presión de vapor calculada:</b> {presion_vapor:.2f} m.c.a.", unsafe_allow_html=True)
        
        # Cálculo presión barométrica
        elevacion = st.session_state.get('elevacion_sitio', 450.0)
        densidad_agua = densidad_liquido * 1000
        G = 9.81
        gamma = densidad_agua * G
        from core.calculations import calcular_presion_atmosferica_mca
        presion_barometrica = calcular_presion_atmosferica_mca(elevacion, gamma)
        st.markdown(f"<b>Presión barométrica calculada:</b> {presion_barometrica:.2f} m.c.a.", unsafe_allow_html=True)
        
        st.session_state['presion_barometrica_calculada'] = presion_barometrica
        st.session_state['presion_vapor_calculada'] = presion_vapor
        
        st.markdown("---")
        
        # Método de Cálculo de Pérdidas
        st.markdown("**Método de Cálculo de Pérdidas**")
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
            """,
            label_visibility="collapsed"
        )
        
        st.session_state.metodo_calculo = metodo
        
        if metodo == 'Hazen-Williams':
            st.info("📘 **Método Empírico**: Usa coef. C según material")
        else:
            st.success("📐 **Método Teórico**: Calcula factor f (Re + rugosidad)")
            st.caption("⚙️ Requiere temperatura del fluido")

def render_common_sidebar_options():
    """Renderiza opciones de sidebar comunes para todos los usuarios (no requieren modo desarrollador)"""
    
    # 1. Análisis IA (con configuración de API key)
    with st.sidebar.expander("🤖 Análisis IA", expanded=False):
        # Cargar API key desde query params si existe (persistencia)
        if 'gemini_api_key' not in st.session_state:
            try:
                params = st.query_params
                if 'gak' in params:
                    st.session_state['gemini_api_key'] = params['gak']
            except:
                pass
        
        # Checkbox para activar análisis IA
        if 'ai_enabled' not in st.session_state:
            st.session_state.ai_enabled = False
        
        ai_enabled = st.checkbox(
            "Activar Análisis IA",
            value=st.session_state.ai_enabled,
            key="ai_analysis_checkbox",
            help="Activa la funcionalidad de análisis con IA en la interfaz principal"
        )
        
        st.session_state.ai_enabled = ai_enabled
        
        if ai_enabled:
            st.info("✅ Análisis IA activado. La pestaña '🤖 Análisis IA' ya está disponible.")
            
            # Subpanel Configuración Avanzada API
            with st.expander("⚙️ Configuración Avanzada API", expanded=False):
                # Selector de modelo
                st.markdown("**Modelo de IA:**")
                modelos_disponibles = [
                    "gemini-2.5-flash",      # Modelo más reciente (por defecto)
                    "gemini-2.0-flash-exp",  # Experimental 2.0
                    "gemini-1.5-flash",      # Flash 1.5 estable
                    "gemini-1.5-flash-8b",   # Flash 1.5 ligero
                    "gemini-1.5-pro",        # Pro 1.5 (mejor calidad)
                ]
                
                modelo_actual = st.session_state.get('selected_model', 'gemini-2.5-flash')
                try:
                    modelo_index = modelos_disponibles.index(modelo_actual)
                except ValueError:
                    modelo_index = 0  # Por defecto gemini-2.5-flash
                
                selected_model = st.selectbox(
                    "Modelo de IA:",
                    modelos_disponibles,
                    index=modelo_index,
                    key="gemini_model_selector",
                    help="Selecciona el modelo de Gemini a utilizar",
                    label_visibility="collapsed"
                )
                
                st.session_state['selected_model'] = selected_model
                
                # Input para API key
                st.markdown("**Clave API Gemini:**")
                api_key_input = st.text_input(
                    "Clave API Gemini:",
                    type="password",
                    value=st.session_state.get('gemini_api_key', ''),
                    key="gemini_api_key_input",
                    help="Obtén tu API key gratuita en https://makersuite.google.com/app/apikey",
                    label_visibility="collapsed"
                )
                
                # Botón para configurar API key
                if st.button("Configurar API Key", key="save_api_key", use_container_width=True):
                    if api_key_input and api_key_input.strip():
                        st.session_state['gemini_api_key'] = api_key_input.strip()
                        # Guardar en query params para persistencia
                        try:
                            st.query_params['gak'] = api_key_input.strip()
                        except:
                            pass
                        st.success("✅ API Key configurada correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Por favor ingresa una clave válida")
                
                # Botón para limpiar estado
                if st.button("🗑️ Limpiar Estado", key="clear_api_key", use_container_width=True):
                    if 'gemini_api_key' in st.session_state:
                        del st.session_state['gemini_api_key']
                    if 'api_key' in st.session_state:
                        del st.session_state['api_key']
                    if 'model' in st.session_state:
                        del st.session_state['model']
                    try:
                        if 'gak' in st.query_params:
                            del st.query_params['gak']
                    except:
                        pass
                    st.success("Estado de API limpiado.")
                    st.rerun()
        else:
            st.info("ℹ️ Activa la casilla para habilitar la pestaña de análisis con IA.")
    
    # 2. Optimización IA (GA)
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
    
    # 3. Herramientas de Análisis
    with st.sidebar.expander("🔧 Herramientas de Análisis", expanded=False):
        if 'selection_enabled' not in st.session_state:
            st.session_state.selection_enabled = True
        
        sel_enabled = st.checkbox(
            "Activar Selección Técnica de Diámetros", 
            value=st.session_state.selection_enabled,
            key="selection_checkbox",
            help="Activa la pestaña de análisis detallado de diámetros (NPSH, Pérdidas, Cavitación)"
        )
        
        st.session_state.selection_enabled = sel_enabled
        
        if sel_enabled:
            st.success("✅ Selección activada")
        else:
            st.info("ℹ️ Selección desactivada")
    
    # 4. Reportes y Visualización
    with st.sidebar.expander("📊 Reportes y Visualización", expanded=False):
        # Resumen del Proyecto
        if 'json_viewer_enabled' not in st.session_state:
            st.session_state.json_viewer_enabled = False
        
        json_enabled = st.checkbox(
            "Activar Resumen del Proyecto", 
            value=st.session_state.json_viewer_enabled,
            key="json_checkbox",
            help="Activa la pestaña de resumen del proyecto en la interfaz principal"
        )
        
        st.session_state.json_viewer_enabled = json_enabled
        
        # Reportes
        if 'informes_enabled' not in st.session_state:
            st.session_state.informes_enabled = False
        
        informes_enabled = st.checkbox(
            "Activar Reportes", 
            value=st.session_state.informes_enabled,
            key="informes_checkbox",
            help="Activa la pestaña de Reportes (Word/Excel) en la interfaz principal"
        )
        
        st.session_state.informes_enabled = informes_enabled
        
        # Tablas de Configuración
        if 'tables_enabled' not in st.session_state:
            st.session_state.tables_enabled = False
        
        tables_enabled = st.checkbox(
            "Activar Tablas de Configuración", 
            value=st.session_state.tables_enabled,
            key="tables_checkbox",
            help="Activa la pestaña de tablas de configuración del sistema"
        )
        
        st.session_state.tables_enabled = tables_enabled
        
        # Mostrar estado consolidado
        active_count = sum([json_enabled, informes_enabled, tables_enabled])
        if active_count > 0:
            st.success(f"✅ {active_count} de 3 opciones activadas")
        else:
            st.info("ℹ️ Todas las opciones desactivadas")
    
    # 5. Recursos
    with st.sidebar.expander("📚 Recursos", expanded=False):
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
    """Renderiza SOLO la sección de Desarrollador con password (disponible solo cuando SHOW_DEVELOPER_SECTION=True)"""
    
    # Sección de Desarrollador con password
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
        # Análisis Transientes
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
        
        # Simulación Operativa
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
