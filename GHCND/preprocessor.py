import datetime
import calendar
import os
import numpy as np
import osgeo.ogr as ogr
import osgeo.osr as osr

class StationPreprocessor(object):
    
    def __init__(self,initStationsMetadata,initInventoryMetadata,initDlyFileDirectory):
        """
        Parameters:
        -----------
        initStationsMetadata: string
            full file path to the ghcnd stations metadata file (ghcnd-stations.txt)
        initInventoryMetadata: string
            full file path to the ghcnd inventory metadata file (ghcnd-inventory.txt)
        initDlyFileDirectory: string
            path to the directory holding the ghcnd dly files (ghcnd_all)
        """
        self.stationsFile = initStationsMetadata
        self.inventoryFile = initInventoryMetadata
        self.dlyFileDir = initDlyFileDirectory
        
        self.stations = np.array([]) # stations of interest: a list of Station objects
        self.states = [] # a list of state abreviations
        self.countries = [] # a list of country abreviations
        
        
        self.countryMap = {'afghanistan': 'AF',
                         'albania': 'AL',
                         'algeria': 'AG',
                         'american samoa [united states]': 'AQ',
                         'angola': 'AO',
                         'antarctica': 'AY',
                         'antigua and barbuda': 'AC',
                         'argentina': 'AR',
                         'armenia': 'AM',
                         'australia': 'AS',
                         'austria': 'AU',
                         'azerbaijan': 'AJ',
                         'bahamas, the': 'BF',
                         'bahrain': 'BA',
                         'bangladesh': 'BG',
                         'barbados': 'BB',
                         'belarus': 'BO',
                         'belgium': 'BE',
                         'belize': 'BH',
                         'benin': 'BN',
                         'bermuda [united kingdom]': 'BD',
                         'bolivia': 'BL',
                         'bosnia and herzegovina': 'BK',
                         'botswana': 'BC',
                         'brazil': 'BR',
                         'british indian ocean territory [united kingdom]': 'IO',
                         'brunei': 'BX',
                         'bulgaria': 'BU',
                         'burkina faso': 'UV',
                         'burma': 'BM',
                         'burundi': 'BY',
                         'cambodia': 'CB',
                         'cameroon': 'CM',
                         'canada': 'CA',
                         'cape verde': 'CV',
                         'cayman islands [united kingdom]': 'CJ',
                         'central african republic': 'CT',
                         'chad': 'CD',
                         'chile': 'CI',
                         'china': 'CH',
                         'christmas island [australia]': 'KT',
                         'cocos (keeling) islands [australia]': 'CK',
                         'colombia': 'CO',
                         'congo (brazzaville)': 'CF',
                         'congo (kinshasa)': 'CG',
                         'cook islands [new zealand]': 'CW',
                         'costa rica': 'CS',
                         "cote d'ivoire": 'IV',
                         'croatia': 'HR',
                         'cuba': 'CU',
                         'cyprus': 'CY',
                         'czech republic': 'EZ',
                         'denmark': 'DA',
                         'dominica': 'DO',
                         'dominican republic': 'DR',
                         'ecuador': 'EC',
                         'egypt': 'EG',
                         'el salvador': 'ES',
                         'equatorial guinea': 'EK',
                         'eritrea': 'ER',
                         'estonia': 'EN',
                         'ethiopia': 'ET',
                         'europa island [france]': 'EU',
                         'falkland islands (islas malvinas) [united kingdom]': 'FK',
                         'federated states of micronesia': 'FM',
                         'fiji': 'FJ',
                         'finland': 'FI',
                         'france': 'FR',
                         'french guiana [france]': 'FG',
                         'french polynesia': 'FP',
                         'french southern and antarctic lands [france]': 'FS',
                         'gabon': 'GB',
                         'gambia, the': 'GA',
                         'georgia': 'GG',
                         'germany': 'GM',
                         'ghana': 'GH',
                         'gibraltar [united kingdom]': 'GI',
                         'greece': 'GR',
                         'greenland [denmark]': 'GL',
                         'guadeloupe [france]': 'GP',
                         'guam [united states]': 'GQ',
                         'guatemala': 'GT',
                         'guinea': 'GV',
                         'guinea-bissau': 'PU',
                         'guyana': 'GY',
                         'honduras': 'HO',
                         'hungary': 'HU',
                         'iceland': 'IC',
                         'india': 'IN',
                         'indonesia': 'ID',
                         'iran': 'IR',
                         'iraq': 'IZ',
                         'ireland': 'EI',
                         'israel': 'IS',
                         'italy': 'IT',
                         'jamaica': 'JM',
                         'jan mayen [norway]': 'JN',
                         'japan': 'JA',
                         'johnston atoll [united states]': 'JQ',
                         'jordan': 'JO',
                         'juan de nova island [france]': 'JU',
                         'kazakhstan': 'KZ',
                         'kenya': 'KE',
                         'kiribati': 'KR',
                         'korea, north': 'KN',
                         'korea, south': 'KS',
                         'kuwait': 'KU',
                         'kyrgyzstan': 'KG',
                         'laos': 'LA',
                         'latvia': 'LG',
                         'lebanon': 'LE',
                         'lesotho': 'LT',
                         'liberia': 'LI',
                         'libya': 'LY',
                         'lithuania': 'LH',
                         'luxembourg': 'LU',
                         'macau s.a.r': 'MC',
                         'macedonia': 'MK',
                         'madagascar': 'MA',
                         'malawi': 'MI',
                         'malaysia': 'MY',
                         'maldives': 'MV',
                         'mali': 'ML',
                         'malta': 'MT',
                         'marshall islands': 'RM',
                         'martinique [france]': 'MB',
                         'mauritania': 'MR',
                         'mauritius': 'MP',
                         'mayotte [france]': 'MF',
                         'mexico': 'MX',
                         'midway islands [united states}': 'MQ',
                         'moldova': 'MD',
                         'mongolia': 'MG',
                         'montenegro': 'MJ',
                         'morocco': 'MO',
                         'mozambique': 'MZ',
                         'namibia': 'WA',
                         'nepal': 'NP',
                         'netherlands': 'NL',
                         'netherlands antilles [netherlands]': 'NT',
                         'new caledonia [france]': 'NC',
                         'new zealand': 'NZ',
                         'nicaragua': 'NU',
                         'niger': 'NG',
                         'nigeria': 'NI',
                         'niue [new zealand]': 'NE',
                         'norfolk island [australia]': 'NF',
                         'northern mariana islands [united states]': 'CQ',
                         'norway': 'NO',
                         'oman': 'MU',
                         'pakistan': 'PK',
                         'palau': 'PS',
                         'palmyra atoll [united states]': 'LQ',
                         'panama': 'PM',
                         'papua new guinea': 'PP',
                         'paraguay': 'PA',
                         'peru': 'PE',
                         'philippines': 'RP',
                         'pitcairn islands [united kingdom]': 'PC',
                         'poland': 'PL',
                         'portugal': 'PO',
                         'puerto rico [united states]': 'RQ',
                         'qatar': 'QA',
                         'reunion [france]': 'RE',
                         'romania': 'RO',
                         'russia': 'RS',
                         'rwanda': 'RW',
                         'saint helena [united kingdom]': 'SH',
                         'saint lucia': 'ST',
                         'saint pierre and miquelon [france]': 'SB',
                         'saudi arabia': 'SA',
                         'senegal': 'SG',
                         'serbia': 'RI',
                         'seychelles': 'SE',
                         'sierra leone': 'SL',
                         'singapore': 'SN',
                         'slovakia': 'LO',
                         'slovenia': 'SI',
                         'solomon islands': 'BP',
                         'south africa': 'SF',
                         'south georgia and the south sandwich islands [united kingdom]': 'SX',
                         'spain': 'SP',
                         'sri lanka': 'CE',
                         'sudan': 'SU',
                         'suriname': 'NS',
                         'svalbard [norway]': 'SV',
                         'swaziland': 'WZ',
                         'sweden': 'SW',
                         'switzerland': 'SZ',
                         'syria': 'SY',
                         'tajikistan': 'TI',
                         'tanzania': 'TZ',
                         'thailand': 'TH',
                         'togo': 'TO',
                         'tokelau [new zealand]': 'TL',
                         'tonga': 'TN',
                         'trinidad and tobago': 'TD',
                         'tromelin island [france]': 'TE',
                         'tunisia': 'TS',
                         'turkey': 'TU',
                         'turkmenistan': 'TX',
                         'tuvalu': 'TV',
                         'uganda': 'UG',
                         'ukraine': 'UP',
                         'united arab emirates': 'AE',
                         'united kingdom': 'UK',
                         'united states': 'US',
                         'uruguay': 'UY',
                         'uzbekistan': 'UZ',
                         'vanuatu': 'NH',
                         'venezuela': 'VE',
                         'vietnam': 'VM',
                         'virgin islands [united states]': 'VQ',
                         'wake island [united states]': 'WQ',
                         'wallis and futuna [france]': 'WF',
                         'western sahara': 'WI',
                         'zambia': 'ZA',
                         'zimbabwe': 'ZI'}
        
        self.stateMap = {'alabama': 'AL',
                         'alaska': 'AK',
                         'alberta': 'AB',
                         'american samoa': 'AS',
                         'arizona': 'AZ',
                         'arkansas': 'AR',
                         'british columbia': 'BC',
                         'california': 'CA',
                         'colorado': 'CO',
                         'connecticut': 'CT',
                         'delaware': 'DE',
                         'district of columbia': 'DC',
                         'florida': 'FL',
                         'georgia': 'GA',
                         'guam': 'GU',
                         'hawaii': 'HI',
                         'idaho': 'ID',
                         'illinois': 'IL',
                         'indiana': 'IN',
                         'iowa': 'IA',
                         'kansas': 'KS',
                         'kentucky': 'KY',
                         'louisiana': 'LA',
                         'maine': 'ME',
                         'manitoba': 'MB',
                         'marshall islands': 'MH',
                         'maryland': 'MD',
                         'massachusetts': 'MA',
                         'michigan': 'MI',
                         'micronesia': 'FM',
                         'minnesota': 'MN',
                         'mississippi': 'MS',
                         'missouri': 'MO',
                         'montana': 'MT',
                         'nebraska': 'NE',
                         'nevada': 'NV',
                         'new brunswick': 'NB',
                         'new hampshire': 'NH',
                         'new jersey': 'NJ',
                         'new mexico': 'NM',
                         'new york': 'NY',
                         'newfoundland and labrador': 'NL',
                         'north carolina': 'NC',
                         'north dakota': 'ND',
                         'northern mariana islands': 'MP',
                         'northwest territories': 'NT',
                         'nova scotia': 'NS',
                         'nunavut': 'NU',
                         'ohio': 'OH',
                         'oklahoma': 'OK',
                         'ontario': 'ON',
                         'oregon': 'OR',
                         'pacific islands': 'PI',
                         'palau': 'PW',
                         'pennsylvania': 'PA',
                         'prince edward island': 'PE',
                         'puerto rico': 'PR',
                         'quebec': 'QC',
                         'rhode island': 'RI',
                         'saskatchewan': 'SK',
                         'south carolina': 'SC',
                         'south dakota': 'SD',
                         'tennessee': 'TN',
                         'texas': 'TX',
                         'u.s. minor outlying islands': 'UM',
                         'utah': 'UT',
                         'vermont': 'VT',
                         'virgin islands': 'VI',
                         'virginia': 'VA',
                         'washington': 'WA',
                         'west virginia': 'WV',
                         'wisconsin': 'WI',
                         'wyoming': 'WY',
                         'yukon territory': 'YT',
                         '':''}
    
    def setStates(self,newStates):
        self.clearStates() # clears the list first. Then sets it
        self.addStates(newStates)
    
    def addStates(self,newStates):
        if type(newStates) != list:
            print("error: states not added. states must be in a list")
            return
        for n in newStates:
            n = n.lower()
            # in order for the state to be added, it must not be in the states list 
            # and it must be in the map.
            if n in self.stateMap and self.stateMap[n] not in self.states: 
                self.states.append(self.stateMap[n]) 
    
    def removeState(self,state):
        state = state.lower()
        if state in self.stateMap and self.stateMap[state] in self.states:
            self.states.remove(self.stateMap[state])
        
    def clearStates(self):
        self.states = []
        
    def setCountries(self,newCountries):
        self.clearCountries()
        self.addCountries(newCountries)
        
    def addCountries(self,newCountries):
        if type(newCountries) != list:
            print("error: countries not added. countries must be in a list")
            return
        for n in newCountries:
            n = n.lower()
            if n in self.countryMap and self.countryMap[n] not in self.countries:
                self.countries.append(self.countryMap[n])
                
    def removeCountry(self,country):
        country = country.lower()
        if country in self.countryMap and self.countryMap[country] in self.countries:
            self.countries.remove(self.countryMap[country])
            
    def clearCountries(self):
        self.countries = []
        
    def setStations(self):
        self.clearStations()
        self.addStations()
        
    def addStations(self):
        """
        Adds stations to the StationPreproccessor's station attribute
        """
        if len(self.countries) == 0:
            print("error: no stations added. must specify countries")
            return
        self.countries.sort()
        self.states.sort()
        
        infile = open(self.stationsFile,"r")
        line = infile.readline()
        while line != "":
            newStation = None
            if line[:2] in self.countries:
                name = line[41:71].strip() 
                stationId = line[:11].strip()
                c = line[:2]
                s = line[38:40].strip()
                lat = float(line[12:20].strip())
                lon = float(line[21:30].strip())
                elev = float(line[31:37].strip())
                gsn = line[72:75].strip()
                hcncrn = line[76:79].strip()
                wmo = line[80:].strip()
                if wmo == "":
                    wmo = None
                if gsn == "GSN":
                    gsn = True
                else:
                    gsn = False
                if hcncrn == "HCN":
                    hcn = True
                    crn = False
                elif hcncrn == "CRN":
                    hcn = False
                    crn = True
                else:
                    hcn = False
                    crn = False
                if line[:2] == "CA" or line[:2] == "US": # if the country is the united states or canada, check the state in case there needs to be more filtering
                    if len(self.states) == 0: # if no states are defined, add all stations for the country
                        newStation = Station(name,stationId,c,s,lat,lon,elev,hcn,crn,gsn,wmo)
                    elif s in self.states:    
                        newStation = Station(name,stationId,c,s,lat,lon,elev,hcn,crn,gsn,wmo)
                else: # else the country is not canada or the united states and therefore there is no state
                    newStation = Station(name,stationId,c,None,lat,lon,elev,hcn,crn,gsn,wmo)
                if newStation != None:
                    self.stations.append(newStation)
            line = infile.readline()
        infile.close()
        self.stations = np.array(self.stations) # set the station list to an np.array
            
    def clearStations(self):
        self.stations = np.array([])
        
    def processDlyFiles(self,variablesOfInterest):
        """
        Parameters
        ----------------
        variablesOfInterest: list
            the data that will be included in the output stations
        
        Returns
        ------------
        None
        """
        for station in self.stations: # iterate through the Station objects
            infile = open(os.path.join(self.dlyFileDir,station.stationId + ".dly"))
            line = infile.readline()
            while line != "":
                dataIdx = 21 # add 8 to get to the next data value
                qFlagIdx = 27 # add 8 to get the qFlag for the next data value
                # only include data that does not fail the quality assurance check (QFLAG1 must be blank (i.e. line[27] == " "))
                # other specifications could exist. For example, checking the MFLAG (measurement flag) or SFLAGE (source flag)
                curYear = int(line[11:15].strip())
                curMonth = int(line[15:17].strip())
                curDay = 1
                varName = line[17:21].strip() # TAVG, TMAX, TMIN, PRCP, etc...
                if varName in variablesOfInterest: # only process the stations that have the variables of interest. Otherwise, skip them
                    if varName not in station.variables: # if variable not in the variables, create it
                        variable = ClimateVar(varName)
                    else:
                        variable = station.variables[varName] # else, point to the variable and append to its data
                    while dataIdx <= 261: # the last dataIdx is 261
                        if curDay <= calendar.monthrange(curYear,curMonth)[1]: # only process data in the time range of the month.
                            value = float(line[dataIdx:dataIdx+5].strip()) # the data value occupies 4 spaces in the txt, so slice appropriately.
                            qFlag = line[qFlagIdx] # the qFlag occupies only 1 space in the txt
                            if qFlag == " " and value != -9999.0: # only include data passing quality assurance, and data that is NoData
                                variable.data.append(value)
                                variable.timelist.append(datetime.date(year=curYear,month=curMonth,day=curDay))
                            else:
                                variable.data.append(np.nan) # if it didn't pass the quality assurance or it was NoData, append NaN
                                variable.timelist.append(datetime.date(year=curYear,month=curMonth,day=curDay))
                        dataIdx+=8
                        qFlagIdx+=8
                        curDay+=1
                    if varName not in station.variables: # the variable wasn't found in the Station's vars, append the newly created variable, otherwise the variable was only modified.
                        station.variables[varName] = variable
                        station.variables[varName].dataDescription = "daily"
                    variable.setData(variable.data) # to set the list to an np.array
                    variable.setTimelist(variable.timelist) # to set the list to an np.array
                line = infile.readline()
            infile.close()
            # now set the time bounds for each variable using its already built timelist (this is just to set variable.start, variable.end, and variable.duration)
            for var in station.variables:
                station.variables[var].setTimeBounds()
                
    def exportToShapefile(self,filename): # could export a shapefile with climate data for a timeslice included.. maybe later
        driver = ogr.GetDriverByName("ESRI Shapefile")
        dataSource = driver.CreateDataSource(filename)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        layerName = filename.split("/")[-1][:-4] # the layerName is the shapefile name without the path and its file extension
        layer = dataSource.CreateLayer(layerName, srs, ogr.wkbPoint)
        # create the fields
        layer.CreateField(ogr.FieldDefn("name", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("stationID", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("country", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("state", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("lat", ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn("lon", ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn("elev", ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn("TMAX", ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn("TMAX_Begin", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("TMAX_End", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("TMIN", ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn("TMIN_Begin", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("TMIN_End", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("PRCP", ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn("PRCP_Begin", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("PRCP_End", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("hcn", ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn("crn", ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn("gsn", ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn("wmoID", ogr.OFTString))

        # iterate through stations, create features, and add their attributes
        for station in self.stations:
            if "TMAX" in station.variables:
                tmax = 1
                tmaxBegin = station.variables["TMAX"].getStart()
                tmaxEnd = station.variables["TMAX"].getEnd()
            else:
                tmax = 0
                tmaxBegin = "" # the earliest representable time. Couldn't figure out how to set null OGR Date types
                tmaxEnd = ""
            if "TMIN" in station.variables:
                tmin = 1
                tminBegin = station.variables["TMIN"].getStart()
                tminEnd = station.variables["TMIN"].getEnd()
            else:
                tmin = 0
                tminBegin = ""
                tminEnd = ""
            if "PRCP" in station.variables:
                prcp = 1
                prcpBegin = station.variables["PRCP"].getStart()
                prcpEnd = station.variables["PRCP"].getEnd()
            else:
                prcp = 0
                prcpBegin = ""
                prcpEnd = ""

            # create the feature
            feature = ogr.Feature(layer.GetLayerDefn())
            # set the attributes
            feature.SetField("name", station.name)
            feature.SetField("stationID", station.stationId)
            feature.SetField("country", self.countryMap.keys()[self.countryMap.values().index(station.country)]) # country will be the full name, not the abreviation
            feature.SetField("state", self.stateMap.keys()[self.stateMap.values().index(station.state)])
            feature.SetField("lat", station.lat)
            feature.SetField("lon", station.lon)
            feature.SetField("elev", station.elev)
            feature.SetField("TMAX", tmax)
            feature.SetField("TMAX_Begin", str(tmaxBegin))
            feature.SetField("TMAX_End", str(tmaxEnd))
            feature.SetField("TMIN", tmin)
            feature.SetField("TMIN_Begin", str(tminBegin))
            feature.SetField("TMIN_End", str(tminEnd))
            feature.SetField("PRCP", prcp)
            feature.SetField("PRCP_Begin", str(prcpBegin))
            feature.SetField("PRCP_End", str(prcpEnd))
            feature.SetField("hcn", int(station.hcn)) # convert the boolean to int
            feature.SetField("crn", int(station.crn))
            feature.SetField("gsn", int(station.gsn))
            feature.SetField("wmoID", station.wmoId)
            # create and set the geometry
            wkt = "POINT(%f %f)" % (float(station.lon), float(station.lat))
            point = ogr.CreateGeometryFromWkt(wkt)
            feature.SetGeometry(point)
            layer.CreateFeature(feature)
            # close the feature
            feature = None
        # close the dataSource
        dataSource = None

class ClimateVar(object):
    
    def __init__(self,initName):
        self.name = initName
        self.dataDescription = None # should be "daily", "monthly mean", "seasonal mean", "annual mean", "monthly anomaly"
        
        self.start = None
        self.end = None
        self.duration = None
        self.data = []
        self.timelist = []
        
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
        self.data = np.array(newData)
        
    def getTimelist(self):
        return self.timelist
        
    def setTimelist(self,newTimelist):
        self.timelist = np.array(newTimelist)
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
        self.variables = {} # a dictionary of ClimateVar objects
        self.hcn = initHCN
        self.crn = initCRN
        self.gsn = initGSN
        self.wmoId = initWMOId
        