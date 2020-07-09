import arcpy, zipfile, os, pyunpack


path_extractTo = r"C:\SyK\07_CARTOBASE\data"
path_extractIn = r"C:\SyK\07_CARTOBASE\data"
srWGS84 = arcpy.SpatialReference(4326)

# # DESCOMPRESION
# Se comprueba si existen ya los directorios donde se descomprimen los archivos. Si existen se eliminan
# Se crean los directorios donde se descomprimiran los archivos
# Se descomprimen cada uno de los archivos que esten en path_extractTo

# TODO:comprobar que no necesite la libreria "tarfile" para descomprimir los archivos tar

listFiles = os.listdir(path_extractTo)
for file in listFiles:
    if os.path.exists(os.path.splitext(os.path.join(path_extractTo, file))[1]) == '':
        os.removedirs(os.path.join(path_extractTo, file))
    # os.mkdir(os.path.join(path_extractTo, file))
    pyunpack.Archive(os.path.join(path_extractTo, file), "patool", 100).extractall(path_extractIn, True, "c://python27//arcgis10.7//lib//site-packages")
    # file_zip = zipfile.ZipFile(os.path.join(path_extractTo,file), "r")
    # file_zip.extractall(path = path_extractIn + file)
    listFilesZip = os.listdir(os.path.join(path_extractTo, file))
    # TODO: comprobar si el siguiente codigo es necesario para que se descompriman los archivos comprimidos dentro del primero
    for fileZip in listFilesZip:
        os.mkdir(os.path.join(path_extractTo, file))
        file_zip = zipfile.ZipFile(path_extractTo + file, "r")
        file_zip.extractall(path = path_extractIn + file)

# CREACION GDB_FINAL
# Se crea la gdb_ginal
# Se mergean todos los shp NamedPLC de cada K
listFiles = os.listdir(path_extractTo)
for file in listFiles:
    gdbName = "Mapa_Base_" + file
    arcpy.CreateFileGDB_management(path_extractTo, gdbName)
    arcpy.env.workspace = os.path.join(path_extractTo, gdbName)
    arcpy.CreateFeatureclass("", "NamedPLC_noProject", "POINT", spatial_reference = srWGS84)
    # TODO: obtener todos los shp NamedPLC de cada K, usar os.walk()?
    # TODO: el output del merge tiene que estar creado previamente?
    inputs = []
    aracpy.Merge_management(inputs, "NamedPLC_noProject")


