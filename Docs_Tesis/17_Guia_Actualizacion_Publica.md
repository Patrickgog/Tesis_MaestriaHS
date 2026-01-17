# 🚀 Guía: Cómo Actualizar la Versión Pública (Commit y Push)

Como consultor técnico, entiendo que no necesitas ser programador para gestionar tu aplicación. Esta guía traduce los términos de software al lenguaje de gestión de proyectos de ingeniería.

---

## 🏗️ La Analogía del Proyecto de Ingeniería

Para entender el proceso, imagina que estamos trabajando en los **planos de un sistema de bombeo** que se está construyendo en obra.

### 1. **Los Cambios Locales** (El Trabajo en el Tablero)
Tú abres un archivo en tu PC (un JSON de costos o un código de Python) y haces cambios. Esto es como si estuvieras dibujando directamente sobre el plano en tu escritorio. 
*   **Estado**: El cambio solo existe en tu oficina.

### 2. **Commit** (El Sello de Aprobación)
Cuando terminas un cambio y estás satisfecho, haces un **Commit**.
*   **Significado**: Es como ponerle un sello de **"REVISADO Y APROBADO"** al plano y guardarlo en tu archivador de versiones.
*   **Función**: Te permite tener un historial. Si el cambio de hoy falla, puedes volver al "plano sellado" de ayer.

### 3. **Push** (El Envío a Supervisión y Obra)
Una vez que tienes tus cambios sellados (commits), haces un **Push**.
*   **Significado**: Es enviar esos planos aprobados a la **Nube (GitHub)**. 
*   **Resultado**: En cuanto los planos llegan a GitHub, la plataforma de Streamlit los lee y actualiza el **Link Público** automáticamente.

---

## � ¿Cómo sabe mi PC a qué repositorio enviar los cambios?

En el mundo de Git, tu carpeta local (`Tesis_MaestriaHS`) tiene una "dirección de envío" guardada internamente llamada **Remote** (Remoto). Es como tener configurada la dirección de la oficina central en el GPS de tu camión de reparto.

### Cómo verificar tu conexión:
Si quieres estar 100% seguro de a dónde se enviarán tus cambios, abre una terminal en tu carpeta y escribe:
```bash
git remote -v
```
**Resultado esperado:** Deberías ver la URL de tu repositorio:
`origin  https://github.com/Patrickgog/Tesis_MaestriaHS.git (fetch)`
`origin  https://github.com/Patrickgog/Tesis_MaestriaHS.git (push)`

### ¿Cómo me "conecto" si no lo estoy?
Si estás usando la carpeta que configuramos originalmente, **ya estás conectado**. Git no te pide usuario y contraseña cada vez porque VS Code o Windows guardan tus credenciales de GitHub de forma segura (Token de Acceso). 

Si alguna vez intentas hacer un `Push` y te sale un error de "Permiso denegado", simplemente significa que la "llave" (el Token) expiró y GitHub te pedirá que inicies sesión nuevamente en una ventana emergente.

---

## �🛠️ Guía Paso a Paso para Actualizar la App

Si decides realizar cambios manuales en tu carpeta local base (`Tesis_MaestriaHS`) y quieres que se vean en el link público, estos son los comandos que debes usar en una terminal (o simplemente pedírmelos a mí):

### Paso 1: "Sellar" los cambios (Commit)
Escribe esto para preparar y nombrar tus cambios:
```bash
git add .
git commit -m "Descripción breve del cambio (ej: Actualización de costos PVC)"
```

### Paso 2: "Publicar" los cambios (Push)
Escribe esto para enviar todo a la nube:
```bash
git push origin public
```
*(Nota: Usamos `public` porque es la rama que alimenta tu link oficial).*

---

## 💡 Recomendación de Oro
**No necesitas memorizar esto.** Como tu asistente senior, la forma más segura y rápida de actualizar la versión pública es simplemente decirme:

> *"Antigravity, acabo de editar los precios de PVC en mi PC. Por favor, haz **Commit** y **Push** a la versión pública."*

Yo me encargaré de limpiar el historial, verificar que no haya errores y asegurar que el link se actualice correctamente por ti.
