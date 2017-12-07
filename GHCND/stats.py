import numpy as np
import datetime
import calendar

validtimeframes = ["month","season","year"]
# default seasons are DJF, MAM, JJA, SON 

def calculateMean(stationCollection,timeframe):
    """
    input data will be modified so that the data is in the form
    of monthly, seasonal, or annual means.
    
    Parameters
    ------------
    stationCollections: StationPreprocessor
        a StationPreprocessor object that has stations and climate variables
    timeframe: string
        a string that indicates the timestep for which the mean will be calculated.
        monthly, seasonal, and annual means can be calculated
        
    Returns
    ----------
    None 
    """
    if timeframe not in validtimeframes:
        print("error: did not enter a valid timeframe")
        print("please enter a timeframe from the following: ")
        print(validtimeframes)
        return
    for station in stationCollection.stations: # for each station in the StationPreprocessor
        for varName in station.variables: # for each climate variable in the station object
            if timeframe == "month":
                self.__calculateMonthlyMean(station.variables[varName])
            elif timeframe == "season":
                self.__calculateSeasonalMean(station.variables[varName])
            else:           
                self.__calculateAnnualMean(station.variables[varName])

def __calculateMonthlyMean(climateVariable):
    timestep = 0
    
    monthlyMeans = np.array([])
    newTimelist = np.array([])
    while timestep < len(climateVariable.timelist):
        curDatetime = climateVariable.timelist[timestep]
        curDay = climateVariable.timelist[timestep].day
        curMonth = climateVariable.timelist[timestep].month
        curYear = climateVariable.timelist[timestep].year
        daysInMonth = calendar.monthrange(curYear,curMonth)[1] # number of days in the current month
        dataChunk = climateVariable.data[timestep:timestep+daysInMonth]
        if np.isnan(dataChunk).sum() > 5: # set the monthly mean to missing if more than 5 days of data are missing in the month
            monthlyMeans = np.append(monthlyMeans,np.nan)
        else:
            if climateVariable.name == "PRCP": # for prcp, it's cumulative
                monthlyMeans = np.append(monthlyMeans,np.nansum(dataChunk))
            elif climateVariable.name in ["TMAX","TMIN","TAVG"]: # for tmin, tmax, and tavg it's the mean
                monthlyMeans = np.append(monthlyMeans,np.nanmean(dataChunk))
        newTimelist = np.append(newTimelist,datetime.datetime(year=curYear,month=curMonth,day=1))
        timestep+=daysInMonth
        if timestep < len(climateVariable.timelist): # need to check if there are missing months
            nextDatetime = climateVariable.data[timestep] # the next month of data is this. Check to see if gaps need to be filled with nan
            if  (nextDatetime - curDatetime) == datetime.timedelta(days=daysInMonth): # if the next datetime object follows the current datetime object just processed, all is well
                pass
            else: # this means there are months of missing data. 
                missingDatetime = curDatetime + datetime.timedelta(calendar.monthrange(curDatetime.year, curDatetime.month)[1])
                while nextDatetime != missingDatetime:# iteratively add missing months until we hit the month that we know there is data for. 
                    monthlyMeans = np.append(monthlyMeans, np.nan)
                    newTimelist = np.append(newTimelist, missingDatetime)
                    missingDatetime = missingDatetime + datetime.timedelta(calendar.monthrange(curDatetime.year, curDatetime.month)[1])
    if (np.isnan(monthlyMeans).sum() / float(len(monthlyMeans))) > 0.75: # if more than 75% of the monthly values are missing. data is invalid, so remove
        climateVariable = None
    else:
        climateVariable.setData(monthlyMeans)
        climateVariable.setTimelist(newTimelist)
        climateVariable.dataDescription = "monthly mean"

def __calculateSeasonalMean():
    return NotImplemented

def __calculateAnnualMean():
    return NotImplemented

def calculateStandardizedAnomalies(stationCollection,timeframe,baselinePeriod):
    return NotImplemented
    """
    Parameters
    ------------
    stationCollections: StationPreprocessor
        a StationPreprocessor object that has stations and climate variables
    timeframe: string
        a string that indicates the timestep for which the mean will be calculated.
        monthly, seasonal, and annual means can be calculated
    baselinePeriod: list 
        containing two datetime objects to describe the bounds (inclusive)
        for the baseline period to calculate standardized anomalies
        from. The day in the datetime objects should be set to 15 ALLWAYS!!
    """
    if timeframe not in validtimeframes:
        print("error: did not enter a valid timeframe")
        print("please enter a timeframe from the following: ")
        print(validtimeframes)
        return
    for station in stationCollection.stations: # for each station in the StationPreprocessor
        for varName in station.variables: # for each climate variable in the station object
            
            # so... the data is assumed to be either daily, or at the same resolution
            # that the anomalies will be calculated for. For example, things will get wierd
            # if you try to calculate monthly anomalies by passing in annual data.
            if timeframe == "month":
                if station.variables[varName].dataDescription == "daily":
                    self.__calculateMonthlyMean(station.variables[varName])
                self.__calculateMonthlyAnomalies(station.variables[varName],baselinePeriod)
            elif timeframe == "season":
                if station.variables[varName].dataDescription == "daily":
                    self.__calculateSeasonalMean(station.variables[varName])
                self.__calculateSeasonalAnomalies(station.variables[varName],baselinePeriod)
            else:
                if station.variables[varName].dataDescription == "daily":
                    self.__calculateAnnualMean(station.variables[varName])
                self.__calculateAnnualAnomalies(station.variables[varName],baselinePeriod)
                
def __calculateMonthlyAnomalies(climateVariable,baselinePeriod):
    newdata = []
    first = climateVariable.timelist.index(baselinePeriod[0])
    last = climateVariable.timelist.index(baselinePeriod[1])
    baselineData = climateVariable.data[first:last+1]
    baselineTimelist = climateVariable.timelist[first:last+1]
    baselineMeanAndStd = [] # has the form [ [mean,standard deviation], [mean,standard deviation], ... , [mean,standard deviation]]
    for m in range(12):
        baselineMeanAndStd.append(np.mean(baselineData[m::12]),np.std(baselineData[m::12]))
    t = 0
    while t < len(climateVariable.data):
        anom = climateVariable.data[t] - baselineMeanAndStd[climateVariable.timelist[t].month-1][0] # the anomaly
        stdAnom = anom / baselineMeanAndStd[climateVariable.timelist[t].month-1][1]
        newdata.append(stdAnom)
        t+=1
    climateVariable.setData(newdata)