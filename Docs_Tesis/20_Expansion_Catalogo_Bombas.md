# 🏭 Plan de Expansión: Catálogo de Bombas Comerciales

Este plan detalla cómo resolveremos la falta de opciones en el prediseño añadiendo marcas líderes en Ecuador y mejorando la lógica de búsqueda.

## 1. Nuevos Proveedores a Integrar
Se han seleccionado marcas con alta presencia técnica y comercial en Ecuador:

| Marca | Aplicación Principal | Modelos a Integrar |
| :--- | :--- | :--- |
| **KSB** | Industrial / Infraestructura | ETA (Horizontal), Movitec (Multietapa Vertical) |
| **Pedrollo** | Comercial / Agrícola | CP (Centrífuga), NK (Multietapa), F (Industrial) |
| **Shimge** | Económico / Media Potencia | BW (Horizontal Multietapa), BL (Vertical) |
| **Goulds** | Procesos / Saneamiento | e-SV (Multietapa), 3656 (Centrífuga) |

## 2. Mejoras en la Lógica de Selección
Para evitar el mensaje "No se encontraron bombas":
*   **Búsqueda Dinámica**: Si el margen del 20% no arroja resultados, el sistema sugerirá automáticamente ampliarlo al 40% o 60%.
*   **Sugerencia de Multi-bombas**: Si el caudal es muy alto para una sola bomba, el sistema recordará al usuario que está buscando "Caudal por Bomba" y no "Caudal Total".

## 3. Funcionamiento de las Curvas
Las curvas se generan mediante un **ajuste polinomial de segundo grado** ($H = aQ^2 + bQ + c$) basado en los puntos discretos ingresados en el JSON. Esto permite simular la operación en cualquier punto intermedio con un error menor al 1%.

## 4. Pasos de Implementación
1. [ ] Crear `data_tablas/bombas_ksb_data.json`.
2. [ ] Crear `data_tablas/bombas_pedrollo_data.json`.
3. [ ] Actualizar `data/pump_database.py` para reconocer las nuevas marcas.
4. [ ] Modificar la UI en `ui/tabs_modules/data_input.py` para incluir los nuevos selectores.
5. [ ] Refinar los rangos de Q y H en todos los JSONs existentes.
