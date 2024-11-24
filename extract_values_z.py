import arcpy
from arcpy import env
from arcpy.sa import *
import numpy as np
import matplotlib.pyplot as plt

def main():
    # Configura el entorno de trabajo
    env.workspace = r"D:\Workspace\LagoValencia\LagoValencia.gdb"
    env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")

    # Rutas de los polígonos
    polygon_paths = [
        r"D:\Workspace\LagoValencia\shp\MNDWI_1986_classified.shp",
        r"D:\Workspace\LagoValencia\shp\MNDWI_1990_classified.shp",
        r"D:\Workspace\LagoValencia\shp\MNDWI_2000_classified.shp",
        r"D:\Workspace\LagoValencia\shp\MNDWI_2014_classified.shp",
        r"D:\Workspace\LagoValencia\shp\MNDWI_2019_classified.shp",
        r"D:\Workspace\LagoValencia\shp\MNDWI_2023_classified.shp"
    ]

    # Define la ruta al DEM
    dem = r"D:\Workspace\LagoValencia\LagoValencia.gdb\mde_corregido_TRfinal"
    dem_raster = arcpy.Raster(dem)
    dem_array = arcpy.RasterToNumPyArray(dem)
    lower_left = arcpy.Point(dem_raster.extent.XMin, dem_raster.extent.YMin)
    cell_size = dem_raster.meanCellWidth

    # Lista de polilíneas para procesar
    polyline_fcs = []

    # Convierte polígonos a líneas
    for polygon_path in polygon_paths:
        year = polygon_path.split('_')[-2]  # Asume que el año está antes de 'classified'
        output_line = f"PolygonToLine_{year}"
        arcpy.management.PolygonToLine(polygon_path, output_line)
        polyline_fcs.append(output_line)

    # Procesar cada línea
    for polyline_fc in polyline_fcs:
        elevation_values, vertex_count = process_polyline(polyline_fc, dem_array, lower_left, cell_size)
        report_elevation_statistics(elevation_values, vertex_count, polyline_fc.split('_')[-1])

def process_polyline(polyline_fc, dem_array, lower_left, cell_size):
    elevation_values = []
    vertex_count = 0
    with arcpy.da.SearchCursor(polyline_fc, ["SHAPE@"]) as cursor:
        for row in cursor:
            for part in row[0]:
                for pnt in part:
                    if pnt:
                        col = int((pnt.X - lower_left.X) / cell_size)
                        row = int((pnt.Y - lower_left.Y) / cell_size)
                        if (0 <= row < dem_array.shape[0]) and (0 <= col < dem_array.shape[1]):
                            elevation = dem_array[row, col]
                            elevation_values.append(elevation)
                            vertex_count += 1
    return elevation_values, vertex_count

def report_elevation_statistics(elevation_values, vertex_count, year):
    """
    Calcula estadísticas de elevación, excluyendo valores atípicos, y genera un histograma.
    """
    elevation_array = np.array(elevation_values)

    # Filtro de valores atípicos basado en desviaciones estándar
    mean = np.mean(elevation_array)
    std = np.std(elevation_array)
    lower_bound = mean - 1 * std  # 2 desviaciones estándar por debajo de la media
    upper_bound = mean + 0.1 * std  # 2 desviaciones estándar por encima de la media

    # Filtrar los valores dentro del rango permitido
    filtered_array = elevation_array[(elevation_array >= lower_bound) & (elevation_array <= upper_bound)]

    # Cálculo de estadísticas sobre los datos filtrados
    varianza = np.var(filtered_array)
    coeficiente_variacion = (np.std(filtered_array) / np.mean(filtered_array)) * 100  # Resultado en porcentaje
    
    # Cálculo de la moda usando numpy
    unique, counts = np.unique(filtered_array, return_counts=True)
    moda = unique[np.argmax(counts)]  # Valor más frecuente
    moda_count = counts[np.argmax(counts)]  # Número de ocurrencias de la moda

    # Generar el histograma
    plt.hist(filtered_array, bins=256, color='blue', alpha=0.7)
    plt.axvline(x=np.median(filtered_array), color='red', linestyle='dashed', label='Median')
    plt.title(f'Distribución de los valores de elevación - {year}')
    plt.xlabel('Elevación')
    plt.ylabel('Frecuencia')
    plt.legend()
    plt.savefig(f"D:\\Workspace\\LagoValencia\\documentos\\alturas_espejo\\histograma_elevacion_{year}.png")
    plt.close()

    # Imprimir estadísticas en consola
    print(f"Estadísticas para el año {year} (sin valores atípicos):")
    print(f"  Vértices procesados: {vertex_count}")
    print(f"  Min: {np.min(filtered_array)}, Max: {np.max(filtered_array)}")
    print(f"  Mean: {np.mean(filtered_array)}, Median: {np.median(filtered_array)}")
    print(f"  Std: {np.std(filtered_array)}, Var: {varianza}, CV: {coeficiente_variacion}%")
    print(f"  Moda: {moda} (aparece {moda_count} veces)")

if __name__ == "__main__":
    main()
