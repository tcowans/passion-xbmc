
import time
START_TIME = time.time()

import os
import re
import sys
from traceback import print_exc

import xbmc
import xbmcgui
from xbmcaddon import Addon

# addon constants
AddonId = "xbmc.translator"
CWD = sys.path[ 0 ]
UNDER_XBOX = ( os.environ.get( "OS", "xbox" ) == "xbox" )

from utilities import *
from Language import Language
from convert import normalize_string
from dialogs import DialogContextMenu



class Translator( xbmcgui.WindowXML ):
    CONTROL_LIST_A = 50

    def __init__( self, *args, **kwargs ):
        self.RestartXBMC_ReloadLanguage = False
        self.IsModified = False
        self.googleTrans = False
        self.listitems = []

        self.Addon = Addon( AddonId )
        self._get_settings()

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "LanguagePath" ] = self.Addon.getSetting( "LanguagePath" )

        self.settings[ "viewmode" ]     = int( self.Addon.getSetting( "viewmode" ) )
        self.settings[ "sortmethod" ]   = int( self.Addon.getSetting( "sortmethod" ) )
        self.settings[ "sortorder" ]    = int( self.Addon.getSetting( "sortorder" ) )
        self.settings[ "savefolderviews" ] = ( self.Addon.getSetting( "savefolderviews" ) == "true" )

    def setListItems( self ):
        self.DefaultLanguage = "English"
        self.CurrentLanguage = xbmc.getLanguage()
        self.FolderLanguage  = self.settings[ "LanguagePath" ]
        self.DefaultFolderLanguage = "special://xbmc/language/"
        if not os.path.exists( xbmc.translatePath( self.FolderLanguage ) ):
            print "Folder language not exists! '%s'" % self.FolderLanguage
            self.FolderLanguage = self.DefaultFolderLanguage

        if not self.FolderLanguage.startswith( "special" ):
            for folder in [ "profile", "home", "xbmc" ]:
                special = "special://%s/" % folder
                self.FolderLanguage = self.FolderLanguage.replace( xbmc.translatePath( special ), special )

        if ( xbmc.translatePath( "special://skin/" ) in xbmc.translatePath( self.FolderLanguage ) ):
            self.FolderLanguage = "special://skin/language/"
        self.FolderLanguage = self.FolderLanguage.replace( "\\", "/" ).rstrip( "/" )

        self.setContainerProperties()
        # get languages source
        self.language = Language( self )
        self.listitems = self.language.listitems

    def onInit( self ):
        xbmc.executebuiltin( "ActivateWindow(busydialog)" )
        self.setSortMethodControl()
        self.setContainer( setviewmode=self.settings[ "viewmode" ] )
        LOG( "notice", "initialized took %s", time_took( START_TIME ) )
        xbmc.executebuiltin( "Dialog.Close(busydialog)" )

    def setSortMethodControl( self ):
        label = ( 20316, 103 )[ self.settings[ "sortmethod" ] ]
        self.getControl( 13 ).setLabel( xbmc.getLocalizedString( label ) )

    def setContainerProperties( self ):
        self.setProperty( "IsModified", ( "", "Language file has been changed!" )[ self.IsModified ] )
        self.setProperty( "CurrentLanguage", self.CurrentLanguage )
        self.setProperty( "FolderLanguage", self.FolderLanguage )
        self.setProperty( "CurrentEnglishString", "" )
        self.Addon = Addon( AddonId )
        self.setProperty( "ExtraKeyboard_TopOrBottom", ( "top", "bottom" )[ int( self.Addon.getSetting( "ExtraKB" ) ) ] )

    def setContainer( self, filter="", SelectId="", setviewmode=None ):
        if setviewmode is not None:
            self.ContainerId = ( 50, 51 )[ setviewmode ]
            if setviewmode: xbmc.executebuiltin( "SendClick(2)" )
        else:
            self.ContainerId = ( 50, 51 )[ xbmc.getCondVisibility( "Control.IsVisible(51)" ) ]
        try:

            if not bool( self.listitems ):
                if self.IsModified:
                    # ask for save change
                    self._save_change()
                self.IsModified = False
                self.googleTrans = False
                self.getControl( self.ContainerId ).reset()
                self.setListItems()

            self.setContainerProperties()
            if self.listitems:
                selectitem = 0

                additems = []
                if not filter:
                    additems = self.listitems
                else:
                    for li in self.listitems:
                        if filter == "UnTranslated" and li.getProperty( "UnTranslated" ) == "false":
                            continue
                        if filter == "Translated" and li.getProperty( "IsModified" ) != "true":
                            continue
                        additems.append( li )

                if additems:
                    if self.settings[ "sortmethod" ]:
                        additems = sorted( additems, key=lambda li: normalize_string( li.getLabel(), True ) )
                    if self.settings[ "sortorder" ]:
                        additems = list( reversed( additems ) )
                    for count, li in enumerate( additems ):
                        if li.getProperty( "id" ) == SelectId:
                            selectitem = count

                # add listitems
                self.getControl( self.ContainerId ).reset()
                self.getControl( self.ContainerId ).addItems( additems )
                if additems: #self.getControl( self.ContainerId ).size():
                    self.getControl( self.ContainerId ).selectItem( selectitem )
                    self.setFocusId( self.ContainerId )

            # fixe view on xbox
            if UNDER_XBOX and setviewmode is not None:
                xbmc.executebuiltin( "Container.SetViewMode(%i)" % self.ContainerId )
                xbmc.sleep( 20 )
                self.setFocusId( self.ContainerId )
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def sendClick( self, controlID ):
        try: self.onClick( controlID )
        except: print_exc()

    def getTranslate( self, text, minimal=2 ):
        translated = ""
        if text:
            if ( len( text ) <= minimal ) or text.isdigit():
                translated = text
            else:
                country = self.Addon.getSetting( "country" )
                if country.lower() == "auto": country = self.CurrentLanguage
                pDialog = xbmcgui.DialogProgress()
                pDialog.create( "Google Translate", "English to %s" % country, text, "Please wait..." )
                try:
                    import LanguageTools
                    translated = LanguageTools.translate_text( text, country, "google" )
                except:
                    print_exc()
        self.googleTrans = False
        xbmc.executebuiltin( "Dialog.Close(progressdialog)" )
        return translated

    def onClick( self, controlID ):
        try:
            self.ContainerId = ( 50, 51 )[ xbmc.getCondVisibility( "Control.IsVisible(51)" ) ]
            if controlID == self.ContainerId:
                # get clicked listitem
                listitem = self.getControl( self.ContainerId ).getSelectedItem()
                # get position
                pos = int( listitem.getProperty( "Position" ) )
                # get id
                id = listitem.getProperty( "id" )
                if id:
                    CurrentEnglishString = fixe_line_return( listitem.getLabel2(), True )
                    
                    DefaultText = fixe_line_return( listitem.getLabel(), True )
                    old_text = DefaultText
                    if self.googleTrans: old_text = self.getTranslate( CurrentEnglishString )
                    old_text = old_text or DefaultText

                    if ( self.Addon.getSetting( "BoldKB" ) == "true" ):
                        CurrentEnglishString = "[B]%s[/B]" % CurrentEnglishString
                    self.setProperty( "CurrentEnglishString", CurrentEnglishString )
                    self.setProperty( "ShowCurrentEnglishString", "true" )
                    
                    kb = xbmc.Keyboard( old_text, self.CurrentLanguage + " (Enter desired string)", False )
                    kb.doModal()
                    if kb.isConfirmed():
                        new_text = kb.getText()
                        if new_text != DefaultText:
                            new_text = fixe_line_return( new_text )
                            self.listitems[ pos ].setLabel( new_text )
                            self.listitems[ pos ].setProperty( "IsModified", "true" )
                            self.setProperty( "IsModified", "Language file has been changed!" )
                            self.IsModified = True
                    self.setProperty( "ShowCurrentEnglishString", "" )

            # PAS TRES BON COMME FILTRE :(
            UnTranslated = self.getControl( 19 ).isSelected()
            Translated = self.getControl( 20 ).isSelected()
            Changed = self.getControl( 21 ).isSelected()
            filter = ( "", "UnTranslated" )[ UnTranslated ]
            filter = ( filter, "Translated" )[ Translated ]
            filter = ( filter, "Changed" )[ Changed ]
            
            # get selected id for selectitem again, if controlID 22 clicked
            SelectId = xbmc.getInfoLabel( "Container(50).ListItem.Property(id)" ) or xbmc.getInfoLabel( "Container(51).ListItem.Property(id)" )
            if controlID == 19:
                # UNTRANSLATED BUTTON
                filter = ( "", "UnTranslated" )[ UnTranslated ]
                self.setContainer( filter, SelectId )
                self.getControl( 19 ).setSelected( UnTranslated )
                self.getControl( 20 ).setSelected( False )
                self.getControl( 21 ).setSelected( False )

            elif controlID == 20:
                # TRANSLATED BUTTON
                filter = ( "", "Translated" )[ Translated ]
                self.setContainer( filter, SelectId )
                self.getControl( 20 ).setSelected( Translated )
                self.getControl( 19 ).setSelected( False )
                self.getControl( 21 ).setSelected( False )

            elif controlID == 21:
                # CHANGED BUTTON
                filter = ( "", "Changed" )[ Changed ]
                self.setContainer( filter, SelectId )
                self.getControl( 21 ).setSelected( Changed )
                self.getControl( 19 ).setSelected( False )
                self.getControl( 20 ).setSelected( False )

            elif controlID == 22:
                # VIEW AS BUTTON
                self.settings[ "viewmode" ] = ( 1, 0 )[ self.settings[ "viewmode" ] ]
                xbmc.sleep( 50 )
                self.setContainer( filter, SelectId )

            elif controlID == 13:
                # SORT BY BUTTON
                self.settings[ "sortmethod" ] = ( 1, 0 )[ self.settings[ "sortmethod" ] ]
                self.setSortMethodControl()
                self.setContainer( filter, SelectId )

            elif controlID == 14:
                # SORT ASC BUTTON
                self.settings[ "sortorder" ] = ( 1, 0 )[ self.settings[ "sortorder" ] ]
                self.setContainer( filter, SelectId )

            elif controlID == 32:
                # SETTINGS BUTTON
                self.Addon = Addon( AddonId )
                self.Addon.openSettings()
                xbmc.sleep( 10 )
                if self.settings[ "LanguagePath" ] != self.Addon.getSetting( "LanguagePath" ):
                    self.settings[ "LanguagePath" ] = self.Addon.getSetting( "LanguagePath" )
                    self.listitems = []
                self.setContainer( filter, SelectId )

            elif controlID == 33:
                # FIND BUTTON
                default = self.getControl( 33 ).getLabel2()
                kb = xbmc.Keyboard( default, "Find what ...", False )
                kb.doModal()
                if kb.isConfirmed():
                    find_text = kb.getText()
                    #self.getControl( 33 ).setLabel( "Find", label2=find_text )
                    self.setProperty( "FindText", find_text )
                    if find_text:# and find_text != default:
                        for count, li in enumerate( self.listitems ):
                            #l_text = find_text.lower()
                            #match = ( l_text in li.getLabel().lower() ) or ( l_text in li.getLabel2().lower() ) or ( l_text == li.getProperty( "id" ) )
                            #match = match or ( l_text == li.getLabel().lower() ) or ( l_text == li.getLabel2().lower() )
                            #if not match: continue
                            if self.findText( find_text, li ):
                                self.getControl( self.ContainerId ).selectItem( count )
                                self.setFocusId( self.ContainerId )
                                break

            elif controlID == 34:
                # FIND NEXT BUTTON
                find_next = self.getControl( 33 ).getLabel2().encode( "utf-8" )
                pos = self.getControl( self.ContainerId ).getSelectedPosition()
                for count, li in enumerate( self.listitems ):
                    if count <= pos: continue
                    #if find_next in li.getLabel() or find_next == li.getProperty( "id" ):
                    if self.findText( find_next, li ):
                        self.getControl( self.ContainerId ).selectItem( count )
                        break

        except:
            print_exc()

    def findText( self, text, listitem ):
        return re.search( text.lower(), "|".join(
            [ listitem.getLabel(), listitem.getLabel2(), listitem.getProperty( "id" ) ]
            ).lower() )

    def onAction( self, action ):
        if action in [ 9, 10 ]:
            self._close_window()

        elif action == 117:
            try:
                cm = DialogContextMenu( "Translator-DialogContextMenu.xml", CWD, parent=self )
                cm.doModal()
                del cm
            except:
                print_exc()
        else:
            try:
                bcode = action.getButtonCode()
                # keyboard press F3
                if bcode == 127138: self.sendClick( 34 )
                #
            except:
                print_exc()

    def _close_window( self ):
        xbmc.executebuiltin( "ActivateWindow(busydialog)" )
        if self.settings[ "savefolderviews" ]:
            self.Addon.setSetting( "viewmode",   str( self.settings[ "viewmode" ] ) )
            self.Addon.setSetting( "sortmethod", str( self.settings[ "sortmethod" ] ) )
            self.Addon.setSetting( "sortorder",  str( self.settings[ "sortorder" ] ) )
            xbmc.sleep( 10 )

        if self.IsModified:
            # ask for save change
            xbmc.executebuiltin( "Dialog.Close(busydialog)" )
            self._save_change()

        try: del self.language
        except: pass
        self.close()

    def _save_change( self ):
        if xbmcgui.Dialog().yesno( "Confirm file save", "Language file has been changed!", self.language.current_xml, "Do you want save your change?", "" ):
            xbmc.executebuiltin( "ActivateWindow(busydialog)" )
            OK = self.language.save_strings()
            xbmc.executebuiltin( "Dialog.Close(busydialog)" )

            if ( self.DefaultFolderLanguage.rstrip( "/" ) == self.FolderLanguage ) or ( xbmc.translatePath( "special://skin/" ) in xbmc.translatePath( self.FolderLanguage ) ):
                # if default xbmc language file has been changed,
                # set True, XBMC require Restart or reload language
                self.RestartXBMC_ReloadLanguage = OK or self.RestartXBMC_ReloadLanguage



def Main():
    restart_reload = False
    try:
        w = Translator( "Translator-Main.xml", CWD )
        w.doModal()
        restart_reload = w.RestartXBMC_ReloadLanguage
        del w
    except:
        print_exc()
    xbmc.executebuiltin( "Dialog.Close(busydialog)" )

    if restart_reload:
        choices = [ "Restart XBMC", "Reload Language", "Close Dialog" ]
        selected = xbmcgui.Dialog().select( "XBMC language file has been changed!", choices )
        if selected == 0:
            if not UNDER_XBOX:
                xbmc.executebuiltin( "XBMC.Minimize()" )
            xbmc.executebuiltin( "XBMC.RestartApp()" )
            if os.environ.get( "OS", "win32" ) == "win32":
                os.startfile( os.path.join( CWD, "resources", "RestartXBMC", "windows.bat" ) )

        elif selected == 1:
            xbmc.executebuiltin( "ActivateWindow(appearancesettings)" )
            xbmc.sleep( 100 )
            xbmc.executebuiltin( "SetFocus(-99)" )
            xbmc.executebuiltin( "SetFocus(-80)" )

        else:
            xbmcgui.Dialog().ok( "XBMC Translator", "XBMC requires to restart to change your language.", "Or reload language." )



if ( __name__ == "__main__" ):
    Main()
