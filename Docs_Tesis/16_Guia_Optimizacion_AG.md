# 🎯 Guía de Optimización Inteligente: Algoritmos Genéticos (AG)

Este módulo representa la frontera entre la **Inteligencia Artificial** y la **Ingeniería Hidráulica Senior**. Su objetivo es encontrar la combinación de materiales y diámetros de tubería que minimice el costo total del proyecto durante toda su vida útil.

---

## 🧬 Metáfora Darwiniana: De la Biología a las Tuberías

La **Optimización Inteligente** se basa en la Teoría de la Evolución de Charles Darwin. En lugar de resolver ecuaciones complejas de forma manual, el programa crea una "población" de diseños posibles y los hace evolucionar mediante **selección natural**.

### Cuadro de Equivalencias: IA vs. Ingeniería

| Concepto Biológico | Equivalente en Ingeniería de Sistemas de Bombeo |
| :--- | :--- |
| **Individuo** | Un diseño específico (ej: Succión PVC 200mm / Impulsión PEAD 160mm). |
| **Población** | Conjunto de 40 a 100 combinaciones de diseño analizadas simultáneamente. |
| **Cromosoma / ADN** | Los diámetros y materiales elegidos para ese diseño. |
| **Aptitud (Fitness)** | El **Costo Total (Inversión + Energía)**. Mientras menor es el costo, más "apto" es el diseño. |
| **Selección** | Los diseños más caros "mueren". Solo los económicos pasan a la siguiente generación. |
| **Mutación** | Cambios aleatorios en un diámetro para descubrir soluciones innovadoras. |

---

## ⚙️ Guía de Entradas (Inputs)

### 1. Parámetros de Diseño
*   **Caudal de Diseño (L/s):** El flujo que requerida la red. Es el motor principal de la fricción.
*   **Altura Estática Real (m):** Diferencia de nivel geométrica. Es un valor **constante** que la IA no puede cambiar.

### 2. Parámetros Económicos (Realismo Financiero)
*   **Costo Energía (USD/kWh):** Precio unitario de la electricidad.
*   **Años de Análisis (Vida Útil):** Generalmente 20 años. Es vital entender que la IA calcula el costo acumulado de 20 años de recibos de luz.
*   **Tasa de Descuento (%):** Representa el valor del dinero en el tiempo. Permite traer costos futuros (luz del año 15) al presente (**Valor Presente Neto - VPN**).

### 3. Parámetros Genéticos (Entrenamiento de la IA)
*   **Tamaño de Población:** Cuántos diseños explorar a la vez. (Sugerido: 40-60).
*   **Generaciones:** Cuántas veces el algoritmo "evolucionará" la solución. (Sugerido: 50-100).

---

## 💰 ¿Por qué los costos parecen elevados? (CAPEX vs. OPEX)

Es común que el **Costo de Vida Útil** mostrado ($300k - $500k) parezca irracionalmente alto comparado con el presupuesto de obra. La razón es técnica:

1.  **CAPEX (Inversión Inicial):** Es el costo de comprar y enterrar los tubos. Es un pago único.
2.  **OPEX (Gasto Operativo):** Es la suma de **20 años de facturas eléctricas**. 

> [!IMPORTANT]
> **Análisis Forense**: Si un sistema gasta $2,000 mensuales en luz, en 20 años habrá gastado **$480,000**. El Algoritmo Genético busca el diámetro que reduzca este gasto masivo, incluso si significa comprar un tubo un poco más caro al inicio. **El ahorro está en la eficiencia, no solo en la compra.**

---

## 📊 Interpretación de Gráficos

### A. Desglose de Costos (Barras)
*   **Barra Naranja (CAPEX):** Refleja la inversión inicial. 
*   **Barra Azul (OPEX):** Refleja el gasto energético.
*   **Interpretación:** Si la barra azul es dominante, significa que el diseño actual está perdiendo mucho dinero por fricción. La IA intentará aumentar el diámetro para achicar la barra azul.

### B. Evolución Genética (Convergencia)
*   Muestra cómo el costo bajó generación tras generación.
*   **Interpretación:** Si la curva se vuelve plana (asíntota), significa que la IA ya encontró la mejor solución posible y no hace falta correr más generaciones.

---

## 🔍 Análisis de Sensibilidad (Comparativa Manual)
Esta sección te permite "desafiar" a la IA. Puedes elegir un material o diámetro diferente y el programa te dirá exactamente cuántos miles de dólares **perderías** o ganarías en comparación con la solución óptima sugerida por el algoritmo.
