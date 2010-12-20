
import os
import sys
from traceback import print_exc

import xbmc
import xbmcgui
import xbmcplugin
from xbmcaddon import Addon

# addon constants
__settings__  = Addon( "repository.xbmc.builds" ) # get Addon object
__addonName__ = __settings__.getAddonInfo( "name" ) # get Addon Name
__addonId__   = __settings__.getAddonInfo( "id" ) # get Addon Name


xbmcplugin.setProperty( int( sys.argv[ 1 ] ), "AddonName", __addonName__ )

CONDITION = "[stringcompare(container.property(AddonName),%s)]" % __addonName__


class addonWindow( xbmcgui.Window ):
    def __init__( self, windowId, skin="confluence", **kwargs ):
        self.windowId = windowId
        if skin in xbmc.getSkinDir().lower():
            try:    
                xbmcgui.lock()
                xbmcgui.Window.__init__( self, self.windowId )
                self.controlsId = kwargs.get( "controlsId" )
                self.AddonCategory = xbmc.getInfoLabel( "ListItem.Property(Addon.Name)" )
                if __addonName__ == self.AddonCategory: self.AddonCategory = ""

                if skin == "confluence":
                    self.addAddonInfoList( 550 )
                    self.setAddonControls()
            except:
                print_exc()
            xbmcgui.unlock()

    def addAddonInfoList( self, controlID ):
        # :( skinner, I use Addon Info in plugins :(
        # ok bypass visible condition by skinner :D ;)
        # ok now work with xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="addons" )
        pass
        #try:
        #    AddonInfoListView1 = self.getControl( controlID )
        #    AddonInfoListView1.setVisibleCondition( "[Container.Content(Addons) | stringcompare(container.property(RepoName),%s)]" % __addonName__ )
        #    self.addControl( AddonInfoListView1 )
        #except ReferenceError: pass #Control is already used :)
        #except:
        #    print_exc()

    def setAddonControls( self ):
        labelOption = { "font": "font12caps", "alignment": 5 }#( 0x00000001+0x00000004 ) }
        animation = [ ( 'Visible', 'effect=fade time=300' ), ( 'Hidden', 'effect=fade time=300' ) ]
        anim_cat  = animation + [ ( 'WindowClose', 'effect=slide end=-1000,0 time=400 tween=quadratic easing=out' ), ( 'WindowOpen', 'effect=slide start=-1000,0 time=400 tween=quadratic easing=out' ) ]
        anim_head = anim_cat#animation + [ ( 'WindowClose', 'effect=slide end=-1000,0 time=400 tween=quadratic easing=out' ), ( 'WindowOpen', 'effect=slide start=-1000,0 time=400 tween=quadratic easing=out' ) ]

        try: bg_addon_category = self.getControl( 3001 )
        except:
            bg_addon_category = xbmcgui.ControlImage( 520, 0, 300, 35, "header.png" )
            self.addControl( bg_addon_category )
            bg_addon_category = self.getControl( bg_addon_category.getId() )

        try: addon_category = self.getControl( 3002 )
        except:
            addon_category = xbmcgui.ControlLabel( 790, 0, 200, 28, self.AddonCategory, **labelOption )
            self.addControl( addon_category )
            addon_category = self.getControl( addon_category.getId() )

        addon_category.setLabel( self.AddonCategory )
        addon_category.setVisibleCondition( CONDITION )
        bg_addon_category.setVisibleCondition( "[Control.IsVisible(3002) + !stringcompare(control.getlabel(3002),)]" )
        bg_addon_category.setAnimations( anim_cat )
        addon_category.setAnimations( anim_cat )

        try: bg_addon_name = self.getControl( 3003 )
        except:
            bg_addon_name = xbmcgui.ControlImage( 240, 0, 350, 35, "header.png" )
            self.addControl( bg_addon_name )
            bg_addon_name = self.getControl( bg_addon_name.getId() )

        try: addon_name = self.getControl( 3004 )
        except:
            addon_name = xbmcgui.ControlLabel( 555, 0, 250, 28, __addonName__, **labelOption )
            self.addControl( addon_name )
            addon_name = self.getControl( addon_name.getId() )

        addon_name.setLabel( __addonName__ )
        addon_name.setVisibleCondition( CONDITION )
        bg_addon_name.setVisibleCondition( "[Control.IsVisible(3004) + !stringcompare(control.getlabel(3004),)]" )
        bg_addon_name.setAnimations( anim_head )
        addon_name.setAnimations( anim_head )

        #try: bg = self.getControl( 3005 )
        #except:
        #    bg = xbmcgui.ControlImage( 60, 0, 250, 35, "header.png" )
        #    self.addControl( bg )
        #try: addon_name = self.getControl( 3006 )
        #except:
        #    addon_name = xbmcgui.ControlLabel( 280, 0, 180, 28, __addonName__, **labelOption )
        #    self.addControl( addon_name )
