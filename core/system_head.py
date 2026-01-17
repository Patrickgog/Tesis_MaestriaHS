# Cálculo de altura del sistema

import numpy as np
from typing import List, Tuple, Dict, Any
from .calculations import calculate_system_head, convert_flow_unit

def calculate_adt_for_multiple_flows(flows: List[float], flow_unit: str, 
                                   system_params: Dict[str, Any]) -> List[float]:
    """
    Calcula la altura total del sistema (ADT) para múltiples caudales (Wrapper).
    """
    from .calculations import calculate_adt_for_multiple_flows as calc_motor
    resultados = calc_motor(flows, flow_unit, system_params)
    return [r['adt_total'] for r in resultados]

def generate_system_curve_points(min_flow: float, max_flow: float, 
                               num_points: int, flow_unit: str,
                               system_params: Dict[str, Any]) -> Tuple[List[float], List[float]]:
    """
    Genera puntos para la curva del sistema.
    
    Args:
        min_flow: Caudal mínimo
        max_flow: Caudal máximo
        num_points: Número de puntos a generar
        flow_unit: Unidad de caudal
        system_params: Parámetros del sistema
    
    Returns:
        Tupla (caudales, alturas) de la curva del sistema
    """
    flows = np.linspace(min_flow, max_flow, num_points).tolist()
    heights = calculate_adt_for_multiple_flows(flows, flow_unit, system_params)
    
    return flows, heights

def calculate_system_curve_coefficients(flows: List[float], heights: List[float], 
                                      degree: int = 2) -> np.ndarray:
    """
    Calcula los coeficientes del polinomio que representa la curva del sistema.
    
    Args:
        flows: Caudales
        heights: Alturas correspondientes
        degree: Grado del polinomio
    
    Returns:
        Coeficientes del polinomio
    """
    if len(flows) < 2:
        return np.array([0])
    
    flows_array = np.array(flows)
    heights_array = np.array(heights)
    
    # Ajustar polinomio
    coef = np.polyfit(flows_array, heights_array, min(degree, len(flows) - 1))
    return coef

def calculate_system_head_at_flow(flow: float, flow_unit: str, 
                                 system_params: Dict[str, Any]) -> float:
    """
    Calcula la altura del sistema para un caudal específico (Wrapper).
    """
    return calculate_adt_for_multiple_flows([flow], flow_unit, system_params)[0]

def calculate_system_efficiency(flow: float, flow_unit: str, 
                              system_params: Dict[str, Any],
                              pump_efficiency: float) -> float:
    """
    Calcula la eficiencia del sistema considerando las pérdidas.
    
    Args:
        flow: Caudal
        flow_unit: Unidad de caudal
        system_params: Parámetros del sistema
        pump_efficiency: Eficiencia de la bomba
    
    Returns:
        Eficiencia del sistema
    """
    # Calcular altura del sistema
    system_head = calculate_system_head_at_flow(flow, flow_unit, system_params)
    
    # Calcular pérdidas del sistema
    static_head = system_params['h_estatica']
    system_losses = system_head - static_head
    
    # Eficiencia del sistema (simplificada)
    if system_head > 0:
        system_efficiency = pump_efficiency * (static_head / system_head)
        return min(system_efficiency, 1.0)
    
    return 0.0

def calculate_system_power(flow: float, flow_unit: str, 
                         system_params: Dict[str, Any],
                         pump_power: float) -> float:
    """
    Calcula la potencia del sistema.
    
    Args:
        flow: Caudal
        flow_unit: Unidad de caudal
        system_params: Parámetros del sistema
        pump_power: Potencia de la bomba
    
    Returns:
        Potencia del sistema
    """
    # Calcular altura del sistema
    system_head = calculate_system_head_at_flow(flow, flow_unit, system_params)
    
    # Calcular potencia del sistema (simplificada)
    if system_head > 0:
        # Factor de corrección basado en las pérdidas del sistema
        static_head = system_params['h_estatica']
        correction_factor = system_head / static_head if static_head > 0 else 1.0
        
        return pump_power * correction_factor
    
    return 0.0
