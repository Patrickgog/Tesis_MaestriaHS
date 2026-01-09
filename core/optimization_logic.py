import numpy as np
import plotly.graph_objs as go

# --- CLASE CENTRIFUGAL PUMP DESIGNER ---
class CentrifugalPumpDesigner:
    RHO_WATER = 1000.0
    G = 9.80665
    def __init__(self, q_design, h_static, rpm, hourly_factors, pipe_length_m, pipe_diameter_m, 
                 n_parallel, hw_c, eff_peak, electricity_cost, min_tank_level_perc, 
                 initial_tank_level_perc, simulation_days=1, tank_capacity_m3=None, tank_round_m3=50):
        # Validaciones y asignación robusta
        if len(hourly_factors) != 24:
            raise ValueError("hourly_factors debe contener 24 valores: uno por cada hora del día")
        if not 0.0 <= min_tank_level_perc < 1.0:
            raise ValueError("min_tank_level_perc debe estar entre 0.0 y 1.0")
        if not 0.0 <= initial_tank_level_perc <= 1.0:
            raise ValueError("initial_tank_level_perc debe estar entre 0.0 y 1.0")
        if not simulation_days > 0:
            raise ValueError("simulation_days debe ser mayor que 0")
        self.q_design = float(q_design)
        self.h_static = float(h_static)
        self.rpm = float(rpm)
        self.hourly_factors = np.asarray(hourly_factors, dtype=float)
        self.n_parallel = int(n_parallel)
        self.initial_tank_level_perc = float(initial_tank_level_perc)
        self.simulation_days = int(simulation_days)
        self.pipe_length_m = float(pipe_length_m)
        self.pipe_diameter_m = float(pipe_diameter_m)
        self.hw_c = float(hw_c)
        self.eff_peak = eff_peak
        self.electricity_cost = electricity_cost
        
        # Curva de la bomba (parábola): H = H_shutoff - a_p * Q^2
        h_design_point = self.system_head(self.q_design) # Altura requerida en el punto de diseño
        h_shutoff = 1.33 * h_design_point # Estimación típica
        a_p = (h_shutoff - h_design_point) / self.q_design**2 if self.q_design > 1e-9 else 0.0
        self.pump_coeffs = (a_p, h_shutoff)
        
        self.q_range = np.linspace(1e-6, 1.5 * self.q_design, 400)
        self.q_op, self.h_op = self._solve_operating_point()
        self.min_tank_level_perc = min_tank_level_perc
        self.tank_capacity_m3_user = tank_capacity_m3
        self.tank_round_m3 = tank_round_m3 if tank_round_m3 is not None and tank_round_m3 > 0 else 50.0
        if self.tank_capacity_m3_user is None:
            self.tank_capacity_m3 = self._size_reservoir()
            self.initial_volume_m3 = self.tank_capacity_m3 * self.initial_tank_level_perc
        else:
            self.tank_capacity_m3 = float(self.tank_capacity_m3_user)
            self.initial_volume_m3 = self.tank_capacity_m3 * self.initial_tank_level_perc
        self.vol_hourly, self.demand_hourly, self.pump_on_hourly = self.daily_balance()
        self.vfd_results = self._analyze_vfd_operation_by_flow(self.q_design * 1000)

    def system_head(self, q):
        q = np.asarray(q, dtype=float)
        L, D, C = self.pipe_length_m, self.pipe_diameter_m, self.hw_c
        hf = 10.67 * L * q**1.852 / (C**1.852 * D**4.871)
        return self.h_static + hf

    def pump_head(self, q):
        a_p, h_shutoff = self.pump_coeffs
        return h_shutoff - a_p * np.asarray(q, dtype=float)**2

    def _solve_operating_point(self):
        q_total = self.q_range * self.n_parallel
        pump_head_curve = self.pump_head(self.q_range)
        # La curva del sistema opera con el caudal TOTAL
        system_head_curve = self.system_head(q_total)
        # La curva de la bomba individual debe compararse ajustando
        # Si las bombas están en paralelo, cada una aporta Q/n al mismo H
        # Aquí simplificamos: Caudal TOTAL vs Altura Sistema.
        # Pero pump_head(q) devuelve H para una sola bomba al caudal q.
        # Si hay N bombas en paralelo, H_total(Q_total) = H_bomba(Q_total/N)
        
        # Corregido: Cruzar curva sistema con curva combinada
        q_per_pump_range = self.q_range
        q_total_range = q_per_pump_range * self.n_parallel
        h_combined_range = self.pump_head(q_per_pump_range) # Altura es la misma en paralelo
        
        system_head_at_total = self.system_head(q_total_range)
        
        diff = np.abs(h_combined_range - system_head_at_total)
        idx = diff.argmin()
        
        q_op_per_pump = q_per_pump_range[idx]
        h_op = h_combined_range[idx]
        return float(q_op_per_pump), float(h_op)

    def efficiency(self, q):
        q = np.asarray(q, dtype=float)
        # Modelo parabólico de eficiencia centrado en q_design
        eta = self.eff_peak * (1 - ((q - self.q_design) / self.q_design)**2)
        return np.clip(eta, 0, None)

    def power_kW(self, q):
        head = self.pump_head(q)
        eta = self.efficiency(q)
        with np.errstate(divide='ignore', invalid='ignore'):
            power = (self.RHO_WATER * self.G * q * head / eta) / 1e3
        return np.nan_to_num(power)

    def power_at_op_kW(self):
        q_op = self.q_op
        h_op = self.h_op
        eta_op = self.efficiency(q_op)
        if eta_op < 1e-6:
            return 0.0
        return (self.RHO_WATER * self.G * q_op * h_op / eta_op) / 1000

    def _size_reservoir(self):
        H = self.simulation_days * 24
        q_in = np.full(H, self.q_op * self.n_parallel)
        q_out = np.tile(self.q_design * self.hourly_factors, self.simulation_days)
        hourly_balance = (q_in - q_out) * 3600.0
        cum_mass = np.cumsum(hourly_balance)
        active_storage = cum_mass.max() - cum_mass.min()
        total_storage = active_storage / (1.0 - self.min_tank_level_perc)
        round_m3 = self.tank_round_m3 if hasattr(self, 'tank_round_m3') and self.tank_round_m3 > 0 else 50.0
        cap = np.ceil(total_storage / round_m3) * round_m3
        return float(max(cap, round_m3))

    def affinity_curves(self, rpm_list):
        curves = {}
        for n in rpm_list:
            ratio = n / self.rpm
            q_new = self.q_range * ratio
            h_new = self.pump_head(self.q_range) * ratio**2
            curves[n] = (q_new, h_new)
        return curves

    def daily_balance(self):
        q_supply = self.q_op * self.n_parallel
        q_demand = np.tile(self.q_design * self.hourly_factors, self.simulation_days)
        num_hours = 24 * self.simulation_days
        vol = np.zeros(num_hours + 1)
        pump_on = np.zeros(num_hours)
        vol[0] = self.initial_volume_m3
        for hour in range(num_hours):
            if vol[hour] < self.tank_capacity_m3:
                pump_on[hour] = 1.0
                current_supply = q_supply
            else:
                pump_on[hour] = 0.0
                current_supply = 0.0
            delta_vol = (current_supply - q_demand[hour]) * 3600
            vol[hour+1] = np.clip(vol[hour] + delta_vol, 0, self.tank_capacity_m3)
        return vol, q_demand, pump_on

    def energy_costs(self):
        power_per_pump = self.power_at_op_kW()
        total_power = power_per_pump * self.n_parallel
        hourly_cost = total_power * self.pump_on_hourly * self.electricity_cost
        total_cost = np.sum(hourly_cost)
        total_volume_pumped = self.q_design * self.n_parallel * np.sum(self.pump_on_hourly) * 3600
        cost_per_m3 = total_cost / total_volume_pumped if total_volume_pumped > 0 else 0
        return hourly_cost, total_cost, cost_per_m3

    def _analyze_vfd_operation_by_flow(self, target_flow_lps):
        q_target_total_m3s = target_flow_lps / 1000.0
        target_head = self.system_head(q_target_total_m3s)
        if target_head > self.pump_coeffs[1]:
            return None
        q_target_per_pump_m3s = q_target_total_m3s / self.n_parallel
        a_p, h_shutoff = self.pump_coeffs
        h_shutoff_100, a_p_100 = h_shutoff, a_p
        
        # H = H0 - A*Q^2 --> H_req = (H0*alpha^2) - A*(Q_req/alpha)^2 * alpha^2 (Mal)
        # Ley afinidad: H2 = H1 * alpha^2, Q2 = Q1 * alpha
        # Punto homólogo en curva 100%: Q1 = Q2/alpha, H1 = H2/alpha^2
        # Cumple curva: H1 = H0 - A*Q1^2
        # H2/alpha^2 = H0 - A*(Q2/alpha)^2
        # H2 = H0*alpha^2 - A*Q2^2
        # alpha = sqrt((H2 + A*Q2^2)/H0)
        
        r_squared = (target_head + a_p_100 * q_target_per_pump_m3s**2) / h_shutoff_100
        if r_squared < 0:
            return None
        speed_ratio = np.sqrt(r_squared)
        q_homologous_100_rpm = q_target_per_pump_m3s / speed_ratio if speed_ratio > 1e-6 else 0
        efficiency = self.efficiency(q_homologous_100_rpm)
        power_kw = (self.RHO_WATER * self.G * q_target_per_pump_m3s * target_head / efficiency) / 1000 if efficiency > 1e-6 else 0.0
        return {
            "target_flow_lps": target_flow_lps,
            "speed_ratio": speed_ratio,
            "q_op_per_pump_lps": q_target_per_pump_m3s * 1000,
            "q_op_total_lps": q_target_total_m3s * 1000,
            "h_op": target_head,
            "efficiency": efficiency * 100,
            "power_per_pump_kw": power_kw,
            "total_power_kw": power_kw * self.n_parallel,
        }

    # --- PLOTTING METHODS UPDATED FOR STREAMLIT ---
    
    def plot_system_vs_pump(self):
        fig = go.Figure()
        q_total_range_m3s = self.q_range * self.n_parallel
        q_total_range_lps = q_total_range_m3s * 1000
        system_head_curve = self.system_head(q_total_range_m3s)
        fig.add_trace(go.Scatter(x=q_total_range_lps, y=system_head_curve, mode='lines', name='Curva del Sistema', line=dict(color='blue', width=3)))
        q_single_range_lps = self.q_range * 1000
        fig.add_trace(go.Scatter(x=q_single_range_lps, y=self.pump_head(self.q_range), mode='lines', name='Curva Bomba Individual', line=dict(color='grey', width=2, dash='dash')))
        combined_pump_head = self.pump_head(self.q_range) # Altura es la misma
        fig.add_trace(go.Scatter(x=q_total_range_lps, y=combined_pump_head, mode='lines', name=f'Curva Combinada ({self.n_parallel} bombas)', line=dict(color='green', width=3)))
        q_op_total_lps = self.q_op * self.n_parallel * 1000
        fig.add_trace(go.Scatter(x=[q_op_total_lps], y=[self.h_op], mode='markers', name='Punto de Operación', marker=dict(color='red', size=12, symbol='x')))
        fig.update_layout(title='Curvas H-Q: Sistema vs. Bombas', xaxis_title='Caudal Total (L/s)', yaxis_title='Carga (m)', height=500)
        return fig

    def plot_vfd_comparison(self):
        if not self.vfd_results:
            return None
        fig = go.Figure()
        r = self.vfd_results['speed_ratio']
        q_total_range_lps = self.q_range * self.n_parallel * 1000
        combined_pump_head_100 = self.pump_head(self.q_range)
        fig.add_trace(go.Scatter(x=q_total_range_lps, y=combined_pump_head_100, mode='lines', name=f'Curva Combinada @ 100% RPM', line=dict(color='green', width=3)))
        
        # Curva VFD: Q2 = Q1*r, H2 = H1*r^2
        q_vfd_range = self.q_range * r
        combined_pump_head_vfd = self.pump_head(self.q_range) * r**2
        q_total_vfd_lps = q_vfd_range * self.n_parallel * 1000
        
        fig.add_trace(go.Scatter(x=q_total_vfd_lps, y=combined_pump_head_vfd, mode='lines', name=f'Curva Combinada @ {r*100:.1f}% RPM', line=dict(color='orange', width=3, dash='dash')))
        system_head_curve = self.system_head(self.q_range * self.n_parallel)
        fig.add_trace(go.Scatter(x=q_total_range_lps, y=system_head_curve, mode='lines', name='Curva del Sistema', line=dict(color='blue', width=3)))
        
        q_op_total_vfd_lps = self.vfd_results['q_op_total_lps']
        h_op_vfd = self.vfd_results['h_op']
        power_vfd = self.vfd_results['total_power_kw']
        fig.add_trace(go.Scatter(x=[q_op_total_vfd_lps], y=[h_op_vfd], mode='markers+text', name=f'OP @ {r*100:.1f}% RPM', marker=dict(color='magenta', size=12, symbol='star'), text=[f"  {power_vfd:.1f} kW"], textposition="bottom right"))
        fig.update_layout(title='Análisis de Operación con VFD', xaxis_title='Caudal Total (L/s)', yaxis_title='Carga (m)', height=500)
        return fig

    def plot_efficiency_vs_flow(self):
        fig = go.Figure()
        q_range_lps = self.q_range * 1000
        q_op_lps = self.q_op * 1000
        eff_op = self.efficiency(self.q_op) * 100
        fig.add_trace(go.Scatter(x=q_range_lps, y=self.efficiency(self.q_range) * 100, mode='lines', name='Eficiencia', line=dict(color='purple', width=3)))
        fig.add_trace(go.Scatter(x=[q_op_lps], y=[eff_op], mode='markers+text', name='Punto de Operación', marker=dict(color='red', size=12, symbol='x'), text=[f" {eff_op:.1f}% @ {q_op_lps:.1f} L/s"], textposition="top right"))
        fig.update_layout(title='Eficiencia por Bomba vs. Caudal por Bomba', xaxis_title='Caudal por Bomba (L/s)', yaxis_title='Eficiencia (%)', height=500)
        return fig

    def plot_cost_per_m3_vs_flow(self):
        fig = go.Figure()
        q_valid_m3s = self.q_range[self.q_range > 1e-6]
        q_valid_lps = q_valid_m3s * 1000
        cost_per_m3 = (self.power_kW(q_valid_m3s) * self.electricity_cost) / (q_valid_m3s * 3600)
        fig.add_trace(go.Scatter(x=q_valid_lps, y=cost_per_m3, mode='lines', name='Costo Unitario', line=dict(color='teal', width=3)))
        if self.q_op > 1e-6:
            q_op_lps = self.q_op * 1000
            cost_op = (self.power_kW(self.q_op) * self.electricity_cost) / (self.q_op * 3600)
            fig.add_trace(go.Scatter(x=[q_op_lps], y=[cost_op], mode='markers', name='Punto de Operación', marker=dict(color='red', size=12, symbol='x')))
        fig.update_layout(title='Costo Unitario vs. Caudal', xaxis_title='Caudal (L/s)', yaxis_title='Costo (USD/m³)', height=500)
        return fig

    def plot_tank_volume(self):
        fig = go.Figure()
        num_hours = 24 * self.simulation_days
        hrs_vol = np.arange(num_hours + 1)
        fig.add_trace(go.Scatter(x=hrs_vol, y=self.vol_hourly, name='Volumen Tanque (m³)', mode='lines', line=dict(color='blue', width=3)))
        fig.add_hline(y=self.tank_capacity_m3, line_dash="dash", line_color="black", annotation_text=f'Capacidad Tanque ({self.tank_capacity_m3:.0f} m³)')
        fig.add_hline(y=self.tank_capacity_m3 * self.min_tank_level_perc, line_dash="dash", line_color="red", annotation_text=f'Reserva Mínima ({self.min_tank_level_perc*100:.0f}%)')
        fig.update_yaxes(range=[0, self.tank_capacity_m3 * 1.1])
        fig.update_layout(title=f'Simulación Operacional ({self.simulation_days} días): Volumen en Tanque', xaxis_title='Hora', yaxis_title='Volumen (m³)', height=500)
        return fig

    def plot_demand_vs_inflow(self):
        fig = go.Figure()
        num_hours = 24 * self.simulation_days
        hrs_op = np.arange(num_hours)
        constant_inflow_lps = np.full(num_hours, self.q_design * self.n_parallel * 1000)
        demand_lps = self.demand_hourly * 1000
        fig.add_trace(go.Bar(x=hrs_op, y=demand_lps, name='Demanda Horaria (L/s)', marker_color='red', opacity=0.6))
        
        # Mostrar cuando el bombeo está activo
        q_pumping_active = constant_inflow_lps * self.pump_on_hourly
        fig.add_trace(go.Scatter(x=hrs_op, y=q_pumping_active, name='Bombeo Activo (L/s)', mode='lines', line=dict(color='green', width=3), fill='tozeroy', fillcolor='rgba(0, 255, 0, 0.2)'))
        
        fig.update_layout(title=f'Simulación Operacional ({self.simulation_days} días): Demanda vs. Bombeo', xaxis_title='Hora', yaxis_title='Caudal (L/s)', height=500)
        return fig
