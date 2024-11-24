import arcpy
import numpy as np
import matplotlib.pyplot as plt

# Configuración del entorno
arcpy.env.workspace = r"D:\Workspace\LagoValencia\LagoValencia.gdb"
raster_path = "mde_integrado"
output_folder = r"C:\Workspace\LagoValencia\datos\perfil"

# Asegurarse de que las salidas puedan sobrescribirse
arcpy.env.overwriteOutput = True

# Función para crear una polilínea entre dos puntos y convertirla en puntos
def create_profile_line_as_points(start_point, end_point, num_points, line_name):
    # Crear la polilínea
    line_fc_path = arcpy.CreateFeatureclass_management(
        output_folder, f"{line_name}.shp", "POLYLINE",
        spatial_reference=arcpy.SpatialReference(2202)  # Asumimos WGS 84, reemplazar con el SR correcto
    )[0]
    array = arcpy.Array([arcpy.Point(*start_point), arcpy.Point(*end_point)])
    polyline = arcpy.Polyline(array)
    with arcpy.da.InsertCursor(line_fc_path, ["SHAPE@"]) as cursor:
        cursor.insertRow([polyline])
    
    # Convertir la polilínea en una serie de puntos
    point_fc_path = arcpy.CreateFeatureclass_management(
        output_folder, f"{line_name}_points.shp", "POINT",
        has_z="ENABLED", spatial_reference=arcpy.SpatialReference(4326)
    )[0]
    
    for i in range(num_points):
        point = polyline.positionAlongLine(float(i)/(num_points-1), True).firstPoint
        arcpy.da.InsertCursor(point_fc_path, ["SHAPE@"]).insertRow([point])
    
    # Añadir información de elevación del MDE a los puntos
    arcpy.ddd.AddSurfaceInformation(point_fc_path, raster_path, "Z", "BILINEAR")

    # Extraer la información de elevación para graficar
    z_values = [row[0] for row in arcpy.da.SearchCursor(point_fc_path, "SHAPE@Z")]
    return z_values

# Crear puntos para los perfiles
num_points = 1000
perfil_ns = create_profile_line_as_points((639804.76, 1136781.41), (639804.76, 1116181.41), num_points, "perfil_ns")
perfil_eo = create_profile_line_as_points((655304.76, 1126481.41), (624304.76, 1126481.41), num_points, "perfil_eo")

# Función para graficar el perfil topográfico
def plot_profile(profile_values, profile_name):
    plt.figure(figsize=(10, 4))
    plt.plot(np.linspace(0, 1, num_points), profile_values, marker='o')
    plt.title(f"Perfil Topográfico {profile_name.replace('_', ' ').title()}")
    plt.xlabel("Fracción de Distancia")
    plt.ylabel("Elevación")
    plt.grid(True)
    plt.savefig(f"{output_folder}\\{profile_name}_profile.png")
    plt.show()

# Graficar perfiles
plot_profile(perfil_ns, "perfil_ns")
plot_profile(perfil_eo, "perfil_eo")
