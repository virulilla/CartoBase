# coding: utf-8
import arcpy, os

path = u"C:\\SyK\\07_CARTOBASE\\data"
path_newsGDBs = u"C:\\SyK\\07_CARTOBASE\\data"

countryDic = {
    "e": u"HERE 2020Q2 España",
    "p": "Portugal",
    "f": "F0CN201E1EF0000AACMN"
}

feattypDic = {
    2000408: 9748,
    2000124: 9790,
    2000403: 9771,
    2000457: 9768,
    2000420: 9788,
    2000200: 9715,
    1907403: 9776,
    1900403: 9732,
    2000460: 9733,
    2000123: 9744,
    900103: 7170,
    900150: 7170,
    900130: 7170
}

query = "FEAT_COD =2000408 OR FEAT_COD =2000124 OR FEAT_COD =2000403 OR FEAT_COD =2000457 OR FEAT_COD =2000420 OR " \
        "FEAT_COD =2000200 OR FEAT_COD =1900403 OR FEAT_COD =900103 OR FEAT_COD =900150 OR FEAT_COD =900130 OR " \
        "FEAT_COD =2000460 OR FEAT_COD = 2000123 OR FEAT_COD = 1907403"

rsWGS84 = arcpy.SpatialReference(3857)


# Eliminacion de MapaBase.gdb
if arcpy.Exists(os.path.join(path_newsGDBs, "MapaBase.gdb")):
    arcpy.Delete_management(os.path.join(path_newsGDBs, "MapaBase.gdb"))

# Renombrado de archivos NamedPlc.shp
for root, dirs, files in os.walk(path, topdown=True):
    for name in files:
        if name == "NamedPlc.shp" or name == "WaterPoly.shp" or name == "WaterSeg.shp" or name == "Oceans.shp" or name == "LandUseA.shp" or name == "LandUseB.shp":
            if root.find("HERE 2020Q2 España") >= 0:
                m = "_e"
            elif root.find("Portugal") >= 0:
                m = "_p"
            elif root.find("F0CN201E1EF0000AACMN") >= 0:
                m = "_f"
            k = root.split('\\')[len(root.split('\\')) - 1][1]
            newName = os.path.splitext(name)[0] + m + k + os.path.splitext(name)[1]
            if name != newName:
                arcpy.Rename_management(os.path.join(root, name), newName)

# Creacion de las gdbs auxiliares
for root, dirs, files in os.walk(path, topdown=True):
    for dir in dirs:
        if dir == u"HERE 2020Q2 España":
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
        shpToMerge_NamedPlc = []
        shpToMerge_WaterPoly = []
        shpToMerge_WaterSeg = []
        shpToMerge_Oceans = []
        shpToMerge_LandUseA = []
        shpToMerge_LandUseB = []
        for root, dirs, files in os.walk(os.path.join(path, countryDic.get(gdb[10])), topdown=True):
            for name in files:
                if name.find("NamedPlc") >= 0 and os.path.splitext(name)[1] == ".shp":
                    shpToMerge_NamedPlc.append(os.path.join(root,name))
                if name.find("WaterPoly") >= 0 and os.path.splitext(name)[1] == ".shp":
                    shpToMerge_WaterPoly.append(os.path.join(root,name))
                if name.find("WaterSeg") >= 0 and os.path.splitext(name)[1] == ".shp":
                    shpToMerge_WaterSeg.append(os.path.join(root, name))
                if name.find("Oceans") >= 0 and os.path.splitext(name)[1] == ".shp":
                    shpToMerge_Oceans.append(os.path.join(root, name))
                if name.find("LandUseA") >= 0 and os.path.splitext(name)[1] == ".shp":
                    shpToMerge_LandUseA.append(os.path.join(root, name))
                if name.find("LandUseB") >= 0 and os.path.splitext(name)[1] == ".shp":
                    shpToMerge_LandUseB.append(os.path.join(root, name))
        arcpy.Merge_management(shpToMerge_NamedPlc, "NamedPlc")
        arcpy.Merge_management(shpToMerge_WaterPoly, "WaterPoly")
        arcpy.Merge_management(shpToMerge_WaterSeg, "WaterSeg")
        arcpy.Merge_management(shpToMerge_Oceans, "Oceans")
        arcpy.Merge_management([shpToMerge_LandUseA, shpToMerge_LandUseB], "LandUse")

# Eliminacion poblaciones repetidas en NamedPlc
for gdb in os.listdir(path_newsGDBs):
    if os.path.splitext(gdb)[1] == ".gdb":
        arcpy.env.workspace = os.path.join(path_newsGDBs, gdb)
        arcpy.MakeFeatureLayer_management("NamedPlc", "NamedPlcLyr")
        arcpy.DeleteRows_management(arcpy.SelectLayerByAttribute_management("NamedPlcLyr", "NEW_SELECTION", "POI_NMTYPE <> 'B'"))
        arcpy.Delete_management("NamedPlcLyr")

# Eliminacion de los FEAT_COD en LandUse
for gdb in os.listdir(path_newsGDBs):
    if os.path.splitext(gdb)[1] == ".gdb":
        arcpy.env.workspace = os.path.join(path_newsGDBs, gdb)
        arcpy.MakeFeatureLayer_management("LandUse", "LandUseLyr")
        selection = arcpy.SelectLayerByAttribute_management("LandUseLyr", "NEW_SELECTION", query)
        arcpy.DeleteRows_management(arcpy.SelectLayerByAttribute_management(selection, "SWITCH_SELECTION"))
        arcpy.Delete_management("NamedPlcLyr")
        arcpy.Delete_management(selection)

# Creacion y calculo de campos
for gdb in os.listdir(path_newsGDBs):
    if os.path.splitext(gdb)[1] == ".gdb":
        arcpy.env.workspace = os.path.join(path_newsGDBs, gdb)
        # Nuevos campos en NamedPlc
        arcpy.AddField_management("NamedPlc", "ADMINCLASS", "Short")
        arcpy.AddField_management("NamedPlc", "NAME", "Text", 100)
        arcpy.AddField_management("NamedPlc", "DISPCLASS", "Short")
        # Nuevos campos en WaterPoly
        arcpy.AddField_management("WaterPoly", "NAME", "Text", 70)
        arcpy.AddField_management("WaterPoly", "TYP", "Short")
        # Nuevos campos en WaterSeg
        arcpy.AddField_management("WaterSeg", "NAME", "Text", 70)
        # Nuevos campos en Oceans
        arcpy.AddField_management("Oceans", "NAME", "Text", 70)
        arcpy.AddField_management("Oceans", "TYP", "Short")
        # Nuevos campos en LandUse
        arcpy.AddField_management("LandUse", "NAME", "Text", 150)
        arcpy.AddField_management("LandUse", "FEATTYP", "Short")
        arcpy.AddField_management("LandUse", "ACRON", "Text", 20)

        # Se calculan los campos ADMINCLASS, NAME y DISPCLASS en NamedPlc
        with arcpy.da.UpdateCursor("NamedPlc", ["POI_NAME", "CAPITAL", "POPULATION", "ADMINCLASS", "NAME", "DISPCLASS"]) as cursorNamedPlc:
            for row in cursorNamedPlc:
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
                cursorNamedPlc.updateRow(row)

        # Se calculan los campos NAME y TYP en WaterPoly
        with arcpy.da.UpdateCursor("WaterPoly", ["POLYGON_NM", "NAME", "TYP"]) as cursorWaterPoly:
            for row in cursorWaterPoly:
                row[1] = row[0].title()
                row[2] = 2
                cursorWaterPoly.updateRow(row)

        # Se calcula el campo NAME en WaterSeg
        with arcpy.da.UpdateCursor("WaterSeg", ["POLYGON_NM", "NAME"]) as cursorWaterSeg:
            for row in cursorWaterSeg:
                row[1] = row[0].title()
                cursorWaterSeg.updateRow(row)

        # Se calculan los campos NAME y TYP en Oceans
        with arcpy.da.UpdateCursor("Oceans", ["POLYGON_NM", "NAME", "TYP"]) as cursorOceans:
            for row in cursorOceans:
                row[1] = row[0].title()
                row[2] = 1
                cursorOceans.updateRow(row)

        # Se calculan los campos NAME, FEATTYP y ACRON en LandUse
        with arcpy.da.UpdateCursor("LandUse", ["POLYGON_NM", "FEAT_COD", "FEATTYP", "NAME", "ACRON"]) as cursorLandUse:
            for row in cursorLandUse:
                row[2] = feattypDic.get(row[1])
                row[3] = row[0].title()
                row[4] = ""
                cursorLandUse.updateRow(row)

# Merge Oceans en WaterPoly
for gdb in os.listdir(path_newsGDBs):
    if os.path.splitext(gdb)[1] == ".gdb":
        arcpy.env.workspace = os.path.join(path_newsGDBs, gdb)
        arcpy.Merge_management(["Oceans","WaterPoly"], "WaterPoly2")
        arcpy.Delete_management("WaterPoly")
        arcpy.Rename_management("WaterPoly2", "WaterPoly")
        arcpy.Delete_management("Oceans")

# Se crea MapaBase.gdb
if arcpy.Exists(os.path.join(path_newsGDBs, "MapaBase.gdb")):
    arcpy.Delete_management(os.path.join(path_newsGDBs, "MapaBase.gdb"))
arcpy.CreateFileGDB_management(path_newsGDBs, "MapaBase.gdb")


# Merge de todas las fc de cada Mapa_Base_e.gdb, Mapa_Base_f.gdb y Mapa_Base_p.gdb

toMerge_NamedPlc = []
toMerge_WaterPoly = []
toMerge_WaterSeg = []
toMerge_LandUse = []

for gdb in os.listdir(path_newsGDBs):
    if os.path.splitext(gdb)[1] == ".gdb" and os.path.splitext(gdb)[0] != "MapaBase":
        arcpy.env.workspace = os.path.join(path_newsGDBs, gdb)
        for fc in arcpy.ListFeatureClasses():
            if fc.find("NamedPlc") >= 0:
                toMerge_NamedPlc.append(os.path.join(path_newsGDBs, gdb, fc))
            if fc.find("WaterPoly") >= 0:
                toMerge_WaterPoly.append(os.path.join(path_newsGDBs, gdb, fc))
            if fc.find("WaterSeg") >= 0:
                toMerge_WaterSeg.append(os.path.join(path_newsGDBs, gdb, fc))
            if fc.find("LandUse") >= 0:
                toMerge_LandUse.append(os.path.join(path_newsGDBs, gdb, fc))

arcpy.env.workspace = os.path.join(path_newsGDBs, "MapaBase.gdb")
arcpy.Merge_management(toMerge_NamedPlc, "esp_sm")
arcpy.Merge_management(toMerge_WaterPoly, "esp_wa")
arcpy.Merge_management(toMerge_WaterSeg, "esp_wl")
arcpy.Merge_management(toMerge_LandUse, "esp_lu")

# Se proyectan las fc a WGS 1984 Web Mercator (auxiliary sphere)
arcpy.env.workspace = os.path.join(path_newsGDBs, "MapaBase.gdb")
for fc in arcpy.ListFeatureClasses():
    if arcpy.Describe(fc).spatialReference != rsWGS84:
        arcpy.Project_management(fc, fc + "_proj", rsWGS84)
        arcpy.Delete_management(fc)
        arcpy.Rename_management(fc + "_proj", fc)

# Se eliminan las gdbs auxiliares
for gdb in os.listdir(path_newsGDBs):
    if os.path.splitext(gdb)[1] == ".gdb" and os.path.splitext(gdb)[0] != "MapaBase":
        arcpy.Delete_management(os.path.join(path_newsGDBs, gdb))