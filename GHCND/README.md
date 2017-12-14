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


Module: preprocessor

Classes:
---------
GHCND.preprocessor.StationPreprocessor

Methods:
-----------
__init__(initStationMetadata, initInventoryMetadata, initDlyFileDirectory)
    Parameters:
    -----------
    initStationsMetadata: string
        full file path to the ghcnd stations metadata file (ghcnd-stations.txt)
    initInventoryMetadata: string
        full file path to the ghcnd inventory metadata file (ghcnd-inventory.txt)
    initDlyFileDirectory: string
        path to the directory holding the ghcnd dly files (ghcnd_all)
        
