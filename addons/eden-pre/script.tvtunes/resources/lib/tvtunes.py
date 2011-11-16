# -*- coding: utf-8 -*-

# General Import's
from solo_mode import *


#https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Key.h#L82
ACTION_PARENT_DIR    = 9
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK      = 92
ACTION_CONTEXT_MENU  = 117
ACTION_CLOSE_TVTUNES = [ ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_NAV_BACK ]
ACTION_CLOSE_DIALOG  = [ ACTION_CONTEXT_MENU ] + ACTION_CLOSE_TVTUNES


class Gui( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        # get class of solo modo for function ( .search_theme_list and .download )
        self.tvtunes = TvTunes( False )
        # get listing of tvshows
        self.tvshows = getTVShows( "list" )
        # dico for already searched on site. don't re-scrape site, check first in dico.
        self.already_searched = {}
        # boolean for disabled "onClick, onContextMenu, and cond_synchronize_containers"
        self.onBusy = False

    def onInit( self ):
        xbmc.executebuiltin( "SetProperty(AnimeWindowXMLDialogClose,true)" )
        # activate busy
        self.busy( True )
        # get you controls
        self.control_tvshows_list = self.getControl( 103 )
        self.control_tunes_list   = self.getControl( 203 )
        self.cond_synchronize_containers = "[Container(103).OnNext | Container(103).OnPrevious] | !StringCompare(Container(103).ListItem.Label,Container(203).ListItem.Property(TVShowTitle))"
        # add tvshows
        self.addContainer()
        # print time for initialized script
        LOGGER.notice.LOG( "initialized Gui took %s", time_took( START_TIME ) )
        # set window property, current scraper name
        try: xbmc.executebuiltin( "SetProperty(scrapername,%s)" % scraper.scraper_name )
        except: LOGGER.error.print_exc()
        # stop busy
        self.busy( False )

    def busy( self, action ):
        # set onBusy boolean( True | False )
        self.onBusy = action
        # start or stop busy
        try: self.getControl( 10 ).setVisible( self.onBusy )
        except: pass

    def addContainer( self ):
        # list of all xbmcgui.ListItem
        self.listitems = self.tvshows #[]
        # set self.listitems
        """
        for tvshow in self.tvshows:
            # get dir of tvshow
            path = tvshow[ "file" ]
            # get tune path
            tune = getThemePath( tvshow[ "file" ] )
            # initialize listitem
            listitem = xbmcgui.ListItem( tvshow[ "label" ], path, tvshow[ "thumbnail" ] )
            # set properties
            listitem.setProperty( "tune", tune )
            IsPlayable = ( "", "true" )[ tune != "" ]
            listitem.setProperty( "IsPlayable", IsPlayable )
            #listitem.setProperty( "isRemoteAndOff", "" )

            # check is remote and get statut
            #if re.search( "((smb|ftp)://)", path.lower() ):
            #    #get statut from remotes dico
            #    if remote_utils.REMOTES.getStatutFromPath( path, "off" ):
            #        # oops! remote is off line
            #        listitem.setProperty( "isRemoteAndOff", "off" )

            # check if has theme
            #if not listitem.getProperty( "isRemoteAndOff" ):
            #    #don't visit path if remote's is off, because script run slowly
            #    if path_exists( path + THEME_FILE ):
            #        # has theme set true
            #        listitem.setProperty( "IsPlayable", "true" )

            # add tvshow to self.listitems
            self.listitems.append( listitem )
        """
        # now add tvshows in container
        self.control_tvshows_list.reset()
        self.control_tvshows_list.addItems( self.listitems )
        self.setFocus( self.control_tvshows_list )

    def refresh( self ):
        pass
        """
        t1 = time.time()
        self.busy( True )
        #remote_utils.REMOTES = remote_utils.Remotes()
        for listitem in self.listitems:
            IsPlayable = ""
            isRemoteAndOff = ""
            path = listitem.getLabel2()

            #if re.search( "((smb|ftp)://)", path.lower() ):
            #    #get statut from remotes dico
            #    if remote_utils.REMOTES.getStatutFromPath( path, "off" ):
            #        if remote_utils.REMOTES.getStatutFromPath( path, "off", True ):
            #            isRemoteAndOff = "off"

            if not isRemoteAndOff:
                #don't visit path script run slowly if remote is off
                if path_exists( path + THEME_FILE ):
                    IsPlayable = "true"

            listitem.setProperty( "IsPlayable", IsPlayable )
            listitem.setProperty( "isRemoteAndOff", isRemoteAndOff )
        self.busy( False )
        LOGGER.notice.LOG( "refresh remote took %s", time_took( t1 ) )
        """

    def sendClick( self, controlID ):
        try: self.onClick( controlID )
        except: LOGGER.error.print_exc()

    def onClick( self, controlID ):
        try:
            if self.onBusy: return
            #action sur une des listes
            if controlID == 203:
                tunes = self.already_searched.get( self.control_tvshows_list.getSelectedItem().getLabel() )
                XBMCPlayer( listitem=self.control_tunes_list.getSelectedItem(), tunes=tunes )

            elif controlID in [ 15, 103 ]:
                #Renvoie l'item selectionne
                listitem = self.control_tvshows_list.getSelectedItem()
                name = listitem.getLabel()
                self.getTunes( name, controlID == 15 )

            elif controlID == 5:
                self._close_dialog()
                Addon.openSettings()
                #xbmc.sleep( 10 )
                # assume path for XBMC4Xbox or old XBMC, get cwd and run full path.
                xbmc.executebuiltin( 'RunScript(%s)' % os.path.join( sys.path[ 0 ], "tvtunes.py" ) )
        except:
            LOGGER.error.print_exc()

    def getTunes( self, name, manual=False ):
        searchname = name
        if manual:
            kb = xbmc.Keyboard( name, Language( 32113 ), False )
            kb.doModal()
            if kb.isConfirmed():
                result = kb.getText()
                if result == name:
                    self.getTunes( name, True )
                    #self.sendClick( 15 )
                    return
                searchname = result
            else:
                return

        tunes = self.already_searched.get( name )
        if manual or not tunes:
            self.busy( True )
            tunes = self.tvtunes.search_theme_list( searchname )
            lis = []
            scrapername = xbmc.getInfoLabel( "Window.Property(scrapername)" ) or "TvTunes"
            for tune in tunes:
                title = setPrettyFormatting( searchname, tune[ "name" ] )
                l = xbmcgui.ListItem( title, tune[ "url" ] )
                l.setProperty( "TVShowTitle", name )
                l.setInfo( 'music', { 'title': title, 'Artist': scrapername, 'Album': searchname } )
                lis.append( l )
            self.already_searched[ name ] = lis
            self.busy( False )
        else:
            lis = tunes

        self.control_tunes_list.reset()
        self.control_tunes_list.addItems( lis )

        if lis:
            xbmc.executebuiltin( "SetProperty(tuneschoice,true)" )
            self.setFocus( self.control_tunes_list )
        else:
            self.setFocus( self.control_tvshows_list )
            xbmc.executebuiltin( "ClearProperty(tuneschoice)" )
            self.getTunes( name, True )
            #self.sendClick( 15 )

    def onContextMenu( self ):
        try:
            if self.onBusy: return
            selected = -1
            buttons = []
            focusId = self.getFocusId()
            if focusId == 103:
                buttons += [ Language( 32200 ) ]
                listitem = self.control_tvshows_list.getSelectedItem()
                IsPlayable = IsTrue( listitem.getProperty( "IsPlayable" ) )
                if IsPlayable: buttons += [ Language( 32201 ), Language( 32202) ]

                #isRemoteAndOff = listitem.getProperty( "isRemoteAndOff" ) == "off"
                #if isRemoteAndOff: buttons += [ Language( 32204 ) ]

                #add manual search
                buttons += [ Language( 32130 ) ]

            elif focusId == 203:
                listitem = self.control_tunes_list.getSelectedItem()
                buttons += [ Language( 32201 ), Language( 32203 ), Language( 32130 ) ]

            if buttons:
                listitem.select( 1 )
                cm = DialogContextMenu( "script-TvTunes-ContextMenu.xml", AddonPath, buttons=buttons )
                cm.doModal()
                selected = cm.selected
                del cm
                listitem.select( 0 )

            if focusId == 103:
                if selected == 0:
                    #get tunes for current selected tvshow
                    self.sendClick( focusId )

                #elif selected == 1 and isRemoteAndOff:
                #    # refresh container for remotes
                #    self.refresh()

                elif selected == 1 and IsPlayable:
                    #play local tune for current selected tvshow
                    XBMCPlayer( listitem=listitem )

                elif selected == 2 and IsPlayable:
                    #delete local tune for current selected tvshow
                    path = listitem.getProperty( "tune" )
                    if path_exists( path ) and xbmcgui.Dialog().yesno( LangXBMC( 122 ), LangXBMC ( 125 ), hide_parts_path( path ) ):
                        FileDelete( path )
                        if path_exists( path ):
                            # error deleting
                            xbmcgui.Dialog().ok( LangXBMC( 16205 ), LangXBMC( 16206 ), hide_parts_path( path ) )
                        else:
                            listitem.setProperty( "IsPlayable", "" )

                elif selected in [ 1, 3 ]:
                    #manual search
                    self.sendClick( 15 )

            elif focusId == 203:
                if selected == 0:
                    #play current selected online tune
                    self.sendClick( focusId )

                elif selected == 1:
                    # download current selected tune
                    if xbmcgui.Dialog().yesno( Language( 32103 ), Language( 32114 ), listitem.getLabel() ):
                        li = self.control_tvshows_list.getSelectedItem()
                        DIALOG_PROGRESS.create( Language( 32107 ), listitem.getLabel() )
                        OK, tune = self.tvtunes.download( listitem.getLabel2(), li.getLabel2(), li.getLabel() )
                        closeDialogProgress()

                        if OK:
                            listitem = self.control_tvshows_list.getSelectedItem()
                            if path_exists( tune ):
                                listitem.setProperty( "tune", tune )
                                listitem.setProperty( "IsPlayable", "true" )
                                #play local tune of current downloaded tune
                                XBMCPlayer( listitem=listitem )
                        else:
                            #error
                            xbmcgui.Dialog().ok( LangXBMC( 257 ), Language( 32120 ), listitem.getLabel() )

                elif selected == 2:
                    #manual search
                    self.sendClick( 15 )
        except:
            LOGGER.error.print_exc()
            closeDialogProgress()

    def onFocus( self, controlID ):
        pass

    def synchronize( self ):
        try:
            if xbmc.getCondVisibility( self.cond_synchronize_containers ):
                if self.onBusy: return
                tunes = self.already_searched.get( self.control_tvshows_list.getSelectedItem().getLabel() )
                if not tunes:
                    xbmc.executebuiltin( "ClearProperty(tuneschoice)" )
                else:
                    xbmc.executebuiltin( "SetProperty(tuneschoice,true)" )
                    self.control_tunes_list.reset()
                    self.control_tunes_list.addItems( tunes )
        except:
            LOGGER.error.print_exc()

    def onAction( self, action ):
        self.synchronize()

        if action == ACTION_CONTEXT_MENU:
            self.onContextMenu()

        elif action in ACTION_CLOSE_TVTUNES:
            self._close_dialog()
            dialog_help_site()

    def _close_dialog( self ):
        xbmc.executebuiltin( "ClearProperty(AnimeWindowXMLDialogClose)" )
        time.sleep( .3 )
        self.close()


class DialogContextMenu( xbmcgui.WindowXMLDialog ):
    BUTTON_START = 1001
    BUTTON_END   = 1012

    def __init__( self, *args, **kwargs ):
        self.TunesListHasFocus = xbmc.getCondVisibility( "Control.HasFocus(203)" )
        self.buttons  = kwargs[ "buttons" ]
        self.selected = -1

    def onInit( self ):
        xbmc.executebuiltin( "SetProperty(AnimeContextMenuOnClose,true)" )
        try:
            if self.TunesListHasFocus:
                xbmc.executebuiltin( "SetProperty(TunesListHasFocus,true)" )

            for count, button in enumerate( self.buttons ):
                try:
                    self.getControl( self.BUTTON_START + count ).setLabel( button )
                    self.getControl( self.BUTTON_START + count ).setVisible( True )
                except:
                    pass
            self.setFocusId( self.BUTTON_START )
            
            for control in range( self.BUTTON_START + count + 1, self.BUTTON_END ):
                try:
                    #self.getControl( control ).setLabel( "" )
                    self.getControl( control ).setVisible( False )
                except:
                    pass
        except:
            LOGGER.error.print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            self.selected = controlID - self.BUTTON_START
            if self.selected < 0: self.selected = -1
        except:
            LOGGER.error.print_exc()
            self.selected = -1
        self._close_dialog()

    def onAction( self, action ):
        if action in ACTION_CLOSE_DIALOG:
            self.selected = -1
            self._close_dialog()

    def _close_dialog( self ):
        xbmc.executebuiltin( "ClearProperty(AnimeContextMenuOnClose)" )
        time.sleep( .2 )
        xbmc.executebuiltin( "ClearProperty(TunesListHasFocus)" )
        self.close()


class XBMCPlayer( xbmc.Player ):
    """ Subclass of XBMC Player class.
        Overrides onplayback events, for custom actions.
    """

    def __init__( self, *args, **kwargs ):
        self.listitem = kwargs[ "listitem" ]

        select_tune = 0
        self.playlist = None
        if kwargs.get( "tunes" ):
            self.playlist = xbmc.PlayList( xbmc.PLAYLIST_MUSIC )
            self.playlist.clear()
            for count, tune in enumerate( kwargs[ "tunes" ] ):
                if tune == self.listitem: select_tune = count
                #tune.setInfo( 'music', { 'title': tune.getLabel() } )
                self.playlist.add( tune.getLabel2(), tune )

        self._setInfo()
        self._play( select_tune )
        self._showPlayerControls()

    def _showPlayerControls( self ):
        if IsTrue( Addon.getSetting( "playercontrols" ) ):
            xbmc.sleep( 100 )
            xbmc.executebuiltin( 'ActivateWindow(PlayerControls)' )

    def _setInfo( self ):
        self.tune = self.listitem.getProperty( "tune" )
        #self.listitem.setInfo( 'music', { 'title': self.listitem.getLabel() } )

    def _play( self, select_tune=0 ):
        if self.playlist is not None:
            if select_tune:
                self.playselected( select_tune )
            else:
                self.play( self.playlist )
        else:
            self.play( self.tune, self.listitem )

    def onPlayBackStarted( self ):
        try: self.listitem.setSelected( True )
        except AttributeError: pass
        except: LOGGER.error.print_exc()

    def onPlayBackEnded( self ):
        try: self.listitem.setSelected( False )
        except AttributeError: pass
        except: LOGGER.error.print_exc()


def Main():
    if params.mode != "solo" or params.isempty():
        LOGGER.info.LOG( "Gui Mode" )
        w = Gui( "script-TvTunes-main.xml", AddonPath )
        w.doModal()
        del w
    else:
        LOGGER.info.LOG( "Solo Mode" )
        TvTunes( True )



if ( __name__ == "__main__" ):
    Main()
