function updateSettings() {
	var calcMethod = $("#calc_method option:selected").val();
	var juristicMethod = $("#juristic_method option:selected").val();
	
	$.cookie("cm", calcMethod);
	$.cookie("jm", juristicMethod);
	$("#prayer_settings").removeClass("open");
	window.location = "/";
	return false;
}

function updateCity(city) {
	$("#city").text(city);
	$.cookie("city", city);
}

function updateLocation(latitude, longitude) {
	$("#latitude").val( latitude );
	$("#longitude").val( longitude );

	$.cookie("lat", latitude);
	$.cookie("long", longitude);
	
	updatePrayerTimes(latitude, longitude);
}

function updatePrayerTimes(latitude, longitude) {
	var date = new Date();
	var offset = date.getTimezoneOffset() / -60;

	var calcMethod = $.cookie("cm");
	if (!calcMethod) calcMethod = "MWL";
	var juristMethod = $.cookie("jm");
	if (!juristMethod) juristMethod = "Hanafi";
		
	prayTimes.setMethod(calcMethod);
	prayTimes.getSetting()['asr'] = juristMethod;
	var times = prayTimes.getTimes(date, [latitude, longitude], offset, false, '12h');
	
	$("#fajrtime").text( times['fajr'] );
	$("#zuhrtime").text( times['dhuhr'] );
	$("#asrtime").text( times['asr'] );
	$("#maghribtime").text( times['maghrib'] );
	$("#ishatime").text( times['isha'] );
}

var userLocation = {};

$(document).ready(function(){
	var longitude = $.cookie("long");
	var latitude = $.cookie("lat");
	var city = $.cookie("city");

	$("#calc_method").val( $.cookie("cm") );
	$("#juristic_method").val( $.cookie("jm") );

	if (!longitude || !latitude) {
		initializeLocation();
	} else {
		updateLocation(latitude, longitude);
		updateCity(city)
	}
});



function initializeLocation() {
  // Try W3C Geolocation (Preferred)
  if(navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(gotNewPosition, handleNoGeolocation, {maximumAge:Infinity, timeout:0});
  } else if (google.gears) {
  // Try Google Gears Geolocation
    var geo = google.gears.factory.create('beta.geolocation');
    geo.getCurrentPosition(gotNewPosition, handleNoGeolocation );
  } else {
  // Browser doesn't support Geolocation
    handleNoGeolocation();
  }
}

function gotNewPosition(position) {
	userLocation = { "city":"w3c", "latitude":position.coords.latitude, "longitude":position.coords.longitude };
	$.cookie("long", position.coords.longitude);
	$.cookie("lat", position.coords.latitude);
	updateLocation(position.coords.latitude, position.coords.longitude);
}

function handleNoGeolocation() {
	updateLocation(30, -97);
	updateCity("Austin, TX");
}
