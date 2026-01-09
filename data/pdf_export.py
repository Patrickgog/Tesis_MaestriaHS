# Módulo para la exportación de datos a formato PDF

import io
from typing import Dict, Any, List
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether, LongTable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend sin interfaz gráfica


def create_pdf_report(
    session_state: Dict[str, Any],
    config: Dict[str, Any]
) -> io.BytesIO:
    """
    Genera un reporte PDF completo basado en la configuración proporcionada
    
    Args:
        session_state: Estado de la sesión con todos los datos
        config: Configuración del PDF con las siguientes claves:
            - calidad: 'Alta', 'Media', 'Baja'
            - orientacion: 'Vertical', 'Horizontal'
            - incluir_portada: bool
            - incluir_indice: bool
            - secciones: dict con flags de qué secciones incluir
    
    Returns:
        BytesIO con el PDF generado
    """
    buffer = io.BytesIO()
    
    # Configurar tamaño de página y orientación
    if config.get('orientacion') == 'Horizontal':
        pagesize = landscape(letter)
    else:
        pagesize = letter
    
    # Configurar calidad (DPI para imágenes)
    dpi_map = {'Alta': 300, 'Media': 150, 'Baja': 72}
    dpi = dpi_map.get(config.get('calidad', 'Media'), 150)
    
    # Crear documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesize,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch
    )
    
    # Contenedor de elementos
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2e5c8a'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    # Portada
    if config.get('incluir_portada', True):
        story.extend(create_portada(session_state, styles, title_style))
        story.append(PageBreak())
    
    # Secciones del contenido
    secciones = config.get('secciones', {})
    
    if secciones.get('condiciones', True):
        story.extend(create_seccion_condiciones(session_state, heading1_style, heading2_style, styles))
        story.append(Spacer(1, 0.2*inch))
    
    if secciones.get('succion', True):
        story.extend(create_seccion_succion(session_state, heading1_style, heading2_style, styles))
        story.append(Spacer(1, 0.2*inch))
    
    if secciones.get('impulsion', True):
        story.extend(create_seccion_impulsion(session_state, heading1_style, heading2_style, styles))
        story.append(Spacer(1, 0.2*inch))
    
    if secciones.get('curvas', True):
        story.extend(create_seccion_curvas(session_state, heading1_style, heading2_style, styles))
        story.append(Spacer(1, 0.2*inch))
    
    if secciones.get('diagrama', True):
        story.extend(create_seccion_diagrama(session_state, heading1_style, heading2_style, styles, dpi))
        story.append(Spacer(1, 0.2*inch))
    
    if secciones.get('npsh', True):
        story.extend(create_seccion_resultados(session_state, heading1_style, heading2_style, styles))
        story.append(Spacer(1, 0.2*inch))
    
    if secciones.get('graficos_100', True):
        story.extend(create_seccion_graficos_100(session_state, heading1_style, heading2_style, styles, dpi))
        story.append(Spacer(1, 0.3*inch))
    
    if secciones.get('graficos_vfd', True):
        story.extend(create_seccion_graficos_vfd(session_state, heading1_style, heading2_style, styles, dpi))
        story.append(Spacer(1, 0.3*inch))
    
    if secciones.get('tablas', True):
        story.extend(create_seccion_tablas(session_state, heading1_style, heading2_style, styles))
        story.append(Spacer(1, 0.3*inch))
    
    if secciones.get('transientes', False):
        story.extend(create_seccion_transientes(session_state, heading1_style, heading2_style, styles, dpi))
        story.append(Spacer(1, 0.3*inch))
    
    # Índice al final
    if config.get('incluir_indice', True):
        story.append(PageBreak())
        story.extend(create_indice(config.get('secciones', {}), heading1_style, styles))
    
    # Generar PDF
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    
    buffer.seek(0)
    return buffer


def create_portada(session_state: Dict[str, Any], styles, title_style) -> List:
    """Crea la portada del PDF"""
    elements = []
    
    # Título principal
    proyecto = session_state.get('proyecto', 'Proyecto de Bombeo')
    elements.append(Spacer(1, 2*inch))
    elements.append(Paragraph(f"<b>REPORTE TÉCNICO</b>", title_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(f"<b>{proyecto}</b>", title_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Información del proyecto
    diseno = session_state.get('diseno', 'N/A')
    fecha = datetime.now().strftime('%d/%m/%Y')
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=6
    )
    
    elements.append(Paragraph(f"<b>Diseño:</b> {diseno}", info_style))
    elements.append(Paragraph(f"<b>Fecha:</b> {fecha}", info_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Parámetros principales
    caudal = session_state.get('caudal_lps', 0)
    adt = session_state.get('adt_total', 0)
    potencia = session_state.get('potencia_motor_final_hp', 0)
    
    elements.append(Paragraph(f"<b>Caudal de Diseño:</b> {caudal:.2f} L/s", info_style))
    elements.append(Paragraph(f"<b>ADT Total:</b> {adt:.2f} m", info_style))
    elements.append(Paragraph(f"<b>Potencia Motor:</b> {potencia:.2f} HP", info_style))
    
    return elements


def create_indice(secciones: Dict[str, bool], heading1_style, styles) -> List:
    """Crea el índice del documento"""
    elements = []
    
    elements.append(Paragraph("<b>ÍNDICE</b>", heading1_style))
    elements.append(Spacer(1, 0.2*inch))
    
    indice_items = []
    page_num = 3  # Asumiendo portada e índice
    
    if secciones.get('condiciones', True):
        indice_items.append(f"1. Condiciones de Operación ........................... {page_num}")
    if secciones.get('succion', True):
        indice_items.append(f"2. Tubería y Accesorios de Succión ................... {page_num}")
    if secciones.get('impulsion', True):
        indice_items.append(f"3. Tubería y Accesorios de Impulsión ................. {page_num}")
    if secciones.get('curvas', True):
        indice_items.append(f"4. Ajuste de Curvas Características .................. {page_num}")
    if secciones.get('diagrama', True):
        indice_items.append(f"5. Diagrama Esquemático del Sistema .................. {page_num}")
    if secciones.get('npsh', True):
        indice_items.append(f"6. Resultados de Cálculos Hidráulicos ................ {page_num}")
    if secciones.get('graficos_100', True):
        indice_items.append(f"7. Gráficos de Curvas 100% RPM ....................... {page_num + 1}")
    if secciones.get('graficos_vfd', True):
        indice_items.append(f"8. Gráficos de Curvas VFD ............................ {page_num + 2}")
    if secciones.get('tablas', True):
        indice_items.append(f"9. Tablas de Datos ................................... {page_num + 3}")
    if secciones.get('transientes', False):
        indice_items.append(f"10. Análisis de Transientes .......................... {page_num + 4}")
    
    for item in indice_items:
        elements.append(Paragraph(item, styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
    
    return elements


def create_seccion_condiciones(session_state: Dict[str, Any], h1_style, h2_style, styles) -> List:
    """Crea la sección de Condiciones de Operación"""
    elements = []
    
    elements.append(Paragraph("1. CONDICIONES DE OPERACIÓN", h1_style))
    
    data = [
        ['Parámetro', 'Valor', 'Unidad'],
        ['Caudal de Diseño', f"{session_state.get('caudal_lps', 0):.2f}", 'L/s'],
        ['Elevación del Sitio', f"{session_state.get('elevacion_sitio', 0):.2f}", 'm.s.n.m.'],
        ['Altura de Succión', f"{session_state.get('altura_succion_input', 0):.2f}", 'm'],
        ['Altura de Descarga', f"{session_state.get('altura_descarga', 0):.2f}", 'm'],
        ['Número de Bombas', f"{session_state.get('num_bombas', 1)}", 'unidades'],
        ['Bomba Inundada', 'Sí' if session_state.get('bomba_inundada', False) else 'No', ''],
    ]
    
    table = Table(data, colWidths=[3*inch, 2*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    return elements


def create_seccion_succion(session_state: Dict[str, Any], h1_style, h2_style, styles) -> List:
    """Crea la sección de Tubería y Accesorios de Succión"""
    elements = []
    
    elements.append(Paragraph("2. TUBERÍA Y ACCESORIOS DE SUCCIÓN", h1_style))
    
    # Tabla de parámetros de tubería
    data = [
        ['Parámetro', 'Valor', 'Unidad'],
        ['Longitud', f"{session_state.get('long_succion', 0):.2f}", 'm'],
        ['Material', session_state.get('mat_succion', 'N/A'), ''],
        ['Diámetro Interno', f"{session_state.get('diam_succion_mm', 0):.2f}", 'mm'],
        ['Coeficiente C', f"{session_state.get('C_succion', 150)}", ''],
        ['Otras Pérdidas', f"{session_state.get('otras_perdidas_succion', 0):.2f}", 'm'],
        ['Velocidad', f"{session_state.get('velocidad_succion', 0):.2f}", 'm/s'],
        ['Pérdida Total', f"{session_state.get('perdida_total_succion', 0):.2f}", 'm'],
    ]
    
    table = Table(data, colWidths=[3*inch, 2*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Tabla de accesorios
    accesorios = session_state.get('accesorios_succion', [])
    if accesorios:
        titulo_acc = Paragraph("Accesorios de Succión", h2_style)
        
        acc_data = [['Tipo de Accesorio', 'Cantidad', 'Lc/D']]
        
        # Obtener longitud equivalente y pérdidas
        le_total = session_state.get('le_total_succion', 0)
        hf_secundaria = session_state.get('hf_secundaria_succion', 0)
        
        for acc in accesorios:
            lc_d = acc.get('Lc/D', acc.get('lc_d', 0))
            cantidad = acc.get('cantidad', 0)
            acc_data.append([
                acc.get('tipo', 'N/A'),
                str(cantidad),
                f"{lc_d:.2f}"
            ])
        
        # Agregar filas de totales
        acc_data.append(['LONGITUD EQUIVALENTE TOTAL', '', f"{le_total:.2f} m"])
        acc_data.append(['TOTAL PÉRDIDAS POR ACCESORIOS', '', f"{hf_secundaria:.3f} m"])
        
        acc_table = Table(acc_data, colWidths=[3*inch, 1.5*inch, 2*inch])
        acc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -3), colors.lightblue),
            ('BACKGROUND', (0, -2), (-1, -2), colors.HexColor('#90EE90')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFD700')),
            ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        # Usar KeepTogether para evitar división entre páginas
        elements.append(KeepTogether([titulo_acc, acc_table]))
    
    return elements


def create_seccion_impulsion(session_state: Dict[str, Any], h1_style, h2_style, styles) -> List:
    """Crea la sección de Tubería y Accesorios de Impulsión"""
    elements = []
    
    elements.append(Paragraph("3. TUBERÍA Y ACCESORIOS DE IMPULSIÓN", h1_style))
    
    # Tabla de parámetros de tubería
    data = [
        ['Parámetro', 'Valor', 'Unidad'],
        ['Longitud', f"{session_state.get('long_impulsion', 0):.2f}", 'm'],
        ['Material', session_state.get('mat_impulsion', 'N/A'), ''],
        ['Diámetro Interno', f"{session_state.get('diam_impulsion_mm', 0):.2f}", 'mm'],
        ['Coeficiente C', f"{session_state.get('C_impulsion', 150)}", ''],
        ['Otras Pérdidas', f"{session_state.get('otras_perdidas_impulsion', 0):.2f}", 'm'],
        ['Velocidad', f"{session_state.get('velocidad_impulsion', 0):.2f}", 'm/s'],
        ['Pérdida Total', f"{session_state.get('perdida_total_impulsion', 0):.2f}", 'm'],
    ]
    
    table = Table(data, colWidths=[3*inch, 2*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Tabla de accesorios
    accesorios = session_state.get('accesorios_impulsion', [])
    if accesorios:
        titulo_acc = Paragraph("Accesorios de Impulsión", h2_style)
        
        acc_data = [['Tipo de Accesorio', 'Cantidad', 'Lc/D']]
        
        # Obtener longitud equivalente y pérdidas
        le_total = session_state.get('le_total_impulsion', 0)
        hf_secundaria = session_state.get('hf_secundaria_impulsion', 0)
        
        for acc in accesorios:
            lc_d = acc.get('Lc/D', acc.get('lc_d', 0))
            cantidad = acc.get('cantidad', 0)
            acc_data.append([
                acc.get('tipo', 'N/A'),
                str(cantidad),
                f"{lc_d:.2f}"
            ])
        
        # Agregar filas de totales
        acc_data.append(['LONGITUD EQUIVALENTE TOTAL', '', f"{le_total:.2f} m"])
        acc_data.append(['TOTAL PÉRDIDAS POR ACCESORIOS', '', f"{hf_secundaria:.3f} m"])
        
        acc_table = Table(acc_data, colWidths=[3*inch, 1.5*inch, 2*inch])
        acc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -3), colors.lightblue),
            ('BACKGROUND', (0, -2), (-1, -2), colors.HexColor('#90EE90')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFD700')),
            ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        # Usar KeepTogether para evitar división entre páginas
        elements.append(KeepTogether([titulo_acc, acc_table]))
    
    return elements


def create_seccion_curvas(session_state: Dict[str, Any], h1_style, h2_style, styles) -> List:
    """Crea la sección de Ajuste de Curvas Características"""
    elements = []
    
    elements.append(Paragraph("4. AJUSTE DE CURVAS CARACTERÍSTICAS", h1_style))
    
    ajuste_tipo = session_state.get('ajuste_tipo', 'Cuadrática (2do grado)')
    elements.append(Paragraph(f"<b>Tipo de Ajuste:</b> {ajuste_tipo}", styles['Normal']))
    elements.append(Spacer(1, 0.1*inch))
    
    return elements


def create_seccion_resultados(session_state: Dict[str, Any], h1_style, h2_style, styles) -> List:
    """Crea la sección de Resultados de Cálculos Hidráulicos"""
    elements = []
    
    elements.append(Paragraph("5. RESULTADOS DE CÁLCULOS HIDRÁULICOS", h1_style))
    
    data = [
        ['Parámetro', 'Valor', 'Unidad'],
        ['ADT Total', f"{session_state.get('adt_total', 0):.2f}", 'm'],
        ['NPSH Disponible', f"{session_state.get('npshd_mca', 0):.2f}", 'm.c.a.'],
        ['Potencia Hidráulica', f"{session_state.get('potencia_hidraulica_hp', 0):.2f}", 'HP'],
        ['Potencia Motor Requerida', f"{session_state.get('potencia_motor_final_hp', 0):.2f}", 'HP'],
        ['Caudal de Operación', f"{session_state.get('caudal_operacion', 0):.2f}", 'L/s'],
        ['Altura de Operación', f"{session_state.get('altura_operacion', 0):.2f}", 'm'],
        ['Eficiencia de Operación', f"{session_state.get('eficiencia_operacion', 0):.2f}", '%'],
    ]
    
    table = Table(data, colWidths=[3*inch, 2*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    return elements


def create_seccion_graficos_100(session_state: Dict[str, Any], h1_style, h2_style, styles, dpi: int) -> List:
    """Crea la sección de Gráficos 100% RPM - 4 gráficos"""
    elements = []
    
    elements.append(Paragraph("6. GRÁFICOS DE CURVAS 100% RPM", h1_style))
    elements.append(Spacer(1, 0.2*inch))
    
    try:
        import numpy as np
        from scipy.interpolate import interp1d
        
        # Obtener DataFrames
        df_bomba = session_state.get('df_bomba_100', pd.DataFrame())
        df_sistema = session_state.get('df_sistema_100', pd.DataFrame())
        df_eff = session_state.get('df_rendimiento_100', pd.DataFrame())
        df_power = session_state.get('df_potencia_100', pd.DataFrame())
        df_npsh = session_state.get('df_npsh_100', pd.DataFrame())
        
        # Función para encontrar intersección
        def find_intersection(df1, df2, col_x='Caudal (L/s)', col_y='Altura (m)'):
            if df1.empty or df2.empty:
                return None, None
            try:
                # Interpolar ambas curvas
                f1 = interp1d(df1[col_x], df1[col_y], kind='linear', fill_value='extrapolate')
                f2 = interp1d(df2[col_x], df2[col_y], kind='linear', fill_value='extrapolate')
                
                # Buscar intersección
                x_range = np.linspace(max(df1[col_x].min(), df2[col_x].min()), 
                                     min(df1[col_x].max(), df2[col_x].max()) * 1.2, 1000)
                diff = f1(x_range) - f2(x_range)
                idx = np.argmin(np.abs(diff))
                return x_range[idx], f1(x_range[idx])
            except:
                return None, None
        
        # Calcular punto de operación (intersección)
        q_op, h_op = find_intersection(df_bomba, df_sistema)
        
        # GRÁFICO 1: Curva Bomba vs Sistema
        if not df_bomba.empty and not df_sistema.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            
            ax.plot(df_bomba['Caudal (L/s)'], df_bomba['Altura (m)'], 
                   'b-', linewidth=2, label='Curva Bomba')
            ax.plot(df_sistema['Caudal (L/s)'], df_sistema['Altura (m)'], 
                   'r-', linewidth=2, label='Curva Sistema')
            
            if q_op and h_op:
                ax.plot(q_op, h_op, 'go', markersize=10, 
                       label=f'Punto Operación ({q_op:.1f} L/s, {h_op:.1f} m)', zorder=5)
            
            ax.set_xlabel('Caudal (L/s)', fontsize=10)
            ax.set_ylabel('Altura (m)', fontsize=10)
            ax.set_title('Curva Bomba vs Sistema - 100% RPM', fontsize=12, fontweight='bold')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
            
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', dpi=dpi, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close(fig)
            
            titulo_grafico = Paragraph("Gráfico 1: Curva Bomba vs Sistema", h2_style)
            img = Image(img_buffer, width=5*inch, height=3.5*inch)
            elements.append(KeepTogether([titulo_grafico, img]))
            elements.append(Spacer(1, 0.2*inch))
        
        # GRÁFICO 2: Eficiencia
        if not df_eff.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            
            ax.plot(df_eff['Caudal (L/s)'], df_eff['Rendimiento (%)'], 
                   'g-', linewidth=2, label='Eficiencia')
            
            if q_op:
                try:
                    f_eff = interp1d(df_eff['Caudal (L/s)'], df_eff['Rendimiento (%)'], 
                                    kind='linear', fill_value='extrapolate')
                    eff_op = f_eff(q_op)
                    ax.plot(q_op, eff_op, 'ro', markersize=10, 
                           label=f'Punto Operación ({q_op:.1f} L/s, {eff_op:.1f}%)', zorder=5)
                except:
                    pass
            
            ax.set_xlabel('Caudal (L/s)', fontsize=10)
            ax.set_ylabel('Eficiencia (%)', fontsize=10)
            ax.set_title('Curva de Eficiencia - 100% RPM', fontsize=12, fontweight='bold')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
            
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', dpi=dpi, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close(fig)
            
            titulo_grafico = Paragraph("Gráfico 2: Curva de Eficiencia", h2_style)
            img = Image(img_buffer, width=5*inch, height=3.5*inch)
            elements.append(KeepTogether([titulo_grafico, img]))
            elements.append(Spacer(1, 0.2*inch))
        
        # GRÁFICO 3: Potencia
        if not df_power.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            
            # Buscar columnas de caudal y potencia (pueden tener diferentes nombres)
            col_caudal = None
            col_potencia = None
            for col in df_power.columns:
                if 'caudal' in col.lower() or 'flow' in col.lower():
                    col_caudal = col
                if 'potencia' in col.lower() or 'power' in col.lower() or 'hp' in col.lower():
                    col_potencia = col
            
            if col_caudal and col_potencia:
                ax.plot(df_power[col_caudal], df_power[col_potencia], 
                       'm-', linewidth=2, label='Potencia')
                
                if q_op:
                    try:
                        f_pow = interp1d(df_power[col_caudal], df_power[col_potencia], 
                                        kind='linear', fill_value='extrapolate')
                        pow_op = f_pow(q_op)
                        ax.plot(q_op, pow_op, 'ro', markersize=10, 
                               label=f'Punto Operación ({q_op:.1f} L/s, {pow_op:.1f})', zorder=5)
                    except:
                        pass
                
                ax.set_xlabel('Caudal (L/s)', fontsize=10)
                ax.set_ylabel('Potencia (HP/kW)', fontsize=10)
                ax.set_title('Curva de Potencia - 100% RPM', fontsize=12, fontweight='bold')
                ax.legend(fontsize=8)
                ax.grid(True, alpha=0.3)
                
                img_buffer = io.BytesIO()
                fig.savefig(img_buffer, format='png', dpi=dpi, bbox_inches='tight')
                img_buffer.seek(0)
                plt.close(fig)
                
                titulo_grafico = Paragraph("Gráfico 3: Curva de Potencia", h2_style)
                img = Image(img_buffer, width=5*inch, height=3.5*inch)
                elements.append(KeepTogether([titulo_grafico, img]))
                elements.append(Spacer(1, 0.2*inch))
        
        # GRÁFICO 4: NPSH
        if not df_npsh.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            
            # Buscar columnas de caudal y NPSH (pueden tener diferentes nombres)
            col_caudal = None
            col_npsh = None
            for col in df_npsh.columns:
                if 'caudal' in col.lower() or 'flow' in col.lower():
                    col_caudal = col
                if 'npsh' in col.lower():
                    col_npsh = col
            
            if col_caudal and col_npsh:
                ax.plot(df_npsh[col_caudal], df_npsh[col_npsh], 
                       'c-', linewidth=2, label='NPSH Requerido')
                
                npsh_disp = session_state.get('npsh_disponible', 0)
                if npsh_disp > 0:
                    ax.axhline(y=npsh_disp, color='orange', linestyle='--', linewidth=2, 
                              label=f'NPSH Disponible ({npsh_disp:.1f} m)')
                
                if q_op:
                    try:
                        f_npsh = interp1d(df_npsh[col_caudal], df_npsh[col_npsh], 
                                         kind='linear', fill_value='extrapolate')
                        npsh_op = f_npsh(q_op)
                        ax.plot(q_op, npsh_op, 'ro', markersize=10, 
                               label=f'Punto Operación ({q_op:.1f} L/s, {npsh_op:.1f} m)', zorder=5)
                    except:
                        pass
                
                ax.set_xlabel('Caudal (L/s)', fontsize=10)
                ax.set_ylabel('NPSH (m)', fontsize=10)
                ax.set_title('Curva de NPSH - 100% RPM', fontsize=12, fontweight='bold')
                ax.legend(fontsize=8)
                ax.grid(True, alpha=0.3)
                
                img_buffer = io.BytesIO()
                fig.savefig(img_buffer, format='png', dpi=dpi, bbox_inches='tight')
                img_buffer.seek(0)
                plt.close(fig)
                
                titulo_grafico = Paragraph("Gráfico 4: Curva de NPSH", h2_style)
                img = Image(img_buffer, width=5*inch, height=3.5*inch)
                elements.append(KeepTogether([titulo_grafico, img]))
                elements.append(Spacer(1, 0.2*inch))
        
    except Exception as e:
        elements.append(Paragraph(f"<i>Error generando gráficos: {str(e)}</i>", styles['Italic']))
    
    return elements


def create_seccion_graficos_vfd(session_state: Dict[str, Any], h1_style, h2_style, styles, dpi: int) -> List:
    """Crea la sección de Gráficos VFD - 4 gráficos"""
    elements = []
    
    vfd_percentage = session_state.get('vfd_speed_percentage', session_state.get('rpm_percentage', 75.0))
    
    elements.append(Paragraph(f"7. GRÁFICOS DE CURVAS VFD ({vfd_percentage:.0f}% RPM)", h1_style))
    elements.append(Spacer(1, 0.2*inch))
    
    try:
        import numpy as np
        from scipy.interpolate import interp1d
        
        # Obtener DataFrames VFD
        df_bomba_vfd = session_state.get('df_bomba_vfd', pd.DataFrame())
        df_sistema = session_state.get('df_sistema_vfd', pd.DataFrame())
        if df_sistema.empty:
            df_sistema = session_state.get('df_sistema_100', pd.DataFrame())
        df_eff_vfd = session_state.get('df_rendimiento_vfd', pd.DataFrame())
        df_power_vfd = session_state.get('df_potencia_vfd', pd.DataFrame())
        df_npsh_vfd = session_state.get('df_npsh_vfd', pd.DataFrame())
        
        # Función para encontrar intersección
        def find_intersection(df1, df2, col_x='Caudal (L/s)', col_y='Altura (m)'):
            if df1.empty or df2.empty:
                return None, None
            try:
                f1 = interp1d(df1[col_x], df1[col_y], kind='linear', fill_value='extrapolate')
                f2 = interp1d(df2[col_x], df2[col_y], kind='linear', fill_value='extrapolate')
                x_range = np.linspace(max(df1[col_x].min(), df2[col_x].min()), 
                                     min(df1[col_x].max(), df2[col_x].max()) * 1.2, 1000)
                diff = f1(x_range) - f2(x_range)
                idx = np.argmin(np.abs(diff))
                return x_range[idx], f1(x_range[idx])
            except:
                return None, None
        
        # Calcular punto de operación VFD (intersección)
        q_op_vfd, h_op_vfd = find_intersection(df_bomba_vfd, df_sistema)
        
        # GRÁFICO 1: Curva Bomba VFD vs Sistema
        if not df_bomba_vfd.empty and not df_sistema.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            
            ax.plot(df_bomba_vfd['Caudal (L/s)'], df_bomba_vfd['Altura (m)'], 
                   'b-', linewidth=2, label=f'Curva Bomba {vfd_percentage:.0f}% RPM')
            ax.plot(df_sistema['Caudal (L/s)'], df_sistema['Altura (m)'], 
                   'r-', linewidth=2, label='Curva Sistema')
            
            if q_op_vfd and h_op_vfd:
                ax.plot(q_op_vfd, h_op_vfd, 'go', markersize=10, 
                       label=f'Punto Operación ({q_op_vfd:.1f} L/s, {h_op_vfd:.1f} m)', zorder=5)
            
            ax.set_xlabel('Caudal (L/s)', fontsize=10)
            ax.set_ylabel('Altura (m)', fontsize=10)
            ax.set_title(f'Curva Bomba vs Sistema - {vfd_percentage:.0f}% RPM', fontsize=12, fontweight='bold')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
            
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', dpi=dpi, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close(fig)
            
            titulo_grafico = Paragraph(f"Gráfico 1: Curva Bomba vs Sistema VFD", h2_style)
            img = Image(img_buffer, width=5*inch, height=3.5*inch)
            elements.append(KeepTogether([titulo_grafico, img]))
            elements.append(Spacer(1, 0.2*inch))
        
        # GRÁFICO 2: Eficiencia VFD
        if not df_eff_vfd.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            
            ax.plot(df_eff_vfd['Caudal (L/s)'], df_eff_vfd['Rendimiento (%)'], 
                   'g-', linewidth=2, label='Eficiencia VFD')
            
            if q_op_vfd:
                try:
                    f_eff = interp1d(df_eff_vfd['Caudal (L/s)'], df_eff_vfd['Rendimiento (%)'], 
                                    kind='linear', fill_value='extrapolate')
                    eff_op_vfd = f_eff(q_op_vfd)
                    ax.plot(q_op_vfd, eff_op_vfd, 'ro', markersize=10, 
                           label=f'Punto Operación ({q_op_vfd:.1f} L/s, {eff_op_vfd:.1f}%)', zorder=5)
                except:
                    pass
            
            ax.set_xlabel('Caudal (L/s)', fontsize=10)
            ax.set_ylabel('Eficiencia (%)', fontsize=10)
            ax.set_title(f'Curva de Eficiencia - {vfd_percentage:.0f}% RPM', fontsize=12, fontweight='bold')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
            
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', dpi=dpi, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close(fig)
            
            titulo_grafico = Paragraph(f"Gráfico 2: Curva de Eficiencia VFD", h2_style)
            img = Image(img_buffer, width=5*inch, height=3.5*inch)
            elements.append(KeepTogether([titulo_grafico, img]))
            elements.append(Spacer(1, 0.2*inch))
        
        # GRÁFICO 3: Potencia VFD
        if not df_power_vfd.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            
            # Buscar columnas de caudal y potencia
            col_caudal = None
            col_potencia = None
            for col in df_power_vfd.columns:
                if 'caudal' in col.lower() or 'flow' in col.lower():
                    col_caudal = col
                if 'potencia' in col.lower() or 'power' in col.lower() or 'hp' in col.lower():
                    col_potencia = col
            
            if col_caudal and col_potencia:
                ax.plot(df_power_vfd[col_caudal], df_power_vfd[col_potencia], 
                       'm-', linewidth=2, label='Potencia VFD')
                
                if q_op_vfd:
                    try:
                        f_pow = interp1d(df_power_vfd[col_caudal], df_power_vfd[col_potencia], 
                                        kind='linear', fill_value='extrapolate')
                        pow_op_vfd = f_pow(q_op_vfd)
                        ax.plot(q_op_vfd, pow_op_vfd, 'ro', markersize=10, 
                               label=f'Punto Operación ({q_op_vfd:.1f} L/s, {pow_op_vfd:.1f})', zorder=5)
                    except:
                        pass
                
                ax.set_xlabel('Caudal (L/s)', fontsize=10)
                ax.set_ylabel('Potencia (HP/kW)', fontsize=10)
                ax.set_title(f'Curva de Potencia - {vfd_percentage:.0f}% RPM', fontsize=12, fontweight='bold')
                ax.legend(fontsize=8)
                ax.grid(True, alpha=0.3)
                
                img_buffer = io.BytesIO()
                fig.savefig(img_buffer, format='png', dpi=dpi, bbox_inches='tight')
                img_buffer.seek(0)
                plt.close(fig)
                
                titulo_grafico = Paragraph(f"Gráfico 3: Curva de Potencia VFD", h2_style)
                img = Image(img_buffer, width=5*inch, height=3.5*inch)
                elements.append(KeepTogether([titulo_grafico, img]))
                elements.append(Spacer(1, 0.2*inch))
        
        # GRÁFICO 4: NPSH VFD
        if not df_npsh_vfd.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            
            # Buscar columnas de caudal y NPSH
            col_caudal = None
            col_npsh = None
            for col in df_npsh_vfd.columns:
                if 'caudal' in col.lower() or 'flow' in col.lower():
                    col_caudal = col
                if 'npsh' in col.lower():
                    col_npsh = col
            
            if col_caudal and col_npsh:
                ax.plot(df_npsh_vfd[col_caudal], df_npsh_vfd[col_npsh], 
                       'c-', linewidth=2, label='NPSH Requerido VFD')
                
                npsh_disp = session_state.get('npsh_disponible', 0)
                if npsh_disp > 0:
                    ax.axhline(y=npsh_disp, color='orange', linestyle='--', linewidth=2, 
                              label=f'NPSH Disponible ({npsh_disp:.1f} m)')
                
                if q_op_vfd:
                    try:
                        f_npsh = interp1d(df_npsh_vfd[col_caudal], df_npsh_vfd[col_npsh], 
                                         kind='linear', fill_value='extrapolate')
                        npsh_op_vfd = f_npsh(q_op_vfd)
                        ax.plot(q_op_vfd, npsh_op_vfd, 'ro', markersize=10, 
                               label=f'Punto Operación ({q_op_vfd:.1f} L/s, {npsh_op_vfd:.1f} m)', zorder=5)
                    except:
                        pass
                
                ax.set_xlabel('Caudal (L/s)', fontsize=10)
                ax.set_ylabel('NPSH (m)', fontsize=10)
                ax.set_title(f'Curva de NPSH - {vfd_percentage:.0f}% RPM', fontsize=12, fontweight='bold')
                ax.legend(fontsize=8)
                ax.grid(True, alpha=0.3)
                
                img_buffer = io.BytesIO()
                fig.savefig(img_buffer, format='png', dpi=dpi, bbox_inches='tight')
                img_buffer.seek(0)
                plt.close(fig)
                
                titulo_grafico = Paragraph(f"Gráfico 4: Curva de NPSH VFD", h2_style)
                img = Image(img_buffer, width=5*inch, height=3.5*inch)
                elements.append(KeepTogether([titulo_grafico, img]))
                elements.append(Spacer(1, 0.2*inch))
        
    except Exception as e:
        elements.append(Paragraph(f"<i>Error generando gráficos VFD: {str(e)}</i>", styles['Italic']))
    
    return elements


def create_seccion_tablas(session_state: Dict[str, Any], h1_style, h2_style, styles) -> List:
    """Crea la sección de Tablas de Datos"""
    elements = []
    
    elements.append(Paragraph("8. TABLAS DE DATOS", h1_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Tabla 100% RPM
    elements.append(Paragraph("Tabla de Curvas 100% RPM", h2_style))
    df_bomba_100 = session_state.get('df_bomba_100', pd.DataFrame())
    
    if not df_bomba_100.empty:
        # Mostrar TODAS las filas usando LongTable (permite división entre páginas)
        df_display = df_bomba_100
        
        # Convertir DataFrame a lista para la tabla
        table_data = [df_display.columns.tolist()]
        for _, row in df_display.iterrows():
            table_data.append([f"{val:.2f}" if isinstance(val, (int, float)) else str(val) for val in row])
        
        # Calcular anchos de columna dinámicamente
        num_cols = len(df_display.columns)
        col_width = 6.5*inch / num_cols
        
        # Usar LongTable para permitir división entre páginas
        table = LongTable(table_data, colWidths=[col_width] * num_cols, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        elements.append(table)
        elements.append(Paragraph(f"<i>Total: {len(df_bomba_100)} filas</i>", styles['Italic']))
    else:
        elements.append(Paragraph("<i>No hay datos disponibles para la tabla 100% RPM</i>", styles['Italic']))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla VFD
    vfd_percentage = session_state.get('vfd_speed_percentage', session_state.get('rpm_percentage', 75.0))
    elements.append(Paragraph(f"Tabla de Curvas VFD ({vfd_percentage:.0f}% RPM)", h2_style))
    df_bomba_vfd = session_state.get('df_bomba_vfd', pd.DataFrame())
    
    if not df_bomba_vfd.empty:
        # Mostrar TODAS las filas usando LongTable (permite división entre páginas)
        df_display = df_bomba_vfd
        
        table_data = [df_display.columns.tolist()]
        for _, row in df_display.iterrows():
            table_data.append([f"{val:.2f}" if isinstance(val, (int, float)) else str(val) for val in row])
        
        num_cols = len(df_display.columns)
        col_width = 6.5*inch / num_cols
        
        # Usar LongTable para permitir división entre páginas
        table = LongTable(table_data, colWidths=[col_width] * num_cols, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        elements.append(table)
        elements.append(Paragraph(f"<i>Total: {len(df_bomba_vfd)} filas</i>", styles['Italic']))
    else:
        elements.append(Paragraph(f"<i>No hay datos disponibles para la tabla VFD ({vfd_percentage:.0f}% RPM)</i>", styles['Italic']))
    
    return elements


def create_seccion_diagrama(session_state: Dict[str, Any], h1_style, h2_style, styles, dpi: int) -> List:
    """Crea la sección del Diagrama Esquemático del Sistema"""
    elements = []
    
    elements.append(Paragraph("📐 Diagrama Esquemático del Sistema", h1_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Verificar si hay un diagrama guardado en session_state
    diagrama_path = session_state.get('diagrama_esquematico_path', None)
    diagrama_fig = session_state.get('diagrama_esquematico_fig', None)
    
    if diagrama_fig is not None:
        # Si hay una figura de matplotlib guardada
        try:
            # Guardar la figura en un buffer
            img_buffer = io.BytesIO()
            diagrama_fig.savefig(img_buffer, format='png', dpi=dpi, bbox_inches='tight')
            img_buffer.seek(0)
            
            # Agregar imagen al PDF
            img = Image(img_buffer, width=6*inch, height=4*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.2*inch))
            
            # Descripción
            elements.append(Paragraph("<b>Descripción del Sistema:</b>", h2_style))
            
            altura_succion = session_state.get('altura_succion_input', 0)
            altura_descarga = session_state.get('altura_descarga', 0)
            bomba_inundada = session_state.get('bomba_inundada', False)
            
            descripcion = f"""
            El diagrama muestra la configuración del sistema de bombeo con:
            <br/>• Altura de succión: {altura_succion:.2f} m
            <br/>• Altura de descarga: {altura_descarga:.2f} m
            <br/>• Tipo de instalación: {'Bomba inundada' if bomba_inundada else 'Bomba en aspiración'}
            """
            
            elements.append(Paragraph(descripcion, styles['Normal']))
            
        except Exception as e:
            elements.append(Paragraph(f"<i>Error al generar el diagrama: {str(e)}</i>", styles['Italic']))
    
    elif diagrama_path is not None:
        # Si hay una ruta a una imagen guardada
        try:
            img = Image(diagrama_path, width=6*inch, height=4*inch)
            elements.append(img)
        except Exception as e:
            elements.append(Paragraph(f"<i>Error al cargar el diagrama: {str(e)}</i>", styles['Italic']))
    
    else:
        elements.append(Paragraph("<i>No hay diagrama esquemático disponible</i>", styles['Italic']))
    
    return elements


def create_seccion_transientes(session_state: Dict[str, Any], h1_style, h2_style, styles, dpi: int) -> List:
    """Crea la sección de Análisis de Transientes"""
    elements = []
    
    elements.append(Paragraph("10. ANÁLISIS DE TRANSIENTES (GOLPE DE ARIETE)", h1_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Verificar si hay resultados de transientes
    transientes_data = session_state.get('transientes_resultados', None)
    
    if transientes_data is not None:
        # Parámetros del análisis
        elements.append(Paragraph("<b>Parámetros del Análisis:</b>", h2_style))
        
        params_data = [
            ['Parámetro', 'Valor', 'Unidad'],
            ['Celeridad de Onda (a)', f"{transientes_data.get('celeridad', 0):.2f}", 'm/s'],
            ['Tiempo de Parada (Tp)', f"{transientes_data.get('tiempo_parada', 0):.2f}", 's'],
            ['Tiempo Crítico (Tc)', f"{transientes_data.get('tiempo_critico', 0):.2f}", 's'],
            ['Longitud Crítica (Lc)', f"{transientes_data.get('longitud_critica', 0):.2f}", 'm'],
            ['Tipo de Conducción', transientes_data.get('tipo_conduccion', 'N/A'), ''],
            ['Tipo de Cierre', transientes_data.get('tipo_cierre', 'N/A'), ''],
            ['Fórmula Usada', transientes_data.get('formula_usada', 'N/A'), ''],
        ]
        
        table = Table(params_data, colWidths=[3*inch, 2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Resultados de Presión
        elements.append(Paragraph("<b>Resultados de Presión:</b>", h2_style))
        
        presion_data = [
            ['Parámetro', 'Valor', 'Unidad'],
            ['Altura Manométrica (Hm)', f"{transientes_data.get('altura_manometrica', 0):.2f}", 'm.c.a.'],
            ['Sobrepresión (ΔH)', f"{transientes_data.get('sobrepresion', 0):.2f}", 'm'],
            ['Presión Máxima', f"{transientes_data.get('presion_maxima', 0):.2f}", 'm.c.a.'],
            ['Presión Mínima (estimada)', f"{session_state.get('presion_minima_transiente', 0):.2f}", 'm.c.a.'],
        ]
        
        presion_table = Table(presion_data, colWidths=[3*inch, 2*inch, 1.5*inch])
        presion_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(presion_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Estado de Seguridad
        elements.append(Paragraph("<b>Verificación de Seguridad:</b>", h2_style))
        
        es_seguro = transientes_data.get('es_seguro', None)
        margen = transientes_data.get('margen_seguridad', 0)
        
        if es_seguro is not None:
            if es_seguro:
                seguridad_texto = f"""
                ✅ <b>SISTEMA SEGURO</b>
                <br/>La presión máxima transitoria ({transientes_data.get('presion_maxima', 0):.2f} m.c.a.) 
                está dentro de los límites de la tubería.
                <br/>Margen de seguridad: +{margen:.2f} m
                """
            else:
                seguridad_texto = f"""
                ⚠️ <b>ATENCIÓN: PRESIÓN EXCEDE PN</b>
                <br/>La presión máxima transitoria ({transientes_data.get('presion_maxima', 0):.2f} m.c.a.) 
                supera la presión nominal de la tubería.
                <br/>Exceso: {abs(margen):.2f} m
                """
            elements.append(Paragraph(seguridad_texto, styles['Normal']))
        
        # Recomendaciones
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("<b>Recomendaciones:</b>", h2_style))
        
        presion_max = transientes_data.get('presion_maxima', 0)
        presion_trabajo = session_state.get('altura_descarga', 0)
        
        if es_seguro is not None and not es_seguro:
            recomendacion = """
            <b>Acciones Recomendadas:</b>
            <br/>• Aumentar la presión nominal (PN) de la tubería
            <br/>• Instalar válvulas de alivio de presión
            <br/>• Considerar tanques amortiguadores o chimeneas de equilibrio
            <br/>• Implementar VFD para parada controlada de bombas
            <br/>• Aumentar el tiempo de cierre de válvulas
            <br/>• Verificar volantes de inercia en las bombas
            """
        else:
            recomendacion = """
            ✅ El sistema opera dentro de rangos seguros.
            <br/><b>Se recomienda:</b>
            <br/>• Verificar periódicamente las válvulas de retención
            <br/>• Mantener el sistema de protección contra transientes
            <br/>• Realizar pruebas de presión según normativa
            """
        
        elements.append(Paragraph(recomendacion, styles['Normal']))
    
    else:
        elements.append(Paragraph("<i>No hay resultados de análisis de transientes disponibles.</i>", styles['Italic']))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("""
        Para incluir el análisis de transientes en el reporte:
        <br/>1. Active la opción "Análisis de Transientes" en el panel de desarrollador
        <br/>2. Vaya a la pestaña "Transientes" y ejecute el análisis
        <br/>3. Genere el reporte PDF nuevamente
        """, styles['Normal']))
    
    return elements


def add_page_number(canvas_obj, doc):
    """Agrega número de página al pie de página"""
    canvas_obj.saveState()
    canvas_obj.setFont('Helvetica', 9)
    page_num = canvas_obj.getPageNumber()
    text = f"Página {page_num}"
    canvas_obj.drawRightString(7.5*inch, 0.5*inch, text)
    canvas_obj.restoreState()
