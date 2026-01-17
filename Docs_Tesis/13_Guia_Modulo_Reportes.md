# 📄 Guía Completa del Módulo de Reportes

## Documentación Técnica - Sistema de Diseño de Bombeo

---

## 📖 INTRODUCCIÓN

El **Módulo de Reportes** es una de las funcionalidades más importantes de la aplicación, ya que te permite **exportar, documentar y compartir** los resultados de tu diseño de sistema de bombeo en diferentes formatos profesionales.

Esta pestaña se encuentra en la barra de navegación principal y contiene **4 subpestañas especializadas**, cada una diseñada para un propósito específico:

1. **📕 PDF** - Memoria de cálculo completa
2. **📘 Word (.docx)** - Informe técnico editable con gráficos
3. **📗 Excel (.xlsx)** - Tablas de datos exportables
4. **🔧 EPANET** - Archivo de simulación hidráulica

---

## 🎯 OBJETIVOS DEL MÓDULO

Este módulo te permite:

✅ **Generar documentos profesionales** listos para presentar a clientes, profesores o revisores técnicos  
✅ **Documentar el diseño completo** con todos los cálculos, gráficos y criterios utilizados  
✅ **Compartir resultados** en formatos universales (PDF, Word, Excel)  
✅ **Validar el diseño** mediante archivo EPANET para simulaciones externas  
✅ **Respaldar el trabajo** con memorias de cálculo detalladas

---

## 📋 PREREQUISITOS

Antes de acceder a la pestaña de Reportes, **debes completar**:

1. ✅ **Datos de entrada** configurados (pestaña "Datos de Entrada")
2. ✅ **Cálculos ejecutados** (botón "🧮 Calcular Sistema" en pestaña "Análisis")
3. ✅ **Gráficos generados** (visibles en la pestaña "Análisis de Curvas")

> **⚠️ IMPORTANTE**: Si no has ejecutado los cálculos, los reportes estarán vacíos o mostrarán valores por defecto. Siempre completa tu diseño antes de generar reportes.

---

## 📕 SUBPESTAÑA 1: REPORTE PDF

### ¿Qué es?

El **Reporte PDF** es una **memoria de cálculo completa** que documenta todo el diseño del sistema de bombeo en un formato no editable, ideal para presentaciones formales y archivo técnico.

### ¿Qué incluye?

El PDF generado contiene las siguientes secciones:

#### 1. **Portada**
- Título del proyecto
- Nombre del diseño
- Nombre del diseñador/ingeniero
- Fecha de generación
- Logo de la aplicación

#### 2. **Resumen Ejecutivo**
- Parámetros principales del diseño
- Punto de operación (Qop, Hop, ηop, Pop)
- Diagnósticos automáticos (NPSH, eficiencia, velocidades)

#### 3. **Datos de Entrada**
- **Parámetros del fluido**: Temperatura, densidad, presión de vapor
- **Elevación del sitio**: Presión atmósférica calculada
- **Requerimientos hidráulicos**: Caudal de diseño, alturas geométricas
- **Tubería de succión**: Material, diámetro, longitud, accesorios
- **Tubería de impulsión**: Material, diámetro, longitud, accesorios

#### 4. **Resultados de Cálculos**
- **TDH (Total Dynamic Head)**: Altura total calculada
- **Pérdidas de fricción**: Succión e impulsión (método utilizado: Darcy-Weisbach o Hazen-Williams)
- **Pérdidas secundarias**: Por accesorios en ambas líneas
- **Velocidades**: En succión e impulsión
- **NPSH disponible vs. requerido**: Margen de seguridad
- **Potencia requerida**: Calculada según eficiencia
- **Motor seleccionado**: Potencia nominal y factor de servicio

#### 5. **Análisis de la Bomba**
- Curva caudal vs. altura (H-Q)
- Curva de eficiencia (η-Q)
- Curva de potencia (P-Q)
- Curva NPSH requerido (NPSHr-Q)
- **Punto de Máxima Eficiencia (BEP)**: Valores de QBEP, HBEP, ηmax

#### 6. **Análisis con Variador de Frecuencia (VFD)**
*(Si está configurado)*
- RPM objetivo calculadas
- Curvas ajustadas a la nueva velocidad
- Ahorro energético proyectado (kWh/año, $/año)
- Retorno de inversión (ROI) estimado

#### 7. **Gráficos Técnicos**
*(Si está activada la opción "Incluir gráficos")*
- Gráfico H-Q: Curva bomba vs. sistema (100% RPM)
- Gráfico η-Q: Eficiencia vs. caudal
- Gráfico P-Q: Potencia vs. caudal
- Gráfico NPSH: NPSHr vs. NPSHd
- Gráficos VFD (si aplica)

#### 8. **Criterios de Diseño y Normativas**
- Velocidades recomendadas vs. calculadas
- Margen NPSH según HI 9.6.1
- Rango de operación respecto al BEP
- Referencias a normas ASME, ISO

#### 9. **Conclusiones y Recomendaciones**
- Viabilidad del diseño
- Alertas técnicas (si existen)
- Sugerencias de optimización

### Cómo Generar el Reporte PDF

1. Ve a la pestaña **"📄 Reportes"**
2. Selecciona la subpestaña **"📕 PDF"**
3. Configura las opciones:
   - `☑️ Incluir gráficos`: Activa esta opción si quieres que el PDF contenga los gráficos generados
   - `☑️ Incluir análisis detallado`: Activar para incluir secciones extendidas de cálculos
4. Haz clic en el botón **"📥 Descargar Reporte PDF"**
5. El archivo se descargará con el nombre: `Reporte_[NombreProyecto]_[Fecha].pdf`

### Resultados Esperados

**✅ Documento PDF de entre 10-30 páginas** (dependiendo de si incluyes gráficos)  
**✅ Formato profesional** con encabezados, numeración, índice  
**✅ Listo para imprimir** o enviar por correo electrónico  
**✅ No editable** (garantiza integridad del contenido)

### Casos de Uso

- **Presentación a cliente**: Memoria de cálculo formal
- **Documentación académica**: Anexo técnico para tesis
- **Revisión por terceros**: Ingenieros revisores, autoridades
- **Archivo de proyecto**: Documentación histórica

---

## 📘 SUBPESTAÑA 2: REPORTE WORD (.docx)

### ¿Qué es?

El **Reporte Word** es un informe técnico **editable** que contiene los gráficos de tu diseño incrustados en un documento `.docx`. A diferencia del PDF, este formato te permite **modificar, agregar notas y personalizar** el contenido según tus necesidades.

### ¿Qué incluye?

El documento Word generado contiene:

#### 1. **Portada y Título**
- Nombre del proyecto
- Diseñador
- Fecha

#### 2. **Introducción Automática**
- Resumen breve del sistema diseñado
- Objetivos del informe

#### 3. **Gráficos de Análisis 100% RPM**
*(Si los gráficos fueron capturados en la pestaña "Análisis de Curvas")*

- **Gráfico 1: Caudal vs. Altura (H-Q)**
  - Curva de la bomba
  - Curva del sistema
  - Punto de operación marcado con estrella naranja ⭐
  - Información del punto: Qop, Hop, ηop

- **Gráfico 2: Caudal vs. Eficiencia (η-Q)**
  - Curva de rendimiento
  - Zona de eficiencia óptima (70%-110% BEP)
  - Punto de operación
  
- **Gráfico 3: Caudal vs. Potencia (P-Q)**
  - Curva de potencia requerida
  - Punto de operación
  - Potencia calculada en el punto

- **Gráfico 4: Caudal vs. NPSH**
  - Curva de NPSH requerido (NPSHr)
  - Línea de NPSH disponible (NPSHd)
  - Margen de seguridad visualizado

#### 4. **Gráficos de Análisis VFD**
*(Si se configuró el Variador de Frecuencia)*

- Gráficos H-Q, η-Q, P-Q, NPSH a RPM reducidas
- Comparación visual 100% RPM vs. VFD
- Punto de operación ajustado

#### 5. **Cuadros de Resumen**
Debajo de cada gráfico se incluye un **recuadro informativo** con:

```
📊 PUNTO DE OPERACIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Caudal (Q):      50.0 L/s
Altura (H):      32.5 m
Eficiencia (η):  72.3 %
Potencia (P):    23.8 kW
NPSH disp.:      8.5 m
NPSH req.:       4.2 m
Margen NPSH:     4.3 m ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Características Técnicas del Documento

- **Formato**: Microsoft Word (.docx)
- **Compatibilidad**: Office 2010 o superior, LibreOffice, Google Docs
- **Imágenes**: Resolución 300 DPI (calidad de impresión)
- **Estilo**: Profesional con encabezados automáticos

### Cómo Generar el Reporte Word

#### Paso 1: Capturar Gráficos (en pestaña "Análisis de Curvas")

> **⚠️ REQUISITO PREVIO**: Los gráficos deben estar **capturados** antes de generar el Word.

1. Ve a la pestaña **"📈 Análisis de Curvas"**
2. Verifica que los gráficos estén visibles (tanto 100% RPM como VFD si aplica)
3. **Los gráficos se capturan automáticamente** al visualizarlos
4. Confirmación visual: Verás los 4 gráficos principales desplegados

#### Paso 2: Activar Captura en Reportes

1. Ve a la pestaña **"📄 Reportes"**
2. Selecciona la subpestaña **"📘 Word"**
3. Activa la opción: `☑️ Incluir gráficos en el documento`
4. Verás un mensaje confirmando cuántos gráficos están disponibles:
   ```
   ✅ Encontrados 8 gráficos capturados:
   • 4 gráficos 100% RPM
   • 4 gráficos VFD
   ```

#### Paso 3: Generar el Documento

1. Haz clic en **"📥 Descargar Informe Word (.docx)"**
2. El sistema procesará los gráficos (puede tomar 10-30 segundos)
3. Se mostrará una barra de progreso:
   ```
   🔄 Generando documento Word...
   ⏳ Procesando gráficos (3/8)...
   ✅ Documento listo para descarga
   ```
4. El archivo se descargará: `Informe_[NombreProyecto]_[Fecha].docx`

### Resultados Esperados

**✅ Documento Word de 8-15 páginas**  
**✅ Gráficos de alta calidad (300 DPI)** incrustados  
**✅ Completamente editable** en Word, LibreOffice o Google Docs  
**✅ Incluye cuadros informativos** debajo de cada gráfico  
**✅ Formato profesional** listo para personalizar

### Solución de Problemas

#### ❌ "No se encontraron gráficos capturados"

**Causa**: No visitaste la pestaña "Análisis de Curvas" o los gráficos no se generaron.

**Solución**:
1. Ve a **"📈 Análisis de Curvas"**
2. Verifica que las 4 gráficas estén visibles
3. Si no aparecen, regresa a **"Análisis"** y haz clic en **"🧮 Calcular Sistema"**
4. Vuelve a **"Análisis de Curvas"** para que se generen
5. Regresa a **"Reportes → Word"** y genera nuevamente

#### ❌ "El documento tiene gráficos en blanco"

**Causa**: Error en la captura de Matplotlib.

**Solución**:
1. En la pestaña Reportes → Word, haz clic en **"🔍 Diagnóstico del Sistema"**
2. Verifica que Matplotlib esté instalado correctamente
3. Si hay error, contacta al administrador del sistema

#### ❌ "El documento Word no abre"

**Causa**: Versión antigua de Microsoft Office.

**Solución**:
- Abre con **LibreOffice** (gratuito)
- Abre con **Google Docs** (subir el archivo a Google Drive)
- Actualiza Microsoft Office a versión 2010 o superior

### Casos de Uso

- **Informes personalizables**: Agregar comentarios, logos de empresa
- **Presentaciones técnicas**: Copiar/pegar gráficos a PowerPoint
- **Documentos colaborativos**: Enviar a colegas para revisión
- **Reportes académicos**: Integrar en tesis o trabajos universitarios

---

## 📗 SUBPESTAÑA 3: REPORTE EXCEL (.xlsx)

### ¿Qué es?

El **Reporte Excel** exporta **todas las tablas de datos** generadas por la aplicación en formato `.xlsx`, permitiéndote realizar análisis adicionales, gráficos personalizados o integrar los datos en tus propias hojas de cálculo.

### ¿Qué incluye?

El archivo Excel generado contiene **múltiples hojas de cálculo** (pestañas), cada una con datos específicos:

#### Hoja 1: **"Datos de Entrada"**
Tabla con todos los parámetros ingresados:

| Parámetro | Valor | Unidad |
|-----------|-------|--------|
| Caudal de diseño | 50.0 | L/s |
| Altura geométrica succión | -2.5 | m |
| Altura geométrica descarga | 28.0 | m |
| Diámetro succión | 100 | mm |
| Diámetro impulsión | 80 | mm |
| Material succión | PVC | - |
| Material impulsión | PVC | - |
| Temperatura agua | 20 | °C |
| Elevación sitio | 2400 | msnm |

#### Hoja 2: **"Curva Bomba - H vs Q (100% RPM)"**
Datos tabulados de la curva característica:

| Caudal (L/s) | Altura (m) |
|--------------|------------|
| 0            | 42.5       |
| 10           | 41.2       |
| 20           | 39.5       |
| 30           | 37.1       |
| 40           | 34.0       |
| 50           | 30.2       |
| ...          | ...        |

#### Hoja 3: **"Curva Eficiencia - η vs Q (100% RPM)"**

| Caudal (L/s) | Eficiencia (%) |
|--------------|----------------|
| 0            | 0.0            |
| 10           | 45.2           |
| 20           | 62.8           |
| 30           | 74.5           |
| 40           | 78.2           |
| 50           | 72.3           |
| ...          | ...            |

#### Hoja 4: **"Curva Potencia - P vs Q (100% RPM)"**

| Caudal (L/s) | Potencia (kW) |
|--------------|---------------|
| 0            | 0.0           |
| 10           | 5.2           |
| 20           | 12.8          |
| 30           | 18.9          |
| 40           | 22.1          |
| 50           | 23.8          |
| ...          | ...           |

#### Hoja 5: **"Curva NPSH - NPSHr vs Q (100% RPM)"**

| Caudal (L/s) | NPSH req. (m) |
|--------------|---------------|
| 0            | 1.2           |
| 10           | 1.5           |
| 20           | 2.1           |
| 30           | 3.0           |
| 40           | 3.8           |
| 50           | 4.2           |
| ...          | ...           |

#### Hoja 6: **"Curva Sistema - Hsis vs Q"**

| Caudal (L/s) | Altura Sistema (m) |
|--------------|--------------------|
| 0            | 25.5               |
| 10           | 25.8               |
| 20           | 26.5               |
| 30           | 27.8               |
| 40           | 29.9               |
| 50           | 32.5               |
| ...          | ...                |

#### Hoja 7: **"Punto de Operación"**
Tabla resumen con valores clave:

| Concepto | Valor | Unidad |
|----------|-------|--------|
| Caudal de operación | 50.0 | L/s |
| Altura total (Hop) | 32.5 | m |
| Eficiencia (ηop) | 72.3 | % |
| Potencia (Pop) | 23.8 | kW |
| TDH calculado | 32.5 | m |
| Pérdidas succión | 0.8 | m |
| Pérdidas impulsión | 3.2 | m |
| Velocidad succión | 0.85 | m/s |
| Velocidad impulsión | 2.12 | m/s |
| NPSH disponible | 8.5 | m |
| NPSH requerido | 4.2 | m |
| Margen NPSH | 4.3 | m |

#### Hojas Adicionales (si VFD está configurado):
- **"Curva Bomba VFD"**
- **"Curva Eficiencia VFD"**
- **"Curva Potencia VFD"**
- **"Curva NPSH VFD"**
- **"Punto Operación VFD"**
- **"Ahorro Energético VFD"**

### Cómo Generar el Reporte Excel

1. Ve a la pestaña **"📄 Reportes"**
2. Selecciona la subpestaña **"📗 Excel"**
3. Verifica que aparezca el mensaje:
   ```
   ✅ Tablas disponibles para exportación: 6 hojas
   ```
4. Haz clic en **"📥 Descargar Reporte Excel (.xlsx)"**
5. El archivo se descargará: `Datos_[NombreProyecto]_[Fecha].xlsx`

### Resultados Esperados

**✅ Archivo Excel con 6-12 hojas de cálculo**  
**✅ Datos tabulados listos para análisis**  
**✅ Compatible con Excel 2010+, LibreOffice Calc, Google Sheets**  
**✅ Datos en formato numérico** (no texto) para fácil manipulación

### Casos de Uso

#### 1. **Análisis Personalizado**
- Crear gráficos propios en Excel
- Aplicar filtros y tablas dinámicas
- Realizar cálculos adicionales

#### 2. **Comparación de Alternativas**
- Exportar múltiples diseños
- Consolidar en una sola hoja de cálculo
- Comparar opciones lado a lado

#### 3. **Integración con Otros Software**
- Importar datos a MATLAB, Python, R
- Análisis estadístico
- Optimización externa

#### 4. **Documentación de Respaldo**
- Anexo de datos para reportes
- Evidencia de cálculos
- Trazabilidad de resultados

### Tip Profesional

> **💡 Consejo**: Para análisis rápidos, usa **filtros automáticos** en Excel:
> 1. Selecciona cualquier celda de la tabla
> 2. `Datos → Filtro` (o `Ctrl+Shift+L`)
> 3. Filtra por rangos de caudal, eficiencia, etc.

---

## 🔧 SUBPESTAÑA 4: EXPORTACIÓN EPANET

### ¿Qué es?

**EPANET** es un software gratuito de la EPA (Environmental Protection Agency) ampliamente utilizado para **simulación hidráulica de redes de agua**. Esta subpestaña te permite exportar tu diseño en formato compatible con EPANET `.inp`, permitiendo:

- **Validación externa** del diseño
- **Simulación de transitorios** (golpe de ariete)
- **Análisis de sensibilidad**
- **Modelado de escenarios** (variación de demanda, fallas, etc.)

### ¿Qué incluye el archivo EPANET?

El archivo `.inp` generado contiene:

#### 1. **Nodos (Nodes)**
```
[JUNCTIONS]
;ID    Elev    Demand
 N1    0       0       ;Tanque de succión
 N2    28      50      ;Punto de descarga
```

#### 2. **Tanques (Reservoirs/Tanks)**
```
[RESERVOIRS]
;ID    Head
 R1    -2.5    ;Nivel de agua en succión
```

#### 3. **Tuberías (Pipes)**
```
[PIPES]
;ID    Node1  Node2  Length  Diameter  Roughness
 P1    R1     N1     12.5    100       0.0015    ;Succión
 P2    N1     N2     45.0    80        0.0015    ;Impulsión
```

#### 4. **Bomba (Pump)**
```
[PUMPS]
;ID    Node1  Node2  Curve
 PU1   N1     N2     C1      ;Bomba principal

[CURVES]
;ID    Flow    Head
 C1    0       42.5
 C1    20      39.5
 C1    40      34.0
 C1    60      26.8
```

#### 5. **Accesorios (Minor Losses)**
```
[VALVES]
;Check valve, gate valve, etc.
```

#### 6. **Opciones de Simulación**
```
[OPTIONS]
 Units           LPS
 Headloss        D-W        ;Darcy-Weisbach
 Specific Gravity 1.0
 Viscosity       1.0
 Trials          40
 Accuracy        0.001
```

### Cómo Exportar a EPANET

1. Ve a la pestaña **"📄 Reportes"**
2. Selecciona la subpestaña **"🔧 EPANET"**
3. Configura las opciones:
   - **Método de pérdidas**: Darcy-Weisbach (recomendado) o Hazen-Williams
   - **Incluir accesorios**: ☑️ Activar para modelar codos, válvulas, etc.
   - **Nombre del proyecto EPANET**: `Sistema_Bombeo_Hospital`
4. Haz clic en **"📥 Descargar archivo EPANET (.inp)"**
5. El archivo se descargará: `[NombreProyecto]_EPANET.inp`

### Cómo Abrir el Archivo en EPANET

#### Paso 1: Instalar EPANET

1. Descarga EPANET 2.2 desde: https://www.epa.gov/water-research/epanet
2. Instalación gratuita (Windows, Mac, Linux disponibles)

#### Paso 2: Abrir el Archivo

1. Abre EPANET
2. `File → Open → Selecciona tu archivo .inp`
3. El modelo se cargará automáticamente

#### Paso 3: Ejecutar Simulación

1. En EPANET, ve a `Project → Run Analysis` (o presiona el ícono ⚙️)
2. Si hay errores, EPANET mostrará un reporte
3. Si todo está correcto: `View → Results`

### Ver Resultados en EPANET

Una vez ejecutada la simulación:

- **Vista de Red**: Muestra el esquema hidráulico con colores según presión/caudal
- **Gráficos de Nodos**: Presión vs. tiempo en cada punto
- **Gráficos de Tuberías**: Caudal vs. tiempo, velocidad
- **Curva de la Bomba**: Punto de operación marcado

### Resultados Esperados

**✅ Archivo `.inp` válido** para EPANET 2.x  
**✅ Modelo hidráulico simplificado** de tu sistema  
**✅ Bomba con curva característica** ya configurada  
**✅ Listo para simular** cambios de caudal, presiones, etc.

### Lim itaciones del Modelo EPANET

> **⚠️ IMPORTANTE - Simplificaciones**:

1. **No incluye VFD**: El modelo se exporta a 100% RPM
2. **Modelo simplificado**: 2-3 nodos (no redes complejas)
3. **Sin transitorios**: Para golpe de ariete, usa HAMMER
4. **Rugosidad fija**: Usa el valor configurado en la app

### Casos de Uso

#### 1. **Validación de Resultados**
- Comparar punto de operación calculado por la app vs. EPANET
- Verificar coherencia de pérdidas de carga

#### 2. **Análisis de Escenarios "What-If"**
- ¿Qué pasa si aumento el caudal en +20%?
- ¿Qué ocurre si cierro parcialmente una válvula?
- ¿Cómo varía la presión si cambio la altura del tanque?

#### 3. **Reporte a Terceros**
- Muchos ingenieros revisores piden archivo EPANET
- Estándar en consultorías de agua potable

#### 4. **Aprendizaje y Validación**
- Comparar tu diseño manual con simulación
- Entender mejor el comportamiento hidráulico

---

## 🔄 FLUJO DE TRABAJO RECOMENDADO

Para aprovechar al máximo el módulo de reportes, sigue este flujo:

### Paso 1: Diseño Completo
1. Ingresa todos los datos (pestaña "Datos de Entrada")
2. Ejecuta cálculos (pestaña "Análisis" → botón "🧮 Calcular Sistema")
3. Revisa gráficos (pestaña "Análisis de Curvas")
4. Optimiza diámetros (pestaña "Optimización IA" - opcional)
5. Configura VFD si es necesario (pestaña "Análisis" → sección VFD)

### Paso 2: Captura de Gráficos
1. Ve a **"Análisis de Curvas"**
2. Verifica que los 4 gráficos principales estén visibles (100% RPM)
3. Si configuraste VFD, verifica los 4 gráficos VFD
4. **Los gráficos se capturan automáticamente** al visualizarlos

### Paso 3: Generación de Reportes
Ahora genera los reportes que necesites **en este orden**:

#### 1. **Excel** (primero - siempre útil)
- Exporta las tablas de datos para respaldo
- Útil si necesitas hacer análisis adicionales

#### 2. **Word** (si requieres informe editable)
- Activa "Incluir gráficos"
- Descarga el `.docx`
- Personaliza según necesidad (agregar logos, notas, etc.)

#### 3. **PDF** (memoria de cálculo formal)
- Activa "Incluir gráficos" y "Análisis detallado"
- Descarga el PDF final
- Este es tu documento oficial para entregar

#### 4. **EPANET** (validación externa - opcional)
- Exporta el `.inp`
- Abre en EPANET y ejecuta simulación
- Compara resultados con la app

### Paso 4: Archivo y Respaldo
- Guarda todos los archivos en una carpeta del proyecto:
  ```
  📁 Proyecto_HospitalRegional/
  ├── 📄 Datos_HospitalRegional_2026-01-11.xlsx
  ├── 📄 Informe_HospitalRegional_2026-01-11.docx
  ├── 📄 Reporte_HospitalRegional_2026-01-11.pdf
  ├── 📄 HospitalRegional_EPANET.inp
  └── 📄 Diseño_HospitalRegional.json (desde pestaña "Gestión")
  ```

---

## ❓ PREGUNTAS FRECUENTES (FAQ)

### ❓ ¿Por qué el PDF no incluye gráficos?

**R**: Debes activar la opción `☑️ Incluir gráficos`. Además, verifica que hayas visitado la pestaña "Análisis de Curvas" para que los gráficos se generen.

### ❓ ¿Puedo generar reportes sin ejecutar cálculos?

**R**: Técnicamente sí, pero los reportes contendrán valores por defecto (ceros o datos de ejemplo). **Siempre ejecuta los cálculos** antes de generar reportes profesionales.

### ❓ ¿Los gráficos en Word son editables?

**R**: Los gráficos se insertan como **imágenes PNG de alta calidad (300 DPI)**, no como objetos editables. Si necesitas editar los gráficos, usa el archivo Excel para recrearlos.

### ❓ ¿Puedo personalizar el formato del PDF?

**R**: En la versión pública, el formato PDF es fijo. Si necesitas personalizaciones (logos, encabezados, etc.), usa el **reporte Word** y conviértelo a PDF después de editarlo.

### ❓ ¿El archivo EPANET incluye el VFD?

**R**: No. El modelo EPANET se exporta siempre a **100% RPM**. EPANET no maneja variadores de frecuencia nativamente.

### ❓ ¿Qué hago si el archivo EPANET da error al abrirlo?

**R**: 
1. Verifica que usas **EPANET 2.2** (no versiones muy antiguas)
2. Revisa que el archivo `.inp` se descargó completamente (no corrupto)
3. Abre el archivo `.inp` con un editor de texto y verifica que contenga datos

### ❓ ¿Puedo generar reportes de múltiples diseños en lote?

**R**: No automáticamente. Debes generar cada reporte individualmente. Sin embargo, puedes:
1. Diseñar la Alternativa 1
2. Descargar todos los reportes
3. Cargar diseño de Alternativa 2
4. Descargar todos los reportes
5. Comparar manualmente

---

## 📚 REFERENCIAS TÉCNICAS

### Formatos de Archivo

- **PDF**: ISO 32000-2 (PDF 2.0)
- **Word**: Office Open XML (.docx) - ISO/IEC 29500
- **Excel**: Office Open XML (.xlsx) - ISO/IEC 29500
- **EPANET**: Formato `.inp` - EPA estándar

### Software Compatibles

- **PDF**: Adobe Reader, Foxit Reader, navegadores web
- **Word**: Microsoft Office 2010+, LibreOffice Writer, Google Docs
- **Excel**: Microsoft Office 2010+, LibreOffice Calc, Google Sheets
- **EPANET**: EPANET 2.0, 2.2 (gratuito de EPA)

---

## 💡 CONSEJOS PROFESIONALES

1. **Genera Excel primero**: Siempre exporta los datos a Excel como respaldo antes de generar PDF/Word.

2. **Verifica antes de entregar**: Abre cada archivo generado y revisa que los datos sean correctos antes de enviarlos.

3. **Nombra descriptivamente**: Aunque la app genera nombres automáticos, renómbralos con información útil:
   - `Diseño_Final_Revisado_2026-01-15.pdf`
   - `Diseño_Alternativa_A_Con_VFD.docx`

4. **Usa el Word para presentaciones**: El formato `.docx` es ideal para copiar/pegar gráficos a PowerPoint.

5. **Valida con EPANET**: Aunque es opcional, correr la simulación en EPANET da confianza adicional a tu diseño.

---

**Guía generada para la Tesis de Maestría en Ingeniería Hidrosanitaria - 2026**  
*Autor: Patricio Sarmiento Reinoso*  
*Sistema de Diseño de Bombeo con Inteligencia Artificial - Versión 1.0*
