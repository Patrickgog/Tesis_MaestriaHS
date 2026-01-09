# Análisis de curvas de bomba

import numpy as np
from typing import List, Tuple, Dict, Any
from scipy.optimize import fsolve

def fit_polynomial(x_data: List[float], y_data: List[float], degree: int) -> np.ndarray:
    """
    Ajusta un polinomio a los datos de la curva.
    
    Args:
        x_data: Datos de x (caudal)
        y_data: Datos de y (altura, eficiencia, etc.)
        degree: Grado del polinomio
    
    Returns:
        Coeficientes del polinomio
    """
    if len(x_data) < 2:
        return np.array([0])
    
    x = np.array(x_data)
    y = np.array(y_data)
    
    # Ajustar polinomio
    coef = np.polyfit(x, y, min(degree, len(x_data) - 1))
    return coef

def calculate_bep(efficiency_curve_data: List[Tuple[float, float]], 
                 degree: int = 2) -> Tuple[float, float]:
    """
    Calcula el Best Efficiency Point (BEP).
    
    Args:
        efficiency_curve_data: Datos de la curva de eficiencia
        degree: Grado del polinomio para el ajuste
    
    Returns:
        Tupla (caudal_BEP, eficiencia_BEP)
    """
    if len(efficiency_curve_data) < 2:
        return (0, 0)
    
    x_data = [p[0] for p in efficiency_curve_data]
    y_data = [p[1] for p in efficiency_curve_data]
    
    # Ajustar polinomio
    coef = fit_polynomial(x_data, y_data, degree)
    
    # Generar puntos para encontrar el máximo
    x_fit = np.linspace(min(x_data), max(x_data), 100)
    y_fit = np.polyval(coef, x_fit)
    
    # Encontrar el índice del máximo
    idx_max = np.argmax(y_fit)
    
    return (x_fit[idx_max], y_fit[idx_max])

def calculate_efficiency_zone(bep_q: float, efficiency_range: Tuple[float, float] = (0.65, 1.15)) -> Tuple[float, float]:
    """
    Calcula la zona de eficiencia basada en el BEP.
    
    Args:
        bep_q: Caudal del BEP
        efficiency_range: Rango de eficiencia (por defecto 65-115% del BEP)
    
    Returns:
        Tupla (caudal_mín, caudal_máx) de la zona de eficiencia
    """
    q_min = bep_q * efficiency_range[0]
    q_max = bep_q * efficiency_range[1]
    return (q_min, q_max)

def find_curve_intersection(pump_coef: np.ndarray, system_coef: np.ndarray, 
                          x_range: Tuple[float, float] = (0, 1000)) -> Tuple[float, float]:
    """
    Encuentra la intersección entre dos curvas polinomiales.
    
    Args:
        pump_coef: Coeficientes de la curva de la bomba
        system_coef: Coeficientes de la curva del sistema
        x_range: Rango de búsqueda para x
    
    Returns:
        Tupla (x_intersección, y_intersección)
    """
    def intersection_func(q):
        return np.polyval(pump_coef, q) - np.polyval(system_coef, q)
    
    # Intentar múltiples valores iniciales
    initial_guesses = np.linspace(x_range[0], x_range[1], 10)
    
    for guess in initial_guesses:
        try:
            q_int = fsolve(intersection_func, guess)[0]
            h_int = np.polyval(system_coef, q_int)
            
            # Verificar que la solución esté en el rango válido
            if x_range[0] <= q_int <= x_range[1] and h_int > 0:
                return (q_int, h_int)
        except:
            continue
    
    return (0, 0)

def calculate_vfd_curves(base_curve_data: List[Tuple[float, float]], 
                        rpm_percentage: float) -> List[Tuple[float, float]]:
    """
    Calcula las curvas ajustadas para VFD basadas en el porcentaje de RPM.
    
    Args:
        base_curve_data: Datos de la curva base (100% RPM)
        rpm_percentage: Porcentaje de RPM (ej: 76 para 76%)
    
    Returns:
        Lista de tuplas (caudal, altura) ajustadas
    """
    if rpm_percentage <= 0:
        return []
    
    # Factor de ajuste basado en las leyes de afinidad
    factor = rpm_percentage / 100.0
    
    adjusted_curve = []
    for q, h in base_curve_data:
        # Leyes de afinidad: Q ∝ N, H ∝ N²
        q_adj = q * factor
        h_adj = h * (factor ** 2)
        adjusted_curve.append((q_adj, h_adj))
    
    return adjusted_curve

def interpolate_curve_value(x_data: List[float], y_data: List[float], 
                           x_target: float) -> float:
    """
    Interpola un valor en la curva.
    
    Args:
        x_data: Datos de x
        y_data: Datos de y
        x_target: Valor de x para interpolar
    
    Returns:
        Valor interpolado de y
    """
    if len(x_data) < 2:
        return 0
    
    return float(np.interp(x_target, x_data, y_data))

def calculate_curve_derivative(coef: np.ndarray, x: float) -> float:
    """
    Calcula la derivada de la curva en un punto específico.
    
    Args:
        coef: Coeficientes del polinomio
        x: Punto donde calcular la derivada
    
    Returns:
        Valor de la derivada
    """
    if len(coef) < 2:
        return 0
    
    # Derivada del polinomio
    deriv_coef = np.polyder(coef)
    return float(np.polyval(deriv_coef, x))

def calculate_curve_area(coef: np.ndarray, x_range: Tuple[float, float]) -> float:
    """
    Calcula el área bajo la curva.
    
    Args:
        coef: Coeficientes del polinomio
        x_range: Rango de integración
    
    Returns:
        Área bajo la curva
    """
    if len(coef) < 1:
        return 0
    
    # Integral del polinomio
    integral_coef = np.polyint(coef)
    return float(np.polyval(integral_coef, x_range[1]) - np.polyval(integral_coef, x_range[0]))
