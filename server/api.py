#!/usr/bin/env python

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db

class Log(db.Model):
	user_id = db.StringProperty()
	date = db.StringProperty()
	actions = db.StringListProperty()

class LogHandler(webapp.RequestHandler):
	def get(self, date):
		user_id = "10"
		log_key = db.Key.from_path('Log', user_id+":"+date)
		log = Log.get(log_key)
		if log is None:
			self.response.set_status(404)
		else:
			self.returnLog(log)

	def post(self, date):
		self.put(date)
		
	def put(self, date):
		user_id = "10"
		actions = self.request.get_all("actions[]")
		if actions is None:
			actions = [ self.request.get("actions") ]
		log = Log.get_or_insert(user_id+":"+date)
		log.date = date
		log.actions = actions
		log.put()
		self.returnLog(log)

	def delete(self, date):
		user_id = "10"
		log_key = db.Key.from_path('Log', user_id+":"+date)
		log = Log.get(log_key)
		log.delete()

	def returnLog(self, log):
		self.response.headers['Content-Type'] = 'application/json'
		actionStr = ""
		for action in log.actions:
			actionStr += '"'+action+'",'
		actionStr = actionStr[:-1]
		self.response.out.write('{"date":'+log.date+', "actions":['+actionStr+']}')

		
		
def main():
    application = webapp.WSGIApplication([
										(r'/api/log/(.*)', LogHandler)
										],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
