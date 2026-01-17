# Guía Completa: Configuración y Uso de la API de Google Gemini

## Documentación Técnica - Sistema de Bombeo con IA

---

## INTRODUCCIÓN

La API de Google Gemini permite integrar capacidades de inteligencia artificial generativa en la aplicación de diseño de sistemas de bombeo. Gemini puede analizar diseños, proporcionar recomendaciones técnicas expertas y explicar conceptos hidráulicos complejos en lenguaje natural.

**Características principales**:
- ✅ Análisis inteligente de parámetros de diseño
- ✅ Recomendaciones basadas en mejores prácticas de ingeniería
- ✅ Detección de riesgos técnicos (cavitación, velocidades excesivas)
- ✅ Explicación de resultados de cálculos
- ✅ Chat técnico interactivo

---

## SECCIÓN 1: OBTENER LA API KEY DE GEMINI

### Paso 1: Crear una Cuenta de Google (si no tiene)

1. Visite https://accounts.google.com/
2. Haga clic en "Crear cuenta"
3. Complete el formulario con sus datos
4. Verifique su correo electrónico
5. Complete la configuración de la cuenta

### Paso 2: Acceder a Google AI Studio

1. **Navegue a Google AI Studio**: https://aistudio.google.com/
2. **Inicie sesión** con su cuenta de Google
3. Acepte los **Términos de Servicio** de Google AI si es la primera vez

![Captura de pantalla esperada: Página principal de Google AI Studio]

### Paso 3: Obtener su API Key

1. En Google AI Studio, busque el menú lateral izquierdo
2. Haga clic en el ícono de **llave** 🔑 o busque la opción **"Get API key"**
3. Se abrirá una ventana con opciones para crear una nueva API key

![Captura: Botón "Create API key"]

4. **Opción A - Proyecto existente**:
   - Si ya tiene un proyecto de Google Cloud, selecciónelo de la lista desplegable
   - Haga clic en **"Create API key in existing project"**

5. **Opción B - Nuevo proyecto (RECOMENDADO para principiantes)**:
   - Haga clic en **"Create API key in new project"**
   - Google creará automáticamente un proyecto nuevo

6. **Copie su API Key**:
   - Aparecerá su API key en formato: `AIzaSy...` (aproximadamente 39 caracteres)
   - Haga clic en el ícono de **copiar** 📋
   - **⚠️ IMPORTANTE**: Guarde esta key en un lugar seguro
   - **NUNCA** comparta su API key públicamente ni la suba a GitHub

![Captura: API key generada con botón de copiar]

### Paso 4: Límites y Cuotas Gratuitas

**Plan gratuito de Gemini API**:
- ✅ **60 solicitudes por minuto** (RPM)
- ✅ **1,500 solicitudes por día** (RPD)
- ✅ **1 millón de tokens por mes**
- ✅ **Suficiente para uso personal y desarrollo**

**Para proyectos grandes**:
- Puede activar facturación en Google Cloud Console
- Tarifas muy competitivas (consulte precios actuales)

---

## SECCIÓN 2: CONFIGURAR LA API KEY EN LA APLICACIÓN (VERSIÓN PÚBLICA)

### ⭐ Método Principal: Ingresar API Key Directamente en la Aplicación

**La versión pública está diseñada para ser SUPER SIMPLE**. No necesita editar archivos ni configurar secrets. Todo se hace desde la interfaz:

#### Paso 1: Abrir la Aplicación

1. **Acceda a la aplicación web pública**: 
   - URL de ejemplo: `https://tesismaestriahs-publica.streamlit.app/`
   - O ejecute localmente: `streamlit run deployment_package/main.py`

2. Verá el banner superior que dice: **"🌐 VERSIÓN PÚBLICA"**

#### Paso 2: Localizar el Panel de Análisis IA

1. En el **sidebar izquierdo** (barra lateral), busque el expander:
   ```
   🤖 Análisis IA
   ```

2. **Haga clic** en ese expander para abrirlo

3. Verá un campo de texto que dice:
   ```
   🔑 API Key de Gemini (opcional)
   ```

![Ubicación del campo API Key en el sidebar]

#### Paso 3: Ingresar su API Key

1. **Pegue su API Key** en el campo de texto:
   ```
   AIzaSy_AQUI_PEGA_TU_API_KEY_COMPLETA
   ```

2. La aplicación **automáticamente** detectará y validará la key

3. **¡Listo!** No necesita guardar ni hacer nada más

#### Paso 4: Verificar que Funciona

1. Complete un diseño en la pestaña **"📊 Entrada de Datos"**
2. Vaya a **"📈 Análisis"** y haga clic en **"🧮 Calcular Sistema"**
3. Regrese al sidebar y en el expander **"🤖 Análisis IA"**
4. Haga clic en el botón **"🔍 Analizar Diseño Actual"**
5. Si configuró correctamente, verá el análisis de Gemini aparecer

**✅ Ventajas de este método**:
- ✨ **Sin archivos**: No necesita editar archivos de configuración
- ✨ **Sin código**: Todo desde la interfaz gráfica
- ✨ **Inmediato**: Funciona al instante
- ✨ **Privado**: Su API key se guarda en la sesión del navegador
- ✨ **Reversible**: Puede cambiarla o eliminarla cuando quiera

### 🔒 ¿Es Seguro Ingresar mi API Key Así?

**Sí, es seguro** porque:

1. **No se almacena permanentemente**: La key solo existe durante su sesión
2. **No se envía a ningún servidor**: Solo se usa entre su navegador y Google Gemini
3. **Se borra al cerrar**: Cuando cierra el navegador, la key desaparece
4. **Solo usted la ve**: Nadie más tiene acceso a su sesión

**⚠️ Precaución**: Si está en una computadora pública o compartida:
- Use modo incógnito/privado del navegador
- Cierre completamente el navegador al terminar
- O simplemente no ingrese su API key en ese caso

### 💡 IMPORTANTE: La API Key es OPCIONAL

**Puede usar la aplicación COMPLETAMENTE sin configurar Gemini**:

- ✅ Todos los cálculos hidráulicos funcionan normalmente
- ✅ Análisis de NPSH funciona
- ✅ Optimización con algoritmos genéticos funciona
- ✅ Generación de gráficos funciona
- ✅ Reportes PDF/Excel funcionan

**Lo único que NO funcionará sin API key**:
- ❌ El botón "🔍 Analizar Diseño Actual" (análisis IA con Gemini)



---

## SECCIÓN 3: VERIFICAR QUE FUNCIONA

### Prueba Directa en la Aplicación (RECOMENDADO)

**La forma más fácil de verificar:**

1. **Abra la aplicación**
2. **Ingrese su API key** en el sidebar (🤖 Análisis IA)
3. **Complete un diseño básico**:
   - Caudal: 50 L/s
   - Altura descarga: 30 m
   - Configure diámetros y tuberías
4. **Calcule** el sistema (pestaña Análisis)
5. **Haga clic** en "🔍 Analizar Diseño Actual"

**✅ Si funciona**:
- Verá un mensaje "🧠 Analizando con Gemini..."
- Luego aparecerá un análisis técnico detallado
- El análisis incluirá recomendaciones y evaluación del diseño

**❌ Si NO funciona**:
- Verá un mensaje de error específico
- Revise que copió la API key completa (sin espacios extra)
- Verifique que tiene conexión a internet
- Consulte la Sección 5 (Solución de Problemas)

### Prueba Visual Rápida

**Indicadores de que la API está configurada**:

✅ **Correcto**:
```
🤖 Análisis IA
  🔑 API Key: AIzaSy...ABC (configurada ✓)
  [🔍 Analizar Diseño Actual]  ← Botón habilitado
```

❌ **Falta configurar**:
```
🤖 Análisis IA
  🔑 API Key: (vacío)
  [🔍 Analizar Diseño Actual]  ← Botón deshabilitado
  ⚠️ Ingrese su API Key de Gemini para habilitar análisis IA
```

---

## SECCIÓN 4: USAR GEMINI EN LA APLICACIÓN

### ¿Dónde está implementado Gemini?

En la aplicación de bombeo, Gemini se utiliza en:

1. **Sidebar - Módulo "🤖 Análisis IA"**
   - Ubicación: Panel lateral izquierdo
   - Función: Analiza el diseño completo y proporciona feedback experto

2. **Botón "Analizar Diseño Actual"**
   - Acción: Envía parámetros del sistema a Gemini
   - Resultado: Recomendaciones técnicas personalizadas

### Cómo Usar el Análisis IA

#### Paso 1: Completar el Diseño

1. Ingrese todos los parámetros en la pestaña **"📊 Entrada de Datos"**:
   - ✓ Caudal
   - ✓ Alturas de succión/descarga
   - ✓ Diámetros
   - ✓ Tuberías y accesorios
   - ✓ Curvas de bomba

2. Vaya a la pestaña **"📈 Análisis"**
3. Haga clic en **"🧮 Calcular Sistema"**
4. Espere a que se completen los cálculos

#### Paso 2: Activar el Análisis IA

1. En el **sidebar izquierdo**, localice el expander **"🤖 Análisis IA"**
2. Haga clic para expandirlo
3. Verá el botón **"🔍 Analizar Diseño Actual"**
4. Haga clic en el botón

#### Paso 3: Revisar los Resultados

Gemini analizará:
- ✅ **Parámetros hidráulicos** (Q, H, TDH)
- ✅ **NPSH** y riesgo de cavitación
- ✅ **Velocidades** en succión e impulsión
- ✅ **Eficiencia** de la bomba
- ✅ **Cumplimiento** con normas (HI 9.6.1, ASME)

**Ejemplo de respuesta**:
```markdown
## 🔍 Análisis del Diseño de Bombeo

### Evaluación General: ✅ APROBADO con Observaciones

**Fortalezas del diseño:**
- ✅ Eficiencia de bomba excelente (72.5%) - dentro del rango óptimo
- ✅ NPSH margen adecuado (2.6 m > 1.5 m requerido)
- ✅ Velocidades dentro de rangos recomendados

**Oportunidades de Mejora:**
1. **Eficiencia Energética**: 
   - Considere instalar un VFD (Variador de Frecuencia)
   - Ahorro proyectado: ~35% en consumo eléctrico
   - Payback estimado: 2.3 años

2. **Optimización de Diámetro**:
   - Diámetro de succión podría aumentarse de 75mm a 90mm
   - Beneficio: Reducción del 40% en pérdidas de succión
   - NPSH disponible aumentaría a 3.8 m

### Comparación con Mejores Prácticas (HI 9.6.1)
- Velocidad succión: 0.85 m/s ✓ (rango 0.6-1.5 m/s)
- Velocidad impulsión: 1.93 m/s ✓ (rango 1.0-2.5 m/s)
- Margen NPSH: 2.6 m ✓ (mínimo 1.5 m)

### Calificación Energética: **A- (Muy Bueno)**
Con VFD podría alcanzar **A+**
```

---

## SECCIÓN 5: SOLUCIÓN DE PROBLEMAS

### Problema 1: "El campo de API Key no aparece"

**Síntoma**: No veo el campo para ingresar la API key en el sidebar

**Solución**:
1. Verifique que está en la **versión pública** (banner superior debe decir "🌐 VERSIÓN PÚBLICA")
2. Busque el expander **"🤖 Análisis IA"** en el sidebar izquierdo
3. **Haga clic** en ese expander para abrirlo
4. El campo de API key debería aparecer dentro

**Si sigue sin aparecer**:
- Refresque la página (F5 o Ctrl+R)
- Cierre y vuelva a abrir el navegador
- Limpie el cache del navegador

### Problema 2: "Error 403: API key not valid"

**Síntoma**: 
```
❌ Error al analizar con IA: 403 API key not valid
```

**Causa**: API key incorrecta, incompleta o desactivada

**Solución**:
1. Vuelva a **Google AI Studio** (https://aistudio.google.com/)
2. Copie la API key **COMPLETA** nuevamente:
   - Debe empezar con `AIzaSy`
   - Tiene aproximadamente 39 caracteres
   - **Asegúrese de copiar TODO** (sin espacios ni saltos de línea)
3. **Pegue nuevamente** en el campo del sidebar
4. **Intente el análisis** otra vez

**Si persiste**:
- Su API key puede haber sido revocada
- Genere una **nueva API key** en Google AI Studio
- Use la nueva key en la aplicación

### Problema 3: "Error 429: Quota exceeded"

**Síntoma**:
```
❌ Error 429: Resource has been exhausted
```

**Causa**: Superó los límites gratuitos

**Limites actuales**:
- 60 solicitudes por minuto
- 1,500 solicitudes por día

**Solución temporal**:
- **Para límite por minuto**: Espere 60 segundos
- **Para límite diario**: Espere hasta el día siguiente
- Use el análisis IA solo cuando realmente lo necesite

**Solución permanente**:
- Active facturación en Google Cloud Console
- Los costos son mínimos (~$0.01 por análisis)

### Problema 4: El botón "Analizar Diseño" está deshabilitado (gris)

**Causa**: Falta alguno de los requisitos

**Solución - Verifique todos estos pasos**:

✓ **1. API Key ingresada**: Campo no debe estar vacío  
✓ **2. Cálculos realizados**: Debe haber hecho clic en "🧮 Calcular Sistema" primero  
✓ **3. Datos completos**: Debe tener al menos caudal y alturas configurados  

**Orden correcto**:
1. Ingresar API key en sidebar
2. Completar datos en pestaña "📊 Entrada de Datos"
3. Ir a pestaña "📈 Análisis"
4. Hacer clic en "🧮 Calcular Sistema"
5. **Ahora sí**, el botón de análisis IA debe estar habilitado

### Problema 5: Gemini responde muy lento (>30 segundos)

**Causas posibles**:

1. **Conexión lenta a internet**:
   - Verifique su velocidad de internet
   - Cierre otras aplicaciones que usen ancho de banda

2. **Servidores de Google saturados** (raro):
   - Es temporal
   - Intente en 5-10 minutos

3. **Diseño muy complejo**:
   - Gemini tarda más con muchos datos
   - 10-20 segundos es normal para análisis completos
   - >30 segundos indica un problema

**Solución**:
- Si tarda más de 1 minuto, refresque la página e intente de nuevo
- Verifique que su API key no haya alcanzado el límite (Error 429)

### Problema 6: "La API key desaparece cuando recargo la página"

**Comportamiento NORMAL**: 
La API key se almacena en la sesión del navegador por seguridad. Al recargar la página o cerrar el navegador, debe volver a ingresarla.

**¿Por qué es así?**:
- **Seguridad**: Evita que su API key quede almacenada permanentemente
- **Privacidad**: Especialmente importante en computadoras compartidas

**Si no quiere ingresarla cada vez**:
- Mantenga la pestaña del navegador abierta
- O guarde su API key en un archivo de texto seguro (solo en SU computadora)
- Cópiela y péguela cuando inicie nueva sesión

**IMPORTANTE**: 
- NO comparta su archivo de API key
- NO lo suba a internet o GitHub

---

## SECCIÓN 6: COSTOS Y PLANES

### Plan Gratuito (Actual)

**Límites**:
- 60 solicitudes/minuto
- 1,500 solicitudes/día
- 1 millón tokens/mes

**Suficiente para**:
- Uso personal
- Desarrollo y pruebas
- ~50 análisis de diseño por día

### Plan de Pago (Opcional)

**Si necesita más**:
1. Visite https://console.cloud.google.com/
2. Active facturación en su proyecto
3. Tarifas Gemini Pro (precios aproximados, verificar actuales):
   - **Input**: $0.00025 / 1K caracteres
   - **Output**: $0.0005 / 1K caracteres
   - **Muy económico**: ~$0.01 por análisis típico

**Ejemplo de costo real**:
- 100 análisis complejos al mes ≈ $1 USD
- 1,000 análisis al mes ≈ $10 USD

---

## SECCIÓN 7: PREGUNTAS FRECUENTES (FAQ)

### ¿Gemini es obligatorio para usar la aplicación?

**No**. La aplicación funciona completamente sin Gemini. Las características IA son **opcionales** y **complementarias**. Todos los cálculos hidráulicos funcionan independientemente.

### ¿Qué hace exactamente Gemini?

Gemini **NO hace cálculos**. Los cálculos hidráulicos son realizados por algoritmos determinísticos en Python. Gemini actúa como **asesor experto** que:
- Interpreta resultados
- Detecta patrones problemáticos
- Sugiere mejoras
- Explica conceptos

### ¿Puedo usar otra IA (ChatGPT, Claude)?

Técnicamente sí, pero requeriría modificar el código. La integración actual está optimizada para Gemini por:
- API gratuita generosa
- Baja latencia
- Excelente calidad de respuestas técnicas

### ¿La API key expira?

No, las API keys de Gemini **no expiran automáticamente**. Sin embargo, es buena práctica de seguridad:
- Rotarlas cada 6-12 meses
- Revocarlas si sospecha compromiso
- Crear keys diferentes por proyecto

### ¿Puedo compartir mi proyecto con otros sin compartir mi API key?

**Sí**, la mejor opción es:

**Cada usuario usa su propia API key**:
- Cada persona obtiene su propia key gratuita en https://aistudio.google.com/
- Cada uno la ingresa en su propia sesión de la aplicación
- No necesita compartir su API key personal con nadie
- Es gratis y toma solo 2 minutos configurar

---

## RESUMEN RÁPIDO

### 🎯 Checklist de Configuración (Versión Pública - SIMPLE)

- [ ] **1. Obtener API Key**
  - [ ] Ir a https://aistudio.google.com/
  - [ ] Hacer clic en "Get API key"
  - [ ] Copiar la API key completa (empieza con `AIzaSy`)

- [ ] **2. Usar en la Aplicación**
  - [ ] Abrir la aplicación web
  - [ ] Buscar expander "🤖 Análisis IA" en sidebar izquierdo
  - [ ] Pegar API key en el campo de texto
  
- [ ] **3. Probar**
  - [ ] Completar un diseño básico
  - [ ] Hacer clic en "🧮 Calcular Sistema"
  - [ ] Hacer clic en "🔍 Analizar Diseño Actual"
  - [ ] Ver el análisis de Gemini
  
- [ ] ✅ **¡Listo para usar!**

---

### ⚡ Inicio Rápido (3 Pasos)

**Paso 1**: Conseguir API Key
```
https://aistudio.google.com/ → Get API key → Copiar
```

**Paso 2**: Pegar en la app
```
Sidebar → 🤖 Análisis IA → Campo de texto → Pegar API key
```

**Paso 3**: Usar
```
Completar diseño → Calcular → Analizar con IA
```

---

### 📝 Para Recordar

**Tu API key**:
- Empieza con: `AIzaSy`
- Largo: ~39 caracteres
- Ejempl

o: `AIzaSyB1nU2n3PbVJxrVKxsPDLZr0oRqP-...`

**Dónde ingresarla**:
- Sidebar izquierdo
- Expander "🤖 Análisis IA"
- Campo de texto con ícono 🔑

**Cuánto cuesta**:
- GRATIS hasta 1,500 análisis/día
- Más que suficiente para uso normal

---

## RECURSOS ADICIONALES

**Documentación oficial**:
- Gemini API Docs: https://ai.google.dev/docs
- Google AI Studio: https://aistudio.google.com/

---

**Autor**: Patricio Sarmiento Reinoso - Tesis Maestría Hidrosanitaria  
**Versión**: 1.0  
**Fecha**: Enero 2026  

