# Cálculo de Pérdidas de Carga

## Métodos de Cálculo

Existen dos métodos principales para calcular pérdidas por fricción en tuberías:

1. **Ecuación de Hazen-Williams** ⭐ (Usado en esta aplicación)
2. **Ecuación de Darcy-Weisbach** (Referencia teórica)

---

## Ecuación de Hazen-Williams ⭐

### Fórmula Principal

La aplicación utiliza la **ecuación de Hazen-Williams** para calcular pérdidas por fricción:

$$h_f = 10.674 \times \frac{L}{C^{1.852}} \times \frac{Q^{1.852}}{D^{4.871}}$$

**Unidades**:
- $h_f$ = Pérdida de carga (m)
- L = Longitud de tubería (m)
- C = Coeficiente de rugosidad de Hazen-Williams
- Q = Caudal (m³/s)
- D = Diámetro interno (m)

### Coeficiente C de Hazen-Williams

El coeficiente C representa la rugosidad del material:

| Material | C (nuevo) | C (usado) |
|----------|-----------|-----------|
| **PVC, Plástico** | 150 | 140 |
| **Acero soldado nuevo** | 140 | 100 |
| **Hierro fundido nuevo** | 130 | 80-100 |
| **Hierro galvanizado** | 120 | 80 |
| **Acero comercial** | 140 | 110 |
| **Concreto liso** | 140 | 120 |
| **Concreto rugoso** | 120 | 100 |
| **Asbesto cemento** | 140 | 120 |

**Nota importante**: Un valor **MAYOR de C** indica **MENOR rugosidad** (menos pérdidas).

### Ventajas de Hazen-Williams

✅ **Simplicidad**: Cálculo directo sin iteraciones  
✅ **Precisión adecuada**: Para agua en condiciones típicas  
✅ **Uso generalizado**: Estándar en ingeniería sanitaria  
✅ **Tablas disponibles**: Amplia documentación de coeficientes C

### Limitaciones

⚠️ **Solo para agua**: No aplicable a otros fluidos  
⚠️ **Rango de velocidad**: Óptimo para 0.3 < v < 3 m/s  
⚠️ **Temperatura**: Asume propiedades del agua a temperatura ambiente

---

## Ecuación de Darcy-Weisbach (Referencia)

### Fórmula

$$h_f = f \frac{L}{D} \frac{v^2}{2g}$$

Donde:
- f = Factor de fricción de Darcy
- L = Longitud de tubería (m)
- D = Diámetro interno (m)
- v = Velocidad media (m/s)
- g = 9.81 m/s²

### Factor de Fricción (f)

**Flujo Laminar** (Re < 2000):
$$f = \frac{64}{Re}$$

**Flujo Turbulento** (Re > 4000):

Ecuación de Colebrook-White:
$$\frac{1}{\sqrt{f}} = -2\log_{10}\left(\frac{\varepsilon/D}{3.7} + \frac{2.51}{Re\sqrt{f}}\right)$$

Aproximación de Swamee-Jain:
$$f = \frac{0.25}{\left[\log_{10}\left(\frac{\varepsilon/D}{3.7} + \frac{5.74}{Re^{0.9}}\right)\right]^2}$$

### Número de Reynolds

$$Re = \frac{\rho vD}{\mu} = \frac{vD}{\nu}$$

Para agua a 20°C: $\nu \approx 1.0 \times 10^{-6}$ m²/s

### Rugosidad Absoluta (ε)

| Material | ε (mm) |
|----------|--------|
| PVC | 0.0015 |
| Acero comercial | 0.045 |
| Hierro galvanizado | 0.15 |
| Hierro fundido | 0.26 |
| Concreto | 0.3 - 3.0 |

---

## Pérdidas Localizadas en Accesorios

Las pérdidas en accesorios se calculan mediante:

$$h_L = K\frac{v^2}{2g}$$

### Método de Longitud Equivalente ⭐

La aplicación utiliza el método de **longitud equivalente** para accesorios:

$$L_{equivalente} = K \times \frac{D}{f_{aproximado}}$$

O directamente desde tablas:

$$L_{eq} = n_{accesorios} \times L_{eq,unitaria}$$

Donde:
- $n_{accesorios}$ = Cantidad de ese tipo de accesorio
- $L_{eq,unitaria}$ = Longitud equivalente por unidad (m o en diámetros)

### Tabla de Longitudes Equivalentes

**Expresadas en metros de tubería** (para D = 100 mm típico):

| Accesorio | $L_{eq}$ (m) | $L_{eq}/D$ |
|-----------|--------------|------------|
| **Válvula compuerta abierta** | 0.8 m | 8 |
| **Válvula globo abierta** | 34 m | 340 |
| **Válvula check** | 10 m | 100 |
| **Válvula mariposa** | 4.5 m | 45 |
| **Codo 90° radio largo** | 1.6 m | 16 |
| **Codo 90° radio corto** | 3.0 m | 30 |
| **Codo 45°** | 0.8 m | 8 |
| **Tee paso directo** | 1.8 m | 18 |
| **Tee bifurcación** | 6.0 m | 60 |
| **Entrada de tanque** | 1.5 m | 15 |
| **Salida de tanque** | 3.0 m | 30 |
| **Reducción gradual** | 0.5 m | 5 |

**Ejemplo de uso**:
- Sistema con 3 codos 90° radio largo
- $L_{eq,total} = 3 \times 1.6 = 4.8$ m
- Esta longitud se **suma** a la longitud real de tubería

### Coeficientes K (Alternativa)

| Accesorio | K |
|-----------|---|
| Válvula compuerta abierta | 0.2 |
| Válvula check | 2.0 - 2.5 |
| Codo 90° radio largo | 0.3 - 0.4 |
| Codo 90° radio corto | 0.9 |
| Tee bifurcación | 1.8 |
| Entrada de tanque | 0.5 |
| Salida de tanque | 1.0 |

---

## Pérdida Total del Sistema

### Succión

$$H_{perdidas,succion} = h_{f,succion} + h_{L,accesorios,succion}$$

Con Hazen-Williams:
$$H_{perdidas,succion} = 10.674 \times \frac{L_{total,succion}}{C^{1.852}} \times \frac{Q^{1.852}}{D_{succion}^{4.871}}$$

Donde:
$$L_{total,succion} = L_{real,succion} + \sum L_{eq,accesorios,succion}$$

### Impulsión

$$H_{perdidas,impulsion} = h_{f,impulsion} + h_{L,accesorios,impulsion}$$

Con Hazen-Williams:
$$H_{perdidas,impulsion} = 10.674 \times \frac{L_{total,impulsion}}{C^{1.852}} \times \frac{Q^{1.852}}{D_{impulsion}^{4.871}}$$

Donde:
$$L_{total,impulsion} = L_{real,impulsion} + \sum L_{eq,accesorios,impulsion}$$

### Total del Sistema

$$H_{perdidas,total} = H_{perdidas,succion} + H_{perdidas,impulsion}$$

---

## Ejemplo de Cálculo (Hazen-Williams)

**Datos del sistema**:
- Tubería PVC (C = 150)
- Diámetro succión: 150 mm = 0.15 m
- Diámetro impulsión: 100 mm = 0.10 m  
- Longitud real succión: 5 m
- Longitud real impulsión: 200 m
- Accesorios succión: 2 codos 90° ($L_{eq}$ = 3.2 m)
- Accesorios impulsión: 4 codos 90°, 1 válvula check, 1 válvula compuerta ($L_{eq}$ = 23.4 m)
- Caudal: 20 L/s = 0.020 m³/s

**Cálculo Succión**:
$$L_{total,succion} = 5 + 3.2 = 8.2\ m$$

$$h_{f,succion} = 10.674 \times \frac{8.2}{150^{1.852}} \times \frac{0.020^{1.852}}{0.15^{4.871}} = 0.12\ m$$

**Cálculo Impulsión**:
$$L_{total,impulsion} = 200 + 23.4 = 223.4\ m$$

$$h_{f,impulsion} = 10.674 \times \frac{223.4}{150^{1.852}} \times \frac{0.020^{1.852}}{0.10^{4.871}} = 5.89\ m$$

**Pérdida Total**:
$$H_{perdidas,total} = 0.12 + 5.89 = 6.01\ m$$

---

## Comparación Hazen-Williams vs Darcy-Weisbach

| Aspecto | Hazen-Williams | Darcy-Weisbach |
|---------|----------------|----------------|
| **Aplicabilidad** | Solo agua | Cualquier fluido |
| **Complejidad** | Simple (directo) | Complejo (iterativo) |
| **Precisión** | ±5-10% | ±2-5% |
| **Uso común** | Ingeniería sanitaria | Ingeniería general |
| **Velocidad cálculo** | Rápido | Lento |
| **Temperatura** | Limitado | Amplio rango |

**Conclusión**: Hazen-Williams es adecuado y ampliamente aceptado para sistemas de bombeo de agua.

---

*La aplicación calcula automáticamente todas las pérdidas usando Hazen-Williams con longitudes equivalentes para accesorios.*
