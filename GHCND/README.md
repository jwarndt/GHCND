This is a small package for processing data from the Global Historical Climatology Network Daily (GHCND) dataset.

This package has the following dependencies:  
gdal  
numpy  
matplotlib  

Modules  
-----------  
preprocessor: a module for reading and preprocessing GHCND data  
stats: a module to calculate common climate statistics  
plotter: a module for plotting time series  
conversion: a module to convert between units  
  
  
# Module: preprocessor  
  
## Classes:   
GHCND.preprocessor.StationPreprocessor  
GHCND.preprocessor.Station  
GHCND.preprocessor.ClimateVar  
  
### GHCND.preprocessor.StationPreprocessor

#### Properties:  
stations: returns a list of GHCND.preprocessor.Station objects  
states: returns a list of state abbreviations  
countries: returns a list of country abbreviations  
  
### Methods:  

### init  
```__init__(initStationMetadata, initInventoryMetadata, initDlyFileDirectory)```  
constructs a preprocessor object to hold station data  
  ##### Parameters:    
  - initStationsMetadata: string  
    - full file path to the ghcnd stations metadata file (ghcnd-stations.txt)  
  - initInventoryMetadata: string  
    - full file path to the ghcnd inventory metadata file (ghcnd-inventory.txt)  
  - initDlyFileDirectory: string  
    - path to the directory holding the ghcnd dly files (ghcnd_all)  

### addStates  
```addStates(newStates)```  
Adds states to the station preprocessor. This will define the states for which you want to process station data for.  
  ##### Parameters:
  - newStates: list  
    - a list of strings. the strings should be state names found in the stateMap  

### removeState    
```removeState(state)```  
Remove states from the station preprocessor  
  ##### Parameters:  
  - state: string  
    - a state name  
    
### setStates    
```setStates(newStates)```  
Removes all states from the current list and resets them with the newStates.  
  ##### Parameters:
  - newStates: list  
    - a list of strings. The strings should be state names found in the stateMap  
    
### addCountries    
```addCountries(newCountries)```  
Adds countries to the station preprocessor. This will define the countries for which you want to process station data for.  
  ##### Parameters:
  - newCountries: list  
    - a list of strings. the strings should be country names found in the countryMap  

### removeCountry    
```removeCountry(country)```  
Remove countries from the station preprocessor  
  ##### Parameters:  
  - country: string  
    - a state name  
 
### setCountries   
```setCountries(newCountries)```  
Removes all countries from the current list and resets them with the newCountries.  
  ##### Parameters:
  - newStates: list  
    - a list of strings. The strings should be country names found in the countryMap  

### addStations   
```addStations()```  
Creates Station objects and stores them in the station preprocessor's ```stations``` attribute  

### clearStations  
```clearStations()```  
Clears the list of stations in the station preprocessor.  

### processDlyFiles   
```processDlyFiles(variablesOfInterest)```  
Parse the fixed width .dly files associated with each Station object present in the station preprocessor. The location of the .dly files is specified when initializing a StationPreprocessor object. For each station, create a ClimateVar object that will store the daily data and datetime objects. Data will only be processed for variables defined by the argument passed in for variablesOfInterest. If the station deos not contain the any of the variables, it will be dropped from the station preprocessor. Running this method when the station preprocessor has many stations will consume a lot of RAM. So in cases where you need to process data for many states/countries, you should chunk them up.  
  
Filtering occurs at this step. Daily data values will only be included if:
1. the measurement did not fail the quality assurance check (indicated by the quality flag in the .dly file)  
2. the measurement's source is from one of the following:  
  - U.S. Cooperative Summary of the Day (NCDC DSI-3200)  
  - CDMP Cooperative Summary of the Day (NCDC DSI-3206)  
  - U.S. Cooperative Summary of the Day -- Transmitted via WxCoder3 (NCDC DSI-3207)  
  - U.S. Automated Surface Observing System (ASOS). Real-time data (since January 1, 2006)  
  - Environment Canada  
  - Official Global Climate Observing System (GCOS) or other government-supplied data.  
  - NCEI Reference Network Database (Climate Reference Network and Regional Climate Reference Network).  
  
Daily data values that fail the filter step described above are marker as NaN.  

  ##### Parameters:
  - variablesOfInterest: list  
    - a list of strings. Each string is a variable name such as "TMAX", "TMIN", or "PRCP". This specifies which variables to process.  
    

### exportToDat  
```exportToDat(out_dir)```  
Exports the data in the station preprocessor to .dat files. There is a single .dat file for each station and variable. This will also record a metadata_log.txt file that can be used to reference the output .dat files. The name of each .dat file is the station ID. This function requires that the dly files have been processed.   
  ##### Parameters:  
  - out_dir: string  
    - The directory where the files will be written.  
    
### exportToShapefile    
```exportToShapefile(filename)```  
Exports the stations to a shapefile. This does not export any of the associated meteorological data with it.  
  ##### Parameters:  
  - filename: string  
    - the name of the shapefile. You need to include the file extension .shp in the filename.
    
### exportToJSON  
```exportToJSON(filename)```  
Exports the station and associated data to JSON. JSON object will appear in this form:  
```
{stationId1:   
    {variable1: 
        {"data": [value1, value2, ... , valuen],
         "timelist": [time1, time2, ..., timen]
         },
     variable2:
        {"data": [value1, value2, ... , valuen],
         "timelist": [time1, time2, ..., timen]
         }
    },
stationId2:
    {variable1: 
        {"data": [value1, value2, ... , valuen],
         "timelist": [time1, time2, ..., timen]
        }
    }
}     
```
