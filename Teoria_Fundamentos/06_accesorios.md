# Cálculo de Accesorios

## Pérdidas Localizadas en Accesorios

Los accesorios como válvulas, codos y tees introducen pérdidas de carga localizadas (también llamadas **pérdidas menores**), que se calculan mediante:

$$h_L = K\frac{v^2}{2g}$$

Donde:
- K = Coeficiente de pérdida del accesorio (adimensional)
- v = Velocidad del flujo (m/s)
- g = 9.81 m/s²

## Coeficientes de Pérdida (K)

### Válvulas

| Tipo de Válvula | Condición | K |
|-----------------|-----------|---|
| **Compuerta** | Completamente abierta | 0.2 |
| **Compuerta** | 75% abierta | 1.0 |
| **Compuerta** | 50% abierta | 5.6 |
| **Globo** | Completamente abierta | 10.0 |
| **Bola** | Completamente abierta | 0.05 |
| **Mariposa** | Completamente abierta | 0.45 |
| **Check** (retención) | Abierta | 2.0 - 2.5 |
| **Pie con alcachofa** | - | 1.5 |

### Codos

| Tipo de Codo | K |
|--------------|---|
| **90° radio largo** ( $r/D = 1.5$ ) | 0.3 - 0.4 |
| **90° radio corto** ( $r/D = 1.0$ ) | 0.9 |
| **90° radio muy corto** (esquina viva) | 1.3 |
| **45° radio largo** | 0.2 |
| **Curva 180°** | 1.5 |

### Tees y Cruces

| Configuración | K |
|---------------|---|
| **Tee paso directo** (flujo recto) | 0.6 |
| **Tee bifurcación** (flujo a 90°) | 1.8 |
| **Cruz paso directo** | 0.9 |
| **Cruz bifurcación** | 2.5 |

### Reducciones y Ampliaciones

**Reducción**:
$$K_{reduccion} = 0.5\left(1 - \frac{D_2^2}{D_1^2}\right)$$

**Ampliación**:
$$K_{ampliacion} = \left(1 - \frac{D_1^2}{D_2^2}\right)^2$$

Donde:
- $D_1$ = Diámetro mayor
- $D_2$ = Diámetro menor

### Entradas y Salidas

| Elemento | K |
|----------|---|
| **Entrada de tanque** (borde vivo) | 0.5 |
| **Entrada de tanque** (borde redondeado) | 0.04 |
| **Salida de tanque** | 1.0 |
| **Entrada de tubería** (proyección hacia adentro) | 0.8 |

## Longitud Equivalente

Una forma alternativa de expresar las pérdidas de accesorios es mediante **longitud equivalente**:

$$L_{eq} = K\frac{D}{f}$$

Donde f = factor de fricción

**Concepto**: Representa la longitud de tubería recta que produciría la misma pérdida que el accesorio.

### Valores Típicos de Longitud Equivalente

Para tubería de hierro galvanizado (f ≈ 0.019):

| Accesorio | $L_{eq}/D$ |
|-----------|-----------|
| Válvula compuerta abierta | 8 |
| Válvula check | 100 |
| Codo 90° radio largo | 16 |
| Codo 90° radio corto | 30 |
| Tee bifurcación | 60 |

## Método de Cálculo en la Aplicación

La aplicación utiliza un **método de suma directa de coeficientes K**:

1. **Ingreso de accesorios**: El usuario especifica cantidad de cada tipo
2. **Suma de K**: Se calcula $\sum K = K_1 + K_2 + ... + K_n$
3. **Cálculo de pérdida**: $h_L = \sum K \frac{v^2}{2g}$

### Ejemplo de Cálculo

**Sistema con**:
- 2 codos 90° radio largo (K = 0.3 cada uno)
- 1 válvula compuerta (K = 0.2)
- 1 válvula check (K = 2.0)
- Velocidad = 2.0 m/s

**Cálculo**:
$$\sum K = 2(0.3) + 0.2 + 2.0 = 2.8$$

$$h_L = 2.8 \times \frac{(2.0)^2}{2 \times 9.81} = 2.8 \times 0.204 = 0.57\ m$$

## Consideraciones de Diseño

### Minimización de Pérdidas

✅ **Usar codos de radio largo** en lugar de radio corto  
✅ **Evitar cambios bruscos de dirección**  
✅ **Válvulas de compuerta** en lugar de globo (cuando sea posible)  
✅ **Reducciones graduales** con ángulo < 15°  
✅ **Minimizar número de accesorios** en succión  

### Importancia en Succión

Los accesorios en la **línea de succión** tienen mayor impacto porque:
- Reducen el NPSH disponible
- Incrementan riesgo de cavitación
- Afectan directamente la capacidad de succión de la bomba

**Recomendación**: Mantener $\sum K_{succion}$ lo más bajo posible.

## Verificación

La aplicación verifica que:
$$NPSH_{disponible} = P_{atm} + h_{succion} - P_{vapor} - h_{f,succion} - \sum K_{succion}\frac{v_{succion}^2}{2g} > NPSH_{requerido} + Margen$$

---

*El cálculo preciso de pérdidas en accesorios es crítico para el diseño correcto del sistema de bombeo.*
