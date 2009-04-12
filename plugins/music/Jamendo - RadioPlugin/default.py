import xbmc, xbmcgui, xbmcplugin
import simplejson as json
import urllib

urllib.urlcleanup()


def make_get2urls(fields, unit, format, joins=None,params=None):
    base_url = 'http://api.jamendo.com/get2/'
    
    get2_fields = '+'.join(fields) 
    query = '/'.join([get2_fields,unit,format])
    
    if joins != None:
        query = '/'.join([query,joins])
    if params != None:
        params = urllib.urlencode(params)
        query = '/?'.join([query,params])

    complete_url = base_url + query
    return complete_url    
    

def get_radio_list():
    fields = ['id','idstr','image']
    unit = 'radio'
    format = 'json'
    file = urllib.urlopen(make_get2urls(fields,unit,format)).read()
    radiolist = json.loads(str(file))       
    return radiolist

def get_radio_playlist(radio_id):
    fields = ['stream',]
    unit = 'track'
    format = 'm3u'
    joins = 'radio_track_inradioplaylist'
    params=({'order':'numradio_asc','radio_id':radio_id})
    m3u=make_get2urls(fields,unit,format,joins,params)
    return m3u

def showradios():
    ok = True
    radio_list=get_radio_list()
    for index in range(len(radio_list)):
        
            url=get_radio_playlist(radio_list[index]['id'])
        
            RadioName = radio_list[index]['idstr']  
            IconeImage = radio_list[index]['image']
            
            
            #On affiche la liste des radios
            item=xbmcgui.ListItem(RadioName,iconImage=IconeImage,thumbnailImage=IconeImage)
            
            #On ajoute les boutons au menu contextuel
            #Enregistrer..
            #c_items = [ ( _(30003), 'XBMC.RunPlugin(%s?download_path=%s)' % ( sys.argv[ 0 ], preparesaving(dico['image'][indice],PictureName)) ) ]
            ##Enregistrer sous...
            #c_items += [ ( _(30004), 'XBMC.RunPlugin(%s?download_as=%s)' % ( sys.argv[ 0 ], preparesaving(dico['image'][indice],PictureName)) ) ]
            #item.addContextMenuItems( c_items)

            ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=False,totalItems=len(radio_list)) 

    return ok

print "PLUGIN JAMENDO"
showradios()

xbmcplugin.endOfDirectory(int(sys.argv[1]))

    


