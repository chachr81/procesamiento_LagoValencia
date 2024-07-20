# Modulo de Construcción de MNDWI

import arcpy
from arcpy.sa import *

# Habilitar la extensión 'Spatial'
arcpy.CheckOutExtension("Spatial")

# Definiendo espacio de trabajo
arcpy.env.workspace = r"C:\Workspace\LagoValencia\LagoValencia.gdb"
arcpy.env.overwriteOutput = True

# Datos de Entrada
# Rutas de las bandas de imágenes satelitales
# [Año: (Green band, SWIR band)]
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
    """Calcula el MNDWI dado los archivos ráster de la banda verde y SWIR"""
    green_raster = Raster(green_band)
    swir_raster = Raster(swir_band)
    mndwi = (green_raster - swir_raster) / (green_raster + swir_raster)
    mndwi.save(output_raster)

def clasificar_lago(mndwi_raster, output_classified):
    """Clasifica el ráster MNDWI en Lago (1) y No Lago (0)"""
    classified = Con(Raster(mndwi_raster) > 0, 1, 0)
    classified.save(output_classified)
# Calcular MNDWI y clasificar por cada año
for year, (green, swir) in bandas.items():
    mndwi_raster = "MNDWI_" + year
    classified_raster = "MNDWI_" + year + "_classified"
    calcular_mndwi(green, swir, mndwi_raster)
    clasificar_lago(mndwi_raster, classified_raster)
print('Script Terminado')