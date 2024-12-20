"""Modulo de Calculo de Superficies de Inundación (MNDWI, condicional de mediana para clasificación por Árbol de decisión)
"""
#Importar librerias
import arcpy
from arcpy.sa import *
import numpy as np
import matplotlib.pyplot as plt

# Habilitar la extensión 'Spatial'
arcpy.CheckOutExtension("Spatial")

# Definir espacio de trabajo
arcpy.env.workspace = r"C:\Workspace\LagoValencia\LagoValencia.gdb"
arcpy.env.overwriteOutput = True

# Definir el sistema de coordenadas de destino (EPSG 2202)
output_coordinate_system = arcpy.SpatialReference(2202)

# Definir carpeta para guardar los histogramas
output_folder = r"C:\Workspace\LagoValencia\datos"

# Datos de Entrada
bandas = {
    '1976': (r"C:\Workspace\LagoValencia\raster\MSS004053_22_12_1975\LM02_L1TP_004053_19751222_20200908_02_T2_B4.TIF",
             r"C:\Workspace\LagoValencia\raster\MSS004053_22_12_1975\LM02_L1TP_004053_19751222_20200908_02_T2_B7.TIF"),
    '1986': (r"C:\Workspace\LagoValencia\raster\TM004053_24_01_1986\LT05_L1TP_004053_19860124_20200918_02_T1_B2.TIF",
             r"C:\Workspace\LagoValencia\raster\TM004053_24_01_1986\LT05_L1TP_004053_19860124_20200918_02_T1_B5.TIF"),
    '1990': (r"C:\Workspace\LagoValencia\raster\TM004053_19_01_1990\LT05_L1TP_004053_19900119_20200916_02_T1_B2.TIF",
             r"C:\Workspace\LagoValencia\raster\TM004053_19_01_1990\LT05_L1TP_004053_19900119_20200916_02_T1_B5.TIF"),
    '2000': (r"C:\Workspace\LagoValencia\raster\ETM+_23_01_2000\LE07_L1TP_004053_20000123_20200918_02_T1_B2.TIF",
             r"C:\Workspace\LagoValencia\raster\ETM+_23_01_2000\LE07_L1TP_004053_20000123_20200918_02_T1_B5.TIF"),
    '2014': (r"C:\Workspace\LagoValencia\raster\OLI_TIRS004053_20140121\LC08_L1TP_004053_20140121_20200912_02_T1_B3.TIF",
             r"C:\Workspace\LagoValencia\raster\OLI_TIRS004053_20140121\LC08_L1TP_004053_20140121_20200912_02_T1_B6.TIF"),
    '2019': (r"C:\Workspace\LagoValencia\raster\OLI_TIRS004053_20190119\LC08_L1TP_004053_20190119_20200830_02_T1_B3.TIF",
             r"C:\Workspace\LagoValencia\raster\OLI_TIRS004053_20190119\LC08_L1TP_004053_20190119_20200830_02_T1_B6.TIF")
}

def calcular_mndwi(green_band, swir_band, output_raster):
    """Calcula el MNDWI"""
    green_raster = Raster(green_band)
    swir_raster = Raster(swir_band)
    mndwi = (green_raster - swir_raster) / (green_raster + swir_raster)
    mndwi.save(output_raster)
    return mndwi

def generar_histograma(mndwi, mndwi_raster):
    """Genera los histogramas y los guarda"""
    mndwi_array = arcpy.RasterToNumPyArray(mndwi, nodata_to_value=np.nan)
    mndwi_flat = mndwi_array.flatten()
    mndwi_flat = mndwi_flat[~np.isnan(mndwi_flat)]

    plt.hist(mndwi_flat, bins=256, color='blue', alpha=0.7)
    plt.axvline(x=np.median(mndwi_flat), color='red', linestyle='dashed')
    plt.title('Histogram of ' + mndwi_raster)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.savefig(output_folder + "\\" + mndwi_raster + "_histogram.png")
    plt.close()

def clasificar_lago(mndwi_raster, output_classified, valor_critico):
    """Clasifica el ráster MNDWI en Lago (1) y No Lago (0)"""
    mndwi = Raster(mndwi_raster)
    classified = Con(mndwi > valor_critico, 1, 0)
    classified.save(output_classified)

def proyectar_feature_class(input_fc, output_fc):
    """Proyecta el feature class a EPSG 2202"""
    output_fc_valid = arcpy.ValidateTableName(output_fc)
    projected_fc = arcpy.Project_management(input_fc, output_fc_valid, output_coordinate_system)
    return projected_fc

# Calcular MNDWI y clasificar por cada año
for year, (green, swir) in bandas.items():
    mndwi_raster = "MNDWI_" + year
    classified_raster = "MNDWI_" + year + "_classified"
    mndwi = calcular_mndwi(green, swir, mndwi_raster)
    generar_histograma(mndwi, mndwi_raster)
    
    mndwi_array = arcpy.RasterToNumPyArray(mndwi, nodata_to_value=np.nan)
    mndwi_flat = mndwi_array.flatten()
    mndwi_flat = mndwi_flat[~np.isnan(mndwi_flat)]
    valor_critico = np.median(mndwi_flat)
    
    print(f"El valor crítico para el año {year} es {valor_critico}")  # Imprimir el valor crítico
    
    clasificar_lago(mndwi_raster, classified_raster, valor_critico)

    # Transformar los MNDWI reclasificados a shapefile
    classified_shapefile = "MNDWI_" + year + "_classified.shp"
    arcpy.RasterToPolygon_conversion(classified_raster, classified_shapefile, "NO_SIMPLIFY")

    # Proyectar el shapefile a EPSG 2202
    output_fc = arcpy.env.workspace + "\\" + "MNDWI_" + year + "_classified_projected.shp"
    output_fc = output_fc.replace(" ", "_")  # Reemplazar espacios en blanco por guiones bajos
    projected_fc = proyectar_feature_class(classified_shapefile, output_fc)

print('Script Terminado')