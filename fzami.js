var dateCheck = null;
var prayerCheck = null;
var latestTimes = null;

startDateCheckTimer();
setupDatePicker();
setSettingsFormToggle();
setLocationFormToggle();
populateLocation();
populateSettings();

function startDateCheckTimer() {
	if (dateCheck) {
		clearInterval(dateCheck);
	} else {
		checkForNewDate();
	}
// checks to see if the date has changed so that the prayer times
// are automatically kept upto date.  set to check every 5 minutes.
	dateCheck = setInterval( function() { checkForNewDate(); }, 5*60*1000 );
}

var dp = null;
function setupDatePicker() {
	Date.firstDayOfWeek = 0;
	Date.format = 'yyyy-mm-dd';
	$(function() {
			var dateText = $("#date th");
			dp = dateText.datePicker({startDate:'1970-01-01', createButton:false });
			dp.val(new Date().asString()).trigger('change');
			dp.dpSetPosition($.dpConst.POS_TOP, $.dpConst.POS_LEFT);
			dp.dpSetOffset(40, 17);
			dateText.bind(
					'click',
					function()
					{
						dp.dpDisplay(this);
						this.blur();
						return false;
					}
				);
			dateText.bind(
					'dateSelected',
					function(ev, date)
					{
						$("#date th").text(date.f("yyyy-MM-dd"));
						updatePrayerTimes(date);
					}
				);
		});
	
}

function startCurrentPrayerTimer() {
	if (prayerCheck) {
		clearInterval(prayerCheck);
	}
	updateCurrentPrayer();
	// checks to see if the current prayer has changed every minute.
	prayerCheck = setInterval( function() { updateCurrentPrayer(); }, 60*1000 );
}

function populateLocation() {
	// pull previous location
	var position = getGeoLocation();
	if (position) {
		updateLocation(position, getData("fzami.location.name"));
	} else {
		updateLocation([null, null], null);
		getLocationFromBrowser(24*60*60*1000);  // accept something less than a day old
		setTimeout( function() { if (!getGeoLocation()) { editLocation(); } }, 5*1000);
	}
}

function populateSettings() {
	var settings = getSettings();
	if (settings) {
		updateCalcMethod(settings.method);
		updateAsrMethod(settings.asr);
		updateTimeFormat(settings.timeFormat);
		summarizeSettings();
	}
}

function setSettingsFormToggle() {
	var settingsFocusCount = 0;
	$("#settings_form *").focusin( function() {
		if (settingsFocusCount < 0) settingsFocusCount = 0;
		settingsFocusCount++;
	} );
	$("#settings_form *").focusout( function() {
		settingsFocusCount--;
//		setTimeout(function() {	if (settingsFocusCount <= 0) summarizeSettings(); }, 50 );
	} );
}

function setLocationFormToggle() {
	var locationFocusCount = 0;
	$("#location_form *").focusin( function() {
		if (locationFocusCount < 0) locationFocusCount = 0;
		locationFocusCount++;
	} );
	$("#location_form *").focusout( function() {
		locationFocusCount--;
//		setTimeout(function() {	if (locationFocusCount <= 0) summarizeLocation(); }, 50 );
	} );
}

function isPrayerDate( date ) {
	return prayTimes.real_date && prayTimes.real_date[0] == date.getFullYear()
		&& prayTimes.real_date[1] == date.getMonth()+1
		&& prayTimes.real_date[2] == date.getDate();
}

function checkForNewDate() {
	if (!prayTimes.real_date) {
		var date = new Date(); // today
		$("#date th").text(date.f("yyyy-MM-dd"));
	}
	var currentDate = new Date();
	if (!isPrayerDate(currentDate)) {
		updatePrayerTimes();
	}
}

function updateCurrentPrayer() {
	var oldPrayerTime = $("#prayers .current .prayertime").attr("id");
	$("#prayers tr").removeClass("current");
	var now = new Date();
	if (isPrayerDate(now)) {
		var currentTime = now.f("HH:mm");
		var currentPrayer = getCurrentPrayer(currentTime);
		if (currentPrayer != null) {
			$("#"+currentPrayer).addClass("current");
			document.title = currentPrayer+" time -- fzami";
			if (currentPrayer != oldPrayerTime) {
				if (oldPrayerTime) {
//					alert("It is now "+currentPrayer+" time.");
				}
			}
		}
	}
}

function getCurrentPrayer(now) {
	if (now < latestTimes.fajr || now >= latestTimes.isha) {
		return "isha";
	} else if (now >= latestTimes.maghrib) {
		return "maghrib";
	} else if (now >= latestTimes.asr) {
		return "asr";
	} else if (now >= latestTimes.dhuhr) {
		return "zuhr";
	} else if (now < latestTimes.sunrise) {
		return "fajr";
	} else {
		return null;
	}
}

function getLocationFromBrowser( maxAge ) {
    //$("#location_summary").attr("alt","unable to determine location");
	// navigator.geolocation.getCurrentPosition(successCallback, errorCallback, options)
	navigator.geolocation.getCurrentPosition(function(position) {		  var city = "(unknown)";		  if (position.address) {			city = position.address.city+", "+position.address.region;		  }
		  updateLocation([position.coords.latitude, position.coords.longitude], city);
	}, function() {
		  //$("#location_summary").attr("alt","unable to determine location");
		  updateLocation([null, null], null);
	}, {maximumAge:maxAge, timeout:5*1000} ); // don't trust a location more than a day old
}

function updatePrayerTimes(date) {
	var times = null;
	latestTimes = null;

	var settings = getSettings();
	prayTimes.setMethod(settings.method);
	prayTimes.adjust(settings);
//		prayTimes.tune(settings);
	
	position = getGeoLocation();
	if (position) {
		if (!date) date = new Date(); // today
		$("#date th").text(date.f("yyyy-MM-dd"));
		var timeZone = date.getTimezoneOffset() / -60.0;
		times = prayTimes.getTimes(date, position, "auto", "auto", settings.timeFormat);
		if (settings.timeFormat == "24h") {
			latestTimes = times;
		} else {
			latestTimes = prayTimes.getTimes(date, position, "auto", "auto", "24h");
		}
	}

	$("#fajr .prayertime").text(times == null ? "--:--" : times.fajr);
	$("#sunrise .prayertime").text(times == null ? "--:--" : times.sunrise);
	$("#zuhr .prayertime").text(times == null ? "--:--" : times.dhuhr);
	$("#asr .prayertime").text(times == null ? "--:--" : times.asr);
	$("#maghrib .prayertime").text(times == null ? "--:--" : times.maghrib);
	$("#isha .prayertime").text(times == null ? "--:--" : times.isha);
	document.title = "fzami";

	startCurrentPrayerTimer();
}

function editLocation() {
	$("#location").addClass("editing");
	$("#latitude").focus();
}

function summarizeLocation() {
/*
	var locationName = "unable to determine location";
	var position = getGeoLocation();
	if (position) {
		var name = getData("fzami.location.name");
		if (name != null && name != "") {
			locationName = name + " ("+position[0] + ", " + position[1]+")";
		} else {
			locationName = position[0] + ", " + position[1];
		}
	}
	$("#location_summary").attr("alt", locationName);
*/
	$("#location").removeClass("editing");
}

function updateLocation(position, name) {
	updateLocationName(name);
	updateLatitude(position[0]);
	updateLongitude(position[1]);
	summarizeLocation();
}

function updateLatitude(lat) {
	putData("fzami.location.latitude", lat);
	$("#latitude").val(lat);
	updatePrayerTimes();
}

function updateLongitude(lng) {
	putData("fzami.location.longitude", lng);
	$("#longitude").val(lng);
	updatePrayerTimes();
}

function updateLocationName(name) {
	putData("fzami.location.name", name);
	$("#locationName").val(name);
}

function editSettings() {
	$("#settings").addClass("editing");
	$("#method").focus();
}

function summarizeSettings() {
/*
	var settings = getSettings();
	var settingsSummary = settings.method +" / "+settings.asr;
	$("#settings_summary").attr("alt", settingsSummary);
*/
	$("#settings").removeClass("editing");
}

function updateCalcMethod(method) {
	var settings = getSettings();
	settings.method = method;
	putData("fzami.settings", $.toJSON(settings));
	$("#method").val(method);
	updatePrayerTimes();
}

function updateAsrMethod(asrMethod) {
	var settings = getSettings();
	settings.asr = asrMethod;
	putData("fzami.settings", $.toJSON(settings));
	$("#asrMethod").val(asrMethod);
	updatePrayerTimes();
}

function updateTimeFormat(timeFormat) {
	var settings = getSettings();
	settings.timeFormat = timeFormat;
	putData("fzami.settings", $.toJSON(settings));
	$("#timeFormat").val(timeFormat);
	updatePrayerTimes();
}


function getSettings() {
	var settings = null;
	var settingsStr = getData("fzami.settings");
	if (settingsStr) {
		settings = $.parseJSON(settingsStr);
	} else {
		settings = { method:'ISNA', asr:'Hanafi', timeFormat:'12h' };
	}
	return settings;
}

function getGeoLocation() {
	var lat = getData("fzami.location.latitude");
	var lng = getData("fzami.location.longitude");
	if (lat && lng) {
		return [lat, lng];
	}
	return null;
}

function getData(key) {
	if (window.localStorage) {
		return window.localStorage.getItem(key);
	}
	return null;
}

function putData(key, data) {
	if (window.localStorage) {
		if (data == null || data == "") {
			window.localStorage.removeItem(key);
		} else {
			window.localStorage.setItem(key, data);
		}
	}
}