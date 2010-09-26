__script__       = "Genre Editor"
__author__       = "GMib"
__url__          = ""
__svn_url__      = ""
__credits__      = ""
__platform__     = "xbmc media center, [LINUX, OS X, WIN32, XBOX]"
__date__         = "20-08-2010"
__version__      = "0.0.2"
__svn_revision__  = "$Revision: 000 $"
__XBMC_Revision__ = "30000" #XBMC Babylon
__useragent__ = "Edit Movie %s" % __version__

import urllib
import os
import re
from traceback import print_exc
import xbmc
import xbmcgui
import shutil

SOURCEPATH = os.getcwd()
RESOURCES_PATH = os.path.join( SOURCEPATH , "resources" )
sys.path.append( os.path.join( RESOURCES_PATH, "lib" ) )

def m(txt):
        xbmcgui.Dialog().ok("Msg" ,str(txt) )
        
class Edit(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs ):
        self.ex = 0
    
    def onFocus( self, controlId ):
        pass  
        
    def onInit( self ):
        try:
            self.title = sys.argv[1]
            self.file = sys.argv[2]
        except:
            xbmcgui.Dialog().ok("Error" ,"Arguments missing!")
            self.close()
            return
        self.visMov = xbmc.getCondVisibility('container.content(movies)')
        self.visTv = xbmc.getCondVisibility('container.content(tvshows) | container.content(episodes) | container.content(seasons)')
        if self.visMov:
            self.mode = "movie"
        elif self.visTv:
            self.mode = "tvshow"
        else:
            xbmcgui.Dialog().ok("Error" ,"Run only on movie or tvshow container!")
            self.close()
            return
            
        if self.mode == "movie":
            sql_data = 'SELECT movie.idMovie, strFilename FROM movie,files WHERE movie.idFile=files.idFile AND strFilename=\"%s\" AND movie.c00=\"%s\"' % (self.file, self.title)
        else:
            sql_data = 'SELECT tvshow.idShow, tvshow.c00 FROM tvshow WHERE tvshow.c00=\"%s\"' % (self.title)
        xml_data = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % urllib.quote_plus( sql_data ), )
        match = re.findall( "<field>(.*?)</field><field>(.*?)</field>", xml_data, re.DOTALL )
        try:
            self.idfilm = match[0][0]
        except:
            xbmcgui.Dialog().ok("Error" ,"Movie not found in DB!")
            self.idfilm = 0
        if self.idfilm == 0:
            self.close()
            return
        self.getGenres()
        self.getMovieGenres()
        self.displayGenre()
            
    def displayGenre( self ):
        self.listGenre = self.getControl( 120 )
        for g in self.genres:
            if g[0] in self.movieGenres:
                listitem = xbmcgui.ListItem(g[1], g[0])
                listitem.setIconImage("GenreEditorSel.png")
            else:
                listitem = xbmcgui.ListItem(g[1], g[0])
                listitem.setIconImage("")
            self.listGenre.addItem( listitem )
        
    def getMovieGenres(self):
        if self.mode == "movie":
            sql_data = 'SELECT idGenre FROM genrelinkmovie WHERE genrelinkmovie.idMovie=%s' % (self.idfilm)
        else:
            sql_data = 'SELECT idGenre FROM genrelinktvshow WHERE genrelinktvshow.idShow=%s' % (self.idfilm)
        xml_data = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % urllib.quote_plus( sql_data ), )
        self.movieGenres = re.findall( "<field>(.*?)</field>", xml_data, re.DOTALL ) # id of movie's genre
        
        
    def getGenres(self):
        sql_data = 'SELECT idGenre, strGenre FROM genre ORDER BY strGenre'
        xml_data = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % urllib.quote_plus( sql_data ), )
        self.genres = re.findall( "<field>(.*?)</field><field>(.*?)</field>", xml_data, re.DOTALL )
        #genre[0][0]:id 1er genre, genre[0][1]:nom 1er genre
       
    def onClick( self, controlId ):
        if controlId == 120: #List genre
            idSelGenre = self.genres[self.listGenre.getSelectedPosition()][0]
            if idSelGenre in self.movieGenres: #remove genre
                self.movieGenres.remove(idSelGenre)
                self.listGenre.getSelectedItem().setIconImage("")
            else:
                self.movieGenres.append(idSelGenre)
                self.listGenre.getSelectedItem().setIconImage("GenreEditorSel.png")
        
        if controlId == 23: #Cancel button
            if xbmcgui.Dialog().yesno('Confirm', 'If you choose yes, informations will not be save',"Are you sure ?"):
                self.close()
            
        if controlId == 22: #save button
            self.saving()

        if controlId == 24: #Add button
            kb = xbmc.Keyboard('', 'Enter desired new genre', False)
            kb.doModal()
            if (kb.isConfirmed()):
                text = kb.getText()
                sql_data = 'SELECT idGenre FROM genre WHERE strGenre=\"%s\"' % (text)
                xml_data = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % urllib.quote_plus( sql_data ), )
                if xml_data:
                    xbmcgui.Dialog().ok("Error" ,"Genre already exist!")
                else:
                    sql_data = 'INSERT INTO genre ("strGenre") VALUES (\"%s\")' % (text)
                    xml_data = xbmc.executehttpapi( "ExecVideoDatabase(%s)" % urllib.quote_plus( sql_data ), ) 
                    self.listGenre.reset()
                    self.getGenres()
                    self.displayGenre()
        if controlId == 25: #Del button
            idSelGenre = self.genres[self.listGenre.getSelectedPosition()][0]
            genreSel = self.listGenre.getSelectedItem().getLabel()
            sql_data = 'SELECT count(*) FROM genrelinkmovie WHERE idGenre=%s' % (idSelGenre)
            xml_data = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % urllib.quote_plus( sql_data ), )
            nbmov = re.findall( "<field>(.*?)</field>", xml_data, re.DOTALL )[0] # 
            
            sql_data = 'SELECT count(*) FROM genrelinktvshow WHERE idGenre=%s' % (idSelGenre)
            xml_data = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % urllib.quote_plus( sql_data ), )
            nbtv = re.findall( "<field>(.*?)</field>", xml_data, re.DOTALL )[0] # 
            
            sql_data = 'SELECT count(*) FROM genrelinkmusicvideo WHERE idGenre=%s' % (idSelGenre)
            xml_data = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % urllib.quote_plus( sql_data ), )
            nbmus = re.findall( "<field>(.*?)</field>", xml_data, re.DOTALL )[0] # 
            
            line1 = 'Delete ' + genreSel + ' genre of DB and of' 
            line2 = nbmov + ' movie(s), ' + nbtv + ' TvShow(s) and ' + nbmus + ' musicvideo(s)'
            line3 = 'who use it ?'
            dialog = xbmcgui.Dialog().yesno('Confirm', line1, line2, line3 )
            if dialog:
                sql_data = 'DELETE FROM genrelinkmovie WHERE idGenre=%s' % (idSelGenre)
                xml_data = xbmc.executehttpapi( "ExecVideoDatabase(%s)" % urllib.quote_plus( sql_data ), )
                sql_data = 'DELETE FROM genrelinktvshow WHERE idGenre=%s' % (idSelGenre)
                xml_data = xbmc.executehttpapi( "ExecVideoDatabase(%s)" % urllib.quote_plus( sql_data ), )
                sql_data = 'DELETE FROM genrelinkmusicvideo WHERE idGenre=%s' % (idSelGenre)
                xml_data = xbmc.executehttpapi( "ExecVideoDatabase(%s)" % urllib.quote_plus( sql_data ), )
                sql_data = 'DELETE FROM genre WHERE idGenre=%s' % (idSelGenre)
                xml_data = xbmc.executehttpapi( "ExecVideoDatabase(%s)" % urllib.quote_plus( sql_data ), ) 
                self.listGenre.reset()
                self.getGenres()
                self.displayGenre()
            
    def saving(self):
        listIdGenres = []
        listStrGenres = []
        for e in self.genres:
            listIdGenres.append(e[0])
            listStrGenres.append(e[1])
        if self.mode == "movie":
            sql_data = 'DELETE FROM genrelinkmovie WHERE idMovie=\"%s\"' % (self.idfilm)
        else:
            sql_data = 'DELETE FROM genrelinktvshow WHERE idShow=\"%s\"' % (self.idfilm)
        xml_data = xbmc.executehttpapi( "ExecVideoDatabase(%s)" % urllib.quote_plus( sql_data ), )
        lg = []
        for g in self.movieGenres:
            lg.append(listStrGenres[listIdGenres.index(g)])
            if self.mode == "movie":
                sql_data = 'INSERT INTO genrelinkmovie ("idGenre","idMovie") VALUES (%s,%s)' % (g, self.idfilm)
            else:
                sql_data = 'INSERT INTO genrelinktvshow ("idGenre","idShow") VALUES (%s,%s)' % (g, self.idfilm)
            xml_data = xbmc.executehttpapi( "ExecVideoDatabase(%s)" % urllib.quote_plus( sql_data ), )
        self.strgenre = " / ".join(lg)
        if self.mode == "movie":
            sql_data = 'UPDATE movie SET c14=\"%s\" WHERE idMovie=%s' % (self.strgenre, self.idfilm)
        else:
            sql_data = 'UPDATE tvshow SET c08=\"%s\" WHERE idShow=%s' % (self.strgenre, self.idfilm)
        xml_data = xbmc.executehttpapi( "ExecVideoDatabase(%s)" % urllib.quote_plus( sql_data ), )
        self.ex = 1
        self.close()


if ( __name__ == "__main__" ): 
    
    
    ui = Edit( "Script-GenreEditor.xml", os.getcwd(), "Default" )
    ui.doModal()
    ex = ui.ex
    del ui
    if ex:
        wid = xbmcgui.getCurrentWindowDialogId()
        if wid == 12003:
            xbmc.executebuiltin('Dialog.Close(2003)')
            xbmc.sleep(600)
        xbmc.executebuiltin( 'Container.Refresh' )
        if wid == 12003:
            xbmc.executebuiltin( "Action(Info)")
    
    #xbmc.executebuiltin('ActivateWindow(2003)')
    
    