import numpy as np
import random
import json
import os
from typing import List, Dict, Any, Tuple
from core.calculations import calcular_hf_hazen_williams, calculate_diametro_interno_pvc, calculate_diametro_interno_pead

class GeneticOptimizer:
    def __init__(self, 
                 caudal_lps: float, 
                 long_succion: float, 
                 long_impulsion: float,
                 h_estatica: float,
                 años_operacion: int = 20,
                 costo_kwh: float = 0.12,
                 horas_dia: float = 12,
                 tasa_interes: float = 0.05,
                 materiales_validos: List[str] = ["PVC", "PEAD", "Hierro Dúctil"],
                 costos_personalizados: Dict[str, Dict[str, float]] = None):
        
        self.caudal_lps = caudal_lps
        self.q_m3s = caudal_lps / 1000.0
        self.long_succion = long_succion
        self.long_impulsion = long_impulsion
        self.h_estatica = h_estatica
        self.años = años_operacion
        self.costo_kwh = costo_kwh
        self.horas_dia = horas_dia
        self.tasa_interes = tasa_interes
        self.materiales_validos = materiales_validos
        
        # 1. Cargar bases de datos reales para costos (si existen)
        self.db_costs = self._load_all_db_costs()
        
        # Base de precios estimados (como fallback)
        if costos_personalizados:
            self.costos_base = costos_personalizados
        else:
            self.costos_base = {
                "PVC": {"base": 5.0, "factor": 1.5},
                "PEAD": {"base": 7.0, "factor": 1.6},
                "Hierro Dúctil": {"base": 25.0, "factor": 1.3},
                "Acero": {"base": 20.0, "factor": 1.4}
            }
        
        # Catálogo simplificado de diámetros nominales (mm) para el GA
        self.catalog_dn = [50, 63, 75, 90, 110, 125, 140, 160, 200, 250, 315, 400, 500, 630]
        
        # Parámetros del GA
        self.pop_size = 40
        self.generations = 50
        self.mutation_rate = 0.1
        self.elitism = 2

    def _load_all_db_costs(self) -> Dict[str, Dict[int, float]]:
        """Carga los costos desde los archivos JSON reales"""
        costs = {"PVC": {}, "PEAD": {}, "Hierro Dúctil": {}}
        try:
            # PVC
            if os.path.exists("data_tablas/pvc_data.json"):
                with open("data_tablas/pvc_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    pvc_root = data.get("pvc_tuberias", {})
                    for union in pvc_root.values():
                        for serie in union.get("series", {}).values():
                            for tuberia in serie.get("tuberias", []):
                                dn = tuberia.get("dn_mm")
                                cost = tuberia.get("costo_usd_m", 0.0)
                                if cost > 0:
                                    # Para el GA simplificamos: tomamos el primer costo encontrado para ese DN
                                    if dn not in costs["PVC"]:
                                        costs["PVC"][dn] = cost
            
            # PEAD
            if os.path.exists("data_tablas/pead_data.json"):
                with open("data_tablas/pead_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("pead_tuberias", []):
                        dn = item.get("diametro_nominal_mm")
                        # Buscamos en cualquier serie que tenga costo
                        for serie_key in ["s12_5", "s10", "s8", "s6_3", "s5", "s4"]:
                            cost = item.get(serie_key, {}).get("costo_usd_m", 0.0)
                            if cost > 0:
                                costs["PEAD"][dn] = cost
                                break
            
            # Hierro Dúctil
            if os.path.exists("data_tablas/hierro_ductil_data.json"):
                with open("data_tablas/hierro_ductil_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f).get("hierro_ductil", {})
                    for clase in data.values():
                        for tuberia in clase.get("tuberias", []):
                            dn = tuberia.get("dn_mm")
                            cost = tuberia.get("costo_usd_m", 0.0)
                            if cost > 0:
                                costs["Hierro Dúctil"][dn] = cost
        except Exception as e:
            print(f"Error cargando base de datos de costos: {e}")
        return costs

    def _get_internal_diameter(self, material: str, dn: int) -> float:
        """Estima el diámetro interno en metros"""
        if material == "PVC":
            return (dn * 0.92) / 1000.0 
        elif material == "PEAD":
            return (dn * 0.85) / 1000.0
        else:
            return (dn * 0.95) / 1000.0

    def _get_pipe_cost_per_m(self, material: str, dn: int) -> float:
        """Busca el costo en la DB real o usa el modelo de potencia como fallback"""
        # 1. Intentar búsqueda en DB real
        if material in self.db_costs and dn in self.db_costs[material]:
            return self.db_costs[material][dn]
            
        # 2. Fallback al modelo de potencia
        d_pulg = dn / 25.4
        c_info = self.costos_base.get(material, self.costos_base["PVC"])
        return c_info["base"] * (d_pulg ** c_info["factor"])

    def calculate_capex(self, suction_mat, suction_dn, discharge_mat, discharge_dn) -> float:
        """Calcula el costo de inversión inicial"""
        cost_suction = self._get_pipe_cost_per_m(suction_mat, suction_dn) * self.long_succion
        cost_discharge = self._get_pipe_cost_per_m(discharge_mat, discharge_dn) * self.long_impulsion
        
        # Estimación de accesorios e instalación (30% adicional)
        return (cost_suction + cost_discharge) * 1.3

    def calculate_opex(self, suction_mat, suction_dn, discharge_mat, discharge_dn) -> float:
        """Calcula el valor presente del costo operativo (energía)"""
        d_suction = self._get_internal_diameter(suction_mat, suction_dn)
        d_discharge = self._get_internal_diameter(discharge_mat, discharge_dn)
        
        # Coeficientes Hazen-Williams
        c_suction = 150 if suction_mat in ["PVC", "PEAD"] else 130
        c_discharge = 150 if discharge_mat in ["PVC", "PEAD"] else 130
        
        # Pérdidas
        hf_s = calcular_hf_hazen_williams(self.q_m3s, self.long_succion, d_suction, c_suction)
        hf_d = calcular_hf_hazen_williams(self.q_m3s, self.long_impulsion, d_discharge, c_discharge)
        
        adt = self.h_estatica + hf_s + hf_d
        
        # Potencia hidráulica (kW)
        p_hid = (9.81 * self.caudal_lps * adt) / 1000.0
        # Asumimos eficiencia global de 70% para la comparación
        p_elec = p_hid / 0.70
        
        consumo_anual_kwh = p_elec * self.horas_dia * 365
        costo_anual = consumo_anual_kwh * self.costo_kwh
        
        # Valor Presente de OPEX
        vp_opex = 0
        for t in range(1, self.años + 1):
            vp_opex += costo_anual / ((1 + self.tasa_interes) ** t)
            
        return vp_opex

    def fitness(self, individual: List[int]) -> float:
        """Función de aptitud: Inverso del costo total con penalizaciones"""
        s_mat_idx, s_dn_idx, d_mat_idx, d_dn_idx = individual
        
        s_mat = self.materiales_validos[s_mat_idx]
        s_dn = self.catalog_dn[s_dn_idx]
        d_mat = self.materiales_validos[d_mat_idx]
        d_dn = self.catalog_dn[d_dn_idx]
        
        # Diámetros internos
        di_s = self._get_internal_diameter(s_mat, s_dn)
        di_d = self._get_internal_diameter(d_mat, d_dn)
        
        # Velocidades
        v_s = self.q_m3s / (np.pi * (di_s/2)**2)
        v_d = self.q_m3s / (np.pi * (di_d/2)**2)
        
        capex = self.calculate_capex(s_mat, s_dn, d_mat, d_dn)
        opex = self.calculate_opex(s_mat, s_dn, d_mat, d_dn)
        
        total_cost = capex + opex
        
        # -- PENALIZACIONES --
        penalty = 1.0
        
        # Velocidad en succión (Ideal 0.6 - 1.5 m/s)
        if v_s > 1.5: penalty += (v_s - 1.5) * 10
        if v_s < 0.3: penalty += (0.3 - v_s) * 2
            
        # Velocidad en impulsión (Ideal 0.8 - 2.5 m/s)
        if v_d > 2.5: penalty += (v_d - 2.5) * 10
        if v_d < 0.5: penalty += (0.5 - v_d) * 2
        
        # Penalizar diámetros de succión menores que impulsión (mala práctica)
        if s_dn < d_dn: penalty += 5.0
            
        return 1.0 / (total_cost * penalty)

    def optimize(self):
        """Ejecuta el ciclo evolutivo"""
        # Población inicial: [mat_s, dn_s, mat_d, dn_d]
        population = []
        for _ in range(self.pop_size):
            ind = [
                random.randint(0, len(self.materiales_validos) - 1),
                random.randint(0, len(self.catalog_dn) - 1),
                random.randint(0, len(self.materiales_validos) - 1),
                random.randint(0, len(self.catalog_dn) - 1)
            ]
            population.append(ind)
            
        history = []
        
        for gen in range(self.generations):
            # Evaluar fitness
            scores = [self.fitness(ind) for ind in population]
            
            # Guardar mejor de la generación
            best_idx = np.argmax(scores)
            best_fitness = scores[best_idx]
            best_ind = population[best_idx]
            
            # Convertir fitness a costo para el historial
            s_mat = self.materiales_validos[best_ind[0]]
            s_dn = self.catalog_dn[best_ind[1]]
            d_mat = self.materiales_validos[best_ind[2]]
            d_dn = self.catalog_dn[best_ind[3]]
            
            best_capex = self.calculate_capex(s_mat, s_dn, d_mat, d_dn)
            best_opex = self.calculate_opex(s_mat, s_dn, d_mat, d_dn)
            
            history.append({
                "gen": gen,
                "fitness": best_fitness,
                "cost": 1.0 / best_fitness, # Costo penalizado
                "real_cost": best_capex + best_opex,
                "capex": best_capex,
                "opex": best_opex,
                "suction": f"{s_mat} DN{s_dn}",
                "discharge": f"{d_mat} DN{d_dn}"
            })
            
            # Selección (Torneo)
            new_population = []
            
            # Elitismo
            sorted_indices = np.argsort(scores)[::-1]
            for i in range(self.elitism):
                new_population.append(population[sorted_indices[i]])
            
            while len(new_population) < self.pop_size:
                # Torneo
                p1 = self._tournament(population, scores)
                p2 = self._tournament(population, scores)
                
                # Cruce (un punto)
                c1, c2 = self._crossover(p1, p2)
                
                # Mutación
                c1 = self._mutate(c1)
                c2 = self._mutate(c2)
                
                new_population.append(c1)
                if len(new_population) < self.pop_size:
                    new_population.append(c2)
            
            population = new_population
            
        return history, population[0]

    def _tournament(self, pop, scores, k=3):
        selection = random.sample(range(len(pop)), k)
        best = selection[0]
        for i in selection[1:]:
            if scores[i] > scores[best]:
                best = i
        return pop[best].copy()

    def _crossover(self, p1, p2):
        point = random.randint(1, 3)
        c1 = p1[:point] + p2[point:]
        c2 = p2[:point] + p1[point:]
        return c1, c2

    def _mutate(self, ind):
        for i in range(len(ind)):
            if random.random() < self.mutation_rate:
                if i in [0, 2]: # Materiales
                    ind[i] = random.randint(0, len(self.materiales_validos) - 1)
                else: # Diámetros
                    ind[i] = random.randint(0, len(self.catalog_dn) - 1)
        return ind
