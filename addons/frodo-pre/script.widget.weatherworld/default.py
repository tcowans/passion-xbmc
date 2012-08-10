
import sys

try: args = sys.argv[ 1 ]
except: args = None

if not args:
    import screensaver
else:
    from backend import WeatherWorld
    WeatherWorld()

