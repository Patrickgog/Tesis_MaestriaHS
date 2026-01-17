# 1. Definición y Estructuración de Parámetros Clave de la Aplicación

## Documento Técnico - Tesis de Maestría en Hidrosanitaria

### Resumen Ejecutivo

Este documento presenta la definición completa y estructuración de todos los parámetros de entrada y salida utilizados en la aplicación de diseño de sistemas de bombeo. La aplicación representa un avance significativo en la automatización del diseño hidráulico, integrando cálculos complejos, optimización mediante inteligencia artificial y una interfaz intuitiva.

---

## 1. PARÁMETROS DE ENTRADA (INPUT)

### 1.1 Parámetros del Proyecto

#### 1.1.1 Identificación del Proyecto
- **`proyecto` (string)**: Nombre identificador del proyecto
  - **Propósito**: Permite trazabilidad y gestión de múltiples diseños
  - **Formato**: Texto libre, máximo 100 caracteres
  - **Ejemplo**: "Sistema de Bombeo Urbanización Los Pinos"

- **`diseno` (string)**: Versión o variante del diseño
  - **Propósito**: Control de versiones dentro del mismo proyecto
  - **Formato**: Texto libre, máximo 50 caracteres
  - **Ejemplo**: "Diseño_Alternativa_A"

#### 1.1.2 Ubicación Geográfica
- **`elevacion_sitio` (float)**: Elevación sobre el nivel del mar [m.s.n.m]
  - **Rango válido**: 0 - 5000 m.s.n.m
  - **Propósito**: Cálculo de presión barométrica local
  - **Impacto**: Afecta NPSH disponible y cavitación
  - **Valor por defecto**: 450 m.s.n.m

### 1.2 Parámetros Hidráulicos Fundamentales

#### 1.2.1 Caudal
- **`caudal_lps` (float)**: Caudal de diseño [L/s]
  - **Rango válido**: 0.1 - 10000 L/s
  - **Propósito**: Caudal a transportar por el sistema
  - **Conversión automática**: El sistema convierte entre L/s y m³/h
  - **Fórmula conversión**: Q[m³/h] = Q[L/s] × 3.6

- **`caudal_m3h` (float)**: Caudal de diseño [m³/h]
  - **Rango válido**: 0.36 - 36000 m³/h
  - **Uso alternativo**: Disponible según preferencia del usuario

#### 1.2.2 Alturas y Presiones

**A. Altura de Succión**
- **`altura_succion_input` (float)**: Altura de succión [m]
  - **Signo**: Negativo para succión bajo nivel, positivo para bomba inundada
  - **Rango válido**: -10 a +20 m
  - **Impacto crítico**: Determina NPSH disponible

- **`bomba_inundada` (boolean)**: Indicador de instalación
  - **True**: Bomba por debajo del nivel de líquido (altura positiva)
  - **False**: Bomba por encima del nivel de líquido (altura negativa)

**B. Altura de Descarga**
- **`altura_descarga` (float)**: Altura estática de descarga [m]
  - **Definición**: Diferencia de elevación desde bomba hasta punto de descarga
  - **Rango válido**: 0 - 500 m
  - **Ejemplo**: Si la bomba está a cota 100 y descarga a cota 150, h = 50 m

#### 1.2.3 Configuración de Bombas
- **`num_bombas` (integer)**: Número de bombas en el sistema
  - **Opciones**: 1, 2, 3, o más
  - **Propósito**: Diseño por redundancia o aumento de capacidad
  - **Configuración típica**:
    - 1 bomba: Sistemas pequeños sin redundancia
    - 2 bombas: 1 operando + 1 stand-by
    - 3+ bombas: Operación escalonada por demanda variable

### 1.3 Parámetros de la Línea de Succión

#### 1.3.1 Geometría
- **`long_succion` (float)**: Longitud de tubería [m]
  - **Rango válido**: 0.5 - 100 m
  - **Incluye**: Longitud total desarrollada incluyendo accesorios

- **`diam_succion_mm` (float)**: Diámetro nominal [mm]
  - **Valores disponibles**: Diámetros comerciales estándar
  - **Serie típica**: 25, 32, 40, 50, 63, 75, 90, 110, 125, 160, 200, 250, 315, 400, 500, 630 mm
  - **Recomendación**: Velocidad 0.6 - 1.5 m/s para evitar cavitación

#### 1.3.2 Material y Rugosidad
- **`mat_succion` (string enum)**: Material de tubería
  - **Opciones disponibles**:
    - PVC: C = 150 (Hazen-Williams), ε = 0.0015 mm
    - HDPE: C = 150, ε = 0.0015 mm
    - Acero: C = 130, ε = 0.045 mm
    - Acero galvanizado: C = 120, ε = 0.15 mm
    - Hierro fundido: C = 110, ε = 0.25 mm
    - Hormigón: C = 120, ε = 0.3 mm

- **`coeficiente_hazen_succion` (float)**: Coeficiente C de Hazen-Williams
  - **Rango válido**: 80 - 150
  - **Asignación automática**: Según material seleccionado
  - **Ajuste manual**: Permitido para condiciones especiales

#### 1.3.3 Accesorios y Pérd

idas
- **`accesorios_succion` (JSON array)**: Lista de accesorios
  - **Estructura**: `[{"tipo": "codo_90", "cantidad": 3}, {"tipo": "valvula_compuerta", "cantidad": 1}]`
  - **Catálogo de accesorios con coeficientes K**:
    ```
    Codos 90°: K = 0.9
    Codos 45°: K = 0.4
    Codos 90° radio largo: K = 0.6
    Tees paso directo: K = 0.6
    Tees paso lateral: K = 1.5
    Válvula compuerta abierta: K = 0.2
    Válvula check: K = 2.5
    Válvula globo: K = 10.0
    Expansión gradual: K = 0.3
    Contracción gradual: K = 0.1
    Entrada brusca: K = 0.5
    Salida: K = 1.0
    ```

- **`otras_perdidas_succion` (float)**: Pérdidas adicionales manuales [m]
  - **Uso**: Pérdidas no contempladas en accesorios estándar
  - **Ejemplo**: Filtros, medidores de flujo especiales

### 1.4 Parámetros de la Línea de Impulsión

**Nota**: Estructura idéntica a la línea de succión, con parámetros específicos:

- **`long_impulsion`** (float): Longitud [m]
- **`diam_impulsion_mm`** (float): Diámetro [mm]
- **`mat_impulsion`** (string): Material
- **`coeficiente_hazen_impulsion`** (float): Coeficiente C
- **`accesorios_impulsion`** (JSON array): Lista de accesorios
- **`otras_perdidas_impulsion`** (float): Pérdidas adicionales [m]

**Consideraciones especiales para impulsión**:
- Velocidad recomendada: 1.0 - 2.5 m/s
- Mayor longitud típica que succión
- Mayores presiones de trabajo

### 1.5 Propiedades del Fluido

#### 1.5.1 Temperatura
- **`temp_liquido` (float)**: Temperatura del líquido [°C]
  - **Rango válido**: 0 - 100 °C
  - **Valor por defecto**: 20 °C
  - **Impacto**:
    - Viscosidad cinemática (para Darcy-Weisbach)
    - Presión de vapor (para NPSH)
    - Densidad del agua

#### 1.5.2 Densidad
- **`densidad_liquido` (float)**: Densidad relativa [g/cm³]
  - **Rango válido**: 0.5 - 2.0
  - **Valor por defecto**: 1.0 (agua pura)
  - **Ejemplos**:
    - Agua: 1.0
    - Agua de mar: 1.025
    - Soluciones salinas: 1.05 - 1.15

### 1.6 Parámetros de Curvas Características

#### 1.6.1 Modo de Ingreso
- **`curva_mode`** (string enum): Método de especificación de curvas
  - **"3 puntos"**: Ingreso manual de 3 puntos (Q, H)
  - **"Excel"**: Importación desde archivo externo
  - **Formatos aceptados**: .xlsx, .csv

#### 1.6.2 Tipo de Ajuste
- **`ajuste_tipo`** (string enum): Tipo de regresión para curvas
  - **"Lineal"**: y = mx + b
  - **"Cuadrática (2do grado)"**: H = a·Q² + b·Q + c (RECOMENDADO)
  - **"Polinomial (3er grado)"**: H = a·Q³ + b·Q² + c·Q + d

**Justificación del ajuste cuadrático**:
- Basado en ecuación de Euler: H ∝ Q²
- Mejor balance entre precisión y simplicidad
- Evita oscilaciones de polinomios de alto grado

#### 1.6.3 Curvas Requeridas

**A. Curva del Sistema**
- **`curva_sistema`** (array): Pares [Q, H_sistema]
  - **Mínimo 3 puntos** para ajuste cuadrático
  - **Representa**: Pérdidas totales vs caudal
  - **Formato**: `[[Q1, H1], [Q2, H2], [Q3, H3]]`

**B. Curva de la Bomba**
- **`curva_bomba`** (array): Pares [Q, H_bomba]
  - **Datos del fabricante**: Obligatorio
  - **Puntos críticos**: Shutoff, nominal, máximo

**C. Curva de Eficiencia**
- **`curva_eficiencia`** (array): Pares [Q, η%]
  - **Rango**: 0 - 100%
  - **Punto óptimo**: Máxima eficiencia

**D. Curva de Potencia**
- **`curva_potencia`** (array): Pares [Q, P_kW]
  - **Incluye**: Potencia al eje de la bomba

**E. Curva de NPSH Requerido**
- **`curva_npsh`** (array): Pares [Q, NPSH_req]
  - **Crítico para**: Prevención de cavitación

### 1.7 Parámetros de Variador de Frecuencia (VFD)

#### 1.7.1 Rangos de Operación
- **`rpm_percentage`** (array): Porcentajes de velocidad nominal
  - **Rango típico**: [40%, 50%, 60%, 70%, 80%, 90%, 100%]
  - **Restricción**: Generalmente no se opera bajo 40% RPM

#### 1.7.2 Leyes de Afinidad
Aplicadas automáticamente por el sistema:
- **Caudal**: Q₂ = Q₁ × (N₂/N₁)
- **Altura**: H₂ = H₁ × (N₂/N₁)²
- **Potencia**: P₂ = P₁ × (N₂/N₁)³

### 1.8 Método de Cálculo de Pérdidas

#### 1.8.1 Hazen-Williams (Empírico)
- **`metodo_calculo = "Hazen-Williams"`**
- **Ecuación**: hf = 10.674 × (Q/C)^1.852 × (D)^-4.87 × L
- **Ventajas**:
  - Simplicidad computacional
  - Amplia aceptación en ingeniería sanitaria
- **Limitaciones**:
  - Solo válido para agua a 5-25°C
  - No considera régimen de flujo explícitamente

#### 1.8.2 Darcy-Weisbach (Teórico)
- **`metodo_calculo = "Darcy-Weisbach"`**
- **Ecuación**: hf = f × (L/D) × (V²/2g)
- **Factor de fricción**: Calculado con ecuación de Swamee-Jain
- **Ventajas**:
  - Válido para cualquier fluido
  - Fundamentado teóricamente
  - Considera número de Reynolds y rugosidad relativa
- **Requisito**: Especificación de temperatura (para viscosidad)

---

## 2. PARÁMETROS DE SALIDA (OUTPUT)

### 2.1 Resultados Hidráulicos

#### 2.1.1 Pérdidas de Carga

**Línea de Succión**:
- **`hf_primaria_succion`** (float): Pérdidas por fricción [m]
  - **Calculadas con**: Hazen-Williams o Darcy-Weisbach
- **`hf_secundaria_succion`** (float): Pérdidas menores [m]
  - **Método**: Σ K × (V²/2g)
- **`perdida_total_succion`** (float): Pérdidas totales [m]
  - **Fórmula**: hf_primaria + hf_secundaria + otras

**Línea de Impulsión**:
- **`hf_primaria_impulsion`** (float)
- **`hf_secundaria_impulsion`** (float)
- **`perdida_total_impulsion`** (float)

#### 2.1.2 Velocidades
- **`velocidad_succion`** (float): [m/s]
  - **Cálculo**: V = Q / A = Q / (π × D²/4)
  - **Verificación**: 0.6 ≤ V ≤ 1.5 m/s (RECOMENDADO)

- **`velocidad_impulsion`** (float): [m/s]
  - **Verificación**: 1.0 ≤ V ≤ 2.5 m/s (RECOMENDADO)

#### 2.1.3 Altura Dinámica Total (TDH)
- **`altura_total_bomba`** (float): [m]
  - **Fórmula compleja**:
    ```
    TDH = h_descarga - h_succion + 
          hf_total_succion + hf_total_impulsion + 
          P_descarga/γ - P_succion/γ
    ```
  - **Representa**: Energía total que debe proporcionar la bomba

### 2.2 Análisis NPSH y Cavitación

#### 2.2.1 NPSH Disponible
- **`npsh_disponible`** (float): [m]
  - **Fórmula**:
    ```
    NPSH_d = P_barométrica/γ + h_succión - hf_succión - P_vapor/γ
    ```
  - **Componentes**:
    - P_barométrica: Función de elevación local
    - h_succión: Altura estática (+ si inundada)
    - hf_succión: Pérdidas totales en succión
    - P_vapor: Función de temperatura

#### 2.2.2 NPSH Requerido
- **`npsh_requerido`** (float): [m]
  - **Fuente**: Curva del fabricante interpolada al caudal de operación

#### 2.2.3 Margen de Seguridad
- **`npsh_margen`** (float): [m]
  - **Cálculo**: NPSH_d - NPSH_r
  - **Criterio de aceptación**:
    - Margen > 1.0 m: ACEPTABLE ✓
    - 0.5 < Margen ≤ 1.0 m: ADVERTENCIA ⚠
    - Margen ≤ 0.5 m: INACEPTABLE (RIESGO DE CAVITACIÓN) ✗

### 2.3 Punto de Operación

#### 2.3.1 Intersección de Curvas
- **`punto_operacion`** (object):
  ```json
  {
    "Q_operacion": float,  // Caudal en punto de operación [L/s]
    "H_operacion": float,  // Altura en punto de operación [m]
    "eficiencia": float,   // Eficiencia de la bomba [%]
    "potencia": float,     // Potencia consumida [kW]
    "npsh_req": float      // NPSH requerido [m]
  }
  ```

#### 2.3.2 Análisis de Desempeño
- **`eficiencia_operacion`** (float): [%]
  - **Evaluación**:
    - η > 70%: EXCELENTE
    - 60% < η ≤ 70%: BUENO
    - 50% < η ≤ 60%: ACEPTABLE
    - η ≤ 50%: DEFICIENTE (considerar otro modelo)

### 2.4 Selección de Bomba

#### 2.4.1 Información del Modelo
- **`bomba_nombre`** (string): Modelo seleccionado
- **`bomba_descripcion`** (string): Descripción técnica
- **`bomba_url`** (string): Enlace a ficha técnica del fabricante

#### 2.4.2 Especificaciones Eléctricas
- **`tension`** (float): Voltaje nominal [V]
  - **Opciones**: 220V, 380V, 440V, 660V
- **`rpm`** (float): Velocidad nominal [RPM]
  - **Estándar**: 1450, 1750, 2900, 3500 RPM
- **`motor_seleccionado`** (string): Potencia y tipo de motor

### 2.5 Optimización con Algoritmos Genéticos

#### 2.5.1 Parámetros de Entrada para GA
- **`diametros_disponibles`** (array): Diámetros comerciales a considerar
- **`poblacion_size`** (int): Tamaño de población (típico: 50-100)
- **`generaciones`** (int): Número de generaciones (típico: 100-200)
- **`probabilidad_mutacion`** (float): 0.01 - 0.1
- **`probabilidad_cruce`** (float): 0.6 - 0.9

#### 2.5.2 Resultados de Optimización
- **`diametro_optimo_succion`** (float): [mm]
- **`diametro_optimo_impulsion`** (float): [mm]
- **`costo_total_optimizado`** (float): [USD]
- **`fitness_value`** (float): Valor de la función objetivo
- **`generacion_convergencia`** (int): Generación donde se alcanzó el óptimo

### 2.6 Análisis de Transitorios (Módulo Avanzado)

#### 2.6.1 Configuración del Análisis
- **`tipo_transitorio`** (string): "cierre_valvula", "parada_bomba", "arranque_bomba"
- **`tiempo_maniobra`** (float): Duración del transitorio [s]
- **`paso_tiempo`** (float): Δt para integración numérica [s]

#### 2.6.2 Resultados
- **`presion_maxima`** (float): Presión máxima generada [m.c.a]
- **`presion_minima`** (float): Presión mínima [m.c.a]
- **`sobrepresion`** (float): ΔP = P_max - P_nominal
- **`riesgo_golpe_ariete`** (boolean): True si sobrepresión > 50% P_nominal

### 2.7 Visualizaciones Generadas

#### 2.7.1 Gráficas Estáticas
1. **Curvas del Sistema**:
   - Curva de la bomba al 100% RPM
   - Curva del sistema
   - Punto de operación
   - Curvas a diferentes RPM (si VFD)

2. **Curvas de Desempeño**:
   - Eficiencia vs Caudal
   - Potencia vs Caudal
   - NPSH vs Caudal

3. **Análisis de Diámetros**:
   - Pérdidas vs Diámetro
   - Velocidad vs Diámetro
   - Costo vs Diámetro

#### 2.7.2 Gráficas Interactivas (Plotly)
- Zoom, pan, y hover interactivo
- Exportación a PNG de alta resolución
- Comparación de escenarios

### 2.8 Reportes y Documentación

#### 2.8.1 Reporte Técnico (PDF)
Contenido generado automáticamente:
```
1. Datos del Proyecto
2. Especificaciones Técnicas
3. Memoria de Cálculo
4. Selección de Equipos
5. Gráficas de Desempeño
6. Recomendaciones Técnicas
7. Lista de Materiales (BOM)
8. Planos Esquemáticos
```

#### 2.8.2 Reporte de Resumen (JSON)
- **`proyecto_completo.json`**: Snapshot completo del proyecto
- **Uso**: Backup, trazabilidad, reproducibilidad
- **Formato**: Estructurado y versionado

### 2.9 Indicadores de Calidad del Diseño

#### 2.9.1 Semáforo de Validación
Sistema de alertas automáticas:

**🟢 VERDE - Diseño Óptimo**:
- Velocidades en rango ideal
- NPSH_margen > 1.5 m
- Eficiencia > 70%
- Sin advertencias

**🟡 AMARILLO - Advertencias**:
- Velocidad ligeramente fuera de rango
- 0.5 < NPSH_margen ≤ 1.0 m
- 60% < Eficiencia ≤ 70%
- Se recomienda revisión

**🔴 ROJO - Problemas Críticos**:
- Velocidad > 3 m/s o < 0.4 m/s
- NPSH_margen ≤ 0.5 m (RIESGO CAVITACIÓN)
- Eficiencia < 50%
- Diseño NO RECOMENDADO

#### 2.9.2 Índice de Eficiencia Energética (IEE)
- **Cálculo**: IEE = (η_bomba × η_motor) / (1 + factor_sobredimensionamiento)
- **Rango**: 0 - 1.0
- **Objetivo**: IEE > 0.65

---

## 3. FLUJO DE DATOS EN LA APLICACIÓN

### 3.1 Pipeline de Procesamiento

```
[ENTRADA USUARIO]
      ↓
[VALIDACIÓN DE DATOS]
      ↓
[CÁLCULOS HIDRÁULICOS]
      ↓
[ANÁLISIS NPSH]
      ↓
[INTERSECCIÓN DE CURVAS]
      ↓
[OPTIMIZACIÓN IA (opcional)]
      ↓
[GENERACIÓN VISUALIZACIONES]
      ↓
[REPORTES]
      ↓
[SALIDA/EXPORTACIÓN]
```

### 3.2 Gestión de Estado (Session State)

Streamlit mantiene persistencia de datos mediante `st.session_state`:

**Ventajas**:
- Navegación entre pestañas sin pérdida de datos
- Cálculos incrementales
- Undo/Redo implícito

**Claves principales**:
```python
session_state = {
    'proyecto': str,
    'caudal_lps': float,
    'curva_sistema': list,
    'resultados_calculados': dict,
    'punto_operacion': dict,
    # ... +50 parámetros más
}
```

---

## 4. VALIDACIÓN Y CONSTRAINTS

### 4.1 Reglas de Negocio Implementadas

1. **Velocidad en Succión**: 0.6 ≤ V ≤ 1.5 m/s
2. **Velocidad en Impulsión**: 1.0 ≤ V ≤ 2.5 m/s
3. **NPSH Margen Mínimo**: > 0.5 m
4. **Eficiencia Mínima Aceptable**: > 50%
5. **Rango de Temperatura**: 0 - 100 °C
6. **Número mínimo de puntos para ajuste**: 3

### 4.2 Manejo de Errores

**Validación en Tiempo Real**:
- Inputs numéricos con restricciones
- Mensajes de error descriptivos
- Sugerencias de corrección automáticas

---

## 5. CONCLUSIONES

La estructuración rigurosa de parámetros de entrada y salida en esta aplicación permite:

1. **Trazabilidad completa**: Desde inputs hasta resultados finales
2. **Reproducibilidad**: Proyectos guardados pueden recalcularse idénticamente
3. **Automatización**: Minimiza errores humanos en cálculos complejos
4. **Optimización**: IA encuentra soluciones óptimas que un diseñador podría pasar por alto
5. **Cumplimiento normativo**: Validaciones automáticas según mejores prácticas

Este enfoque sistemático representa un avance significativo sobre métodos tradicionales de diseño manual, reduciendo el tiempo de diseño de días a minutos, mientras mejora la calidad y optimización del resultado final.

---

**Autor**: Sistema Experto en Diseño de Sistemas de Bombeo  
**Versión del Documento**: 1.0  
**Fecha**: Enero 2026  
**Aplicación**: Tesis de Maestría en Hidrosanitaria
