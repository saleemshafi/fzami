#!/usr/bin/env python

from datetime import date
from math import *
from datetime import datetime

#--------------------- Copyright Block ----------------------

# PrayTime.py: Prayer Times Calculator (ver 1.2.1)
# Copyright (C) 2007-2010 PrayTimes.org

# Developer: Saleem Shafi
# License: GNU General Public License, ver 3

# TERMS OF USE:
	# Permission is granted to use this code, with or
	# without modification, in any website or application
	# provided that credit is given to the original work
	# with a link back to PrayTimes.org.

# This program is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY.

# PLEASE DO NOT REMOVE THIS COPYRIGHT BLOCK.

#--------------------- Help and Manual ----------------------

# User's Manual:
# http://praytimes.org/manual

# Calculating Formulas:
# http://praytimes.org/calculation



#------------------------ User Interface -------------------------


	# getPrayerTimes (date, latitude, longitude, timeZone)
	# getDatePrayerTimes (year, month, day, latitude, longitude, timeZone)

	# setCalcMethod (methodID)
	# setAsrMethod (methodID)

	# setFajrAngle (angle)
	# setMaghribAngle (angle)
	# setIshaAngle (angle)
	# setDhuhrMinutes (minutes)  	# minutes after mid-day
	# setMaghribMinutes (minutes)	# minutes after sunset
	# setIshaMinutes (minutes)	    # minutes after maghrib

	# setHighLatsMethod (methodID)  # adjust method for higher latitudes

	# setTimeFormat (timeFormat)
	# floatToTime24 (time)
	# floatToTime12 (time)
	# floatToTime12NS (time)


#------------------------- Sample Usage --------------------------

#	prayTime.setCalcMethod(prayTime.ISNA);
#	var times = prayTime.getPrayerTimes(new Date(), 43, -80, -5);
#	document.write('Sunrise = '+ times[1])

#------------------------ Constants --------------------------


	# Calculation Methods
PT_CALC_JAFARI     = 0    # Ithna Ashari
PT_CALC_KARACHI    = 1    # University of Islamic Sciences, Karachi
PT_CALC_ISNA       = 2    # Islamic Society of North America (ISNA)
PT_CALC_MWL        = 3    # Muslim World League (MWL)
PT_CALC_MAKKAH     = 4    # Umm al-Qura, Makkah
PT_CALC_EGYPT      = 5    # Egyptian General Authority of Survey
PT_CALC_CUSTOM     = 6    # Custom Setting
PT_CALC_TEHRAN     = 7    # Institute of Geophysics, University of Tehran

	# Juristic Methods
PT_JURIST_SHAFII     = 0    # Shafii (standard)
PT_JURIST_HANAFI     = 1    # Hanafi

	# Adjusting Methods for Higher Latitudes
PT_ADJUST_NONE        = 0    # No adjustment
PT_ADJUST_MIDNIGHT    = 1    # middle of night
PT_ADJUST_ONE_SEVENTH = 2    # 1/7th of night
PT_ADJUST_ANGLE       = 3    # angle/60th of night

	# Time Formats
PT_TIME_24         = 0    # 24-hour format
PT_TIME_12         = 1    # 12-hour format
PT_TIME_12NS       = 2    # 12-hour format with no suffix
PT_TIME_FLOAT      = 3    # floating point number

	# Time Names
PT_TIME_NAMES = ('Fajr', 'Sunrise',	'Dhuhr', 'Asr',	'Sunset', 'Maghrib', 'Isha')

PT_INVALID_TIME  = '-----'	 # The string used for invalid times

EPOCH = datetime.utcfromtimestamp(0)

#--------------------- PrayTime Class -----------------------

class PrayTime():

#---------------------- Global Variables --------------------
	def __init__( self ) :
		self.asrJuristic  = 0		# Juristic method for Asr
		self.dhuhrMinutes = 0		# minutes after mid-day for Dhuhr
		self.adjustHighLats = 1	    # adjusting method for higher latitudes
		self.timeFormat   = 0		# time format

#--------------------- Technical Settings --------------------
		# number of iterations needed to compute times
		self.numIterations = 1;		

#------------------- Calc Method Parameters --------------------
		self.calcParams = [ (16, 0, 4, 0, 14),
							(18, 1, 0, 0, 18),
							(15, 1, 0, 0, 15),
							(18, 1, 0, 0, 17),
							(18.5, 1, 0, 1, 90),
							(19.5, 1, 0, 0, 17.5),
							[],
							(18, 1, 0, 0, 17) ] 

		self.setCalcMethod( PT_CALC_MWL )

#-------------------- Interface Functions --------------------

	# return prayer times for a given date
	def getDatePrayerTimes(self, year, month, day, latitude, longitude, timeZone):
		self.lat = latitude
		self.lng = longitude
		self.timeZone = timeZone
		self.JDate = julianDate(year, month, day)- longitude/ (15* 24)
		return self.computeDayTimes()

	# return prayer times for a given date
	def getPrayerTimes(self, date, latitude, longitude, timeZone):
		return self.getDatePrayerTimes(date.year, date.month, date.day,	latitude, longitude, timeZone)

	# set the calculation method
	def setCalcMethod(self, methodID):
		self.calcMethod = methodID
		self.calcParams[PT_CALC_CUSTOM] = [0] * len(self.calcParams[methodID])
		for setting in xrange(0, 5):
			self.calcParams[PT_CALC_CUSTOM][setting] = self.calcParams[methodID][setting]

	# set the juristic method for Asr
	def setAsrMethod(self, methodID):
		if methodID < 0 or methodID > 1:
			return;
		self.asrJuristic = methodID;

	# set the angle for calculating Fajr
	def setFajrAngle(self, angle):
		self.calcParams[PT_CALC_CUSTOM][PT_FAJR_ANGLE] = angle
		self.setCalcMethod(PT_CALC_CUSTOM)

	# set the angle for calculating Maghrib
	def setMaghribAngle(self, angle):
		self.calcParams[PT_CALC_CUSTOM][1] = 0
		self.calcParams[PT_CALC_CUSTOM][2] = angle
		self.setCalcMethod(PT_CALC_CUSTOM)

	# set the angle for calculating Isha
	def setIshaAngle(self, angle):
		self.calcParams[PT_CALC_CUSTOM][3] = 0
		self.calcParams[PT_CALC_CUSTOM][4] = angle
		self.setCalcMethod(PT_CALC_CUSTOM)

	# set the minutes after mid-day for calculating Dhuhr
	def setDhuhrMinutes(self, minutes):
		self.dhuhrMinutes = minutes;

	# set the minutes after Sunset for calculating Maghrib
	def setMaghribMinutes(self, minutes):
		self.calcParams[PT_CALC_CUSTOM][1] = 1
		self.calcParams[PT_CALC_CUSTOM][2] = minutes
		self.setCalcMethod(PT_CALC_CUSTOM)

	# set the minutes after Maghrib for calculating Isha
	def setIshaMinutes(self, minutes):
		self.calcParams[PT_CALC_CUSTOM][3] = 1
		self.calcParams[PT_CALC_CUSTOM][4] = minutes
		self.setCalcMethod(PT_CALC_CUSTOM)

	# set adjusting method for higher latitudes
	def setHighLatsMethod(self, methodID):
		self.adjustHighLats = methodID

	# set the time format
	def setTimeFormat(self, timeFormat):
		self.timeFormat = timeFormat

#---------------------- Compute Prayer Times -----------------------

	# compute prayer times at given julian date
	def computeTimes(self, times):
		t = dayPortion(times)
		Fajr    = self.computeTime(180- self.calcParams[self.calcMethod][0], t[0])
		Sunrise = self.computeTime(180- 0.833, t[1])
		Dhuhr   = self.computeMidDay(t[2])
		Asr     = self.computeAsr(1+ self.asrJuristic, t[3])
		Sunset  = self.computeTime(0.833, t[4])
		Maghrib = self.computeTime(self.calcParams[self.calcMethod][2], t[5])
		Isha    = self.computeTime(self.calcParams[self.calcMethod][4], t[6])
		return [Fajr, Sunrise, Dhuhr, Asr, Sunset, Maghrib, Isha]

	# compute prayer times at given julian date
	def computeDayTimes(self):
		times = [5, 6, 12, 13, 18, 18, 18]  #default times
		for i in xrange( 0, self.numIterations):
			times = self.computeTimes(times)

		times = self.adjustTimes(times)
		return self.adjustTimesFormat(times)

	# adjust times in a prayer time array
	def adjustTimes(self, times):
		for i in xrange(0, 7):
			times[i] += self.timeZone - self.lng / 15.0
		times[2] += self.dhuhrMinutes / 60.0   # Dhuhr
		if self.calcParams[self.calcMethod][1] == 1: # Maghrib
			times[5] = times[4] + self.calcParams[self.calcMethod][2]/ 60.0
		if (self.calcParams[self.calcMethod][3] == 1): # Isha
			times[6] = times[5] + self.calcParams[self.calcMethod][4]/ 60.0

		if self.adjustHighLats != None:
			times = self.adjustHighLatTimes(times)
		return times

	# convert times array to given time format
	def adjustTimesFormat(self, times):
		if self.timeFormat == PT_TIME_FLOAT:
			return times
		for i in xrange(0,7):
			if self.timeFormat == PT_TIME_12:
				times[i] = floatToTime12(times[i])
			else: 
				if self.timeFormat == PT_TIME_12NS:
					times[i] = floatToTime12(times[i], true)
				else:
					times[i] = floatToTime24(times[i])
		return times

	# adjust Fajr, Isha and Maghrib for locations in higher latitudes
	def adjustHighLatTimes(self, times):
		nightTime = timeDiff(times[4], times[1]) # sunset to sunrise

		# Adjust Fajr
		FajrDiff = self.nightPortion(self.calcParams[self.calcMethod][0])* nightTime
		if isNaN(times[0]) or timeDiff(times[0], times[1]) > FajrDiff:
			times[0] = times[1]- FajrDiff

		# Adjust Isha
		IshaAngle = self.calcParams[self.calcMethod][4] if self.calcParams[self.calcMethod][3] == 0 else 18
		IshaDiff = self.nightPortion(IshaAngle)* nightTime
		if isNaN(times[6]) or timeDiff(times[4], times[6]) > IshaDiff:
			times[6] = times[4]+ IshaDiff

		# Adjust Maghrib
		MaghribAngle = self.calcParams[self.calcMethod][2] if self.calcParams[self.calcMethod][1] == 0 else 4
		MaghribDiff = self.nightPortion(MaghribAngle)* nightTime
		if isNaN(times[5]) or timeDiff(times[4], times[5]) > MaghribDiff:
			times[5] = times[4]+ MaghribDiff

		return times

	# the night portion used for adjusting times in higher latitudes
	def nightPortion(self, angle):
		if self.adjustHighLats == PT_ADJUST_ANGLE:
			return 1/60.0 * angle
		if self.adjustHighLats == PT_ADJUST_MIDNIGHT:
			return 1/2.0
		if self.adjustHighLats == PT_ADJUST_ONE_SEVENTH:
			return 1/7.0

#---------------------- Calculation Functions -----------------------

# References:
# http://www.ummah.net/astronomy/saltime
# http://aa.usno.navy.mil/faq/docs/SunApprox.html

	# compute mid-day (Dhuhr, Zawal) time
	def computeMidDay(self, t):
		T = equationOfTime(self.JDate + t)
		Z = fixhour(12 - T)
		return Z

	# compute time for a given angle G
	def computeTime(self, G, t):
		D = sunDeclination(self.JDate+ t)
		Z = self.computeMidDay(t);
		V = 1/15.0* darccos((-dsin(G)- dsin(D)* dsin(self.lat))/
				(dcos(D)* dcos(self.lat)))
		return Z+ (-V if G>90 else V)

	# compute the time of Asr
	def computeAsr(self, step, t):  # Shafii: step=1, Hanafi: step=2
		D = sunDeclination(self.JDate+ t)
		G = -darccot(step+ dtan(abs(self.lat- D)))
		return self.computeTime(G, t)

			
# compute declination angle of sun and equation of time
def sunPosition(jd):
	D = jd - 2451545.0
	g = fixangle(357.529 + 0.98560028* D)
	q = fixangle(280.459 + 0.98564736* D)
	L = fixangle(q + 1.915* dsin(g) + 0.020* dsin(2*g))

	R = 1.00014 - 0.01671*dcos(g) - 0.00014*dcos(2*g)
	e = 23.439 - 0.00000036* D

	d = darcsin(dsin(e)* dsin(L))
	RA = darctan2(dcos(e)* dsin(L), dcos(L))/ 15.0
	RA = fixhour(RA)
	EqT = q/15.0 - RA

	return (d, EqT)

# compute equation of time
def equationOfTime(jd):
	return sunPosition(jd)[1]

# compute declination angle of sun
def sunDeclination(jd):
	return sunPosition(jd)[0]
				
#---------------------- Misc Functions -----------------------

# convert hours to day portions
def dayPortion(times):
	for i in xrange(0,7):
		times[i] /= 24.0
	return times

# compute the difference between two times
def timeDiff(time1, time2):
	return fixhour(time2- time1)

def isNaN(value):
	return not isinstance( value, (float, int, long, complex) )

#---------------------- Julian Date Functions -----------------------

# calculate julian date from a calendar date
def julianDate(year, month, day):
	if month <= 2:
		year -= 1
		month += 12
	A = floor(year / 100)
	B = 2 - A + floor(A / 4)
	return floor(365.25 * (year + 4716)) + floor(30.6001 * (month + 1)) + day + B - 1524.5

# convert a calendar date to julian date (second method)
def calcJD(year, month, day):
	J1970 = 2440587.5
	theDay = date(year, month, day)
	days = (theDay - EPOCH).days
	return J1970 + days

#---------------------- Time Formatting Functions -----------------------

# convert float hours to 24h format
def floatToTime24(time):
	if isNaN(time):
		return PT_INVALID_TIME
	time = fixhour(time+ 0.5/ 60)  # add 0.5 minutes to round
	hours = floor(time)
	minutes = floor((time- hours)* 60)
	return "%02d:%02d" % (hours, minutes)

# convert float hours to 12h format
def floatToTime12(time, noSuffix):
	if isNaN(time):
		return PT_INVALID_TIME
	time = fixhour(time+ 0.5/ 60)  # add 0.5 minutes to round
	hours = floor(time)
	minutes = floor((time- hours)* 60)
	suffix = ' pm' if hours >= 12 else ' am'
	hours = (hours+ 12- 1)% 12+ 1
	return "%2d:%02d" % (hours, minutes) + ('' if noSuffix else suffix)

# convert float hours to 12h format with no suffix
def floatToTime12NS(time):
	return floatToTime12(time, true);

#---------------------- Trigonometric Functions -----------------------

def dsin(d):
    return sin(radians(d))

# degree cos
def dcos(d):
    return cos(radians(d))

# degree tan
def dtan(d):
    return tan(radians(d))

# degree arcsin
def darcsin(x):
    return degrees(asin(x))

# degree arccos
def darccos(x):
    return degrees(acos(x))

# degree arctan
def darctan(x):
    return degrees(atan(x))

# degree arctan2
def darctan2(y, x):
    return degrees(atan2(y, x))

# degree arccot
def darccot(x):
    return degrees(atan(1.0/x))

# range reduce angle in degrees.
def fixangle(angle):
	angle = angle - 360 * ( floor( angle / 360.0 ) )
	return angle + 360 if angle < 0 else angle

# range reduce hours to 0..23
def fixhour(hour):
	hour = hour - 24 * ( floor( hour / 24.0 ) )
	return hour + 24 if hour < 0 else hour


#---------------------- prayTime Object -----------------------

prayTime = PrayTime()

def main():
    application = webapp.WSGIApplication([('/api/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
