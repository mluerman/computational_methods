import pandas as pd
import numpy as np
import time
from coordinate import *
from opensky_api import OpenSkyApi


class ATC_Data:
	def __init__(self):
		# Initialize live data API and state vector
		self.api = OpenSkyApi()
		self.aircraft_dict = {}
		self.aircraft_df = None


	def get_live_data(self, bounds=None):
		"""
		Get current aircraft data from OpenSky API and create a dataframe with info of interest
		Input:
			bounds - if only interested in aircraft within a specified lat and long range.
					 Otherwise, gets current data for all aircraft
		"""
		# Get current state vector for aircraft. If bbox argument is passed in, will
		# only get info for aircraft in that coordinate range
		if bounds:
			self.states = self.api.get_states(bbox=bounds)
		else:
			self.states = self.api.get_states()

		# For each aircraft, extract relevant values and place into dictionary
		for s in self.states.states:
		    self.aircraft_dict[s.icao24] = [s.latitude, s.longitude, s.heading, s.velocity,
		    		s.geo_altitude, s.vertical_rate, s.on_ground, s.callsign, time.time()-s.last_contact]

		# Create dataframe from dictionary
		self.aircraft_df = pd.DataFrame.from_dict(self.aircraft_dict, orient='index',
			columns=['Latitude', 'Longitude', 'Heading', 'Velocity', 'Altitude', 'Vertical Velocity',
					'On Ground', 'Callsign', 'Time Since Last Contact'])

		#print(self.aircraft_df)


	def get_csv_data(self, filename):
		# TODO record live data, make csv file from recorded info, then add in csv reader to work with
		# the recorded data. Alternatively pull csv data from openskyapi website
		pass


	def get_cpa_info(p0, u, q0, v):
		# TODO check if this works, debug
		# TODO add in an altitude filter so only aircraft within some height threshold are compared
		"""
		Find CPA distance and time to CPA between two aircraft
		Formulas at http://geomalgorithms.com/a07-_distance.html
		Input:
			p0, q0 - current 2D position vectors of aircraft one and two
			u, v   - current 2D velocity vectors of aircraft one and two
		Output:
			cpa distance and time to cpa
		"""
		# Calculate time to CPA
		if u - v == 0.0:
			time_to_cpa = 0
		else:
			time_to_cpa = np.dot((q0 - p0), (u-v)) / sum((u-v)**2)
		# Estimate position at CPA time
		pos1 = p0 + u * time_to_cpa
		pos2 = q0 + v * time_to_cpa
		# Calculate CPA distance
		cpa_distance = np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
		return cpa_distance, time_to_cpa


	def get_nearby_aircraft(self, pos, distance):
		#TODO actually implement this function, everything is just a placeholder currently
		"""
		Get aircraft within a distance theshold of a given coordinate position
		Input:
			pos 	 - Coordinate object reference position
			distance - theshold distance used to create a bounding box to return aircraft of interest
		Output:
			nearby_aircraft - dataframe of nearby aircraft with heading, velocity, and altitude info
		"""		
		bounds = ((pos[0]-distance, pos[1]-distance), (pos[0]+distance, pos[1]+distance))
		states = self.api.get_states(bbox=bounds)
		return states


	def nearest_neighbors_cpa(self, aircraft):
		# TODO Actually implement this function, currently everything is just a placeholder
		neighbors = self.get_nearby_aircraft(aircraft)
		for plane in neighbors:
			cpa = self.get_cpa_info(aircraft.thing1, aircraft.thing2, plane.thing1, plane.thing2)


if __name__ == "__main__":
	ad = ATC_Data()
	ad.get_live_data(bounds=(45.8389, 47.8229, 5.9962, 10.5226))
