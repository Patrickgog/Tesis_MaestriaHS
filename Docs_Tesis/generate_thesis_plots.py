import matplotlib.pyplot as plt
import numpy as np
import os

# Configuration for aesthetic technical plots
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
    'figure.titlesize': 18
})

OUTPUT_DIR = r"c:\Users\psciv\OneDrive\Desktop\PYTHON\App_bombeo\app_bombeo_modulos\Docs_Tesis\Tesis_maestria_HS\Capitulo_1_Marco_Teorico"

def plot_pump_system_curve():
    """Generates the Operating Point curve (Pump vs System)."""
    Q = np.linspace(0, 100, 200)  # Flow in L/s
    
    # Pump Curve (Quadratic approximation: H = A - B*Q^2)
    H_shutoff = 50
    H_pump = H_shutoff - 0.004 * Q**2
    
    # System Curve (H = H_static + K*Q^2)
    H_static = 20
    H_system = H_static + 0.003 * Q**2
    
    # Find intersection (approximate)
    idx = np.argwhere(np.diff(np.sign(H_pump - H_system))).flatten()
    Q_op = Q[idx][0]
    H_op = H_pump[idx][0]

    plt.figure(figsize=(10, 6))
    plt.plot(Q, H_pump, 'b-', linewidth=2.5, label='Curva de la Bomba (H-Q)')
    plt.plot(Q, H_system, 'r-', linewidth=2.5, label='Curva del Sistema')
    
    # Efficiency Curve (secondary axis) - Theoretical Parabola
    eff = -0.016 * (Q - 55)**2 + 80
    eff = np.clip(eff, 0, 100)
    
    # Plotting Intersection
    plt.plot(Q_op, H_op, 'ko', markersize=10, markerfacecolor='orange', markeredgewidth=2, label='Punto de Operación')
    plt.annotate(f'Q={Q_op:.1f} L/s\nH={H_op:.1f} m', xy=(Q_op, H_op), xytext=(Q_op+10, H_op+10),
                 arrowprops=dict(facecolor='black', shrink=0.05))

    plt.xlabel('Caudal Q (L/s)')
    plt.ylabel('Altura Dinámica Total H (m)')
    plt.title('Interacción Curva del Sistema vs. Curva de la Bomba')
    plt.legend(loc='upper right')
    plt.grid(True, which='both', linestyle='--', alpha=0.7)
    plt.ylim(0, 60)
    plt.xlim(0, 100)
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'Fig_1_1_Punto_Operacion.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_economic_diameter():
    """Generates the Economic Diameter Optimization curve."""
    D = np.linspace(100, 500, 200)  # Diameter in mm
    
    # Cost approximations for illustration
    # Investment Cost (Linear/Quadratic with D)
    Cost_Inv = 5000 + 10 * D + 0.05 * D**2
    
    # Energy Cost (Inverse 5th power of D roughly, due to friction)
    # Head loss proportional to 1/D^5, Power proportional to Head loss
    Cost_Energy = 2e9 / D**2.5 # Adjusted for visual balance
    
    Total_Cost = Cost_Inv + Cost_Energy
    
    # Find minimum
    min_idx = np.argmin(Total_Cost)
    D_opt = D[min_idx]
    Cost_min = Total_Cost[min_idx]

    plt.figure(figsize=(10, 6))
    plt.plot(D, Cost_Inv, 'g--', linewidth=2, label='Costo de Inversión (Tubería + Equipos)')
    plt.plot(D, Cost_Energy, 'r--', linewidth=2, label='Costo de Energía (Operación)')
    plt.plot(D, Total_Cost, 'k-', linewidth=3, label='Costo Total Capitalizado')
    
    plt.plot(D_opt, Cost_min, 'bo', markersize=10)
    plt.annotate(f'Diámetro Económico\nOptimo ≈ {D_opt:.0f} mm', xy=(D_opt, Cost_min), xytext=(D_opt, Cost_min+5000),
                 arrowprops=dict(facecolor='blue', shrink=0.05), ha='center')

    plt.xlabel('Diámetro de Tubería (mm)')
    plt.ylabel('Costo Presente Neto ($ USD)')
    plt.title('Optimización Económica del Diámetro de Impulsión')
    plt.legend()
    plt.grid(True, alpha=0.5)
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'Fig_1_2_Diametro_Economico.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_npsh_cavitation():
    """Generates NPSH available vs NPSH required."""
    Q = np.linspace(0, 100, 200)
    
    # NPSH Required (Increases with Q^2 usually)
    NPSH_r = 1.5 + 0.0008 * Q**2
    
    # NPSH Available (Decreases with Q due to friction losses in suction)
    H_atm = 10.33 # sea level
    H_vap = 0.2
    Hs = 2.0 # Suction lift
    Hf_s = 0.0005 * Q**2
    NPSH_a = H_atm - H_vap - Hs - Hf_s
    
    plt.figure(figsize=(10, 6))
    plt.plot(Q, NPSH_r, 'r-', linewidth=2.5, label='NPSH Requerido (Bomba)')
    plt.plot(Q, NPSH_a, 'b-', linewidth=2.5, label='NPSH Disponible (Sistema)')
    
    # Shade cavitation zone
    idx_cross = np.argwhere(np.diff(np.sign(NPSH_a - NPSH_r))).flatten()
    if len(idx_cross) > 0:
        Q_cav = Q[idx_cross][0]
        plt.fill_between(Q, 0, 15, where=(Q > Q_cav), color='red', alpha=0.2, label='Zona de Cavitación')
        plt.axvline(x=Q_cav, color='k', linestyle=':')
        plt.text(Q_cav + 2, 8, 'Inicio de Cavitación', rotation=90)

    plt.xlabel('Caudal Q (L/s)')
    plt.ylabel('Altura Neta Positiva de Succión (m)')
    plt.title('Análisis de Cavitación: NPSH Disponbile vs. Requerido')
    plt.legend()
    plt.grid(True)
    plt.ylim(0, 12)
    plt.xlim(0, 100)
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'Fig_1_3_Analisis_NPSH.png'), dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    plot_pump_system_curve()
    plot_economic_diameter()
    plot_npsh_cavitation()
    print("Gráficos generados exitosamente.")
