"""Construcción de Modelo digital continuo
"""
# Importacion de librerías
import arcpy
from arcpy import env
from arcpy.sa import RasterCalculator

# Definiendo espacio de trabajo
arcpy.env.workspace = r"C:\Workspace\LagoValencia\LagoValencia.gdb"
arcpy.env.overwriteOutput = True
# Definiendo datos de entrada
mde_100000 = r"C:\Workspace\LagoValencia\LagoValencia.gdb\N10W068_clip"
ASCII = r"C:\Workspace\LagoValencia\datos previos\estudio batimetrico\Sort\valenciasel100.xyz"
# Definiendo sistema de coordenadas
sr = arcpy.SpatialReference(2202)
# Crear una capa de puntos a partir del archivo XYZ de batimetría
capa_puntos = arcpy.ddd.ASCII3DToFeatureClass(
    input=ASCII,
    in_file_type="XYZ",
    out_feature_class=r"C:\Workspace\LagoValencia\LagoValencia.gdb\puntos1",
    out_geometry_type="POINT",
    z_factor=1,
    input_coordinate_system=sr,
    average_point_spacing=None,
    file_suffix="",
    decimal_separator="DECIMAL_POINT",
)
arcpy.AddXY_management(capa_puntos)
topo_fc = r"C:\Workspace\LagoValencia\LagoValencia.gdb\puntos1 POINT_Z PointElevation"
# Desarrollar MDE con valores Negativos
mde_bat = arcpy.ddd.TopoToRaster(
    in_topo_features=topo_fc,
    out_surface_raster="mde_bat",
    cell_size=30,
    enforce="ENFORCE",
    data_type="SPOT",
)
# Desarrollar MDE con valores en metros
mde_completo = arcpy.sa.RasterCalculator(
    rasters=[mde_100000, "mde_bat"],
    input_names=["mde1", "mde2"],
    expression="mde1 + mde2",
)
mde_completo.save(r"C:\Workspace\LagoValencia\LagoValencia.gdb\mde_completo")
# Añadir datos de Altura a los puntos en metros
arcpy.sa.AddSurfaceInformation(
    in_feature_class="puntos1",
    in_surface="mde_completo",
    out_property="Z",
    method="BILINEAR",
    sample_distance=None,
    z_factor=1,
    pyramid_level_resolution=0,
    noise_filtering="",
)
# Aplicar Contour al MDE1
lineas1 = arcpy.sa.Contour(
    mde_100000, r"C:\Workspace\LagoValencia\LagoValencia.gdb\lineas3", 10
)

# Extraer líneas de contorno del MDE Completo
lineas2 = arcpy.sa.Contour(
    mde_completo, r"C:\Workspace\LagoValencia\LagoValencia.gdb\lineas4", 10
)

# Aplicar TopoToRaster con contornos y puntos
arcpy.ddd.TopoToRaster(
    in_topo_features="puntos1 Z PointElevation;lineas3 Contour Contour;lineas4 Contour Contour",
    out_surface_raster=r"C:\Workspace\LagoValencia\LagoValencia.gdb\mde_integrado1",
    extent='608664.424127324 1104797.38249404 664864.424127325 1142557.38249404 PROJCS["REGVEN_UTM_Zone_19N".GEOGCS["GCS_REGVEN".DATUM["D_REGVEN".SPHEROID["GRS_1980".6378137.0.298.257222101]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]].PROJECTION["Transverse_Mercator"].PARAMETER["False_Easting".500000.0].PARAMETER["False_Northing".0.0].PARAMETER["Central_Meridian".-69.0].PARAMETER["Scale_Factor".0.9996].PARAMETER["Latitude_Of_Origin".0.0].UNIT["Meter".1.0]]',
    cell_size=30,
    enforce="ENFORCE",
    data_type="SPOT",
)
print('Script Terminado')