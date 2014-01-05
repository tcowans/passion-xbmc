
import sys
import time
import xbmc
import xbmcgui

start = "0,0"

if sys.argv[ 1: ]:
    start = "%s,%s" % ( xbmc.getInfoLabel( "Window.Property(LongitudePosX)" ) or "0",  xbmc.getInfoLabel( "Window.Property(LatitudePosY)" ) or "0" )
    xbmc.executebuiltin( sys.argv[ 1 ] )
    time.sleep( 1 )

while xbmc.getCondVisibility( "!Weather.IsFetched + IsEmpty(Window(Weather).Property(Weather.ExtraIsFetched))" ):
    time.sleep( .5 )

def getPosition( lat, long, width=1280, height=720 ):
    # set our pos y
    height = height / 2.0
    y = str( lat * height / 90 ).strip( "-" )
    if lat > 0: y = height - float( y )
    else: y = height + float( y )
    # set our pos x
    width = width / 2.0
    x = str( long * width / 180 ).strip( "-" )
    if long < 0: x = width - float( x )
    else: x = width + float( x )
    # return values
    return int( x ), int( y )


lat  = xbmc.getInfoLabel( "Window(Weather).Property(Current.Location.LatitudeDec)" )
long = xbmc.getInfoLabel( "Window(Weather).Property(Current.Location.LongitudeDec)" )
x, y = getPosition( float( lat or "90.0" ), float( long or "-180.0" ) )

window  = xbmcgui.Window( 10000 )
control = window.getControl( 2600 )

control.setAnimations( [ ( 'conditional', 'condition=!Window.Next(Weather)+Container(9000).Hasfocus(7) effect=slide start=%s end=%i,%i time=300 easing=out tween=quadratic' % ( start, x, y ) ) ] )
window.setProperty( "LongitudePosX", str( x ) )
window.setProperty( "LatitudePosY", str( y ) )
