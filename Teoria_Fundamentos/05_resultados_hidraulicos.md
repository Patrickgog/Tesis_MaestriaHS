# Resultados Hidráulicos

## Parámetros Calculados

### 1. Altura Total de Bombeo (H_total)
$$H_{total} = H_{estatica} + H_{perdidas}$$

Donde:
- $H_{estatica}$ = Diferencia de cotas entre descarga y succión
- $H_{perdidas}$ = Pérdidas por fricción + pérdidas localizadas

### 2. Potencia Hidráulica
$$P_{hidraulica} = \gamma QH = \rho gQH$$

**En unidades prácticas**:
$$P_{kW} = \frac{QH}{102\eta_{bomba}}$$

Donde Q en m³/h, H en m

### 3. Potencia al Freno
$$P_{freno} = \frac{P_{hidraulica}}{\eta_{bomba}}$$

### 4. Potencia del Motor
$$P_{motor} \geq \frac{P_{freno}}{\eta_{motor} \times FS}$$

Donde:
- $\eta_{motor}$ ≈ 0.90 - 0.95 (motores eficientes)
- FS = 1.15 (factor de servicio típico)

### 5. NPSH Calculado
$$NPSH_{disponible} = \frac{P_{atm}}{\gamma} + h_{succion} - \frac{P_{vapor}}{\gamma} - h_{perdidas,succion}$$

**Valores típicos**:
- $P_{atm}$ (nivel del mar) = 10.33 m
- $P_{vapor}$ (20°C) = 0.24 m
- $h_{succion}$ = positivo o negativo según configuración

### 6. Velocidades
$$v = \frac{4Q}{\pi D^2}$$

**Rangos recomendados**:
- Tubería succión: 0.6 - 1.5 m/s
- Tubería impulsión: 1.0 - 2.5 m/s
- > 3 m/s: Excesivo (erosión, ruido, pérdidas altas)

### 7. Presiones
$$P = \gamma(H - z)$$

Donde:
- H = Altura piezométrica en el punto
- z = Elevación del punto

## Verificaciones de Diseño

✅ **NPSH**: $NPSH_{disponible} > NPSH_{requerido} + 0.5\ m$  
✅ **Velocidades**: Dentro de rangos recomendados  
✅ **Presiones**: No exceder clase de tubería  
✅ **Eficiencia**: Operar cerca del BEP (70-110%)  
✅ **Potencia**: Motor adecuadamente dimensionado  

## Análisis Económico

### Costo de Energía Anual
$$Costo_{anual} = P_{kW} \times h_{operacion} \times Tarifa_{kWh}$$

### Tiempo de Recuperación
Comparación entre:
- Bomba de mayor eficiencia (mayor costo inicial)
- Bomba estándar (menor eficiencia, mayor consumo)

$$Payback = \frac{\Delta Costo_{inicial}}{\Delta Costo_{energia,anual}}$$

---
*Todos estos resultados se presentan de forma clara en la pestaña de Tablas y Reportes.*
