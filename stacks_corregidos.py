import arcpy
from arcpy import env
import os

def generar_composite(rutas, gdb_salida):
    """
    Genera composite rásters a partir de carpetas de bandas especificadas.

    :param rutas: Lista de rutas base de las carpetas que contienen las bandas.
    :param gdb_salida: Ruta de la Geodatabase donde se guardarán los rásters compuestos.
    """
    # Configurar el entorno de trabajo
    env.workspace = gdb_salida  # Se define la Geodatabase de salida como espacio de trabajo
    env.overwriteOutput = True  # Permitir sobrescribir los resultados
    arcpy.CheckOutExtension("Spatial")  # Activar la extensión "Spatial Analyst"
    env.extent = "MINOF"  # Utilizar la extensión mínima común entre los rásters

    # Iterar sobre cada carpeta y generar el composite
    for ruta_base in rutas:
        # Obtener el nombre de la carpeta para usarlo como nombre del ráster de salida
        nombre_composite = os.path.basename(ruta_base)  # El nombre de la carpeta será el identificador del composite
        salida_composite = os.path.join(gdb_salida, f"{nombre_composite}_composite")  # Define la ruta del composite en la GDB

        # Obtener todas las bandas (archivos TIF) dentro de la carpeta
        bandas = [os.path.join(ruta_base, archivo) for archivo in os.listdir(ruta_base) if archivo.endswith(".TIF")]

        # Verificar si se encontraron bandas en la carpeta
        if not bandas:
            print(f"Advertencia: No se encontraron bandas en la carpeta: {ruta_base}")
            continue

        try:
            # Combinar las bandas en un composite ráster
            arcpy.management.CompositeBands(bandas, salida_composite)
            print(f"Composite generado exitosamente: {salida_composite}")
        except Exception as e:
            print(f"Error al generar el composite para {ruta_base}: {e}")

def main():
    """
    Función principal para ejecutar el proceso de generación de composites.
    """
    # Lista de rutas base de las carpetas con las bandas
    rutas = [
        r"D:\Workspace\LagoValencia\raster\TM004053_24_01_1986",
        r"D:\Workspace\LagoValencia\raster\TM004053_19_01_1990",
        r"D:\Workspace\LagoValencia\raster\ETM_23_01_2000",
        r"D:\Workspace\LagoValencia\raster\OLI_TIRS004053_20140121",
        r"D:\Workspace\LagoValencia\raster\OLI_TIRS005053_20190211",
        r"D:\Workspace\LagoValencia\raster\OLI_TIRS004053_20230130"
    ]

    # Ruta de la Geodatabase de salida
    gdb_salida = r"D:\Workspace\LagoValencia\LagoValencia.gdb"

    # Llamar a la función para generar los composites
    generar_composite(rutas, gdb_salida)
    print("El proceso ha finalizado exitosamente.")

if __name__ == "__main__":
    main()
