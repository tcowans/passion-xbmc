
# Modules general
import sys
import time

# Modules XBMC
import xbmc
import xbmcgui
from xbmcaddon import Addon

from videolibrary import *

from log import logAPI
LOGGER = logAPI()


# constants
CURRENT_SET = ", ".join( sys.argv[ 2: ] ).decode( "utf-8" ) or xbmc.getInfoLabel( "listitem.label" )
#print ( sys.argv[ 2 ], xbmc.getInfoLabel( "listitem.label" ) )

ADDON      = Addon( "plugin.moviesets" )
ADDON_DIR  = ADDON.getAddonInfo( "path" )

Language   = ADDON.getLocalizedString # ADDON strings
LangXBMC   = xbmc.getLocalizedString  # XBMC strings


# https://raw.github.com/xbmc/xbmc/master/xbmc/input/ButtonTranslator.cpp
# https://raw.github.com/xbmc/xbmc/master/xbmc/guilib/Key.h
ACTION_PARENT_DIR    =   9
ACTION_PREVIOUS_MENU =  10
ACTION_SHOW_INFO     =  11
ACTION_NAV_BACK      =  92
ACTION_CONTEXT_MENU  = 117
CLOSE_DIALOG         = [ ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_NAV_BACK ]
CLOSE_SUB_DIALOG     = [ ACTION_CONTEXT_MENU ] + CLOSE_DIALOG


class DialogSelect( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        self.listitems  = []
        self.ismodified = False
        self.mode       = str( sys.argv[ 1 ] ) #( "addmovie", "remmovie" )[ 0 ]
        self.selectItem = 0

        self.listitems = []
        xbmc.executebuiltin( 'ActivateWindow(busydialog)' )
        try: self.setListItems()
        except: LOGGER.error.print_exc()
        xbmc.executebuiltin( 'Dialog.Close(busydialog,true)' )

        if self.mode == "newset":
            xbmcgui.Dialog().ok( CURRENT_SET, "Remember: If you want saving new Set!", "Select one movie or more." )

    def setListItems( self ):
        movies = getMovies( [ "set", "sorttitle", "title", "thumbnail", "year" ] )
        self.listitems = []
        for count, movie in enumerate( movies ):
            strSet = "".join( movie[ "set" ] )
            if self.mode in [ "remmovie", "remset" ] and CURRENT_SET != strSet:
                continue
            label  = "%s  (%s)" % ( movie[ "label" ], movie[ "year" ] )
            label2 = ""
            if strSet: label2 = "[B]%s[/B]: %s" % ( LangXBMC( 20457 ), strSet )
            #
            listitem = xbmcgui.ListItem( label, label2, "DefaultVideo.png", movie[ "thumbnail" ] )
            listitem.setProperty( "Addon.Summary", label2 )
            #
            listitem.setProperty( "ismodified", "0" )
            listitem.setProperty( "set",        strSet )
            listitem.setProperty( "sorttitle",  movie[ "sorttitle" ] )
            listitem.setProperty( "movieid",    str( movie[ "movieid" ] ) )
            #
            if self.mode in [ "addmovie", "newset" ] and CURRENT_SET == strSet:
                listitem.select( 1 )
                self.selectItem = count
            #
            if self.mode == "remset" and CURRENT_SET == strSet:
                #
                self.ismodified = True
                listitem.setProperty( "ismodified", "1" )
                listitem.setProperty( "set",        "" )
                listitem.setProperty( "sorttitle",  "" )

            #print ( CURRENT_SET, strSet )
            self.listitems.append( listitem )

    def onInit( self ):
        st = time.time()
        self.getControl( 1 ).setLabel( "Manage Set (%s)" % CURRENT_SET )
        try:
            self.control_list = self.getControl( 6 )
            self.getControl( 3 ).setVisible( False )
            self.getControl( 5 ).controlUp( self.control_list )
        except:
            self.control_list = self.getControl( 3 )
            LOGGER.error.print_exc()
        #xbmc.executebuiltin( "SetProperty(ismodified,0)" )
        #try: self.getControl( 5 ).setEnableCondition( 'stringcompare(window.property(ismodified),1)' ) #.setLabel( LangXBMC( 413 ) )
        #except: LOGGER.error.print_exc()

        if self.listitems:
            try: self.setContainer()
            except: LOGGER.error.print_exc()
        print "MovieSets::DialogSelect::onInit took %r" % time_took( st )

    def setContainer( self, selectItem=0 ):
        self.control_list.reset()
        self.control_list.addItems( self.listitems )
        self.control_list.selectItem( selectItem or self.selectItem )
        self.setFocus( self.control_list )

        if not self.listitems:
            self.setFocusId( 5 )

    def onClick( self, controlID ):
        try:
            if controlID in [ 3, 6 ]:
                item = self.control_list.getSelectedItem()
                strSet = item.getProperty( "set" )

                if not strSet:
                    label2 = "[B]%s[/B]: %s" % ( LangXBMC( 20457 ), CURRENT_SET )
                    item.setLabel2( CURRENT_SET )
                    item.setProperty( "Addon.Summary", label2 )
                    item.setProperty( "set",  CURRENT_SET )
                    item.setProperty( "ismodified", "1" )
                    #xbmc.executebuiltin( "SetProperty(ismodified,1)" )
                    self.ismodified = True
                    item.select( self.mode in [ "addmovie", "newset" ] )

                else:
                    #
                    sorttitle = item.getProperty( "sorttitle" )
                    choice = [
                        "Remove from Set  (%s)" % strSet,
                        "Edit SortTitle  (%s)" % sorttitle,
                        ]
                    selected = xbmcgui.Dialog().select( item.getLabel(), choice )

                    if selected == 0:
                        item.setLabel2( "" )
                        item.setProperty( "Addon.Summary", "" )
                        item.setProperty( "set", "" )
                        item.setProperty( "ismodified", "1" )
                        #xbmc.executebuiltin( "SetProperty(ismodified,1)" )
                        self.ismodified = True
                        item.select( 0 )

                    elif selected == 1:
                        kb = xbmc.Keyboard( sorttitle, "Edit SortTitle" )
                        kb.doModal()
                        if kb.isConfirmed():
                            new_sort = kb.getText()
                            item.setProperty( "sorttitle",  new_sort )
                            item.setProperty( "ismodified", "1" )
                            #xbmc.executebuiltin( "SetProperty(ismodified,1)" )
                            self.ismodified = True

            elif controlID == 5:
                self._close_dialog()
        except:
            LOGGER.error.print_exc()

    def onFocus( self, controlID ):
        pass

    def onAction( self, action ):
        if action in CLOSE_DIALOG:
            self.ismodified = False
            self._close_dialog()

    def _close_dialog( self, t=500 ):
        if self.ismodified:
            self.listitems = [ li for li in self.listitems if li.getProperty( "ismodified" ) == "1" ]
        self.close()
        if t: xbmc.sleep( t )



def Main():
    if str( sys.argv[ 1 ] ) == "newset":
        new_set = ""
        kb = xbmc.Keyboard( "", Language( 32331 ) )
        kb.doModal()
        if kb.isConfirmed():
            new_set = kb.getText() #.decode( "utf-8" )
        if not new_set: return
        global CURRENT_SET
        CURRENT_SET = new_set

    heading = ""
    w = DialogSelect( "DialogSelect.xml", ADDON_DIR )
    if str( sys.argv[ 1 ] ) != "remset":
        w.doModal()
    else:
        heading = LangXBMC( 646 )
    ismodified = w.ismodified
    listitems = w.listitems
    del w
    heading = heading or "Confirm changes (%i)" % len( listitems )

    if ismodified and xbmcgui.Dialog().yesno( heading, "[B]%s[/B]: %s" % ( LangXBMC( 20457 ), CURRENT_SET ), LangXBMC( 14070 ) ):
        DIALOG_PROGRESS = xbmcgui.DialogProgress()
        DIALOG_PROGRESS.create( "Updating library..." )
        diff = 100.0 / len( listitems )
        percent = 0
        OK = False
        for li in listitems:
            percent += diff
            if li.getProperty( "ismodified" ) == "1":
                strSet    = li.getProperty( "set" )
                DIALOG_PROGRESS.update( int( percent ), "[B]Movie[/B]: %s" % li.getLabel(), "[B]%s[/B]: %s" % ( LangXBMC( 20457 ), strSet ), "Please wait..." )
                movieid   = li.getProperty( "movieid" )
                sorttitle = li.getProperty( "sorttitle" )
                params = { "set": strSet, "sorttitle": sorttitle, "movieid": int( movieid ) }
                #if strSet: params[ "set" ].append( strSet )
                OK = setMovieDetails( params ) or OK

        if xbmc.getCondVisibility( "Window.IsVisible(progressdialog)" ):
            xbmc.executebuiltin( "Dialog.Close(progressdialog)" )
        if OK:
            xbmc.executebuiltin( "Container.Refresh" )

    del ismodified, listitems

