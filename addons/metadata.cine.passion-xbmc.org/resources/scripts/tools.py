
import os
from traceback import print_exc

import xbmc
import xbmcgui


def Main():
    # setup language
    CWD = os.path.dirname( os.path.dirname( os.getcwd() ) )
    __language__ = xbmc.Language( CWD ).getLocalizedString

    # récupère la plateforme
    PLATFORM = os.environ.get( "OS", "xbox" ).lower()

    # vérifie si on est pas sur xbox, si oui c'est pas supporter
    if PLATFORM == "xbox":
        xbmcgui.Dialog().ok( __language__( 32000 ), __language__( 32002 ), __language__( 32003 ), "http://passion-xbmc.org/forum-xbmc" )
        raise

    # setup settings
    SETTINGS = xbmc.Settings( os.path.basename( CWD ) )#'metadata.cine.passion-xbmc.org' )

    # url du scraper en ligne ou pour avoir du support
    LAUNCH_URL = ""

    # setup tools
    WEBBROWSER = SETTINGS.getSetting( "webbrowser" )
    XBNE = SETTINGS.getSetting( "XBNE" )
    EMM = SETTINGS.getSetting( "EMM" )

    # commande qui doit être lancer par os.system( ... )
    command = None

    # setup list based on platform and settings
    DICO = {
        0: __language__( 32004 ),#"Scraper Ciné-Passion Support Fr - En"
        1: __language__( 32005 ),#"Visiter et/ou participer au scraper Ciné-Passion",
        2: __language__( 32006 ),#"NFO Creator Ciné-passion",
        3: __language__( 32007 ),#"XBNE NFO Éditeur",
        4: __language__( 32008 ),#"EMM - Ember Media Manager - Ciné-Passion",
        5: __language__( 32009 ),#"Annuler/Quitter"
        }

    list_choice = []
    if WEBBROWSER and os.path.exists( WEBBROWSER ): list_choice += [ 1, 0, 2 ]
    if XBNE and os.path.exists( XBNE ): list_choice.append( 3 )
    if EMM and os.path.exists( EMM ): list_choice.append( 4 )
    list_choice.append( 5 )

    heading = " - ".join( [ __language__( 32000 ), __language__( 32001 ) ] )
    selected = xbmcgui.Dialog().select( heading, [ DICO[ k ] for k in list_choice ] )
    if selected != -1:
        selected = list_choice[ selected ]

        if selected in [ 0, 1, 2 ]:
            LAUNCH_URL = "http://passion-xbmc.org/scraper/index2.php"
            if selected == 2: LAUNCH_URL += "?Page=NFO"

            if selected == 0: LAUNCH_URL = "http://passion-xbmc.org/scraper-cine-passion-support-francais/"
            
            if PLATFORM == "win32":
                # windows
                command = 'start "%s" "%s"' % ( WEBBROWSER, LAUNCH_URL, )
            else:
                # autre plateforme
                command = '%s %s' % ( WEBBROWSER, LAUNCH_URL, )

        elif selected in [ 3, 4 ]:
            app = ( XBNE,EMM )[ selected == 4 ]
            if PLATFORM == "win32":
                # windows
                command = '"%s"' % ( app, )
            else:
                # autre plateforme
                command = app

    if command:
        #on lance la commande
        os.system( command )


if __name__ == "__main__":
    try:
        Main()
    except:
        print_exc()
