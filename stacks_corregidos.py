import arcpy
from arcpy import env
from arcpy.sa import *

def main():
    # Configura el entorno de trabajo
    env.workspace = r"C:\Workspace\LagoValencia\LagoValencia.gdb"
    env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")
    env.extent = "MINOF"
    
    # Define las rutas de las bandas
    ruta_base = r"C:\Workspace\LagoValencia\raster\TM004053_24_01_1986"
    bandas = [f"{ruta_base}\LT05_L1TP_004053_19860124_20200918_02_T1_B{i}.TIF" for i in range(1, 8)]  # Genera rutas desde B1 a B7

    # Ruta para el archivo de salida del composite
    salida_composite = r"C:\Workspace\LagoValencia\LagoValencia.gdb\imagen_composite"

    # Combina las bandas
    arcpy.management.CompositeBands(bandas, salida_composite)

    # Ruta del DEM
    dem_path = r"C:\Workspace\LagoValencia\LagoValencia.gdb\mde_corregido_TRfinal1"

    # Aplica la corrección geométrica
    raster_ortorrectificado = arcpy.ia.Geometric(salida_composite, dem=dem_path)

    # Guarda la imagen ortorrectificada
    salida_ortorrectificada = r"C:\Workspace\LagoValencia\LagoValencia.gdb\imagen_ortorrectificada"
    raster_ortorrectificado.save(salida_ortorrectificada)

    print('El proceso ha finalizado exitosamente.')

if __name__ == "__main__":
    main()
