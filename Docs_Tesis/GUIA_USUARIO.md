# 📘 Guía del Usuario - Sistema de Diseño de Bombeo

**Herramienta Avanzada de Diseño Hidráulico con Optimización por Inteligencia Artificial**

¡Bienvenido! Esta guía te llevará paso a paso por el flujo de trabajo recomendado para diseñar un sistema de bombeo eficiente y técnicamente robusto utilizando esta herramienta profesional.

---

## 🚀 1. INICIO DESDE CERO

### Primera Apertura de la Aplicación

Al abrir la aplicación por primera vez, el sistema cargará automáticamente **datos por defecto** que te servirán como ejemplo de referencia. Estos valores están precargados para que puedas familiarizarte con la interfaz y entender cómo funciona cada módulo antes de ingresar tu propio proyecto.

### ¿Tienes un Proyecto Previo?

Si ya has trabajado anteriormente con la aplicación y guardaste tus datos en formato **JSON**, puedes cargarlos inmediatamente:

1. Ve a la pestaña **"Gestión de Datos"** o al módulo de **"Cargar/Guardar"**
2. Haz clic en **"Cargar Proyecto"**
3. Selecciona tu archivo `.json` guardado previamente
4. Todo tu diseño (caudales, diámetros, curvas de bomba, configuración) se restaurará automáticamente

### Empezando un Diseño Nuevo

Si no tienes un archivo previo, **este es tu punto de partida**. Los datos por defecto te permitirán explorar todas las funcionalidades mientras vas ingresando la información real de tu proyecto.

> **💡 Recomendación**: Antes de comenzar a ingresar datos técnicos, tómate unos minutos para explorar todas las pestañas de la aplicación y familiarizarte con su estructura.

---

## ⚙️ 2. CONFIGURACIÓN INICIAL (Panel Lateral)

Antes de ingresar datos técnicos específicos de tu proyecto, es **fundamental** ajustar los parámetros generales en el **panel lateral izquierdo**. Esta configuración afectará todos los cálculos posteriores.

### 🌡️ Parámetros Físicos del Fluido

#### Temperatura del Líquido
La temperatura del agua es un parámetro **crítico** porque determina:

- **Presión de Vapor (Pv)**: A mayor temperatura, mayor presión de vapor, lo que reduce el NPSH disponible y aumenta el riesgo de cavitación
- **Viscosidad**: Afecta las pérdidas por fricción en tuberías
- **Densidad**: Influye en los cálculos de potencia

**Rango típico**: 5°C a 90°C (dependiendo de tu aplicación)

#### Elevación del Sitio (msnm)
La altura sobre el nivel del mar de tu instalación afecta:

- **Presión Barométrica (Patm)**: A mayor altitud, menor presión atmosférica disponible
- **NPSH disponible**: Se reduce significativamente en sitios de gran altitud

**Importancia**: Un diseño que funciona perfectamente a nivel del mar puede presentar cavitación severa a 2,500 msnm si no se considera este parámetro.

> **⚠️ CRÍTICO**: La aplicación calcula automáticamente la **Presión de Vapor** y **Presión Barométrica** basándose en estos dos parámetros. Estos valores son fundamentales para el cálculo del **NPSH disponible**, que determina si tu bomba sufrirá cavitación o no.

### 📏 Sistema de Unidades

Selecciona tu preferencia entre:
- **L/s** (Litros por segundo) - Común en diseño de sistemas pequeños y medianos
- **m³/h** (Metros cúbicos por hora) - Estándar en bombas comerciales grandes

**La app convertirá automáticamente** todos los valores mostrados en gráficas, tablas y reportes. Puedes cambiar esta configuración en cualquier momento sin perder datos.

### 🔧 Métodos de Cálculo

#### Método de Pérdidas por Fricción
Selecciona entre:

- **Hazen-Williams**: Más utilizado en sistemas de agua potable y distribución. Más simple pero menos preciso para fluidos viscosos
- **Darcy-Weisbach**: Más riguroso y universal. Recomendado para análisis académicos y proyectos críticos

#### Tipo de Ajuste de Curvas
La aplicación ajusta las curvas de la bomba mediante regresión polinomial. Puedes seleccionar:
- **Polinomio Grado 2**: Para curvas más suaves y generales
- **Polinomio Grado 3**: Más preciso para curvas con inflexiones

---

## 📝 3. INGRESO DE DATOS DE PROYECTO

En la pestaña **"Datos de Entrada"**, ingresa la información técnica de tu sistema siguiendo este orden lógico:

### Identificación del Proyecto

- **Nombre del Proyecto**: "Estación de Bombeo Hospital Regional"
- **Nombre del Diseño**: "Bombeo Principal - Alternativa 1"
- **Diseñador**: Tu nombre y título profesional

Estos datos aparecerán en todos los reportes y documentos técnicos generados.

### Definición de Requerimientos Hidráulicos

#### Caudal de Diseño (Q)
Este es **el parámetro más importante** de tu sistema. Define:
- Cuánta agua necesitas bombear (L/s o m³/h)
- Debe considerar factores como: consumo pico, factor de simultaneidad, reserva de incendios, etc.

**Ejemplo**: Si diseñas para un edificio con 100 departamentos con consumo promedio de 0.5 L/s pero pico de 1.2 L/s, debes usar el valor pico con factor de seguridad.

#### Alturas Geométricas

**Altura Geométrica de Succión (Hs)**:
- Diferencia de elevación entre el nivel del agua en la fuente y el eje de la bomba
- **Positiva**: Si el agua está por encima de la bomba (succión negativa o "flooded suction")
- **Negativa**: Si la bomba está por encima del agua (succión positiva o "suction lift")

**Altura Geométrica de Descarga (Hd)**:
- Diferencia de elevación entre el eje de la bomba y el punto de descarga final
- Siempre es un valor positivo

### Definición de Líneas de Tubería

#### Línea de Succión

**Material de Tubería**:
Selecciona entre las opciones disponibles:
- **PVC** (Policloruro de Vinilo): Más económico, bajo peso, fácil instalación
- **HG** (Hierro Galvanizado): Mayor resistencia mecánica
- **PEAD** (Polietileno de Alta Densidad): Flexible, resistente a corrosión
- **Acero**: Máxima resistencia para altas presiones

La rugosidad absoluta de cada material está precargada en la aplicación y afecta las pérdidas por fricción.

**Longitud Real**:
- Mide la longitud total de tubería desde la fuente hasta la brida de entrada de la bomba
- Incluye tramos horizontales, verticales e inclinados

**Accesorios**:
Utiliza el **multiselector** para agregar todos los accesorios presentes en tu línea:
- Codos 90°
- Codos 45°
- Válvulas de compuerta
- Válvulas de retención (check)
- Tees
- Reducciones
- Ampliaciones

**La aplicación calcula automáticamente** las pérdidas secundarias (locales) usando el método de longitud equivalente o coeficiente K según el accesorio.

#### Línea de Impulsión (Descarga)

Sigue el mismo procedimiento que para la succión:
1. Material de tubería
2. Longitud total
3. Accesorios instalados

> **💡 Tip Profesional**: En la línea de impulsión, es crítico incluir **válvula de retención** (check valve) para evitar retroceso y posible golpe de ariete, así como **válvula de compuerta** para aislamiento y mantenimiento.

---

## 🏭 4. PREDISEÑO Y SELECCIÓN DE BOMBA

Una vez definidos los requerimientos hidráulicos, necesitas seleccionar una bomba que pueda satisfacerlos. La aplicación ofrece **dos caminos** para ingresar las características de la bomba.

### Opción A: Catálogo de Bombas Comerciales (Recomendado)

1. **Accede al expander** "🏭 Catálogo de Bombas Comerciales (Prediseño)"
2. **Filtra por marca**: Selecciona el fabricante de tu preferencia (Ej: Grundfos, KSB, Ebara, Pedrollo, etc.)
3. **Selecciona el modelo**: Elige la bomba específica que mejor se ajuste a tu rango de caudal y altura
4. **Carga automática**: Al seleccionar el modelo, la aplicación cargará automáticamente:
   - Curva Caudal vs. Altura (H-Q)
   - Curva de Rendimiento (η-Q)
   - Curva de Potencia (P-Q)
   - Curva de NPSHr (NPSH requerido)

**Ventajas**:
- ✅ Datos precisos tomados directamente de catálogos de fábrica
- ✅ Ahorro de tiempo (no necesitas transcribir manualmente)
- ✅ Menor probabilidad de errores de digitación
- ✅ Incluye múltiples puntos de operación para un ajuste preciso

### Opción B: Ingreso Manual (3 Puntos Mínimos)

Si tienes un **catálogo físico, PDF, o una bomba no incluida** en la base de datos:

1. Ve a la sección **"Ajuste de Curvas Características"** en la pestaña de Datos de Entrada
2. Para cada curva (H-Q, η-Q, P-Q, NPSHr-Q), necesitas ingresar **mínimo 3 puntos**
3. Identifica 3 puntos representativos de cada curva en el catálogo:
   - **Punto de caudal mínimo** (extremo izquierdo de la curva)
   - **Punto de máxima eficiencia (BEP)** - Best Efficiency Point
   - **Punto de caudal máximo** (extremo derecho)

#### Formato de Ingreso

**Desde Excel**:
Si tienes los datos en Excel, simplemente:
1. Organiza 2 columnas: Caudal | Altura (o Rendimiento, o Potencia, o NPSHr)
2. Selecciona las celdas y copia (Ctrl+C)
3. Pega directamente en el área de texto de la aplicación (Ctrl+V)

**Formato manual**:
```
Caudal [TAB] Altura
0       42.5
15      40.0
25      38.0
35      34.5
45      28.0
```

> **🎯 Recomendación**: Mientras más puntos ingreses (5-7 puntos), más preciso será el ajuste polinomial que genera la aplicación para crear la curva continua.

#### Ajuste Polinomial Automático

Una vez ingresados los puntos, la aplicación:
1. Ejecuta una **regresión polinomial** (grado 2 o 3 según configuración)
2. Genera la **curva continua** para todo el rango de caudales
3. Muestra el **coeficiente de determinación (R²)** para que evalúes la calidad del ajuste
   - R² > 0.95 = Excelente ajuste
   - R² < 0.90 = Considera ingresar más puntos o verificar datos

---

## 🎯 5. OPTIMIZACIÓN IA (Algoritmos Genéticos)

**Antes de fijar manualmente los diámetros**, utiliza el poder de la Inteligencia Artificial para encontrar la solución óptima.

### ¿Qué es la Optimización por Algoritmos Genéticos?

Es un **motor de inteligencia artificial inspirado en la evolución natural** que:

1. **Genera miles de "individuos"** (cada uno es una combinación diferente de diámetros comerciales para succión e impulsión)
2. **Evalúa cada individuo** calculando su "fitness" (aptitud) basándose en:
   - **Costo de Inversión**: Precio de las tuberías según diámetros seleccionados
   - **Costo Operativo**: Consumo energético proyectado durante la vida útil del proyecto (generalmente 20 años) debido a pérdidas por fricción
3. **Evoluciona las soluciones** mediante:
   - **Selección**: Los mejores individuos tienen mayor probabilidad de reproducirse
   - **Cruza**: Combinación de características de dos buenos individuos
   - **Mutación**: Cambios aleatorios para explorar nuevas soluciones
4. **Converge hacia la solución óptima** que **minimiza el costo total** del ciclo de vida

### ¿Qué Problema Resuelve?

En diseño hidráulico existe un **trade-off fundamental**:

- **Diámetros grandes**:
  - ✅ Bajas velocidades → Bajas pérdidas de fricción → Menor consumo energético
  - ❌ Alto costo de inversión en tuberías
  
- **Diámetros pequeños**:
  - ✅ Bajo costo de inversión
  - ❌ Altas velocidades → Altas pérdidas → Mayor consumo energético → Mayor costo operativo
  - ❌ Mayor riesgo de erosión y ruido

**El algoritmo genético encuentra el balance perfecto** entre ambos extremos.

### Cómo Utilizarlo

1. Ve a la pestaña **"🎯 Optimización IA (GA)"**
2. Configura los parámetros (opcional, los valores por defecto son buenos):
   - **Población**: 50-100 individuos (más población = mayor exploración pero más tiempo)
   - **Generaciones**: 50-100 iteraciones
   - **Costo energético** ($/kWh): Tarifa eléctrica de tu región
   - **Vida útil del proyecto**: 20-25 años típicamente
3. Haz clic en **"🚀 Iniciar Optimización Inteligente"**
4. **Espera** mientras la IA trabaja (puede tomar 30 segundos a 2 minutos dependiendo de la complejidad)

### Interpretación de Resultados

Al finalizar, obtendrás:

- **Diámetros óptimos** para succión e impulsión
- **Comparación económica**:
  - Costo total con tus diámetros actuales vs. diámetros optimizados
  - **Ahorro proyectado** en dinero sobre la vida útil
- **Gráfica de evolución**: Muestra cómo el algoritmo fue mejorando la solución generación tras generación
- **Análisis de sensibilidad**: Cómo varían los costos si cambias a diámetros comerciales cercanos

> **⚠️ IMPORTANTE**: Los diámetros sugeridos por la IA son una **recomendación técnico-económica**. Debes validarlos en el siguiente paso para asegurar que cumplan con restricciones de velocidad y normativas.

---

## 📏 6. SELECCIÓN TÉCNICA DE DIÁMETROS

Dirígete a la pestaña **"Selección de Diámetros"**. Aquí **validarás y ajustarás** los resultados de la optimización IA según criterios técnicos y normativos.

### Validación de Velocidades

La aplicación muestra automáticamente las velocidades en cada línea. Verifica que estén dentro de rangos recomendados:

**Línea de Succión**:
- **Mínimo**: 0.6 m/s (evita sedimentación de partículas)
- **Óptimo**: 0.9 - 1.5 m/s
- **Máximo**: 2.0 m/s (evita erosión y pérdidas excesivas que reducen NPSH disponible)

**Línea de Impulsión**:
- **Mínimo**: 0.9 m/s
- **Óptimo**: 1.5 - 2.5 m/s
- **Máximo**: 3.0 m/s (evita erosión, ruido y vibraciones)

> **⚠️ Alerta de Cavitación**: Si en la línea de succión la velocidad es muy alta, las pérdidas por fricción se disparan, reduciendo el NPSH disponible y provocando cavitación en la bomba.

### Análisis Gráfico: Pérdidas vs. Caudal

Este es uno de los **gráficos más críticos** del diseño. Muestra cómo varían las pérdidas de carga conforme aumenta el caudal.

#### Comportamiento de la Curva

Las pérdidas de fricción siguen una relación **exponencial** con el caudal (en Darcy-Weisbach es Q², en Hazen-Williams es Q^1.85).

**Zona Segura (Lineal aparente)**:
- Incrementos moderados de caudal causan incrementos proporcionales de pérdidas
- La curva tiene pendiente suave
- **Diseño ideal**: Tu punto de operación debe estar aquí

**Zona Asintótica (Roja - PELIGROSA)**:
- La curva se vuelve casi vertical
- Un pequeño aumento de caudal (+5%) puede duplicar las pérdidas
- **Consecuencias**:
  - La bomba no puede vencer la resistencia del sistema
  - Consumo energético se dispara
  - Imposible aumentar el caudal sin cambiar el diámetro
  - Riesgo de golpe de ariete severo

#### Criterio del 75%

La aplicación evalúa si tu **caudal de diseño** está por debajo del **75% del caudal crítico** (donde comienza la zona roja).

- ✅ **Está en zona segura**: "El diseño tiene margen de seguridad adecuado"
- ⚠️ **Está cerca del límite**: "Advertencia: se aproxima a la zona asintótica"
- ❌ **Está en zona roja**: "CRÍTICO: Incrementar diámetro inmediatamente"

> **💡 Regla de Oro**: Mantén siempre un **margen de seguridad mínimo del 25%** entre tu punto de operación y el inicio de la zona asintótica.

### Sincronización de Diámetros

Una vez validados y conformes con los diámetros:

1. Haz clic en **"Importar Diámetro Óptimo a Succión"**
2. Haz clic en **"Importar Diámetro Óptimo a Impulsión"**

Estos botones **transfieren automáticamente** los diámetros seleccionados de vuelta a las pestañas de "Datos de Entrada" y "Análisis", recalculando todo el sistema con los nuevos valores.

---

## 📊 7. ANÁLISIS DE RESULTADOS Y CURVAS

### Análisis a 100% RPM

En la pestaña **"Análisis de Curvas"**, el sistema superpone:

1. **Curva de la Bomba** (H-Q): Capacidad que ofrece la bomba seleccionada
2. **Curva del Sistema**: Resistencia hidráulica total (altura estática + pérdidas por fricción)

#### Punto de Operación

Es el **punto de intersección** de ambas curvas. Representa dónde realmente operará tu sistema:

- **Qop**: Caudal real de operación
- **Hop**: Altura total que entrega la bomba
- **ηop**: Eficiencia en ese punto
- **Pop**: Potencia consumida
- **NPSHd vs NPSHr**: Margen de seguridad contra cavitación

### Diagnósticos Automáticos

La aplicación genera **diagnósticos inteligentes** basados en mejores prácticas de ingeniería:

#### 1. Análisis de Eficiencia

- **Eficiencia > 65%**: "✅ Operación eficiente"
- **Eficiencia 50-65%**: "⚠️ Eficiencia moderada, considere alternativas"
- **Eficiencia < 50%**: "❌ Eficiencia baja, seleccione otra bomba"

#### 2. Análisis de NPSH (Cavitación)

- **NPSHd > NPSHr + 1.5m**: "✅ Margen adecuado, no hay riesgo de cavitación"
- **NPSHd > NPSHr + 0.5m**: "⚠️ Margen justo, monitorear en operación"
- **NPSHd ≤ NPSHr**: "❌ RIESGO CRÍTICO DE CAVITACIÓN - Rediseño necesario"

**¿Qué es la cavitación?**
Formación de burbujas de vapor en el interior de la bomba cuando la presión local cae por debajo de la presión de vapor. Causa daño catastrófico: erosión, ruido, vibraciones, falla prematura.

#### 3. Proximidad al BEP (Best Efficiency Point)

- **80% ≤ Qop/QBEP ≤ 110%**: "✅ Operación cerca del BEP"
- **Fuera de ese rango**: "⚠️ Operación alejada del BEP, vida útil reducida"

### ⚙️ Análisis con Variador de Frecuencia (VFD)

#### ¿Por qué es necesario un VFD?

En muchos casos, la bomba seleccionada del catálogo entrega **más presión de la necesaria** para vencer la altura de diseño. Esto ocurre porque:

- Los fabricantes producen modelos estándar con curvas fijas
- Tu punto de diseño puede no coincidir exactamente con ninguna bomba disponible
- Por seguridad, se selecciona una bomba ligeramente sobredimensionada

**Consecuencias de operar sin VFD**:
- ❌ **Desperdicio energético**: Estás pagando más electricidad de la necesaria
- ❌ **Presión excesiva**: Puede dañar tuberías, generar ruido, reducir vida útil de accesorios
- ❌ **Operación ineficiente**: La bomba trabaja fuera de su zona óptima

#### ¿Qué hace el VFD?

Un **Variador de Frecuencia** (Variable Frequency Drive) es un dispositivo electrónico que:

1. Controla la velocidad del motor eléctrico
2. **Reduce las RPM** de la bomba según necesidad
3. **Ajusta toda la curva H-Q** proporcionalmente siguiendo las leyes de afinidad:
   - Q₂/Q₁ = N₂/N₁ (caudal proporcional a velocidad)
   - H₂/H₁ = (N₂/N₁)² (altura proporcional al cuadrado de velocidad)
   - P₂/P₁ = (N₂/N₁)³ (potencia proporcional al cubo de velocidad)

**Beneficios**:
- ✅ **Ahorro energético**: Reducción de 30% a 60% en consumo eléctrico
- ✅ **Arranque suave**: Evita golpes de ariete y picos de corriente
- ✅ **Ajuste preciso**: Opera exactamente en tu punto de diseño
- ✅ **Flexibilidad**: Permite ajustes futuros si cambian las condiciones

#### Cómo Utilizar el Análisis VFD

1. Haz clic en **"Cálculo de RPM objetivo"**
2. La IA calcula la **velocidad exacta** (en RPM o % de velocidad nominal) necesaria para que la curva de la bomba pase exactamente por tu punto de diseño (Qd, Hd)
3. La aplicación genera automáticamente:
   - **Curvas ajustadas** a la nueva velocidad (H-Q, η-Q, P-Q, NPSH)
   - **Nuevo punto de operación** con VFD
   - **Cálculo de ahorro energético** proyectado (kWh/año y $/año)

#### Gráficos Comparativos

- **Superposición 100% RPM vs VFD**: Muestra ambas curvas y puntos de operación
- **Gráfico de ahorro**: Barras comparando consumo energético con/sin VFD
- **Eficiencia ajustada**: Cómo cambia la eficiencia de la bomba con la nueva velocidad

#### Resumen y Comentarios Técnicos con VFD

La aplicación genera diagnósticos actualizados considerando el VFD:

- **Eficiencia con VFD**: "✅ Eficiencia mejorada a 72% con VFD"
- **NPSH con VFD**: "✅ Margen de seguridad mantenido: NPSHd = 8.5m, NPSHr = 4.2m"
- **Ahorro proyectado**: "💰 Ahorro estimado: $1,250 USD/año (20% reducción en consumo)"
- **Retorno de inversión**: "📊 ROI del VFD: 2.5 años"

> **⚡ Dato Importante**: En muchos proyectos, el **costo del VFD se recupera en menos de 3 años** solo con el ahorro energético. Además, extiende la vida útil de la bomba y reduce mantenimientos.

---

## 🔄 8. EVALUACIÓN FINAL E ITERACIÓN

El diseño hidráulico es un **proceso iterativo** de optimización. Debes verificar múltiples criterios antes de dar por finalizado el diseño:

### Checklist de Verificación Final

#### ✅ 1. NPSH - Seguridad contra Cavitación

- [ ] NPSHd > NPSHr + 1.5 m (mínimo)
- [ ] NPSHd > 1.3 × NPSHr (criterio alternativo: 30% de margen)
- [ ] Si el margen es insuficiente:
  - Aumentar diámetro de succión (reduce pérdidas)
  - Elevar nivel de agua en tanque de succión
  - Cambiar a una bomba con menor NPSHr
  - Considerar bomba sumergible

#### ✅ 2. Potencia y Motor

- [ ] Motor seleccionado cubre Prequerida con factor de servicio (FS = 1.15 típicamente)
- [ ] Pmotor ≥ Pbomba × 1.15
- [ ] Si no:
  - Seleccionar motor de potencia inmediata superior
  - Verificar disponibilidad comercial del motor

#### ✅ 3. Eficiencia y Economía

- [ ] Eficiencia ≥ 65% en punto de operación
- [ ] Punto de operación dentro de 70%-110% del BEP (Best Efficiency Point)
- [ ] Si está muy alejado del BEP:
  - Buscar otra bomba del catálogo
  - Considerar VFD para ajustar punto de operación

#### ✅ 4. Velocidades

- [ ] Velocidad en succión: 0.9 - 1.8 m/s
- [ ] Velocidad en impulsión: 1.5 - 2.5 m/s
- [ ] Si están fuera de rango:
  - Ajustar diámetros
  - Verificar que no estés en zona asintótica

#### ✅ 5. Zona de Operación Segura

- [ ] Caudal de operación < 75% del caudal crítico (zona asintótica)
- [ ] Gráfica de pérdidas muestra pendiente moderada
- [ ] Si estás en zona roja:
  - **CRÍTICO**: Incrementar diámetro inmediatamente
  - Recalcular todo el sistema

#### ✅ 6. Costos

- [ ] Comparar costo total (inversión + operación 20 años) con alternativas
- [ ] Evaluar retorno de inversión si consideras VFD
- [ ] Documentar justificación de selección final

### ¿Los resultados NO son óptimos?

**No te preocupes, es normal.** El diseño hidráulico requiere varias iteraciones:

#### Estrategias de Iteración

1. **Si la eficiencia es baja**:
   - Regresa a "Catálogo de Bombas" y selecciona otro modelo
   - Busca bombas con BEP más cercano a tu caudal de diseño

2. **Si hay riesgo de cavitación**:
   - Aumenta el diámetro de succión
   - Reduce la longitud de succión si es posible
   - Considera bomba sumergible o con mejores características de NPSH

3. **Si las pérdidas son muy altas**:
   - Ejecuta nuevamente la Optimización IA con diámetros mayores
   - Reduce accesorios innecesarios
   - Considera materiales con menor rugosidad (PVC en lugar de HG)

4. **Si el costo es muy alto**:
   - Ajusta el balance inversión vs. operación en el algoritmo genético
   - Considera aumentar ligeramente la velocidad (con precaución)
   - Evalúa opciones de financiamiento para VFD (alto ROI)

### Guardar tu Diseño Final

Una vez satisfecho con los resultados:

1. Ve a **"Gestión de Datos"**
2. Haz clic en **"Guardar Proyecto"**
3. Asigna un nombre descriptivo: `Proyecto_HospitalRegional_Alternativa1_Final.json`
4. **Descarga el reporte PDF** desde la pestaña "Reportes"

Ahora tienes un **diseño técnicamente robusto, económicamente optimizado y documentado profesionalmente**.

---

## 📚 Referencias Técnicas y Normativas

- **NPSH**: Norma HI 9.6.1 (Hydraulic Institute - NPSH Margin)
- **Velocidades**: ASME, ISO 2548, normas locales de diseño sanitario
- **Pérdidas de carga**: 
  - Hazen-Williams (AWWA M11)
  - Darcy-Weisbach (ISO 1438, Moody)
- **Algoritmos Genéticos**: Goldberg (1989), Deb (2001)
- **Bombas centrífugas**: Karassik Pump Handbook, 4th Edition

---

## 💡 Consejos Profesionales

1. **Siempre comienza por el NPSH**: Es el factor limitante más crítico
2. **No confíes ciegamente en la IA**: Valida siempre con criterio ingenieril
3. **Documenta tus decisiones**: El reporte PDF es tu respaldo técnico y legal
4. **Considera el ciclo de vida completo**: Un sistema barato hoy puede ser carísimo en operación
5. **El VFD casi siempre se justifica**: Analízalo en todo proyecto > 5 HP

---

**Guía generada para la Tesis de Maestría en Ingeniería Hidrosanitaria - 2026**  
*Autor: Patricio Sarmiento Reinoso*  
*Herramienta de Diseño de Sistemas de Bombeo con Inteligencia Artificial - Versión 1.0*
