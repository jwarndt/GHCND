class ClimateVar(object):
    
    def __init__(self,initName):
        self.name = initName
        
        self.start = None
        self.end = None
        self.duration = None
        self.data = []
        self.timelist = []

        self.monthbounds = [] # a nested list holding the index values of the start and end of each month in the daily data.
        
    def getName(self):
        return self.name
    
    def setName(self,newName):
        self.name = newName
        
    def setTimeBounds(self):
        self.start = self.timelist[0]
        self.end = self.timelist[-1]
        self.duration = self.end - self.start
        
    def getStart(self):
        return self.start
    
    def setStart(self,newStart):
        self.start = newStart
        
    def getEnd(self):
        return self.end
    
    def setEnd(self,newEnd):
        self.end = newEnd
        
    def getData(self):
        return self.data
        
    def setData(self,newData):
        self.data = newData
        
    def getTimelist(self):
        return self.timelist
        
    def setTimelist(self,newTimelist):
        self.timelist = newTimelist
        self.start = self.timelist[0]
        self.end = self.timelist[-1]
        self.duration = self.end - self.start
            

class Station(object):
    
    def __init__(self,initName,initStationId,initCountry,initState,initLat,initLon,initElev,initHCN,initCRN,initGSN,initWMOId):
        """
        Parameters:
        initStationId: int
            the station id gathered from the ghcnd-stations.txt file
        intiLat: float
            station latitude
        initLon: float
            station longitude
        initVars: list
            list of ClimateVar objects
        initHCN: boolean
            True if the station is part of the U.S. Historical Climatology Network (HSN), False otherwise
        initCRN: boolean
            True if the station is part of the U.S. Climate Reference Network or U.S. Regional Climate Network Station, False otherwise
        initGSN: boolean
            True if the station is part of the GCOS Surface Network (GSN), False otherwise
        """
        self.name = initName
        self.stationId = initStationId
        self.country = initCountry
        self.state = initState
        self.lat = initLat
        self.lon = initLon
        self.elev = initElev
        self.variables = {} # a list of ClimateVar objects
        self.hcn = initHCN
        self.crn = initCRN
        self.gsn = initGSN
        self.wmoId = initWMOId
