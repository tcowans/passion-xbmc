
import urllib,sys,os
import xbmcplugin,xbmcgui,xbmc

RootDir = os.getcwd().replace(';','')
def downloadimage(image,url):
    #PicturePath = get_settings()
    PicturePath = os.path.join(RootDir, 'Cache')
    #if PicturePath == 'default':
        #PicturePath = os.path.join(RootDir, 'Cache')
    
    if not os.path.isdir(PicturePath):
        os.makedirs(PicturePath) #,mode=0777)
    LocalPicture = os.path.join(PicturePath, image)
    
    if not os.path.isfile(LocalPicture):
        f=open(LocalPicture,"wb")
        f.write(urllib.urlopen(url).read())
        f.close()
    
    return LocalPicture
    
stringparams2 = sys.argv[2]
print 'STRING PARAMS = %s'%stringparams2
#try:
    #if stringparams[0]=="?":
        #stringparams=stringparams[1:]
#except:
    #pass
#parametres={}
#for param in stringparams.split("&"):
    #try:
        #cle,valeur=param.split("=")
    #except:
        #cle=param
        #valeur=""
    #parametres[cle]=valeur

#if "jpg" in parametres.keys():

    #show_icones(parametres["cat"].replace('cat=',''))
    ###paramètre 'cat' : on liste l'image correspondante
 
    
#else:
    ##pas de paramètres : début du plugin
    #show_icones(0)
    
