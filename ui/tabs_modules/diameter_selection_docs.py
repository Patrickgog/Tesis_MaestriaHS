"""
Módulo de documentación técnica para selección de diámetros con diseño de 3 columnas (40-40-20)
"""

import streamlit as st
import pandas as pd


def render_technical_documentation():
    """Renderiza la pestaña de Análisis de Resultados con diseño profesional de 3 columnas"""
    
    st.title("📊 Análisis de Resultados y Diagnóstico Hidráulico")
    
    res_suc = st.session_state.get('last_pt_res_suc')
    res_imp = st.session_state.get('last_pt_res_imp')
    
    if not res_suc and not res_imp:
        st.warning("⚠️ **Sin datos de análisis:** Por favor, seleccione un diámetro en las pestañas de Succión o Impulsión para ver el diagnóstico detallado aquí.")
        return

    st.markdown("---")

    # DISEÑO DE 3 COLUMNAS: 40% - 40% - 20%
    col_analisis_1, col_analisis_2, col_guia_links = st.columns([0.4, 0.4, 0.2])

    # --- COLUMNA 1: DIAGNÓSTICO DE DINÁMICA Y ENERGÍA (40%) ---
    with col_analisis_1:
        st.markdown("### 🚀 1. Dinámica y Eficiencia")
        
        # Succión
        st.markdown("#### 💧 Succión")
        if res_suc:
            di_s = st.session_state.get('last_pt_di_suc', 0)
            v_s = res_suc['velocity']
            j_s = res_suc['hydraulic_gradient'] * 1000
            st.markdown(f"**Para DN {di_s:.1f} mm:**")
            if 0.6 <= v_s <= 0.9: 
                st.success(f"Velocidad: {v_s:.2f} m/s (Óptima)")
            else: 
                st.error(f"Velocidad: {v_s:.2f} m/s (Revisar)")
            
            st.info(f"**Costo Energético (J):** {j_s:.2f} m/km. *El Gradiente J representa las pérdidas por km; valores altos indican ineficiencia.*")
        else:
            st.write("*Sin datos de succión.*")

        st.divider()
        
        # Impulsión
        st.markdown("#### 🚀 Impulsión")
        if res_imp:
            di_i = st.session_state.get('last_pt_di_imp', 0)
            v_i = res_imp['velocity']
            j_i = res_imp['hydraulic_gradient'] * 1000
            st.markdown(f"**Para DN {di_i:.1f} mm:**")
            if 1.0 <= v_i <= 2.5: 
                st.success(f"Velocidad: {v_i:.2f} m/s (Óptima)")
            else: 
                st.warning(f"Velocidad: {v_i:.2f} m/s (Fuera de rango)")
            
            if j_i < 15: 
                st.success(f"**Eficiencia (J):** {j_i:.2f} m/km")
            else: 
                st.error(f"**Ineficiencia (J):** {j_i:.2f} m/km. *Exceso de pérdida por fricción.*")
        else:
            st.write("*Sin datos de impulsión.*")

    # --- COLUMNA 2: SEGURIDAD Y ESTABILIDAD (40%) ---
    with col_analisis_2:
        st.markdown("### 🛡️ 2. Seguridad y Estabilidad")
        
        st.markdown("#### 🌊 Cavitación (NPSH)")
        if res_suc:
            npshd = res_suc['npsh_available']
            npshr = st.session_state.get('npsh_requerido', 3.0)
            margen = npshd - npshr
            st.markdown(f"**Para DN {di_s:.1f} mm:**")
            if margen > 1.0: 
                st.success(f"Margen NPSH: {margen:.2f} m (Seguro)")
            elif margen > 0.5: 
                st.warning(f"Margen NPSH: {margen:.2f} m (Ajustado)")
            else: 
                st.error(f"Margen NPSH: {margen:.2f} m (¡RIESGO!)")
        else:
            st.write("*Requiere análisis de succión.*")

        st.divider()

        st.markdown("#### 🛡️ Integridad Estructural")
        if res_imp:
            presion_kpa = res_imp['pressure_kpa']
            pn_tuberia = st.session_state.get('presion_nominal', 1000)
            uso_pn = (presion_kpa / pn_tuberia) * 100
            st.markdown(f"**Para DN {di_i:.1f} mm:**")
            if uso_pn < 80:
                st.success(f"Presión: {presion_kpa:.1f} kPa ({uso_pn:.1f}% de la PN)")
            else:
                st.error(f"Presión: {presion_kpa:.1f} kPa ({uso_pn:.1f}% de la PN).")
        else:
            st.write("*Requiere análisis de impulsión.*")

    # --- COLUMNA 3: GUÍA TÉCNICA Y EXPORTACIÓN (20%) ---
    with col_guia_links:
        st.markdown("### 📚 Guía")
        with st.expander("🔗 Límite Técnico", expanded=True):
            st.markdown("""
            La **línea punteada** marca el punto donde el sistema se vuelve inestable. 
            
            ✅ **A la Derecha:** Zona robusta.
            
            ❌ **A la Izquierda:** Zona asintótica (pérdidas disparadas).
            """)
        
        st.divider()
        st.markdown("### 🤖 IA vs Técnica")
        st.caption("La IA busca el costo mínimo, este análisis asegura que ese punto sea estable hidráulicamente.")
        
        st.divider()
        st.markdown("### 📥 Reportes")
        
        doc_markdown = generate_technical_doc_content()
        
        st.download_button(label="📄 Guía MD", data=doc_markdown, file_name="Reporte_Hidraulico.md", mime="text/markdown", use_container_width=True)
        
        try:
            html_doc = generate_html_doc(doc_markdown)
            st.download_button(label="🌐 Reporte HTML", data=html_doc, file_name="Reporte_Hidraulico.html", mime="text/html", use_container_width=True)
        except Exception as e: st.error(f"Error HTML: {e}")


def generate_technical_doc_content():
    """Genera el contenido técnico exhaustivo con análisis dinámico y definiciones de ingeniería"""
    
    res_suc = st.session_state.get('last_pt_res_suc')
    res_imp = st.session_state.get('last_pt_res_imp')
    di_s = st.session_state.get('last_pt_di_suc', 0)
    di_i = st.session_state.get('last_pt_di_imp', 0)
    
    analisis_detallado = ""
    if res_suc and res_imp:
        analisis_detallado = f"""
### 📍 Resultados por Punto Específico
- **Succión (DN {di_s:.1f} mm):** Velocidad de {res_suc['velocity']:.2f} m/s y NPSH Disponible de {res_suc['npsh_available']:.2f} m.
- **Impulsión (DN {di_i:.1f} mm):** Velocidad de {res_imp['velocity']:.2f} m/s y Gradiente J de {res_imp['hydraulic_gradient']*1000:.2f} m/km.
"""

    content = f"""
## Reporte Técnico de Ingeniería Hidráulica

Este informe analiza el comportamiento del flujo y valida el diseño frente a leyes físicas y económicas.

---

### 1️⃣ Estabilidad de Flujo (Velocidad)
**Definición:** La velocidad define la capacidad operativa. Si es baja, hay sedimentación; si es alta, erosión.
**Veredicto:** El diseño en DN {di_i:.1f} mm busca maximizar la vida útil de la tubería.

{analisis_detallado}

---

### 2️⃣ El Impuesto Energético (Gradiente J)
**Definición:** J representa los metros de presión que se pierden por cada kilómetro de red. 
**Análisis:** Un gradiente bajo reduce directamente el OPEX (factura eléctrica). Se recomienda mantenerse en el rango de 10-15 m/km.

---

### 3️⃣ Seguridad Operativa (NPSH y Cavitación)
**Definición:** El NPSH es la energía mínima que el líquido debe tener en la entrada para no 'hervir' en frío debido a la succión. La cavitación destruye los impulsores de la bomba en horas.

---

### 4️⃣ Criterio de la IA vs Ingeniería
El algoritmo genético (IA) integrado busca el **mínimo costo total**. Este reporte técnico complementa esa búsqueda asegurando que el punto elegido no esté en la **zona asintótica** (izquierda de la línea punteada), donde el sistema se vuelve altamente sensible y vibrante.

---
*Generado por App Bombeo - Especialización en Hidráulica*
"""
    return content


def generate_html_doc(markdown_content):
    """Genera documento HTML profesional con estilo corporativo"""
    import markdown
    
    res_suc = st.session_state.get('last_pt_res_suc')
    res_imp = st.session_state.get('last_pt_res_imp')
    
    session_report = "<div class='session-header'>📊 Resumen Ejecutivo</div><div class='session-container'>"
    if res_suc:
        session_report += f"<div class='card card-suc'><b>💧 SUCCIÓN</b><br>v={res_suc['velocity']:.2f} m/s<br>NPSH={res_suc['npsh_available']:.2f} m</div>"
    if res_imp:
        session_report += f"<div class='card card-imp'><b>🚀 IMPULSIÓN</b><br>v={res_imp['velocity']:.2f} m/s<br>J={res_imp['hydraulic_gradient']*1000:.2f} m/km</div>"
    session_report += "</div>"

    processed_content = markdown.markdown(markdown_content, extensions=['extra'])
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; color: #222; max-width: 850px; margin: 40px auto; padding: 30px; background: #f4f7f9; }}
        .wrapper {{ background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1, h2 {{ color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }}
        .session-header {{ background: #1e3a8a; color: white; padding: 12px; border-radius: 8px 8px 0 0; font-weight: bold; }}
        .session-container {{ display: flex; gap: 15px; border: 2px solid #1e3a8a; padding: 20px; border-radius: 0 0 8px 8px; margin-bottom: 40px; }}
        .card {{ flex: 1; padding: 15px; border-radius: 8px; font-size: 0.95em; }}
        .card-suc {{ background: #ecfdf5; border: 1px solid #10b981; color: #065f46; }}
        .card-imp {{ background: #fffbeb; border: 1px solid #f59e0b; color: #92400e; }}
        .content {{ line-height: 1.7; }}
    </style>
</head>
<body>
    <div class="wrapper">
        <h1>Análisis Hidráulico de Diámetros</h1>
        {session_report}
        <div class="content">{processed_content}</div>
    </div>
</body>
</html>
"""
    return html
