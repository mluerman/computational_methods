# Coordinate class from Lab 2
# New method added to get the true heading to another coordinate

import math
import datetime


class Coordinate:
    '''A simple class to represent lat/lon values.'''
    
    def __init__(self,lat,lon):
        self.lat = float(lat)  # make sure it's a float
        self.lon = float(lon)  
        
    # Follows the specification described in the Aviation Formulary v1.46
    # by Ed Williams (originally at http://williams.best.vwh.net/avform.htm)
    def calc_dist(self, other):
        lat1 = deg2rad(self.lat)
        lon1 = deg2rad(self.lon)
        lat2 = deg2rad(other.lat)
        lon2 = deg2rad(other.lon)
        
        # there are two implementations of this function.
        # implementation #1:
        #dist_rad = math.acos(math.sin(lat1) * math.sin(lat2) 
        #                   + math.cos(lat1) * math.cos(lat2) * math.cos(lon1-lon2))

        # implementation #2: (less subject to numerical error for short distances)
        dist_rad=2*math.asin(math.sqrt((math.sin((lat1-lat2)/2))**2 +
                   math.cos(lat1)*math.cos(lat2)*(math.sin((lon1-lon2)/2))**2))

        return rad2nm(dist_rad)
    

    def calc_true_heading(self, other):
        #TODO Check if this works
        # Adapted from https://gist.github.com/jeromer/2005586
        lat1 = math.radians(self.lat)
        lat2 = math.radians(other.lat)

        diffLong = math.radians(other.lon - self.lon)

        x = math.sin(diffLong) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))

        initial_bearing = math.atan2(x, y)

        # Now we have the initial bearing but math.atan2 return values
        # from -180° to + 180° which is not what we want for a compass bearing
        # The solution is to normalize the initial bearing as shown below
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360

        return compass_bearing
        

# end of class Coordinate


# The following functions are of general use.

def dms_to_decimal(degrees,minutes,seconds):
    '''Convertes coordinates in dms to decimals.'''
    return degrees + minutes/60 + seconds/3600

def deg2rad(degrees):
    '''Converts degrees (in decimal) to radians.'''
    return (math.pi/180)*degrees

def rad2nm(radians):
    '''Converts a distance in radians to a distance in nautical miles.'''
    return ((180*60)/math.pi)*radians

def meters2nm(meters):
    '''Converts a distance in meters to a distance in nautical miles.'''
    return meters * 0.000539957
