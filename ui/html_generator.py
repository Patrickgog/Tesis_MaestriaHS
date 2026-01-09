"""
Módulo para generar reportes HTML del resumen del proyecto
"""

def generate_html_report(project_data, nombre_proyecto):
    """
    Genera un reporte HTML completo del proyecto con todos los datos y resultados.
    
    Args:
        project_data: Diccionario con los datos del proyecto
        nombre_proyecto: Nombre del proyecto
    
    Returns:
        String con el contenido HTML completo
    """
    
    # Función helper para formatear valores
    def fmt(value, decimals=2):
        if value == 'N/A' or value is None:
            return 'N/A'
        try:
            return f"{float(value):.{decimals}f}"
        except:
            return str(value)
    
    # Función helper para generar tabla de accesorios
    def generar_tabla_accesorios_html(accesorios_data, titulo):
        if not accesorios_data:
            return f"<p><strong>{titulo}:</strong> No hay accesorios disponibles.</p>"
        
        html = f"<h4>{titulo}</h4>"
        html += """
        <table>
        <thead>
            <tr>
                <th>Tipo</th>
                <th>Cantidad</th>
                <th>K</th>
                <th>Lc/D</th>
            </tr>
        </thead>
        <tbody>
        """
        for acc in accesorios_data:
            html += f"""
            <tr>
                <td>{acc.get('tipo', 'N/A')}</td>
                <td>{acc.get('cantidad', 'N/A')}</td>
                <td>{acc.get('k', 'N/A')}</td>
                <td>{acc.get('lc_d', 'N/A')}</td>
            </tr>
            """
        html += "</tbody></table>"
        return html
    
    # Inicio del HTML con estilo sobrio técnico (blancos y beige)
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resumen del Proyecto: {nombre_proyecto}</title>
        <style>
            * {{
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #faf9f7;
                color: #4a4a4a;
                line-height: 1.7;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: #ffffff;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 20px rgba(0,0,0,0.06);
                border: 1px solid #e8e4df;
            }}
            h1 {{
                color: #3d3d3d;
                font-weight: 500;
                letter-spacing: 0.5px;
                border-bottom: 2px solid #d4cfc7;
                padding-bottom: 15px;
                margin-bottom: 25px;
            }}
            h2 {{
                color: #4a4a4a;
                font-weight: 500;
                margin-top: 35px;
                padding-bottom: 10px;
                border-bottom: 1px solid #e8e4df;
                font-size: 1.25rem;
            }}
            h3 {{
                color: #666666;
                font-weight: 500;
                margin-top: 25px;
                font-size: 1.05rem;
            }}
            h4 {{
                color: #888888;
                font-weight: 500;
                margin-top: 20px;
                font-size: 0.95rem;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background-color: #ffffff;
                border-radius: 6px;
                overflow: hidden;
                box-shadow: 0 1px 8px rgba(0,0,0,0.04);
            }}
            th {{
                background: linear-gradient(135deg, #f5f3ef 0%, #ebe8e3 100%);
                color: #4a4a4a;
                padding: 14px 16px;
                text-align: left;
                font-weight: 600;
                border-bottom: 2px solid #d4cfc7;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            td {{
                border-bottom: 1px solid #f0ece6;
                padding: 12px 16px;
                transition: all 0.2s ease;
            }}
            tr {{
                transition: all 0.25s ease;
            }}
            tr:hover td {{
                background-color: #faf8f5;
                transform: translateX(2px);
            }}
            tr:nth-child(even) td {{
                background-color: #fcfbf9;
            }}
            tr:nth-child(even):hover td {{
                background-color: #f5f3ef;
            }}
            .section {{
                margin: 30px 0;
                padding: 25px;
                background-color: #fdfcfa;
                border-radius: 6px;
                border: 1px solid #ebe8e3;
                transition: all 0.3s ease;
            }}
            .section:hover {{
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                transform: translateY(-2px);
            }}
            hr {{
                border: none;
                border-top: 1px solid #e8e4df;
                margin: 35px 0;
            }}
            .info-box {{
                background: linear-gradient(135deg, #f9f7f4 0%, #f5f3ef 100%);
                border-left: 4px solid #c9c3b8;
                padding: 16px 20px;
                margin: 15px 0;
                border-radius: 0 6px 6px 0;
                transition: all 0.3s ease;
            }}
            .info-box:hover {{
                border-left-color: #a9a299;
                box-shadow: 0 2px 10px rgba(0,0,0,0.04);
            }}
            .highlight {{
                background-color: #f5f3ef;
                padding: 3px 8px;
                border-radius: 4px;
                font-weight: 600;
            }}
            a {{
                color: #7a7568;
                text-decoration: none;
                border-bottom: 1px dashed #c9c3b8;
                transition: all 0.2s ease;
            }}
            a:hover {{
                color: #4a4a4a;
                border-bottom-color: #7a7568;
            }}
            .badge {{
                display: inline-block;
                padding: 4px 10px;
                background-color: #ebe8e3;
                color: #666666;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 500;
            }}
            .footer {{
                text-align: center;
                padding: 25px;
                margin-top: 40px;
                color: #999999;
                font-size: 0.85rem;
                border-top: 1px solid #e8e4df;
            }}
            /* Animación suave para carga de página */
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .section {{
                animation: fadeIn 0.5s ease-out;
            }}
        </style>
    </head>
    <body>
        <div class="container">
        <h1>📋 Resumen del Proyecto: {nombre_proyecto}</h1>
        <p style="color: #888888;">Datos del Proyecto y Resultados</p>
        
        <div class="section">
            <h2>📋 PROYECTO</h2>
            <p>{project_data.get('proyecto', 'N/A')}</p>
            
            <h2>👨‍💻 DISEÑO</h2>
            <p>{project_data.get('diseno', 'N/A')}</p>
        </div>
        
        <hr>
        
        <div class="section">
            <h2>1. Condiciones de Operación</h2>
            
            <h3>Parámetros Principales</h3>
            <table>
                <thead>
                    <tr>
                        <th>Parámetro</th>
                        <th>Dato</th>
                        <th>Unidad</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Caudal de Diseño</td>
                        <td>{fmt(project_data.get('caudal_diseno_lps', 'N/A'))}</td>
                        <td>L/s</td>
                    </tr>
                    <tr>
                        <td>Elevación del Sitio</td>
                        <td>{fmt(project_data.get('elevacion_sitio', 'N/A'))}</td>
                        <td>m</td>
                    </tr>
                    <tr>
                        <td>Altura de Succión</td>
                        <td>{fmt(project_data.get('altura_succion', 'N/A'))}</td>
                        <td>m</td>
                    </tr>
                    <tr>
                        <td>Altura de Descarga</td>
                        <td>{fmt(project_data.get('altura_descarga', 'N/A'))}</td>
                        <td>m</td>
                    </tr>
                    <tr>
                        <td>Número de Bombas</td>
                        <td>{project_data.get('num_bombas_paralelo', 'N/A')}</td>
                        <td>-</td>
                    </tr>
                    <tr>
                        <td>Bomba Inundada</td>
                        <td>{"Sí" if project_data.get('bomba_inundada', False) else "No"}</td>
                        <td>-</td>
                    </tr>
                </tbody>
            </table>
            
            <h3>Condiciones del Fluido</h3>
            <table>
                <thead>
                    <tr>
                        <th>Condición</th>
                        <th>Dato</th>
                        <th>Unidad</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Temperatura</td>
                        <td>{fmt(project_data.get('temperatura', 'N/A'))}</td>
                        <td>°C</td>
                    </tr>
                    <tr>
                        <td>Densidad</td>
                        <td>{fmt(project_data.get('densidad_liquido', 'N/A'))}</td>
                        <td>g/cm³</td>
                    </tr>
                    <tr>
                        <td>Presión de Vapor</td>
                        <td>{fmt(project_data.get('presion_vapor_calculada', 'N/A'))}</td>
                        <td>m.c.a.</td>
                    </tr>
                    <tr>
                        <td>Presión Barométrica</td>
                        <td>{fmt(project_data.get('presion_barometrica_calculada', 'N/A'))}</td>
                        <td>m.c.a.</td>
                    </tr>
                </tbody>
            </table>
            
            <h3>Método de Cálculo de Pérdidas</h3>
    """
    
    # Agregar información del método
    metodo_calc = project_data.get('metodo_calculo', 'Hazen-Williams')
    html += f"""
            <div class="info-box">
                <p><strong>Método utilizado:</strong> <span class="highlight">{metodo_calc}</span></p>
    """
    
    # Si es Darcy-Weisbach, mostrar parámetros adicionales
    if metodo_calc == 'Darcy-Weisbach':
        det_suc = project_data.get('detalles_darcy_succion', {})
        det_imp = project_data.get('detalles_darcy_impulsion', {})
        
        if det_suc:
            html += f"""
                <p><strong>📘 Succión:</strong> Reynolds = {fmt(det_suc.get('Re', 0), 0)}, 
                Factor f = {fmt(det_suc.get('f', 0), 6)}, 
                Régimen = {det_suc.get('regimen', 'N/A')}</p>
            """
        
        if det_imp:
            html += f"""
                <p><strong>📕 Impulsión:</strong> Reynolds = {fmt(det_imp.get('Re', 0), 0)}, 
                Factor f = {fmt(det_imp.get('f', 0), 6)}, 
                Régimen = {det_imp.get('regimen', 'N/A')}</p>
            """
    
    html += """
            </div>
        </div>
        
        <hr>
    """
    
    # 2. Tubería y Accesorios de Succión
    if 'succion' in project_data:
        succion = project_data['succion']
        html += f"""
        <div class="section">
            <h2>2. Tubería y Accesorios de Succión</h2>
            
            <h3>Resultados Hidráulicos</h3>
            <table>
                <thead>
                    <tr>
                        <th>Parámetro</th>
                        <th>Valor</th>
                        <th>Unidad</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Velocidad</td>
                        <td>{fmt(succion.get('velocidad', 'N/A'))}</td>
                        <td>m/s</td>
                    </tr>
                    <tr>
                        <td>Pérdida Primaria</td>
                        <td>{fmt(succion.get('perdida_primaria', 'N/A'))}</td>
                        <td>m</td>
                    </tr>
                    <tr>
                        <td>Pérdida Secundaria</td>
                        <td>{fmt(succion.get('perdida_secundaria', 'N/A'))}</td>
                        <td>m</td>
                    </tr>
                    <tr>
                        <td>Longitud Equivalente Accesorios</td>
                        <td>{fmt(succion.get('long_equiv_accesorios', 'N/A'))}</td>
                        <td>m</td>
                    </tr>
                    <tr>
                        <td>Pérdida Total</td>
                        <td>{fmt(succion.get('perdida_total', 'N/A'))}</td>
                        <td>m</td>
                    </tr>
                    <tr>
                        <td>Altura Dinámica</td>
                        <td>{fmt(succion.get('altura_dinamica', 'N/A'))}</td>
                        <td>m</td>
                    </tr>
                </tbody>
            </table>
            
            {generar_tabla_accesorios_html(project_data.get('accesorios_succion', []), "Accesorios de Succión")}
        </div>
        
        <hr>
        """
    
    # 3. Tubería y Accesorios de Impulsión
    if 'impulsion' in project_data:
        impulsion = project_data['impulsion']
        html += f"""
        <div class="section">
            <h2>3. Tubería y Accesorios de Impulsión</h2>
            
            <h3>Resultados Hidráulicos</h3>
            <table>
                <thead>
                    <tr>
                        <th>Parámetro</th>
                        <th>Valor</th>
                        <th>Unidad</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Velocidad</td>
                        <td>{fmt(impulsion.get('velocidad', 'N/A'))}</td>
                        <td>m/s</td>
                    </tr>
                    <tr>
                        <td>Pérdida Primaria</td>
                        <td>{fmt(impulsion.get('perdida_primaria', 'N/A'))}</td>
                        <td>m</td>
                    </tr>
                    <tr>
                        <td>Pérdida Secundaria</td>
                        <td>{fmt(impulsion.get('perdida_secundaria', 'N/A'))}</td>
                        <td>m</td>
                    </tr>
                    <tr>
                        <td>Longitud Equivalente Accesorios</td>
                        <td>{fmt(impulsion.get('long_equiv_accesorios', 'N/A'))}</td>
                        <td>m</td>
                    </tr>
                    <tr>
                        <td>Pérdida Total</td>
                        <td>{fmt(impulsion.get('perdida_total', 'N/A'))}</td>
                        <td>m</td>
                    </tr>
                    <tr>
                        <td>Altura Dinámica</td>
                        <td>{fmt(impulsion.get('altura_dinamica', 'N/A'))}</td>
                        <td>m</td>
                    </tr>
                </tbody>
            </table>
            
            {generar_tabla_accesorios_html(project_data.get('accesorios_impulsion', []), "Accesorios de Impulsión")}
        </div>
        
        <hr>
        """
    
    # 4. Ajuste de Curvas Características (3 puntos)
    if 'curva_inputs' in project_data:
        curva_inputs = project_data['curva_inputs']
        bomba_data = curva_inputs.get('bomba', [])
        rendimiento_data = curva_inputs.get('rendimiento', [])
        potencia_data = curva_inputs.get('potencia', [])
        npsh_data = curva_inputs.get('npsh', [])
        
        # Obtener datos del sistema
        sistema_data = []
        if 'curvas_texto' in project_data and 'sistema' in project_data['curvas_texto']:
            sistema_texto = project_data['curvas_texto']['sistema']
            for linea in sistema_texto.split('\n'):
                if linea.strip():
                    partes = linea.strip().split()
                    if len(partes) >= 2:
                        try:
                            sistema_data.append([float(partes[0]), float(partes[1])])
                        except:
                            pass
        
        max_rows = max(len(bomba_data), len(rendimiento_data), len(potencia_data), len(npsh_data), len(sistema_data))
        
        html += """
        <div class="section">
            <h2>4. Ajuste de Curvas Características (3 puntos)</h2>
            <table>
                <thead>
                    <tr style="background-color: #3498db;">
                        <th>Curva Bomba (H-Q)</th>
                        <th>Curva Rendimiento (η-Q)</th>
                        <th>Curva Potencia (PBHP-Q)</th>
                        <th>Curva NPSH (NPSHR-Q)</th>
                        <th>Curva del Sistema (H-Q)</th>
                    </tr>
                    <tr style="background-color: #5dade2;">
                        <th>Q (L/s) | H (m)</th>
                        <th>Q (L/s) | η (%)</th>
                        <th>Q (L/s) | P (HP)</th>
                        <th>Q (L/s) | NPSH (m)</th>
                        <th>Q (L/s) | H (m)</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i in range(max_rows):
            html += "<tr>"
            
            # Curva Bomba
            if i < len(bomba_data):
                html += f'<td style="text-align: center;">{bomba_data[i][0]:.2f} | {bomba_data[i][1]:.2f}</td>'
            else:
                html += '<td style="text-align: center;">-</td>'
            
            # Curva Rendimiento
            if i < len(rendimiento_data):
                html += f'<td style="text-align: center;">{rendimiento_data[i][0]:.2f} | {rendimiento_data[i][1]:.2f}</td>'
            else:
                html += '<td style="text-align: center;">-</td>'
            
            # Curva Potencia
            if i < len(potencia_data):
                html += f'<td style="text-align: center;">{potencia_data[i][0]:.2f} | {potencia_data[i][1]:.2f}</td>'
            else:
                html += '<td style="text-align: center;">-</td>'
            
            # Curva NPSH
            if i < len(npsh_data):
                html += f'<td style="text-align: center;">{npsh_data[i][0]:.2f} | {npsh_data[i][1]:.2f}</td>'
            else:
                html += '<td style="text-align: center;">-</td>'
            
            # Curva del Sistema
            if i < len(sistema_data):
                html += f'<td style="text-align: center;">{sistema_data[i][0]:.2f} | {sistema_data[i][1]:.2f}</td>'
            else:
                html += '<td style="text-align: center;">-</td>'
            
            html += "</tr>"
        
        html += """
                </tbody>
            </table>
        </div>
        
        <hr>
        """
    
    # 5. Resultados de Cálculos Hidráulicos
    html += """
    <div class="section">
        <h2>5. Resultados de Cálculos Hidráulicos</h2>
    """
    
    # Datos de NPSH
    if 'npsh' in project_data:
        npsh = project_data['npsh']
        html += f"""
        <h3>Datos de NPSH</h3>
        <table>
            <thead>
                <tr>
                    <th>Parámetro</th>
                    <th>Valor</th>
                    <th>Unidad</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>NPSH Disponible</td>
                    <td>{fmt(npsh.get('disponible', 'N/A'))}</td>
                    <td>m.c.a.</td>
                </tr>
                <tr>
                    <td>NPSH Requerido</td>
                    <td>{fmt(npsh.get('requerido', 'N/A'))}</td>
                    <td>m.c.a.</td>
                </tr>
                <tr>
                    <td>Margen NPSH</td>
                    <td>{fmt(npsh.get('margen', 'N/A'))}</td>
                    <td>m.c.a.</td>
                </tr>
            </tbody>
        </table>
        """
    
    # Motor de la Bomba
    if 'motor_bomba' in project_data:
        motor_bomba = project_data['motor_bomba']
        eficiencia = motor_bomba.get('motor_seleccionado', {}).get('eficiencia_porcentaje', 'N/A')
        
        html += f"""
        <h3>Motor de la Bomba</h3>
        <table>
            <thead>
                <tr>
                    <th>Parámetro</th>
                    <th>Valor</th>
                    <th>Unidad</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Eficiencia de la bomba</td>
                    <td>{fmt(eficiencia)}</td>
                    <td>%</td>
                </tr>
                <tr>
                    <td>Factor de seguridad</td>
                    <td>{fmt(motor_bomba.get('factor_seguridad', 'N/A'))}</td>
                    <td>-</td>
                </tr>
                <tr>
                    <td>Potencia Hidráulica</td>
                    <td>{fmt(motor_bomba.get('potencia_hidraulica_kw', 'N/A'))} kW ({fmt(motor_bomba.get('potencia_hidraulica_hp', 'N/A'))} HP)</td>
                    <td>kW/HP</td>
                </tr>
                <tr>
                    <td>Potencia del Motor</td>
                    <td>{fmt(motor_bomba.get('potencia_motor_final_kw', 'N/A'))} kW ({fmt(motor_bomba.get('potencia_motor_final_hp', 'N/A'))} HP)</td>
                    <td>kW/HP</td>
                </tr>
            </tbody>
        </table>
        """
    
    # Motor Estándar Seleccionado
    if 'motor_bomba' in project_data and 'motor_seleccionado' in project_data['motor_bomba']:
        motor_sel = project_data['motor_bomba']['motor_seleccionado']
        html += f"""
        <h3>🔧 Motor Estándar Seleccionado</h3>
        <table>
            <thead>
                <tr>
                    <th>Parámetro</th>
                    <th>Valor</th>
                    <th>Unidad</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>ID</td>
                    <td>{motor_sel.get('id', 'N/A')}</td>
                    <td>-</td>
                </tr>
                <tr>
                    <td>Potencia</td>
                    <td>{motor_sel.get('potencia_hp', 'N/A')} HP ({motor_sel.get('potencia_kw', 'N/A')} kW)</td>
                    <td>HP/kW</td>
                </tr>
                <tr>
                    <td>RPM</td>
                    <td>{motor_sel.get('rpm_estandar', 'N/A')}</td>
                    <td>rpm</td>
                </tr>
                <tr>
                    <td>Tensión</td>
                    <td>{motor_sel.get('tension', 'N/A')}</td>
                    <td>V</td>
                </tr>
                <tr>
                    <td>Eficiencia</td>
                    <td>{fmt(motor_sel.get('eficiencia_porcentaje', 'N/A'))}</td>
                    <td>%</td>
                </tr>
                <tr>
                    <td>Factor de Potencia</td>
                    <td>{fmt(motor_sel.get('factor_potencia', 'N/A'))}</td>
                    <td>-</td>
                </tr>
            </tbody>
        </table>
        """
    
    # Resumen del Sistema
    if 'resumen' in project_data:
        resumen = project_data['resumen']
        html += f"""
        <h3>📊 Resumen del Sistema</h3>
        <table>
            <thead>
                <tr>
                    <th>Parámetro</th>
                    <th>Valor</th>
                    <th>Unidad</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Altura Estática Total</td>
                    <td>{fmt(resumen.get('altura_estatica_total', 'N/A'))}</td>
                    <td>m</td>
                </tr>
                <tr>
                    <td>Pérdidas Totales</td>
                    <td>{fmt(resumen.get('perdidas_totales', 'N/A'))}</td>
                    <td>m</td>
                </tr>
                <tr>
                    <td>🎯 Altura Dinámica Total (ADT)</td>
                    <td>{fmt(resumen.get('altura_dinamica_total', 'N/A'))}</td>
                    <td>m</td>
                </tr>
                <tr>
                    <td>Caudal de Diseño</td>
                    <td>{fmt(resumen.get('caudal_diseno', 'N/A'))}</td>
                    <td>L/s</td>
                </tr>
                <tr>
                    <td>Caudal de Diseño</td>
                    <td>{fmt(resumen.get('caudal_diseno_m3h', 'N/A'))}</td>
                    <td>m³/h</td>
                </tr>
                <tr>
                    <td>Número de Bombas</td>
                    <td>{resumen.get('num_bombas', 'N/A')}</td>
                    <td>-</td>
                </tr>
            </tbody>
        </table>
        """
    
    # Punto de Operación
    if 'punto_operacion' in project_data:
        punto_op = project_data['punto_operacion']
        html += f"""
        <h3>🎯 Punto de Operación</h3>
        <table>
            <thead>
                <tr>
                    <th>Parámetro</th>
                    <th>Valor</th>
                    <th>Unidad</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Caudal</td>
                    <td>{fmt(punto_op.get('caudal', 'N/A'))}</td>
                    <td>L/s</td>
                </tr>
                <tr>
                    <td>Altura</td>
                    <td>{fmt(punto_op.get('altura', 'N/A'))}</td>
                    <td>m</td>
                </tr>
                <tr>
                    <td>Eficiencia</td>
                    <td>{fmt(punto_op.get('eficiencia', 'N/A'))}</td>
                    <td>%</td>
                </tr>
                <tr>
                    <td>Potencia</td>
                    <td>{fmt(punto_op.get('potencia', 'N/A'))}</td>
                    <td>HP</td>
                </tr>
            </tbody>
        </table>
        """
    
    # Análisis VDF
    if 'analisis_vdf' in project_data:
        vdf = project_data['analisis_vdf']
        html += f"""
        <h3>🔄 Análisis VDF</h3>
        <table>
            <thead>
                <tr>
                    <th>Parámetro</th>
                    <th>Valor</th>
                    <th>Unidad</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Caudal Nominal VDF</td>
                    <td>{fmt(vdf.get('caudal_nominal_vdf', 'N/A'))}</td>
                    <td>L/s</td>
                </tr>
                <tr>
                    <td>Caudal de Diseño</td>
                    <td>{fmt(vdf.get('caudal_diseno_lps', 'N/A'))}</td>
                    <td>L/s</td>
                </tr>
                <tr>
                    <td>Potencia Ajustada</td>
                    <td>{fmt(vdf.get('potencia_ajustada', 'N/A'))}</td>
                    <td>kW</td>
                </tr>
                <tr>
                    <td>Eficiencia Ajustada</td>
                    <td>{fmt(vdf.get('eficiencia_ajustada', 'N/A'))}</td>
                    <td>%</td>
                </tr>
                <tr>
                    <td>RPM Porcentaje</td>
                    <td>{fmt(vdf.get('rpm_porcentaje', 'N/A'))}</td>
                    <td>%</td>
                </tr>
            </tbody>
        </table>
        """
    
    # Bomba Seleccionada
    if 'bomba_seleccionada' in project_data:
        bomba_sel = project_data['bomba_seleccionada']
        html += f"""
        <h3>🚰 Bomba Seleccionada</h3>
        <div class="info-box">
            <p><strong>Nombre:</strong> {bomba_sel.get('nombre', 'N/A')}</p>
            <p><strong>URL:</strong> <a href="{bomba_sel.get('url', '#')}" target="_blank">{bomba_sel.get('url', 'N/A')}</a></p>
            <p><strong>Descripción:</strong> {bomba_sel.get('descripcion', 'N/A')[:500]}...</p>
        </div>
        """
    
    html += """
    </div>
    <hr>
    """
    
    # 6. Gráfico de Curvas 100% RPM
    if 'punto_operacion' in project_data:
        punto_op = project_data['punto_operacion']
        
        # Obtener datos de NPSH
        npsh_op = "N/A"
        if 'curva_inputs' in project_data and 'npsh' in project_data['curva_inputs']:
            npsh_data = project_data['curva_inputs']['npsh']
            if len(npsh_data) >= 2:
                punto_npsh = npsh_data[1]
                npsh_op = f"{punto_npsh[1]:.2f}"
        
        html += f"""
        <div class="section">
            <h2>6. Gráfico de Curvas 100% RPM</h2>
            <h3>Punto de Operación a 100% RPM</h3>
            <table>
                <thead>
                    <tr>
                        <th>Curva del Sistema y Curva de la Bomba (H-Q)</th>
                        <th>Curva de Rendimiento (η-Q)</th>
                        <th>Curva de Potencia (PBHP-Q)</th>
                        <th>Curva de NPSH Requerido (NPSHR-Q)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="text-align: center;">
                            <strong>Caudal (Q):</strong> {fmt(punto_op.get('caudal', 'N/A'))} L/s<br>
                            <strong>Altura (H):</strong> {fmt(punto_op.get('altura', 'N/A'))} m
                        </td>
                        <td style="text-align: center;">
                            <strong>Caudal (Q):</strong> {fmt(punto_op.get('caudal', 'N/A'))} L/s<br>
                            <strong>Rendimiento (η):</strong> {fmt(punto_op.get('eficiencia', 'N/A'))} %
                        </td>
                        <td style="text-align: center;">
                            <strong>Caudal (Q):</strong> {fmt(punto_op.get('caudal', 'N/A'))} L/s<br>
                            <strong>Potencia (PBHP):</strong> {fmt(punto_op.get('potencia', 'N/A'))} HP
                        </td>
                        <td style="text-align: center;">
                            <strong>Caudal (Q):</strong> {fmt(punto_op.get('caudal', 'N/A'))} L/s<br>
                            <strong>NPSHreq:</strong> {npsh_op} m
                        </td>
                    </tr>
                </tbody>
            </table>
        """
        
        # Porcentaje de RPM para curvas VDF
        if 'vfd' in project_data:
            vfd = project_data['vfd']
            html += f"""
            <p><strong>Porcentaje de RPM para curvas VFD:</strong> {vfd.get('rpm_percentage', 'N/A')}%</p>
            """
        
        html += """
        </div>
        <hr>
        """
    
    # 7. Gráfico de Curvas VDF
    if 'vfd' in project_data and 'analisis_vdf' in project_data:
        vfd = project_data['vfd']
        analisis_vdf = project_data['analisis_vdf']
        rpm_percentage = vfd.get('rpm_percentage', 'N/A')
        
        # Datos del punto de operación VDF
        caudal_vfd = analisis_vdf.get('caudal_diseno_lps', 'N/A')
        altura_vfd = analisis_vdf.get('interseccion_vfd', ['N/A', 'N/A'])
        eficiencia_vfd = analisis_vdf.get('eficiencia_operacion', 'N/A')
        potencia_vfd = analisis_vdf.get('potencia_ajustada', 'N/A')
        
        # Formatear altura VDF
        if isinstance(altura_vfd, list) and len(altura_vfd) > 1 and altura_vfd[1] != 'N/A':
            altura_vfd_str = fmt(altura_vfd[1])
        else:
            altura_vfd_str = "N/A"
        
        # Obtener datos de NPSH VDF
        npsh_vfd = "N/A"
        if 'curvas_texto' in project_data and 'npsh' in project_data['curvas_texto']:
            npsh_texto = project_data['curvas_texto']['npsh']
            puntos_npsh = []
            for linea in npsh_texto.split('\n'):
                if linea.strip():
                    partes = linea.strip().split('\t')
                    if len(partes) >= 2:
                        try:
                            puntos_npsh.append([float(partes[0]), float(partes[1])])
                        except:
                            pass
            
            if len(puntos_npsh) >= 2:
                punto_npsh_vfd = puntos_npsh[1]
                npsh_vfd = f"{punto_npsh_vfd[1]:.2f}"
        
        html += f"""
        <div class="section">
            <h2>7. Gráfico de Curvas VDF</h2>
            <p><strong>Porcentaje de RPM para curvas VFD:</strong> {rpm_percentage}%</p>
            
            <h3>Punto de Operación VDF</h3>
            <table>
                <thead>
                    <tr>
                        <th>Curva del Sistema y Curva de la Bomba ({rpm_percentage}% RPM)</th>
                        <th>Curva de Rendimiento ({rpm_percentage}% RPM)</th>
                        <th>Curva de Potencia ({rpm_percentage}% RPM)</th>
                        <th>Curva de NPSH Requerido ({rpm_percentage}% RPM)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="text-align: center;">
                            <strong>Caudal (Q):</strong> {fmt(caudal_vfd)} L/s<br>
                            <strong>Altura (H):</strong> {altura_vfd_str} m
                        </td>
                        <td style="text-align: center;">
                            <strong>Caudal (Q):</strong> {fmt(caudal_vfd)} L/s<br>
                            <strong>Rendimiento (η):</strong> {fmt(eficiencia_vfd)} %
                        </td>
                        <td style="text-align: center;">
                            <strong>Caudal (Q):</strong> {fmt(caudal_vfd)} L/s<br>
                            <strong>Potencia (PBHP):</strong> {fmt(potencia_vfd)} HP
                        </td>
                        <td style="text-align: center;">
                            <strong>Caudal (Q):</strong> {fmt(caudal_vfd)} L/s<br>
                            <strong>NPSHreq:</strong> {npsh_vfd} m
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        <hr>
        """
    
    # 8. Tablas
    tablas_graficos = project_data.get('tablas_graficos', {})
    if tablas_graficos:
        html += """
        <div class="section">
            <h2>8. Tablas</h2>
        """
        
        # Función helper para generar tabla horizontal HTML
        def generar_tabla_horizontal_html_export(df_data_list, titulo, config):
            tabla_html = f"""
            <h3>{titulo}</h3>
            <p><strong>Q min:</strong> {config.get('q_min', 0.0)} L/s | 
               <strong>Q max:</strong> {config.get('q_max', 70.0)} L/s | 
               <strong>Paso del caudal:</strong> {config.get('paso_caudal', 5.0)} L/s</p>
            <table>
            <thead>
                <tr>
                    <th>Curva Bomba (H-Q)</th>
                    <th>Curva Rendimiento (η-Q)</th>
                    <th>Curva Potencia (PBHP-Q)</th>
                    <th>Curva NPSH (NPSHR-Q)</th>
                    <th>Curva del Sistema (H-Q)</th>
                </tr>
                <tr style="background-color: #5dade2;">
                    <th>Q (L/s) | H (m)</th>
                    <th>Q (L/s) | η (%)</th>
                    <th>Q (L/s) | P (HP)</th>
                    <th>Q (L/s) | NPSH (m)</th>
                    <th>Q (L/s) | H (m)</th>
                </tr>
            </thead>
            <tbody>
            """
            
            # Determinar el número máximo de filas - manejar diferentes estructuras de datos
            max_rows = 0
            for df_info in df_data_list:
                if df_info:
                    if 'data' in df_info:
                        max_rows = max(max_rows, len(df_info['data']))
                    elif isinstance(df_info, dict) and 'columns' in df_info:
                        # Es un DataFrame serializado con columns e index
                        if 'data' in df_info:
                            max_rows = max(max_rows, len(df_info['data']))
            
            if max_rows == 0:
                tabla_html += '<tr><td colspan="5" style="text-align: center;">No hay datos disponibles</td></tr>'
            else:
                for i in range(max_rows):
                    tabla_html += "<tr>"
                    
                    for df_info in df_data_list:
                        if df_info and 'data' in df_info and i < len(df_info['data']):
                            row = df_info['data'][i]
                            if isinstance(row, list) and len(row) >= 2:
                                try:
                                    tabla_html += f'<td style="text-align: center;">{float(row[0]):.2f} | {float(row[1]):.2f}</td>'
                                except:
                                    tabla_html += '<td style="text-align: center;">-</td>'
                            elif isinstance(row, dict):
                                # Si es un diccionario, intentar obtener los valores por índice
                                try:
                                    values = list(row.values())
                                    if len(values) >= 2:
                                        tabla_html += f'<td style="text-align: center;">{float(values[0]):.2f} | {float(values[1]):.2f}</td>'
                                    else:
                                        tabla_html += '<td style="text-align: center;">-</td>'
                                except:
                                    tabla_html += '<td style="text-align: center;">-</td>'
                            else:
                                tabla_html += '<td style="text-align: center;">-</td>'
                        else:
                            tabla_html += '<td style="text-align: center;">-</td>'
                    
                    tabla_html += "</tr>"
            
            tabla_html += """
            </tbody>
            </table>
            """
            return tabla_html
        
        # Tablas 100% RPM
        tablas_100 = tablas_graficos.get('tablas_100_rpm', {})
        if tablas_100:
            config_100 = tablas_100.get('configuracion', {})
            df_list_100 = [
                tablas_100.get('df_bomba_100'),
                tablas_100.get('df_rendimiento_100'),
                tablas_100.get('df_potencia_100'),
                tablas_100.get('df_npsh_100'),
                tablas_100.get('df_sistema_100')
            ]
            
            config_dict_100 = {
                'q_min': config_100.get('q_min_100', 0.0),
                'q_max': config_100.get('q_max_100', 70.0),
                'paso_caudal': config_100.get('paso_caudal_100', 5.0)
            }
            
            html += generar_tabla_horizontal_html_export(
                df_list_100,
                "📈 Tablas de Gráficos a 100% RPM",
                config_dict_100
            )
            
            if 'nota' in tablas_100:
                html += f"<p><em>Nota: {tablas_100['nota']}</em></p>"
        
        # Tablas VFD
        tablas_vfd = tablas_graficos.get('tablas_vfd_rpm', {})
        if tablas_vfd:
            config_vfd = tablas_vfd.get('configuracion', {})
            rpm_pct = config_vfd.get('rpm_percentage', 75.0)
            
            df_list_vfd = [
                tablas_vfd.get('df_bomba_vfd'),
                tablas_vfd.get('df_rendimiento_vfd'),
                tablas_vfd.get('df_potencia_vfd'),
                tablas_vfd.get('df_npsh_vfd'),
                tablas_vfd.get('df_sistema_vfd')
            ]
            
            config_dict_vfd = {
                'q_min': config_vfd.get('q_min_vdf', 0.0),
                'q_max': config_vfd.get('q_max_vdf', 70.0),
                'paso_caudal': config_vfd.get('paso_caudal_vfd', 5.0)
            }
            
            html += generar_tabla_horizontal_html_export(
                df_list_vfd,
                f"📈 Tablas de Gráficos VDF a {rpm_pct}% RPM",
                config_dict_vfd
            )
            
            if 'nota' in tablas_vfd:
                html += f"<p><em>Nota: {tablas_vfd['nota']}</em></p>"
        
        html += """
        </div>
        <hr>
        """
    
    # Cerrar el HTML
    html += """
        <div class="section">
            <p style="text-align: center; color: #7f8c8d; margin-top: 40px;">
                <em>Reporte generado automáticamente por el Sistema de Diseño de Bombeo</em>
            </p>
        </div>
        </div>
    </body>
    </html>
    """
    
    return html
