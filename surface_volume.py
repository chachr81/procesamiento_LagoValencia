import arcpy
from arcpy.sa import *

def main():
    arcpy.env.workspace = r"C:\Workspace\LagoValencia\LagoValencia.gdb"
    arcpy.CheckOutExtension("3D")

    # Diccionario que mapea los años con sus alturas promedio y medianas
    heights = {
        "1986": {"mean": 384.34, "median": 382.73},
        "1990": {"mean": 384.32, "median": 382.41},
        "2000": {"mean": 385.48, "median": 383.55},
        "2014": {"mean": 391.29, "median": 385.82},
        "2019": {"mean": 395.15, "median": 390.65},
        "2023": {"mean": 395.23, "median": 390.64}
    }

    # Lista de rutas a los shapefiles clasificados
    shapefiles = [
        r"D:\Workspace\LagoValencia\LagoValencia.gdb\lago1986_corrected",
        r"D:\Workspace\LagoValencia\LagoValencia.gdb\lago1990_corrected",
        r"D:\Workspace\LagoValencia\LagoValencia.gdb\lago2000_corrected",
        r"D:\Workspace\LagoValencia\LagoValencia.gdb\lago2014_corrected",
        r"D:\Workspace\LagoValencia\LagoValencia.gdb\lago2019_corrected",
        r"D:\Workspace\LagoValencia\LagoValencia.gdb\lago2023_corrected"
    ]

    # DEM de referencia
    dem = r"D:\Workspace\LagoValencia\LagoValencia.gdb\mde_corregido_TRfinal2000"

    # Validar si el DEM existe
    if not arcpy.Exists(dem):
        print(f"Error: El DEM '{dem}' no existe o no es compatible.")
        return

    # Procesar cada shapefile con sus respectivos años
    for shapefile, year in zip(shapefiles, heights.keys()):
        # Validar si el shapefile existe
        if not arcpy.Exists(shapefile):
            print(f"Advertencia: El shapefile '{shapefile}' no existe. Se omite el año {year}.")
            continue

        # Calcula el volumen de la superficie usando el promedio
        try:
            volume_info_average = calculate_surface_volume(dem, heights[year]["mean"], "mean", year)
        except Exception as e:
            print(f"Error al calcular el volumen para el promedio en el año {year}: {e}")
            volume_info_average = None

        # Calcula el volumen de la superficie usando la mediana
        try:
            volume_info_median = calculate_surface_volume(dem, heights[year]["median"], "median", year)
        except Exception as e:
            print(f"Error al calcular el volumen para la mediana en el año {year}: {e}")
            volume_info_median = None
        
        print(f"Año: {year}, Volumen (Promedio): {volume_info_average}, Volumen (Mediana): {volume_info_median}")

def calculate_surface_volume(dem, reference_height, height_type, year):
    """
    Calcula el volumen de la superficie.
    """
    out_surface_volume = f"D:\\Workspace\\LagoValencia\\documentos\\volumenes\\Surface_Volume_{year}_{height_type}.txt"
    reference_plane = "BELOW"
    z_factor = 1  # Ajusta si las unidades verticales del DEM son diferentes

    # Validar que el DEM existe antes de ejecutar la herramienta
    if not arcpy.Exists(dem):
        raise RuntimeError(f"El DEM '{dem}' no existe o no es compatible.")

    # Ejecutar SurfaceVolume y manejar errores
    try:
        result = arcpy.ddd.SurfaceVolume(
            in_surface=dem,
            out_text_file=out_surface_volume,
            reference_plane=reference_plane,
            base_z=reference_height,
            z_factor=z_factor,
            pyramid_level_resolution="0"
        )
        return result.getOutput(0)
    except arcpy.ExecuteError as e:
        raise RuntimeError(f"Error ejecutando SurfaceVolume: {e}")

if __name__ == "__main__":
    main()