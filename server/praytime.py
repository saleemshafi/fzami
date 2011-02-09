#!/usr/bin/env python

from datetime import date
from datetime import datetime
from math import *
from trig import *
import re

# --------------------- Copyright Block ----------------------

# PrayTimes.py: Prayer Times Calculator (ver 2.1)
# Copyright (C) 2007-2010 PrayTimes.org

# Developer: Hamid Zarrabi-Zadeh
#			 Saleem Shafi
# License: GNU LGPL v3.0

# TERMS OF USE:
	# Permission is granted to use this code, with or
	# without modification, in any website or application
	# provided that credit is given to the original work
	# with a link back to PrayTimes.org.

# This program is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY.

# PLEASE DO NOT REMOVE THIS COPYRIGHT BLOCK.

# --------------------- Help and Manual ----------------------

# User's Manual:
# http://praytimes.org/manual

# Calculation Formulas:
# http://praytimes.org/calculation

# ------------------------ User Interface -------------------------

	# getTimes (date, coordinates, timeZone [, dst [, timeFormat]])

	# setMethod (method)       // set calculation method
	# adjust (parameters)      // adjust calculation parameters
	# tune (offsets)           // tune times by given offsets

	# getMethod ()             // get calculation method
	# getSetting ()            // get current calculation parameters
	# getOffsets ()            // get current time offsets

#------------------------- Sample Usage --------------------------

	# PT = PrayTimes('ISNA');
	# times = PT.getTimes(date.today(), (-80, 43), -5);
	# print 'Sunrise = ', times['sunrise']

#------------------------ Constants --------------------------

# Time Names
PT_TIME_NAMES = {
		'imsak'    : 'Imsak',
		'fajr'     : 'Fajr',
		'sunrise'  : 'Sunrise',
		'dhuhr'    : 'Dhuhr',
		'asr'      : 'Asr',
		'sunset'   : 'Sunset',
		'maghrib'  : 'Maghrib',
		'isha'     : 'Isha',
		'midnight' : 'Midnight'
	}

PT_ASR_METHODS = {'Standard': 1, 'Hanafi': 2}

# Default Parameters in Calculation Methods
PT_CALC_DEFAULT_PARAMS = {
		'maghrib': '0 min', 'midnight': 'Standard'
	}

# Calculation Methods
PT_CALC_METHODS = {
		'MWL': {
			'name': 'Muslim World League',
			'params': { 'fajr': 18, 'isha': 17 } },
		'ISNA': {
			'name': 'Islamic Society of North America (ISNA)',
			'params': { 'fajr': 15, 'isha': 15 } },
		'Egypt': {
			'name': 'Egyptian General Authority of Survey',
			'params': { 'fajr': 19.5, 'isha': 17.5 } },
		'Makkah': {
			'name': 'Umm Al-Qura University, Makkah',
			'params': { 'fajr': 18.5, 'isha': '90 min' } },  # fajr was 19 degrees before 1430 hijri
		'Karachi': {
			'name': 'University of Islamic Sciences, Karachi',
			'params': { 'fajr': 18, 'isha': 18 } },
		'Tehran': {
			'name': 'Institute of Geophysics, University of Tehran',
			'params': { 'fajr': 17.7, 'isha': 14, 'maghrib': 4.5, 'midnight': 'Jafari' } },  # isha is not explicitly specified in this method
		'Jafari': {
			'name': 'Shia Ithna-Ashari, Leva Institute, Qum',
			'params': { 'fajr': 16, 'isha': 14, 'maghrib': 4, 'midnight': 'Jafari' } }
	}

# set methods defaults
for method, config in PT_CALC_METHODS.iteritems():
	for name, value in PT_CALC_DEFAULT_PARAMS.iteritems():
		if not name in config['params'] or config['params'][name] is None:
			config['params'][name] = value

PT_TIME_SUFFIX = ("am", "pm")
PT_INVALID_TIME  = '-----'	 # The string used for invalid times

EPOCH = datetime.utcfromtimestamp(0)

#----------------------- PrayTimes Object ------------------------

class PrayTimes():

	def __init__( self, method = "MWL" ) :
		self.settings = {
			"imsak"    : '10 min',
			"dhuhr"    : '0 min',
			"asr"      : 'Standard',
			"highLats" : 'NightMiddle'
			}
		self.numIterations = 1
		self.timeFormat = "24h"
		self.offsets = {}
		
	#---------------------- Initialization -----------------------
			
		# initialize settings
		self.calcMethod = method if method in PT_CALC_METHODS else 'MWL'
		params = PT_CALC_METHODS[self.calcMethod]['params']
		for name, value in params.iteritems():
			self.settings[name] = value

		# init time offsets
		for name in PT_TIME_NAMES:
			self.offsets[name] = 0

#-------------------- Interface Functions --------------------
	def setMethod(self, method):
		if method in PT_CALC_METHODS:
			self.adjust(PT_CALC_METHODS[method].params)
			self.calcMethod = method

	def adjust(self, params):
		for name, value in params.iteritems():
			self.settings[name] = value

	def tune(self, timeOffsets):
		for name, value in timeOffsets.iteritems():
			self.offsets[name] = value
			
	def getMethod(self):
		return self.method

	def getSettings(self):
		return self.settings
		
	def getOffsets(self):
		return self.offsets

	def getDefaults(self):
		return PT_CALC_METHODS

	# return prayer times for a given date
	def getTimes(self, date, coords, timezone, dst = False, format = None):
		self.lat = coords[0]
		self.lng = coords[1]
		self.elv = coords[2] if len(coords)>2 else 0
		if not format == None:
			self.timeFormat = format
		self.timeZone = timezone + ( 1 if dst else 0 )
		self.jDate = julian(date.year, date.month, date.day) - self.lng / (15 * 24.0)
		return self.computeTimes()


#---------------------- Compute Prayer Times -----------------------

	# compute mid-day time
	def midDay(self, time):
		eqt = sunPosition(self.jDate + time)[1]
		return fixhour(12 - eqt)

	# compute time for a given angle 
	def sunAngleTime(self, angle, time, direction = None):
		decl = sunPosition(self.jDate + time)[0]
		noon = self.midDay(time)
		t = 1/15.0* darccos((-dsin(angle)- dsin(decl)* dsin(self.lat))/
				(dcos(decl)* dcos(self.lat)))
		return noon+ (-t if direction == 'ccw' else t)

	# compute the time of Asr
	def asrTime(self, factor, time):  # Shafii: factor=1, Hanafi: step=2
		decl = sunPosition(self.jDate + time)[0]
		angle = -darccot(factor + dtan(abs(self.lat - decl)))
		return self.sunAngleTime(angle, time)

	# compute prayer times at given julian date
	def computePrayerTimes(self, times):
		times = dayPortion(times)
		params = self.settings
		
		imsak   = self.sunAngleTime( eval(params['imsak']), times['imsak'], 'ccw')
		fajr    = self.sunAngleTime( eval(params['fajr']), times['fajr'], 'ccw')
		sunrise = self.sunAngleTime( riseSetAngle(self.elv), times['sunrise'], 'ccw')
		dhuhr   = self.midDay(times['dhuhr'])
		asr     = self.asrTime(asrFactor(params['asr']), times['asr'])
		sunset  = self.sunAngleTime( riseSetAngle(self.elv), times['sunset'])
		maghrib = self.sunAngleTime(eval(params['maghrib']), times['maghrib'])
		isha    = self.sunAngleTime(eval(params['isha']), times['isha']) 
		return {
				'imsak': imsak, 'fajr': fajr, 'sunrise': sunrise, 'dhuhr': dhuhr,
				'asr': asr, 'sunset': sunset, 'maghrib': maghrib, 'isha': isha
			}

	# compute prayer times
	def computeTimes(self):
		times = {
				'imsak': 5, 'fajr': 5, 'sunrise': 6, 'dhuhr': 12,
				'asr': 13, 'sunset': 18, 'maghrib': 18, 'isha': 18
			}
		# main iterations
		for i in xrange( 0, self.numIterations):
			times = self.computePrayerTimes(times)
		times = self.adjustTimes(times)
		# add midnight time
		if self.settings['midnight'] == 'Jafari':
			times['midnight'] = times['maghrib'] + timeDiff(times['maghrib'], times['fajr']) / 2
		else:
			times['midnight'] = times['sunset'] + timeDiff(times['sunset'], times['sunrise']) / 2

		times = self.tuneTimes(times)
		return self.modifyFormats(times)
		
	# adjust times in a prayer time array
	def adjustTimes(self, times):
		params = self.settings
		tzAdjust = self.timeZone - self.lng / 15.0
		for t,v in times.iteritems():
			times[t] += tzAdjust

		if params['highLats'] != None:
			times = self.adjustHighLats(times)

		if isMin(params['imsak']):
			times['imsak'] = times['fajr'] - eval(params['imsak']) / 60.0
		# need to ask about 'min' settings
		if isMin(params['maghrib']):
			times['maghrib'] = times['sunset'] - eval(params['maghrib']) / 60.0
		if isMin(params['isha']):
			times['isha'] = times['maghrib'] - eval(params['isha']) / 60.0
		times['dhuhr'] += eval(params['dhuhr']) / 60.0

		return times

	# apply offsets to the times
	def tuneTimes(self, times):
		for name, value in times.iteritems():
			times[name] += self.offsets[name] / 60.0
		return times

	# convert times to given time format
	def modifyFormats(self, times):
		for name, value in times.iteritems():
			times[name] = getFormattedTime(times[name], self.timeFormat)
		return times
	
	# adjust times for locations in higher latitudes
	def adjustHighLats(self, times):
		params = self.settings
		nightTime = timeDiff(times['sunset'], times['sunrise']) # sunset to sunrise
		times['imsak'] = self.adjustHLTime(times['imsak'], times['sunrise'], eval(params['imsak']), nightTime, 'ccw')
		times['fajr']  = self.adjustHLTime(times['fajr'], times['sunrise'], eval(params['fajr']), nightTime, 'ccw')
		times['isha']  = self.adjustHLTime(times['isha'], times['sunset'], eval(params['isha']), nightTime)
		times['maghrib'] = self.adjustHLTime(times['maghrib'], times['sunset'], eval(params['maghrib']), nightTime)
		return times

	# adjust a time for higher latitudes
	def adjustHLTime(self, time, base, angle, night, direction = None):
		portion = self.nightPortion(angle, night)
		diff = timeDiff(time, base) if direction == 'ccw' else timeDiff(base, time)
		if isNaN(time) or diff > portion:
			time = base + (-portion if direction == 'ccw' else portion)
		return time

	# the night portion used for adjusting times in higher latitudes
	def nightPortion(self, angle, night):
		method = self.settings['highLats']
		portion = 1/2.0  # midnight
		if method == 'AngleBased':
			portion = 1/60.0 * angle
		if method == 'OneSeventh':
			portion = 1/7.0
		return portion * night


#---------------------- Calculation Functions -----------------------

# References:
# http://www.ummah.net/astronomy/saltime
# http://aa.usno.navy.mil/faq/docs/SunApprox.html
			
# convert hours to day portions
def dayPortion(times):
	for i in times:
		times[i] /= 24.0
	return times

# compute declination angle of sun and equation of time
# Ref: http://aa.usno.navy.mil/faq/docs/SunApprox.php
def sunPosition(jd):
	D = jd - 2451545.0
	g = fixangle(357.529 + 0.98560028* D)
	q = fixangle(280.459 + 0.98564736* D)
	L = fixangle(q + 1.915* dsin(g) + 0.020* dsin(2*g))

	R = 1.00014 - 0.01671*dcos(g) - 0.00014*dcos(2*g)
	e = 23.439 - 0.00000036* D

	RA = darctan2(dcos(e)* dsin(L), dcos(L))/ 15.0
	eqt = q/15.0 - fixhour(RA)
	decl = darcsin(dsin(e)* dsin(L))

	return (decl, eqt)

# get asr shadow factor
def asrFactor(asrParam):
	return PT_ASR_METHODS[asrParam] if asrParam in PT_ASR_METHODS else eval(asrParam)

# return sun angle for sunset/sunrise
def riseSetAngle(elevation = 0):
	elevation = 0 if elevation == None else elevation
	return 0.833 + 0.0347 * sqrt(elevation) # an approximation

# convert float time to the given format (see timeFormats)
def getFormattedTime(time, format, suffixes = None):
	if isNaN(time):
		return PT_INVALID_TIME
	if format == 'Float':
		return time
	if suffixes == None:
		suffixes = PT_TIME_SUFFIX

	time = fixhour(time+ 0.5/ 60)  # add 0.5 minutes to round
	hours = floor(time)
	
	minutes = floor((time- hours)* 60)
	suffix = suffixes[ 0 if hours < 12 else 1 ] if format == '12h' else ''
	formattedTime = "%02d:%02d" % (hours, minutes) if format == "24h" else "%d:%02d" % ((hours+11)%12+1, minutes)
	return formattedTime + suffix

#---------------------- Misc Functions -----------------------

# compute the difference between two times
def timeDiff(time1, time2):
	return fixhour(time2- time1)

def isNaN(value):
	return not isinstance( value, (float, int, long, complex) )

# convert given string into a number
def eval(str):
	return int(re.split('[^0-9.+-]', ""+str, 1)[0]) if isNaN(str) else str

# detect if input contains 'min'
def isMin(arg):
	return isinstance( arg, str) and arg.find('min') > -1


#---------------------- Julian Date Functions -----------------------

# calculate julian date from a calendar date
def julian(year, month, day):
	if month <= 2:
		year -= 1
		month += 12
	A = floor(year / 100)
	B = 2 - A + floor(A / 4)
	return floor(365.25 * (year + 4716)) + floor(30.6001 * (month + 1)) + day + B - 1524.5


#---------------------- prayTime Object -----------------------

prayTime = PrayTimes()
