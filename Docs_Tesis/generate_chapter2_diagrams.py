from graphviz import Digraph
import os

OUTPUT_DIR = r"c:\Users\psciv\OneDrive\Desktop\PYTHON\App_bombeo\app_bombeo_modulos\Docs_Tesis\Tesis_maestria_HS\Capitulo_2_Metodologia"

def generate_architecture_diagram():
    dot = Digraph(comment='Arquitectura del Sistema', format='png')
    dot.attr(rankdir='TB', size='10')

    # Frontend
    with dot.subgraph(name='cluster_frontend') as c:
        c.attr(label='Frontend (Streamlit)', style='filled', color='lightgrey')
        c.node('UI', 'Interfaz de Usuario\n(ui/ folder)')
        c.node('Sidebar', 'Barra Lateral\n(sidebar.py)')
        c.node('Graphs', 'Visualización\n(Plotly/Matplotlib)')
        c.edge('Sidebar', 'UI')
        c.edge('UI', 'Graphs')

    # Backend / Logic
    with dot.subgraph(name='cluster_backend') as c:
        c.attr(label='Lógica de Negocio (Python Core)', style='filled', color='lightblue')
        c.node('Calc_Hyd', 'Cálculos Hidráulicos\n(core/hydraulic.py)')
        c.node('Calc_Trans', 'Transientes (Allievi)\n(core/transients.py)')
        c.node('Economic', 'Evaluación Económica\n(core/economy.py)')
        c.node('Gemini', 'Asistente IA\n(Gemini API)')
        
    # Data Layer
    with dot.subgraph(name='cluster_data') as c:
        c.attr(label='Capa de Datos', style='filled', color='lightyellow')
        c.node('JSON', 'Persistencia Proyectos\n(JSON Files)')
        c.node('DB', 'Base de Datos\n(SQLite/Excel)')

    # Edges
    dot.edge('UI', 'Calc_Hyd', label=' Inputs')
    dot.edge('UI', 'Calc_Trans', label=' Config')
    dot.edge('Calc_Hyd', 'Graphs', label=' Resultados')
    dot.edge('Calc_Trans', 'Graphs')
    dot.edge('UI', 'Gemini', label=' Prompt')
    dot.edge('Gemini', 'UI', label=' Respuesta')
    dot.edge('Sidebar', 'JSON', label=' Load/Save')
    dot.edge('Calc_Hyd', 'DB', label=' Catálogos')

    output_path = os.path.join(OUTPUT_DIR, 'Fig_2_1_Arquitectura_Software')
    dot.render(output_path, cleanup=True)
    print(f"Diagrama de arquitectura generado en {output_path}.png")

def generate_flowchart_transients():
    dot = Digraph(comment='Flujograma Transientes', format='png')
    dot.attr(rankdir='TB')
    
    dot.node('Start', 'Inicio', shape='oval')
    dot.node('Input', 'Lectura de Datos\n(Geometría, Bomba, Tubería)', shape='parallelogram')
    dot.node('Steady', 'Cálculo Estado Estacionario\n(Punto Operación Q0, H0)', shape='box')
    dot.node('Method', 'Método de las Características (MOC)\nDiscretización dt = dx/a', shape='box')
    dot.node('Loop', 'Bucle de Tiempo t = 0 a T_sim', shape='diamond')
    dot.node('BC', 'Cálculo Condiciones de Borde\n(Embalse, Bomba, Válvula)', shape='box')
    dot.node('Interior', 'Cálculo Nodos Interiores', shape='box')
    dot.node('Store', 'Almacenar H(x,t), V(x,t)', shape='cylinder')
    dot.node('EndLoop', '¿t > T_sim?', shape='diamond')
    dot.node('Plot', 'Generar Envolventes\nMax/Min Presión', shape='box')
    dot.node('End', 'Fin', shape='oval')
    
    dot.edge('Start', 'Input')
    dot.edge('Input', 'Steady')
    dot.edge('Steady', 'Method')
    dot.edge('Method', 'Loop')
    dot.edge('Loop', 'BC')
    dot.edge('BC', 'Interior')
    dot.edge('Interior', 'Store')
    dot.edge('Store', 'EndLoop')
    dot.edge('EndLoop', 'Loop', label=' No')
    dot.edge('EndLoop', 'Plot', label=' Sí')
    dot.edge('Plot', 'End')

    output_path = os.path.join(OUTPUT_DIR, 'Fig_2_2_Flujo_Transientes')
    dot.render(output_path, cleanup=True)
    print(f"Flujograma generado en {output_path}.png")

if __name__ == "__main__":
    # Ensure Graphviz is installed or this will fail. 
    # Since I cannot install system binaries, I will create a fallback mermaid code generator if this fails?
    # Actually, for the user's local machine, pydot/graphviz might need the binary. 
    # Plan B: Generate Mermaid diagrams in text files that the user can render, OR generate simplified matplotlib flowcharts.
    # Let's try to generate pure Python diagrams using 'diagrams' or 'matplotlib' if possible? 
    # No, let's keep it creating a python script. If the user doesn't have graphviz installed, I will generate text-based mermaid blocks.
    try:
        generate_architecture_diagram()
        generate_flowchart_transients()
    except Exception as e:
        print(f"Error generando graficos con Graphviz: {e}")
        print("Se generarán bloques mermaid en el MD.")
