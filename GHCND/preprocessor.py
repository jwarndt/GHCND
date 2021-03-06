import datetime
import calendar
import os
import time
import json
import numpy as np
import osgeo.ogr as ogr
import osgeo.osr as osr

"""
High level description of how this is used. It's easy to think of
this as a preprocessing pipeline. In fact, that's exactly what this is. 

To begin reading the the daily station data, you
must first define which stations you would like to read.

The way you define which stations to process is by specifying
the 1) countries and 2) states/provinces/territories of the stations
you want. Specifying the states/provinces/territories is only applicable
 for the United States and Canada.

Once you have defined the states and countries you want to process, you will
then add the stations to the StationPreprocessor by using the addStations()
function.

Once the stations have been added, you are ready to process the daily data.
To begin the data read, simply run the processDlyFiles(vars) function with
a list of variables you are interested in. Note: this loads a lot of data
into main memory (in some cases 120 years of daily data).
Be wise about how many countries and states you use to
define the stations. Furthermore, be wise about how many variables
you would like data for. (perhaps at a later date I will incorporate
 file and data queues so large amounts of data can be
processed without the user having to manually chunk up data themselves).
At the end of this step your StationPreprocessor will contain all the
stations you have defined and all their daily data for the variables 
you defined.

The next step is convert the daily data to monthly means. To do this,
you must use the GHCND.stats module. At present, the stats module only
supports monthly mean calculation for temperature and precipitation.
(In the case of precipitation, it's the total accumulated precipitation
over the month)

Behind the scenes there has been some filtering going on to remove unwanted
data. The current hard-coded settings for filtering and reading the data are:
(These hard-coded settings should be modified if you are interested in data outside
Canada and the United States)

Daily data values that do not pass this criteria are set to NaN
1. only include data that has passed the quality check of NOAA NCDC
2. only include data from the sources:
    - U.S. Cooperative Summary of the Day
    - CDMP Cooperative Summary of the Day
    - U.S. Cooperative Summary of the Day -- Transmitted via WxCoder3
    - U.S. Automated Surface Observing System (ASOS)
    - Environment Canada  
    - Official Global Climate Observing System (GCOS) or other
        government-supplied data
    - NCEI Reference Network Database (Climate Reference Network and Regional Climate
        Reference Network)
3. days with missing values are set to NaN 
4. eliminate all stations that hold only NaN values for data. (In other
words, eliminate stations where none of the data they recorded passed the filter step).

The following steps are applied when aggregating to monthly mean data.
1. If there are more than 5 missing daily data values in the month, set the
month data value to NaN.
2. If more than 75% of the monthly mean values for a variable are NaN, remove the variable
from the station.
3. If all the monthly station data is NaN, remove the station
4. If the station did not operate or record valid data past 2016, 
remove the station. 

You can write the cleaned data to disk using the export functions.
There are three ways of exporting:
1. exportToShapefile()
       -This does not contain the monthly data values. It includes station location
       station name, station id, which variables it recorded, etc..
2. exportToJSON()
        -This will write all the monthly data to JSON. Keys are the stationId
        It is not GeoJSON.
3. exportToDat()
        -Write the data seperate data files for each station and variable in the
        stationPreprocessor. See the metadata_log.txt file to find see associated
        metadata for each file. 
"""


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
        
        self.stations = [] # stations of interest: a list of Station objects
        self.states = [] # a list of state abreviations
        self.countries = [] # a list of country abreviations
        
        # country map for mapping user input to country abreviations for
        # retrieving stations from the data.
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
        """
        Parameters: 
        -----------
        newStates: list
            a list of strings. the strings should be state names
            found in the stateMap

        Returns:
        ---------
        None
        """
        self.clearStates() # clears the list first. Then sets it
        self.addStates(newStates)
    
    def addStates(self,newStates):
        """
        adds states to the station preprocessor.
        """
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
        """
        removes states from the station preprocessor
        """
        state = state.lower()
        if state in self.stateMap and self.stateMap[state] in self.states:
            self.states.remove(self.stateMap[state])
        
    def clearStates(self):
        """
        removes all previously added states in the station preprocessor
        """
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
            if line[:2] in self.countries:
                newStation = None
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
            
    def clearStations(self):
        self.stations = []
        
    def processDlyFiles(self,variablesOfInterest):
        """
        parses the fixed width .dly files associated with each Station object present
        in the StationPreprocessor. For each station, create a ClimateVar object
        that will store the daily data and datetime objects.
        
        Data will only be processed for variables defined by variablesOfInterest.
        If the station does not contain the variable, it will be dropped from
        the StationPreprocessor.

        running this function when the station preprocessor has many countries/states
        consumes a lot of RAM. So in cases where you need to process many states/countries
        chunk them up.

        Daily data values will only be included if...
        1) the measurement did not fail the quality assurance check 
        (indicated by the quality flag)
        2) the measurement's source is from one of these:
        - U.S. Cooperative Summary of the Day (NCDC DSI-3200)
        - CDMP Cooperative Summary of the Day (NCDC DSI-3206)
        - U.S. Cooperative Summary of the Day -- Transmitted 
               via WxCoder3 (NCDC DSI-3207)
        - U.S. Automated Surface Observing System (ASOS) 
                   real-time data (since January 1, 2006)
        - Environment Canada
        - Official Global Climate Observing System (GCOS) or 
                   other government-supplied data
        - NCEI Reference Network Database (Climate Reference Network
               and Regional Climate Reference Network)

        Daily data values that fail the filter step described above
        are marked as NaN

        Additional filtering occurs when calculating monthly means (see Stats class).
        (if there are more than five daily values marked as NaN, the monthly
        mean is set to NaN). During this step, variables are also dropped
        if more than 75% of the months in their record period are marked as
        NaN

        Parameters
        ----------------
        variablesOfInterest: list
            the data that will be included in the output stations
        
        Returns
        ------------
        None
        """
        count = 0
        newstationlist = [] # this station list will only contain stations that have recorded data for the variablesOfInterest. (essentially removing stations that didn;t record data we wanted)
        numberOfStations = len(self.stations)
        print("reading " + str(numberOfStations) + " stations")
        startprocesstime = time.time()
        for station in self.stations: # iterate through the Station objects
            infile = open(os.path.join(self.dlyFileDir,station.stationId + ".dly"))
            line = infile.readline()
            datacount = 0
            varinfile = False
            while line != "":
                dataIdx = 21 # add 8 to get to the next data value
                qFlagIdx = 27 # add 8 to get the qFlag for the next data value
                sFlagIdx = 28 # add 8 to get the sFlag for the next data value. (source flag).
                # only include data that does not fail the quality assurance check (QFLAG1 must be blank (i.e. line[27] == " "))
                # other specifications could exist. For example, checking the MFLAG (measurement flag) or SFLAGE (source flag)
                curYear = int(line[11:15].strip())
                curMonth = int(line[15:17].strip())
                curDay = 1
                varName = line[17:21].strip() # TAVG, TMAX, TMIN, PRCP, etc...
                if varName in variablesOfInterest: # only process the stations that have the variables of interest. Otherwise, skip them
                    varinfile = True
                    if varName not in station.variables: # if variable not already in the station variables, create it
                        station.variables[varName] = ClimateVar(varName, "daily")
                    while dataIdx <= 261: # the last dataIdx is 261. iterate through the file line appending data and datetime objects to the ClimateVar object
                        if curDay <= calendar.monthrange(curYear,curMonth)[1]: # only process data in the time range of the month.
                            value = float(line[dataIdx:dataIdx+5].strip()) # the data value occupies 4 spaces in the txt, so slice appropriately.
                            qFlag = line[qFlagIdx] # the qFlag occupies only 1 space in the txt
                            sFlag = line[sFlagIdx] # the sFlag occupies only 1 space in the txt
                            # source flag must be coop summary of the day, asos network, environment canada, or global observing system
                            if qFlag == " " and value != -9999 and sFlag in ["0","6","7","A","C","G","R"]: # only include data passing quality assurance, and data that is not NoData
                                station.variables[varName].data.append(value)
                                station.variables[varName].timelist.append(datetime.date(year=curYear,month=curMonth,day=curDay))
                                datacount+=1
                            else:
                                station.variables[varName].data.append(np.nan) # if it didn't pass the quality assurance or it was NoData, append NaN
                                station.variables[varName].timelist.append(datetime.date(year=curYear,month=curMonth,day=curDay))
                                datacount+=1
                        dataIdx+=8
                        qFlagIdx+=8
                        sFlagIdx+=8
                        curDay+=1
                line = infile.readline()
            infile.close()
            #print("file processed: " + (os.path.join(self.dlyFileDir,station.stationId + ".dly")) + " time to process: " + str(time.time() - s))
            count+=1
            if count % 200 == 0: # print a status report every so often. count is the number of stations processed
                print("done with " + str(count) + " stations. " + str(int((count / float(numberOfStations))*100)) + "% complete.")
            if len(station.variables) > 0: # append the station to the new list only if it has variables with recorded data
                newstationlist.append(station)
        
        finalStationList = []
        for s in newstationlist: # filter out all variables with only nan values and all stations with only nan values
            newVarDict = {} # rebuild the station's variable dictionary. Only include variables that include valid values (not all nan)
            for v in s.variables:
                if np.nansum(s.variables[v].data) > 0: # if there are real values in the data (not just NaN)
                    newVarDict[v] = ClimateVar(v,"daily")
                    newVarDict[v].setAll(s.variables[v].data, s.variables[v].timelist)
            s.variables = newVarDict
            if s not in finalStationList and len(s.variables) > 0: # only append the station if it has variables that don't have all nan
                finalStationList.append(s)
        self.stations = finalStationList
        print("done reading stations. " + str(len(self.stations)) + " stations left after filtering")
        print("total data read time: " + str(time.time() - startprocesstime))                                        
    
    def exportToDat(self,out_dir):
        """
        will write every station in the StationPreprocessor to a .dat file 
        for gap filling in the ssa-mtm toolkit.
        
        A dat file here is a file with a single column of data
        This also writes out a metadata file. The output filename is the same as the 
        data's station ID and variable. 
        """
        if os.path.isfile(os.path.join(out_dir,"metadata_log.txt")): # the log file already exists, append to it.
            outmetadata = open(os.path.join(out_dir,"metadata_log.txt"),"a")
        else:
            outmetadata = open(os.path.join(out_dir,"metadata_log.txt"),"w")
        for station in self.stations:
            for var in station.variables:
                out_filename = station.stationId + "_" + var + ".dat"
                outmetadata.write(str(station) + "," + str(station.variables[var]) + "\n") # keep a log of meteadata about each file. this includes the station and variable information
                outfile = open(os.path.join(out_dir,out_filename),"w")
                for value in station.variables[var].data:
                	if np.isnan(value):
                		outfile.write("NaN")
                	else:
                		outfile.write(str(value))
                	outfile.write("\n")     

    def exportToJSON(self,filename):
        outfile = open(filename,"w")
        """ 
        will write the station and climate var data to json 
        this data is not geographic though. it will be queried based
        on stationId
        """
        outdata = {}
        for station in self.stations:
            outdata[station.stationId] = {}
            for var in station.variables:
                # datetime objects and numpy arrays are not json serializeable
                outdata[station.stationId][var] = {"data": [val for val in station.variables[var].data],
                                                    "timelist": [str(time)[:-9] for time in station.variables[var].timelist]}
        json_string = json.dumps(outdata)
        outfile.write(json_string)
        outfile.close()


    def exportToShapefile(self,filename): # could export a shapefile with climate data for a timeslice included.. maybe later
        driver = ogr.GetDriverByName("ESRI Shapefile")
        dataSource = driver.CreateDataSource(filename)
        spatialRef = osr.SpatialReference()
        spatialRef.SetWellKnownGeogCS("WGS84") # ImportFromEPSG() was not working. more gdal troubles.. :(
        layerName = filename.split("/")[-1][:-4] # the layerName is the shapefile name without the path and its file extension
        layer = dataSource.CreateLayer(layerName, spatialRef, ogr.wkbPoint)
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

        # dont know why the spatial reference isn't being set when I create the layer.
        # so, mannually edit the .prj file.
        spatialRef.MorphToESRI()
        file = open(filename[:-4] + ".prj", 'w')
        file.write(spatialRef.ExportToWkt())
        file.close()

class ClimateVar(object):
    
    def __init__(self,initName,initDataDescription):
        self.name = initName #TMAX, TMIN, PRCP, etc..
        self.dataDescription = initDataDescription # should be "daily", "monthly mean", "seasonal mean", "annual mean", "monthly anomaly"
        
        self.start = None
        self.end = None
        self.duration = None
        self.data = []
        self.timelist = []
        
    def getName(self):
        return self.name
    
    def setName(self,newName):
        self.name = newName
        
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

    def setAll(self,newData,newTimelist):
        """
        will set all relevant attributes of the ClimateVar
        """
        self.setData(newData)
        self.setTimelist(newTimelist)

    def __str__(self):
        return self.name + "," + self.dataDescription + "," + str(self.start) + "," + str(self.end)
            

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

    def __str__(self):
        return str(self.stationId) + "," + self.country + "," + self.state + "," + str(self.lat) + "," + str(self.lon) + "," + str(self.elev) + "," + str(self.hcn) + "," + str(self.crn) + "," + str(self.gsn) + "," + str(self.wmoId)
