# CAPÍTULO I: MARCO TEÓRICO Y FUNDAMENTOS DE SISTEMAS DE BOMBEO

## 1.1 Introducción a la Hidráulica de Sistemas a Presión

El diseño de sistemas de abastecimiento de agua potable mediante bombeo requiere una comprensión profunda de los principios fundamentales de la mecánica de fluidos incompresibles. A diferencia de los modelos simplificados, la ingeniería de detalle debe considerar no solo el estado estacionario, sino también los fenómenos transitorios y la interacción no lineal entre los componentes del sistema.

### 1.1.1 Ecuación de la Energía y Línea de Gradiente Hidráulico

El principio de conservación de la energía en un flujo permanente e incompresible se expresa mediante la ecuación de Bernoulli generalizada, que relaciona la energía de posición, presión y velocidad entre dos secciones de control. Para un volumen de control entre un punto de succión (S) y un punto de descarga (D), la ecuación se formula como:

$$ \frac{P_S}{\gamma} + z_S + \frac{V_S^2}{2g} + H_B = \frac{P_D}{\gamma} + z_D + \frac{V_D^2}{2g} + \sum h_{f_{S-D}} + \sum h_{loc_{S-D}} $$

**Donde:**
*   $P/\gamma$: Carga de presión o altura piezométrica $[m]$.
*   $z$: Carga de posición o altura geodésica respecto a un plano de referencia (DATUM) $[m]$.
*   $V^2/2g$: Carga de velocidad o altura cinética $[m]$.
*   $H_B$: Altura Dinámica Total (ADT) añadida por el equipo de bombeo al fluido $[m]$.
*   $\sum h_f$: Sumatoria de pérdidas de carga por fricción a lo largo de la conducción $[m]$.
*   $\sum h_{loc}$: Sumatoria de pérdidas locales o menores debidas a accesorios $[m]$.
*   $\gamma$: Peso específico del agua ($9810 N/m^3$ a 20°C).
*   $g$: Aceleración de la gravedad ($9.81 m/s^2$).

La **Línea de Gradiente Hidráulico (LGH)** representa la suma de las energías potencial y de presión ($\frac{P}{\gamma} + z$) a lo largo de la tubería. Es imperativo que, en condiciones normales de operación, la LGH se mantenga por encima del perfil de la tubería para evitar presiones negativas que podrían inducir cavitación o intrusión de contaminantes.

### 1.1.2 Modelos Matemáticos para Pérdidas por Fricción

La correcta estimación de las pérdidas por fricción es crítica para determinar la potencia requerida. Aunque existen diversas formulaciones empíricas, este proyecto prioriza el uso de la ecuación de **Darcy-Weisbach** debido a su fundamentación física y aplicabilidad general, complementada por la ecuación de Hazen-Williams para validaciones rápidas en tuberías de agua.

#### A. Ecuación de Darcy-Weisbach
Es la formulación teóricamente más exacta para flujos a presión:

$$ h_f = f \cdot \frac{L}{D_{int}} \cdot \frac{V^2}{2g} $$

**Donde:**
*   $h_f$: Pérdida de carga por fricción $[m]$.
*   $f$: Factor de fricción de Darcy (adimensional), función del Número de Reynolds ($Re$) y la rugosidad relativa ($\epsilon/D$).
*   $L$: Longitud de la tubería $[m]$.
*   $D_{int}$: Diámetro interno real de la conducción $[m]$.
*   $V$: Velocidad media del flujo $[m/s]$.

Para la determinación del factor de fricción $f$ en régimen turbulento ($Re > 4000$), se utiliza la ecuación implícita de **Colebrook-White**:

$$ \frac{1}{\sqrt{f}} = -2 \log_{10} \left( \frac{\epsilon/D}{3.7} + \frac{2.51}{Re\sqrt{f}} \right) $$

**Donde:**
*   $\epsilon$: Rugosidad absoluta de la pared interna del tubo $[m]$ (ej. $1.5 \times 10^{-6} m$ para PVC).
*   $Re$: Número de Reynolds, $Re = \frac{V \cdot D}{\nu}$.
*   $\nu$: Viscosidad cinemática del agua ($1.004 \times 10^{-6} m^2/s$ a 20°C).

Dado que Colebrook-White requiere solución iterativa, en el desarrollo computacional de este proyecto se implementan aproximaciones explícitas de alta precisión como la de **Swamee-Jain (1976)** para optimizar el tiempo de cálculo sin sacrificar exactitud ingenieril.

#### B. Ecuación de Hazen-Williams
Ampliamente utilizada en la ingeniería sanitaria norteamericana para agua a temperatura ambiente:

$$ h_f = \frac{10.67 \cdot L \cdot Q^{1.852}}{C^{1.852} \cdot D^{4.87}} $$

**Donde:**
*   $Q$: Caudal $[m^3/s]$.
*   $C$: Coeficiente de rugosidad de Hazen-Williams (ej. 150 para PVC, 140 para PEAD).

El software desarrollado permite al usuario seleccionar entre ambos métodos, recomendando Darcy-Weisbach para cálculos de golpe de ariete y sistemas de alta presión.

## 1.2 Teoría de Bombas Centrifugas

Las bombas centrífugas son turbomáquinas que transforman energía mecánica en energía hidráulica mediante la acción de la fuerza centrífuga. Su comportamiento no es constante, sino que depende de las condiciones del sistema hidráulico al que están acopladas.

### 1.2.1 Curvas Características

La operación de una bomba se describe mediante sus curvas características, las cuales relacionan el caudal ($Q$) con otras variables fundamentales. Estas curvas son provistas por el fabricante mediante pruebas de banco.

1.  **Curva Caudal vs. Altura (Q-H):** Describe la energía por unidad de peso que la bomba entrega al fluido para un caudal dado. Tiene una pendiente negativa; a mayor caudal, menor altura dinámica entregada. Se modela matemáticamente como un polinomio de segundo orden:
    $$ H_{bomba} = A - B \cdot Q^2 $$
    Donde $A$ representa la altura a válvula cerrada (Shut-off head).

2.  **Curva de Eficiencia ($\eta$):** Muestra el rendimiento de la conversión de energía. Presenta un máximo en el Punto de Mejor Eficiencia (BEP).
    $$ \eta = \frac{P_{hid}}{P_{freno}} = \frac{\gamma \cdot Q \cdot H}{76 \cdot HP_{motor}} $$

3.  **Curva de Potencia (P):** Indica la potencia al freno (BHP) requerida en el eje de la bomba.

### 1.2.2 Punto de Operación del Sistema

El punto de operación se obtiene mediante la intersección de la **Curva del Sistema** y la **Curva de la Bomba**. La curva del sistema representa la energía necesaria para transportar un caudal $Q$ desde la succión hasta la descarga y viene dada por:

$$ H_{sistema} = H_{estática} + K \cdot Q^2 $$

**Donde:**
*   $H_{estática}$: Desnivel geométrico total ($z_D - z_S$) más la diferencia de presión residual requerida.
*   $K$: Coeficiente de resistencia global, que agrupa todas las pérdidas por fricción y locales ($K = \sum R_{fricción} + \sum R_{locales}$).

**[INSERTAR GRÁFICO: Fig_1_1_Punto_Operacion.png]**
*Figura 1.1: Representación gráfica del Punto de Operación como la intersección entre la curva motriz de la bomba y la curva resistente del sistema. Se observa también la variación de la eficiencia.*

El software desarrollado calcula iterativamente este punto para asegurar que la bomba seleccionada opere cerca de su BEP, garantizando la eficiencia energética y la longevidad del equipo.

## 1.3 Fenómeno de Cavitación y NPSH

La cavitación es uno de los problemas más destructivos en sistemas de bombeo. Ocurre cuando la presión absoluta del líquido en cualquier punto de la bomba (generalmente en el ojo del impulsor) desciende por debajo de su presión de vapor ($P_v$), provocando la formación de burbujas de vapor que colapsan violentamente al entrar en zonas de mayor presión.

### 1.3.1 NPSH Disponible (NPSHa) vs. NPSH Requerido (NPSHr)

Para evitar la cavitación, es condición necesaria y suficiente que:

$$ NPSH_a > NPSH_r + Margen_{seguridad} $$

Normalmente se recomienda un margen de seguridad de al menos 0.5 m o 10% del $NPSH_r$.

*   **NPSH Requerido ($NPSH_r$):** Es una característica intrínseca de la bomba, determinada por el fabricante. Depende del diseño del impulsor y aumenta con el caudal.
*   **NPSH Disponible ($NPSH_a$):** Depende exclusivamente del diseño del sistema de succión y las condiciones atmosféricas. Se calcula como:

$$ NPSH_a = \frac{P_{atm}}{\gamma} - \frac{P_v}{\gamma} - h_{s_g} - h_{f_s} $$

**Donde:**
*   $P_{atm}/\gamma$: Altura de presión atmosférica local. Disminuye con la altitud sobre el nivel del mar.
    $$ P_{atm(m)} = 10.33 - \frac{Altitud}{900} \quad (Aproximación) $$
*   $P_v/\gamma$: Presión de vapor del agua (depende de la temperatura).
*   $h_{s_g}$: Altura geométrica de succión (positiva si la bomba está por encima del nivel del agua, "succión negativa").
*   $h_{f_s}$: Pérdidas por fricción en la línea de succión.

El desarrollo de este software incluye un módulo específico que corrige la presión atmosférica según la altitud del proyecto y verifica el riesgo de cavitación en todo el rango operativo.

**[INSERTAR GRÁFICO: Fig_1_3_Analisis_NPSH.png]**
*Figura 1.2: Análisis de cavitación mostrando la relación entre el NPSH disponible del sistema y el NPSH requerido por la bomba. La zona sombreada indica riesgo de cavitación.*

## 1.4 Transientes Hidráulicos (Golpe de Ariete)

El golpe de ariete es un fenómeno oscilatorio de ondas de presión causado por cambios bruscos en la velocidad del flujo (cierre de válvulas, parada de bombas). Si no se controla, puede generar sobrepresiones que revienten tuberías o subpresiones que las colapsen.

### 1.4.1 Celeridad de la Onda ($a$)

La velocidad de propagación de la onda de presión, o celeridad, depende de la elasticidad del fluido y de la tubería. Se calcula según la fórmula de Zhukovsky generalizada:

$$ a = \frac{\sqrt{K_{bulk}/\rho}}{\sqrt{1 + \left( \frac{K_{bulk}}{E} \right) \left( \frac{D}{e} \right) \cdot \phi}} $$

**Donde:**
*   $K_{bulk}$: Módulo de elasticidad volumétrico del agua ($~2.2 \times 10^9 Pa$).
*   $\rho$: Densidad del agua ($1000 kg/m^3$).
*   $E$: Módulo de elasticidad (Young) del material de la tubería (ej. PVC: $3.0 \times 10^9 Pa$).
*   $D$: Diámetro de la tubería.
*   $e$: Espesor de pared de la tubería.
*   $\phi$: Factor de anclaje de la tubería (usualmente 1.0 para juntas con empaque).

### 1.4.2 Fases del Golpe de Ariete (Teoría de Allievi)

L. Allievi desarrolló la teoría de la columna elástica, que discretiza el fenómeno en intervalos de tiempo $2L/a$.
La sobrepresión máxima directa ($\Delta H$) ante un cierre instantáneo ($T_c < 2L/a$) viene dada por la ecuación de Joukowsky:

$$ \Delta H = \frac{a \cdot \Delta V}{g} $$

Si el tiempo de cierre es mayor ($T_c > 2L/a$), la sobrepresión se reduce (cierre lento). El software utiliza el **Método de las Características (MOC)** para resolver numéricamente las ecuaciones diferenciales parciales de flujo no permanente, permitiendo simular escenarios complejos como el paro por falla eléctrica.

## 1.5 Ingeniería Económica y Optimización de Diámetros

El diseño óptimo no es solo el que funciona hidráulicamente, sino el que minimiza el costo a lo largo de la vida útil del proyecto.

### 1.5.1 Fórmula del Diámetro Económico (Bresse y Variantes)

Tradicionalmente se usaba la fórmula de Bresse: $D = k \sqrt{Q}$. Sin embargo, esta es estática y no considera costos actuales. El enfoque moderno requiere un análisis de **Valor Presente Neto (VPN)** de costos totales ($CT$):

$$ CT = C_{inversión} + VPN(C_{operación}) $$

1.  **Costo de Inversión:** Aumenta con el diámetro ($D$). Tuberías más grandes son más caras.
2.  **Costo de Operación (Energía):** Disminuye drásticamente con el diámetro. Al aumentar $D$, disminuyen las pérdidas por fricción ($h_f \propto 1/D^5$), reduciendo la potencia requerida y el consumo eléctrico.

El **Diámetro Económico** es aquel que minimiza la suma de estos dos costos opuestos.

**[INSERTAR GRÁFICO: Fig_1_2_Diametro_Economico.png]**
*Figura 1.3: Curvas de optimización económica. La curva de costo total muestra un mínimo claro que define el diámetro óptimo de diseño, balanceando inversión inicial (Capex) y costos operativos (Opex).*

### 1.5.2 Indicadores Financieros

El software integra un módulo económico que calcula:
*   **VAN (Valor Actual Neto):** Suma de flujos de caja descontados.
*   **TIR (Tasa Interna de Retorno):** Rentabilidad del proyecto.
*   **CaE (Costo Anual Equivalente):** Útil para comparar alternativas con diferentes vidas útiles.

## 1.6 Inteligencia Artificial Aplicada a la Ingeniería Hidráulica

La integración de Modelos de Lenguaje Grande (LLMs) como Gemini representa un cambio de paradigma en la ingeniería asistida por computadora. A diferencia de los sistemas expertos tradicionales basados en reglas rígidas (`if-then`), los LLMs pueden:
1.  **Interpretar Contexto:** Analizar resultados numéricos y ofrecer diagnósticos cualitativos (ej. "La eficiencia es baja, considere aumentar el diámetro").
2.  **Sintetizar Normativa:** Buscar y relacionar criterios de normas técnicas (INEN, ASTM) aplicables al caso específico.
3.  **Generar Reportes:** Automatizar la redacción de memorias técnicas a partir de datos crudos.

Este proyecto explora la implementación de una arquitectura **RAG (Retrieval-Augmented Generation)** simplificada, donde el software alimenta al modelo de IA con datos precisos del cálculo hidráulico para obtener recomendaciones validadas y contextualizadas.

---
**Fin del Capítulo I**
