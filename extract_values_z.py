import arcpy
from arcpy import env
from arcpy.sa import *
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

def main():
    # Configura el entorno de trabajo
    env.workspace = r"C:\Workspace\LagoValencia\LagoValencia.gdb"
    env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")

    # Rutas de los polígonos
    polygon_paths = [
        r"C:\Workspace\LagoValencia\shp\MNDWI_1986_classified.shp",
        r"C:\Workspace\LagoValencia\shp\MNDWI_1990_classified.shp",
        r"C:\Workspace\LagoValencia\shp\MNDWI_2000_classified.shp",
        r"C:\Workspace\LagoValencia\shp\MNDWI_2014_classified.shp",
        r"C:\Workspace\LagoValencia\shp\MNDWI_2019_classified.shp",
        r"C:\Workspace\LagoValencia\shp\MNDWI_2023_classified.shp"
    ]

    # Define la ruta al DEM
    dem = r"C:\Workspace\LagoValencia\LagoValencia.gdb\mde_corregido_TRfinal2000"
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
    elevation_array = np.array(elevation_values)
    varianza = np.var(elevation_array)
    coeficiente_variacion = (np.std(elevation_array) / np.mean(elevation_array)) * 100  # Resultado en porcentaje
    moda, count = stats.mode(elevation_array)  # Cálculo de la moda

    plt.hist(elevation_array, bins=256, color='blue', alpha=0.7)
    plt.axvline(x=np.median(elevation_array), color='red', linestyle='dashed', label='Median')
    plt.title(f'Distribución de los valores de elevación - {year}')
    plt.xlabel('Elevación')
    plt.ylabel('Frecuencia')
    plt.legend()
    plt.savefig(f"C:\\Workspace\\LagoValencia\\documentos\\alturas_espejo\\histograma_elevacion_{year}.png")
    plt.close()
    print(f"Total vertices procesados por año {year}: {vertex_count}")
    print(f"Min: {np.min(elevation_array)}, Max: {np.max(elevation_array)}, Mean: {np.mean(elevation_array)}, Median: {np.median(elevation_array)}, Std: {np.std(elevation_array)}, Var: {varianza}, CV: {coeficiente_variacion}%")
    print(f"Moda: {moda[0]} (aparece {count[0]} veces)")

if __name__ == "__main__":
    main()