
# WARNINGS: NOT REMOVE PATH NUMBER, IF YOU NOT SURE.
IGNORE_DASH_PATH = [ 30, 31, 32, 33 ]


class DashboardPath( dict ):
    def __init__( self ):
        # C DRIVE
        self[ 0 ]  = [ "C:", "avadash.xbe" ]
        self[ 1 ]  = [ "C:", "avalaunch.xbe" ]
        self[ 2 ]  = [ "C:", "evoxdash.xbe" ] # default path in plugin settings
        self[ 3 ]  = [ "C:", "mxmdash.xbe" ]
        self[ 4 ]  = [ "C:", "nexgen.xbe" ]
        self[ 5 ]  = [ "C:", "Sys", "Dashboard", "Xdash.xbe" ]
        self[ 6 ]  = [ "C:", "Sys", "Xdash.xbe" ]
        self[ 7 ]  = [ "C:", "unleashx.xbe" ]
        self[ 8 ]  = [ "C:", "xbmc.xbe" ]

        # E DRIVE
        self[ 9 ]  = [ "E:", "Apps", "altdash", "default.xbe" ]
        self[ 10 ] = [ "E:", "apps", "altdash", "default.xbe" ]
        self[ 11 ] = [ "E:", "avadash.xbe" ]
        self[ 12 ] = [ "E:", "avalaunch.xbe" ]
        self[ 13 ] = [ "E:", "dashboard", "altdash", "default.xbe" ]
        self[ 14 ] = [ "E:", "dashboard", "default.xbe" ]
        self[ 15 ] = [ "E:", "evoxdash.xbe" ]
        self[ 16 ] = [ "E:", "mxmdash.xbe" ]
        self[ 17 ] = [ "E:", "nexgen.xbe" ]
        self[ 18 ] = [ "E:", "Systeme", "Dashboard", "hackdash.xbe" ]
        self[ 19 ] = [ "E:", "unleashx.xbe" ]
        self[ 20 ] = [ "E:", "xbmc.xbe" ]
        self[ 21 ] = [ "E:", "Xdash.xbe" ]

        # F DRIVE
        self[ 22 ] = [ "F:", "avadash.xbe" ]
        self[ 23 ] = [ "F:", "avalaunch.xbe" ]
        self[ 24 ] = [ "F:", "evoxdash.xbe" ]
        self[ 25 ] = [ "F:", "mxmdash.xbe" ]
        self[ 26 ] = [ "F:", "nexgen.xbe" ]
        self[ 27 ] = [ "F:", "unleashx.xbe" ]
        self[ 28 ] = [ "F:", "xbmc.xbe" ]
        self[ 29 ] = [ "F:", "Xdash.xbe" ]

        # MICROSOFT DASHBOARD ON C DRIVE WARNINGS, THIS PATH IS FOR A ORIGINAL MSDash OR SPECIAL XBOX CONFIG...
        self[ 30 ] = [ "C:", "xboxdash.xbe" ]

        # Other posibility
        self[ 31 ] = [ "C:", "Dash_original.xbe" ]
        self[ 32 ] = [ "E:", "xboxdash.xbe" ]
        self[ 33 ] = [ "F:", "xboxdash.xbe" ]

        # Custom Path
        # Add your missing path on number 34
        # self[ 34 ] = [ ":", ".xbe" ]

    def __delitem__( self, key ):
        if self.has_key( key ):
            dict.__delitem__( self, key )


class Team_UIX_ShortcutXbePath( dict ):
    def __init__( self ):
        # E,F & G DRIVE IN APPS ONLY
        self[ 0 ] = [ "E:", "Apps", "XBMC", "default.xbe" ] # default path in plugin settings
        self[ 1 ] = [ "F:", "Apps", "XBMC", "default.xbe" ]
        self[ 2 ] = [ "G:", "Apps", "XBMC", "default.xbe" ]

        # E,F & G DRIVE IN LOGICIELS ONLY
        self[ 3 ] = [ "E:", "Logiciels", "XBMC", "default.xbe" ]
        self[ 4 ] = [ "F:", "Logiciels", "XBMC", "default.xbe" ]
        self[ 5 ] = [ "G:", "Logiciels", "XBMC", "default.xbe" ]

    def __delitem__( self, key ):
        if self.has_key( key ):
            dict.__delitem__( self, key )



if __name__ == "__main__":
    from os import sep
    dt = DashboardPath()#Team_UIX_ShortcutXbePath()
    [ dt.__delitem__( x ) for x in IGNORE_DASH_PATH ]
    for key, value in dt.items():
        print key, sep.join( value )
