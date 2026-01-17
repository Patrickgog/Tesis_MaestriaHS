# 🚀 Mejoras en el Catálogo de Bombas Comerciales (Prediseño)

Se han implementado cambios profundos para garantizar que siempre encuentres una bomba adecuada para tus proyectos de ingeniería.

## ✅ Cambios Principales

### 1. Nuevos Catálogos Integrados
Se añadieron dos marcas fundamentales en el mercado ecuatoriano:
*   **KSB**: Incluye modelos **Etanorm** (procesos industriales) y **Movitec** (multietapa vertical para alta presión).
*   **Pedrollo**: Incluye series **CP**, **2CP** y **F** (industriales), ideales para sistemas medianos y comunales.

### 2. Búsqueda Inteligente "Auto-Flexible"
Se modificó el motor de búsqueda en `data/pump_database.py`. Ahora, si la búsqueda inicial con el margen del usuario (ej. 20%) no arroja resultados, el sistema:
1.  **Duplica automáticamente el margen** de búsqueda.
2.  Marca los resultados encontrados como **"Búsqueda Flexible"** para alertarte de que el ajuste es más amplio del ideal.
3.  Prioriza siempre los modelos que más se acerquen al **Punto de Operación** teórico.

### 3. Documentación Técnica para la Tesis
Se crearon archivos de guía profesional en la carpeta `Docs_Tesis`:
*   [Expansión del Catálogo](file:///c:/Users/psciv/OneDrive/Desktop/PYTHON/App_bombeo/app_bombeo_modulos/Docs_Tesis/20_Expansion_Catalogo_Bombas.md): Detalles de la estrategia y proveedores.
*   [Cálculo de Curvas](file:///c:/Users/psciv/OneDrive/Desktop/PYTHON/App_bombeo/app_bombeo_modulos/Docs_Tesis/21_Guia_Curvas_Bombas.md): Explicación matemática sobre la **Regresión Polinomial de 2do Grado** utilizada para el modelado de curvas.

## 🛠️ Verificación Técnica
*   [x] Archivos JSON creados y validados.
*   [x] Interfaz de usuario actualizada con selectores de KSB y Pedrollo.
*   [x] Lógica de filtrado probada (evita el error de "no bombs found").
*   [x] Cambios subidos a la rama `public` (`git push` exitoso).

> [!TIP]
> Si diseñas una planta de tratamiento con caudales altos, prueba la serie **KSB Etanorm**. Para edificios o sistemas de riego con mucha altura, la serie **KSB Movitec** es ahora la mejor opción.
