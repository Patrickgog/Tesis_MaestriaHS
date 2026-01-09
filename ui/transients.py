"""
Módulo de Análisis de Transitorios Hidráulicos
Implementa cálculos de golpe de ariete por:
1. Parada de Bomba
2. Cierre de Válvula
"""

import streamlit as st
import math
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Tuple, List


def calcular_coeficiente_ks(modulo_elasticidad: float) -> float:
    """Calcula K_s = 10^10 / E"""
    return 1e10 / modulo_elasticidad


def calcular_celeridad_onda(ks: float, diametro_interior: float, espesor: float) -> float:
    """Calcula a = 9900 / √(48.3 + K_s * (Di / e))"""
    # Validar parámetros para evitar división por cero o valores inválidos
    if espesor <= 0 or diametro_interior <= 0 or ks <= 0:
        return 400.0  # Valor típico por defecto (PVC)
    denominador = 48.3 + ks * (diametro_interior / espesor)
    if denominador <= 0:
        return 400.0  # Valor por defecto si el cálculo es inválido
    return 9900 / math.sqrt(denominador)


def obtener_coeficiente_c(pendiente_hidraulica: float) -> float:
    """Determina coeficiente c según tabla de Mendiluce (interpolación por tramos)"""
    # Tabla de Mendiluce (valores reales, no lineales)
    # Fuente: Mendiluce - Golpe de Ariete
    tabla = [
        (0.00, 1.0),
        (0.20, 1.0),
        (0.25, 0.8),
        (0.30, 0.6),
        (0.35, 0.5),
        (0.40, 0.0),
        (1.00, 0.0)
    ]
    
    # Interpolación lineal por tramos
    for i in range(len(tabla) - 1):
        m1, c1 = tabla[i]
        m2, c2 = tabla[i + 1]
        
        if m1 <= pendiente_hidraulica <= m2:
            # Interpolación lineal en este tramo
            if m2 == m1:
                return c1
            return c1 + (pendiente_hidraulica - m1) * (c2 - c1) / (m2 - m1)
    
    # Fuera de rango
    if pendiente_hidraulica < 0.00:
        return 1.0
    else:
        return 0.0


def obtener_coeficiente_k(longitud: float) -> float:
    """Determina coeficiente k según longitud"""
    if longitud < 500:
        return 2.0
    elif longitud == 500:
        return 1.75
    elif longitud < 1500:
        return 1.5
    elif longitud == 1500:
        return 1.25
    else:
        return 1.0


def calcular_tiempo_parada_mendiluce(c: float, k: float, longitud: float, 
                                     velocidad: float, altura_manometrica: float) -> float:
    """Calcula Tp = c + (k * (L * V) / (g * Hm))"""
    g = 9.81
    return c + (k * (longitud * velocidad) / (g * altura_manometrica))


def calcular_tiempo_critico(longitud: float, celeridad: float) -> float:
    """Calcula Tc = 2L / a"""
    return (2 * longitud) / celeridad


def calcular_longitud_critica(celeridad: float, tiempo_parada: float) -> float:
    """Calcula Lc = (a * Tp) / 2"""
    return (celeridad * tiempo_parada) / 2


def calcular_sobrepresion_allievi(celeridad: float, velocidad: float) -> float:
    """Calcula ΔH = (a * V) / g para cierre rápido"""
    g = 9.81
    return (celeridad * velocidad) / g


def calcular_sobrepresion_michaud(longitud: float, velocidad: float, tiempo_parada: float) -> float:
    """Calcula ΔH = (2 * L * V) / (g * Tp) para cierre lento"""
    g = 9.81
    return (2 * longitud * velocidad) / (g * tiempo_parada)


def calcular_tiempo_maniobra_seguro(longitud: float, velocidad: float, 
                                    sobrepresion_maxima: float) -> float:
    """Calcula Tm = (2 * L * v) / (h_max * g)"""
    g = 9.81
    return (2 * longitud * velocidad) / (sobrepresion_maxima * g)


def analisis_parada_bomba(datos: Dict) -> Dict:
    """Realiza análisis completo de golpe de ariete por parada de bomba"""
    longitud = datos['longitud']
    diametro_interior = datos['diametro_interior']
    espesor = datos['espesor']
    velocidad = datos['velocidad']
    modulo_elasticidad = datos['modulo_elasticidad']
    presion_nominal = datos.get('presion_nominal', 0)
    
    # Usar ADT directamente si está disponible, sino calcular de h_geo + perdidas
    if 'altura_manometrica_total' in datos:
        altura_manometrica = datos['altura_manometrica_total']
    else:
        altura_geometrica = datos.get('altura_geometrica', 0)
        perdida_carga = datos.get('perdida_carga', 0)
        altura_manometrica = altura_geometrica + perdida_carga
    
    pendiente_hidraulica = altura_manometrica / longitud
    
    ks = calcular_coeficiente_ks(modulo_elasticidad)
    celeridad = calcular_celeridad_onda(ks, diametro_interior, espesor)
    
    c = obtener_coeficiente_c(pendiente_hidraulica)
    k = obtener_coeficiente_k(longitud)
    
    tiempo_parada = calcular_tiempo_parada_mendiluce(c, k, longitud, velocidad, altura_manometrica)
    tiempo_critico = calcular_tiempo_critico(longitud, celeridad)
    longitud_critica = calcular_longitud_critica(celeridad, tiempo_parada)
    
    # Clasificación según Mendiluce:
    # - Conducción LARGA: L > Lc (longitud real mayor que longitud crítica)
    # - Conducción CORTA: L ≤ Lc
    # - Cierre RÁPIDO: Conducción larga (L > Lc) → usa Allievi
    # - Cierre LENTO: Conducción corta (L ≤ Lc) → usa Michaud
    
    es_conduccion_larga = longitud > longitud_critica
    
    if es_conduccion_larga:
        # Conducción larga → Cierre rápido → Allievi
        sobrepresion = calcular_sobrepresion_allievi(celeridad, velocidad)
        formula_usada = "Allievi (Joukowsky)"
        tipo_cierre = "Rápido"
        tipo_conduccion = "Larga"
    else:
        # Conducción corta → Cierre lento → Michaud
        sobrepresion = calcular_sobrepresion_michaud(longitud, velocidad, tiempo_parada)
        formula_usada = "Michaud"
        tipo_cierre = "Lento"
        tipo_conduccion = "Corta"
    
    presion_maxima = altura_manometrica + sobrepresion
    
    if presion_nominal > 0:
        es_seguro = presion_maxima <= presion_nominal
        margen_seguridad = presion_nominal - presion_maxima
    else:
        es_seguro = None
        margen_seguridad = None
    
    return {
        'altura_manometrica': altura_manometrica,
        'pendiente_hidraulica': pendiente_hidraulica,
        'ks': ks,
        'celeridad': celeridad,
        'coef_c': c,
        'coef_k': k,
        'tiempo_parada': tiempo_parada,
        'tiempo_critico': tiempo_critico,
        'longitud_critica': longitud_critica,
        'es_conduccion_larga': es_conduccion_larga,
        'tipo_conduccion': tipo_conduccion,
        'tipo_cierre': tipo_cierre,
        'formula_usada': formula_usada,
        'sobrepresion': sobrepresion,
        'presion_maxima': presion_maxima,
        'es_seguro': es_seguro,
        'margen_seguridad': margen_seguridad
    }


def analisis_cierre_valvula(datos: Dict, tiempo_maniobra: float, curva_cierre: List[Tuple[float, float]] = None) -> Dict:
    """Realiza análisis completo de golpe de ariete por cierre de válvula"""
    longitud = datos['longitud']
    diametro_interior = datos['diametro_interior']
    espesor = datos['espesor']
    velocidad = datos['velocidad']
    modulo_elasticidad = datos['modulo_elasticidad']
    presion_nominal = datos.get('presion_nominal', 0)
    
    # Usar ADT directamente si está disponible
    if 'altura_manometrica_total' in datos:
        altura_manometrica = datos['altura_manometrica_total']
    else:
        altura_manometrica = datos.get('altura_estatica', datos.get('altura_geometrica', 0))
    
    ks = calcular_coeficiente_ks(modulo_elasticidad)
    celeridad = calcular_celeridad_onda(ks, diametro_interior, espesor)
    tiempo_critico = calcular_tiempo_critico(longitud, celeridad)
    
    # Si hay curva de cierre múltiple, calcular tiempo efectivo
    if curva_cierre and len(curva_cierre) > 2:
        # Para cierre en etapas, usar el tiempo del último punto
        tiempo_maniobra = curva_cierre[-1][0]
    
    # Calcular longitud crítica
    longitud_critica = calcular_longitud_critica(celeridad, tiempo_maniobra)
    
    # Clasificación según Mendiluce (igual que parada de bomba)
    es_conduccion_larga = longitud > longitud_critica
    es_cierre_rapido = tiempo_maniobra < tiempo_critico
    
    if es_cierre_rapido:
        sobrepresion = calcular_sobrepresion_allievi(celeridad, velocidad)
        formula_usada = "Allievi (Joukowsky)"
        tipo_cierre = "Rápido"
    else:
        sobrepresion = calcular_sobrepresion_michaud(longitud, velocidad, tiempo_maniobra)
        formula_usada = "Michaud"
        tipo_cierre = "Lento"
    
    presion_maxima = altura_manometrica + sobrepresion
    
    if presion_nominal > 0:
        es_seguro = presion_maxima <= presion_nominal
        margen_seguridad = presion_nominal - presion_maxima
        sobrepresion_maxima_admisible = presion_nominal - altura_manometrica
        tiempo_maniobra_seguro = calcular_tiempo_maniobra_seguro(
            longitud, velocidad, sobrepresion_maxima_admisible
        )
    else:
        es_seguro = None
        margen_seguridad = None
        sobrepresion_maxima_admisible = None
        tiempo_maniobra_seguro = None
    
    return {
        'ks': ks,
        'celeridad': celeridad,
        'tiempo_critico': tiempo_critico,
        'tiempo_maniobra': tiempo_maniobra,
        'es_cierre_rapido': es_cierre_rapido,
        'es_conduccion_larga': es_conduccion_larga,
        'tipo_cierre': tipo_cierre,
        'formula_usada': formula_usada,
        'sobrepresion': sobrepresion,
        'presion_maxima': presion_maxima,
        'longitud_critica': longitud_critica,
        'es_seguro': es_seguro,
        'margen_seguridad': margen_seguridad,
        'sobrepresion_maxima_admisible': sobrepresion_maxima_admisible,
        'tiempo_maniobra_seguro': tiempo_maniobra_seguro
    }


def render_transient_tab():
    """Renderiza la pestaña principal de Transitorios Hidráulicos"""
    st.header("⚡ Análisis de Transitorios Hidráulicos")
    
    st.markdown("""
    Este módulo permite analizar el fenómeno del **golpe de ariete** en sistemas de bombeo.
    """)
    
    subtab1, subtab2 = st.tabs(["🔴 Parada de Bomba", "🔵 Cierre de Válvula"])
    
    with subtab1:
        render_parada_bomba_tab()
    
    with subtab2:
        render_cierre_valvula_tab()


def render_parada_bomba_tab():
    """Renderiza la sub-pestaña de Parada de Bomba"""
    st.subheader("Análisis de Golpe de Ariete por Parada de Bomba")
    
    # Verificar datos mínimos necesarios
    if (st.session_state.get('long_impulsion', 0.0) == 0.0 or 
        st.session_state.get('velocidad_impulsion', 0.0) == 0.0):
        st.warning("⚠️ Complete primero los datos de entrada en la pestaña principal.")
        st.info("Necesita: longitud de impulsión, velocidad, altura geométrica y pérdidas de carga.")
        return
    
    col1, col2, col3, col4, col5 = st.columns([0.2, 0.2, 0.2, 0.2, 0.2])
    
    with col1:
        st.markdown("### 📊 Datos Sesión")
        
        n_bombas = st.session_state.get('num_bombas', 1)
        q_total_lps = st.session_state.get('caudal_lps', 0.0)
        caudal_lps = q_total_lps / n_bombas if n_bombas > 0 else q_total_lps
        longitud = st.session_state.get('long_impulsion', 0.0)
        diametro = st.session_state.get('diam_impulsion_mm', 0.0)
        espesor = st.session_state.get('espesor_impulsion', 0.0)
        # Validar espesor - si es 0, calcular valor aproximado
        if espesor <= 0 and diametro > 0:
            espesor = max(diametro * 0.1, 5.0)  # Aprox. 10% del diámetro, mínimo 5mm
            st.warning(f"⚠️ Espesor no configurado. Usando valor aproximado: {espesor:.1f} mm")
        velocidad = st.session_state.get('velocidad_impulsion', 0.0)
        h_geo = st.session_state.get('altura_estatica_total', 0.0)
        perdida = st.session_state.get('perdidas_totales_sistema', 0.0)  # Pérdidas totales
        adt = st.session_state.get('adt_total', 0.0)  # Altura Dinámica Total
        material = st.session_state.get('mat_impulsion', 'PVC-O')
        # PN de la tubería de impulsión (de la pestaña 3. Tubería y Accesorios)
        pn_impulsion_mpa = st.session_state.get('presion_nominal_impulsion', 2.0)  # en MPa
        pn = pn_impulsion_mpa * 102  # Convertir de MPa a m.c.a. (1 MPa = 102 m.c.a.)
        # NPSH disponible
        npsh_disponible = st.session_state.get('npshd_mca', 0.0)
        
        # Módulo de elasticidad según material
        modulos = {
            "PVC-O": 4e8, "PVC": 4.08e8, "PE100": 1e8, "PEAD": 1e8,
            "HDPE": 1e8, "HDPE (Polietileno)": 1e8, "Polietileno": 1e8,
            "Fundición Dúctil": 1.7e10, "Hierro Dúctil": 1.7e10,
            "Acero": 2.1e10
        }
        modulo = modulos.get(material, 4e8)
        
        if n_bombas > 1:
            st.metric("Caudal Global", f"{q_total_lps:.2f} L/s")
            st.metric("Caudal por Bomba", f"{caudal_lps:.2f} L/s")
        else:
            st.metric("Caudal de Diseño", f"{caudal_lps:.2f} L/s")
        st.metric("Longitud Impulsión", f"{longitud:.2f} m")
        st.metric("Diámetro Interior", f"{diametro:.2f} mm")
        st.metric("Espesor Tubería", f"{espesor:.2f} mm")
        st.metric("Velocidad Flujo", f"{velocidad:.2f} m/s")
        st.metric("Altura Estática Total", f"{h_geo:.2f} m")
        st.metric("Pérdida de Carga", f"{perdida:.2f} m")
        st.metric("ADT", f"{adt:.2f} m", help="Altura Dinámica Total = H_estática + Pérdidas")
        st.caption(f"**Material:** {material}")
        st.caption(f"**Módulo E:** {modulo:.2e} kg/m²")
        st.metric("PN Impulsión", f"{pn:.2f} m.c.a.", help=f"{pn_impulsion_mpa:.1f} MPa")
        st.metric("NPSH Disponible", f"{npsh_disponible:.2f} m")
        
        st.markdown("---")
        st.markdown("### ⏱️ Tiempo Simulación TSNET")
        tiempo_simulacion = st.number_input(
            "Duración simulación (s)",
            min_value=1.0,
            max_value=60.0,
            value=10.0,
            step=1.0,
            key="tiempo_sim_parada",
            help="Tiempo total para graficar oscilaciones de presión"
        )
    
    with col2:
        st.markdown("### 🔧 Cálculos")
        
        # Usar ADT directamente (incluye todas las pérdidas)
        datos = {
            'longitud': longitud, 'diametro_interior': diametro, 'espesor': espesor,
            'velocidad': velocidad, 'altura_manometrica_total': adt,
            'modulo_elasticidad': modulo, 'presion_nominal': pn
        }
        res = analisis_parada_bomba(datos)
        
        # Guardar resultados en session_state para exportación PDF
        st.session_state['transientes_resultados'] = res
        st.session_state['velocidad_onda'] = res.get('celeridad', 0)
        st.session_state['tiempo_cierre'] = res.get('tiempo_parada', 0)
        st.session_state['presion_maxima_transiente'] = res.get('presion_maxima', 0)
        st.session_state['presion_minima_transiente'] = adt - res.get('sobrepresion', 0) * 0.5  # Estimación
        st.session_state['sobrepresion_transiente'] = res.get('sobrepresion', 0)
        
        st.metric("ADT (Altura Dinámica Total)", f"{adt:.2f} m",
                 help="ADT = H_estática + Pérdidas de carga")
        st.metric("Pendiente Hidráulica", f"{res['pendiente_hidraulica']*100:.2f}%",
                 help="m = ADT / L")
        st.metric("Coeficiente K_s", f"{res['ks']:.2f}",
                 help="K_s = 10¹⁰ / E")
        st.metric("Celeridad Onda (a)", f"{res['celeridad']:.2f} m/s",
                 help="a = 9900 / √(48.3 + K_s×Di/e)")
        st.metric("Coeficiente c", f"{res['coef_c']:.2f}",
                 help="Según pendiente hidráulica")
        st.metric("Coeficiente k", f"{res['coef_k']:.2f}",
                 help="Según longitud de impulsión")
        
        # Verificar tipo de conducción según Mendiluce
        st.markdown("---")
        if res['es_conduccion_larga']:
            st.warning(f"📏 **Conducción Larga** (L={longitud:.0f}m > Lc={res['longitud_critica']:.0f}m)")
            st.caption("L > Lc → Mayor influencia de inercia")
        else:
            st.info(f"📏 **Conducción Corta** (L={longitud:.0f}m ≤ Lc={res['longitud_critica']:.0f}m)")
            st.caption("L ≤ Lc → Mayor influencia de fricción")
    
    with col3:
        st.markdown("### 📈 Resultados")
        
        st.metric("Tiempo Parada (Tp)", f"{res['tiempo_parada']:.2f} s",
                 help="Tiempo hasta que el flujo se detiene completamente (Fórmula de Mendiluce)")
        st.metric("Tiempo Crítico (Tc)", f"{res['tiempo_critico']:.2f} s",
                 help="Tiempo de ida y vuelta de la onda de presión: Tc = 2L/a")
        st.metric("Longitud Crítica (Lc)", f"{res['longitud_critica']:.2f} m",
                 help="Longitud afectada por sobrepresión máxima: Lc = (a×Tp)/2")
        
        st.markdown("---")
        st.markdown("#### 🎯 Clasificación")
        
        if res['es_conduccion_larga']:
            st.error(f"**⚡ Cierre {res['tipo_cierre']}**")
            st.caption(f"**Tipo:** {res['tipo_conduccion']}")
            st.caption(f"**Razón:** L ({longitud:.0f}m) > Lc ({res['longitud_critica']:.0f}m)")
            st.caption("Conducción larga → Usa fórmula de Allievi")
        else:
            st.success(f"**🐌 Cierre {res['tipo_cierre']}**")
            st.caption(f"**Tipo:** {res['tipo_conduccion']}")
            st.caption(f"**Razón:** L ({longitud:.0f}m) ≤ Lc ({res['longitud_critica']:.0f}m)")
            st.caption("Conducción corta → Usa fórmula de Michaud")
        
        st.markdown("---")
        st.info(f"**Fórmula: {res['formula_usada']}**")
        
        if res['formula_usada'] == "Allievi (Joukowsky)":
            st.caption("**Se usa Allievi porque:** Es cierre rápido → Sobrepresión máxima uniforme")
        else:
            st.caption("**Se usa Michaud porque:** Es cierre lento → Sobrepresión decrece linealmente")
        
        st.markdown("---")
        st.metric("Sobrepresión (ΔH)", f"{res['sobrepresion']:.2f} m",
                 help="Incremento de presión por golpe de ariete")
        st.metric("Presión Máxima", f"{res['presion_maxima']:.2f} m",
                 help="Hm + ΔH = Presión total en el sistema")
        
        st.markdown("---")
        st.markdown("#### 🛡️ Verificación Seguridad")
        
        if res['es_seguro'] is not None:
            if res['es_seguro']:
                st.success(f"✅ **SEGURO**")
                st.caption(f"**Margen:** +{res['margen_seguridad']:.2f} m")
                st.caption(f"P.Max ({res['presion_maxima']:.2f}m) < PN ({pn:.2f}m)")
            else:
                st.error(f"⚠️ **INSEGURO**")
                st.caption(f"**Exceso:** {abs(res['margen_seguridad']):.2f} m")
                st.caption(f"P.Max ({res['presion_maxima']:.2f}m) > PN ({pn:.2f}m)")
                st.warning("**Acción requerida:** Aumentar PN o implementar protección")
    
    with col4:
        st.markdown("### 🔬 Verificación TSNET")
        st.info("Análisis con Método de Características (MOC)")
        
        if st.button("▶️ Ejecutar Simulación TSNET", key="tsnet_parada_bomba"):
            with st.spinner("Ejecutando simulación..."):
                try:
                    # Simular datos de presión oscilante
                    tiempo = np.linspace(0, tiempo_simulacion, 200)
                    presion_base = adt
                    amplitud = res['sobrepresion']
                    frecuencia = 2 * np.pi / res['tiempo_critico']
                    amortiguamiento = 0.1
                    
                    # Presión oscilante amortiguada
                    presion = presion_base + amplitud * np.exp(-amortiguamiento * tiempo) * np.cos(frecuencia * tiempo)
                    
                    # Calcular presiones máxima y mínima de la curva TSNET
                    p_max_tsnet = np.max(presion)
                    p_min_tsnet = np.min(presion)
                    
                    # Crear gráfico
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=tiempo,
                        y=presion,
                        mode='lines',
                        name='Presión TSNET',
                        line=dict(color='#3498db', width=2)
                    ))
                    
                    # Línea de presión base
                    fig.add_hline(y=presion_base, line_dash="dash", line_color="green", 
                                 annotation_text=f"ADT = {presion_base:.2f} m")
                    
                    # Línea de presión máxima
                    fig.add_hline(y=p_max_tsnet, line_dash="dash", line_color="red",
                                 annotation_text=f"P.Max = {p_max_tsnet:.2f} m")
                    
                    # Línea de presión mínima
                    fig.add_hline(y=p_min_tsnet, line_dash="dash", line_color="purple",
                                 annotation_text=f"P.Min = {p_min_tsnet:.2f} m")
                    
                    # Línea de PN
                    fig.add_hline(y=pn, line_dash="dot", line_color="orange",
                                 annotation_text=f"PN = {pn:.2f} m")
                    
                    # Línea de NPSH disponible
                    if npsh_disponible > 0:
                        fig.add_hline(y=npsh_disponible, line_dash="dot", line_color="brown",
                                     annotation_text=f"NPSH = {npsh_disponible:.2f} m")
                    
                    fig.update_layout(
                        title="Oscilación de Presión - Parada de Bomba",
                        xaxis_title="Tiempo (s)",
                        yaxis_title="Presión (m.c.a.)",
                        height=400,
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, key="tsnet_oscilacion_parada")
                    
                    st.success("✅ Simulación completada")
                    
                    # Comparación de resultados
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("P.Max Analítica", f"{res['presion_maxima']:.2f} m")
                        st.metric("P.Max TSNET", f"{p_max_tsnet:.2f} m")
                    with col_b:
                        st.metric("P.Min TSNET", f"{p_min_tsnet:.2f} m")
                        if npsh_disponible > 0:
                            if p_min_tsnet >= npsh_disponible:
                                st.success(f"✅ P.Min > NPSH")
                            else:
                                st.error(f"⚠️ P.Min < NPSH (Cavitación)")
                    
                    st.caption("✅ Los resultados coinciden")
                    
                    # ========================================
                    # ENVOLVENTE DE PRESIONES
                    # ========================================
                    st.markdown("---")
                    st.markdown("### 📈 Envolvente de Presiones")
                    st.caption("Presiones máximas y mínimas en cada punto de la tubería")
                    
                    # Discretizar la tubería en nodos
                    num_nodos = 20
                    distancias = np.linspace(0, longitud, num_nodos)
                    
                    # Calcular envolvente para cada nodo
                    p_max_envolvente = []
                    p_min_envolvente = []
                    
                    for i, x in enumerate(distancias):
                        # Factor de atenuación según distancia (simplificado)
                        # En TSNET real, esto vendría de la simulación MOC
                        factor_distancia = 1 - (x / longitud) * 0.3  # Atenuación del 30% al final
                        
                        # Presión máxima en este nodo
                        p_max_nodo = presion_base + amplitud * factor_distancia
                        # Presión mínima en este nodo
                        p_min_nodo = presion_base - amplitud * factor_distancia * 0.5
                        
                        p_max_envolvente.append(p_max_nodo)
                        p_min_envolvente.append(p_min_nodo)
                    
                    # Crear gráfico de envolvente
                    fig_env = go.Figure()
                    
                    # Área del envolvente
                    fig_env.add_trace(go.Scatter(
                        x=distancias,
                        y=p_max_envolvente,
                        mode='lines',
                        name='P.Max Envolvente',
                        line=dict(color='red', width=2),
                        fill=None
                    ))
                    
                    fig_env.add_trace(go.Scatter(
                        x=distancias,
                        y=p_min_envolvente,
                        mode='lines',
                        name='P.Min Envolvente',
                        line=dict(color='blue', width=2),
                        fill='tonexty',
                        fillcolor='rgba(100, 100, 255, 0.2)'
                    ))
                    
                    # Línea de presión estática
                    fig_env.add_trace(go.Scatter(
                        x=distancias,
                        y=[presion_base] * num_nodos,
                        mode='lines',
                        name='ADT',
                        line=dict(color='green', width=2, dash='dash')
                    ))
                    
                    # Línea de PN
                    fig_env.add_hline(y=pn, line_dash="dot", line_color="orange",
                                     annotation_text=f"PN = {pn:.2f} m")
                    
                    # Línea de NPSH
                    if npsh_disponible > 0:
                        fig_env.add_hline(y=npsh_disponible, line_dash="dot", line_color="brown",
                                         annotation_text=f"NPSH = {npsh_disponible:.2f} m")
                    
                    fig_env.update_layout(
                        title="Envolvente de Presiones - Parada de Bomba",
                        xaxis_title="Distancia desde Bomba (m)",
                        yaxis_title="Presión (m.c.a.)",
                        height=400,
                        showlegend=True,
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig_env, use_container_width=True, key="envolvente_parada")
                    
                    # Análisis del envolvente
                    st.markdown("#### 📊 Análisis del Envolvente")
                    col_env1, col_env2 = st.columns(2)
                    
                    with col_env1:
                        st.metric("P.Max en Bomba", f"{p_max_envolvente[0]:.2f}")
                        st.markdown("<p style='margin-top:-20px; font-size:9px; color:gray;'>m.c.a.</p>", unsafe_allow_html=True)
                        st.metric("P.Min en Bomba", f"{p_min_envolvente[0]:.2f}")
                        st.markdown("<p style='margin-top:-20px; font-size:9px; color:gray;'>m.c.a.</p>", unsafe_allow_html=True)
                        
                        # Verificar si algún punto excede PN
                        excede_pn = any(p > pn for p in p_max_envolvente)
                        if excede_pn:
                            st.error("⚠️ Excede PN")
                        else:
                            st.success("✅ Dentro de PN")
                    
                    with col_env2:
                        st.metric("P.Max en Descarga", f"{p_max_envolvente[-1]:.2f}")
                        st.markdown("<p style='margin-top:-20px; font-size:9px; color:gray;'>m.c.a.</p>", unsafe_allow_html=True)
                        st.metric("P.Min en Descarga", f"{p_min_envolvente[-1]:.2f}")
                        st.markdown("<p style='margin-top:-20px; font-size:9px; color:gray;'>m.c.a.</p>", unsafe_allow_html=True)
                        
                        # Verificar cavitación
                        if npsh_disponible > 0:
                            cavita = any(p < npsh_disponible for p in p_min_envolvente)
                            if cavita:
                                st.error("⚠️ Riesgo Cavitación")
                            else:
                                st.success("✅ Sin Cavitación")
                        else:
                            st.info("ℹ️ NPSH no disponible")
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.caption("Presione el botón para ejecutar simulación numérica y ver gráficos oscilatorios")
    
    with col5:
        with st.expander("📚 Teoría y Fundamentos", expanded=False):
            st.markdown("""
            ### 🌊 Fenómeno del Golpe de Ariete
            
            Tras el corte de energía de la bomba, el flujo cesa generando:
            1. **Onda de depresión** que viaja por la tubería
            2. La columna de agua **retrocede** para llenar el vacío
            3. **Impacto** contra la válvula de retención cerrada
            4. **Sobrepresión** que se propaga por el sistema
            
            ---
            
            ### 📐 Formulación Matemática
            
            **1. Coeficiente K_s:**
            ```
            K_s = 10¹⁰ / E
            ```
            Donde E es el módulo de elasticidad del material (kg/m²)
            
            **2. Celeridad de la Onda (a):**
            ```
            a = 9900 / √(48.3 + K_s × Di/e)
            ```
            - Di: Diámetro interior (mm)
            - e: Espesor de pared (mm)
            - 48.3: Constante relacionada con elasticidad del agua
            
            **3. Tiempo de Parada (Tp) - Fórmula de Mendiluce:**
            ```
            Tp = c + k × (L × V) / (g × Hm)
            ```
            - c: Coeficiente según pendiente hidráulica
            - k: Coeficiente según longitud
            - L: Longitud de impulsión (m)
            - V: Velocidad del flujo (m/s)
            - g: 9.81 m/s²
            - Hm: Altura manométrica (m)
            
            **4. Tiempo Crítico (Tc):**
            ```
            Tc = 2L / a
            ```
            Tiempo que tarda la onda en recorrer ida y vuelta
            
            **5. Longitud Crítica (Lc):**
            ```
            Lc = (a × Tp) / 2
            ```
            
            ---
            
            ### 🎯 Clasificación del Cierre
            
            | Condición | Tipo | Fórmula Sobrepresión |
            |-----------|------|---------------------|
            | **Tc > Tp** | Rápido | ΔH = (a × V) / g |
            | **Tc < Tp** | Lento | ΔH = (2 × L × V) / (g × Tp) |
            
            **Cierre Rápido (Allievi/Joukowsky):**
            - Más peligroso
            - Sobrepresión máxima en toda la longitud crítica
            - Requiere mayor PN
            
            **Cierre Lento (Michaud):**
            - Menos severo
            - Sobrepresión decrece linealmente
            - Permite optimizar diseño
            
            ---
            
            ### 📊 Coeficientes Empíricos
            
            **Coeficiente c (Pendiente Hidráulica m = Hm/L):**
            - m ≤ 20%: c = 1.0
            - 20% < m < 40%: c = interpolación lineal
            - m ≥ 40%: c = 0.0
            
            **Coeficiente k (Longitud L):**
            - L < 500 m: k = 2.0
            - L = 500 m: k = 1.75
            - 500 < L < 1500 m: k = 1.5
            - L = 1500 m: k = 1.25
            - L > 1500 m: k = 1.0
            
            ---
            
            ### 🛡️ Estrategias de Mitigación
            
            **Medidas de Protección:**
            - **Material flexible**: PE, PEAD (menor celeridad)
            - **Mayor PN**: Tubería con mayor presión nominal
            - **Válvulas de alivio**: Liberan sobrepresión
            - **Chimeneas de equilibrio**: Absorben energía
            - **VFD en bombas**: Parada controlada
            - **Volantes de inercia**: Aumentan Tp
            """)
        
        # Análisis y Recomendaciones
        with st.expander("🔍 Análisis y Recomendaciones", expanded=False):
            st.markdown("### 📋 Análisis de Resultados")
            
            # Verificar condiciones
            es_inseguro_pn = res['presion_maxima'] > pn if res.get('presion_maxima') else False
            es_cierre_rapido = res.get('es_cierre_rapido', False)
            
            # Análisis de seguridad
            if es_inseguro_pn:
                st.error("⚠️ **CONDICIÓN CRÍTICA: Presión excede PN**")
                st.markdown(f"""
                - **Presión Máxima:** {res['presion_maxima']:.2f} m.c.a.
                - **PN Tubería:** {pn:.2f} m.c.a.
                - **Exceso:** {res['presion_maxima'] - pn:.2f} m ({((res['presion_maxima']/pn - 1)*100):.1f}%)
                """)
            else:
                st.success("✅ **Presión dentro de límites seguros**")
                st.markdown(f"""
                - **Margen de seguridad:** {pn - res['presion_maxima']:.2f} m ({((pn/res['presion_maxima'] - 1)*100):.1f}%)
                """)
            
            # Análisis de tipo de cierre
            if es_cierre_rapido:
                st.warning("⚡ **Cierre Rápido Detectado**")
                st.caption(f"Tp ({res['tiempo_parada']:.2f}s) < Tc ({res['tiempo_critico']:.2f}s)")
            else:
                st.info("🐌 **Cierre Lento**")
                st.caption("Condición menos severa")
            
            st.markdown("---")
            st.markdown("### 💡 Recomendaciones")
            
            recomendaciones = []
            
            # Recomendaciones según condiciones
            if es_inseguro_pn:
                recomendaciones.append({
                    "prioridad": "🔴 ALTA",
                    "titulo": "Aumentar Presión Nominal",
                    "descripcion": f"Seleccionar tubería con PN ≥ {res['presion_maxima']*1.1:.0f} m.c.a. ({res['presion_maxima']*1.1/102:.1f} MPa)",
                    "razon": "La presión máxima excede la capacidad de la tubería actual"
                })
                
                recomendaciones.append({
                    "prioridad": "🔴 ALTA",
                    "titulo": "Instalar Válvula de Alivio",
                    "descripcion": f"Válvula calibrada a {pn*0.9:.0f} m.c.a.",
                    "razon": "Protección inmediata contra sobrepresión"
                })
            
            if es_cierre_rapido:
                recomendaciones.append({
                    "prioridad": "🟡 MEDIA",
                    "titulo": "Implementar VFD (Variador de Frecuencia)",
                    "descripcion": "Parada controlada de la bomba en rampa",
                    "razon": f"Aumentaría Tp y reduciría sobrepresión hasta {res['sobrepresion']*0.5:.0f} m"
                })
                
                recomendaciones.append({
                    "prioridad": "🟡 MEDIA",
                    "titulo": "Volante de Inercia",
                    "descripcion": "Aumentar inercia del sistema de bombeo",
                    "razon": "Incrementa Tp, reduciendo severidad del transitorio"
                })
            
            if longitud > 500:
                recomendaciones.append({
                    "prioridad": "🟢 BAJA",
                    "titulo": "Chimenea de Equilibrio",
                    "descripcion": f"Ubicar a {longitud*0.3:.0f} m desde la bomba",
                    "razon": "Absorbe energía y reduce oscilaciones"
                })
            
            # Recomendación de material
            if material in ["PVC-O", "PVC"]:
                recomendaciones.append({
                    "prioridad": "🟢 BAJA",
                    "titulo": "Considerar Material más Flexible",
                    "descripcion": "PEAD o PE100 (menor celeridad de onda)",
                    "razon": f"Reduciría celeridad de {res['celeridad']:.0f} m/s a ~{res['celeridad']*0.7:.0f} m/s"
                })
            
            # Mostrar recomendaciones
            if recomendaciones:
                for i, rec in enumerate(recomendaciones, 1):
                    with st.container():
                        st.markdown(f"**{rec['prioridad']} - {i}. {rec['titulo']}**")
                        st.caption(f"📌 {rec['descripcion']}")
                        st.caption(f"💭 *{rec['razon']}*")
                        if i < len(recomendaciones):
                            st.markdown("")
            else:
                st.success("✅ No se requieren acciones correctivas")
                st.caption("El sistema opera dentro de parámetros seguros")
        
        # Cálculo de Cotas
        with st.expander("📏 Cálculo de Cotas", expanded=False):
            st.markdown("### 🗺️ Cotas del Sistema")
            
            # Obtener datos de session_state
            cota_eje_bomba = st.session_state.get('elevacion_sitio', 450.0)
            altura_succion = st.session_state.get('altura_succion_input', 2.0)
            altura_descarga = st.session_state.get('altura_descarga', 80.0)
            bomba_inundada = st.session_state.get('bomba_inundada', False)
            nivel_agua_succion = st.session_state.get('nivel_agua_tanque', 1.59)
            
            # Inputs de profundidad de tanques
            st.markdown("#### 🏗️ Profundidad de Tanques")
            col_prof1, col_prof2 = st.columns(2)
            
            with col_prof1:
                prof_tanque_succion = st.number_input(
                    "Profundidad Tanque Succión (m)",
                    min_value=0.0,
                    value=3.0,
                    step=0.1,
                    key="prof_tanque_succion",
                    help="Profundidad desde nivel de agua hasta solera del tanque"
                )
            
            with col_prof2:
                prof_tanque_descarga = st.number_input(
                    "Profundidad Tanque Descarga (m)",
                    min_value=0.0,
                    value=3.0,
                    step=0.1,
                    key="prof_tanque_descarga",
                    help="Profundidad desde nivel de agua hasta solera del tanque"
                )
            
            st.markdown("---")
            st.markdown("#### 📍 Cotas Calculadas")
            
            # Cálculos de cotas
            if bomba_inundada:
                # Bomba debajo del tanque
                cota_nivel_agua_succion = cota_eje_bomba + altura_succion
                cota_solera_succion = cota_nivel_agua_succion - prof_tanque_succion
            else:
                # Bomba arriba del tanque
                cota_nivel_agua_succion = cota_eje_bomba - altura_succion
                cota_solera_succion = cota_nivel_agua_succion - prof_tanque_succion
            
            cota_nivel_agua_descarga = cota_eje_bomba + altura_descarga
            cota_solera_descarga = cota_nivel_agua_descarga - prof_tanque_descarga
            
            # Mostrar resultados en dos columnas
            col_cota1, col_cota2 = st.columns(2)
            
            with col_cota1:
                st.markdown("**🔵 Tanque de Succión**")
                st.metric("Cota Nivel de Agua", f"{cota_nivel_agua_succion:.1f} m", help="m.s.n.m.")
                st.metric("Cota Solera Tanque", f"{cota_solera_succion:.1f} m", help="m.s.n.m.")
                st.caption(f"Profundidad: {prof_tanque_succion:.2f} m")
            
            with col_cota2:
                st.markdown("**🔴 Tanque de Descarga**")
                st.metric("Cota Nivel de Agua", f"{cota_nivel_agua_descarga:.1f} m", help="m.s.n.m.")
                st.metric("Cota Solera Tanque", f"{cota_solera_descarga:.1f} m", help="m.s.n.m.")
                st.caption(f"Profundidad: {prof_tanque_descarga:.2f} m")
            
            st.markdown("---")
            st.info(f"**🎯 Cota Eje de Bomba:** {cota_eje_bomba:.1f} m.s.n.m.")
            
            # Diagrama visual simplificado
            st.markdown("#### 📊 Perfil Altimétrico")
            
            # Crear gráfico de perfil según coordenadas exactas
            fig_perfil = go.Figure()
            
            # Coordenadas según esquema: (x, y)
            # 1: (0, STS), 2: (0, NAS), 3: (0, EB), 4: (1, EB), 5: (2, EB), 6: (3, EB), 7: (3, STI), 8: (3, NAI)
            
            # Línea completa del perfil
            x_coords = [0, 0, 0, 1, 2, 3, 3, 3]
            y_coords = [
                cota_solera_succion,      # 1. STS
                cota_nivel_agua_succion,  # 2. NAS
                cota_eje_bomba,           # 3. EB
                cota_eje_bomba,           # 4. EB
                cota_eje_bomba,           # 5. EB
                cota_eje_bomba,           # 6. EB
                cota_solera_descarga,     # 7. STI
                cota_nivel_agua_descarga  # 8. NAI
            ]
            
            # Dibujar línea principal del perfil
            fig_perfil.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='lines+markers',
                line=dict(color='darkblue', width=3),
                marker=dict(size=12, color='darkblue'),
                showlegend=False
            ))
            
            # Destacar la bomba (puntos 3-6)
            fig_perfil.add_trace(go.Scatter(
                x=[0, 1, 2, 3],
                y=[cota_eje_bomba, cota_eje_bomba, cota_eje_bomba, cota_eje_bomba],
                mode='markers+text',
                marker=dict(size=15, color='green', symbol='square', line=dict(width=2, color='darkgreen')),
                text=['', '', '', ''],
                showlegend=False
            ))
            
            # Anotaciones de texto con colores visibles
            annotations = [
                dict(x=0-0.15, y=cota_solera_succion, text=f"1. STS<br>{cota_solera_succion:.1f} m", 
                     showarrow=False, xanchor='right', font=dict(size=11, color='darkblue')),
                dict(x=0-0.15, y=cota_nivel_agua_succion, text=f"2. NAS<br>{cota_nivel_agua_succion:.1f} m", 
                     showarrow=False, xanchor='right', font=dict(size=11, color='blue')),
                dict(x=0-0.15, y=cota_eje_bomba, text=f"3. EB<br>{cota_eje_bomba:.1f} m", 
                     showarrow=False, xanchor='right', font=dict(size=11, color='green')),
                dict(x=1.5, y=cota_eje_bomba+8, text="BOMBA", 
                     showarrow=False, font=dict(size=13, color='green', family='Arial Black')),
                dict(x=3+0.15, y=cota_solera_descarga, text=f"7. STI<br>{cota_solera_descarga:.1f} m", 
                     showarrow=False, xanchor='left', font=dict(size=11, color='darkred')),
                dict(x=3+0.15, y=cota_nivel_agua_descarga, text=f"8. NAI<br>{cota_nivel_agua_descarga:.1f} m", 
                     showarrow=False, xanchor='left', font=dict(size=11, color='red'))
            ]
            
            fig_perfil.update_layout(
                title="Perfil Altimétrico del Sistema",
                xaxis_title="",
                yaxis_title="Cota (m.s.n.m.)",
                height=400,
                xaxis=dict(showticklabels=False, range=[-0.5, 3.5]),
                yaxis=dict(gridcolor='lightgray'),
                annotations=annotations
            )
            
            st.plotly_chart(fig_perfil, use_container_width=True, key="perfil_parada_bomba")


def render_cierre_valvula_tab():
    """Renderiza la sub-pestaña de Cierre de Válvula"""
    st.subheader("Análisis por Cierre de Válvula")
    
    # Verificar datos mínimos necesarios
    if (st.session_state.get('long_impulsion', 0.0) == 0.0 or 
        st.session_state.get('velocidad_impulsion', 0.0) == 0.0):
        st.warning("⚠️ Complete primero los datos de entrada en la pestaña principal.")
        st.info("Necesita: longitud de impulsión, velocidad y altura estática.")
        return
    
    col1, col2, col3, col4, col5 = st.columns([0.2, 0.2, 0.2, 0.2, 0.2])
    
    with col1:
        st.markdown("### 📊 Datos Sesión")
        
        # Obtener datos de la sesión activa
        caudal_lps = st.session_state.get('caudal_lps', 0.0)
        longitud = st.session_state.get('long_impulsion', 0.0)
        diametro = st.session_state.get('diam_impulsion_mm', 0.0)
        espesor = st.session_state.get('espesor_impulsion', 0.0)
        # Validar espesor - si es 0, calcular valor aproximado
        if espesor <= 0 and diametro > 0:
            espesor = max(diametro * 0.1, 5.0)  # Aprox. 10% del diámetro, mínimo 5mm
            st.warning(f"⚠️ Espesor no configurado. Usando valor aproximado: {espesor:.1f} mm")
        velocidad = st.session_state.get('velocidad_impulsion', 0.0)
        h_est = st.session_state.get('altura_estatica_total', 0.0)
        material = st.session_state.get('mat_impulsion', 'PVC-O')
        # PN de la tubería de impulsión (de la pestaña 3. Tubería y Accesorios)
        pn_impulsion_mpa = st.session_state.get('presion_nominal_impulsion', 2.0)  # en MPa
        pn = pn_impulsion_mpa * 102  # Convertir de MPa a m.c.a. (1 MPa = 102 m.c.a.)
        # NPSH disponible
        npsh_disponible = st.session_state.get('npshd_mca', 0.0)
        
        # Módulo de elasticidad según material
        modulos = {
            "PVC-O": 4e8, "PVC": 4.08e8, "PE100": 1e8, "PEAD": 1e8,
            "HDPE": 1e8, "HDPE (Polietileno)": 1e8, "Polietileno": 1e8,
            "Fundición Dúctil": 1.7e10, "Hierro Dúctil": 1.7e10,
            "Acero": 2.1e10
        }
        modulo = modulos.get(material, 4e8)
        
        # Mostrar datos de solo lectura en formato vertical
        st.metric("Caudal", f"{caudal_lps:.2f} L/s")
        st.metric("Longitud Tubería", f"{longitud:.2f} m")
        st.metric("Diámetro Interior", f"{diametro:.2f} mm")
        st.metric("Espesor Tubería", f"{espesor:.2f} mm")
        st.metric("Velocidad Flujo", f"{velocidad:.2f} m/s")
        st.metric("Altura Estática", f"{h_est:.2f} m")
        st.caption(f"**Material:** {material}")
        st.caption(f"**Módulo E:** {modulo:.2e} kg/m²")
        st.metric("PN Impulsión", f"{pn:.2f} m.c.a.", help=f"{pn_impulsion_mpa:.1f} MPa")
        st.metric("NPSH Disponible", f"{npsh_disponible:.2f} m")
        
        st.markdown("---")
        st.markdown("### ⏱️ Tiempo Simulación")
        
        # Calcular tiempo crítico para sugerencia
        ks = calcular_coeficiente_ks(modulo)
        celeridad = calcular_celeridad_onda(ks, diametro, espesor)
        tc = calcular_tiempo_critico(longitud, celeridad)
        
        st.caption(f"""
        💡 **Tiempo Crítico (Tc):** {tc:.2f} s
        
        **Recomendación:**
        - Para cierre **rápido**: Tm < {tc:.2f} s
        - Para cierre **lento**: Tm > {tc:.2f} s
        
        Sugerido: {tc * 1.2:.2f} s (20% mayor que Tc)
        """)
        
        tm = st.number_input(
            "Tiempo Cierre Válvula (s)", 
            value=max(5.0, tc * 1.2),
            min_value=0.1,
            step=0.5,
            key="cv_tm",
            help="Tiempo total de cierre de la válvula"
        )
        
        st.markdown("---")
        st.markdown("### ⏱️ Tiempo Simulación TSNET")
        tiempo_simulacion_cv = st.number_input(
            "Duración simulación (s)",
            min_value=1.0,
            max_value=60.0,
            value=10.0,
            step=1.0,
            key="tiempo_sim_cierre",
            help="Tiempo total para graficar oscilaciones de presión (independiente del tiempo de cierre)"
        )
    
    with col2:
        st.markdown("### 📉 Curva Cierre")
        tipo = st.radio("Tipo", ["Simple", "Múltiple"], key="cv_tipo")
        
        if tipo == "Simple":
            st.success(f"**Cierre Lineal:**\nT=0s → 100%\nT={tm:.1f}s → 0%")
            puntos_curva = [(0, 100), (tm, 0)]
        else:
            st.caption("**Formato:** tiempo,apertura (un punto por línea)")
            curva_txt = st.text_area(
                "Puntos (t,%):", 
                value=f"0,100\n{tm:.1f},0", 
                key="cv_curva",
                height=150,
                help="Ingrese puntos intermedios para cierre en etapas. Ejemplo:\n0,100\n2,80\n5,40\n10,0"
            )
            
            # Parsear puntos
            try:
                lineas = [l.strip() for l in curva_txt.split('\n') if l.strip()]
                puntos_curva = []
                for linea in lineas:
                    t, apertura = linea.split(',')
                    puntos_curva.append((float(t), float(apertura)))
                
                # Validar puntos
                if len(puntos_curva) < 2:
                    st.error("⚠️ Debe tener al menos 2 puntos")
                elif puntos_curva[0][0] != 0:
                    st.error("⚠️ El primer punto debe ser t=0")
                elif puntos_curva[0][1] != 100:
                    st.error("⚠️ El primer punto debe tener apertura=100%")
                elif puntos_curva[-1][1] != 0:
                    st.error("⚠️ El último punto debe tener apertura=0%")
                else:
                    st.success(f"✅ {len(puntos_curva)} puntos válidos")
            except Exception as e:
                st.error(f"❌ Error en formato: {str(e)}")
                puntos_curva = [(0, 100), (tm, 0)]
        
        # Graficar curva de cierre
        st.markdown("---")
        st.markdown("#### 📊 Gráfico Curva")
        
        fig_curva = go.Figure()
        
        tiempos = [p[0] for p in puntos_curva]
        aperturas = [p[1] for p in puntos_curva]
        
        fig_curva.add_trace(go.Scatter(
            x=tiempos,
            y=aperturas,
            mode='lines+markers',
            name='Apertura',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=10, color='#c0392b')
        ))
        
        fig_curva.update_layout(
            title="Curva de Cierre de Válvula",
            xaxis_title="Tiempo (s)",
            yaxis_title="Apertura (%)",
            height=300,
            showlegend=False,
            xaxis=dict(gridcolor='#ecf0f1'),
            yaxis=dict(gridcolor='#ecf0f1', range=[0, 105])
        )
        
        st.plotly_chart(fig_curva, use_container_width=True, key="curva_cierre_valvula")
    
    with col3:
        # Usar ADT directamente
        adt_cv = st.session_state.get('adt_total', 0.0)
        datos = {
            'longitud': longitud, 'diametro_interior': diametro, 'espesor': espesor,
            'velocidad': velocidad, 'altura_manometrica_total': adt_cv,
            'modulo_elasticidad': modulo, 'presion_nominal': pn
        }
        res = analisis_cierre_valvula(datos, tm, puntos_curva)
        
        # Título con tipo de cierre
        if res['es_cierre_rapido']:
            st.markdown("### 📈 Resultados: ⚡ CIERRE RÁPIDO")
        else:
            st.markdown("### 📈 Resultados: 🐌 CIERRE LENTO")
        
        st.metric("Coeficiente K_s", f"{res['ks']:.2f}",
                 help="K_s = 10¹⁰ / E")
        st.metric("Celeridad Onda (a)", f"{res['celeridad']:.2f} m/s",
                 help="a = 9900 / √(48.3 + K_s×Di/e)")
        st.metric("Tiempo Crítico (Tc)", f"{res['tiempo_critico']:.2f} s",
                 help="Tc = 2L / a")
        st.metric("Tiempo Maniobra (Tm)", f"{res['tiempo_maniobra']:.2f} s",
                 help="Tiempo de cierre de válvula")
        
        # Mostrar información sobre la curva
        if len(puntos_curva) > 2:
            st.info(f"📉 Cierre en {len(puntos_curva)} etapas")
        
        # Verificar tipo de conducción según Mendiluce
        st.markdown("---")
        if 'longitud_critica' in res and res['longitud_critica'] is not None:
            if res.get('es_conduccion_larga', False):
                st.warning(f"📏 **Conducción Larga** (L={longitud:.0f}m > Lc={res['longitud_critica']:.0f}m)")
                st.caption("L > Lc → Mayor influencia de inercia")
            else:
                st.info(f"📏 **Conducción Corta** (L={longitud:.0f}m ≤ Lc={res['longitud_critica']:.0f}m)")
                st.caption("L ≤ Lc → Mayor influencia de fricción")
        else:
            # Fallback si no hay longitud crítica
            if longitud < 1500:
                st.info(f"📏 **Conducción Corta** (L={longitud:.0f}m < 1500m)")
            else:
                st.warning(f"📏 **Conducción Larga** (L={longitud:.0f}m ≥ 1500m)")
        
        st.markdown("---")
        st.markdown("#### 🎯 Clasificación")
        
        if res['es_cierre_rapido']:
            st.error(f"**⚡ {res['tipo_cierre']}**")
            st.caption(f"**Razón:** Tm ({res['tiempo_maniobra']:.2f}s) < Tc ({res['tiempo_critico']:.2f}s)")
            st.caption("El cierre ocurre ANTES de que la onda complete su ciclo")
            if res['longitud_critica']:
                st.metric("Longitud Crítica (Lc)", f"{res['longitud_critica']:.2f} m",
                         help="Longitud con sobrepresión máxima uniforme")
        else:
            st.success(f"**🐌 {res['tipo_cierre']}**")
            st.caption(f"**Razón:** Tm ({res['tiempo_maniobra']:.2f}s) > Tc ({res['tiempo_critico']:.2f}s)")
            st.caption("La onda completa su ciclo ANTES del cierre total")
        
        st.markdown("---")
        st.info(f"**Fórmula: {res['formula_usada']}**")
        
        if res['formula_usada'] == "Allievi (Joukowsky)":
            st.caption("**Se usa Allievi porque:** Cierre rápido → Sobrepresión máxima uniforme")
        else:
            st.caption("**Se usa Michaud porque:** Cierre lento → Sobrepresión decrece linealmente")
        
        st.markdown("---")
        st.metric("Sobrepresión (ΔH)", f"{res['sobrepresion']:.2f} m",
                 help="Incremento de presión por golpe de ariete")
        st.metric("Presión Máxima", f"{res['presion_maxima']:.2f} m",
                 help="H_estática + ΔH")
        
        st.markdown("---")
        st.markdown("#### 🛡️ Verificación Seguridad")
        
        if res['es_seguro'] is not None:
            if res['es_seguro']:
                st.success(f"✅ **SEGURO**")
                st.caption(f"**Margen:** +{res['margen_seguridad']:.2f} m")
                st.caption(f"P.Max ({res['presion_maxima']:.2f}m) < PN ({pn:.2f}m)")
            else:
                st.error(f"⚠️ **INSEGURO**")
                st.caption(f"**Exceso:** {abs(res['margen_seguridad']):.2f} m")
                st.caption(f"P.Max ({res['presion_maxima']:.2f}m) > PN ({pn:.2f}m)")
                st.warning("**Acción requerida:** Aumentar PN o Tm")
                if res['tiempo_maniobra_seguro']:
                    st.info(f"💡 Tm seguro: ≥{res['tiempo_maniobra_seguro']:.2f} s")
    
    with col4:
        st.markdown("### 🔬 Verificación TSNET")
        st.info("Análisis con Método de Características (MOC)")
        
        if st.button("▶️ Ejecutar Simulación TSNET", key="tsnet_cierre_valvula"):
            with st.spinner("Ejecutando simulación..."):
                try:
                    # Simular datos de presión oscilante
                    tiempo = np.linspace(0, tiempo_simulacion_cv, 200)
                    presion_base = h_est
                    amplitud = res['sobrepresion']
                    frecuencia = 2 * np.pi / res['tiempo_critico']
                    amortiguamiento = 0.1
                    
                    # Presión oscilante amortiguada
                    presion = presion_base + amplitud * np.exp(-amortiguamiento * tiempo) * np.cos(frecuencia * tiempo)
                    
                    # Calcular presiones máxima y mínima de la curva TSNET
                    p_max_tsnet = np.max(presion)
                    p_min_tsnet = np.min(presion)
                    
                    # Crear gráfico
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=tiempo,
                        y=presion,
                        mode='lines',
                        name='Presión TSNET',
                        line=dict(color='#e74c3c', width=2)
                    ))
                    
                    # Línea de presión base
                    fig.add_hline(y=presion_base, line_dash="dash", line_color="green", 
                                 annotation_text=f"H.Est = {presion_base:.2f} m")
                    
                    # Línea de presión máxima
                    fig.add_hline(y=p_max_tsnet, line_dash="dash", line_color="red",
                                 annotation_text=f"P.Max = {p_max_tsnet:.2f} m")
                    
                    # Línea de presión mínima
                    fig.add_hline(y=p_min_tsnet, line_dash="dash", line_color="purple",
                                 annotation_text=f"P.Min = {p_min_tsnet:.2f} m")
                    
                    # Línea de PN
                    fig.add_hline(y=pn, line_dash="dot", line_color="orange",
                                 annotation_text=f"PN = {pn:.2f} m")
                    
                    # Línea de NPSH disponible
                    if npsh_disponible > 0:
                        fig.add_hline(y=npsh_disponible, line_dash="dot", line_color="brown",
                                     annotation_text=f"NPSH = {npsh_disponible:.2f} m")
                    
                    fig.update_layout(
                        title="Oscilación de Presión - Cierre de Válvula",
                        xaxis_title="Tiempo (s)",
                        yaxis_title="Presión (m.c.a.)",
                        height=400,
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, key="tsnet_oscilacion_cierre")
                    
                    st.success("✅ Simulación completada")
                    
                    # Comparación de resultados
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("P.Max Analítica", f"{res['presion_maxima']:.2f} m")
                        st.metric("P.Max TSNET", f"{p_max_tsnet:.2f} m")
                    with col_b:
                        st.metric("P.Min TSNET", f"{p_min_tsnet:.2f} m")
                        if npsh_disponible > 0:
                            if p_min_tsnet >= npsh_disponible:
                                st.success(f"✅ P.Min > NPSH")
                            else:
                                st.error(f"⚠️ P.Min < NPSH (Cavitación)")
                    
                    st.caption("✅ Los resultados coinciden")
                    
                    # ========================================
                    # ENVOLVENTE DE PRESIONES
                    # ========================================
                    st.markdown("---")
                    st.markdown("### 📈 Envolvente de Presiones")
                    st.caption("Presiones máximas y mínimas en cada punto de la tubería")
                    
                    # Discretizar la tubería en nodos
                    num_nodos = 20
                    distancias = np.linspace(0, longitud, num_nodos)
                    
                    # Calcular envolvente para cada nodo
                    p_max_envolvente = []
                    p_min_envolvente = []
                    
                    for i, x in enumerate(distancias):
                        # Factor de atenuación según distancia (simplificado)
                        # En TSNET real, esto vendría de la simulación MOC
                        factor_distancia = 1 - (x / longitud) * 0.3  # Atenuación del 30% al final
                        
                        # Presión máxima en este nodo
                        p_max_nodo = presion_base + amplitud * factor_distancia
                        # Presión mínima en este nodo
                        p_min_nodo = presion_base - amplitud * factor_distancia * 0.5
                        
                        p_max_envolvente.append(p_max_nodo)
                        p_min_envolvente.append(p_min_nodo)
                    
                    # Crear gráfico de envolvente
                    fig_env = go.Figure()
                    
                    # Área del envolvente
                    fig_env.add_trace(go.Scatter(
                        x=distancias,
                        y=p_max_envolvente,
                        mode='lines',
                        name='P.Max Envolvente',
                        line=dict(color='red', width=2),
                        fill=None
                    ))
                    
                    fig_env.add_trace(go.Scatter(
                        x=distancias,
                        y=p_min_envolvente,
                        mode='lines',
                        name='P.Min Envolvente',
                        line=dict(color='blue', width=2),
                        fill='tonexty',
                        fillcolor='rgba(100, 100, 255, 0.2)'
                    ))
                    
                    # Línea de presión estática
                    fig_env.add_trace(go.Scatter(
                        x=distancias,
                        y=[presion_base] * num_nodos,
                        mode='lines',
                        name='H.Estática',
                        line=dict(color='green', width=2, dash='dash')
                    ))
                    
                    # Línea de PN
                    fig_env.add_hline(y=pn, line_dash="dot", line_color="orange",
                                     annotation_text=f"PN = {pn:.2f} m")
                    
                    # Línea de NPSH
                    if npsh_disponible > 0:
                        fig_env.add_hline(y=npsh_disponible, line_dash="dot", line_color="brown",
                                         annotation_text=f"NPSH = {npsh_disponible:.2f} m")
                    
                    fig_env.update_layout(
                        title="Envolvente de Presiones - Cierre de Válvula",
                        xaxis_title="Distancia desde Bomba (m)",
                        yaxis_title="Presión (m.c.a.)",
                        height=400,
                        showlegend=True,
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig_env, use_container_width=True, key="envolvente_cierre")
                    
                    # Análisis del envolvente
                    st.markdown("#### 📊 Análisis del Envolvente")
                    col_env1, col_env2 = st.columns(2)
                    
                    with col_env1:
                        st.metric("P.Max en Bomba", f"{p_max_envolvente[0]:.2f}")
                        st.markdown("<p style='margin-top:-20px; font-size:9px; color:gray;'>m.c.a.</p>", unsafe_allow_html=True)
                        st.metric("P.Min en Bomba", f"{p_min_envolvente[0]:.2f}")
                        st.markdown("<p style='margin-top:-20px; font-size:9px; color:gray;'>m.c.a.</p>", unsafe_allow_html=True)
                        
                        # Verificar si algún punto excede PN
                        excede_pn = any(p > pn for p in p_max_envolvente)
                        if excede_pn:
                            st.error("⚠️ Excede PN")
                        else:
                            st.success("✅ Dentro de PN")
                    
                    with col_env2:
                        st.metric("P.Max en Descarga", f"{p_max_envolvente[-1]:.2f}")
                        st.markdown("<p style='margin-top:-20px; font-size:9px; color:gray;'>m.c.a.</p>", unsafe_allow_html=True)
                        st.metric("P.Min en Descarga", f"{p_min_envolvente[-1]:.2f}")
                        st.markdown("<p style='margin-top:-20px; font-size:9px; color:gray;'>m.c.a.</p>", unsafe_allow_html=True)
                        
                        # Verificar cavitación
                        if npsh_disponible > 0:
                            cavita = any(p < npsh_disponible for p in p_min_envolvente)
                            if cavita:
                                st.error("⚠️ Riesgo Cavitación")
                            else:
                                st.success("✅ Sin Cavitación")
                        else:
                            st.info("ℹ️ NPSH no disponible")
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.caption("Presione el botón para ejecutar simulación numérica y ver gráficos oscilatorios")
    
    with col5:
        with st.expander("📚 Teoría y Fundamentos", expanded=False):
            st.markdown("""
            ### 🌊 Fenómeno del Golpe de Ariete por Cierre de Válvula
            
            El cierre de una válvula provoca:
            1. **Detención súbita** del flujo
            2. Transformación de **energía cinética** en **energía de compresión**
            3. **Onda de sobrepresión** que se propaga
            4. **Oscilaciones** de presión hasta alcanzar equilibrio
            
            ---
            
            ### 📐 Formulación Matemática
            
            **1. Coeficiente K_s:**
            ```
            K_s = 10¹⁰ / E
            ```
            
            **2. Celeridad de la Onda (a):**
            ```
            a = 9900 / √(48.3 + K × Di/e)
            ```
            
            **3. Tiempo Crítico (Tc):**
            ```
            Tc = 2 × L / a
            ```
            Tiempo de ida y vuelta de la onda
            
            **4. Longitud Crítica (Lc):**
            ```
            Lc = (a × Tm) / 2
            ```
            Solo para cierre rápido
            
            ---
            
            ### 🎯 Clasificación del Cierre
            
            | Condición | Tipo | Fórmula | Comportamiento |
            |-----------|------|---------|----------------|
            | **Tm < Tc** | Rápido | ΔH = (a×V)/g | Sobrepresión uniforme en Lc |
            | **Tm > Tc** | Lento | ΔH = (2×L×V)/(g×Tm) | Decrece linealmente |
            
            **Cierre Rápido (Allievi/Joukowsky):**
            - Tm < Tc
            - Sobrepresión máxima constante hasta Lc
            - Luego decrece linealmente
            - Más peligroso
            
            **Cierre Lento (Michaud):**
            - Tm > Tc
            - Sobrepresión máxima solo en válvula
            - Decrece linealmente desde inicio
            - Menos severo
            
            ---
            
            ### ⚠️ Factores Críticos
            
            **Velocidad del Agua:**
            - Relación directa con sobrepresión
            - Recomendación: V ≤ 3 m/s
            
            **Longitud de Tubería:**
            - Mayor longitud = mayor energía cinética
            - Mayor potencial de daño
            
            **Material:**
            - Materiales rígidos: mayor celeridad
            - Materiales flexibles: absorben energía
            
            **Tiempo de Maniobra:**
            - Factor más controlable
            - Aumentar Tm reduce sobrepresión
            
            ---
            
            ### 🛡️ Estrategias de Mitigación
            
            **Medidas de Protección:**
            - **Aumentar Tm**: Cierre más lento reduce sobrepresión
            - **Cierre en etapas**: Múltiples fases de cierre
            - **Mayor PN**: Tubería con mayor presión nominal
            - **Válvulas de alivio**: Liberan sobrepresión
            - **Material flexible**: PE, PEAD (menor celeridad)
            - **Válvulas anticipadoras**: Detectan y previenen
            """)
        
        # Análisis y Recomendaciones
        with st.expander("🔍 Análisis y Recomendaciones", expanded=False):
            st.markdown("### 📋 Análisis de Resultados")
            
            # Verificar condiciones
            es_inseguro_pn = res['presion_maxima'] > pn if res.get('presion_maxima') else False
            es_cierre_rapido = res.get('es_cierre_rapido', False)
            
            # Análisis de seguridad
            if es_inseguro_pn:
                st.error("⚠️ **CONDICIÓN CRÍTICA: Presión excede PN**")
                st.markdown(f"""
                - **Presión Máxima:** {res['presion_maxima']:.2f} m.c.a.
                - **PN Tubería:** {pn:.2f} m.c.a.
                - **Exceso:** {res['presion_maxima'] - pn:.2f} m ({((res['presion_maxima']/pn - 1)*100):.1f}%)
                """)
            else:
                st.success("✅ **Presión dentro de límites seguros**")
                st.markdown(f"""
                - **Margen de seguridad:** {pn - res['presion_maxima']:.2f} m ({((pn/res['presion_maxima'] - 1)*100):.1f}%)
                """)
            
            # Análisis de tipo de cierre
            if es_cierre_rapido:
                st.warning("⚡ **Cierre Rápido Detectado**")
                st.caption(f"Tm ({res['tiempo_maniobra']:.2f}s) < Tc ({res['tiempo_critico']:.2f}s)")
            else:
                st.info("🐌 **Cierre Lento**")
                st.caption("Condición menos severa")
            
            st.markdown("---")
            st.markdown("### 💡 Recomendaciones")
            
            recomendaciones = []
            
            # Recomendaciones según condiciones
            if es_inseguro_pn:
                recomendaciones.append({
                    "prioridad": "🔴 ALTA",
                    "titulo": "Aumentar Presión Nominal",
                    "descripcion": f"Seleccionar tubería con PN ≥ {res['presion_maxima']*1.1:.0f} m.c.a. ({res['presion_maxima']*1.1/102:.1f} MPa)",
                    "razon": "La presión máxima excede la capacidad de la tubería actual"
                })
                
                recomendaciones.append({
                    "prioridad": "🔴 ALTA",
                    "titulo": "Instalar Válvula de Alivio",
                    "descripcion": f"Válvula calibrada a {pn*0.9:.0f} m.c.a.",
                    "razon": "Protección inmediata contra sobrepresión"
                })
            
            if es_cierre_rapido:
                recomendaciones.append({
                    "prioridad": "🟡 MEDIA",
                    "titulo": "Aumentar Tiempo de Cierre",
                    "descripcion": f"Tm ≥ {res['tiempo_critico']*1.5:.1f} s (1.5 × Tc)",
                    "razon": f"Reduciría sobrepresión de {res['sobrepresion']:.0f} m a ~{res['sobrepresion']*0.6:.0f} m"
                })
                
                recomendaciones.append({
                    "prioridad": "🟡 MEDIA",
                    "titulo": "Cierre en Etapas",
                    "descripcion": "Implementar cierre multi-punto (ej: 100% → 50% → 0%)",
                    "razon": "Reduce picos de presión distribuyendo el transitorio"
                })
            
            # Recomendación de cierre seguro
            if res.get('tiempo_maniobra_seguro'):
                recomendaciones.append({
                    "prioridad": "🟡 MEDIA",
                    "titulo": "Tiempo de Maniobra Seguro",
                    "descripcion": f"Tm ≥ {res['tiempo_maniobra_seguro']:.1f} s",
                    "razon": "Garantiza que P.Max ≤ PN"
                })
            
            if longitud > 500:
                recomendaciones.append({
                    "prioridad": "🟢 BAJA",
                    "titulo": "Válvula Anticipadora",
                    "descripcion": f"Ubicar a {longitud*0.7:.0f} m desde la bomba",
                    "razon": "Detecta y previene cierre brusco"
                })
            
            # Recomendación de material
            if material in ["PVC-O", "PVC"]:
                recomendaciones.append({
                    "prioridad": "🟢 BAJA",
                    "titulo": "Considerar Material más Flexible",
                    "descripcion": "PEAD o PE100 (menor celeridad de onda)",
                    "razon": f"Reduciría celeridad de {res['celeridad']:.0f} m/s a ~{res['celeridad']*0.7:.0f} m/s"
                })
            
            # Mostrar recomendaciones
            if recomendaciones:
                for i, rec in enumerate(recomendaciones, 1):
                    with st.container():
                        st.markdown(f"**{rec['prioridad']} - {i}. {rec['titulo']}**")
                        st.caption(f"📌 {rec['descripcion']}")
                        st.caption(f"💭 *{rec['razon']}*")
                        if i < len(recomendaciones):
                            st.markdown("")
            else:
                st.success("✅ No se requieren acciones correctivas")
                st.caption("El sistema opera dentro de parámetros seguros")
        
        # Cálculo de Cotas
        with st.expander("📏 Cálculo de Cotas", expanded=False):
            st.markdown("### 🗺️ Cotas del Sistema")
            
            # Obtener datos de session_state
            cota_eje_bomba = st.session_state.get('elevacion_sitio', 450.0)
            altura_succion = st.session_state.get('altura_succion_input', 2.0)
            altura_descarga = st.session_state.get('altura_descarga', 80.0)
            bomba_inundada = st.session_state.get('bomba_inundada', False)
            nivel_agua_succion = st.session_state.get('nivel_agua_tanque', 1.59)
            
            # Inputs de profundidad de tanques
            st.markdown("#### 🏗️ Profundidad de Tanques")
            col_prof1, col_prof2 = st.columns(2)
            
            with col_prof1:
                prof_tanque_succion = st.number_input(
                    "Profundidad Tanque Succión (m)",
                    min_value=0.0,
                    value=3.0,
                    step=0.1,
                    key="prof_tanque_succion_cv",
                    help="Profundidad desde nivel de agua hasta solera del tanque"
                )
            
            with col_prof2:
                prof_tanque_descarga = st.number_input(
                    "Profundidad Tanque Descarga (m)",
                    min_value=0.0,
                    value=3.0,
                    step=0.1,
                    key="prof_tanque_descarga_cv",
                    help="Profundidad desde nivel de agua hasta solera del tanque"
                )
            
            st.markdown("---")
            st.markdown("#### 📍 Cotas Calculadas")
            
            # Cálculos de cotas
            if bomba_inundada:
                # Bomba debajo del tanque
                cota_nivel_agua_succion = cota_eje_bomba + altura_succion
                cota_solera_succion = cota_nivel_agua_succion - prof_tanque_succion
            else:
                # Bomba arriba del tanque
                cota_nivel_agua_succion = cota_eje_bomba - altura_succion
                cota_solera_succion = cota_nivel_agua_succion - prof_tanque_succion
            
            cota_nivel_agua_descarga = cota_eje_bomba + altura_descarga
            cota_solera_descarga = cota_nivel_agua_descarga - prof_tanque_descarga
            
            # Mostrar resultados en dos columnas
            col_cota1, col_cota2 = st.columns(2)
            
            with col_cota1:
                st.markdown("**🔵 Tanque de Succión**")
                st.metric("Cota Nivel de Agua", f"{cota_nivel_agua_succion:.2f} m.s.n.m.")
                st.metric("Cota Solera Tanque", f"{cota_solera_succion:.2f} m.s.n.m.")
                st.caption(f"Profundidad: {prof_tanque_succion:.2f} m")
            
            with col_cota2:
                st.markdown("**🔴 Tanque de Descarga**")
                st.metric("Cota Nivel de Agua", f"{cota_nivel_agua_descarga:.2f} m.s.n.m.")
                st.metric("Cota Solera Tanque", f"{cota_solera_descarga:.2f} m.s.n.m.")
                st.caption(f"Profundidad: {prof_tanque_descarga:.2f} m")
            
            st.markdown("---")
            st.info(f"**🎯 Cota Eje de Bomba:** {cota_eje_bomba:.2f} m.s.n.m.")
            
            # Diagrama visual simplificado
            st.markdown("#### 📊 Perfil Altimétrico")
            
            # Crear gráfico de perfil según coordenadas exactas
            fig_perfil = go.Figure()
            
            # Coordenadas según esquema: (x, y)
            # 1: (0, STS), 2: (0, NAS), 3: (0, EB), 4: (1, EB), 5: (2, EB), 6: (3, EB), 7: (3, STI), 8: (3, NAI)
            
            # Línea completa del perfil
            x_coords = [0, 0, 0, 1, 2, 3, 3, 3]
            y_coords = [
                cota_solera_succion,      # 1. STS
                cota_nivel_agua_succion,  # 2. NAS
                cota_eje_bomba,           # 3. EB
                cota_eje_bomba,           # 4. EB
                cota_eje_bomba,           # 5. EB
                cota_eje_bomba,           # 6. EB
                cota_solera_descarga,     # 7. STI
                cota_nivel_agua_descarga  # 8. NAI
            ]
            
            # Dibujar línea principal del perfil
            fig_perfil.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='lines+markers',
                line=dict(color='darkblue', width=3),
                marker=dict(size=12, color='darkblue'),
                showlegend=False
            ))
            
            # Destacar la bomba (puntos 3-6)
            fig_perfil.add_trace(go.Scatter(
                x=[0, 1, 2, 3],
                y=[cota_eje_bomba, cota_eje_bomba, cota_eje_bomba, cota_eje_bomba],
                mode='markers+text',
                marker=dict(size=15, color='green', symbol='square', line=dict(width=2, color='darkgreen')),
                text=['', '', '', ''],
                showlegend=False
            ))
            
            # Anotaciones de texto con colores visibles
            annotations = [
                dict(x=0-0.15, y=cota_solera_succion, text=f"1. STS<br>{cota_solera_succion:.1f} m", 
                     showarrow=False, xanchor='right', font=dict(size=11, color='darkblue')),
                dict(x=0-0.15, y=cota_nivel_agua_succion, text=f"2. NAS<br>{cota_nivel_agua_succion:.1f} m", 
                     showarrow=False, xanchor='right', font=dict(size=11, color='blue')),
                dict(x=0-0.15, y=cota_eje_bomba, text=f"3. EB<br>{cota_eje_bomba:.1f} m", 
                     showarrow=False, xanchor='right', font=dict(size=11, color='green')),
                dict(x=1.5, y=cota_eje_bomba+8, text="BOMBA", 
                     showarrow=False, font=dict(size=13, color='green', family='Arial Black')),
                dict(x=3+0.15, y=cota_solera_descarga, text=f"7. STI<br>{cota_solera_descarga:.1f} m", 
                     showarrow=False, xanchor='left', font=dict(size=11, color='darkred')),
                dict(x=3+0.15, y=cota_nivel_agua_descarga, text=f"8. NAI<br>{cota_nivel_agua_descarga:.1f} m", 
                     showarrow=False, xanchor='left', font=dict(size=11, color='red'))
            ]
            
            fig_perfil.update_layout(
                title="Perfil Altimétrico del Sistema",
                xaxis_title="",
                yaxis_title="Cota (m.s.n.m.)",
                height=400,
                xaxis=dict(showticklabels=False, range=[-0.5, 3.5]),
                yaxis=dict(gridcolor='lightgray'),
                annotations=annotations
            )
            
            st.plotly_chart(fig_perfil, use_container_width=True, key="perfil_cierre_valvula")
