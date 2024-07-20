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

def calcular_ndbi(nir_band_path, swir_band_path, output_raster):
    """Calcula el NDBI"""
    nir_raster = Raster(nir_band_path)
    swir_raster = Raster(swir_band_path)
    ndbi = (swir_raster - nir_raster) / (swir_raster + nir_raster)
    ndbi.save(output_raster)
    return ndbi

def generar_histograma(ndbi, ndbi_raster):
    """Genera los histogramas y los guarda"""
    ndbi_array = arcpy.RasterToNumPyArray(ndbi, nodata_to_value=np.nan)
    ndbi_flat = ndbi_array.flatten()
    ndbi_flat = ndbi_flat[~np.isnan(ndbi_flat)]

    plt.hist(ndbi_flat, bins=256, color='blue', alpha=0.7)
    plt.axvline(x=np.median(ndbi_flat), color='red', linestyle='dashed')
    plt.title('Histogram of ' + ndbi_raster)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.savefig(output_folder + "\\" + ndbi_raster + "_histogram.png")
    plt.close()
    
    # Imprimir el valor crítico
    print(f"El valor crítico para {ndbi_raster} es: {np.median(ndbi_flat)}")

def clasificar_urbano(ndbi_raster, output_classified):
    """Clasifica el ráster NDBI en Urbano (1) y No Urbano (0)"""
    ndbi = Raster(ndbi_raster)
    classified = Con(ndbi > 0, 1, 0)  # Usando la mediana como valor crítico
    classified.save(output_classified)

def proyectar_feature_class(input_fc, output_fc):
    """Proyecta el feature class a EPSG 2202"""
    # Reemplazar caracteres no válidos en el nombre de archivo de salida
    output_fc_valid = arcpy.ValidateTableName(output_fc)

    # Proyectar el feature class y asignar el resultado a una nueva variable
    projected_fc = arcpy.Project_management(input_fc, output_fc_valid, output_coordinate_system)
    return projected_fc

# Rutas a las bandas de las imágenes
nir_band_path_1 = r"C:\Workspace\LagoValencia\raster\OLI_TIRS004053_20190119\LC08_L1TP_004053_20190119_20200830_02_T1_B5.TIF"
swir_band_path_1 = r"C:\Workspace\LagoValencia\raster\OLI_TIRS004053_20190119\LC08_L1TP_004053_20190119_20200830_02_T1_B6.TIF"
nir_band_path_2 = r"C:\Workspace\LagoValencia\raster\OLI_TIRS005053_20190211\LC08_L1TP_005053_20190211_20200829_02_T1_B5.TIF"
swir_band_path_2 = r"C:\Workspace\LagoValencia\raster\OLI_TIRS005053_20190211\LC08_L1TP_005053_20190211_20200829_02_T1_B6.TIF"

# Calcular NDBI y clasificar
for date, (nir, swir) in {"20190119": (nir_band_path_1, swir_band_path_1), "20190211": (nir_band_path_2, swir_band_path_2)}.items():
    ndbi_raster = f"NDBI_{date}"
    ndbi = calcular_ndbi(nir, swir, ndbi_raster)
    generar_histograma(ndbi, ndbi_raster)
    classified_raster = ndbi_raster + "_classified"
    clasificar_urbano(ndbi_raster, classified_raster)
    
    # Convertir el raster clasificado a shapefile
    classified_shapefile = classified_raster + ".shp"
    arcpy.RasterToPolygon_conversion(classified_raster, classified_shapefile, "NO_SIMPLIFY")
    
    # Proyectar el shapefile a EPSG 2202
    projected_shapefile = classified_raster + "_projected.shp"
    proyectar_feature_class(classified_shapefile, projected_shapefile)

print('Script Terminado')