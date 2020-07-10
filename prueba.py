import arcpy, os

path = u"C:\\SyK\\07_CARTOBASE\\data"

for root, dirs, files in os.walk(path, topdown=True):
    for name in files:
        if name == "NamedPlc.shp":
            if root.find("HERE 2020Q2 Espana") > 0:
                m = "_e"
            elif root.find("Portugal") > 0:
                m = "_p"
            elif root.find("F0CN201E1EF0000AACMN") > 0:
                m = "_f"
            k = root.split('\\')[len(root.split('\\')) - 1][1]
            newName = os.path.splitext(name)[0] + m + k + os.path.splitext(name)[1]
            if name != newName:
                arcpy.Rename_management(os.path.join(root, name), newName)
                print(newName)

