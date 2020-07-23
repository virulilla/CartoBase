# coding: utf-8
import arcpy, os, time
from datetime import datetime

# Importante: Todos los archivos deben descomprimirse antes de utilizar el script.
# Importante: Las tres carpetas descomprimidas tienen que estar en el mismo directorio.

path = u"C:\\SyK\\07_CARTOBASE\\data"
path_newsGDB = u"C:\\SyK\\07_CARTOBASE\\data"

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

# Backup de MapaBase.gdb anterior
if arcpy.Exists(os.path.join(path_newsGDB, "MapaBase.gdb")):
    hoy = time.strftime("%Y%m%d_%H%M%S")
    out_data = os.path.join(path, "MapaBase" + "_" + hoy + ".gdb")
    os.rename(os.path.join(path_newsGDB, "MapaBase.gdb"), out_data)

# Renombrado de archivos NamedPlc.shp
for root, dirs, files in os.walk(path, topdown=True):
    for name in files:
        if name == "NamedPlc.shp" or name == "WaterPoly.shp" or name == "WaterSeg.shp" or name == "Oceans.shp" or name == "LandUseA.shp" or name == "LandUseB.shp" or name == "AltStreets.shp":
            if root.find(u"HERE 2020Q2 España") >= 0:
                m = "_e"
            elif root.find("Portugal") >= 0:
                m = "_p"
            elif root.find("F0CN201E1EF0000AACMN") >= 0:
                m = "_f"
            k = root.split('\\')[len(root.split('\\')) - 1][1]
            newName = os.path.splitext(name)[0] + m + k + os.path.splitext(name)[1]
            if name != newName:
                arcpy.Rename_management(os.path.join(root, name), newName)

# Se crea MapaBase.gdb
arcpy.CreateFileGDB_management(path_newsGDB, "MapaBase.gdb")

# Merge de todos los paises
shpToMerge_NamedPlc = []
shpToMerge_WaterPoly = []
shpToMerge_WaterSeg = []
shpToMerge_Oceans = []
shpToMerge_LandUseA = []
shpToMerge_LandUseB = []
shpToMerge_AltStreets = []
for root, dirs, files in os.walk(path, topdown=True):
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
        if name.find("AltStreets") >= 0 and os.path.splitext(name)[1] == ".shp":
            shpToMerge_AltStreets.append(os.path.join(root, name))

arcpy.env.workspace = os.path.join(path_newsGDB, "MapaBase.gdb")

arcpy.Merge_management(shpToMerge_NamedPlc, "esp_sm")
arcpy.Merge_management(shpToMerge_WaterPoly, "WaterPoly")
arcpy.Merge_management(shpToMerge_WaterSeg, "esp_wl")
arcpy.Merge_management(shpToMerge_Oceans, "Oceans")
arcpy.Merge_management(shpToMerge_LandUseA, "esp_lu1")
arcpy.Merge_management(shpToMerge_LandUseB, "esp_lu2")
arcpy.Merge_management(["esp_lu1", "esp_lu2"], "esp_lu")
arcpy.Delete_management("esp_lu1")
arcpy.Delete_management("esp_lu2")
arcpy.Merge_management(shpToMerge_AltStreets, "AltStreets")


# Eliminacion poblaciones repetidas en esp_sm
arcpy.MakeFeatureLayer_management("esp_sm", "esp_smLyr")
arcpy.DeleteRows_management(arcpy.SelectLayerByAttribute_management("esp_smLyr", "NEW_SELECTION", "POI_NMTYPE <> 'B'"))
arcpy.Delete_management("esp_smLyr")

# Eliminacion de los FEAT_COD en esp_lu
arcpy.MakeFeatureLayer_management("esp_lu", "esp_luLyr")
selection = arcpy.SelectLayerByAttribute_management("esp_luLyr", "NEW_SELECTION", query)
arcpy.DeleteRows_management(arcpy.SelectLayerByAttribute_management(selection, "SWITCH_SELECTION"))
arcpy.Delete_management("esp_luLyr")
arcpy.Delete_management(selection)

# Nuevos campos en esp_sm
arcpy.AddField_management("esp_sm", "ADMINCLASS", "Short")
arcpy.AddField_management("esp_sm", "NAME", "Text", 100)
arcpy.AddField_management("esp_sm", "DISPCLASS", "Short")
# Nuevos campos en WaterPoly
arcpy.AddField_management("WaterPoly", "NAME", "Text", 70)
arcpy.AddField_management("WaterPoly", "TYP", "Short")
# Nuevos campos en esp_wl
arcpy.AddField_management("esp_wl", "NAME", "Text", 70)
# Nuevos campos en Oceans
arcpy.AddField_management("Oceans", "NAME", "Text", 70)
arcpy.AddField_management("Oceans", "TYP", "Short")
# Nuevos campos en esp_lu
arcpy.AddField_management("esp_lu", "NAME", "Text", 150)
arcpy.AddField_management("esp_lu", "FEATTYP", "Short")
arcpy.AddField_management("esp_lu", "ACRON", "Text", 20)


# Se crean y rellenan esp_00, esp02, esp_03, esp06, esp_07 (Streets)

for root, dirs, files in os.walk(path, topdown=True):
    for name in files:
        if name == "Streets.shp":
            pathTemplate = os.path.join(root, name)
            break

rsShp = arcpy.Describe(pathTemplate).spatialReference

arcpy.CreateFeatureclass_management(arcpy.env.workspace, "esp_00", "POLYLINE", template= pathTemplate, spatial_reference = rsShp)
arcpy.CreateFeatureclass_management(arcpy.env.workspace, "esp_02", "POLYLINE", template= pathTemplate, spatial_reference = rsShp)
arcpy.CreateFeatureclass_management(arcpy.env.workspace, "esp_03", "POLYLINE", template= pathTemplate, spatial_reference = rsShp)
arcpy.CreateFeatureclass_management(arcpy.env.workspace, "esp_06", "POLYLINE", template= pathTemplate, spatial_reference = rsShp)
arcpy.CreateFeatureclass_management(arcpy.env.workspace, "esp_07", "POLYLINE", template= pathTemplate, spatial_reference = rsShp)

for root, dirs, files in os.walk(path, topdown=True):
    for name in files:
        if name == "Streets.shp":
            arcpy.MakeFeatureLayer_management(os.path.join(root, name), "selectionLyr", where_clause = "FUNC_CLASS ='1' AND FERRY_TYPE <> 'B'")
            arcpy.Append_management("selectionLyr", "esp_00", schema_type = "TEST")
            arcpy.Delete_management("selectionLyr")
            arcpy.MakeFeatureLayer_management(os.path.join(root, name), "selectionLyr", where_clause = "FUNC_CLASS ='2' AND FERRY_TYPE <> 'B'")
            arcpy.Append_management("selectionLyr", "esp_02", schema_type = "TEST")
            arcpy.Delete_management("selectionLyr")
            arcpy.MakeFeatureLayer_management(os.path.join(root, name), "selectionLyr", where_clause = "FUNC_CLASS ='3' AND FERRY_TYPE <> 'B'")
            arcpy.Append_management("selectionLyr", "esp_03", schema_type = "TEST")
            arcpy.Delete_management("selectionLyr")
            arcpy.MakeFeatureLayer_management(os.path.join(root, name), "selectionLyr", where_clause = "FUNC_CLASS ='4' AND FERRY_TYPE <> 'B'")
            arcpy.Append_management("selectionLyr", "esp_06", schema_type = "TEST")
            arcpy.Delete_management("selectionLyr")
            arcpy.MakeFeatureLayer_management(os.path.join(root, name), "selectionLyr", where_clause = "FUNC_CLASS ='5' AND FERRY_TYPE <> 'B'")
            arcpy.Append_management("selectionLyr", "esp_07", schema_type = "TEST")
            arcpy.Delete_management("selectionLyr")

# Se calculan los campos ADMINCLASS, NAME y DISPCLASS en NamedPlc
with arcpy.da.UpdateCursor("esp_sm", ["POI_NAME", "CAPITAL", "POPULATION", "ADMINCLASS", "NAME", "DISPCLASS"]) as cursorNamedPlc:
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
        row[4] = row[0].title()
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
with arcpy.da.UpdateCursor("esp_wl", ["POLYGON_NM", "NAME"]) as cursorWaterSeg:
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
with arcpy.da.UpdateCursor("esp_lu", ["POLYGON_NM", "FEAT_COD", "FEATTYP", "NAME", "ACRON"]) as cursorLandUse:
    for row in cursorLandUse:
        row[2] = feattypDic.get(row[1])
        row[3] = row[0].title()
        row[4] = ""
        cursorLandUse.updateRow(row)

# Se calculan NAME, SHIELDNUM en esp_00 (FC = 1), esp_02 (FC = 2) y esp_03 (FC = 3)
#   Se crean los campos NAME, SHIELDNUM, ST_NAME_1 y ROUTE_TYPE_1
#   Se hace un join entre cada una de estas capas con AltStreets
arcpy.MakeFeatureLayer_management("AltStreets", "AltStreetsLyr")
for fc in ["esp_00", "esp_02", "esp_03"]:
    arcpy.AddField_management(fc, "NAME", "Text", 100)
    arcpy.AddField_management(fc, "SHIELDNUM", "Text", 100)
    arcpy.AddField_management(fc, "ST_NAME_1", "Text", 240)
    arcpy.AddField_management(fc, "ROUTE_TYPE_1", "Text", 1)
    arcpy.MakeFeatureLayer_management(fc, "fcLyr")
    arcpy.AddJoin_management("fcLyr", "LINK_ID", "AltStreetsLyr", "LINK_ID", "KEEP_COMMON")
    arcpy.CalculateField_management("fcLyr", "ST_NAME_1", "!AltStreets.ST_NAME!", "PYTHON")
    arcpy.CalculateField_management("fcLyr", "ROUTE_TYPE_1", "!AltStreets.ROUTE_TYPE!", "PYTHON")
    arcpy.RemoveJoin_management("fcLyr")
    arcpy.Delete_management("fcLyr")
    with arcpy.da.UpdateCursor(fc, ["NAME", "SHIELDNUM", "ST_NAME", "ROUTE_TYPE", "ST_NAME_1", "ROUTE_TYPE_1", "EXITNAME", "JUNCTIONNM"]) as cursorStreet1:
        for row in cursorStreet1:
            if row[3] != " " and (row[5] != " " or row[5] is None):
                row[0] = row[2]
                row[1] = row[2]
            elif row[3] != " " and row[5] == " ":
                row[0] = row[4].title()
                row[1] = row[2]
            elif row[3] == " " and row[5] != " ":
                row[0] = row[2].title()
                row[1] = row[4]
            elif row[3] == " " and (row[5] == " " or row[5] is None):
                row[0] = row[2].title()
                row[1] = row[2].title()
            if row[6] == "Y" or row[0] is None or row[7] == "Y":
                row[0] = ""
                row[1] = ""
            cursorStreet1.updateRow(row)

arcpy.Delete_management("AltStreetsLyr")

#   Se calculan NAME, SHIELDNUM en esp_06 (FC = 4) y esp_07 (FC = 5)
for fc in ["esp_06", "esp_07"]:
    arcpy.AddField_management(fc, "NAME", "Text", 100)
    arcpy.AddField_management(fc, "SHIELDNUM", "Text", 100)
    with arcpy.da.UpdateCursor(fc, ["NAME", "SHIELDNUM", "ST_NAME", "ROUTE_TYPE", "EXITNAME", "JUNCTIONNM"]) as cursorStreet2:
        for row in cursorStreet2:
            if row[3] == " ":
                row[0] = row[2].title()
                row[1] = row[2].title()
            if row[4] == "Y" or row[5] == "Y":
                row[0] = ""
                row[1] = ""
            cursorStreet2.updateRow(row)

# Merge Oceans y WaterPoly en esp_wa
arcpy.Merge_management(["Oceans","WaterPoly"], "esp_wa")
arcpy.Delete_management("Oceans")
arcpy.Delete_management("WaterPoly")
arcpy.Delete_management("AltStreets")

# Se proyectan las fc a WGS 1984 Web Mercator (auxiliary sphere)
for fc in arcpy.ListFeatureClasses():
    if arcpy.Describe(fc).spatialReference != rsWGS84:
        arcpy.Project_management(fc, fc + "_proj", rsWGS84)
        arcpy.Delete_management(fc)
        arcpy.Rename_management(fc + "_proj", fc)

