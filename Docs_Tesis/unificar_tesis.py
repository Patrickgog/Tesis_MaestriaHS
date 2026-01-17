import os

# Rutas de los archivos generados
base_dir = r"c:\Users\psciv\OneDrive\Desktop\PYTHON\App_bombeo\app_bombeo_modulos\Docs_Tesis\Tesis_maestria_HS"
output_file = os.path.join(base_dir, "Tesis_Completa_Final.md")

capitulos = [
    os.path.join(base_dir, "Capitulo_1_Marco_Teorico", "Capitulo_1_Marco_Teorico.md"),
    os.path.join(base_dir, "Capitulo_2_Metodologia", "Capitulo_2_Metodologia.md"),
    os.path.join(base_dir, "Capitulo_3_Funcionalidad", "Capitulo_3_Funcionalidad.md"),
    os.path.join(base_dir, "Capitulo_4_Resultados", "Capitulo_4_Resultados.md"),
    os.path.join(base_dir, "Capitulo_5_Conclusiones", "Capitulo_5_Conclusiones.md"),
    os.path.join(base_dir, "Bibliografia", "Bibliografia.md")
]

def unificar_tesis():
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Título General para la Tesis
        outfile.write("# TESIS DE MAESTRÍA EN INGENIERÍA HIDROSANITARIA\n\n")
        outfile.write("## DISEÑO Y VALIDACIÓN DE SOFTWARE PARA SISTEMAS DE BOMBEO ASISTIDO POR IA\n\n")
        outfile.write("---\n\n") # Separador para la portada

        for i, file_path in enumerate(capitulos):
            if os.path.exists(file_path):
                print(f"Añadiendo: {os.path.basename(file_path)}")
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content)
                    # Añadir saltos de página para que Pandoc los interprete (Opcional)
                    outfile.write("\n\n---\n\n") # Esto ayuda a Pandoc a separar secciones
            else:
                print(f"Advertencia: No se encontró el archivo {file_path}")

    print(f"\n¡Éxito! Archivo unificado en: {output_file}")

if __name__ == "__main__":
    unificar_tesis()
