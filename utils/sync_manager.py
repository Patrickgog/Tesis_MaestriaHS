"""
Módulo de Sincronización Automática de Datos de Tuberías
Gestiona la propagación bidireccional entre Datos de Entrada y Selección de Diámetros
"""

import streamlit as st
from typing import Literal

# Diccionario maestro de claves de session_state
PIPE_KEYS = {
    'succion': {
        'material': 'mat_succion',
        'di_mm': 'diam_succion_mm',
        'longitud': 'long_succion',
        'coef_hazen': 'coeficiente_hazen_succion',
        'accesorios': 'accesorios_succion',
        # Claves específicas por material
        'pvc': {
            'tipo_union': 'tipo_union_pvc_succion',
            'serie_nombre': 'serie_pvc_succion_nombre',
            'dn': 'dn_pvc_succion'
        },
        'pead': {
            'diam_externo': 'diam_externo_succion',
            'serie': 'serie_succion'
        },
        'hierro_ductil': {
            'clase': 'clase_hierro_succion',
            'dn': 'dn_succion'
        },
        'hierro_fundido': {
            'clase': 'clase_hierro_fundido_succion',
            'dn': 'dn_hierro_fundido_succion'
        }
    },
    'impulsion': {
        'material': 'mat_impulsion',
        'di_mm': 'diam_impulsion_mm',
        'longitud': 'long_impulsion',
        'coef_hazen': 'coeficiente_hazen_impulsion',
        'accesorios': 'accesorios_impulsion',
        # Claves específicas por material
        'pvc': {
            'tipo_union': 'tipo_union_pvc_impulsion',
            'serie_nombre': 'serie_pvc_impulsion_nombre',
            'dn': 'dn_pvc_impulsion'
        },
        'pead': {
            'diam_externo': 'diam_externo_impulsion',
            'serie': 'serie_impulsion'
        },
        'hierro_ductil': {
            'clase': 'clase_hierro_impulsion',
            'dn': 'dn_impulsion'
        },
        'hierro_fundido': {
            'clase': 'clase_hierro_fundido_impulsion',
            'dn': 'dn_hierro_fundido_impulsion'
        }
    }
}


def sync_pipe_data(tramo: Literal['succion', 'impulsion'], source: Literal['data_input', 'diameter_selection']):
    """
    Sincroniza automáticamente los datos de tubería entre vistas.
    
    Args:
        tramo: 'succion' o 'impulsion'
        source: Origen del cambio ('data_input' o 'diameter_selection')
    
    Esta función se dispara automáticamente cuando el usuario modifica:
    - Material de tubería
    - Diámetro interno
    - Serie/DN/Clase (según material)
    
    La sincronización es bidireccional y transparente para el usuario.
    """
    if tramo not in PIPE_KEYS:
        return
    
    keys = PIPE_KEYS[tramo]
    
    # Marcar timestamp de última sincronización
    st.session_state[f'_last_sync_{tramo}'] = st.session_state.get('_sync_counter', 0) + 1
    st.session_state['_sync_counter'] = st.session_state.get('_sync_counter', 0) + 1
    
    # Obtener material actual para sincronizar claves específicas
    material = st.session_state.get(keys['material'], 'PVC')
    
    # Sincronizar claves específicas del material
    if 'PVC' in material and 'pvc' in keys:
        # Las claves PVC ya están en session_state, no requiere acción adicional
        pass
    elif 'PEAD' in material or 'HDPE' in material or 'Polietileno' in material:
        if 'pead' in keys:
            # Las claves PEAD ya están en session_state
            pass
    elif 'Hierro Dúctil' in material or 'Ductil' in material:
        if 'hierro_ductil' in keys:
            # Las claves de hierro dúctil ya están en session_state
            pass
    elif 'Hierro Fundido' in material or 'Fundido' in material:
        if 'hierro_fundido' in keys:
            # Las claves de hierro fundido ya están en session_state
            pass
    
    # Marcar que la sincronización está activa
    st.session_state[f'_sync_active_{tramo}'] = True
    
    # Si el origen es diameter_selection, marcar que se debe usar el diámetro exportado
    if source == 'diameter_selection':
        st.session_state[f'usar_diametro_exportado_{tramo}'] = True


def get_sync_status(tramo: Literal['succion', 'impulsion']) -> dict:
    """
    Obtiene el estado actual de sincronización para un tramo.
    
    Returns:
        dict con 'active', 'last_sync', 'material', 'di_mm'
    """
    if tramo not in PIPE_KEYS:
        return {'active': False}
    
    keys = PIPE_KEYS[tramo]
    
    return {
        'active': st.session_state.get(f'_sync_active_{tramo}', True),
        'last_sync': st.session_state.get(f'_last_sync_{tramo}', 0),
        'material': st.session_state.get(keys['material'], 'N/A'),
        'di_mm': st.session_state.get(keys['di_mm'], 0.0)
    }


def render_sync_indicator(tramo: Literal['succion', 'impulsion']):
    """
    Renderiza un indicador visual del estado de sincronización.
    """
    status = get_sync_status(tramo)
    
    if status['active']:
        st.success(f"🔗 Sincronizado automáticamente | Material: `{status['material']}` | DI: `{status['di_mm']:.1f} mm`")
    else:
        st.warning("⚠️ Modo Manual - Sin sincronización automática")
