import arcpy, os
# -*- coding: utf-8 -*-
# TODO: permitir que reconozca las 'n'

path = u"C:\\SyK\\07_CARTOBASE\\data"
path_newsGDBs = u"C:\\SyK\\07_CARTOBASE\\data"

country = {
    "e": "HERE 2020Q2 Espana",
    "p": "Portugal",
    "f": "F0CN201E1EF0000AACMN"
}

# Renombrado de archivos NamedPlc.shp
for root, dirs, files in os.walk(path, topdown=True):
    for name in files:
        if name == "NamedPlc.shp":
            if root.find("HERE 2020Q2 Espana") >= 0:
                m = "_e"
            elif root.find("Portugal") >= 0:
                m = "_p"
            elif root.find("F0CN201E1EF0000AACMN") >= 0:
                m = "_f"
            k = root.split('\\')[len(root.split('\\')) - 1][1]
            newName = os.path.splitext(name)[0] + m + k + os.path.splitext(name)[1]
            if name != newName:
                arcpy.Rename_management(os.path.join(root, name), newName)

# Creacion de las nuevas gdbs
for root, dirs, files in os.walk(path, topdown=True):
    for dir in dirs:
        if dir == "HERE 2020Q2 Espana":
            m = "_e"
        elif dir == "Portugal":
            m = "_p"
        elif dir == "F0CN201E1EF0000AACMN":
            m = "_f"
        if not arcpy.Exists(os.path.join(path_newsGDBs,"Mapa_Base" + m + ".gdb")):
            arcpy.CreateFileGDB_management(path_newsGDBs, "Mapa_Base" + m + ".gdb")
    break

# Merge por paises
for gdb in os.listdir(path_newsGDBs):
    if os.path.splitext(gdb)[1] == ".gdb":
        arcpy.env.workspace = os.path.join(path_newsGDBs, gdb)
        shpToMerge = []
        for root, dirs, files in os.walk(os.path.join(path, country.get(gdb[10])), topdown=True):
            for name in files:
                if name.find("NamedPlc") >= 0 and os.path.splitext(name)[1] == ".shp":
                    shpToMerge.append(os.path.join(root,name))
        arcpy.Merge_management(shpToMerge,"NamedPlc")
