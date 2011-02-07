#!/usr/bin/env python

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from praytime import *
from datetime import date

class Log(db.Model):
	user_id = db.StringProperty()
	date = db.StringProperty()
	actions = db.StringListProperty()

class LogHandler(webapp.RequestHandler):
	def get(self, dateParam):
		user_id = "10"
		log_key = db.Key.from_path('Log', user_id+":"+dateParam)
		log = Log.get(log_key)
		if log is None:
			self.response.set_status(404)
		else:
			self.returnLog(log)

	def post(self, dateParam):
		self.put(dateParam)
		
	def put(self, dateParam):
		user_id = "10"
		actions = self.request.get_all("actions[]")
		if actions is None:
			actions = [ self.request.get("actions") ]
		log = Log.get_or_insert(user_id+":"+dateParam)
		log.date = dateParam
		log.actions = actions
		log.put()
		self.returnLog(log)

	def delete(self, dateParam):
		user_id = "10"
		log_key = db.Key.from_path('Log', user_id+":"+dateParam)
		log = Log.get(log_key)
		log.delete()

	def returnLog(self, log):
		self.response.headers['Content-Type'] = 'application/json'
		actionStr = ""
		for action in log.actions:
			actionStr += '"'+action+'",'
		actionStr = actionStr[:-1]
		self.response.out.write('{"date":'+log.date+', "actions":['+actionStr+']}')

class PrayerTimeHandler(webapp.RequestHandler):
	def get(self, dateParam):
		if (dateParam == ""):
			today = date()
		else:
			year = int(dateParam[:4])
			month = int(dateParam[4:6])
			day = int(dateParam[-2:])
			today = date(year, month, day)

		longitude = float(self.request.get("longitude"))
		latitude = float(self.request.get("latitude"))
		elevation = self.request.get("elevation")
		if (elevation is None):
			location = ( longitude, latitude, float(elevation) )
		else :
			location = ( longitude, latitude )
		timezone = float(self.request.get("timezone-offset")) if self.request.get("timezone-offset") != "" else -6
		format = self.request.get("format")
		format = format if format in ('24h', '12h', '12ns') else '24h'
		dst = 1 if self.request.get("dst") == "true" else 0
		method = self.request.get("method")
		method = method if method in ("MWL", "ISNA", "Egype", "Makkah", "Karachi", "Tehran", "Jarafi") else "MWL"
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
		
		
def main():
    application = webapp.WSGIApplication([
										(r'/api/log/(.*)', LogHandler)
										],
                                         debug=True)
										 
    application = webapp.WSGIApplication([
										(r'/api/prayertimes/(.*)', PrayerTimeHandler)
										],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
