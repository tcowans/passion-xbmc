
# Modules general
import os
import sys
import shutil
from traceback import print_exc

# Modules XBMC
import xbmc

# Modules custom
from utilities import getUserSkin


CURRENT_SKIN, FORCE_FALLBACK = getUserSkin()


def addMyFontsToSkin():
    import MyFont
    return MyFont.addFonts()


def addIncludesXmlToSkin():
    reload_skin = False
    includes_path = os.path.join( os.getcwd(), "resources", "skins", CURRENT_SKIN, "720p", "scripts_includes", "Installer Passion-XBMC" )
    destination_path = xbmc.translatePath( "special://skin/720p/scripts_includes/Installer Passion-XBMC/" )
    if os.path.exists( includes_path ):
        try:
            if not os.path.exists( destination_path ):
                os.makedirs( destination_path )
            for xml in os.listdir( includes_path ):
                if os.path.isdir( xml ): continue
                # update at all times
                shutil.copyfile( os.path.join( includes_path, xml ), os.path.join( destination_path, xml ) )
                print "skins_utilities::addIncludesXmlToSin: [%s -> %s]" % ( os.path.join( includes_path, xml ), os.path.join( destination_path, xml ) ) 

            scripts_includes = '<include file="scripts_includes/Installer Passion-XBMC/IPX_Includes.xml" />'
            for resolution in [ "1080i", "720p", "NTSC16x9", "NTSC", "PAL16x9", "PAL" ]:
                includes_xml = xbmc.translatePath( "special://skin/%s/includes.xml" % resolution )
                if not os.path.exists( includes_xml ): continue
                str_includes = file( includes_xml, "r" ).read()
                if not scripts_includes in str_includes:
                    str_includes = str_includes.replace( "<includes>", "<includes>\n\t%s" % scripts_includes )
                    file( includes_xml, "w" ).write( str_includes )
                    reload_skin = True
                    print "skins_utilities::addIncludesXmlToSin: added missing skin includes! [%s]" % includes_xml
        except:
            print_exc()
    return reload_skin


def addBackgroundsToSkin():
    # fonction pour une meilleur prise en change des images par XBMC
    # ça prend un chemin complet dans l'attribut fallback pour etre afficher plus vite !!!
    # <imagepath fallback="special://profile/script_data/skin_backgrounds/IPX/pictures.jpg" background="true">
    # copy all BG in skin if not exists :P
    OK = False
    bg_path = os.path.join( os.getcwd(), "resources", "skins", CURRENT_SKIN, "backgrounds" )
    cache_bg_path = xbmc.translatePath( "special://profile/script_data/skin_backgrounds/IPX/" )
    if os.path.exists( bg_path ):
        try:
            if not os.path.exists( cache_bg_path ):
                os.makedirs( cache_bg_path )
            for bg in os.listdir( bg_path ):
                if bg.lower().endswith( ".db" ) or os.path.isdir( bg ): continue
                #if not os.path.exists( os.path.join( cache_bg_path, bg ) ):
                # update at all times
                try:
                    shutil.copyfile( os.path.join( bg_path, bg ), os.path.join( cache_bg_path, bg ) )
                    print "skins_utilities::addBackgroundsToSin: [%s -> %s]" % ( os.path.join( bg_path, bg ), os.path.join( cache_bg_path, bg ) )
                except:
                    print_exc()
            OK = True
        except:
            print_exc()
    return OK


def setupUtilities():
    #ok = addBackgroundsToSkin()
    reload_skin1 = addMyFontsToSkin()
    #reload_skin2 = addIncludesXmlToSkin()
    #reload_skin = ( reload_skin1 or reload_skin2 )
    return reload_skin1
