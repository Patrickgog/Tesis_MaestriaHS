# VFD y Eficiencia Energética

## Variadores de Frecuencia (VFD)

### ¿Qué es un VFD?

Un **Variador de Frecuencia** (Variable Frequency Drive) es un dispositivo electrónico que controla la velocidad de un motor eléctrico mediante el ajuste de la frecuencia de alimentación.

**Ventajas**:
- 🔋 **Ahorro energético significativo** (30-70% en aplicaciones variables)
- 🎯 **Control preciso de caudal** sin válvulas de estrangulamiento
- 🔧 **Arranque suave** (reduce estrés mecánico)
- 🛡️ **Protección del motor** (sobrecarga, sub/sobretensión)
- 📊 **Flexibilidad operativa**

### Leyes de Afinidad

Cuando se varía la velocidad de una bomba centrífuga mediante VFD, se aplican las **Leyes de Afinidad**:

#### Ley 1: Caudal
$$ Q_2 = Q_1 \left(\frac{N_2}{N_1}\right) $$

El caudal es directamente proporcional a la velocidad.

#### Ley 2: Altura
$$ H_2 = H_1 \left(\frac{N_2}{N_1}\right)^2 $$

La altura varía con el cuadrado de la velocidad.

#### Ley 3: Potencia
$$ P_2 = P_1 \left(\frac{N_2}{N_1}\right)^3 $$

La potencia varía con el **cubo** de la velocidad (esto es clave para el ahorro).

Donde:
- $N_1$ = Velocidad nominal (típicamente 3600 o 1800 RPM)
- $N_2$ = Velocidad reducida
- Subíndice 1 = Condición nominal
- Subíndice 2 = Condición a velocidad reducida

### Ejemplo Numérico

**Bomba operando a 100% velocidad**:
- $Q_1$ = 100 L/s
- $H_1$ = 50 m
- $P_1$ = 50 kW

**Reduciendo a 80% velocidad** ( $N_2/N_1 = 0.8$ ):
- $Q_2 = 100 \times 0.8 = 80$ L/s
- $H_2 = 50 \times (0.8)^2 = 32$ m
- $P_2 = 50 \times (0.8)^3 = 25.6$ kW

**Ahorro de potencia**: $50 - 25.6 = 24.4$ kW (48.8%)

## Curvas Características con VFD

Al aplicar VFD, se genera una **familia de curvas H-Q** a diferentes velocidades:

- 100% RPM (Curva nominal del fabricante)
- 90% RPM (Curva escalada según Ley 2)
- 80% RPM
- 70% RPM
- 60% RPM (Mínimo recomendado)

### Punto de Operación con VFD

Para cada velocidad, existe un nuevo punto de operación donde:
$$H_{bomba}(Q, N) = H_{sistema}(Q)$$

**Importante**: La curva del sistema NO cambia con la velocidad de la bomba.

## Eficiencia con VFD

### Eficiencia del Motor

La eficiencia del motor típicamente:
- **Máxima** cerca del 100% carga a frecuencia nominal
- **Disminuye ligeramente** a velocidades reducidas
- **Pérdida típica**: 2-5% a 60-80% frecuencia

### Eficiencia del VFD

El VFD introduce pérdidas de conversión:
- **VFD eficiente**: η ≈ 96-98%
- **Pérdidas típicas**: 2-4%

###Eficiencia Global del Sistema

$$\eta_{global} = \eta_{bomba} \times \eta_{motor} \times \eta_{VFD}$$

**Ejemplo**:
- $\eta_{bomba}$ = 75%
- $\eta_{motor}$ = 92%
- $\eta_{VFD}$ = 97%
- $\eta_{global}$ = 0.75 × 0.92 × 0.97 = 66.9%

## Análisis Económico

### Costo de Implementación

**Inversión típica**:
- VFD (30-50 HP): USD 2,000 - 4,000
- Instalación y puesta en marcha: USD 1,000 - 2,000
- **Total**: USD 3,000 - 6,000

### Ahorro Anual

Para un sistema operando con demanda variable:

$$Ahorro_{anual} = \sum_{i=1}^{n} (P_{sin\ VFD,i} - P_{con\ VFD,i}) \times h_i \times C_{energia}$$

Donde:
- $P_{sin\ VFD}$ = Potencia sin VFD (con estrangulamiento)
- $P_{con\ VFD}$ = Potencia con VFD a velocidad reducida
- $h_i$ = Horas de operación en condición i
- $C_{energia}$ = Costo de energía (USD/kWh)

### Período de Recuperación

$$Payback = \frac{Inversion\ VFD}{Ahorro\ Anual}$$

**Típico**: 1-3 años en sistemas con operación variable

### Caso de Estudio

**Sistema**:
- Potencia nominal: 40 HP (30 kW)
- Operación: 8,000 h/año
- Costo energía: 0.12 USD/kWh
- 50% del tiempo requiere solo 60% caudal

**Sin VFD** (estrangulamiento con válvula):
- Potencia promedio: 28 kW
- Costo anual: $28 \times 8000 \times 0.12$ = USD 26,880

**Con VFD** (60% velocidad):
- Potencia a 60%: $30 \times (0.6)^3$ = 6.48 kW
- Potencia promedio: $(30 + 6.48)/2$ = 18.24 kW  
- Costo anual: $18.24 \times 8000 \times 0.12$ = USD 17,510

**Ahorro anual**: USD 9,370  
**Payback**: $5000 / 9370$ ≈ **0.53 años** (6.4 meses)

## Aplicaciones Ideales para VFD

✅ **Sistemas con demanda variable** (consumo varía según hora/día)  
✅ **Carga dominada por fricción** (curva del sistema parabólica)  
✅ **Operación continua** (muchas horas/año)  
✅ **Tarifa eléctrica alta**  
✅ **Múltiples puntos de operación**

## Aplicaciones NO Ideales

❌ **Carga dominada por altura estática** (poco ahorro)  
❌ **Operación constante** en un solo punto  
❌ **Sistemas pequeños** (< 5 HP)  
❌ **Presiones muy variables** (mejor tanque hidroneumático)

### Carga Estática vs Dinámica

**Curva del Sistema**:
$$H_{sistema} = H_{estatica} + k_{sistema}Q^2$$

**Con alta $H_{estatica}$**:
- VFD tiene **poco impacto** en ahorro
- La altura requerida no disminuye proporcionalmente con Q

**Con alta componente dinámica** ( $k_{sistema}Q^2$ ):
- VFD tiene **gran impacto**
- Al reducir Q, la presión disminuye significativamente

## Consideraciones de Diseño

### Velocidad Mínima

**No operar por debajo del 55-60% de velocidad nominal**:
- Refrigeración del motor puede ser insuficiente
- Eficiencia muy baja
- Posible resonancia mecánica

### Selección de Bomba con VFD

**Criterio**: Seleccionar bomba para que opere cerca del **BEP (Best Efficiency Point)** a la condición más frecuente, NO la máxima.

### Protecciones Necesarias

- 🛡️ **Protección de sobrecarga** del motor
- 🛡️ **Límite de velocidad mínima** (para refrigeración)
- 🛡️ **Protección contra ciclos cortos**
- 🛡️ **Monitoreo de presión** (para evitar cavitación)

## Comparación: VFD vs Estrangulamiento

| Criterio | VFD | Estrangulamiento con Válvula |
|----------|-----|------------------------------|
| **Ahorro energético** | ✅ Excelente (30-70%) | ❌ Nulo |
| **Control de caudal** | ✅ Preciso y continuo | ⚠️ Limitado |
| **Costo inicial** | ⚠️ Alto | ✅ Bajo |
| **Mantenimiento** | ⚠️ Requiere electrónica | ✅ Simple |
| **Confiabilidad** | ⚠️ Componente adicional | ✅ Alta |
| **Vida útil equipo** | ✅ Arranque suave | ⚠️ Mayor estrés mecánico |

## Conclusión

Los **VFD son una inversión altamente rentable** en sistemas de bombeo con demanda variable. El ahorro energético por la **ley cúbica de potencia** hace que el período de recuperación sea típicamente muy corto (< 2 años).

**Recomendación**: Evaluar siempre la opción de VFD en el diseño preliminar, especialmente en:
- Sistemas de distribución de agua
- Torres de enfriamiento
- Sistemas HVAC
- Procesos industriales variables

---

*La aplicación permite simular el impacto del VFD en curvas, potencia y ahorro energético.*
