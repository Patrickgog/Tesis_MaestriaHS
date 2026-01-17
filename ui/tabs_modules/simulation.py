import streamlit as st
import numpy as np
import pandas as pd
from core.optimization_logic import CentrifugalPumpDesigner
from scipy.optimize import fsolve

def default_hourly_factors():
    """Factores horarios por defecto (curva de demanda típica)"""
    return [0.6, 0.6, 0.6, 0.6, 0.7, 0.85, 1.1, 1.4, 1.7, 2.1, 1.95, 1.8, 
            1.7, 1.6, 1.5, 1.55, 1.7, 1.9, 2.0, 1.6, 1.2, 1.0, 0.8, 0.7]

def verificar_datos_minimos():
    """Verifica que existan los datos mínimos necesarios para la simulación"""
    required_keys = {
        'caudal_lps': 'Caudal de diseño',
        'long_impulsion': 'Longitud de tubería',
        'diam_interno_impulsion': 'Diámetro de tubería',
        'coeficiente_hazen_impulsion': 'Coeficiente Hazen-Williams'
    }
    
    missing = []
    for key, label in required_keys.items():
        value = st.session_state.get(key)
        if value is None or value == 0:
            missing.append(label)
    
    return len(missing) == 0, missing

def crear_simulador():
    """Crea instancia del simulador con datos de session_state y sidebar"""
    q_design_lps = st.session_state.get('caudal_lps', 10.0)
    q_design_m3s = q_design_lps / 1000.0
    
    h_static = st.session_state.get('altura_estatica_total', 
                                    st.session_state.get('h_estatica', 50.0))
    
    rpm = st.session_state.get('rpm', 3500)
    
    pipe_length_m = st.session_state.get('long_impulsion', 100.0)
    
    pipe_diameter_mm = st.session_state.get('diam_interno_impulsion', 100.0)
    pipe_diameter_m = pipe_diameter_mm / 1000.0
    
    n_parallel = int(st.session_state.get('num_bombas', 1))
    
    hw_c = st.session_state.get('coeficiente_hazen_impulsion', 130)
    
    eff_op_pct = st.session_state.get('eficiencia_operacion', 78.0)
    eff_peak = eff_op_pct / 100.0
    
    electricity_cost = st.session_state.get('sim_electricity_cost', 0.12)
    
    hourly_factors_list = st.session_state.get('sim_hourly_factors', default_hourly_factors())
    
    simulation_days = int(st.session_state.get('sim_days', 1))
    
    min_tank_level_perc = st.session_state.get('sim_min_tank_perc', 30.0) / 100.0
    
    initial_tank_level_perc = st.session_state.get('sim_initial_tank_perc', 80.0) / 100.0
    
    tank_capacity_m3 = st.session_state.get('sim_tank_capacity_m3', None)
    
    tank_round_m3 = st.session_state.get('sim_tank_round_m3', 50.0)
    
    try:
        simulator = CentrifugalPumpDesigner(
            q_design=q_design_m3s,
            h_static=h_static,
            rpm=rpm,
            hourly_factors=np.array(hourly_factors_list),
            pipe_length_m=pipe_length_m,
            pipe_diameter_m=pipe_diameter_m,
            n_parallel=n_parallel,
            hw_c=hw_c,
            eff_peak=eff_peak,
            electricity_cost=electricity_cost,
            min_tank_level_perc=min_tank_level_perc,
            initial_tank_level_perc=initial_tank_level_perc,
            simulation_days=simulation_days,
            tank_capacity_m3=tank_capacity_m3,
            tank_round_m3=tank_round_m3
        )
        return simulator
    except Exception as e:
        st.error(f"Error al crear simulador: {str(e)}")
        return None

def render_theory_column_curvas():
    """Renderiza teoría para tab Curvas y Operación"""
    with st.expander("📐 Fundamentos Teóricos", expanded=False):
        st.markdown("""
        #### Ecuación de Hazen-Williams
        La pérdida de carga por fricción en la tubería se calcula mediante:
        
        $$h_f = 10.67 \\cdot \\frac{L \\cdot Q^{1.852}}{C^{1.852} \\cdot D^{4.871}}$$
        
        Donde:
        - $h_f$ = Pérdida por fricción (m)
        - $L$ = Longitud tubería (m)
        - $Q$ = Caudal ($m^3/s$)
        - $C$ = Coeficiente rugosidad (adimensional)
        - $D$ = Diámetro interno (m)
        
        #### Curva del Sistema
        La altura total que debe vencer el sistema:
        
        $$H_{sistema} = H_{estática} + h_f$$
        
        #### Curva de la Bomba
        Aproximación parabólica:
        
        $$H_{bomba} = H_0 - a \\cdot Q^2$$
        
        Donde:
        - $H_0$ = Altura de shutoff (Q = 0)
        - $a$ = Coeficiente de curvatura
        
        #### Punto de Operación
        Se encuentra en la intersección:
        
        $$H_{bomba}(Q_{op}) = H_{sistema}(Q_{op})$$
        
        #### Leyes de Afinidad (VFD)
        Al variar la velocidad de rotación:
        
        $$\\frac{Q_2}{Q_1} = \\frac{N_2}{N_1}$$
        
        $$\\frac{H_2}{H_1} = \\left(\\frac{N_2}{N_1}\\right)^2$$
        
        $$\\frac{P_2}{P_1} = \\left(\\frac{N_2}{N_1}\\right)^3$$
        
        Donde $N$ = RPM, $Q$ = Caudal, $H$ = Altura, $P$ = Potencia
        
        ---
        
        #### 💡 Aplicación Práctica
        - **Curva Sistema**: Define requerimientos hidráulicos
        - **Curva Bomba**: Capacidad disponible
        - **Punto Operación**: Estado real de trabajo
        - **VFD**: Ajuste dinámico para eficiencia
        """)

def render_theory_column_eficiencia():
    """Renderiza teoría para tab Eficiencia y Costos"""
    with st.expander("📐 Fundamentos Teóricos", expanded=False):
        st.markdown("""
        #### Potencia Hidráulica
        La potencia útil entregada al fluido:
        
        $$P_{hidráulica} = \\rho \\cdot g \\cdot Q \\cdot H$$
        
        Donde:
        - $\\rho$ = Densidad agua (1000 kg/m³)
        - $g$ = Gravedad (9.80665 m/s²)
        - $Q$ = Caudal (m³/s)
        - $H$ = Altura total (m)
        
        #### Eficiencia de la Bomba
        Modelo parabólico centrado en el BEP:
        
        $$\\eta(Q) = \\eta_{max} \\cdot \\left[1 - \\left(\\frac{Q - Q_{BEP}}{Q_{BEP}}\\right)^2\\right]$$
        
        #### Potencia al Eje
        Potencia mecánica requerida:
        
        $$P_{eje} = \\frac{P_{hidráulica}}{\\eta}$$
        
        En kW:
        
        $$P_{eje}[kW] = \\frac{\\rho \\cdot g \\cdot Q \\cdot H}{1000 \\cdot \\eta}$$
        
        #### Potencia del Motor
        Incluyendo factor de seguridad:
        
        $$P_{motor} = P_{eje} \\cdot F_s$$
        
        Típicamente $F_s = 1.15$ (15% seguridad)
        
        #### Costo Energético
        Costo por unidad de volumen bombeado:
        
        $$C_{unitario} = \\frac{P_{eje} \\cdot T_{electricidad}}{Q \\cdot 3600}$$
        
        Donde $T_{electricidad}$ es la tarifa en USD/kWh
        
        ---
        
        #### 💰 Análisis Económico
        - **Eficiencia Alta**: Menor consumo eléctrico
        - **Costo Operativo**: Proporcional a potencia y tiempo
        - **VFD**: Ahorro cúbico según ley de afinidad
        - **ROI**: Inversión vs ahorro mensual
        """)

def render_theory_column_tanque():
    """Renderiza teoría para tab Simulación de Tanque"""
    with st.expander("📐 Fundamentos Teóricos", expanded=False):
        st.markdown("""
        #### Método de Rippl
        Balance de masa horario:
        
        $$\\Delta V_h = (Q_{entrada} - Q_{demanda}) \\cdot \\Delta t$$
        
        $$V_{h+1} = V_h + \\Delta V_h$$
        
        #### Almacenamiento Activo
        Capacidad útil para compensar variaciones:
        
        $$V_{activo} = \\max(\\sum \\Delta V) - \\min(\\sum \\Delta V)$$
        
        #### Capacidad Total
        Incluyendo reserva mínima:
        
        $$V_{total} = \\frac{V_{activo}}{1 - \\alpha}$$
        
        Donde $\\alpha$ = Nivel mínimo (%)
        
        #### Curva de Demanda
        Factor horario para cada hora $i$:
        
        $$Q_{demanda}(i) = Q_{diseño} \\cdot f_i$$
        
        Con $\\sum_{i=1}^{24} f_i = 24$ (promedio = 1.0)
        
        #### Ciclo de Bombeo
        Porcentaje de tiempo en operación:
        
        $$\\text{Ciclo} = \\frac{\\text{Horas ON}}{\\text{Horas Total}} \\times 100\\%$$
        
        ---
        
        #### 🔧 Criterios de Diseño
        - **Ciclo < 40%**: Posible sobredimensionamiento
        - **Ciclo > 80%**: Bomba muy pequeña o tanque insuficiente
        - **Ciclo 40-70%**: Rango óptimo de operación
        - **Reserva**: Mínimo 20-30% para emergencias
        
        #### 📊 Simulación Dinámica
        Permite:
        - Validar dimensionamiento de tanque
        - Prever arranques/paradas
        - Optimizar costos operativos
        - Detectar insuficiencias de capacidad
        """)

def render_theory_column_resumen():
    """Renderiza teoría para tab Resumen Ejecutivo"""
    pot_motor_app = st.session_state.get('potencia_motor_final_kw', 0)
    pot_motor_app_hp = st.session_state.get('potencia_motor_final_hp', 0)
    
    with st.expander("📐 Fundamentos Teóricos", expanded=False):
        teoria_text = """
        #### Ecuaciones Completas del Sistema
        
        **1. Altura Total:**
        
        $$H_{{total}} = H_{{estática}} + h_f + h_{{accesorios}}$$
        
        **2. Potencia Hidráulica:**
        
        $$P_{{hid}} = \\frac{{\\rho \\cdot g \\cdot Q \\cdot H}}{{1000}}$$ [kW]
        
        **3. Potencia Motor (Individual):**
        
        $$P_{{motor}} = \\frac{{P_{{hid}}}}{{\\eta_{{bomba}}}} \\cdot F_s$$
        
        **4. Potencia Total Sistema:**
        
        $$P_{{total}} = P_{{motor}} \\cdot N_{{bombas}}$$
        
        ---
        
        #### 🔗 Relación con Análisis Principal
        
        **Potencia Motor (Análisis Principal):**
        - $P_{{motor}} = {pot_kw:.2f}$ kW ({pot_hp:.2f} HP)
        
        **Potencia Motor (Simulador):**
        - Calculada con eficiencia en punto de operación
        - Considera curva parabólica completa
        - Incluye análisis dinámico
        
        **Diferencias:**
        - Análisis principal: Usa punto de diseño fijo
        - Simulador: Considera punto de operación real (intersección curvas)
        - Ambos deben ser consistentes dentro del 5-10%
        
        ---
        
        #### 📊 Metodología de Validación
        
        1. **Verificar Consistencia:**
           $$\\left|\\frac{{P_{{sim}} - P_{{app}}}}{{P_{{app}}}}\\right| < 0.10$$
        
        2. **Analizar Discrepancias:**
           - Diferencia en eficiencia asumida
           - Pérdidas menores consideradas
           - Factor de seguridad aplicado
        
        3. **Criterio de Aceptación:**
           - < 5%: Excelente concordancia
           - 5-10%: Consistente
           - > 10%: Revisar parámetros
        
        ---
        
        #### 💡 Recomendaciones
        - Usar simulador para optimización fina
        - Validar con catálogos de fabricantes
        - Considerar variaciones de demanda
        - Incluir costos de ciclo de vida
        """.format(pot_kw=pot_motor_app, pot_hp=pot_motor_app_hp)
        
        st.markdown(teoria_text)

def render_simulation_tab():
    """Renderiza la pestaña de Simulación Operativa"""
    st.header("📈 Simulación Dinámica y Optimización Energética")
    
    # Verificar datos mínimos
    datos_ok, missing = verificar_datos_minimos()
    
    if not datos_ok:
        st.warning("⚠️ **Datos insuficientes para simulación**")
        st.info("Complete primero los siguientes datos en la pestaña **'1. Datos de Entrada'**:")
        for item in missing:
            st.markdown(f"- {item}")
        return
    
    # Sidebar con parámetros adicionales
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Parámetros de Simulación")
    
    rpm_app = st.session_state.get('rpm', 3500)
    st.sidebar.markdown(f"**RPM Sistema:** {rpm_app}")
    
    simulation_days = st.sidebar.number_input(
        "Días de Simulación",
        min_value=1,
        max_value=30,
        value=1,
        step=1,
        key="sim_days",
        help="Número de días consecutivos a simular"
    )
    
    col_tank1, col_tank2 = st.sidebar.columns(2)
    with col_tank1:
        initial_tank_perc = st.number_input(
            "Nivel Inicial (%)",
            min_value=0,
            max_value=100,
            value=80,
            step=5,
            key="sim_initial_tank_perc",
            help="Nivel de llenado inicial del tanque"
        )
    with col_tank2:
        min_tank_perc = st.number_input(
            "Nivel Mínimo (%)",
            min_value=0,
            max_value=99,
            value=30,
            step=5,
            key="sim_min_tank_perc",
            help="Reserva mínima de seguridad"
        )
    
    tank_capacity = st.sidebar.number_input(
        "Capacidad Tanque (m³) [Opcional]",
        min_value=0.0,
        value=0.0,
        step=10.0,
        key="sim_tank_capacity_input",
        help="Dejar en 0 para cálculo automático"
    )
    
    if tank_capacity > 0:
        st.session_state.sim_tank_capacity_m3 = tank_capacity
    else:
        st.session_state.sim_tank_capacity_m3 = None
    
    tank_round = st.sidebar.number_input(
        "Redondeo Tanque (múltiplo de m³)",
        min_value=1.0,
        max_value=500.0,
        value=50.0,
        step=10.0,
        key="sim_tank_round_m3",
        help="El tanque se redondeará al múltiplo superior más cercano"
    )
    
    with st.sidebar.expander("📊 Curva de Demanda Horaria", expanded=False):
        st.caption("24 factores (uno por hora del día)")
        
        use_default = st.checkbox("Usar curva típica", value=True, key="sim_use_default_curve")
        
        if use_default:
            hourly_factors_list = default_hourly_factors()
            st.session_state.sim_hourly_factors = hourly_factors_list
            
            import plotly.graph_objects as go
            fig_preview = go.Figure()
            fig_preview.add_trace(go.Bar(
                x=list(range(24)),
                y=hourly_factors_list,
                marker_color='steelblue'
            ))
            fig_preview.update_layout(
                height=200,
                margin=dict(l=10, r=10, t=20, b=20),
                xaxis_title="Hora",
                yaxis_title="Factor",
                showlegend=False
            )
            st.plotly_chart(fig_preview, use_container_width=True, key="sim_preview_curve")
        else:
            hourly_text = st.text_area(
                "Factores (24 valores separados por coma)",
                value=",".join([str(f) for f in default_hourly_factors()]),
                height=100,
                key="sim_hourly_text"
            )
            
            try:
                hourly_factors_list = [float(x.strip()) for x in hourly_text.split(',')]
                if len(hourly_factors_list) != 24:
                    st.error(f"⚠️ Se requieren 24 valores. Ingresados: {len(hourly_factors_list)}")
                    hourly_factors_list = default_hourly_factors()
                st.session_state.sim_hourly_factors = hourly_factors_list
            except:
                st.error("⚠️ Formato inválido. Use números separados por coma.")
                hourly_factors_list = default_hourly_factors()
                st.session_state.sim_hourly_factors = hourly_factors_list
    
    st.sidebar.markdown("---")
    
    simulator = crear_simulador()
    
    if simulator is None:
        st.error("⚠️ Error al crear el simulador. Verifique los datos de entrada.")
        return
    
    # Leer valores de operación de Análisis de Curvas
    q_op_100_lps = st.session_state.get('caudal_operacion', 0)
    h_op_100 = st.session_state.get('altura_operacion', 0)
    eff_op_100 = st.session_state.get('eficiencia_operacion', 0)
    power_op_100_hp = st.session_state.get('potencia_operacion', 0)
    power_op_100_kw = power_op_100_hp * 0.746 if power_op_100_hp > 0 else 0
    
    
    n_bombas = st.session_state.get('num_bombas', 1)
    power_total_100_kw = power_op_100_kw * n_bombas
    
    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
    
    with col_info1:
        st.metric("Caudal Total", f"{q_op_100_lps:.1f} L/s")
    
    with col_info2:
        st.metric("Altura Operación", f"{h_op_100:.1f} m")
    
    with col_info3:
        st.metric("Potencia Total", f"{power_total_100_kw:.1f} kW")
    
    with col_info4:
        st.metric("Eficiencia", f"{eff_op_100:.1f}%")
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔄 Curvas y Operación",
        "⚡ Eficiencia y Costos",
        "💧 Simulación de Tanque",
        "📊 Resumen Ejecutivo"
    ])
    
    # Tab 1: LEER VALORES DIRECTAMENTE DE SESSION_STATE (MISMO CÁLCULO QUE ANÁLISIS)
    with tab1:
        st.subheader("Curvas del Sistema y Bomba")
        
        # Leer curva_inputs (las curvas REALES)
        curva_inputs = st.session_state.get('curva_inputs', {})
        ajuste_tipo = st.session_state.get('ajuste_tipo', 'Cuadrática (2do grado)')
        rpm_percentage = st.session_state.get('rpm_percentage', 100.0)
        
        # Si hay curvas disponibles, usarlas
        if curva_inputs and 'bomba' in curva_inputs and len(curva_inputs['bomba']) >= 2:
            puntos_bomba = curva_inputs['bomba']
            puntos_sistema = curva_inputs.get('sistema', [])
            puntos_rend = curva_inputs.get('rendimiento', [])
            puntos_pot = curva_inputs.get('potencia', [])
            
            # Grado del ajuste
            grado = 1 if ajuste_tipo == "Lineal" else 2 if ajuste_tipo == "Cuadrática (2do grado)" else 3
            
            # Ajustar curvas
            if len(puntos_sistema) >= 2:
                x_sis = np.array([pt[0] for pt in puntos_sistema])
                y_sis = np.array([pt[1] for pt in puntos_sistema])
                coef_sis = np.polyfit(x_sis, y_sis, grado)
            else:
                # Generar curva sistema from simulator
                x_sis = simulator.q_range * simulator.n_parallel * 1000
                y_sis = simulator.system_head(simulator.q_range * simulator.n_parallel)
                coef_sis = np.polyfit(x_sis, y_sis, grado)
            
            x_bom = np.array([pt[0] for pt in puntos_bomba])
            y_bom = np.array([pt[1] for pt in puntos_bomba])
            coef_bom = np.polyfit(x_bom, y_bom, grado)
            
            # ========== CÁLCULO 100% RPM - CALCULAR DIRECTAMENTE (REPLICAR ANALYSIS.PY) ==========
            # NO usar session_state, calcular directamente desde las curvas
            # Esto replica EXACTAMENTE analysis.py líneas 351-366
            
            # Calcular intersección para 100%
            def intersection_func_100(q):
                return np.polyval(coef_bom, q) - np.polyval(coef_sis, q)
            
            try:
                from scipy.optimize import fsolve
                q_op_100_calc = fsolve(intersection_func_100, 10.0)[0]  # Usar guess genérico
                h_op_100_calc = np.polyval(coef_sis, q_op_100_calc)
                
                # Interpolar rendimiento DIRECTAMENTE (igual que analysis.py línea 359)
                eff_op_100_calc = 0
                if len(puntos_rend) >= 2:
                    x_rend = np.array([pt[0] for pt in puntos_rend])
                    y_rend = np.array([pt[1] for pt in puntos_rend])
                    eff_op_100_calc = float(np.interp(q_op_100_calc, x_rend, y_rend))
                
                # Interpolar potencia DIRECTAMENTE (igual que analysis.py línea 366)
                power_op_100_hp_calc = 0
                if len(puntos_pot) >= 2:
                    x_pot = np.array([pt[0] for pt in puntos_pot])
                    y_pot = np.array([pt[1] for pt in puntos_pot])
                    power_op_100_hp_calc = float(np.interp(q_op_100_calc, x_pot, y_pot))
                
                # USAR valores calculados (NO de session_state)
                q_op_100_lps = q_op_100_calc
                h_op_100 = h_op_100_calc
                eff_op_100 = eff_op_100_calc
                power_op_100_hp = power_op_100_hp_calc
                power_op_100_kw = power_op_100_hp * 0.746
                power_total_100_kw = power_op_100_kw * n_bombas
                
            except Exception as e:
                # Fallback: usar valores de session_state si el cálculo falla
                pass  # Variables ya están definidas desde líneas 445-448
            
            # ========== CÁLCULO VFD ==========
            speed_ratio = rpm_percentage / 100.0
            x_bom_vfd = x_bom * speed_ratio
            y_bom_vfd = y_bom * speed_ratio**2
            coef_bom_vfd = np.polyfit(x_bom_vfd, y_bom_vfd, grado)
            
            def intersection_func_vfd(q):
                return np.polyval(coef_bom_vfd, q) - np.polyval(coef_sis, q)
            
            try:
                # Calcular intersección para VFD
                q_op_vfd_lps = fsolve(intersection_func_vfd, q_op_100_lps * speed_ratio)[0]
                h_op_vfd = np.polyval(coef_sis, q_op_vfd_lps)
                
                # CRÍTICO: Interpolar DIRECTAMENTE en puntos originales (NO en curvas VFD)
                # Exactamente como lo hace analysis.py línea 359
                if len(puntos_rend) >= 2:
                    x_rend = np.array([pt[0] for pt in puntos_rend])
                    y_rend = np.array([pt[1] for pt in puntos_rend])
                    # Interpolar en curva ESCALADA de rendimiento (X*speed_ratio, Y sin cambio)
                    x_rend_vfd = x_rend * speed_ratio
                    eff_vfd = float(np.interp(q_op_vfd_lps, x_rend_vfd, y_rend))
                else:
                    eff_vfd = eff_op_100
                
                # Interpolar potencia
                if len(puntos_pot) >= 2:
                    x_pot = np.array([pt[0] for pt in puntos_pot])
                    y_pot = np.array([pt[1] for pt in puntos_pot])
                    # Interpolar en curva ESCALADA de potencia (X*speed_ratio, Y*speed_ratio³)
                    x_pot_vfd = x_pot * speed_ratio
                    y_pot_vfd = y_pot * speed_ratio**3
                    power_vfd_hp = float(np.interp(q_op_vfd_lps, x_pot_vfd, y_pot_vfd))
                    power_vfd_kw = power_vfd_hp * 0.746
                else:
                    power_vfd_hp = power_op_100_hp * speed_ratio**3
                    power_vfd_kw = power_vfd_hp * 0.746
                    
            except Exception as e:
                # Fallback
                q_op_vfd_lps = q_op_100_lps * speed_ratio
                h_op_vfd = h_op_100 * speed_ratio**2
                eff_vfd = eff_op_100
                power_vfd_hp = power_op_100_hp * speed_ratio**3
                power_vfd_kw = power_vfd_hp * 0.746
            
            power_total_vfd_kw = power_vfd_kw * n_bombas
            
            col_t1_1, col_t1_2, col_t1_3 = st.columns([1.2, 1.2, 0.8])
            
            with col_t1_1:
                # Gráfico Sistema vs Bomba 100%
                import plotly.graph_objects as go
                fig_system = go.Figure()
                
                # Curva sistema (ajustada)
                x_plot = np.linspace(0, max(x_sis.max(), x_bom.max()) * 1.5, 200)
                y_sis_plot = np.polyval(coef_sis, x_plot)
                fig_system.add_trace(go.Scatter(
                    x=x_plot, y=y_sis_plot,
                    mode='lines', name='Sistema',
                    line=dict(color='red', width=2)
                ))
                
                # Curva bomba (ajustada)
                y_bom_plot = np.polyval(coef_bom, x_plot)
                fig_system.add_trace(go.Scatter(
                    x=x_plot, y=y_bom_plot,
                    mode='lines', name='Bomba 100%',
                    line=dict(color='blue', width=2)
                ))
                
                # Punto de operación
                fig_system.add_trace(go.Scatter(
                    x=[q_op_100_lps],
                    y=[h_op_100],
                    mode='markers', name='Operación',
                    marker=dict(size=12, color='orange', symbol='star')
                ))
                
                fig_system.update_layout(
                    xaxis_title='Caudal (L/s)',
                    yaxis_title='Altura (m)',
                    height=400,
                    showlegend=True,
                    legend=dict(orientation="h", y=0.15, xanchor="center", x=0.5),
                    margin=dict(l=60, r=20, t=40, b=100),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_system, use_container_width=True, key="sim_system_vs_pump")
            
            with col_t1_2:
                # Gráfico VFD
                fig_vfd = go.Figure()
                
                # Curva sistema
                fig_vfd.add_trace(go.Scatter(
                    x=x_plot, y=y_sis_plot,
                    mode='lines', name='Sistema',
                    line=dict(color='red', width=2)
                ))
                
                # Curva bomba 100% (SIEMPRE VISIBLE para comparar)
                fig_vfd.add_trace(go.Scatter(
                    x=x_plot, y=y_bom_plot,
                    mode='lines', name='Bomba 100%',
                    line=dict(color='blue', width=2, dash='dot')
                ))
                
                # Curva bomba VFD
                y_bom_vfd_plot = np.polyval(coef_bom_vfd, x_plot)
                fig_vfd.add_trace(go.Scatter(
                    x=x_plot, y=y_bom_vfd_plot,
                    mode='lines', name=f'Bomba {rpm_percentage:.1f}%',
                    line=dict(color='green', width=3)
                ))
                
                # Punto VFD
                fig_vfd.add_trace(go.Scatter(
                    x=[q_op_vfd_lps],
                    y=[h_op_vfd],
                    mode='markers', name='Operación VFD',
                    marker=dict(size=12, color='purple', symbol='circle')
                ))
                
                # Punto 100% (SIEMPRE VISIBLE para comparar)
                fig_vfd.add_trace(go.Scatter(
                    x=[q_op_100_lps],
                    y=[h_op_100],
                    mode='markers', name='Punto Nominal (100%)',
                    marker=dict(size=10, color='red', symbol='diamond')
                ))
                
                fig_vfd.update_layout(
                    title=f'Análisis VFD ({rpm_percentage:.1f}% RPM)',
                    xaxis_title='Caudal (L/s)',
                    yaxis_title='Altura (m)',
                    height=400,
                    showlegend=True,
                    legend=dict(orientation="h", y=-0.15, xanchor="center", x=0.5),
                    margin=dict(l=60, r=20, t=60, b=100),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_vfd, use_container_width=True, key="sim_vfd_dynamic")
                
                # Slider debajo (con callback para evitar error de session_state)
                def update_rpm():
                    """Callback para actualizar rpm_percentage"""
                    st.session_state['rpm_percentage'] = st.session_state['sim_rpm_vfd_slider']
                
                rpm_vfd_slider_value = st.slider(
                    "Ajustar % RPM VFD",
                    min_value=50.0,
                    max_value=100.0,
                    value=float(rpm_percentage),
                    step=0.5,
                    key="sim_rpm_vfd_slider",
                    on_change=update_rpm
                )

            
            with col_t1_3:
                render_theory_column_curvas()
            
            st.markdown("---")
            
            # Métricas - USAR VALORES EXACTOS DE ANÁLISIS DE CURVAS
            col_op1, col_op2, col_op3 = st.columns(3)
            
            with col_op1:
                st.markdown("#### 🎯 Operación (100% RPM)")
                col_op1_1, col_op1_2 = st.columns(2)
                with col_op1_1:
                    st.metric("Q Total", f"{q_op_100_lps:.2f} L/s")
                    st.metric("H", f"{h_op_100:.2f} m")
                with col_op1_2:
                    power_total_100_hp = power_total_100_kw / 0.746 if power_total_100_kw > 0 else 0
                    st.metric("P Total", f"{power_total_100_kw:.2f} kW")
                    st.caption(f"({power_total_100_hp:.2f} HP)")
                    st.metric("η", f"{eff_op_100:.2f}%")
            
            with col_op2:
                st.markdown(f"#### 🎛️ Operación VFD ({rpm_percentage:.1f}%)")
                
                col_vfd1, col_vfd2 = st.columns(2)
                with col_vfd1:
                    st.metric("Q Total", f"{q_op_vfd_lps:.2f} L/s")
                    st.metric("H", f"{h_op_vfd:.2f} m")
                with col_vfd2:
                    power_total_vfd_hp = power_total_vfd_kw / 0.746 if power_total_vfd_kw > 0 else 0
                    st.metric("P Total", f"{power_total_vfd_kw:.2f} kW")
                    st.caption(f"({power_total_vfd_hp:.2f} HP)")
                    st.metric("η", f"{eff_vfd:.2f}%")
            
            with col_op3:
                st.markdown(f"#### 💰 Ahorro")
                
                ahorro_kw = power_total_100_kw - power_total_vfd_kw
                ahorro_hp = ahorro_kw / 0.746 if ahorro_kw > 0 else ahorro_kw * 0.746
                ahorro_pct = (ahorro_kw / power_total_100_kw * 100) if power_total_100_kw > 0 else 0
                
                st.metric(
                    "Δ Potencia", 
                    f"{ahorro_kw:.2f} kW",
                    delta=f"{ahorro_pct:.1f}%"
                )
                st.caption(f"({ahorro_hp:.2f} HP)")
                st.caption(f"""
                100%: {power_total_100_kw:.2f} kW  
                VFD: {power_total_vfd_kw:.2f} kW
                """)
        else:
            st.warning("⚠️ No hay curvas disponibles. Cargue primero las curvas en 'Análisis de Curvas'.")
    
    # Tab 2: Eficiencia y Costos
    with tab2:
        st.subheader("Análisis de Eficiencia y Costos Operacionales")
        
        col_cost_input1, col_cost_input2 = st.columns([2, 2])
        with col_cost_input1:
            electricity_cost = st.number_input(
                "💵 Costo Energía (USD/kWh)",
                min_value=0.01,
                max_value=1.0,
                value=0.12,
                step=0.01,
                key="sim_electricity_cost",
                help="Tarifa eléctrica para calcular costos operacionales"
            )
        with col_cost_input2:
            st.info(f"**Tarifa actual:** ${electricity_cost:.3f}/kWh")
        
        st.markdown("---")
        
        col_t2_1, col_t2_2, col_t2_3 = st.columns([1.2, 1.2, 0.8])
        
        with col_t2_1:
            fig_eff = simulator.plot_efficiency_vs_flow()
            st.plotly_chart(fig_eff, use_container_width=True, key="sim_efficiency")
        
        with col_t2_2:
            fig_cost = simulator.plot_cost_per_m3_vs_flow()
            st.plotly_chart(fig_cost, use_container_width=True, key="sim_cost_per_m3")
        
        with col_t2_3:
            render_theory_column_eficiencia()
        
        st.markdown("---")
        
        st.markdown("#### 💰 Costos Operacionales")
        
        hourly_cost, total_cost, cost_per_m3 = simulator.energy_costs()
        
        col_cost1, col_cost2, col_cost3 = st.columns(3)
        
        with col_cost1:
            st.metric("Costo Total", f"${total_cost:.2f}")
            st.caption(f"Para {simulation_days} día(s)")
        
        with col_cost2:
            st.metric("Costo Unitario", f"${cost_per_m3:.4f}/m³")
        
        with col_cost3:
            monthly_cost = total_cost * 30 / simulation_days
            st.metric("Proyección Mensual", f"${monthly_cost:.2f}")
    
    # Tab 3: Simulación de Tanque
    with tab3:
        st.subheader("Simulación Operacional del Sistema")
        
        col_t3_1, col_t3_2, col_t3_3 = st.columns([1.2, 1.2, 0.8])
        
        with col_t3_1:
            fig_tank = simulator.plot_tank_volume()
            st.plotly_chart(fig_tank, use_container_width=True, key="sim_tank_volume")
        
        with col_t3_2:
            fig_demand = simulator.plot_demand_vs_inflow()
            st.plotly_chart(fig_demand, use_container_width=True, key="sim_demand_inflow")
        
        with col_t3_3:
            render_theory_column_tanque()
        
        st.markdown("---")
        
        st.markdown("#### 🏗️ Dimensionamiento del Tanque")
        
        col_tank1, col_tank2, col_tank3, col_tank4 = st.columns(4)
        
        with col_tank1:
            st.metric("Capacidad Calculada", f"{simulator.tank_capacity_m3:.0f} m³")
        
        with col_tank2:
            active_storage = simulator.tank_capacity_m3 * (1 - simulator.min_tank_level_perc)
            st.metric("Almacenamiento Activo", f"{active_storage:.0f} m³")
        
        with col_tank3:
            reserve = simulator.tank_capacity_m3 * simulator.min_tank_level_perc
            st.metric("Reserva Mínima", f"{reserve:.0f} m³")
        
        with col_tank4:
            pump_on_hours = np.sum(simulator.pump_on_hourly)
            duty_cycle = (pump_on_hours / len(simulator.pump_on_hourly)) * 100
            st.metric("Ciclo de Bombeo", f"{duty_cycle:.1f}%")
            st.caption(f"{pump_on_hours:.0f}/{len(simulator.pump_on_hourly)} horas")
    
    # Tab 4: Resumen Ejecutivo
    with tab4:
        st.subheader("Resumen Ejecutivo del Análisis")
        
        col_res1, col_res2, col_res3 = st.columns([1.2, 1.2, 0.8])
        
        with col_res1:
            st.markdown("### 🎯 Configuración del Sistema")
            
            config_data = {
                "Parámetro": [
                    "Caudal de Diseño",
                    "Altura Estática",
                    "Número de Bombas",
                    "Tubería (L × Ø)",
                    "Material (C H-W)",
                    "Eficiencia Pico",
                    "Costo Energía"
                ],
                "Valor": [
                    f"{simulator.q_design * 1000:.2f} L/s ({simulator.q_design * 3600:.1f} m³/h)",
                    f"{simulator.h_static:.1f} m",
                    f"{simulator.n_parallel} bomba(s) en paralelo",
                    f"{simulator.pipe_length_m:.0f} m × {simulator.pipe_diameter_m*1000:.0f} mm",
                    f"C = {simulator.hw_c}",
                    f"{simulator.eff_peak * 100:.1f}%",
                    f"${simulator.electricity_cost:.3f}/kWh"
                ]
            }
            
            df_config = pd.DataFrame(config_data)
            st.dataframe(df_config, use_container_width=True, hide_index=True)
        
        with col_res2:
            st.markdown("### 📊 Resultados Clave")
            
            results_data = {
                "Métrica": [
                    "Caudal Total",
                    "Altura Operación",
                    "Eficiencia",
                    "Potencia Total",
                    "Capacidad Tanque",
                    "Ciclo Bombeo"
                ],
                "Valor": [
                    f"{q_op_100_lps:.2f} L/s",
                    f"{h_op_100:.2f} m",
                    f"{eff_op_100:.2f}%",
                    f"{power_total_100_kw:.2f} kW",
                    f"{simulator.tank_capacity_m3:.0f} m³",
                    f"{duty_cycle:.1f}%"
                ]
            }
            
            df_results = pd.DataFrame(results_data)
            st.dataframe(df_results, use_container_width=True, hide_index=True)
        
        with col_res3:
            render_theory_column_resumen()
        
        st.markdown("---")
        
        st.markdown("### 💡 Recomendaciones")
        
        recommendations = []
        
        if eff_op_100 < 70:
            recommendations.append("⚠️ **Eficiencia Baja**: Considerar bomba más eficiente o ajustar punto de operación.")
        elif eff_op_100 >= 75:
            recommendations.append("✅ **Eficiencia Adecuada**: Sistema opera en rango aceptable.")
        
        if duty_cycle > 80:
            recommendations.append("⚠️ **Ciclo Alto**: Bomba opera >80% del tiempo. Considerar tanque más grande o bomba adicional.")
        elif duty_cycle < 40:
            recommendations.append("ℹ️ **Ciclo Bajo**: Sistema sobredimensionado. Posible optimización de capacidad.")
        
        if recommendations:
            for rec in recommendations:
                st.markdown(f"- {rec}")
        else:
            st.success("✅ Sistema diseñado adecuadamente. No se detectan optimizaciones críticas.")
