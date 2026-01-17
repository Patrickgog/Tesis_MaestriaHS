# 7. Diseño del Esquema y Funcionalidades de la Interfaz Gráfica de Usuario (GUI)

## Documento Técnico - Tesis de Maestría en Hidrosanitaria

### Resumen Ejecutivo

Este documento presenta el diseño conceptual y funcional de la interfaz gráfica de usuario (GUI), sus principios de usabilidad, wireframes, flujos de trabajo y decisiones de diseño UX/UI que guiaron el desarrollo de la aplicación.

---

## 1. PRINCIPIOS DE DISEÑO UX/UI

### 1.1 Objetivos de Usabilidad

**Audiencia objetivo**:
- Ingenieros civiles/hidráulicos (primaria)
- Estudiantes de ingeniería (secundaria)
- Técnicos de mantenimiento (terciaria)

**Metas de experiencia**:
1. **Intuitivo**: Ingeniero puede usar sin manual en < 10 min
2. **Autoguiado**: Tooltips y ayuda contextual en cada paso
3. **Visual**: Resultados gráficos inmediatos, no solo números
4. **Confiable**: Validaciones en tiempo real previenen errores
5. **Eficiente**: Diseño completo en 15-30 min vs 5-10 horas manual

### 1.2 Principios de Nielsen (Usabilidad)

✅ **Visibilidad del estado del sistema**: Progress bars, spinners, mensajes de confirmación  
✅ **Coincidencia con el mundo real**: Terminología ingenieril estándar (TDH, NPSH, VFD)  
✅ **Control y libertad del usuario**: Deshacer cambios, guardar múltiples versiones  
✅ **Consistencia**: Mismos controles en toda la app  
✅ **Prevención de errores**: Validación inputs, restricciones en campos numéricos  
✅ **Reconocimiento vs recuerdo**: Labels claros, valores por defecto razonables  
✅ **Flexibilidad**: Modo básico y avanzado  
✅ **Diseño minimalista**: Sin información irrelevante  
✅ **Ayuda**: Tooltips, documentación integrada  
✅ **Recuperación de errores**: Mensajes claros si algo falla  

---

## 2. ARQUITECTURA DE NAVEGACIÓN

### 2.1 Estructura de la Aplicación

```
┌──────────────────────────────────────────────────┐
│            🌐 VERSIÓN PÚBLICA                    │
│               Banner Superior                     │
└──────────────────────────────────────────────────┘
┌──────────────┬───────────────────────────────────┐
│              │                                   │
│   SIDEBAR    │         ÁREA PRINCIPAL            │
│  (Controles) │      (Contenido Dinámico)         │
│              │                                   │
│ • Análisis IA│    ┌─────────────────────────┐    │
│ • Optimiza IA│    │  📊 Pestaña Activa      │    │
│ • Config     │    │                         │    │
│ • Herramient │    │  [Contenido aquí]       │    │
│              │    │                         │    │
│              │    └─────────────────────────┘    │
│              │                                   │
│ [Widgets]    │    [Tabs: Datos│Análisis│...]    │
│              │                                   │
└──────────────┴───────────────────────────────────┘
```

### 2.2 Sistema de Pestañas (Tabs)

**Tabs habilitados por defecto (versión pública)**:
1. 📊 **Entrada de Datos**
2. 📈 **Análisis**
3. 🔍 **Selección Técnica de Diámetros**
4. 📄 **Reportes**

**Tabs opcionales** (activables desde sidebar):
5. 🎯 **Optimización IA (GA)** - Algoritmo genético
6. ⚡ **Análisis Transitorios** - Golpe de ariete (modo desarrollador)
7. 📈 **Simulación Operativa** - Análisis 24h (modo desarrollador)

---

## 3. WIREFRAMES DETALLADOS

### 3.1 Pestaña: 📊 Entrada de Datos

```
┌────────────────────────────────────────────────────────────┐
│ 📊 ENTRADA DE DATOS                                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ▼ 1. Identificación del Proyecto                          │
│ ┌──────────────┬──────────────┬───────────────────┐       │
│ │ Proyecto:    │ Diseño:      │ Elevación [msnm]: │       │
│ │ [_________]  │ [________]   │ [____450____]     │       │
│ └──────────────┴──────────────┴───────────────────┘       │
│                                                            │
│ ▼ 2. Parámetros Hidráulicos Fundamentales                 │
│ ┌────────────────┬─────────────┬──────────┬──────────┐    │
│ │ Caudal:        │ Unidad:     │ Altura   │ Altura   │    │
│ │ [____75___] ●L/s│             │ Succión: │ Descarga:│    │
│ │             ○m³/h│             │ [__-2__] │ [__45__] │    │
│ └────────────────┴─────────────┴──────────┴──────────┘    │
│                                                            │
│ ▼ 3. Línea de Succión                                     │
│ ┌──────────┬─────────┬──────────┬──────────────────┐      │
│ │ Long [m] │ Diam mm │ Material │ Accesorios       │      │
│ │ [__15__] │ [_75__] │[PVC ▼]   │[+ Agregar]       │      │
│ └──────────┴─────────┴──────────┴──────────────────┘      │
│                                                            │
│ 📋 Tabla Accesorios:                                       │
│ ┌─────────────────┬──────────┬────────┐                   │
│ │ Tipo            │ Cantidad │ Acción │                   │
│ ├─────────────────┼──────────┼────────┤                   │
│ │ Codo 90°        │    3     │  [🗑]  │                   │
│ │ Válvula check   │    1     │  [🗑]  │                   │
│ │ Entrada brusca  │    1     │  [🗑]  │                   │
│ └─────────────────┴──────────┴────────┘                   │
│                                                            │
│ ▼ 4. Línea de Impulsión                                   │
│ [Similar a succión]                                        │
│                                                            │
│ ▼ 5. Propiedades del Fluido                               │
│ ┌───────────────┬──────────────────────────────────┐      │
│ │ Temperatura:  │ Presión vapor calculada:         │      │
│ │ [__20__] °C   │ 📊 0.24 m.c.a                    │      │
│ │ Densidad:     │ Presión barométrica calculada:   │      │
│ │ [_1.0_] g/cm³ │ 📊 9.55 m.c.a (elevación 450m)   │      │
│ └───────────────┴──────────────────────────────────┘      │
│                                                            │
│ ▼ 6. Curvas Características de la Bomba                   │
│ Modo: ●3 puntos  ○Excel                                   │
│                                                            │
│ ┌─────────────────────────────────────────────┐           │
│ │ Curva H-Q (Bomba):                          │           │
│ │ ┌────────────────────────────────────────┐  │           │
│ │ │ Q [L/s]    H [m]                       │  │           │
│ │ │ 0          120                          │  │           │
│ │ │ 50         110                          │  │           │
│ │ │ 100        85                           │  │           │
│ │ │ 150        45                           │  │           │
│ │ └────────────────────────────────────────┘  │           │
│ └─────────────────────────────────────────────┘           │
│                                                            │
│            [💾 Guardar Proyecto] [📊 Calcular]            │
└────────────────────────────────────────────────────────────┘
```

### 3.2 Pestaña: 📈 Análisis

```
┌────────────────────────────────────────────────────────────┐
│ 📈 ANÁLISIS - RESULTADOS                                   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ┌────────────┬──────────────────────┬──────────────────┐  │
│ │ COLUMNA 1  │     COLUMNA 2        │    COLUMNA 3     │  │
│ │ Resultados │ Gráficos 100% RPM    │ Gráficos VFD     │  │
│ │            │                      │                  │  │
│ │ 📊 TDH     │ ═════════ Curvas: ════│ ══ VFD Curves ═══│  │
│ │ 45.3 m     │    │                 │                  │  │
│ │            │120 │    /╲           │    ╱──╲──╲── 100%│  │
│ │ ⭐ Pto Op: │    │   /  ╲  Bomba   │   ╱    ╲ 80%     │  │
│ │ Q: 75.2 L/s│  H │  /Sistema ╲     │  ╱60%  ╲ 40%    │  │
│ │ H: 45.3 m  │    │ /         ╲     │                  │  │
│ │ η: 72.5%   │  0 └──────────────   │                  │  │
│ │ P: 52.1 kW │      Q────→          │   Q────→         │  │
│ │            │                      │                  │  │
│ │ 💧 NPSH    │ ══ Eficiencia: ══    │ ══ Ahorro        │  │
│ │ Disp: 5.8m │    │                 │    Energético ═══ │  │
│ │ Req:  3.2m │ η% │    ╱──╲         │                  │  │
│ │ ✅ 2.6m OK │    │   /    ╲        │  35% ahorro anual│  │
│ │            │    │  /      ╲       │  VFD @ 60% RPM   │  │
│ │ ⚡ Estado  │  0 └──────────────   │                  │  │
│ │ ✅ SEGURO  │      Q────→          │  $4,200/año      │  │
│ │            │                      │                  │  │
│ └────────────┴──────────────────────┴──────────────────┘  │
│                                                            │
│ 📋 DIAGNÓSTICO AUTOMATIZADO:                               │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ ✅ Diseño APROBADO - Sistema cumple todos los criterios││ │
│ │                                                        ││ │
│ │ • Velocidad succión: 0.85 m/s ✓ (rango 0.6-1.5)       ││ │
│ │ • Velocidad impulsión: 1.93 m/s ✓ (rango 1.0-2.5)     ││ │
│ │ • NPSH margen: 2.6 m ✓ (> 1.5m requerido)             ││ │
│ │ • Eficiencia bomba: 72.5% ✓ (> 65% objetivo)          ││ │
│ │                                                        ││ │
│ │ 💡 RECOMENDACIÓN ENERGÉTICA:                           ││ │
│ │ Considerar VFD para operación variable - Ahorro 35%   ││ │
│ │ Payback estimado: 2.1 años                            ││ │
│ └────────────────────────────────────────────────────────┘ │
│                                                            │
│         [📄 Generar Reporte PDF] [💾 Guardar Resultados]  │
└────────────────────────────────────────────────────────────┘
```

### 3.3 Pestaña: 🔍 Selección Técnica de Diámetros

```
┌────────────────────────────────────────────────────────────┐
│ 🔍 SELECCIÓN TÉCNICA DE DIÁMETROS                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ 📊 Comparativa Diámetros Comerciales - SUCCIÓN:           │
│                                                            │
│ ┌──────┬────────┬─────────┬────────┬──────────────────┐   │
│ │  D   │  Vel.  │ Pérdidas│  Costo │ Recomendación    │   │
│ │ [mm] │ [m/s]  │   [m]   │  [USD] │                  │   │
│ ├──────┼────────┼─────────┼────────┼──────────────────┤   │
│ │  50  │ 🔴3.82 │  25.2   │   450  │ ⛔ Velocidad alta│   │
│ │  63  │ 🟡1.93 │  9.8    │   550  │ ⚠️ Aceptable     │   │
│ │  75  │ 🟢0.85 │  3.5    │   680  │ ✅ ÓPTIMO        │   │
│ │  90  │ 🟢0.60 │  1.2    │   820  │ ⚠️ Sobredimen.   │   │
│ │ 110  │ 🟢0.40 │  0.4    │  1050  │ ⚠️ Sobredimen.   │   │
│ └──────┴────────┴─────────┴────────┴──────────────────┘   │
│                                                            │
│ 📈 Gráfico: Pérdidas vs Diámetro                           │
│ ┌────────────────────────────────────────────────────┐     │
│ │  hf│                                               │     │
│ │  25├─╲                                            │     │
│ │  20│  ╲   🔴 Zona Roja                            │     │
│ │  15│   ╲  (Velocidad/Pérdidas altas)              │     │
│ │  10│    ╲──╲ 🟡 Zona Transición                   │     │
│ │   5│        ╲__🟢 ✅Zona Verde (Óptimo)           │     │
│ │   0└────────────────────────────────────           │     │
│ │      50  63  75  90  110  D[mm]→                  │     │
│ └────────────────────────────────────────────────────┘     │
│                                                            │
│ 🤖 [Optimizar con IA] ← Algoritmo genético encuentra      │
│                          diámetro óptimo automáticamente   │
│                                                            │
│ 🔬 Análisis Detallado - Diámetro seleccionado: 75mm       │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Reynolds: 127,500 (Turbulento)                         ││ │
│ │ Factor fricción (f): 0.0195                            ││ │
│ │ Pérdidas primarias: 2.8 m                              ││ │
│ │ Pérdidas secundarias: 0.7 m                            ││ │
│ │ Coef. K total accesorios: 5.2                          ││ │
│ │                                                        ││ │
│ │ ✅ Cumple criterioos HI 9.6.1                           ││ │
│ └────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## 4. PALETA DE COLORES Y TIPOGRAFÍA

### 4.1 Esquema de Colores (Streamlit Default Enhanced)

**Colores semáforo para validaciones**:
```css
Verde éxito:    #00D26A  /* Diseño aprobado */
Amarillo warn:  #FFB800  /* Advertencias */
Rojo peligro:   #FF4B4B  /* Errores críticos */
Azul info:      #1E88E5  /* Información neutral */
Gris subtle:    #808495  /* Texto secundario */
```

### 4.2 Tipografía

**Primary**: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto  
**Monospace**: "Source Code Pro", Consolas, monospace (para números y código)

---

## 5. INTERACTIVIDAD Y FEEDBACK

### 5.1 Estados de Carga

**Spinner con mensaje**:
```python
with st.spinner('🧮 Calculando pérdidas de carga...'):
    resultados = calcular()
```

**Progress bar para optimización**:
```python
progress_bar = st.progress(0)
for gen in range(200):
    # ... algoritmo genético
    progress_bar.progress((gen+1)/200)
```

### 5.2 Mensajes de Validación

**Sistema de alertas en tiempo real**:
- `st.success("✅ Cálculo completado exitosamente")`
- `st.warning("⚠️ NPSH margen bajo")`
- `st.error("❌ Velocidad excede límite permitido")`
- `st.info("ℹ️ Sugerencia: Considerar diámetro mayor")`

---

## 6. RESPONSIVE DESIGN

### 6.1 Adaptación a Pantallas

**Desktop (>1200px)**: 3 columnas  
**Tablet (768-1200px)**: 2 columnas  
**Mobile (< 768px)**: 1 columna (limitado en Streamlit)

**Nota**: Streamlit está optimizado para desktop primero.

---

## 7. CONCLUSIONES DEL DISEÑO UX/UI

### 7.1 Decisiones Clave

✅ **Sidebar colapsable** - Maximiza espacio gráficos  
✅ **Tabs sobre multi-página** - Navegación más rápida  
✅ **Validación en tiempo real** - Previene errores  
✅ **Visualización prioritaria** - Gráficos > Tablas > Texto  
✅ **Tooltips omnipresentes** - Ayuda contextual siempre disponible  

### 7.2 Mejoras Futuras (Roadmap)

1. **Dark mode** - Para uso prolongado
2. **Dashboard personalizable** - Arrastrar/soltar widgets
3. **Comparación lado a lado** - Múltiples diseños simultáneos
4. **Export interactivo HTML** - Reportes autocontenidos

---

**Autor**: Equipo UX/UI - Tesis Maestría Hidrosanitaria  
**Fecha**: Enero 2026  
**Herramientas**: Figma (wireframes), Streamlit Components (implementación)
