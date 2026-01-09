# Módulo de visualización de curvas y gráficos

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Tuple, Optional, List
from core.curves import calculate_vfd_curves

def create_hq_curve_plot(pump_curve_data: pd.DataFrame, 
                        system_curve_data: pd.DataFrame,
                        operating_point: Optional[Tuple[float, float]],
                        flow_unit: str = 'L/s',
                        title: str = "Curvas H-Q") -> go.Figure:
    fig = go.Figure()
    if pump_curve_data is not None and not pump_curve_data.empty:
        fig.add_trace(go.Scatter(x=pump_curve_data.iloc[:, 0], y=pump_curve_data.iloc[:, 1], mode='lines+markers', name='Curva de la Bomba', line=dict(color='blue', width=3)))
    if system_curve_data is not None and not system_curve_data.empty:
        fig.add_trace(go.Scatter(x=system_curve_data.iloc[:, 0], y=system_curve_data.iloc[:, 1], mode='lines+markers', name='Curva del Sistema', line=dict(color='red', width=3)))
    if operating_point and len(operating_point) == 2 and operating_point[0] > 0:
        fig.add_trace(go.Scatter(x=[operating_point[0]], y=[operating_point[1]], mode='markers', name='Punto de Operación', marker=dict(size=12, color='green', symbol='star')))
    fig.update_layout(title=title, xaxis_title=f'Caudal ({flow_unit})', yaxis_title='Altura (m)', legend_title="Leyenda")
    return fig

def create_efficiency_curve_plot(efficiency_curve_data: pd.DataFrame,
                                bep_point: Optional[Tuple[float, float]],
                                flow_unit: str = 'L/s',
                                title: str = "Curva de Eficiencia") -> go.Figure:
    fig = go.Figure()
    if efficiency_curve_data is not None and not efficiency_curve_data.empty:
        fig.add_trace(go.Scatter(x=efficiency_curve_data.iloc[:, 0], y=efficiency_curve_data.iloc[:, 1], mode='lines+markers', name='Eficiencia', line=dict(color='purple', width=3)))
    if bep_point and len(bep_point) == 2 and bep_point[0] > 0:
        fig.add_trace(go.Scatter(x=[bep_point[0]], y=[bep_point[1]], mode='markers', name='BEP', marker=dict(size=12, color='orange', symbol='star')))
    fig.update_layout(title=title, xaxis_title=f'Caudal ({flow_unit})', yaxis_title='Eficiencia (%)', legend_title="Leyenda")
    return fig

def create_power_curve_plot(power_curve_data: pd.DataFrame,
                           flow_unit: str = 'L/s',
                           title: str = "Curva de Potencia") -> go.Figure:
    fig = go.Figure()
    if power_curve_data is not None and not power_curve_data.empty:
        fig.add_trace(go.Scatter(x=power_curve_data.iloc[:, 0], y=power_curve_data.iloc[:, 1], mode='lines+markers', name='Potencia', line=dict(color='brown', width=3)))
    fig.update_layout(title=title, xaxis_title=f'Caudal ({flow_unit})', yaxis_title='Potencia (HP)', legend_title="Leyenda")
    return fig

def create_npsh_curve_plot(npsh_curve_data: pd.DataFrame,
                          flow_unit: str = 'L/s',
                          title: str = "Curva de NPSH Requerido") -> go.Figure:
    fig = go.Figure()
    if npsh_curve_data is not None and not npsh_curve_data.empty:
        fig.add_trace(go.Scatter(x=npsh_curve_data.iloc[:, 0], y=npsh_curve_data.iloc[:, 1], mode='lines+markers', name='NPSH Requerido', line=dict(color='darkred', width=3)))
    fig.update_layout(title=title, xaxis_title=f'Caudal ({flow_unit})', yaxis_title='NPSH (m)', legend_title="Leyenda")
    return fig

def create_vfd_analysis_plot(base_curve_data: pd.DataFrame,
                            vfd_percentages: List[float],
                            flow_unit: str = 'L/s',
                            title: str = "Análisis VFD") -> go.Figure:
    fig = go.Figure()
    if base_curve_data is not None and not base_curve_data.empty:
        base_curve_list = [tuple(x) for x in base_curve_data.to_numpy()]
        fig.add_trace(go.Scatter(x=base_curve_data.iloc[:, 0], y=base_curve_data.iloc[:, 1], mode='lines+markers', name='100% RPM (Base)', line=dict(color='blue', width=3)))
        colors = ['red', 'green', 'orange', 'purple']
        for i, percentage in enumerate(vfd_percentages):
            if percentage != 100:
                vfd_curve_list = calculate_vfd_curves(base_curve_list, percentage)
                if vfd_curve_list:
                    vfd_q = [p[0] for p in vfd_curve_list]
                    vfd_h = [p[1] for p in vfd_curve_list]
                    color = colors[i % len(colors)]
                    fig.add_trace(go.Scatter(x=vfd_q, y=vfd_h, mode='lines+markers', name=f'{percentage}% RPM', line=dict(color=color, width=2)))
    fig.update_layout(title=title, xaxis_title=f'Caudal ({flow_unit})', yaxis_title='Altura (m)', legend_title="Leyenda")
    return fig

def create_comprehensive_analysis_plot(pump_curve_data: pd.DataFrame, system_curve_data: pd.DataFrame, efficiency_curve_data: pd.DataFrame, power_curve_data: pd.DataFrame, npsh_curve_data: pd.DataFrame, operating_point: Optional[Tuple[float, float]], bep_point: Optional[Tuple[float, float]], flow_unit: str = 'L/s') -> go.Figure:
    fig = make_subplots(rows=2, cols=2, subplot_titles=('Curvas H-Q', 'Eficiencia', 'Potencia', 'NPSH'))
    if pump_curve_data is not None and not pump_curve_data.empty:
        fig.add_trace(go.Scatter(x=pump_curve_data.iloc[:, 0], y=pump_curve_data.iloc[:, 1], mode='lines', name='Bomba'), row=1, col=1)
    if system_curve_data is not None and not system_curve_data.empty:
        fig.add_trace(go.Scatter(x=system_curve_data.iloc[:, 0], y=system_curve_data.iloc[:, 1], mode='lines', name='Sistema'), row=1, col=1)
    if operating_point and len(operating_point) == 2 and operating_point[0] > 0:
        fig.add_trace(go.Scatter(x=[operating_point[0]], y=[operating_point[1]], mode='markers', name='Operación', marker=dict(size=10, symbol='star')), row=1, col=1)
    if efficiency_curve_data is not None and not efficiency_curve_data.empty:
        fig.add_trace(go.Scatter(x=efficiency_curve_data.iloc[:, 0], y=efficiency_curve_data.iloc[:, 1], mode='lines', name='Eficiencia'), row=1, col=2)
    if bep_point and len(bep_point) == 2 and bep_point[0] > 0:
        fig.add_trace(go.Scatter(x=[bep_point[0]], y=[bep_point[1]], mode='markers', name='BEP', marker=dict(size=10, symbol='star')), row=1, col=2)
    if power_curve_data is not None and not power_curve_data.empty:
        fig.add_trace(go.Scatter(x=power_curve_data.iloc[:, 0], y=power_curve_data.iloc[:, 1], mode='lines', name='Potencia'), row=2, col=1)
    if npsh_curve_data is not None and not npsh_curve_data.empty:
        fig.add_trace(go.Scatter(x=npsh_curve_data.iloc[:, 0], y=npsh_curve_data.iloc[:, 1], mode='lines', name='NPSH'), row=2, col=2)
    fig.update_xaxes(title_text=f'Caudal ({flow_unit})', row=1, col=1)
    fig.update_yaxes(title_text='Altura (m)', row=1, col=1)
    fig.update_xaxes(title_text=f'Caudal ({flow_unit})', row=1, col=2)
    fig.update_yaxes(title_text='Eficiencia (%)', row=1, col=2)
    fig.update_xaxes(title_text=f'Caudal ({flow_unit})', row=2, col=1)
    fig.update_yaxes(title_text='Potencia (HP)', row=2, col=1)
    fig.update_xaxes(title_text=f'Caudal ({flow_unit})', row=2, col=2)
    fig.update_yaxes(title_text='NPSH (m)', row=2, col=2)
    fig.update_layout(title_text="Análisis Completo de Curvas", showlegend=True, height=700)
    return fig

def create_results_table(operating_point: Optional[Tuple[float, float]], bep_point: Optional[Tuple[float, float]], efficiency_at_op: float, power_at_op: float, npsh_at_op: float, flow_unit: str = 'L/s') -> pd.DataFrame:
    """Crea una tabla de resultados del análisis."""
    data = {
        'Parámetro': [
            'Punto de Operación - Caudal',
            'Punto de Operación - Altura',
            'Eficiencia en Operación',
            'Potencia en Operación',
            'NPSH Requerido en Operación',
            'BEP - Caudal',
            'BEP - Eficiencia Máxima'
        ],
        'Valor': [
            f"{operating_point[0]:.2f}" if operating_point and len(operating_point) == 2 and operating_point[0] > 0 else "N/A",
            f"{operating_point[1]:.2f}" if operating_point and len(operating_point) == 2 and operating_point[1] > 0 else "N/A",
            f"{efficiency_at_op:.2f}" if efficiency_at_op > 0 else "N/A",
            f"{power_at_op:.2f}" if power_at_op > 0 else "N/A",
            f"{npsh_at_op:.2f}" if npsh_at_op > 0 else "N/A",
            f"{bep_point[0]:.2f}" if bep_point and len(bep_point) == 2 and bep_point[0] > 0 else "N/A",
            f"{bep_point[1]:.2f}" if bep_point and len(bep_point) == 2 and bep_point[1] > 0 else "N/A"
        ],
        'Unidad': [
            flow_unit,
            'm',
            '%',
            'HP',
            'm',
            flow_unit,
            '%'
        ]
    }
    return pd.DataFrame(data)
