# Datos de Entrada

## Parámetros Geométricos

### Altura Totales y Cotas

El diseño de un sistema de bombeo requiere definir las cotas de elevación de cada componente:

#### 1. Cota del Eje de la Bomba
**Definición**: Elevación del centro del eje de la bomba respecto al nivel de referencia (generalmente nivel del mar o terreno).

**Importancia**:
- Det

ermina la altura de succión estática
- Afecta el cálculo de NPSH disponible
- Crítico para evitar cavitación

**Rango típico**: 0 - 50 m.s.n.m. (dependiendo del proyecto)

#### 2. Cota del Nivel de Agua en Succión
**Definición**: Elevación del nivel de agua en el tanque o pozo de succión.

**Consideraciones**:
- Puede variar según nivel del tanque (mínimo operativo)
- Si está POR ENCIMA del eje: **succión positiva** (favorable)
- Si está POR DEBAJO del eje: **succión negativa** (requiere cuidado especial)

$$h_{succion} = Cota_{agua\ succion} - Cota_{eje\ bomba}$$

#### 3. Cota del Nivel de Agua en Descarga
**Definición**: Elevación del nivel de agua al cual se debe bombear.

**Aplicaciones típicas**:
- Tanque elevado
- Punto de entrega en presión
- Sistema de distribución

#### 4. Cota de la Válvula
**Definición**: Elevación de la válvula de control instalada en la línea de impulsión.

**Propósito**:
- Regulación de caudal
- Protección contra transitorios
- Aislamiento del sistema

## Parámetros Hidráulicos

### Caudal de Diseño

**Definición**: Flujo volumétrico que el sistema debe transportar.

$$Q = \\frac{Volumen}{Tiempo}$$

**Unidades comunes**:
- Litros por segundo (L/s)
- Metros cúbicos por hora (m³/h)
- Galones por minuto (GPM)

**Factores que determinan el caudal**:
- Demanda del sistema
- Población servida
- Tipo de servicio (doméstico, industrial, riego)
- Factor de simultaneidad

**Conversiones útiles**:
```
1 L/s = 3.6 m³/h = 15.85 GPM
1 m³/h = 0.278 L/s = 4.40 GPM
```

### Número de Bombas

**Configuraciones posibles**:

#### Bomba Única
- Simplicidad de operación
- Menor inversión inicial
- Sin redundancia (mayor riesgo)

#### Sistema Duplex (2 bombas)
- Una en operación + una de respaldo
- Redundancia total
- Mantenimiento sin detener servicio

#### Sistema Triplex (3 bombas)  
- Dos en operación + una de respaldo
- Mayor capacidad con redundancia
- Optimización de eficiencia según demanda

#### Bombas en Paralelo
**Aplicación**: Cuando Q requerido > Q nominal de una bomba

**Consideración importante**:
$$Q_{total} \\neq n \\times Q_{individual}$$

El caudal total es MENOR que la suma aritmética debido a que operan en un punto diferente de su curva característica.

#### Bombas en Serie
**Aplicación**: Cuando H requerida > H nominal de una bomba

$$H_{total} = H_1 + H_2 + ... + H_n$$

Las alturas SÍ se suman directamente.

## Parámetros de Tuberías

### Diámetros

**Tubería de Succión**:
- Generalmente 1 o 2 tamaños MAYOR que la brida de succión de la bomba
- Minimiza pérdidas de carga en succión
- Mejora NPSH disponible

**Tubería de Impulsión**:
- Se dimensiona según velocidad económica (1.5 - 2.5 m/s)
- Balance entre costo de tubería y pérdidas de energía
- Formula de Bresse: $D_{optimo} = k \\sqrt{Q}$ donde k ≈ 1.1 - 1.3

### Longitudes

**Longitud Real**: Distancia física medida entre puntos

**Longitud Equivalente**: Longitud adicional que representa las pérdidas de accesorios

$$L_{total} = L_{real} + L_{equivalente}$$

### Material y Rugosidad

**Coeficiente de rugosidad absoluta (ε)**:
- PVC: ε = 0.0015 mm (muy liso)
- Acero comercial: ε = 0.045 mm
- Hierro galvanizado: ε = 0.15 mm  
- Concreto: ε = 0.3 - 3.0 mm

**Afecta**:
- Factor de fricción de Darcy-Weisbach
- Pérdidas de carga
- Eficiencia global del sistema

## Accesorios

### Tipos Comunes

1. **Válvulas**:
   - Compuerta (bajo Cv)
   - Globo (alto Cv)
   - Check (anti-retorno)
   - Mariposa (regulación)

2. **Codos**:
   - 90° radio corto/largo
   - 45°
   - Tees o cruces

3. **Transiciones**:
   - Reducciones concéntricas/excéntricas
   - Ampliaciones

### Coeficiente de Pérdida (K)

Cada accesorio introduce una pérdida localizada:

$$h_L = K \\frac{v^2}{2g}$$

Valores típicos:
- Válvula compuerta abierta: K = 0.2
- Codo 90° radio largo: K = 0.3
- Tee paso directo: K = 0.6
- Reducción: K = 0.1 - 0.5

## Validación de Datos

La aplicación verifica automáticamente:

✅ **Coherencia geométrica**: $Cota_{descarga} > Cota_{succion}$  
✅ **Rangos físicos razonables**: Q > 0, D > 0  
✅ **NPSH disponible > NPSH requerido**  
✅ **Velocidades dentro de rango**: 0.5 m/s < v < 3 m/s

---

*Todos estos parámetros se ingresan en la pestaña "Datos de Entrada" y son fundamentales para el cálculo preciso del sistema.*
