
*** Default Properties of XBMC ***

Locations				number of configured locations
Location[1-2-3]			name of location
Location				name of current location
Updated					last update time
WeatherProvider			name of weather provider
Current.Condition		current weather condition in words
Current.Temperature		current temperature
Current.FeelsLike		current feels like temperature
Current.Wind			current wind converted by XBMC (From DIRECTION at SPEED) (converted by addon)
Current.WindDirection	current wind direction
Current.OutlookIcon		path of current condition icon
Current.FanartCode		number of current condition icon
Current.Humidity		current humidity
Current.DewPoint		current dew point
Current.UVIndex			current UV index

Day[0-6].Title			name of day of week
Day[0-6].HighTemp		Maximal temperature
Day[0-6].LowTemp		minimal temperature
Day[0-6].Outlook		day weather condition in words
Day[0-6].OutlookIcon	path of day condition icon
Day[0-6].FanartCode		number of day condition icon


*** Extra Properties ***

Weather.IsFetched				Returns true if the weather data has been downloaded.
Weather.ExtraIsFetched			Returns true if the extra data has been downloaded.
Current.Location.LocalTime		Return full date and time of current location. (if possible)
Current.Location.Latitude		return latitude of current location. Format: 46° 50' N
Current.Location.Longitude		return longitude of current location. Format: 71° 15' W
Current.Location.LatitudeDec	return latitude in decimal of current location. Format: 46.8333333333
Current.Location.LongitudeDec	return longitude in decimal of current location. Format: -71.25

http://www.timeanddate.com/worldclock/aboutastronomy.html
Current.AstroTwilight.Start		Astronomical Twilight starts (Astronomical twilight is the time when the center of the sun is between 12° and 18° below the horizon. From the end of astronomical twilight in the evening to the beginning of astronomical twilight in the morning, the sky (away from urban light pollution) is dark enough for all astronomical observations.)
Current.AstroTwilight.End		Astronomical Twilight ends
Current.NauticTwilight.Start	Nautical Twilight starts (Nautical twilight is the time when the center of the sun is between 6° and 12° below the horizon. In general, nautical twilight ends when navigation via the horizon at sea is no longer possible.)
Current.NauticTwilight.End		Nautical Twilight ends
Current.CivilTwilight.Start		Civil Twilight starts (Morning civil twilight begins when the geometric center of the sun is 6° below the horizon (civil dawn) and ends at sunrise. Evening civil twilight begins at sunset and ends when the geometric center of the sun reaches 6° below the horizon (civil dusk).)
Current.CivilTwilight.End		Civil Twilight ends
Current.Sunrise					Sunrise (Sunrise or sun up is the instant at which the upper edge of the Sun appears on the horizon in the east.[1] The term can also refer to the entire process of the sun crossing the horizon and its accompanying atmospheric effects.)
Current.Sunset					Sunset (Sunset or sundown is the daily disappearance of the Sun below the horizon in the west as a result of Earth's rotation.)
Current.Sunrise.Azimuth			Azimuth Sunrise (degree) (The solar azimuth angle is the azimuth angle of the sun. It is most often defined as the angle from due north in a clockwise direction.)
Current.Sunset.Azimuth			Azimuth Sunset (degree)
Current.Sun.Length				Length of day This day (0h 0m 0s)
Current.Sun.Diff				Length of day Difference (-+ 0m 0s)
Current.Solarnoon.Time			Solar noon Time (Solar noon is the moment when the Sun transits the celestial meridian—roughly the time when it highest above the horizon on that day. This is also the origin of the terms ante meridiem and post meridiem as noted below. The Sun is directly overhead at solar noon at the equator on the equinoxes; at Tropic of Cancer (latitude 23° 26' 22? N) on the June solstice; and at Tropic of Capricorn (23° 26' 22? S) on the December solstice.)
Current.Solarnoon.Altitude		Solar noon Altitude (degree)
Current.Solarnoon.Distance		Solar noon Distance (10**6 km)
In.Broad.Daylight				En plein jour=true ; en pleine nuit=false (based on time between sunrise and sunset)

http://www.timeanddate.com/worldclock/aboutmoonrise.html
Current.Moonrise					Moonrise (Moonrise is the first appearance of the Moon over the Earth's horizon. It may also refer to)
Current.Moonset						Moonset (reverse of moonrise)
Current.Moonrise.Azimuth			Azimuth Moonrise (degree) (The azimuth displayed is the horizontal direction of the Moon at moonrise or moonset, at the times displayed in the Moonrise and Moonset columns. As on a compass, the azimuth is measured in degrees, with 360 in a full circle, counting in a clockwise direction starting from north. North has an azimuth value of 0 degrees, east is 90 degrees, south is 180 degrees, and west is 270 degrees. A small arrow is displayed after the azimuth value to indicate the map direction where the Moon will rise or set (for a map where north is upward).)
Current.Moonset.Azimuth				Azimuth Moonset (degree)
Current.Moon.Meridian.Time			Meridian Passing Time (shows the local time of the moment when the Moon's position will be above the horizon either directly north or directly south (except for Polar Regions, where the Moon might be down all day during the winter). For locations near the equator, the Moon can be right over one's head, at the point nearest the zenith position (altitude 90 degrees).)
Current.Moon.Meridian.Altitude		Meridian Passing Altitude (degree) (shows the altitude of the Moon's center above the ideal horizon at the passing time. Typically this is the highest position it reaches in the sky that day (except near the South and North Poles, where the altitude often increases or decreases all day and night). The altitude takes into account typical refraction in the Earth's atmosphere. If the Moon is below the horizon all day, the altitude will be labeled below.)
Current.Moon.Meridian.Distance		Meridian Passing Distance (km) (is the distance from the Earth's center to the Moon's center in kilometers. To compare, the Earth has an equatorial diameter of 12,756 km and the Moon an equatorial diameter of 3,476 km.)
Current.Moon.Meridian.Illuminated	Meridian Passing Illuminated (percent) (fraction of the Moon illuminated at the meridian passing.)
Current.Moon.Phase					Phase of moon and time (New Moon (dark moon), First quarter, Full Moon, Third quarter) (The Phase column will be displayed only on days when a certain Moon phase event occurs. The local time will be displayed after one of these Moon phases	)


*** Extra Images Properties ***

Current.Earth.Phase.LargeImage	http://api.usno.navy.mil/imagery/earth.png           (2048x1024) large image (What Earth looks like now) (auto refresh every 1 hour)
Current.Earth.Phase.Image		http://api.usno.navy.mil/imagery/earth.png?view=rise (1024x1024) (What Earth looks like now) (auto refresh every 1 hour)
Current.Moon.Phase.Image		http://api.usno.navy.mil/imagery/moon.png            (1024x1024) (What the Moon looks like now) (auto refresh every 1 hour)
