# Cálculos principales del sistema de análisis de bombas

import math
import numpy as np
from typing import List, Tuple, Dict, Any
from config.constants import HAZEN_WILLIAMS_C, ACCESORIOS_DATA, MOTORES_ESTANDAR, TUBERIAS_DATA, PEAD_DATA, HIERRO_DUCTIL_DATA, HIERRO_FUNDIDO_DATA, PVC_DATA

def interpolar_propiedad(valor: float, x: List[float], y: List[float]) -> float:
    """
    Interpola linealmente el valor dado en los arrays x (independiente) y y (dependiente).
    Si el valor está fuera del rango, retorna el valor más cercano.
    """
    x = np.array(x)
    y = np.array(y)
    if valor <= x[0]:
        return y[0]
    elif valor >= x[-1]:
        return y[-1]
    else:
        return float(np.interp(valor, x, y))

def calcular_hf_hazen_williams(caudal_m3s: float, longitud: float, diametro_m: float, C: float) -> float:
    """
    Calcula las pérdidas por fricción usando la ecuación de Hazen-Williams.
    
    Args:
        caudal_m3s: Caudal en m³/s
        longitud: Longitud de la tubería en metros
        diametro_m: Diámetro interno en metros
        C: Coeficiente de Hazen-Williams
    
    Returns:
        Pérdidas por fricción en metros
    """
    # Asegurarse de que caudal_m3s sea un escalar numérico
    caudal_m3s_scalar = float(caudal_m3s)
    if C == 0 or diametro_m == 0 or caudal_m3s_scalar <= 0:
        return 0
    return 10.67 * longitud * math.pow(caudal_m3s_scalar / C, 1.852) / math.pow(diametro_m, 4.87)

def get_le_over_d(accessory_type: str, D1_mm: float = None, D2_mm: float = None) -> float:
    """
    Devuelve el valor de Le/D para un accesorio dado.
    Para accesorios con k variable, devuelve Le/D = 0 por simplicidad.
    
    Args:
        accessory_type: Tipo de accesorio
        D1_mm: Diámetro 1 en mm (opcional)
        D2_mm: Diámetro 2 en mm (opcional)
    
    Returns:
        Valor de Le/D para el accesorio
    """
    # Buscar en todas las categorías de accesorios
    for categoria in ["valvulas", "accesorios", "medidores"]:
        if categoria in ACCESORIOS_DATA:
            for item in ACCESORIOS_DATA[categoria]:
                # Buscar por singularidad o tipo
                if (item.get("singularidad") == accessory_type or 
                    item.get("tipo") == accessory_type):
                    return item.get("lc_d_medio", 0)
    
    return 0

def convert_flow_unit(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convierte unidades de caudal.
    
    Args:
        value: Valor a convertir
        from_unit: Unidad de origen
        to_unit: Unidad de destino
    
    Returns:
        Valor convertido
    """
    # Conversiones a m³/s
    to_m3s = {
        'L/s': value / 1000,
        'm³/s': value,
        'm³/h': value / 3600,
        'L/min': value / 60000,
        'GPM': value * 0.00006309,  # Galones por minuto a m³/s
        'CFM': value * 0.000471947  # Pies cúbicos por minuto a m³/s
    }
    
    # Conversiones desde m³/s
    from_m3s = {
        'L/s': to_m3s[from_unit] * 1000,
        'm³/s': to_m3s[from_unit],
        'm³/h': to_m3s[from_unit] * 3600,
        'L/min': to_m3s[from_unit] * 60000,
        'GPM': to_m3s[from_unit] / 0.00006309,
        'CFM': to_m3s[from_unit] / 0.000471947
    }
    
    return from_m3s.get(to_unit, value)

def get_display_unit_label(unit: str) -> str:
    """
    Obtiene la etiqueta de visualización para una unidad.
    
    Args:
        unit: Unidad de caudal
    
    Returns:
        Etiqueta de visualización
    """
    labels = {
        'L/s': 'L/s',
        'm³/h': 'm³/h',
        'm³/s': 'm³/s',
        'L/min': 'L/min',
        'GPM': 'GPM',
        'CFM': 'CFM'
    }
    return labels.get(unit, unit)

def convert_curve_data_to_display_unit(curve_data: List[Tuple[float, float]], 
                                     from_unit: str, to_unit: str) -> List[Tuple[float, float]]:
    """
    Convierte los datos de una curva a la unidad de visualización.
    
    Args:
        curve_data: Lista de tuplas (caudal, altura)
        from_unit: Unidad de origen
        to_unit: Unidad de destino
    
    Returns:
        Lista de tuplas convertidas
    """
    converted_data = []
    for q, h in curve_data:
        converted_q = convert_flow_unit(q, from_unit, to_unit)
        converted_data.append((converted_q, h))
    return converted_data

def calculate_system_head(q_display_unit: float, flow_unit: str, h_estatica: float,
                         long_succion: float, diam_succion_m: float, C_succion: float, 
                         accesorios_succion: List[Dict], otras_perdidas_succion: float,
                         long_impulsion: float, diam_impulsion_m: float, C_impulsion: float, 
                         accesorios_impulsion: List[Dict], otras_perdidas_impulsion: float) -> float:
    """
    Calcula la altura total del sistema (ADT).
    
    Args:
        q_display_unit: Caudal en unidad de visualización
        flow_unit: Unidad de caudal
        h_estatica: Altura estática
        long_succion: Longitud de succión
        diam_succion_m: Diámetro de succión en metros
        C_succion: Coeficiente de Hazen-Williams de succión
        accesorios_succion: Lista de accesorios de succión
        otras_perdidas_succion: Otras pérdidas de succión
        long_impulsion: Longitud de impulsión
        diam_impulsion_m: Diámetro de impulsión en metros
        C_impulsion: Coeficiente de Hazen-Williams de impulsión
        accesorios_impulsion: Lista de accesorios de impulsión
        otras_perdidas_impulsion: Otras pérdidas de impulsión
    
    Returns:
        Altura total del sistema (ADT) en metros
    """
    q_m3s = convert_flow_unit(q_display_unit, flow_unit, 'm³/s')

    # Succión
    hf_primaria_succion = calcular_hf_hazen_williams(q_m3s, long_succion, diam_succion_m, C_succion)
    # Calcular longitud equivalente total: Le/D * cantidad * diámetro (en metros)
    diam_succion_mm = diam_succion_m * 1000
    le_total_succion = sum(get_le_over_d(acc['tipo'], diam_succion_mm, acc.get('diam2_mm')) * acc['cantidad'] * diam_succion_m for acc in accesorios_succion)
    hf_secundaria_succion = calcular_hf_hazen_williams(q_m3s, le_total_succion, diam_succion_m, C_succion)
    perdida_total_succion = hf_primaria_succion + hf_secundaria_succion + otras_perdidas_succion

    # Impulsión
    hf_primaria_impulsion = calcular_hf_hazen_williams(q_m3s, long_impulsion, diam_impulsion_m, C_impulsion)
    # Calcular longitud equivalente total: Le/D * cantidad * diámetro (en metros)
    diam_impulsion_mm = diam_impulsion_m * 1000
    le_total_impulsion = sum(get_le_over_d(acc['tipo'], diam_impulsion_mm, acc.get('diam2_mm')) * acc['cantidad'] * diam_impulsion_m for acc in accesorios_impulsion)
    hf_secundaria_impulsion = calcular_hf_hazen_williams(q_m3s, le_total_impulsion, diam_impulsion_m, C_impulsion)
    perdida_total_impulsion = hf_primaria_impulsion + hf_secundaria_impulsion + otras_perdidas_impulsion
    
    adt = h_estatica + perdida_total_succion + perdida_total_impulsion
    return adt

def find_operating_point(pump_curve_data_m3h: List[Tuple[float, float]], 
                        system_params: Dict[str, Any], 
                        display_flow_unit: str) -> Tuple[float, float]:
    """
    Encuentra el punto de operación entre la curva de la bomba y el sistema.
    
    Args:
        pump_curve_data_m3h: Datos de la curva de la bomba en m³/h
        system_params: Parámetros del sistema
        display_flow_unit: Unidad de caudal para visualización
    
    Returns:
        Tupla (caudal, altura) del punto de operación
    """
    pump_q_m3h = np.array([p[0] for p in pump_curve_data_m3h])
    pump_h_m3h = np.array([p[1] for p in pump_curve_data_m3h])

    # Verificar si la curva de la bomba es válida
    if len(pump_q_m3h) < 2:
        return (0, 0)

    # Generar puntos del sistema para diferentes caudales usando el motor unificado
    system_flows = np.linspace(0, pump_q_m3h.max(), 100).tolist()
    
    # Convertir caudales a la unidad de visualización para el motor
    display_flows = [convert_flow_unit(f, 'm³/h', display_flow_unit) for f in system_flows]
    
    resultados_adt = calculate_adt_for_multiple_flows(display_flows, display_flow_unit, system_params)
    system_heads = np.array([r['adt_total'] for r in resultados_adt])
    
    # Encontrar intersección
    diff = pump_h_m3h - np.interp(pump_q_m3h, system_flows, system_heads)
    sign_changes = np.where(np.diff(np.sign(diff)))[0]
    
    if len(sign_changes) > 0:
        idx = sign_changes[0]
        # Interpolación lineal para encontrar el punto exacto
        x1, x2 = pump_q_m3h[idx], pump_q_m3h[idx + 1]
        y1, y2 = diff[idx], diff[idx + 1]
        
        if abs(y2 - y1) > 1e-9:
            intersection_q = x1 - y1 * (x2 - x1) / (y2 - y1)
            intersection_h = np.interp(intersection_q, pump_q_m3h, pump_h_m3h)
            return (intersection_q, intersection_h)
    
    return (0, 0)

def calculate_adt_for_multiple_flows(flows: List[float], flow_unit: str, 
                                   system_params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Calcula la altura total del sistema (ADT) para múltiples caudales.
    Soporta Hazen-Williams y Darcy-Weisbach.
    
    Args:
        flows: Lista de caudales
        flow_unit: Unidad de caudal
        system_params: Parámetros del sistema
    
    Returns:
        Lista de diccionarios con resultados detallados
    """
    from core.hydraulics import calcular_perdidas_darcy_weisbach
    
    resultados = []
    
    # Extraer parámetros generales
    metodo = system_params.get('metodo_calculo', 'Hazen-Williams')
    temp = system_params.get('temp_liquido', 20.0)
    bomba_inundada = system_params.get('bomba_inundada', False)
    altura_succion_val = system_params.get('altura_succion', 0.0)
    altura_descarga_val = system_params.get('altura_descarga', 0.0)
    
    # Altura Estática Total (Hs = Z_descarga - Z_nivel_agua)
    if bomba_inundada:
        z_nivel_agua = +altura_succion_val  # Agua POR ENCIMA de la bomba
    else:
        z_nivel_agua = -altura_succion_val  # Agua POR DEBAJO de la bomba
        
    altura_estatica_total = altura_descarga_val - z_nivel_agua

    for flow in flows:
        # Convertir caudal a m³/s para cálculos
        caudal_m3s = convert_flow_unit(flow, flow_unit, 'm³/s')
        
        if metodo == 'Darcy-Weisbach':
            # --- CÁLCULO POR DARCY-WEISBACH ---
            # Succión
            res_suc = calcular_perdidas_darcy_weisbach(
                caudal_m3s, system_params['long_succion'], 
                system_params['diam_succion_m'], system_params['mat_succion'], temp
            )
            hf_primaria_succion = res_suc['hf']
            
            # Guardar el método en los detalles para la UI
            res_suc['metodo'] = 'Darcy-Weisbach'
            detalles_darcy_suc = res_suc
            
            # Longitud equivalente para accesorios
            le_total_succion = 0
            for acc in system_params['accesorios_succion']:
                if 'lc_d' in acc and acc['lc_d'] is not None:
                    le_over_d_val = float(acc['lc_d'])
                else:
                    diam_succion_mm = system_params['diam_succion_m'] * 1000
                    le_over_d_val = get_le_over_d(acc['tipo'], diam_succion_mm, acc.get('diam2_mm'))
                le_total_succion += le_over_d_val * acc['cantidad'] * system_params['diam_succion_m']
            
            res_sec_suc = calcular_perdidas_darcy_weisbach(
                caudal_m3s, le_total_succion, 
                system_params['diam_succion_m'], system_params['mat_succion'], temp
            )
            hf_secundaria_succion = res_sec_suc['hf']
            
            # Impulsión
            res_imp = calcular_perdidas_darcy_weisbach(
                caudal_m3s, system_params['long_impulsion'], 
                system_params['diam_impulsion_m'], system_params['mat_impulsion'], temp
            )
            hf_primaria_impulsion = res_imp['hf']
            
            # Guardar el método en los detalles para la UI
            res_imp['metodo'] = 'Darcy-Weisbach'
            detalles_darcy_imp = res_imp
            
            # Longitud equivalente para accesorios
            le_total_impulsion = 0
            for acc in system_params['accesorios_impulsion']:
                if 'lc_d' in acc and acc['lc_d'] is not None:
                    le_over_d_val = float(acc['lc_d'])
                else:
                    diam_impulsion_mm = system_params['diam_impulsion_m'] * 1000
                    le_over_d_val = get_le_over_d(acc['tipo'], diam_impulsion_mm, acc.get('diam2_mm'))
                le_total_impulsion += le_over_d_val * acc['cantidad'] * system_params['diam_impulsion_m']
            
            res_sec_imp = calcular_perdidas_darcy_weisbach(
                caudal_m3s, le_total_impulsion, 
                system_params['diam_impulsion_m'], system_params['mat_impulsion'], temp
            )
            hf_secundaria_impulsion = res_sec_imp['hf']
            
        else:
            # --- CÁLCULO POR HAZEN-WILLIAMS ---
            detalles_darcy_suc = {}
            detalles_darcy_imp = {}
            # Succión
            hf_primaria_succion = calcular_hf_hazen_williams(
                caudal_m3s, system_params['long_succion'], 
                system_params['diam_succion_m'], system_params['C_succion']
            )
            
            le_total_succion = 0
            for acc in system_params['accesorios_succion']:
                if 'lc_d' in acc and acc['lc_d'] is not None:
                    le_over_d_val = float(acc['lc_d'])
                else:
                    diam_succion_mm = system_params['diam_succion_m'] * 1000
                    le_over_d_val = get_le_over_d(acc['tipo'], diam_succion_mm, acc.get('diam2_mm'))
                le_total_succion += le_over_d_val * acc['cantidad'] * system_params['diam_succion_m']
            
            hf_secundaria_succion = calcular_hf_hazen_williams(
                caudal_m3s, le_total_succion, 
                system_params['diam_succion_m'], system_params['C_succion']
            )
            
            # Impulsión
            hf_primaria_impulsion = calcular_hf_hazen_williams(
                caudal_m3s, system_params['long_impulsion'], 
                system_params['diam_impulsion_m'], system_params['C_impulsion']
            )
            
            le_total_impulsion = 0
            for acc in system_params['accesorios_impulsion']:
                if 'lc_d' in acc and acc['lc_d'] is not None:
                    le_over_d_val = float(acc['lc_d'])
                else:
                    diam_impulsion_mm = system_params['diam_impulsion_m'] * 1000
                    le_over_d_val = get_le_over_d(acc['tipo'], diam_impulsion_mm, acc.get('diam2_mm'))
                le_total_impulsion += le_over_d_val * acc['cantidad'] * system_params['diam_impulsion_m']
            
            hf_secundaria_impulsion = calcular_hf_hazen_williams(
                caudal_m3s, le_total_impulsion, 
                system_params['diam_impulsion_m'], system_params['C_impulsion']
            )
        
        # Totales
        perdida_total_succion = hf_primaria_succion + hf_secundaria_succion + system_params.get('otras_perdidas_succion', 0.0)
        perdida_total_impulsion = hf_primaria_impulsion + hf_secundaria_impulsion + system_params.get('otras_perdidas_impulsion', 0.0)
        
        perdidas_totales = perdida_total_succion + perdida_total_impulsion
        adt_total = altura_estatica_total + perdidas_totales
        
        # Convertir caudal a diferentes unidades para el resultado
        caudal_lps = convert_flow_unit(flow, flow_unit, 'L/s')
        caudal_m3h = convert_flow_unit(flow, flow_unit, 'm³/h')
        
        resultados.append({
            'caudal_lps': caudal_lps,
            'caudal_m3h': caudal_m3h,
            'perdida_succion': perdida_total_succion,
            'perdida_impulsion': perdida_total_impulsion,
            'altura_estatica_total': altura_estatica_total,
            'adt_total': adt_total,
            'hf_primaria_succion': hf_primaria_succion,
            'hf_secundaria_succion': hf_secundaria_succion,
            'hf_primaria_impulsion': hf_primaria_impulsion,
            'hf_secundaria_impulsion': hf_secundaria_impulsion,
            'detalles_darcy_suc': detalles_darcy_suc,
            'detalles_darcy_imp': detalles_darcy_imp
        })
    
    return resultados

def process_curve_data(curva_inputs: Dict[str, str]) -> Dict[str, List[Tuple[float, float]]]:
    """
    Procesa los datos de los text areas de las curvas y los convierte en listas de tuplas.
    Migrado desde ../app.py
    
    Args:
        curva_inputs: Diccionario con los datos de entrada de las curvas
    
    Returns:
        Diccionario con las curvas procesadas
    """
    curva_names = [
        ("Curva del Sistema (H-Q)", "sistema"),
        ("Curva de la Bomba (H-Q)", "bomba"),
        ("Curva de Rendimiento (η-Q)", "rendimiento"),
        ("Curva de Potencia (PBHP-Q)", "potencia"),
        ("Curva de NPSH Requerido (NPSHR-Q)", "npsh")
    ]
    
    processed_curves = {}
    
    for curva_label, curva_key in curva_names:
        # Obtener el contenido del text area
        text_area_key = f"textarea_{curva_key}"
        if text_area_key in curva_inputs:
            puntos_str = curva_inputs[text_area_key]
            puntos = []
            
            # Detectar si el input es vertical (columnas) o horizontal (filas)
            lines = [line.strip() for line in puntos_str.splitlines() if line.strip()]
            # Si hay al menos dos líneas y cada línea tiene un solo valor, es vertical
            if len(lines) >= 2 and all(len(line.split()) == 1 for line in lines):
                # Input vertical: cada línea es un valor
                if len(lines) % 2 == 0:  # Debe ser par para tener pares x,y
                    for i in range(0, len(lines), 2):
                        try:
                            x = float(lines[i])
                            y = float(lines[i + 1])
                            puntos.append((x, y))
                        except ValueError:
                            continue
            else:
                # Input horizontal: cada línea tiene pares x,y
                for line in lines:
                    # Separar por espacio, coma o punto y coma
                    parts = line.replace(',', ' ').replace(';', ' ').split()
                    if len(parts) >= 2:
                        try:
                            x = float(parts[0])
                            y = float(parts[1])
                            puntos.append((x, y))
                        except ValueError:
                            continue
            
            processed_curves[curva_key] = puntos
    
    return processed_curves

def convert_curve_data(curve_data: List[Tuple[float, float]], from_unit: str, to_unit: str) -> List[Tuple[float, float]]:
    """
    Convierte los datos de una curva de una unidad a otra.
    Migrado desde ../app.py
    
    Args:
        curve_data: Lista de tuplas (caudal, altura)
        from_unit: Unidad de origen
        to_unit: Unidad de destino
    
    Returns:
        Lista de tuplas convertidas
    """
    converted_data = []
    for q, h in curve_data:
        converted_data.append((convert_flow_unit(q, from_unit, to_unit), h))
    return converted_data

def calcular_presion_atmosferica_mca(elevacion: float, gamma: float) -> float:
    """
    Calcula la presión atmosférica en metros de columna de agua (m.c.a.).
    Migrado desde ../app.py
    
    Args:
        elevacion: Elevación sobre el nivel del mar en metros
        gamma: Peso específico del agua en N/m³
    
    Returns:
        Presión atmosférica en m.c.a.
    """
    altitude_m = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200, 1250, 1300, 1350, 1400, 1450, 1500, 1550, 1600, 1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000, 2050, 2100, 2150, 2200, 2250, 2300, 2350, 2400, 2450, 2500, 2550, 2600, 2650, 2700, 2750, 2800, 2850, 2900, 2950, 3000, 3050, 3100, 3150, 3200, 3250, 3300, 3350, 3400, 3450, 3500, 3550, 3600, 3650, 3700, 3750, 3800, 3850, 3900, 3950, 4000, 4050, 4100, 4150, 4200, 4250, 4300, 4350, 4400, 4450, 4500, 4550, 4600, 4650, 4700, 4750, 4800, 4850, 4900, 4950, 5000, 5050, 5100, 5150, 5200, 5250, 5300, 5350, 5400, 5450, 5500, 5550, 5600, 5650, 5700, 5750, 5800, 5850, 5900, 5950]
    pressure_mbar = [1013, 1007, 1001, 995, 989, 984, 978, 972, 966, 960, 955, 949, 943, 938, 932, 926, 921, 915, 910, 904, 899, 893, 888, 883, 877, 872, 867, 861, 856, 851, 846, 840, 835, 830, 825, 820, 815, 810, 805, 800, 795, 790, 785, 780, 775, 771, 766, 761, 756, 752, 747, 742, 737, 733, 728, 724, 719, 715, 710, 706, 701, 697, 692, 688, 683, 679, 675, 670, 666, 662, 658, 653, 649, 645, 641, 637, 633, 629, 624, 620, 616, 612, 608, 604, 600, 597, 593, 589, 585, 581, 577, 573, 570, 566, 562, 558, 555, 551, 547, 544, 540, 537, 533, 529, 526, 522, 519, 515, 512, 508, 505, 502, 498, 495, 492, 488, 485, 482, 478, 475]
    
    presion_mbar_interpolada = interpolar_propiedad(elevacion, altitude_m, pressure_mbar)
    presion_pa = presion_mbar_interpolada * 100
    
    if gamma == 0:
        return 0
    
    return presion_pa / gamma

def get_motor_data(potencia_hp: float) -> Dict[str, Any]:
    """
    Obtiene los datos de un motor estándar basado en la potencia en HP.
    
    Args:
        potencia_hp: Potencia del motor en HP
    
    Returns:
        Diccionario con los datos del motor o None si no se encuentra
    """
    for motor in MOTORES_ESTANDAR:
        if abs(motor.get("potencia_hp", 0) - potencia_hp) < 0.01:  # Tolerancia de 0.01 HP
            return motor
    return None

def seleccionar_motor_estandar(potencia_calculada_hp: float) -> Dict[str, Any]:
    """
    Selecciona automáticamente el motor estándar inmediato superior al calculado.
    
    Args:
        potencia_calculada_hp: Potencia calculada en HP
    
    Returns:
        Diccionario con los datos del motor seleccionado o None si no se encuentra
    """
    if not MOTORES_ESTANDAR or potencia_calculada_hp <= 0:
        return None
    
    # Ordenar motores por potencia
    motores_ordenados = sorted(MOTORES_ESTANDAR, key=lambda x: x.get("potencia_hp", 0))
    
    # Buscar el motor inmediato superior
    for motor in motores_ordenados:
        if motor.get("potencia_hp", 0) >= potencia_calculada_hp:
            return motor
    
    # Si no se encuentra uno superior, devolver el más potente
    return motores_ordenados[-1] if motores_ordenados else None

def calcular_potencia_motor(caudal_m3s: float, altura_m: float, eficiencia_bomba: float = 0.75, 
                           eficiencia_motor: float = 0.85, gamma: float = 9810) -> float:
    """
    Calcula la potencia del motor en HP.
    
    Args:
        caudal_m3s: Caudal en m³/s
        altura_m: Altura en metros
        eficiencia_bomba: Eficiencia de la bomba (por defecto 75%)
        eficiencia_motor: Eficiencia del motor (por defecto 85%)
        gamma: Peso específico del agua en N/m³
    
    Returns:
        Potencia del motor en HP
    """
    if caudal_m3s <= 0 or altura_m <= 0 or eficiencia_bomba <= 0 or eficiencia_motor <= 0:
        return 0
    
    # Potencia hidráulica en W
    potencia_hidraulica_w = gamma * caudal_m3s * altura_m
    
    # Potencia del motor en W (considerando eficiencias)
    potencia_motor_w = potencia_hidraulica_w / (eficiencia_bomba * eficiencia_motor)
    
    # Convertir a HP (1 HP = 745.7 W)
    potencia_motor_hp = potencia_motor_w / 745.7
    
    return potencia_motor_hp

def get_tuberia_data(material: str) -> Dict[str, Any]:
    """
    Obtiene los datos de una tubería basado en el material.
    
    Args:
        material: Material de la tubería
    
    Returns:
        Diccionario con los datos de la tubería o None si no se encuentra
    """
    for tuberia in TUBERIAS_DATA:
        if tuberia.get("material", "").lower() == material.lower():
            return tuberia
    return None

def get_pead_data(diametro_externo_mm: float) -> Dict[str, Any]:
    """
    Obtiene los datos de una tubería PEAD basado en el diámetro externo.
    
    Args:
        diametro_externo_mm: Diámetro externo en mm
    
    Returns:
        Diccionario con los datos de la tubería PEAD o None si no se encuentra
    """
    for tuberia in PEAD_DATA:
        if tuberia.get("diametro_nominal_mm") == diametro_externo_mm:
            return tuberia
    return None

def get_pead_espesor(diametro_externo_mm: float, serie: str) -> float:
    """
    Obtiene el espesor de pared para una tubería PEAD específica.
    
    Args:
        diametro_externo_mm: Diámetro externo en mm
        serie: Serie del tubo (s12_5, s10, s8, s6_3, s5, s4)
    
    Returns:
        Espesor en mm o None si no está disponible
    """
    tuberia_data = get_pead_data(diametro_externo_mm)
    if tuberia_data and serie in tuberia_data:
        serie_data = tuberia_data[serie]
        return serie_data.get("espesor_mm")
    return None

def calculate_diametro_interno_pead(diametro_externo_mm: float, espesor_mm: float) -> float | None:
    """
    Calcula el diámetro interno para tubería PEAD.
    
    Args:
        diametro_externo_mm: Diámetro externo en mm
        espesor_mm: Espesor de pared en mm
    
    Returns:
        Diámetro interno en mm
    """
    if espesor_mm is None:
        return None
    return diametro_externo_mm - 2 * espesor_mm

def get_hazen_williams_coefficient(material: str) -> float:
    """
    Obtiene el coeficiente C de Hazen-Williams para un material dado.
    
    Args:
        material: Material de la tubería
    
    Returns:
        Coeficiente C de Hazen-Williams o 150 por defecto
    """
    return HAZEN_WILLIAMS_C.get(material, 150)

def get_hierro_ductil_data(clase: str, dn_mm: float) -> Dict[str, Any]:
    """
    Obtiene los datos de una tubería de hierro dúctil basado en la clase y diámetro nominal.
    
    Args:
        clase: Clase de presión (C20, C25, C30, C40)
        dn_mm: Diámetro nominal en mm
    
    Returns:
        Diccionario con los datos de la tubería o None si no se encuentra
    """
    if clase not in HIERRO_DUCTIL_DATA:
        return None
    
    clase_data = HIERRO_DUCTIL_DATA[clase]
    tuberias = clase_data.get("tuberias", [])
    
    for tuberia in tuberias:
        if tuberia.get("dn_mm") == dn_mm:
            return {
                "dn_mm": tuberia["dn_mm"],
                "de_mm": tuberia["de_mm"],
                "espesor_nominal_mm": tuberia["espesor_nominal_mm"],
                "espesor_minimo_mm": tuberia["espesor_minimo_mm"],
                "pfa_bar": clase_data["pfa_bar"],
                "pma_bar": clase_data["pma_bar"],
                "rigidez_kn_m2": tuberia["rigidez_kn_m2"],
                "deflexion_admisible_porcentaje": tuberia["deflexion_admisible_porcentaje"],
                "clase": clase,
                "descripcion": clase_data["descripcion"]
            }
    return None

def get_hierro_ductil_diametros_disponibles(clase: str) -> List[float]:
    """
    Obtiene los diámetros nominales disponibles para una clase de hierro dúctil.
    
    Args:
        clase: Clase de presión (C20, C25, C30, C40)
    
    Returns:
        Lista de diámetros nominales en mm
    """
    if clase not in HIERRO_DUCTIL_DATA:
        return []
    
    tuberias = HIERRO_DUCTIL_DATA[clase].get("tuberias", [])
    return [tuberia["dn_mm"] for tuberia in tuberias]

def calculate_diametro_interno_hierro_ductil(de_mm: float, espesor_nominal_mm: float) -> float:
    """
    Calcula el diámetro interno para tubería de hierro dúctil.
    
    Args:
        de_mm: Diámetro externo en mm
        espesor_nominal_mm: Espesor nominal en mm
    
    Returns:
        Diámetro interno en mm
    """
    return de_mm - 2 * espesor_nominal_mm

def get_hierro_fundido_data(clase: str, dn_mm: float) -> Dict[str, Any]:
    """
    Obtiene los datos de una tubería de hierro fundido basado en la clase y diámetro nominal.
    
    Args:
        clase: Clase de presión (clase_150, clase_125, clase_100)
        dn_mm: Diámetro nominal en mm
    
    Returns:
        Diccionario con los datos de la tubería o None si no se encuentra
    """
    if clase not in HIERRO_FUNDIDO_DATA:
        return None
    
    clase_data = HIERRO_FUNDIDO_DATA[clase]
    tuberias = clase_data.get("tuberias", [])
    
    for tuberia in tuberias:
        if tuberia.get("dn_mm") == dn_mm:
            return {
                "dn_mm": tuberia["dn_mm"],
                "de_mm": tuberia["de_mm"],
                "espesor_mm": tuberia["espesor_mm"],
                "di_mm": tuberia["di_mm"],
                "peso_kg_m": tuberia["peso_kg_m"],
                "pfa_bar": clase_data["pfa_bar"],
                "pma_bar": clase_data["pma_bar"],
                "clase": clase,
                "descripcion": clase_data["descripcion"]
            }
    return None

def get_hierro_fundido_diametros_disponibles(clase: str) -> List[float]:
    """
    Obtiene los diámetros nominales disponibles para una clase de hierro fundido.
    
    Args:
        clase: Clase de presión (clase_150, clase_125, clase_100)
    
    Returns:
        Lista de diámetros nominales en mm
    """
    if clase not in HIERRO_FUNDIDO_DATA:
        return []
    
    tuberias = HIERRO_FUNDIDO_DATA[clase].get("tuberias", [])
    return [tuberia["dn_mm"] for tuberia in tuberias]

def get_pvc_data(tipo_union: str, serie: str, dn_mm: float) -> Dict[str, Any]:
    """
    Obtiene los datos de una tubería PVC basado en el tipo de unión, serie y diámetro nominal.
    
    Args:
        tipo_union: Tipo de unión (union_elastomerica, union_espiga_campana)
        serie: Serie del tubo (s20, s16, s12_5, s10, s8, s6_3)
        dn_mm: Diámetro nominal en mm
    
    Returns:
        Diccionario con los datos de la tubería o None si no se encuentra
    """
    if tipo_union not in PVC_DATA:
        return None
    
    union_data = PVC_DATA[tipo_union]
    if serie not in union_data.get("series", {}):
        return None
    
    serie_data = union_data["series"][serie]
    tuberias = serie_data.get("tuberias", [])
    
    for tuberia in tuberias:
        if tuberia.get("dn_mm") == dn_mm:
            return {
                "dn_mm": tuberia["dn_mm"],
                "de_mm": tuberia["de_mm"],
                "tolerancia": tuberia["tolerancia"],
                "espesor_min_mm": tuberia["espesor_min_mm"],
                "espesor_max_mm": tuberia["espesor_max_mm"],
                "presion_mpa": serie_data["presion_mpa"],
                "presion_bar": serie_data["presion_bar"],
                "serie": serie_data["serie"],
                "descripcion": serie_data["descripcion"],
                "tipo_union": union_data["tipo"]
            }
    return None

def get_pvc_series_disponibles(tipo_union: str) -> List[str]:
    """
    Obtiene las series disponibles para un tipo de unión PVC.
    
    Args:
        tipo_union: Tipo de unión (union_elastomerica, union_espiga_campana)
    
    Returns:
        Lista de series disponibles
    """
    if tipo_union not in PVC_DATA:
        return []
    
    series = PVC_DATA[tipo_union].get("series", {})
    return list(series.keys())

def get_pvc_diametros_disponibles(tipo_union: str, serie: str) -> List[float]:
    """
    Obtiene los diámetros nominales disponibles para un tipo de unión y serie PVC.
    
    Args:
        tipo_union: Tipo de unión (union_elastomerica, union_espiga_campana)
        serie: Serie del tubo (s20, s16, s12_5, s10, s8, s6_3)
    
    Returns:
        Lista de diámetros nominales en mm
    """
    if tipo_union not in PVC_DATA:
        return []
    
    union_data = PVC_DATA[tipo_union]
    if serie not in union_data.get("series", {}):
        return []
    
    tuberias = union_data["series"][serie].get("tuberias", [])
    return [tuberia["dn_mm"] for tuberia in tuberias]

def calculate_diametro_interno_pvc(de_mm: float, espesor_min_mm: float, espesor_max_mm: float) -> float:
    """
    Calcula el diámetro interno para tubería PVC.
    DI = DE - 2 * (espesor_max + espesor_min) / 2
    
    Args:
        de_mm: Diámetro externo en mm
        espesor_min_mm: Espesor mínimo en mm
        espesor_max_mm: Espesor máximo en mm
    
    Returns:
        Diámetro interno en mm
    """
    espesor_promedio = (espesor_max_mm + espesor_min_mm) / 2
    return de_mm - 2 * espesor_promedio

def get_accessory_data(accessory_type: str) -> Dict[str, Any]:
    """
    Obtiene los datos de un accesorio basado en el tipo.
    
    Args:
        accessory_type: Tipo de accesorio
    
    Returns:
        Diccionario con los datos del accesorio o None si no se encuentra
    """
    for categoria in ["valvulas", "accesorios", "medidores"]:
        if categoria in ACCESORIOS_DATA:
            for item in ACCESORIOS_DATA[categoria]:
                if (item.get("singularidad") == accessory_type or 
                    item.get("tipo") == accessory_type):
                    return item
    return None