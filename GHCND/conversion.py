import numpy as np

# conversion functions

def TenthsCelsiusToCelsius(stationCollection):
	"""
	The station data is in tenths of a degree celsius.
	This will convert all temperature data in the station
	collection to Celsius

	Parameters:
	------------
	stationCollection: StationPreprocessor object

	Returns:
	----------
	None
	"""
	for s in stationCollection.stations:
		for v in s.variables:
			if v == "TMAX" or v == "TMIN" or v == "TAVG":
				s.variables[v].setData(np.array(s.variables[v].data) / 10.)

def CelsiusToFahrenheit(stationCollection):
	return NotImplemented

def FahrenheitToCelsius(stationCollection):
	return NotImplemented

def MillimetersToInches(stationCollection):
	return NotImplemented

def InchesToMillimeters(stationCollection):
	return NotImplemented