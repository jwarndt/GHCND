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
  
#### Methods:  

<b> init </b>  
```__init__(initStationMetadata, initInventoryMetadata, initDlyFileDirectory)```  
constructs a preprocessor object to hold station data  
  ##### Parameters:    
  - initStationsMetadata: string  
    - full file path to the ghcnd stations metadata file (ghcnd-stations.txt)  
  - initInventoryMetadata: string  
    - full file path to the ghcnd inventory metadata file (ghcnd-inventory.txt)  
  - initDlyFileDirectory: string  
    - path to the directory holding the ghcnd dly files (ghcnd_all)  

<b> addStates </b>  
```addStates(newStates)```  
Adds states to the station preprocessor. This will define the states for which you want to process station data for.  
  ##### Parameters:
  - newStates: list  
    - a list of strings. the strings should be state names found in the stateMap  

<b> removeState </b>  
```removeState(state)```  
Remove states from the station preprocessor  
  ##### Parameters:  
  - state: string  
    - a state name  
    
<b> setStates </b>  
```setStates(newStates)```  
Removes all states from the current list and resets them with the newStates.  
  ##### Parameters:
  - newStates: list  
    - a list of strings. The strings should be state names found in the stateMap  
    
<b> addCountries </b>  
```addCountries(newCountries)```  
Adds countries to the station preprocessor. This will define the countries for which you want to process station data for.  
  ##### Parameters:
  - newCountries: list  
    - a list of strings. the strings should be country names found in the countryMap  

<b> removeCountry </b>  
```removeCountry(country)```  
Remove countries from the station preprocessor  
  ##### Parameters:  
  - country: string  
    - a state name  
 
<b> setCountries </b>  
```setCountries(newCountries)```  
Removes all countries from the current list and resets them with the newCountries.  
  ##### Parameters:
  - newStates: list  
    - a list of strings. The strings should be country names found in the countryMap  

<b> addStations </b>  
```addStations()```  
Creates Station objects and stores them in the station preprocessor's ```stations``` attribute  

<b> clearStations </b>  
```clearStations()```  
Clears the list of stations in the station preprocessor.  

<b> processDlyFiles </b>  
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
    

