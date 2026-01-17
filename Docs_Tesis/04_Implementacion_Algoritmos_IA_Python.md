# 4. Desarrollo e Implementación de Algoritmos de IA en Python


## Documento Técnico - Tesis de Maestría en Hidrosanitaria

### Resumen Ejecutivo

Este documento detalla la implementación en Python de los algoritmos de inteligencia artificial para la selección automatizada de componentes en sistemas de bombeo, incluyendo código fuente, decisiones de diseño y optimizaciones de rendimiento.

---

## 1. IMPLEMENTACIÓN DEL ALGORITMO GENÉTICO

### 1.1 Estructura de Clases

```python
# File: core/genetic_optimizer.py

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import concurrent.futures
from functools import lru_cache

@dataclass
class Cromosoma:
    """
    Representación inmutable de un diseño candidato
    """
    D_succion_idx: int          # Índice en catálogo diámetros [0-14]
    D_impulsion_idx: int        # Índice en catálogo diámetros [0-14]
    bomba_idx: int              # Índice en base datos bombas [0-99]
    rpm_percent: float          # Factor RPM para VFD [0.4-1.0]
    
    def __hash__(self):
        """Permite usar como key en cache"""
        return hash((self.D_succion_idx, self.D_impulsion_idx, 
                     self.bomba_idx, round(self.rpm_percent, 3)))
    
    def to_design_params(self, catalogo_D, base_datos_bombas):
        """Decodifica a parámetros reales de diseño"""
        return {
            'D_succion_mm': catalogo_D[self.D_succion_idx],
            'D_impulsion_mm': catalogo_D[self.D_impulsion_idx],
            'bomba': base_datos_bombas[self.bomba_idx],
            'rpm_factor': self.rpm_percent
        }


class GeneticOptimizer:
    """
    Optimizador genético para sistemas de bombeo
    """
    
    def __init__(self, 
                 parametros_sistema: Dict,
                 catalogo_diametros: List[float],
                 base_datos_bombas: List[Dict],
                 config: Optional[Dict] = None):
        """
        Args:
            parametros_sistema: Q, H, L, elevación, temp, etc.
            catalogo_diametros: Lista diámetros comerciales mm
            base_datos_bombas: Lista diccionarios con specs bombas
            config: Configuración AG (población, gen, prob_cruce, etc.)
        """
        self.params = parametros_sistema
        self.catalogo_D = catalogo_diametros
        self.database_bombas = base_datos_bombas
        
        # Configuración por defecto
        self.config = {
            'poblacion_size': 100,
            'max_generaciones': 200,
            'prob_cruce': 0.8,
            'prob_mutacion': 0.05,
            'elite_size': 5,
            'torneo_size': 3,
            'convergencia_tol': 1e-6,
            'gen_sin_mejora_max': 20,
            'pool_workers': 4  # CPUs para paralelización
        }
        
        if config:
            self.config.update(config)
        
        # Estado interno
        self.poblacion = []
        self.fitness_historia = []
        self.mejor_individuo = None
        self.mejor_fitness = float('inf')
        
        # Cache: evita recalcular mismo individuo
        self._fitness_cache = {}
    
    def optimizar(self) -> Tuple[Cromosoma, float, Dict]:
        """
        Ejecuta optimización genética
        
        Returns:
            mejor_individuo: Cromosoma óptimo
            mejor_fitness: Fitness del óptimo
            info: Dict con estadísticas convergencia
        """
        print("🧬 Iniciando Algoritmo Genético...")
        print(f"   Población: {self.config['poblacion_size']}")
        print(f"   Generaciones máx: {self.config['max_generaciones']}")
        
        # 1. Inicialización
        self.poblacion = self._generar_poblacion_inicial()
        gen_sin_mejora = 0
        
        # 2. Loop evolutivo
        for gen in range(self.config['max_generaciones']):
            # Evaluar población
            fitness_values = self._evaluar_poblacion_paralelo(self.poblacion)
            
            # Registrar mejor
            min_fitness_gen = min(fitness_values)
            idx_mejor = fitness_values.index(min_fitness_gen)
            
            if min_fitness_gen < self.mejor_fitness:
                self.mejor_fitness = min_fitness_gen
                self.mejor_individuo = self.poblacion[idx_mejor]
                gen_sin_mejora = 0
                print(f"   Gen {gen}: Nuevo mejor fitness = ${self.mejor_fitness:,.0f}")
            else:
                gen_sin_mejora += 1
            
            self.fitness_historia.append(min_fitness_gen)
            
            # Criterio de parada
            if gen_sin_mejora >= self.config['gen_sin_mejora_max']:
                print(f"   ✓ Convergencia alcanzada en gen {gen}")
                break
            
            # Nueva generación
            self.poblacion = self._generar_nueva_generacion(
                self.poblacion, fitness_values
            )
        
        # 3. Refinamiento con búsqueda local
        print("🔍 Refinando solución con Hill Climbing...")
        self.mejor_individuo = self._hill_climbing_local(self.mejor_individuo)
        self.mejor_fitness = self.calcular_fitness(self.mejor_individuo)
        
        print(f"✅ Optimización completada")
        print(f"   Fitness final: ${self.mejor_fitness:,.0f}")
        
        info = {
            'generaciones_ejecutadas': len(self.fitness_historia),
            'fitness_historia': self.fitness_historia,
            'individuos_evaluados': len(self._fitness_cache),
            'hit_rate_cache': self._calcular_hit_rate_cache()
        }
        
        return self.mejor_individuo, self.mejor_fitness, info
