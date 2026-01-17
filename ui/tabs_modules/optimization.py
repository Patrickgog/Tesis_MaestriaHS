import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from core.genetic_optimizer import GeneticOptimizer
from ui.tabs_modules.common import render_footer

def render_optimization_tab():
    """Renderiza la pestaña de Optimización con Algoritmos Genéticos"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E3A5F 0%, #2C3E50 100%); 
                padding: 30px; border-radius: 15px; margin-bottom: 25px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3); border-left: 8px solid #FFD700;">
        <h1 style="color: #FFD700; margin: 0; font-size: 2.2em; font-weight: 700;">
            🎯 Optimización Inteligente (AG)
        </h1>
        <p style="color: #ECF0F1; margin-top: 10px; font-size: 1.1em; opacity: 0.9;">
            Dimensionamiento económico de tuberías mediante Algoritmos Genéticos (Selección Natural)
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Obtener datos de entrada base si existen
    q_lps_total = st.session_state.get('caudal_lps', 10.0)
    num_bombas = st.session_state.get('num_bombas', 1)
    q_lps_def = q_lps_total / num_bombas  # Caudal por bomba
    l_succion_def = st.session_state.get('long_succion', 10.0)
    l_impulsion_def = st.session_state.get('long_impulsion', 100.0)
    h_estatica_def = st.session_state.get('altura_descarga', 30.0)

    col_conf1, col_conf2, col_vacia = st.columns([25, 50, 25])
    
    with col_conf1:
        st.subheader("⚙️ Configuración del Escenario")
        caudal = st.number_input("Caudal de Diseño por Bomba (L/s)", value=q_lps_def, step=1.0, help="Flujo volumétrico requerido por cada bomba individual.")
        h_est = st.number_input("Altura Estática Real (m)", value=h_estatica_def, step=1.0, help="Diferencia de elevación entre succión y descarga.")
        
        with st.expander("📏 Longitudes de Tubería", expanded=True):
            l_succion = st.number_input("Longitud Succión (m)", value=l_succion_def, step=1.0)
            l_impulsion = st.number_input("Longitud Impulsión (m)", value=l_impulsion_def, step=1.0)

        with st.expander("💰 Parámetros Económicos", expanded=False):
            costo_kwh = st.number_input("Costo Energía (USD/kWh)", value=0.09, step=0.01, help="Tarifa ARCONEL 2025 para bombeo público.")
            años = st.slider("Años de Análisis (Vida Útil)", 5, 50, 25, help="Periodo normativo recomendado (NTE INEN 1680).")
            horas = st.slider("Horas de Operación / Día", 1, 24, 12)
            tasa = st.number_input("Tasa de Descuento Anual (%)", value=5.0, step=0.5, help="Tasa usada para traer costos futuros al presente (Valor Presente Neto).") / 100.0

        with st.expander("🧬 Parámetros Genéticos (IA)", expanded=False):
            pop = st.slider("Tamaño de Población (Individuos)", 20, 100, 40, help="Número de combinaciones aleatorias generadas en cada generación.")
            gens = st.slider("Generaciones Máximas (Iteraciones)", 10, 200, 50, help="Número de ciclos de 'evolución' que realizará el algoritmo.")

        with st.expander("📈 Costos de Mercado (Plastigama/Rival)", expanded=False):
            st.info("Calibra el costo por metro: $Base \cdot (D_{pulg})^{Factor}$")
            c_pvc_b = st.number_input("PVC: Valor Base", value=1.0, step=0.1, help="Costo base para tubería de 1 pulgada.")
            c_pvc_f = st.number_input("PVC: Factor Exp.", value=1.6, step=0.05, help="Exponente de crecimiento de costo según el diámetro.")
            
            c_pead_b = st.number_input("PEAD: Valor Base", value=1.5, step=0.1)
            c_pead_f = st.number_input("PEAD: Factor Exp.", value=1.65, step=0.05)
            
            c_hd_b = st.number_input("Dúctil: Valor Base", value=10.0, step=0.5)
            c_hd_f = st.number_input("Dúctil: Factor Exp.", value=1.4, step=0.05)
            
            dict_costos = {
                "PVC": {"base": c_pvc_b, "factor": c_pvc_f},
                "PEAD": {"base": c_pead_b, "factor": c_pead_f},
                "Hierro Dúctil": {"base": c_hd_b, "factor": c_hd_f}
            }
            
        btn_run = st.button("🚀 Iniciar Evolución Genética", use_container_width=True, type="primary")

    with col_conf2:
        # Pestañas de la derecha: Resultados vs Guía
        main_tab1, main_tab2 = st.tabs(["📊 Resultados de Optimización", "📚 Guía Técnica y Manual"])

        with main_tab2:
            st.markdown(r"""
            ### 📖 Guía Técnica Detallada: Optimización Económica
            
            Este módulo utiliza **Algoritmos Genéticos (AG)** para resolver el problema del **Diámetro Económico**. Se denomina "Evolución Genética" porque imita la selección natural de Darwin para encontrar la solución más apta (la más barata y eficiente).

            #### 🧬 ¿Por qué "Evolución Genética"?
            1.  **Cromosomas**: Cada diseño candidato es un "individuo" con una combinación única de materiales y diámetros.
            2.  **Población**: El sistema analiza muchos diseños a la vez (por defecto 40).
            3.  **Selección**: Los diseños que generan facturas de luz muy altas o que son demasiado caros de construir "mueren" simbólicamente.
            4.  **Cruce y Mutación**: Los mejores diseños intercambian sus "genes" (diámetros) para crear nuevas generaciones de tuberías aún más eficientes.

            #### ⚖️ Altura Estática vs. Altura Dinámica Total (ADT)
            Es común confundir estos términos al configurar la bomba:
            *   **Altura Estática ($H_e$):** Es la diferencia de nivel real entre el agua en la succión y el punto de descarga. **Es el dato que debes ingresar**, ya que es una constante física del terreno.
            *   **ADT (Altura Dinámica Total):** Es la carga total que la bomba debe vencer. 
                $$ ADT = H_e + \sum h_f + \frac{v^2}{2g} $$
                La ADT **varía según el diámetro** (a menor diámetro, mayor fricción $\sum h_f$ y mayor ADT). Por eso, el algoritmo recibe la altura estática y *calcula automáticamente* la ADT para cada diámetro evaluado para hallar el costo de energía real.

            #### 💸 1. Definiciones de Costos
            *   **CAPEX (Gasto de Capital):** Inversión inicial (compra de tubos, válvulas y obra civil).
            *   **OPEX (Gasto Operativo):** Costo acumulado de energía eléctrica durante la vida útil (ej. 20 años).

            #### 📈 Concepto Teórico del Diámetro Económico
            """)
            
            # Gráfico educativo siempre visible en el manual
            diametros_ej = np.array([50, 75, 110, 160, 200, 250, 315])
            capex_ej = 1000 * (diametros_ej/100)**1.5
            opex_ej = 5000 / (diametros_ej/100)**2
            total_ej = capex_ej + opex_ej
            
            fig_theory = go.Figure()
            fig_theory.add_trace(go.Scatter(x=diametros_ej, y=capex_ej, name="CAPEX (Inversión Inicial)", line=dict(dash='dash', color='orange')))
            fig_theory.add_trace(go.Scatter(x=diametros_ej, y=opex_ej, name="OPEX (Gasto de Energía)", line=dict(dash='dash', color='blue')))
            fig_theory.add_trace(go.Scatter(x=diametros_ej, y=total_ej, name="COSTO TOTAL (Suma)", line=dict(width=4, color='green')))
            
            fig_theory.update_layout(
                title="Curva del Diámetro Económico Ideal",
                xaxis_title="Diámetro de Tubería (mm)",
                yaxis_title="Costo Proyectado (USD)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig_theory, use_container_width=True)

            st.info("💡 **Dato Clave**: El punto más bajo de la línea verde es tu solución ideal. Menos diámetro sube la luz (OPEX), más diámetro sube la inversión (CAPEX).")

        with main_tab1:
            # Inicializar claves de estado para persistencia
            if 'ga_results' not in st.session_state:
                st.session_state.ga_results = None

            if btn_run:
                with st.status("🧬 Evolucionando población...", expanded=True) as status:
                    optimizer_engine = GeneticOptimizer(
                        caudal_lps=caudal,
                        long_succion=l_succion,
                        long_impulsion=l_impulsion,
                        h_estatica=h_est,
                        años_operacion=años,
                        costo_kwh=costo_kwh,
                        horas_dia=horas,
                        tasa_interes=tasa,
                        costos_personalizados=dict_costos
                    )
                    optimizer_engine.pop_size = pop
                    optimizer_engine.generations = gens
                    
                    history, best_ind = optimizer_engine.optimize()
                    
                    # Guardar en session_state para persistencia
                    st.session_state.ga_results = {
                        "history": history,
                        "best_ind": best_ind,
                        "params": {
                            "caudal": caudal, "l_s": l_succion, "l_i": l_impulsion, 
                            "h_est": h_est, "años": años, "costo_kwh": costo_kwh, 
                            "horas": horas, "tasa": tasa, "costos": dict_costos
                        }
                    }
                    status.update(label="✅ Optimización Completada", state="complete")

            if st.session_state.ga_results:
                results = st.session_state.ga_results
                history = results["history"]
                best_ind = results["best_ind"]
                best_data = history[-1]
                
                # Re-crear objeto optimizer para cálculos de sensibilidad (sin re-optimizar)
                optimizer_calc = GeneticOptimizer(
                    caudal_lps=results["params"]["caudal"],
                    long_succion=results["params"]["l_s"],
                    long_impulsion=results["params"]["l_i"],
                    h_estatica=results["params"]["h_est"],
                    años_operacion=results["params"]["años"],
                    costo_kwh=results["params"]["costo_kwh"],
                    horas_dia=results["params"]["horas"],
                    tasa_interes=results["params"]["tasa"],
                    costos_personalizados=results["params"].get("costos")
                )

                st.success("🏆 **¡Solución Óptima Encontrada!**")
                
                # Best Individual Details
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Succión Óptima", best_data["suction"])
                with c2:
                    st.metric("Impulsión Óptima", best_data["discharge"])
                with c3:
                    st.metric("Costo Vida Útil", f"${best_data['real_cost']:,.2f}")
                    
                # Gráficos de Resultados
                res_tab1, res_tab2 = st.tabs(["📊 Análisis Económico", "📈 Evolución Genética"])
                
                with res_tab1:
                    # CAPEX vs OPEX
                    fig_breakdown = px.bar(
                        x=["CAPEX (Inversión)", "OPEX (Operación 20 años)"],
                        y=[best_data["capex"], best_data["opex"]],
                        labels={'x': 'Categoría', 'y': 'Costo (USD)'},
                        title="Desglose de Costos de la Solución Óptima",
                        color=["CAPEX", "OPEX"],
                        color_discrete_map={"CAPEX": "orange", "OPEX": "blue"}
                    )
                    st.plotly_chart(fig_breakdown, use_container_width=True)
                    
                    st.markdown(f"""
                    > [!NOTE]
                    > **Interpretación**: La solución de **{best_data['discharge']}** ha sido elegida porque optimiza el costo total considerando la fricción acumulada (ADT).
                    """)

                with res_tab2:
                    # Convergencia
                    df_hist = pd.DataFrame(history)
                    fig_conv = px.line(df_hist, x="gen", y="cost", title="Convergencia: Costo Penalizado vs Generaciones")
                    fig_conv.update_traces(line_color='#FFD700', line_width=3)
                    st.plotly_chart(fig_conv, use_container_width=True)
                    
                    st.info(f"💡 **Interpretación**: Esta curva muestra cómo la 'inteligencia' del algoritmo mejora el diseño en cada iteración.")

                # --- ANÁLISIS DE SENSIBILIDAD ---
                st.divider()
                st.subheader("🔍 Comparativa Manual (Análisis de Sensibilidad)")
                st.markdown("Verifica por qué el algoritmo descartó otros materiales o diámetros:")
                
                col_sens1, col_sens2 = st.columns([1, 2])
                
                with col_sens1:
                    mat_comp = st.selectbox("Material Alternativo", optimizer_calc.materiales_validos)
                    dn_comp = st.select_slider("Diámetro Alternativo (mm)", options=optimizer_calc.catalog_dn, 
                                              value=optimizer_calc.catalog_dn[best_ind[3]] if best_ind[3] < len(optimizer_calc.catalog_dn) else optimizer_calc.catalog_dn[-1])
                    
                    # Cálculos
                    opt_s_mat = optimizer_calc.materiales_validos[best_ind[0]]
                    opt_s_dn = optimizer_calc.catalog_dn[best_ind[1]]
                    
                    capex_comp = optimizer_calc.calculate_capex(opt_s_mat, opt_s_dn, mat_comp, dn_comp)
                    opex_comp = optimizer_calc.calculate_opex(opt_s_mat, opt_s_dn, mat_comp, dn_comp)
                    total_comp = capex_comp + opex_comp
                    
                    diferencia = total_comp - best_data['real_cost']
                    if diferencia <= 0:
                        st.success(f"⚠️ El ajuste manual mejoró el costo en ${abs(diferencia):,.2f}.")
                    else:
                        st.warning(f"❌ Esta opción es **${diferencia:,.2f} más costosa** que el óptimo.")

                with col_sens2:
                    df_comp = pd.DataFrame({
                        "Escenario": ["Óptimo IA", "Demás Opciones"],
                        "CAPEX (USD)": [best_data["capex"], capex_comp],
                        "OPEX (USD)": [best_data["opex"], opex_comp]
                    })
                    fig_comp = px.bar(df_comp, x="Escenario", y=["CAPEX (USD)", "OPEX (USD)"], 
                                     title="Comparativa de Inversión vs Energía",
                                     barmode="group", color_discrete_sequence=['#F39C12', '#2980B9'])
                    st.plotly_chart(fig_comp, use_container_width=True)

            else:
                st.info("💡 **Aviso**: Haz clic en el botón de la izquierda para generar la optimización. Los resultados se mostrarán en esta pestaña.")

