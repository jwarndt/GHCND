import datetime
import numpy as np
import matplotlib.pyplot as plt


def plotStationSeries(stationObject, variableName, saveFigDirectory=None):
    """
    the plotter assumes we are working in celsius
    the plotter only plots axis labels for temperature and
    precipitation variables.

    Parameters:
    -------------
    stationObjects: a Station object
        a station object created by the station
        preprocessor when adding stations with
        state and country name
    variableName: string
        the name of the variable you want to plot
        a variableName is only valid if that variable
        exists in the station
    saveFigDirectory: string
        the path to the directory in which you want to save
        the figure. default is None (the figure won't save) 

    Returns:
    ---------
    plt.show(): a matplot lib plot
    """
    if variableName not in stationObject.variables:
        print("error: variable doesn't exist in station")
        return
    x = stationObject.variables[variableName].timelist
    y = stationObject.variables[variableName].data
    plt.figure(figsize=(20,10))
    plt.plot(x, y, label=variableName)
    plt.xlabel('time')
    if variableName in ["TMAX","TMIN","TAVG"]:
        plt.ylabel("temperature (C)")
    elif variableName == "PRCP":
        plt.ylabel("precipitation (mm)")
    plt.title("Station ID: " + stationObject.stationId + ". " + stationObject.variables[variableName].dataDescription + " " + variableName)
    plt.legend()
    if saveFigDirectory != None:
        plt.savefig(saveFigDirectory + "/" + stationObject.stationId + "_" + stationObject.variables[variableName].dataDescription + "_" + variableName + ".png")
    plt.show()


def plotOutFile(filename):
    # DEPRECATED
    """
    quick plot of data values outputted from the gap fill software ssa-mtm
    """
    infile = open(filename,"r")
    line = infile.readline()
    data_array = []
    while line != "":
        data_array.append(float(line))
        line = infile.readline()
    plt.figure(figsize=(20,10))
    plt.plot(range(len(data_array)), data_array)
    plt.show()

