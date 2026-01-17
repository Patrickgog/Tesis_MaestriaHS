# Pestañas principales de la aplicación

import streamlit as st
import pandas as pd
import numpy as np
import json
import io
import math
import os
import plotly.graph_objects as go
from scipy.optimize import fsolve
from typing import Dict, Any
from ui.ai_module import render_ai_question_response
from ui.transient_tab import render_transient_tab as render_transient_simulation_tab
from ui.transients import render_transient_tab
from ui.html_generator import generate_html_report
from ui.tabs_modules.common import fix_mixed_types_in_dataframe
from ui.tabs_modules.tables_pump_editor import render_bombas_comerciales_editor


def render_tables_tab():
    """Renderiza la pestaña de tablas editables"""
    st.header("📊 Tablas de Configuración")
    st.markdown("""
    Esta sección permite editar las tablas de datos utilizadas en la aplicación.
    Los cambios se guardan automáticamente en los archivos JSON correspondientes.
    """)
    
    # Crear sub-pestañas para cada tipo de tabla
    sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5, sub_tab6, sub_tab7 = st.tabs([
        "Hazen-Williams", "Accesorios", "Tuberías", "Motores Estándar", "Celeridad",
        "Bombas Grundfos", "Bombas Ebara"
    ])
    
    with sub_tab1:
        render_hazen_williams_editor()
    
    with sub_tab2:
        render_accessories_editor()
    
    with sub_tab3:
        render_tuberias_editor()
    
    with sub_tab4:
        render_motores_editor()
    
    with sub_tab5:
        render_celeridad_editor()
    
    with sub_tab6:
        render_bombas_comerciales_editor("Grundfos")
    
    with sub_tab7:
        render_bombas_comerciales_editor("Ebara")

def render_hazen_williams_editor():
    """Editor para tabla de coeficientes Hazen-Williams"""
    st.subheader("Coeficientes C de Hazen-Williams")
    st.markdown("Edita los coeficientes C para diferentes materiales de tubería.")
    
    # Cargar datos
    try:
        with open("data_tablas/hazen_williams_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        materiales = data.get("materiales", [])
    except FileNotFoundError:
        st.error("Archivo hazen_williams_data.json no encontrado")
        return
    except Exception as e:
        st.error(f"Error cargando archivo: {e}")
        return
    
    if materiales:
        # Convertir a DataFrame
        df = pd.DataFrame(materiales)
        
        # Mostrar tabla editable
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "material": st.column_config.TextColumn("Material", required=True),
                "coeficiente_c": st.column_config.NumberColumn("Coeficiente C", min_value=50, max_value=200, required=True),
                "descripcion": st.column_config.TextColumn("Descripción"),
                "aplicacion": st.column_config.TextColumn("Aplicación"),
                "rango_diametros": st.column_config.TextColumn("Rango Diámetros"),
                "presion_maxima": st.column_config.TextColumn("Presión Máxima"),
                "temperatura_maxima": st.column_config.TextColumn("Temp. Máxima")
            }
        )
        
        # Botones de acción
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Guardar Cambios", key="save_hazen"):
                try:
                    # Crear respaldo
                    import shutil
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    shutil.copy("data_tablas/hazen_williams_data.json", f"data_tablas/backups/hazen_williams_backup_{timestamp}.json")
                    
                    # Actualizar datos
                    data["materiales"] = edited_df.to_dict("records")
                    
                    # Guardar archivo
                    with open("data_tablas/hazen_williams_data.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    st.success("✅ Cambios guardados exitosamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error guardando: {e}")
        
        with col2:
            if st.button("🔄 Recargar", key="reload_hazen"):
                st.rerun()
        
        with col3:
            # Descargar JSON
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            st.download_button(
                "📥 Descargar JSON",
                json_str,
                file_name="hazen_williams_data.json",
                mime="application/json"
            )
    else:
        st.warning("No hay datos disponibles")

def render_accessories_editor():
    """Editor para tabla de accesorios"""
    st.subheader("Accesorios de Tubería")
    st.markdown("Edita los datos de accesorios, válvulas y medidores.")
    
    # Cargar datos
    try:
        with open("data_tablas/accesorios_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        st.error("Archivo accesorios_data.json no encontrado")
        return
    except Exception as e:
        st.error(f"Error cargando archivo: {e}")
        return
    
    # Crear sub-pestañas para cada tipo de accesorio
    acc_tab1, acc_tab2, acc_tab3 = st.tabs(["Válvulas", "Accesorios", "Medidores"])
    
    with acc_tab1:
        st.markdown("### Válvulas")
        if "valvulas" in data and data["valvulas"]:
            df_valvulas = pd.DataFrame(data["valvulas"])
            edited_df = st.data_editor(
                df_valvulas,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "singularidad": st.column_config.TextColumn("Singularidad", required=True),
                    "tipo": st.column_config.TextColumn("Tipo", required=True),
                    "k": st.column_config.NumberColumn("k", min_value=0.0, max_value=1000.0, required=True),
                    "lc_d": st.column_config.NumberColumn("Lc/D", min_value=0.0, max_value=10000.0),
                    "lc_d_medio": st.column_config.NumberColumn("Lc/D Medio", min_value=0.0, max_value=10000.0),
                    "descripcion": st.column_config.TextColumn("Descripción")
                }
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Guardar Válvulas", key="save_valvulas"):
                    try:
                        data["valvulas"] = edited_df.to_dict("records")
                        with open("data_tablas/accesorios_data.json", "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        st.success("✅ Válvulas guardadas")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            with col2:
                if st.button("🔄 Recargar", key="reload_valvulas"):
                    st.rerun()
            with col3:
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                st.download_button("📥 Descargar", json_str, "accesorios_data.json", "application/json", key="download_valvulas")
        else:
            st.warning("No hay datos de válvulas")
    
    with acc_tab2:
        st.markdown("### Accesorios")
        if "accesorios" in data and data["accesorios"]:
            df_accesorios = pd.DataFrame(data["accesorios"])
            df_accesorios = fix_mixed_types_in_dataframe(df_accesorios)
            
            edited_df = st.data_editor(
                df_accesorios,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "singularidad": st.column_config.TextColumn("Singularidad", required=True),
                    "tipo": st.column_config.TextColumn("Tipo", required=True),
                    "k": st.column_config.TextColumn("k", required=True),
                    "lc_d": st.column_config.NumberColumn("Lc/D", min_value=0.0, max_value=10000.0),
                    "lc_d_medio": st.column_config.NumberColumn("Lc/D Medio", min_value=0.0, max_value=10000.0),
                    "descripcion": st.column_config.TextColumn("Descripción")
                }
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Guardar Accesorios", key="save_accesorios"):
                    try:
                        data["accesorios"] = edited_df.to_dict("records")
                        with open("data_tablas/accesorios_data.json", "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        st.success("✅ Accesorios guardados")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            with col2:
                if st.button("🔄 Recargar", key="reload_accesorios"):
                    st.rerun()
            with col3:
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                st.download_button("📥 Descargar", json_str, "accesorios_data.json", "application/json", key="download_accesorios")
        else:
            st.warning("No hay datos de accesorios")
    
    with acc_tab3:
        st.markdown("### Medidores")
        if "medidores" in data and data["medidores"]:
            df_medidores = pd.DataFrame(data["medidores"])
            edited_df = st.data_editor(
                df_medidores,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "singularidad": st.column_config.TextColumn("Singularidad", required=True),
                    "tipo": st.column_config.TextColumn("Tipo", required=True),
                    "k": st.column_config.NumberColumn("k", min_value=0.0, max_value=1000.0, required=True),
                    "lc_d": st.column_config.NumberColumn("Lc/D", min_value=0.0, max_value=10000.0),
                    "lc_d_medio": st.column_config.NumberColumn("Lc/D Medio", min_value=0.0, max_value=10000.0),
                    "descripcion": st.column_config.TextColumn("Descripción")
                }
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Guardar Medidores", key="save_medidores"):
                    try:
                        data["medidores"] = edited_df.to_dict("records")
                        with open("data_tablas/accesorios_data.json", "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        st.success("✅ Medidores guardados")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            with col2:
                if st.button("🔄 Recargar", key="reload_medidores"):
                    st.rerun()
            with col3:
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                st.download_button("📥 Descargar", json_str, "accesorios_data.json", "application/json", key="download_medidores")
        else:
            st.warning("No hay datos de medidores")

def render_tuberias_editor():
    """Editor para tabla de tuberías con sub-pestañas"""
    st.subheader("Datos de Tuberías")
    st.markdown("Edita los datos técnicos de diferentes tipos de tubería.")
    st.info("💡 **Nota:** Las columnas marcadas con 💰 indican los **Costos por Metro Lineal** que se usarán en la optimización.")
    
    # Crear sub-pestañas para tuberías
    tuberia_sub_tab1, tuberia_sub_tab2, tuberia_sub_tab3, tuberia_sub_tab4, tuberia_sub_tab5 = st.tabs([
        "Otros Materiales", "PEAD", "Hierro Dúctil", "Hierro Fundido", "PVC"
    ])
    
    with tuberia_sub_tab1:
        render_tuberias_otros_materiales()
    
    with tuberia_sub_tab2:
        render_pead_editor()
    
    with tuberia_sub_tab3:
        render_hierro_ductil_editor()
    
    with tuberia_sub_tab4:
        render_hierro_fundido_editor()
    
    with tuberia_sub_tab5:
        render_pvc_editor()

def render_tuberias_otros_materiales():
    """Editor para tabla de tuberías (otros materiales)"""
    st.subheader("Datos de Tuberías - Otros Materiales")
    st.markdown("Edita los datos técnicos de diferentes tipos de tubería (PVC, Acero, Hierro Fundido, etc.).")
    
    # Cargar datos
    try:
        with open("data_tablas/tuberias_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        tuberias = data.get("tuberias", [])
    except FileNotFoundError:
        st.error("Archivo tuberias_data.json no encontrado")
        return
    except Exception as e:
        st.error(f"Error cargando archivo: {e}")
        return
    
    if tuberias:
        # Convertir a DataFrame
        df = pd.DataFrame(tuberias)
        
        # Mostrar tabla editable
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "material": st.column_config.TextColumn("Material", required=True),
                "tipo": st.column_config.TextColumn("Tipo", required=True),
                "diametros_disponibles": st.column_config.TextColumn("Diámetros Disponibles"),
                "propiedades": st.column_config.TextColumn("Propiedades"),
                "aplicaciones": st.column_config.TextColumn("Aplicaciones"),
                "ventajas": st.column_config.TextColumn("Ventajas"),
                "desventajas": st.column_config.TextColumn("Desventajas")
            }
        )
        
        # Botones de acción
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Guardar Cambios", key="save_tuberias"):
                try:
                    # Crear respaldo
                    import shutil
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    shutil.copy("data_tablas/tuberias_data.json", f"data_tablas/backups/tuberias_backup_{timestamp}.json")
                    
                    # Actualizar datos
                    data["tuberias"] = edited_df.to_dict("records")
                    
                    # Guardar archivo
                    with open("data_tablas/tuberias_data.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    st.success("✅ Cambios guardados exitosamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error guardando: {e}")
        
        with col2:
            if st.button("🔄 Recargar", key="reload_tuberias"):
                st.rerun()
        
        with col3:
            # Descargar JSON
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            st.download_button(
                "📥 Descargar JSON",
                json_str,
                file_name="tuberias_data.json",
                mime="application/json"
            )
    else:
        st.warning("No hay datos disponibles")

def render_pead_editor():
    """Editor para tabla de tuberías PEAD"""
    st.subheader("Tabla 1 - Tuberías PEAD")
    st.markdown("""
    **Especificaciones para tuberías PEAD (Polietileno de Alta Densidad)**
    
    Esta tabla permite determinar el espesor nominal de pared basado en:
    - Diámetro nominal externo
    - Serie del tubo (S12.5, S10, S8, S6.3, S5, S4)
    - Presión nominal de trabajo
    
    **Notas importantes:**
    - Las tuberías de 20 mm a 110 mm se despachan en rollos de 50 o 100 metros
    - Las tuberías mayores a 110 mm se despachan en tiras de 6 o 12 metros
    - Las tuberías pueden ser fabricadas en color azul, negro o negro con líneas azules
    - Para diámetros mayores a 1200 mm, comunicarse con su asesor comercial
    """)
    
    # Cargar datos
    try:
        with open("data_tablas/pead_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        pead_tuberias = data.get("pead_tuberias", [])
    except FileNotFoundError:
        st.error("Archivo pead_data.json no encontrado")
        return
    except Exception as e:
        st.error(f"Error cargando archivo: {e}")
        return
    
    if pead_tuberias:
        # Crear DataFrame simplificado para edición
        df_data = []
        for tuberia in pead_tuberias:
            row = {
                "diametro_nominal_mm": tuberia["diametro_nominal_mm"],
                "s12_5_espesor": tuberia["s12_5"]["espesor_mm"] if tuberia["s12_5"]["espesor_mm"] is not None else "-",
                "s12_5_costo": tuberia["s12_5"].get("costo_usd_m", 0.0),
                "s10_espesor": tuberia["s10"]["espesor_mm"] if tuberia["s10"]["espesor_mm"] is not None else "-",
                "s10_costo": tuberia["s10"].get("costo_usd_m", 0.0),
                "s8_espesor": tuberia["s8"]["espesor_mm"] if tuberia["s8"]["espesor_mm"] is not None else "-",
                "s8_costo": tuberia["s8"].get("costo_usd_m", 0.0),
                "s6_3_espesor": tuberia["s6_3"]["espesor_mm"] if tuberia["s6_3"]["espesor_mm"] is not None else "-",
                "s6_3_costo": tuberia["s6_3"].get("costo_usd_m", 0.0),
                "s5_espesor": tuberia["s5"]["espesor_mm"] if tuberia["s5"]["espesor_mm"] is not None else "-",
                "s5_costo": tuberia["s5"].get("costo_usd_m", 0.0),
                "s4_espesor": tuberia["s4"]["espesor_mm"] if tuberia["s4"]["espesor_mm"] is not None else "-",
                "s4_costo": tuberia["s4"].get("costo_usd_m", 0.0)
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        
        # Mostrar tabla editable
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "diametro_nominal_mm": st.column_config.NumberColumn("Diámetro Nominal (mm)", disabled=True),
                "s12_5_espesor": st.column_config.NumberColumn("S12.5 e(mm)", format="%.1f"),
                "s12_5_costo": st.column_config.NumberColumn("💰 Costo S12.5 (USD/m)", format="%.2f"),
                "s10_espesor": st.column_config.NumberColumn("S10 e(mm)", format="%.1f"),
                "s10_costo": st.column_config.NumberColumn("💰 Costo S10 (USD/m)", format="%.2f"),
                "s8_espesor": st.column_config.NumberColumn("S8 e(mm)", format="%.1f"),
                "s8_costo": st.column_config.NumberColumn("💰 Costo S8 (USD/m)", format="%.2f"),
                "s6_3_espesor": st.column_config.NumberColumn("S6.3 e(mm)", format="%.1f"),
                "s6_3_costo": st.column_config.NumberColumn("💰 Costo S6.3 (USD/m)", format="%.2f"),
                "s5_espesor": st.column_config.NumberColumn("S5 e(mm)", format="%.1f"),
                "s5_costo": st.column_config.NumberColumn("💰 Costo S5 (USD/m)", format="%.2f"),
                "s4_espesor": st.column_config.NumberColumn("S4 e(mm)", format="%.1f"),
                "s4_costo": st.column_config.NumberColumn("💰 Costo S4 (USD/m)", format="%.2f")
            }
        )
        
        # Botones de acción
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Guardar Cambios", key="save_pead"):
                try:
                    # Crear respaldo
                    import shutil
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    shutil.copy("data_tablas/pead_data.json", f"data_tablas/backups/pead_backup_{timestamp}.json")
                    
                    # Actualizar datos
                    for i, row in edited_df.iterrows():
                        if i < len(pead_tuberias):
                            pead_tuberias[i]["s12_5"]["espesor_mm"] = row["s12_5_espesor"] if row["s12_5_espesor"] != "-" else None
                            pead_tuberias[i]["s12_5"]["costo_usd_m"] = row["s12_5_costo"]
                            pead_tuberias[i]["s10"]["espesor_mm"] = row["s10_espesor"] if row["s10_espesor"] != "-" else None
                            pead_tuberias[i]["s10"]["costo_usd_m"] = row["s10_costo"]
                            pead_tuberias[i]["s8"]["espesor_mm"] = row["s8_espesor"] if row["s8_espesor"] != "-" else None
                            pead_tuberias[i]["s8"]["costo_usd_m"] = row["s8_costo"]
                            pead_tuberias[i]["s6_3"]["espesor_mm"] = row["s6_3_espesor"] if row["s6_3_espesor"] != "-" else None
                            pead_tuberias[i]["s6_3"]["costo_usd_m"] = row["s6_3_costo"]
                            pead_tuberias[i]["s5"]["espesor_mm"] = row["s5_espesor"] if row["s5_espesor"] != "-" else None
                            pead_tuberias[i]["s5"]["costo_usd_m"] = row["s5_costo"]
                            pead_tuberias[i]["s4"]["espesor_mm"] = row["s4_espesor"] if row["s4_espesor"] != "-" else None
                            pead_tuberias[i]["s4"]["costo_usd_m"] = row["s4_costo"]
                    
                    data["pead_tuberias"] = pead_tuberias
                    
                    # Guardar archivo
                    with open("data_tablas/pead_data.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    st.success("✅ Cambios guardados exitosamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error guardando: {e}")
        
        with col2:
            if st.button("🔄 Recargar", key="reload_pead"):
                st.rerun()
        
        with col3:
            # Descargar JSON
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            st.download_button(
                "📥 Descargar JSON",
                json_str,
                file_name="pead_data.json",
                mime="application/json"
            )
    else:
        st.warning("No hay datos disponibles")

def render_motores_editor():
    """Editor para tabla de motores estándar"""
    st.subheader("Motores Eléctricos Estándar")
    st.markdown("Edita los datos de motores eléctricos para sistemas de bombeo.")
    
    # Cargar datos
    try:
        with open("data_tablas/motores_estandar_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        motores = data.get("motores_estandar", [])
    except FileNotFoundError:
        st.error("Archivo motores_estandar_data.json no encontrado")
        return
    except Exception as e:
        st.error(f"Error cargando archivo: {e}")
        return
    
    if motores:
        # Convertir a DataFrame
        df = pd.DataFrame(motores)
        
        # Mostrar tabla editable
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "potencia_hp": st.column_config.NumberColumn("Potencia HP", min_value=0.1, max_value=1000.0, required=True),
                "potencia_kw": st.column_config.NumberColumn("Potencia kW", min_value=0.1, max_value=1000.0, required=True),
                "rpm_estandar": st.column_config.NumberColumn("RPM", min_value=500, max_value=5000, required=True),
                "eficiencia_porcentaje": st.column_config.NumberColumn("Eficiencia %", min_value=50, max_value=100, required=True),
                "factor_potencia": st.column_config.NumberColumn("Factor Potencia", min_value=0.5, max_value=1.0, required=True),
                "corriente_nominal_a": st.column_config.NumberColumn("Corriente A", min_value=0.1, max_value=1000.0, required=True),
                "tension_nominal_v": st.column_config.NumberColumn("Tensión V", min_value=110, max_value=1000, required=True),
                "fases": st.column_config.NumberColumn("Fases", min_value=1, max_value=3, required=True),
                "tipo_arranque": st.column_config.TextColumn("Tipo Arranque", required=True),
                "aplicacion": st.column_config.TextColumn("Aplicación"),
                "costo_estimado_usd": st.column_config.NumberColumn("Costo USD", min_value=0, max_value=100000),
                "peso_kg": st.column_config.NumberColumn("Peso kg", min_value=0, max_value=10000)
            }
        )
        
        # Botones de acción
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Guardar Cambios", key="save_motores"):
                try:
                    # Crear respaldo
                    import shutil
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    shutil.copy("data_tablas/motores_estandar_data.json", f"data_tablas/backups/motores_backup_{timestamp}.json")
                    
                    # Actualizar datos
                    data["motores_estandar"] = edited_df.to_dict("records")
                    
                    # Guardar archivo
                    with open("data_tablas/motores_estandar_data.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    st.success("✅ Cambios guardados exitosamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error guardando: {e}")
        
        with col2:
            if st.button("🔄 Recargar", key="reload_motores"):
                st.rerun()
        
        with col3:
            # Descargar JSON
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            st.download_button(
                "📥 Descargar JSON",
                json_str,
                file_name="motores_estandar_data.json",
                mime="application/json"
            )
    else:
        st.warning("No hay datos disponibles")

def render_hierro_ductil_editor():
    """Editor para tabla de tuberías de hierro dúctil"""
    st.subheader("Tabla de Espesores, Presiones y Rigideces - Tuberías de Hierro Dúctil")
    st.markdown("""
    **Especificaciones para tuberías de hierro dúctil según ISO 2531:2009**
    
    Esta tabla permite determinar las características técnicas basadas en:
    - Clase de presión (C20, C25, C30, C40)
    - Diámetro nominal (DN)
    
    **Clases de Presión (ISO 2531):**
    - **C40** = PN 40 → 40 bar - Sistemas de alta presión, impulsiones de bombeo
    - **C30** = PN 30 → 30 bar - Redes principales de distribución de agua
    - **C25** = PN 25 → 25 bar - Redes secundarias, zonas con presiones moderadas
    - **C20** = PN 20 → 20 bar - Sistemas de baja presión, riego
    
    **Parámetros incluidos:**
    - DN: Diámetro nominal
    - DE: Diámetro externo
    - Espesor nominal y mínimo
    - PFA: Presión de trabajo admisible
    - PMA: Presión máxima admisible
    - Rigidez diametral
    - Deflexión diametral admisible
    """)
    
    # Cargar datos
    try:
        with open("data_tablas/hierro_ductil_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        hierro_ductil = data.get("hierro_ductil", {})
    except FileNotFoundError:
        st.error("Archivo hierro_ductil_data.json no encontrado")
        return
    except Exception as e:
        st.error(f"Error cargando archivo: {e}")
        return
    
    if hierro_ductil:
        # Crear sub-pestañas para cada clase
        clase_tab1, clase_tab2, clase_tab3, clase_tab4 = st.tabs([
            "C40 (40 bar)", "C30 (30 bar)", "C25 (25 bar)", "C20 (20 bar)"
        ])
        
        clases = ["c40", "c30", "c25", "c20"]
        tabs = [clase_tab1, clase_tab2, clase_tab3, clase_tab4]
        
        for i, (clase_key, tab) in enumerate(zip(clases, tabs)):
            with tab:
                if clase_key in hierro_ductil:
                    clase_data = hierro_ductil[clase_key]
                    tuberias = clase_data.get("tuberias", [])
                    
                    st.markdown(f"**{clase_data['clase']} - {clase_data['descripcion']}**")
                    st.info(f"PFA: {clase_data['pfa_bar']} bar | PMA: {clase_data['pma_bar']} bar")
                    
                    if tuberias:
                        # Crear DataFrame
                        df = pd.DataFrame(tuberias)
                        
                        # Mostrar tabla editable
                        edited_df = st.data_editor(
                            df,
                            use_container_width=True,
                            num_rows="dynamic",
                            column_config={
                                "dn_mm": st.column_config.NumberColumn("DN (mm)", disabled=True),
                                "de_mm": st.column_config.NumberColumn("DE (mm)", format="%.0f"),
                                "espesor_nominal_mm": st.column_config.NumberColumn("Espesor Nominal (mm)", format="%.1f"),
                                "espesor_minimo_mm": st.column_config.NumberColumn("Espesor Mínimo (mm)", format="%.1f"),
                                "rigidez_kn_m2": st.column_config.NumberColumn("Rigidez (kN/m²)", format="%.0f"),
                                "deflexion_admisible_porcentaje": st.column_config.NumberColumn("Deflexión Admisible (%)", format="%.2f"),
                                "costo_usd_m": st.column_config.NumberColumn("💰 Costo (USD/m)", format="%.2f", min_value=0.0)
                            }
                        )
                        
                        # Botones de acción
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button(f"💾 Guardar {clase_data['clase']}", key=f"save_{clase_key}"):
                                try:
                                    # Crear respaldo
                                    import shutil
                                    from datetime import datetime
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    shutil.copy("data_tablas/hierro_ductil_data.json", f"data_tablas/backups/hierro_ductil_backup_{timestamp}.json")
                                    
                                    # Actualizar datos
                                    hierro_ductil[clase_key]["tuberias"] = edited_df.to_dict("records")
                                    data["hierro_ductil"] = hierro_ductil
                                    
                                    # Guardar archivo
                                    with open("data_tablas/hierro_ductil_data.json", "w", encoding="utf-8") as f:
                                        json.dump(data, f, indent=2, ensure_ascii=False)
                                    
                                    st.success(f"✅ Cambios guardados para {clase_data['clase']}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error guardando: {e}")
                        
                        with col2:
                            if st.button(f"🔄 Recargar {clase_data['clase']}", key=f"reload_{clase_key}"):
                                st.rerun()
                        
                        with col3:
                            # Descargar JSON
                            json_str = json.dumps(data, indent=2, ensure_ascii=False)
                            st.download_button(
                                f"📥 Descargar {clase_data['clase']}",
                                json_str,
                                file_name="hierro_ductil_data.json",
                                mime="application/json",
                                key=f"download_{clase_key}"
                            )
                    else:
                        st.warning(f"No hay datos disponibles para {clase_data['clase']}")
                else:
                    st.warning(f"No se encontró la clase {clase_key}")
    else:
        st.warning("No hay datos de hierro dúctil disponibles")

def render_hierro_fundido_editor():
    """Editor para tabla de tuberías de hierro fundido"""
    st.subheader("Tabla de Espesores, Presiones y Pesos - Tuberías de Hierro Fundido")
    st.markdown("""
    **Especificaciones para tuberías de hierro fundido según clases de presión**
    
    Esta tabla permite determinar las características técnicas basadas en:
    - Clase de presión (Clase 150, Clase 125, Clase 100)
    - Diámetro nominal (DN)
    
    **Clases de Presión:**
    - **Clase 150** = 15 bar - Sistemas de presión estándar
    - **Clase 125** = 12.5 bar - Sistemas de presión media
    - **Clase 100** = 10 bar - Sistemas de baja presión
    
    **Parámetros incluidos:**
    - DN: Diámetro nominal
    - DE: Diámetro externo
    - Espesor de pared
    - DI: Diámetro interno (directo de tabla)
    - P. Trabajo: Presión de trabajo admisible
    - P. Máxima: Presión máxima admisible
    - Peso: Peso por metro lineal
    """)
    
    # Cargar datos
    try:
        with open("data_tablas/hierro_fundido_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        hierro_fundido = data.get("hierro_fundido", {})
    except FileNotFoundError:
        st.error("Archivo hierro_fundido_data.json no encontrado")
        return
    except Exception as e:
        st.error(f"Error cargando archivo: {e}")
        return
    
    if hierro_fundido:
        # Crear sub-pestañas para cada clase
        clase_tab1, clase_tab2, clase_tab3 = st.tabs([
            "Clase 150 (15 bar)", "Clase 125 (12.5 bar)", "Clase 100 (10 bar)"
        ])
        
        clases = ["clase_150", "clase_125", "clase_100"]
        tabs = [clase_tab1, clase_tab2, clase_tab3]
        
        for i, (clase_key, tab) in enumerate(zip(clases, tabs)):
            with tab:
                if clase_key in hierro_fundido:
                    clase_data = hierro_fundido[clase_key]
                    tuberias = clase_data.get("tuberias", [])
                    
                    st.markdown(f"**{clase_data['clase']} - {clase_data['descripcion']}**")
                    st.info(f"P. Trabajo: {clase_data['pfa_bar']} bar | P. Máxima: {clase_data['pma_bar']} bar")
                    
                    if tuberias:
                        # Crear DataFrame
                        df = pd.DataFrame(tuberias)
                        
                        # Mostrar tabla editable
                        edited_df = st.data_editor(
                            df,
                            use_container_width=True,
                            num_rows="dynamic",
                            column_config={
                                "dn_mm": st.column_config.NumberColumn("DN (mm)", disabled=True),
                                "de_mm": st.column_config.NumberColumn("DE (mm)", format="%.0f"),
                                "espesor_mm": st.column_config.NumberColumn("Espesor (mm)", format="%.1f"),
                                "di_mm": st.column_config.NumberColumn("DI (mm)", format="%.1f"),
                                "peso_kg_m": st.column_config.NumberColumn("Peso (kg/m)", format="%.1f")
                            }
                        )
                        
                        # Botones de acción
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button(f"💾 Guardar {clase_data['clase']}", key=f"save_hf_{clase_key}"):
                                try:
                                    # Crear respaldo
                                    import shutil
                                    from datetime import datetime
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    shutil.copy("data_tablas/hierro_fundido_data.json", f"data_tablas/backups/hierro_fundido_backup_{timestamp}.json")
                                    
                                    # Actualizar datos
                                    hierro_fundido[clase_key]["tuberias"] = edited_df.to_dict("records")
                                    data["hierro_fundido"] = hierro_fundido
                                    
                                    # Guardar archivo
                                    with open("data_tablas/hierro_fundido_data.json", "w", encoding="utf-8") as f:
                                        json.dump(data, f, indent=2, ensure_ascii=False)
                                    
                                    st.success(f"✅ Cambios guardados para {clase_data['clase']}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error guardando: {e}")
                        
                        with col2:
                            if st.button(f"🔄 Recargar {clase_data['clase']}", key=f"reload_hf_{clase_key}"):
                                st.rerun()
                        
                        with col3:
                            # Descargar JSON
                            json_str = json.dumps(data, indent=2, ensure_ascii=False)
                            st.download_button(
                                f"📥 Descargar {clase_data['clase']}",
                                json_str,
                                file_name="hierro_fundido_data.json",
                                mime="application/json",
                                key=f"download_hf_{clase_key}"
                            )
                    else:
                        st.warning(f"No hay datos disponibles para {clase_data['clase']}")
                else:
                    st.warning(f"No se encontró la clase {clase_key}")
    else:
        st.warning("No hay datos de hierro fundido disponibles")

def render_pvc_editor():
    """Editor para tabla de tuberías PVC"""
    st.subheader("Tabla de Espesores y Presiones - Tuberías PVC para Presión")
    st.markdown("""
    **Especificaciones para tuberías PVC según tipo de unión y serie**
    
    Esta tabla permite determinar las características técnicas basadas en:
    - Tipo de unión (Unión Sellado Elastomérico, Unión Espiga Campana)
    - Serie del tubo (S 20.0, S 16.0, S 12.5, S 10.0, S 8.0, S 6.3)
    - Diámetro nominal (DN)
    
    **Tipos de Unión:**
    - **Unión Sellado Elastomérico (Unión R)** - Para sistemas de presión
    - **Unión Espiga Campana** - Para sistemas de presión
    
    **Series y Presiones:**
    - **S 20.0** = 0.63 MPa (6.3 bar) - Espesores delgados, bajo costo
    - **S 16.0** = 0.80 MPa (8.0 bar) - Balance costo/performance
    - **S 12.5** = 1.00 MPa (10.0 bar) - Uso general, más común
    - **S 10.0** = 1.25 MPa (12.5 bar) - Alta resistencia
    - **S 8.0** = 1.60 MPa (16.0 bar) - Alta presión
    - **S 6.3** = 2.00 MPa (20.0 bar) - Muy alta presión
    
    **Parámetros incluidos:**
    - DN: Diámetro nominal
    - DE: Diámetro externo
    - Tolerancia: Tolerancia de fabricación
    - Espesor Mín/Máx: Espesor mínimo y máximo de pared
    - Presión: Presión nominal de trabajo
    - DI: Diámetro interno calculado = DE - 2 * (espesor_max + espesor_min) / 2
    """)
    
    # Cargar datos
    try:
        with open("data_tablas/pvc_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        pvc_tuberias = data.get("pvc_tuberias", {})
    except FileNotFoundError:
        st.error("Archivo pvc_data.json no encontrado")
        return
    except Exception as e:
        st.error(f"Error cargando archivo: {e}")
        return
    
    if pvc_tuberias:
        # Crear sub-pestañas para cada tipo de unión
        union_tab1, union_tab2 = st.tabs([
            "Unión Sellado Elastomérico (Unión R)", "Unión Espiga Campana"
        ])
        
        tipos_union = ["union_elastomerica", "union_espiga_campana"]
        tabs = [union_tab1, union_tab2]
        
        for i, (tipo_union_key, tab) in enumerate(zip(tipos_union, tabs)):
            with tab:
                if tipo_union_key in pvc_tuberias:
                    union_data = pvc_tuberias[tipo_union_key]
                    series = union_data.get("series", {})
                    
                    st.markdown(f"**{union_data['tipo']}**")
                    st.info(f"{union_data['descripcion']}")
                    
                    if series:
                        # Crear sub-pestañas para cada serie
                        serie_tabs = st.tabs([
                            "S 20.0 (0.63 MPa)", "S 16.0 (0.80 MPa)", "S 12.5 (1.00 MPa)", 
                            "S 10.0 (1.25 MPa)", "S 8.0 (1.60 MPa)", "S 6.3 (2.00 MPa)"
                        ])
                        
                        serie_keys = ["s20", "s16", "s12_5", "s10", "s8", "s6_3"]
                        
                        for j, (serie_key, serie_tab) in enumerate(zip(serie_keys, serie_tabs)):
                            with serie_tab:
                                if serie_key in series:
                                    serie_data = series[serie_key]
                                    tuberias = serie_data.get("tuberias", [])
                                    
                                    st.markdown(f"**{serie_data['serie']} - {serie_data['descripcion']}**")
                                    st.info(f"Presión: {serie_data['presion_mpa']} MPa ({serie_data['presion_bar']} bar)")
                                    
                                    if tuberias:
                                        # Crear DataFrame
                                        df = pd.DataFrame(tuberias)
                                        
                                        # Calcular DI para cada tubería
                                        df['di_mm'] = df.apply(
                                            lambda row: row['de_mm'] - 2 * (row['espesor_max_mm'] + row['espesor_min_mm']) / 2, 
                                            axis=1
                                        )
                                        
                                        # Mostrar tabla editable
                                        edited_df = st.data_editor(
                                            df,
                                            use_container_width=True,
                                            num_rows="dynamic",
                                            column_config={
                                                "dn_mm": st.column_config.NumberColumn("DN (mm)", disabled=True),
                                                "de_mm": st.column_config.NumberColumn("DE (mm)", format="%.0f"),
                                                "tolerancia": st.column_config.NumberColumn("Tolerancia", format="%.1f"),
                                                "espesor_min_mm": st.column_config.NumberColumn("Espesor Mín (mm)", format="%.1f"),
                                                "espesor_max_mm": st.column_config.NumberColumn("Espesor Máx (mm)", format="%.1f"),
                                                "costo_usd_m": st.column_config.NumberColumn("💰 Costo (USD/m)", format="%.2f", min_value=0.0),
                                                "di_mm": st.column_config.NumberColumn("DI (mm)", format="%.1f", disabled=True)
                                            }
                                        )
                                        
                                        # Botones de acción
                                        col1, col2, col3 = st.columns(3)
                                        
                                        with col1:
                                            if st.button(f"💾 Guardar {serie_data['serie']}", key=f"save_pvc_{tipo_union_key}_{serie_key}"):
                                                try:
                                                    # Crear respaldo
                                                    import shutil
                                                    from datetime import datetime
                                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                                    shutil.copy("data_tablas/pvc_data.json", f"data_tablas/backups/pvc_backup_{timestamp}.json")
                                                    
                                                    # Actualizar datos (remover columna DI calculada)
                                                    edited_data = edited_df.drop(columns=['di_mm']).to_dict("records")
                                                    pvc_tuberias[tipo_union_key]["series"][serie_key]["tuberias"] = edited_data
                                                    data["pvc_tuberias"] = pvc_tuberias
                                                    
                                                    # Guardar archivo
                                                    with open("data_tablas/pvc_data.json", "w", encoding="utf-8") as f:
                                                        json.dump(data, f, indent=2, ensure_ascii=False)
                                                    
                                                    st.success(f"✅ Cambios guardados para {serie_data['serie']}")
                                                    st.rerun()
                                                except Exception as e:
                                                    st.error(f"Error guardando: {e}")
                                        
                                        with col2:
                                            if st.button(f"🔄 Recargar {serie_data['serie']}", key=f"reload_pvc_{tipo_union_key}_{serie_key}"):
                                                st.rerun()
                                        
                                        with col3:
                                            # Descargar JSON
                                            json_str = json.dumps(data, indent=2, ensure_ascii=False)
                                            st.download_button(
                                                f"📥 Descargar {serie_data['serie']}",
                                                json_str,
                                                file_name="pvc_data.json",
                                                mime="application/json",
                                                key=f"download_pvc_{tipo_union_key}_{serie_key}"
                                            )
                                    else:
                                        st.warning(f"No hay datos disponibles para {serie_data['serie']}")
                                else:
                                    st.warning(f"No se encontró la serie {serie_key}")
                    else:
                        st.warning(f"No hay series disponibles para {union_data['tipo']}")
                else:
                    st.warning(f"No se encontró el tipo de unión {tipo_union_key}")
        else:
            st.warning("No hay datos de PVC disponibles")

def render_celeridad_editor():
    """Editor para tabla de velocidades de onda (celeridad)"""
    st.subheader("Velocidades de Onda - Celeridad")
    st.markdown("""
    Esta tabla contiene las velocidades de onda de presión para diferentes materiales de tuberías,
    utilizadas en el análisis de transientes hidráulicos (golpe de ariete).
    """)
    
    import shutil
    import os
    from datetime import datetime
    
    try:
        # Cargar datos existentes
        with open("data_tablas/wave_speeds_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            wave_speeds = data.get("wave_speeds", {})
            notes = data.get("notes", {})
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo wave_speeds_data.json")
        return
    except json.JSONDecodeError:
        st.error("❌ Error al leer el archivo JSON")
        return
    
    # Mostrar información general
    st.markdown("### 📋 Información General")
    st.info(f"""
    **Descripción:** {notes.get('description', 'N/A')}
    
    **Referencias:** {notes.get('references', 'N/A')}
    """)
    
    # Mostrar fórmula en LaTeX
    st.markdown("### 🧮 Fórmula de Velocidad de Onda")
    formula_latex = notes.get('speed_formula', 'N/A')
    if formula_latex != 'N/A':
        st.latex(formula_latex)
        st.markdown("""
        **Donde:**
        - $a$ = Velocidad de onda de presión (m/s)
        - $K_{bulk}$ = Módulo de compresibilidad del fluido (Pa)
        - $\\rho$ = Densidad del fluido (kg/m³)
        - $E_{young}$ = Módulo de Young del material de tubería (Pa)
        - $D$ = Diámetro interno de la tubería (m)
        - $e$ = Espesor de la pared de la tubería (m)
        """)
    else:
        st.warning("Fórmula no disponible")
    
    # Crear DataFrame para edición
    if wave_speeds:
        df_data = []
        for material, properties in wave_speeds.items():
            df_data.append({
                'Material': material,
                'Código': properties.get('material_code', ''),
                'Velocidad Onda (m/s)': properties.get('typical_wave_speed', 0),
                'Velocidad Mín (m/s)': properties.get('min_wave_speed', 0),
                'Velocidad Máx (m/s)': properties.get('max_wave_speed', 0),
                'Densidad (kg/m³)': properties.get('density', 0),
                'Módulo Young (Pa)': properties.get('young_modulus', 0),
                'Notas': properties.get('notes', '')
            })
        
        df = pd.DataFrame(df_data)
        
        # Mostrar tabla editable
        st.markdown("### ✏️ Editar Datos")
        
        # Crear columnas para la edición
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Tabla de Velocidades de Onda:**")
            edited_df = st.data_editor(
                df,
                key="celeridad_editor",
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "Material": st.column_config.TextColumn(
                        "Material",
                        help="Nombre del material de tubería",
                        width="medium"
                    ),
                    "Código": st.column_config.TextColumn(
                        "Código",
                        help="Código identificador del material",
                        width="small"
                    ),
                    "Velocidad Onda (m/s)": st.column_config.NumberColumn(
                        "Velocidad Onda (m/s)",
                        help="Velocidad típica de onda de presión (promedio del rango)",
                        min_value=0,
                        max_value=2000,
                        step=10,
                        format="%.0f"
                    ),
                    "Velocidad Mín (m/s)": st.column_config.NumberColumn(
                        "Velocidad Mín (m/s)",
                        help="Velocidad mínima de onda de presión",
                        min_value=0,
                        max_value=2000,
                        step=10,
                        format="%.0f"
                    ),
                    "Velocidad Máx (m/s)": st.column_config.NumberColumn(
                        "Velocidad Máx (m/s)",
                        help="Velocidad máxima de onda de presión",
                        min_value=0,
                        max_value=2000,
                        step=10,
                        format="%.0f"
                    ),
                    "Densidad (kg/m³)": st.column_config.NumberColumn(
                        "Densidad (kg/m³)",
                        help="Densidad del material",
                        min_value=0,
                        max_value=10000,
                        step=10,
                        format="%.0f"
                    ),
                    "Módulo Young (Pa)": st.column_config.NumberColumn(
                        "Módulo Young (Pa)",
                        help="Módulo de elasticidad del material",
                        min_value=0,
                        step=1000000000,
                        format="%.0e"
                    ),
                    "Notas": st.column_config.TextColumn(
                        "Notas",
                        help="Información adicional sobre el material",
                        width="large"
                    )
                }
            )
        
        with col2:
            st.markdown("**Acciones:**")
            
            # Botón para guardar cambios
            if st.button("💾 Guardar Cambios", key="save_celeridad", type="primary"):
                try:
                    # Crear backup
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    os.makedirs("data_tablas/backups", exist_ok=True)
                    shutil.copy("data_tablas/wave_speeds_data.json", f"data_tablas/backups/wave_speeds_backup_{timestamp}.json")
                    
                    # Convertir DataFrame editado de vuelta al formato JSON
                    new_wave_speeds = {}
                    for _, row in edited_df.iterrows():
                        material = row['Material']
                        new_wave_speeds[material] = {
                            'material_code': row['Código'],
                            'typical_wave_speed': int(row['Velocidad Onda (m/s)']),
                            'min_wave_speed': int(row['Velocidad Mín (m/s)']),
                            'max_wave_speed': int(row['Velocidad Máx (m/s)']),
                            'density': int(row['Densidad (kg/m³)']),
                            'young_modulus': int(row['Módulo Young (Pa)']),
                            'notes': row['Notas']
                        }
                    
                    # Crear estructura completa del JSON
                    new_data = {
                        "wave_speeds": new_wave_speeds,
                        "notes": notes
                    }
                    
                    # Guardar archivo
                    with open("data_tablas/wave_speeds_data.json", "w", encoding="utf-8") as f:
                        json.dump(new_data, f, indent=2, ensure_ascii=False)
                    
                    st.success("✅ Cambios guardados exitosamente!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error al guardar: {str(e)}")
            
            # Botón para descargar JSON
            if st.button("📥 Descargar JSON", key="download_celeridad"):
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📄 Descargar wave_speeds_data.json",
                    data=json_str,
                    file_name="wave_speeds_data.json",
                    mime="application/json",
                    key="download_celerity_json"
                )
            
            # Botón para descargar CSV
            if st.button("📊 Descargar CSV", key="download_celeridad_csv"):
                csv_str = edited_df.to_csv(index=False)
                st.download_button(
                    label="📄 Descargar celeridad.csv",
                    data=csv_str,
                    file_name="celeridad.csv",
                    mime="text/csv",
                    key="download_celerity_csv"
                )
        
        # Mostrar información técnica
        st.markdown("### 📚 Información Técnica")
        st.info("""
        **Velocidad de Onda de Presión:**
        - Es la velocidad a la que se propagan las ondas de presión en un fluido dentro de una tubería
        - Depende de las propiedades del fluido y del material de la tubería
        - Es fundamental para el análisis de transientes hidráulicos
        
        **Rangos de Velocidad:**
        - **Valor Típico**: Promedio del rango, usado por defecto en cálculos
        - **Valor Mínimo**: Límite inferior del rango para condiciones conservadoras
        - **Valor Máximo**: Límite superior del rango para condiciones extremas
        - **Selección**: El usuario puede elegir valores dentro del rango según condiciones específicas
        
        **Factores que Afectan la Celeridad:**
        - Rigidez del material de la tubería (módulo de Young)
        - Espesor de la pared de la tubería
        - Propiedades del fluido (densidad, módulo de compresibilidad)
        - Condiciones de soporte de la tubería
        
        **Uso en Análisis Transientes:**
        - Cálculo del tiempo de onda: T = 2L/a (donde L=longitud, a=celeridad)
        - Determinación de períodos de oscilación
        - Análisis de estabilidad del sistema
        """)
