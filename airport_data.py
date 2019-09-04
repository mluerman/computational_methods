import pandas as pd
import numpy as np
import urllib.request
import bs4
from coordinate import Coordinate, dms_to_decimal, deg2rad, rad2nm, meters2nm


class AirportData:
	def __init__(self):
		self.airport_df = None


	def get_csv_data(self, filename='airports.csv'):
		#https://openflights.org/data.html
		self.airport_df = pd.read_csv(filename, usecols=['Name','ICAO', 'Latitude', 'Longitude', 'Altitude'])
		#print(self.airport_df)


	def get_nearby_airports(self, pos, dist=250):
		"""
		Get the airports within a distance threshold of a given position
		Input:
			pos  - reference position, Coordinate object
			dist - theshold distance in terms of nauthical miles
		Output:
			nearby_airports - dataframe of airports that meet the filtering criteria
		"""
		# Create dataframe with airports within a distance threshold of pos
		dist_bool = self.airport_df.apply(lambda x: abs(pos.calc_dist(Coordinate(x['Latitude'], x['Longitude']))) < dist, axis=1)
		nearby_airports = self.airport_df[dist_bool]
		# Add a column with the distance between the position reference and each nearby airport
		nearby_airports['Distance'] = nearby_airports.apply(lambda x: pos.calc_dist(Coordinate(x['Latitude'], x['Longitude'])), axis=1)
		return nearby_airports


	def get_reachable_airports(self, pos, altitude, glide_ratio=20):
		"""
		Get the airports that an aircraft can feasibly glide to, based on its glide ratio and current altitude.
		Input:
			pos 		- aircraft's current position coordinate
			altitude 	- aircraft's current altitude (meters)
			glide_ratio - aircraft's glide ratio, default set to 20 (20 units of horizontal travel
						  for every unit of lost altitude)
		Output:
			valid_airports - pandas dataframe with reachable airports, with columns for buffer 
							 distance and true heading added
		"""
		# Get nearby airports and add glide distance column, which describes how far the aircraft can glide 
		# from its altitude to the altitude of each airport
		nearby_airports = self.get_nearby_airports(pos)
		nearby_airports['Glide Distance'] = nearby_airports['Altitude'].apply(lambda x: meters2nm((altitude - x)*glide_ratio))
		# Valid airports as those which are closer than the glide distance
		valid_airports = nearby_airports[nearby_airports['Glide Distance'] > nearby_airports['Distance']]
		return valid_airports


	def get_airport_lookup_info(self, icao):
		#TODO implement more scrapping to get more info of interest, such as comm frequencies
		"""
		Performs webscrapping on SkyVector to get more information about a given airport
		Input:
			icao - unique airport identification code
		Output:
			airport_info - dataframe containing the following information about the airport
						   of interest: .......
		"""
		# Get xml data for the airport corresponding to the icao code from url request, convert to bs4 object
		req = urllib.request.Request('https://skyvector.com/airport/'+icao)
		response = urllib.request.urlopen(req)
		self.page = bs4.BeautifulSoup(response.read(), "lxml")

		# Get all aptdata objects
		sections = self.page.find_all('div', class_='aptdata')
		# Iterate through each table, looking for values of interest
		for table in sections:
			# Determine which table type is being parsed
			title = table.find('div', class_='aptdatatitle').text
			# If runway table, isolate runway name and dimensions
			if 'Runway' in title:
				tr = table.find('tr')
				td = tr.find('td')
				runway_name = title
				runway_dim = td.text
			elif 'Operations' in title:
				pass
			elif 'Airport Comm' in title:
				pass
			else:
				continue


if __name__ == "__main__":
	ad = AirportData()
	ad.get_csv_data("airports.csv")
	#ad.get_reachable_airports(Coordinate(33, -118), 10000)
	ad.get_airport_lookup_info('KLAX')
