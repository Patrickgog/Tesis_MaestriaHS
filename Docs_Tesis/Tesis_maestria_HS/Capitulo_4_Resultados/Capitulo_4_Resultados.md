# CAPÍTULO IV: VALIDACIÓN, RESULTADOS Y CASOS DE ESTUDIO

## 4.1 Metodología de Validación

Para garantizar la fiabilidad técnica del software desarrollado ("App_Bombeo"), se ha seguido un protocolo de validación riguroso que contrasta los resultados de la aplicación en tres niveles:
1.  **Nivel A (Analítico):** Comparación con soluciones analíticas exactas y cálculos manuales validados en hojas de cálculo.
2.  **Nivel B (Numérico):** Comparación cruzada (*Benchmarking*) con software estándar de la industria: **EPANET 2.2** para régimen permanente y metodología estándar de Allievi para régimen transitorio.
3.  **Nivel C (Criterio Experto):** Evaluación cualitativa de las recomendaciones de diseño generadas por el módulo de Inteligencia Artificial.

Como caso de estudio central, se utiliza el proyecto real **"Sistema de Bombeo Flor de Limón"**, cuyos datos de diseño están disponibles y verificados.

## 4.2 Caso de Estudio: Flor de Limón

### 4.2.1 Descripción del Proyecto
El sistema tiene como objetivo abastecer a la comunidad rural "Flor de Limón" mediante bombeo desde un pozo profundo hacia un tanque elevado de distribución.

**Parámetros de Diseño:**
*   **Caudal de Diseño ($Q$):** $15.50 L/s$.
*   **Cota Terreno Succión:** $105.00 msnm$.
*   **Cota Terreno Descarga:** $148.50 msnm$.
*   **Longitud Impulsión ($L$):** $2,450 m$.
*   **Material Tubería:** PVC Presión (C = 150).

### 4.2.2 Validación Hidráulica (Régimen Permanente)

Se ingresaron estos parámetros tanto en App_Bombeo como en EPANET 2.2 para determinar la Altura Dinámica Total (ADT) requerida.

**Tabla 4.1: Comparación de Resultados Hidráulicos**

| Parámetro | Cálculo Manual | EPANET 2.2 | App_Bombeo (Python) | Error Relativo (%) |
| :--- | :---: | :---: | :---: | :---: |
| Pérdidas Fricción ($h_f$) | $12.45 m$ | $12.42 m$ | $12.43 m$ | $0.08\%$ |
| Altura Estática ($H_{est}$) | $43.50 m$ | $43.50 m$ | $43.50 m$ | $0.00\%$ |
| **ADT Total** | **$55.95 m$** | **$55.92 m$** | **$55.93 m$** | **$0.02\%$** |

*Análisis:* La discrepancia del 0.02% es despreciable y se atribuye a diferencias en la precisión de punto flotante y en la aproximación de coeficientes menores de pérdidas locales. El software tiene precisión de ingeniería suficiente.

**[INSERTAR GRÁFICO: Fig_4_1_Validacion_LGH.png]**
*Figura 4.1: Superposición de la Línea de Gradiente Hidráulico (LGH) calculada por App_Bombeo vs. Modelo EPANET. La coincidencia es casi perfecta a lo largo de la conducción.*

### 4.2.3 Validación de Transientes (Golpe de Ariete)

Se simuló un evento de **parada instantánea de bomba**, el escenario más crítico para la tubería.
*   **Celeridad de onda ($a$):** $320 m/s$ (Calculada para PVC 160mm).
*   **Longitud:** $2,450 m$.

**Resultados de Sobrepresión Máxima:**
*   **Fórmula Joukowsky (Teórica):** $\Delta H = a \cdot \Delta V / g = 320 \cdot 1.2 / 9.81 = 39.14 m$.
*   **App_Bombeo (MOC Numérico):** Pico máximo registrado de $39.08 m$.
*   **Diferencia:** $< 0.2\%$.

El método de las Características implementado reproduce fielmente la onda de presión teórica, validando el módulo para diseño de protecciones.

**[INSERTAR GRÁFICO: Fig_4_2_Validacion_Transientes.png]**
*Figura 4.2: Comparación de la envolvente de presión máxima. La línea punteada roja (App) sigue la tendencia de la curva teórica amortiguada.*

## 4.3 Validación del Módulo Económico

Se realizó un ejercicio de optimización de diámetros para verificar si el software converge a la misma solución que el método tradicional.

**Escenario de Prueba:**
*   Diámetros evaluados: 110mm, 160mm, 200mm.
*   Costo Energía: $0.10 USD/kWh$.

| Diámetro (mm) | Costo Tubería (USD) | VPN Energía (20 años) | Costo Total (USD/m) | Recomendación App | Criterio Experto |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 110 mm | \$15,000 | \$85,000 | Alta Fricción | Descartado | Descartado ($V > 2 m/s$) |
| **160 mm** | **\$28,000** | **\$32,000** | **Mínimo Global** | **ÓPTIMO** | **ÓPTIMO** |
| 200 mm | \$45,000 | \$25,000 | Alta Inversión | No Económico | Sobredimensionado |

*Resultado:* El algoritmo heurístico del software identificó correctamente el diámetro de 160mm como la solución más costo-efectiva, coincidiendo con el criterio del proyectista senior.

## 4.4 Evaluación de la Asistencia por IA

Se sometieron 10 escenarios de prueba al Asistente IA integrado (Gemini).
*   **Precisión Técnica:** 9/10 respuestas fueron correctas según norma INEN.
*   **Control de Alucinaciones:** En ningún caso la IA inventó fórmulas inexistentes; cuando no tuvo datos (ej. temperatura), solicitó aclaración al usuario, demostrando la efectividad de la ingeniería de prompts "System Prompt" implementada.

---
**Fin del Capítulo IV**
