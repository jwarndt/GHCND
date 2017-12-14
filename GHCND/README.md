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
```__init__(initStationMetadata, initInventoryMetadata, initDlyFileDirectory)```  
constructs a preprocessor object to hold station data  
  #### Parameters:    
  - initStationsMetadata: string  
    - full file path to the ghcnd stations metadata file (ghcnd-stations.txt)  
  - initInventoryMetadata: string  
    - full file path to the ghcnd inventory metadata file (ghcnd-inventory.txt)  
  - initDlyFileDirectory: string  
    - path to the directory holding the ghcnd dly files (ghcnd_all)  
