# 📈 Guía Técnica: Generación y Cálculo de Curvas de Bombas

Esta guía explica el modelo matemático utilizado por la aplicación para generar las curvas características visibles en el panel de análisis.

---

## 1. Modelo Matemático: Regresión Polinomial
Para convertir los puntos discretos (coordenadas Q, H) de los catálogos en curvas continuas, la aplicación emplea una **regresión polinomial de segundo grado** (parábola), siguiendo la ecuación clásica de la hidráulica de bombas:

$$H(Q) = aQ^2 + bQ + c$$

Donde:
*   $H$: Altura dinámica total (m).
*   $Q$: Caudal (L/s o m³/h).
*   $a, b, c$: Coeficientes calculados mediante el método de mínimos cuadrados.

### ¿Por qué segundo grado?
Se utiliza el segundo grado porque representa fielmente la pérdida de energía cinética y de fricción interna en el rodete de la bomba, donde la altura disminuye de forma parabólica a medida que el caudal aumenta.

---

## 2. Cálculo del Punto de Operación
El punto de operación se encuentra resolviendo la intersección entre la **Curva de la Bomba** ($H_b$) y la **Curva del Sistema** ($H_s$):

$$H_b(Q) = H_s(Q)$$

La aplicación utiliza un algoritmo de búsqueda de raíces (`fsolve`) para encontrar el valor exacto de $Q$ donde ambas funciones coinciden, garantizando un margen de error despreciable.

---

## 3. Curvas de Eficiencia, Potencia y NPSH
Para estas curvas, el sistema permite elegir entre un ajuste lineal o cuadrático:
*   **Eficiencia ($\eta$)**: Suele aproximarse a una parábola invertida cuyo vértice es el **BEP** (Best Efficiency Point).
*   **Potencia ($P$)**: Depende de si la bomba es de flujo radial (creciente con Q) o axial. El modelo cuadrático se adapta a ambos casos.
*   **NPSH Requerido**: Sigue una curva cuadrática creciente, reflejando el aumento de la velocidad de entrada al rodete.

---

## 4. Estabilidad y Validación
Para asegurar que los gráficos sean "estéticos" y fieles a la realidad:
*   Se requieren al menos **3 puntos** para un ajuste cuadrático.
*   Si el usuario ingresa solo 2 puntos, el sistema conmuta automáticamente a un **ajuste lineal**.
*   Se realiza una extrapolación controlada para mostrar la curva hasta el caudal de "cierre" (Shut-off, $Q=0$).
