# Teoría y Fundamentos de Sistemas de Bombeo

**Documento Técnico Profesional**  
**Aplicación de Análisis y Diseño de Sistemas de Bombeo**

---

## Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Fundamentos de Mecánica de Fluidos](#2-fundamentos-de-mecánica-de-fluidos)
3. [Flujo en Tuberías](#3-flujo-en-tuberías)
4. [Pérdidas de Carga](#4-pérdidas-de-carga)
5. [Fundamentos de Bombas Centrífugas](#5-fundamentos-de-bombas-centrífugas)
6. [Curvas Características de Bombas](#6-curvas-características-de-bombas)
7. [Punto de Operación del Sistema](#7-punto-de-operación-del-sistema)
8. [Selección Técnica y Económica de Diámetros](#8-selección-técnica-y-económica-de-diámetros)
9. [Cavitación y NPSH](#9-cavitación-y-npsh)
10. [Variadores de Frecuencia (VFD)](#10-variadores-de-frecuencia-vfd)
11. [Transitorios Hidráulicos](#11-transitorios-hidráulicos)
12. [Análisis de Costos y Optimización](#12-análisis-de-costos-y-optimización)
13. [Referencias](#13-referencias)

---

## 1. Introducción

Los sistemas de bombeo son componentes esenciales en proyectos de ingeniería hidrosanitaria, responsables del transporte de agua desde fuentes de abastecimiento hasta puntos de consumo o almacenamiento. El diseño adecuado de estos sistemas requiere un profundo conocimiento de mecánica de fluidos, hidráulica de tuberías, características de equipos de bombeo y análisis económico.

### 1.1 Objetivos del Documento

Este documento presenta los fundamentos teóricos y metodologías de cálculo implementados en la aplicación de análisis y diseño de sistemas de bombeo, cubriendo:

- Principios fundamentales de hidráulica aplicada
- Métodos de cálculo de pérdidas de carga
- Análisis de curvas características de bombas
- Selección técnica y económica de componentes
- Evaluación de fenómenos transitorios
- Optimización de sistemas de bombeo

### 1.2 Alcance de la Aplicación

La aplicación desarrollada implementa metodologías rigurosas para:

1. **Cálculo hidráulico**: Métodos Hazen-Williams y Darcy-Weisbach
2. **Análisis de bombas**: Curvas características, punto de operación, BEP
3. **Selección de diámetros**: Análisis técnico-económico de tuberías
4. **Evaluación de NPSH**: Prevención de cavitación en succión
5. **VFD**: Análisis con variadores de frecuencia
6. **Transitorios**: Golpe de ariete y protecciones

---

## 2. Fundamentos de Mecánica de Fluidos

### 2.1 Propiedades de los Fluidos

#### 2.1.1 Densidad

La densidad del agua varía con la temperatura. Para condiciones estándar (20°C):

```
ρ = 998.2 kg/m³
```

El peso específico se relaciona con la densidad mediante:

```
γ = ρ · g
```

Donde:
- γ = Peso específico (N/m³)
- ρ = Densidad (kg/m³)  
- g = 9.81 m/s² (aceleración gravitacional)

Para agua a 20°C: γ ≈ 9,790 N/m³

#### 2.1.2 Viscosidad Dinámica y Cinemática

La viscosidad caracteriza la resistencia interna del fluido al flujo. La **viscosidad dinámica** (μ) y la **viscosidad cinemática** (ν) se relacionan:

```
ν = μ / ρ
```

**Tabla 1: Viscosidad cinemática del agua según temperatura**

| Temperatura (°C) | Viscosidad (m²/s) |
|------------------|-------------------|
| 0                | 1.787 × 10⁻⁶     |
| 10               | 1.307 × 10⁻⁶     |
| 20               | 1.004 × 10⁻⁶     |
| 30               | 0.801 × 10⁻⁶     |
| 40               | 0.658 × 10⁻⁶     |
| 50               | 0.553 × 10⁻⁶     |
| 60               | 0.475 × 10⁻⁶     |
| 70               | 0.413 × 10⁻⁶     |
| 80               | 0.365 × 10⁻⁶     |
| 90               | 0.326 × 10⁻⁶     |
| 100              | 0.294 × 10⁻⁶     |

La aplicación utiliza interpolación lineal para temperaturas intermedias.

### 2.2 Ecuación de Continuidad

Para flujo incompresible en régimen permanente:

```
Q = A · V = constante
```

Donde:
- Q = Caudal (m³/s)
- A = Área transversal (m²)
- V = Velocidad media (m/s)

Para tuberías circulares:

```
A = π · D² / 4
V = 4Q / (π · D²)
```

Donde D es el diámetro interno de la tubería (m).

### 2.3 Ecuación de Bernoulli

Para flujo ideal (sin fricción) entre dos puntos de una línea de corriente:

```
z₁ + (P₁/γ) + (V₁²/2g) = z₂ + (P₂/γ) + (V₂²/2g)
```

Donde:
- z = Elevación (m)
- P/γ = Altura de presión (m)
- V²/2g = Altura de velocidad (m)

### 2.4 Ecuación de Energía

Para flujo real, incorporando pérdidas:

```
z₁ + (P₁/γ) + (V₁²/2g) = z₂ + (P₂/γ) + (V₂²/2g) + hf + hm
```

Donde:
- hf = Pérdidas por fricción (m)
- hm = Pérdidas menores o singulares (m)

---

## 3. Flujo en Tuberías

### 3.1 Número de Reynolds

El número de Reynolds determina el régimen de flujo:

```
Re = (V · D) / ν = (4Q) / (π · D · ν)
```

**Clasificación del régimen:**

| Régimen      | Rango de Re |
|--------------|-------------|
| Laminar      | Re < 2,000  |
| Transición   | 2,000 ≤ Re ≤ 4,000 |
| Turbulento   | Re > 4,000  |

En sistemas de agua potable y alcantarillado, el flujo es típicamente turbulento.

### 3.2 Rugosidad Absoluta

La rugosidad absoluta (ε) caracteriza la aspereza interna de la tubería:

**Tabla 2: Rugosidad absoluta según material**

| Material              | ε (mm)     | ε (m)        |
|-----------------------|------------|--------------|
| PVC                   | 0.0015     | 1.5 × 10⁻⁶  |
| PEAD                  | 0.007      | 7.0 × 10⁻⁶  |
| Hierro fundido nuevo  | 0.26       | 2.6 × 10⁻⁴  |
| Hierro fundido usado  | 1.5 - 3.0  | 1.5-3.0×10⁻³|
| Hierro dúctil nuevo   | 0.12       | 1.2 × 10⁻⁴  |
| Acero nuevo           | 0.046      | 4.6 × 10⁻⁵  |
| Acero comercial       | 0.15       | 1.5 × 10⁻⁴  |
| Concreto liso         | 0.3        | 3.0 × 10⁻⁴  |

### 3.3 Rugosidad Relativa

```
ε/D = Rugosidad absoluta / Diámetro interno
```

Este parámetro adimensional es fundamental en el cálculo del factor de fricción.

---

## 4. Pérdidas de Carga

Las pérdidas de energía en tuberías se clasifican en:

1. **Pérdidas primarias o por fricción** (hf)
2. **Pérdidas secundarias o singulares** (hm)

### 4.1 Método de Hazen-Williams

Ecuación empírica ampliamente utilizada en diseño de acueductos:

```
hf = 10.674 · L · Q^1.852 / (C^1.852 · D^4.87)
```

Donde:
- hf = Pérdida por fricción (m)
- L = Longitud de tubería (m)
- Q = Caudal (m³/s)
- C = Coeficiente de Hazen-Williams
- D = Diámetro interno (m)

**Tabla 3: Coeficiente C de Hazen-Williams**

| Material/Condición           | C    | Observaciones                    |
|------------------------------|------|----------------------------------|
| Acero soldado nuevo          | 140  | Sin incrustaciones               |
| Acero soldado usado          | 100  | Con incrustaciones moderadas     |
| Hierro fundido nuevo         | 130  | Revestimiento interior           |
| Hierro fundido usado         | 100  | 10-15 años de servicio           |
| Hierro dúctil                | 140  | Con revestimiento                |
| PVC                          | 150  | Liso, no se degrada              |
| PEAD                         | 150  | Liso, resistente                 |
| Hormigón liso                | 130  | Bien terminado                   |
| Hormigón bruto               | 120  | Acabado rugoso                   |
| Asbesto-cemento              | 140  | Superficie lisa                  |

**Limitaciones:**
- Válido solo para agua (ρ ≈ 1000 kg/m³)
- Temperatura entre 5°C y 25°C
- Diámetros > 50 mm
- Velocidades < 3 m/s
- No considera explícitamente viscosidad ni régimen

**Forma alternativa (gradiente hidráulico):**

```
J = hf/L = 10.674 · Q^1.852 / (C^1.852 · D^4.87)
```

**Despeje para velocidad:**

```
V = 0.849 · C · R^0.63 · J^0.54
```

Donde R es el radio hidráulico (para tubería llena: R = D/4).

### 4.2 Método de Darcy-Weisbach

Ecuación universal aplicable a cualquier fluido, régimen y tubería:

```
hf = f · (L/D) · (V²/2g)
```

Donde:
- f = Factor de fricción de Darcy (adimensional)
- L = Longitud de tubería (m)
- D = Diámetro interno (m)
- V = Velocidad media (m/s)
- g = 9.81 m/s²

**Ventajas:**
- Base teórica sólida
- Aplicable a cualquier fluido
- Considera viscosidad y régimen explícitamente
- Válido para todos los diámetros y velocidades

#### 4.2.1 Factor de Fricción para Flujo Laminar

Para Re < 2000:

```
f = 64 / Re
```

Esta ecuación es exacta y deriva analíticamente de la ecuación de Navier-Stokes.

#### 4.2.2 Factor de Fricción para Flujo Turbulento

**Ecuación de Colebrook-White** (implícita):

```
1/√f = -2 · log₁₀[(ε/D)/3.71 + 2.51/(Re·√f)]
```

Esta ecuación requiere solución iterativa. La aplicación utiliza la **ecuación de Swamee-Jain** (explícita):

```
f = 0.25 / [log₁₀((ε/D)/3.7 + 5.74/Re^0.9)]²
```

**Rango de validez:**
- 4,000 < Re < 10⁸
- 10⁻⁶ < ε/D < 10⁻²

**Error:** < 1% respecto a Colebrook-White

#### 4.2.3 Diagrama de Moody

Representación gráfica del factor de fricción f en función de Re y ε/D. Herramienta visual fundamental en hidráulica de tuberías.

### 4.3 Pérdidas Singulares o Menores

Producidas por accesorios, válvulas, cambios de sección, etc.:

```
hm = K · (V²/2g)
```

Donde K es el coeficiente de pérdida singular (adimensional).

**Tabla 4: Coeficientes de Pérdidas Singulares**

| Accesorio                    | K      | Observaciones                     |
|------------------------------|--------|-----------------------------------|
| Entrada brusca               | 0.50   | De depósito a tubería             |
| Entrada abocinada            | 0.04   | Transición suave                  |
| Salida de tubería            | 1.00   | A depósito                        |
| Codo 90° radio corto         | 0.90   | r/D ≈ 1                          |
| Codo 90° radio largo         | 0.60   | r/D ≈ 1.5                        |
| Codo 45°                     | 0.40   |                                   |
| Te paso directo              | 0.60   |                                   |
| Te derivación 90°            | 1.80   |                                   |
| Válvula compuerta abierta    | 0.15   | Totalmente abierta                |
| Válvula globo abierta        | 10.0   | Totalmente abierta                |
| Válvula check                | 2.50   | Tipo columpio                     |
| Válvula mariposa             | 0.40   | Ángulo 0°                         |
| Reducción brusca             | 0.50   | Depende de relación D₁/D₂         |
| Ampliación brusca            | 1.00   | (1 - A₁/A₂)²                     |

#### 4.3.1 Método de Longitud Equivalente

Expresa las pérdidas singulares como longitud adicional de tubería:

```
Le = K · D / f
```

Donde Le/D es la relación longitud equivalente/diámetro propia de cada accesorio.

### 4.4 Pérdidas Totales del Sistema

```
hT = hf_succión + hf_impulsión + hm_succión + hm_impulsión
```

---

## 5. Fundamentos de Bombas Centrífugas

Las bombas centrífugas son las más empleadas en sistemas de agua potable y alcantarillado por su:
- Versatilidad operativa
- Alta eficiencia
- Bajo mantenimiento
- Costo razonable

### 5.1 Principio de Funcionamiento

La bomba centrífuga convierte energía mecánica en energía hidráulica mediante:

1. **Entrada axial**: El fluido ingresa paralelo al eje del impulsor
2. **Aceleración centrífuga**: El impulsor rotatorio imparte energía cinética
3. **Conversión de energía**: La voluta convierte velocidad en presión
4. **Descarga radial**: El fluido sale con alta presión

### 5.2 Componentes Principales

1. **Impulsor**: Elemento rotatorio con álabes que imparte energía
2. **Voluta o difusor**: Envolvente que convierte velocidad en presión
3. **Eje**: Transmite torque del motor al impulsor
4. **Carcasa**: Contiene el conjunto hidráulico
5. **Sellos mecánicos**: Previenen fugas en el eje

### 5.3 Clasificación

**Por posición del eje:**
- Horizontales (más comunes)
- Verticales (sumergibles, turbina)

**Por número de impulsores:**
- Etapa simple
- Múltiples etapas

**Por diseño del impulsor:**
- Flujo radial
- Flujo mixto
- Flujo axial

### 5.4 Altura Total de Bombeo (H)

Energía por unidad de peso que suministra la bomba:

```
H = (P₂ - P₁)/γ + (z₂ - z₁) + (V₂² - V₁²)/2g
```

En la práctica:

```
H = Altura estática + Pérdidas totales
H = He + hf + hm
```

**Componentes:**

1. **Altura estática (He)**: Diferencia de elevación entre niveles
2. **Pérdidas por fricción (hf)**: En tuberías de succión e impulsión
3. **Pérdidas menores (hm)**: En accesorios y válvulas

### 5.5 Potencia Hidráulica

Potencia transferida al fluido:

```
Ph = γ · Q · H = 9.81 · Q · H  [kW]
```

Donde:
- Ph = Potencia hidráulica (kW)
- γ = 9,810 N/m³ (peso específico del agua)
- Q = Caudal (m³/s)
- H = Altura total (m)

### 5.6 Eficiencia de la Bomba

La eficiencia total de la bomba (η) relaciona potencia hidráulica con potencia al freno:

```
η = Ph / Pb
```

Donde:
- Pb = Potencia al freno o en el eje (kW)

Despejando:

```
Pb = Ph / η = (γ · Q · H) / η
```

**Eficiencias típicas:**
- Bombas pequeñas (< 10 HP): 50-70%
- Bombas medianas (10-100 HP): 70-85%
- Bombas grandes (> 100 HP): 85-92%

### 5.7 Potencia del Motor

La potencia del motor debe considerar factor de seguridad:

```
Pm = Pb · F.S. = (γ · Q · H · F.S.) / η
```

**Factor de seguridad típico:**
- 10-15% adicional (F.S. = 1.10 a 1.15)

---

## 6. Curvas Características de Bombas

Las curvas características describen el comportamiento hidráulico y energético de una bomba centrífuga operando a velocidad constante.

### 6.1 Curva Q-H (Caudal-Altura)

Relaciona el caudal bombeado con la altura desarrollada. Es la curva fundamental para el diseño.

**Forma matemática típica:**

```
H = a₀ + a₁·Q + a₂·Q²
```

Donde a₀, a₁, a₂ son coeficientes de ajuste polinomial.

**Características:**
- Forma típicamente descendente (H disminuye al aumentar Q)
- **Shutoff head** (Q = 0): Altura máxima con válvula cerrada
- **Free delivery** (H = 0): Caudal máximo teórico
- Punto de diseño: intersección con curva del sistema

**Forma de la curva:**
- **Curva plana**: Pequeña variación de H con Q (bombas de bajo Ns)
- **Curva empinada**: Gran variación de H con Q (bombas de alto Ns)

**Ajuste polinomial:**
La aplicación utiliza regresión por mínimos cuadrados (grado 2) para modelar datos experimentales del fabricante.

### 6.2 Curva Q-η (Caudal-Eficiencia)

Muestra cómo varía la eficiencia hidráulica con el caudal:

```
η = b₀ + b₁·Q + b₂·Q²  
```

**Características:**
- Forma parabólica con un máximo definido
- Eficiencia nula o muy baja en Q = 0 (toda la energía se disipa)
- Máximo en el BEP (Best Efficiency Point)
- Descenso a ambos lados del BEP

### 6.3 Best Efficiency Point (BEP)

El BEP es el punto de operación óptimo de la bomba donde se alcanza la máxima eficiencia.

**Cálculo matemático:**

Para un polinomio de segundo grado η(Q) = b₀ + b₁·Q + b₂·Q²:

```
dη/dQ = 0  →  b₁ + 2·b₂·Q = 0

Q_BEP = -b₁ / (2·b₂)
η_max = η(Q_BEP) = b₀ + b₁·Q_BEP + b₂·Q_BEP²
```

**Importancia operativa del BEP:**

1. **Eficiencia energética**: Máximo rendimiento, mínimo consumo
2. **Desgaste mecánico**: Mínimas vibraciones y esfuerzos
3. **Generación de calor**: Mínima temperatura de operación
4. **Estabilidad operativa**: Flujo estable sin recirculación
5. **Vida útil**: Máxima duración de componentes

**Velocidad específica (Ns):**

Caracteriza la geometría del impulsor en el BEP:

```
Ns = (N · √Q) / H^0.75
```

Donde:
- N = Velocidad rotacional (RPM)
- Q = Caudal en el BEP (GPM o m³/s)
- H = Altura en el BEP (ft o m)

### 6.4 Zona de Operación Recomendada

**Rango preferido:**

```
 0.70·Q_BEP ≤ Q_operación ≤ 1.10·Q_BEP
```

**Rango aceptable:**

```
0.65·Q_BEP ≤ Q_operación ≤ 1.15·Q_BEP
```

**Fuera de la zona recomendada:**

| Condición          | Problemas Asociados                                    |
|--------------------|--------------------------------------------------------|
| Q << Q_BEP         | Recirculación interna, sobrecalentamiento, vibración  |
| Q >> Q_BEP         | Cavitación, sobrecarga del motor, baja eficiencia     |

### 6.5 Curva Q-P (Caudal-Potencia)

Muestra la potencia al freno requerida en función del caudal:

```
P = (γ · Q · H(Q)) / η(Q)
```

**Tipos de curvas:**

1. **No-overloading**: P alcanza máximo antes de Q_máx (diseño preferido)
2. **Overloading**: P aumenta continuamente con Q (riesgo de sobrecarga)

### 6.6 Curva Q-NPSH_req (Caudal-NPSH Requerido)

Indica el Net Positive Suction Head requerido por la bomba:

```
NPSH_req = c₀ + c₁·Q + c₂·Q²
```

**Comportamiento típico:**
- Aumenta gradualmente con el caudal
- Incremento acelerado a altos caudales (> 1.2·Q_BEP)
- Crítico para prevención de cavitación

### 6.7 Leyes de Afinidad (Affinity Laws)

Permiten predecir desempeño a diferentes velocidades:

**Primera ley (caudal):**
```
Q₂/Q₁ = N₂/N₁
```

**Segunda ley (altura):**
```
H₂/H₁ = (N₂/N₁)²
```

**Tercera ley (potencia):**
```
P₂/P₁ = (N₂/N₁)³
```

Donde:
- N = Velocidad de rotación (RPM)
- Subíndices 1 y 2 indican condiciones inicial y final

**Aplicación:** Fundamental para análisis con variadores de frecuencia (VFD).

---

## 7. Punto de Operación del Sistema

El punto de operación es la intersección entre la curva característica de la bomba y la curva del sistema.

### 7.1 Curva del Sistema

Representa la energía requerida para transportar un caudal Q:

```
H_sistema(Q) = He + K·Q²
```

Donde:
- He = Altura estática total (constante)
- K = Coeficiente que agrupa pérdidas de fricción y singulares

**Desglose del coeficiente K:**

```
K = (f_suc·L_suc)/(2·g·D_suc⁵·π²/16) + (f_imp·L_imp)/(2·g·D_imp⁵·π²/16) + Σ(K_i/(2·g·A_i²))
```

### 7.2 Determinación del Punto de Operación

**Método gráfico:**
Intersección visual de ambas curvas en gráfica Q-H.

**Método analítico:**
Resolver ecuación:

```
H_bomba(Q) = H_sistema(Q)
a₀ + a₁·Q + a₂·Q² = He + K·Q²
```

Simplificando:

```
(a₂ - K)·Q² + a₁·Q + (a₀ - He) = 0
```

Solución por fórmula cuadrática:

```
Q_op = [-a₁ + √(a₁² - 4·(a₂-K)·(a₀-He))] / [2·(a₂-K)]
```

Una vez determinado Q_op:

```
H_op = He + K·Q_op²
η_op = η(Q_op)
P_op = (γ·Q_op·H_op)/η_op
```

### 7.3 Rango de Operación del Sistema

Si el sistema tiene demanda variable (Q_mín a Q_máx), se debe verificar:

1. Todos los puntos de operación caen en zona eficiente de la bomba
2. NPSHdisp > NPSHreq en todo el rango
3. Potencia no excede capacidad del motor

**Ajuste mediante regulación:**
- Válvula de control (ineficiente, aumenta pérdidas)
- VFD (eficiente, reduce velocidad)
- Bypass (muy ineficiente, solo emergencias)

---

## 8. Selección Técnica y Económica de Diámetros

La aplicación implementa análisis riguroso para determinar el diámetro óptimo de tuberías considerando:

### 8.1 Criterios Técnicos

#### 8.1.1 Velocidad del Flujo

**Rango recomendado para líneas de conducción:**
```
0.6 m/s ≤ V ≤ 3.0 m/s
```

**Razones:**
- V < 0.6 m/s: Sedimentación, estancamiento
- V > 3.0 m/s: Erosión, ruido, golpe de ariete severo

**Para succión de bombas:**
```
V_succión ≤ 2.0 m/s  (recomendado: 1.0-1.8 m/s)
```

**Para impulsión de bombas:**
```
V_impulsión ≤ 3.0 m/s  (recomendado: 1.5-2.5 m/s)
```

#### 8.1.2 Gradiente Hidráulico

**Pérdida unitaria máxima recommended:**
```
J = hf/L ≤ 0.010 m/m  (1% pendiente energética)
```

Para líneas largas:
```
J ≤ 0.005 m/m  (0.5%)
```

#### 8.1.3 Presión Disponible

Se debe verificar:
```
P_mín ≥ 10 m.c.a. (presión mínima de servicio)
P_máx ≤ P_trabajo_tubería / 1.5
```

### 8.2 NPSH Disponible (Línea de Succión)

**Cálculo fundamental:**

```
NPSHdisp = (P_atm/γ) + h_s - hf_s - hm_s - (P_v/γ)
```

Donde:
- P_atm/γ = Presión atmosférica (función de elevación)
- h_s = Altura estática de succión (+ si sobre bomba, - si bajo bomba)
- hf_s = Pérdidas por fricción en succión
- hm_s = Pérdidas singulares en succión  
- P_v/γ = Presión de vapor del agua (función de temperatura)

**Criterio de seguridad:**

```
NPSHdisp ≥ NPSHreq + Margen_seguridad
```

Margen típico: 0.5 - 1.0 m

**Presión atmosférica según elevación:**

```
P_atm(z) = 10.33 · e^(-z/10000)  [m.c.a.]
```

Aproximación simplificada:
```
P_atm(z) ≈ 10.33 - 0.001·z  [m.c.a.]
```

### 8.3 Criterios Económicos

#### 8.3.1 Costo de Tubería

Función del diámetro y material:

```
C_tubería = c₀ · D^α · L
```

Donde:
- c₀ = Costo base unitario
- α = Exponente típico 1.5 - 2.0
- L = Longitud

#### 8.3.2 Costo de Energía (Valor Presente)

```
C_energía = (P · t · Ce · FP) / i
```

Donde:
- P = Potencia consumida (kW)
- t = Horas de operación anual
- Ce = Costo unitario energía ($/kWh)
- FP = Factor de planta (típico 0.85-0.95)
- i = Tasa de descuento

**Potencia proporcional a pérdidas:**

```
P ∝ Q · hf ∝ Q³/D⁵  (Hazen-Williams)
P ∝ Q · hf ∝ Q³/D⁵  (Darcy-Weisbach, flujo turbulento rugoso)
```

#### 8.3.3 Diámetro Económico

Minimizar función de costo total:

```
CT(D) = C_tubería(D) + C_energía(D) + C_operación(D)
```

**Condición de óptimo:**

```
dCT/dD = 0
```

Genera la **fórmula de Bresse** (simplificada):

```
D_económico = k · √Q
```

Donde k varía de 0.9 a 1.4 según condiciones económicas locales.

### 8.4 Metodología de la Aplicación

La aplicación implementa:

1. **Generación de alternativas**: Diámetros comerciales en rango factible
2. **Análisis hidráulico**: Velocidad, pérdidas, NPSH para cada alternativa
3. **Análisis económico**: Costos de inversión y operación actualizados
4. **Ranking multicriterio**: Ponderación técnica-económica
5. **Recomendación**: Diámetro óptimo con justificación

**Salidas:**
- Tabla comparativa de alternativas
- Gráficos: Costo vs Diámetro, Pérdidas vs Diámetro
- Análisis de sensibilidad
- Diagnóstico técnico detallado

---

## 9. Cavitación y NPSH

La cavitación es uno de los fenómenos más destructivos en sistemas de bombeo.

### 9.1 Física de la Cavitación

**Secuencia del fenómeno:**

1. **Formación de burbujas**: Presión local cae bajo presión de vapor
2. **Crecimiento**: Burbujas crecen en zona de baja presión
3. **Colapso violento**: Burbujas implosionan al entrar a zona de alta presión
4. **Daño por microchorro**: Erosión del material (pitting)

**Presión de vapor del agua:**

| Temperatura (°C) | P_v (kPa) | P_v/γ (m.c.a.) |
|------------------|-----------|----------------|
| 0                | 0.61      | 0.06           |
| 10               | 1.23      | 0.13           |
| 20               | 2.34      | 0.24           |
| 30               | 4.25      | 0.43           |
| 40               | 7.38      | 0.75           |
| 50               | 12.35     | 1.26           |
| 60               | 19.94     | 2.03           |

### 9.2 Net Positive Suction Head (NPSH)

#### 9.2.1 NPSH Disponible

Energía total disponible en la brida de succión de la bomba por encima de la presión de vapor:

```
NPSHdisp = (P_atm/γ) ± h_s - hf_s - hm_s - (P_v/γ)
```

Signos:
- (+) si nivel de succión está sobre la bomba (succión positiva)
- (-) si nivel está bajo la bomba (succión negativa o cebado)

#### 9.2.2 NPSH Requerido

Energía mínima necesaria en succión para evitar cavitación. Es una característica de la bomba proporcionada por el fabricante.

**Variación con caudal:**
```
NPSHreq aumenta con Q (típicamente proporcional a Q²)
```

### 9.3 Criterio de No-Cavitación

```
NPSHdisp > NPSHreq + Margen_seguridad
```

**Margenes recomendados:**

| Aplicación                  | Margen     |
|-----------------------------|------------|
| Agua fría, servicio continuo| 0.5 - 1.0 m|
| Agua caliente               | 1.0 - 1.5 m|
| Servicio crítico            | 1.5 - 2.0 m|
| Hidrocarburos               | 2.0 - 3.0 m|

### 9.4 Efectos de la Cavitación

**Daños mecánicos:**
- Erosión de impulsores (pitting)
- Desgaste de sellos y cojinetes
- Fatiga de materiales

**Efectos operativos:**
- Caída de caudal y altura
- Pérdida de eficiencia
- Vibraciones severas
- Ruido característico (grava)

**Consecuencias económicas:**
- Paradas no programadas
- Reemplazo prematuro de componentes
- Pérdida de producción
- Costos de mantenimiento elevados

### 9.5 Prevención de Cavitación

**Opciones de diseño:**

1. **Aumentar NPSHdisp:**
   - Reducir altura de succión (bajar bomba)
   - Minimizar longitud y pérdidas en succión
   - Aumentar diámetro de tubería de succión
   - Usar temperatura más baja
   - Presurizar el tanque de succión

2. **Reducir NPSHreq:**
   - Seleccionar bomba con menor NPSHreq
   - Operar a menor caudal
   - Usar inductor (booster)

3. **Diseño especial:**
   - Bomba de doble succión
   - Impulsores especiales anti-cavitación

---

## 10. Variadores de Frecuencia (VFD)

Los variadores de frecuencia permiten control eficiente del caudal mediante variación de la velocidad de la bomba.

### 10.1 Principio de Operación

El VFD ajusta la frecuencia de alimentación eléctrica al motor:

```
N ∝ f
```

Donde:
- N = Velocidad del motor (RPM)
- f = Frecuencia eléctrica (Hz)

**Ejemplo:**
- 60 Hz → 100% velocidad
- 45 Hz → 75% velocidad  
- 30 Hz → 50% velocidad

### 10.2 Leyes de Afinidad con VFD

Al cambiar la velocidad de N₁ a N₂:

**Caudal:**
```
Q₂ = Q₁ · (N₂/N₁) = Q₁ · (f₂/f₁)
```

**Altura:**
```
H₂ = H₁ · (N₂/N₁)² = H₁ · (f₂/f₁)²
```

**Potencia:**
```
P₂ = P₁ · (N₂/N₁)³ = P₁ · (f₂/f₁)³
```

### 10.3 Curvas con VFD

La aplicación genera curvas ajustadas para diferentes velocidades:

Para N = α · N₁₀₀% (donde α = porcentaje/100):

```
Q_vfd(α) = α · Q₁₀₀%
H_vfd(α) = α² · H₁₀₀%
P_vfd(α) = α³ · P₁₀₀%
η_vfd(α) ≈ η₁₀₀%  (eficiencia relativamente constante)
```

### 10.4 Punto de Operación con VFD

El nuevo punto de operación se encuentra en la intersección de:
- Curva de bomba ajustada (a velocidad reducida)
- Curva del sistema (no cambia)

**Ventaja energética:**

Para alcanzar Q₂ < Q₁:
- **Con válvula**: Se aumentan pérdidas, P se reduce poco
- **Con VFD**: Se reduce drásticamente P ∝ Q³

**Ahorro de energía:**

```
Ahorro% = [1 - (Q₂/Q₁)³] × 100
```

**Ejemplo:**
- Reducción a 75% caudal → Ahorro ≈ 58%
- Reducción a 50% caudal → Ahorro ≈ 88%

### 10.5 Consideraciones Técnicas

**Ventajas:**
- Ahorro energético significativo
- Control preciso de caudal
- Arranque suave (reduce golpe de ariete)
- Menor desgaste mecánico

**Limitaciones:**
- Frecuencia mínima práctica: 30-35 Hz
- Afectación de ventilación a bajas velocidades
- Aumento de armónicos en red eléctrica
- Costo inicial mayor

**Aplicaciones ideales:**
- Demanda variable
- Operación continua
- Altos costos de energía
- Sistemas con alta componente estática

---

## 11. Transitorios Hidráulicos

Los transitorios hidráulicos (golpe de ariete) son cambios bruscos de presión causados por variaciones rápidas de velocidad.

### 11.1 Fenómeno Físico

**Causas:**
- Cierre/apertura rápida de válvulas
- Paro súbito de bombas (falla eléctrica)
- Arranque rápido de bombas

**Secuencia:**
1. Reducción súbita de velocidad
2. Conversión de energía cinética en presión
3. Propagación de onda de presión
4. Reflexión en extremos
5. Oscilación amortiguada

### 11.2 Ecuaciones Fundamentales

**Celeridad de la onda:**

Fórmula de Joukowsky modificada:

```
a = √[K/(ρ·(1 + (K·D)/(E·e)))]
```

Donde:
- K = Módulo de compresibilidad del agua (≈ 2.1 × 10⁹ Pa)
- ρ = Densidad del agua
- D = Diámetro interno tubería
- E = Módulo de elasticidad del material tubería
- e = Espesor de pared

**Valores típicos de celeridad:**

| Material Tubería | a (m/s)  |
|------------------|----------|
| Acero            | 1000-1200|
| Hierro dúctil    | 1000-1150|
| PVC              | 350-450  |
| PEAD             | 250-350  |

**Sobrepresión (fórmula de Allievi):**

Para cierre instantáneo:

```
ΔH = (a · ΔV) / g
```

Donde:
- ΔH = Sobrepresión (m.c.a.)
- ΔV = Cambio de velocidad (m/s)
- g = 9.81 m/s²

**Ejemplo:**
- V₀ = 2 m/s, a = 1000 m/s
- ΔH = (1000 × 2) / 9.81 ≈ 204 m.c.a.  ¡Enorme!

### 11.3 Tiempo de Cierre Crítico

```
T_crítico = 2L / a
```

Donde L es la longitud de la tubería.

- Si T_cierre < T_crítico → Cierre rápido (sobrepresión máxima)
- Si T_cierre > T_crítico → Cierre lento (sobrepresión reducida)

### 11.4 Dispositivos de Protección

**1. Válvulas de alivio:**
- Se abren a presión predeterminada
- Descargan flujo temporal
- Económicas pero ineficientes (energía)

**2. Tanques hidroneumáticos:**
- Absorben y amortiguan ondas de presión
- Proveen caudal instantáneo
- Efectivos para sistemas pequeños-medianos

**3. Chimeneas de equilibrio:**
- Permiten oscilación de nivel
- Ideales para líneas largas de gravedad
- Requieren espacio y altura disponible

**4. Válvulas de admisión y expulsión de aire:**
- Previenen vacío y columna separada
- Críticas en puntos altos y cambios de pendiente
- Bajo costo, alta efectividad

**5. Volantes de inercia en bombas:**
- Prolongan tiempo de desaceleración
- Reducen magnitud del transitorio
- Solución mecánica clásica

### 11.5 Análisis mediante Software

La aplicación integra análisis de transitorios mediante:

- **Método de las características (MOC)**
- Modelación de componentes reales
- Simulación de escenarios críticos
- Dimensionamiento de protecciones
- Generación de perfiles de presión vs tiempo

**Salidas:**
- Envolventes de presión máxima y mínima
- Gráficos temporales en puntos críticos
- Identificación de zonas de riesgo
- Recomendaciones de protección

---

## 12. Análisis de Costos y Optimización

### 12.1 Componentes de Costo

**Inversión inicial (CAPEX):**
```
CAPEX = C_tubería + C_accesorios + C_bomba + C_motor + C_VFD + C_instalación
```

**Costos de operación (OPEX anual):**
```
OPEX = C_energía + C_mantenimiento + C_personal + C_químicos
```

### 12.2 Valor Presente Neto

```
VPN = -CAPEX + Σ[OPEX_i / (1 + r)^i] para i = 1 a n
```

Donde:
- r = Tasa de descuento
- n = Vida útil (típico 20-30 años para bombeo)

### 12.3 Costo del Ciclo de Vida (LCC)

```
LCC = CAPEX + Σ[OPEX_i / (1+r)^i] + C_reemplazo/(1+r)^m - V_rescate/(1+r)^n
```

### 12.4 Optimización Multi-objetivo

La aplicación implementa algoritmos genéticos para optimizar simultáneamente:

1. **Minimizar costos**: VPN, LCC
2. **Maximizar confiabilidad**: NPSHdisp/NPSHreq
3. **Maximizar eficiencia**: η operación
4. **Minimizar impacto ambiental**: Emisiones CO₂

**Función objetivo ponderada:**

```
F = w₁·(Costo normalizado) + w₂·(1/Confiabilidad) + w₃·(1/Eficiencia) + w₄·(Emisiones)
```

---

## 13. Referencias

### Normativa Técnica

1. **Comisión Nacional del Agua (México)**
   - Manual de Agua Potable, Alcantarillado y Saneamiento: Sistemas de Bombeo
   - Manual: Diseño de Conducciones
   - Manual: Fenómenos Transitorios
   - Manual: Selección de Equipos y Materiales

2. **American Water Works Association (AWWA)**
   - AWWA M11: Steel Pipe Design and Installation
   - AWWA M23: PVC Pipe Design and Installation

3. **Hydraulic Institute (HI)**
   - ANSI/HI 9.6.1: Rotodynamic Pumps Guideline for NPSH

### Bibliografía Técnica

4. **Mataix, C.** (1986). *Mecánica de Fluidos y Máquinas Hidráulicas*. 2ª Ed. Ediciones del Castillo.

5. **Streeter, V.L. & Wylie, E.B.** (1999). *Fluid Transients in Systems*. Prentice Hall.

6. **Karassik, I.J. et al.** (2008). *Pump Handbook*. 4th Ed. McGraw-Hill.

7. **Swamee, P.K. & Jain, A.K.** (1976). "Explicit equations for pipe-flow problems". *Journal of Hydraulics Division, ASCE*, 102(5): 657-664.

8. **Tullis, J.P.** (1989). *Hydraulics of Pipelines: Pumps, Valves, Cavitation, Transients*. John Wiley & Sons.

### Manuales de Fabricantes

9. **Grundfos**: Pump Handbook
10. **KSB**: Centrifugal Pump Lexicon
11. **Goulds**: System Curve and Pump Selection

---

**FIN DEL DOCUMENTO**

---

*Documento elaborado como fundamento teórico de la aplicación de análisis y diseño de sistemas de bombeo para agua potable y alcantarillado.*

*Integra metodologías rigurosas, normativa técnica nacional e internacional, y buenas prácticas de ingeniería hidrosanitaria.*
