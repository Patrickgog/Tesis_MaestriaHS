# 🤖 Guía Completa del Módulo de Análisis con Inteligencia Artificial

## Documentación Técnica - Sistema de Diseño de Bombeo

---

## 📖 INTRODUCCIÓN

El **Módulo de Análisis con IA** integra **Google Gemini** (inteligencia artificial generativa) en la aplicación de diseño de bombeo para proporcionarte:

✅ **Análisis experto automático** de tu diseño  
✅ **Recomendaciones técnicas** basadas en mejores prácticas de ingeniería  
✅ **Detección de problemas** antes de implementar el sistema  
✅ **Explicaciones didácticas** de conceptos hidráulicos complejos  
✅ **Revisión técnica instantánea** disponible 24/7

El módulo **NO reemplaza tu criterio ingenieril**, sino que actúa como un **asesor técnico virtual** que complementa tu análisis.

---

## 🎯 OBJETIVOS DEL MÓDULO

### ¿Para Qué Sirve la IA en Esta Aplicación?

El sistema de IA evalúa tu diseño y genera un **informe técnico en lenguaje natural** que incluye:

1. **Evaluación General**: ¿El diseño es viable? ¿Hay problemas críticos?
2. **Análisis de Eficiencia**: ¿La bomba está operando en un rango óptimo?
3. **Análisis de NPSH**: ¿Hay riesgo de cavitación?
4. **Análisis de Velocidades**: ¿Las velocidades cumplen con normativas?
5. **Comparación con Normativas**: ¿El diseño sigue HI 9.6.1, ASME, ISO?
6. **Sugerencias de Optimización**: ¿Cómo mejorar el diseño?
7. **Análisis Económico**: ¿Es rentable instalar un VFD?

### ¿Qué NO Hace la IA?

❌ **NO hace los cálculos hidráulicos**: Los cálculos los realiza la aplicación con algoritmos determinísticos en Python  
❌ **NO diseña por ti**: Tú defines los parámetros, la IA solo analiza  
❌ **NO garantiza cumplimiento legal**: La responsabilidad profesional es siempre del ingeniero  
❌ **NO reemplaza la revisión por pares**: Siempre es recomendable que otro ingeniero revise diseños críticos

---

## 📍 UBICACIÓN DEL MÓDULO

El módulo de IA se encuentra en **dos ubicaciones** en la interfaz:

### 1. **Panel Lateral (Sidebar) - Configuración**
En la barra lateral izquierda, expander: **"🤖 Análisis IA"**

Aquí puedes:
- Ingresar tu API Key de Google Gemini
- Activar/desactivar el análisis automático
- Ver el estado de la conexión con Gemini

### 2. **Botón de Análisis en Reportes**
En algunas versiones, hay un botón **"🔍 Analizar Diseño Actual con IA"** que ejecuta el análisis bajo demanda.

---

## 🔑 CONFIGURACIÓN PREVIA (API KEY)

Antes de poder usar el análisis IA, necesitas configurar tu **API Key de Google Gemini**.

### ¿Qué es una API Key?

Una **API Key** (clave de API) es un código único que te identifica cuando usas el servicio de inteligencia artificial de Google. Es como una "contraseña" que permite a la aplicación conectarse con Gemini.

### Obtener tu API Key (GRATIS)

> **💡 Importante**: El servicio de Gemini tiene un **plan gratuito generoso** suficiente para uso normal de la aplicación.

Sigue estos pasos:

#### Paso 1: Acceder a Google AI Studio

1. Abre tu navegador
2. Ve a: **https://aistudio.google.com/**
3. Inicia sesión con tu cuenta de Google (Gmail)

#### Paso 2: Crear API Key

1. En el menú lateral, busca el ícono de **llave** 🔑 o la opción **"Get API key"**
2. Haz clic en **"Create API key"**
3. Selecciona:
   - **"Create API key in new project"** (si es tu primera vez)
   - O selecciona un proyecto existente si ya tienes uno

#### Paso 3: Copiar la API Key

1. Aparecerá tu API key en formato: `AIzaSy...` (aproximadamente 39 caracteres)
2. Haz clic en el botón de **copiar** 📋
3. **⚠️ GUARDA esta key en un lugar seguro** (bloc de notas, administrador de contraseñas)

> **🔒 Seguridad**: **NUNCA compartas tu API key públicamente** ni la subas a GitHub. Es personal e intransferible.

### Configurar la API Key en la Aplicación

#### Método: Ingreso Directo en la Interfaz (Versión Pública)

1. Abre la aplicación de diseño de bombeo
2. En el **sidebar izquierdo**, busca el expander **"🤖 Análisis IA"**
3. Haz clic para expandirlo
4. Verás un campo de texto: **"🔑 API Key de Gemini (opcional)"**
5. **Pega tu API key** completa en el campo:
   ```
   AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```
6. Presiona `Enter` o haz clic fuera del campo
7. Verás una confirmación:
   ```
   ✅ API Key configurada correctamente
   ```

### Límites del Plan Gratuito

El plan gratuito de Gemini incluye:

- **60 solicitudes por minuto**
- **1,500 solicitudes por día**
- **1 millón de tokens por mes**

**¿Es suficiente?**  
✅ Sí, más que suficiente para uso típico. Cada análisis consume ~1 solicitud, así que podrías hacer **1,500 análisis diarios** sin problema.

---

## 🔍 USAR EL ANÁLISIS IA

### Prerequisitos

Antes de solicitar un análisis con IA, asegúrate de:

1. ✅ **API Key configurada** (ver sección anterior)
2. ✅ **Diseño completo ingresado** (mínimo: caudal, alturas, diámetros)
3. ✅ **Cálculos ejecutados** (botón "🧮 Calcular Sistema" en pestaña "Análisis")
4. ✅ **Resultados visibles** (gráficos y tablas generados)

### Paso a Paso: Análisis del Diseño

#### Paso 1: Completar el Diseño

Asegúrate de tener ingresados y calculados:

- Caudal de diseño
- Alturas geométricas (succión y descarga)
- Diámetros y materiales de tuberías
- Curvas de la bomba (H-Q, η-Q, P-Q, NPSHr-Q)
- Resultados de cálculos (TDH, velocidades, NPSH)

#### Paso 2: Ejecutar Cálculos

1. Ve a la pestaña **"📈 Análisis"**
2. Haz clic en el botón **"🧮 Calcular Sistema"**
3. Espera a que aparezcan los resultados (punto de operación, gráficos)
4. Verifica que no haya errores

#### Paso 3: Solicitar Análisis IA

**Opción A: Desde el Sidebar**

1. En el **sidebar izquierdo**, expande **"🤖 Análisis IA"**
2. Verás el botón **"🔍 Analizar Diseño Actual"**
3. **Haz clic** en el botón
4. Aparecerá un mensaje:
   ```
   🧠 Analizando diseño con Gemini...
   ⏳ Esto puede tomar 10-30 segundos
   ```

**Opción B: Desde Reportes** (si existe en tu versión)

1. Ve a la pestaña **"📄 Reportes"**
2. Busca el botón **"🔍 Análisis IA del Diseño"**
3. Haz clic

#### Paso 4: Esperar Respuesta

- El análisis tarda típicamente **10-30 segundos**
- Dependiendo de:
  - Complejidad del diseño
  - Velocidad de tu conexión a internet
  - Carga de servidores de Google

#### Paso 5: Revisar Resultados

Una vez completado, verás el **informe generado por Gemini** en un contenedor expandible.

---

## 📊 INTERPRETACIÓN DEL INFORME DE IA

### Estructura Típica del Informe

El informe generado por Gemini sigue generalmente esta estructura:

#### 1. **Encabezado y Evaluación General**

```markdown
## 🔍 Análisis del Diseño de Sistema de Bombeo

**Proyecto**: Hospital Regional  
**Caudal de diseño**: 50.0 L/s  
**Altura total requerida (TDH)**: 32.5 m  

### ✅ EVALUACIÓN GENERAL: APROBADO con observaciones menores
```

**Interpretación**:
- **✅ APROBADO**: El diseño es técnicamente viable
- **⚠️ APROBADO CON OBSERVACIONES**: Viable pero tiene áreas de mejora
- **❌ REQUIERE REVISIÓN**: Hay problemas críticos que deben corregirse

#### 2. **Fortalezas del Diseño**

```markdown
**Fortalezas identificadas:**
- ✅ Eficiencia de bomba excelente (72.5%) - dentro del rango óptimo
- ✅ NPSH con margen adecuado (4.3 m de seguridad)
- ✅ Velocidades dentro de rangos recomendados
- ✅ Punto de operación cerca del BEP (95% del caudal óptimo)
```

**Qué hacer**: Reconocer lo que está bien hecho. Estas son confirmaciones de que tu diseño sigue buenas prácticas.

#### 3. **Oportunidades de Mejora**

```markdown
**Oportunidades de mejora:**

1. **Eficiencia Energética**:
   - La bomba está entregando 5.2 m más de altura que la requerida
   - **Recomendación**: Considerar instalación de VFD (Variador de Frecuencia)
   - **Ahorro proyectado**: ~35% en consumo eléctrico
   - **Retorno de inversión estimado**: 2.3 años

2. **Optimización de Diámetro de Succión**:
   - Diámetro actual: 75 mm
   - **Recomendación**: Aumentar a 90 mm
   - **Beneficio**: Reducción del 40% en pérdidas de succión
   - **Impacto**: NPSH disponible aumentaría de 8.5 m a 9.8 m
```

**Qué hacer**:
- Evalúa cada sugerencia
- Usa tu criterio profesional para decidir si implementarlas
- No todas las recomendaciones aplican en todos los casos (presupuesto, disponibilidad, etc.)

#### 4. **Comparación con Normas y Estándares**

```markdown
### 📋 Comparación con Mejores Prácticas (HI 9.6.1)

| Parámetro | Valor Calculado | Rango Normativo | Estado |
|-----------|-----------------|-----------------|--------|
| Velocidad succión | 0.85 m/s | 0.6 - 1.5 m/s | ✅ CUMPLE |
| Velocidad impulsión | 1.93 m/s | 1.0 - 2.5 m/s | ✅ CUMPLE |
| Margen NPSH | 4.3 m | > 1.5 m | ✅ CUMPLE |
| Eficiencia bomba | 72.5% | > 65% | ✅ CUMPLE |
| Proximidad BEP | 95% | 80-110% | ✅ CUMPLE |
```

**Interpretación**:
- **✅ CUMPLE**: El parámetro está dentro de lo aceptable según normativa
- **⚠️ LÍMITE**: Está en el borde del rango aceptable, monitorear
- **❌ NO CUMPLE**: Requiere corrección inmediata

#### 5. **Análisis de Riesgos**

```markdown
### ⚠️ Análisis de Riesgos

**Riesgo de Cavitación**: 🟢 BAJO
- NPSH disponible (8.5 m) \u003e\u003e NPSH requerido (4.2 m)
- Margen de seguridad: 4.3 m (103% sobre el mínimo)

**Riesgo de Erosión**: 🟡 MODERADO
- Velocidad en impulsión: 1.93 m/s (cerca del límite superior)
- Monitorear desgaste en codos y accesorios

**Riesgo de Golpe de Ariete**: 🟢 BAJO
- Velocidades moderadas
- Recomendar válvula de retención de cierre suave
```

**Niveles de Riesgo**:
- 🟢 **BAJO**: No requiere acción inmediata
- 🟡 **MODERADO**: Monitorear, aplicar buenas prácticas
- 🟠 **ALTO**: Requiere medidas preventivas
- 🔴 **CRÍTICO**: Acción correctiva inmediata necesaria

#### 6. **Calificación Energética**

```markdown
### ⚡ Calificación Energética: **B+ (Bueno)**

**Detalle**:
- Eficiencia operativa actual: 72.5%
- Consumo energético proyectado: 4,800 $/año
- **Con VFD podría alcanzar calificación A** (ahorro de 35%)
```

**Escala de Calificación**:
- **A+**: Excelente (eficiencia > 80%, VFD optimizado)
- **A**: Muy bueno (eficiencia 75-80%)
- **B**: Bueno (eficiencia 70-75%)
- **C**: Aceptable (eficiencia 60-70%)
- **D**: Mejorable (eficiencia 50-60%)
- **F**: Deficiente (eficiencia < 50%)

#### 7. **Conclusiones y Próximos Pasos**

```markdown
### 📌 Conclusiones

1. El diseño es **técnicamente viable** y cumple con normativas aplicables
2. La eficiencia es **buena** pero mejorable con inversión en VFD
3. No se detectaron riesgos críticos de cavitación o falla
4. El sistema está sobredimensionado en ~16% respecto al punto óptimo

### 🎯 Próximos Pasos Recomendados

1. **Evaluar económicamente** la instalación de un VFD:
   - Inversión estimada: $2,500 - $3,500 USD
   - Ahorro anual: ~$1,700 USD
   - ROI: ~2 años

2. **Considerar aumento de diámetro de succión** (de 75mm a 90mm):
   - Inversión adicional mínima (~$200 USD en tubería)
   - Beneficio: Mayor margen de seguridad NPSH

3. **Especificar válvula de retención** de cierre suave para evitar golpe de ariete

4. **Documentar el diseño final** con memoria de cálculo
```

---

## 🔧 CONFIGURACIÓN AVANZADA

### Personalizar el Análisis

Aunque en la versión pública el análisis es automático, puedes influir en él mediante:

#### 1. **Completitud de Datos**

Mientras más datos ingreses, más completo será el análisis:

- ✅ Todos los accesorios (codos, válvulas, etc.)
- ✅ Curvas completas de la bomba (no solo 3 puntos)
- ✅ Configuración VFD si aplica
- ✅ Resultados de optimización IA (algoritmo genético)

#### 2. **Contexto del Proyecto**

En el campo "Descripción del proyecto" o "Notas", puedes agregar:

```
Sistema crítico. Hospital con cirugías 24/7.
Prioridad: Confiabilidad sobre costo.
```

La IA considerará este contexto al generar recomendaciones.

---

## ❓ PREGUNTAS FRECUENTES (FAQ)

### ❓ ¿Es obligatorio usar la IA?

**R**: No, es completamente **opcional**. La aplicación funciona al 100% sin configurar Gemini. Los cálculos hidráulicos son independientes de la IA.

### ❓ ¿La IA puede equivocarse?

**R**: **Sí**. Gemini es una IA generativa que puede ocasionalmente:
- Malinterpretar datos
- Hacer suposiciones incorrectas
- Generar recomendaciones no aplicables a tu contexto específico

**Por eso es fundamental**: Usar tu criterio profesional y **no seguir ciegamente** las recomendaciones de la IA.

### ❓  ¿Qué tan actualizada está la IA?

**R**: Gemini 2.5 Flash (el modelo usado) tiene conocimiento general hasta su fecha de corte de entrenamiento. Para normativas muy recientes (publicadas hace menos de 6 meses), podrían no estar reflejadas.

### ❓ ¿Puedo usar la IA sin internet?

**R**: No. El análisis con IA requiere:
- ✅ Conexión a internet activa
- ✅ API Key válida
- ✅ Acceso a servidores de Google

Sin internet, la app funciona normalmente excepto por el módulo de IA.

### ❓ ¿La API Key caduca?

**R**: No, las API Keys de Google Gemini **no expiran automáticamente**. Sin embargo:
- Puedes revocarlas manualmente desde AI Studio
- Es buena práctica rotarlas cada 6-12 meses por seguridad

### ❓ ¿Qué pasa si supero el límite gratuito?

**R**: Si superas las1,500 solicitudes diarias:
- Recibirás un error: `429: Resource exhausted`
- Deberás esperar hasta el día siguiente
- O activar facturación en Google Cloud Console (costos muy bajos: ~$0.01 por análisis)

### ❓ ¿Puedo guardar el análisis de IA?

**R**: Sí, el análisis se puede:
1. **Copiar texto**: Selecciona y copia (Ctrl+C) el contenido del informe
2. **Incluir en PDF**: Al generar el reporte PDF completo, el análisis IA se incluirá (si está disponible)
3. **Captura de pantalla**: Toma screenshot del análisis para uso futuro

### ❓ ¿El análisis IA se guarda en el JSON?

**R**: **No**. El archivo JSON guarda solo los datos técnicos. El análisis de IA es **temporal** y se genera cada vez que lo solicitas.

**Ventaja**: Siempre tendrás el análisis más actualizado si modificas tu diseño.

### ❓ ¿Puedo hacer preguntas específicas a la IA?

**R**: En la versión pública actual, **no hay chat interactivo**. El análisis es automático y estándar.

Si necesitas análisis personalizados, puedes:
1. Copiar los datos de tu diseño (desde reportes Excel)
2. Ir directamente a https://aistudio.google.com/
3. Hacer preguntas específicas a Gemini con tus datos

### ❓ ¿La IA considera costos locales (tarifas eléctricas de mi país)?

**R**: No automáticamente. La IA usa valores genéricos para estimaciones económicas. **Tú debes ajustar** según tu contexto:

- Tarifas eléctricas de tu región
- Costos de materiales locales
- Disponibilidad de equipos (VFD, bombas, etc.)

---

## ⚠️ LIMITACIONES Y ADVERTENCIAS

### Lo que debes saber antes de usar IA

1. **No es un ingeniero certificado**: Las recomendaciones de la IA son orientativas, no sustituyen la responsabilidad profesional del ingeniero.

2. **Conocimiento general, no específico**: Gemini tiene conocimiento amplio pero puede no conocer:
   - Normativas locales específicas de tu país
   - Condiciones particulares de tu proyecto
   - Restricciones presupuestarias o de disponibilidad de materiales

3. **Puede "alucinar"**: En raras ocasiones, la IA puede generar información incorrecta con mucha confianza. **Siempre verifica** datos críticos.

4. **Dependencia de internet**: Si tu conexión falla, el análisis no estará disponible.

5. **Privacidad**: Los datos enviados a Gemini pasan por servidores de Google. No envíes información confidencial crítica.

---

## 💡 MEJORES PRÁCTICAS

### Cómo Aprovechar al Máximo el Análisis IA

#### 1. **Úsalo como Segunda Opinión**

✅ Haz tu diseño primero con tu criterio profesional  
✅ Luego pide el análisis IA  
✅ Compara tu análisis vs. IA  
✅ Identifica puntos ciegos que no habías considerado

#### 2. **Itera con la IA**

1. Diseño inicial → Análisis IA → Identificar mejoras
2. Aplicar mejoras → Recalcular → Nuevo análisis IA
3. Comparar versiones → Elegir la mejor alternativa

#### 3. **Documenta las Recomendaciones**

Cuando la IA sugiera algo importante:

```
ANÁLISIS IA - 2026-01-11
=======================
Recomendación: Instalar VFD
Justificación IA: Ahorro 35% energía, ROI 2.3 años
Decisión: ACEPTADA
Justificación ingeniero: Se ajusta al presupuesto y objetivos de sostenibilidad del cliente
```

#### 4. **Combina con Análisis EPANET**

1. Diseño en la app
2. Análisis con IA de Gemini
3. Exportar a EPANET
4. Validar con simulación hidráulica
5. **Triple validación** = Mayor confianza

---

## 📚 CONCEPTOS TÉCNICOS QUE LA IA EVALÚA

### Criterios de Evaluación Automática

La IA analiza tu diseño según estos criterios técnicos (basados en HI 9.6.1, ASME, ISO):

#### 1. **Velocidades óptimas**

| Línea | Mínimo | Óptimo | Máximo |
|-------|--------|--------|--------|
| Succión | 0.6 m/s | 0.9 - 1.2 m/s | 1.5 m/s |
| Impulsión | 1.0 m/s | 1.5 - 2.0 m/s | 2.5 m/s |

#### 2. **NPSH - Margen de Seguridad**

- **Mínimo absoluto**: NPSHd > NPSHr + 0.5 m
- **Recomendado**: NPSHd > NPSHr + 1.5 m
- **Ideal**: NPSHd > 1.3 × NPSHr

#### 3. **Eficiencia de Bomba**

- **Excelente**: η > 75%
- **Buena**: η = 65-75%
- **Aceptable**: η = 55-65%
- **Mejorable**: η < 55%

#### 4. **Proximidad al BEP**

- **Óptimo**: 80% ≤ Qop/QBEP ≤ 110%
- **Aceptable**: 70% ≤ Qop/QBEP ≤ 120%
- **Riesgoso**: Fuera de 70%-120%

#### 5. **Pérdidas en Succión**

- **Ideal**: Pérdidas < 5% de TDH
- **Aceptable**: Pérdidas < 10% de TDH
- **Excesivas**: Pérdidas > 10% de TDH

#### 6. **Factor de Servicio del Motor**

- **Mínimo**: FS ≥ 1.10
- **Recomendado**: FS = 1.15 - 1.25

---

## 🎓 EJEMPLO DE CASO REAL

### Escenario: Hospital Regional

**Diseño Inicial**:
- Caudal: 50 L/s
- TDH requerido: 30 m
- Bomba seleccionada: KSB Etanorm 125-100-250
- Sin VFD

**Análisis IA - Primera Iteración**:

```markdown
⚠️ APROBADO CON OBSERVACIONES

**Problema identificado**:
- La bomba entrega 36 m de altura
- Se requieren solo 30 m
- 20% de sobredimensionamiento
- Consumo energético: 5,200 $/año

**Recomendación**:
Instalar VFD para reducir RPM de 1750 a 1520 RPM
- Ahorro energético: 38%
- Inversión VFD: $3,000 USD
- ROI: 1.9 años
```

**Acción del Ingeniero**:
1. Configurar VFD en la app (pestaña Análisis → Botón "Cálculo RPM objetivo")
2. Nuevo análisis IA

**Análisis IA - Segunda Iteración**:

```markdown
✅ DISEÑO OPTIMIZADO - APROBADO

**Mejoras logradas**:
- Ahorro energético: 38% ($1,950/año)
- Eficiencia aumentó de 71% a 76%
- Punto de operación ahora al 98% del BEP
- Calificación energética: A

**Conclusión**:
Diseño final técnica y económicamente óptimo.
Listo para implementación.
```

---

## 🔒 PRIVACIDAD Y SEGURIDAD

### ¿Qué Datos se Envían a Gemini?

Cuando solicitas un análisis, se envían:

✅ Parámetros hidráulicos (caudales, alturas, diámetros)  
✅ Resultados de cálculos (TDH, velocidades, eficiencia)  
✅ Configuración de la bomba (curvas, BEP)  
✅ Nombre del proyecto (si lo ingresaste)

❌ **NO se envía**:
- Tu API Key (permanece solo en tu navegador)
- Información personal
- Archivos JSON completos
- Datos de otros proyectos

### ¿Google Guarda Mis Diseños?

Según las políticas de Google:
- Los datos enviados a Gemini pueden usarse para mejorar el servicio
- No se comparten con terceros
- No se utilizan para publicidad dirigida

**Recomendación**: Si tu diseño es **altamente confidencial** (proyectos militares, patentes, etc.):
- 🔴 **NO uses el análisis IA**
- O usa la API empresarial de Google con acuerdos de confidencialidad

---

**Guía generada para la Tesis de Maestría en Ingeniería Hidrosanitaria - 2026**  
*Autor: Patricio Sarmiento Reinoso*  
*Sistema de Diseño de Bombeo con Inteligencia Artificial - Versión 1.0*
