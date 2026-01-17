# CAPÍTULO III: FUNCIONALIDAD Y GUÍA OPERATIVA DEL SOFTWARE

## 3.1 Descripción General de la Interfaz

La aplicación ha sido diseñada priorizando la experiencia del usuario ingeniero, ofreciendo un flujo de trabajo lineal y lógico que abarca desde la concepción del proyecto hasta la generación de entregables. La interfaz gráfica se estructura en un panel lateral de control y un área principal de visualización dinámica.

### 3.1.1 Panel de Configuración Lateral (Sidebar)
El panel izquierdo actúa como el centro de mando del proyecto. Permite al usuario:
1.  **Gestión de Archivos:** Cargar proyectos existentes (`.json`), guardar el estado actual o iniciar un diseño desde cero.
2.  **Parámetros Globales:** Definir variables del entorno físico como la temperatura del agua (que recalcula automáticamente viscosidad y densidad) y la altitud del proyecto (para correcciones de presión atmosférica).
3.  **Selección de Materiales:** Acceso a catálogos normalizados de tuberías (PVC, Acero, PEAD) con sus respectivas rugosidades absolutas y diámetros internos reales.

**[INSERTAR CAPTURA: Interfaz_General_Sidebar.png]**
*Figura 3.1: Vista general de la barra lateral de configuración y gestión de proyectos.*

## 3.2 Módulo de Diseño Hidráulico y Selección de Diámetros

Este módulo constituye la primera etapa del diseño. Su objetivo es determinar el diámetro óptimo de la tubería de impulsión y seleccionar el equipo de bombeo preliminar.

### 3.2.1 Entrada de Datos Geométricos
El usuario ingresa las elevaciones de los niveles de agua en la succión y descarga, así como las longitudes de tubería. El software valida instantáneamente la consistencia de los datos (ej. $Cota_{descarga} > Cota_{succión}$).

### 3.2.2 Análisis de Alternativas
Al presionar "Calcular", el sistema evalúa múltiples diámetros comerciales. Para cada uno, genera:
*   **Velocidad Media:** Se alerta si $V < 0.6 m/s$ (riesgo de sedimentación) o $V > 2.5 m/s$ (riesgo de golpe de ariete excesivo y altas pérdidas).
*   **Pérdidas de Carga ($H_f$):** Desglose de pérdidas por fricción y locales.
*   **ADT (Altura Dinámica Total):** $H_{estática} + \sum h_f$.
*   **Potencia Hidráulica:** $P = \gamma Q H / 75$.

El software resalta automáticamente la opción "Económica", pero permite al ingeniero forzar la selección de otro diámetro según su criterio experto.

**[INSERTAR CAPTURA: Tabla_Resultados_Diametros.png]**
*Figura 3.2: Tabla comparativa de diámetros analizados con indicación de velocidades y pérdidas.*

## 3.3 Módulo de Análisis de Succión y NPSH

Dada la criticidad de la succión en bombas centrífugas, se ha dedicado una pestaña exclusiva para este análisis.

### 3.3.1 Verificación de Cavitación
El módulo calcula el **NPSH Disponible** considerando:
1.  **Presión Barométrica:** Ajustada por la altitud ingresada.
2.  **Presión de Vapor:** Ajustada por la temperatura del agua.
3.  **Sumergencia Mínima:** Calcula la altura mínima de agua requerida sobre la boca de succión para evitar la formación de vórtices, utilizando la fórmula del Instituto Hidráulico: $S = D (1 + 2.3 Fr)$.

El sistema genera una gráfica de "Margen de Seguridad de NPSH" a lo largo de todo el rango de caudales posibles.

**[INSERTAR CAPTURA: Grafico_NPSH_App.png]**
*Figura 3.3: Interfaz de análisis de NPSH mostrando el margen disponible vs requerido.*

## 3.4 Módulo Avanzado de Transientes (Golpe de Ariete)

Este módulo permite simular el comportamiento dinámico del sistema ante eventos de parada de bomba, que es el escenario más crítico.

### 3.4.1 Configuración de la Simulación
El usuario define:
*   **Celeridad de la Onda ($a$):** Puede ser calculada automáticamente por el software según el material y espesor de la tubería o ingresada manualmente.
*   **Momento de Inercia ($WR^2$):** Del grupo motor-bomba, crucial para determinar la rampa de desaceleración.
*   **Tiempo de Simulación:** Duración total del evento a analizar.

### 3.4.2 Visualización de Resultados
El software genera las "Envolventes de Presión Máxima y Mínima" a lo largo del perfil de la conducción.
*   **Línea Roja (Piezométrica Máxima):** Indica las sobrepresiones. Si supera la presión nominal de la tubería, el sistema alerta de riesgo de estallido.
*   **Línea Azul (Piezométrica Mínima):** Indica las subpresiones. Si la línea cruza el perfil de la tubería (presiones negativas), existe riesgo inminente de aplastamiento o cavitación de la tubería.

**[INSERTAR CAPTURA: Envolventes_Presion.png]**
*Figura 3.4: Envolventes de presión máxima y mínima a lo largo de la conducción generadas por el modelo de Allievi.*

## 3.5 Módulo de Evaluación Económica

Permite realizar un análisis de "Ciclo de Vida" del proyecto.
El usuario ingresa:
*   Costo de la energía eléctrica ($/kWh$).
*   Horas de operación diaria.
*   Tasa de descuento anual.
*   Vida útil del proyecto.

El sistema proyecta los flujos de caja y determina el Valor Presente Neto (VPN) de la operación, facilitando la toma de decisiones entre una tubería más económica (menor inversión inicial) versus una más eficiente (menor costo operativo).

## 3.6 Asistente Inteligente (Integración AI)

El botón "Consultar AI Assistant" activa el análisis contextual.
1.  **Diagnóstico Automático:** La IA lee los resultados (velocidades, presiones, NPSH) y genera un resumen ejecutivo. *Ejemplo: "El sistema opera de manera eficiente, pero el margen de NPSH es de solo 0.3m, lo cual es riesgoso según norma HI 9.6.1".*
2.  **Consultas Abiertas:** El usuario puede preguntar directivas específicas, como "¿Qué tipo de válvula de aire recomiendas para el punto alto en la abscisa 1+200?".

Esta funcionalidad transforma al software de una simple calculadora a un asistente de diseño integral.

---
**Fin del Capítulo III**
