import xbmc
import urllib
from traceback import print_exc

try:
    #print "args: %s" % sys.argv[ 1 ]
    path= urllib.unquote_plus(sys.argv[ 1 ].split("&")[1])
    url= urllib.unquote_plus(sys.argv[ 1 ].split("&")[0])
    xbmc.executebuiltin( "XBMC.Notification( %s, 'Téléchargement en cours...', 'icone.png')" % path )
    
    print "path: %s" % path
    print "url: %s" % url
    
    Filename, headers = urllib.urlretrieve( url , path )
    #print Filename
    #print headers
     
    notif = "%s,%s,5000,%s" % ( Filename, "Téléchargement terminé", "icone.png" )
except:
    print_exc()
    notif = "%s,%s,5000,%s" % ( "Erreur de téléchargement !!!", "", "icone.png" )
    
xbmc.executebuiltin( "XBMC.Notification(%s)" % notif )