# Análisis de Curvas Características

## Curva H-Q de la Bomba

### Ecuación Característica

La curva altura-caudal de una bomba centrífuga se representa mediante un polinomio:

$$H(Q) = a_0 + a_1Q + a_2Q^2$$

Donde:
- $a_0$ = Altura de cierre (shut-off head)
- $a_1$ = Coeficiente lineal (típicamente negativo)
- $a_2$ = Coeficiente cuadrático (siempre negativo)

### Ajuste de Curva

La aplicación utiliza **regresión de mínimos cuadrados** para ajustar los coeficientes a partir de los puntos proporcionados por el fabricante.

**Método de cálculo**:
```python
# Sistema de ecuaciones normales
A = [[n, ΣQ, ΣQ²],
     [ΣQ, ΣQ², ΣQ³],
     [ΣQ², ΣQ³, ΣQ⁴]]

b = [ΣH, ΣQH, ΣQ²H]

# Solución: a = A⁻¹ · b
coef = np.linalg.solve(A, b)
```

**Coeficiente de determinación (R²)**:
$$R^2 = 1 - \\frac{SS_{res}}{SS_{tot}}$$

Valores aceptables: R² > 0.98

### Variación con VFD (Variador de Frecuencia)

Cuando se utiliza un **variador de frecuencia**, la curva se modifica según las **leyes de afinidad**:

$$Q_2 = Q_1 \left(\frac{N_2}{N_1}\right)$$

$$H_2 = H_1 \left(\frac{N_2}{N_1}\right)^2$$

$$P_2 = P_1 \left(\frac{N_2}{N_1}\right)^3$$

**Aplicación**: Generar familia de curvas a diferentes RPM (60%, 70%, 80%, 90%, 100%)

## Curva de Eficiencia (η-Q)

### Definición

La eficiencia relaciona la potencia hidráulica útil con la potencia mecánica consumida:

$$\\eta = \\frac{P_{hidraulica}}{P_{mecanica}} = \\frac{\\gamma Q H}{P_{shaft}}$$

### Características

- Forma típica: Curva parabólica con un **punto de máxima eficiencia** (BEP - Best Efficiency Point)
- Operación recomendada: 70% - 110% del BEP
- Fuera del BEP: Mayor desgaste, vibración, consumo energético

### Ajuste Polinomial

Similar a la curva H-Q, se ajusta mediante:

$$\\eta(Q) = b_0 + b_1Q + b_2Q^2$$

Con verificación de que existe un máximo en el rango operativo.

## Curva NPSH Requerido

### Concepto

**NPSH (Net Positive Suction Head)** = Carga neta positiva de succión

$$NPSH_{disponible} = \\frac{P_{atm}}{\\gamma} + h_{succion} - \\frac{P_{vapor}}{\\gamma} - h_{perdidas\ succion}$$

$$NPSH_{requerido} = f(Q)$$

### Verificación de Cavitación

**Condición para evitar cavitación**:
$$NPSH_{disponible} > NPSH_{requerido} + Margen_{seguridad}$$

Típicamente: Margen = 0.5 - 1.0 m

### Ajuste de Curva NPSH

La curva NPSH_req aumenta con el caudal (generalmente proporcional a Q²):

$$NPSH_{req}(Q) = c_0 + c_1Q + c_2Q^2$$

## Curva de Potencia (P-Q)

### Potencia al Freno (Brake HP)

$$P_{freno} = \\frac{\\gamma Q H}{\\eta}$$

**Conversiones**:
- 1 HP = 0.746 kW
- 1 kW = 1.341 HP

### Selección del Motor

**Potencia nominal del motor** debe ser:
$$P_{motor} ≥ \\frac{P_{freno,max}}{FS}$$

Donde FS (Factor de Servicio) típicamente = 1.15

### Consideraciones de Diseño

1. **Curva de potencia creciente**: Motor debe dimensionarse para caudal máximo
2. **Curva de potencia decreciente**: Motor se dimensiona para cierre (menos común)
3. **VFD**: Potencia reducida significativamente a RPM bajas ($P \\propto N^3$)

## Curva del Sistema

### Componentes

$$H_{sistema}(Q) = H_{estatica} + H_{dinamica}(Q)$$

Donde:
$$H_{dinamica}(Q) = \left(\frac{f L}{D} + \sum K\right) \frac{v^2}{2g} = k_{sistema} Q^2$$

### Cálculo del Coeficiente k_sistema

$$k_{sistema} = \frac{8}{g\pi^2} \left(\frac{fL}{D^5} + \frac{\sum K}{D^4}\right)$$

### Efecto de Accesorios

Cada accesorio contribuye a $\sum K$:
$$L_{equivalente} = K \frac{D}{f}$$

## Punto de Operación

### Intersección Curvas

El punto de operación se obtiene resolviendo:
$$H_{bomba}(Q) = H_{sistema}(Q)$$

**Método numérico** (Newton-Raphson):
```python
def f(Q):
    return H_bomba(Q) - H_sistema(Q)

Q_op = fsolve(f, Q_inicial)
H_op = H_bomba(Q_op)
```

### Análisis de Estabilidad

**Sistema estable** si:
$$\left|\frac{dH_{bomba}}{dQ}\right| > \left|\frac{dH_{sistema}}{dQ}\right|$$

Pendiente de bomba más pronunciada que sistema.

## Visualización

La aplicación genera gráficos interactivos que muestran:

- ✅ Curva H-Q de la bomba (con y sin VFD)
- ✅ Curva deI sistema
- ✅ Punto de operación marcado
- ✅ Curvas de eficiencia y potencia
- ✅ NPSH disponible vs requerido
- ✅ Zona de operación recomendada (70-110% BEP)

---

*El análisis de curvas es crucial para garantizar que la bomba seleccionada opera en condiciones óptimas.*
