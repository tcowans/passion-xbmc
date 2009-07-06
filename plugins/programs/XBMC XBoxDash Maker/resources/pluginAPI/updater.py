
update_xml = r'''<?xml version="1.0" encoding="utf-8"?>
<UnleashX>
	<Settings>
		<MSDashBoard>C:\Xboxdash.xbe</MSDashBoard>
		<Password MaxTries="3"></Password>
		<Network Enable="Yes" Type="Static">
			<IP>%(IP)s</IP>
			<Subnet>%(SUBNET)s</Subnet>
			<Gateway>%(GATEWAY)s</Gateway>
			<DNS1>%(DNS1)s</DNS1>
			<DNS2>%(DNS2)s</DNS2>
		</Network>
		<FTP Enable="Yes">
			<User>xbox</User>
			<Password>xbox</Password>
			<Port>21</Port>
			<MaxUsers>3</MaxUsers>
			<AllowAnon>Yes</AllowAnon>
			<Greeting>XBMC Updater</Greeting>
		</FTP>
		<Newsfeed Enable="False" Interval="30"></Newsfeed>
		<Preference>
			<Games AutoLaunch="No"></Games>
			<DVD AutoLaunch="No"></DVD>
			<AudioCD AutoLaunch="No"></AudioCD>
			<Data AutoLaunch="No"></Data>
			<SNTP Synchronize="No">216.244.192.3</SNTP>
			<FanSpeed>1</FanSpeed>
			<ScreenSaver Wait="0">
				<Text></Text>
			</ScreenSaver>
			<AutoTurnOff>0</AutoTurnOff>
			<EnableDriveF>True</EnableDriveF>
			<EnableDriveG>Yes</EnableDriveG>
			<Skin Path="D:\skin">PM3.SD</Skin>
			<ContextMenu AllowItemEdit="No" LinkToGame="No" LinkToSave="No"></ContextMenu>
			<LanguageFile>%(XBMC_HOME_PATH)s\plugins\Programs\XBMC XBoxDash Maker\resources\language\%(LANGUAGE)s\%(LANGUAGE)s.xml</LanguageFile>
			<DefaultFolder></DefaultFolder>
		</Preference>
		<Audio>
			<EnableSoundTrack Random="Yes" Global="Yes" MusicPath="E:\musiques">Both</EnableSoundTrack>
			<MusicVolume>95</MusicVolume>
			<SoundVolume>85</SoundVolume>
		</Audio>
		<LED>
			<Default>Green</Default>
			<Busy>Flashing Red</Busy>
			<FileCopy>Flashing Orange</FileCopy>
		</LED>
	</Settings>
	<Menu>
		<List Text="%(30750)s" Sort="off" Batch="True" Icon="D:\skin\PM3.SD\backgrounds\scripts.jpg">
			<Item Action="AskUser" Arg1="XBMC Updater">%(30751)s\n\nArchive: %(BUILD_RAR)s\nUpdate: %(XBMC_HOME_PATH)s\</Item>
			<!-- copy a dummy file in temp dir and clean dir for unrar new archive -->
			<Item Action="Copy" Arg1="update.xml" Arg2="%(BUILD_PATH)s\BUILD\">Copying dummy file...</Item>
			<Item Action="Delete" Arg1="%(BUILD_PATH)s\BUILD\">Deleting dummy build folder...</Item>
			<!-- extract build and error on "rar" update auto stop -->
			<Item Action="UnRar" Arg1="%(BUILD_RAR)s" Arg2="%(BUILD_PATH)s\">Extracting new build...</Item>
			<!-- copytree build in xbmc dir -->
			<Item Action="Copy" Arg1="%(BUILD_PATH)s\BUILD\" Arg2="%(XBMC_HOME_PATH)s\">Copytree...</Item>
			<!-- don't take any chance move build, a copytree not work 100 percent -->
			<Item Action="Move" Arg1="%(BUILD_PATH)s\BUILD\default.xbe" Arg2="%(XBMC_HOME_PATH)s\">Updating default.xbe...</Item>
			<Item Action="Move" Arg1="%(BUILD_PATH)s\BUILD\credits\" Arg2="%(XBMC_HOME_PATH)s\">Updating credits\...</Item>
			<Item Action="Move" Arg1="%(BUILD_PATH)s\BUILD\language\" Arg2="%(XBMC_HOME_PATH)s\">Updating language\...</Item>
			<Item Action="Move" Arg1="%(BUILD_PATH)s\BUILD\media\" Arg2="%(XBMC_HOME_PATH)s\">Updating media\...</Item>
			<Item Action="Move" Arg1="%(BUILD_PATH)s\BUILD\screensavers\" Arg2="%(XBMC_HOME_PATH)s\">Updating screensavers\...</Item>
			<Item Action="Move" Arg1="%(BUILD_PATH)s\BUILD\skin\" Arg2="%(XBMC_HOME_PATH)s\">Updating skin\...</Item>
			<Item Action="Move" Arg1="%(BUILD_PATH)s\BUILD\sounds\" Arg2="%(XBMC_HOME_PATH)s\">Updating sounds\...</Item>
			<Item Action="Move" Arg1="%(BUILD_PATH)s\BUILD\system\" Arg2="%(XBMC_HOME_PATH)s\">Updating system\...</Item>
			<Item Action="Move" Arg1="%(BUILD_PATH)s\BUILD\UserData\" Arg2="%(XBMC_HOME_PATH)s\">Updating UserData\...</Item>
			<Item Action="Move" Arg1="%(BUILD_PATH)s\BUILD\Visualisations\" Arg2="%(XBMC_HOME_PATH)s\">Updating Visualisations\...</Item>
			<!-- delete temp dir -->
			<Item Action="Delete" Arg1="%(BUILD_PATH)s\BUILD\">Deleting temp build folder...</Item>
			<!-- notify user for update well done -->
			<Item Action="MessageBox" Arg1="XBMC rev.%(SVN_REV)s">%(30752)s</Item>
			<!-- optional format xbox caches -->
			<Item Action="Format" Arg1="X">Cleaning X Cache...</Item>
			<Item Action="Format" Arg1="Y">Cleaning Y Cache...</Item>
			<Item Action="Format" Arg1="Z">Cleaning Z Cache...</Item>
			<!-- now :) return on xbmc -->
			<Item Action="%(XBMC_HOME_PATH)s\default.xbe">%(30753)s.</Item>
		</List>
		<Item Action="%(XBMC_HOME_PATH)s\default.xbe" Icon="D:\skin\PM3.SD\backgrounds\xbmc.png">%(30760)s</Item>
		<Item Action="Restart" Icon="D:\skin\PM3.SD\backgrounds\xbox.jpg">%(30770)s</Item>
		<Item Action="Shutdown" Icon="D:\skin\PM3.SD\backgrounds\xbox.jpg">%(30780)s</Item>
		<Item Action="FileManager" Icon="D:\skin\PM3.SD\backgrounds\files.jpg">%(30790)s</Item>
		<Item Action="Settings" Icon="D:\skin\PM3.SD\backgrounds\settings.jpg">+</Item>
	</Menu>
</UnleashX>
'''


import os
import sys
from urllib import unquote_plus
from traceback import print_exc

import xbmc

from utilities import GET_XBMC_IS_MAPPED_TO
XBMC_HOME_PATH = os.path.dirname( GET_XBMC_IS_MAPPED_TO )
# not sure to get current xbmc, maybe later use other xbmc in plugin setting
#XBMC_HOME_PATH = xbmcplugin.getSetting( "apps_path" )


UPDATER_PATH = xbmc.translatePath( os.path.join( os.getcwd().rstrip( ";" ), "resources", "updater" ) )

LANG = xbmc.getLanguage().capitalize()
LANG_PATH = xbmc.translatePath( os.path.join( os.getcwd().rstrip( ";" ), "resources", "language" ) )
LANG_EXISTS = os.path.exists( os.path.join( LANG_PATH, LANG.lower(), "%s.xml" % LANG ) )


configs = {
    "IP": xbmc.getInfoLabel( "Network.IPAddress" ),
    "SUBNET": xbmc.getInfoLabel( "Network.SubnetAddress" ),
    "GATEWAY": xbmc.getInfoLabel( "Network.GatewayAddress" ),
    "DNS1": xbmc.getInfoLabel( "Network.DNS1Address" ),
    "DNS2": xbmc.getInfoLabel( "Network.DNS2Address" ),

    "XBMC_HOME_PATH": XBMC_HOME_PATH,
    #infos in sys.argv[ 2 ]
    "SVN_REV": "",
    "BUILD_RAR": "",
    "BUILD_PATH": "",

    "LANGUAGE": ( "English", LANG )[ LANG_EXISTS ],
    "30750": xbmc.getLocalizedString( 30750 ).encode( "iso-8859-1" ),
    "30751": xbmc.getLocalizedString( 30751 ).encode( "iso-8859-1" ),
    "30752": xbmc.getLocalizedString( 30752 ).encode( "iso-8859-1" ),
    "30753": xbmc.getLocalizedString( 30753 ).encode( "iso-8859-1" ),
    "30760": xbmc.getLocalizedString( 30760 ).encode( "iso-8859-1" ),
    "30770": xbmc.getLocalizedString( 30770 ).encode( "iso-8859-1" ),
    "30780": xbmc.getLocalizedString( 30780 ).encode( "iso-8859-1" ),
    "30790": xbmc.getLocalizedString( 30790 ).encode( "iso-8859-1" )
    }


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


def Main():
    if sys.argv[ 2 ]:
        try:
            if configs[ "XBMC_HOME_PATH" ].lower() != "q:\\":
                exec "args = _Info(%s)" % ( unquote_plus( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ) ), )

                configs[ "SVN_REV" ] = args.svn_rev
                configs[ "BUILD_RAR" ] = args.build_rar
                configs[ "BUILD_PATH" ] = os.path.dirname( args.build_rar )

                conf = update_xml % configs
                file( os.path.join( UPDATER_PATH, "update.xml" ), "w" ).write( conf )

                try:
                    skin_xml = file( os.path.join( UPDATER_PATH, "skin", "PM3.SD", "system_label.xml" ), "r" ).read()
                    skin = skin_xml % { "SYSTEM_LABEL": xbmc.getLocalizedString( 30795 ).encode( "iso-8859-1" ) }
                except:
                    try:
                        skin_xml = file( os.path.join( UPDATER_PATH, "skin", "PM3.SD", "system_label.xml" ), "r" ).read()
                        skin = skin_xml % { "SYSTEM_LABEL": "Settings" }
                    except: pass
                try:
                    if skin:
                        file( os.path.join( UPDATER_PATH, "skin", "PM3.SD", "Skin.xml" ), "w" ).write( skin )
                except: pass

                try:
                    try: os.makedirs( os.path.join( "E:\\UDATA", "9e115330", "0064122817A8" ) )
                    except: pass
                    from shutil import copy
                    copy( os.path.join( UPDATER_PATH, "skin", "PM3.SD", "UXSplash.jpg" ), os.path.join( "E:\\UDATA", "9e115330", "0064122817A8", "Splash.jpg" ) )
                    copy( os.path.join( "E:\\UDATA", "9e115330", "0064122817A8", "Splash.jpg" ), os.path.join( "X:\\0064122817A8", "Splash.jpg" ) )
                except: pass

                xbmc.executebuiltin( "XBMC.RunXBE(%s)" % os.path.join( UPDATER_PATH, "updater.xbe" ) )
        except:
            print_exc()
