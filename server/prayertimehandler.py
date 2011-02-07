#!/usr/bin/env python

from google.appengine.ext import webapp
from praytime import *
from datetime import date

class PrayerTimeHandler(webapp.RequestHandler):
	def get(self, dateParam):
		if (dateParam == ""):
			today = date()
		else:
			year = int(dateParam[:4])
			month = int(dateParam[4:6])
			day = int(dateParam[-2:])
			today = date(year, month, day)

		# what if we create a settings obj, serialize it to a cookie, and deserialize
		# for each req as a starting point, then apply any query params on top of that?
		# i don't think this should affect caching
		longitude = float(self.request.get("longitude"))
		latitude = float(self.request.get("latitude"))
		elevation = self.request.get("elevation")
		if (elevation != ""):
			location = ( longitude, latitude, float(elevation) )
		else :
			location = ( longitude, latitude )
		timezone = float(self.request.get("timezone-offset")) if self.request.get("timezone-offset") != "" else -6
		format = self.request.get("format")
		format = format if format in ('24h', '12h', '12ns') else '24h'
		dst = 1 if self.request.get("dst") == "true" else 0
		method = self.request.get("method")
		method = method if method in PT_CALC_METHODS.keys() else "MWL"
		returnSettings = self.request.get("debug") or 0
		# customizations
		settings = {}
		for opt in ("asr", "midnight", "highLats", "fajr", "imsak", "maghrib", "isha" ):
			value = self.request.get(opt)
			if value != "":
				settings[opt] = value
		value = self.request.get("zuhr")
		if value != "":
			settings["dhuhr"] = value

		offsets = {}
		for offset in ("fajr", "zuhr", "asr", "maghrib", "isha"):
			value = self.request.get(offset+"-offset")
			if value != "":
				offsets[offset] = int(value)
			
		praytime = PrayTime(method)
		praytime.adjust(settings)
		praytime.tune(offsets)
		times = praytime.getTimes( today, location, timezone, dst, format )

		#self.response.headers['Content-Type'] = 'application/json'
		jsonResponse = '{"date":"'+dateParam+'"'
		jsonResponse +=	', "times":{"imsak":"'+times["imsak"]+'"'
		jsonResponse +=	', "fajr":"'+times["fajr"]+'"'
		jsonResponse +=	', "sunrise":"'+times["sunrise"]+'"'
		jsonResponse +=	', "zuhr":"'+times["dhuhr"]+'"'
		jsonResponse +=	', "asr":"'+times["asr"]+'"'
		jsonResponse +=	', "sunset":"'+times["sunset"]+'"'
		jsonResponse +=	', "maghrib":"'+times["maghrib"]+'"'
		jsonResponse +=	', "isha":"'+times["isha"]+'"'
		jsonResponse +=	', "midnight":"'+times["midnight"]+'"}'
		if (returnSettings):
			jsonResponse += ', "settings":"{"method":"'+praytime.calcMethod+'"'
			jsonResponse += ', "longitude":%1.8f'%praytime.lng
			jsonResponse += ', "latitude":%1.8f'%praytime.lat
			jsonResponse += ', "elevation":%1.4f'%praytime.elv
			for name, value in praytime.settings.iteritems():
				jsonResponse += ', "'+name+'":"'+str(value)+'"'
			jsonResponse += '}'
		jsonResponse +=	'}'
		self.response.out.write(jsonResponse)
