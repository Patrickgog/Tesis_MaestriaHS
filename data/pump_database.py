"""
Módulo para gestión de base de datos de bombas comerciales

Este módulo proporciona funciones para cargar, filtrar y convertir datos
de catálogos de bombas comerciales (Grundfos, Ebara) al formato compatible
con la aplicación de diseño de sistemas de bombeo.

Autor: Sistema de Bombeo - Módulo de Catálogo
Fecha: 2025-12-23
"""

import json
import os
from typing import Dict, List, Optional, Tuple


def load_pump_database(marca: str) -> Dict:
    """
    Carga la base de datos de bombas de una marca específica
    
    Args:
        marca (str): Nombre de la marca ("Grundfos" o "Ebara")
    
    Returns:
        dict: Base de datos completa con estructura de categorías y bombas
    
    Raises:
        FileNotFoundError: Si el archivo JSON no existe
        ValueError: Si la marca no es válida
    """
    marcas_validas = ["Grundfos", "Ebara"]
    
    if marca not in marcas_validas:
        raise ValueError(f"Marca '{marca}' no válida. Debe ser una de: {marcas_validas}")
    
    archivo = f"data_tablas/bombas_{marca.lower()}_data.json"
    
    if not os.path.exists(archivo):
        raise FileNotFoundError(f"No se encontró el archivo de catálogo: {archivo}")
    
    with open(archivo, "r", encoding="utf-8") as f:
        database = json.load(f)
    
    return database


def filter_pumps_by_requirements(
    database: Dict, 
    caudal_lps: float, 
    altura_m: float,
    margen_porcentaje: float = 20
) -> List[Dict]:
    """
    Filtra bombas que cumplen con los requerimientos de diseño
    
    Args:
        database (dict): Base de datos cargada de bombas
        caudal_lps (float): Caudal de diseño en L/s
        altura_m (float): Altura de diseño en metros
        margen_porcentaje (float): Margen de tolerancia (default 20%)
    
    Returns:
        list: Lista de bombas que cumplen los requisitos, ordenadas por
              proximidad al punto de operación óptimo
    """
    bombas_compatibles = []
    
    # Calcular rangos con margen (Tolerancia del usuario)
    margen_factor = 1 + (margen_porcentaje / 100)
    q_min_req = caudal_lps / margen_factor
    q_max_req = caudal_lps * margen_factor
    h_min_req = altura_m / margen_factor
    h_max_req = altura_m * margen_factor
    
    # Recorrer todas las categorías y bombas
    for categoria in database.get('categorias', []):
        for bomba in categoria.get('bombas', []):
            # Obtener rangos óptimos del catálogo
            q_opt_min, q_opt_max = bomba['rango_caudal_optimo_lps']
            
            if isinstance(bomba['rango_altura_optima_m'], list):
                h_opt_min, h_opt_max = bomba['rango_altura_optima_m']
            else:
                h_opt_central = bomba['rango_altura_optima_m']
                h_opt_min = h_opt_central * 0.80 # 20% de margen inferior
                h_opt_max = h_opt_central * 1.25 # 25% de margen superior
            
            # LÓGICA DE FILTRADO FLEXIBLE:
            # Una bomba es compatible si hay solapamiento entre el rango de requerimiento
            # (con el margen del usuario) y una zona extendida del rango óptimo del catálogo (15% extra).
            
            extension = 0.15 # 15% de extensión sobre el rango de catálogo para visibilidad
            q_cat_min, q_cat_max = q_opt_min * (1 - extension), q_opt_max * (1 + extension)
            h_cat_min, h_cat_max = h_opt_min * (1 - extension), h_opt_max * (1 + extension)
            
            cumple_caudal = (q_min_req <= q_cat_max) and (q_max_req >= q_cat_min)
            cumple_altura = (h_min_req <= h_cat_max) and (h_max_req >= h_cat_min)
            
            if cumple_caudal and cumple_altura:
                # Calcular "score" de proximidad al punto de diseño real
                # El score ahora se basa en la distancia relativa al punto de diseño del usuario
                # en lugar del centro del rango del catálogo, para priorizar el ajuste real.
                
                dist_q = abs(caudal_lps - (q_opt_min + q_opt_max)/2) / ((q_opt_min + q_opt_max)/2)
                dist_h = abs(altura_m - (h_opt_min + h_opt_max)/2) / ((h_opt_min + h_opt_max)/2)
                
                # Penalizar ligeramente si el punto está fuera del rango óptimo estricto
                penalizacion = 0
                if not (q_opt_min <= caudal_lps <= q_opt_max):
                    penalizacion += 0.1
                if not (h_opt_min <= altura_m <= h_opt_max):
                    penalizacion += 0.1
                
                score = dist_q + dist_h + penalizacion
                
                bomba_info = bomba.copy()
                bomba_info['_score'] = score
                bomba_info['_categoria'] = categoria['categoria']
                bomba_info['_tipo'] = categoria['tipo']
                bombas_compatibles.append(bomba_info)
    
    # Ordenar por score (mejores primero: menor score)
    bombas_compatibles.sort(key=lambda x: x['_score'])
    
    return bombas_compatibles


def get_pump_curves(bomba: Dict, flow_unit: str = 'L/s') -> Dict:
    """
    Obtiene las curvas características de una bomba en el formato
    compatible con el ajuste de curvas existente
    
    Args:
        bomba (dict): Diccionario con datos de la bomba
        flow_unit (str): Unidad de caudal ('L/s' o 'm³/h')
    
    Returns:
        dict: Diccionario con las curvas convertidas
              Keys: 'bomba', 'rendimiento', 'potencia', 'npsh'
              Values: listas de tuplas (caudal, valor)
    """
    curvas_originales = bomba.get('curvas', {})
    curvas_convertidas = {}
    
    # Factor de conversión de caudal
    factor_q = 3.6 if flow_unit == 'm³/h' else 1.0
    
    # Curva H-Q
    if 'h_q' in curvas_originales:
        caudales = [q * factor_q for q in curvas_originales['h_q']['caudales_lps']]
        alturas = curvas_originales['h_q']['alturas_m']
        curvas_convertidas['bomba'] = list(zip(caudales, alturas))
    
    # Curva η-Q
    if 'eta_q' in curvas_originales:
        caudales = [q * factor_q for q in curvas_originales['eta_q']['caudales_lps']]
        eficiencias = curvas_originales['eta_q']['eficiencias_porcentaje']
        curvas_convertidas['rendimiento'] = list(zip(caudales, eficiencias))
    
    # Curva P-Q
    if 'pbhp_q' in curvas_originales:
        caudales = [q * factor_q for q in curvas_originales['pbhp_q']['caudales_lps']]
        potencias = curvas_originales['pbhp_q']['potencias_kw']
        curvas_convertidas['potencia'] = list(zip(caudales, potencias))
    
    # Curva NPSH-Q
    if 'npshr_q' in curvas_originales:
        caudales = [q * factor_q for q in curvas_originales['npshr_q']['caudales_lps']]
        npsh = curvas_originales['npshr_q']['npsh_requerido_m']
        curvas_convertidas['npsh'] = list(zip(caudales, npsh))
    
    return curvas_convertidas


def convert_pump_to_textarea_format(bomba: Dict, flow_unit: str = 'L/s') -> Dict[str, str]:
    """
    Convierte las curvas de una bomba al formato de texto
    que se usa en los textarea del ajuste de curvas
    
    Args:
        bomba (dict): Diccionario con datos de la bomba
        flow_unit (str): Unidad de caudal ('L/s' o 'm³/h')
    
    Returns:
        dict: Diccionario con keys: 'bomba', 'rendimiento', 'potencia', 'npsh'
              cada uno con string en formato "x y\\nx y\\nx y"
    """
    curvas = get_pump_curves(bomba, flow_unit)
    curvas_texto = {}
    
    for curva_key, puntos in curvas.items():
        lineas = []
        for x, y in puntos:
            lineas.append(f"{x:.2f} {y:.2f}")
        curvas_texto[curva_key] = "\n".join(lineas)
    
    return curvas_texto


def get_pump_summary_info(bomba: Dict) -> str:
    """
    Genera un resumen textual de las especificaciones de una bomba
    
    Args:
        bomba (dict): Diccionario con datos de la bomba
    
    Returns:
        str: Texto con resumen de especificaciones
    """
    info_lines = []
    
    info_lines.append(f"**{bomba['modelo']}** - Serie {bomba['serie']}")
    info_lines.append(f"Código: {bomba['codigo']}")
    info_lines.append(f"Tipo: {bomba['tipo_bomba']}")
    info_lines.append(f"Potencia: {bomba['potencia_hp']} HP ({bomba['potencia_kw']} kW)")
    info_lines.append(f"RPM: {bomba['rpm']} | Etapas: {bomba['etapas']}")
    info_lines.append(f"Peso: {bomba['peso_kg']} kg")
    info_lines.append(f"Material: {bomba['material_impulsor']}")
    info_lines.append(f"Temp. máx: {bomba['temperatura_max_c']}°C | Presión máx: {bomba['presion_max_bar']} bar")
    
    q_opt_min, q_opt_max = bomba['rango_caudal_optimo_lps']
    
    if isinstance(bomba['rango_altura_optima_m'], list):
        h_opt_min, h_opt_max = bomba['rango_altura_optima_m']
        info_lines.append(f"Rangos óptimos: Q = {q_opt_min}-{q_opt_max} L/s | H = {h_opt_min}-{h_opt_max} m")
    else:
        h_opt = bomba['rango_altura_optima_m']
        info_lines.append(f"Rangos óptimos: Q = {q_opt_min}-{q_opt_max} L/s | H ≈ {h_opt} m")
    
    info_lines.append(f"Costo estimado: ${bomba['costo_estimado_usd']:,.0f} USD")
    
    return "\n".join(info_lines)


# Funciones auxiliares para validación

def validate_pump_data(bomba: Dict) -> Tuple[bool, List[str]]:
    """
    Valida que una bomba tenga todos los campos requeridos y curvas completas
    
    Args:
        bomba (dict): Datos de la bomba a validar
    
    Returns:
        tuple: (es_valida, lista_de_errores)
    """
    errores = []
    
    # Campos requeridos
    campos_requeridos = [
        'codigo', 'modelo', 'serie', 'tipo_bomba', 'potencia_hp', 'potencia_kw',
        'rpm', 'etapas', 'peso_kg', 'costo_estimado_usd', 'material_impulsor',
        'temperatura_max_c', 'presion_max_bar', 'rango_caudal_optimo_lps',
        'rango_altura_optima_m', 'url_ficha_tecnica', 'curvas'
    ]
    
    for campo in campos_requeridos:
        if campo not in bomba:
            errores.append(f"Falta el campo requerido: {campo}")
    
    # Validar curvas
    if 'curvas' in bomba:
        curvas_requeridas = ['h_q', 'eta_q', 'pbhp_q', 'npshr_q']
        for curva_key in curvas_requeridas:
            if curva_key not in bomba['curvas']:
                errores.append(f"Falta la curva: {curva_key}")
            else:
                curva = bomba['curvas'][curva_key]
                if 'caudales_lps' not in curva:
                    errores.append(f"Curva {curva_key} no tiene 'caudales_lps'")
                elif 'alturas_m' in curva_key or 'eficiencias' in curva_key or 'potencias' in curva_key or 'npsh' in curva_key:
                    # Verificar que tenga valores
                    valor_key = list(set(curva.keys()) - {'descripcion', 'caudales_lps'})
                    if not valor_key:
                        errores.append(f"Curva {curva_key} no tiene valores")
    
    es_valida = len(errores) == 0
    return es_valida, errores


if __name__ == "__main__":
    # Pruebas básicas del módulo
    print("=== Pruebas del modulo pump_database ===\n")
    
    # Test 1: Cargar base de datos
    print("Test 1: Cargar base de datos de Grundfos")
    try:
        db_grundfos = load_pump_database("Grundfos")
        print(f"[OK] Cargado: {db_grundfos['marca']}")
        print(f"  Categorias: {len(db_grundfos['categorias'])}")
        total_bombas = sum(len(cat['bombas']) for cat in db_grundfos['categorias'])
        print(f"  Total de bombas: {total_bombas}\n")
    except Exception as e:
        print(f"[ERROR] {e}\n")
    
    # Test 2: Filtrar bombas
    print("Test 2: Filtrar bombas para Q=20 L/s, H=80 m, margen=20%")
    try:
        bombas_encontradas = filter_pumps_by_requirements(db_grundfos, 20.0, 80.0, 20)
        print(f"[OK] Bombas compatibles encontradas: {len(bombas_encontradas)}")
        if bombas_encontradas:
            mejor = bombas_encontradas[0]
            print(f"  Mejor opcion: {mejor['modelo']} (score: {mejor['_score']:.3f})\n")
    except Exception as e:
        print(f"[ERROR] {e}\n")
    
    # Test 3: Convertir curvas
    print("Test 3: Convertir curvas al formato textarea")
    try:
        if bombas_encontradas:
            bomba_test = bombas_encontradas[0]
            curvas_texto = convert_pump_to_textarea_format(bomba_test, 'L/s')
            print(f"[OK] Curvas convertidas para {bomba_test['modelo']}")
            print(f"  Curva H-Q (primeras 2 lineas):")
            lineas = curvas_texto['bomba'].split('\n')[:2]
            for linea in lineas:
                print(f"    {linea}")
            print()
    except Exception as e:
        print(f"[ERROR] {e}\n")
    
    # Test 4: Validar datos
    print("Test 4: Validar datos de bomba")
    try:
        if bombas_encontradas:
            bomba_test = bombas_encontradas[0]
            es_valida, errores = validate_pump_data(bomba_test)
            if es_valida:
                print(f"[OK] Bomba {bomba_test['modelo']} es valida")
            else:
                print(f"[ERROR] Bomba tiene errores:")
                for error in errores:
                    print(f"  - {error}")
            print()
    except Exception as e:
        print(f"[ERROR] {e}\n")
    
    print("=== Pruebas completadas ===")
