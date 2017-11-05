import numpy as np

class StationStats(object):
    validtimeframes = ["month","season","year"]
    # default seasons are DJF, MAM, JJA, SON 

    def __init__(self):
        pass

    def calculateMean(climateVariable,timeframe):
        """
        valid timeframes include: month, season, year
        """
        if timeframe not in validtimeframes:
            print("error: did not enter a valid timeframe")
            print("please enter a timeframe from the following: ")
            print(validtimeframes)
            return
        
        if climateVariable.name == 'PRCP':
            if timeframe == "month":
                self.__calculateCumulativeMonthlyPrcp(climateVariable)
            elif timeframe == "season":
                self.__calculateCumulativeSeasonalPrcp(climateVariable)
            else:           
                self.__calculateCumulativeAnnualPrcp(climateVariable)
        elif climateVariable.name in ["TAVG","TMIN","TMAX"]:
            if timeframe == "month":
                self.__calculateMonthlyMean(climateVariable)
            elif timeframe == "season":
                self.__calculateSeasonalMean(climateVariable)
            else:
                self.__calculateAnnualMean(climateVariable)
        else:
            # do some other stuff
            return

    def __calculateMonthlyMean(climateVariable):
        timestep = 0
        total = 0 # the running total 
        count = 0 # the number of days that go into the total

        monthlyMeans = []
        newTimelist = []
        while timestep < len(climateVariable.timelist):
            curDay = climateVariable.timelist[timestep].day
            curMonth = climateVariable.timelist[timestep].month
            if curDay == 1: # begin runningTotal and count on day 1
                 

                timestep+=1

    """def __calculateCumulativeMonthlyPrcp():

    def __calculateSeasonalMean():

    def __calculateCumulativeSeasonalPrcp():

    def __calculateAnnualMean():

    def __calculateCumulativeAnnualPrcp():"""
