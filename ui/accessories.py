# Módulo de gestión de accesorios

import streamlit as st
from config.constants import ACCESORIOS_DATA

def get_accesorios_options():
    """Procesa los datos del JSON y retorna opciones para los ComboBox"""
    try:
        valvulas_options = []
        accesorios_options = []
        medidores_options = []
        
        # Procesar válvulas
        for idx, item in enumerate(ACCESORIOS_DATA.get("valvulas", [])):
            display_name = f"{item['singularidad']} - {item['tipo']}"
            valvulas_options.append({
                "display": display_name,
                "data": item,
                "id": f"V{idx+1}"
            })
        
        # Procesar accesorios
        for idx, item in enumerate(ACCESORIOS_DATA.get("accesorios", [])):
            display_name = f"{item['singularidad']} - {item['tipo']}"
            accesorios_options.append({
                "display": display_name,
                "data": item,
                "id": f"A{idx+1}"
            })
        
        # Procesar medidores
        for idx, item in enumerate(ACCESORIOS_DATA.get("medidores", [])):
            display_name = f"{item['singularidad']} - {item['tipo']}"
            medidores_options.append({
                "display": display_name,
                "data": item,
                "id": f"M{idx+1}"
            })
        
        return valvulas_options, accesorios_options, medidores_options
    except Exception as e:
        st.error(f"Error procesando datos de accesorios: {e}")
        return [], [], []

def add_accesorio_selection(seccion, categoria, item_data, cantidad, diam2_mm=None):
    """Agrega una selección de accesorio a la lista correspondiente"""
    if seccion == "succion":
        if "accesorios_succion" not in st.session_state:
            st.session_state.accesorios_succion = []
        lista = st.session_state.accesorios_succion
    else:
        if "accesorios_impulsion" not in st.session_state:
            st.session_state.accesorios_impulsion = []
        lista = st.session_state.accesorios_impulsion
    
    # Crear entrada con formato unificado para compatibilidad con código existente
    entrada = {
        'tipo': f"{item_data['singularidad']} - {item_data['tipo']}",
        'categoria': categoria,
        'id': item_data.get('id', ''),
        'cantidad': cantidad,
        'k': item_data.get('k', 0),
        'lc_d': item_data.get('lc_d_medio', item_data.get('lc_d', 0)),
        'diam2_mm': diam2_mm
    }
    
    lista.append(entrada)
    st.success(f"✅ Agregado: {entrada['tipo']} (Cantidad: {cantidad}, Le/D: {entrada['lc_d']})")
    # Forzar actualización inmediata de la interfaz
    st.rerun()

def render_accessories_panel(section_name: str, session_state_key: str):
    """Renderiza el panel de selección de accesorios para succión o impulsión"""
    
    st.markdown(f"### {section_name}")
    
    # Actualizar automáticamente el diámetro cuando cambie el diámetro interno de la tubería
    if session_state_key == "accesorios_succion":
        diam_real = st.session_state.get('diam_succion_mm', 200.0)
        if f"panel_diam2_{session_state_key}" in st.session_state:
            st.session_state[f"panel_diam2_{session_state_key}"] = diam_real
        
        # Actualizar el diámetro de todos los accesorios existentes
        if 'accesorios_succion' in st.session_state and st.session_state['accesorios_succion']:
            for acc in st.session_state['accesorios_succion']:
                acc['diam2_mm'] = diam_real
    else:
        diam_real = st.session_state.get('diam_impulsion_mm', 150.0)
        if f"panel_diam2_{session_state_key}" in st.session_state:
            st.session_state[f"panel_diam2_{session_state_key}"] = diam_real
        
        # Actualizar el diámetro de todos los accesorios existentes
        if 'accesorios_impulsion' in st.session_state and st.session_state['accesorios_impulsion']:
            for acc in st.session_state['accesorios_impulsion']:
                acc['diam2_mm'] = diam_real
    
    # Obtener opciones de accesorios
    valvulas_options, accesorios_options, medidores_options = get_accesorios_options()
    
    # Combinar todas las opciones en una sola lista por sección con prefijos
    all_options = ["Seleccionar..."]
    
    # Mapas para encontrar los datos originales
    option_map = {"Seleccionar...": None}
    
    # Agregar válvulas
    for opt in valvulas_options:
        display_name = f"📋 {opt['display']}"
        all_options.append(display_name)
        option_map[display_name] = ("valvulas", opt["data"])
    
    # Agregar accesorios  
    for opt in accesorios_options:
        display_name = f"🔧 {opt['display']}"
        all_options.append(display_name)
        option_map[display_name] = ("accesorios", opt["data"])
    
    # Agregar medidores
    for opt in medidores_options:
        display_name = f"📊 {opt['display']}"
        all_options.append(display_name)
        option_map[display_name] = ("medidores", opt["data"])
    
    # Panel de selección
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected = st.selectbox("Seleccionar accesorio:", options=all_options, key=f"panel_selection_{session_state_key}")
    
    with col2:
        cant = st.number_input("Cantidad", min_value=1, value=1, key=f"panel_cant_{session_state_key}")
        
        if f"panel_diam2_{session_state_key}" not in st.session_state:
            if session_state_key == "accesorios_succion":
                # Usar el diámetro interno real calculado por la aplicación
                diam_real = st.session_state.get('diam_succion_mm', 200.0)
                st.session_state[f"panel_diam2_{session_state_key}"] = diam_real
            else:
                # Usar el diámetro interno real calculado por la aplicación
                diam_real = st.session_state.get('diam_impulsion_mm', 150.0)
                st.session_state[f"panel_diam2_{session_state_key}"] = diam_real
        diam2 = st.number_input("Diámetro 2 (mm)", key=f"panel_diam2_{session_state_key}")
        
        if st.button("➕ Agregar", key=f"panel_add_{session_state_key}", help="Agrega el accesorio seleccionado a la lista de accesorios. El accesorio aparecerá inmediatamente en la lista."):
            if selected != "Seleccionar..." and option_map[selected]:
                categoria, item_data = option_map[selected]
                seccion = "succion" if session_state_key == "accesorios_succion" else "impulsion"
                add_accesorio_selection(seccion, categoria, item_data, cant, diam2)
            else:
                st.error("⚠️ Por favor selecciona un accesorio")
    
    # Mostrar información del item seleccionado
    if selected != "Seleccionar..." and option_map[selected]:
        _, item_data = option_map[selected]
        k_val = item_data.get('k', 'N/A')
        lc_d_val = item_data.get('lc_d_medio', item_data.get('lc_d', 'N/A'))
        st.markdown(f"<span style='color:#888888'>📊 **Coeficientes:** k = <b>{k_val}</b> &nbsp;&nbsp; Le/D = <b>{lc_d_val}</b></span>", unsafe_allow_html=True)
        st.markdown(f"<span style='font-size:12px;color:#666666'>📋 {item_data.get('descripcion', 'Sin descripción')}</span>", unsafe_allow_html=True)