import arcpy
from arcpy.sa import *

def main():
    arcpy.env.workspace = r"C:\Workspace\LagoValencia\LagoValencia.gdb"
    arcpy.CheckOutExtension("3D")

    # Diccionario que mapea los años con sus alturas promedio y medianas
    heights = {
        "1986": {"mean": 384.87, "median": 390.71},
        "1990": {"mean": 384.87, "median": 390.88},
        "2000": {"mean": 385.41, "median": 392.64},
        "2014": {"mean": 387.93, "median": 407.94},
        "2019": {"mean": 388.21, "median": 409.58},
        "2023": {"mean": 388.19, "median": 410.60}
    }

    # Lista de rutas a los shapefiles clasificados
    shapefiles = [
        r"C:\Workspace\LagoValencia\shp\MNDWI_1986_classified.shp",
        r"C:\Workspace\LagoValencia\shp\MNDWI_1990_classified.shp",
        r"C:\Workspace\LagoValencia\shp\MNDWI_2000_classified.shp",
        r"C:\Workspace\LagoValencia\shp\MNDWI_2014_classified.shp",
        r"C:\Workspace\LagoValencia\shp\MNDWI_2019_classified.shp",
        r"C:\Workspace\LagoValencia\shp\MNDWI_2023_classified.shp"
    ]

    # DEM de referencia
    dem = "mde_corregido_TRfinal1"

    # Procesar cada shapefile con sus respectivos años
    for shapefile, year in zip(shapefiles, heights.keys()):
        # Calcula el volumen de la superficie usando el promedio
        volume_info_average = calculate_surface_volume(dem, heights[year]["mean"], "mean", year)
        # Calcula el volumen de la superficie usando la mediana
        volume_info_median = calculate_surface_volume(dem, heights[year]["median"], "median", year)
        
        print(f"Año: {year}, Volumen (Promedio): {volume_info_average}, Volumen (Mediana): {volume_info_median}")

def calculate_surface_volume(dem, reference_height, height_type, year):
    out_surface_volume = f"C:\\Workspace\\LagoValencia\\documentos\\volumenes\\SurfaceVolume_{year}_{height_type}.txt"
    reference_plane = "BELOW"
    z_factor = 1  # Ajusta si las unidades verticales del DEM son diferentes

    result = arcpy.ddd.SurfaceVolume(in_surface=dem, out_text_file=out_surface_volume,
                                     reference_plane=reference_plane, base_z=reference_height, 
                                     z_factor=z_factor, pyramid_level_resolution="0")
    return result.getOutput(0)

if __name__ == "__main__":
    main()