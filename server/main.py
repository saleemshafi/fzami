#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db

class MainHandler(webapp.RequestHandler):
    def get(self):
		ipAddress = self.request.remote_addr;
		user = users.get_current_user()
		if user:
			self.response.out.write('''
			<html>
			<head>
			<title> fzami </title>
			<link rel="stylesheet" type="text/css" href="styles/fzami.css">
			<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.4.4/jquery.min.js"></script>
			<!--<script type="text/javascript" src="http://code.jquery.com/jquery-1.4.4.js"></script>-->
			<script type="text/javascript" src="http://code.google.com/apis/gears/gears_init.js"></script>
			<script type="text/javascript" src="scripts/jquery.cookie.js"></script>
			<script type="text/javascript" src="scripts/PrayTimes.js"></script>
			<script type="text/javascript" src="scripts/fzami.js"></script>
			<script type="text/javascript">
				var ipAddress = "''')
			self.response.out.write(ipAddress)
			self.response.out.write('''";
			</script>
			</head>
			<body>
			<div id="name">''')
			self.response.out.write(user.nickname())
			self.response.out.write('<a href="'+users.create_logout_url(self.request.uri)+'">[X]</a>');
			self.response.out.write('''</div>
			<a href="#settings" onclick="$('#prayer_settings').addClass('open')">Settings</a>
			<p id="city" align="center"><p>
			<div align="center" id="prayers"  onclick="$('#log_popup').addClass('open')">
				<div class="prayer">Fajr<span id="fajrtime"></span></div>
				<div class="prayer">Zuhr<span id="zuhrtime"></span></div>
				<div class="prayer">Asr<span id="asrtime"></span></div>
				<div class="prayer">Maghrib<span id="maghribtime"></span></div>
				<div class="prayer">Isha<span id="ishatime"></span></div>
			</div>
			<div id="prayer_settings">
				<a href="#" onclick="$('#prayer_settings').removeClass('open')">Close</a>
				<form id="settings_form" method="get" action="#" onsubmit="return updateSettings();">
					<div><label>Latitude</label><input id="latitude" name="latitude" /></div>
					<div><label>Longitude</label><input id="longitude" name="longitude" /></div>
					<div><label>Method</label><select id="calc_method" name="calc_method">
						<option>MWL</option>
						<option>ISNA</option>
						<option>Egypt</option>
						<option>Makkah</option>
						<option>Karachi</option>
						<option>Tehran</option>
						<option>Jafari</option>
					</select></div>
					<div><label>Asr Type</label><select id="juristic_method" name="juristic_method">
						<option>Hanafi</option>
						<option>Standard</option>
					</select></div>
					<button type="submit">Save Settings</button>
				</form>
			</div>
			<div id="log_popup">
				<a href="#" onclick="$('#log_popup').removeClass('open')">Close</a>
				<form id="log_form" method="get" action="#" onsubmit="return submitLog();">
					<div><input type="checkbox" name="actions" id="actions_fajr" value="fajr"><label for="actions_fajr">Fajr</label></div>
					<div><input type="checkbox" name="actions" id="actions_zuhr" value="zuhr"><label for="actions_fajr">Zuhr</label></div>
					<div><input type="checkbox" name="actions" id="actions_asr" value="asr"><label for="actions_fajr">Asr</label></div>
					<div><input type="checkbox" name="actions" id="actions_maghrib" value="maghrib"><label for="actions_fajr">Maghrib</label></div>
					<div><input type="checkbox" name="actions" id="actions_isha" value="isha"><label for="actions_fajr">Isha</label></div>
					<button type="submit">Save Settings</button>
				</form>
			</div>
			</body>
			</html>
			''')
		else:
			self.redirect(users.create_login_url(self.request.uri));



def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
