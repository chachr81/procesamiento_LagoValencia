"""Transformar de Polígono a líneas
"""
import arcpy
from arcpy.sa import *

# ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")
# Definiendo espacio de trabajo
arcpy.env.workspace = r"C:\Workspace\\LagoValencia\\LagoValencia.gdb"
arcpy.env.overwriteOutput = True

def convertir_poligono_a_linea(input_polygon, output_line):
    """Convierte un shapefile de polígono a línea"""
    arcpy.PolygonToLine_management(input_polygon, output_line)

def agregar_informacion_superficie(input_line, mde_path):
    """Agrega información de superficie a las líneas utilizando el MDE integrado"""
    arcpy.ddd.AddSurfaceInformation(
        in_feature_class=input_line,
        in_surface=mde_path,
        out_property="Z_MIN;Z_MAX;Z_MEAN",
        method="BILINEAR",
        z_factor=1.0
        )
def main():
    # Ruta del MDE integrado
    mde_path = "mde_integrado"

    # Convertir polígonos a líneas y agregar información de superficie
    poligonos = ["lago1976", "lago1986", "lago1990", "lago2000", "lago2014", "lago2019", "lago2023"]
    for poligono in poligonos:
        input_polygon = f"lagoValencia.gdb\\{poligono}"
        output_line = f"lagoValencia.gdb\\{poligono}_lines"
        convertir_poligono_a_linea(input_polygon, output_line)
        agregar_informacion_superficie(output_line, mde_path)

    print('Script Terminado')

if __name__ == "__main__":
    main()
