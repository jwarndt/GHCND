This is a small package for processing data from the Global Historical Climatology Network Daily (GHCND) dataset. It is not fully functional yet. The only way to use it at this point is to download the master branch, have the dependencies installed, and work within the GHCND folder. It was developed in Python 2.7. I haven't tested it with Python 3.5 or 3.6.  

This package has the following dependencies:  
gdal  (reading and writing spatial data. Specifically for exporting data to shapefile)
numpy  (general computation)
matplotlib  (for plotting timeseries using the plotter module)

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
  
### Class: GHCND.preprocessor.StationPreprocessor

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
  ##### Parameters:
  - filename: string  
    - the name of the output file  
    
### Class: GHCND.preprocessor.Station  

#### Properties:  
name: the name of the station  
stationId: the station ID
country: the country the station is in  
state: the state the station is in. This will be None if it is a station outsite the United States or Canada.  
lat: latitude  
lon: longitude  
elev: elevation  
variables: a dictionary where the keys are variable names ("TMAX","TMIN","PRCP") and the values are ClimateVar objects  
crn: a boolean saying whether the station is part of the U.S. Climate Reference Network or U.S. Regional Climate Network Station  
hcn: a boolean saying whether the station is part of the U.S. Historical CLimatology Network (HSN)  
gsn: a boolean saying whether the station is part of the GCOS Surface Network (GSN)  
wmoId: the world meteorlogical organization station ID. This will be None for stations not in the wmo.  

### Class: GHCND.preprocessor.ClimateVar  

#### Properties:  
name: the variable name ("TMAX", "TMIN", "PRCP", etc...)  
dataDescription: a description of the data in the climate variable ("daily", "monthly_mean", etc...)  
start: the date corresponding to the first recorded value in the variable's data    
end: the date corresponding to the last recorded value in the variable's data    
duration: the length of the record  
data: a list of values  
timelist: a list of datetime objects  


# Module: stats  
A module for calculating basic climate statistics on stations and variables in the station preprocessor.  

#### Functions:  

### calculateMean  
Calculates the mean for a given timeframe all stations and variables in a station preprocessor object. 
```calculateMean(stationPreprocessor, timeframe)```  
  ##### Parameters:  
  - stationPreprocessor: a stationPreprocessor object  
    - should have stations and climate variables in it.
  - timeframe: string
    - a timeframe that will be used to calculate the mean. For example, to calculate monthly mean, use "month". The only valid timeframe at this point is "month". Future releases will include "season" and "annual".  
    
# Module: plotter  
A module for plotting data in a climate variable.  

#### Functions:  

### plotStationSeries  
Creates a time series plot of a variable for a given station.  
```plotStationSeries(stationObject, variableName, saveFigDirectory=None)```  
  ##### Parameters:  
  - stationObject: a Station object  
    - a station from a station preprocessor  
  - variableName: string  
    - the name of the variable to plot ("TMAX","TMIN","PRCP")  
  - saveFigDirectory: string  
    - this defaults to None if not specified. Otherwise, pass in the name of the directory that you want to write the time series plot to. Times series are saved as .png. The file name is the station Id.  
    
# Module: conversion  
A module for converting between units. This is not implemented entirely yet. It's used within the other modules.  
