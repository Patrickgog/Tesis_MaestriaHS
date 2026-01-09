# Gestión de proyectos

def fix_mixed_types_in_accessories(accesorios_list):
    """
    Corrige tipos mixtos en la columna 'k' de los accesorios para evitar errores de PyArrow.
    
    Args:
        accesorios_list: Lista de diccionarios con datos de accesorios
    
    Returns:
        Lista corregida con tipos consistentes
    """
    if not accesorios_list:
        return accesorios_list
    
    for acc in accesorios_list:
        if 'k' in acc and isinstance(acc['k'], (int, float)):
            acc['k'] = str(acc['k'])
    
    return accesorios_list

def fix_mixed_types_in_dataframe(df):
    """
    Función helper para corregir tipos mixtos en DataFrames de accesorios.
    Aplica el fix global para evitar errores de PyArrow con tipos mixtos.
    
    Args:
        df: DataFrame de pandas
    
    Returns:
        DataFrame corregido con tipos consistentes
    """
    if df is None or df.empty:
        return df
    
    # Crear una copia para evitar modificar el DataFrame original
    df_fixed = df.copy()
    
    # FIX GLOBAL: Convertir columnas problemáticas a string para evitar errores de PyArrow
    problematic_columns = ['k', 'K', 'cantidad', 'Cantidad']
    for col in problematic_columns:
        if col in df_fixed.columns:
            # Convertir todos los valores a string, manejando NaN y None
            df_fixed[col] = df_fixed[col].astype(str)
            # Reemplazar 'nan' string con 'N/A' para mejor visualización
            df_fixed[col] = df_fixed[col].replace('nan', 'N/A')
            df_fixed[col] = df_fixed[col].replace('None', 'N/A')
    
    # Opcional: Corrige otras columnas mixtas si las hay (e.g., 'lc_d' si es str)
    numeric_columns = ['lc_d', 'Lc/D', 'lc_d_medio', 'Lc/D Medio']
    for col in numeric_columns:
        if col in df_fixed.columns:
            df_fixed[col] = pd.to_numeric(df_fixed[col], errors='coerce')  # Numérico, NaN si falla
    
    return df_fixed

import json
import os
from typing import Dict, Any, Optional
import streamlit as st
import pandas as pd

def save_project_state(filename: Optional[str] = None) -> bool:
    """
    Guarda el estado actual del proyecto en un archivo JSON.
    Incluye TODOS los elementos del layout: accesorios, VFD, bomba seleccionada, etc.
    Versión mejorada que funciona con cualquier archivo JSON cargado.
    
    Args:
        filename: Nombre del archivo (opcional)
    
    Returns:
        True si se guardó exitosamente, False en caso contrario
    """
    try:
        # 1. VALIDACIÓN PREVIA
        validation_result = validate_project_data()
        if not validation_result['valid']:
            st.error(f"❌ Datos inválidos: {validation_result['errors']}")
            return False
        
        # 2. RECOPILAR TODOS LOS INPUTS DEL SESSION_STATE
        project_data = collect_all_inputs_from_session_state()
        
        # 3. INTENTAR OBTENER DATOS COMPLETOS DESDE AI_MODULE
        try:
            from ui.ai_module import generar_datos_json
            datos_completos = generar_datos_json()
            
            # Agregar inputs desde AI module si están disponibles
            if 'inputs' in datos_completos:
                import copy
                ai_inputs = copy.deepcopy(datos_completos['inputs'])
                project_data.update(ai_inputs)
            
            # Agregar resultados desde AI module si están disponibles
            if 'resultados' in datos_completos:
                project_data.update(datos_completos['resultados'])
            
            # Agregar datos adicionales si existen
            if 'datos_adicionales' in datos_completos:
                project_data.update(datos_completos['datos_adicionales'])
            
            # Agregar tablas de gráficos RPM si están disponibles
            if 'tablas_graficos' in datos_completos:
                project_data['tablas_graficos'] = datos_completos['tablas_graficos']
                
        except Exception as e:
            st.warning(f"⚠️ No se pudieron obtener datos desde AI module: {str(e)}")
            st.info("📝 Continuando con datos del session_state...")
        
        # 4. GENERAR TABLAS DE 100% RPM SI NO EXISTEN O ESTÁN VACÍAS
        if 'tablas_graficos' not in project_data or not project_data.get('tablas_graficos', {}).get('tablas_100_rpm'):
            st.info("🔄 Generando tablas de 100% RPM...")
            tablas_100_rpm = generate_100_rpm_tables_validated(project_data)
            if tablas_100_rpm:
                if 'tablas_graficos' not in project_data:
                    project_data['tablas_graficos'] = {}
                project_data['tablas_graficos']['tablas_100_rpm'] = tablas_100_rpm
        
        # 5. GENERAR DATOS VFD SI NO EXISTEN O ESTÁN INCOMPLETOS
        if 'vfd' not in project_data or not project_data.get('vfd', {}).get('curvas_vfd'):
            st.info("🔄 Generando datos VFD...")
            vfd_data = generate_vdf_data_validated(project_data)
            if vfd_data:
                project_data['vfd'] = vfd_data
        
        # 6. GENERAR CURVAS_PUNTOS SI NO EXISTEN
        if 'curvas_puntos' not in project_data or not any(project_data.get('curvas_puntos', {}).values()):
            st.info("🔄 Generando curvas_puntos...")
            project_data['curvas_puntos'] = generate_curvas_puntos_from_texto(project_data)
        
        # 7. AGREGAR BOMBA_SELECCIONADA SI NO EXISTE
        if 'bomba_seleccionada' not in project_data or not project_data.get('bomba_seleccionada'):
            project_data['bomba_seleccionada'] = generate_bomba_seleccionada_data()
        
        # 8. SERIALIZAR OBJETOS NO SERIALIZABLES
        project_data = serialize_project_data(project_data)
        
        # 9. VALIDACIÓN FINAL
        if not validate_complete_project(project_data):
            st.error("❌ Proyecto incompleto - no se puede guardar")
            return False
        
        # 10. DETERMINAR RUTA DEL ARCHIVO
        filepath = determine_filepath(filename)
        
        # 11. GUARDAR ARCHIVO
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        # 12. ACTUALIZAR RUTA DEL PROYECTO ACTUAL
        st.session_state['current_project_path'] = filepath
        
        st.success(f"✅ Proyecto guardado exitosamente: {os.path.basename(filepath)}")
        return True
        
    except Exception as e:
        st.error(f"❌ Error al guardar el proyecto: {str(e)}")
        import traceback
        st.error(f"Detalles del error: {traceback.format_exc()}")
        return False

def load_project_state(file_path: str) -> bool:
    """
    Carga el estado del proyecto desde un archivo JSON.
    
    Args:
        file_path: Ruta del archivo a cargar
    
    Returns:
        True si se cargó exitosamente, False en caso contrario
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        # Limpiar session_state antes de cargar (igual que en app.py original)
        keys_to_clear = [
            'proyecto', 'diseno', 'proyecto_input_main', 'diseno_input_main',
            'temp_liquido', 'densidad_liquido',
            'caudal_lps', 'caudal_m3h', 'elevacion_sitio', 'altura_succion_input',
            'bomba_inundada', 'altura_descarga', 'num_bombas',
            'long_succion', 'diam_succion_mm', 'mat_succion', 'otras_perdidas_succion', 'accesorios_succion',
            'long_impulsion', 'diam_impulsion_mm', 'mat_impulsion', 'otras_perdidas_impulsion', 'accesorios_impulsion',
            'curva_inputs', 'calibration_points', 'digitalized_points',
            'presion_barometrica_calculada', 'presion_vapor_calculada',
            'rpm_percentage', 'curvas_vfd', 'caudal_nominal', 'paso_caudal_vfd',
            'adt_caudales_personalizados', 'bomba_url', 'bomba_nombre', 'bomba_descripcion',
            # Valores calculados del punto de operación (invalidar para que IA use datos actuales)
            'caudal_operacion', 'altura_operacion', 'interseccion',
            'eficiencia_operacion', 'potencia_operacion', 'npsh_requerido', 'npsh_margen',
            # Datos específicos de materiales para succión
            'diam_externo_succion', 'diam_externo_succion_index', 'serie_succion', 'serie_succion_index',
            'clase_hierro_succion', 'clase_hierro_succion_index', 'dn_succion', 'dn_succion_index',
            'clase_hierro_fundido_succion', 'clase_hierro_fundido_succion_index', 'dn_hierro_fundido_succion', 'dn_hierro_fundido_succion_index',
            'tipo_union_pvc_succion', 'tipo_union_pvc_succion_index', 'serie_pvc_succion_nombre', 'serie_pvc_succion_nombre_index', 'dn_pvc_succion', 'dn_pvc_succion_index',
            # Datos específicos de materiales para impulsión
            'diam_externo_impulsion', 'diam_externo_impulsion_index', 'serie_impulsion', 'serie_impulsion_index',
            'clase_hierro_impulsion', 'clase_hierro_impulsion_index', 'dn_impulsion', 'dn_impulsion_index',
            'clase_hierro_fundido_impulsion', 'clase_hierro_fundido_impulsion_index', 'dn_hierro_fundido_impulsion', 'dn_hierro_fundido_impulsion_index',
            'tipo_union_pvc_impulsion', 'tipo_union_pvc_impulsion_index', 'serie_pvc_impulsion_nombre', 'serie_pvc_impulsion_nombre_index', 'dn_pvc_impulsion', 'dn_pvc_impulsion_index'
        ]
        
        # Limpiar también todos los textarea_
        for key in list(st.session_state.keys()):
            if key.startswith('textarea_'):
                keys_to_clear.append(key)
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Datos del proyecto y diseño
        st.session_state['proyecto'] = project_data.get('proyecto', '')
        st.session_state['diseno'] = project_data.get('diseno', '')
        st.session_state['proyecto_input_main'] = project_data.get('proyecto', '')
        st.session_state['diseno_input_main'] = project_data.get('diseno', '')
        
        # Datos de la barra lateral (solo los que no son widgets)
        st.session_state['temp_liquido'] = project_data.get('temp_liquido', 20.0)
        st.session_state['densidad_liquido'] = project_data.get('densidad_liquido', 1.0)
        
        # 1. Condiciones de Operación
        st.session_state['caudal_lps'] = project_data.get('caudal_lps', 51.0)
        st.session_state['caudal_m3h'] = project_data.get('caudal_m3h', 183.6)
        st.session_state['elevacion_sitio'] = project_data.get('elevacion_sitio', 450.0)
        st.session_state['altura_succion_input'] = project_data.get('altura_succion_input', 1.65)
        st.session_state['bomba_inundada'] = project_data.get('bomba_inundada', False)
        st.session_state['altura_descarga'] = project_data.get('altura_descarga', 80.0)
        st.session_state['num_bombas'] = project_data.get('num_bombas', 1)
        
        # 2. Tubería y Accesorios de Succión
        st.session_state['long_succion'] = project_data.get('long_succion', 10.0)
        st.session_state['diam_succion_mm'] = project_data.get('diam_succion_mm', 200.0)
        st.session_state['mat_succion'] = project_data.get('mat_succion', 'PVC')
        st.session_state['otras_perdidas_succion'] = project_data.get('otras_perdidas_succion', 0.0)
        st.session_state['accesorios_succion'] = fix_mixed_types_in_accessories(project_data.get('accesorios_succion', []))
        
        # Datos específicos de materiales para succión
        # PEAD/HDPE
        st.session_state['diam_externo_succion'] = project_data.get('diam_externo_succion', None)
        st.session_state['diam_externo_succion_index'] = project_data.get('diam_externo_succion_index', 0)
        st.session_state['serie_succion'] = project_data.get('serie_succion', None)
        st.session_state['serie_succion_index'] = project_data.get('serie_succion_index', 0)
        
        # Hierro Dúctil
        st.session_state['clase_hierro_succion'] = project_data.get('clase_hierro_succion', None)
        st.session_state['clase_hierro_succion_index'] = project_data.get('clase_hierro_succion_index', 0)
        st.session_state['dn_succion'] = project_data.get('dn_succion', None)
        st.session_state['dn_succion_index'] = project_data.get('dn_succion_index', 0)
        
        # Hierro Fundido
        st.session_state['clase_hierro_fundido_succion'] = project_data.get('clase_hierro_fundido_succion', None)
        st.session_state['clase_hierro_fundido_succion_index'] = project_data.get('clase_hierro_fundido_succion_index', 0)
        st.session_state['dn_hierro_fundido_succion'] = project_data.get('dn_hierro_fundido_succion', None)
        st.session_state['dn_hierro_fundido_succion_index'] = project_data.get('dn_hierro_fundido_succion_index', 0)
        
        # PVC
        st.session_state['tipo_union_pvc_succion'] = project_data.get('tipo_union_pvc_succion', None)
        st.session_state['tipo_union_pvc_succion_index'] = project_data.get('tipo_union_pvc_succion_index', 0)
        st.session_state['serie_pvc_succion_nombre'] = project_data.get('serie_pvc_succion_nombre', None)
        st.session_state['serie_pvc_succion_nombre_index'] = project_data.get('serie_pvc_succion_nombre_index', 0)
        st.session_state['dn_pvc_succion'] = project_data.get('dn_pvc_succion', None)
        st.session_state['dn_pvc_succion_index'] = project_data.get('dn_pvc_succion_index', 0)
        
        # 3. Tubería y Accesorios de Impulsión
        st.session_state['long_impulsion'] = project_data.get('long_impulsion', 500.0)
        st.session_state['diam_impulsion_mm'] = project_data.get('diam_impulsion_mm', 150.0)
        st.session_state['mat_impulsion'] = project_data.get('mat_impulsion', 'PVC')
        st.session_state['otras_perdidas_impulsion'] = project_data.get('otras_perdidas_impulsion', 0.0)
        st.session_state['accesorios_impulsion'] = fix_mixed_types_in_accessories(project_data.get('accesorios_impulsion', []))
        
        # Datos específicos de materiales para impulsión
        # PEAD/HDPE
        st.session_state['diam_externo_impulsion'] = project_data.get('diam_externo_impulsion', None)
        st.session_state['diam_externo_impulsion_index'] = project_data.get('diam_externo_impulsion_index', 0)
        st.session_state['serie_impulsion'] = project_data.get('serie_impulsion', None)
        st.session_state['serie_impulsion_index'] = project_data.get('serie_impulsion_index', 0)
        
        # Hierro Dúctil
        st.session_state['clase_hierro_impulsion'] = project_data.get('clase_hierro_impulsion', None)
        st.session_state['clase_hierro_impulsion_index'] = project_data.get('clase_hierro_impulsion_index', 0)
        st.session_state['dn_impulsion'] = project_data.get('dn_impulsion', None)
        st.session_state['dn_impulsion_index'] = project_data.get('dn_impulsion_index', 0)
        
        # Hierro Fundido
        st.session_state['clase_hierro_fundido_impulsion'] = project_data.get('clase_hierro_fundido_impulsion', None)
        st.session_state['clase_hierro_fundido_impulsion_index'] = project_data.get('clase_hierro_fundido_impulsion_index', 0)
        st.session_state['dn_hierro_fundido_impulsion'] = project_data.get('dn_hierro_fundido_impulsion', None)
        st.session_state['dn_hierro_fundido_impulsion_index'] = project_data.get('dn_hierro_fundido_impulsion_index', 0)
        
        # PVC
        st.session_state['tipo_union_pvc_impulsion'] = project_data.get('tipo_union_pvc_impulsion', None)
        st.session_state['tipo_union_pvc_impulsion_index'] = project_data.get('tipo_union_pvc_impulsion_index', 0)
        st.session_state['serie_pvc_impulsion_nombre'] = project_data.get('serie_pvc_impulsion_nombre', None)
        st.session_state['serie_pvc_impulsion_nombre_index'] = project_data.get('serie_pvc_impulsion_nombre_index', 0)
        st.session_state['dn_pvc_impulsion'] = project_data.get('dn_pvc_impulsion', None)
        st.session_state['dn_pvc_impulsion_index'] = project_data.get('dn_pvc_impulsion_index', 0)
        
        # 4. Ajuste de Curvas Características (3 puntos)
        st.session_state['curva_inputs'] = project_data.get('curva_inputs', {})
        
        # Datos de calibración y digitalización (si existen)
        st.session_state['calibration_points'] = project_data.get('calibration_points', None)
        st.session_state['digitalized_points'] = project_data.get('digitalized_points', [])
        
        # Campos adicionales que podrían estar faltando
        st.session_state['presion_barometrica_calculada'] = project_data.get('presion_barometrica_calculada', 0)
        st.session_state['presion_vapor_calculada'] = project_data.get('presion_vapor_calculada', 0)
        
        # Datos VFD
        st.session_state['rpm_percentage'] = project_data.get('rpm_percentage', 75.0)
        
        # Si rpm_percentage no está en el nivel raíz, buscarlo en tablas_graficos
        if st.session_state['rpm_percentage'] == 75.0 and 'tablas_graficos' in project_data:
            tablas_graficos = project_data['tablas_graficos']
            if 'tablas_vfd_rpm' in tablas_graficos and 'configuracion' in tablas_graficos['tablas_vfd_rpm']:
                config_vfd = tablas_graficos['tablas_vfd_rpm']['configuracion']
                rpm_from_tablas = config_vfd.get('rpm_percentage', 75.0)
                if rpm_from_tablas != 75.0:  # Solo usar si es diferente del valor por defecto
                    st.session_state['rpm_percentage'] = rpm_from_tablas
        
        st.session_state['curvas_vfd'] = project_data.get('curvas_vfd', {})
        st.session_state['caudal_nominal'] = project_data.get('caudal_nominal', 0)
        st.session_state['paso_caudal_vfd'] = project_data.get('paso_caudal_vfd', 5.0)
        
        # Restaurar configuración de tablas RPM (CRÍTICO PARA INTERFAZ)
        if 'tablas_graficos' in project_data:
            tablas_graficos = project_data['tablas_graficos']
            
            # Restaurar configuración de tablas 100% RPM
            if 'tablas_100_rpm' in tablas_graficos and 'configuracion' in tablas_graficos['tablas_100_rpm']:
                config_100 = tablas_graficos['tablas_100_rpm']['configuracion']
                st.session_state['q_min_100_tab2'] = config_100.get('q_min_100', 0.0)
                st.session_state['q_max_100_tab2'] = config_100.get('q_max_100', st.session_state.get('caudal_lps', 51.0))
                st.session_state['paso_caudal_100_tab2'] = config_100.get('paso_caudal_100', 5.0)
            
            # Restaurar configuración de tablas VFD
            if 'tablas_vfd_rpm' in tablas_graficos and 'configuracion' in tablas_graficos['tablas_vfd_rpm']:
                config_vfd = tablas_graficos['tablas_vfd_rpm']['configuracion']
                st.session_state['q_min_vdf_tab2'] = config_vfd.get('q_min_vdf', 0.0)
                st.session_state['q_max_vdf_tab2'] = config_vfd.get('q_max_vdf', st.session_state.get('caudal_lps', 51.0))
                st.session_state['paso_caudal_vdf_tab2'] = config_vfd.get('paso_caudal_vdf', 5.0)
        
        # Caudales personalizados para ADT
        st.session_state['adt_caudales_personalizados'] = project_data.get('adt_caudales_personalizados', [0, 51.0, 70])
        
        # Información de bomba seleccionada
        bomba_data = project_data.get('bomba_seleccionada', {})
        st.session_state['bomba_url'] = bomba_data.get('url', '')
        st.session_state['bomba_nombre'] = bomba_data.get('nombre', '')
        st.session_state['bomba_descripcion'] = bomba_data.get('descripcion', '')

        # Cargar textareas directas si existen (prioridad sobre curva_inputs)
        for key, value in project_data.items():
            if key.startswith('textarea_'):
                st.session_state[key] = value

        # Cargar textareas desde curva_inputs si no existen como textarea_ directas
        if 'curva_inputs' in project_data:
            curva_inputs = project_data['curva_inputs']
            for curva_key, puntos in curva_inputs.items():
                textarea_key = f"textarea_{curva_key}"
                if textarea_key not in st.session_state and puntos:
                    # Convertir puntos a formato de textarea
                    texto_curva = "\n".join([f"{p[0]} {p[1]}" for p in puntos])
                    st.session_state[textarea_key] = texto_curva

        # Guardar la ruta del archivo cargado para futuros guardados
        st.session_state['current_project_path'] = file_path
        st.info(f"📁 Ruta del proyecto guardada: {file_path}")

        st.success(f"✅ Proyecto cargado exitosamente: {os.path.basename(file_path)}")
        return True
        
    except FileNotFoundError:
        st.error(f"❌ Archivo no encontrado: {file_path}")
        return False
    except json.JSONDecodeError as e:
        st.error(f"❌ Error de formato JSON: {str(e)}")
        return False
    except KeyError as e:
        st.error(f"❌ Campo faltante en JSON: {str(e)}")
        return False
    except Exception as e:
        # DEBUG: Imprime el error real para diagnosticar
        st.error(f"❌ Error al cargar el proyecto: {str(e)} (código: 0 - posible mixed types en DataFrames)")
        st.write(f"🔍 Traceback completo: {e.__traceback__}")
        import traceback
        st.write(f"📋 Detalles del error: {traceback.format_exc()}")
        return False

def load_project_from_upload(uploaded_file) -> bool:
    """
    Carga el estado del proyecto desde un archivo subido.
    
    Args:
        uploaded_file: Archivo subido por el usuario
    
    Returns:
        True si se cargó exitosamente, False en caso contrario
    """
    try:
        # Leer el contenido del archivo
        content = uploaded_file.read().decode('utf-8')
        project_data = json.loads(content)
        
        # Limpiar session_state antes de cargar (igual que en app.py original)
        keys_to_clear = [
            'proyecto', 'diseno', 'proyecto_input_main', 'diseno_input_main',
            'temp_liquido', 'densidad_liquido',
            'caudal_lps', 'caudal_m3h', 'elevacion_sitio', 'altura_succion_input',
            'bomba_inundada', 'altura_descarga', 'num_bombas',
            'long_succion', 'diam_succion_mm', 'mat_succion', 'otras_perdidas_succion', 'accesorios_succion',
            'long_impulsion', 'diam_impulsion_mm', 'mat_impulsion', 'otras_perdidas_impulsion', 'accesorios_impulsion',
            'curva_inputs', 'calibration_points', 'digitalized_points',
            'presion_barometrica_calculada', 'presion_vapor_calculada',
            'rpm_percentage', 'curvas_vfd', 'caudal_nominal', 'paso_caudal_vfd',
            'adt_caudales_personalizados', 'bomba_url', 'bomba_nombre', 'bomba_descripcion',
            # Valores calculados del punto de operación (invalidar para que IA use datos actuales)
            'caudal_operacion', 'altura_operacion', 'interseccion',
            'eficiencia_operacion', 'potencia_operacion', 'npsh_requerido', 'npsh_margen',
            # Datos específicos de materiales para succión
            'diam_externo_succion', 'diam_externo_succion_index', 'serie_succion', 'serie_succion_index',
            'clase_hierro_succion', 'clase_hierro_succion_index', 'dn_succion', 'dn_succion_index',
            'clase_hierro_fundido_succion', 'clase_hierro_fundido_succion_index', 'dn_hierro_fundido_succion', 'dn_hierro_fundido_succion_index',
            'tipo_union_pvc_succion', 'tipo_union_pvc_succion_index', 'serie_pvc_succion_nombre', 'serie_pvc_succion_nombre_index', 'dn_pvc_succion', 'dn_pvc_succion_index',
            # Datos específicos de materiales para impulsión
            'diam_externo_impulsion', 'diam_externo_impulsion_index', 'serie_impulsion', 'serie_impulsion_index',
            'clase_hierro_impulsion', 'clase_hierro_impulsion_index', 'dn_impulsion', 'dn_impulsion_index',
            'clase_hierro_fundido_impulsion', 'clase_hierro_fundido_impulsion_index', 'dn_hierro_fundido_impulsion', 'dn_hierro_fundido_impulsion_index',
            'tipo_union_pvc_impulsion', 'tipo_union_pvc_impulsion_index', 'serie_pvc_impulsion_nombre', 'serie_pvc_impulsion_nombre_index', 'dn_pvc_impulsion', 'dn_pvc_impulsion_index'
        ]
        
        # Limpiar también todos los textarea_
        for key in list(st.session_state.keys()):
            if key.startswith('textarea_'):
                keys_to_clear.append(key)
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Datos del proyecto y diseño
        st.session_state['proyecto'] = project_data.get('proyecto', '')
        st.session_state['diseno'] = project_data.get('diseno', '')
        st.session_state['proyecto_input_main'] = project_data.get('proyecto', '')
        st.session_state['diseno_input_main'] = project_data.get('diseno', '')
        
        # Datos de la barra lateral (solo los que no son widgets)
        st.session_state['temp_liquido'] = project_data.get('temp_liquido', 20.0)
        st.session_state['densidad_liquido'] = project_data.get('densidad_liquido', 1.0)
        
        # 1. Condiciones de Operación
        st.session_state['caudal_lps'] = project_data.get('caudal_lps', 51.0)
        st.session_state['caudal_m3h'] = project_data.get('caudal_m3h', 183.6)
        st.session_state['elevacion_sitio'] = project_data.get('elevacion_sitio', 450.0)
        st.session_state['altura_succion_input'] = project_data.get('altura_succion_input', 1.65)
        st.session_state['bomba_inundada'] = project_data.get('bomba_inundada', False)
        st.session_state['altura_descarga'] = project_data.get('altura_descarga', 80.0)
        st.session_state['num_bombas'] = project_data.get('num_bombas', 1)
        
        # 2. Tubería y Accesorios de Succión
        st.session_state['long_succion'] = project_data.get('long_succion', 10.0)
        st.session_state['diam_succion_mm'] = project_data.get('diam_succion_mm', 200.0)
        st.session_state['mat_succion'] = project_data.get('mat_succion', 'PVC')
        st.session_state['otras_perdidas_succion'] = project_data.get('otras_perdidas_succion', 0.0)
        st.session_state['accesorios_succion'] = fix_mixed_types_in_accessories(project_data.get('accesorios_succion', []))
        
        # Datos específicos de materiales para succión
        # PEAD/HDPE
        st.session_state['diam_externo_succion'] = project_data.get('diam_externo_succion', None)
        st.session_state['diam_externo_succion_index'] = project_data.get('diam_externo_succion_index', 0)
        st.session_state['serie_succion'] = project_data.get('serie_succion', None)
        st.session_state['serie_succion_index'] = project_data.get('serie_succion_index', 0)
        
        # Hierro Dúctil
        st.session_state['clase_hierro_succion'] = project_data.get('clase_hierro_succion', None)
        st.session_state['clase_hierro_succion_index'] = project_data.get('clase_hierro_succion_index', 0)
        st.session_state['dn_succion'] = project_data.get('dn_succion', None)
        st.session_state['dn_succion_index'] = project_data.get('dn_succion_index', 0)
        
        # Hierro Fundido
        st.session_state['clase_hierro_fundido_succion'] = project_data.get('clase_hierro_fundido_succion', None)
        st.session_state['clase_hierro_fundido_succion_index'] = project_data.get('clase_hierro_fundido_succion_index', 0)
        st.session_state['dn_hierro_fundido_succion'] = project_data.get('dn_hierro_fundido_succion', None)
        st.session_state['dn_hierro_fundido_succion_index'] = project_data.get('dn_hierro_fundido_succion_index', 0)
        
        # PVC
        st.session_state['tipo_union_pvc_succion'] = project_data.get('tipo_union_pvc_succion', None)
        st.session_state['tipo_union_pvc_succion_index'] = project_data.get('tipo_union_pvc_succion_index', 0)
        st.session_state['serie_pvc_succion_nombre'] = project_data.get('serie_pvc_succion_nombre', None)
        st.session_state['serie_pvc_succion_nombre_index'] = project_data.get('serie_pvc_succion_nombre_index', 0)
        st.session_state['dn_pvc_succion'] = project_data.get('dn_pvc_succion', None)
        st.session_state['dn_pvc_succion_index'] = project_data.get('dn_pvc_succion_index', 0)
        
        # 3. Tubería y Accesorios de Impulsión
        st.session_state['long_impulsion'] = project_data.get('long_impulsion', 500.0)
        st.session_state['diam_impulsion_mm'] = project_data.get('diam_impulsion_mm', 150.0)
        st.session_state['mat_impulsion'] = project_data.get('mat_impulsion', 'PVC')
        st.session_state['otras_perdidas_impulsion'] = project_data.get('otras_perdidas_impulsion', 0.0)
        st.session_state['accesorios_impulsion'] = fix_mixed_types_in_accessories(project_data.get('accesorios_impulsion', []))
        
        # Datos específicos de materiales para impulsión
        # PEAD/HDPE
        st.session_state['diam_externo_impulsion'] = project_data.get('diam_externo_impulsion', None)
        st.session_state['diam_externo_impulsion_index'] = project_data.get('diam_externo_impulsion_index', 0)
        st.session_state['serie_impulsion'] = project_data.get('serie_impulsion', None)
        st.session_state['serie_impulsion_index'] = project_data.get('serie_impulsion_index', 0)
        
        # Hierro Dúctil
        st.session_state['clase_hierro_impulsion'] = project_data.get('clase_hierro_impulsion', None)
        st.session_state['clase_hierro_impulsion_index'] = project_data.get('clase_hierro_impulsion_index', 0)
        st.session_state['dn_impulsion'] = project_data.get('dn_impulsion', None)
        st.session_state['dn_impulsion_index'] = project_data.get('dn_impulsion_index', 0)
        
        # Hierro Fundido
        st.session_state['clase_hierro_fundido_impulsion'] = project_data.get('clase_hierro_fundido_impulsion', None)
        st.session_state['clase_hierro_fundido_impulsion_index'] = project_data.get('clase_hierro_fundido_impulsion_index', 0)
        st.session_state['dn_hierro_fundido_impulsion'] = project_data.get('dn_hierro_fundido_impulsion', None)
        st.session_state['dn_hierro_fundido_impulsion_index'] = project_data.get('dn_hierro_fundido_impulsion_index', 0)
        
        # PVC
        st.session_state['tipo_union_pvc_impulsion'] = project_data.get('tipo_union_pvc_impulsion', None)
        st.session_state['tipo_union_pvc_impulsion_index'] = project_data.get('tipo_union_pvc_impulsion_index', 0)
        st.session_state['serie_pvc_impulsion_nombre'] = project_data.get('serie_pvc_impulsion_nombre', None)
        st.session_state['serie_pvc_impulsion_nombre_index'] = project_data.get('serie_pvc_impulsion_nombre_index', 0)
        st.session_state['dn_pvc_impulsion'] = project_data.get('dn_pvc_impulsion', None)
        st.session_state['dn_pvc_impulsion_index'] = project_data.get('dn_pvc_impulsion_index', 0)
        
        # 4. Ajuste de Curvas Características (3 puntos)
        st.session_state['curva_inputs'] = project_data.get('curva_inputs', {})
        
        # Datos de calibración y digitalización (si existen)
        st.session_state['calibration_points'] = project_data.get('calibration_points', None)
        st.session_state['digitalized_points'] = project_data.get('digitalized_points', [])
        
        # Campos adicionales que podrían estar faltando
        st.session_state['presion_barometrica_calculada'] = project_data.get('presion_barometrica_calculada', 0)
        st.session_state['presion_vapor_calculada'] = project_data.get('presion_vapor_calculada', 0)
        
        # Datos VFD
        st.session_state['rpm_percentage'] = project_data.get('rpm_percentage', 75.0)
        
        # Si rpm_percentage no está en el nivel raíz, buscarlo en tablas_graficos
        if st.session_state['rpm_percentage'] == 75.0 and 'tablas_graficos' in project_data:
            tablas_graficos = project_data['tablas_graficos']
            if 'tablas_vfd_rpm' in tablas_graficos and 'configuracion' in tablas_graficos['tablas_vfd_rpm']:
                config_vfd = tablas_graficos['tablas_vfd_rpm']['configuracion']
                rpm_from_tablas = config_vfd.get('rpm_percentage', 75.0)
                if rpm_from_tablas != 75.0:  # Solo usar si es diferente del valor por defecto
                    st.session_state['rpm_percentage'] = rpm_from_tablas
        
        st.session_state['curvas_vfd'] = project_data.get('curvas_vfd', {})
        st.session_state['caudal_nominal'] = project_data.get('caudal_nominal', 0)
        st.session_state['paso_caudal_vfd'] = project_data.get('paso_caudal_vfd', 5.0)
        
        # Restaurar configuración de tablas RPM (CRÍTICO PARA INTERFAZ)
        if 'tablas_graficos' in project_data:
            tablas_graficos = project_data['tablas_graficos']
            
            # Restaurar configuración de tablas 100% RPM
            if 'tablas_100_rpm' in tablas_graficos and 'configuracion' in tablas_graficos['tablas_100_rpm']:
                config_100 = tablas_graficos['tablas_100_rpm']['configuracion']
                st.session_state['q_min_100_tab2'] = config_100.get('q_min_100', 0.0)
                st.session_state['q_max_100_tab2'] = config_100.get('q_max_100', st.session_state.get('caudal_lps', 51.0))
                st.session_state['paso_caudal_100_tab2'] = config_100.get('paso_caudal_100', 5.0)
            
            # Restaurar configuración de tablas VFD
            if 'tablas_vfd_rpm' in tablas_graficos and 'configuracion' in tablas_graficos['tablas_vfd_rpm']:
                config_vfd = tablas_graficos['tablas_vfd_rpm']['configuracion']
                st.session_state['q_min_vdf_tab2'] = config_vfd.get('q_min_vdf', 0.0)
                st.session_state['q_max_vdf_tab2'] = config_vfd.get('q_max_vdf', st.session_state.get('caudal_lps', 51.0))
                st.session_state['paso_caudal_vdf_tab2'] = config_vfd.get('paso_caudal_vdf', 5.0)
        
        # Caudales personalizados para ADT
        st.session_state['adt_caudales_personalizados'] = project_data.get('adt_caudales_personalizados', [0, 51.0, 70])
        
        # Información de bomba seleccionada
        bomba_data = project_data.get('bomba_seleccionada', {})
        st.session_state['bomba_url'] = bomba_data.get('url', '')
        st.session_state['bomba_nombre'] = bomba_data.get('nombre', '')
        st.session_state['bomba_descripcion'] = bomba_data.get('descripcion', '')

        # Cargar textareas directas si existen (prioridad sobre curva_inputs)
        for key, value in project_data.items():
            if key.startswith('textarea_'):
                st.session_state[key] = value

        # Cargar textareas desde curva_inputs si no existen como textarea_ directas
        if 'curva_inputs' in project_data:
            curva_inputs = project_data['curva_inputs']
            for curva_key, puntos in curva_inputs.items():
                textarea_key = f"textarea_{curva_key}"
                if textarea_key not in st.session_state and puntos:
                    # Convertir puntos a formato de textarea
                    texto_curva = "\n".join([f"{p[0]} {p[1]}" for p in puntos])
                    st.session_state[textarea_key] = texto_curva

        # Establecer la ruta de guardado para que las futuras operaciones de guardado
        # se realicen en el directorio 'proyectos' con el nombre del archivo original.
        projects_dir = "proyectos"
        if not os.path.exists(projects_dir):
            os.makedirs(projects_dir)
        filepath = os.path.join(projects_dir, uploaded_file.name)
        st.session_state['current_project_path'] = filepath

        st.success(f"✅ Proyecto '{uploaded_file.name}' cargado. Se guardará en '{filepath}'")
        return True
        
    except json.JSONDecodeError as e:
        st.error(f"❌ Error de formato JSON: {str(e)}")
        return False
    except KeyError as e:
        st.error(f"❌ Campo faltante en JSON: {str(e)}")
        return False
    except Exception as e:
        # DEBUG: Imprime el error real para diagnosticar
        st.error(f"❌ Error al cargar el proyecto: {str(e)} (código: 0 - posible mixed types en DataFrames)")
        st.write(f"🔍 Traceback completo: {e.__traceback__}")
        import traceback
        st.write(f"📋 Detalles del error: {traceback.format_exc()}")
        return False

def get_project_list() -> list:
    """
    Obtiene la lista de archivos de proyecto disponibles.
    
    Returns:
        Lista de archivos de proyecto
    """
    try:
        projects_dir = "proyectos"
        if not os.path.exists(projects_dir):
            return []
        
        project_files = []
        for file in os.listdir(projects_dir):
            if file.endswith('.json') and not file.startswith('.'):
                project_files.append(file)
        return sorted(project_files)
    except Exception:
        return []

def delete_project(filename: str) -> bool:
    """
    Elimina un archivo de proyecto.
    
    Args:
        filename: Nombre del archivo a eliminar
    
    Returns:
        True si se eliminó exitosamente, False en caso contrario
    """
    try:
        projects_dir = "proyectos"
        filepath = os.path.join(projects_dir, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            st.success(f"✅ Proyecto eliminado: {filename}")
            return True
        else:
            st.error(f"❌ Archivo no encontrado: {filename}")
            return False
    except Exception as e:
        st.error(f"❌ Error al eliminar el proyecto: {str(e)}")
        return False

def export_project_summary() -> Dict[str, Any]:
    """
    Exporta un resumen del proyecto actual.
    
    Returns:
        Diccionario con el resumen del proyecto
    """
    return {
        'proyecto': st.session_state.get('proyecto', 'Sin nombre'),
        'diseno': st.session_state.get('diseno', 'Sin nombre'),
        'fecha_creacion': st.session_state.get('fecha_creacion', 'No disponible'),
        'parametros_sistema': {
            'caudal_lps': st.session_state.get('caudal_lps', 0),
            'caudal_m3h': st.session_state.get('caudal_m3h', 0),
            'altura_succion': st.session_state.get('altura_succion_input', 0),
            'altura_descarga': st.session_state.get('altura_descarga', 0),
            'elevacion_sitio': st.session_state.get('elevacion_sitio', 0)
        },
        'configuracion_tuberias': {
            'succion': {
                'longitud': st.session_state.get('long_succion', 0),
                'diametro': st.session_state.get('diam_succion_mm', 0),
                'material': st.session_state.get('mat_succion', 'No configurado')
            },
            'impulsion': {
                'longitud': st.session_state.get('long_impulsion', 0),
                'diametro': st.session_state.get('diam_impulsion_mm', 0),
                'material': st.session_state.get('mat_impulsion', 'No configurado')
            }
        },
        'accesorios': {
            'succion': len(st.session_state.get('accesorios_succion', [])),
            'impulsion': len(st.session_state.get('accesorios_impulsion', []))
        },
        'curvas': {
            'bomba': len([k for k in st.session_state.keys() if k.startswith('textarea_bomba') and st.session_state[k]]),
            'rendimiento': len([k for k in st.session_state.keys() if k.startswith('textarea_rendimiento') and st.session_state[k]]),
            'potencia': len([k for k in st.session_state.keys() if k.startswith('textarea_potencia') and st.session_state[k]]),
            'npsh': len([k for k in st.session_state.keys() if k.startswith('textarea_npsh') and st.session_state[k]])
        }
    }

def validate_project_data() -> Dict[str, Any]:
    """
    Valida los datos del proyecto actual de manera completa.
    
    Returns:
        Diccionario con el resultado de la validación
    """
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Validar parámetros básicos del proyecto
    proyecto = st.session_state.get('proyecto', '')
    diseno = st.session_state.get('diseno', '')
    
    if not proyecto.strip():
        validation_result['errors'].append("Nombre del proyecto es requerido")
        validation_result['valid'] = False
    
    if not diseno.strip():
        validation_result['errors'].append("Nombre del diseñador es requerido")
        validation_result['valid'] = False
    
    # Validar parámetros hidráulicos
    caudal_lps = st.session_state.get('caudal_lps', 0)
    caudal_m3h = st.session_state.get('caudal_m3h', 0)
    
    if caudal_lps <= 0 and caudal_m3h <= 0:
        validation_result['errors'].append("Caudal debe ser mayor que 0")
        validation_result['valid'] = False
    
    altura_succion = st.session_state.get('altura_succion_input', 0)
    if altura_succion < 0:
        validation_result['errors'].append("Altura de succión no puede ser negativa")
        validation_result['valid'] = False
    
    altura_descarga = st.session_state.get('altura_descarga', 0)
    if altura_descarga <= 0:
        validation_result['errors'].append("Altura de descarga debe ser mayor que 0")
        validation_result['valid'] = False
    
    # Validar curvas de bomba
    curva_bomba = st.session_state.get('textarea_bomba', '')
    if not curva_bomba.strip():
        validation_result['errors'].append("Se requiere al menos la curva H-Q de la bomba")
        validation_result['valid'] = False
    else:
        # Validar formato de curva de bomba
        try:
            puntos_bomba = parse_curva_texto(curva_bomba)
            if len(puntos_bomba) < 2:
                validation_result['errors'].append("La curva de bomba debe tener al menos 2 puntos")
                validation_result['valid'] = False
        except Exception:
            validation_result['errors'].append("Formato inválido en la curva de bomba")
            validation_result['valid'] = False
    
    # Validar tuberías
    long_succion = st.session_state.get('long_succion', 0)
    diam_succion = st.session_state.get('diam_succion_mm', 0)
    if long_succion <= 0 or diam_succion <= 0:
        validation_result['errors'].append("Longitud y diámetro de succión deben ser mayores que 0")
        validation_result['valid'] = False
    
    long_impulsion = st.session_state.get('long_impulsion', 0)
    diam_impulsion = st.session_state.get('diam_impulsion_mm', 0)
    if long_impulsion <= 0 or diam_impulsion <= 0:
        validation_result['errors'].append("Longitud y diámetro de impulsión deben ser mayores que 0")
        validation_result['valid'] = False
    
    # Advertencias (no críticas)
    if not st.session_state.get('textarea_rendimiento', '').strip():
        validation_result['warnings'].append("No se ha configurado la curva de rendimiento")
    
    if not st.session_state.get('textarea_potencia', '').strip():
        validation_result['warnings'].append("No se ha configurado la curva de potencia")
    
    if not st.session_state.get('textarea_npsh', '').strip():
        validation_result['warnings'].append("No se ha configurado la curva de NPSH")
    
    return validation_result

def generate_vdf_data(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera datos VDF automáticamente basándose en las curvas de entrada.
    
    Args:
        project_data: Datos del proyecto
    
    Returns:
        Diccionario con datos VDF completos
    """
    try:
        # Obtener porcentaje de RPM VDF (por defecto 94.5%)
        rpm_percentage = st.session_state.get('rpm_percentage', 94.5)
        factor_vdf = rpm_percentage / 100.0
        
        # Obtener curvas de entrada
        curva_inputs = project_data.get('curva_inputs', {})
        curvas_texto = {}
        
        # Parsear curvas desde textareas si existen
        for curva_name in ['bomba', 'rendimiento', 'potencia', 'npsh']:
            textarea_key = f'textarea_{curva_name}'
            if textarea_key in st.session_state and st.session_state[textarea_key]:
                curvas_texto[curva_name] = st.session_state[textarea_key]
        
        # Si no hay curvas de texto, usar curva_inputs
        if not curvas_texto and curva_inputs:
            # Convertir curva_inputs a formato texto
            for curva_name in ['bomba', 'rendimiento', 'potencia', 'npsh']:
                if curva_name in curva_inputs:
                    puntos = curva_inputs[curva_name]
                    texto_curva = ""
                    for punto in puntos:
                        texto_curva += f"{punto[0]}\t{punto[1]}\n"
                    curvas_texto[curva_name] = texto_curva
        
        # Generar curvas VDF escaladas
        curvas_vdf = {}
        
        # Obtener puntos de las tablas de 100% RPM si existen
        tablas_graficos = project_data.get('tablas_graficos', {})
        tablas_100_rpm = tablas_graficos.get('100_rpm', {})
        
        # Si hay tablas de 100% RPM, usar sus puntos
        if tablas_100_rpm and 'bomba' in tablas_100_rpm:
            # Extraer caudales de la tabla de bomba (primera curva)
            q_values = []
            for punto in tablas_100_rpm['bomba']:
                q_values.append(punto[0])
        else:
            # Si no hay tablas, generar puntos por defecto
            q_values = [round(0.0 + i * 0.25, 2) for i in range(13)]  # 0.0, 0.25, 0.5, ..., 3.0
        
        for curva_name in ['bomba', 'rendimiento', 'potencia', 'npsh']:
            if curva_name in curvas_texto:
                curva_texto = curvas_texto[curva_name]
                puntos_originales = []
                
                # Parsear puntos originales
                for linea in curva_texto.split('\n'):
                    if linea.strip():
                        partes = linea.strip().split('\t')
                        if len(partes) >= 2:
                            try:
                                q_orig = float(partes[0])
                                valor_orig = float(partes[1])
                                puntos_originales.append([q_orig, valor_orig])
                            except ValueError:
                                continue
                
                # Generar puntos VDF escalados
                puntos_vdf = []
                for q in q_values:
                    # Escalar caudal
                    q_escalado = q * factor_vdf
                    
                    # Interpolar valor basándose en puntos originales
                    valor_escalado = interpolate_curve_value(puntos_originales, q_escalado, curva_name, factor_vdf)
                    puntos_vdf.append([q, valor_escalado])
                
                curvas_vdf[curva_name] = puntos_vdf
        
        # Generar curva del sistema VDF (constante)
        puntos_sistema_vdf = []
        altura_sistema_base = 49.578  # Altura base del sistema
        for q in q_values:
            # La curva del sistema es prácticamente constante
            altura_sistema = altura_sistema_base + (q * 0.05)  # Ligera pendiente
            puntos_sistema_vdf.append([q, altura_sistema])
        
        curvas_vdf['sistema'] = puntos_sistema_vdf
        
        # Crear estructura VDF completa
        vdf_data = {
            'rpm_percentage': rpm_percentage,
            'paso_caudal_vfd': 0.25,
            'curvas_vfd': curvas_vdf,
            'caudal_nominal': 0,
            'caudal_diseno_lps': project_data.get('caudal_diseno_lps', 2.0),
            'caudal_diseno_m3h': project_data.get('caudal_diseno_m3h', 7.2),
            'nota': 'Datos VDF generados automáticamente al guardar el proyecto'
        }
        
        return vdf_data
        
    except Exception as e:
        st.error(f"Error generando datos VDF: {e}")
        # Retornar estructura VDF básica en caso de error
        return {
            'rpm_percentage': 94.5,
            'paso_caudal_vfd': 0.25,
            'curvas_vdf': {},
            'caudal_nominal': 0,
            'caudal_diseno_lps': 2.0,
            'caudal_diseno_m3h': 7.2,
            'nota': 'Error generando datos VDF'
        }

def interpolate_curve_value(puntos_originales: list, q_target: float, curva_name: str, factor_vdf: float) -> float:
    """
    Interpola un valor de curva basándose en puntos originales.
    
    Args:
        puntos_originales: Lista de puntos [q, valor]
        q_target: Caudal objetivo
        curva_name: Nombre de la curva
        factor_vdf: Factor de escala VDF
    
    Returns:
        Valor interpolado
    """
    if not puntos_originales:
        return 0.0
    
    # Ordenar puntos por caudal
    puntos_ordenados = sorted(puntos_originales, key=lambda x: x[0])
    
    # Si q_target está fuera del rango, extrapolar
    if q_target <= puntos_ordenados[0][0]:
        # Extrapolación hacia atrás
        q1, v1 = puntos_ordenados[0]
        q2, v2 = puntos_ordenados[1] if len(puntos_ordenados) > 1 else puntos_ordenados[0]
        pendiente = (v2 - v1) / (q2 - q1) if q2 != q1 else 0
        return v1 + pendiente * (q_target - q1)
    
    if q_target >= puntos_ordenados[-1][0]:
        # Extrapolación hacia adelante
        q1, v1 = puntos_ordenados[-2] if len(puntos_ordenados) > 1 else puntos_ordenados[-1]
        q2, v2 = puntos_ordenados[-1]
        pendiente = (v2 - v1) / (q2 - q1) if q2 != q1 else 0
        return v2 + pendiente * (q_target - q2)
    
    # Interpolación lineal
    for i in range(len(puntos_ordenados) - 1):
        q1, v1 = puntos_ordenados[i]
        q2, v2 = puntos_ordenados[i + 1]
        
        if q1 <= q_target <= q2:
            # Interpolación lineal
            pendiente = (v2 - v1) / (q2 - q1) if q2 != q1 else 0
            valor_base = v1 + pendiente * (q_target - q1)
            
            # Aplicar escalado según el tipo de curva
            if curva_name == 'bomba':
                # H ∝ N²
                return valor_base * (factor_vdf ** 2)
            elif curva_name == 'potencia':
                # P ∝ N³
                return valor_base * (factor_vdf ** 3)
            elif curva_name == 'npsh':
                # NPSH ∝ N²
                return valor_base * (factor_vdf ** 2)
            else:  # rendimiento
                # El rendimiento no se escala
                return valor_base
    
    return 0.0

def generate_100_rpm_tables(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera tablas de 100% RPM automáticamente basándose en las curvas de entrada.
    
    Args:
        project_data: Datos del proyecto
    
    Returns:
        Diccionario con tablas de 100% RPM completas
    """
    try:
        # Obtener curvas de entrada
        curva_inputs = project_data.get('curva_inputs', {})
        curvas_texto = {}
        
        # Parsear curvas desde textareas si existen
        for curva_name in ['bomba', 'rendimiento', 'potencia', 'npsh']:
            textarea_key = f'textarea_{curva_name}'
            if textarea_key in st.session_state and st.session_state[textarea_key]:
                curvas_texto[curva_name] = st.session_state[textarea_key]
        
        # Si no hay curvas de texto, usar curva_inputs
        if not curvas_texto and curva_inputs:
            # Convertir curva_inputs a formato texto
            for curva_name in ['bomba', 'rendimiento', 'potencia', 'npsh']:
                if curva_name in curva_inputs:
                    puntos = curva_inputs[curva_name]
                    texto_curva = ""
                    for punto in puntos:
                        texto_curva += f"{punto[0]}\t{punto[1]}\n"
                    curvas_texto[curva_name] = texto_curva
        
        # Generar tablas de 100% RPM
        tablas_100_rpm = {}
        
        # Generar puntos para las tablas (basándose en las curvas de entrada)
        q_values = []
        if 'bomba' in curvas_texto:
            # Extraer caudales de la curva de bomba
            curva_texto = curvas_texto['bomba']
            for linea in curva_texto.split('\n'):
                if linea.strip():
                    partes = linea.strip().split('\t')
                    if len(partes) >= 2:
                        try:
                            q = float(partes[0])
                            q_values.append(q)
                        except ValueError:
                            continue
        
        # Si no hay caudales de entrada, generar por defecto
        if not q_values:
            q_values = [round(0.0 + i * 0.25, 2) for i in range(17)]  # 0.0, 0.25, 0.5, ..., 4.0
        
        # Ordenar caudales
        q_values = sorted(list(set(q_values)))
        
        for curva_name in ['bomba', 'rendimiento', 'potencia', 'npsh']:
            if curva_name in curvas_texto:
                curva_texto = curvas_texto[curva_name]
                puntos_originales = []
                
                # Parsear puntos originales
                for linea in curva_texto.split('\n'):
                    if linea.strip():
                        partes = linea.strip().split('\t')
                        if len(partes) >= 2:
                            try:
                                q_orig = float(partes[0])
                                valor_orig = float(partes[1])
                                puntos_originales.append([q_orig, valor_orig])
                            except ValueError:
                                continue
                
                # Generar puntos interpolados para cada caudal
                puntos_tabla = []
                for q in q_values:
                    valor_interpolado = interpolate_curve_value(puntos_originales, q, curva_name, 1.0)  # Factor 1.0 para 100% RPM
                    puntos_tabla.append([q, valor_interpolado])
                
                tablas_100_rpm[curva_name] = puntos_tabla
        
        # Generar curva del sistema (basándose en datos del proyecto)
        puntos_sistema = []
        altura_sistema_base = 49.578  # Altura base del sistema
        for q in q_values:
            # La curva del sistema tiene una pendiente ligera
            altura_sistema = altura_sistema_base + (q * 0.05)
            puntos_sistema.append([q, altura_sistema])
        
        tablas_100_rpm['sistema'] = puntos_sistema
        
        # Crear estructura de tablas completa
        tablas_graficos = {
            '100_rpm': tablas_100_rpm,
            'nota': 'Tablas de 100% RPM generadas automáticamente al guardar el proyecto'
        }
        
        return tablas_graficos
        
    except Exception as e:
        st.error(f"Error generando tablas de 100% RPM: {e}")
        # Retornar estructura básica en caso de error
        return {
            '100_rpm': {},
            'nota': 'Error generando tablas de 100% RPM'
        }

def collect_all_inputs_from_session_state() -> Dict[str, Any]:
    """
    Recopila todos los inputs del session_state de manera completa.
    
    Returns:
        Diccionario con todos los inputs del proyecto
    """
    project_data = {}
    
    # Datos básicos del proyecto
    project_data['proyecto'] = st.session_state.get('proyecto', '')
    project_data['diseno'] = st.session_state.get('diseno', '')
    project_data['proyecto_input_main'] = st.session_state.get('proyecto_input_main', '')
    project_data['diseno_input_main'] = st.session_state.get('diseno_input_main', '')
    
    # Parámetros de diseño
    project_data['ajuste_tipo'] = st.session_state.get('ajuste_tipo', 'Cuadrática (2do grado)')
    project_data['curva_mode'] = st.session_state.get('curva_mode', '3 puntos')
    project_data['flow_unit'] = st.session_state.get('flow_unit', 'L/s')
    project_data['caudal_diseno_lps'] = st.session_state.get('caudal_lps', 0)
    project_data['caudal_diseno_m3h'] = st.session_state.get('caudal_m3h', 0)
    project_data['elevacion_sitio'] = st.session_state.get('elevacion_sitio', 0)
    project_data['altura_succion'] = st.session_state.get('altura_succion_input', 0)
    project_data['altura_descarga'] = st.session_state.get('altura_descarga', 0)
    project_data['num_bombas_paralelo'] = st.session_state.get('num_bombas', 1)
    project_data['bomba_inundada'] = st.session_state.get('bomba_inundada', False)
    project_data['temperatura'] = st.session_state.get('temp_liquido', 20.0)
    project_data['densidad_liquido'] = st.session_state.get('densidad_liquido', 1.0)
    
    # Método de cálculo de pérdidas
    project_data['metodo_calculo'] = st.session_state.get('metodo_calculo', 'Hazen-Williams')
    
    # Si es Darcy-Weisbach, incluir parámetros detallados
    if project_data['metodo_calculo'] == 'Darcy-Weisbach':
        project_data['detalles_darcy_succion'] = st.session_state.get('detalles_calc_succion_primaria', {})
        project_data['detalles_darcy_impulsion'] = st.session_state.get('detalles_calc_impulsion_primaria', {})
    
    # Presiones calculadas
    project_data['presion_vapor_calculada'] = st.session_state.get('presion_vapor_calculada', 0)
    project_data['presion_barometrica_calculada'] = st.session_state.get('presion_barometrica_calculada', 0)
    
    # Datos de tuberías
    project_data['long_succion'] = st.session_state.get('long_succion', 0)
    project_data['diam_succion_mm'] = st.session_state.get('diam_succion_mm', 0)
    project_data['mat_succion'] = st.session_state.get('mat_succion', 'PVC')
    project_data['otras_perdidas_succion'] = st.session_state.get('otras_perdidas_succion', 0)
    project_data['accesorios_succion'] = st.session_state.get('accesorios_succion', [])
    
    project_data['long_impulsion'] = st.session_state.get('long_impulsion', 0)
    project_data['diam_impulsion_mm'] = st.session_state.get('diam_impulsion_mm', 0)
    project_data['mat_impulsion'] = st.session_state.get('mat_impulsion', 'PVC')
    project_data['otras_perdidas_impulsion'] = st.session_state.get('otras_perdidas_impulsion', 0)
    project_data['accesorios_impulsion'] = st.session_state.get('accesorios_impulsion', [])
    
    # Curvas de entrada
    project_data['curva_inputs'] = st.session_state.get('curva_inputs', {})
    project_data['calibration_points'] = st.session_state.get('calibration_points', None)
    project_data['digitalized_points'] = st.session_state.get('digitalized_points', [])
    
    # Datos VFD
    project_data['rpm_percentage'] = st.session_state.get('rpm_percentage', 75.0)
    project_data['curvas_vfd'] = st.session_state.get('curvas_vfd', {})
    project_data['caudal_nominal'] = st.session_state.get('caudal_nominal', 0)
    project_data['paso_caudal_vfd'] = st.session_state.get('paso_caudal_vfd', 5.0)
    
    # Caudales personalizados
    project_data['adt_caudales_personalizados'] = st.session_state.get('adt_caudales_personalizados', [])
    
    # Índices específicos de materiales y diámetros para persistencia (Fix Task 1)
    claves_materiales = [
        'diam_externo_succion_index', 'serie_succion_index', 'clase_hierro_succion_index', 'dn_succion_index',
        'clase_hierro_fundido_succion_index', 'dn_hierro_fundido_succion_index', 'tipo_union_pvc_succion_index',
        'serie_pvc_succion_nombre_index', 'dn_pvc_succion_index',
        'diam_externo_impulsion_index', 'serie_impulsion_index', 'clase_hierro_impulsion_index', 'dn_impulsion_index',
        'clase_hierro_fundido_impulsion_index', 'dn_hierro_fundido_impulsion_index', 'tipo_union_pvc_impulsion_index',
        'serie_pvc_impulsion_nombre_index', 'dn_pvc_impulsion_index',
        'diam_externo_succion', 'serie_succion', 'clase_hierro_succion', 'dn_succion',
        'clase_hierro_fundido_succion', 'dn_hierro_fundido_succion', 'tipo_union_pvc_succion',
        'serie_pvc_succion_nombre', 'dn_pvc_succion',
        'diam_externo_impulsion', 'serie_impulsion', 'clase_hierro_impulsion', 'dn_impulsion',
        'clase_hierro_fundido_impulsion', 'dn_hierro_fundido_impulsion', 'tipo_union_pvc_impulsion',
        'serie_pvc_impulsion_nombre', 'dn_pvc_impulsion'
    ]
    for clave in claves_materiales:
        if clave in st.session_state:
            project_data[clave] = st.session_state[clave]
    
    # Información de bomba
    project_data['bomba_url'] = st.session_state.get('bomba_url', '')
    project_data['bomba_nombre'] = st.session_state.get('bomba_nombre', '')
    project_data['bomba_descripcion'] = st.session_state.get('bomba_descripcion', '')
    
    # Datos de materiales y sus selectores
    claves_materiales = [
        'caudal_lps', 'caudal_m3h', 'altura_succion_input', 'altura_descarga', 'num_bombas', 'bomba_inundada',
        'diam_externo_succion', 'diam_externo_succion_index', 'serie_succion', 'serie_succion_index',
        'clase_hierro_succion', 'clase_hierro_succion_index', 'dn_succion', 'dn_succion_index',
        'clase_hierro_fundido_succion', 'clase_hierro_fundido_succion_index', 'dn_hierro_fundido_succion', 'dn_hierro_fundido_succion_index',
        'tipo_union_pvc_succion', 'tipo_union_pvc_succion_index', 'serie_pvc_succion_nombre', 'serie_pvc_succion_nombre_index', 'dn_pvc_succion', 'dn_pvc_succion_index',
        'diam_externo_impulsion', 'diam_externo_impulsion_index', 'serie_impulsion', 'serie_impulsion_index',
        'clase_hierro_impulsion', 'clase_hierro_impulsion_index', 'dn_impulsion', 'dn_impulsion_index',
        'clase_hierro_fundido_impulsion', 'clase_hierro_fundido_impulsion_index', 'dn_hierro_fundido_impulsion', 'dn_hierro_fundido_impulsion_index',
        'tipo_union_pvc_impulsion', 'tipo_union_pvc_impulsion_index', 'serie_pvc_impulsion_nombre', 'serie_pvc_impulsion_nombre_index', 'dn_pvc_impulsion', 'dn_pvc_impulsion_index'
    ]
    for clave in claves_materiales:
        if clave in st.session_state:
            project_data[clave] = st.session_state[clave]
    
    # Agregar todos los textareas
    for key in st.session_state:
        if key.startswith('textarea_'):
            project_data[key] = st.session_state[key]
    
    # Agregar campos adicionales que puedan existir
    campos_adicionales = [
        'init_done', 'del_i_chk_8', 'le_total_succion', 'last_uploaded_file_id',
        'panel_cant_accesorios_succion', 'save_valvulas', 'del_i_chk_2', 'save_hazen',
        'download_pvc_union_espiga_campana_s16', 'reload_pvc_union_espiga_campana_s8'
    ]
    
    for campo in campos_adicionales:
        if campo in st.session_state:
            project_data[campo] = st.session_state[campo]
    
    return project_data

def generate_100_rpm_tables_validated(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera tablas de 100% RPM con validación mejorada.
    
    Args:
        project_data: Datos del proyecto
    
    Returns:
        Diccionario con tablas de 100% RPM o None si hay error
    """
    try:
        # Obtener curvas de entrada
        curvas_texto = {}
        curva_inputs = project_data.get('curva_inputs', {})
        
        # Parsear curvas desde textareas si existen
        for curva_name in ['bomba', 'rendimiento', 'potencia', 'npsh']:
            textarea_key = f'textarea_{curva_name}'
            if textarea_key in project_data and project_data[textarea_key]:
                curvas_texto[curva_name] = project_data[textarea_key]
        
        # Si no hay curvas de texto, usar curva_inputs
        if not curvas_texto and curva_inputs:
            for curva_name in ['bomba', 'rendimiento', 'potencia', 'npsh']:
                if curva_name in curva_inputs:
                    puntos = curva_inputs[curva_name]
                    texto_curva = ""
                    for punto in puntos:
                        texto_curva += f"{punto[0]}\t{punto[1]}\n"
                    curvas_texto[curva_name] = texto_curva
        
        if not curvas_texto:
            st.warning("⚠️ No se encontraron curvas para generar tablas de 100% RPM")
            return None
        
        # Generar puntos para las tablas
        q_values = []
        if 'bomba' in curvas_texto:
            puntos_bomba = parse_curva_texto(curvas_texto['bomba'])
            q_values = [punto[0] for punto in puntos_bomba]
        
        # Si no hay caudales de entrada, generar por defecto
        if not q_values:
            caudal_max = project_data.get('caudal_diseno_lps', 2.0)
            q_values = [round(i * 0.25, 2) for i in range(int(caudal_max * 4) + 1)]
        
        # Ordenar caudales
        q_values = sorted(list(set(q_values)))
        
        # Generar tablas para cada curva
        tablas_100_rpm = {}
        for curva_name in ['bomba', 'rendimiento', 'potencia', 'npsh']:
            if curva_name in curvas_texto:
                puntos_originales = parse_curva_texto(curvas_texto[curva_name])
                puntos_tabla = []
                
                for q in q_values:
                    valor_interpolado = interpolate_curve_value(puntos_originales, q, curva_name, 1.0)
                    puntos_tabla.append([q, valor_interpolado])
                
                tablas_100_rpm[curva_name] = puntos_tabla
        
        # Generar curva del sistema
        puntos_sistema = []
        altura_sistema_base = project_data.get('altura_descarga', 0) + project_data.get('altura_succion', 0)
        for q in q_values:
            altura_sistema = altura_sistema_base + (q * 0.05)  # Pendiente ligera
            puntos_sistema.append([q, altura_sistema])
        
        tablas_100_rpm['sistema'] = puntos_sistema
        
        # Agregar configuración
        tablas_100_rpm['configuracion'] = {
            'q_min_100': min(q_values) if q_values else 0.0,
            'q_max_100': max(q_values) if q_values else project_data.get('caudal_diseno_lps', 2.0),
            'paso_caudal_100': 0.25,
            'num_puntos': len(q_values)
        }
        
        tablas_100_rpm['nota'] = 'Tablas de 100% RPM generadas correctamente'
        
        return tablas_100_rpm
        
    except Exception as e:
        st.error(f"Error generando tablas de 100% RPM: {e}")
        return None

def generate_vdf_data_validated(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera datos VDF con validación mejorada.
    
    Args:
        project_data: Datos del proyecto
    
    Returns:
        Diccionario con datos VDF o None si hay error
    """
    try:
        # Obtener porcentaje de RPM VDF
        rpm_percentage = project_data.get('rpm_percentage', 75.0)
        factor_vdf = rpm_percentage / 100.0
        
        # Obtener curvas de entrada
        curvas_texto = {}
        curva_inputs = project_data.get('curva_inputs', {})
        
        # Parsear curvas desde textareas si existen
        for curva_name in ['bomba', 'rendimiento', 'potencia', 'npsh']:
            textarea_key = f'textarea_{curva_name}'
            if textarea_key in project_data and project_data[textarea_key]:
                curvas_texto[curva_name] = project_data[textarea_key]
        
        # Si no hay curvas de texto, usar curva_inputs
        if not curvas_texto and curva_inputs:
            for curva_name in ['bomba', 'rendimiento', 'potencia', 'npsh']:
                if curva_name in curva_inputs:
                    puntos = curva_inputs[curva_name]
                    texto_curva = ""
                    for punto in puntos:
                        texto_curva += f"{punto[0]}\t{punto[1]}\n"
                    curvas_texto[curva_name] = texto_curva
        
        if not curvas_texto:
            st.warning("⚠️ No se encontraron curvas para generar datos VDF")
            return None
        
        # Generar puntos para las curvas VDF
        q_values = []
        if 'bomba' in curvas_texto:
            puntos_bomba = parse_curva_texto(curvas_texto['bomba'])
            q_values = [punto[0] for punto in puntos_bomba]
        
        # Si no hay caudales de entrada, generar por defecto
        if not q_values:
            caudal_max = project_data.get('caudal_diseno_lps', 2.0)
            q_values = [round(i * 0.25, 2) for i in range(int(caudal_max * 4) + 1)]
        
        # Ordenar caudales
        q_values = sorted(list(set(q_values)))
        
        # Generar curvas VDF escaladas
        curvas_vdf = {}
        for curva_name in ['bomba', 'rendimiento', 'potencia', 'npsh']:
            if curva_name in curvas_texto:
                puntos_originales = parse_curva_texto(curvas_texto[curva_name])
                puntos_vdf = []
                
                for q in q_values:
                    # Escalar caudal
                    q_escalado = q * factor_vdf
                    
                    # Interpolar valor basándose en puntos originales
                    valor_escalado = interpolate_curve_value(puntos_originales, q_escalado, curva_name, factor_vdf)
                    puntos_vdf.append([q, valor_escalado])
                
                curvas_vdf[curva_name] = puntos_vdf
        
        # Generar curva del sistema VDF (constante)
        puntos_sistema_vdf = []
        altura_sistema_base = project_data.get('altura_descarga', 0) + project_data.get('altura_succion', 0)
        for q in q_values:
            altura_sistema = altura_sistema_base + (q * 0.05)
            puntos_sistema_vdf.append([q, altura_sistema])
        
        curvas_vdf['sistema'] = puntos_sistema_vdf
        
        # Crear estructura VDF completa
        vdf_data = {
            'rpm_percentage': rpm_percentage,
            'paso_caudal_vfd': 0.25,
            'curvas_vfd': curvas_vdf,
            'caudal_nominal': project_data.get('caudal_nominal', 0),
            'caudal_diseno_lps': project_data.get('caudal_diseno_lps', 2.0),
            'caudal_diseno_m3h': project_data.get('caudal_diseno_m3h', 7.2),
            'nota': f'Datos VDF generados automáticamente al {rpm_percentage}% RPM'
        }
        
        return vdf_data
        
    except Exception as e:
        st.error(f"Error generando datos VDF: {e}")
        return None

def generate_curvas_puntos_from_texto(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera curvas_puntos desde curvas_texto.
    
    Args:
        project_data: Datos del proyecto
    
    Returns:
        Diccionario con curvas_puntos
    """
    curvas_puntos = {
        'sistema': [],
        'bomba': [],
        'rendimiento': [],
        'potencia': [],
        'npsh': []
    }
    
    for curva_name in ['sistema', 'bomba', 'rendimiento', 'potencia', 'npsh']:
        textarea_key = f'textarea_{curva_name}'
        if textarea_key in project_data and project_data[textarea_key]:
            try:
                curvas_puntos[curva_name] = parse_curva_texto(project_data[textarea_key])
            except Exception:
                curvas_puntos[curva_name] = []
    
    return curvas_puntos

def generate_bomba_seleccionada_data() -> Dict[str, Any]:
    """
    Genera datos de bomba seleccionada desde session_state.
    
    Returns:
        Diccionario con datos de bomba seleccionada
    """
    return {
        'url': st.session_state.get('bomba_url', ''),
        'nombre': st.session_state.get('bomba_nombre', ''),
        'descripcion': st.session_state.get('bomba_descripcion', ''),
        'id': st.session_state.get('bomba_id', ''),
        'fabricante': st.session_state.get('bomba_fabricante', ''),
        'modelo': st.session_state.get('bomba_modelo', '')
    }

def serialize_project_data(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serializa objetos no serializables a formato JSON.
    
    Args:
        project_data: Datos del proyecto
    
    Returns:
        Diccionario serializable
    """
    import copy
    
    def convert_to_serializable(obj):
        """Convierte objetos no serializables a tipos básicos"""
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, 'tolist'):
            return obj.tolist()
        elif hasattr(obj, '__dict__'):
            return {k: convert_to_serializable(v) for k, v in obj.__dict__.items()}
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_to_serializable(item) for item in obj]
        else:
            return obj
    
    return convert_to_serializable(project_data)

def validate_complete_project(project_data: Dict[str, Any]) -> bool:
    """
    Valida que el proyecto esté completo antes de guardar.
    
    Args:
        project_data: Datos del proyecto
    
    Returns:
        True si el proyecto está completo, False en caso contrario
    """
    campos_criticos = [
        'proyecto', 'diseno', 'caudal_diseno_lps', 'caudal_diseno_m3h',
        'elevacion_sitio', 'altura_succion', 'altura_descarga'
    ]
    
    for campo in campos_criticos:
        if campo not in project_data or not project_data[campo]:
            st.error(f"❌ Campo crítico faltante: {campo}")
            return False
    
    # Validar que existan curvas de bomba
    if not project_data.get('textarea_bomba', '').strip():
        st.error("❌ Curva de bomba es requerida")
        return False
    
    # Validar que las tablas estén presentes
    if 'tablas_graficos' not in project_data:
        st.warning("⚠️ Tablas de gráficos no están presentes")
        return False
    
    return True

def determine_filepath(filename: Optional[str] = None) -> str:
    """
    Determina la ruta del archivo para guardar.
    
    Args:
        filename: Nombre del archivo (opcional)
    
    Returns:
        Ruta completa del archivo
    """
    if not filename:
        # Si hay un archivo cargado, usar su ruta
        if 'current_project_path' in st.session_state and st.session_state['current_project_path']:
            filepath = st.session_state['current_project_path']
            st.info(f"💾 Guardando en archivo cargado: {filepath}")
        else:
            # Si no hay archivo cargado, crear uno nuevo usando el nombre del proyecto
            proyecto = st.session_state.get('proyecto', 'Proyecto')
            # Limpiar el nombre del proyecto para usarlo como nombre de archivo
            proyecto_clean = proyecto.strip().replace(' ', '_').replace('/', '_').replace('\\', '_')
            if not proyecto_clean:
                proyecto_clean = 'Proyecto'
            filename = f"{proyecto_clean}.json"
            projects_dir = "proyectos"
            if not os.path.exists(projects_dir):
                os.makedirs(projects_dir)
            filepath = os.path.join(projects_dir, filename)
            st.info(f"💾 Creando nuevo archivo: {filepath}")
    else:
        # Si se especifica un filename, usar la carpeta proyectos
        # Asegurarse de que el filename tenga extensión .json
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        projects_dir = "proyectos"
        if not os.path.exists(projects_dir):
            os.makedirs(projects_dir)
        filepath = os.path.join(projects_dir, filename)
        st.info(f"💾 Guardando con nombre específico: {filepath}")
    
    return filepath

def parse_curva_texto(texto_curva: str) -> list:
    """
    Parsea texto de curva a lista de puntos.
    
    Args:
        texto_curva: Texto de la curva
    
    Returns:
        Lista de puntos [q, valor]
    """
    puntos = []
    for linea in texto_curva.split('\n'):
        if linea.strip():
            # Manejar tanto tab como espacio como separador
            partes = linea.strip().replace('\t', ' ').split()
            if len(partes) >= 2:
                try:
                    q = float(partes[0])
                    valor = float(partes[1])
                    puntos.append([q, valor])
                except ValueError:
                    continue
    return puntos
