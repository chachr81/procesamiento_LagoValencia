#Importar librerias
import arcpy
from arcpy.sa import *
import numpy as np
import matplotlib.pyplot as plt

# Habilitar la extensión 'Spatial'
arcpy.CheckOutExtension("Spatial")

# Definir espacio de trabajo
arcpy.env.workspace = r"C:\\Workspace\\LagoValencia\\LagoValencia.gdb"
arcpy.env.overwriteOutput = True

# Definir el sistema de coordenadas de destino (EPSG 2202)
output_coordinate_system = arcpy.SpatialReference(2202)

# Definir carpeta para guardar los histogramas
output_folder = r"C:\\Workspace\\LagoValencia\\datos"

# Datos de Entrada (actualizado para usar rasters en stack)
stack_bandas = {
    
    '1986': (r"C:\\Workspace\\LagoValencia\\raster\\imagenes_corregidas\\1986.tif", 'Green', 'NearInfrared_2'),
    '1990': (r"C:\\Workspace\\LagoValencia\\raster\\imagenes_corregidas\\1990.tif", 'Green', 'NearInfrared_2'),
    '2000': (r"C:\\Workspace\\LagoValencia\\raster\\imagenes_corregidas\\2000.tif", 'sr_band2', 'sr_band5'),
    '2014': (r"C:\\Workspace\\LagoValencia\\raster\\imagenes_corregidas\\2014.tif", 'Green', 'ShortWaveInfrared_1'),
    '2019': (r"C:\\Workspace\\LagoValencia\\raster\\imagenes_corregidas\\2019.tif", 'Green', 'ShortWaveInfrared_1'),
    '2023': (r"C:\\Workspace\\LagoValencia\\raster\\imagenes_corregidas\\2023.tif", 'sr_band3', 'sr_band6')
}

def calcular_mndwi(stack_path, green_band_name, swir_band_name, output_raster):
    """Calcula el MNDWI a partir de un stack de rasters usando los nombres de las bandas"""
    # Usar los nombres de las bandas del stack
    green_raster = Raster(stack_path + "\\" + green_band_name)
    swir_raster = Raster(stack_path + "\\" + swir_band_name)                                                                                             
    
    # Calcular el MNDWI
    mndwi = Float(green_raster - swir_raster) / Float(green_raster + swir_raster)
    # Guardar el resultado
    mndwi.save(output_raster)
    return mndwi

def generar_histograma(mndwi, mndwi_raster):
    """Genera los histogramas y los guarda"""
    mndwi_array = arcpy.RasterToNumPyArray(mndwi, nodata_to_value=np.nan)
    mndwi_flat = mndwi_array.flatten()
    mndwi_flat = mndwi_flat[~np.isnan(mndwi_flat)]

    plt.hist(mndwi_flat, bins=256, color='blue', alpha=0.7)
    plt.axvline(x=np.median(mndwi_flat), color='red', linestyle='dashed')
    plt.title('Histograma de ' + mndwi_raster)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.savefig(output_folder + "\\" + mndwi_raster + "_histogram.png")
    plt.close()

def clasificar_lago(mndwi_raster, output_classified):
    """Clasifica el ráster MNDWI en Lago (1) y No Lago (0)"""
    mndwi = Raster(mndwi_raster)
    classified = Con(mndwi > 0, 1, 0)
    classified.save(output_classified)

def proyectar_feature_class(input_fc, output_fc):
    """Proyecta el feature class a EPSG 2202"""
    # Reemplazar caracteres no válidos en el nombre de archivo de salida
    output_fc_valid = arcpy.ValidateTableName(output_fc)

    # Proyectar el feature class y asignar el resultado a una nueva variable
    projected_fc = arcpy.Project_management(input_fc, output_fc_valid, output_coordinate_system)
    return projected_fc

# Calcular MNDWI y clasificar por cada año
for year, (stack_path, green_index, swir_index) in stack_bandas.items():
    mndwi_raster = "MNDWI_" + year
    classified_raster = "MNDWI_" + year + "_classified"
    mndwi = calcular_mndwi(stack_path, green_index, swir_index, mndwi_raster)
    generar_histograma(mndwi, mndwi_raster)
    clasificar_lago(mndwi_raster, classified_raster)

    mndwi_array = arcpy.RasterToNumPyArray(mndwi, nodata_to_value=np.nan)
    mndwi_flat = mndwi_array.flatten()
    mndwi_flat = mndwi_flat[~np.isnan(mndwi_flat)]
    valor_critico = np.median(mndwi_flat)
    print(f"El valor crítico para el año {year} es {valor_critico}")

    # Transformar los MNDWI reclasificados a shapefile
    classified_shapefile = "MNDWI_" + year + "_classified.shp"
    arcpy.RasterToPolygon_conversion(classified_raster, classified_shapefile, "NO_SIMPLIFY")

    # Proyectar el shapefile a EPSG 2202
    output_fc = arcpy.env.workspace + "\\" + "MNDWI_" + year + "_classified_projected_corrected.shp"
    output_fc = output_fc.replace(" ", "_")  # Reemplazar espacios en blanco por guiones bajos
    projected_fc = proyectar_feature_class(classified_shapefile, output_fc)

print('Script Terminado')
