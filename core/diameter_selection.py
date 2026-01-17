"""
Motor de cálculo para el análisis técnico y económico de diámetros de tubería.
Abstrae la lógica de succión (NPSH) e impulsión (Pérdidas/Energía).
Soporta métodos Hazen-Williams y Darcy-Weisbach.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple

class PipeDiameterAnalyzer:
    """
    Analizador genérico de tuberías para selección de diámetros.
    Soporta análisis de Succión (NPSH/Cavitación) e Impulsión (Energía/Pérdidas).
    Soporta métodos Hazen-Williams y Darcy-Weisbach.
    """
    
    def __init__(
        self,
        fluid_props: Dict[str, float],
        operating_conditions: Dict[str, float],
        pipe_params: Dict[str, float],
        calculation_method: str = 'Darcy-Weisbach',
        hazen_c: float = 150.0
    ):
        """
        Args:
            fluid_props: density (kg/m3), viscosity (m2/s), vapor_pressure (m)
            operating_conditions: flow_rate (m3/s), temperature (°C), 
                                 atmospheric_pressure (m), npsh_required (m)
            pipe_params: length (m), absolute_roughness (m), le_over_d (adm)
            calculation_method: 'Hazen-Williams' o 'Darcy-Weisbach'
            hazen_c: Coeficiente C de Hazen-Williams (solo si method='Hazen-Williams')
        """
        self.fluid = fluid_props
        self.ops = operating_conditions
        self.pipe = pipe_params
        self.g = 9.81
        self.method = calculation_method
        self.hazen_c = hazen_c
        
        # Parámetros para costo energético (fallback)
        self.eficiencia_bomba = 0.75
        self.costo_kwh = 0.12
        
        # Motor de costos fallbacks (Consistente con GeneticOptimizer)
        self.costos_base = {
            "PVC": {"base": 5.0, "factor": 1.5},
            "HDPE": {"base": 7.0, "factor": 1.6},
            "Hierro Ductil": {"base": 25.0, "factor": 1.3},
            "Hierro Fundido": {"base": 20.0, "factor": 1.4}
        }
        
    def _get_pipe_cost_per_m(self, mat_sess: str, di_mm: float) -> float:
        """Estima el costo por metro basado en el modelo de potencia"""
        d_pulg = di_mm / 25.4
        mat_key = "PVC"
        mat_upper = mat_sess.upper()
        if "PVC" in mat_upper: mat_key = "PVC"
        elif "HDPE" in mat_upper or "PEAD" in mat_upper: mat_key = "HDPE"
        elif "DUCTIL" in mat_upper: mat_key = "Hierro Ductil"
        elif "FUNDIDO" in mat_upper: mat_key = "Hierro Fundido"
        
        c_info = self.costos_base.get(mat_key, self.costos_base["PVC"])
        return c_info["base"] * (d_pulg ** c_info["factor"])
        
    def analyze_range(self, diameters_mm: List[float], is_suction: bool = True) -> pd.DataFrame:
        """Analiza un rango de diámetros comerciales o internos directos"""
        results = []
        q = self.ops['flow_rate']
        nu = self.fluid.get('viscosity', 1.004e-6)
        epsilon = self.pipe.get('absolute_roughness', 0.000046)
        le_over_d = self.pipe.get('le_over_d', 0.0)
        rho = self.fluid.get('density', 1000.0)
        temp = self.ops.get('temperature', 20.0)
        
        # Presiones base en mca para convertirlas luego
        h_atm = self.ops['atmospheric_pressure']
        h_vap = self.fluid['vapor_pressure']
        h_static = self.ops.get('static_head', 0.0)
        
        # Parámetros para costo energético
        pass 
        
        for d_in in diameters_mm:
            # Asumimos que d_in es el diámetro interno REAL si viene de la base de datos
            di_m = d_in / 1000.0 if d_in > 0 else 0.001
            
            # 1. Velocidad
            area = np.pi * (di_m**2) / 4
            v = q / area if area > 0 else 0
            
            # 2. Reynolds
            re = (v * di_m) / nu if nu > 0 else 0
            
            # 3. Régimen
            if re < 2000:
                regimen = "Laminar"
            elif re < 4000:
                regimen = "Transición"
            else:
                regimen = "Turbulento"
            
            # 4. Cálculo de pérdidas según método seleccionado
            if self.method == 'Hazen-Williams':
                # Hazen-Williams: hf = 10.674 * (Q^1.852) / (C^1.852 * D^4.87) * L
                # Q en m³/s, D en m, L en m
                if di_m > 0 and self.hazen_c > 0:
                    hf = 10.674 * (q**1.852) / (self.hazen_c**1.852 * di_m**4.87) * self.pipe['length']
                    l_equiv = le_over_d * di_m
                    ha = 10.674 * (q**1.852) / (self.hazen_c**1.852 * di_m**4.87) * l_equiv
                    f = 0.0  # No aplica para HW
                else:
                    hf = 0
                    ha = 0
                    f = 0
            else:
                # Darcy-Weisbach
                if re < 2000:
                    f = 64 / re if re > 0 else 0.064
                elif re < 4000:
                    f_lam = 64 / 2000
                    f_turb = 0.25 / (np.log10((epsilon/di_m)/3.7 + 5.74/(4000**0.9)))**2
                    f = f_lam + (f_turb - f_lam) * (re - 2000) / 2000
                else:
                    f = 0.25 / (np.log10((epsilon/di_m)/3.7 + 5.74/(re**0.9)))**2
                
                # Pérdidas (hf + ha)
                hf = f * (self.pipe['length'] / di_m) * (v**2) / (2 * self.g) if di_m > 0 else 0
                l_equiv = le_over_d * di_m
                ha = f * (l_equiv / di_m) * (v**2) / (2 * self.g) if di_m > 0 else 0
            
            h_total = hf + ha
            
            # 5. Gradiente Hidráulico J (m/m) - pérdida por metro de tubería
            longitud_total = self.pipe['length'] + l_equiv
            j_gradient = h_total / longitud_total if longitud_total > 0 else 0
            
            # 6. Presiones Operativas (Manométricas/Gauge para comparación con PN)
            gamma = rho * self.g
            if is_suction:
                # En succión, la presión que "ve" la tubería es el nivel estático menos las pérdidas
                # (Presión relativa a la atmosférica en la entrada de la bomba)
                h_gauge = h_static - h_total
            else:
                # En impulsión, la presión es el cabezal estático más las pérdidas por fricción
                h_gauge = h_static + h_total
            
            p_gauge_kpa = (h_gauge * gamma) / 1000.0
            
            # NPSH (Requiere Presión Absoluta)
            h_abs_suction = h_atm + h_gauge
            nps_d = h_abs_suction - h_vap
            
            # Presión de Vapor para referencia
            pv_kpa_abs = (h_vap * gamma) / 1000.0
            
            # 7. Sumergencia
            fr = v / np.sqrt(self.g * di_m) if di_m > 0 else 0
            s_min = di_m * (1.0 + 2.3 * fr)
            
            # 8. Costo Energético Anual (USD/año)
            # Potencia hidráulica: P = gamma * Q * H (W)
            # Potencia eléctrica: P_elec = P_hidraulica / eficiencia
            # Costo = P_elec * horas * costo_kwh
            if not is_suction:  # Solo calcular para impulsión
                h_bomba = abs(h_static) + h_total  # Altura total de bombeo
                potencia_hidraulica_w = gamma * q * h_bomba  # W
                potencia_electrica_kw = (potencia_hidraulica_w / 1000.0) / self.eficiencia_bomba
                costo_energia_anual = potencia_electrica_kw * (self.ops.get('operational_hours', 12) * 365) * self.costo_kwh
            else:
                costo_energia_anual = 0
            
            # 9. CAPEX (Inversión)
            mat_sess = self.pipe.get('material', 'PVC')
            costo_m = self._get_pipe_cost_per_m(mat_sess, d_in)
            capex_total = costo_m * self.pipe['length'] * 1.3 # 30% adicional por accesorios
            
            results.append({
                'di_mm': d_in,
                'velocity': v,
                'reynolds': re,
                'regime': regimen,
                'friction_factor': f,
                'h_primary': hf,
                'h_secondary': ha,
                'friction_loss': h_total,
                'hydraulic_gradient': j_gradient,
                'npsh_available': nps_d,
                'pressure_kpa': p_gauge_kpa, # Mostrar Presión Manométrica
                'pressure_abs_kpa': h_abs_suction * gamma / 1000.0,
                'vapor_pressure_kpa': pv_kpa_abs,
                'submergence_min': max(s_min, 1.5 * di_m),
                'cavitation_risk': nps_d < (self.ops.get('npsh_required', 3.0) + 0.5),
                'energy_cost_annual': costo_energia_anual,
                'capex': capex_total,
                'method_used': self.method
            })
            
        return pd.DataFrame(results)
