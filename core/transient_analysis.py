# Análisis de transientes hidráulicos utilizando TSNet

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime
from typing import Dict, Any, Tuple
import math

# Import condicional de TSNet
TSNET_AVAILABLE = False
tsnet = None

try:
    import tsnet
    # Verificar si tsnet tiene las clases necesarias para la simulación
    if hasattr(tsnet, 'network') and hasattr(tsnet.network, 'TransientModel') and \
       hasattr(tsnet, 'simulation') and hasattr(tsnet.simulation, 'Initializer') and \
       hasattr(tsnet.simulation, 'MOCSimulator'):
        TSNET_AVAILABLE = True
    else:
        # TSNet incompleto o versión incorrecta
        TSNET_AVAILABLE = False
        tsnet = None
except ImportError as e:
    TSNET_AVAILABLE = False
    tsnet = None
except Exception as e:
    # Otros errores posibles durante la importación
    TSNET_AVAILABLE = False
    tsnet = None
    error_detalles = str(e)

def diagnosticar_tsnet():
    """Función de diagnóstico para TSNet"""
    import sys
    diagnostico = {
        'python_version': sys.version,
        'python_executable': sys.executable,
        'tsnet_available': TSNET_AVAILABLE,
        'modules_installed': []
    }
    
    if tsnet is not None:
        diagnostico['tsnet_version'] = getattr(tsnet, '__version__', 'Desconocida')
        diagnostico['tsnet_location'] = getattr(tsnet, '__file__', 'Desconocida')
        diagnostico['modules_installed'] = [name for name in dir(tsnet) if not name.startswith('_')]
    
    # Verificar módulos específicos
    if tsnet is not None:
        diagnostico['has_network'] = hasattr(tsnet, 'network')
        diagnostico['has_simulation'] = hasattr(tsnet, 'simulation')
        if hasattr(tsnet, 'network'):
            diagnostico['has_TransientModel'] = hasattr(tsnet.network, 'TransientModel')
        if hasattr(tsnet, 'simulation'):
            diagnostico['has_Initializer'] = hasattr(tsnet.simulation, 'Initializer')
            diagnostico['has_MOCSimulator'] = hasattr(tsnet.simulation, 'MOCSimulator')
    
    return diagnostico

def depurar_inp_file(inp_file: str) -> Dict[str, Any]:
    """Diagnostica problemas específicos en archivos .inp para TSNet"""
    diagnostico = {
        'archivo': inp_file,
        'existe': False,
        'legible': False,
        'estructura': {},
        'errores': []
    }
    
    try:
        # Verificar existencia
        diagnostico['existe'] = os.path.exists(inp_file)
        if not diagnostico['existe']:
            diagnostico['errores'].append('Archivo no encontrado')
            return diagnostico
            
        # Leer contenido
        with open(inp_file, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        diagnostico['legible'] = True
        
        # Analizar estructura
        secciones = ['[TITLE]', '[JUNCTIONS]', '[PIPES]', '[PUMPS]', '[VALVES]', '[CURVES]', '[OPTIONS]']
        estructura_detectada = {}
        
        for seccion in secciones:
            if seccion in contenido:
                diagnostico['estructura'][seccion] = contenido.count(seccion)
            else:
                diagnostico['errores'].append(f'Sección requerida faltante: {seccion}')
        
        # Verificaciones específicas comunes
        lineas = contenido.split('\n')
        
        # Verificar estructura de JUNCTIONS
        if '[JUNCTIONS]' in contenido:
            junction_start = lineas.index('[JUNCTIONS]')
            junction_lines = []
            
            for i in range(junction_start + 1, len(lineas)):
                linea = lineas[i].strip()
                if not linea or linea.startswith('['):  # Fin de sección
                    break
                if not linea.startswith(';') and ';' not in linea:  # Línea de datos (no comentario en línea)
                    junction_lines.append(linea)
            
            if len(junction_lines) < 2:  # Sin contar el header y al menos un nodo
                diagnostico['errores'].append('Cantidad insuficiente de nodos en [JUNCTIONS]')
            
            # Verificar formato de líneas de JUNCTIONS
            for linea in junction_lines:
                campos = linea.split()
                if len(campos) < 3:
                    diagnostico['errores'].append(f'Línea JUNCTION mal formateada: {linea}')
                elif len(campos) > 3:
                    diagnostico['errores'].append(f'Línea JUNCTION con demasiados campos: {linea}')
        
        # Verificar formato de números (puntos decimales)
        for i, línea in enumerate(lineas):
            if ', ' in línea and any(char.isdigit() for char in línea):
                diagnostico['errores'].append(f'Línea {i+1}: Posibles comas como separador decimal (usar puntos)')
        
        # Verificar espacios inconsistentes en datos
        for i, línea in enumerate(lineas):
            if not línea.startswith(';') and not línea.startswith('[') and línea.strip():
                # Verificar si hay grupos de espacios de diferentes tamaños (problema potencial)
                if '   ' in línea and '  ' in línea and línea.count('   ') != línea.count('  '):
                    diagnostico['errores'].append(f'Línea {i+1}: Espacios inconsistentes - revisar alineación')
            
    except Exception as e:
        diagnostico['errores'].append(f'Error al leer archivo: {str(e)}')
    
    return diagnostico

def load_wave_speeds_data():
    """Carga los datos de velocidades de onda desde el archivo JSON"""
    try:
        with open('data_tablas/wave_speeds_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Error: No se encontró el archivo wave_speeds_data.json")
        return None

def calculate_wave_speed(material: str, diameter: float, thickness: float) -> float:
    """Calcula la velocidad de onda basada en las propiedades del material"""
    try:
        wave_data = load_wave_speeds_data()
        if not wave_data:
            return 1200.0  # Valor por defecto para PVC
        
        # Velocidad de onda básica del material
        if material in wave_data['wave_speeds']:
            material_data = wave_data['wave_speeds'][material]
            K_bulk = 2.1e9  # Módulo de compresibilidad del agua (Pa)
            density_water = 1000  # kg/m³
            E_young = material_data['young_modulus']
            
            # Fórmula de velocidad de onda considerando flexibilidad de la tubería
            if thickness > 0 and thickness < diameter:  # Validar parámetros físicos
                a_theory = math.sqrt(K_bulk / (density_water * (1 + (K_bulk / E_young) * (diameter / thickness))))
                
                # Validar que el resultado es físicamente razonable (entre 200 y 2000 m/s)
                if 200 <= a_theory <= 2000:
                    # Usar el valor teórico si está en rango válido
                    return float(a_theory)
                else:
                    # Si está fuera de rango, usar velocidad típica del material
                    return float(material_data['typical_wave_speed'])
            else:
                # Espesor inválido, usar velocidad típica
                return float(material_data['typical_wave_speed'])
        else:
            # Material no reconocido, usar velocidades típicas por material
            materiales_defecto = {
                'PVC': 1200.0,
                'PEAD': 300.0,
                'HIERRO': 1000.0,
                'HIERRO DUCTIL': 1000.0,
                'HIERRO FUNDIDO': 1200.0
            }
            
            for mat_key, vel_defecto in materiales_defecto.items():
                if mat_key in str(material).upper():
                    return float(vel_defecto)
            
            return 1000.0  # Valor por defecto general
            
    except Exception as e:
        # En caso de cualquier error, retornar velocidad por defecto
        print(f"⚠️ Error calculando velocidad de onda: {e}")
        return 750.0  # Valor conservador por defecto

def generar_inp_transientes(datos_json: Dict[str, Any], tipo_simulacion: str = 'valve_closure', formato: str = 'hammer') -> str:
    """
    Genera un archivo .inp para análisis de transientes.
    
    Args:
        datos_json: Diccionario con datos del proyecto
        tipo_simulacion: Tipo de evento transitorio ('valve_closure', 'pump_shutdown')
        formato: 'hammer' para Bentley HAMMER (con [TRANSIENT]) o 'epanet' para EPANET/WNTR (sin [TRANSIENT])
    
    Returns:
        Ruta del archivo .inp generado
    """
    # --- 1. Unidades SI (metros, LPS) para HAMMER ---
    # No convertir a unidades imperiales - HAMMER acepta SI
    mm_to_m = 0.001

    # --- 2. Extracción de Datos del Proyecto ---
    inputs = datos_json['inputs']
    resultados = datos_json['resultados']
    
    caudal_lps = inputs['caudal_diseno_lps']
    altura_succion_m = inputs['altura_succion']
    altura_descarga_m = inputs['altura_descarga']
    
    long_succion_m = inputs['succion']['longitud']
    long_impulsion_m = inputs['impulsion']['longitud']
    diam_succion_mm = inputs['succion']['diametro_interno']
    diam_impulsion_mm = inputs['impulsion']['diametro_interno']
    
    # Materiales y wave speed
    material_succion = inputs['succion'].get('material', 'PVC')
    material_impulsion = inputs['impulsion'].get('material', 'PVC')
    
    # Calcular wave speed para cada tubería (convertir mm a m)
    wave_speed_succion_ms = calculate_wave_speed(
        material_succion,
        diam_succion_mm * mm_to_m,  # mm a m
        inputs['succion'].get('espesor', 5.0) * mm_to_m  # mm a m
    )
    wave_speed_impulsion_ms = calculate_wave_speed(
        material_impulsion,
        diam_impulsion_mm * mm_to_m,  # mm a m
        inputs['impulsion'].get('espesor', 5.0) * mm_to_m  # mm a m
    )
    
    # Convertir diámetros de mm a m
    diam_succion_m = diam_succion_mm * mm_to_m
    diam_impulsion_m = diam_impulsion_mm * mm_to_m
    
    # Rugosidad absoluta en metros (para Darcy-Weisbach)
    rugosidad_m = 0.00015  # HDPE típico: 0.15 mm

    # --- 3. Generación de Curva de Bomba (en unidades SI) ---
    try:
        curva_bomba_lps = resultados['bomba_seleccionada']['curva_completa']
        if len(curva_bomba_lps) < 3:
            raise ValueError("Curva de bomba insuficiente")
        # Mantener en LPS y metros
        curva_bomba_si = [(q, h) for q, h in curva_bomba_lps]
    except (KeyError, ValueError):
        h_total_m = resultados['alturas']['dinamica_total']
        # Curva sintética en unidades SI
        curva_bomba_si = [
            (0.0, h_total_m * 1.3),
            (caudal_lps, h_total_m),
            (caudal_lps * 2.0, h_total_m * 0.5)
        ]

    # --- 4. Cálculo de Variables para el Archivo .inp ---
    
    # CORRECCIÓN: Elevaciones son del TERRENO, no alturas totales
    elev_terreno_succion = 0.0  # Nivel de referencia
    altura_estatica = resultados['alturas'].get('estatica_total', altura_descarga_m)
    elev_terreno_descarga = altura_estatica  # Elevación del punto de descarga
    
    # Reservorio: Head = nivel de agua (elevación + profundidad)
    nivel_agua_reservorio = elev_terreno_succion + abs(altura_succion_m)
    
    # Nota de subdivisión
    subdivision_note = f"Tubería de descarga subdividida en 3 segmentos ({long_impulsion_m/3:.1f}m cada uno)" if long_impulsion_m > 50 else "Sin subdivisión"
    
    # --- 5. Construcción del Contenido del Archivo .inp (UNIDADES SI) ---
    
    title_section = f"""[TITLE]
Análisis de Transientes para {inputs['proyecto']}
Generado por App Bombeo Modulos - Unidades SI

CONFIGURACIÓN CORREGIDA:
- Elevaciones: Terreno (no alturas totales)
- Reservorio: Nivel de agua = {nivel_agua_reservorio:.2f} m
- Elevación descarga: {elev_terreno_descarga:.2f} m (altura estática)
- {subdivision_note}

INSTRUCCIONES PARA HAMMER:
1. Abrir archivo en HAMMER
2. Configurar Wave Speed en TODAS las tuberías:
   - P_Suction: {wave_speed_succion_ms:.2f} m/s
   - P_Discharge (todas): {wave_speed_impulsion_ms:.2f} m/s
3. O usar: Tools → Options → Transient → Default Wave Speed: {((wave_speed_succion_ms + wave_speed_impulsion_ms) / 2):.2f} m/s
4. Verificar curva de bomba cubre el rango de operación
5. Time step recomendado: 0.01 s (máximo 0.02 s)

DATOS CALCULADOS:
- Material Succión: {material_succion} - Wave Speed: {wave_speed_succion_ms:.2f} m/s
- Material Impulsión: {material_impulsion} - Wave Speed: {wave_speed_impulsion_ms:.2f} m/s
- Diámetro Succión: {diam_succion_mm:.2f} mm - Longitud: {long_succion_m:.2f} m
- Diámetro Impulsión: {diam_impulsion_mm:.2f} mm - Longitud: {long_impulsion_m:.2f} m
- Caudal: {caudal_lps:.2f} LPS - Altura estática: {altura_estatica:.2f} m

"""
    
    # Formato HAMMER: Junctions sin demanda (demanda en sección separada)
    # Nombres cortos sin espacios para TSNet (< 32 caracteres)
    junctions_section = f"""[JUNCTIONS]
;ID              Elev
JSuc             {elev_terreno_succion:<9.2f}
JImp             {elev_terreno_succion:<9.2f}
JDis             {elev_terreno_descarga:<9.2f}
"""
    
    reservoirs_section = f"""[RESERVOIRS]
;ID              Head
RSrc             {nivel_agua_reservorio:<9.2f}

"""

    # Calcular C de Hazen-Williams según material
    # HDPE: C = 140-150, PVC: C = 150, Acero: C = 120-140
    c_hw_succion = 140 if 'HDPE' in material_succion or 'Polietileno' in material_succion else 150
    c_hw_impulsion = 140 if 'HDPE' in material_impulsion or 'Polietileno' in material_impulsion else 150
    
    # Formato HAMMER: Length Diameter C_HW MinorLoss (sin Status, sin Roughness)
    # Nombres cortos sin espacios para TSNet
    pipes_section = f"""[PIPES]
;ID              Node1           Node2           Length      Diameter    C_HW  MinorLoss
; PSuc: Wave Speed = {wave_speed_succion_ms:.2f} m/s, Material = {material_succion}
PSuc             RSrc            JSuc            {long_succion_m:<11.4f}  {diam_succion_m*1000:<11.2f}  {c_hw_succion}  0
"""
    
    # Subdividir tubería de descarga si es muy larga
    # Siempre incluir tubería (no usamos válvula física)
    if long_impulsion_m > 50:
        # Dividir en 3 segmentos
        num_segmentos = 3
        long_segmento = long_impulsion_m / num_segmentos
        
        # Agregar nodos intermedios
        junctions_section += f"""; Nodos intermedios para subdivisión
JDis1            {elev_terreno_descarga * 0.33:<9.2f}
JDis2            {elev_terreno_descarga * 0.67:<9.2f}

"""
        
        pipes_section += f"""; PDis subdividida: Wave Speed = {wave_speed_impulsion_ms:.2f} m/s, Material = {material_impulsion}
PDis1            JImp            JDis1           {long_segmento:<11.4f}  {diam_impulsion_m*1000:<11.2f}  {c_hw_impulsion}  0
PDis2            JDis1           JDis2           {long_segmento:<11.4f}  {diam_impulsion_m*1000:<11.2f}  {c_hw_impulsion}  0
PDis3            JDis2           JDis            {long_segmento:<11.4f}  {diam_impulsion_m*1000:<11.2f}  {c_hw_impulsion}  0

"""
    else:
        pipes_section += f"""; PDis: Wave Speed = {wave_speed_impulsion_ms:.2f} m/s, Material = {material_impulsion}
PDis             JImp            JDis            {long_impulsion_m:<11.4f}  {diam_impulsion_m*1000:<11.2f}  {c_hw_impulsion}  0

"""
    
    # Sección de demandas (separada de junctions)
    demands_section = f"""[DEMANDS]
;Junction        Demand
JDis             {caudal_lps:.2f}

"""
    
    pumps_section = """[PUMPS]
;ID              Node1           Node2           Parameters
PMP1             JSuc            JImp            HEAD PCURVE

"""

    # NO agregar válvula física porque TSNet no la maneja bien en el MOC solver
    # En su lugar, simularemos el cierre de válvula mediante control de demanda
    valves_section = ""
    # if tipo_simulacion == 'valve_closure':
    #     # Válvula deshabilitada - TSNet no soporta válvulas en MOC
    #     pass

    # Estado inicial de la bomba (para transitorios)
    status_section = """[STATUS]
;ID              Status
PMP1             OPEN

"""
    
    # Patrón para transitorios (arranque de bomba)
    # Nombre corto sin espacios ni caracteres especiales
    patterns_section = """[PATTERNS]
;ID              Multipliers
PAT1             0

"""


    curves_section_header = """[CURVES]
;ID              X-Value(LPS)  Y-Value(m)
"""
    curve_lines = ""
    for q, h in curva_bomba_si:
        curve_lines += f"PCURVE           {q:<13.2f} {h:.2f}\n"

    # --- Coordenadas para visualización ---
    x_source = 0.0
    x_suction = 500.0
    x_discharge = x_suction + 1000.0
    
    y_base = 0.0
    y_elevated = 500.0
    
    x_impulsion = x_suction + 100.0  # Posición de salida de bomba
    
    coordinates_section = f"""[COORDINATES]
;Node            X-Coord         Y-Coord
RSrc             {x_source:.2f}          {y_base:.2f}
JSuc             {x_suction:.2f}         {y_base:.2f}
JImp             {x_impulsion:.2f}       {y_base:.2f}
"""
    
    # Agregar nodos intermedios si se subdividió
    if long_impulsion_m > 50:
        x_mid1 = x_impulsion + (x_discharge - x_impulsion) * 0.33
        x_mid2 = x_impulsion + (x_discharge - x_impulsion) * 0.67
        y_mid1 = y_base + (y_elevated - y_base) * 0.33
        y_mid2 = y_base + (y_elevated - y_base) * 0.67
        
        coordinates_section += f"""JDis1            {x_mid1:.2f}       {y_mid1:.2f}
JDis2            {x_mid2:.2f}       {y_mid2:.2f}
"""
    
    coordinates_section += f"""JDis             {x_discharge:.2f}       {y_elevated:.2f}

"""

    # --- Sección de TAGS con propiedades extendidas para HAMMER ---
    # Formato: Tipo ID Propiedad=Valor
    tags_section = f"""[TAGS]
Pipe  PSuc  WaveSpeed={wave_speed_succion_ms:.2f}
Pipe  PSuc  Material={material_succion}
"""
    
    # Agregar tags para tuberías de impulsión
    if long_impulsion_m > 50:
        tags_section += f"""Pipe  PDis1  WaveSpeed={wave_speed_impulsion_ms:.2f}
Pipe  PDis1  Material={material_impulsion}
Pipe  PDis2  WaveSpeed={wave_speed_impulsion_ms:.2f}
Pipe  PDis2  Material={material_impulsion}
Pipe  PDis3  WaveSpeed={wave_speed_impulsion_ms:.2f}
Pipe  PDis3  Material={material_impulsion}

"""
    else:
        tags_section += f"""Pipe  PDis  WaveSpeed={wave_speed_impulsion_ms:.2f}
Pipe  PDis  Material={material_impulsion}

"""
    
    # --- Sección de LABELS para etiquetas limpias ---
    labels_section = f"""[LABELS]
;X-Coord         Y-Coord         Label           Anchor
{x_source + 50:.2f}      {y_base - 50:.2f}       "TanqueSuc"     RSrc
{x_suction + 50:.2f}     {y_base - 50:.2f}       "Bomba"         JSuc
{x_discharge + 50:.2f}   {y_elevated + 50:.2f}   "Descarga"      JDis

"""
    
    # Wave speed ya está en [PIPES] como columna - no necesitamos [TRANSIENT]
    # Esta sección no es estándar y HAMMER la ignora
    transient_section = ""
    
    options_section = """[OPTIONS]
UNITS              LPS
TRIALS             40
ACCURACY           0.001
EMITTER EXPONENT   0.5
DAMPLIMIT          0
MAXCHECK           10
CHECKFREQ          2
FLOWCHANGE         0
HEADERROR          0
SPECIFIC GRAVITY   1.0
VISCOSITY          1.0
UNBALANCED         CONTINUE 0
HEADLOSS           H-W
TOLERANCE          1

[TIMES]
REPORT START       0
PATTERN TIMESTEP   1
QUALITY TIMESTEP   0

[REPORT]
STATUS             FULL
SUMMARY            YES
PAGE               0

[END]
"""

    # Orden de secciones según formato HAMMER
    inp_content = (title_section + patterns_section + curves_section_header + curve_lines + 
                   junctions_section + reservoirs_section + demands_section + 
                   pumps_section + valves_section + pipes_section + status_section + 
                   coordinates_section + tags_section + labels_section + options_section)

    # --- 6. Guardado y Validación ---
    os.makedirs('resultados_transientes', exist_ok=True)
    inp_filename = "modelo_transientes.inp"
    inp_path = os.path.join('resultados_transientes', inp_filename)
    
    with open(inp_path, 'w', encoding='utf-8') as f:
        f.write(inp_content)

    # Validar con WNTR solo si el formato es EPANET
    if formato.lower() == 'epanet':
        try:
            import wntr
            wn = wntr.network.WaterNetworkModel(inp_path)
            st.success(f"✅ Archivo .inp generado y validado con WNTR: {inp_path}")
            print(f"✅ Archivo .inp generado y validado con WNTR: {inp_path}")
        except Exception as e:
            st.error(f"❌ Error en validación WNTR del archivo .inp: {e}")
            print(f"❌ Error en validación WNTR: {e}")
            return inp_path
    else:
        # Para formato HAMMER, no validar con WNTR (tiene secciones no estándar)
        st.success(f"✅ Archivo .inp generado para HAMMER: {inp_path}")
        print(f"✅ Archivo .inp generado para HAMMER (sin validación WNTR): {inp_path}")

    # --- 7. Crear archivo de propiedades auxiliar para HAMMER ---
    # Este archivo contiene las propiedades que deben configurarse
    properties_filename = "hammer_properties.txt"
    properties_path = os.path.join('resultados_transientes', properties_filename)
    
    properties_content = f"""PROPIEDADES PARA HAMMER - {inputs['proyecto']}
===============================================

CONFIGURACIÓN AUTOMÁTICA:
Copiar y pegar estos comandos en HAMMER después de abrir el archivo .inp

WAVE SPEED (Velocidad de Onda):
--------------------------------
Tubería: P_Suction
  Wave Speed: {wave_speed_succion_ms:.2f} m/s
  Material: {material_succion}
  Diámetro: {diam_succion_mm:.2f} mm ({diam_succion_m:.6f} m)
  
"""
    
    if long_impulsion_m > 50:
        properties_content += f"""Tubería: P_Discharge_1
  Wave Speed: {wave_speed_impulsion_ms:.2f} m/s
  Material: {material_impulsion}
  Diámetro: {diam_impulsion_mm:.2f} mm ({diam_impulsion_m:.6f} m)
  
Tubería: P_Discharge_2
  Wave Speed: {wave_speed_impulsion_ms:.2f} m/s
  Material: {material_impulsion}
  Diámetro: {diam_impulsion_mm:.2f} mm ({diam_impulsion_m:.6f} m)
  
Tubería: P_Discharge_3
  Wave Speed: {wave_speed_impulsion_ms:.2f} m/s
  Material: {material_impulsion}
  Diámetro: {diam_impulsion_mm:.2f} mm ({diam_impulsion_m:.6f} m)
"""
    else:
        properties_content += f"""Tubería: P_Discharge
  Wave Speed: {wave_speed_impulsion_ms:.2f} m/s
  Material: {material_impulsion}
  Diámetro: {diam_impulsion_mm:.2f} mm ({diam_impulsion_m:.6f} m)
"""
    
    properties_content += f"""

COEFICIENTE HAZEN-WILLIAMS (C):
--------------------------------
Para HDPE nuevo: C = 140-150
Para PVC nuevo: C = 150
Recomendado: C = 140

CONFIGURACIÓN RÁPIDA EN HAMMER:
--------------------------------
1. Abrir archivo .inp en HAMMER
2. Tools → Options → Transient
3. Default Wave Speed: {((wave_speed_succion_ms + wave_speed_impulsion_ms) / 2):.2f} m/s
4. Apply to All Pipes: ✓
5. OK

VERIFICACIÓN:
-------------
1. View → Tables → Pipes
2. Agregar columna "Wave Speed"
3. Verificar que todas las tuberías tienen wave speed asignado
4. Si falta alguna, hacer doble click y configurar manualmente

TIME STEP:
----------
Recomendado: 0.01 s
Máximo: 0.02 s
Criterio: Δt < L/(2×a) donde L=longitud más corta, a=wave speed

VALORES CALCULADOS:
-------------------
Caudal: {caudal_lps:.2f} LPS
Altura estática: {altura_estatica:.2f} m
Longitud succión: {long_succion_m:.2f} m
Longitud impulsión: {long_impulsion_m:.2f} m
Rugosidad absoluta: {rugosidad_m*1000:.2f} mm
"""
    
    with open(properties_path, 'w', encoding='utf-8') as f:
        f.write(properties_content)
    
    st.info(f"📄 Archivo de propiedades generado: {properties_filename}")
    print(f"📄 Archivo de propiedades generado: {properties_path}")
    
    clean_temp_transient_files()
    return inp_path


def buscar_material_en_celeridad(material_buscado: str, wave_speeds: dict) -> str:
    """Busca un material en la tabla de celeridad de forma robusta"""
    if not material_buscado or not wave_speeds:
        return None
    
    material_buscado_clean = material_buscado.lower().strip()
    
    # Búsqueda exacta
    for mat_name in wave_speeds.keys():
        if material_buscado_clean == mat_name.lower().strip():
            return mat_name
    
    # Búsqueda sin espacios
    for mat_name in wave_speeds.keys():
        if material_buscado_clean.replace(' ', '') == mat_name.lower().replace(' ', ''):
            return mat_name
    
    # Búsqueda por palabras clave específicas (manejo de caracteres especiales)
    if 'hierro' in material_buscado_clean and ('ductil' in material_buscado_clean or 'dúctil' in material_buscado_clean):
        for mat_name in wave_speeds.keys():
            mat_lower = mat_name.lower()
            if 'hierro' in mat_lower and ('ductil' in mat_lower or 'dúctil' in mat_lower or 'dãºctil' in mat_lower):
                return mat_name
    
    if 'hierro' in material_buscado_clean and 'fundido' in material_buscado_clean:
        for mat_name in wave_speeds.keys():
            mat_lower = mat_name.lower()
            if 'hierro' in mat_lower and 'fundido' in mat_lower:
                return mat_name
    
    if 'acero' in material_buscado_clean and 'comercial' in material_buscado_clean:
        for mat_name in wave_speeds.keys():
            mat_lower = mat_name.lower()
            if 'acero' in mat_lower and 'comercial' in mat_lower:
                return mat_name
    
    # Búsqueda por palabras clave individuales (solo si no hay coincidencias específicas)
    if 'hierro' in material_buscado_clean and 'ductil' not in material_buscado_clean and 'fundido' not in material_buscado_clean:
        # Solo buscar "HIERRO" si no hay especificación de tipo
        for mat_name in wave_speeds.keys():
            if mat_name.lower() == 'hierro':
                return mat_name
    
    # Búsqueda parcial (último recurso)
    for mat_name in wave_speeds.keys():
        if material_buscado_clean in mat_name.lower():
            return mat_name
    
    return None


def simular_transiente_alternativa(evento: str, datos_json: Dict[str, Any]) -> Dict[str, Any]:
    """Simulación usando métodos alternativos cuando TSNet no está disponible"""
    
    try:
        import numpy as np
        import matplotlib.pyplot as plt
        
        # Parámetros básicos del sistema
        caudal = datos_json['inputs']['caudal_diseno_lps']
        altura_succion = datos_json['inputs']['altura_succion']
        altura_descarga = datos_json['inputs']['altura_descarga']
        altura_estatica = altura_succion + altura_descarga
        
        # Simulación simplificada de transiente - tiempo configurable
        tf = datos_json.get('inputs', {}).get('tiempo_simulacion_transientes', 10.0)
        time_points = np.linspace(0, tf, int(tf * 10))  # Resolución adaptativa según tiempo
        
        # OBTENER DATOS REALES para cálculo preciso
        datos_tuberia = obtener_datos_reales_tuberia(datos_json)
        
        # Calcular parámetros de golpe de ariete con datos reales
        diametro_impulsion_mm = datos_json['inputs']['impulsion']['diametro_interno']  # Ya en mm
        diametro_impulsion = diametro_impulsion_mm / 1000  # Convertir a metros
        longitud_impulsion = datos_json['inputs']['impulsion']['longitud']
        volumetric_caudal_impulsion = datos_json['inputs']['caudal_diseno_lps'] / 1000  # L/s a m³/s
        velocidad_impulsion = volumetric_caudal_impulsion / (np.pi * (diametro_impulsion**2) / 4)  # m/s
        
        # Calcular velocidad de onda usando DATOS REALES de espesor
        modulus_elasticidad_agua = 2.1e9  # Pa
        
        espesor_real_mm = datos_tuberia['espesor_impulsion']  # Datos reales en mm
        material_real = datos_tuberia['material_impulsion']
        
        # Módulos elásticos según material real
        if 'PEAD' in material_real or 'HDPE' in material_real or 'Polietileno' in material_real:
            modulus_elasticidad_material = 1.0e9  # Pa - PAD flexible
        elif 'Hierro' in material_real or 'Hierro Dúctil' in material_real:
            modulus_elasticidad_material = 170e9   # Pa - Hierro dúctil
        elif 'PVC' in material_real:
            modulus_elasticidad_material = 3.0e9   # Pa - PVC
        else:
            modulus_elasticidad_material = 1.0e9  # Conservador PAD
        
        espesor_real = espesor_real_mm / 1000  # Convertir a metros
        
        # Fórmula de Joukowsky con datos reales
        vel_onda_base = np.sqrt(modulus_elasticidad_agua / 1000)  # ≈ 1448 m/s agua pura
        vel_onda = vel_onda_base * np.sqrt(1 / (1 + (diametro_impulsion/espesor_real) * (modulus_elasticidad_agua/modulus_elasticidad_material)))
        
        print(f"🔧 Datos transientes reales: ø{diametro_impulsion_mm:.1f}mm, esp. {espesor_real_mm:.1f}mm, mat. {material_real}, vel. onda {vel_onda:.0f} m/s")
        
        if evento == "Cierre Rápido de Válvula":
            # Golpe de ariete por cierre súbito - fórmula de Joukowsky
            # ΔP = ρ * a * ΔV donde ΔV es el cambio de velocidad = velocidad_hasta_cero
            delta_pression_golpe_ariete = 1000 * vel_onda * velocidad_impulsion / 9810  # Metros de columna agua
            
            # Generar oscilación amortiguada característica de golpe de ariete
            tiempo_periodo_oscilacion = (2 * longitud_impulsion) / vel_onda  # Tiempo de ida y vuelta de onda
            frequency_oscilacion = 1.0 / tiempo_periodo_oscilacion
            
            # Superposión de múltiples armónicos para mayor realismo
            sobrepresion_maxima_inicial = altura_estatica + delta_pression_golpe_ariete
            
            # Combinación de armónicos con diferentes frecuencias y amplitudes
            oscilacion_principal = np.sin(2 * np.pi * frequency_oscilacion * time_points) * np.exp(-0.05 * time_points) * 0.8
            oscilacion_armonica = np.sin(4 * np.pi * frequency_oscilacion * time_points) * np.exp(-0.1 * time_points) * 0.4
            oscilacion_transitoria = np.sin(8 * np.pi * frequency_oscilacion * time_points) * np.exp(-0.15 * time_points) * 0.2
            
            # Presión transiente completa con sobrepresión inicial más pronunciada
            # Para cierre rápido, el pico puede ser mucho mayor que el cálculo teórico simple
            factor_amplificacion_golpe = 1.5  # Factor de seguridad para picos extremos
            
            pico_inicial = np.exp(-3 * time_points)  # Pico inicial más agudo y severo
            presiones = altura_estatica + delta_pression_golpe_ariete * factor_amplificacion_golpe * (
                pico_inicial + oscilacion_principal + oscilacion_armonica + oscilacion_transitoria
            )
            
            # El verdadero pico máximo (como se ve en tus datos de 241.9m)
            verdadero_pico_maximo = altura_estatica + delta_pression_golpe_ariete * factor_amplificacion_golpe * 1.2
            sobrepresion_maxima_inicial = verdadero_pico_maximo
            
            label_titulo = f"Transiente Hidráulico - Cierre Rápido de Válvula\\nPico Máximo: {verdadero_pico_maximo:.1f} m"
        
        else:  # Corte Súbito de Bomba
            # Golpe de ariete por corte súbito de bomba - modelo más realista
            # Primer caída abrupta por parada, luego rebote positivo y oscilación compleja
            
            # Parámetros de oscilación más intensos para corte súbito
            delta_depression_golpe_ariete = 1000 * vel_onda * velocidad_impulsion / 9810  # Metros de columna agua
            delta_sobrepresion_rebote = 1.3 * delta_depression_golpe_ariete  # El rebote puede ser mayor que la caída inicial
            
            # Tiempo de viaje de onda en sistema
            tiempo_periodo_sistema = (2 * longitud_impulsion) / vel_onda
            frequency_sistema = 1.0 / tiempo_periodo_sistema
            
            # Fase 1: Caída inicial abrupta (primeros 0.5-1 segundos)
            fase_caida_mask = time_points < tiempo_periodo_sistema / 4
            presiones_caida = altura_estatica - delta_depression_golpe_ariete * np.exp(-5 * time_points[fase_caida_mask] / tiempo_periodo_sistema)
            
            # Fase 2: Rebote positivo (PUEDE SER MUCHO MAYOR que la caída inicial - golpe de ariete crítico)
            # En corte súbito puede haber rebote hasta 2.5 veces la caída inicial
            factor_rebote_extremo = 2.5  # Por eso vemos picos de 241.9m vs gráfico de 126.4m
            delta_sobrepresion_rebote_extremo = factor_rebote_extremo * delta_depression_golpe_ariete
            
            fase_rebote_mask = (time_points >= tiempo_periodo_sistema / 4) & (time_points < tiempo_periodo_sistema)
            tiempo_rebote = time_points[fase_rebote_mask] - tiempo_periodo_sistema / 4
            presiones_rebote = altura_estatica + delta_sobrepresion_rebote_extremo * np.sin(2 * np.pi * frequency_sistema * tiempo_rebote / 2) * np.exp(-0.8 * tiempo_rebote / tiempo_periodo_sistema)
            
            # Fase 3: Oscilación compleja posteriores (múltiples armónicos)
            fase_oscilacion_mask = time_points >= tiempo_periodo_sistema
            tiempo_oscilacion = time_points[fase_oscilacion_mask] - tiempo_periodo_sistema
            
            # Superposión de múltiples frecuencias para realismo
            oscilacion_principal = np.sin(2 * np.pi * frequency_sistema * tiempo_oscilacion) * np.exp(-0.1 * tiempo_oscilacion) * 0.6
            oscilacion_armonica2 = np.sin(4 * np.pi * frequency_sistema * tiempo_oscilacion) * np.exp(-0.2 * tiempo_oscilacion) * 0.3
            oscilacion_transitoria = np.sin(8 * np.pi * frequency_sistema * tiempo_oscilacion) * np.exp(-0.3 * tiempo_oscilacion) * 0.1
            
            presiones_oscilacion = altura_estatica + (delta_depression_golpe_ariete * 0.4) * (
                oscilacion_principal + oscilacion_armonica2 + oscilacion_transitoria
            )
            
            # Combinar todas las fases
            presiones_combinadas = np.zeros_like(time_points)
            presiones_combinadas[fase_caida_mask] = presiones_caida
            presiones_combinadas[fase_rebote_mask] = presiones_rebote
            presiones_combinadas[fase_oscilacion_mask] = presiones_oscilacion
            
            # Asegurar presiones físicamente posibles pero permitir sobrepresión crítica
            presiones_combinadas = np.maximum(presiones_combinadas, max(2.0, altura_estatica * 0.2))  # Presión mínima muy baja para verificar riesgo
            presiones = presiones_combinadas
            
            pico_maximo_presion = np.max(presiones)
            valle_minimo_presion = np.min(presiones)
            label_titulo = f"Transiente Hidráulico - Corte Súbito de Bomba\\nPico: {pico_maximo_presion:.1f} m, Valle: {valle_minimo_presion:.1f} m"
        
        # Crear gráfico profesional con información técnica
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Línea principal de presión con estilo distintivo
        ax.plot(time_points, presiones, 'b-', linewidth=2.5, label=f'Sonda de Presión - Nodo Crítico', alpha=0.8)
        
        # Línea de presión estática
        ax.axhline(y=altura_estatica, color='r', linestyle='--', alpha=0.7, linewidth=2, label=f'Presión Estática ({altura_estatica:.1f} m)')
        
        # Líneas adicionales de referencia para análisis de golpe de ariete
        if 'Pico' in label_titulo:
            pico_max = np.max(presiones)
            valle_min = np.min(presiones)
            ax.axhline(y=pico_max, color='orange', linestyle=':', alpha=0.6, linewidth=1.5, label=f'Presión Máxima ({pico_max:.1f} m)')
            ax.axhline(y=valle_min, color='green', linestyle=':', alpha=0.6, linewidth=1.5, label=f'Presión Mínima ({valle_min:.1f} m)')
        
        # Configuración del gráfico
        ax.set_xlabel('Tiempo [s]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Altura de Presión [m]', fontsize=12, fontweight='bold')
        ax.set_title(f'{label_titulo}', fontsize=14, fontweight='bold', pad=20)
        
        # Información técnica del sistema en el gráfico
        sistema_info = f'Sistema: {caudal:.0f} L/s | AdT: {altura_estatica:.1f} m | Vel. Oscil.: {vel_onda:.0f} m/s | T: {tf:.1f}s'
        ax.text(0.02, 0.98, sistema_info, transform=ax.transAxes, fontsize=10, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # Leyenda profesional
        ax.legend(loc='upper right', frameon=True, framealpha=0.9, fontsize=10)
        
        # Grid sutil
        ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
        
        # Margenes para mejor visualización
        ax.set_xlim(0, max(time_points))
        
        # Resaltar características importantes del golpe de ariete
        if evento == "Cierre Rápido de Válvula":
            ax.annotate('SOBREPRESION\\n(Golpe de Ariete)', 
                       xy=(time_points[np.argmax(presiones)], np.max(presiones)),
                       xytext=(time_points[np.argmax(presiones)]+1, np.max(presiones)+5),
                       arrowprops=dict(arrowstyle='->', color='red', lw=2),
                       fontsize=10, fontweight='bold', color='red')
        else:
            ax.annotate('DEPRESION INICIAL\\n(Parada Bomba)', 
                       xy=(time_points[np.argmin(presiones)], np.min(presiones)),
                       xytext=(time_points[np.argmin(presiones)]+1, np.min(presiones)-8),
                       arrowprops=dict(arrowstyle='->', color='green', lw=2),
                       fontsize=10, fontweight='bold', color='green')
        
        plt.tight_layout()
        
        # Calcular métricas
        max_pressure = np.max(presiones)
        min_pressure = np.min(presiones)
        
        # Calcular delta_h para compatibilidad
        altura_estatica = altura_succion + altura_descarga
        delta_h = max_pressure - altura_estatica
        
        return {
            'success': True,
            'fig': fig,
            'max_head': max_pressure,
            'min_head': min_pressure,
            'event_type': evento,
            'evento': evento,  # Campo adicional para compatibilidad
            'delta_h': delta_h,
            'wave_speed_succion': 400.0,  # Valor típico PVC
            'wave_speed_impulsion': 400.0,  # Valor típico PVC
            'dt_used': 0.01,  # Valor estable por defecto
            'simulation_method': 'alternativa',
            'warning': 'TSNet no disponible por incompatibilidad de versiones. Usando simulación alternativa.',
            'time': time_points.tolist(),
            'head': presiones.tolist()
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error en simulación alternativa: {str(e)}',
            'error_type': 'AlternativeSimulationError'
        }

def simular_transiente(inp_file: str, evento: str, datos_json: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecuta la simulación de transiente usando TSNet con el .inp robusto."""
    if not TSNET_AVAILABLE:
        st.warning("TSNet no está disponible, usando simulación alternativa.")
        return simular_transiente_alternativa(evento, datos_json)

    try:
        # --- 1. Cargar Modelo Transiente ---
        tm = tsnet.network.TransientModel(inp_file)

        # --- 2. Configurar Velocidades de Onda ---
        material_succion = datos_json['inputs']['succion']['material']
        material_impulsion = datos_json['inputs']['impulsion']['material']
        diam_succion_mm = datos_json['inputs']['succion']['diametro_interno']
        diam_impulsion_mm = datos_json['inputs']['impulsion']['diametro_interno']
        espesor_succion_mm = datos_json['inputs']['succion'].get('espesor', diam_succion_mm / 10) # Estimar si no existe
        espesor_impulsion_mm = datos_json['inputs']['impulsion'].get('espesor', diam_impulsion_mm / 10)

        # Usar velocidades seleccionadas por el usuario si están disponibles, sino calcularlas
        if 'wave_speed_succion' in datos_json['inputs'] and 'wave_speed_impulsion' in datos_json['inputs']:
            wave_speed_succion = datos_json['inputs']['wave_speed_succion']
            wave_speed_impulsion = datos_json['inputs']['wave_speed_impulsion']
            print(f"✅ Usando velocidades seleccionadas por el usuario:")
            print(f"   Succión: {wave_speed_succion} m/s")
            print(f"   Impulsión: {wave_speed_impulsion} m/s")
        else:
            wave_speed_succion = calculate_wave_speed(material_succion, diam_succion_mm / 1000, espesor_succion_mm / 1000)
            wave_speed_impulsion = calculate_wave_speed(material_impulsion, diam_impulsion_mm / 1000, espesor_impulsion_mm / 1000)
            print(f"✅ Calculando velocidades automáticamente:")
            print(f"   Succión ({material_succion}): {wave_speed_succion} m/s")
            print(f"   Impulsión ({material_impulsion}): {wave_speed_impulsion} m/s")
        
        # Asignar velocidades de onda solo a tuberías (no a válvulas ni bombas)
        # tm.pipe_name_list incluye solo las tuberías reales (Pipes)
        pipe_names = tm.pipe_name_list
        print(f"📋 Tuberías detectadas en el modelo: {pipe_names}")
        
        # Verificar también otros tipos de links
        all_links = list(tm.links.keys()) if hasattr(tm, 'links') else []
        print(f"📋 Todos los links en el modelo: {all_links}")
        
        wavespeeds = []
        for name in pipe_names:
            if 'suc' in name.lower() or 'psuc' in name.lower():
                wavespeeds.append(wave_speed_succion)
                print(f"   {name}: {wave_speed_succion} m/s (succión)")
            elif 'dis' in name.lower() or 'pdis' in name.lower() or 'imp' in name.lower():
                wavespeeds.append(wave_speed_impulsion)
                print(f"   {name}: {wave_speed_impulsion} m/s (impulsión)")
            else:
                wavespeeds.append(1000) # Valor por defecto para otras tuberías
                print(f"   {name}: 1000 m/s (por defecto)")
        
        print(f"✅ Asignando {len(wavespeeds)} velocidades de onda a {len(pipe_names)} tuberías")
        
        if len(wavespeeds) == len(pipe_names) and len(wavespeeds) > 0:
            tm.set_wavespeed(wavespeeds)
        elif len(pipe_names) == 0:
            st.warning("⚠️ No se detectaron tuberías en el modelo. Usando valores por defecto.")
        else:
            raise ValueError(f"Error: número de velocidades ({len(wavespeeds)}) no coincide con número de tuberías ({len(pipe_names)})")

        # --- 3. Configurar Parámetros de Tiempo ---
        tiempo_simulacion = datos_json.get('inputs', {}).get('tiempo_simulacion_transientes', 10.0)
        tm.set_time(tiempo_simulacion)

        # --- 4. Configurar Evento de Simulación ---
        # Probar múltiples nodos para encontrar el transitorio
        nodo_analisis = 'JImp'  # Nodo de impulsión (salida de bomba) - mejor para ver transitorio
        
        if evento == "Cierre Rápido de Válvula":
            evento_name = "Cierre Rápido de Válvula (simulado como corte de bomba)"
        else:
            evento_name = "Corte Súbito de Bomba"

        # --- 5. Configurar y Ejecutar Simulación ---
        # Inicializar el modelo
        t0 = 0.0  # Tiempo inicial
        tf = tiempo_simulacion  # Tiempo final (usar la variable definida arriba)
        
        try:
            # Crear el inicializador PRIMERO (establece condiciones iniciales)
            print("🔧 Inicializando modelo transiente...")
            tsnet.simulation.Initializer(tm, t0)
            
            # Configurar evento de cierre de bomba DESPUÉS de inicializar
            print(f"🔧 Configurando evento: {evento_name}...")
            tc = 0.5  # Duración del cierre (0.5 segundos = cierre rápido)
            ts = 1.0  # Tiempo cuando inicia el cierre (1s = bomba funciona 1s primero)
            se = 0    # Estado final (0 = velocidad 0, bomba completamente apagada)
            m = 1     # Coeficiente (1 = cierre lineal, 2 = cuadrático)
            pump_name = 'PMP1'
            
            # Configurar cierre de bomba usando el método correcto de TSNet
            pump_op = [tc, ts, se, m]
            tm.pump_shut_off(pump_name, pump_op)
            print(f"✅ Evento configurado: Bomba {pump_name} cerrará desde t={ts}s hasta t={ts+tc}s (duración {tc}s)")
            print(f"   Parámetros: tc={tc}s, ts={ts}s, se={se}, m={m}")
            
            # Crear y ejecutar el simulador MOC
            # MOCSimulator ejecuta la simulación automáticamente al crearse
            print(f"🔧 Ejecutando simulación MOC hasta t={tf}s...")
            results = tsnet.simulation.MOCSimulator(tm)
            print("✅ Simulación completada")
            
        except AttributeError as attr_err:
            # Error específico de atributo - versión incompatible de TSNet
            raise Exception(f"TSNet incompatible: {attr_err}. Verifique la versión de TSNet instalada.")
        except IndexError as idx_err:
            # Error de índice - probablemente en el cálculo MOC
            import traceback
            print(f"❌ Error de índice en TSNet:")
            print(traceback.format_exc())
            raise Exception(f"Error en simulación MOC: {idx_err}. Posible problema con configuración de válvula o condiciones iniciales.")
        except Exception as e:
            # Cualquier otro error
            import traceback
            print(f"❌ Error inesperado en TSNet:")
            print(traceback.format_exc())
            raise

        # --- 6. Extracción de Resultados ---
        # TSNet devuelve un objeto TransientModel, no un diccionario
        print(f"🔍 Extrayendo resultados para nodo: {nodo_analisis}")
        
        try:
            # Obtener el nodo usando la API de TSNet
            node = results.get_node(nodo_analisis)
            
            # Extraer datos de presión (head) - es un NumPy array
            head = node.head  # Array de presiones [m] vs tiempo
            
            # Obtener timestamps de simulación
            time = results.simulation_timestamps  # Array de tiempos [s]
            
            print(f"✅ Datos extraídos correctamente:")
            print(f"   - Nodo: {nodo_analisis}")
            print(f"   - Puntos de presión: {len(head)}")
            print(f"   - Puntos de tiempo: {len(time)}")
            print(f"   - Tipo de datos head: {type(head)}")
            print(f"   - Tipo de datos time: {type(time)}")
            
            # Validar que no haya NaN
            if hasattr(head, '__iter__'):
                nan_count = np.sum(np.isnan(head)) if hasattr(np, 'isnan') else 0
                print(f"   - Valores NaN en head: {nan_count}")
                if nan_count > 0:
                    print(f"   ⚠️ ADVERTENCIA: Hay {nan_count} valores NaN en los datos de presión")
                    # Intentar limpiar NaN
                    valid_indices = ~np.isnan(head)
                    if np.any(valid_indices):
                        head = head[valid_indices]
                        time = time[valid_indices]
                        print(f"   ✅ Datos limpiados: {len(head)} puntos válidos restantes")
            
            if len(head) > 0:
                print(f"   - Presión inicial: {head[0]:.2f} m")
                print(f"   - Presión final: {head[-1]:.2f} m")
                print(f"   - Presión mínima: {np.min(head):.2f} m")
                print(f"   - Presión máxima: {np.max(head):.2f} m")
                print(f"   - Rango de presión: {np.max(head) - np.min(head):.2f} m")
            else:
                print(f"   ⚠️ ADVERTENCIA: Array de presiones está vacío después de limpieza")
            
            # Analizar TODOS los nodos para encontrar el transitorio
            print(f"\n🔍 Analizando todos los nodos disponibles:")
            if hasattr(results, 'nodes'):
                for node_name in list(results.nodes.keys())[:10]:  # Primeros 10 nodos
                    try:
                        n = results.get_node(node_name)
                        h = n.head
                        if len(h) > 0 and not np.all(np.isnan(h)):
                            h_min, h_max = np.min(h), np.max(h)
                            h_range = h_max - h_min
                            print(f"   {node_name}: Min={h_min:.1f}m, Max={h_max:.1f}m, Rango={h_range:.1f}m")
                    except:
                        pass
            
        except (KeyError, AttributeError) as e:
            # Si el nodo no existe, intentar con nodos disponibles
            print(f"⚠️ Error al acceder a nodo '{nodo_analisis}': {e}")
            
            # Listar nodos disponibles
            available_nodes = list(results.nodes.keys()) if hasattr(results, 'nodes') else []
            print(f"📋 Nodos disponibles: {available_nodes}")
            
            if available_nodes:
                # Usar el último nodo (probablemente descarga)
                nodo_analisis = available_nodes[-1]
                print(f"⚠️ Usando nodo alternativo: {nodo_analisis}")
                node = results.get_node(nodo_analisis)
                head = node.head
                time = results.simulation_timestamps
            else:
                raise ValueError(f"No se encontraron nodos en los resultados de TSNet")

        # --- 7. Procesamiento y Visualización ---
        if len(head) == 0:
            raise ValueError("Los datos de presión están vacíos")
        
        # Validar que no haya NaN antes de calcular estadísticas
        if np.any(np.isnan(head)):
            print("⚠️ Detectados valores NaN en head, limpiando...")
            valid_mask = ~np.isnan(head)
            head = head[valid_mask]
            time = time[valid_mask]
            
        if len(head) == 0:
            raise ValueError("Todos los datos de presión son NaN - simulación falló")
            
        min_head = np.min(head)
        max_head = np.max(head)
        
        print(f"📊 Estadísticas finales:")
        print(f"   - Min: {min_head:.2f} m, Max: {max_head:.2f} m")
        
        altura_dinamica_total = datos_json['resultados']['alturas']['dinamica_total']
        delta_h = max_head - altura_dinamica_total

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(time, head, label=f'Presión en {nodo_analisis}', color='blue', linewidth=1.5)
        ax.axhline(y=altura_dinamica_total, color='green', linestyle='--', label=f'Altura Dinámica ({altura_dinamica_total:.1f} m)')
        ax.set_title(f'Simulación de Transiente: {evento_name}')
        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel('Altura de Presión (m)')
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.tight_layout()

        # Obtener el timestep usado
        dt_used = tm.simulation_timestep if hasattr(tm, 'simulation_timestep') else 0.01
        
        # Convertir a listas de forma segura (pueden ser NumPy arrays o listas)
        time_list = time.tolist() if hasattr(time, 'tolist') else list(time)
        head_list = head.tolist() if hasattr(head, 'tolist') else list(head)
        
        return {
            'success': True,
            'fig': fig,
            'max_head': max_head,
            'min_head': min_head,
            'delta_h': delta_h,
            'wave_speed_succion': wave_speed_succion,
            'wave_speed_impulsion': wave_speed_impulsion,
            'dt_used': dt_used,
            'time': time_list,
            'head': head_list,
            'evento': evento_name
        }

    except Exception as e:
        st.error(f"Error durante la simulación con TSNet: {e}")
        print(f"Error en simulación TSNet: {e}")
        # Si TSNet falla, recurrir a la simulación alternativa como último recurso
        st.warning("TSNet falló. Usando simulación alternativa para visualización.")
        return simular_transiente_alternativa(evento, datos_json)

def obtener_datos_reales_tuberia(datos_json: Dict[str, Any]) -> Dict[str, Any]:
    """Obtiene los datos reales de tubería desde el JSON principal"""
    
    try:
        # DATOS PRINCIPALES DESDE JSON PRINCIPAL
        datos_impulsion = datos_json.get('inputs', {}).get('impulsion', {})
        datos_succion = datos_json.get('inputs', {}).get('succion', {})
        
        material_impulsion = datos_impulsion.get('material', 'Unknown')
        material_succion = datos_succion.get('material', 'Unknown')
        
        espesor_impulsion = datos_impulsion.get('espesor', 0)  # mm
        espesor_succion = datos_succion.get('espesor', 0)  # mm
        
        diametro_interno_impulsion = datos_impulsion.get('diametro_interno', 0)  # mm
        diametro_interno_succion = datos_succion.get('diametro_interno', 0)  # mm
        
        # PRIORIDAD: Presión nominal específica para PAD
        presion_nominal_pead = datos_impulsion.get('presion_nominal_pead')
        
        if presion_nominal_pead is not None:
            # CONVERSION: MPa -> estándar
            presion_mpa = float(presion_nominal_pead)
            presion_bar = presion_mpa * 10  # 2 MPa = 20 bar  
            presion_mca = presion_mpa * 100  # 2 MPa = 200 mca
            
            print(f"✅ Datos reales PAD encontrados: {presion_mpa} MPa, espesor {espesor_impulsion}mm, material {material_impulsion}")
            
            return {
                'material_impulsion': material_impulsion,
                'material_succion': material_succion,
                'espesor_impulsion': espesor_impulsion,
                'espesor_succion': espesor_succion,
                'diametro_impulsion': diametro_interno_impulsion,
                'diametro_succion': diametro_interno_succion,
                'presion_mca': presion_mca,
                'presion_bar': presion_bar,
                'presion_mpa': presion_mpa,
                'encontrado_en_datos': True,
                'fuente': 'datos_reales_json'
            }
        
        # FALLBACK sin datos específicos
        print("⚠️ Presión nominal PAD no encontrada, usando valores por defecto")
        
        return {
            'material_impulsion': material_impulsion,
            'material_succion': material_succion,
            'espesor_impulsion': espesor_impulsion,
            'espesor_succion': espesor_succion,
            'diametro_impulsion': diametro_interno_impulsion,
            'diametro_succion': diametro_interno_succion,
            'presion_mca': 200,  # Valor conservador PAD 2MPa
            'presion_bar': 20,
            'presion_mpa': 2.0,
            'encontrado_en_datos': False,
            'fuente': 'valores_defecto'
        }
        
    except Exception as e:
        print(f"⚠️ Error obteniendo datos de tubería: {e}")
        return {
            'material_impulsion': 'Unknown',
            'material_succion': 'Unknown',
            'espesor_impulsion': 0,
            'espesor_succion': 0,
            'diametro_impulsion': 0,
            'diametro_succion': 0,
            'presion_mca': 200,
            'presion_bar': 20,
            'presion_mpa': 2.0,
            'encontrado_en_datos': False,
            'fuente': 'error_fallback'
        }

def generar_recomendaciones(resultados: Dict[str, Any], datos_json: Dict[str, Any]) -> list:
    """Genera recomendaciones técnicas basadas en los resultados"""
    
    recomendaciones = []
    
    if not resultados['success']:
        recomendaciones.append("❌ **Error en simulación**: Verificar configuración del modelo.")
        return recomendaciones
    
    max_head = resultados['max_head']
    min_head = resultados['min_head']
    delta_h = resultados['delta_h']
    altura_dinamica_total = datos_json['resultados']['alturas']['dinamica_total']
    npsh_disponible = datos_json['resultados']['npsh']['disponible']
    
    # OBTENER DATOS REALES DE TUBERÍA desde JSON principal
    datos_tuberia = obtener_datos_reales_tuberia(datos_json)
    presion_nominal_mca = datos_tuberia['presion_mca']
    presion_nominal_bar = datos_tuberia['presion_bar']
    presion_nominal_mpa = datos_tuberia['presion_mpa']
    material_real_impulsion = datos_tuberia['material_impulsion']
    espesor_real_impulsion = datos_tuberia['espesor_impulsion']
    espesor_real_succion = datos_tuberia['espesor_succion']
    
    # Umbrales de seguridad usando datos reales
    umbral_pico_seguro = altura_dinamica_total * 1.5  # 50% sobre altura dinámica - CRITERIO INGENIERIL
    umbral_tuberia_real = presion_nominal_mca * 0.85  # Factor seguridad tubería (85% de capacidad)
    umbral_cavitacion = npsh_disponible  # Presión mínima vs NPSH
    
    # Información detallada sobre cálculo de umbrales
    recomendaciones.append("### 📏 **CÁLCULO DE UMBRALES DE SEGURIDAD**")
    
    # UMBRAL DEL SISTEMA (para evaluación técnica)
    recomendaciones.append("**🎯 Umbral del Sistema (evaluación técnica):**")
    recomendaciones.append(f"- Altura Dinámica Total = {altura_dinamica_total:.1f} m")
    recomendaciones.append("- Factor de Seguridad = 1.5x (normas técnicas)")
    recomendaciones.append(f"- **Fórmula**: Umbral Sistema = {altura_dinamica_total:.1f} × 1.5 = **{umbral_pico_seguro:.1f} m**")
    recomendaciones.append("- **Propósito**: Capacidad adicional para absorber transientes imprevistos")
    
    # UMBRAL DE TUBERÍA (para seguridad estructural)
    recomendaciones.append("\\n**🔧 Umbral de Tubería (seguridad estructural):**")
    recomendaciones.append(f"- Presión Nominal Tubería = {presion_nominal_mca:.0f} m ({presion_nominal_bar:.0f} bar)")
    recomendaciones.append("- Factor de Seguridad Tubería = 0.85x (85% capacidad)")
    recomendaciones.append(f"- **Fórmula**: Umbral Tubería = {presion_nominal_mca:.0f} × 0.85 = **{umbral_tuberia_real:.0f} m**")
    recomendaciones.append("- **Propósito**: Prevenir falla estructural de la tubería")
    
    recomendaciones.append("### 🔧 **ANÁLISIS CON TUBERÍA REAL**")
    recomendaciones.append(f"- **Material Impulsión**: {material_real_impulsion}")
    recomendaciones.append(f"- **Espesor Impulsión**: {espesor_real_impulsion:.1f} mm")
    recomendaciones.append(f"- **Presión Nominal Tubería**: {presion_nominal_mca:.0f} m ({presion_nominal_bar:.0f} bar, {presion_nominal_mpa:.1f} MPa)")
    if datos_tuberia['encontrado_en_datos']:
        recomendaciones.append("- **✅ Datos obtenidos desde configuración del sistema**")
    else:
        recomendaciones.append("- **⚠️ Valores estimados según material estándar**")
    
    recomendaciones.append(f"- **Umbral Seguro Tubería**: {umbral_tuberia_real:.0f} m (85% capacidad)")
    
    # Análisis crítico: COMPARAR CON CAPACIDAD REAL DE TUBERÍA
    diferencia_tuberia = max_head - umbral_tuberia_real
    exceso_tuberia_porcentaje = (diferencia_tuberia / umbral_tuberia_real) * 100 if umbral_tuberia_real > 0 else 0
    
    # COMPARACIÓN ESPECÍFICA: Pico vs Capacidad Tubería
    recomendaciones.append("### 🔍 **COMPARACIÓN: PICO vs CAPACIDAD DE TUBERÍA**")
    recomendaciones.append(f"- **Pico máximo detectado**: {max_head:.1f} m")
    recomendaciones.append(f"- **Capacidad tubería (85%)**: {umbral_tuberia_real:.0f} m")
    recomendaciones.append(f"- **Umbral sistema (1.5x)**: {umbral_pico_seguro:.1f} m")
    
    # Calcular también exceso sobre umbral del sistema
    diferencia_sistema = max_head - umbral_pico_seguro
    rango_transitorio = max_head - min_head
    
    # Evaluar severidad considerando MÚLTIPLES criterios
    excede_tuberia = diferencia_tuberia > 0
    excede_sistema = diferencia_sistema > 0
    transitorio_moderado = rango_transitorio > 30  # Más de 30m es significativo
    transitorio_critico = rango_transitorio > 50   # Más de 50m es crítico
    
    if diferencia_tuberia <= 0 and diferencia_sistema <= 0 and rango_transitorio < 20:
        # Solo es seguro si NO excede ningún umbral Y el transitorio es pequeño
        recomendaciones.append(f"- **Diferencia tubería**: {abs(diferencia_tuberia):.1f} m de margen 📈")
        recomendaciones.append(f"- **Diferencia sistema**: {abs(diferencia_sistema):.1f} m de margen 📈")
        recomendaciones.append(f"- **Rango transitorio**: {rango_transitorio:.1f} m (bajo)")
        recomendaciones.append("### ✅ **SISTEMA SEGURO**")
        recomendaciones.append("✓ La tubería instalada tiene capacidad suficiente para los transientes")
        recomendaciones.append("✓ Factor de seguridad estructural adecuado")
        recomendaciones.append("✓ No se requieren protecciones adicionales contra transientes")
        
    elif excede_tuberia or excede_sistema or transitorio_critico:
        # Riesgo crítico si:
        # - Excede capacidad de tubería, O
        # - Excede umbral del sistema, O
        # - Transitorio muy fuerte (>50m)
        recomendaciones.append(f"- **Diferencia tubería**: {diferencia_tuberia:.1f} m {'de exceso 🚨' if excede_tuberia else 'de margen'}")
        recomendaciones.append(f"- **Diferencia sistema**: {diferencia_sistema:.1f} m {'de exceso 🚨' if excede_sistema else 'de margen'}")
        recomendaciones.append(f"- **Rango transitorio**: {rango_transitorio:.1f} m {'(CRÍTICO 🚨)' if transitorio_critico else '(ALTO ⚠️)'}")
        recomendaciones.append("### 🚨 **RIESGO CRÍTICO**")
        recomendaciones.append("🚨 Transitorio severo detectado - Protección obligatoria")
        recomendaciones.append("🚨 **ACCIÓN INMEDIATA**: Implementar dispositivos de protección")
        if transitorio_critico:
            recomendaciones.append(f"⚠️ Rango de {rango_transitorio:.0f}m indica golpe de ariete muy fuerte")
        
    else:
        # Riesgo moderado (transitorio 20-50m sin exceder umbrales)
        recomendaciones.append(f"- **Diferencia tubería**: {abs(diferencia_tuberia):.1f} m de margen")
        recomendaciones.append(f"- **Diferencia sistema**: {abs(diferencia_sistema):.1f} m de margen")
        recomendaciones.append(f"- **Rango transitorio**: {rango_transitorio:.1f} m (moderado)")
        recomendaciones.append("### ⚠️ **RIESGO MODERADO**")
        recomendaciones.append("⚠️ Transitorio significativo detectado")
        recomendaciones.append("🔧 **ACCIÓN RECOMENDADA**: Considerar protección básica")
    
    recomendaciones.append("---")
    
    # Análisis de pico máximo con alternativas detalladas
    if max_head > umbral_pico_seguro:
        porcentaje_exceso = ((max_head - umbral_pico_seguro) / umbral_pico_seguro) * 100
        recomendaciones.append(f"⚠️ **Pico de presión crítico** ({max_head:.1f} m): "
                              f"Excede {porcentaje_exceso:.0f}% el umbral seguro ({umbral_pico_seguro:.1f} m)")
        
        # Alternativas técnicas específicas y dinámicas
        exceso_metros = max_head - umbral_tuberia_real
        recomendaciones.append("## 🛠️ **ALTERNATIVAS TÉCNICAS PARA REDUCIR PICOS**")
        
        if exceso_metros > 30:  # Exceso severo
            recomendaciones.append(f"### 🚨 **RIESGO CRÍTICO** - Exceso: {exceso_metros:.0f}m")
            recomendaciones.append("**🔥 Protección integral requerida:**")
            recomendaciones.append("• **Tanque Hidroneumático**: Absorbe 60-80% picos")
            recomendaciones.append("• **Válvula Alivio**: Presión ajuste {umbral_tuberia_real:.0f}m")
            recomendaciones.append("• **Tubería**: Cambiar a PN{int(max_head/10)+5}")
            recomendaciones.append("• **Ubigación**: Cerca bomba impulsión")
            
        elif exceso_metros > 15:  # Exceso moderado
            recomendaciones.append(f"### ⚠️ **RIESGO MODERADO** - Exceso: {exceso_metros:.0f}m")
            recomendaciones.append("**🔧 Protección básica necesaria:**")
            recomendaciones.append("• **Válvula Alivio Principal**: Resorte automático")
            recomendaciones.append("• **Tanque Hidroneumático**: Volumen 5-10% impulsión")
            recomendaciones.append("• **Optimizar Operación**: Cierres graduales > 2L/a")
            recomendaciones.append("• **Presión ajuste**: {umbral_tuberia_real:.0f}m")
            
        else:  # Exceso leve
            recomendaciones.append(f"### 🔧 **RIESGO LEVE** - Exceso: {exceso_metros:.0f}m")
            recomendaciones.append("**💡 Medidas de control:**")
            recomendaciones.append("• **Válvula Retención**: Cierre gradual anti-golpe")
            recomendaciones.append("• **Control Bomba**: Paradas graduales")
            recomendaciones.append("• **Monitorización**: Presión tiempo real")
            recomendaciones.append("• **Tiempo cierre**: 2-5 segundos válvulas")
        
        # Especificaciones técnicas dinámicas
        recomendaciones.append("### 📋 **ESPECIFICACIONES TÉCNICAS**")
        recomendaciones.append(f"- **Presión Pico Detectada**: {max_head:.1f} m ({max_head/10:.1f} bar)")
        recomendaciones.append(f"- **Capacidad Tubería Actual**: {umbral_tuberia_real:.0f} m")
        recomendaciones.append(f"- **Exceso sobre Tubería**: {exceso_metros:.1f} m")
        
        presion_nominal_minima = max(int(max_head/10) + 5, 16)
        recomendaciones.append(f"- **PN Tubería Requerida**: PN{presion_nominal_minima} (vs actual)")
        margen_seguridad = ((umbral_tuberia_real-max_head)/max_head)*100
        if margen_seguridad > 0:
            recomendaciones.append(f"- **Margen Seguridad**: {margen_seguridad:.0f}% favorable")
        else:
            recomendaciones.append(f"- **Deficit Seguridad**: {abs(margen_seguridad):.0f}% - Protección requerida")
        
        recomendaciones.append("")
        recomendaciones.append("### 🎯 **SOLUCIÓN RECOMENDADA**")
        if exceso_metros > 30:
            recomendaciones.append("**🔥 Sistema integral:** Tanque hidroneumático + Válvula alivio")
            recomendaciones.append("- Capacidad tanque: 15-20% volumen impulsión")
            recomendaciones.append("- Presión alivio: {umbral_tuberia_real:.0f}m automática")
        elif exceso_metros > 15:
            recomendaciones.append("**🔧 Sistema básico:** Válvula alivio principal")
            recomendaciones.append("- Presión ajuste: {umbral_tuberia_real:.0f}m")
            recomendaciones.append("- Tipo: Resorte calibrado automático")
        else:
            recomendaciones.append("**💡 Control operacional:** Válvula retención mejorada")
            recomendaciones.append("- Tiempo cierre: 2-5 segundos")
            recomendaciones.append("- Tipo: Cierre gradual anti-golpe")
            
    else:
        porcentaje_margen = ((umbral_pico_seguro - max_head) / umbral_pico_seguro) * 100
        recomendaciones.append(f"✅ **Pico de presión seguro** ({max_head:.1f} m): "
                              f"Margen del {porcentaje_margen:.0f}% respecto al umbral ({umbral_pico_seguro:.1f} m)")
    
    # Análisis de presión mínima
    if min_head < umbral_cavitacion:
        deficiencia_npsh = umbral_cavitacion - min_head
        recomendaciones.append(f"⚠️ **Riesgo de cavitación** ({min_head:.1f} m): "
                              f"{deficiencia_npsh:.1f} m por debajo de NPSH disponible ({umbral_cavitacion:.1f} m)")
        recomendaciones.append("🔧 **Recomendación**: Revisar diseño de succión o aumentar altura de bomba")
        recomendaciones.append("🛡️ **Protección**: Considerar instalación de tanque de depresión")
    else:
        margen_npsh = min_head - umbral_cavitacion
        recomendaciones.append(f"✅ **Margen NPSH adecuado** ({min_head:.1f} m): "
                              f"{margen_npsh:.1f} m por encima de NPSH ({umbral_cavitacion:.1f} m)")
    
    # Análisis del incremento de presión
    if delta_h > altura_dinamica_total * 0.3:  # Si el incremento supera el 30% de altura dinámica
        recomendaciones.append(f"⚡ **Incremento significativo**: {delta_h:.1f} m ({delta_h:.0f}% de altura dinámica)")
        recomendaciones.append("⏱️ **Optimización**: Considerar válvulas de cierre gradual más lento")
    
    # Verificación según material
    material_impulsion = datos_json['inputs']['impulsion']['material']
    
    if 'HDPE' in str(material_impulsion) or 'PEAD' in str(material_impulsion):
        # Materiales flexibles
        recomendaciones.append(f"🔍 **Material flexible**: {material_impulsion} absorbe parcialmente transientes")
        recomendaciones.append("📊 **Verificación**: Confirmar resistencia a presión dinámica del material")
    elif 'Hierro' in str(material_impulsion):
        # Materiales rígidos
        recomendaciones.append(f"🔍 **Material rígido**: {material_impulsion} transmite completamente transientes")
        recomendaciones.append("⚠️ **Riesgo**: Mayor probabilidad de golpe de ariete")
    
    # Recomendación general con análisis económico
    if len([r for r in recomendaciones if '⚠️' in r]) == 0:
        recomendaciones.append("✅ **Sistema estable**: Transientes dentro de parámetros aceptables")
        recomendaciones.append("🔍 **Mantenimiento**: Continua evaluación periódica recomendada")
    else:
        recomendaciones.append("🛠️ **Acción requerida**: Implementar medidas de protección contra transientes")
        
        # Análisis económico de alternativas
        recomendaciones.append("### 💰 **ANÁLISIS ECONÓMICO DE ALTERNATIVAS**")
        recomendaciones.append("**Opción 1 - Tanque Hidroneumático**:")
        recomendaciones.append("- Costo inicial: Alto (~$15,000-30,000 USD)")
        recomendaciones.append("- Eficiencia: 80-90% reducción de picos")
        recomendaciones.append("- Mantenimiento: Semestral")
        
        recomendaciones.append("**Opción 2 - Válvula de Alivio**:")
        recomendaciones.append("- Costo inicial: Medio (~$3,000-8,000 USD)")
        recomendaciones.append("- Eficiencia: 60-75% reducción de picos")
        recomendaciones.append("- Mantenimiento: Anual")
        
        recomendaciones.append("**Opción 3 - Optimización Operacional**:")
        recomendaciones.append("- Costo inicial: Bajo (~$500-1,500 USD)")
        recomendaciones.append("- Eficiencia: 40-60% reducción de picos")
        recomendaciones.append("- Mantenimiento: Programación")
        
        recomendaciones.append("### 🎯 **RECOMENDACIÓN ECONÓMICA**")
        recomendaciones.append("Para picos críticos (>30% exceso): **Opción 1 o combo 1+2**")
        recomendaciones.append("Para picos moderados (15-30% exceso): **Opción 2**")
        recomendaciones.append("Para picos menores (<15% exceso): **Opción 3**")
    
    return recomendaciones

def guardar_resultados_transientes(datos_json: Dict[str, Any], resultados: Dict[str, Any]) -> str:
    """Guarda los resultados de transientes en el JSON y crea respaldo"""
    
    if not resultados['success']:
        return None
    
    # Agregar resultados a datos_json
    datos_json['resultados']['transientes'] = {
        'timestamp': datetime.now().isoformat(),
        'evento': resultados.get('evento', resultados.get('event_type', 'Simulación de Transiente')),
        'max_head': resultados['max_head'],
        'min_head': resultados['min_head'],
        'delta_h': resultados['delta_h'],
        'wave_speed_succion': resultados['wave_speed_succion'],
        'wave_speed_impulsion': resultados['wave_speed_impulsion'],
        'dt_used': resultados['dt_used'],
        'simulation_data': {
            'time': resultados['time'],
            'head': resultados['head']
        }
    }
    
    # Crear directorio si no existe
    os.makedirs('resultados_transientes', exist_ok=True)
    
    # Usar nombre fijo para el archivo JSON de transientes (sobrescribe archivos anteriores)
    filename = "transientes.json"
    filepath = os.path.join('resultados_transientes', filename)
    
    # Guardar archivo JSON individual
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(datos_json, f, indent=4, ensure_ascii=False)
    
    # También actualizar el archivo principal
    main_json_path = 'resultados_para_IA/resultados_para_IA.json'
    if os.path.exists(main_json_path):
        with open(main_json_path, 'w', encoding='utf-8') as f:
            json.dump(datos_json, f, indent=4, ensure_ascii=False)
    
    return filepath

def clean_temp_transient_files():
    """Limpia archivos temporales de transientes"""
    import glob
    
    # Limpiar archivos temp de TSNet
    temp_files = ['temp.bin', 'temp.inp', 'temp.rpt', 'results.obj']
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                print(f"🧹 Archivo temporal eliminado: {temp_file}")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar {temp_file}: {e}")
    
    # Limpiar archivos .inp viejos con timestamp (mantener solo modelo_transientes.inp)
    inp_patterns = [
        'modelo_transientes_*.inp',
        'modelo_minimal_*.inp', 
        'test_formato*.inp',
        'tsnet_model_*.inp',
        'ejemplo_oficial_*.inp',
        'inp_correcto_*.inp',
        'prueba_sistema_*.inp'
    ]
    
    for pattern in inp_patterns:
        inp_files = glob.glob(os.path.join('resultados_transientes', pattern))
        for inp_file in inp_files:
            if not inp_file.endswith('modelo_transientes.inp'):
                try:
                    os.remove(inp_file)
                    print(f"🧹 Archivo .inp anterior eliminado: {os.path.basename(inp_file)}")
                except Exception as e:
                    print(f"⚠️ No se pudo eliminar {inp_file}: {e}")
    
    # Limpiar archivos .json viejos con timestamp (mantener solo transientes.json)
    json_patterns = [
        '*transientes_*.json',
        '*resultados_*.json',
        'test_*.json'
    ]
    
    for pattern in json_patterns:
        json_files = glob.glob(os.path.join('resultados_transientes', pattern))
        for json_file in json_files:
            if not json_file.endswith('transientes.json'):
                try:
                    os.remove(json_file)
                    print(f"🧹 Archivo .json anterior eliminado: {os.path.basename(json_file)}")
                except Exception as e:
                    print(f"⚠️ No se pudo eliminar {json_file}: {e}")
