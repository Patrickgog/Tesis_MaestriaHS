
def render_bombas_comerciales_editor(marca: str):
    """Editor para tablas de bombas comerciales"""
    import pandas as pd
    import json
    import os
    import streamlit as st
    
    st.markdown(f"#### 🏭 Catálogo de Bombas {marca}")
    
    # Cargar archivo
    archivo = f"data_tablas/bombas_{marca.lower()}_data.json"
    if not os.path.exists(archivo):
        st.error(f"No se encontró el archivo de datos: {archivo}")
        return
        
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return
        
    # Mostrar metadatos
    st.text_input("Descripción del Catálogo:", value=data.get('descripcion', ''), key=f"desc_{marca}", disabled=True)
    st.text_input("URL del Catálogo:", value=data.get('url_catalogo', ''), key=f"url_{marca}", disabled=True)
    st.caption(f"Última actualización: {data.get('ultima_actualizacion', 'No especificada')}")
    
    # Resumen
    if data.get('categorias'):
        total_bombas = sum(len(cat.get('bombas', [])) for cat in data['categorias'])
        st.success(f"✅ **{len(data['categorias'])} categorías** con **{total_bombas} bombas** en el catálogo")
        
        # Tabla resumen
        for cat in data['categorias']:
            with st.expander(f"📂 {cat.get('categoria', 'Categoría')}", expanded=False):
                st.metric("Bombas", len(cat.get('bombas', [])))
                st.caption(f"Rangos: Q={cat.get('rango_caudal_min_lps')}-{cat.get('rango_caudal_max_lps')} L/s, H={cat.get('rango_altura_min_m')}-{cat.get('rango_altura_max_m')} m")
                
                if cat.get('bombas'):
                    bombas_list = []
                    for b in cat['bombas']:
                        bombas_list.append({
                            "Modelo": b.get('modelo'),
                            "HP": b.get('potencia_hp'),
                            "kW": b.get('potencia_kw'),
                            "RPM": b.get('rpm'),
                            "Etapas": b.get('etapas')
                        })
                    st.dataframe(pd.DataFrame(bombas_list), use_container_width=True)
    else:
        st.info("No hay categorías configuradas")
    
    # Botones
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Recargar", key=f"reload_{marca}"):
            st.rerun()
    with col2:
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        st.download_button("📥 Descargar JSON", json_str, f"bombas_{marca.lower()}.json", "application/json", key=f"dl_{marca}")
    with col3:
        st.caption("Ver/editar JSON")
    
    st.info(f"💡 Para editar bombas, descarga el JSON, modifícalo y reemplázalo en `data_tablas/{archivo}`")
