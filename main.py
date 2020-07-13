import arcpy, os
# -*- coding: utf-8 -*-
# TODO: permitir que reconozca las 'n'

path = u"C:\\SyK\\07_CARTOBASE\\data"
path_newsGDBs = u"C:\\SyK\\07_CARTOBASE\\data"

countryDic = {
    "e": "HERE 2020Q2 Espana",
    "p": "Portugal",
    "f": "F0CN201E1EF0000AACMN"
}

queryEsp = "POI_LANGCD = 'BAQ' OR POI_LANGCD = 'CAT' OR POI_LANGCD = 'GLG' OR POI_LANGCD = 'SPA'"
queryFra = "POI_LANGCD = 'FRE' OR POI_LANGCD = 'CAT'"
queryPor = "POI_LANGCD = 'POR'"

# Renombrado de archivos NamedPlc.shp
# for root, dirs, files in os.walk(path, topdown=True):
#     for name in files:
#         if name == "NamedPlc.shp":
#             if root.find("HERE 2020Q2 Espana") >= 0:
#                 m = "_e"
#             elif root.find("Portugal") >= 0:
#                 m = "_p"
#             elif root.find("F0CN201E1EF0000AACMN") >= 0:
#                 m = "_f"
#             k = root.split('\\')[len(root.split('\\')) - 1][1]
#             newName = os.path.splitext(name)[0] + m + k + os.path.splitext(name)[1]
#             if name != newName:
#                 arcpy.Rename_management(os.path.join(root, name), newName)
#
# Creacion de las nuevas gdbs
for root, dirs, files in os.walk(path, topdown=True):
    for dir in dirs:
        if dir == "HERE 2020Q2 Espana":
            m = "_e"
        elif dir == "Portugal":
            m = "_p"
        elif dir == "F0CN201E1EF0000AACMN":
            m = "_f"
        if arcpy.Exists(os.path.join(path_newsGDBs,"Mapa_Base" + m + ".gdb")):
            arcpy.Delete_management(os.path.join(path_newsGDBs,"Mapa_Base" + m + ".gdb"))
        arcpy.CreateFileGDB_management(path_newsGDBs, "Mapa_Base" + m + ".gdb")
    break

# Merge por paises
for gdb in os.listdir(path_newsGDBs):
    if os.path.splitext(gdb)[1] == ".gdb":
        arcpy.env.workspace = os.path.join(path_newsGDBs, gdb)
        shpToMerge = []
        for root, dirs, files in os.walk(os.path.join(path, countryDic.get(gdb[10])), topdown=True):
            for name in files:
                if name.find("NamedPlc") >= 0 and os.path.splitext(name)[1] == ".shp":
                    shpToMerge.append(os.path.join(root,name))
        arcpy.Merge_management(shpToMerge,"NamedPlc")

# Eliminacion poblaciones repetidas en NamedPlc
for gdb in os.listdir(path_newsGDBs):
    if os.path.splitext(gdb)[1] == ".gdb":
        arcpy.env.workspace = os.path.join(path_newsGDBs, gdb)
        if os.path.splitext(gdb)[0] == "Mapa_Base_e":
            query = queryEsp
        elif os.path.splitext(gdb)[0] == "Mapa_Base_f":
            query = queryFra
        elif os.path.splitext(gdb)[0] == "Mapa_Base_p":
            query = queryPor
        arcpy.MakeFeatureLayer_management("NamedPlc", "NamedPlcLyr")
        arcpy.MakeFeatureLayer_management(arcpy.SelectLayerByAttribute_management("NamedPlcLyr", "NEW_SELECTION", query), "selectLyr")
        arcpy.DeleteRows_management(arcpy.SelectLayerByAttribute_management("selectLyr", "SWITCH_SELECTION"))
        arcpy.MakeFeatureLayer_management("NamedPlc", "NamedPlcLyr2")
        # TODO: La siguiente seleccion elimina todas las entidades menos Gibraltar (en el caso de España)
        arcpy.DeleteRows_management(arcpy.SelectLayerByAttribute_management("NamedPlcLyr2", "NEW_SELECTION", "POI_NMTYPE <> 'B'"))
        print "Filas en NamedPlc despues de delete2: " + str(arcpy.GetCount_management("NamedPlc").getOutput(0))
        print "Filas en NamedPlcLyr2 despues de delete2: " + str(arcpy.GetCount_management("NamedPlcLyr2").getOutput(0))
        arcpy.Delete_management("selectLyr")
        arcpy.Delete_management("NamedPlcLyr")
        arcpy.Delete_management("NamedPlcLyr2")

# Creacion y calculo de campos ADMINCLASS, NAME y DISPCLASS
for gdb in os.listdir(path_newsGDBs):
    if os.path.splitext(gdb)[1] == ".gdb":
        arcpy.env.workspace = os.path.join(path_newsGDBs, gdb)
        arcpy.AddField_management("NamedPlc", "ADMINCLASS", "Short")
        arcpy.AddField_management("NamedPlc", "NAME", "Text", 100)
        arcpy.AddField_management("DISPCLASS", "Short")
        with arcpy.da.UpdateCursor("NamedPlc", ["POI_NAME", "CAPITAL", "POPULATION", "ADMINCLASS", "NAME", "DISPCLASS"]) as cursor:
            for row in cursor:

                # Se calcula campo ADMINCLASS
                if row[1] == "1":
                    row[3] = 0
                elif row[1] == "2":
                    row[3] = 1
                elif row[1] == "3":
                    row[3] = 7
                elif row[1] == " " and row[2] != 0:
                    row[3] = 8
                elif row[1] == " " and row[2] == 0:
                    row[3] = 9

                # Se calcula campo NAME
                row[4] = row[0].capitalize()

                # Se calcula campo DISPCLASS
                if row[2] > 800000:
                    row[5] = 2
                elif row[2] <= 800000 and row[2] > 500000:
                    row[5] = 4
                elif row[2] <= 500000 and row[2] > 250000:
                    row[5] = 5
                elif row[2] <= 250000 and row[2] > 150000:
                    row[5] = 7
                elif row[2] <= 150000 and row[2] > 80000:
                    row[5] = 8
                elif row[2] <= 80000 and row[2] > 10000:
                    row[5] = 10
                elif row[2] <= 10000 and row[2] > 0:
                    row[5] = 11
                elif row[2] == 0:
                    row[5] = 12
                cursor.updateRow(row)