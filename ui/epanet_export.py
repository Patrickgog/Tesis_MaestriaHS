#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de exportación a EPANET para la aplicación de bombeo
Genera archivos .inp compatibles con EPANET 2.0+
"""

import json
import os
import math
import streamlit as st
from core.hydraulics import obtener_rugosidad_absoluta
from ui.epanet_utils import (
    obtener_cotas_sistema,
    obtener_propiedades_tuberias,
    obtener_propiedades_bomba,
    calcular_coordenadas_geometria
)

def clean_json_for_curves(data):
    """Limpia curvas si hay tabs/newlines (de curvas_texto, si usas)."""
    if 'curvas_texto' in data:
        for key in ['bomba', 'npsh']:  # Solo HEAD y NPSH para EPANET
            if key in data['curvas_texto']:
                text = data['curvas_texto'][key].replace('\t', ' ').replace('\n', ' ')
                data['curvas_texto'][key] = text
    return data

def get_project_name_safe(data):
    """Obtiene nombre del proyecto de forma segura para usar en IDs EPANET"""
    import unicodedata
    import re
    
    proyecto = data.get('inputs', {}).get('proyecto', 'PROYECTO')
    
    # Eliminar tildes y caracteres especiales
    # Normalizar a NFD (descomponer caracteres con tildes)
    proyecto_nfd = unicodedata.normalize('NFD', proyecto)
    # Eliminar marcas diacríticas (tildes, acentos)
    proyecto_sin_tildes = ''.join(char for char in proyecto_nfd if unicodedata.category(char) != 'Mn')
    
    # Reemplazar espacios, guiones y otros caracteres especiales por guión bajo
    proyecto_limpio = re.sub(r'[^A-Za-z0-9_]', '_', proyecto_sin_tildes)
    
    # Eliminar guiones bajos múltiples consecutivos
    proyecto_limpio = re.sub(r'_+', '_', proyecto_limpio)
    
    # Eliminar guiones bajos al inicio y final
    proyecto_limpio = proyecto_limpio.strip('_')
    
    # Convertir a mayúsculas y limitar a 15 caracteres (límite EPANET)
    return proyecto_limpio.upper()[:15]


def pad_value(value, width):
    """Agrega padding de espacios a la derecha hasta alcanzar width"""
    value_str = str(value)
    if len(value_str) >= width:
        return value_str
    return value_str + ' ' * (width - len(value_str))

def convert_to_allievi_format(inp_text):
    """
    Convierte un archivo .inp de formato EPANET estándar a formato Allievi
    
    FORMATO CRÍTICO (16-dic-2025):
    - Columnas FIJAS con padding de espacios (no solo tabs)
    - CRLF (\\r\\n) line endings
    - Tabs vacíos (espacios) antes de comentarios en líneas de datos
    - Sin línea vacía entre TITLE y GEOMETRIA
    
    Basado en análisis exhaustivo de FLOR_DE_LIMON_aalievi.inp funcional
    
    Args:
        inp_text: String con contenido .inp en formato EPANET estándar
    
    Returns:
        String con contenido .inp en formato Allievi (columnas fijas)
    """
    import re
    
    # PASO 1: Normalizar line endings
    inp_text = inp_text.replace('\r\n', '\n').replace('\r', '\n')
    lines = inp_text.split('\n')
    
    # PASO 2: Parsear secciones
    sections = {}
    current_section = None
    current_content = []
    
    for line in lines:
        line = line.rstrip('\r\n')
        
        if line.startswith('[') and line.endswith(']'):
            # Guardar sección anterior
            if current_section:
                sections[current_section] = current_content
            
            # Nueva sección
            current_section = line[1:-1].upper()
            current_content = []
        else:
            if current_section:
                current_content.append(line)
    
    # Guardar última sección
    if current_section:
        sections[current_section] = current_content
    
    # PASO 3: Reconstruir con formato Allievi
    allievi_lines = []
    
    # === [TITLE] ===
    allievi_lines.append('[TITLE]')
    if 'TITLE' in sections:
        # Eliminar líneas vacías que preceden a GEOMETRIA
        title_lines = sections['TITLE']
        for i, line in enumerate(title_lines):
            # Skip línea vacía si la siguiente línea es GEOMETRIA
            if line.strip() == '' and i + 1 < len(title_lines) and 'GEOMETRIA' in title_lines[i + 1]:
                continue
            allievi_lines.append(line)
    # NO agregar línea vacía aquí - el archivo funcional tiene [JUNCTIONS] inmediatamente después
    
    
    
    # === [JUNCTIONS] ===
    allievi_lines.append('[JUNCTIONS]')
    # HEADER con padding fijo: ID(16), Elev(12), Demand(12), Pattern(16)
    allievi_lines.append(';ID              \tElev        \tDemand      \tPattern         ')
    
    if 'JUNCTIONS' in sections:
        for line in sections['JUNCTIONS']:
            if line.strip() and not line.strip().startswith(';'):
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 3:
                    id_val = parts[0]
                    elev = parts[1]
                    demand = parts[2]
                    pattern = parts[3] if len(parts) > 3 and not parts[3].startswith(';') else ''
                    comment = ';' + ' '.join([p for p in parts[3:] if p.startswith(';')][0][1:] if any(p.startswith(';') for p in parts[3:]) else '') if len(parts) > 3 else ''
                    
                    # Formato: " ID(16)	Elev(12)	Demand(12)	Pattern(16)	;Comentario"
                    formatted = f' {pad_value(id_val, 16)}\t{pad_value(elev, 12)}\t{pad_value(demand, 12)}\t{pad_value(pattern, 16)}\t{comment}'
                    allievi_lines.append(formatted)
    allievi_lines.append('')
    
    # === [RESERVOIRS] ===
    allievi_lines.append('[RESERVOIRS]')
    allievi_lines.append(';ID              \tHead        \tPattern         ')
    
    if 'RESERVOIRS' in sections:
        for line in sections['RESERVOIRS']:
            if line.strip() and not line.strip().startswith(';'):
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 2:
                    id_val = parts[0]
                    head = parts[1]
                    pattern = parts[2] if len(parts) > 2 and not parts[2].startswith(';') else ''
                    comment = ';' + ' '.join([p for p in parts[2:] if p.startswith(';')][0][1:] if any(p.startswith(';') for p in parts[2:]) else '') if len(parts) > 2 else ''
                    
                    formatted = f' {pad_value(id_val, 16)}\t{pad_value(head, 12)}\t{pad_value(pattern, 16)}\t{comment}'
                    allievi_lines.append(formatted)
    allievi_lines.append('')
    
    # === [TANKS] ===
    allievi_lines.append('[TANKS]')
    allievi_lines.append(';ID              \tElevation   \tInitLevel   \tMinLevel    \tMaxLevel    \tDiameter    \tMinVol      \tVolCurve        \tOverflow')
    
    if 'TANKS' in sections:
        for line in sections['TANKS']:
            if line.strip() and not line.strip().startswith(';'):
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 7:
                    id_val = parts[0]
                    elevation = parts[1]
                    init_level = parts[2]
                    min_level = parts[3]
                    max_level = parts[4]
                    diameter = parts[5]
                    min_vol = parts[6]
                    comment = ';' + ' '.join([p for p in parts[7:] if p.startswith(';')][0][1:] if any(p.startswith(';') for p in parts[7:]) else '') if len(parts) > 7 else ''
                    
                    # Incluir VolCurve y Overflow vacíos
                    formatted = f' {pad_value(id_val, 16)}\t{pad_value(elevation, 12)}\t{pad_value(init_level, 12)}\t{pad_value(min_level, 12)}\t{pad_value(max_level, 12)}\t{pad_value(diameter, 12)}\t{pad_value(min_vol, 12)}\t{pad_value("", 16)}\t{comment}'
                    allievi_lines.append(formatted)
    allievi_lines.append('')
    
    # === [PIPES] ===
    allievi_lines.append('[PIPES]')
    allievi_lines.append(';ID              \tNode1           \tNode2           \tLength      \tDiameter    \tRoughness   \tMinorLoss   \tStatus')
    
    if 'PIPES' in sections:
        for line in sections['PIPES']:
            if line.strip() and not line.strip().startswith(';'):
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 8:
                    id_val = parts[0]
                    node1 = parts[1]
                    node2 = parts[2]
                    length = parts[3]
                    diameter = parts[4]
                    roughness = parts[5]
                    minor_loss = parts[6]
                    status = parts[7]
                    comment = ';' + ' '.join([p for p in parts[8:] if p.startswith(';')][0][1:] if any(p.startswith(';') for p in parts[8:]) else '') if len(parts) > 8 else ''
                    
                    formatted = f' {pad_value(id_val, 16)}\t{pad_value(node1, 16)}\t{pad_value(node2, 16)}\t{pad_value(length, 12)}\t{pad_value(diameter, 12)}\t{pad_value(roughness, 12)}\t{pad_value(minor_loss, 12)}\t{pad_value(status, 6)}\t{comment}'
                    allievi_lines.append(formatted)
    allievi_lines.append('')
    
    # === [PUMPS] ===
    allievi_lines.append('[PUMPS]')
    allievi_lines.append(';ID              \tNode1           \tNode2           \tParameters')
    
    if 'PUMPS' in sections:
        for line in sections['PUMPS']:
            if line.strip() and not line.strip().startswith(';'):
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 3:
                    id_val = parts[0]
                    # MANTENER IDs SIMPLES - Allievi agrega prefijos automáticamente
                    node1 = parts[1]
                    node2 = parts[2]
                    params = ' '.join(parts[3:])
                    # Separar comentario si existe
                    if ';' in params:
                        param_parts = params.split(';', 1)
                        params_clean = param_parts[0].strip()
                        comment = ';' + param_parts[1]
                    else:
                        params_clean = params
                        comment = ''
                    
                    formatted = f' {pad_value(id_val, 16)}\t{pad_value(node1, 16)}\t{pad_value(node2, 16)}\t{params_clean}\t{comment}'
                    allievi_lines.append(formatted)
    allievi_lines.append('')
    
    # === [VALVES] ===
    allievi_lines.append('[VALVES]')
    allievi_lines.append(';ID              \tNode1           \tNode2           \tDiameter    \tType\tSetting     \tMinorLoss   ')
    
    if 'VALVES' in sections:
        for line in sections['VALVES']:
            if line.strip() and not line.strip().startswith(';'):
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 7:
                    id_val = parts[0]
                    # MANTENER IDs SIMPLES - Allievi agrega prefijos automáticamente
                    node1 = parts[1]
                    node2 = parts[2]
                    diameter = parts[3]
                    valve_type = parts[4]
                    setting = parts[5]
                    minor_loss = parts[6]
                    comment = ';' + ' '.join([p for p in parts[7:] if p.startswith(';')][0][1:] if any(p.startswith(';') for p in parts[7:]) else '') if len(parts) > 7 else ''
                    
                    formatted = f' {pad_value(id_val, 16)}\t{pad_value(node1, 16)}\t{pad_value(node2, 16)}\t{pad_value(diameter, 12)}\t{valve_type}\t{pad_value(setting, 12)}\t{pad_value(minor_loss, 12)}\t{comment}'
                    allievi_lines.append(formatted)
    allievi_lines.append('')
    
    # === SECCIONES ADICIONALES (en orden Allievi) ===
    # NO agregar [TAGS] vacío aquí - se agregará después con contenido real
    

    allievi_lines.append('[DEMANDS]')
    allievi_lines.append(';Junction        \tDemand      \tPattern         \tCategory')
    allievi_lines.append('')
    
    allievi_lines.append('[STATUS]')
    allievi_lines.append(';ID              \tStatus/Setting')
    # Copiar STATUS si existe
    if 'STATUS' in sections:
        for line in sections['STATUS']:
            if line.strip() and not line.strip().startswith(';'):
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 2:
                    id_val = parts[0]
                    status = parts[1]
                    formatted = f' {pad_value(id_val, 16)}\t{status}'
                    allievi_lines.append(formatted)
    allievi_lines.append('')
    
    allievi_lines.append('[PATTERNS]')
    allievi_lines.append(';ID              \tMultipliers')
    allievi_lines.append('')
    
    # === [CURVES] ===
    allievi_lines.append('[CURVES]')
    allievi_lines.append(';ID              \tX-Value     \tY-Value')
    
    if 'CURVES' in sections:
        for line in sections['CURVES']:
            if line.strip():
                if line.strip().startswith(';'):
                    # Comentarios - limpiar y formatear
                    comment_text = line.strip()
                    # Convertir a formato PUMP:
                    if 'CURVA_' in comment_text and not comment_text.startswith(';PUMP:'):
                        if 'CURVA_VALV' in comment_text:
                            comment_text = ';PUMP: CURVA_VALV'
                        elif 'CURVA_HQ' in comment_text:
                            comment_text = ';PUMP: CURVA_HQ'
                        elif 'CURVA_ETA' in comment_text:
                            comment_text = ';PUMP: CURVA_ETA'
                        elif 'CURVA_POT' in comment_text:
                            comment_text = ';PUMP: CURVA_POT'
                        elif 'CURVA_NPSH' in comment_text:
                            comment_text = ';PUMP: CURVA_NPSH'
                        
                        # Agregar separador extra para Allievi
                        allievi_lines.append(';')
                        allievi_lines.append(';=========================================')
                    
                    # Skip líneas de "Leyes de afinidad" y "Puntos exportados"
                    if any(skip in comment_text for skip in ['Leyes de afinidad', 'Ley de afinidad', 'Puntos exportados', 'ESCALADA', 'Total puntos']):
                        continue
                    
                    allievi_lines.append(comment_text)
                else:
                    # Datos de curva
                    parts = re.split(r'\s+', line.strip())
                    if len(parts) >= 3:
                        curve_id = parts[0]
                        x_val = parts[1]
                        y_val = parts[2]
                        
                        formatted = f' {pad_value(curve_id, 16)}\t{pad_value(x_val, 12)}\t{pad_value(y_val, 12)}'
                        allievi_lines.append(formatted)
    allievi_lines.append('')
    
    # === SECCIONES INTERMEDIAS ===
    allievi_lines.append('[CONTROLS]')
    allievi_lines.append('')
    
    allievi_lines.append('[RULES]')
    allievi_lines.append('')
    
    allievi_lines.append('[ENERGY]')
    # Formato con padding
    if 'ENERGY' in sections:
        for line in sections['ENERGY']:
            if line.strip() and not line.strip().startswith(';'):
                parts = line.strip().split(None, 1)
                if len(parts) == 2:
                    keyword = parts[0]
                    value = parts[1]
                    
                    # Capitalizar keywords
                    if keyword.upper() == 'GLOBAL':
                        # Es "GLOBAL EFFICIENCY", "GLOBAL PRICE", etc
                        full_parts = line.strip().split(None, 2)
                        if len(full_parts) >= 3:
                            keyword_full = full_parts[0] + ' ' + full_parts[1]
                            value = full_parts[2]
                            
                            if 'EFFICIENCY' in keyword_full.upper():
                                formatted = f' Global Efficiency  \t{value}'
                            elif 'PRICE' in keyword_full.upper():
                                formatted = f' Global Price       \t{value}'
                            else:
                                formatted = f' Global {full_parts[1].capitalize()}  \t{value}'
                            
                            allievi_lines.append(formatted)
                    elif keyword.upper() == 'DEMAND':
                        full_parts = line.strip().split(None, 2)
                        if len(full_parts) >= 3:
                            formatted = f' Demand Charge      \t{full_parts[2]}'
                            allievi_lines.append(formatted)
    allievi_lines.append('')
    
    allievi_lines.append('[EMITTERS]')
    allievi_lines.append(';Junction        \tCoefficient')
    allievi_lines.append('')
    
    allievi_lines.append('[QUALITY]')
    allievi_lines.append(';Node            \tInitQual')
    allievi_lines.append('')
    
    allievi_lines.append('[SOURCES]')
    allievi_lines.append(';Node            \tType        \tQuality     \tPattern')
    allievi_lines.append('')
    
    allievi_lines.append('[REACTIONS]')
    allievi_lines.append(';Type     \tPipe/Tank       \tCoefficient')
    allievi_lines.append('')
    allievi_lines.append('')
    
    allievi_lines.append('[REACTIONS]')
    allievi_lines.append(' Order Bulk            \t1')
    allievi_lines.append(' Order Tank            \t1')
    allievi_lines.append(' Order Wall            \t1')
    allievi_lines.append(' Global Bulk           \t0')
    allievi_lines.append(' Global Wall           \t0')
    allievi_lines.append(' Limiting Potential    \t0')
    allievi_lines.append(' Roughness Correlation \t0')
    allievi_lines.append('')
    
    allievi_lines.append('[MIXING]')
    allievi_lines.append(';Tank            \tModel')
    allievi_lines.append('')
    
    # === [TIMES] ===
    allievi_lines.append('[TIMES]')
    if 'TIMES' in sections:
        for line in sections['TIMES']:
            if line.strip() and not line.strip().startswith(';'):
                parts = line.strip().split(None, 1)
                if len(parts) >= 2:
                    keyword = parts[0]
                    value = parts[1]
                    
                    # Capitalizar según formato Allievi
                    keyword_map = {
                        'DURATION': ' Duration',
                        'HYDRAULIC': ' Hydraulic Timestep',
                        'QUALITY': ' Quality Timestep',
                        'PATTERN': ' Pattern Timestep',
                        'REPORT': ' Report Timestep',
                        'START': ' Start ClockTime',
                        'STATISTIC': ' Statistic'
                    }
                    
                    # Detectar keyword compuesto
                    if keyword.upper() in ['HYDRAULIC', 'QUALITY', 'PATTERN', 'REPORT']:
                        full_parts = line.strip().split(None, 2)
                        if len(full_parts) >= 3 and full_parts[1].upper() in ['TIMESTEP', 'START']:
                            keyword_full = full_parts[0] + ' ' + full_parts[1]
                            value = full_parts[2]
                            
                            if 'HYDRAULIC' in keyword_full.upper():
                                formatted = f' Hydraulic Timestep \t{value}'
                            elif 'QUALITY TIMESTEP' in keyword_full.upper():
                                formatted = f' Quality Timestep   \t{value}'
                            elif 'PATTERN TIMESTEP' in keyword_full.upper():
                                formatted = f' Pattern Timestep   \t{value}'
                            elif 'PATTERN START' in keyword_full.upper():
                                formatted = f' Pattern Start      \t{value}'
                            elif 'REPORT TIMESTEP' in keyword_full.upper():
                                formatted = f' Report Timestep    \t{value}'
                            elif 'REPORT START' in keyword_full.upper():
                                formatted = f' Report Start       \t{value}'
                            else:
                                formatted = f' {keyword_full.capitalize()}   \t{value}'
                            
                            allievi_lines.append(formatted)
                        else:
                            formatted = f' {keyword.capitalize()}           \t{value}'
                            allievi_lines.append(formatted)
                    elif keyword.upper() == 'DURATION':
                        formatted = f' Duration           \t{value}'
                        allievi_lines.append(formatted)
                    elif keyword.upper() == 'START':
                        formatted = f' Start ClockTime    \t{value}'
                        allievi_lines.append(formatted)
                    elif keyword.upper() == 'STATISTIC':
                        formatted = f' Statistic          \t{value}'
                        allievi_lines.append(formatted)
    allievi_lines.append('')
    
    # === [REPORT] ===
    allievi_lines.append('[REPORT]')
    if 'REPORT' in sections:
        for line in sections['REPORT']:
            if line.strip() and not line.strip().startswith(';'):
                parts = line.strip().split(None, 1)
                if len(parts) >= 2:
                    keyword = parts[0].upper()
                    value = parts[1]
                    
                    # Cambiar YES a No en SUMMARY
                    if keyword == 'SUMMARY' and value.upper() == 'YES':
                        value = 'No'
                    
                    # Skip NODES y LINKS
                    if keyword in ['NODES', 'LINKS']:
                        continue
                    
                    # Capitalizar
                    if keyword == 'STATUS':
                        formatted = f' Status             \t{value}'
                    elif keyword == 'SUMMARY':
                        formatted = f' Summary            \t{value}'
                    elif keyword == 'PAGE':
                        formatted = f' Page               \t{value}'
                    else:
                        formatted = f' {keyword.capitalize()}             \t{value}'
                    
                    allievi_lines.append(formatted)
    allievi_lines.append('')
    
    # === [OPTIONS] ===
    allievi_lines.append('[OPTIONS]')
    if 'OPTIONS' in sections:
        for line in sections['OPTIONS']:
            if line.strip() and not line.strip().startswith(';'):
                parts = line.strip().split(None, 1)
                if len(parts) >= 2:
                    keyword = parts[0].upper()
                    value = parts[1]
                    
                    # Capitalizar según formato Allievi
                    keyword_map = {
                        'UNITS': ' Units',
                        'HEADLOSS': ' Headloss',
                        'SPECIFIC': ' Specific Gravity',
                        'VISCOSITY': ' Viscosity',
                        'TRIALS': ' Trials',
                        'ACCURACY': ' Accuracy',
                        'CHECKFREQ': ' CHECKFREQ',
                        'MAXCHECK': ' MAXCHECK',
                        'DAMPLIMIT': ' DAMPLIMIT',
                        'UNBALANCED': ' Unbalanced',
                        'PATTERN': ' Pattern',
                        'DEMAND': ' Demand Multiplier',
                        'EMITTER': ' Emitter Exponent',
                        'QUALITY': ' Quality',
                        'DIFFUSIVITY': ' Diffusivity',
                        'TOLERANCE': ' Tolerance'
                    }
                    
                    # Manejar keywords compuestos
                    if keyword in ['SPECIFIC', 'DEMAND', 'EMITTER']:
                        full_parts = line.strip().split(None, 2)
                        if len(full_parts) >= 3:
                            keyword_full = full_parts[0] + ' ' + full_parts[1]
                            value = full_parts[2]
                            
                            if 'SPECIFIC' in keyword_full.upper():
                                formatted = f' Specific Gravity   \t{value}'
                            elif 'DEMAND' in keyword_full.upper():
                                formatted = f' Demand Multiplier  \t{value}'
                            elif 'EMITTER' in keyword_full.upper():
                                formatted = f' Emitter Exponent   \t{value}'
                            else:
                                formatted = f' {keyword_full}   \t{value}'
                            
                            allievi_lines.append(formatted)
                    else:
                        formatted_keyword = keyword_map.get(keyword, f' {keyword.capitalize()}')
                        formatted = f'{formatted_keyword}              \t{value}'
                        allievi_lines.append(formatted)
    
    # Agregar opciones extra si no existen
    options_content = '\n'.join([l for l in allievi_lines if '[OPTIONS]' in l or (allievi_lines.index(l) > allievi_lines.index('[OPTIONS]') if '[OPTIONS]' in allievi_lines else False)])
    
    if 'CHECKFREQ' not in options_content:
        allievi_lines.append(' CHECKFREQ          \t2')
    if 'MAXCHECK' not in options_content:
        allievi_lines.append(' MAXCHECK           \t10')
    if 'DAMPLIMIT' not in options_content:
        allievi_lines.append(' DAMPLIMIT          \t0')
    if 'Quality' not in options_content and 'QUALITY' not in options_content:
        allievi_lines.append(' Quality            \tNone mg/L')
    if 'Diffusivity' not in options_content and 'DIFFUSIVITY' not in options_content:
        allievi_lines.append(' Diffusivity        \t1')
    if 'Tolerance' not in options_content and 'TOLERANCE' not in options_content:
        allievi_lines.append(' Tolerance          \t0.01')
    allievi_lines.append('')
    
    # === [TAGS] - CRÍTICO PARA ALLIEVI ===
    if 'TAGS' in sections:
        allievi_lines.append('[TAGS]')
        for line in sections['TAGS']:
            if line.strip():
                allievi_lines.append(line)
        allievi_lines.append('')
    
    # === [PATTERNS] - Para maniobras de válvula ===
    if 'PATTERNS' in sections:
        allievi_lines.append('[PATTERNS]')
        allievi_lines.append(';ID              \tMultipliers')
        for line in sections['PATTERNS']:
            if line.strip():
                allievi_lines.append(line)
        allievi_lines.append('')
    
    # === [COORDINATES] ===
    allievi_lines.append('[COORDINATES]')
    allievi_lines.append(';Node            \tX-Coord           \tY-Coord')
    
    if 'COORDINATES' in sections:
        for line in sections['COORDINATES']:
            if line.strip() and not line.strip().startswith(';'):
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 3:
                    node_id = parts[0]
                    x_coord = parts[1]
                    y_coord = parts[2]
                    
                    formatted = f' {pad_value(node_id, 16)}\t{pad_value(x_coord, 18)}\t{y_coord}'
                    allievi_lines.append(formatted)
    allievi_lines.append('')
    
    # === SECCIONES FINALES ===
    allievi_lines.append('[VERTICES]')
    allievi_lines.append(';Link            \tX-Coord           \tY-Coord')
    allievi_lines.append('')
    
    allievi_lines.append('[LABELS]')
    allievi_lines.append(';X-Coord             Y-Coord             Label & Anchor Node')
    allievi_lines.append('')
    
    allievi_lines.append('[BACKDROP]')
    allievi_lines.append('  DIMENSIONS  \t-10.000           \t1218.104          \t210.000           \t1316.576          ')
    allievi_lines.append(' UNITS          \tNone')
    allievi_lines.append(' FILE           \t')
    allievi_lines.append(' OFFSET         \t0.00            \t0.00            ')
    allievi_lines.append('')
    
    allievi_lines.append('[END]')
    
    # === PASO FINAL: CRLF ===
    cleaned_lines = [line.rstrip('\r\n') for line in allievi_lines]
    result = '\r\n'.join(cleaned_lines)
    
    if not result.endswith('\r\n'):
        result += '\r\n'
    
    return result


def calcular_k_total_accesorios(seccion='succion'):
    """Calcula el coeficiente K total de los accesorios de una sección"""
    try:
        if seccion == 'succion':
            accesorios = st.session_state.get('accesorios_succion', [])
        else:
            accesorios = st.session_state.get('accesorios_impulsion', [])
        
        k_total = 0.0
        for acc in accesorios:
            # Convertir a float para manejar casos donde k o cantidad sean strings
            try:
                k_value = acc.get('k', 0)
                cantidad = float(acc.get('cantidad', 1))
                
                # Si k es un string con rango (ej: '0.1 - 0.2'), tomar el promedio
                if isinstance(k_value, str):
                    # Intentar parsear rango
                    if '-' in k_value:
                        parts = k_value.split('-')
                        if len(parts) == 2:
                            k_min = float(parts[0].strip())
                            k_max = float(parts[1].strip())
                            k_individual = (k_min + k_max) / 2.0  # Promedio
                        else:
                            k_individual = float(k_value)
                    else:
                        k_individual = float(k_value)
                else:
                    k_individual = float(k_value)
                
                k_total += k_individual * cantidad
                
            except (ValueError, TypeError) as e:
                # Si hay error de conversión, usar valor por defecto conservador
                tipo_acc = acc.get('tipo', 'Desconocido')
                # No mostrar warning, usar valor por defecto de 0.2 (conservador)
                k_individual = 0.2
                cantidad = float(acc.get('cantidad', 1))
                k_total += k_individual * cantidad
        
        return k_total
    except Exception as e:
        st.warning(f"Error calculando K total de {seccion}: {e}")
        return 0.0

def generate_epanet_inp_base(data, use_mm=False, use_minor_loss=False):
    """
    Genera .inp para 100% RPM (base) con datos reales del proyecto.
    
    Args:
        data: Diccionario con datos del proyecto
        use_mm: Si True, usa milímetros para diámetros. Si False, usa metros (default)
        use_minor_loss: Si True, usa Minor Loss Coefficient (K) en lugar de longitud equivalente (para WaterGEMS)
    """
    data = clean_json_for_curves(data)
    project_name = get_project_name_safe(data)
    
    # --- FASE 4: Documentación mejorada en el encabezado ---
    from datetime import datetime
    
    lines = []
    lines.append('[TITLE]')
    lines.append(f'Sistema de Bombeo: {data["inputs"]["proyecto"]}')
    lines.append(f'Diseñado por: {data["inputs"].get("diseno", "N/A")}')
    lines.append(f'Configuracion: 100% RPM (Base)')
    lines.append(f'Caudal de diseno: {data["inputs"]["caudal_diseno_lps"]:.2f} L/s')
    lines.append(f'Generado: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    lines.append('')
    lines.append(';=== RESUMEN DE PARAMETROS ===')
    lines.append(f';Elevacion sitio: {data["inputs"].get("elevacion_sitio", 0):.2f} m.s.n.m.')
    lines.append(f';Altura succion: {data["inputs"].get("altura_succion", 0):.2f} m')
    lines.append(f';Altura estatica total: {data["resultados"]["alturas"].get("estatica_total", 0):.2f} m')
    lines.append(f';Tuberia succion: D={data["inputs"].get("diam_succion_mm", 0):.0f}mm, L={data["inputs"].get("long_succion", 0):.1f}m')
    lines.append(f';Tuberia impulsion: D={data["inputs"].get("diam_impulsion_mm", 0):.0f}mm, L={data["inputs"].get("long_impulsion", 0):.1f}m')
    lines.append(f';Puntos curva H-Q: {len(data["inputs"]["curva_inputs"].get("bomba", []))}')
    lines.append(';==============================')
    lines.append('')

    lines.append('[JUNCTIONS]')
    lines.append(';ID              Elev        Demand      Pattern')
    # CÁLCULO DE COTAS REALES
    cota_eje_bomba = data['inputs']['elevacion_sitio']
    altura_succion = data['inputs']['altura_succion']
    
    # Calcular cota del espejo de agua (nivel del tanque de succión)
    # altura_succion ya tiene el signo correcto:
    # - Positivo: bomba inundada (agua arriba del eje)
    # - Negativo: bomba no inundada (agua abajo del eje)
    cota_espejo_agua = cota_eje_bomba + altura_succion
    
    # Calcular cota de descarga
    altura_descarga = data['resultados']['alturas']['estatica_total']
    cota_descarga = cota_eje_bomba + altura_descarga
    
    # Junctions en el eje de la bomba
    lines.append(f'J_Suction       {cota_eje_bomba:.3f}      0           ;')
    lines.append(f'J_Impulsion     {cota_eje_bomba:.3f}      0           ;')
    # Junction de descarga con demanda = caudal de diseño (100% RPM)
    caudal_base = data['inputs']['caudal_diseno_lps']
    lines.append(f'J_Discharge     {cota_descarga:.3f}      {caudal_base:.3f}       ;')
    lines.append('')

    lines.append('[RESERVOIRS]')
    lines.append(';ID              Head        Pattern')
    lines.append(f'R_Suction       {cota_espejo_agua:.3f}                ;Tanque de succión')
    lines.append('')

    lines.append('[TANKS]')
    lines.append(';ID              Elevation   InitLevel   MinLevel    MaxLevel    Diameter    MinVol      VolCurve')
    lines.append('')

    lines.append('[PIPES]')
    if use_mm:
        lines.append(';ID              Node1           Node2           Length      Diameter(mm) Roughness   MinorLoss   Status')
    else:
        lines.append(';ID              Node1           Node2           Length      Diameter    Roughness   MinorLoss   Status')
    
    # Obtener Wave Speed (celeridad) para análisis transitorio
    # Prioridad: session_state > calcular desde material
    wave_speed_suc = st.session_state.get('celeridad_succion', st.session_state.get('wave_speed_succion', 1200))
    wave_speed_imp = st.session_state.get('celeridad_impulsion', st.session_state.get('wave_speed_impulsion', 1200))
    material_suc = st.session_state.get('material_succion', 'Acero')
    material_imp = st.session_state.get('material_impulsion', 'Acero')
    
    # TUBERÍA DE SUCCIÓN
    len_suc_real = data['inputs'].get('long_succion', 0)
    len_equiv_suc = data['resultados']['succion']['long_equiv_accesorios']
    diam_suc_mm = data['inputs'].get('diam_succion_mm', 0)
    haz_suc = data['inputs'].get('coeficiente_hazen_succion', 150)
    
    # Decidir método: Longitud Equivalente (EPANET) o Minor Loss (WaterGEMS)
    if use_minor_loss:
        # WaterGEMS: Longitud real + K en MinorLoss
        len_suc_total = len_suc_real
        k_suc = calcular_k_total_accesorios('succion')
        lines.append(f';Succión: Material={material_suc}, WaveSpeed={wave_speed_suc:.0f} m/s')
        lines.append(f';L_real={len_suc_real:.2f}m, K_total={k_suc:.4f}')
    else:
        # EPANET: Longitud real + equivalente, K=0
        len_suc_total = len_suc_real + len_equiv_suc
        k_suc = 0.0
        lines.append(f';Succión: Material={material_suc}, WaveSpeed={wave_speed_suc:.0f} m/s')
        lines.append(f';L_total={len_suc_total:.2f}m (L_real + L_equiv)')
    
    # Usar mm o m según configuración
    if use_mm:
        diam_suc_value = diam_suc_mm
        diam_imp_value = diam_imp_mm
        diam_format = '.2f'
    else:
        diam_suc_value = diam_suc_mm / 1000.0
        diam_imp_value = diam_imp_mm / 1000.0
        diam_format = '.4f'

    # Determinar rugosidad según método
    if is_dw:
        rough_suc = obtener_rugosidad_absoluta(data['inputs'].get('material_succion', 'PVC')) * 1000.0
    else:
        rough_suc = data['inputs'].get('coeficiente_hazen_succion', 150)
        
    lines.append(f'P_Suction       R_Suction       J_Suction       {len_suc_total:.3f}     {diam_suc_value:{diam_format}}      {rough_suc:.4f}         {k_suc:.4f}      Open')
    
    # TUBERÍA DE IMPULSIÓN
    len_imp_real = data['inputs'].get('long_impulsion', 0)
    len_imp_equiv = data['resultados']['impulsion']['long_equiv_accesorios']
    diam_imp_mm = data['inputs'].get('diam_impulsion_mm', 0)
    haz_imp = data['inputs'].get('coeficiente_hazen_impulsion', 150)
    
    # Decidir método: Longitud Equivalente (EPANET) o Minor Loss (WaterGEMS)
    if use_minor_loss:
        # WaterGEMS: Longitud real + K en MinorLoss
        len_imp_total = len_imp_real
        k_imp = calcular_k_total_accesorios('impulsion')
        lines.append(f';Impulsión: Material={material_imp}, WaveSpeed={wave_speed_imp:.0f} m/s')
        lines.append(f';L_real={len_imp_real:.2f}m, K_total={k_imp:.4f}')
    else:
        # EPANET: Longitud real + equivalente, K=0
        len_imp_total = len_imp_real + len_imp_equiv
        k_imp = 0.0
        lines.append(f';Impulsión: Material={material_imp}, WaveSpeed={wave_speed_imp:.0f} m/s')
        lines.append(f';L_total={len_imp_total:.2f}m (incluye L_equiv)')
    
    # Determinar rugosidad según método
    if is_dw:
        rough_imp = obtener_rugosidad_absoluta(data['inputs'].get('material_impulsion', 'PVC')) * 1000.0
    else:
        rough_imp = data['inputs'].get('coeficiente_hazen_impulsion', 150)
        
    lines.append(f'P_Impulsion     J_Impulsion     J_Discharge     {len_imp_total:.3f}     {diam_imp_value:{diam_format}}      {rough_imp:.4f}         {k_imp:.4f}      Open')
    lines.append('')
    
    # --- Sección especial para WaterGEMS/HAMMER: Wave Speeds ---
    lines.append(';[WAVESPEEDS] - Para análisis transitorio en HAMMER')
    lines.append(f';P_Suction       {wave_speed_suc:.0f}')
    lines.append(f';P_Impulsion     {wave_speed_imp:.0f}')
    lines.append('')

    lines.append('[PUMPS]')
    lines.append(';ID              Node1           Node2           Parameters')
    curve_name = f'PUMP_{project_name}_100RPM'
    eficiencia_curve_name = f'EFF_{project_name}_100RPM'
    potencia_curve_name = f'POW_{project_name}_100RPM'
    
    # Línea principal de la bomba con curva HEAD
    lines.append(f'PUMP_1          J_Suction       J_Impulsion     HEAD {curve_name}')
    
    # Comentarios para WaterGEMS con curvas adicionales
    lines.append(f';[WATERGEMS] PUMP_1 EFFICIENCY {eficiencia_curve_name}')
    lines.append(f';[WATERGEMS] PUMP_1 POWER {potencia_curve_name}')
    lines.append('')

    lines.append('[VALVES]')
    lines.append(';ID              Node1           Node2           Diameter    Type    Setting     MinorLoss')
    lines.append('')

    lines.append('[TAGS]')
    lines.append('')

    lines.append('[DEMANDS]')
    lines.append(';Junction        Demand      Pattern         Category')
    lines.append('')

    lines.append('[STATUS]')
    lines.append(';ID              Status/Setting')
    lines.append('')

    lines.append('[PATTERNS]')
    lines.append(';ID              Multipliers')
    lines.append('PAT_CONSTANT    1.0')
    lines.append('')

    lines.append('[CURVES]')
    lines.append(';ID              X-Value     Y-Value')
    lines.append('')
    
    # ===== 1. CURVA DE LA BOMBA (H-Q) - HEAD vs FLOW =====
    # Prioridad: data > session_state directo > error
    lines.append(f';PUMP CURVE H-Q: {project_name} - 100% RPM')
    lines.append(f';Curva de altura (HEAD) vs caudal (FLOW)')
    
    # Intentar obtener curva desde múltiples fuentes
    bomba_points = data['inputs'].get('curva_inputs', {}).get('bomba', [])
    if not bomba_points:
        # Fallback a session_state directo
        bomba_points = st.session_state.get('curva_inputs', {}).get('bomba', [])
    if not bomba_points:
        # Fallback a curva_bomba (nombre alternativo)
        bomba_points = st.session_state.get('curva_bomba', [])
    if not bomba_points:
        # Fallback a puntos calculados en dataframes
        df_bomba = st.session_state.get('df_bomba_100')
        if df_bomba is not None and hasattr(df_bomba, 'values') and len(df_bomba) > 0:
            try:
                bomba_points = [(row[0], row[1]) for row in df_bomba.values[:20]]  # Max 20 puntos
            except:
                pass
    
    # Exportar puntos de curva
    if bomba_points and len(bomba_points) >= 2:
        lines.append(f';Total puntos exportados: {len(bomba_points)}')
        for point in bomba_points:
            if isinstance(point, (list, tuple)) and len(point) >= 2:
                q, h = point[0], point[1]
                lines.append(f'{curve_name}    {q:.4f}      {h:.4f}')
    else:
        # Sin datos - crear curva de advertencia
        lines.append(f';ERROR: No se encontraron puntos de curva H-Q')
        lines.append(f';Se requiere definir curva en Datos de Entrada > Curvas')
        # Curva mínima para evitar error en WaterGEMS
        lines.append(f'{curve_name}    0.0000      100.0000')
        lines.append(f'{curve_name}    50.0000     80.0000')
        lines.append(f'{curve_name}    100.0000    50.0000')
    lines.append('')
    
    # ===== 2. CURVA DE RENDIMIENTO (η-Q) - EFFICIENCY vs FLOW =====
    # Formato WaterGEMS: CURVE_NAME EFFICIENCY
    eficiencia_curve_name = f'EFF_{project_name}_100RPM'
    lines.append(f';EFFICIENCY CURVE η-Q: {project_name} - 100% RPM')
    lines.append(f';Curva de rendimiento (%) vs caudal (L/s)')
    eficiencia_points = data['inputs']['curva_inputs'].get('rendimiento', [])
    if eficiencia_points and len(eficiencia_points) >= 3:
        for q, eff in eficiencia_points:
            lines.append(f'{eficiencia_curve_name}    {q:.4f}      {eff:.4f}')
        lines.append('')
    elif eficiencia_points and len(eficiencia_points) >= 2:
        # Interpolar para tener al menos 3 puntos
        q1, eff1 = eficiencia_points[0]
        q2, eff2 = eficiencia_points[-1]
        q_mid = (q1 + q2) / 2
        eff_mid = (eff1 + eff2) / 2
        lines.append(f'{eficiencia_curve_name}    {q1:.4f}      {eff1:.4f}')
        lines.append(f'{eficiencia_curve_name}    {q_mid:.4f}      {eff_mid:.4f}')
        lines.append(f'{eficiencia_curve_name}    {q2:.4f}      {eff2:.4f}')
        lines.append('')
    else:
        lines.append(f';No hay datos de curva de rendimiento')
        lines.append('')
    
    # ===== 3. CURVA DE POTENCIA (PBHP-Q) - POWER vs FLOW =====
    # WaterGEMS no tiene tipo POWER en CURVES, se usa VOLUME para curvas genéricas
    potencia_curve_name = f'POW_{project_name}_100RPM'
    lines.append(f';POWER CURVE PBHP-Q: {project_name} - 100% RPM')
    lines.append(f';Curva de potencia al freno (kW) vs caudal (L/s)')
    potencia_points = data['inputs']['curva_inputs'].get('potencia', [])
    if potencia_points and len(potencia_points) >= 3:
        for q, p in potencia_points:
            lines.append(f'{potencia_curve_name}    {q:.4f}      {p:.4f}')
        lines.append('')
    elif potencia_points and len(potencia_points) >= 2:
        # Interpolar para tener al menos 3 puntos
        q1, p1 = potencia_points[0]
        q2, p2 = potencia_points[-1]
        q_mid = (q1 + q2) / 2
        p_mid = (p1 + p2) / 2
        lines.append(f'{potencia_curve_name}    {q1:.4f}      {p1:.4f}')
        lines.append(f'{potencia_curve_name}    {q_mid:.4f}      {p_mid:.4f}')
        lines.append(f'{potencia_curve_name}    {q2:.4f}      {p2:.4f}')
        lines.append('')
    else:
        lines.append(f';No hay datos de curva de potencia')
        lines.append('')
    
    # ===== 4. CURVA NPSH REQUERIDO (NPSHR-Q) - NPSH vs FLOW =====
    # WaterGEMS no reconoce tipo NPSH en CURVES, pero se puede incluir como referencia
    npsh_curve_name = f'NPSH_{project_name}_100RPM'
    lines.append(f';NPSH REQUIRED CURVE NPSHR-Q: {project_name} - 100% RPM')
    lines.append(f';Curva de NPSH requerido (m) vs caudal (L/s)')
    npsh_points = data['inputs']['curva_inputs'].get('npsh', [])
    if len(npsh_points) >= 3:
        for q, n in npsh_points:
            lines.append(f'{npsh_curve_name}    {q:.4f}      {n:.4f}')
    else:
        if len(npsh_points) >= 2:
            q1, n1 = npsh_points[0]
            q2, n2 = npsh_points[-1]
            q_mid = (q1 + q2) / 2
            n_mid = (n1 + n2) / 2
            lines.append(f'{npsh_curve_name}    {q1:.4f}      {n1:.4f}')
            lines.append(f'{npsh_curve_name}    {q_mid:.4f}      {n_mid:.4f}')
            lines.append(f'{npsh_curve_name}    {q2:.4f}      {n2:.4f}')
    lines.append('')

    lines.append('[CONTROLS]')
    lines.append('')

    lines.append('[RULES]')
    lines.append('')

    lines.append('[ENERGY]')
    lines.append('Global Efficiency  {:.1f}'.format(data['resultados']['motor_bomba']['motor_seleccionado']['eficiencia_porcentaje']))
    lines.append('Global Price       0')
    lines.append('Demand Charge      0')
    lines.append('')

    lines.append('[EMITTERS]')
    lines.append(';Junction        Coefficient')
    lines.append('')

    lines.append('[QUALITY]')
    lines.append(';Node            InitQual')
    lines.append('')

    lines.append('[SOURCES]')
    lines.append(';Node            Type        Quality     Pattern')
    lines.append('')

    lines.append('[REACTIONS]')
    lines.append(';Type     Pipe/Tank       Coefficient')
    lines.append('')

    lines.append('[REACTIONS]')
    lines.append(' Order Bulk            1')
    lines.append(' Order Tank            1')
    lines.append(' Order Wall            1')
    lines.append(' Global Bulk           0')
    lines.append(' Global Wall           0')
    lines.append(' Limiting Potential    0')
    lines.append(' Roughness Correlation 0')
    lines.append('')

    lines.append('[MIXING]')
    lines.append(';Tank            Model')
    lines.append('')

    lines.append('[TIMES]')
    lines.append(' Duration           0:00')
    lines.append(' Hydraulic Timestep 1:00')
    lines.append(' Quality Timestep   0:05')
    lines.append(' Pattern Timestep   1:00')
    lines.append(' Pattern Start      0:00')
    lines.append(' Report Timestep    1:00')
    lines.append(' Report Start       0:00')
    lines.append(' Start ClockTime    12 am')
    lines.append(' Statistic          NONE')
    lines.append('')

    lines.append('[REPORT]')
    lines.append(' Status             Yes')
    lines.append(' Summary            Yes')
    lines.append(' Page               0')
    lines.append('')

    # Determinar método de cálculo según session_state
    metodo_calc = st.session_state.get('metodo_calculo', 'Hazen-Williams')
    is_dw = metodo_calc == 'Darcy-Weisbach'
    loss_option = "D-W" if is_dw else "H-W"

    lines.append('[OPTIONS]')
    lines.append(' Units              LPS')
    lines.append(f' Headloss           {loss_option}        ;{metodo_calc}')
    lines.append(' Specific Gravity   1')
    lines.append(' Viscosity          1')
    lines.append(' Trials             40')
    lines.append(' Accuracy           0.001')
    lines.append(' CHECKFREQ          2')
    lines.append(' MAXCHECK           10')
    lines.append(' DAMPLIMIT          0')
    lines.append(' Unbalanced         Continue 10')
    lines.append(' Pattern            PAT_CONSTANT')
    lines.append(' Demand Multiplier  1.0')
    lines.append(' Emitter Exponent   0.5')
    lines.append(' Quality            None mg/L')
    lines.append(' Diffusivity        1')
    lines.append(' Tolerance          0.01')
    lines.append('')

    lines.append('[COORDINATES]')
    lines.append(';Node            X-Coord         Y-Coord')
    # Coordenadas con espaciado adecuado para visualización
    x_reservoir = 0.0
    x_suction = len_suc_total * 10  # Escalar para mejor visualización
    x_impulsion = x_suction + 10
    x_discharge = x_impulsion + (len_imp_total * 10)
    
    lines.append(f'R_Suction       {x_reservoir:.2f}            0.00')
    lines.append(f'J_Suction       {x_suction:.2f}            0.00')
    lines.append(f'J_Impulsion     {x_impulsion:.2f}            0.00')
    lines.append(f'J_Discharge     {x_discharge:.2f}            0.00')
    lines.append('')

    lines.append('[VERTICES]')
    lines.append(';Link            X-Coord         Y-Coord')
    lines.append('')

    lines.append('[LABELS]')
    lines.append(';X-Coord           Y-Coord          Label & Anchor Node')
    lines.append('')

    lines.append('[BACKDROP]')
    lines.append(' DIMENSIONS     0.00            0.00            10000.00        10000.00')
    lines.append(' UNITS          None')
    lines.append(' FILE')
    lines.append(' OFFSET         0.00            0.00')
    lines.append('')

    lines.append('[END]')
    return '\n'.join(lines)

def generate_epanet_inp_vfd(data, use_mm=False):
    """
    Genera .inp para VFD con datos reales del proyecto, escalando curvas con rpm_percentage.
    
    Args:
        data: Diccionario con datos del proyecto
        use_mm: Si True, usa milímetros para diámetros. Si False, usa metros (default)
    """
    data = clean_json_for_curves(data)
    ratio = data['inputs']['vfd']['rpm_percentage'] / 100.0
    lines = []
    lines.append('[TITLE]')
    lines.append(f'Sistema de Bombeo {data["inputs"]["proyecto"]} - EPANET VFD ({data["inputs"]["vfd"]["rpm_percentage"]:.1f}% RPM)')
    lines.append('')

    # Determinar método de cálculo según session_state
    metodo_calc = st.session_state.get('metodo_calculo', 'Hazen-Williams')
    is_dw = metodo_calc == 'Darcy-Weisbach'
    loss_option = "D-W" if is_dw else "H-W"

    lines.append('[OPTIONS]')
    lines.append('FLOW UNITS LPS')
    lines.append(f'HEADLOSS {loss_option}        ;{metodo_calc}')
    lines.append('VISCOSITY 1.004E-06')
    lines.append('TRIALS 40')
    lines.append('ACCURACY 0.001')
    lines.append('QUALITY NONE')
    lines.append('HEADFLOW UNITS LPS')
    lines.append('')

    # CÁLCULO DE COTAS REALES (igual que en base)
    cota_eje_bomba = data['inputs']['elevacion_sitio']
    altura_succion = data['inputs']['altura_succion']
    
    # Calcular cota del espejo de agua (nivel del tanque de succión)
    # altura_succion ya tiene el signo correcto:
    # - Positivo: bomba inundada (agua arriba del eje)
    # - Negativo: bomba no inundada (agua abajo del eje)
    cota_espejo_agua = cota_eje_bomba + altura_succion
    
    altura_descarga = data['resultados']['alturas']['estatica_total']
    cota_descarga = cota_eje_bomba + altura_descarga
    
    lines.append('[RESERVOIRS]')
    lines.append(f'Reservoir_Suction {cota_espejo_agua:.3f}')
    lines.append('')

    lines.append('[JUNCTIONS]')
    lines.append(f'Junction_Suction {cota_eje_bomba:.3f} 0')
    lines.append(f'Junction_Impulsion {cota_eje_bomba:.3f} 0')
    caudal_dem = data['inputs']['caudal_diseno_lps']
    lines.append(f'Junction_Discharge {cota_descarga:.3f} {caudal_dem:.3f}')
    lines.append('')

    lines.append('[PIPES]')
    # TUBERÍA DE SUCCIÓN: datos reales
    len_suc_real = data['inputs'].get('long_succion', 0)
    len_equiv_suc = data['resultados']['succion'].get('long_equiv_accesorios', 0)
    len_suc_total = len_suc_real + len_equiv_suc
    diam_suc_mm = data['inputs'].get('diam_succion_mm', 0)
    
    # TUBERÍA DE IMPULSIÓN: datos reales
    len_imp_real = data['inputs'].get('long_impulsion', 0)
    len_equiv_imp = data['resultados']['impulsion'].get('long_equiv_accesorios', 0)
    len_imp_total = len_imp_real + len_equiv_imp
    diam_imp_mm = data['inputs'].get('diam_impulsion_mm', 0)

    # Usar mm o m según configuración
    if use_mm:
        diam_suc_value = diam_suc_mm
        diam_imp_value = diam_imp_mm
        diam_format = '.2f'
    else:
        diam_suc_value = diam_suc_mm / 1000.0
        diam_imp_value = diam_imp_mm / 1000.0
        diam_format = '.4f'

    # Determinar rugosidad según método
    if is_dw:
        rough_suc = obtener_rugosidad_absoluta(data['inputs'].get('material_succion', 'PVC')) * 1000.0
        rough_imp = obtener_rugosidad_absoluta(data['inputs'].get('material_impulsion', 'PVC')) * 1000.0
    else:
        rough_suc = data['inputs'].get('coeficiente_hazen_succion', 150)
        rough_imp = data['inputs'].get('coeficiente_hazen_impulsion', 150)
    
    lines.append(f'Pipe_Suction Reservoir_Suction Junction_Suction {len_suc_total:.3f} {diam_suc_value:{diam_format}} {rough_suc:.4f} 0 Open')
    lines.append(f'Pipe_Impulsion Junction_Impulsion Junction_Discharge {len_imp_total:.3f} {diam_imp_value:{diam_format}} {rough_imp:.4f} 0 Open')
    lines.append('')

    lines.append('[PUMPS]')
    lines.append('Pump1 Junction_Suction Junction_Impulsion CURVE_PUMP_VFD')
    lines.append('')

    lines.append('[CURVES]')
    lines.append(';ID              X-Value     Y-Value')
    lines.append('')
    
    # ===== 1. CURVA DE LA BOMBA (H-Q) - HEAD vs FLOW (VFD ESCALADA) =====
    lines.append(f';PUMP CURVE H-Q VFD: {data["inputs"]["vfd"]["rpm_percentage"]:.1f}% RPM')
    lines.append(f';Curva escalada con leyes de afinidad: Q2=Q1*(N2/N1), H2=H1*(N2/N1)^2')
    lines.append('CURVE_PUMP_VFD HEAD')
    bomba_points = data['inputs']['curva_inputs'].get('bomba', [])
    if len(bomba_points) >= 3:
        for q, h in bomba_points:
            q_new = q * ratio
            h_new = h * (ratio ** 2)
            lines.append(f'{q_new:.4f} {h_new:.4f}')
    else:
        if len(bomba_points) >= 2:
            q1, h1 = bomba_points[0]
            q2, h2 = bomba_points[-1]
            q_mid = (q1 + q2) / 2
            h_mid = h1 + (h2 - h1) * (q_mid - q1) / (q2 - q1)
            lines.append(f'{q1 * ratio:.4f} {h1 * (ratio ** 2):.4f}')
            lines.append(f'{q_mid * ratio:.4f} {h_mid * (ratio ** 2):.4f}')
            lines.append(f'{q2 * ratio:.4f} {h2 * (ratio ** 2):.4f}')
    lines.append('')
    
    # ===== 2. CURVA DE RENDIMIENTO (η-Q) - EFFICIENCY vs FLOW (VFD) =====
    lines.append(f';EFFICIENCY CURVE η-Q VFD: {data["inputs"]["vfd"]["rpm_percentage"]:.1f}% RPM')
    lines.append(f';Curva de rendimiento escalada')
    lines.append('CURVE_EFF_VFD EFFICIENCY')
    eficiencia_points = data['inputs']['curva_inputs'].get('rendimiento', [])
    if eficiencia_points and len(eficiencia_points) >= 3:
        for q, eff in eficiencia_points:
            q_new = q * ratio
            # Eficiencia se mantiene aproximadamente igual en VFD
            lines.append(f'{q_new:.4f} {eff:.4f}')
        lines.append('')
    elif eficiencia_points and len(eficiencia_points) >= 2:
        q1, eff1 = eficiencia_points[0]
        q2, eff2 = eficiencia_points[-1]
        q_mid = (q1 + q2) / 2
        eff_mid = (eff1 + eff2) / 2
        lines.append(f'{q1 * ratio:.4f} {eff1:.4f}')
        lines.append(f'{q_mid * ratio:.4f} {eff_mid:.4f}')
        lines.append(f'{q2 * ratio:.4f} {eff2:.4f}')
        lines.append('')
    else:
        lines.append(';No hay datos de curva de rendimiento')
        lines.append('')
    
    # ===== 3. CURVA DE POTENCIA (PBHP-Q) - POWER vs FLOW (VFD ESCALADA) =====
    lines.append(f';POWER CURVE PBHP-Q VFD: {data["inputs"]["vfd"]["rpm_percentage"]:.1f}% RPM')
    lines.append(f';Curva escalada con leyes de afinidad: P2=P1*(N2/N1)^3')
    lines.append('CURVE_POW_VFD POWER')
    potencia_points = data['inputs']['curva_inputs'].get('potencia', [])
    if potencia_points and len(potencia_points) >= 3:
        for q, p in potencia_points:
            q_new = q * ratio
            p_new = p * (ratio ** 3)  # Potencia escala con cubo de RPM
            lines.append(f'{q_new:.4f} {p_new:.4f}')
        lines.append('')
    elif potencia_points and len(potencia_points) >= 2:
        q1, p1 = potencia_points[0]
        q2, p2 = potencia_points[-1]
        q_mid = (q1 + q2) / 2
        p_mid = (p1 + p2) / 2
        lines.append(f'{q1 * ratio:.4f} {p1 * (ratio ** 3):.4f}')
        lines.append(f'{q_mid * ratio:.4f} {p_mid * (ratio ** 3):.4f}')
        lines.append(f'{q2 * ratio:.4f} {p2 * (ratio ** 3):.4f}')
        lines.append('')
    else:
        lines.append(';No hay datos de curva de potencia')
        lines.append('')
    
    # ===== 4. CURVA NPSH REQUERIDO (NPSHR-Q) - NPSH vs FLOW (VFD ESCALADA) =====
    lines.append(f';NPSH REQUIRED CURVE NPSHR-Q VFD: {data["inputs"]["vfd"]["rpm_percentage"]:.1f}% RPM')
    lines.append(f';Curva escalada con leyes de afinidad: NPSH2=NPSH1*(N2/N1)^2')
    lines.append('CURVE_PUMP_NPSH_VFD NPSH')
    npsh_points = data['inputs']['curva_inputs'].get('npsh', [])
    if len(npsh_points) >= 3:
        for q, n in npsh_points:
            q_new = q * ratio
            n_new = n * (ratio ** 2)  # NPSH escala con cuadrado de RPM
            lines.append(f'{q_new:.4f} {n_new:.4f}')
    else:
        if len(npsh_points) >= 2:
            q1, n1 = npsh_points[0]
            q2, n2 = npsh_points[-1]
            q_mid = (q1 + q2) / 2
            n_mid = n1 + (n2 - n1) * (q_mid - q1) / (q2 - q1)
            lines.append(f'{q1 * ratio:.4f} {n1 * (ratio ** 2):.4f}')
            lines.append(f'{q_mid * ratio:.4f} {n_mid * (ratio ** 2):.4f}')
            lines.append(f'{q2 * ratio:.4f} {n2 * (ratio ** 2):.4f}')
    lines.append('')
    lines.append('')

    lines.append('[DEMANDS]')
    lines.append('; Ya definidas en junctions')
    lines.append('')

    lines.append('[PATTERNS]')
    lines.append('PATTERN_CONSTANT 1.0')
    lines.append('')

    lines.append('[REPORT]')
    lines.append('STATUS YES')
    lines.append('SUMMARY YES')
    lines.append('')

    lines.append('[ENERGY]')
    lines.append('GLOBAL PATTERN PATTERN_CONSTANT')
    eff_porcentaje = data['resultados']['motor_bomba']['motor_seleccionado']['eficiencia_porcentaje']
    lines.append(f'GLOBAL EFFIC {eff_porcentaje:.1f}')  # Corregido: GLOBAL EFFIC en %
    lines.append('')

    lines.append('[COORDINATES]')
    lines.append(';Node            X-Coord         Y-Coord')
    # Coordenadas con espaciado adecuado para visualización
    x_reservoir = 0.0
    x_suction = len_suc_total * 10  # Escalar para mejor visualización
    x_impulsion = x_suction + 10
    x_discharge = x_impulsion + (len_imp_total * 10)
    
    lines.append(f'Reservoir_Suction       {x_reservoir:.2f}            0.00')
    lines.append(f'Junction_Suction        {x_suction:.2f}            0.00')
    lines.append(f'Junction_Impulsion      {x_impulsion:.2f}            0.00')
    lines.append(f'Junction_Discharge      {x_discharge:.2f}            0.00')
    lines.append('')

    lines.append('[VERTICES]')
    lines.append(';Link            X-Coord         Y-Coord')
    lines.append('')

    lines.append('[LABELS]')
    lines.append(';X-Coord           Y-Coord          Label & Anchor Node')
    lines.append('')

    lines.append('[BACKDROP]')
    lines.append(' DIMENSIONS     0.00            0.00            10000.00        10000.00')
    lines.append(' UNITS          None')
    lines.append(' FILE')
    lines.append(' OFFSET         0.00            0.00')
    lines.append('')

    lines.append('[END]')
    return '\n'.join(lines)


def calcular_bep_bomba(bomba):
    """Calcula el Punto de Rendimiento Óptimo (BEP) a partir de las curvas"""
    q_bep, h_bep, p_bep, eta_max = 0.0, 0.0, 0.0, 0.0
    try:
        # 1. Buscar maximo rendimiento
        if bomba.get('curvas', {}).get('rendimiento'):
            rend_pts = bomba['curvas']['rendimiento']
            if len(rend_pts) > 0:
                q_bep, eta_max = max(rend_pts, key=lambda x: x[1])
                
                # 2. Interpolar H en la curva HQ
                if bomba.get('curvas', {}).get('hq'):
                    hq_pts = sorted(bomba['curvas']['hq'], key=lambda x: x[0])
                    if len(hq_pts) > 0:
                        h_bep = hq_pts[0][1] # Default
                        for i in range(len(hq_pts)-1):
                            q1, h1 = hq_pts[i]
                            q2, h2 = hq_pts[i+1]
                            if q1 <= q_bep <= q2:
                                if q2 != q1:
                                    h_bep = h1 + (h2-h1)*(q_bep-q1)/(q2-q1)
                                else:
                                    h_bep = h1
                                break
                            elif q_bep > hq_pts[-1][0]:
                                h_bep = hq_pts[-1][1]
                    
                # 3. Potencia en el BEP (kW)
                # P = (rho * g * Q * H) / (eta/100)
                if eta_max > 0:
                    p_bep = (1000 * 9.81 * (q_bep/1000.0) * h_bep) / (eta_max/100.0)
    except Exception as e:
        print(f"Error calculando BEP: {e}")
    return q_bep, h_bep, p_bep, eta_max


def calcular_inercia_bomba(caudal_lps, bomba, h_m=None):
    """Calcula el momento de inercia J (kg.m2) del grupo motobomba"""
    import math
    j_val = 0.5
    try:
        rho = 1000
        q_m3s = caudal_lps / 1000.0
        if h_m is None:
            h_m = st.session_state.get('adt_total', 100.0)
        
        eta_global = (st.session_state.get('eficiencia_operacion', 70.0)) / 100.0
        p_w = (rho * 9.81 * q_m3s * h_m) / eta_global if eta_global > 0 else 1000.0
        
        rpm = bomba.get("rpm_actual", 3500)
        omega = (2 * math.pi * rpm) / 60.0 # rad/s
        
        # Tiempo de parada estimado (s) - por defecto 2s
        t_parada = st.session_state.get('tiempo_parada_bomba', 2.0)
        
        # Ecuacion de la energia: J * omega^2 / 2 = P * t_parada
        if omega > 0:
            j_val = (2 * t_parada * p_w) / (omega**2)
        
        # Limitar valor razonable
        j_val = max(0.01, min(j_val, 50.0))
    except:
        pass
    return j_val


def generate_epanet_inp_bombeo_mejorado(data, use_mm=False, use_allievi=False, force_100rpm=False):
    """
    Genera archivo .inp MEJORADO para análisis de bombeo (steady-state)
    Incluye válvula de compuerta y tanque de descarga con geometría completa
    
    Args:
        data: Diccionario con datos del proyecto
        use_mm: Si True, usa milímetros para diámetros
        use_allievi: Si True, genera formato compatible con Allievi (tabs, secciones extra, etc)
        force_100rpm: Si True, fuerza el uso de curvas de 100% RPM (sin escalar)
    
    Returns:
        String con contenido del archivo .inp
    """
    try:
        # Obtener datos del sistema usando las nuevas funciones
        cotas = obtener_cotas_sistema()
        tuberias = obtener_propiedades_tuberias()
        bomba = obtener_propiedades_bomba(force_100rpm=force_100rpm)  # Pasar flag
        
        # Calcular BEP e Inercia usando las nuevas funciones
        q_bep, h_bep, p_bep, eta_max_bep = calcular_bep_bomba(bomba)
        j_val = calcular_inercia_bomba(caudal_lps=data.get('inputs', {}).get('caudal_diseno_lps', 25.0), bomba=bomba)
        
        coordenadas = calcular_coordenadas_geometria(cotas)
        
        # Datos del proyecto
        proyecto = data.get('inputs', {}).get('proyecto', 'PROYECTO')
        caudal_lps = data.get('inputs', {}).get('caudal_diseno_lps', 25.0)
        
        lines = []
        
        # [TITLE] - SIN TILDES NI CARACTERES ESPECIALES
        lines.append('[TITLE]')
        lines.append(f'Sistema de Bombeo: {proyecto}')
        lines.append(f'Tipo de Analisis: BOMBEO (Regimen Permanente)')
        # Mostrar 100% RPM si force_100rpm está activo
        if force_100rpm:
            lines.append(f'Configuracion: 100.0% RPM ({bomba["rpm_nominal"]:.0f} RPM)')
        else:
            lines.append(f'Configuracion: {bomba["rpm_percentage"]:.1f}% RPM ({bomba["rpm_actual"]:.0f} RPM)')
        lines.append(f'Caudal de diseno: {caudal_lps:.2f} L/s')
        
        # Unificar IDs para Allievi si se requiere
        if use_allievi:
            id_ns = "NS"
            id_ni = "NI"
            id_nv = "NV"
            id_td = "TD"
            id_ts = "TS"
            id_bomba = "B1" # Sera BB1 en Allievi
            id_tag_bomba = "BB1"
            id_pipe_suc = "TPS"
            id_pipe_imp = "TPI"
        else:
            id_ns = "NS"
            id_ni = "NI"
            id_nv = "NV"
            id_td = "TD"
            id_ts = "TS"
            id_bomba = "B1"
            id_tag_bomba = "B1"
            id_pipe_suc = "PS"
            id_pipe_imp = "PI"
        
        # Resultados de la App para validación en EPANET
        lines.append('')
        lines.append(';--- RESULTADOS CALCULADOS POR LA APLICACION (Validacion) ---')
        adt_app = st.session_state.get('adt_total', 0)
        hf_suc = st.session_state.get('hf_total_succion', 0)
        hf_imp = st.session_state.get('hf_total_impulsion', 0)
        pot_hp = st.session_state.get('potencia_operacion', 0)
        eff_p = st.session_state.get('eficiencia_operacion', 0)
        
        lines.append(f';ADT App: {adt_app:.2f} m')
        lines.append(f';Perdidas Succion: {hf_suc:.2f} m')
        lines.append(f';Perdidas Impulsion: {hf_imp:.2f} m')
        lines.append(f';Potencia Requerida: {pot_hp:.2f} HP')
        lines.append(f';Eficiencia Operacion: {eff_p:.2f} %')
        lines.append(';-----------------------------------------------------------')
        
        lines.append('')
        lines.append('GEOMETRIA DEL SISTEMA:')
        lines.append(f'- Cota Eje Bomba: {cotas["cota_eje_bomba"]:.2f} m.s.n.m.')
        lines.append(f'- Tanque Succion: Solera {cotas["cota_solera_succion"]:.2f} m, Nivel {cotas["cota_nivel_agua_succion"]:.2f} m')
        lines.append(f'- Tanque Descarga: Solera {cotas["cota_solera_descarga"]:.2f} m, Nivel {cotas["cota_nivel_agua_descarga"]:.2f} m')
        lines.append('')
        
        lines.append('[JUNCTIONS]')
        lines.append(';ID              Elev            Demand          Pattern')
        lines.append(f'{id_ns:<15} {cotas["cota_eje_bomba"]:.3f}        0               ;Nodo Succion')
        lines.append(f'{id_ni:<15} {cotas["cota_eje_bomba"]:.3f}        0               ;Nodo Impulsion')
        lines.append(f'{id_nv:<15} {cotas["cota_valvula"]:.3f}        0               ;Nodo Valvula')
        
        # Ajuste para Allievi: El nudo final TD debe tener la misma cota que NV para válvulas
        cota_td = cotas["cota_valvula"] if use_allievi else cotas["cota_nivel_agua_descarga"]
        lines.append(f'{id_td:<15} {cota_td:.3f}        {caudal_lps:.3f}        ;Nodo Descarga')
        lines.append('')
        
        if use_allievi:
            lines.append('[RESERVOIRS]')
            lines.append('')
            lines.append('[TANKS]')
            lines.append(';ID              Elevation       InitLevel       MinLevel        MaxLevel        Diameter        MinVol          VolCurve')
            lines.append(f'{id_ts:<15} {cotas["cota_solera_succion"]:.3f}        {cotas["altura_succion"]:.3f}          0               {cotas["prof_tanque_succion"]:.3f}      1000            0')
        else:
            lines.append('[RESERVOIRS]')
            lines.append(';ID              Head            Pattern')
            lines.append(f'{id_ts:<15} {cotas["cota_nivel_agua_succion"]:.3f}                ;Tanque Succion')
        lines.append('')
        
        
        # Propiedades de tuberías para el archivo
        diam_suc = tuberias['succion']['diametro_interno_mm'] if use_mm else tuberias['succion']['diametro_interno_m']
        diam_imp = tuberias['impulsion']['diametro_interno_mm'] if use_mm else tuberias['impulsion']['diametro_interno_m']
        diam_unit = "mm" if use_mm else "m"
        
        long_suc = tuberias['succion']['longitud']
        long_imp = tuberias['impulsion']['longitud']
        
        # Ajuste de longitud para Allievi para evitar error de trazado (L > dZ)
        if use_allievi:
            dz_suc = abs(cotas["cota_eje_bomba"] - cotas["cota_solera_succion"])
            if long_suc < (dz_suc + 0.5):
                long_suc = dz_suc + 1.0  # Asegurar que L > dZ
        
        # CALCULAR K DE ACCESORIOS A PARTIR DE PÉRDIDAS SECUNDARIAS
        # K = hf_accesorios × 2g / V²
        import math
        g = 9.81  # m/s²
        
        # Obtener pérdidas secundarias de la app
        hf_sec_suc = st.session_state.get('hf_secundaria_succion', 0.0)
        hf_sec_imp = st.session_state.get('hf_secundaria_impulsion', 0.0)
        
        # Obtener velocidades
        v_suc = st.session_state.get('velocidad_succion', 0.0)
        v_imp = st.session_state.get('velocidad_impulsion', 0.0)
        
        # Calcular K
        if v_suc > 0.001:
            k_suc = (hf_sec_suc * 2 * g) / (v_suc ** 2)
        else:
            k_suc = tuberias['succion']['k_accesorios']
        
        if v_imp > 0.001:
            k_imp = (hf_sec_imp * 2 * g) / (v_imp ** 2)
        else:
            k_imp = tuberias['impulsion']['k_accesorios']
        
        mat_suc = tuberias['succion']['material'].split('(')[0].strip()
        mat_imp = tuberias['impulsion']['material'].split('(')[0].strip()
        wave_suc = tuberias['succion']['celeridad_ms']
        wave_imp = tuberias['impulsion']['celeridad_ms']
        
        # Determinar método de cálculo según session_state
        metodo_calc = st.session_state.get('metodo_calculo', 'Hazen-Williams')
        is_dw = metodo_calc == 'Darcy-Weisbach'
        
        # Rugosidad para el archivo: C (H-W) o epsilon (D-W)
        if is_dw:
            rough_suc = tuberias['succion']['rugosidad_m'] * 1000.0  # EPANET usa mm para D-W
            rough_imp = tuberias['impulsion']['rugosidad_m'] * 1000.0
            rough_unit = "(mm)"
            rough_label = "(D-W e)"
        else:
            rough_suc = tuberias['succion']['c_hazen_williams']
            rough_imp = tuberias['impulsion']['c_hazen_williams']
            rough_unit = " "
            rough_label = "(C H-W)"
            
        lines.append('[PIPES]')
        lines.append(f';ID              Node1           Node2           Length          Diameter        Roughness       MinorLoss       Status')
        lines.append(f';                                                (m)             ({diam_unit})           {rough_label:<10}      (K)')
        lines.append(f';Material: {mat_suc}, WaveSpeed: {wave_suc:.0f} m/s')
        lines.append(f'{id_pipe_suc:<15} {id_ts:<15} {id_ns:<15} {long_suc:.3f}        {diam_suc:.4f}        {rough_suc:.4f}        {k_suc:.3f}            Open')
        lines.append(f';Material: {mat_imp}, WaveSpeed: {wave_imp:.0f} m/s')
        lines.append(f'{id_pipe_imp:<15} {id_ni:<15} {id_nv:<15} {long_imp:.3f}        {diam_imp:.4f}        {rough_imp:.4f}        {k_imp:.3f}            Open')
        lines.append('')
        
        # [PUMPS] - CON PROPIEDADES COMPLETAS
        lines.append('[PUMPS]')
        lines.append(';ID              Node1           Node2           Parameters')
        
        # Cálculo de inercia simplificado para exportación (Allievi)
        try:
            rho = 1000
            q_m3s = caudal_lps / 1000.0
            h_m = st.session_state.get('adt_total', 100.0)
            eta = (st.session_state.get('eficiencia_operacion', 70.0)) / 100.0
            rpm = bomba["rpm_actual"]
            p_w = (rho * 9.81 * q_m3s * h_m) / eta if eta > 0 else 1000.0
            omega = (2 * math.pi * rpm) / 60.0 # Usar math.pi
            t_parada = st.session_state.get('tiempo_parada_bomba', 2.0)
            j_val = (2 * t_parada * p_w) / (omega**2) if omega > 0 else 0.5
        except:
            j_val = 0.5
            
        # CALCULO DE BEP (Punto de Rendimiento Optimo) para Allievi
        # Ya calculado al inicio para uso en UI tambien

        allievi_params = f" ; I={j_val:.3f} Nnom={bomba['rpm_nominal']:.0f} VRet=Si" if use_allievi else ""
        lines.append(f';RPM: {bomba["rpm_actual"]:.0f}, Caudal: {caudal_lps:.2f} L/s, Eficiencia: {bomba["eficiencia_motor"]:.1f}%')
        
        # CRÍTICO PARA ALLIEVI: Usar curva "Por puntos" en lugar de "HEAD" (universal)
        if use_allievi:
            # Allievi requiere curva por puntos, no HEAD
            lines.append(f'{id_bomba:<15} {id_ns:<15} {id_ni:<15} CURVA_HQ{allievi_params}')
        else:
            # EPANET estándar usa HEAD
            lines.append(f'{id_bomba:<15} {id_ns:<15} {id_ni:<15} HEAD CURVA_HQ{allievi_params}')
        lines.append('')
        
        # [VALVES] - VALVULA CONECTADA DIRECTAMENTE A TD
        lines.append('[VALVES]')
        lines.append(';ID              Node1           Node2           Diameter        Type    Setting         MinorLoss')
        lines.append(f';Valvula de compuerta - En analisis de bombeo esta completamente ABIERTA')
        lines.append(f'V1              {id_nv:<15} {id_td:<15} {diam_imp:.4f}        GPV     CURVA_VALV      0')
        lines.append('')
        
        # [CURVES] - TODAS LAS CURVAS SIN TILDES
        lines.append('[CURVES]')
        lines.append(';ID              X-Value         Y-Value')
        
        # Maniobra para Allievi (Puntos de apertura)
        if use_allievi:
            lines.append(';MANIOBRA_V1 - Curva de maniobra apertura 100% total')
            lines.append('MANIOBRA_V1      0.0             1.0')
            lines.append('MANIOBRA_V1      10.0            1.0')
            lines.append('MANIOBRA_V1      100.0           1.0')
            lines.append('')
        
        # Curva de valvula abierta (perdida de carga minima)
        lines.append(';CURVA_VALV - Valvula completamente abierta (perdida minima)')
        lines.append('CURVA_VALV      0.0             0.0')
        lines.append('CURVA_VALV      100.0           0.01')
        lines.append('')
        
        # Calcular ratio VFD para escalar curvas
        rpm_ratio = bomba['rpm_percentage'] / 100.0
        is_vfd = rpm_ratio < 0.999  # Si no es 100%
        
        # Curva H-Q de la bomba - CON ESCALADO VFD Y DENSIFICACION
        # IMPORTANTE: WaterGEMS requiere que H sea estrictamente DECRECIENTE
        if bomba['curvas']['hq'] and len(bomba['curvas']['hq']) > 0:
            if is_vfd:
                lines.append(f';CURVA_HQ - Curva Altura-Caudal ESCALADA al {bomba["rpm_percentage"]:.1f}% RPM')
                lines.append(f';Leyes de afinidad: Q2=Q1*(N2/N1), H2=H1*(N2/N1)^2')
            else:
                lines.append(';CURVA_HQ - Curva Altura-Caudal (m vs L/s) - 100% RPM')
            
            # Procesar curva - USAR PUNTOS ORIGINALES SIN DENSIFICAR
            # La interpolación cúbica puede distorsionar la curva original
            curve_points = []
            for q, h in bomba['curvas']['hq']:
                # Los puntos ya vienen escalados de obtener_propiedades_bomba si es VFD
                curve_points.append((q, h))
            
            # Ordenar por Q ascendente
            curve_points.sort(key=lambda x: x[0])
            
            # Filtrar para que H sea ESTRICTAMENTE decreciente
            # (EPANET/WaterGEMS requiere curvas monótonas)
            filtered_points = []
            last_h = float('inf')
            epsilon = 0.001  # Tolerancia mínima
            
            for q, h in curve_points:
                # Solo agregar si H es menor que el anterior
                if h < (last_h - epsilon):
                    filtered_points.append((q, h))
                    last_h = h
            
            # Asegurar que comience en Q=0 con H máxima
            if len(filtered_points) > 0:
                max_h = max(h for q, h in curve_points)
                if filtered_points[0][0] > epsilon:
                    filtered_points.insert(0, (0.0, max_h))
                elif filtered_points[0][1] < max_h - epsilon:
                    filtered_points[0] = (0.0, max_h)
            
            # Exportar la curva filtrada
            lines.append(f';Puntos exportados: {len(filtered_points)} (puntos originales, H estrictamente decreciente)')
            for q, h in filtered_points:
                lines.append(f'CURVA_HQ        {q:.3f}           {h:.3f}')
            lines.append('')
        else:
            # Si no hay curva, agregar mensaje de advertencia
            lines.append(';ADVERTENCIA: No se encontro curva H-Q en session_state')
            lines.append(';Verifique que las curvas esten cargadas en la pestana Tablas')
            lines.append('')
        
        # Curva de rendimiento (La eficiencia se mantiene aproximadamente igual en VFD)
        if bomba['curvas']['rendimiento'] and len(bomba['curvas']['rendimiento']) > 0:
            if is_vfd:
                lines.append(f';CURVA_ETA - Curva de Rendimiento (%) - Q escalado al {bomba["rpm_percentage"]:.1f}% RPM')
            else:
                lines.append(';CURVA_ETA - Curva de Rendimiento (%)')
            for q, eta in bomba['curvas']['rendimiento']:
                # Los puntos ya vienen escalados de obtener_propiedades_bomba si es VFD
                lines.append(f'CURVA_ETA       {q:.3f}           {eta:.3f}')
            lines.append('')
        
        # Curva de potencia - CON ESCALADO VFD (P escala con cubo de RPM)
        if bomba['curvas']['potencia'] and len(bomba['curvas']['potencia']) > 0:
            if is_vfd:
                lines.append(f';CURVA_POT - Curva de Potencia (kW) - ESCALADA al {bomba["rpm_percentage"]:.1f}% RPM')
                lines.append(f';Ley de afinidad: P2=P1*(N2/N1)^3')
            else:
                lines.append(';CURVA_POT - Curva de Potencia (kW)')
            for q, p in bomba['curvas']['potencia']:
                # Los puntos ya vienen escalados de obtener_propiedades_bomba si es VFD
                lines.append(f'CURVA_POT       {q:.3f}           {p:.3f}')
            lines.append('')
        
        # Curva NPSH - CON ESCALADO VFD (NPSH escala con cuadrado de RPM)
        if bomba['curvas']['npsh'] and len(bomba['curvas']['npsh']) > 0:
            if is_vfd:
                lines.append(f';CURVA_NPSH - Curva NPSH Requerido (m) - ESCALADA al {bomba["rpm_percentage"]:.1f}% RPM')
                lines.append(f';Ley de afinidad: NPSH2=NPSH1*(N2/N1)^2')
            else:
                lines.append(';CURVA_NPSH - Curva NPSH Requerido (m)')
            for q, npsh in bomba['curvas']['npsh']:
                # Los puntos ya vienen escalados de obtener_propiedades_bomba si es VFD
                lines.append(f'CURVA_NPSH      {q:.3f}           {npsh:.3f}')
            lines.append('')
        
        # [ENERGY]
        lines.append('[ENERGY]')
        lines.append(f'GLOBAL EFFICIENCY  {bomba["eficiencia_motor"]:.1f}')
        lines.append('GLOBAL PRICE       0.0')
        lines.append('DEMAND CHARGE      0.0')
        lines.append('')
        
        # [STATUS]
        lines.append('[STATUS]')
        lines.append(';ID              Status/Setting')
        lines.append('V1              OPEN        ;Valvula abierta')
        lines.append('')
        
        # [COORDINATES] - INCLUYE JUNCTION_DEMAND
        lines.append('[COORDINATES]')
        lines.append(';Node            X-Coord         Y-Coord')
        # Mapeo de nombres largos a cortos
        coord_map = {
            'TANQUE_SUC': 'TS',
            'NODO_SUC': 'NS',
            'NODO_IMP': 'NI',
            'NODO_VALV': 'NV',
            'TANQUE_DESC': 'TD'
        }
        for nodo_largo, (x, y) in coordenadas.items():
            nodo_corto = coord_map.get(nodo_largo, nodo_largo)
            lines.append(f'{nodo_corto:<15} {x:.2f}          {y:.2f}')
        
        # TD ya está en coordenadas como TANQUE_DESC
        lines.append('')
        
        # [TAGS] - CRÍTICO PARA ALLIEVI (Inercia y Nnom y BEP)
        if use_allievi:
            lines.append('[TAGS]')
            lines.append(f'PUMP {id_tag_bomba} I {j_val:.3f}')
            lines.append(f'PUMP {id_tag_bomba} Nnom {bomba["rpm_nominal"]:.0f}')
            lines.append(f'PUMP {id_tag_bomba} Qnom {q_bep:.3f}')
            lines.append(f'PUMP {id_tag_bomba} Hnom {h_bep:.3f}')
            lines.append(f'PUMP {id_tag_bomba} Pnom {p_bep:.3f}')
            lines.append(f'PUMP {id_tag_bomba} VRet Si')
            lines.append('')
            
            # Tag para maniobra de valvula (Allievi 13 requiere puntos)
            lines.append(f'VALVE VV1 MANIOBRA_V1')
            lines.append('')
        
        # [OPTIONS] - USAR METODO SELECCIONADO
        loss_option = "D-W" if is_dw else "H-W"
        lines.append('[OPTIONS]')
        lines.append('UNITS              LPS')
        lines.append(f'HEADLOSS           {loss_option}        ;{metodo_calc}')
        lines.append('SPECIFIC GRAVITY   1.0')
        lines.append('VISCOSITY          1.0')
        lines.append('TRIALS             40')
        lines.append('ACCURACY           0.001')
        lines.append('UNBALANCED         CONTINUE 10')
        lines.append('PATTERN            1')
        lines.append('DEMAND MULTIPLIER  1.0')
        lines.append('EMITTER EXPONENT   0.5')
        lines.append('')
        
        # [CONTROLS] - Maniobra para Allievi
        if use_allievi:
            lines.append('[CONTROLS]')
            lines.append('; Definicion de maniobra para valvula V1 (Allievi)')
            lines.append('; Time (s) Status/Setting')
            lines.append(' LINK V1 OPEN AT TIME 0')
            lines.append('')
            
            lines.append('[RULES]')
            lines.append('')
        
        # [TIMES]
        lines.append('[TIMES]')
        lines.append('DURATION           0:00')
        lines.append('HYDRAULIC TIMESTEP 1:00')
        lines.append('QUALITY TIMESTEP   0:05')
        lines.append('PATTERN TIMESTEP   1:00')
        lines.append('PATTERN START      0:00')
        lines.append('REPORT TIMESTEP    1:00')
        lines.append('REPORT START       0:00')
        lines.append('START CLOCKTIME    12 am')
        lines.append('STATISTIC          NONE')
        lines.append('')
        
        # [REPORT]
        lines.append('[REPORT]')
        lines.append('STATUS             FULL')
        lines.append('SUMMARY            YES')
        lines.append('PAGE               0')
        lines.append('NODES              ALL')
        lines.append('LINKS              ALL')
        lines.append('')
        
        lines.append('[END]')
        
        # Convertir a formato Allievi si es necesario
        if use_allievi:
            return convert_to_allievi_format('\n'.join(lines))
        else:
            return '\n'.join(lines)
        
    except Exception as e:
        st.error(f"Error generando archivo .inp mejorado: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None


def load_project_data():
    """Carga los datos del proyecto DIRECTAMENTE desde st.session_state"""
    try:
        # Primero intentar tomar todo desde session_state directamente
        # Nota: Las claves reales en session_state son diferentes a las esperadas
        
        # Verificar si hay datos básicos en session_state
        has_data = any(key in st.session_state for key in ['proyecto', 'caudal_lps', 'long_succion', 'diam_succion_mm'])
        
        if has_data:
            # Construir datos desde session_state con las claves CORRECTAS
            organized_data = {
                'inputs': {
                    # Datos generales
                    'proyecto': st.session_state.get('proyecto', 'Proyecto Sin Nombre'),
                    'diseno': st.session_state.get('diseno', ''),
                    'elevacion_sitio': st.session_state.get('elevacion_sitio', 0.0),
                    # altura_succion puede estar como altura_succion_input o altura_succion
                    'altura_succion': st.session_state.get('altura_succion_input', st.session_state.get('altura_succion', 0.0)),
                    'altura_descarga': st.session_state.get('altura_descarga', 0.0),
                    # Caudal: la clave real es caudal_lps, no caudal_diseno_lps
                    'caudal_diseno_lps': st.session_state.get('caudal_lps', st.session_state.get('caudal_diseno_lps', 0.0)),
                    
                    # Datos de SUCCIÓN
                    'long_succion': st.session_state.get('long_succion', 0.0),
                    'diam_succion_mm': st.session_state.get('diam_succion_mm', 0.0),
                    'coeficiente_hazen_succion': st.session_state.get('coeficiente_hazen_succion', 150),
                    'material_succion': st.session_state.get('mat_succion', 'PVC'),
                    
                    # Datos de IMPULSIÓN
                    'long_impulsion': st.session_state.get('long_impulsion', 0.0),
                    'diam_impulsion_mm': st.session_state.get('diam_impulsion_mm', 0.0),
                    'coeficiente_hazen_impulsion': st.session_state.get('coeficiente_hazen_impulsion', 150),
                    'material_impulsion': st.session_state.get('mat_impulsion', 'PVC'),
                    
                    # Curvas de bomba
                    'curva_inputs': st.session_state.get('curva_inputs', {}),
                    
                    # VFD
                    'vfd': st.session_state.get('vfd', {'rpm_percentage': st.session_state.get('rpm_percentage', 100)})
                },
                'resultados': {
                    # Alturas - pueden estar como dict o valores individuales
                    'alturas': st.session_state.get('alturas', {
                        'estatica_total': st.session_state.get('altura_estatica_total', st.session_state.get('adt_total', 0.0))
                    }),
                    # Motor/bomba
                    'motor_bomba': st.session_state.get('motor_bomba', {
                        'motor_seleccionado': {
                            'eficiencia_porcentaje': st.session_state.get('eficiencia_motor', 80),
                            'potencia_kw': st.session_state.get('potencia_motor_final_kw', 0)
                        }
                    }),
                    # Succión - resultados de cálculo
                    'succion': st.session_state.get('succion', {
                        'long_equiv_accesorios': st.session_state.get('long_equiv_succion', st.session_state.get('hf_secundaria_succion', 0) / 0.01 if st.session_state.get('hf_secundaria_succion') else 0)
                    }),
                    # Impulsión - resultados de cálculo
                    'impulsion': st.session_state.get('impulsion', {
                        'long_equiv_accesorios': st.session_state.get('long_equiv_impulsion', st.session_state.get('hf_secundaria_impulsion', 0) / 0.01 if st.session_state.get('hf_secundaria_impulsion') else 0)
                    })
                }
            }
            
            # Si hay resultados en session_state como dicts separados, usarlos
            if 'perdida_total_succion' in st.session_state:
                organized_data['resultados']['succion']['long_equiv_accesorios'] = st.session_state.get('long_equiv_succion', 0)
            if 'perdida_total_impulsion' in st.session_state:
                organized_data['resultados']['impulsion']['long_equiv_accesorios'] = st.session_state.get('long_equiv_impulsion', 0)
            
            return organized_data
        
        # PRIORIDAD 2: Cargar desde archivo JSON si existe
        if 'current_project_path' in st.session_state:
            project_path = st.session_state['current_project_path']
            if os.path.exists(project_path):
                with open(project_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return organize_json_data(data)
        
        # Si no hay datos disponibles
        st.error("❌ No se encontraron datos del proyecto")
        st.info("💡 Asegúrese de haber cargado un proyecto y ejecutado los cálculos")
        return None
        
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo de datos del proyecto")
        return None
    except json.JSONDecodeError as e:
        st.error(f"❌ Error al leer el archivo JSON: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Error inesperado al cargar datos: {e}")
        st.exception(e)
        return None

def render_epanet_export_section():
    """Renderiza la sección de exportación a EPANET en la pestaña de informes"""
    st.markdown("#### 🌐 Exportar a EPANET")
    
    # Cargar datos del proyecto
    project_data = load_project_data()
    
    if project_data is None:
        return
    
    # --- FASE 1 MEJORA: Validación de datos mejorada con rangos ---
    inputs = project_data.get('inputs', {})
    resultados = project_data.get('resultados', {})
    
    # Validar datos críticos (presencia)
    missing_data = []
    warnings_data = []
    
    # Validaciones de presencia
    if not inputs.get('proyecto'):
        missing_data.append('Nombre del proyecto')
    if not inputs.get('caudal_diseno_lps'):
        missing_data.append('Caudal de diseño')
    if inputs.get('elevacion_sitio') is None:
        missing_data.append('Elevación del sitio')
    
    # Validación de diámetros con RANGOS (10-2000mm)
    diam_suc = inputs.get('diam_succion_mm', 0)
    diam_imp = inputs.get('diam_impulsion_mm', 0)
    
    if not diam_suc or diam_suc <= 0:
        missing_data.append('Diámetro de succión')
    elif diam_suc < 10:
        warnings_data.append(f'⚠️ Diámetro succión muy pequeño: {diam_suc}mm (mín. recomendado: 10mm)')
    elif diam_suc > 2000:
        warnings_data.append(f'⚠️ Diámetro succión muy grande: {diam_suc}mm (máx. recomendado: 2000mm)')
    
    if not diam_imp or diam_imp <= 0:
        missing_data.append('Diámetro de impulsión')
    elif diam_imp < 10:
        warnings_data.append(f'⚠️ Diámetro impulsión muy pequeño: {diam_imp}mm (mín. recomendado: 10mm)')
    elif diam_imp > 2000:
        warnings_data.append(f'⚠️ Diámetro impulsión muy grande: {diam_imp}mm (máx. recomendado: 2000mm)')
    
    # Validación de longitudes POSITIVAS
    long_suc = inputs.get('long_succion', 0)
    long_imp = inputs.get('long_impulsion', 0)
    
    if long_suc < 0:
        warnings_data.append(f'⚠️ Longitud succión negativa: {long_suc}m')
    if long_imp < 0:
        warnings_data.append(f'⚠️ Longitud impulsión negativa: {long_imp}m')
    
    # Validación de curva de bomba (mínimo 3 puntos)
    curva_inputs = inputs.get('curva_inputs', {})
    bomba_points = curva_inputs.get('bomba', [])
    
    if not bomba_points:
        missing_data.append('Curva de la bomba (H-Q)')
    elif len(bomba_points) < 3:
        warnings_data.append(f'⚠️ Curva H-Q tiene solo {len(bomba_points)} puntos (recomendado: mínimo 3)')
    
    # Validar otras curvas
    eff_points = curva_inputs.get('rendimiento', [])
    pot_points = curva_inputs.get('potencia', [])
    npsh_points = curva_inputs.get('npsh', [])
    
    if eff_points and len(eff_points) < 3:
        warnings_data.append(f'⚠️ Curva Eficiencia tiene solo {len(eff_points)} puntos')
    if pot_points and len(pot_points) < 3:
        warnings_data.append(f'⚠️ Curva Potencia tiene solo {len(pot_points)} puntos')
    if npsh_points and len(npsh_points) < 3:
        warnings_data.append(f'⚠️ Curva NPSH tiene solo {len(npsh_points)} puntos')
    
    # Validaciones de resultados
    if not resultados.get('succion') or 'long_equiv_accesorios' not in resultados.get('succion', {}):
        missing_data.append('Resultados de succión (longitud equivalente)')
    if not resultados.get('impulsion') or 'long_equiv_accesorios' not in resultados.get('impulsion', {}):
        missing_data.append('Resultados de impulsión (longitud equivalente)')
    if not resultados.get('alturas'):
        missing_data.append('Resultados de alturas')
    if not resultados.get('motor_bomba') or not resultados.get('motor_bomba', {}).get('motor_seleccionado'):
        missing_data.append('Resultados de motor/bomba')
    
    # Mostrar errores críticos
    if missing_data:
        st.error(f"❌ Faltan los siguientes datos del proyecto:")
        for item in missing_data:
            st.write(f"   • {item}")
        st.info("💡 Asegúrese de haber cargado un proyecto completo con todos los cálculos")
        return
    
    # Mostrar warnings (no bloquean)
    if warnings_data:
        with st.expander("⚠️ Advertencias de validación (ver detalles)", expanded=False):
            for warning in warnings_data:
                st.warning(warning)
    
    st.success("✅ Datos del proyecto cargados correctamente")
    
    # ===== SECCIÓN INFORMATIVA: Datos que se cargarán en el .inp =====
    with st.expander("📊 Datos del Proyecto para EPANET", expanded=False):
        # Calcular valores que se usarán
        cota_eje_bomba = project_data['inputs']['elevacion_sitio']
        altura_succion = project_data['inputs']['altura_succion']
        
        # Calcular cota del espejo de agua
        cota_espejo_agua = cota_eje_bomba + altura_succion
        
        # Determinar tipo de bomba para mostrar
        if altura_succion >= 0:
            tipo_bomba = "Inundada"
        else:
            tipo_bomba = "No inundada"
        
        altura_descarga = project_data['resultados']['alturas']['estatica_total']
        cota_descarga = cota_eje_bomba + altura_descarga
        
        # Datos de tuberías
        len_suc_real = project_data['inputs'].get('long_succion', 0)
        diam_suc_mm = project_data['inputs'].get('diam_succion_mm', 0)
        len_equiv_suc = project_data['resultados']['succion'].get('long_equiv_accesorios', 0)
        
        # Si longitud equivalente es 0, calcularla desde K
        if len_equiv_suc == 0:
            k_suc = calcular_k_total_accesorios('succion')
            diam_suc_m = diam_suc_mm / 1000.0  # Convertir mm a m
            f_aprox = 0.02  # Factor de fricción aproximado
            len_equiv_suc = k_suc * diam_suc_m / f_aprox if k_suc > 0 else 0
        
        len_suc_total = len_suc_real + len_equiv_suc
        haz_suc = project_data['inputs'].get('coeficiente_hazen_succion', 150)
        
        len_imp_real = project_data['inputs'].get('long_impulsion', 0)
        diam_imp_mm = project_data['inputs'].get('diam_impulsion_mm', 0)
        len_equiv_imp = project_data['resultados']['impulsion'].get('long_equiv_accesorios', 0)
        
        # Si longitud equivalente es 0, calcularla desde K
        if len_equiv_imp == 0:
            k_imp = calcular_k_total_accesorios('impulsion')
            diam_imp_m = diam_imp_mm / 1000.0  # Convertir mm a m
            f_aprox = 0.02  # Factor de fricción aproximado
            len_equiv_imp = k_imp * diam_imp_m / f_aprox if k_imp > 0 else 0
        
        len_imp_total = len_imp_real + len_equiv_imp
        haz_imp = project_data['inputs'].get('coeficiente_hazen_impulsion', 150)
        
        # Datos de motor/bomba
        caudal = project_data['inputs']['caudal_diseno_lps']
        eficiencia = project_data['resultados']['motor_bomba']['motor_seleccionado'].get('eficiencia_porcentaje', 0)
        potencia = project_data['resultados']['motor_bomba']['motor_seleccionado'].get('potencia_kw', 0)
        num_puntos_bomba = len(project_data['inputs']['curva_inputs'].get('bomba', []))
        
        # Obtener puntos de las curvas
        import pandas as pd
        bomba_points = project_data['inputs']['curva_inputs'].get('bomba', [])
        eficiencia_points = project_data['inputs']['curva_inputs'].get('rendimiento', [])
        potencia_points = project_data['inputs']['curva_inputs'].get('potencia', [])
        npsh_points = project_data['inputs']['curva_inputs'].get('npsh', [])
        
        # --- NUEVO: Cálculo de BEP e Inercia para mostrar en UI ---
        bomba_prop = obtener_propiedades_bomba()
        q_bep_ui, h_bep_ui, p_bep_ui, eta_bep_ui = calcular_bep_bomba(bomba_prop)
        j_val_ui = calcular_inercia_bomba(caudal, bomba_prop)
        
        # ===== CREAR 5 COLUMNAS CON SECCIONES COMPLETAS =====
        col1, col2, col3, col4, col5 = st.columns([20, 20, 20, 20, 20])
        
        # ===== COLUMNA 1: ELEVACIONES =====
        with col1:
            st.markdown("#### 🏔️ Elevaciones")
            st.markdown("")
            st.markdown("**Cota Eje Bomba**")
            st.markdown(f"{cota_eje_bomba:.2f} m")
            st.markdown("")
            st.markdown("**Cota Espejo Agua**")
            st.markdown(f"{cota_espejo_agua:.2f} m")
            st.markdown("")
            st.markdown("**Cota Descarga**")
            st.markdown(f"{cota_descarga:.2f} m")
            st.markdown("")
            st.markdown("**Tipo Bomba**")
            st.markdown(f"{tipo_bomba}")
        
        # ===== COLUMNA 2: ALTURAS =====
        with col2:
            st.markdown("#### 📏 Alturas")
            st.markdown("")
            st.markdown("**Altura Succión**")
            st.markdown(f"{altura_succion:.2f} m")
            st.markdown("")
            st.markdown("**Altura Descarga**")
            st.markdown(f"{altura_descarga:.2f} m")
            st.markdown("")
            st.markdown("**Altura Estática**")
            st.markdown(f"{altura_descarga:.2f} m")
            st.markdown("")
            st.markdown("**Diferencia Nivel**")
            st.markdown(f"{abs(altura_succion):.2f} m")
        
        # ===== COLUMNA 3: TUBERÍA SUCCIÓN =====
        with col3:
            st.markdown("#### 🔵 Succión")
            st.markdown("")
            st.markdown("**Longitud Física**")
            st.markdown(f"{len_suc_real:.2f} m")
            st.markdown("")
            st.markdown("**Long. Equivalente**")
            st.markdown(f"{len_equiv_suc:.2f} m")
            st.markdown("")
            st.markdown("**Long. TOTAL**")
            st.markdown(f"**{len_suc_total:.2f} m**")
            st.markdown("")
            st.markdown("**Ø Interno**")
            st.markdown(f"{diam_suc_mm:.1f} mm")
            st.markdown("")
            st.markdown("**C (Hazen-Williams)**")
            st.markdown(f"{haz_suc}")
        
        # ===== COLUMNA 4: TUBERÍA IMPULSIÓN =====
        with col4:
            st.markdown("#### 🔴 Impulsión")
            st.markdown("")
            st.markdown("**Longitud Física**")
            st.markdown(f"{len_imp_real:.2f} m")
            st.markdown("")
            st.markdown("**Long. Equivalente**")
            st.markdown(f"{len_equiv_imp:.2f} m")
            st.markdown("")
            st.markdown("**Long. TOTAL**")
            st.markdown(f"**{len_imp_total:.2f} m**")
            st.markdown("")
            st.markdown("**Ø Interno**")
            st.markdown(f"{diam_imp_mm:.1f} mm")
            st.markdown("")
            st.markdown("**C (Hazen-Williams)**")
            st.markdown(f"{haz_imp}")
        
        # ===== COLUMNA 5: MOTOR/BOMBA Y CAUDAL =====
        with col5:
            st.markdown("#### ⚙️ Motor/Bomba")
            st.markdown("")
            st.markdown("**Eficiencia Motor**")
            st.markdown(f"{eficiencia:.1f} %")
            st.markdown("")
            st.markdown("**Potencia Motor**")
            st.markdown(f"{potencia:.2f} kW")
            st.markdown("")
            st.markdown("**Puntos Curva H-Q**")
            st.markdown(f"{num_puntos_bomba}")
            st.markdown("")
            st.markdown("**Caudal Diseño**")
            st.markdown(f"{caudal:.2f} L/s")
            st.markdown("")
            st.markdown("**Estado**")
            st.markdown("✅ Configurado")
        
        st.markdown("---")
        
        # ===== SECCIÓN 5: CURVAS DE LA BOMBA (SIN CAMBIOS) =====
        st.markdown("#### 📊 Curvas de la Bomba")
        
        curve_col1, curve_col2, curve_col3, curve_col4, curve_col5 = st.columns([20, 20, 20, 20, 20])
        
        with curve_col1:
            st.markdown("**H-Q (Altura)**")
            if bomba_points:
                df_bomba = pd.DataFrame(bomba_points, columns=['Q (L/s)', 'H (m)'])
                st.dataframe(
                    df_bomba.style.format({'Q (L/s)': '{:.2f}', 'H (m)': '{:.2f}'}),
                    hide_index=True,
                    use_container_width=True,
                    height=150
                )
            else:
                st.caption("No hay datos")
        
        with curve_col2:
            st.markdown("**η-Q (Rendimiento)**")
            if eficiencia_points:
                df_eficiencia = pd.DataFrame(eficiencia_points, columns=['Q (L/s)', 'η (%)'])
                st.dataframe(
                    df_eficiencia.style.format({'Q (L/s)': '{:.2f}', 'η (%)': '{:.2f}'}),
                    hide_index=True,
                    use_container_width=True,
                    height=150
                )
            else:
                st.caption("No hay datos")
        
        with curve_col3:
            st.markdown("**P-Q (Potencia)**")
            if potencia_points:
                df_potencia = pd.DataFrame(potencia_points, columns=['Q (L/s)', 'P (kW)'])
                st.dataframe(
                    df_potencia.style.format({'Q (L/s)': '{:.2f}', 'P (kW)': '{:.2f}'}),
                    hide_index=True,
                    use_container_width=True,
                    height=150
                )
            else:
                st.caption("No hay datos")
        
        with curve_col4:
            st.markdown("**NPSH-Q**")
            if npsh_points:
                df_npsh = pd.DataFrame(npsh_points, columns=['Q (L/s)', 'NPSH (m)'])
                st.dataframe(
                    df_npsh.style.format({'Q (L/s)': '{:.2f}', 'NPSH (m)': '{:.2f}'}),
                    hide_index=True,
                    use_container_width=True,
                    height=150
                )
            else:
                st.caption("No hay datos")
        
        with curve_col5:
            st.markdown("**Resumen**")
            st.markdown(f"✅ H-Q: {len(bomba_points)} pts")
            st.markdown(f"✅ η-Q: {len(eficiencia_points) if eficiencia_points else 0} pts")
            st.markdown(f"✅ P-Q: {len(potencia_points) if potencia_points else 0} pts")
            st.markdown(f"✅ NPSH: {len(npsh_points) if npsh_points else 0} pts")
        
        st.caption("**H-Q:** Altura-Caudal | **η-Q:** Rendimiento-Caudal | **P-Q:** Potencia-Caudal | **NPSH-Q:** NPSH requerido-Caudal")
    
    # ===== EXPANDER: Datos del Proyecto para ALLIEVI =====
    with st.expander("📊 Datos del Proyecto para ALLIEVI", expanded=False):
        st.info("ℹ️ Copiar estos datos manualmente en Allievi 13.0.0 después de importar el archivo .inp")
        
        # Obtener datos necesarios
        cotas = obtener_cotas_sistema()
        tuberias = obtener_propiedades_tuberias()
        
        # Detectar si VFD está activo (desde radio button en sección de configuración)
        rpm_option = st.session_state.get('epanet_rpm_option', '100% RPM (Base)')
        vfd_activo = (rpm_option == "VFD Personalizado")
        rpm_percentage = st.session_state.get('rpm_percentage', 100.0)
        
        # Seleccionar DataFrames según modo (VFD o 100% RPM)
        if vfd_activo and rpm_percentage < 100:
            # Usar datos de VFD
            df_bomba = st.session_state.get('df_bomba_vfd')
            df_potencia = st.session_state.get('df_potencia_vfd')
            df_rendimiento = st.session_state.get('df_rendimiento_vfd')
            rpm_text = f"{rpm_percentage:.2f}% RPM"
        else:
            # Usar datos de 100% RPM
            df_bomba = st.session_state.get('df_bomba_100')
            df_potencia = st.session_state.get('df_potencia_100')
            df_rendimiento = st.session_state.get('df_rendimiento_100')
            rpm_text = "100% RPM"
        
        # Obtener BEP desde session_state (calculado en analysis.py)
        # Esto asegura consistencia con los valores mostrados en Análisis
        q_bep, h_bep, p_bep_kw, eta_bep = 0, 0, 0, 0
        
        if vfd_activo and rpm_percentage < 100:
            # Usar BEP de VFD
            q_bep = st.session_state.get('bep_q_vfd', 0)
            h_bep = st.session_state.get('bep_h_vfd', 0)
            eta_bep = st.session_state.get('bep_eta_vfd', 0)
        else:
            # Usar BEP de 100% RPM
            q_bep = st.session_state.get('bep_q_100', 0)
            h_bep = st.session_state.get('bep_h_100', 0)
            eta_bep = st.session_state.get('bep_eta_100', 0)
        
        # Calcular potencia en el BEP: P = (rho * g * Q * H) / eta
        if eta_bep > 0 and q_bep > 0:
            p_bep_kw = (1000 * 9.81 * (q_bep/1000.0) * h_bep) / (eta_bep/100.0) / 1000  # kW
        # Calcular inercia
        bomba_props = obtener_propiedades_bomba(force_100rpm=True)
        caudal_lps = project_data['inputs'].get('caudal_diseno_lps', 25.0)
        j_val = calcular_inercia_bomba(caudal_lps, bomba_props)
        
        # ===== SECCIÓN 1: TABLA DE CURVAS (Q, H, P) - USAR DATOS DE session_state =====
        st.markdown(f"### 1️⃣ Curvas Características de Bomba ({rpm_text})")
        st.caption("**Copiar en Allievi**: Estación de Bombeo BB1 → Curvas características por puntos")
        
        # Crear tabla combinada Q, H, P (SIN Rendimiento)
        if df_bomba is not None and df_potencia is not None:
            # Extraer solo las columnas numéricas (filtrar "⭐" si existe)
            tabla_allievi = pd.DataFrame({
                'Q (l/s)': pd.to_numeric(df_bomba.iloc[:, 0], errors='coerce'),
                'H (m)': pd.to_numeric(df_bomba.iloc[:, 1].apply(lambda x: str(x).replace('⭐', '').strip()), errors='coerce'),
                'P (kw)': pd.to_numeric(df_potencia.iloc[:, 1].apply(lambda x: str(x).replace('⭐', '').strip()), errors='coerce')
            })
            
            # Eliminar filas con NaN
            tabla_allievi = tabla_allievi.dropna()
            
            # Convertir P de HP a kW
            tabla_allievi['P (kw)'] = tabla_allievi['P (kw)'] * 0.7457  # HP a kW
            
            # Crear dos columnas: tabla a la izquierda, texto para copiar a la derecha
            col_tabla, col_copiar = st.columns([3, 1])
            
            with col_tabla:
                st.dataframe(
                    tabla_allievi.style.format({
                        'Q (l/s)': '{:.2f}',
                        'H (m)': '{:.2f}',
                        'P (kw)': '{:.3f}'
                    }),
                    hide_index=True,
                    use_container_width=True,
                    height=300
                )
            
            with col_copiar:
                st.markdown("**📋 Copiar**")
                # Crear texto para copiar
                curve_text = "Q (l/s)\tH (m)\tP (kw)\n"
                for _, row in tabla_allievi.iterrows():
                    curve_text += f"{row['Q (l/s)']:.2f}\t{row['H (m)']:.2f}\t{row['P (kw)']:.3f}\n"
                
                if st.button("📋 Copiar", key="copy_curves_allievi"):
                    st.code(curve_text, language=None)
            
            st.caption(f"📊 {len(tabla_allievi)} puntos | {rpm_text} ({bomba_props['rpm_nominal']:.0f} RPM nominal)")
            
            # Validar rango para Allievi
            from utils.allievi_validation import validar_rango_primer_cuadrante
            validacion = validar_rango_primer_cuadrante(df_bomba, df_potencia)
            
            if validacion['completo']:
                st.success("✅ Curvas completas para método 'Curvas por Puntos' en Allievi (cubre Q=0 a H≈0)")
            else:
                st.warning("⚠️ Curvas incompletas. Ir a **Análisis → 8. Tablas → Activar 'Optimizar para Allievi'**")
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    if validacion['cubre_q_min']:
                        st.caption("✅ Q mínimo correcto")
                    else:
                        st.caption(f"❌ Q mínimo: {validacion['q_min_actual']:.2f} L/s (ajustar a 0)")
                with col_info2:
                    if validacion['cubre_h_min']:
                        st.caption("✅ H mínimo correcto")
                    else:
                        st.caption(f"⚠️ H mínimo: {validacion['h_min_actual']:.2f} m (activar extrapolación)")
        else:
            if vfd_activo and rpm_percentage < 100:
                st.warning(f"⚠️ No hay datos de tablas {rpm_percentage:.2f}% RPM disponibles. Ir a pestaña Análisis → sección 8. Tablas (VFD) y generar las tablas.")
            else:
                st.warning("⚠️ No hay datos de tablas 100% RPM disponibles. Ir a pestaña Análisis → sección 8. Tablas y generar las tablas.")
        
        st.markdown("---")
        
        # ===== SECCIONES 2-5 EN UNA SOLA FILA (5 COLUMNAS) =====
        col1, col2, col3, col4, col5 = st.columns(5)
        
        # COLUMNA 1: MANIOBRA DE VÁLVULA
        with col1:
            st.markdown("**2️⃣ Válvula VV1**")
            st.caption("Maniobra tabulada")
            valve_data = [
                {'t (s)': 0.0, 'Ap (%)': 100},
                {'t (s)': 10.0, 'Ap (%)': 100},
                {'t (s)': 100.0, 'Ap (%)': 100}
            ]
            df_valve = pd.DataFrame(valve_data)
            st.dataframe(df_valve, hide_index=True, use_container_width=True, height=130)
            if st.button("📋", key="copy_valve_allievi"):
                st.code("t (s)\tAp (%)\n0.0\t100\n10.0\t100\n100.0\t100")
        
        # COLUMNA 2: BEP
        with col2:
            st.markdown("**3️⃣ BEP**")
            st.caption("Punto óptimo")
            st.markdown(f"**Qnom:** {q_bep:.3f} L/s")
            st.markdown(f"**Hnom:** {h_bep:.3f} m")
            st.markdown(f"**Pnom:** {p_bep_kw:.3f} kW")
        
        # COLUMNA 3: CELERIDADES, ESPESORES Y MINOR LOSS
        with col3:
            st.markdown("**4️⃣ Tuberías**")
            st.caption("Celeridad, espesor y K")
            st.markdown(f"**TPS:**")
            st.markdown(f"• {tuberias['succion']['celeridad_ms']:.0f} m/s")
            st.markdown(f"• e: {tuberias['succion']['espesor_mm']/1000:.4f} m")
            # Minor Loss K (siempre mostrar para Allievi)
            k_suc = calcular_k_total_accesorios('succion')
            st.markdown(f"• K: {k_suc:.2f}")
            st.markdown(f"**TPI:**")
            st.markdown(f"• {tuberias['impulsion']['celeridad_ms']:.0f} m/s")
            st.markdown(f"• e: {tuberias['impulsion']['espesor_mm']/1000:.4f} m")
            # Minor Loss K (siempre mostrar para Allievi)
            k_imp = calcular_k_total_accesorios('impulsion')
            st.markdown(f"• K: {k_imp:.2f}")
        
        # COLUMNA 4: INERCIA Y RPM
        with col4:
            st.markdown("**5️⃣ Bomba BB1**")
            st.caption("Parámetros")
            st.markdown(f"**J:** {j_val:.4f} kg·m²")
            st.markdown(f"**Nnom:** {bomba_props['rpm_nominal']:.0f} RPM")
            st.success("✅ VRet: Sí")
        
        # COLUMNA 5: REFERENCIA
        with col5:
            st.markdown("**📈 Info**")
            st.caption("Datos del proyecto")
            if df_bomba is not None:
                st.markdown(f"Puntos H-Q: {len(df_bomba)}")
            if df_potencia is not None:
                st.markdown(f"Puntos P-Q: {len(df_potencia)}")
            st.markdown(f"**Material TPS:**")
            st.caption(f"{tuberias['succion']['material']}")
            st.markdown(f"**Material TPI:**")
            st.caption(f"{tuberias['impulsion']['material']}")
    
    # ===== SECCIÓN NORMAL: CONFIGURACIÓN DEL SISTEMA =====
    
    # Crear 5 columnas de 20% cada una
    col1, col2, col3, col4, col5 = st.columns([20, 20, 20, 20, 20])
    
    # ===== COLUMNA 1: Configuración =====
    with col1:
        st.markdown("**⚙️ Configuración**")
        
        # Tipo de exportación
        tipo_exportacion = st.selectbox(
            "Tipo de análisis",
            ["Sistema de Bombeo", "Análisis Transitorio"],
            index=0,
            key="epanet_tipo_exportacion",
            help="Seleccione el tipo de análisis EPANET"
        )
        
        # Mostrar información del proyecto
        st.markdown("**📋 Proyecto**")
        st.caption(f"🏷️ {project_data['inputs']['proyecto']}")
        st.caption(f"💧 Q: {project_data['inputs']['caudal_diseno_lps']:.2f} L/s")
        st.caption(f"📏 H: {project_data['resultados']['alturas']['estatica_total']:.2f} m")
    
    # ===== COLUMNA 2: Opciones de RPM =====
    with col2:
        st.markdown("**🔄 Velocidad de Bomba**")
        
        if tipo_exportacion == "Sistema de Bombeo":
            # Opción de RPM
            rpm_option = st.radio(
                "Seleccione RPM",
                ["100% RPM (Base)", "VFD Personalizado"],
                index=0,
                key="epanet_rpm_option"
            )
            
            # Si selecciona VFD, mostrar slider
            if rpm_option == "VFD Personalizado":
                # Verificar si hay datos VDF en el proyecto
                if 'vfd' in project_data['inputs'] and 'rpm_percentage' in project_data['inputs']['vfd']:
                    default_rpm = project_data['inputs']['vfd']['rpm_percentage']
                else:
                    default_rpm = 100.0
                
                rpm_percentage = st.slider(
                    "% RPM",
                    min_value=50.0,
                    max_value=100.0,
                    value=default_rpm,
                    step=0.5,
                    key="epanet_custom_rpm",
                    help="Ajuste el porcentaje de RPM para VFD"
                )
                st.caption(f"⚡ RPM: {rpm_percentage:.1f}%")
            else:
                rpm_percentage = 100.0
                st.caption("⚡ RPM: 100% (Nominal)")
        else:
            st.info("Análisis transitorio usa configuración base")
            rpm_percentage = 100.0
    
    # ===== COLUMNA 3: Configuración de Exportación =====
    with col3:
        st.markdown("**⚙️ Configuración**")
        
        # NUEVO: Selector de versión de exportación (solo para bombeo)
        if tipo_exportacion == "Sistema de Bombeo":
            version_export = st.radio(
                "Versión de exportación",
                ["Mejorada (con válvula y tanque)", "Clásica (nodo final)"],
                index=0,  # Por defecto la mejorada
                key="epanet_export_version",
                help="• **Mejorada**: Incluye válvula de compuerta y tanque de descarga con geometría completa\n• **Clásica**: Termina en nodo simple (versión anterior)"
            )
            st.session_state['epanet_use_mejorada'] = (version_export == "Mejorada (con válvula y tanque)")
            
            if st.session_state['epanet_use_mejorada']:
                st.caption("✅ Geometría completa con cotas")
            else:
                st.caption("⚠️ Versión simplificada")
        
        # Selector de unidades para diámetro
        diameter_unit = st.radio(
            "Unidad de diámetro",
            ["Metros (m)", "Milímetros (mm)"],
            index=1,  # Por defecto en milímetros (WaterGEMS)
            key="epanet_diameter_unit",
            help="• EPANET: Metros (m)\n• WaterGEMS: Milímetros (mm)"
        )
        
        # Guardar la selección en session_state
        if diameter_unit == "Metros (m)":
            st.session_state['epanet_use_mm'] = False
        else:
            st.session_state['epanet_use_mm'] = True
        
        # Selector de método de pérdidas por accesorios
        loss_method = st.radio(
            "Método de pérdidas",
            ["Longitud Equivalente", "Minor Loss (K)"],
            index=1,  # Por defecto Minor Loss para WaterGEMS
            key="epanet_loss_method",
            help="• Longitud Equiv.: Para EPANET (suma L_real + L_equiv)\n• Minor Loss (K): Para WaterGEMS (usa coeficiente K)"
        )
        
        # Guardar la selección de método de pérdidas
        if loss_method == "Minor Loss (K)":
            st.session_state['epanet_use_minor_loss'] = True
        else:
            st.session_state['epanet_use_minor_loss'] = False
        
        # NUEVO: Checkbox para formato Allievi
        use_allievi = st.checkbox(
            "Formato Allievi",
            value=False,
            key="epanet_use_allievi",
            help="✅ Activar para análisis transitorio con software Allievi\n• Usa TABS como separadores\n• Agrega secciones adicionales (CONTROLS, RULES, etc)\n• Compatible con análisis de golpe de ariete"
        )
        # NO asignar a session_state - el widget con key ya lo hace automáticamente
        
        if use_allievi:
            st.caption("🔨 Formato para transitorios (Allievi)")
        else:
            st.caption("💧 Formato estándar (EPANET/WaterGEMS)")
        
        # Mostrar K totales si está en modo Minor Loss
        if st.session_state.get('epanet_use_minor_loss', False) and not use_allievi:
            k_suc = calcular_k_total_accesorios('succion')
            k_imp = calcular_k_total_accesorios('impulsion')
            st.caption(f"K Succión: {k_suc:.2f}")
            st.caption(f"K Impulsión: {k_imp:.2f}")
    
    
    # ===== COLUMNA 4: Generación =====
    with col4:
        st.markdown("**🚀 Generar Archivo**")
        
        if tipo_exportacion == "Sistema de Bombeo":
            # Botón de generación
            if rpm_option == "100% RPM (Base)":
                button_label = "🔄 Generar Base"
                button_key = "generate_epanet_base_new"
            else:
                button_label = f"🔄 Generar VFD {rpm_percentage:.1f}%"
                button_key = "generate_epanet_vfd_new"
            
            if st.button(button_label, key=button_key, type="primary", use_container_width=True):
                with st.spinner("Generando archivo .inp..."):
                    try:
                        # Obtener configuración de exportación
                        use_mm = st.session_state.get('epanet_use_mm', False)
                        use_minor_loss = st.session_state.get('epanet_use_minor_loss', False)
                        use_mejorada = st.session_state.get('epanet_use_mejorada', True)
                        use_allievi = st.session_state.get('epanet_use_allievi', False)
                        
                        # Generar archivo según tipo y versión
                        if use_mejorada:
                            # VERSIÓN MEJORADA: Con válvula y tanque de descarga
                            # Determinar si forzar 100% RPM basado en selección del usuario
                            force_100rpm = (rpm_option == "100% RPM (Base)")
                            
                            # Generar archivo con flag force_100rpm
                            inp_text = generate_epanet_inp_bombeo_mejorado(
                                project_data, 
                                use_mm=use_mm, 
                                use_allievi=use_allievi,
                                force_100rpm=force_100rpm
                            )
                            
                            project_name_safe = get_project_name_safe(project_data)
                            
                            if rpm_option == "100% RPM (Base)":
                                filename = f"{project_name_safe}_bombeo_epanet_base.inp" if not use_allievi else f"{project_name_safe}_allievi.inp"
                            else:
                                filename = f"{project_name_safe}_bombeo_epanet_vfd_{rpm_percentage:.1f}rpm.inp" if not use_allievi else f"{project_name_safe}_allievi.inp"
                        else:
                            # VERSIÓN CLÁSICA: Nodo final simple
                            if rpm_option == "100% RPM (Base)":
                                inp_text = generate_epanet_inp_base(project_data, use_mm=use_mm, use_minor_loss=use_minor_loss)
                                project_name_safe = get_project_name_safe(project_data)
                                filename = f"{project_name_safe}_base.inp"
                            else:
                                # Actualizar rpm_percentage en project_data si es necesario
                                if 'vfd' not in project_data['inputs']:
                                    project_data['inputs']['vfd'] = {}
                                project_data['inputs']['vfd']['rpm_percentage'] = rpm_percentage
                                
                                inp_text = generate_epanet_inp_vfd(project_data, use_mm=use_mm)
                                project_name_safe = get_project_name_safe(project_data)
                                filename = f"{project_name_safe}_vfd_{rpm_percentage:.1f}rpm.inp"
                        
                        # Guardar archivo
                        filepath = f"resultados_EPANET/{filename}"
                        os.makedirs("resultados_EPANET", exist_ok=True)
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(inp_text)
                        
                        # Guardar en session_state para descarga
                        st.session_state['epanet_last_generated'] = {
                            'content': inp_text,
                            'filename': filename,
                            'filepath': filepath
                        }
                        
                        st.success(f"✅ Archivo generado: {filename}")
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc(), language='python')
            
            # Botón de descarga (si hay archivo generado)
            if 'epanet_last_generated' in st.session_state:
                last_gen = st.session_state['epanet_last_generated']
                st.download_button(
                    label="📥 Descargar .inp",
                    data=last_gen['content'],
                    file_name=last_gen['filename'],
                    mime='text/plain',
                    key="download_epanet_file",
                    use_container_width=True
                )
                
                # --- FASE 3: Preview del archivo generado ---
                with st.expander("👁️ Vista Previa del Archivo .inp", expanded=False):
                    lines = last_gen['content'].split('\n')
                    preview_lines = lines[:50]  # Primeras 50 líneas
                    preview_text = '\n'.join(preview_lines)
                    if len(lines) > 50:
                        preview_text += f"\n\n... ({len(lines) - 50} líneas más) ..."
                    st.code(preview_text, language='ini')
                    st.caption(f"📊 Total: {len(lines)} líneas | {len(last_gen['content'])} bytes")
        else:
            # Análisis Transitorio - Generar .inp para HAMMER o EPANET
            st.markdown("**🌊 Análisis Transitorio**")
            
            # Selector de formato
            formato_transient = st.radio(
                "Formato de archivo",
                ["HAMMER (con [TRANSIENT])", "EPANET (compatible WNTR)"],
                index=0,
                key="formato_transient_selector",
                help="HAMMER: Incluye sección [TRANSIENT] nativa\nEPANET: Compatible con WNTR (sin [TRANSIENT])"
            )
            
            formato_key = 'hammer' if 'HAMMER' in formato_transient else 'epanet'
            
            if st.button("🔄 Generar .inp Transitorio", key="generate_transient_inp", type="primary", use_container_width=True):
                with st.spinner("Generando archivo .inp para análisis transitorio..."):
                    try:
                        # Importar la función desde transient_analysis
                        from core.transient_analysis import generar_inp_transientes
                        
                        # Preparar datos en el formato esperado por generar_inp_transientes
                        datos_transientes = {
                            'inputs': {
                                'proyecto': project_data['inputs']['proyecto'],
                                'caudal_diseno_lps': project_data['inputs']['caudal_diseno_lps'],
                                'altura_succion': project_data['inputs']['altura_succion'],
                                'altura_descarga': project_data['inputs']['altura_descarga'],
                                'densidad_liquido': st.session_state.get('densidad_liquido', 1.0),
                                'succion': {
                                    'longitud': project_data['inputs'].get('long_succion', 0.0),
                                    'diametro_interno': project_data['inputs'].get('diam_succion_mm', 0.0),
                                    'material': st.session_state.get('mat_succion', 'PVC'),
                                    'espesor': st.session_state.get('espesor_succion', 10.0)
                                },
                                'impulsion': {
                                    'longitud': project_data['inputs'].get('long_impulsion', 0.0),
                                    'diametro_interno': project_data['inputs'].get('diam_impulsion_mm', 0.0),
                                    'material': st.session_state.get('mat_impulsion', 'PVC'),
                                    'espesor': st.session_state.get('espesor_impulsion', 8.0)
                                }
                            },
                            'resultados': {
                                'alturas': {
                                    'estatica_total': project_data['resultados']['alturas'].get('estatica_total', 0.0),
                                    'dinamica_total': st.session_state.get('adt_total', 0.0)
                                },
                                'bomba_seleccionada': {
                                    'curva_completa': project_data['inputs']['curva_inputs'].get('bomba', [])
                                }
                            }
                        }
                        
                        # Generar archivo .inp con formato seleccionado
                        inp_file = generar_inp_transientes(
                            datos_transientes, 
                            tipo_simulacion='valve_closure',
                            formato=formato_key
                        )
                        
                        if inp_file and os.path.exists(inp_file):
                            # Leer contenido del archivo
                            with open(inp_file, 'r', encoding='utf-8') as f:
                                inp_content = f.read()
                            
                            # Nombre del archivo según formato
                            formato_suffix = 'hammer' if formato_key == 'hammer' else 'epanet'
                            project_name_safe = get_project_name_safe(project_data)
                            filename = f"{project_name_safe}_transitorio_{formato_suffix}.inp"
                            
                            # Guardar en session_state para descarga
                            st.session_state['epanet_last_generated'] = {
                                'content': inp_content,
                                'filename': filename,
                                'filepath': inp_file
                            }
                            
                            if formato_key == 'hammer':
                                st.success(f"✅ Archivo .inp generado para HAMMER")
                                st.caption(f"📄 {filename}")
                                
                                # Mostrar opciones de configuración
                                st.markdown("### 🔧 Configuración de Wave Speed")
                                
                                config_method = st.radio(
                                    "Método de configuración:",
                                    ["Automático (Script Python)", "Manual (Copiar valores)"],
                                    key="config_method_hammer"
                                )
                                
                                if config_method == "Automático (Script Python)":
                                    st.info("""
                                    **📜 Script de configuración automática generado:**
                                    
                                    1. Instalar dependencia: `pip install pywin32`
                                    2. Abrir HAMMER y cargar el archivo .inp
                                    3. Ejecutar: `python resultados_transientes/configurar_hammer.py`
                                    4. El script configurará automáticamente wave speed en todas las tuberías
                                    
                                    📄 Archivos generados:
                                    - `configurar_hammer.py` - Script de configuración
                                    - `hammer_properties.txt` - Valores calculados
                                    """)
                                else:
                                    st.warning("""
                                    **⚠️ Configuración manual requerida:**
                                    
                                    1. Abrir archivo .inp en HAMMER
                                    2. Tools → Options → Transient
                                    3. Ver archivo `hammer_properties.txt` para valores exactos
                                    4. Configurar wave speed en cada tubería
                                    
                                    📄 Archivo con valores: `hammer_properties.txt`
                                    """)
                            else:
                                st.success(f"✅ Archivo .inp generado para EPANET/WNTR")
                                st.caption(f"📄 {filename}")
                                st.info("💡 Compatible con EPANET y WNTR (wave speed en comentarios)")
                        else:
                            st.error("❌ No se pudo generar el archivo .inp")
                            
                    except Exception as e:
                        st.error(f"❌ Error al generar archivo transitorio: {str(e)}")
                        st.exception(e)
            
            # Botón de descarga (si hay archivo generado)
            if 'epanet_last_generated' in st.session_state:
                last_gen = st.session_state['epanet_last_generated']
                st.download_button(
                    label="📥 Descargar .inp",
                    data=last_gen['content'],
                    file_name=last_gen['filename'],
                    mime='text/plain',
                    key="download_transient_file",
                    use_container_width=True
                )
                st.caption(f"📁 {last_gen['filepath']}")
    
    # ===== COLUMNA 4: Vista Previa =====
    with col4:
        st.markdown("**👁️ Vista Previa**")
        
        if 'epanet_last_generated' in st.session_state:
            last_gen = st.session_state['epanet_last_generated']
            
            # Mostrar primeras líneas del archivo
            preview_lines = last_gen['content'].split('\n')[:15]
            preview_text = '\n'.join(preview_lines)
            
            with st.expander("📄 Ver contenido", expanded=False):
                st.code(preview_text, language="text")
                st.caption(f"Mostrando primeras 15 líneas de {len(last_gen['content'].split(chr(10)))} totales")
        else:
            st.info("Genere un archivo para ver la vista previa")
    
    # ===== COLUMNA 5: Información =====
    with col5:
        st.markdown("**ℹ️ Información**")
        
        with st.expander("📋 Características .inp", expanded=False):
            st.markdown("""
            **Incluye:**
            - ✅ Red de tuberías
            - ✅ Curvas de bomba
            - ✅ Nodos y reservorios
            - ✅ Longitudes equivalentes
            - ✅ Coeficientes Hazen-Williams
            - ✅ Eficiencia del motor
            - ✅ Coordenadas de visualización
            """)
        
        with st.expander("🔧 Instrucciones", expanded=False):
            st.markdown("""
            **Pasos:**
            1. Configure el tipo de análisis
            2. Seleccione RPM deseado
            3. Genere el archivo .inp
            4. Descargue el archivo
            5. Abra en EPANET 2.0+
            6. Ejecute la simulación
            7. Analice resultados
            """)
        
        with st.expander("⚡ Leyes de Afinidad", expanded=False):
            st.markdown("""
            **Para VFD:**
            - Q₂ = Q₁ × (N₂/N₁)
            - H₂ = H₁ × (N₂/N₁)²
            - P₂ = P₁ × (N₂/N₁)³
            
            Donde N = RPM
            """)
        
        with st.expander("📊 Datos del Sistema", expanded=False):
            st.markdown(f"""
            **Proyecto:** {project_data['inputs']['proyecto']}
            
            **Succión:**
            - L: {project_data['inputs'].get('long_succion', 0):.2f} m
            - Ø: {project_data['inputs'].get('diam_succion_mm', 0):.1f} mm
            - C: {project_data['inputs'].get('coeficiente_hazen_succion', 150)}
            
            **Impulsión:**
            - L: {project_data['inputs'].get('long_impulsion', 0):.2f} m
            - Ø: {project_data['inputs'].get('diam_impulsion_mm', 0):.1f} mm
            - C: {project_data['inputs'].get('coeficiente_hazen_impulsion', 150)}
            
            **Motor:**
            - η: {project_data['resultados']['motor_bomba']['motor_seleccionado']['eficiencia_porcentaje']:.1f}%
            """)
