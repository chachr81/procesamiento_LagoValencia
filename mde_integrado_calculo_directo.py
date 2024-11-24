import arcpy
from arcpy import env
from arcpy.sa import *

def configurar_entorno(ruta_trabajo, raster_referencia):
    """Configura el espacio de trabajo y las extensiones necesarias, ajustando el entorno al raster de referencia."""
    env.workspace = ruta_trabajo
    env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")
    env.extent = "MAXOF"
    

def crear_raster_desde_puntos(ruta_xyz, raster_salida, tamaño_celda, sistema_coordenadas):
    """Crea un raster a partir de datos de puntos utilizando TopoToRaster."""
    puntos = arcpy.ddd.ASCII3DToFeatureClass(ruta_xyz, "XYZ", "puntos_batimetricos", "POINT", z_factor=1, input_coordinate_system=sistema_coordenadas)
    lago = r'D:\Workspace\LagoValencia\shp\MNDWI_2000_classified.shp'
    input_features = [(puntos, "Shape.Z", "PointElevation"), (lago, "Shape", "Boundary")]
    
    try:
        result = arcpy.ddd.TopoToRaster(
            input_features, 
            out_surface_raster=raster_salida, 
            cell_size=tamaño_celda, 
            enforce="NO_ENFORCE",
            data_type="SPOT"
        )
        raster_puntos = result.getOutput(0)
        raster_ajustado = Raster(raster_puntos) + 410.26
        return raster_ajustado
    except Exception as e:
        arcpy.AddError(f"Error en TopoToRaster: {str(e)}")
        return None

def ajustar_y_resamplear_raster(raster_entrada, raster_salida, tamaño_resampleo):
    """Realiza un resampleo del raster."""
    return arcpy.Resample_management(raster_entrada, raster_salida, tamaño_resampleo, "CUBIC")

# Flujo principal
ruta_trabajo = r"D:\Workspace\LagoValencia\LagoValencia.gdb"
sr = arcpy.SpatialReference(2202)
mde_hipsometrico = Raster(r"D:\Workspace\LagoValencia\raster\modelo.tif")
configurar_entorno(ruta_trabajo, mde_hipsometrico)

mde_bat = crear_raster_desde_puntos(r"D:\Workspace\LagoValencia\datos previos\estudio batimetrico\Sort\valenciasel100.xyz", "batimetria_raster", 12, sr)
if mde_bat is not None:  # Cambio aquí para verificar correctamente la variable
    mde_bat_resampleado = ajustar_y_resamplear_raster(mde_bat, "batimetria_resampleada", "30 30")
    mde_corregido = CellStatistics([mde_hipsometrico, mde_bat_resampleado], "MEDIAN", "DATA")
    mde_corregido_TRfinal = r"D:\Workspace\LagoValencia\LagoValencia.gdb\mde_corregido_TRfinal2000"
    mde_corregido.save(mde_corregido_TRfinal)
    print('Proceso con TopoToRaster y resampleo completado exitosamente.')
else:
    print('Error en la creación del raster de batimetría. Verificar los logs de errores.')
