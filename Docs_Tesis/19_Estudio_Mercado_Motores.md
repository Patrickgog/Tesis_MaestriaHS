# ⚡ Estudio de Mercado: Motores Eléctricos Comerciales (Ecuador)

Este estudio calibra los costos y pesos de los motores eléctricos integrados en la aplicación, facilitando un cálculo de CAPEX más preciso y reduciendo el sobredimensionamiento.

---

## 1. Marcas y Presencia en el Mercado
En Ecuador, el mercado industrial está dominado por tres marcas principales que cumplen con las normativas locales (NEMA e IEC):
*   **WEG**: Distribuido principalmente por **Acero Comercial** e **Inducom**. Es la marca con mayor stock en Cuenca y Guayaquil.
*   **Siemens**: Distribuido por **VVA Industrial** e **Improselec**. Muy común en aplicaciones de bombeo de alta eficiencia (Línea Simotics).
*   **ABB / Bonfiglioli**: Presentes en proyectos industriales de gran escala.

---

## 2. Parámetros de Calibración (2024-2025)

### 💰 Costos Referenciales (Trifásicos 220/440V):
Basado en cotizaciones locales aproximadas:
*   **Pequeña Potencia (1 - 5 HP)**: $250 - $800 USD.
*   **Mediana Potencia (10 - 50 HP)**: $1,200 - $4,200 USD.
*   **Alta Potencia (>100 HP)**: >$7,000 USD.

### ⚖️ Pesos Industriales:
Se han corregido los pesos para reflejar carcasas de hierro fundido (tipo industrial) en lugar de aluminio, lo cual es vital para el diseño de bancadas y cimentaciones:
*   **5 HP**: ~35-40 kg.
*   **50 HP**: ~220-250 kg.
*   **100 HP**: ~450-500 kg.

---

## 3. Optimización para evitar Sobredimensionamiento
Se han añadido potencias comerciales "intermedias" que suelen encontrarse en catálogos de **Siemens** y **ISO/IEC** para permitir un ajuste más fino al punto de operación de la bomba:
*   **Nuevas potencias incluidas**: 1.2 HP, 4 HP, 12.5 HP, 35 HP, 45 HP, 70 HP.

Esto permite que, si el diseño requiere 32 HP, el sistema no salte directamente a 40 HP, sino que evalúe la opción de 35 HP si está disponible en stock.

---

## 📚 Fuentes Empleadas
1.  **Catálogo WEG W22**: *Motores Eléctricos de Inducción Trifásicos* (Versión industrial Ecuador).
2.  **Precios Referenciales Siemens 1LA7**: Consultados vía distribuidores locales (Guayaquil/Quito).
3.  **Inducom Ecuador**: Listas de precios para motores monofásicos y trifásicos Bonfiglioli/Thompson.
4.  **Acero Comercial S.A.**: Tarifario referencial de motores IP55 para ambientes húmedos (bombeo).
