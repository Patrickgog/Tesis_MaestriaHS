#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades para exportación EPANET mejorada
Funciones auxiliares para obtener datos del sistema
"""

import streamlit as st
from typing import Dict, Any, Tuple

def obtener_cotas_sistema() -> Dict[str, float]:
    """
    Obtiene todas las cotas del sistema desde session_state
    Calcula cotas de solera y niveles de agua según configuración actual
    
    Returns:
        Dict con todas las cotas del sistema en m.s.n.m.
    """
    # Datos básicos
    cota_eje_bomba = st.session_state.get('elevacion_sitio', 450.0)
    altura_succion = st.session_state.get('altura_succion_input', 2.0)
    altura_descarga = st.session_state.get('altura_descarga', 80.0)
    bomba_inundada = st.session_state.get('bomba_inundada', False)
    nivel_agua_succion = st.session_state.get('nivel_agua_tanque', 1.59)
    
    # Profundidades de tanques
    prof_tanque_succion = st.session_state.get('prof_tanque_succion', 3.0)
    prof_tanque_descarga = st.session_state.get('prof_tanque_descarga', 3.0)
    
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
    
    # Cotas de tuberías (inicio y fin)
    cota_inicio_succion = cota_nivel_agua_succion
    cota_fin_succion = cota_eje_bomba
    cota_inicio_impulsion = cota_eje_bomba
    cota_fin_impulsion = cota_nivel_agua_descarga
    
    # Cota de válvula (misma que solera de tanque descarga)
    cota_valvula = cota_solera_descarga
    
    return {
        'cota_eje_bomba': cota_eje_bomba,
        'cota_solera_succion': cota_solera_succion,
        'cota_nivel_agua_succion': cota_nivel_agua_succion,
        'prof_tanque_succion': prof_tanque_succion,
        'cota_solera_descarga': cota_solera_descarga,
        'cota_nivel_agua_descarga': cota_nivel_agua_descarga,
        'prof_tanque_descarga': prof_tanque_descarga,
        'cota_inicio_succion': cota_inicio_succion,
        'cota_fin_succion': cota_fin_succion,
        'cota_inicio_impulsion': cota_inicio_impulsion,
        'cota_fin_impulsion': cota_fin_impulsion,
        'cota_valvula': cota_valvula,
        'altura_succion': altura_succion,
        'altura_descarga': altura_descarga,
        'bomba_inundada': bomba_inundada
    }

def obtener_propiedades_tuberias() -> Dict[str, Dict[str, Any]]:
    """Obtiene propiedades de tuberías desde session_state"""
    from core.transient_analysis import calculate_wave_speed
    
    succion = {
        'longitud': st.session_state.get('long_succion', 10.0),
        'diametro_interno_mm': st.session_state.get('diam_succion_mm', 61.4),
        'diametro_interno_m': st.session_state.get('diam_succion_mm', 61.4) / 1000.0,
        'espesor_mm': st.session_state.get('espesor_succion', 5.0),
        'material': st.session_state.get('mat_succion', 'PVC'),
        'c_hazen_williams': st.session_state.get('coef_hazen_succion', 150),
        'rugosidad_m': 0.00015,
        'long_equiv_accesorios': st.session_state.get('long_equiv_succion', 0.0),
        'k_accesorios': st.session_state.get('k_total_succion', 0.0),
    }
    
    impulsion = {
        'longitud': st.session_state.get('long_impulsion', 150.0),
        'diametro_interno_mm': st.session_state.get('diam_impulsion_mm', 40.8),
        'diametro_interno_m': st.session_state.get('diam_impulsion_mm', 40.8) / 1000.0,
        'espesor_mm': st.session_state.get('espesor_impulsion', 8.0),
        'material': st.session_state.get('mat_impulsion', 'PVC'),
        'c_hazen_williams': st.session_state.get('coef_hazen_impulsion', 150),
        'rugosidad_m': 0.00015,
        'long_equiv_accesorios': st.session_state.get('long_equiv_impulsion', 0.0),
        'k_accesorios': st.session_state.get('k_total_impulsion', 0.0),
    }
    
    succion['celeridad_ms'] = calculate_wave_speed(
        succion['material'],
        succion['diametro_interno_m'],
        succion['espesor_mm'] / 1000.0
    )
    
    impulsion['celeridad_ms'] = calculate_wave_speed(
        impulsion['material'],
        impulsion['diametro_interno_m'],
        impulsion['espesor_mm'] / 1000.0
    )
    
    return {'succion': succion, 'impulsion': impulsion}

def obtener_propiedades_bomba() -> Dict[str, Any]:
    """Obtiene propiedades de la bomba desde session_state"""
    rpm_nominal = st.session_state.get('rpm_bomba', 3500)
    rpm_percentage = st.session_state.get('rpm_percentage', 100.0)
    rpm_actual = rpm_nominal * (rpm_percentage / 100.0)
    
    # Determinar si usar curvas 100% o VFD basado en rpm_percentage
    use_vfd = rpm_percentage < 99.5  # Si es menos de 100%, usar curvas VFD
    
    # Buscar curvas H-Q
    hq_points = []
    if use_vfd:
        # PRIORIDAD VFD: Usar df_bomba_vfd (ya escalado)
        df_bomba = st.session_state.get('df_bomba_vfd')
        if df_bomba is not None and hasattr(df_bomba, 'values') and len(df_bomba) > 0:
            try:
                hq_points = [(float(row[0]), float(row[1])) for row in df_bomba.values[:20]]
            except:
                pass
    
    if not hq_points:
        # Fallback: curva_inputs['bomba'] (100% RPM)
        curva_inputs = st.session_state.get('curva_inputs', {})
        hq_points = curva_inputs.get('bomba', [])
    
    if not hq_points:
        # Fallback: df_bomba_100 (100% RPM desde tabla)
        df_bomba = st.session_state.get('df_bomba_100')
        if df_bomba is not None and hasattr(df_bomba, 'values') and len(df_bomba) > 0:
            try:
                hq_points = [(float(row[0]), float(row[1])) for row in df_bomba.values[:20]]
            except:
                pass
    
    # Curvas de rendimiento, potencia y NPSH
    rendimiento_points = []
    potencia_points = []
    npsh_points = []
    
    if use_vfd:
        # Usar dataframes VFD ya escalados
        df_eff = st.session_state.get('df_rendimiento_vfd')
        if df_eff is not None and hasattr(df_eff, 'values') and len(df_eff) > 0:
            try:
                rendimiento_points = [(float(row[0]), float(row[1])) for row in df_eff.values[:20]]
            except:
                pass
        
        df_pow = st.session_state.get('df_potencia_vfd')
        if df_pow is not None and hasattr(df_pow, 'values') and len(df_pow) > 0:
            try:
                potencia_points = [(float(row[0]), float(row[1])) for row in df_pow.values[:20]]
            except:
                pass
        
        df_npsh = st.session_state.get('df_npsh_vfd')
        if df_npsh is not None and hasattr(df_npsh, 'values') and len(df_npsh) > 0:
            try:
                npsh_points = [(float(row[0]), float(row[1])) for row in df_npsh.values[:20]]
            except:
                pass
    
    # Fallback a curva_inputs o tablas 100%
    if not rendimiento_points:
        curva_inputs = st.session_state.get('curva_inputs', {})
        rendimiento_points = curva_inputs.get('rendimiento', [])
    if not potencia_points:
        curva_inputs = st.session_state.get('curva_inputs', {})
        potencia_points = curva_inputs.get('potencia', [])
    if not npsh_points:
        curva_inputs = st.session_state.get('curva_inputs', {})
        npsh_points = curva_inputs.get('npsh', [])
    
    curvas = {
        'hq': hq_points,
        'rendimiento': rendimiento_points,
        'potencia': potencia_points,
        'npsh': npsh_points,
    }
    
    eficiencia_motor = st.session_state.get('eficiencia_motor', 90.0)
    
    return {
        'rpm_nominal': rpm_nominal,
        'rpm_percentage': rpm_percentage,
        'rpm_actual': rpm_actual,
        'curvas': curvas,
        'eficiencia_motor': eficiencia_motor,
        'use_vfd': use_vfd
    }

def calcular_coordenadas_geometria(cotas: Dict[str, float]) -> Dict[str, Tuple[float, float]]:
    """Calcula coordenadas X-Y para visualización según geometría real
    
    AJUSTADO (16-dic-2025) para Allievi:
    - Tanque TS: X más a la derecha para que salida sea visible
    - Tanque TD: X significativamente a la derecha para invertir orientación visual
      (el símbolo del tanque se dibujará a la IZQUIERDA del label, mostrando entrada correcta)
    """
    # Coordenadas ajustadas para orientación visual correcta en Allievi
    x_tanque_succion = 10.0      # Movido de 0 → 10 (salida visible a la derecha)
    x_entrada_bomba = 60.0       # Ajustado proporcionalmente de 50 → 60
    x_salida_bomba = 65.0        # Ajustado proporcionalmente de 55 → 65
    x_valvula = 195.0            # Mantenido (punto intermedio antes de tanque)
    x_tanque_descarga = 220.0    # CRÍTICO: Movido de 200 → 220 para invertir visual
                                 # Esto hace que el símbolo del tanque quede a la IZQUIERDA
                                 # del label "TD", mostrando la entrada correctamente
    
    coordenadas = {
        'TANQUE_SUC': (x_tanque_succion, cotas['cota_nivel_agua_succion']),
        'NODO_SUC': (x_entrada_bomba, cotas['cota_eje_bomba']),
        'NODO_IMP': (x_salida_bomba, cotas['cota_eje_bomba']),
        'NODO_VALV': (x_valvula, cotas['cota_valvula']),
        'TANQUE_DESC': (x_tanque_descarga, cotas['cota_nivel_agua_descarga']),
    }
    
    return coordenadas
