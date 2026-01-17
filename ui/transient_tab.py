# Pestaña de Simulación de Transientes Hidráulicos

import streamlit as st
import pandas as pd
import json
from typing import Dict, Any
from core.transient_analysis import (
    generar_inp_transientes, 
    simular_transiente, 
    generar_recomendaciones,
    guardar_resultados_transientes,
    load_wave_speeds_data,
    buscar_material_en_celeridad
)

def render_transient_tab():
    """Renderiza la pestaña de Simulación de Transientes"""
    
    # Asegurar que existe el estado para esta pestaña
    if 'transient_simulation_data' not in st.session_state:
        st.session_state.transient_simulation_data = None
    if 'ejecutar_simulacion_transiente' not in st.session_state:
        st.session_state.ejecutar_simulacion_transiente = False
    
    # Obtener datos de st.session_state (NO de JSON)
    if 'proyecto' not in st.session_state or not st.session_state.get('proyecto'):
        st.error("⚠️ Error: No hay datos del proyecto en la sesión activa. Ejecute primero los cálculos en las pestañas anteriores.")
        return
    
    # Construir estructura de datos desde session_state
    # Usar nombres correctos de las claves en session_state
    # IMPORTANTE: Estructura debe coincidir con lo que espera generar_inp_transientes
    
    datos_proyecto = {
        'inputs': {
            'proyecto': st.session_state.get('proyecto', 'Sin nombre'),
            'caudal_diseno_lps': st.session_state.get('caudal_lps', 0.0),
            'altura_succion': st.session_state.get('altura_succion_input', 0.0),
            'altura_descarga': st.session_state.get('altura_descarga', 0.0),
            'densidad_liquido': st.session_state.get('densidad_liquido', 1.0),
            # Estructura anidada para succión (requerida por generar_inp_transientes)
            'succion': {
                'longitud': st.session_state.get('long_succion', 0.0),  # ✅ Corregido
                'diametro_interno': st.session_state.get('diam_succion_mm', 0.0),  # ✅ Corregido
                'material': st.session_state.get('mat_succion', 'PVC'),  # ✅ Corregido
                'espesor': st.session_state.get('espesor_succion', 10.0)
            },
            # Estructura anidada para impulsión (requerida por generar_inp_transientes)
            'impulsion': {
                'longitud': st.session_state.get('long_impulsion', 0.0),  # ✅ Corregido
                'diametro_interno': st.session_state.get('diam_impulsion_mm', 0.0),  # ✅ Corregido
                'material': st.session_state.get('mat_impulsion', 'PVC'),  # ✅ Corregido
                'espesor': st.session_state.get('espesor_impulsion', 8.0)
            }
        },
        'resultados': {
            'alturas': {
                'estatica_total': st.session_state.get('altura_estatica_total', 0.0),
                'dinamica_total': st.session_state.get('adt_total', 0.0)
            },
            'succion': {
                'long_equiv_accesorios': st.session_state.get('le_total_succion', 0.0)  # ✅ Corregido
            },
            'impulsion': {
                'long_equiv_accesorios': st.session_state.get('le_total_impulsion', 0.0)  # ✅ Corregido
            },
            'npsh': {
                'disponible': st.session_state.get('npshd_mca', 0.0)
            },
            'bomba_seleccionada': {
                'curva_completa': st.session_state.get('curva_bomba_completa', [])
            }
        }
    }
    
    # Validar que los datos críticos no sean cero
    if datos_proyecto['inputs']['succion']['longitud'] == 0.0:
        st.error("⚠️ Error: Longitud de succión es 0. Verifique que haya ejecutado los cálculos en las pestañas anteriores.")
    if datos_proyecto['inputs']['succion']['diametro_interno'] == 0.0:
        st.error("⚠️ Error: Diámetro de succión es 0. Verifique que haya ejecutado los cálculos en las pestañas anteriores.")
    if datos_proyecto['inputs']['impulsion']['longitud'] == 0.0:
        st.error("⚠️ Error: Longitud de impulsión es 0. Verifique que haya ejecutado los cálculos en las pestañas anteriores.")
    if datos_proyecto['inputs']['impulsion']['diametro_interno'] == 0.0:
        st.error("⚠️ Error: Diámetro de impulsión es 0. Verifique que haya ejecutado los cálculos en las pestañas anteriores.")
    if datos_proyecto['inputs']['caudal_diseno_lps'] == 0.0:
        st.error("⚠️ Error: Caudal de diseño es 0. Verifique que haya ejecutado los cálculos en las pestañas anteriores.")
    
    # Título principal
    st.markdown("### 🔄 Simulación de Transientes Hidráulicos")
    st.markdown("*Análisis de golpe de ariete y fenómenos transitorios mediante TSNet*")
    
    # Mostrar estado de TSNet
    from core.transient_analysis import TSNET_AVAILABLE, diagnosticar_tsnet
    if TSNET_AVAILABLE:
        st.success("✅ TSNet está disponible - Simulaciones habilitadas")
    else:
        st.warning("⚠️ TSNet no está instalado - Solo configuración disponible")
        
        # Mostrar diagnóstico detallado en caso de problemas
        with st.expander("🔍 Diagnóstico detallado de TSNet", expanded=False):
            diagnostico = diagnosticar_tsnet()
            
            st.write("**Información del entorno:**")
            st.write(f"- Python: {diagnostico['python_version'].split()[0]}")
            st.write(f"- Ejecutable: `{diagnostico['python_executable']}`")
            st.write(f"- Estado TSNet: {'✅ Disponible' if diagnostico['tsnet_available'] else '❌ No disponible'}")
            
            if 'tsnet_version' in diagnostico:
                st.write(f"- Versión TSNet: {diagnostico['tsnet_version']}")
                st.write(f"- Ubicación: `{diagnostico['tsnet_location']}`")
                st.write(f"- Módulos disponibles: {', '.join(diagnostico['modules_installed'])}")
                
                if 'has_network' in diagnostico:
                    st.write("**Componentes críticos:**")
                    st.write(f"- tsnet.network: {'✅' if diagnostico['has_network'] else '❌'}")
                    st.write(f"- tsnet.simulation: {'✅' if diagnostico['has_simulation'] else '❌'}")
                    if diagnostico.get('has_network'):
                        st.write(f"- TransientModel: {'✅' if diagnostico['has_TransientModel'] else '❌'}")
                    if diagnostico.get('has_simulation'):
                        st.write(f"- Initializer: {'✅' if diagnostico['has_Initializer'] else '❌'}")
                        st.write(f"- MOCSimulator: {'✅' if diagnostico['has_MOCSimulator'] else '❌'}")
            
            st.error("""
            **Instrucciones para corregir el problema:**
            
            1. **Verificar instalación:** Ejecute en terminal:
               ```bash
               pip list | findstr tsnet
               ```
            
            2. **Reinstalar TSNet:** Si no aparece o hay problemas:
               ```bash
               pip uninstall tsnet
               pip install tsnet>=0.1.10
               ```
            
            3. **Reiniciar aplicación:** Cierre la aplicación Streamlit y vuelva a ejecutar:
               ```bash
               streamlit run main.py
               ```
            """)
    
    # CSS personalizado para la interfaz
    st.markdown("""
    <style>
    .transient-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #e9ecef;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .metric-value {
        font-size: 16px;
        font-weight: bold;
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Layout de cinco columnas (20% cada una)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown('<div class="transient-container">', unsafe_allow_html=True)
        st.markdown("#### ⚙️ Configuración del Sistema")
        
        # Configuración editable del sistema para transientes
        with st.expander("📊 Configuración del Sistema para Transientes", expanded=True):
            
            st.markdown("**Parámetros Principales:**")
            
            # Mostrar datos de solo lectura desde session_state
            caudal_actual = datos_proyecto['inputs']['caudal_diseno_lps']
            altura_succion_actual = datos_proyecto['inputs']['altura_succion']
            altura_descarga_actual = datos_proyecto['inputs']['altura_descarga']
            
            st.markdown(f"""
            <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin: 5px 0;'>
            <b>Caudal de Diseño:</b> {caudal_actual:.2f} L/s<br>
            <b>Altura de Succión:</b> {altura_succion_actual:.2f} m<br>
            <b>Altura de Descarga:</b> {altura_descarga_actual:.2f} m<br>
            <b>Altura Estática Total:</b> {datos_proyecto['resultados']['alturas']['estatica_total']:.2f} m
            </div>
            """, unsafe_allow_html=True)
            
            st.caption("💡 Estos datos provienen de la configuración activa del proyecto")
            
            # Tiempo de simulación configurable (ÚNICO INPUT EDITABLE)
            st.markdown("---")
            st.markdown("**⏱️ Tiempo de Simulación:**")
            tiempo_simulacion_editado = st.number_input(
                "Duración del análisis (segundos)",
                value=st.session_state.get('tiempo_simulacion_transientes', 10.0),
                min_value=1.0,
                max_value=1800.0,  # 30 minutos
                step=1.0,
                key="transient_tiempo_simulacion",
                help="Duración del análisis transiente (máximo 30 minutos = 1800 segundos)"
            )
            
            # Mostrar tiempo en formato legible
            if tiempo_simulacion_editado >= 60:
                minutos = int(tiempo_simulacion_editado // 60)
                segundos = int(tiempo_simulacion_editado % 60)
                st.caption(f"⏱️ Equivalente a: {minutos} min {segundos} seg")
            
            # Guardar en session_state
            st.session_state['tiempo_simulacion_transientes'] = tiempo_simulacion_editado
            
            # Selección de velocidad de onda
            st.markdown("**🌊 Configuración de Velocidad de Onda:**")
            
            # Inicializar velocidades por defecto
            wave_speed_succion = 400
            wave_speed_impulsion = 400
            
            # Cargar datos de celeridad
            wave_data = load_wave_speeds_data()
            if wave_data and 'wave_speeds' in wave_data:
                wave_speeds = wave_data['wave_speeds']
                
                # Obtener materiales de succión e impulsión desde session_state
                material_succion = datos_proyecto['inputs']['succion']['material']
                material_impulsion = datos_proyecto['inputs']['impulsion']['material']
                
                col_mat1, col_mat2 = st.columns(2)
                
                with col_mat1:
                    st.markdown(f"**Material Succión:** {material_succion}")
                    
                    # Búsqueda robusta del material usando función auxiliar
                    material_encontrado = buscar_material_en_celeridad(material_succion, wave_speeds)
                    
                    if material_encontrado:
                        mat_data = wave_speeds[material_encontrado]
                        min_speed = mat_data.get('min_wave_speed', 300)
                        max_speed = mat_data.get('max_wave_speed', 500)
                        typical_speed = mat_data.get('typical_wave_speed', 400)
                        
                        st.success(f"✅ Material encontrado: {material_encontrado}")
                        
                        wave_speed_succion = st.slider(
                            f"Velocidad Onda Succión (m/s)",
                            min_value=min_speed,
                            max_value=max_speed,
                            value=typical_speed,
                            step=10,
                            key="wave_speed_succion",
                            help=f"Rango: {min_speed}-{max_speed} m/s (típico: {typical_speed} m/s)"
                        )
                    else:
                        st.warning(f"Material '{material_succion}' no encontrado en tabla de celeridad")
                        st.info(f"Materiales disponibles: {', '.join(wave_speeds.keys())}")
                        wave_speed_succion = 400  # Valor por defecto
                
                with col_mat2:
                    st.markdown(f"**Material Impulsión:** {material_impulsion}")
                    
                    # Búsqueda robusta del material usando función auxiliar
                    material_encontrado = buscar_material_en_celeridad(material_impulsion, wave_speeds)
                    
                    if material_encontrado:
                        mat_data = wave_speeds[material_encontrado]
                        min_speed = mat_data.get('min_wave_speed', 300)
                        max_speed = mat_data.get('max_wave_speed', 500)
                        typical_speed = mat_data.get('typical_wave_speed', 400)
                        
                        st.success(f"✅ Material encontrado: {material_encontrado}")
                        
                        wave_speed_impulsion = st.slider(
                            f"Velocidad Onda Impulsión (m/s)",
                            min_value=min_speed,
                            max_value=max_speed,
                            value=typical_speed,
                            step=10,
                            key="wave_speed_impulsion",
                            help=f"Rango: {min_speed}-{max_speed} m/s (típico: {typical_speed} m/s)"
                        )
                    else:
                        st.warning(f"Material '{material_impulsion}' no encontrado en tabla de celeridad")
                        st.info(f"Materiales disponibles: {', '.join(wave_speeds.keys())}")
                        wave_speed_impulsion = 400  # Valor por defecto
                
                # Mostrar velocidad promedio
                vel_promedio = (wave_speed_succion + wave_speed_impulsion) / 2
                st.metric("Velocidad Promedio Seleccionada", f"{vel_promedio:.1f} m/s")
                
                # Indicar que estos valores se usarán en la simulación
                st.success(f"✅ Estos valores se aplicarán en la simulación de transientes")
                
                # Detectar cambios en velocidades y ejecutar simulación automáticamente
                if 'velocidades_anteriores' not in st.session_state:
                    st.session_state.velocidades_anteriores = {
                        'succion': wave_speed_succion,
                        'impulsion': wave_speed_impulsion
                    }
                
                # Verificar si las velocidades cambiaron
                velocidades_cambiaron = (
                    st.session_state.velocidades_anteriores['succion'] != wave_speed_succion or
                    st.session_state.velocidades_anteriores['impulsion'] != wave_speed_impulsion
                )
                
                if velocidades_cambiaron:
                    st.session_state.velocidades_anteriores = {
                        'succion': wave_speed_succion,
                        'impulsion': wave_speed_impulsion
                    }
                    st.session_state.ejecutar_simulacion_transiente = True
                    st.session_state.mod_l_simulacion_prueba = False  # Usar datos reales
                    st.session_state.velocidades_cambiaron = True  # Marcar que hubo cambios
                    st.info("🔄 Velocidades cambiadas - Ejecutando simulación automáticamente...")
                    st.rerun()  # Forzar actualización de la página
                
            else:
                st.warning("No se pudieron cargar los datos de celeridad. Usando valores por defecto.")
                wave_speed_succion = 400
                wave_speed_impulsion = 400
            
            # Altura dinámica (calculada)
            altura_dinamica = datos_proyecto['resultados']['alturas']['dinamica_total']
            npsh_real = datos_proyecto['resultados']['npsh']['disponible']
            
            st.markdown("---")
            st.markdown("**📊 Métricas Calculadas:**")
            
            # Obtener valores directamente de session_state (NO calcular)
            adt_total_valor = st.session_state.get('adt_total', 0.0)
            npsh_disponible_valor = st.session_state.get('npshd_mca', 0.0)
            
            st.markdown(f"""
            <div style='background-color: #e8f4f8; padding: 10px; border-radius: 5px; margin: 5px 0;'>
            <b>Altura Dinámica Total (ADT):</b> {adt_total_valor:.2f} m<br>
            <b>NPSH Disponible:</b> {npsh_disponible_valor:.2f} m
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("**📏 Geometría de Tuberías:**")
            
            # Obtener datos de tuberías desde la estructura datos_proyecto
            long_succion_editada = datos_proyecto['inputs']['succion']['longitud']
            diam_succion_editado = datos_proyecto['inputs']['succion']['diametro_interno']
            long_impulsion_editada = datos_proyecto['inputs']['impulsion']['longitud']
            diam_impulsion_editado = datos_proyecto['inputs']['impulsion']['diametro_interno']
            
            long_succion_equiv_accesorios = datos_proyecto['resultados']['succion']['long_equiv_accesorios']
            long_impulsion_equiv_accesorios = datos_proyecto['resultados']['impulsion']['long_equiv_accesorios']
            
            # Mostrar información de geometría
            st.markdown(f"""
            <div style='background-color: #fff3cd; padding: 10px; border-radius: 5px; margin: 5px 0;'>
            <b>🔵 Succión:</b><br>
              • Longitud real: {long_succion_editada:.2f} m<br>
              • Long. equiv. accesorios: {long_succion_equiv_accesorios:.2f} m<br>
              • Diámetro interno: {diam_succion_editado:.2f} mm<br>
              • Material: {material_succion}<br>
            <br>
            <b>🔴 Impulsión:</b><br>
              • Longitud real: {long_impulsion_editada:.2f} m<br>
              • Long. equiv. accesorios: {long_impulsion_equiv_accesorios:.2f} m<br>
              • Diámetro interno: {diam_impulsion_editado:.2f} mm<br>
              • Material: {material_impulsion}
            </div>
            """, unsafe_allow_html=True)
            
            st.caption("💡 Estos datos provienen de la configuración activa del proyecto")
            
            # Explicación sobre discrepancias en picos de presión
            with st.expander("🔍 ⚠️ Explicación sobre Picos de Presión Transiente", expanded=False):
                st.markdown("""
                **¿Por qué pueden haber discrepancias entre valores?**
                
                **Pico en Gráfico (ej: 126.4m)**: 
                - Representa un punto específico en el tiempo
                - Puede ser un promedio o valor en zona específica
                
                **Pico en Datos (ej: 241.9m)**:
                - Representa EL VALOR MÁXIMO ABSOLUTO durante toda la simulación
                - Se encuentra analizando todos los puntos de tiempo y ubicaciones
                - Este es el valor que **debe usarse para diseño de protección**
                
                **Recomendación Ingenieril**:
                - 🎯 **SIEMPRE usar el valor más alto** (241.9m en el ejemplo) para diseño
                - 📏 Dimensionar tuberías y protecciones para el pico máximo real
                - 🔧 Este valor determina la presión nominal (PN) requerida
                - ⚠️ Si usa 126.4m para diseño, el sistema puede fallar en el pico real de 241.9m
                
                **Corrección implementada**: El nuevo modelo muestra tanto la curva temporal como el verdadero pico máximo.
                """)
            
            # Calcular tiempo de viaje de onda aproximado
            with st.expander("⏱️ Tiempo de Viaje de Onda", expanded=False):
                if material_impulsion.upper() in ['HDPE', 'PEAD', 'POLIETILENO']:
                    vel_onda_aproxima = 600  # m/s para PEAD
                elif 'HIERRO' in material_impulsion.upper():
                    vel_onda_aproxima = 1200  # m/s para hierro
                elif 'PVC' in material_impulsion.upper():
                    vel_onda_aproxima = 400  # m/s para PVC
                else:
                    vel_onda_aproxima = 800  # m/s valor promedio
                
                tiempo_viaje_onda = (2 * long_impulsion_editada) / vel_onda_aproxima
                
                st.markdown(f"""
                **Tiempo de viaje de onda:** ~{tiempo_viaje_onda:.2f} s
                
                **Velocidad aproximada:** {vel_onda_aproxima} m/s
                
                **Fórmula:** T = 2L/a
                - L = Longitud tubería impulsión ({long_impulsion_editada:.2f} m)
                - a = Velocidad de onda ({vel_onda_aproxima} m/s)
                
                **Criterio de cierre:**
                - Si Tc ≤ {tiempo_viaje_onda:.2f} s → Cierre rápido (golpe de ariete severo)
                - Si Tc > {tiempo_viaje_onda:.2f} s → Cierre gradual (golpe controlado)
                """)
            
            # Nota explicativa sobre longitudes equivalentes en expander
            with st.expander("📝 Criterio para Análisis de Transientes", expanded=False):
                st.markdown("""
                **Longitud real**: Longitud física de la tubería → **USADA PARA TRANSIENTES**
                - Determina el tiempo de viaje de la onda de presión (Δt = 2L/a)
                - Crucial para evaluar si el cierre es rápido (Tc < Δt) → golpe de ariete severo
                
                **Longitud equivalente por accesorios**: Solo para análisis estacionario (ADT)
                - Se usa únicamente para calcular pérdidas por fricción en válvulas y accesorios
                - NO se suma para análisis de transientes
                
                **Importante**: Las válvulas y accesorios se modelan con sus curvas características reales y tiempo de operación, no como longitud adicional.
                
                **Criterio de cierre:** 
                - Si tiempo de cierre ≤ tiempo viaje onda → **Cierre rápido** → Golpe de ariete severo
                - Si tiempo de cierre > tiempo viaje onda → **Cierre gradual** → Golpe de ariete controlado
                
                **Modelado en TSNet:**
                - Tuberías: Longitud real + diámetro interno
                - Válvulas: Curva de cierre (% apertura vs tiempo)
                - Accesorios: Coeficiente de pérdida K (no longitud)
                """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="transient-container">', unsafe_allow_html=True)
        # Selector de tipo de transiente
        st.markdown("#### 🎯 Tipo de Transiente")
        evento = st.selectbox(
            "Evento a simular:",
            ["Cierre Rápido de Válvula", "Corte Súbito de Bomba"],
            help="Seleccione el tipo de evento transiente para analizar"
        )
        
        # Mostrar parámetros específicos del evento
        if evento == "Cierre Rápido de Válvula":
            st.info("🔧 **Cierre Rápido**: Simulación de cierre instantáneo")
            st.markdown("""
            **Comportamiento esperado:**
            - ⚡ **Sobrepresión inicial** (~+30%) por detención súbita del flujo
            - 📈 **Picos de presión** que pueden superar resistencia del material
            - 🔄 **Oscilaciones amortiguadas** tras el impacto inicial
            - ⚠️ **Riesgo**: Ruptura si excede presión nominal
            """)
        else:
            st.info("⚡ **Corte Súbito**: Simulación de parada instantánea de bomba")
            st.markdown("""
            **Comportamiento esperado:**
            - 📉 **Depresión inicial** (~-40%) por pérdida de suministro
            - 💧 **Riesgo de cavitación** si presión < presión vapor
            - 🌊 **Ondas de depresión** que se propagan por el sistema
            - ⚠️ **Riesgo**: Implosión si presión muy baja
            """)
        
        # Opciones de ejecución
        st.markdown("#### ▶️ Opciones de Ejecución")
        
        modo_simulacion = st.radio(
            "Modo de simulación:",
            ["Sistema Real (datos calculados)", "Sistema de Prueba (modelo simple)"],
            help="Elija si usar los datos reales del proyecto o un modelo simple para verificar funcionamiento"
        )
        
        if modo_simulacion == "Sistema Real (datos calculados)":
            if st.button("🚀 Ejecutar Simulación Real", type="primary", use_container_width=True):
                st.session_state.ejecutar_simulacion_transiente = True
                st.session_state.mod_l_simulacion_prueba = False
        else:
            if st.button("🧪 Ejecutar Simulación de Prueba", type="secondary", use_container_width=True):
                st.session_state.ejecutar_simulacion_transiente = True
                st.session_state.mod_l_simulacion_prueba = True
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="transient-container">', unsafe_allow_html=True)
        st.markdown("#### 📈 Resultados de Simulación")
        
        # Ejecutar simulación si se presionó el botón
        if st.session_state.ejecutar_simulacion_transiente:
            
            # Verificar disponibilidad de TSNet
            from core.transient_analysis import TSNET_AVAILABLE
            if not TSNET_AVAILABLE:
                st.error("❌ TSNet no está instalado")
                st.markdown("""
                **Para usar la simulación de transientes:**
                
                1. Instale TSNet ejecutando en terminal:
                   ```bash
                   pip install tsnet
                   ```
                
                2. Reinicie la aplicación:
                   ```bash
                   streamlit run main.py
                   ```
                
                3. Ejecute nuevamente la simulación
                """)
                st.session_state.ejecutar_simulacion_transiente = False
                return
            
            with st.spinner("🔄 Ejecutando simulación transiente..."):
                try:
                    # Verificar si usar simulación de prueba o datos reales
                    usar_prueba = st.session_state.get('mod_l_simulacion_prueba', False)
                    
                    if usar_prueba:
                        st.info("🧪 Usando modelo de simulación de prueba...")
                        # Crear datos ficticios para la simulación de prueba
                        datos_prueba = {
                            'inputs': {
                                'proyecto': 'Sistema de Prueba TSNet',
                                'caudal_diseno_lps': 10.0,
                                'altura_succion': 2.0,
                                'altura_descarga': 20.0,
                                'densidad_liquido': 1.0,
                                'succion': {'material': 'PVC', 'espesor': 10, 'longitud': 10, 'diametro_interno': 100},
                                'impulsion': {'material': 'PVC', 'espesor': 8, 'longitud': 100, 'diametro_interno': 80}
                            },
                            'resultados': {
                                'alturas': {'dinamica_total': 25.0},
                                'npsh': {'disponible': 8.0},
                                'bomba_seleccionada': {'curva_completa': [(0,30),(5,28),(10,25),(15,20)]}
                            }
                        }
                        inp_file = generar_inp_transientes(datos_prueba)
                        resultados = simular_transiente(inp_file, evento, datos_prueba)
                    else:
                        # Usar datos_proyecto con tiempo de simulación actualizado
                        datos_proyecto_modificado = datos_proyecto.copy()
                        
                        # Actualizar tiempo de simulación
                        datos_proyecto_modificado['inputs']['tiempo_simulacion_transientes'] = tiempo_simulacion_editado
                        
                        # Agregar velocidades de onda seleccionadas por el usuario
                        datos_proyecto_modificado['inputs']['wave_speed_succion'] = wave_speed_succion
                        datos_proyecto_modificado['inputs']['wave_speed_impulsion'] = wave_speed_impulsion
                        
                        # Generar archivo .inp con datos del proyecto
                        st.info("📝 Generando archivo .inp para TSNet...")
                        inp_file = generar_inp_transientes(datos_proyecto_modificado)
                        
                        if inp_file is None:
                            st.error("❌ No se pudo generar el archivo .inp")
                            st.session_state.ejecutar_simulacion_transiente = False
                            return
                        
                        # Ejecutar simulación con datos del proyecto
                        st.info(f"⚙️ Ejecutando simulación: {evento}...")
                        resultados = simular_transiente(inp_file, evento, datos_proyecto_modificado)
                    
                    # Mostrar resultados
                    if resultados['success']:
                        st.success("✅ Simulación completada exitosamente")
                        
                        # Mostrar gráfico
                        st.pyplot(resultados['fig'])
                        
                        # Indicador de simulación automática
                        if 'velocidades_cambiaron' in st.session_state and st.session_state.velocidades_cambiaron:
                            st.success("🔄 Simulación ejecutada automáticamente debido a cambios en velocidades de onda")
                            st.session_state.velocidades_cambiaron = False  # Resetear flag
                        
                        # Guardar datos para usar en otras columnas
                        st.session_state['transient_max_head'] = resultados['max_head']
                        st.session_state['transient_min_head'] = resultados['min_head']
                        st.session_state['transient_dt_used'] = resultados.get('dt_used', 0.01)
                        st.session_state['transient_wave_speed_suc'] = resultados.get('wave_speed_succion', 400.0)
                        st.session_state['transient_wave_speed_imp'] = resultados.get('wave_speed_impulsion', 400.0)
                        st.session_state['transient_usar_prueba'] = usar_prueba
                        
                        # Guardar para el PDF
                        st.session_state['transientes_resultados'] = resultados
                        st.session_state['fig_transientes'] = resultados.get('fig', None)
                        st.session_state['velocidad_onda'] = resultados.get('wave_speed_succion', 400.0)
                        st.session_state['tiempo_cierre'] = datos_proyecto.get('tiempo_cierre', 5.0)
                        st.session_state['presion_maxima_transiente'] = resultados['max_head']
                        st.session_state['presion_minima_transiente'] = resultados['min_head']
                        
                        # Guardar resultados en archivo (solo para simulaciones reales)
                        if not usar_prueba:
                            archivo_guardado = guardar_resultados_transientes(datos_proyecto, resultados)
                            if archivo_guardado:
                                st.info(f"💾 Resultados guardados en: `{archivo_guardado}`")
                        else:
                            st.info("ℹ️ Simulación de prueba - resultados no guardados")
                        
                        # Resetear flag
                        st.session_state.ejecutar_simulacion_transiente = False
                        st.session_state.transient_simulation_data = resultados
                        
                        st.markdown("#### 📊 Métricas Principales")
                        
                        col_max, col_min = st.columns(2)
                        with col_max:
                            # Calcular delta respecto a altura estática
                            max_head = resultados['max_head']
                            altura_estatica = datos_proyecto['resultados']['alturas']['estatica_total']
                            delta_positivo = max_head - altura_estatica if max_head > altura_estatica else 0.0
                            st.metric(
                                "Pico Máximo",
                                f"{max_head:.1f} m",
                                delta=f"Δ+{delta_positivo:.1f} m"
                            )
                        
                        with col_min:  
                            # Acceso defensivo para NPSH
                            npsh_disponible = datos_proyecto['resultados']['npsh']['disponible']
                            min_head = resultados['min_head']
                            st.metric(
                                "Presión Mínima", 
                                f"{min_head:.1f} m",
                                delta=f"NPSH: {npsh_disponible:.2f} m"
                            )
                        
                        # Información técnica del timestep
                        st.markdown("#### 🔧 Parámetros de Simulación")
                        col_dt, col_wave = st.columns(2)
                        with col_dt:
                            # Acceso defensivo para dt_used
                            dt_used = resultados.get('dt_used', 0.01)  # Valor por defecto razonable
                            st.metric(
                                "Timestep utilizado",
                                f"{dt_used:.6f} s",
                                help="Timestep para estabilidad numérica de TSNet"
                            )
                        with col_wave:
                            # Acceso defensivo para velocidades de onda
                            wave_speed_succion_result = resultados.get('wave_speed_succion', 400.0)
                            wave_speed_impulsion_result = resultados.get('wave_speed_impulsion', 400.0)
                            vel_promedio = (wave_speed_succion_result + wave_speed_impulsion_result) / 2
                            
                            # Mostrar velocidad promedio
                            st.metric(
                                "Velocidad promedio",
                                f"{vel_promedio:.1f} m/s",
                                delta="Valores seleccionados",
                                help="Velocidad promedio usando valores seleccionados en configuración"
                            )
                        
                        # Alertas según umbrales (usar datos apropiados)
                        datos_usar = datos_prueba if usar_prueba else datos_proyecto
                        altura_dinamica = datos_usar['resultados']['alturas']['dinamica_total']
                        umbral_pico = altura_dinamica * 1.5
                        npsh_disponible = datos_usar['resultados']['npsh']['disponible']
                        
                        if max_head > umbral_pico:
                            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                            st.warning(f"⚠️ **ALERTA**: Pico crítico ({max_head:.1f} m) excede umbral seguro ({umbral_pico:.1f} m)")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        if min_head < npsh_disponible:
                            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                            st.warning(f"⚠️ **CAVITACIÓN**: Presión mínima ({min_head:.1f} m) < NPSH ({npsh_disponible:.2f} m)")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        if (max_head <= umbral_pico and min_head >= npsh_disponible):
                            st.markdown('<div class="success-box">', unsafe_allow_html=True)
                            st.success("✅ Presiones dentro de límites seguros")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Guardar resultados (solo para simulaciones reales)
                        if not usar_prueba:
                            archivo_guardado = guardar_resultados_transientes(datos_proyecto, resultados)
                            if archivo_guardado:
                                st.info(f"💾 Resultados guardados en: `{archivo_guardado}`")
                        else:
                            st.info("ℹ️ Simulación de prueba - resultados no guardados")
                        
                        # Resetear flag
                        st.session_state.ejecutar_simulacion_transiente = False
                        st.session_state.transient_simulation_data = resultados
                        
                    else:
                        st.error(f"❌ Error en simulación: {resultados['error']}")
                        
                        # Mostrar diagnóstico detallado del archivo .inp si hay errores
                        if resultados.get('error_type') == 'InputFileError':
                            st.warning("🔍 **Diagnóstico del archivo .inp:**")
                            from core.transient_analysis import depurar_inp_file
                            diagnostico_inp = depurar_inp_file(inp_file)
                            
                            with st.expander("📋 Detalles del diagnóstico", expanded=True):
                                st.write(f"**Archivo:** `{diagnostico_inp['archivo']}`")
                                st.write(f"**Existe:** {'✅ Sí' if diagnostico_inp['existe'] else '❌ No'}")
                                st.write(f"**Legible:** {'✅ Sí' if diagnostico_inp['legible'] else '❌ No'}")
                                
                                if diagnostico_inp['estructura']:
                                    st.write("**Secciones detectadas:**")
                                    for seccion, count in diagnostico_inp['estructura'].items():
                                        st.write(f"- {seccion}: {count} ocurrencias")
                                
                                if diagnostico_inp['errores']:
                                    st.write("**Problemas encontrados:**")
                                    for error in diagnostico_inp['errores']:
                                        st.write(f"- ❌ {error}")
                                
                                # Mostrar contenido del archivo .inp para revisión
                                st.write("**Contenido del archivo .inp:**")
                                try:
                                    with open(inp_file, 'r', encoding='utf-8') as f:
                                        contenido_inp = f.read()
                                    st.code(contenido_inp, language='text')
                                except:
                                    st.error("No se pudo leer el contenido del archivo")
                        
                        st.info("💡 **Sugerencias:**")
                        sugerencias = [
                            "- Verificar que TSNet esté instalado: `pip install tsnet`",
                            "- Revisar configuración del archivo .inp",
                            "- Validar datos de entrada del sistema",
                            "- Verificar que todos los nodos existen en [JUNCTIONS]",
                            "- Comprobar formato de números (puntos decimales, no comas)",
                            "- Asegurar que las secciones requeridas estén presentes"
                        ]
                        
                        for sugerencia in sugerencias:
                            st.markdown(sugerencia)
                        
                        st.session_state.ejecutar_simulacion_transiente = False
                
                except Exception as e:
                    error_msg = str(e)
                    if 'time' in error_msg.lower():
                        st.error(f"❌ Error accediendo a datos temporales: {error_msg}")
                        st.info("💡 **Solución**: Este es un problema interno de acceso a datos. Intente ejecutar la simulación nuevamente o ajuste los parámetros de tiempo.")
                    else:
                        st.error(f"❌ Error inesperado: {error_msg}")
                    st.session_state.ejecutar_simulacion_transiente = False
        
        else:
            st.info("ℹ️ Seleccione configuraciones en la columna izquierda y presione 'Ejecutar Simulación' para comenzar")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="transient-container">', unsafe_allow_html=True)
        st.markdown("#### 📈 Análisis Visual")
        
        # Espacio reservado para futuras visualizaciones adicionales
        if st.session_state.transient_simulation_data:
            resultados = st.session_state.transient_simulation_data
            if resultados['success']:
                st.info("ℹ️ El gráfico principal se muestra en la columna de resultados (izquierda)")
            else:
                st.warning("⚠️ No hay datos de simulación disponibles")
        else:
            st.info("ℹ️ Ejecute una simulación para ver los resultados gráficos")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="transient-container">', unsafe_allow_html=True)
        st.markdown("#### 📋 Resumen y Comentarios Técnicos")
        
        # Mostrar información técnica si hay datos
        if st.session_state.transient_simulation_data:
            resultados = st.session_state.transient_simulation_data
            
            if resultados['success']:
                # Información técnica adicional
                st.markdown("##### 🔧 Información Técnica")
                wave_speed_succion = resultados.get('wave_speed_succion', 400.0)
                wave_speed_impulsion = resultados.get('wave_speed_impulsion', 400.0)
                dt_usado = resultados.get('dt_used', 0.01)
                st.write(f"**Velocidad de onda succión**: {wave_speed_succion:.0f} m/s")
                st.write(f"**Velocidad de onda impulsión**: {wave_speed_impulsion:.0f} m/s")
                st.write(f"**Timestep utilizado**: {dt_usado:.4f} s")
                
                # Verificación de estabilidad numérica
                if dt_usado > 0.01:
                    st.warning("⚠️ Timestep elevado - Verificar estabilidad numérica")
                else:
                    st.success("✅ Timestep adecuado para estabilidad")
            else:
                st.error("No se puede mostrar información técnica por errores en la simulación")
        else:
            st.info("ℹ️ Ejecute una simulación para mostrar recomendaciones técnicas")
            
        # Información educativa en expanders (siempre visible)
        with st.expander("📚 ¿Qué es un Transiente Hidráulico?", expanded=False):
            st.markdown("""
            **Transientes hidráulicos** son cambios súbitos en presión y velocidad debido a:
            
            - 🔧 **Cierre rápido de válvulas**: Genera "golpe de ariete"
            - ⚡ **Parada súbita de bombas**: Causa vacuaciones y cavitación
            - 🌊 **Ondas de presión**: Se propagan a velocidad de onda característica
            
            **Impactos críticos:**
            - 💥 Sobrepresión que puede romper tuberías
            - 🏺 Cavitación que daña bombas
            - ⚖️ Diseño de protección adecuada es esencial
            
            **Fenómenos físicos:**
            - La onda de presión viaja a velocidad del sonido en el fluido
            - Se refleja en cambios de sección y extremos de tubería
            - Puede generar oscilaciones que duran varios segundos
            """)
        
        # Guía de interpretación técnica dinámica
        with st.expander("📋 GUÍA DE INTERPRETACIÓN TÉCNICA", expanded=False):
            st.markdown("""
            **📊 Cómo interpretar los resultados:**
            
            **🎯 Métricas principales:**
            - **Altura Dinámica**: Capacidad de trabajo normal del sistema
            - **Pico Máximo**: Presión máxima durante transientes
            - **Presión Mínima**: Menor presión (riesgo de cavitación)
            
            **🔍 Análisis automático:**
            - El sistema lee los datos **REALES** desde la configuración
            - Compara picos transientes con capacidad de tubería instalada
            - Aplica factor de seguridad según normas técnicas
            
            **⚖️ Criterios de evaluación:**
            1. **Pico ≤ Capacidad Tubería**: Sistema seguro ✓
            2. **Pico > Capacidad Tubería**: Protección requerida ⚠️
            3. **Exceso >30%**: Acción inmediata crítica 🚨
            
            **💡 Próxima simulación mostrará:**
            - Comparación específica con tubería instalada
            - Factor de seguridad aplicado en cálculo
            - Alternativas técnicas según nivel de riesgo
            
            **📐 Fórmulas clave:**
            - Sobrepresión Joukowsky: ΔP = ρ × a × ΔV
            - Tiempo de onda: T = 2L/a
            - Criterio de cierre rápido: Tc < T
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col5:
        st.markdown('<div class="transient-container">', unsafe_allow_html=True)
        st.markdown("#### 💡 Recomendaciones")
        
        # Mostrar recomendaciones si hay datos
        if st.session_state.transient_simulation_data:
            resultados = st.session_state.transient_simulation_data
            
            if resultados['success']:
                # Usar datos adecuados para recomendaciones
                datos_usar_recomendaciones = datos_proyecto if not st.session_state.get('mod_l_simulacion_prueba', False) else None
                if datos_usar_recomendaciones:
                    recomendaciones = generar_recomendaciones(resultados, datos_usar_recomendaciones)
                    
                    st.markdown("##### 💡 Conclusiones y Recomendaciones")
                    for recomendacion in recomendaciones:
                        st.markdown(recomendacion)
                else:
                    st.info("ℹ️ Simulación de prueba - recomendaciones no aplicables")
            else:
                st.error("No se pueden generar recomendaciones por errores en la simulación")
        else:
            st.info("ℹ️ Ejecute una simulación para ver recomendaciones personalizadas")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer informativo
    st.markdown("""---""")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 12px;'>
    💡 <strong>Consejo:</strong> Para análisis precisos, verifique siempre los datos de entrada y considere múltiples escenarios de transientes
    </div>
    """, unsafe_allow_html=True)
