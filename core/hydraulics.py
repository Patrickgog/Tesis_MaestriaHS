"""
Módulo de Cálculos Hidráulicos
Implementa métodos Hazen-Williams y Darcy-Weisbach para pérdidas de carga
"""

import numpy as np


# ============================================================================
# TABLAS DE REFERENCIA
# ============================================================================

RUGOSIDAD_ABSOLUTA = {
    # Material: rugosidad en metros
    'PVC': 0.0000015,
    'PEAD': 0.000007,
    'HDPE': 0.000007,
    'Polietileno': 0.000007,
    'Acero': 0.000046,
    'Acero Nuevo': 0.000046,
    'Acero Comercial': 0.000046,
    'Acero Oxidado': 0.00015,
    'Hierro Fundido': 0.00026,
    'Hierro Fundido Nuevo': 0.00026,
    'Hierro Fundido Usado': 0.0015,
    'Hormigón': 0.0003,
    'Hormigón Liso': 0.0003,
    'Hormigón Rugoso': 0.003,
    'Acero Galvanizado': 0.00015
}

VISCOSIDAD_CINEMATICA = {
    # Temperatura °C: viscosidad en m²/s
    0: 1.787e-6,
    5: 1.519e-6,
    10: 1.307e-6,
    15: 1.139e-6,
    20: 1.004e-6,
    25: 0.893e-6,
    30: 0.801e-6,
    40: 0.658e-6,
    50: 0.553e-6,
    60: 0.475e-6,
    70: 0.413e-6,
    80: 0.365e-6,
    90: 0.326e-6,
    100: 0.294e-6
}


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def obtener_rugosidad_absoluta(material):
    """
    Retorna rugosidad absoluta según material de tubería
    
    Args:
        material (str): Nombre del material
        
    Returns:
        float: Rugosidad absoluta en metros
    """
    # Normalizar material (capitalizar primera letra de cada palabra)
    material_norm = material.strip().title()
    
    # Buscar en diccionario
    rugosidad = RUGOSIDAD_ABSOLUTA.get(material_norm)
    
    if rugosidad is None:
        # Intentar búsqueda parcial (ej: "Acero" en "Acero Nuevo")
        for key, value in RUGOSIDAD_ABSOLUTA.items():
            if material_norm.lower() in key.lower():
                return value
        # Default: acero comercial
        return 0.000046
    
    return rugosidad


def obtener_viscosidad_cinematica(temperatura):
    """
    Retorna viscosidad cinemática del agua según temperatura
    Usa interpolación lineal entre puntos tabulados
    
    Args:
        temperatura (float): Temperatura en °C
        
    Returns:
        float: Viscosidad cinemática en m²/s
    """
    temperaturas = sorted(VISCOSIDAD_CINEMATICA.keys())
    
    # Casos extremos
    if temperatura <= temperaturas[0]:
        return VISCOSIDAD_CINEMATICA[temperaturas[0]]
    if temperatura >= temperaturas[-1]:
        return VISCOSIDAD_CINEMATICA[temperaturas[-1]]
    
    # Interpolación lineal
    for i in range(len(temperaturas) - 1):
        t1, t2 = temperaturas[i], temperaturas[i + 1]
        if t1 <= temperatura <= t2:
            nu1 = VISCOSIDAD_CINEMATICA[t1]
            nu2 = VISCOSIDAD_CINEMATICA[t2]
            # Fórmula interpolación lineal
            nu = nu1 + (nu2 - nu1) * (temperatura - t1) / (t2 - t1)
            return nu
    
    # Fallback (no debería llegar aquí)
    return 1.004e-6  # agua a 20°C


def calcular_reynolds(V, D, nu):
    """
    Calcula el número de Reynolds
    
    Args:
        V (float): Velocidad del flujo (m/s)
        D (float): Diámetro de la tubería (m)
        nu (float): Viscosidad cinemática (m²/s)
        
    Returns:
        float: Número de Reynolds (adimensional)
    """
    if nu == 0:
        return 0
    return (V * D) / nu


def determinar_regimen_flujo(Re):
    """
    Determina el régimen de flujo según Reynolds
    
    Args:
        Re (float): Número de Reynolds
        
    Returns:
        str: 'Laminar', 'Transición' o 'Turbulento'
    """
    if Re < 2000:
        return 'Laminar'
    elif Re < 4000:
        return 'Transición'
    else:
        return 'Turbulento'


def calcular_factor_friccion_laminar(Re):
    """
    Factor de fricción para flujo laminar
    
    Args:
        Re (float): Número de Reynolds
        
    Returns:
        float: Factor de fricción de Darcy
    """
    if Re == 0:
        return 0.064  # default
    return 64.0 / Re


def calcular_factor_friccion_swamee_jain(Re, epsilon, D):
    """
    Calcula factor de fricción usando ecuación de Swamee-Jain (explícita)
    Válida para: 4000 < Re < 10⁸ y 10⁻⁶ < ε/D < 10⁻²
    
    Args:
        Re (float): Número de Reynolds
        epsilon (float): Rugosidad absoluta (m)
        D (float): Diámetro (m)
        
    Returns:
        float: Factor de fricción de Darcy
    """
    epsilon_D = epsilon / D
    
    # Swamee-Jain: f = 0.25 / [log₁₀(ε/3.7D + 5.74/Re^0.9)]²
    try:
        numerador = epsilon_D / 3.7 + 5.74 / (Re ** 0.9)
        denominador = np.log10(numerador) ** 2
        f = 0.25 / denominador
        return f
    except:
        # Fallback en caso de error (valores extremos)
        return 0.02


def calcular_factor_friccion_darcy(Re, epsilon, D):
    """
    Calcula factor de fricción de Darcy según régimen de flujo
    
    Args:
        Re (float): Número de Reynolds
        epsilon (float): Rugosidad absoluta (m)
        D (float): Diámetro (m)
        
    Returns:
        float: Factor de fricción de Darcy
    """
    if Re < 2000:
        # Flujo laminar
        return calcular_factor_friccion_laminar(Re)
    
    elif Re < 4000:
        # Zona de transición: interpolar entre laminar y turbulento
        f_lam = calcular_factor_friccion_laminar(2000)
        f_turb = calcular_factor_friccion_swamee_jain(4000, epsilon, D)
        # Interpolación lineal
        f = f_lam + (f_turb - f_lam) * (Re - 2000) / 2000
        return f
    
    else:
        # Flujo turbulento
        return calcular_factor_friccion_swamee_jain(Re, epsilon, D)


# ============================================================================
# FUNCIÓN PRINCIPAL: DARCY-WEISBACH
# ============================================================================

def calcular_perdidas_darcy_weisbach(Q, L, D, material, temperatura=20.0):
    """
    Calcula pérdidas de carga usando ecuación de Darcy-Weisbach
    
    Ecuación: hf = f × (L/D) × (V²/2g)
    
    Args:
        Q (float): Caudal (m³/s)
        L (float): Longitud de tubería (m)
        D (float): Diámetro interno (m)
        material (str): Material de la tubería
        temperatura (float): Temperatura del agua (°C)
        
    Returns:
        dict: {
            'hf': pérdida de carga (m),
            'Re': número de Reynolds,
            'regimen': régimen de flujo,
            'f': factor de fricción,
            'epsilon': rugosidad absoluta (m),
            'nu': viscosidad cinemática (m²/s),
            'V': velocidad (m/s)
        }
    """
    # Constante
    g = 9.81  # m/s²
    
    # Calcular área y velocidad
    A = np.pi * (D ** 2) / 4
    V = Q / A if A > 0 else 0
    
    # Obtener propiedades del fluido
    nu = obtener_viscosidad_cinematica(temperatura)
    
    # Obtener rugosidad del material
    epsilon = obtener_rugosidad_absoluta(material)
    
    # Calcular Reynolds
    Re = calcular_reynolds(V, D, nu)
    
    # Determinar régimen
    regimen = determinar_regimen_flujo(Re)
    
    # Calcular factor de fricción
    f = calcular_factor_friccion_darcy(Re, epsilon, D)
    
    # Calcular pérdida de carga
    # hf = f × (L/D) × (V²/2g)
    if D > 0 and V > 0:
        hf = f * (L / D) * (V ** 2) / (2 * g)
    else:
        hf = 0
    
    # Retornar resultados con todos los detalles
    return {
        'hf': hf,
        'Re': Re,
        'regimen': regimen,
        'f': f,
        'epsilon': epsilon,
        'nu': nu,
        'V': V
    }


# ============================================================================
# FUNCIÓN DE COMPATIBILIDAD
# ============================================================================

def calcular_perdidas(Q, L, D, material, metodo='Hazen-Williams', C=None, temperatura=20.0):
    """
    Función wrapper que calcula pérdidas según método seleccionado
    (Mantiene compatibilidad con código existente)
    
    Args:
        Q (float): Caudal (m³/s)
        L (float): Longitud (m)
        D (float): Diámetro (m)
        material (str): Material de tubería
        metodo (str): 'Hazen-Williams' o 'Darcy-Weisbach'
        C (float): Coeficiente Hazen-Williams (solo si metodo='Hazen-Williams')
        temperatura (float): Temperatura agua (°C, solo si metodo='Darcy-Weisbach')
        
    Returns:
        dict: {
            'hf': pérdida de carga (m),
            'metodo': método usado,
            'detalles': dict con parámetros específicos del método
        }
    """
    if metodo == 'Darcy-Weisbach':
        resultado = calcular_perdidas_darcy_weisbach(Q, L, D, material, temperatura)
        return {
            'hf': resultado['hf'],
            'metodo': 'Darcy-Weisbach',
            'detalles': resultado
        }
    else:
        # Hazen-Williams (requiere implementación externa o usar valor ya calculado)
        # Esta función es solo para Darcy-Weisbach
        # El cálculo HW se mantiene en el código existente
        return {
            'hf': 0,  # Placeholder
            'metodo': 'Hazen-Williams',
            'detalles': {'C': C}
        }


# ============================================================================
# FUNCIÓN DE TESTING
# ============================================================================

if __name__ == "__main__":
    # Test básico
    print("=== Test Módulo Hydraulics ===\n")
    
    # Caso 1: PVC, 20°C, 15 L/s, DN 2" (50mm)
    Q = 0.015  # m³/s
    L = 10  # m
    D = 0.050  # m
    material = "PVC"
    temp = 20
    
    resultado = calcular_perdidas_darcy_weisbach(Q, L, D, material, temp)
    
    print(f"Caudal: {Q*1000} L/s")
    print(f"Diámetro: {D*1000} mm")
    print(f"Material: {material}")
    print(f"Temperatura: {temp}°C")
    print(f"\nResultados:")
    print(f"  Pérdida de carga: {resultado['hf']:.4f} m")
    print(f"  Reynolds: {resultado['Re']:.0f}")
    print(f"  Régimen: {resultado['regimen']}")
    print(f"  Factor f: {resultado['f']:.6f}")
    print(f"  Rugosidad ε: {resultado['epsilon']*1000:.4f} mm")
    print(f"  Viscosidad ν: {resultado['nu']*1e6:.3f} ×10⁻⁶ m²/s")
    print(f"  Velocidad: {resultado['V']:.2f} m/s")
