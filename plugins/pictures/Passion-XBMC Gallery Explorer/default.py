# -*- coding: utf-8 -*-
"""
Passion-XBMC Gallery Explorer Beta 2
Auteurs : Seb & Frost
"""

import sys

print "PARAM = %s"%sys.argv[2]

if "slideshow" in sys.argv[2]:
    print "ici 0"
    from resources.pluginAPI import screensaver as plugin

elif "set_screensaver" in sys.argv[2]:
    from resources.pluginAPI import advancedsettings as plugin

elif "download" in sys.argv[2]:
    from resources.pluginAPI import download as plugin

else:
    from resources.pluginAPI import mainapi as plugin

plugin.main()
   

