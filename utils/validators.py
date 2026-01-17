# Validadores de datos

from typing import List, Dict, Any, Tuple
import numpy as np

def validate_flow_value(value: float, min_val: float = 0.0, max_val: float = 10000.0) -> bool:
    """
    Valida un valor de caudal.
    
    Args:
        value: Valor a validar
        min_val: Valor mínimo permitido
        max_val: Valor máximo permitido
    
    Returns:
        True si el valor es válido, False en caso contrario
    """
    return isinstance(value, (int, float)) and min_val <= value <= max_val

def validate_head_value(value: float, min_val: float = 0.0, max_val: float = 1000.0) -> bool:
    """
    Valida un valor de altura.
    
    Args:
        value: Valor a validar
        min_val: Valor mínimo permitido
        max_val: Valor máximo permitido
    
    Returns:
        True si el valor es válido, False en caso contrario
    """
    return isinstance(value, (int, float)) and min_val <= value <= max_val

def validate_efficiency_value(value: float, min_val: float = 0.0, max_val: float = 100.0) -> bool:
    """
    Valida un valor de eficiencia.
    
    Args:
        value: Valor a validar
        min_val: Valor mínimo permitido
        max_val: Valor máximo permitido
    
    Returns:
        True si el valor es válido, False en caso contrario
    """
    return isinstance(value, (int, float)) and min_val <= value <= max_val

def validate_power_value(value: float, min_val: float = 0.0, max_val: float = 10000.0) -> bool:
    """
    Valida un valor de potencia.
    
    Args:
        value: Valor a validar
        min_val: Valor mínimo permitido
        max_val: Valor máximo permitido
    
    Returns:
        True si el valor es válido, False en caso contrario
    """
    return isinstance(value, (int, float)) and min_val <= value <= max_val

def validate_npsh_value(value: float, min_val: float = 0.0, max_val: float = 100.0) -> bool:
    """
    Valida un valor de NPSH.
    
    Args:
        value: Valor a validar
        min_val: Valor mínimo permitido
        max_val: Valor máximo permitido
    
    Returns:
        True si el valor es válido, False en caso contrario
    """
    return isinstance(value, (int, float)) and min_val <= value <= max_val

def validate_curve_point(point: List[float]) -> bool:
    """
    Valida un punto de curva.
    
    Args:
        point: Punto de curva [x, y]
    
    Returns:
        True si el punto es válido, False en caso contrario
    """
    if not isinstance(point, list) or len(point) != 2:
        return False
    
    x, y = point
    
    # Validar que ambos valores sean numéricos y positivos
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        return False
    
    if x < 0 or y < 0:
        return False
    
    return True

def validate_curve_data(curve_data: List[List[float]], min_points: int = 2) -> Tuple[bool, str]:
    """
    Valida los datos de una curva completa.
    
    Args:
        curve_data: Datos de la curva
        min_points: Número mínimo de puntos requeridos
    
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not curve_data:
        return False, "La curva no tiene datos"
    
    if len(curve_data) < min_points:
        return False, f"La curva debe tener al menos {min_points} puntos"
    
    # Validar cada punto
    for i, point in enumerate(curve_data):
        if not validate_curve_point(point):
            return False, f"Punto {i+1} inválido: {point}"
    
    # Validar que los valores de x sean crecientes
    x_values = [point[0] for point in curve_data]
    if x_values != sorted(x_values):
        return False, "Los valores de caudal deben estar en orden creciente"
    
    # Validar que no haya valores duplicados de x
    if len(x_values) != len(set(x_values)):
        return False, "No se permiten valores duplicados de caudal"
    
    return True, ""

def validate_system_parameters(params: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida los parámetros del sistema.
    
    Args:
        params: Diccionario con parámetros del sistema
    
    Returns:
        Tupla (es_válido, lista_errores)
    """
    errors = []
    
    # Validar altura estática
    h_estatica = params.get('h_estatica', 0)
    if not validate_head_value(h_estatica):
        errors.append("Altura estática inválida")
    
    # Validar caudal nominal
    caudal_nominal = params.get('caudal_nominal', 0)
    if not validate_flow_value(caudal_nominal):
        errors.append("Caudal nominal inválido")
    
    # Validar NPSH disponible
    npshd = params.get('npshd', 0)
    if not validate_npsh_value(npshd):
        errors.append("NPSH disponible inválido")
    
    # Validar longitudes
    long_succion = params.get('long_succion', 0)
    if not isinstance(long_succion, (int, float)) or long_succion < 0:
        errors.append("Longitud de succión inválida")
    
    long_impulsion = params.get('long_impulsion', 0)
    if not isinstance(long_impulsion, (int, float)) or long_impulsion < 0:
        errors.append("Longitud de impulsión inválida")
    
    # Validar diámetros
    diam_succion = params.get('diam_succion', 0)
    if not isinstance(diam_succion, (int, float)) or diam_succion <= 0:
        errors.append("Diámetro de succión inválido")
    
    diam_impulsion = params.get('diam_impulsion', 0)
    if not isinstance(diam_impulsion, (int, float)) or diam_impulsion <= 0:
        errors.append("Diámetro de impulsión inválido")
    
    return len(errors) == 0, errors

def validate_accessory_data(accessory: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Valida los datos de un accesorio.
    
    Args:
        accessory: Diccionario con datos del accesorio
    
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not isinstance(accessory, dict):
        return False, "El accesorio debe ser un diccionario"
    
    # Validar tipo
    if 'tipo' not in accessory or not accessory['tipo']:
        return False, "El accesorio debe tener un tipo"
    
    # Validar cantidad
    if 'cantidad' not in accessory:
        return False, "El accesorio debe tener una cantidad"
    
    cantidad = accessory['cantidad']
    if not isinstance(cantidad, (int, float)) or cantidad <= 0:
        return False, "La cantidad debe ser un número positivo"
    
    return True, ""

def validate_vfd_parameters(rpm_percentage: float, paso_caudal: float) -> Tuple[bool, List[str]]:
    """
    Valida los parámetros de VFD.
    
    Args:
        rpm_percentage: Porcentaje de RPM
        paso_caudal: Paso del caudal
    
    Returns:
        Tupla (es_válido, lista_errores)
    """
    errors = []
    
    # Validar porcentaje de RPM
    if not isinstance(rpm_percentage, (int, float)) or rpm_percentage <= 0 or rpm_percentage > 100:
        errors.append("El porcentaje de RPM debe estar entre 0 y 100")
    
    # Validar paso del caudal
    if not isinstance(paso_caudal, (int, float)) or paso_caudal <= 0:
        errors.append("El paso del caudal debe ser un número positivo")
    
    return len(errors) == 0, errors

def validate_polynomial_degree(degree: int, num_points: int) -> Tuple[bool, str]:
    """
    Valida el grado del polinomio para el número de puntos dados.
    
    Args:
        degree: Grado del polinomio
        num_points: Número de puntos disponibles
    
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if degree < 1:
        return False, "El grado del polinomio debe ser al menos 1"
    
    if degree >= num_points:
        return False, f"El grado del polinomio ({degree}) debe ser menor que el número de puntos ({num_points})"
    
    return True, ""

def validate_export_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida los datos para exportación.
    
    Args:
        data: Diccionario con datos a exportar
    
    Returns:
        Tupla (es_válido, lista_errores)
    """
    errors = []
    
    # Validar que hay datos de curvas
    if 'curva_inputs' not in data or not data['curva_inputs']:
        errors.append("No hay datos de curvas para exportar")
    
    # Validar cada curva
    curva_inputs = data.get('curva_inputs', {})
    for curve_name, curve_data in curva_inputs.items():
        if curve_data:
            is_valid, error_msg = validate_curve_data(curve_data)
            if not is_valid:
                errors.append(f"Curva {curve_name}: {error_msg}")
    
    return len(errors) == 0, errors
