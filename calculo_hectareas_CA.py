import arcpy

arcpy.env.workspace = "C:\\Workspace\\LagoValencia\\LagoValencia.gdb"
arcpy.env.overwriteOutput = True

# Define las rutas de los shapefiles de entrada y salida
suelos_shapefile = r"C:\\Workspace\\LagoValencia\\LagoValencia.gdb\\mapasuelos_attr_poten"
lago_2019_shapefile = r"C:\\Workspace\\LagoValencia\\LagoValencia.gdb\\lago2019"
resultado_erase = r"C:\\Workspace\\LagoValencia\\LagoValencia.gdb\\suelos_sin_lago2019"

# Realiza el geoproceso PairwiseErase
arcpy.analysis.PairwiseErase(suelos_shapefile, lago_2019_shapefile, resultado_erase)

# Realiza una selección de los registros con aptitud '1 Muy apta' y '2 Mod_apta'
consulta = "CANA_AZUCAR IN ('1 Muy apta', '2 Mod_apta')"
arcpy.management.SelectLayerByAttribute(resultado_erase, "NEW_SELECTION", consulta)

# Calcula las hectáreas (suponiendo que el campo de área está en metros cuadrados)
arcpy.management.AddField(resultado_erase, "HECTAREAS", "DOUBLE")
arcpy.management.CalculateField(resultado_erase, "HECTAREAS", "!shape.area@hectares!", "PYTHON3")

# Totaliza las hectáreas por aptitud y las imprime en consola
with arcpy.da.SearchCursor(resultado_erase, ["CANA_AZUCAR", "HECTAREAS"]) as cursor:
    total_muy_apta = 0
    total_mod_apta = 0
    for row in cursor:
        if row[0] == '1 Muy apta':
            total_muy_apta += row[1]
        elif row[0] == '2 Mod_apta':
            total_mod_apta += row[1]

print(f"Total hectáreas 'Muy apta': {total_muy_apta}")
print(f"Total hectáreas 'Mod apta': {total_mod_apta}")
print(f"Total hectáreas: {total_muy_apta + total_mod_apta}")