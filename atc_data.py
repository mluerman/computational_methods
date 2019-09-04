import pandas as pd
import numpy as np
import time
from opensky_api import OpenSkyApi


class ATC_Data:
	def __init__(self):
		# Initialize live data API and state vector
		self.api = OpenSkyApi()
		self.aircraft_dict = {}
		self.aircraft_df = None


	def get_live_data(self, bounds=None):
		"""
		Get aircraft atc data from 
		Input:
			bounds - if only interested in aircraft within a specified lat and long range.
					 Otherwise, gets current data for all aircraft
		"""
		# Get current state vector
		if bounds:
			self.states = self.api.get_states(bbox=bounds)
		else:
			self.states = self.api.get_states()

		# For each aircraft, extract relevant values and place into dictionary
		for s in self.states.states:
		    self.aircraft_dict[s.icao24] = [s.latitude, s.longitude, s.heading, s.velocity,
		    		s.geo_altitude, s.vertical_rate, s.on_ground, s.callsign, time.time()-s.last_contact]

		self.aircraft_df = pd.DataFrame.from_dict(self.aircraft_dict, orient='index',
			columns=['Latitude', 'Longitude', 'Heading', 'Velocity', 'Altitude', 'Vertical Velocity',
					'On Ground', 'Callsign', 'Time Since Last Contact'])

		print(self.aircraft_df)


	def get_csv_data(self, filename):
		pass


	def get_cpa_info(p0, u, q0, v):
		"""
		Find CPA distance and time to CPA between two aircraft
		Input:
			p0, q0 - current 3D position vectors of aircraft one and two
			u, v   - current 3D velocity vectors of aircraft one and two
		Output:
			cpa distance and time to cpa
		"""
		# formulas at http://geomalgorithms.com/a07-_distance.html
		if u - v == 0.0:
			time_to_cpa = 0
		else:
			time_to_cpa = np.dot((q0 - p0), (u-v)) / sum((u-v)**2)
		pos1 = p0 + u * time_to_cpa
		pos2 = q0 + v * time_to_cpa
		cpa_distance = np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
		return cpa_distance, time_to_cpa


	def get_nearby_aircraft(self, aircraft, distance):
		pos = aircraft.position
		bounds = ((pos[0]-distance, pos[1]-distance), (pos[0]+distance, pos[1]+distance))
		states = self.api.get_states(bbox=bounds)
		return states


	def nearest_neighbors_cpa(self, aircraft):
		neighbors = self.get_nearby_aircraft(aircraft)
		for plane in neighbors:
			cpa = self.get_cpa_info(aircraft.thing1, aircraft.thing2, plane.thing1, plane.thing2)


if __name__ == "__main__":
	ad = ATC_Data()
	ad.get_live_data(bounds=(45.8389, 47.8229, 5.9962, 10.5226))
