import datetime
import numpy as np
import matplotlib.pyplot as plt

# the plotter assumes we are working in celsius
# the plotter only plots axis labels for a few variables.
def plotStationSeries(stationObject, variableName, saveFigDirectory=None):
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
    # quick plot of data values outputted from the gap fill software
    infile = open(filename,"r")
    line = infile.readline()
    data_array = []
    while line != "":
        data_array.append(float(line))
        line = infile.readline()
    plt.figure(figsize=(20,10))
    plt.plot(range(len(data_array)), data_array)
    plt.show()

