

__all__ = [
    # public names
    "base_xml",
    "listitems_update",
    "listitems_cleaner",
    ]

listitems_update = r'''
		<List Text="%(32750)s" Sort="Off" Auto="On" Batch="True" Icon="skin\Confluence\media\update.png">
			<Item Action="MessageBox" Arg1="XBMC Updater">%(32709)s</Item>
			<!-- Test existence of XBMC home path, if error on rename log update auto stopped -->
			<Item Action="rename" Arg1="%(XBMC_HOME_PATH)s\xbmc.log" Arg2="%(XBMC_HOME_PATH)s\xbmc.log.exists">Testing XBMC Home Path [%(XBMC_HOME_PATH)s\]</Item>
			<Item Action="rename" Arg1="%(XBMC_HOME_PATH)s\xbmc.log.exists" Arg2="%(XBMC_HOME_PATH)s\xbmc.log">OK XBMC Home Path Exists...</Item>
			<!-- Test existence of Build ZIP, if error on rename update auto stopped -->
			<Item Action="rename" Arg1="%(BUILD_ZIP)s" Arg2="%(BUILD_ZIP)s.exists">Testing Build: [%(BUILD_ZIP)s]</Item>
			<Item Action="rename" Arg1="%(BUILD_ZIP)s.exists" Arg2="%(BUILD_ZIP)s">OK Build Exists...</Item>
			<!-- Ask User if realy want update, if don't want update auto stopped -->
			<Item Action="AskUser" Arg1="XBMC SVN r%(SVN_REV)s">%(32749)s: [%(BUILD_ZIP)s &gt;&gt; %(XBMC_HOME_PATH)s\]\n%(32751)s</Item>
			<!-- Clean Z cache for extracting fresh build -->
			<Item Action="Format" Arg1="Z">Cleaning Z Cache...</Item>
			<!-- extract build and error on "ZIP" update auto stopped -->
			<Item Action="unzip" Arg1="%(BUILD_ZIP)s" Arg2="Z:\">Extracting new build...</Item>
			<!-- Test existence of new default.xbe, if error on rename update auto stopped -->
			<Item Action="rename" Arg1="Z:\BUILD\default.xbe" Arg2="Z:\BUILD\default.xbe.exists">Testing existence of new default.xbe...</Item>
			<Item Action="rename" Arg1="Z:\BUILD\default.xbe.exists" Arg2="Z:\BUILD\default.xbe">OK new default.xbe exists...</Item>
			<!-- copytree build in xbmc dir, but not work if xbmc already exists -->
			<!-- <Item Action="Copy" Arg1="Z:\BUILD\" Arg2="%(XBMC_HOME_PATH)s\">Copytree...</Item> -->
			<!-- don't take any chance move build, a copytree not work 100 percent if xbmc exists -->
			<Item Action="Move" Arg1="Z:\BUILD\default.xbe" Arg2="%(XBMC_HOME_PATH)s\">Updating default.xbe...</Item>
			<Item Action="Move" Arg1="Z:\BUILD\system\" Arg2="%(XBMC_HOME_PATH)s\">Updating system\...</Item>
			<Item Action="Move" Arg1="Z:\BUILD\language\" Arg2="%(XBMC_HOME_PATH)s\">Updating language\...</Item>
			<Item Action="Move" Arg1="Z:\BUILD\skin\" Arg2="%(XBMC_HOME_PATH)s\">Updating skin\...</Item>
			<Item Action="Move" Arg1="Z:\BUILD\media\" Arg2="%(XBMC_HOME_PATH)s\">Updating media\...</Item>
			<Item Action="Move" Arg1="Z:\BUILD\sounds\" Arg2="%(XBMC_HOME_PATH)s\">Updating sounds\...</Item>
			<Item Action="Move" Arg1="Z:\BUILD\credits\" Arg2="%(XBMC_HOME_PATH)s\">Updating credits\...</Item>
			<Item Action="Move" Arg1="Z:\BUILD\screensavers\" Arg2="%(XBMC_HOME_PATH)s\">Updating screensavers\...</Item>
			<Item Action="Move" Arg1="Z:\BUILD\Visualisations\" Arg2="%(XBMC_HOME_PATH)s\">Updating Visualisations\...</Item>
			<!-- <Item Action="Move" Arg1="Z:\BUILD\UserData\" Arg2="%(XBMC_HOME_PATH)s\">Updating UserData\...</Item> -->
			<!-- optional format xbox caches -->
			<Item Action="Format" Arg1="X">Cleaning X Cache...</Item>
			<Item Action="Format" Arg1="Y">Cleaning Y Cache...</Item>
			<Item Action="Format" Arg1="Z">Cleaning Z Cache...</Item>
			<!-- notify user for update well done -->
			<Item Action="AskUser" Arg1="XBMC r%(SVN_REV)s">%(32752)s</Item>
			<!-- now :) return on xbmc -->
			<Item Action="%(XBMC_HOME_PATH)s\default.xbe">%(32753)s</Item>
		</List>'''


listitems_cleaner = r'''
		<List Text="%(32800)s" Sort="Off" Auto="On" Icon="skin\Confluence\media\cleaner.png">
			<List Text="%(32801)s" Sort="Off" Batch="True" Icon="skin\Confluence\media\info.png">
				<Item Action="MessageBox" Arg1="%(32800)s !">%(32802)s</Item>
			</List>
			<List Text="%(32810)s" Sort="Off" Batch="True" Icon="skin\Confluence\media\cleaner.png">
				<Item Action="AskUser" Arg1="Reset XBMC">%(32811)s</Item>
				<Item Action="zip" Arg1="%(UPDATER_PARDIR)s\userdata\" Arg2="%(UPDATER_PARDIR)s\userdata.zip">Creating Fresh UserData...</Item>
				<Item Action="rename" Arg1="%(UPDATER_PARDIR)s\userdata.zip" Arg2="%(UPDATER_PARDIR)s\userdata.zip.exists">Testing Fresh UserData Exists...</Item>
				<Item Action="rename" Arg1="%(UPDATER_PARDIR)s\userdata.zip.exists" Arg2="%(UPDATER_PARDIR)s\userdata.zip">OK Fresh UserData Exists...</Item>
				<Item Action="InputBox" Arg1="%(32812)s">backup</Item>
				<!--<Item Action="zip" Arg1="%(XBMC_HOME_PATH)s\userdata\" Arg2="%(XBMC_HOME_PATH)s\$KBResult$.zip">Creating Backup of UserData...</Item>-->
				<Item Action="rename" Arg1="%(XBMC_HOME_PATH)s\userdata" Arg2="%(XBMC_HOME_PATH)s\userdata_$KBResult$">Creating Backup of UserData...</Item>
				<Item Action="unzip" Arg1="%(UPDATER_PARDIR)s\userdata.zip" Arg2="%(XBMC_HOME_PATH)s\userdata\">Creating New Fresh Userdata...</Item>
				<Item Action="MessageBox" Arg1="%(32799)s">%(32813)s</Item>
			</List>
			<List Text="%(32820)s" Sort="Off" Batch="True" Icon="skin\Confluence\media\cleaner.png">
				<Item Action="AskUser" Arg1="XBMC Settings">%(32821)s</Item>
				<Item Action="delete" Arg1="%(XBMC_HOME_PATH)s\userdata\guisettings.xml">Deleting XBMC Settings...</Item>
				<Item Action="MessageBox" Arg1="%(32799)s">%(32822)s</Item>
			</List>
			<List Text="%(32830)s" Sort="Off" Batch="True" Icon="skin\Confluence\media\cleaner.png">
				<Item Action="AskUser" Arg1="XBMC Save">%(32831)s</Item>
				<Item Action="delete" Arg1="E:\TDATA\0face008">Cleaning XBMC TDATA...</Item>
				<Item Action="delete" Arg1="E:\UDATA\0face008">Cleaning XBMC UDATA...</Item>
				<Item Action="MessageBox" Arg1="%(32799)s">%(32832)s</Item>
			</List>
			<List Text="%(32840)s" Sort="Off" Batch="True" Icon="skin\Confluence\media\cleaner.png">
				<Item Action="AskUser" Arg1="Caches X, Y &amp; Z">%(32841)s</Item>
				<Item Action="Format" Arg1="X">Cleaning X Cache...</Item>
				<Item Action="Format" Arg1="Y">Cleaning Y Cache...</Item>
				<Item Action="Format" Arg1="Z">Cleaning Z Cache...</Item>
				<Item Action="MessageBox" Arg1="%(32799)s">%(32842)s</Item>
			</List>
			<List Text="%(32850)s" Sort="Off" Batch="True" Icon="skin\Confluence\media\cleaner.png">
				<Item Action="AskUser" Arg1="Cache E">%(32851)s</Item>
				<Item Action="delete" Arg1="E:\CACHE">Cleaning E Cache...</Item>
				<Item Action="Copy" Arg1="updater.tbn" Arg2="E:\CACHE">Creating E Cache...</Item>
				<Item Action="delete" Arg1="E:\CACHE\updater.tbn">Deleting dummy file...</Item>
				<Item Action="MessageBox" Arg1="%(32799)s">%(32852)s</Item>
			</List>
		</List>'''


base_xml = r'''<?xml version="1.0" encoding="utf-8"?>
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
			<Greeting>XBMC SVN Updater</Greeting>
		</FTP>
		<Newsfeed Enable="Yes" Interval="30" Continuous="Yes" Separator=" ~ ">
			<URL>www.xbox-scene.com/xbox1data/xbox-scene.xml</URL>
		</Newsfeed>
		<Preference>
			<DVD AutoLaunch="No"></DVD>
			<Data AutoLaunch="No"></Data>
			<Games AutoLaunch="No"></Games>
			<AudioCD AutoLaunch="No"></AudioCD>
			<SNTP Synchronize="No">216.244.192.3</SNTP>
			<ScreenSaver Wait="0" Type="1" EnableBGM="No">
				<Text>XBMC SVN Updater</Text>
			</ScreenSaver>
			<FanSpeed>1</FanSpeed>
			<AutoTurnOff>0</AutoTurnOff>
			<Use24HFormat>Yes</Use24HFormat>
			<AutoSetTime>Yes</AutoSetTime>
			<EnableDriveF>Yes</EnableDriveF>
			<EnableDriveG>Yes</EnableDriveG>
			<DefaultFolder></DefaultFolder>
			<Skin Path="skin\">Confluence</Skin>
			<ContextMenu AllowRecentList="Yes"></ContextMenu>
			<VideoSettings FastRefresh="Yes" Soften="Yes" EnableTextureCompression="Yes"></VideoSettings>
			<LanguageFile>%(LANGUAGE)s</LanguageFile>
		</Preference>
		<Audio>
			<EnableSoundTrack MusicPath="media\">Custom</EnableSoundTrack>
			<MusicVolume>95</MusicVolume>
			<SoundVolume>85</SoundVolume>
			<Back>%(UPDATER_PATH)s\skin\Confluence\sounds\back.wav</Back>
			<Select>%(UPDATER_PATH)s\skin\Confluence\sounds\click.wav</Select>
			<Scroll>%(UPDATER_PATH)s\skin\Confluence\sounds\cursor.wav</Scroll>
			<Menu_Up>%(UPDATER_PATH)s\skin\Confluence\sounds\cursor.wav</Menu_Up>
			<Menu_Down>%(UPDATER_PATH)s\skin\Confluence\sounds\cursor.wav</Menu_Down>
			<Memory_Slot>%(UPDATER_PATH)s\skin\Confluence\sounds\shutter.wav</Memory_Slot>
			<Action_Complete>%(UPDATER_PATH)s\skin\Confluence\sounds\click.wav</Action_Complete>
			<Game_Save_Select>%(UPDATER_PATH)s\skin\Confluence\sounds\out.wav</Game_Save_Select>
			<Keyboard_Stroke>%(UPDATER_PATH)s\skin\Confluence\sounds\click.wav</Keyboard_Stroke>
		</Audio>
		<LED>
			<Default>Orange</Default>
			<Busy>Flashing Red</Busy>
			<FileCopy>Flashing Red</FileCopy>
		</LED>
	</Settings>
	<Menu>%(LISTITEMS_UPDATE)s%(LISTITEMS_CLEANER)s
		<List Text="%(32790)s" Sort="Off" Auto="On" Icon="skin\Confluence\media\files.png">
			<List Text="%(32702)s" Sort="Off" Batch="True" Icon="skin\Confluence\media\info.png">
				<Item Action="MessageBox" Arg1="%(32700)s">%(32701)s</Item>
			</List>
			<Item Action="FileManager" Arg1="%(XBMC_HOME_PATH)s" Icon="skin\Confluence\media\files.png">%(32789)s</Item>
			<Item Action="FileManager" Icon="skin\Confluence\media\files.png">%(32790)s</Item>
			<!--<Item Action="FileManager" Arg1="%(UPDATER_PATH)s" Icon="skin\Confluence\media\files.png">DEVS ONLY</Item>-->
			<Item Action="TextEditor" Arg1="%(XBMC_HOME_PATH)s\xbmc.log" Icon="skin\Confluence\media\info.png">XBMC.log</Item>
		</List>
		<Item Action="TextEditor" Icon="skin\Confluence\media\editor.png">%(32791)s</Item>
		<Item Action="Settings" Icon="skin\Confluence\media\settings.png">UnleashX %(32795)s</Item>
		<Item Action="%(XBMC_HOME_PATH)s\default.xbe" Icon="skin\Confluence\media\goxbmc.png">%(32760)s</Item>
		<Item Action="%(UPDATER_PATH)s\updater.xbe" Icon="skin\Confluence\media\reload.png">%(32761)s</Item>
		<Item Action="Restart" Icon="skin\Confluence\media\restart.png">%(32770)s</Item>
		<Item Action="Shutdown" Icon="skin\Confluence\media\exit.png">%(32780)s</Item>
	</Menu>
</UnleashX>
'''


def test():
    import os
    configs = {
        "IP": "0.0.0.0",
        "SUBNET": "0.0.0.0",
        "GATEWAY": "0.0.0.0",
        "DNS1": "0.0.0.0",
        "DNS2": "0.0.0.0",

        "UPDATER_PATH": os.getcwd(),
        "UPDATER_PARDIR": os.getcwd(),
        "XBMC_HOME_PATH": os.getcwd(),

        #infos in paths.txt
        "SVN_REV": "0",
        "BUILD_ZIP": "test.zip",
        #"BUILD_PATH": os.getcwd(),
        "LISTITEMS_UPDATE": "",
        "LISTITEMS_CLEANER": "",

        "LANGUAGE": os.getcwd()+"\\test.xml",
        "32700": "",
        "32701": "",
        "32702": "",
        "32709": "",
        "32749": "",
        "32750": "",
        "32751": "",
        "32752": "",
        "32753": "",
        "32760": "",
        "32761": "",
        "32770": "",
        "32780": "",
        "32789": "",
        "32790": "",
        "32791": "",
        "32795": "",
        "32799": "",
        "32800": "",
        "32801": "",
        "32802": "",
        "32810": "",
        "32811": "",
        "32812": "",
        "32813": "",
        "32820": "",
        "32821": "",
        "32822": "",
        "32830": "",
        "32831": "",
        "32832": "",
        "32840": "",
        "32841": "",
        "32842": "",
        "32850": "",
        "32851": "",
        "32852": "",
        }
    configs[ "LISTITEMS_UPDATE" ] = listitems_update % configs
    configs[ "LISTITEMS_CLEANER" ] = listitems_cleaner % configs
    print base_xml % configs



if __name__ == "__main__":
    test()
    #print __all__
