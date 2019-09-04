import pandas as pd
import numpy as np
import urllib.request
import bs4
from coordinate import Coordinate, dms_to_decimal, deg2rad, rad2nm, meters2nm


class AirportData:
	def __init__(self):
		self.airport_df = None


	def bound_csv_data(self, filename, bbox=None):
		pass


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
		dist_bool = self.airport_df.apply(lambda x: abs(pos.calc_dist(Coordinate(x['Latitude'], x['Longitude']))) < dist, axis=1)
		nearby_airports = self.airport_df[dist_bool]
		nearby_airports['Distance'] = nearby_airports.apply(lambda x: pos.calc_dist(Coordinate(x['Latitude'], x['Longitude'])), axis=1)
		#print(nearby_airports)
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
		nearby_airports = self.get_nearby_airports(pos)
		print(nearby_airports)
		nearby_airports['Glide Distance'] = nearby_airports['Altitude'].apply(lambda x: meters2nm((altitude - x)*glide_ratio))

		valid_airports = nearby_airports[nearby_airports['Glide Distance'] > nearby_airports['Distance']]
		print(valid_airports)
		return valid_airports


	def get_airport_lookup_info(self, icao):
		# Get xml data from url request, convert to bs4 object
		req = urllib.request.Request('https://skyvector.com/airport/'+icao)
		response = urllib.request.urlopen(req)
		self.page = bs4.BeautifulSoup(response.read(), "lxml")

		sections = self.page.find_all('div', class_='aptdata')
		for table in sections:

			title = table.find('div', class_='aptdatatitle').text
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