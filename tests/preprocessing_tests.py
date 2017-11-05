from "C:/Users/Jacob/Projects/GHCND/tests/DataStructs.py" import *

# initStationsMetadata,initInventoryMetadata,initDlyFileDirectory
sp = StationPreprocessor("D:/GHCND_data/ghcnd-stations.txt",
                         "D:/GHCND_data/ghcnd-inventory.txt",
                         "D:/GHCND_data/ghcnd_all.tar/ghcnd_all/ghcnd_all")
sp.addCountries(["united states","canada"])
sp.addStates(["minnesota"])
sp.addStations()
sp.processDlyFiles(["TMAX","TMIN","PRCP"])
