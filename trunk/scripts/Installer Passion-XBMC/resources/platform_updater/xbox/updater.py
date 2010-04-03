
import os
import re
import sys
from traceback import print_exc

import xbmc

from dataxml import *


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__


def getXbmcIsMappedTo():
    ismapped = None
    try:
        xbmc_log = file( xbmc.translatePath( "special://home/xbmc.log" ), "r" ).read()
        ismapped = re.compile( "NOTICE: The executable running is: (.*)", re.IGNORECASE ).findall( xbmc_log )
        if not ismapped: ismapped = re.compile( "NOTICE: Q is mapped to: (.*)", re.IGNORECASE ).findall( xbmc_log )
        if ismapped:
            ismapped = ismapped[ 0 ]
            if not ismapped.endswith( ".xbe", ( len( ismapped )-4 ), len( ismapped ) ):
                ismapped = os.path.join( ismapped, "default.xbe" )
            if not os.path.isfile( ismapped ): ismapped = None
    except:
        print_exc()
    if not ismapped: xbmc.translatePath( "special://home/default.xbe" )
    return ismapped


XBMC_HOME_PATH = os.path.dirname( getXbmcIsMappedTo() )

UPDATER_PATH = xbmc.translatePath( os.path.join( os.getcwd().rstrip( ";" ), "resources", "platform_updater", "xbox", "updater" ) )

LANG = xbmc.getLanguage().capitalize()
LANG_PATH = xbmc.translatePath( os.path.join( os.getcwd().rstrip( ";" ), "resources", "language" ) )
LANG = ( "English", LANG )[ os.path.exists( os.path.join( LANG_PATH, LANG.lower(), "%s.xml" % LANG ) ) ]
LANGUAGE = os.path.join( LANG_PATH, LANG.lower(), "%s.xml" % LANG ).replace( "Q:", XBMC_HOME_PATH )

configs = {
    "IP": xbmc.getInfoLabel( "Network.IPAddress" ),
    "SUBNET": xbmc.getInfoLabel( "Network.SubnetAddress" ),
    "GATEWAY": xbmc.getInfoLabel( "Network.GatewayAddress" ),
    "DNS1": xbmc.getInfoLabel( "Network.DNS1Address" ),
    "DNS2": xbmc.getInfoLabel( "Network.DNS2Address" ),

    "XBMC_HOME_PATH": XBMC_HOME_PATH,
    "UPDATER_PATH": UPDATER_PATH.replace( "Q:", XBMC_HOME_PATH ),
    "UPDATER_PARDIR": os.path.dirname( UPDATER_PATH.replace( "Q:", XBMC_HOME_PATH ) ),

    "LANGUAGE": LANGUAGE,
    "32700": _( 32700 ).encode( "iso-8859-1" ),
    "32701": _( 32701 ).encode( "iso-8859-1" ),
    "32702": _( 32702 ).encode( "iso-8859-1" ),
    "32709": _( 32709 ).encode( "iso-8859-1" ),
    "32749": _( 32749 ).encode( "iso-8859-1" ),
    "32750": _( 32750 ).encode( "iso-8859-1" ),
    "32751": _( 32751 ).encode( "iso-8859-1" ),
    "32752": _( 32752 ).encode( "iso-8859-1" ),
    "32753": _( 32753 ).encode( "iso-8859-1" ),
    "32760": _( 32760 ).encode( "iso-8859-1" ),
    "32761": _( 32761 ).encode( "iso-8859-1" ),
    "32770": _( 32770 ).encode( "iso-8859-1" ),
    "32780": _( 32780 ).encode( "iso-8859-1" ),
    "32789": _( 32789 ).encode( "iso-8859-1" ),
    "32790": _( 32790 ).encode( "iso-8859-1" ),
    "32791": _( 32791 ).encode( "iso-8859-1" ),
    "32795": _( 32795 ).encode( "iso-8859-1" ),
    "32799": _( 32799 ).encode( "iso-8859-1" ),
    "32800": _( 32800 ).encode( "iso-8859-1" ),
    "32801": _( 32801 ).encode( "iso-8859-1" ),
    "32802": _( 32802 ).encode( "iso-8859-1" ),
    "32810": _( 32810 ).encode( "iso-8859-1" ),
    "32811": _( 32811 ).encode( "iso-8859-1" ),
    "32812": _( 32812 ).encode( "iso-8859-1" ),
    "32813": _( 32813 ).encode( "iso-8859-1" ),
    "32820": _( 32820 ).encode( "iso-8859-1" ),
    "32821": _( 32821 ).encode( "iso-8859-1" ),
    "32822": _( 32822 ).encode( "iso-8859-1" ),
    "32830": _( 32830 ).encode( "iso-8859-1" ),
    "32831": _( 32831 ).encode( "iso-8859-1" ),
    "32832": _( 32832 ).encode( "iso-8859-1" ),
    "32840": _( 32840 ).encode( "iso-8859-1" ),
    "32841": _( 32841 ).encode( "iso-8859-1" ),
    "32842": _( 32842 ).encode( "iso-8859-1" ),
    "32850": _( 32850 ).encode( "iso-8859-1" ),
    "32851": _( 32851 ).encode( "iso-8859-1" ),
    "32852": _( 32852 ).encode( "iso-8859-1" ),

    "SVN_REV": "", #infos in paths.txt
    "BUILD_ZIP": "", #infos in paths.txt

    "LISTITEMS_UPDATE": "",
    "LISTITEMS_CLEANER": "",
    }


def parse_paths_txt():
    svn_rev = build_zip = ""
    try:
        text = file( os.path.join( os.path.dirname( UPDATER_PATH ), "paths.txt" ), "r" ).read()
        paths = dict( [ tuple( txt.split( "=" ) ) for txt in text.strip( "\n" ).split( "\n" ) ] )
        if os.path.exists( paths[ "xbmc_build" ].strip( "\"'" ) ):
            build_zip = paths[ "xbmc_build" ].strip( "\"'" )
            svn_rev = re.search( "_(\d+).", build_zip ).group( 1 )
    except:
        print_exc()
    return svn_rev, build_zip


def Main():
    try:
        if configs[ "XBMC_HOME_PATH" ].lower() != "q:\\":
            svn_rev, build_zip = parse_paths_txt()
            if bool( build_zip ) and os.path.exists( build_zip ):
                configs[ "SVN_REV" ] = svn_rev #"27495"
                configs[ "BUILD_ZIP" ] = build_zip #"G:\WebDownload\XBMC_Xbox_27495.zip"
                configs[ "LISTITEMS_UPDATE" ] = listitems_update % configs

            configs[ "LISTITEMS_CLEANER" ] = listitems_cleaner % configs
            conf = base_xml % configs
            file( os.path.join( UPDATER_PATH, "update.xml" ), "w" ).write( conf )

            try:
                default_save = os.path.join( "E:\\UDATA", "9e115330", "0064122817A8" )
                #if not os.path.exists( default_save ): os.makedirs( default_save )
                #from shutil import copy
                import shutil2
                shutil2.copytree( os.path.join( UPDATER_PATH, "media", "UDATA" ), "E:\\UDATA", overwrite=True )
                #copy( os.path.join( UPDATER_PATH, "skin", "Confluence", "UXSplash.jpg" ), os.path.join( default_save, "Splash.jpg" ) )
                if os.path.exists( "X:\\0064122817A8" ): 
                    shutil2.copy( os.path.join( default_save, "Splash.jpg" ), os.path.join( "X:\\0064122817A8", "Splash.jpg" ) )
            except:
                print_exc()

            xbmc.executebuiltin( "XBMC.RunXBE(%s)" % os.path.join( UPDATER_PATH, "updater.xbe" ) )
            return
    except:
        print_exc()
    print "impossible de faire la mise a jour!!!"
