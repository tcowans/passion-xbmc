# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcplugin

import os.path, re, htmlentitydefs
import urllib
import sys
from traceback import print_exc

def _addDir(  name, name2="", url="", iconimage="DefaultFolder.png", itemInfoType="Video", itemInfoLabels=None, c_items=None, totalItems=0 ):
    #u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    lstItem=xbmcgui.ListItem( label=name, label2=name2, iconImage=iconimage, thumbnailImage=iconimage )
    
    if c_items : 
        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("_addDir","l 16"))  
        lstItem.addContextMenuItems( c_items, replaceItems=True )
        
    if itemInfoLabels:
        iLabels = itemInfoLabels
    else:
        iLabels = { "Title": name }
        
    lstItem.setInfo( type=itemInfoType, infoLabels=iLabels )
    ok=xbmcplugin.addDirectoryItem( handle=int( sys.argv[1] ), url=url, listitem=lstItem, isFolder=True, totalItems=totalItems )        
    return ok

def _end_of_directory(  OK, update=False ):
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK, updateListing=update )#, cacheToDisc=True )#updateListing = True,

def _add_sort_methods(  OK ):
    if ( OK ):
        try:
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_TITLE )
            #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )
            #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
            #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_STUDIO )
        except Exception,msg:
            xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("ERROR _add_sort_methods ",msg))  
            print ("Error _add_sort_methods")
            print_exc()            
    _end_of_directory( OK )

def _coloring(  text , color , colorword ):
    if color == "red": color="FFFF0000"
    if color == "green": color="ff00FF00"
    if color == "yellow": color="ffFFFF00"
    colored_text = text.replace( colorword , "[COLOR=%s]%s[/COLOR]" % ( color , colorword ) )
    return colored_text

def verifrep( folder ):
    try:
        #print("verifrep check if directory: " + folder + " exists")
        if not os.path.exists( folder ):
            print( "verifrep Impossible to find the directory - trying to create the directory: " + folder )
            os.makedirs( folder )
    except Exception, msg:
        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("Exception while creating folder  ",msg))  
        print ("Error verifrep")
        print_exc()         
        
def _parse_params( ):
    """
    Parses Plugin parameters and returns it as a dictionary
    """
    paramDic={}
    # Parameters are on the 3rd arg passed to the script
    paramStr=sys.argv[2]
    print paramStr
    if len(paramStr)>1:
        paramStr = paramStr.replace('?','')
        
        # Ignore last char if it is a '/'
        if (paramStr[len(paramStr)-1]=='/'):
            paramStr=paramStr[0:len(paramStr)-2]
            
        # Processing each parameter splited on  '&'   
        for param in paramStr.split("&"):
            try:
                # Spliting couple key/value
                key,value=param.split("=")
            except:
                key=param
                value=""
                
            key = urllib.unquote_plus(key)
            value = urllib.unquote_plus(value)
            
            # Filling dictionnary
            paramDic[key]=value
    print paramDic
    return paramDic

def _addLink(  name, name2="", url="", iconimage="DefaultVideo.png", itemInfoType="Video", itemInfoLabels=None, c_items=None, totalItems=0 ):
    ok=True
    print iconimage
    lstItem=xbmcgui.ListItem( label=name, label2=name2, iconImage=iconimage, thumbnailImage=iconimage )
    if c_items : 
        lstItem.addContextMenuItems( c_items, replaceItems=True )
        
    if itemInfoLabels:
        iLabels = itemInfoLabels
    else:
        iLabels = { "Title": name }
        
    lstItem.setInfo( type=itemInfoType, infoLabels=iLabels )
    lstItem.setProperty('IsPlayable', 'true')
    ok=xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]), url=url, listitem=lstItem, totalItems=totalItems )
    return ok

def _create_param_url( paramsDic, quote_plus=False):
    """
    Create an plugin URL based on the key/value passed in a dictionary
    """
    url = sys.argv[ 0 ]
    sep = '?'
    print paramsDic
    try:
        for param in paramsDic:
            #TODO: solve error on name with non ascii char (generate exception)
            if quote_plus:
                url = url + sep + urllib.quote_plus( param ) + '=' + urllib.quote_plus( paramsDic[param] )
            else:
                url = url + sep + param + '=' + paramsDic[param]
                
            sep = '&'
    except Exception,msg:
        print_exc()
        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("ERROR _create_param_url ",msg))  
        url = None
    return url

def _add_to_index(context, name):
    paramsAddons = {}
    paramsAddons[context] = "True"
    url = _create_param_url( paramsAddons )	
    _addDir( name=name, url=url )

def strip_html(text):
    def fixup(m):
        text = m.group(0).encode('utf-8')
        text = text.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&").replace("&#39;","\\").replace("&quot;","\"").replace("&szlig;","ß").replace("&ndash;","-")
        text = text.replace("&Auml;","Ä").replace("&Uuml;","Ü").replace("&Ouml;","Ö").replace("&auml;","ä").replace("&uuml;","ü").replace("&ouml;","ö")
        if text[:1] == "<":
            return "" # ignore tags
        if text[:2] == "&#":
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        elif text[:1] == "&":
            import htmlentitydefs
            entity = htmlentitydefs.entitydefs.get(text[1:-1])
            if entity:
                if entity[:2] == "&#":
                    try:
                        return unichr(int(entity[2:-1]))
                    except ValueError:
                        pass
                else:
                    return unicode(entity, "iso-8859-1")
        return text # leave as is
    return re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)
