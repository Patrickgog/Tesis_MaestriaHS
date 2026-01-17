"""
Utilidades para validación y extrapolación de curvas de bomba para Allievi 13.0.0

Este módulo proporciona funciones para:
- Validar que las curvas cubran el rango completo del primer cuadrante (Q=0 a H≈0)
- Extrapolar curvas automáticamente hasta H≈0 cuando sea necesario
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional


def validar_rango_primer_cuadrante(
    df_bomba: Optional[pd.DataFrame],
    df_potencia: Optional[pd.DataFrame] = None,
    tolerancia_h: float = 5.0
) -> Dict:
    """
    Valida si las curvas de bomba cubren el rango completo del primer cuadrante.
    
    Según manual de Allievi, el método "Curvas por Puntos" requiere:
    - Q mínimo = 0 (válvula cerrada)
    - H mínimo ≈ 0 (bomba en shutoff)
    
    Args:
        df_bomba: DataFrame con curva H-Q (columnas: Caudal, Altura)
        df_potencia: DataFrame con curva P-Q (opcional)
        tolerancia_h: Tolerancia en metros para considerar H≈0 (default: 5.0)
    
    Returns:
        Diccionario con:
        - cubre_q_min: bool - ¿Incluye Q=0?
        - cubre_h_min: bool - ¿Llega hasta H≈0?
        - q_min_actual: float - Q mínimo actual
        - q_max_actual: float - Q máximo actual
        - h_min_actual: float - H mínimo actual
        - h_max_actual: float - H máximo actual
        - q_para_h_cero: float - Q estimado donde H≈0 (usando regresión)
        - mensaje_validacion: str - Mensaje descriptivo
        - completo: bool - ¿Cumple ambos requisitos?
    """
    resultado = {
        'cubre_q_min': False,
        'cubre_h_min': False,
        'q_min_actual': 0.0,
        'q_max_actual': 0.0,
        'h_min_actual': 0.0,
        'h_max_actual': 0.0,
        'q_para_h_cero': 0.0,
        'mensaje_validacion': '',
        'completo': False
    }
    
    if df_bomba is None or len(df_bomba) == 0:
        resultado['mensaje_validacion'] = "❌ No hay datos de curva H-Q disponibles"
        return resultado
    
    # Extraer caudales y alturas
    try:
        # Limpiar datos (remover emojis y convertir a numérico)
        caudales = pd.to_numeric(
            df_bomba.iloc[:, 0].apply(lambda x: str(x).replace('⭐', '').strip()),
            errors='coerce'
        )
        alturas = pd.to_numeric(
            df_bomba.iloc[:, 1].apply(lambda x: str(x).replace('⭐', '').strip()),
            errors='coerce'
        )
        
        # Eliminar NaN
        mask = ~(caudales.isna() | alturas.isna())
        caudales = caudales[mask].values
        alturas = alturas[mask].values
        
        if len(caudales) == 0:
            resultado['mensaje_validacion'] = "❌ Datos de curva H-Q no válidos"
            return resultado
    except Exception as e:
        resultado['mensaje_validacion'] = f"❌ Error procesando datos: {e}"
        return resultado
    
    # Calcular valores
    resultado['q_min_actual'] = float(np.min(caudales))
    resultado['q_max_actual'] = float(np.max(caudales))
    resultado['h_min_actual'] = float(np.min(alturas))
    resultado['h_max_actual'] = float(np.max(alturas))
    
    # Validar Q mínimo (debe ser 0 o muy cercano)
    resultado['cubre_q_min'] = resultado['q_min_actual'] <= 0.1
    
    # Validar H mínimo (debe estar cerca de 0)
    resultado['cubre_h_min'] = resultado['h_min_actual'] <= tolerancia_h
    
    # Estimar Q para H≈0 usando regresión polinómica
    try:
        if len(caudales) >= 2:
            # Ajuste cuadrático H = a + bQ + cQ²
            grado = min(2, len(caudales) - 1)
            coef = np.polyfit(caudales, alturas, grado)
            
            # Resolver H ≈ 0
            # Para cuadrática: cQ² + bQ + a = 0
            if grado == 2:
                a, b, c = coef[2], coef[1], coef[0]
                discriminante = b**2 - 4*a*c
                if discriminante >= 0 and a != 0:
                    q1 = (-b + np.sqrt(discriminante)) / (2*a)
                    q2 = (-b - np.sqrt(discriminante)) / (2*a)
                    # Tomar la raíz positiva mayor
                    q_cero = max(q1, q2) if q1 > 0 or q2 > 0 else resultado['q_max_actual'] * 1.5
                else:
                    q_cero = resultado['q_max_actual'] * 1.5
            else:
                # Lineal: Q = -a/b donde H=0
                q_cero = -coef[1] / coef[0] if coef[0] != 0 else resultado['q_max_actual'] * 1.5
            
            resultado['q_para_h_cero'] = max(float(q_cero), resultado['q_max_actual'])
    except Exception:
        resultado['q_para_h_cero'] = resultado['q_max_actual'] * 1.5
    
    # Generar mensaje de validación
    resultado['completo'] = resultado['cubre_q_min'] and resultado['cubre_h_min']
    
    if resultado['completo']:
        resultado['mensaje_validacion'] = "✅ Curvas completas para Allievi (cubre Q=0 a H≈0)"
    else:
        mensajes = []
        if not resultado['cubre_q_min']:
            mensajes.append(f"Q mín={resultado['q_min_actual']:.2f} (debe ser 0)")
        if not resultado['cubre_h_min']:
            mensajes.append(f"H mín={resultado['h_min_actual']:.2f}m (falta llegar a ≈0)")
        resultado['mensaje_validacion'] = "⚠️ Curvas incompletas: " + ", ".join(mensajes)
    
    return resultado


def extrapolar_hasta_h_cero(
    caudales: np.ndarray,
    alturas: np.ndarray,
    potencias: Optional[np.ndarray],
    coef_bomba: np.ndarray,
    coef_potencia: Optional[np.ndarray],
    q_objetivo: float,
    paso: float
) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray], int]:
    """
    Extiende el rango de caudales hasta que H≈0.
    
    Args:
        caudales: Array de caudales originales
        alturas: Array de alturas originales
        potencias: Array de potencias originales (opcional)
        coef_bomba: Coeficientes del polinomio H-Q
        coef_potencia: Coeficientes del polinomio P-Q (opcional)
        q_objetivo: Caudal objetivo donde H≈0
        paso: Paso de caudal para extrapolación
    
    Returns:
        Tupla con:
        - caudales_extendidos: np.array
        - alturas_extendidas: np.array
        - potencias_extendidas: np.array o None
        - num_puntos_extrapolados: int
    """
    q_max_original = np.max(caudales)
    
    # Generar nuevos puntos desde Q max hasta Q objetivo
    if q_objetivo <= q_max_original:
        # No hay necesidad de extrapolar
        return caudales, alturas, potencias, 0
    
    # Crear puntos extrapolados
    q_extra = np.arange(q_max_original + paso, q_objetivo + paso, paso)
    
    # Calcular alturas extrapoladas
    h_extra = np.polyval(coef_bomba, q_extra)
    
    # No permitir alturas negativas
    h_extra = np.maximum(h_extra, 0.0)
    
    # Calcular potencias extrapoladas si hay coeficientes
    p_extra = None
    if coef_potencia is not None and potencias is not None:
        p_extra = np.polyval(coef_potencia, q_extra)
        p_extra = np.maximum(p_extra, 0.0)  # No permitir potencias negativas
    
    # Combinar datos originales con extrapolados
    caudales_ext = np.concatenate([caudales, q_extra])
    alturas_ext = np.concatenate([alturas, h_extra])
    
    if p_extra is not None:
        potencias_ext = np.concatenate([potencias, p_extra])
    else:
        potencias_ext = potencias
    
    num_extrapolados = len(q_extra)
    
    return caudales_ext, alturas_ext, potencias_ext, num_extrapolados


def crear_marcador_extrapolacion(
    df: pd.DataFrame,
    q_max_original: float
) -> pd.DataFrame:
    """
    Agrega una columna indicadora de puntos extrapolados.
    
    Args:
        df: DataFrame con datos de curva
        q_max_original: Q máximo original (antes de extrapolación)
    
    Returns:
        DataFrame con columna 'Tipo' agregada
    """
    df_copy = df.copy()
    
    # Extraer caudales (primera columna)
    caudales = pd.to_numeric(
        df_copy.iloc[:, 0].apply(lambda x: str(x).replace('⭐', '').strip()),
        errors='coerce'
    )
    
    # Marcar como 'Normal' o 'Extrapolado'
    df_copy['Tipo'] = ['Normal' if q <= q_max_original else '⚡ Extrapolado' 
                        for q in caudales]
    
    return df_copy
