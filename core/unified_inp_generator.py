"""
Generador Unificado de Archivos .inp
Genera archivos compatibles con:
- EPANET / WaterGEMS (análisis de bombeo)
- HAMMER (análisis transitorio)

Características:
- Formato adaptable según software destino
- Incluye propiedades para análisis transitorio
- Compatible con análisis de bombeo estándar
"""

import os
from typing import Dict, Literal

def generate_unified_inp(
    data: Dict,
    target_software: Literal['epanet', 'watergems', 'hammer'] = 'epanet',
    analysis_type: Literal['steady', 'transient'] = 'steady',
    rpm_percentage: float = 100.0
) -> str:
    """
    Genera archivo .inp unificado compatible con múltiples software.
    
    Args:
        data: Diccionario con datos del proyecto
        target_software: Software destino ('epanet', 'watergems', 'hammer')
        analysis_type: Tipo de análisis ('steady', 'transient')
        rpm_percentage: Porcentaje de RPM (para VFD)
    
    Returns:
        Contenido del archivo .inp como string
    """
    
    # Extraer datos
    inputs = data['inputs']
    resultados = data['resultados']
    
    # Configuración según software
    use_hazen_williams = target_software in ['hammer', 'watergems']
    include_transient_sections = analysis_type == 'transient'
    include_patterns = target_software == 'hammer' and include_transient_sections
    
    # --- SECCIÓN [TITLE] ---
    title_lines = _generate_title_section(
        inputs, resultados, target_software, analysis_type, rpm_percentage
    )
    
    # --- SECCIÓN [PATTERNS] (solo HAMMER transitorio) ---
    patterns_section = _generate_patterns_section() if include_patterns else ""
    
    # --- SECCIÓN [CURVES] ---
    curves_section = _generate_curves_section(
        data, rpm_percentage, target_software
    )
    
    # --- SECCIÓN [JUNCTIONS] ---
    junctions_section = _generate_junctions_section(
        inputs, resultados, target_software
    )
    
    # --- SECCIÓN [RESERVOIRS] ---
    reservoirs_section = _generate_reservoirs_section(
        inputs, resultados
    )
    
    # --- SECCIÓN [DEMANDS] (solo HAMMER) ---
    demands_section = _generate_demands_section(
        inputs, target_software
    ) if target_software == 'hammer' else ""
    
    # --- SECCIÓN [PIPES] ---
    pipes_section = _generate_pipes_section(
        inputs, resultados, target_software, use_hazen_williams
    )
    
    # --- SECCIÓN [PUMPS] ---
    pumps_section = _generate_pumps_section(
        data, rpm_percentage, target_software
    )
    
    # --- SECCIÓN [STATUS] (solo HAMMER transitorio) ---
    status_section = _generate_status_section() if include_patterns else ""
    
    # --- SECCIÓN [COORDINATES] ---
    coordinates_section = _generate_coordinates_section(
        inputs, resultados
    )
    
    # --- SECCIÓN [TAGS] ---
    tags_section = _generate_tags_section(
        inputs, resultados, target_software
    )
    
    # --- SECCIÓN [LABELS] ---
    labels_section = _generate_labels_section()
    
    # --- SECCIÓN [OPTIONS] ---
    options_section = _generate_options_section(
        target_software, use_hazen_williams
    )
    
    # Ensamblar archivo según orden del software
    if target_software == 'hammer':
        # Orden HAMMER
        sections = [
            title_lines,
            patterns_section,
            curves_section,
            junctions_section,
            reservoirs_section,
            demands_section,
            pumps_section,
            pipes_section,
            status_section,
            coordinates_section,
            tags_section,
            labels_section,
            options_section
        ]
    else:
        # Orden EPANET/WaterGEMS
        sections = [
            title_lines,
            junctions_section,
            reservoirs_section,
            pipes_section,
            pumps_section,
            curves_section,
            coordinates_section,
            tags_section,
            labels_section,
            options_section
        ]
    
    return '\n'.join([s for s in sections if s])


def _generate_title_section(inputs, resultados, target_software, analysis_type, rpm_percentage):
    """Genera sección [TITLE]"""
    lines = ['[TITLE]']
    lines.append(f'Sistema de Bombeo: {inputs["proyecto"]}')
    lines.append(f'Software destino: {target_software.upper()}')
    lines.append(f'Tipo de análisis: {analysis_type.upper()}')
    
    if rpm_percentage != 100.0:
        lines.append(f'Configuración: VFD {rpm_percentage:.1f}% RPM')
    else:
        lines.append('Configuración: 100% RPM (Base)')
    
    lines.append(f'Caudal de diseño: {inputs["caudal_diseno_lps"]:.2f} L/s')
    lines.append('')
    
    if analysis_type == 'transient':
        # Agregar información de wave speed
        material_suc = inputs['succion'].get('material', 'PVC')
        material_imp = inputs['impulsion'].get('material', 'PVC')
        
        lines.append('PROPIEDADES TRANSITORIAS:')
        lines.append(f'- Material Succión: {material_suc}')
        lines.append(f'- Material Impulsión: {material_imp}')
        lines.append('- Wave speed: Ver archivo hammer_properties.txt')
        lines.append('')
    
    return '\n'.join(lines)


def _generate_patterns_section():
    """Genera sección [PATTERNS] para HAMMER"""
    return """[PATTERNS]
;ID                                      Multipliers
Operational(Transient,Pump)Pattern-1    0

"""


def _generate_curves_section(data, rpm_percentage, target_software):
    """Genera sección [CURVES]"""
    lines = ['[CURVES]']
    
    # Obtener curva de bomba
    try:
        curva_bomba = data['resultados']['bomba_seleccionada']['curva_completa']
    except KeyError:
        # Curva sintética
        q_diseno = data['inputs']['caudal_diseno_lps']
        h_total = data['resultados']['alturas']['dinamica_total']
        curva_bomba = [
            (0.0, h_total * 1.3),
            (q_diseno, h_total),
            (q_diseno * 2.0, h_total * 0.5)
        ]
    
    # Escalar curva según RPM
    factor_q = rpm_percentage / 100.0
    factor_h = (rpm_percentage / 100.0) ** 2
    
    lines.append(';PUMP: Curva Q-H')
    lines.append(f';RPM: {rpm_percentage:.1f}%')
    for q, h in curva_bomba:
        q_scaled = q * factor_q
        h_scaled = h * factor_h
        lines.append(f'PUMP_CURVE      {q_scaled:<12.2f}  {h_scaled:.2f}')
    
    lines.append('')
    return '\n'.join(lines)


def _generate_junctions_section(inputs, resultados, target_software):
    """Genera sección [JUNCTIONS]"""
    lines = ['[JUNCTIONS]']
    
    # Calcular cotas
    cota_eje_bomba = inputs['elevacion_sitio']
    altura_estatica = resultados['alturas']['estatica_total']
    cota_descarga = cota_eje_bomba + altura_estatica
    
    if target_software == 'hammer':
        # HAMMER: Sin demanda en junctions
        lines.append(';ID              Elev')
        lines.append(f'J_Suction       {cota_eje_bomba:.2f}')
        lines.append(f'J_Impulsion     {cota_eje_bomba:.2f}')
        lines.append(f'J_Discharge     {cota_descarga:.2f}')
    else:
        # EPANET/WaterGEMS: Con demanda
        lines.append(';ID              Elev        Demand      Pattern')
        lines.append(f'J_Suction       {cota_eje_bomba:.3f}      0           ;')
        lines.append(f'J_Impulsion     {cota_eje_bomba:.3f}      0           ;')
        caudal = inputs['caudal_diseno_lps']
        lines.append(f'J_Discharge     {cota_descarga:.3f}      {caudal:.3f}       ;')
    
    lines.append('')
    return '\n'.join(lines)


def _generate_reservoirs_section(inputs, resultados):
    """Genera sección [RESERVOIRS]"""
    lines = ['[RESERVOIRS]']
    lines.append(';ID              Head        Pattern')
    
    # Calcular cota del espejo de agua
    cota_eje_bomba = inputs['elevacion_sitio']
    altura_succion = inputs['altura_succion']
    cota_espejo_agua = cota_eje_bomba + altura_succion
    
    lines.append(f'R_Suction       {cota_espejo_agua:.3f}                ;Tanque de succión')
    lines.append('')
    return '\n'.join(lines)


def _generate_demands_section(inputs, target_software):
    """Genera sección [DEMANDS] (solo HAMMER)"""
    if target_software != 'hammer':
        return ""
    
    lines = ['[DEMANDS]']
    lines.append(';Junction        Demand')
    caudal = inputs['caudal_diseno_lps']
    lines.append(f'J_Discharge      {caudal:.2f}')
    lines.append('')
    return '\n'.join(lines)


def _generate_pipes_section(inputs, resultados, target_software, use_hazen_williams):
    """Genera sección [PIPES]"""
    lines = ['[PIPES]']
    
    # Obtener datos de tuberías
    len_suc_real = inputs.get('long_succion', 0)
    len_equiv_suc = resultados['succion']['long_equiv_accesorios']
    len_suc_total = len_suc_real + len_equiv_suc
    diam_suc_mm = inputs.get('diam_succion_mm', 0)
    
    len_imp_real = inputs.get('long_impulsion', 0)
    len_equiv_imp = resultados['impulsion']['long_equiv_accesorios']
    len_imp_total = len_imp_real + len_equiv_imp
    diam_imp_mm = inputs.get('diam_impulsion_mm', 0)
    
    if use_hazen_williams:
        # HAMMER/WaterGEMS: C de Hazen-Williams, diámetro en mm
        lines.append(';ID              Node1           Node2           Length      Diameter(mm) C_HW  MinorLoss')
        
        c_hw_suc = inputs.get('coeficiente_hazen_succion', 150)
        c_hw_imp = inputs.get('coeficiente_hazen_impulsion', 150)
        
        lines.append(f'P_Suction       R_Suction       J_Suction       {len_suc_total:<11.3f}  {diam_suc_mm:<12.2f}  {c_hw_suc}  0')
        lines.append(f'P_Impulsion     J_Impulsion     J_Discharge     {len_imp_total:<11.3f}  {diam_imp_mm:<12.2f}  {c_hw_imp}  0')
    else:
        # EPANET: Rugosidad absoluta, diámetro en metros
        lines.append(';ID              Node1           Node2           Length      Diameter    Roughness   MinorLoss   Status')
        
        diam_suc_m = diam_suc_mm / 1000.0
        diam_imp_m = diam_imp_mm / 1000.0
        rugosidad = 0.00015  # 0.15 mm típico para HDPE/PVC
        
        lines.append(f'P_Suction       R_Suction       J_Suction       {len_suc_total:.3f}     {diam_suc_m:.4f}      {rugosidad}         0           Open')
        lines.append(f'P_Impulsion     J_Impulsion     J_Discharge     {len_imp_total:.3f}     {diam_imp_m:.4f}      {rugosidad}         0           Open')
    
    lines.append('')
    return '\n'.join(lines)


def _generate_pumps_section(data, rpm_percentage, target_software):
    """Genera sección [PUMPS]"""
    lines = ['[PUMPS]']
    lines.append(';ID              Node1           Node2           Parameters')
    
    if target_software == 'hammer':
        # HAMMER: Incluir SPEED
        lines.append('PUMP_1           J_Suction       J_Impulsion     HEAD PUMP_CURVE SPEED 1')
    else:
        # EPANET/WaterGEMS: Sin SPEED
        lines.append('PUMP_1          J_Suction       J_Impulsion     HEAD PUMP_CURVE')
    
    lines.append('')
    return '\n'.join(lines)


def _generate_status_section():
    """Genera sección [STATUS] para HAMMER"""
    return """[STATUS]
;ID              Status
PUMP_1           CLOSED

"""


def _generate_coordinates_section(inputs, resultados):
    """Genera sección [COORDINATES]"""
    lines = ['[COORDINATES]']
    lines.append(';Node            X-Coord         Y-Coord')
    
    # Coordenadas para visualización
    lines.append('R_Suction        0.00            0.00')
    lines.append('J_Suction        500.00          0.00')
    lines.append('J_Impulsion      600.00          0.00')
    lines.append('J_Discharge      1500.00         500.00')
    lines.append('')
    return '\n'.join(lines)


def _generate_tags_section(inputs, resultados, target_software):
    """Genera sección [TAGS]"""
    if target_software != 'hammer':
        return "[TAGS]\n\n"
    
    # Para HAMMER: incluir propiedades extendidas
    lines = ['[TAGS]']
    
    material_suc = inputs['succion'].get('material', 'PVC')
    material_imp = inputs['impulsion'].get('material', 'PVC')
    
    lines.append(f'Pipe  P_Suction  Material={material_suc}')
    lines.append(f'Pipe  P_Impulsion  Material={material_imp}')
    lines.append('')
    return '\n'.join(lines)


def _generate_labels_section():
    """Genera sección [LABELS]"""
    lines = ['[LABELS]']
    lines.append(';X-Coord         Y-Coord         Label           Anchor')
    lines.append('50.00            -50.00          "Tanque Succión"   R_Suction')
    lines.append('550.00           -50.00          "Bomba"            J_Suction')
    lines.append('1550.00          550.00          "Descarga"         J_Discharge')
    lines.append('')
    return '\n'.join(lines)


def _generate_options_section(target_software, use_hazen_williams):
    """Genera sección [OPTIONS]"""
    lines = ['[OPTIONS]']
    lines.append('UNITS              LPS')
    lines.append('TRIALS             40')
    lines.append('ACCURACY           0.001')
    
    if target_software == 'hammer':
        # Opciones adicionales para HAMMER
        lines.append('EMITTER EXPONENT   0.5')
        lines.append('DAMPLIMIT          0')
        lines.append('MAXCHECK           10')
        lines.append('CHECKFREQ          2')
        lines.append('FLOWCHANGE         0')
        lines.append('HEADERROR          0')
    
    lines.append('SPECIFIC GRAVITY   1.0')
    lines.append('VISCOSITY          1.0')
    
    if target_software == 'hammer':
        lines.append('UNBALANCED         CONTINUE 0')
    
    if use_hazen_williams:
        lines.append('HEADLOSS           H-W')
    else:
        lines.append('HEADLOSS           D-W')
    
    lines.append('TOLERANCE          1')
    lines.append('')
    
    if target_software == 'hammer':
        lines.append('[TIMES]')
        lines.append('REPORT START       0')
        lines.append('PATTERN TIMESTEP   1')
        lines.append('QUALITY TIMESTEP   0')
        lines.append('')
    
    lines.append('[REPORT]')
    lines.append('STATUS             FULL')
    lines.append('SUMMARY            YES')
    lines.append('PAGE               0')
    lines.append('')
    lines.append('[END]')
    
    return '\n'.join(lines)
