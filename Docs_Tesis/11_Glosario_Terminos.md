# 11. Glosario de Términos Técnicos

## Documentación Técnica - Tesis de Maestría en Hidrosanitaria

### Glosario Completo: Ingeniería de Software, Hidráulica, IA y Tecnologías Web

---

## A

**ALLievi**: Software especializado para análisis de transitorios hidráulicos (golpe de ariete) en sistemas de tuberías. Desarrollado por la Universidad de Perugia (Italia), utiliza el Método de las Características (MOC) para simular fenómenos transitorios con alta precisión, permitiendo evaluar sobrepresiones y diseñar sistemas de protección.

**ANSI** (American National Standards Institute): Organismo privado sin fines de lucro que supervisa el desarrollo de estándares de consenso voluntario para productos, servicios, procesos y sistemas en Estados Unidos.

**API** (Application Programming Interface): Conjunto de definiciones y protocolos que se utiliza para desarrollar e integrar el software de las aplicaciones, permitiendo que dos aplicaciones de software se comuniquen entre sí.

**API Gemini**: Interfaz de programación de aplicaciones proporcionada por Google para acceder a los modelos de lenguaje grande (LLM) de la familia Gemini (Gemini Pro, Gemini Pro Vision, Gemini Ultra). Permite integrar capacidades de IA generativa en aplicaciones mediante llamadas HTTP REST o SDKs oficiales de Python. Ver guía de configuración en documento separado.

**ASME** (American Society of Mechanical Engineers): Asociación profesional estadounidense que desarrolla códigos y estándares asociados con el arte, ciencia y práctica de la ingeniería mecánica y multidisciplinaria.

**AWWA** (American Water Works Association): Asociación internacional científica y educativa fundada para mejorar la calidad y el suministro de agua potable en América del Norte y más allá.

**Algoritmo**: Conjunto ordenado y finito de operaciones que permite hallar la solución a un problema. En programación, es una secuencia de instrucciones precisas y bien definidas.

**Algoritmo Genético (GA)**: Metaheurística inspirada en el proceso de selección natural que pertenece a la clase más amplia de algoritmos evolutivos. Los AG se usan para generar soluciones de alta calidad a problemas de optimización y búsqueda.

**Altura Dinámica Total (TDH)**: Energía total por unidad de peso que una bomba debe agregar al fluido para moverlo del punto de succión al punto de descarga, incluyendo pérdidas por fricción.

---

## B

**Backend**: Parte de un sistema de software que procesa la entrada del usuario desde el frontend. Generalmente se refiere a los servidores, bases de datos y aplicaciones que trabajan detrás de las bambalinas para entregar información al usuario.

**Banner**: Elemento visual prominente en la parte superior de una interfaz de usuario que muestra información importante, alertas o identificación del sistema. En la aplicación, se utiliza para indicar "🌐 VERSIÓN PÚBLICA" o "🔧 MODO DESARROLLADOR".

**Bug**: Error, fallo o defecto en el código fuente de un programa que produce un resultado incorrecto o inesperado, o que hace que actúe de maneras no previstas.

**Bomba Centrífuga**: Máquina hidráulica que transforma energía mecánica en energía hidráulica mediante la fuerza centrífuga, utilizada para incrementar la presión y/o el movimiento de un fluido.

---

## C

**CAPEX** (Capital Expenditure): Fondos utilizados por una compañía para adquirir, actualizar y mantener activos físicos. En bombeo, se refiere al costo inicial de equipos (bomba, tubería, motores, etc.).

**CPU** (Central Processing Unit): Unidad central de procesamiento, el cerebro del computador que ejecuta instrucciones de programas mediante operaciones aritméticas, lógicas y de control. En aplicaciones Python, determina la velocidad de ejecución de algoritmos secuenciales.

**CRUD** (Create, Read, Update, Delete): Cuatro funciones básicas del almacenamiento persistente, especialmente en bases de datos relacionales y APIs RESTful.

**CSS** (Cascading Style Sheets): Lenguaje de hojas de estilo usado para describir la presentación de un documento escrito en HTML o XML, controlando la apariencia visual de las páginas web.

**Cache**: Componente de hardware o software que almacena datos de modo que futuras solicitudes de esos datos puedan ser atendidas con mayor rapidez.

**Cavitación**: Formación de burbujas de vapor en un líquido cuando la presión local desciende por debajo de la presión de vapor del fluido a la temperatura de operación. En bombas, causa daño mecánico y pérdida de rendimiento.

**Coeficiente de Hazen-Williams (C)**: Coeficiente empírico que caracteriza la rugosidad de una tubería en la fórmula de Hazen-Williams para cálculo de pérdidas de carga. Valores típicos: PVC = 150, Acero = 130, Hierro fundido = 100.

**Cromosoma**: En algoritmos genéticos, representación codificada de una solución candidata al problema de optimización.

**Cruce (Crossover)**: Operador genético utilizado para combinar la información genética de dos padres para generar nuevos descendientes.

---

## D

**Dashboard**: Panel de control que organiza y presenta información de manera fácil de leer, generalmente mediante gráficos y tablas dinámicas.

**DataFrame**: Estructura de datos bidimensional etiquetada con columnas que pueden ser de diferentes tipos, implementada en pandas (Python). Similar a una tabla de base de datos o una hoja de cálculo.

**Debug (Depuración)**: Proceso de identificar, localizar y corregir errores (bugs) en el código de un programa. Los mensajes debug proporcionan información detallada sobre el estado de la aplicación durante la ejecución para facilitar la identificación de problemas.

**Deploy (Desplegar)**: Proceso de poner una aplicación en producción, haciéndola accesible para los usuarios finales. En Streamlit, se puede desplegar en Streamlit Cloud, Heroku, AWS, o servidores propios.

**Deployment**: Proceso de instalación, configuración y puesta en marcha de un sistema de software en un entorno de producción donde estará disponible para los usuarios finales.

**DevOps**: Conjunto de prácticas que combinan desarrollo de software (Dev) y operaciones de TI (Ops) con el objetivo de acortar el cicloclo de vida del desarrollo de sistemas.

**Drop Zone**: Área interactiva en una interfaz gráfica donde los usuarios pueden arrastrar y soltar archivos para cargarlos. En Streamlit, se implementa con `st.file_uploader()` para permitir subida de archivos de manera intuitiva.

**DRY** (Don't Repeat Yourself): Principio de desarrollo de software dirigido a reducir la repetición de información de todo tipo, especialmente útil en sistemas multi-capa.

---

## E

**EPANET**: Software de distribución pública desarrollado por la EPA (Environmental Protection Agency) de EE.UU. para el modelado de redes de distribución de agua potable.

**Eficiencia de Bomba (η)**: Relación entre la potencia hidráulica útil entregada al fluido y la potencia mecánica consumida en el eje de la bomba, expresada como porcentaje.

**Endpoint**: URL específica en una API que representa un objeto o una colección de objetos. Cada endpoint realiza una función específica.

**Expander**: Widget de Streamlit que crea secciones colapsables/expandibles en la interfaz. Permite organizar contenido de forma jerárquica y reducir el scroll, mejorando la experiencia de usuario. Se implementa con `st.expander()`.

---

## F

**Fitness**: En algoritmos genéticos, función objetivo que asigna un valor numérico a cada individuo (solución candidata) indicando qué tan buena es la solución para el problema planteado.

**Frontend**: Parte de un sistema de software que interactúa directamente con el usuario. En desarrollo web, se refiere al código HTML, CSS y JavaScript que se ejecuta en el navegador.

**Framework**: Marco de trabajo que provee una estructura y metodología para el desarrollo de software, incluyendo componentes, bibliotecas y herramientas que facilitan la construcción de aplicaciones.

---

## G

**GA** (Genetic Algorithm): Ver Algoritmo Genético.

**Git**: Sistema de control de versiones distribuido ampliamente utilizado para rastrear cambios en archivos y coordinar el trabajo entre múltiples personas.

**GitHub**: Plataforma de alojamiento de código para el control de versiones y la colaboración basada en Git, propiedad de Microsoft.

**GPU** (Graphics Processing Unit): Unidad de procesamiento gráfico, procesador especializado diseñado para acelerar el procesamiento de gráficos y cálculos paralelos masivos. En IA, se usa para entrenar modelos de deep learning de forma mucho más rápida que con CPU.

**GUI** (Graphical User Interface): Tipo de interfaz de usuario que permite a las personas interactuar con dispositivos electrónicos a través de iconos gráficos y indicadores visuales.

**Golpe de Ariete**: Fenómeno transitorio que se produce cuando el momentum de un fluido en movimiento es forzado a detenerse o cambiar de dirección súbitamente, generando sobrepresiones peligrosas.

---

## H

**HTML** (HyperText Markup Language): Lenguaje de marcado estándar para documentos diseñados para ser visualizados en un navegador web, define la estructura y el contenido de las páginas web.

**HTTP** (HyperText Transfer Protocol): Protocolo de comunicación que permite las transferencias de información en la World Wide Web.

**Hazen-Williams**: Ecuación empírica que relaciona el caudal de agua en una tubería con las propiedades físicas de la tubería y la caída de presión causada por la fricción.

---

## I

**IDE** (Integrated Development Environment): Aplicación de software que proporciona facilidades integrales a los programadores para el desarrollo, incluyendo

 editor de código, compilador/intérprete, depurador y más.

**IA** (Inteligencia Artificial): Simulación de procesos de inteligencia humana por parte de sistemas informáticos, incluyendo aprendizaje, razonamiento y auto-corrección.

**JSON** (JavaScript Object Notation): Formato ligero de intercambio de datos fácil de leer y escribir para humanos y fácil de analizar y generar para máquinas.

---

## L

**Layout**: Disposición y organización de elementos visuales en una interfaz de usuario. En Streamlit, se controla con funciones como `st.columns()`, `st.sidebar`, y `st.container()` para crear diseños multi-columna y organizados.

**LCC** (Life Cycle Cost): Costo total de posesión de un activo durante toda su vida útil, incluyendo CAPEX y OPEX.

**Library (Librería)**: Colección de código pre-escrito que puede ser llamado por un programa para realizar tareas comunes, evitando que el programador tenga que escribir todo desde cero.

**LLM** (Large Language Model): Modelo de lenguaje grande, red neuronal entrenada con cantidades masivas de texto para comprender y generar lenguaje natural humano. Ejemplos: GPT-4, Gemini, Claude. Se usan para análisis inteligente, generación de texto, y asistencia contextual.

**Log (Mensajes de registro)**: Archivo o sistema que registra eventos, errores, advertencias e información de depuración durante la ejecución de una aplicación. Los logs son fundamentales para diagnosticar problemas y monitorear el comportamiento del sistema.

---

## M

**MVC** (Model-View-Controller): Patrón de arquitectura de software que separa una aplicación en tres componentes interconectados: Model (datos), View (interfaz de usuario) y Controller (lógica de negocio).

**Machine Learning (Aprendizaje Automático)**: Subcampo de la inteligencia artificial que permite a las computadoras aprender sin ser explícitamente programadas, mediante algoritmos que mejoran automáticamente a través de la experiencia.

**Metaheurística**: Método de solución de problemas de optimización de propósito general que no garantiza encontrar el óptimo global pero que encuentra buenas soluciones en tiempo razonable.

**Metaprompt**: Prompt de nivel superior que instruye a un LLM sobre cómo debe comportarse, qué rol debe adoptar, y qué formato de respuesta debe generar. Es esencialmente un "prompt para crear prompts" que define el contexto y las reglas de interacción con la IA.

**Mutación**: En algoritmos genéticos, operador que altera aleatoriamente uno o más valores de un cromosoma para mantener diversidad genética en la población.

---

## N

**NPSH** (Net Positive Suction Head): Diferencia entre la presión total en la entrada de la bomba y la presión de vapor del líquido, expresada en altura de columna de líquido. Crítico para evitar cavitación.

**NPSH Disponible (NPSHa)**: NPSH que proporciona el sistema en la succión de la bomba.

**NPSH Requerido (NPSHr)**: NPSH mínimo que requiere la bomba para operar sin cavitación, determinado por el fabricante.

**NumPy**: Biblioteca fundamental para computación científica en Python, proporciona soporte para arrays multidimensionales y funciones matemáticas de alto nivel.

---

## O

**OPEX** (Operating Expenditure): Costos continuos para operar un producto, negocio o sistema. En bombeo, incluye electricidad, mantenimiento, reparaciones.

**OOP** (Object-Oriented Programming)**: Paradigma de programación basado en el concepto de "objetos", que pueden contener datos en forma de campos (atributos) y código en forma de procedimientos (métodos).

**Open Source**: Software cuyo código fuente está disponible públicamente, permitiendo a cualquiera estudiar, modificar y distribuir el software para cualquier propósito.

**Optimización Multiobjetivo**: Proceso de optimizar simultáneamente dos o más funciones objetivo conflictivas sujetas a restricciones.

---

## P

**pandas**: Biblioteca de Python que proporciona estructuras de datos y herramientas de análisis de datos de alto rendimiento y fáciles de usar.

**Pérdida de Carga (Head Loss)**: Disminución de la altura de presión (energía) de un fluido debido a la fricción con las paredes de la tubería y la turbulencia interna.

**Pérdidas Primarias**: Pérdidas de energía debidas a la fricción en tramos rectos de tubería.

**Pérdidas Secundarias (Menores)**: Pérdidas de energía en accesorios como válvulas, codos, tees, expansiones y contracciones.

**Placeholder**: Texto temporal que aparece en un campo de entrada para indicar al usuario qué tipo de información se espera. Desaparece cuando el usuario comienza a escribir. En Streamlit: `st.text_input("Nombre", placeholder="Ingrese su nombre aquí")`.

**Plotly**: Biblioteca de gráficos interactivos de Python que puede crear visualizaciones sofisticadas y publicarlas para web.

**Popup (Ventana emergente)**: Ventana secundaria que aparece sobre la interfaz principal para mostrar información adicional, solicitar confirmación, o capturar datos del usuario sin abandonar la página actual.

**Prompt**: Instrucción o pregunta en lenguaje natural que se proporciona a un modelo de IA (LLM) para generar una respuesta. La calidad del prompt determina directamente la calidad de la respuesta obtenida. Ver también: Metaprompt.

**Python**: Lenguaje de programación interpretado de alto nivel y propósito general, conocido por su sintaxis clara y legibilidad.

---

## R

**RAG** (Retrieval-Augmented Generation): Técnica de IA que combina recuperación de información con generación de lenguaje. El modelo primero busca información relevante en una base de conocimiento y luego genera respuestas basadas en esos datos recuperados, mejorando precisión y reduciendo alucinaciones.

**Render (Renderizar)**: Proceso de generar la representación visual final de una interfaz de usuario o gráfico a partir de código. En Streamlit, "renderizar" se refiere a mostrar widgets, gráficos y contenido en la página web que ve el usuario.

**RESTful API**: Interfaz de programación de aplicaciones que se adhiere a los principios de REST (Representational State Transfer), utilizando solicitudes HTTP estándar.

**RPM** (Revolutions Per Minute): Revoluciones por minuto, unidad de velocidad angular que indica el número de rotaciones completas que un objeto da en un minuto.

**Refactoring**: Proceso de reestructurar código existente sin cambiar su comportamiento externo, mejorando su estructura interna, legibilidad y mantenibilidad.

**Reynolds (Número de)**: Número adimensional que relaciona las fuerzas inerciales con las viscosas en un fluido, utilizado para predecir patrones de flujo (laminar vs turbulento).

---

## S

**Session State**: Mecanismo en aplicaciones web (especialmente Streamlit) para almacenar datos que persisten entre re-ejecuciones del script, manteniendo el estado de la aplicación.

**Slider**: Widget de interfaz gráfica que permite al usuario seleccionar un valor numérico deslizando un control a lo largo de una barra. En Streamlit se implementa con `st.slider()` y es útil para ajustar parámetros de forma intuitiva.

**SPA** (Single Page Application): Aplicación web que interactúa con el usuario recargando dinámicamente la página actual en lugar de cargar páginas enteras nuevas del servidor.

**SQL** (Structured Query Language): Lenguaje de programación diseñado para administrar y recuperar información de sistemas de gestión de bases de datos relacionales.

**Streamlit**: Framework de código abierto de Python para crear aplicaciones web interactivas de ciencia de datos y machine learning rápidamente. No requiere conocimientos de HTML, CSS o JavaScript. Permite construir interfaces profesionales con código Python puro.

**SciPy**: Biblioteca de Python utilizada para computación científica y técnica, construida sobre NumPy.

---

## T

**TDH**: Ver Altura Dinámica Total.

**Textarea (Área de texto)**: Widget de entrada que permite al usuario escribir múltiples líneas de texto. En Streamlit se usa con `st.text_area()` y es ideal para ingresar datos tabulares, listas de valores, o texto largo. En la aplicación se usa para ingresar curvas características de bombas.

**Tooltip**: Pequeño mensaje informativo que aparece cuando el usuario pasa el cursor sobre un elemento de la interfaz. Proporciona ayuda contextual sin saturar la pantalla. En Streamlit se agrega con el parámetro `help="..."` en widgets.

**Type Hints (Python)**: Anotaciones opcionales en Python que especifican el tipo esperado de variables, parámetros de función y valores de retorno, mejorando la legibilidad y permitiendo análisis estático.

**Throughput**: Cantidad de datos transferidos de un lugar a otro, o procesados en un período de tiempo especificado.

---

## U

**UI** (User Interface): Espacio donde ocurren las interacciones entre humanos y máquinas, incluyendo todos los elementos que permiten al usuario interactuar con el software.

**URL** (Uniform Resource Locator): Dirección de un recurso específico en la World Wide Web.

**UX** (User Experience): Experiencia del usuario al interactuar con un producto, sistema o servicio, abarcando usabilidad, accesibilidad y eficiencia.

---

## V

**VFD** (Variable Frequency Drive): Dispositivo electrónico que controla la velocidad de un motor eléctrico variando la frecuencia de la alimentación eléctrica, permitiendo ahorro energético en bombeo.

**VPN** (Valor Presente Neto): Método de evaluación de inversiones que calcula el valor presente de un flujo futuro de efectivo usando una tasa de descuento.

**VS Code** (Visual Studio Code): Editor de código fuente gratuito desarrollado por Microsoft, ampliamente utilizado para desarrollo Python, HTML, JavaScript y otros lenguajes. Ofrece debugging integrado, control Git, extensiones, y terminal incorporado.

**Validación**: Proceso de evaluar un software al final del desarrollo para determinar si satisface los requisitos especificados.

**Vectorización**: Técnica de programación que aprovecha operaciones sobre arrays completos en lugar de elementos individuales, logrando mejoras significativas de rendimiento.

---

## W

**WNTR** (Water Network Tool for Resilience): Paquete de Python diseñado para simular y analizar la resiliencia de sistemas de distribución de agua.

**Webhook**: Método de aumentar o alterar el comportamiento de una página web o aplicación web con callbacks personalizados.

**Widget**: Componente de interfaz gráfica de usuario que permite al usuario interactuar con la aplicación (botones, sliders, campos de texto, etc.).

---

## X

**XML** (eXtensible Markup Language): Lenguaje de marcado que define un conjunto de reglas para codificar documentos en un formato que es legible tanto para humanos como para máquinas.

---

**Total de Términos**: 110+  
**Categorías**:  
- Ingeniería de Software y Desarrollo: 44  
- Hidráulica y Sistemas de Bombeo: 24  
- Inteligencia Artificial y LLM: 20  
- Tecnologías Web y UI: 22  

---

**Autor**: Equipo de Documentación - Tesis Maestría Hidrosanitaria  
**Fecha**: Enero 2026  
**Aplicación**: Sistema Experto de Diseño de Sistemas de Bombeo
