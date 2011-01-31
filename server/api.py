#!/usr/bin/env python

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db

class MainHandler(webapp.RequestHandler):
    def get(self):
		self.response.out.write("{}");


def main():
    application = webapp.WSGIApplication([('/api/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
