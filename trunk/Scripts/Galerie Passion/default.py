# -*- coding: cp1252 -*-
#############################
# Galerie Passion           #
#############################

#
# import des librairies
#
import urllib,re,sys,os
import ConfigParser
import xbmcplugin,xbmcgui,xbmc



class passiongallerie:
    def __init__(self):
        # état des variables initiales
        self.BaseUrl = "http://passion-xbmc.org"
        self.home = os.getcwd().replace(';','')
        self.cachedir = os.path.join(self.home,'cache')
        self.picturedir = os.path.join(self.home,'images')
        
        #initialisation du fichier de config pour stocker les couples url / nom de l'image entre deux tours de plugin
        self.fichier = os.path.join(self.home, "conf.cfg")
        self.ConfParser = ConfigParser.ConfigParser()
        self.ConfParser.read(self.fichier)
        
        urllib.urlcleanup()
        
    def get_galerie(self):
        #on récupère la page de base
        html = urllib.urlopen(self.BaseUrl + "/gallery/?cat=51").read()
        #on parse pour trouver toutes les images
        exp=re.compile(r'<td align="center">([^>]+?)<br /><a href="(http://passion-xbmc\.org/gallery/\?sa=view;id=\d+)"><img src="(http://passion-xbmc\.org/gallery/\d+/thumb[_\d]+\.jpg)" /></a>')
        thumbinfos=exp.findall(html)
        return thumbinfos


    def get_icone(self,icone,iconeURL):
        #Télécharge les icones de la galerie
        icone = 'thumb_' + icone
        self.localicone = os.path.join(self.cachedir, icone)
        f=open(self.localicone,"wb")
        f.write(urllib.urlopen(iconeURL).read())
        f.close()


    def show_icones(self):
        ok=True
        for self.PictureName, self.urlPic, self.urlThumb in self.get_galerie():
            #Ajoute un couple Picturename / url dans le fichier de config
            self.ConfParser.set('Dictionnaire', self.PictureName, self.urlThumb) 
            self.get_icone(self.PictureName, self.urlThumb)
            
            #On passe en parametre le nom de l'image
            url=sys.argv[0]+"?icone="+urllib.quote_plus(self.PictureName)
            print url

            #On affiche la liste des icones de la galerie
            item=xbmcgui.ListItem(self.PictureName,iconImage=self.localicone,thumbnailImage=self.localicone)
            ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=False)

        
        #sauvegarde du fichier de config pour le deuxieme tour de piste
        self.ConfParser.write(open(self.fichier,'w'))             
        return ok
    
    def get_image(self,image,imageURL):
        #on telecharge les images selectionnees
        self.localimage = os.path.join(self.picturedir, image)
        f=open(self.localimage,"wb")
        f.write(urllib.urlopen(imageURL).read())
        f.close()
    
    def show_image(self,icone):
        #pavé qui pose probleme, je ne sais pas comment afficher une image en plein ecran
        ok=True
        icone = icone.replace('icone=','')
        print 'icone = ',icone
        tempimageurl = self.ConfParser.get('Dictionnaire', icone) 
        imageurl = tempimageurl.replace('thumb_','')
        self.get_image(icone, imageurl)
        #url=sys.argv[0]+"?image="+urllib.quote_plus(image)
        #print url
        #item=xbmcgui.ListItem(PictureName)
        #NE FONCTIONNE PAS
        imagetoshow = xbmcgui.ControlImage(100, 250, 125, 75,self.localimage, aspectRatio=2)
        imagetoshow.setImage(self.localimage, '0xFFFF3300')
        #item.setInfo(type="Video",infoLabels={ "Title": artiste } )
        #ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=False)
        return ok

    def start(self):
        #Pave repris des investigations de alexsolex en matiere de plugin
        stringparams = sys.argv[2]
        print stringparams
        try:
            if stringparams[0]=="?":
                stringparams=stringparams[1:]
        except:
            pass
        parametres={}
        for param in stringparams.split("&"):
            try:
                cle,valeur=param.split("=")
            except:
                cle=param
                valeur=""
            parametres[cle]=valeur

        if "icone" in parametres.keys():
            print "paramètre icone="+parametres["icone"]
            self.show_image(parametres["icone"])
            #paramètre 'icone' : on liste l'image correspondante

          
            
        else:
            #pas de paramètres : début du plugin
            print "pas de paramètres..."
            self.show_icones()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

print("===================================================================")
print("")
print("        PASSIONXBMC GALERIE")
print("")
print("===================================================================")

w = passiongallerie()
w.start()
del w 
