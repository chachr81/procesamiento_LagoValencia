import arcpy
from arcpy import env
from arcpy.sa import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def main():
    # Configura el entorno de trabajo
    env.workspace = r"D:\Workspace\LagoValencia\LagoValencia.gdb"
    env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")

    # Rutas de los polígonos
    polygon_paths = [
        r"D:\Workspace\LagoValencia\LagoValencia.gdb\lago1986_corrected",
        r"D:\Workspace\LagoValencia\LagoValencia.gdb\lago1990_corrected",
        r"D:\Workspace\LagoValencia\LagoValencia.gdb\lago2000_corrected",
        r"D:\Workspace\LagoValencia\LagoValencia.gdb\lago2014_corrected",
        r"D:\Workspace\LagoValencia\LagoValencia.gdb\lago2019_corrected",
        r"D:\Workspace\LagoValencia\LagoValencia.gdb\lago2023_corrected"
    ]

    # Define la ruta al DEM
    dem = r"D:\Workspace\LagoValencia\LagoValencia.gdb\mde_corregido_TRfinal2000"
    dem_raster = arcpy.Raster(dem)
    dem_array = arcpy.RasterToNumPyArray(dem)
    lower_left = arcpy.Point(dem_raster.extent.XMin, dem_raster.extent.YMin)
    cell_size = dem_raster.meanCellWidth

    # Lista de polilíneas para procesar
    polyline_fcs = []

    # Convierte polígonos a líneas
    for polygon_path in polygon_paths:
        # Extraer el año del archivo usando el nombre
        year = polygon_path.split('lago')[-1].split('_')[0]
        output_line = f"PolygonToLine_{year}"

        # Validar el nombre de la salida
        valid_output_line = arcpy.ValidateTableName(output_line, env.workspace)

        # Comprobar si la salida ya existe
        if arcpy.Exists(valid_output_line):
            print(f"Advertencia: La salida {valid_output_line} ya existe. Se omitirá este paso.")
        else:
            # Ejecutar la herramienta PolygonToLine
            try:
                arcpy.management.PolygonToLine(polygon_path, valid_output_line)
                print(f"Polígono convertido a líneas para el año {year}: {valid_output_line}")
                polyline_fcs.append(valid_output_line)
            except Exception as e:
                print(f"Error al convertir el polígono {polygon_path} a líneas: {e}")
                continue

    # Lista para guardar las estadísticas
    stats_data = []

    # Procesar cada línea
    for polyline_fc in polyline_fcs:
        year = polyline_fc.split('_')[-1]  # Extraer el año del nombre
        elevation_values, vertex_count = process_polyline(polyline_fc, dem_array, lower_left, cell_size)
        stats = report_elevation_statistics(elevation_values, vertex_count, year)
        stats_data.append(stats)

    # Crear un DataFrame con los datos y exportar a Excel
    df = pd.DataFrame(stats_data, columns=["Año", "Mínima", "Máxima", "Media", "Mediana", "Moda", "DE", "CV"])
    output_excel = r"D:\Workspace\LagoValencia\documentos\alturas_espejo\estadisticas_elevacion.xlsx"
    df.to_excel(output_excel, index=False, sheet_name="Estadísticas")
    print(f"Archivo Excel generado: {output_excel}")


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
    median = np.median(elevation_array)
    std = np.std(elevation_array)
    lower_bound = median - 1 * std  # 1 desviación estándar por debajo de la media
    upper_bound = median + 0.3 * std  # 1 desviación estándar por encima de la media

    # Filtrar los valores dentro del rango permitido
    filtered_array = elevation_array[(elevation_array >= lower_bound) & (elevation_array <= upper_bound)]

    # Verificar si el arreglo filtrado está vacío
    if filtered_array.size == 0:
        print(f"Advertencia: El arreglo de elevaciones filtrado está vacío para el año {year}.")
        return [year, None, None, None, None, None, None, None]

    # Cálculo de estadísticas sobre los datos filtrados
    minima = np.min(filtered_array)
    maxima = np.max(filtered_array)
    media = np.mean(filtered_array)
    mediana = np.median(filtered_array)
    varianza = np.var(filtered_array)
    std_filtered = np.std(filtered_array)
    coeficiente_variacion = (std_filtered / media) * 100  # Resultado en porcentaje
    
    # Cálculo de la moda usando bins del histograma
    hist, bin_edges = np.histogram(filtered_array, bins=256)
    bin_index = np.argmax(hist)
    moda_hist = (bin_edges[bin_index] + bin_edges[bin_index + 1]) / 2

    # Generar el histograma
    plt.hist(filtered_array, bins=256, color='blue', alpha=0.7)
    plt.axvline(x=mediana, color='red', linestyle='dashed', label='Median')
    plt.title(f'Distribución de los valores de elevación - {year}')
    plt.xlabel('Elevación')
    plt.ylabel('Frecuencia')
    plt.legend()
    plt.savefig(f"D:\\Workspace\\LagoValencia\\documentos\\alturas_espejo\\histograma_elevacion_{year}.png")
    plt.close()

    # Imprimir estadísticas en consola
    print(f"Estadísticas para el año {year} (sin valores atípicos):")
    print(f"  Vértices procesados: {vertex_count}")
    print(f"  Min: {minima}, Max: {maxima}")
    print(f"  Mean: {media}, Median: {mediana}")
    print(f"  Std: {std_filtered}, Var: {varianza}, CV: {coeficiente_variacion}%")
    print(f"  Moda (basada en histograma): {moda_hist}")

    # Retornar estadísticas para el Excel
    return [year, minima, maxima, media, mediana, moda_hist, std_filtered, coeficiente_variacion]


if __name__ == "__main__":
    main()
