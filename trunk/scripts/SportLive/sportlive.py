# -*- coding: cp1252 -*-

# script constants
__script__       = "Sportlive"
__author__       = "Ppic"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/scripts/"
__credits__      = "Team XBMC passion, http://passion-xbmc.org/developpement-python/%28script%29-sporlive-display/"
__platform__     = "xbmc media center, [LINUX, OS X, WIN32, XBOX]"
__date__         = "22-02-2009"
__version__      = "1.5"
__svn_revision__  = "$Revision$".replace( "Revision", "" ).strip( "$: " )
__XBMC_Revision__ = "20000" #XBMC Babylon
__useragent__    = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.6"


import urllib
import re
import os
import time
import xbmc
import xbmcgui
from traceback import print_exc

BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
img_path = os.path.join( os.getcwd() , "resources" , "images" )
flag_list = {}
filterfile = os.path.join( os.getcwd() , "resources" , "filter" )
import mydialog
import MyFont
import display

XBMC_SETTINGS = xbmc.Settings( os.getcwd() )

process = os.path.join( BASE_RESOURCE_PATH , "sportlive.pid")
print BASE_RESOURCE_PATH
##if os.path.exists(process):
##    if xbmcgui.Dialog().yesno("Sportlive est déjà en cours", "Voulez-vous stopper la surveillance?" ):
##        os.remove(process)        
##    print "sportlive déja en cours, arreter?"
##else: file( process , "w" ).write( "" )

MyFont.addFont( "sportlive13" , "sportlive.ttf" , "20" )
MyFont.addFont( "sportlive24" , "sportlive.ttf" , "24" )
MyFont.addFont( "sportlive45" , "sportlive.ttf" , "45" )


#coloration texte:
def coloring( text , color , colorword ):
    if color == "red": color="FFFF0000"
    if color == "green": color="ff00FF00"
    if color == "yellow": color="ffFFFF00"
    colored_text = text.replace( colorword , "[COLOR=%s]%s[/COLOR]" % ( color , colorword ) )
    return colored_text

def get_html_source( url ):
    """ fetch the html source """
    class AppURLopener(urllib.FancyURLopener):
        version = __useragent__
    urllib._urlopener = AppURLopener()

    try:
        if os.path.isfile( url ): sock = open( url, "r" )
        else:
            urllib.urlcleanup()
            sock = urllib.urlopen( url )

        htmlsource = sock.read()
        sock.close()
        return htmlsource
    except:
        print_exc()
        print "impossible d'ouvrir la page %s" % url
        return ""

    
class Sportsfr:
    def __init__( self ):
        self.site_url="http://www.sports.fr/"
        self.tempfile = os.path.join( os.getcwd() , "resources" , "sportsfr.temp" )

    def save_match( self , txt ):
        file( self.tempfile , "w" ).write( repr( txt ) )

    def get_current_match( self ):
        all_live=[]
        txt = get_html_source( self.site_url )
        
        try: livescore=re.compile( '<div id="livescore">(.*)</div><!-- /livescore -->', re.DOTALL ).findall( txt )[0]
        except:
            print_exc()
            txt = get_html_source( self.site_url )
            livescore=re.compile( '<div id="livescore">(.*)</div><!-- /livescore -->', re.DOTALL ).findall( txt )[0]
            
        count=0
        for balise in  re.compile( "<li class='live'>(.*?)</li>", re.DOTALL ).findall( livescore ):
            live={}
			
            count = count + 1
            #print count
            #print balise
            try:live['url']=re.findall( "<a href='(.*?)'>", balise )[0]
            except:print_exc()
            try:live['sport']=live['url'].split("/")[1]
            except:print_exc()

            try:
                if live['url'] == "/nfl/directs/mc/index.html" : multiplex = True
                elif live['url'].split("/")[5] == "mtpx" : multiplex = True
                elif live['url'].split("/")[5] == "mc" : multiplex = True
		else: multiplex = False
            except:
                print "error in finding multiplex"
                multiplex = False
            print "url: %s" % live['url']
            print "multiplex: %s" % multiplex

            if not multiplex:
                if live['sport'] in ( "nba" , "football" , "rugby" , "nfl" , "Handball" , "basket" , "nhl" ):
                    print "nba,basket,foot,rugby,nhl"
                    try:live['country']=live['url'].split("/")[4]
                    except:pass
                    if live['sport'] == "nfl" or live['sport'] == "nba" :live['country']="US"
                    try:live['start']=re.findall( "<i class='i2'>(.*?)</i>", balise )[0].strip( " " )
                    except:print_exc()
                    try:live['part']=re.findall( "<i class='i1'>(.*?)</i>", balise )[0].strip( " " )
                    except:print_exc()
                    try:live['A_name']=re.findall( "<i class='i3'>(.*?)</i>", balise )[0].strip( " " )
                    except:print_exc()
                    try:live['A_score']=re.findall( "<i class='i4'>(.*?)</i>", balise )[0].strip( " " )
                    except:print_exc()
                    try:live['B_name']=re.findall( "<i class='i3'>(.*?)</i>", balise )[1].strip( " " )
                    except:print_exc()
                    try:live['B_score']=re.findall( "<i class='i4'>(.*?)</i>", balise )[1].strip( " " )
                    except:print_exc()
                    all_live.append(live)
                    

                elif live['sport'] in ( "f1" , "moto"):
                    #print "formule1"
                    try:live['start']=re.findall( "<i class='i2'>(.*?)</i>", balise )[0]
                    except:print_exc()
                    try:live['part']=re.findall( "<i class='i1'>(.*?)</i>", balise )[0]
                    except:print_exc()
                    try:live['pilote1']=re.findall( "<i class='i3'>(.*?)</i>", balise )[0]
                    except:print_exc()
                    try:live['pilote2']=re.findall( "<i class='i3'>(.*?)</i>", balise )[1]
                    except:print_exc()
                    try:live['pilote3']=re.findall( "<i class='i3'>(.*?)</i>", balise )[2]
                    except:print_exc()
                    try:live['pilote4']=re.findall( "<i class='i3'>(.*?)</i>", balise )[3]
                    except:print_exc()
                    try:live['pilote5']=re.findall( "<i class='i3'>(.*?)</i>", balise )[4]
                    except:print_exc()

                elif live['sport'] == "tennis":
                    #print "tennis"
                    try:live['country']=live['url'].split("/")[3].strip( " " )
                    except:print_exc()
                    try:live['start']= ""
                    except:print_exc()
                    try:live['A_name']=re.findall( "<i class='i3'>(.*?)</i>", balise )[0].strip( " " )
                    except:print_exc()
                    try:live['B_name']=re.findall( "<i class='i3'>(.*?)</i>", balise )[1].strip( " " )
                    except:print_exc()
                    try:live['A_score']=re.findall( "<i class='i4'>(.*?)</i>", balise )[0].replace( "<b>" , "" ).replace( "</b>" , "/" ).strip("/")
                    except:print_exc()
                    try:live['B_score']=re.findall( "<i class='i4'>(.*?)</i>", balise )[1].replace( "<b>" , "" ).replace( "</b>" , "/" ).strip("/")
                    except:print_exc()
                    try:live['part']=""
                    except:print_exc()
                    all_live.append(live)

                    
                else:
                    print "other type"
                    try:live['start']=re.findall( "<i class='i2'>(.*?)</i>", balise )[0]
                    except:print_exc()
                    try:live['part']=re.findall( "<i class='i1'>(.*?)</i>", balise )[0]
                    except:print_exc()
                    try:live['A_name']=re.findall( "<i class='i3'>(.*?)</i>", balise )[0]
                    except:print_exc()
                    try:live['A_score']=re.findall( "<i class='i4'>(.*?)</i>", balise )[0]
                    except:print_exc()
                    try:live['B_name']=re.findall( "<i class='i3'>(.*?)</i>", balise )[1]
                    except:print_exc()
                    try:live['B_score']=re.findall( "<i class='i4'>(.*?)</i>", balise )[1]
                    except:print_exc()
             
        #print count        
        return all_live
    
    def get_last_changes(self):
        txt = self.get_current_match()
        try:old_score = eval( file( self.tempfile , "r" ).read() )
        except:
            self.save_match(txt)
            print "pas de références"
            return "pas de références"
        
        #print test
        #print old_score
        if txt != old_score:
            print "structure change"
            self.save_match(txt)
            all_change=[]
            for new   in txt :
                
                for old in old_score:
                    change = new
                    
                    if new['sport'] == old['sport'] and new['A_name'].strip(" *") == old['A_name'].strip(" *") and new['B_name'].strip(" *") == old['B_name'].strip(" *"):
                        change["diff"]=False
                        if new['A_score'] != old['A_score']:
                            print "changement %s %s X %s vers %s" % ( new['sport'] , new['A_name'] , old['A_score'] , new['A_score'] )
                            change["diff"]=True
                            change["A"]=True
                        if new['B_score'] != old['B_score']:
                            print "changement %s %s X %s vers %s" % ( new['sport'] , new['B_name'] , old['B_score'] , new['B_score'])
                            change["diff"]=True
                            change["B"]=True
                        
                            
                            
    ##                        print "pas de changement %s %s %s" % ( new['sport'] , new['A_name'] , new['B_name'] )
                if not "diff" in change: change["diff"] = False
                if "diff" in change:
                
                    if change["diff"]==False: print "1 no score change diff %s " % change["diff"]
                    else : print "score change"
                    #print change
                    all_change.append(change)
                else:
                    print_exc()
                    print "2 no score change "
                
            return all_change
        else:
            #print "no structure change"
            return False

def print_all_stats(txt):
    for affich in txt:
        #print txt
        try:
            if affich["diff"]: affich['sport']= "*%s" % affich['sport']
        except:pass
        print "%s %s | %s %s - %s %s  -  %s" % ( affich['sport'] , affich['country'] , affich['A_name'] , affich['A_score'] , affich['B_score'] , affich['B_name'] , affich['part'] )

def check_filter(update):
    user_filter = eval( file( filterfile , "r" ).read() )
    #print "update:%s" % update
    #print "filtre:%s" % user_filter
    for line in user_filter:
        if line['sport'] == update['sport'] and line['A_name'] == update['A_name'].strip(" *") and line['B_name'] == update['B_name'].strip(" *") : return True
    return False

def watcher():
    while os.path.exists(process):
        print eval( file( filterfile , "r" ).read() )
        if eval( file( filterfile , "r" ).read() ) == []:
            print "no filters, stopping..."
            os.remove(process)
            break

        #test = sportsfr.get_current_match()

        #save_stats(test)
        result= sportsfr.get_last_changes()
        if result != "pas de r‚f‚rences" and result != False:
            #os.system('cls')
            #print_all_stat(result)
            all_update = []
            for update in result:
                #print "filtered: %s" % check_filter(update)
                if update['diff'] and check_filter(update):
                    #print update
                    all_update.append(update)
                    if int(XBMC_SETTINGS.getSetting( "visualisation" )) == 0:
                        print "%s %s | %s  %s - %s  %s" % ( update['sport'] , update['country'] , update['A_name'] , update['A_score'] , update['B_score'] , update['B_name'] )
                        if "A" in update and "B" in update or update['sport'] == "tennis":
                            print "both scored or tennis"
                            try:img = os.path.join ( img_path , update['sport'] , "default.png" )
                            except:print "no image for %s" % update['B_name']
                            B_name = coloring( update['B_name'] , "yellow" , update['B_name'] )
                            A_name = coloring( update['A_name'] , "yellow" , update['A_name'] )
                        elif "A" in update:
                            print "A"
                            try:img = os.path.join ( img_path , update['sport'] , "%s.png" % update['A_name'] )
                            except: print "no image for %s" % update['A_name']
                            A_name = coloring( update['A_name'] , "green" , update['A_name'] )
                            B_name = coloring( update['B_name'] , "red" , update['B_name'] )
                        elif "B" in update:
                            print "B"
                            try:img = os.path.join ( img_path , update['sport'] , "%s.png" % update['B_name'] )
                            except:print "no image for %s" % update['B_name']
                            B_name = coloring( update['B_name'] , "green" , update['B_name'] )
                            A_name = coloring( update['A_name'] , "red" , update['A_name'] )
                        

                        lign2 = ("%s %s - %s" % ( update['sport'] , update['country'] , update['part'] )).strip( "- ")
                        lign1 = "%s %s - %s %s" % ( A_name , update['A_score'] , update['B_score'] , B_name )
                        xbmc.executebuiltin("XBMC.Notification(%s,%s,5000,%s)"%(lign1,lign2,img))
                        time.sleep(3)
            if int(XBMC_SETTINGS.getSetting( "visualisation" )) == 1: display.display( all_update )
                    
                         
        if os.path.exists(process):time.sleep(15)
        if os.path.exists(process):time.sleep(10)

if os.path.exists(process):
    sportsfr = Sportsfr()        
    match_list = sportsfr.get_current_match()
    sportsfr.save_match( match_list )
    mydialog.MyDialog()
    print_all_stats(match_list)
    try:watcher()
    except: print_exc()

##try:old_score = eval( file( "sportfr.temp", "r" ).read() )
##except:
##    save_stats(test)
##    print "pas de old"
##
##try:
##    if test != old_score:
##        os.system('cls')
##        print_all_stat(test)
##        save_stats(test)
##    else:
##        print "*"
##except:print "pas de compare"
##    

#print test


