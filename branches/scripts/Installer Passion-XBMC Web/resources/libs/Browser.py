"""
Browser: this module allows browsing of server content
"""

# Modules general
import os
import sys
from threading import Thread
from traceback import print_exc

# Modules custom
import Item


class ImageQueueElement:
    """ Structure d'un element a mettre dans la FIFO des images a telecharger """
    def __init__( self, filename, updateImage_cb=None, item=None ):
        self.filename       = filename
        self.updateImage_cb = updateImage_cb
        self.item           = item

    def __repr__( self ):
        return "(%s, %s, %s)" % ( self.filename, self.updateImage_cb, self.item )


class Browser:
    """
    This abstract class allow to browse item to download available on the server
    """
    def __init__( self, *args, **kwargs ):
        try:
            self.mainwin  = kwargs[ "mainwin" ]
            self.configManager = self.mainwin.configManager
            self.thumb_size_on_load = self.mainwin.settings[ "thumb_size" ]
        except:
            import CONF
            config = CONF.ReadConfig()
            self.configManager = CONF.configCtrl()
            del CONF
            self.thumb_size_on_load = 512

        # FIFO des images a telecharger
        self.image_queue = []
        self.curCategory = "root"
        
        self.stopUpdateImageThread = False # Flag indiquant si on doit stopper ou non le thread getImagesQueue_thread
        
    def reset( self ):
        """
        Reset the browser (back to start page)
        """
        pass
    
    def close( self ):
        """
        Close browser: i.e close connection, free memory ...
        """
        pass
    
    def getNextList( self, index=0 ):
        """
        Returns the list of item (dictionary) on the server depending on the location we are on the server
        Retrieves list of the items and information about each item
        Other possible name: down
        """
        pass
    
    def getPrevList( self ):
        """
        Returns the list (up) of item (dictionary) on the server depending on the location we are on the server
        Go to previous page/list 
        Other possible name: Up
        """
        pass
    
    def reloadList( self ):
        """
        Reload and returns the current list
        """
        pass
    
    def getContextMenu( self ):
        """
        Returns the list of the commands available via the context menu
        """
        pass
    
    def getInfo( self, itemId ):
        """
        Returns the information about a specific item (dictionnary)
        """
        pass
    
    def _loadData ( self ):
        """
        Load the data for the current page
        """
    
    def sortByDate( self ):
        """
        Returns current list sorted by date
        """
        pass

    def sortByLang( self ):
        """
        Returns current list sorted by language
        """
        pass
    
    def sortByAuthor( self ):
        """
        Returns current list sorted by author
        """
        pass    
    
    def isCat( self, index ):
        """
        Returns True when selected item is a category
        """
        pass
    
    def getInstaller( self, index ):
        """
        Returns an ItemInstaller instance
        """
        pass

    def applyFilter( self ):
        """
        Apply a specific filter in order to get a filtered list of item (specific author, date, ...)
        """
        pass

    def getCurrentCategory(self):
        """
        returns the current category
        """
        return self.curCategory
    
    def update_Images( self ):
        """
        Recupere toutes les image dans la FIFO et met a jour l'appelant via la callBack
        """
        #print "update_Images"
        #print self.image_queue
        if ( len(self.image_queue) > 0 ):
            self.getImagesQueue_thread = Thread( target=self._thread_getImagesQueue )
            self.getImagesQueue_thread.start()

    def cancel_update_Images(self):
        self.stopUpdateImageThread = True
        print "cancel_update_Images: Stopping theard ..."

        # On attend la fin du thread
        self.getImagesQueue_thread.join(10)
        print "cancel_update_Images: Thread STOPPED"
        
         # on vide la liste vide la Queue
        del self.image_queue[ : ]
        
#    def getImage( self, index, updateImage_cb=None, obj2update=None  ):
    def imageUpdateRegister( self, item, updateImage_cb=None, obj2update=None ):
        """
        Register an external graphic object needing to update the picture (listitem, image ...)
        """
#        pass
#        item = self.curList[ index ]
        previewPictureURL   = item['previewpictureurl']
#        previewPictureLocal = item['previewpicture']
#        previewThumbLocal   = item['thumbnail']
        
        if item['image2retrieve'] == True:
            # Telechargement et mise a jour de l'image (thread de separe)
            # Ajout a de l'image a la queue de telechargement
            #self.image_queue.append( ImageQueueElement( previewPictureURL, updateImage_cb, listitem ) )
            self.image_queue.append( ImageQueueElement( previewPictureURL, updateImage_cb=updateImage_cb, item=obj2update  ) )
            #TODO: dynamic update of image (right now image is not updatd in the GUI after download)

#        return previewThumbLocal, previewPictureLocal
       
#    def imageUpdateRegister( self, listItemId, updateImage_cb=None, obj2update=None ):
#        """
#        Register an external graphic object needing to update the picture (listitem, image ...)
#        """
#        previewPictureURL   = self.curList[listItemId]['previewpictureurl']
#        previewPictureLocal = self.curList[listItemId]['previewpicture']
#        previewThumbLocal   = self.curList[listItemId]['thumbnail']
#        if  ( previewPictureURL != 'None' and ( ( previewPictureLocal=="IPX-NotAvailable2.png"  ) or ( previewThumbLocal=="IPX-NotAvailable2.png" ) ) ):
#            # We will download the picture only we we have the url and we currently have a default picture displayed
#            self.image_queue.append( ImageQueueElement(previewPictureURL, updateImage_cb, obj2update ) )
    
    def _thread_getImagesQueue( self ):
        self.stopUpdateImageThread = False
        while ( len( self.image_queue ) > 0 and self.stopUpdateImageThread == False ):
            imageElt = self.image_queue.pop( 0 )
            
            # Download picture and create local Thumbnail
            thumbnail, previewPicture = self._downloadImage( imageElt.filename )
            if ( thumbnail == "" ):
                # Impossible to download picture and/or create thumb
                thumbnail = "IPX-NotAvailable2.png" # Item.THUMB_NOT_AVAILABLE

            # Notifie la callback de mettre a jour l'image
            if imageElt.updateImage_cb:
                try:
                    imageElt.updateImage_cb( thumbnail, imageElt.item )
                except TypeError:
                    print_exc()
                        
        if ( self.stopUpdateImageThread == True):
            print "_thread_getImagesQueue CANCELLED"

    def _downloadImage( self, picname ):
        """
        Download picture from the server, save it, create the thumbnail and return path of it
        ABSTRACT
        """
        pass
    
    
class History:
    """
    Class history save history of webpage browsed
    in the future we can even cache here all the page info including lists
    """
    def __init__(self):
        self.handler        = []
        self.handlerType    = []
        self.titleLabel     = []
        self.current        = - 1
        
    def push(self, title, hdl, hdlType):
        """
        Add a webpage to history
        @param title:
        @param hdl:
        @param hdlType:
        """
        self.handler.append(hdl)
        self.handlerType.append(hdlType)
        self.titleLabel.append(title)
        self.current = self.current + 1
        
    def pop(self):
        """
        Remove a webpage from 
        """
        if self.current >= 0:
            self.handler.pop()
            self.handlerType.pop()
            self.titleLabel.pop()
            self.current = self.current - 1
        else:
            print "history: History already empty!!! - cannot do pop"
            
    def getCurrent(self):
        """
        Returns current page info (index / Handler / Handler Type) on succes
                or "None" if failure (no current page)
        """
        if self.current >= 0:
            return self.titleLabel[self.current],self.handler[self.current], self.handlerType[self.current]
        else:
            return "None", "None", "None"
            
    def getPrevious(self):
        """
        Returns previous page info (index / Handler / Handler Type) on succes
                or "None" if failure (no previous page)
        """
        if (self.current - 1) >= 0:
            return self.titleLabel[(self.current - 1)], self.handler[(self.current - 1)], self.handlerType[(self.current - 1)]
        else:
            return "None", "None", "None"

    def getEntry(self, index):
        """
        Returns an history entry for a specific Index
        @param index: history entry index 
        """
        return self.titleLabel[index], self.handler[index], self.handlerType[index]
        
    def getHistoryTitle(self):
        """
        Returns list ot Titles stored in history
        """
        return self.titleLabel
        
