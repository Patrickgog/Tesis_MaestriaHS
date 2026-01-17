# 📊 Guía de Tablas de Configuración y Gestión de Archivos JSON

## Documentación Técnica - Sistema de Diseño de Bombeo

---

## 📖 INTRODUCCIÓN

El sistema de **Tablas de Configuración** y **Gestión JSON** es el módulo que te permite **guardar, cargar, editar y respaldar** tus diseños de sistemas de bombeo. Este módulo es fundamental para:

✅ **Preservar tu trabajo** entre sesiones  
✅ **Comparar alternativas** de diseño  
✅ **Compartir proyectos** con col egas  
✅ **Mantener historial** de versiones  
✅ **Migrar diseños** entre computadoras

---

## 🔑 CONCEPTOS CLAVE

### ¿Qué es un archivo JSON?

**JSON** (JavaScript Object Notation) es un formato de texto plano que almacena datos estructurados de forma legible tanto para humanos como para máquinas. En esta aplicación, el JSON almacena **TODOS los datos** de tu diseño en un solo archivo.

**Ejemplo simplificado**:
```json
{
  "proyecto": {
    "nombre": "Sistema de Bombeo Hospital Regional",
    "disenador": "Ing. María González",
    "fecha": "2026-01-11"
  },
  "datos_entrada": {
    "caudal_diseno": 50.0,
    "unidades_caudal": "L/s",
    "altura_succion": -2.5,
    "altura_descarga": 28.0
  },
  "tuberia_succion": {
    "diametro": 100,
    "material": "PVC",
    "longitud": 12.5,
    "accesorios": ["Codo 90°", "Válvula check"]
  }
}
```

### ¿Dónde se guardan los archivos?

Los archivos JSON se guardan en la **carpeta que elijas** al descargarlos desde la aplicación. La ubicación típica es:

- **Windows**: `C:\Users\TuUsuario\Downloads\` o carpeta de proyecto específica
- **Mac**: `/Users/TuUsuario/Downloads/` o carpeta de proyecto
- **Linux**: `/home/TuUsuario/Downloads/` o carpeta de proyecto

> **💡 Recomendación**: Crea una carpeta dedicada para cada proyecto:
> ```
> 📁 C:\Proyectos\HospitalRegional\
> ├── 📄 Diseño_Inicial_2026-01-05.json
> ├── 📄 Diseño_Optimizado_2026-01-08.json
> ├── 📄 Diseño_Final_Con_VFD_2026-01-11.json
> └── 📁 Reportes\
>     ├── PDF\
>     ├── Word\
>     └── Excel\
> ```

---

## 📂 UBICACIÓN DEL MÓDULO EN LA INTERFAZ

El módulo de gestión de archivos JSON se encuentra en **dos ubicaciones**:

### 1. **Panel Lateral (Sidebar)**
En la barra lateral izquierda, expander: **"📊 Tablas de Configuración"**

Aquí puedes:
- Ver resumen del diseño actual
- Guardar el diseño actual
- Cargar un diseño previo

### 2. **Pestaña "Gestión de Datos"** (si existe)
*(Opcional, dependiendo de la versión)*

Gestión avanzada con opciones adicionales de importación/exportación.

---

## 💾 GUARDAR UN DISEÑO (Crear archivo JSON)

### Paso a Paso

#### Paso 1: Completar tu Diseño

Antes de guardar, asegúrate de haber ingresado al menos:

- ✅ Nombre del proyecto
- ✅ Caudal de diseño
- ✅ Alturas geométricas (succión y descarga)
- ✅ Diámetros (succión e impulsión)
- ✅ Materiales de tubería

> **📝 Nota**: Puedes guardar en cualquier momento, incluso con el diseño incompleto. El JSON guardará el estado actual.

#### Paso 2: Abrir el Módulo de Guardado

1. Ve al **sidebar izquierdo**
2. Expande el panel **"📊 Tablas de Configuración"**
3. Busca la sección **"Guardar Diseño Actual"**

#### Paso 3: Configurar Nombre del Archivo

Verás dos opciones:

**Opción A: Guardar con nombre automático**
- Haz clic directamente en **"💾 Guardar Diseño"**
- El archivo se descargará con el nombre:
  ```
  Diseno_[NombreProyecto]_[Fecha].json
  ```
  Ejemplo: `Diseno_HospitalRegional_2026-01-11.json`

**Opción B: Guardar con nombre personalizado** (Recomendado)
1. Busca el campo de texto: **"Nombre del archivo (opcional)"**
2. Ingresa un nombre descriptivo:
   ```
   Alternativa_1_Bomba_KSB_125mm
   ```
3. Haz clic en **"💾 Guardar como..."**
4. El archivo se descargará: `Alternativa_1_Bomba_KSB_125mm.json`

#### Paso 4: Confirmar Descarga

- El archivo JSON se descargará automáticamente a tu carpeta de descargas
- Verás un mensaje de confirmación:
  ```
  ✅ Diseño guardado exitosamente
  📁 Archivo: Diseño_HospitalRegional_2026-01-11.json
  ```

### ¿Qué se Guarda en el Archivo JSON?

El archivo JSON contiene **absolutamente TODO** el estado de tu diseño:

#### 1. **Información del Proyecto**
- Nombre del proyecto
- Nombre del diseño
- Nombre del diseñador/ingeniero
- Fecha de creación
- Fecha de última modificación

#### 2. **Datos de Entrada**
- **Parámetros hidráulicos**:
  - Caudal de diseño y unidades (L/s o m³/h)
  - Altura geométrica de succión
  - Altura geométrica de descarga
- **Propiedades del fluido**:
  - Temperatura del agua
  - Densidad (calculada automáticamente)
  - Presión de vapor (calculada)
- **Ubicación del sitio**:
  - Elevación sobre el nivel del mar
  - Presión barométrica (calculada)

#### 3. **Configuración de Tuberías**
- **Tubería de Succión**:
  - Material seleccionado (PVC, HG, PEAD, etc.)
  - Diámetro nominal y diámetro interno
  - Longitud total
  - Rugosidad absoluta del material
  - Lista completa de accesorios (codos, válvulas, etc.)
- **Tubería de Impulsión**:
  - Mismo conjunto de datos que la succión

#### 4. **Curvas de la Bomba**
- **Puntos de la curva H-Q** (Caudal vs. Altura):
  - Todos los puntos ingresados manualmente o del catálogo
- **Puntos de la curva η-Q** (Eficiencia vs. Caudal)
- **Puntos de la curva P-Q** (Potencia vs. Caudal)
- **Puntos de la curva NPSHr-Q** (NPSH requerido vs. Caudal)
- **Coeficientes del ajuste polinomial** (grado 2 o 3)
- **BEP (Best Efficiency Point)**: Caudal, altura y eficiencia máxima

#### 5. **Resultados de Cálculos**
*(Si ya ejecutaste el botón "Calcular Sistema")*
- TDH (Total Dynamic Head) calculado
- Pérdidas de fricción en succión e impulsión
- Pérdidas secundarias por accesorios
- Velocidades en ambas líneas
- Punto de operación (Qop, Hop, ηop, Pop)
- NPSH disponible vs. requerido
- Margen de seguridad NPSH
- Potencia requerida y potencia del motor

#### 6. **Configuración VFD**
*(Si configuraste el Variador de Frecuencia)*
- RPM objetivo calculadas
- Porcentaje de velocidad (% de RPM nominales)
- Curvas ajustadas a la nueva velocidad
- Nuevo punto de operación con VFD
- Ahorro energético proyectado (kWh/año, $/año)
- Período de retorno de inversión (ROI)

#### 7. **Configuración de Optimización IA**
- Parámetros del algoritmo genético (población, generaciones)
- Resultados de la optimización (diámetros óptimos)
- Costos calculados (inversión vs. operación)

#### 8. **Tablas de Gráficos**
*(Datos para recrear gráficos)*
- Tablas completas de datos para gráficos 100% RPM
- Tablas completas de datos para gráficos VFD
- Configuración de ejes (rangos personalizados si los definiste)

#### 9. **Configuración de la Aplicación**
- Método de pérdidas seleccionado (Hazen-Williams o Darcy-Weisbach)
- Tipo de ajuste de curvas (polinomio grado 2 o 3)
- Unidades preferidas (L/s o m³/h)
- Otros parámetros de configuración global

### Tamaño Típico del Archivo

- **Diseño simple** (datos básicos): ~5-10 KB
- **Diseño completo** (con resultados y curvas): ~20-50 KB
- **Diseño con VFD y optimización**: ~50-100 KB

> **💡 Tip**: Los archivos JSON son muy pequeños, ¡puedes tener cientos sin problema de espacio!

---

## 📂 CARGAR UN DISEÑO (Abrir archivo JSON)

### Paso a Paso

#### Paso 1: Localizar tu Archivo JSON

Ubica el archivo JSON que guardaste previamente en tu computadora.

Ejemplo de nombre: `Diseño_HospitalRegional_2026-01-11.json`

#### Paso 2: Acceder al Módulo de Carga

1. Ve al **sidebar izquierdo**
2. Expande el panel **"📊 Tablas de Configuración"**
3. Busca la sección **"Cargar Diseño Previo"**

#### Paso 3: Subir el Archivo

1. Haz clic en el botón **"📁 Cargar Diseño desde JSON"**
2. Se abrirá un cuadro de diálogo del explorador de archivos
3. **Navega** hasta la carpeta donde guardaste el JSON
4. **Selecciona** el archivo `.json`
5. Haz clic en **"Abrir"**

#### Paso 4: Confirmación de Carga

El sistema procesará el archivo y mostrará un mensaje:

```
✅ Diseño cargado exitosamente
📊 Proyecto: Hospital Regional
👤 Diseñador: Ing. María González
📅 Fecha: 2026-01-11
🔧 Caudal diseño: 50.0 L/s
```

#### Paso 5: Verificación

**Todos los datos se restaurarán automáticamente**:

- ✅ Pestaña "Datos de Entrada": Todos los campos completados
- ✅ Pestaña "Análisis": Resultados precalculados (si existían)
- ✅ Pestaña "Análisis de Curvas": Gráficos recreados
- ✅ Configuración VFD (si existía)
- ✅ Resultados de optimización IA (si existían)

### ¿Qué Sucede con los Datos Actuales?

> **⚠️ ADVERTENCIA**: Al cargar un archivo JSON, **todo el diseño actual se sobrescribirá** con los datos del archivo cargado.

Si tenías trabajo sin guardar, **se perderá**. Por eso es importante:

1. **Guardar tu trabajo actual** antes de cargar otro diseño
2. **Usar nombres descriptivos** para identificar cada versión
3. **Crear versiones incrementales** (V1, V2, V3, etc.)

---

## ✏️ EDITAR UN ARCHIVO JSON MANUALMENTE

### ¿Cuándo Editar Manualmente?

En situaciones especiales, podrías querer editar el archivo JSON directamente:

- Corregir un dato sin abrir la aplicación
- Modificar múltiples valores en lote
- Migrar datos entre diferentes proyectos
- Depurar errores

> **⚠️ PRECAUCIÓN**: La edición manual requiere conocimientos técnicos. Un error de sintaxis puede corromper el archivo.

### Editores Recomendados

**Opción 1: Visual Studio Code** (Recomendado)
- Gratis y potente
- Resaltado de sintaxis JSON
- **Validación automática** de errores
- Descarga: https://code.visualstudio.com/

**Opción 2: Notepad++** (Windows)
- Ligero y rápido
- Plugin JSON Viewer disponible
- Descarga: https://notepad-plus-plus.org/

**Opción 3: Sublime Text**
- Editor de texto avanzado
- Soporte nativo JSON

**❌ NO USAR**:
- Notepad/Bloc de notas de Windows (puede corromper formato)
- Microsoft Word (agrega formato invisible)

### Procedimiento de Edición Segura

#### Paso 1: Crear Respaldo

**SIEMPRE** haz una copia de seguridad antes de editar:

```
📄 Diseño_HospitalRegional_2026-01-11.json  (original)
📄 Diseño_HospitalRegional_2026-01-11_RESPALDO.json  (copia)
```

#### Paso 2: Abrir con Editor

1. Click derecho sobre el archivo `.json`
2. **"Abrir con..."**
3. Selecciona **Visual Studio Code** o tu editor preferido

#### Paso 3: Localizar el Dato a Editar

El archivo JSON está estructurado jerárquicamente. Ejemplo:

```json
{
  "datos_entrada": {
    "hidraulicos": {
      "caudal_diseno": 50.0,     ← Aquí puedes cambiar el caudal
      "unidades_caudal": "L/s",
      "altura_succion": -2.5,    ← Aquí la altura de succión
      "altura_descarga": 28.0    ← Aquí la altura de descarga
    }
  }
}
```

#### Paso 4: Editar el Valor

**Reglas CRÍTICAS de sintaxis JSON**:

✅ **CORRECTO**:
```json
"caudal_diseno": 50.0,    ← Número sin comillas
"material_succion": "PVC", ← Texto CON comillas
```

❌ **INCORRECTO**:
```json
"caudal_diseno": "50.0",  ← NO poner números entre comillas (a menos que sea requerido)
"material_succion": PVC,  ← Texto SIN comillas (causará error)
"caudal_diseno": 50.0     ← Falta coma al final (error si no es el último)
```

#### Paso 5: Validar JSON

**Antes de guardar**, valida que el JSON sea correcto:

**Método 1: En Visual Studio Code**
- Si hay errores, verás subrayados rojos
- Pasa el mouse sobre el error para ver el problema

**Método 2: Validador Online**
- Copia todo el contenido del archivo
- Pega en: https://jsonlint.com/
- Haz clic en "Validate JSON"
- Si da error, corrige según el mensaje

#### Paso 6: Guardar

1. En el editor, `Archivo → Guardar` (o `Ctrl+S`)
2. **NO cambies la extensión** (debe seguir siendo `.json`)
3. **NO cambies la codificación** (debe ser UTF-8)

#### Paso 7: Probar en la Aplicación

1. Abre la aplicación de diseño de bombeo
2. Carga el JSON editado
3. Verifica que todos los campos se cargaron correctamente
4. Si hay error: restaura el respaldo y revisa qué salió mal

### Campos Más Comunes a Editar

| Campo | Ubicación en JSON | Ejemplo |
|-------|-------------------|---------|
| Caudal de diseño | `datos_entrada.hidraulicos.caudal_diseno` | `50.0` |
| Altura succión | `datos_entrada.hidraulicos.altura_succion` | `-2.5` |
| Diámetro succión | `tuberia_succion.diametro_nominal` | `100` |
| Material tubería | `tuberia_succion.material` | `"PVC"` |
| Nombre proyecto | `proyecto.nombre` | `"Hospital Regional"` |
| Temperatura agua | `datos_entrada.fluido.temperatura` | `20.0` |

---

## 🔄 RESPALDOS AUTOMÁTICOS vs. MANUALES

### Respaldos Automáticos

> **⚠️ IMPORTANTE**: La versión pública de la aplicación **NO tiene respaldos automáticos**. Streamlit no guarda datos entre sesiones.

Esto significa:
- ❌ Si cierras el navegador, los datos se pierden
- ❌ Si refrescas la página, los datos se pierden
- ❌ Si hay un error, los datos se pierden

**Solución**: **Guarda manualmente** tu diseño con frecuencia.

### Estrategia de Respaldos Manuales

#### 1. **Guardar al Iniciar** (Primera vez)

Apenas ingreses los datos básicos:
```
📄 Proyecto_Inicial_[Fecha].json
```

#### 2. **Guardar Después de Calcular**

Cuando completes los cálculos por primera vez:
```
📄 Diseño_Calculado_[Fecha].json
```

#### 3. **Guardar Después de Optimizar**

Si usaste el algoritmo genético:
```
📄 Diseño_Optimizado_IA_[Fecha].json
```

#### 4. **Guardar Versión Final**

Cuando el diseño esté completo y validado:
```
📄 Diseño_FINAL_[Proyecto]_[Fecha].json
```

#### 5. **Guardar Alternativas**

Si exploras diferentes opciones:
```
📄 Alternativa_A_Bomba_KSB.json
📄 Alternativa_B_Bomba_Grundfos.json
📄 Alternativa_C_Con_VFD.json
```

### Sistema de Versionado Recomendado

**Opción 1: Incremental**
```
Diseño_V1_2026-01-05.json
Diseño_V2_2026-01-08.json
Diseño_V3_2026-01-11.json
Diseño_FINAL_2026-01-12.json
```

**Opción 2: Descriptivo**
```
01_Prediseño_Inicial.json
02_Con_Diametros_Optimizados.json
03_Con_VFD_Configurado.json
04_Final_Aprobado_Cliente.json
```

**Opción 3: Por Fecha y Descripción**
```
2026-01-05_Inicial.json
2026-01-08_Optimizado.json
2026-01-11_Con_VFD.json
2026-01-12_FINAL.json
```

---

## 🔍 COMPARAR ALTERNATIVAS

### Método Manual

1. **Carga Alternativa 1**:
   - Cargar JSON: `Alternativa_A.json`
   - Ir a Reportes → Excel
   - Descargar: `Resultados_Alternativa_A.xlsx`

2. **Carga Alternativa 2**:
   - Cargar JSON: `Alternativa_B.json`
   - Ir a Reportes → Excel
   - Descargar: `Resultados_Alternativa_B.xlsx`

3. **Comparar en Excel**:
   - Abrir ambos archivos Excel
   - Crear una hoja de "Comparación"
   - Copiar datos clave de cada alternativa

Ejemplo de tabla comparativa:

| Criterio | Alternativa A | Alternativa B | Diferencia |
|----------|---------------|---------------|------------|
| **Caudal (L/s)** | 50.0 | 50.0 | - |
| **TDH (m)** | 32.5 | 31.8 | -0.7 m |
| **Eficiencia (%)** | 72.3 | 75.1 | +2.8% |
| **Potencia (kW)** | 23.8 | 22.1 | -1.7 kW |
| **Diámetro succión (mm)** | 100 | 125 | +25 mm |
| **Diámetro impulsión (mm)** | 80 | 80 | - |
| **NPSH margen (m)** | 4.3 | 5.8 | +1.5 m |
| **Costo tubería ($)** | 2,500 | 3,200 | +700 |
| **Costo energía ($/año)** | 4,800 | 4,200 | -600 |
| **Payback (años)** | - | 1.17 | ⭐ |

---

## ❓ PREGUNTAS FRECUENTES (FAQ)

### ❓ ¿Puedo abrir el JSON en Excel?

**R**: Excel puede abrir archivos JSON, pero **no es recomendable editarlos ahí** porque Excel puede alterar el formato. Usa un editor de texto como Visual Studio Code.

### ❓ ¿El JSON guarda los gráficos?

**R**: **No**. El JSON guarda los **datos numéricos** que permiten recrear los gráficos, pero no las imágenes. Los gráficos se regeneran automáticamente al cargar el JSON.

### ❓ ¿Puedo compartir el JSON con un colega?

**R**: ✅ **Sí, totalmente**. El JSON es independiente de tu computadora. Tu colega solo necesita:
1. Tener acceso a la aplicación (puede ser la versión pública online)
2. Cargar tu archivo JSON
3. ¡Listo! Verá exactamente tu diseño

### ❓ ¿Qué pasa si edito mal el JSON y lo corrompo?

**R**: Si al cargar el JSON la aplicación muestra error, significa que hay un error de sintaxis. Opciones:
1. Restaura el **respaldo** que hiciste antes de editar
2. Usa un **validador JSON** online para encontrar el error
3. Empieza de nuevo desde un JSON funcional

### ❓ ¿Los JSON de versiones antiguas funcionarán en versiones nuevas?

**R**: En general **sí**, pero con advertencias:
- Campos nuevos tendrán valores por defecto
- Campos eliminados se ignorarán
- Puede haber advertencias en la consola

**Recomendación**: Mantén los JSON con la versión de la app que los generó.

### ❓ ¿Puedo combinar datos de dos JSON diferentes?

**R**: No automáticamente. Pero podrías:
1. Abrir ambos JSON en Visual Studio Code
2. Copiar manualmente secciones de uno a otro
3. Validar y guardar
4. **MUY técnico** - solo para usuarios avanzados

### ❓ ¿Dónde está el JSON cuando lo descargo?

**R**: 
- **Windows**: Generalmente en `C:\Users\TuUsuario\Downloads\`
- **Mac**: `/Users/TuUsuario/Downloads/`
- **Linux**: `/home/TuUsuario/Downloads/`

Puedes moverlo a cualquier carpeta después de la descarga.

### ❓ ¿Cuántos diseños puedo guardar?

**R**: ¡Ilimitados! Cada archivo JSON es independiente. Solo estás limitado por el espacio en disco (pero son archivos muy pequeños).

---

## 💡 CONSEJOS PROFESIONALES

1. **Guarda frecuentemente**: Como mínimo, guarda después de cada **sesión de trabajo importante**.

2. **Nombres descriptivos**: Usa nombres que te permitan identificar fácilmente el diseño meses después:
   - ✅ `Hospital_Regional_Alternativa_B_Con_VFD_2026-01-11.json`
   - ❌ `diseno1.json`

3. **Carpetas organizadas**: Estructura tus proyectos:
   ```
   📁 Mis_Proyectos/
   ├── 📁 HospitalRegional/
   │   ├── 📁 Versiones/
   │   │   ├── V1.json
   │   │   ├── V2.json
   │   │   └── FINAL.json
   │   └── 📁 Reportes/
   ├── 📁 EdificioOficinas/
   └── 📁 PlantaIndustrial/
   ```

4. **Respaldo en la nube**: GitHub, Dropbox para almacenar versiones importantes.

5. **Documentación externa**: Crea un archivo `README.txt` en cada carpeta de proyecto explicando cada versión:
   ```
   PROYECTO: Hospital Regional - Sistema de Bombeo Principal
   
   V1 (2026-01-05): Diseño inicial con datos del cliente
   V2 (2026-01-08): Optimización con IA, diámetros ajustados
   V3 (2026-01-11): Configuración VFD agregada
   FINAL (2026-01-12): Diseño aprobado por cliente
   ```

---

## 📚 ESTRUCTURA TÉCNICA DEL JSON

### Esquema Jer árquico (Simplificado)

```json
{
  "metadata": {
    "version_app": "1.0",
    "fecha_creacion": "2026-01-11T10:30:00",
    "fecha_modificacion": "2026-01-11T15:45:00"
  },
  "proyecto": {
    "nombre": "...",
    "disenador": "...",
    "descripcion": "..."
  },
  "datos_entrada": {
    "hidraulicos": { ... },
    "fluido": { ... },
    "sitio": { ... }
  },
  "tuberia_succion": { ... },
  "tuberia_impulsion": { ... },
  "bomba": {
    "curvas": {
      "hq": [...],
      "eq": [...],
      "pq": [...],
      "npsh": [...]
    },
    "bep": { ... }
  },
  "resultados": { ... },
  "vfd": { ... },
  "optimizacion": { ... },
  "configuracion_app": { ... }
}
```

---

**Guía generada para la Tesis de Maestría en Ingeniería Hidrosanitaria - 2026**  
*Autor: Patricio Sarmiento Reinoso*  
*Sistema de Diseño de Bombeo con Inteligencia Artificial - Versión 1.0*
