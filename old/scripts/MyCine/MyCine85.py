# -*- coding: iso-8859-1 -*-

import urllib, os, re, string, time, sys, MyCineUtils
from random import choice
import xbmcgui, xbmc


w = xbmcgui.Window()
if w.getResolution() in ( 1, 12 ):
    from MyCineDatas720p import *
else:
    if w.getResolution() == 0:
        from MyCineDatas1080i import *
    else:
        from MyCinedatas import *
del w

try:
    import Image # PIL librairie
except:
    dialog = xbmcgui.Dialog()
    dialog.ok("MyCine : ERREUR", "Vous devez installer la librairie PIL", "dans le répertoire /python/Lib/ de XBMC.", "Les photos ne seront pas disponibles.")


VERSION = '8.6.10'
HOME = os.getcwd().replace(';','') + os.sep
DOSSIER_TEMP = HOME + 'cine' + os.sep 
PICS    = HOME + 'images' + os.sep
HRATIO = 1
#os.environ['http_proxy'] = 'http://proxy:3128'

# codes keymap
ACTION_PREVIOUS_MENU    = 10
ACTION_SELECT_ITEM      = 7
ACTION_MOVE_LEFT        = 1
ACTION_MOVE_RIGHT       = 2
ACTION_MOVE_UP          = 3
ACTION_MOVE_DOWN        = 4
ACTION_X                = 18
ACTION_B                = 9

LISTE_WINDOWS=[]

def ping(host):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # Create socket and connect to host
    t1=float(0)
    t2=float(0)
    t1 = float(time.time()*1000)
    try:
        s.connect((host, 80))
        t2 = float(time.time()*1000)
        s.close()
        del s
        return int((t2 - t1))
    except socket.error, (errcode, errmsg):
        t2 = time.time()
        # problem connecting... service must be down
        if errcode == 111:# connection refused; means that the machine is up
            return int((t2 - t1))
        else:# something else; means that the machine is not up
            return None

def convertstr(string, charset = "iso-8859-15"):
    """
    convertstr( string , [ charset ] ) --> string
        Renvoi la chaine 'string' dans le 'charset' (iso-8859-15 par défaut)
    """
    try:
        s=str(unicode(string, charset))
    except:
        s=string
    return s

def pop(titre, message1, message2="", message3=""):
    """
    Affiche un popup avec le titre et le message1 (message2 et 3 facultatifs)
    """
    dialog = xbmcgui.Dialog()
    dialog.ok(titre, message1, message2, message3)

def extrait(chaine, debut, fin, nb):
    """
    renvoi le texte commencant par 'debut' et terminant par 'fin', trouvé dans une 'chaine' .
        chaine (string) : le texte entier
        debut (string) : la chaine de départ recherchée
        fin (string) : la chaine finale recherchée
        nb (int) : le décalage du début
    """
    try:
        chaineDebut = chaine.index(debut, 0) + nb
        chaineFin = chaine.index(fin, chaineDebut)
        chaine = chaine[chaineDebut:chaineFin]
        chaine = chaine.replace("&nbsp;", " ")
    except:
        chaine = '...'
    return chaine

def suppr_balises(html):
    """
    Supprime les balises html dans le 'html' (string)
    Renvoi un 'string' sans les balises html.
    Le caractère '&nbsp' est remplacé par un espace
    """
    exp=r"""<.*?>"""
    compile_obj = re.compile(exp, re.IGNORECASE| re.DOTALL)
    match_obj = compile_obj.search(html)
    retour = compile_obj.subn('', html, 0)[0]
    retour=retour.replace("&nbsp;", " ")
    return retour


def removeOlder(path, age, ext):
    fileList = os.listdir(path)
    limit = time.time() / 3600 / 24 - age
    for fileName in fileList:
        if fileName[-4:] == "." + ext:
            statinfo = os.stat(path + fileName)
            if statinfo.st_ctime / 3600 / 24 < limit:
                os.remove(path + fileName)

def downloadJPG(source, destination):
    """
    Télécharge SI BESOIN une url 'source' (string) , dans une URL 'destination' (string)
    La source n'est téléchargée que si la destination n'existe pas déjà
    """
    if os.path.exists(destination):
        pass
    else:
        try:
            loc = urllib.URLopener()
            loc.retrieve(source, destination)
        except:
            pass

def verifrep(folder):
    """
    S'assure de l'existence du dossier folder, et le créé si absent.
    """
    try:
        os.makedirs(folder)
        if not os.path.exists(DOSSIER_TEMP + "A00000.gif"):
            print "Error: " + DOSSIER_TEMP + "A00000.gif n'existe pas!"
            return # TODO: Le fichier par défaut n'existe pas -> pb
    except:
        pass
    
def get_masalle():
    """
    Renvoi la salle par défaut stockée dans le fichier 'masalle.txt'
    Retourne un tuple ( id_salle(string) , nom_salle(string) )
    Si 'masalle.txt' n'existe pas ou est mal erronée, lance la création de la salle avec une salle par défaut ("C0002","Rex")
    """
    try:
        f=open(DOSSIER_TEMP+"masalle.txt", "r")
        num, nom=f.read().split("|")
        f.close()
        return num, nom.replace("\n", "")
    except:
        define_masalle("C0002", "Rex")
        return "C0002", "Rex"

def define_masalle(num, nom):
    f=open(DOSSIER_TEMP+"masalle.txt", "w")
    f.write("%s|%s"%(num, nom))
    f.close()

def add_salle(num, nom):
    """
    Ajoute la salle 'num' (string id de la salle), 'nom' (string) dans la liste de mes salles
    """
    messalles=[]
    try:
        f=open(DOSSIER_TEMP+"messalles.txt", "r")
        messalles=f.readlines()
        f.close()
        i=0
        while True:
            try:
                numsal, nomsal=messalles[i].split("|")
                if numsal==num:
                    pop("Mon Cinéma : Ajout de salle", "La salle %s existe déjà. (#%s)"%(nom, num))
                    return
                else:
                    i+=1
                    pass
            except:#arrive à la fin des salles
                messalles.append("%s|%s\n"%(num, nom))
                break
    except:#le fichier n'a pu être lu : on créé une entrée avec num et nom
        messalles.append("%s|%s\n"%(num, nom))
        
    #maintenant on réécrit le fichier
    f=open(DOSSIER_TEMP+"messalles.txt", "w")
    for salle in messalles:
        f.write(salle)
    f.close()

def del_salle(num):
    """
    Supprime la salle 'num' (string id de la salle) de la liste de mes salles
    """
    try:
        f=open(DOSSIER_TEMP+"messalles.txt", "r")
        messalles=f.readlines()
        f.close()
        i=0
        while True:
            try:
                numsal, nomsal=messalles[i].split("|")
                if numsal==num:
                    delete=i
                    break
                else:
                    i=i+1
            except:#arrive à la fin des salles
                pop("MyCine : Supprimer une salle", "La salle \"%s\" n'a pas été trouvée. (#%s)"%(nom, num))
                return
    except:#le fichier n'a pu être lu : on sort
        pop("MyCine : Supprimer une salle", "Fichier \"messalles.txt\" introuvable.")
        return
    f=open(DOSSIER_TEMP+"messalles.txt", "w")
    for i in range(0,len(messalles)):
        if i != delete:
            f.write(messalles[i])
    f.close()
    
def liste_salle():
    """
    Renvoi une liste de toutes les salles de mes salles
    """
    lstsalles=[]
    try:
        f=open(DOSSIER_TEMP+"messalles.txt", "r")
        salles=f.readlines()
        f.close()
    except:
        pop("MyCine : Liste les salles", "Fichier \"messalles.txt\" manquant !")
        return []
    for salle in salles:
        sa=salle.split("|")
        lstsalles.append([sa[0], sa[1].replace("\n", "")])
    return lstsalles

def GaleriePhoto(id,type):
    """
    """
    ret = []
    urlTpl = "http://www.allocine.fr/photo/ajax/galerie.ws.asp?cat=%s&key=%s&page=%s"
    try:
        url = urlTpl%(type,id,1)
        html = urllib.urlopen(url).read()
        exp = '"total":([0-9]*).*?"paging":([0-9]*)'
        list = re.findall(exp,html)
        nbPhotos = int(list[0][0])
        nbPages = int((nbPhotos - 1) / int(list[0][1])) + 1
        for i in range(0,nbPages):
            if i > 0:
                url = urlTpl%(type,id,i + 1)
                html = urllib.urlopen(url).read()
            exp = '"fichier":"(.*?)","titre":"(.*?)"'
            list = re.findall(exp,html)
            ret.extend(list)
    except:
        print "Error during pictures retrieving"
    return ret

def litSalle(num):
    """
    Parse la salle référencée par son ID 'num' pour en renvoyer les infos :
        -nom
        -adresse
        -listefilms
    """
    progress=xbmcgui.DialogProgress()
    progress.create("MyCine : Mon Cinéma", "Récupération des informations de la salle #%s."%num, "Veuillez patienter...")

    try:
        html = urllib.urlopen("http://www.allocine.fr/seance/salle_gen_csalle=%s.html"%num).read()
    except:
        html = ""

    #INFOS SUR LA SALLE
    #   nom
    try:
        nom=re.findall("""<title>(.*?)</title>""", html)[0]
    except:
        nom="- / -"
    #   adresse
    try:
        adresse=re.findall("""<h4 style="color:#777777">(.*?)<br""", html)[0]
    except:
        adresse="-"

    #restriction de la zone de recherche
    try:
        deb=html.index("""<input type="submit" value="Rechercher" >""")
        fin=html.index("""Liens sponsorisés""")
        html=html[deb:fin]
    except:
        pass

    #liste des (num,url image, titre)
    try:
        exp = re.compile(r'valign="top"><a class="link1" href="/film/fichefilm_gen_cfilm=(.*?)\.html"><img src="(.*?)" border="0" alt="(.*?)"')
        liste=exp.findall(html)
    except:
        liste=[]
    #tous les horaires
    try:
        exp = re.compile(r'<h4 style="color:#D20000">(.*?)</h4>')
        horaires=exp.findall(html)
    except:
        horaires=[]

    listefilms=[]
    i=0
    for l in liste:
        item=[l[0], suppr_balises(l[2])]
        try:
            downloadJPG(l[1], DOSSIER_TEMP+l[0]+".jpg")
            pic=DOSSIER_TEMP+l[0]+".jpg"
        except:
            pic=DOSSIER_TEMP+"A00000.gif"
        item.append(pic)
        item.append(suppr_balises(horaires[i]))
        diffusion=horaires[i].replace("<br />", "\n")
        diffusion=suppr_balises(diffusion)
        item.append(diffusion)
        listefilms.append(item)
        i+=1

    progress.close()
    return nom, adresse, listefilms #num,titre,image,horaire,diffusion
    
def quizz():
    """
    Récupère une question parmis les différentes pages de allocine
    et renvoi la question et le lien vers la réponse
    """
    urllist=["http://www.allocine.fr/default.html", 
             "http://www.allocine.fr/article/default.html", 
             "http://www.allocine.fr/dvd/default.html", 
             "http://www.allocine.fr/boxoffice/default.html", 
             "http://www.allocine.fr/jeux/default.html", 
             "http://www.allocine.fr/video/haute_definition.html", 
             "http://www.allocine.fr/video/default.html", 
             "http://www.allocine.fr/video/cettesemaine.html", 
             "http://www.allocine.fr/video/alaffiche.html", 
             "http://www.allocine.fr/video/prochainement.html", 
             "http://www.allocine.fr/photo/default.html", 
             "http://www.allocine.fr/photo/galerieaffiche.html", 
             "http://www.allocine.fr/photo/galeriephoto.html", 
             "http://www.allocine.fr/personne/default.html", 
             "http://www.allocine.fr/personne/peoplesemaine.html", 
             "http://www.allocine.fr/personne/peopletoujoursaffiche.html", 
             "http://www.allocine.fr/personne/peopleprochainementaffiche.html", 
             "http://www.allocine.fr/personne/peopletempsreel.html", 
             "http://www.allocine.fr/service/mobiles/bouygues.html", 
             "http://www.allocine.fr/service/mobiles/orange.html", 
             "http://www.allocine.fr/service/mobiles/sfr.html", 
             "http://www.allocine.fr/critique/default.html", 
             "http://www.allocine.fr/film/default.html", 
             "http://www.allocine.fr/film/sites_officiels.html", 
             "http://www.allocine.fr/film/alaffiche.html", 
             "http://www.allocine.fr/film/alaffiche_presse.html", 
             "http://www.allocine.fr/film/alaffiche_genre.html", 
             "http://www.allocine.fr/film/alaffiche_alpha.html", 
             "http://www.allocine.fr/film/agenda.html", 
             "http://www.allocine.fr/film/agenda_mois.html", 
             "http://www.allocine.fr/film/agenda_3mois.html", 
             "http://www.allocine.fr/film/agenda_titre.html", 
             "http://www.allocine.fr/film/agenda_distributeur.html", 
             "http://www.allocine.fr/film/agenda_nodate.html"]
    url = choice(urllist)
    sourceHtml = urllib.urlopen(url).read()

    sourceHtml=sourceHtml[sourceHtml.index("<b>Ciné Quizz"):]
    exp="""<h4 style="color: #000000">(.*?)&nbsp;"""
    try:
        question=re.findall(exp, sourceHtml)[0]
        question=suppr_balises(question)
    except:
        question= "Impossible de récupérer une question"
        pop("myCine : Le Quizz", question)
   
    exp="""<a href="(.*?)" class="link1">"""
    try:
        lienreponse=re.findall(exp, sourceHtml)[0]
    except:
        lienreponse=[]
    return question, lienreponse

def Search(searchtext, ch):
    """
    Récupère les résultats d'une recherche sur les mots 'searchtext' (string)
        ch = 0 --> Chercher parmis des films
        ch = 1 --> Chercher parmis les personnes
        ch = 2 --> Chercher parmis les salles
    """
    
    Liste=[]
    page=1
    progress = xbmcgui.DialogProgress()
    progress.create("MyCine : Recherches", "Veuillez patienter...", "Lecture de la première page...")
    
    if ch==1:
        rub=2#cherche des personnes
        nb_resultat_exp="""Stars <h4>.(.*?) réponse[^<]*?</h4>"""
        page_suivante_exp="""<a href="/recherche/default.html.motcle=%s&rub=%s&page=(.*?)" class="link1"><b>Voir les .*? stars"""%(searchtext, rub)
        liste_exp="""<h4><a href="/personne/fichepersonne_gen_cpersonne=([0-9]*?).html" class="link1">(.*?)</a>"""
    elif ch==0:
        rub=1#cherche des films
        nb_resultat_exp="""Films <h4>.(.*?) réponse[^<]*?</h4>"""
        page_suivante_exp="""<a href="/recherche/default.html\?motcle=%s&rub=%s&page=(.*?)" class="link1"><b>Voir"""%(searchtext, rub)
        liste_exp="""<h4><a href="/film/fichefilm_gen_cfilm=([0-9].*?).html" class="link1">(.*?)</a>"""
    elif ch==2:
        rub=3#cherche des salles
        nb_resultat_exp="""Cinémas <h4>.(.*?) réponse[^<]*?</h4>"""
        page_suivante_exp="""<a href="/recherche/default.html.motcle=%s&rub=%s&page=(.*?)" class="link1">Salles suivantes</a>"""%(searchtext, rub)
        liste_exp="""<a href="/seance/salle_gen_csalle=(.*?).html" class="link1">(.*?)</a>"""

    cp_ville = []
    while True:
        html=urllib.urlopen('http://www.allocine.fr/recherche/?rub=%s&motcle=%s&page=%s'%(rub, searchtext.replace(" ", "+"), page)).read()
        debut=html.index(""">Recherche : <b>"%s"</b><"""%searchtext)
        fin=html.index("<b>Rechercher :", debut)
        html=html[debut:fin]

        try:
            html.index("Pas de résultats")
            break
        except:
            pass
            
        try:
            nb_resultat = int(re.findall(nb_resultat_exp, html)[0])
            #nb_resultat=int(re.findall(nb_resultat_exp, html)[0].split(" ")[0][1:])
            #Pmax=int(nb_resultat/20.0)+1
            Pmax = 0
        except:
            print "exception avec le nb de rsulats" 
            Pmax=0
            nb_resultat=0
            break

        page+=1
        
        Liste+=re.findall(liste_exp, html)

        if ch==2:
            exp="""<h4 style="color: #808080">(.*?), </h4><h4 style="color: #808080">(.*?)</h4>"""
            #exp="""<h4 style="color: #666666">(.*?)</h4>"""
            cp_ville+=re.findall(exp, html)#[(CP,ville),(CP,ville),...]

        try:
            PageSuivante=int(re.findall(page_suivante_exp, html)[0])
        except:
            PageSuivante=0
        if not PageSuivante:
		    break
        progress.close()
        progress.create("MyCine : Recherches", "Veuillez patienter...", "Page %s sur %s"%(page, Pmax))
        
    progress.close()
    progress.create("MyCine : Recherches", "Nettoyage des données en cours...")
    nb=len(Liste)
    if nb==0:
        step=0
    else:
        step=(100.0/nb)
    s=0
    i=0
    for l in Liste:
        s+=step
        progress.update(int(s))
        Liste[i]=(l[0], suppr_balises(l[1]))
        try:
            if ch==2:
                Liste[i]=(l[0], suppr_balises(l[1]+" (%s %s)"%(cp_ville[i][0], cp_ville[i][1])))
        except:
            pass
        i+=1
    progress.close()
    return Liste


########
# Menu #
########

class Menu(xbmcgui.Window):
    def __init__(self):
        xbmcgui.Window.__init__(self)
        global HRATIO
        if self.getResolution()==7 or self.getResolution()==9: HRATIO = 4.0/3.0

        self.Position=0
        #Pré-chargement des images focus
        self.img=[]
        a=0
        for img in clipart:
            self.img.append(xbmcgui.ControlImage(PC[a][0], PC[a][1], PC[a][2], PC[a][3], PICS + img))
            a+=1
        self.addControl(xbmcgui.ControlImage(WIN[0], WIN[1], WIN[2], WIN[3], PICS + BG_HOME))
        self.addControl(self.img[0])
        
        # Ajout des boutons
        if USE_TEXTURE==1:
            self.BP1 = xbmcgui.ControlButton(FBP1[0], FBP1[1], FBP1[2], FBP1[3], '', PICS+ONBP1, PICS+OFFBP1)
            self.BP2 = xbmcgui.ControlButton(FBP2[0], FBP2[1], FBP2[2], FBP2[3], '', PICS+ONBP2, PICS+OFFBP2)
            self.BP3 = xbmcgui.ControlButton(FBP3[0], FBP3[1], FBP3[2], FBP3[3], '', PICS+ONBP3, PICS+OFFBP3)
            self.BP4 = xbmcgui.ControlButton(FBP4[0], FBP4[1], FBP4[2], FBP4[3], '', PICS+ONBP4, PICS+OFFBP4)
            self.BP5 = xbmcgui.ControlButton(FBP5[0], FBP5[1], FBP5[2], FBP5[3], '', PICS+ONBP5, PICS+OFFBP5)
            self.BP6 = xbmcgui.ControlButton(FBP6[0], FBP6[1], FBP6[2], FBP6[3], '', PICS+ONBP6, PICS+OFFBP6)
            self.BP7 = xbmcgui.ControlButton(FBP7[0], FBP7[1], FBP7[2], FBP7[3], '', PICS+ONBP7, PICS+OFFBP7)
        if USE_TEXTURE==0:
            self.BP1 = xbmcgui.ControlButton(FBP1[0], FBP1[1], FBP1[2], FBP1[3], TXTBP1, font=TXTf)
            self.BP2 = xbmcgui.ControlButton(FBP2[0], FBP2[1], FBP2[2], FBP2[3], TXTBP2, font=TXTf)
            self.BP3 = xbmcgui.ControlButton(FBP3[0], FBP3[1], FBP3[2], FBP3[3], TXTBP3, font=TXTf)
            self.BP4 = xbmcgui.ControlButton(FBP4[0], FBP4[1], FBP4[2], FBP4[3], TXTBP4, font=TXTf)
            self.BP5 = xbmcgui.ControlButton(FBP5[0], FBP5[1], FBP5[2], FBP5[3], TXTBP5, font=TXTf)
            self.BP6 = xbmcgui.ControlButton(FBP6[0], FBP6[1], FBP6[2], FBP6[3], TXTBP6, font=TXTf)
            self.BP7 = xbmcgui.ControlButton(FBP7[0], FBP7[1], FBP7[2], FBP7[3], TXTBP7, font=TXTf)
        if USE_TEXTURE==-1:
            self.BP1 = xbmcgui.ControlButton(FBP1[0], FBP1[1], FBP1[2], FBP1[3], TXTBP1, PICS+ONBP1, PICS+OFFBP1, font=TXTf)
            self.BP2 = xbmcgui.ControlButton(FBP2[0], FBP2[1], FBP2[2], FBP2[3], TXTBP2, PICS+ONBP2, PICS+OFFBP2, font=TXTf)
            self.BP3 = xbmcgui.ControlButton(FBP3[0], FBP3[1], FBP3[2], FBP3[3], TXTBP3, PICS+ONBP3, PICS+OFFBP3, font=TXTf)
            self.BP4 = xbmcgui.ControlButton(FBP4[0], FBP4[1], FBP4[2], FBP4[3], TXTBP4, PICS+ONBP4, PICS+OFFBP4, font=TXTf)
            self.BP5 = xbmcgui.ControlButton(FBP5[0], FBP5[1], FBP5[2], FBP5[3], TXTBP5, PICS+ONBP5, PICS+OFFBP5, font=TXTf)
            self.BP6 = xbmcgui.ControlButton(FBP6[0], FBP6[1], FBP6[2], FBP6[3], TXTBP6, PICS+ONBP6, PICS+OFFBP6, font=TXTf)
            self.BP7 = xbmcgui.ControlButton(FBP7[0], FBP7[1], FBP7[2], FBP7[3], TXTBP7, PICS+ONBP7, PICS+OFFBP7, font=TXTf)

        self.addControl(self.BP1)
        self.addControl(self.BP2)
        self.addControl(self.BP3)
        self.addControl(self.BP4)
        self.addControl(self.BP5)
        self.addControl(self.BP6)
        self.addControl(self.BP7)

        #Déplacements            
        self.BP1.controlDown(self.BP2)
        self.BP2.controlUp(self.BP1)
        self.BP2.controlDown(self.BP3)
        self.BP3.controlUp(self.BP2)
        self.BP3.controlDown(self.BP4)
        self.BP4.controlUp(self.BP3)
        self.BP4.controlDown(self.BP5)
        self.BP5.controlUp(self.BP4)
        self.BP5.controlDown(self.BP6)
        self.BP6.controlUp(self.BP5)
        #self.BP6.controlDown(self.BP7)
        #self.BP7.controlUp(self.BP6)
        self.BP7.controlUp(self.BP5)
        self.BP6.controlRight(self.BP7)
        self.BP7.controlLeft(self.BP6)
        self.BP1.controlRight(self.BP7)
        self.BP2.controlRight(self.BP7)
        self.BP3.controlRight(self.BP7)
        self.BP4.controlRight(self.BP7)
        self.BP5.controlRight(self.BP7)

        #Flux RSS
        #self.rssreader = RssReader()
        #self.news = self.rssreader.getNews(RSS_URL) 
        #self.rss = xbmcgui.ControlFadeLabel(RSSp[0], RSSp[1], RSSp[2], RSSp[3], RSS_FONT, RSS_COLOR)
        #self.addControl(self.rss)
        #self.rss.addLabel(' ..:: '+RSS_TITLE+' ::..')
        #for i in range(1, len(self.news)):
        #    self.rss.addLabel('  #'+str(i)+'- '+convertstr(self.news[i]))

        #Donne le focus
        self.setFocus(self.BP1)
        
    def onControl(self, control):
        global FondEcran
        
        # Les sorties au cinema
        if control == self.BP1:
            retr1 = TrailerRetriever(boType=1)
            retr2 = TrailerRetriever(boType=0)
            retr3 = TrailerRetriever(boType=2)
            #retr4 = MustSeeTrailerRetriever()
            movieList = MovieList(retrievers = [retr1,retr2,retr3])
            movieList.doModal()
            del movieList # TODO: ne pas la supprimer mais la garder

        # Box Office 
        if control == self.BP2:
            retr = BORetriever()
            movieList = MovieList(retrievers = [retr,retr,retr,retr,retr,retr,retr])
            movieList.doModal()
            del movieList

        # Actualités
        if control == self.BP3:
            #minuteList = MinuteList()
            #minuteList.doModal()
            #del minuteList
            retr = FlashsRetriever()
            movieList = MovieList(retrievers = [retr])
            movieList.doModal()
            del movieList

        # Mon Cinema 
        if control == self.BP4:
            masalle=get_masalle()#récupère la salle par défaut
            Choix=[masalle[1], 'Changer de salle', 'Ajouter une salle', 'Consulter mes salles', 'Supprimer une salle']
            selection = choix(titre='Mon Cinéma', leschoix=Choix)
            selection.show()
            selection.show_panel()
            selection.doModal()
            ch=selection.retour
            if not ch==None:
                if ch==0:#salle par défaut
                    retr = TheaterRetriever(theaterId = masalle[0])
                    movieList = MovieList(retrievers = [retr])
                    movieList.doModal()
                    del movieList

                if ch==1:#changer de salle par defaut
                    messalles=liste_salle()
                    nomsalles=[]
                    for salle in messalles:
                        nomsalles.append(salle[1])
                    Choix=nomsalles
                    selection = choix(titre='Mon Cinéma', leschoix=Choix)
                    selection.show()
                    selection.show_panel()
                    selection.doModal()
                    ch1=selection.retour
                    if not ch1==None:
                        define_masalle(messalles[ch1][0], messalles[ch1][1])
                        #sa=Salle(num=messalles[ch1][0], nom=messalles[ch1][1])
                        #sa.doModal()
                        #del sa
                if ch==2:#ajouter une salle
                    keyboard = xbmc.Keyboard('')
                    keyboard.doModal()
                    if (keyboard.isConfirmed()):
                        sallesdispo=Search(keyboard.getText(), 2)
                        if sallesdispo==[]:
                            pop("Mon Cinéma : Recherche Salle", "Aucun résultats pour \"%s\""%keyboard.getText())
                        else:
                            nomsalles=[]
                            for salle in sallesdispo:
                                nomsalles.append(salle[1])
                            selection = choix(titre='Choisir une salle', leschoix=nomsalles)
                            selection.show()
                            selection.show_panel()
                            selection.doModal()
                            ch1=selection.retour
                            if not ch1==None:
                                add_salle(sallesdispo[ch1][0], nomsalles[ch1])
                                pop("MyCine : Ajout de salle", "La salle \"%s\" a été ajouté ! (#%s)"%(sallesdispo[ch1][1], sallesdispo[ch1][0]))
                                dialog=xbmcgui.Dialog()
                                if dialog.yesno("Mon Cinema : %s ?"%sallesdispo[ch1][1], "Voulez vous définir cette salle par défaut ?"):
                                    define_masalle(sallesdispo[ch1][0], sallesdispo[ch1][1])
                                    #sa=Salle(num=sallesdispo[ch1][0], nom=sallesdispo[ch1][1])
                                    #sa.doModal()
                                    #del sa

                if ch==3:#consulter mes salles
                    messalles=liste_salle()
                    nomsalles=[]
                    for salle in messalles:
                        nomsalles.append(salle[1])
                    Choix=nomsalles
                    selection = choix(titre='Mes salles', leschoix=Choix)
                    selection.show()
                    selection.show_panel()
                    selection.doModal()
                    ch1=selection.retour
                    if not ch1==None:
                        #tml = TheaterMovieList(theaterId = messalles[ch1][0])
                        #tml.doModal()
                        #del tml
                        retr = TheaterRetriever(theaterId = messalles[ch1][0])
                        movieList = MovieList(retrievers = [retr])
                        movieList.doModal()
                        del movieList

                if ch==4:#supprimer une salle
                    messalles=liste_salle()
                    nomsalles=[]
                    for salle in messalles:
                        nomsalles.append(salle[1])
                    Choix=nomsalles
                    selection = choix(titre='Mes salles', leschoix=Choix)
                    selection.show()
                    selection.show_panel()
                    selection.doModal()
                    ch1=selection.retour
                    if not ch1==None:
                        dialog=xbmcgui.Dialog()
                        valide=dialog.yesno("Mon Cinéma : Supprimer une salle", "Vous allez supprimer la salle %s,"%messalles[ch1][1], "Voulez-vous continuer ?")
                        if valide:
                            del_salle(messalles[ch1][0])
                            pop("Mon Cinéma : Suppression d'une salle", "La salle %s a bien été supprimée."%messalles[ch1][1])
                        else:
                            pop("Mon Cinéma : Annulation", "La salle %s n'a pas été supprimée."%messalles[ch1][1])

        # Informations
        if control == self.BP5:
            info_scr=Infos()
            info_scr.doModal()
            del info_scr
            
        # QUIZZ        
        if control == self.BP6:
            q=QUIZZ()
            q.show()
            q.show_panel()
            q.doModal()
            del q


        # Recherche 
        if control == self.BP7:
            Choix=['Chercher un film', 'Chercher une personnalité', 'Chercher une salle']
            selection = choix(titre='Recherches', leschoix=Choix)
            selection.show()
            selection.show_panel()
            selection.doModal()
            ch=selection.retour
            if not ch==None:
                TitrePage = Choix[ch]
                FondEcran = PICS + BG_SEARCH
                keyboard = xbmc.Keyboard('')
                keyboard.doModal()
                if (keyboard.isConfirmed()):
                    listetrouvee = Search(keyboard.getText(), ch)
                    if listetrouvee==[]:
                        dialog=xbmcgui.Dialog()
                        dialog.ok("MyCine - Recherche ", "Aucun résultats pour \"%s\""%keyboard.getText())
                    else:
                        if ch==0:
                            lst_scr = Listefilm0(titrepage=TitrePage, films=listetrouvee, horaires="" , HITEM=LFHSearch, SEARCHflag=True, flagsalle=False)
                            lst_scr.doModal()
                            del lst_scr
                        elif ch==1:
                            listenom=[]
                            for elmt in listetrouvee:
                                nom=suppr_balises(elmt[1])
                                listenom.append(nom)
                            selection = choix(titre="Résultats pour \"%s\""%keyboard.getText(), leschoix=listenom)
                            selection.show()
                            selection.show_panel()
                            selection.doModal()
                            chp=selection.retour
                            if chp>=0:
                                fiche=FichePerso(actid=listetrouvee[chp][0])
                                fiche.doModal()
                                del fiche
                        elif ch==2:
                            listesalles=[]
                            for elmt in listetrouvee:
                                salle=suppr_balises(elmt[1])
                                listesalles.append(salle)
                            selection = choix(titre="Résultats pour \"%s\""%keyboard.getText(), leschoix=listesalles)
                            selection.show()
                            selection.show_panel()
                            selection.doModal()
                            chp=selection.retour
                            if chp>=0:
                                retr = TheaterRetriever(theaterId = listetrouvee[chp][0])
                                movieList = MovieList(retrievers = [retr])
                                movieList.doModal()
                                del movieList
                                #sal=Salle(num=listetrouvee[chp][0], nom=listesalles[chp])
                                #sal.doModal()
                                #del sal
       
                else:
                    print "RECHERCHE DE FILM : recherche annulée"
                       
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        if action == ACTION_MOVE_DOWN:
            if self.Position < 5:
                oldp=self.Position
                self.Position+=1
                self.changefocus(oldp, self.Position)

        if action == ACTION_MOVE_UP:
            if self.Position==6:
                oldp=self.Position
                self.Position=5
                self.changefocus(oldp, self.Position)
            if self.Position > 0:
                oldp=self.Position
                self.Position -=1
                self.changefocus(oldp, self.Position)

        if action == ACTION_MOVE_LEFT:
            if self.Position==6:
                oldp=self.Position
                self.Position -=1
                self.changefocus(oldp, self.Position)
            else:
                pass
        if action == ACTION_MOVE_RIGHT:
            if self.Position<6:
                oldp=self.Position
                self.Position=6
                self.changefocus(oldp, self.Position)
            else:
                pass

    def changefocus(self, oldp, newp):
        self.addControl(self.img[newp])
        self.removeControl(self.img[oldp])


##################
# LISTES DE FILM #
##################

class MovieList(xbmcgui.Window):
    def __init__(self,retrievers):
        self.__retrievers = retrievers
        xbmcgui.Window.__init__(self)
        self.addControl(xbmcgui.ControlImage(WIN[0], WIN[1], WIN[2], WIN[3], PICS + BG_SORTIES))
        self.__hIndex = 0;
        self.__titleLabelCtl0 = xbmcgui.ControlLabel(TLF0[0], TLF0[1], TLF0[2], TLF0[3],"",textColor='0x55FFFFFF',alignment=6)
        self.addControl(self.__titleLabelCtl0)
        self.__titleLabelCtl1 = xbmcgui.ControlLabel(TLF1[0], TLF1[1], TLF1[2], TLF1[3],"",textColor='0xFFFFFFFF', alignment=6)
        self.addControl(self.__titleLabelCtl1)
        self.__titleLabelCtl2 = xbmcgui.ControlLabel(TLF2[0], TLF2[1], TLF2[2], TLF2[3],"",textColor='0x55FFFFFF', alignment=6)
        self.addControl(self.__titleLabelCtl2)
        self.__advertLabelCtrl = xbmcgui.ControlLabel(ADVERT_EXTLIST[0],ADVERT_EXTLIST[1],ADVERT_EXTLIST[2],ADVERT_EXTLIST[3],"Appuyez pour afficher",textColor='0xFFFFFFFF', alignment=6)
        self.addControl(self.__advertLabelCtrl)
        self.__advertLabelCtrl.setVisible(False)
        self.__list = []
        self.__movieList = []
        self.__hasNext = []
        self.__pageId = []
        self.__titleList = []
        for i in range(0,len(self.__retrievers)):
            self.__titleList.append(self.__retrievers[i].getTitles(i))
            self.__list.append(MyCineUtils.ExtendedList(self,MOVIE_EXTLIST[0],MOVIE_EXTLIST[1],MOVIE_EXTLIST[2],MOVIE_EXTLIST[3],self.__retrievers[i].itemSpacing,self.__retrievers[i].itemsDisplayed))
            self.__list[i].hideInfosWhenUnselected = self.__retrievers[i].hideInfosWhenUnselected
            self.__movieList.append([])
            self.__hasNext.append(True)
            self.__pageId.append(0)
        self.getMovies()
        self.__list[0].display()
        self.setTitles()

    def setTitles(self):
        leftTitle = ""
        rightTitle = ""
        if self.__hIndex > 0:
            leftTitle = self.__titleList[self.__hIndex - 1]
        if self.__hIndex < len(self.__titleList) - 1:
            rightTitle = self.__titleList[self.__hIndex + 1]
        self.__titleLabelCtl0.setLabel(leftTitle)
        self.__titleLabelCtl1.setLabel(self.__titleList[self.__hIndex])
        self.__titleLabelCtl2.setLabel(rightTitle)
        self.__advertLabelCtrl.setVisible(len(self.__movieList[self.__hIndex]) == 0)

    def getMovies(self):
        retriever = self.__retrievers[self.__hIndex]
        movies = retriever.getMovies(self.__pageId[self.__hIndex],self.__hIndex)
        self.__movieList[self.__hIndex].extend(movies)
        for movie in movies:
            item = MyCineUtils.ExtendedListItem(retriever.itemHeight)
            if not item.setBean(movie):
                try:
                    os.remove(movie.pictureFilePath)
                except:
                    print "[MovieList][getMovies] Error in removing " + movie.pictureFilePath
                movie.pictureFilePath = None
                item.setBean(movie)
            item.HRATIO = HRATIO
            self.__list[self.__hIndex].addItem(item)
            if movie.pictureFilePath == None or not os.path.exists(movie.pictureFilePath):
                
                loader = MyCineUtils.Loader(movie.pictureUrl,movie.pictureFilePath,item,"pictureLoaded")
                loader.start()
            else:
                item.pictureLoaded()
        self.__list[self.__hIndex].display()
        return movies
        
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()
            return
        if action == ACTION_SELECT_ITEM:
            if len(self.__movieList[self.__hIndex]) == 0:
                self.__advertLabelCtrl.setVisible(False)
                self.getMovies()
                self.__list[self.__hIndex].display()
                return
            movie = self.__movieList[self.__hIndex][self.__list[self.__hIndex].selectedIndex]
            self.__retrievers[self.__hIndex].onSelect(movie)
            return
        if action == ACTION_MOVE_RIGHT:
            if self.__hIndex < len(self.__titleList) - 1:
                self.__list[self.__hIndex].setVisible(False)
                self.__hIndex += 1
                self.setTitles()
                if len(self.__movieList[self.__hIndex]) > 0:
                    self.__list[self.__hIndex].display()
                #self.__list[self.__hIndex].setVisible(True)
            return
        if action == ACTION_MOVE_LEFT:
            if self.__hIndex > 0:
                self.__list[self.__hIndex].setVisible(False)
                self.__hIndex -= 1
                self.setTitles()
                if len(self.__movieList[self.__hIndex]) > 0:
                    self.__list[self.__hIndex].display()
                #self.__list[self.__hIndex].setVisible(True)
            return
        if action == ACTION_MOVE_DOWN:
            if self.__hasNext[self.__hIndex] and self.__list[self.__hIndex].selectedIndex == len(self.__movieList[self.__hIndex]) - 1:
                self.__pageId[self.__hIndex] += 1
                movies = self.getMovies()
                if len(movies) == 0:
                    self.__hasNext[self.__hIndex] = False
        self.__list[self.__hIndex].onAction(action)


class FlashsRetriever:
    def __init__(self):
        self.itemHeight = 80
        self.itemSpacing = FLASHES_ITEM_SPACING_EXT_LIST
        self.itemsDisplayed = FLASHES_ITEM_DISPLAYED_EXT_LIST
        self.hideInfosWhenUnselected = True
        self.date = None
    
    def getTitles(self,index):
        return "Flashes Allociné"
    
    def getMovies(self,pageId,index):
        ret = []
        if pageId > 1:
            return ret
        dialog = xbmcgui.DialogProgress()
        dialog.create("MyCine: Actualités", "Recherche des flashes", "Veuillez patienter...")
        if pageId == 0:
            url = "http://www.allocine.fr/video/laminute/"
            data = None
        else:
            url = "http://www.allocine.fr/video/laminute/ajax_videosdumois.inc"
            mois = int(self.date[0]) - 1
            annee = int(self.date[1])
            if mois == 0:
                mois = 12
                annee -= 1
            data = "mois=%s&annee=%s"%(mois,annee)
        try:
            html = urllib.urlopen(url,data).read()
        except:
            dialog.close()
            return ret
        exp = """<a href="/video/laminute/default_gen_cmedia=([0-9]*?).html"><img src="(.*?)" width="100" height="80" border="0" alt="(.*?)"></a>"""
        list = re.findall(exp,html)
        if pageId == 0:
            exp = """var MoisDerniereVideo=(.*?)\r\nvar AnneeDerniereVideo=(.*?)\r\n"""
            self.date = re.findall(exp,html)
            if len(self.date) == 1:
                self.date = self.date[0]
        
        for element in list:
            movie = ListItem()
            movie.id = element[0]
            movie.pictureFilePath = DOSSIER_TEMP + "lmt" + movie.id + ".jpg"
            movie.pictureUrl = element[1]
            movie.title = element[2]
            movie.infos = ""
            movie.info2 = ""
            ret.append(movie)
        dialog.close()
        return ret
   
    def onSelect(self,movie):
        trailer = Trailer(mediaId = movie.id)
        trailer.play(True)
        del trailer

class TrailerRetriever:
    # type: 0=prochaines sorties, 1=cette semaine, 2=a ne pas manquer
    def __init__(self,boType):
        self.itemHeight = 133
        self.itemSpacing = 15
        self.itemsDisplayed = TRAILERS_ITEM_DISPLAYED_EXT_LIST
        self.hideInfosWhenUnselected = True
        self.boType = boType
        self.nextDate = ""
    
    def getTitles(self,index):
        titles = ("Cette semaine","Prochaines sorties","Plus attendus")
        return titles[index] 
    
    def getMovies(self,pageId,index):
        ret = []
        if self.boType == 1:
            if pageId != 0:
                return ret
            #url = "http://www.allocine.fr/video/cettesemaine.html"
            #exp = """<a href="/film/fichefilm_gen_cfilm=(.*?).html" class="link1"><img src="(.*?)".*?<h2><a href="/film/fichefilm_gen_cfilm=.*?.html" class="link1"><b>(.*?)</b></a>.*?<h4 style="color: #808080">(.*?)</h4>"""
            url = "http://www.allocine.fr/film/cettesemaine.html"
            exp = """<a class="link1" href="fichefilm_gen_cfilm=([0-9]*?).html" title=".*?"><img src="(.*?)".*?<a class="link1" href="/film/fichefilm_gen_cfilm=.*?.html">(.*?)</a>.*?><h4>(.*?)</h4>"""
        if self.boType == 0:
            if pageId == 0:
                url = "http://www.allocine.fr/film/agenda.html"
            else:
                if self.nextDate == "":
                    return ret
            	#url = "http://www.allocine.fr/video/prochainement_gen_page=%s.html"%(pageId + 1)
            	url = "http://www.allocine.fr/film/agenda_gen_date=%s.html"%(self.nextDate)
            #exp = """<a href="/film/fichefilm_gen_cfilm=(.*?).html" class="link1"><img src="(.*?)".*?<h2><a href="/film/fichefilm_gen_cfilm=.*?.html" class="link1"><b>(.*?)</b></a>.*?<h4 style="color: #808080">(.*?)</h4>"""
            exp = """<a class="link1" href="/film/fichefilm_gen_cfilm=([0-9]*?).html" title=".*?"><img src="(.*?)" border.*?<a class="link1" href="/film/fichefilm_gen_cfilm=.*?.html">(.*?)</a>.*?><h4>(.*?)</h4>"""
        if self.boType == 2:
            if pageId == 0:
                url = "http://www.allocine.fr/film/attendus.html"
            else:
                if self.nextDate == "":
                    return ret
            	url = "http://www.allocine.fr/film/attendus_gen_page=%s.html"%(self.nextDate)
            exp = """<td width="120" valign="top" style="padding-right: 10px;">.*?<a href="/film/fichefilm_gen_cfilm=([0-9]*?).html" title=".*?"><img src="(.*?)".*?<a href="/film/fichefilm_gen_cfilm=\d*?.html" class="link1">(.*?)</a>.*?<div style="padding-top: 5px;">(.*?)</h4><br /></div>"""

        dialog = xbmcgui.DialogProgress()
        dialog.create("MyCine: Sorties", "Recherche des informations", "Veuillez patienter...")
        try:
            html = urllib.urlopen(url).read()
        except:
            dialog.close()
            return ret

        #récuperation de la date
        date = re.findall("<b>Semaine du mercredi (.*?)</b>",html)
        
        list = re.findall(exp,html,re.DOTALL)
        for element in list:
            movie = ListItem()
            movie.id = element[0]
            movie.pictureFilePath = DOSSIER_TEMP + "trp" + movie.id
            movie.pictureUrl = element[1]
            if movie.pictureUrl.endswith(".jpg"):
                movie.pictureFilePath = movie.pictureFilePath + ".jpg"
            if movie.pictureUrl.endswith(".gif"):
                movie.pictureFilePath = movie.pictureFilePath + ".gif"
            movie.title = element[2]
            details = element[3].split("<br />")
            for detail in details:
                detail = suppr_balises(detail).replace("\r\n","")
                if detail.startswith("Un film") or detail.startswith("De "):
                    movie.infos = movie.infos + "\n" + detail
                if detail.startswith("Avec"):
                    movie.infos = movie.infos + "\n" + detail
                #if detail.startswith("Date"):
                    #movie.info2 = detail
                if self.boType == 2 and detail.find("Date de sortie") > -1:
                    movie.info2 = detail[detail.find("Date de sortie"):]
            if self.boType == 0:
                movie.info2 = "Date de sortie: " + date[0]
            ret.append(movie)
        # parsing de la date suivante
        if self.boType == 0:
            exp = """<h4><a href="/film/agenda_gen_date=([0-9]*?).html" class="link1">Semaine suiv.</a>"""
            list = re.findall(exp,html,re.DOTALL)
            if(len(list) == 0):
                self.nextDate = ""
            else:
                self.nextDate = list[0]
        if self.boType == 2:
            exp = """<h4><a href="/film/attendus_gen_page=([0-9]*?).html"><b>Suiv.</b>"""
            list = re.findall(exp,html,re.DOTALL)
            if(len(list) == 0):
                self.nextDate = ""
            else:
                self.nextDate = list[0]
        dialog.close()
        return ret
    
    def onSelect(self,movie):
        fiche = Fichefilm(numero = movie.id)
        fiche.doModal()


class MustSeeTrailerRetriever:
    def __init__(self):
        self.itemHeight = 80
        self.itemSpacing = 15
        self.itemsDisplayed = 6

        self.hideInfosWhenUnselected = True
    
    def getTitles(self,index):
        return "Nouvelles BA"
    
    def getMovies(self,pageId,index):
        ret = []
        if pageId > 0:
            return ret
        url = "http://www.allocine.fr/video/anepasmanquer.html"
        dialog = xbmcgui.DialogProgress()
        dialog.create("MyCine: Sorties", "Recherche des bandes-annonces", "Veuillez patienter...")
        try:
            html = urllib.urlopen(url).read()
        except:
            dialog.close()
            return ret

        exp = """<tr>.*?<td style="padding: 5 10 5 0" valign="top" width="110">(.*?)</tr>"""
        list = re.findall(exp,html,re.DOTALL)
       
        for element in list:
            movie = ListItem()
            exp = """<img width="100" height="80" src="(.*?)" """
            movie.pictureUrl = re.findall(exp,element)[0]
            exp = """<a href="/video/player_gen_cmedia=.*?&cfilm=([0-9]*?).html" class="link1"><b>(.*?)</b>"""
            l = re.findall(exp,element)
            movie.id = l[0][0]
            movie.pictureFilePath = DOSSIER_TEMP + "tri" + movie.id
            if movie.pictureUrl.endswith(".jpg"):
                movie.pictureFilePath = movie.pictureFilePath + ".jpg"
            if movie.pictureUrl.endswith(".gif"):
                movie.pictureFilePath = movie.pictureFilePath + ".gif"
            movie.title = l[0][1]
            exp = """<h4>(.*?)</h4>"""
            l = re.findall(exp,element)
            movie.infos = l[0].replace("<br />","\n")
            if len(l) == 3 and l[1].startswith("Date"):
                movie.info2 = l[1]
            ret.append(movie)
        dialog.close()
        return ret
    
    def onSelect(self,movie):
        fiche = Fichefilm(numero = movie.id)
        fiche.doModal()


class BORetriever:
    def __init__(self):
        self.itemHeight = 120
        self.itemSpacing = BOXOFFICE_ITEM_SPACING_EXT_LIST
        self.itemsDisplayed = BOXOFFICE_ITEM_DISPLAYED_EXT_LIST
        self.__titles = ["Box-Office France","Box-Office USA","Spectateurs","Presse","Top 250 Spect.","BO général FR","BO général USA"]
        self.hideInfosWhenUnselected = True
    
    def getTitles(self,index):
        return self.__titles[index]
    
    def getMovies(self,pageId,index):
        ret = []
        if index == 0:
            if pageId > 1:
                return ret
            url = "http://www.allocine.fr/film/meilleurs_gen_filtre=bofrance&critique=&annee=&tri=cettesemaine&page=%s.html"%(pageId + 1)
            url2 = "http://www.allocine.fr/boxoffice/boxofficedetail_gen_pays=5001.html"
        if index == 1:
            if pageId > 1:
                return ret
            url = "http://www.allocine.fr/film/meilleurs_gen_filtre=bousa&critique=&annee=&tri=cettesemaine&page=%s.html"%(pageId + 1)
            url2 = "http://www.allocine.fr/boxoffice/boxofficedetail_gen_pays=5002.html"
        if index == 2:
            url = "http://www.allocine.fr/film/meilleurs_gen_filtre=alaffiche&critique=public&annee=&tri=cettesemaine&page=%s.html"%(pageId + 1)
        if index == 3:
            url = "http://www.allocine.fr/film/meilleurs_gen_filtre=alaffiche&critique=presse&annee=&tri=cettesemaine&page=%s.html"%(pageId + 1)
        if index == 4:
            url = "http://www.allocine.fr/film/meilleurs_gen_filtre=top250&critique=public&annee=&tri=cettesemaine&page=%s.html"%(pageId + 1)
        if index == 5:
            url = "http://www.allocine.fr/film/meilleurs_gen_filtre=bofrance&critique=&annee=&tri=touslestemps&page=%s.html"%(pageId + 1)
        if index == 6:
            url = "http://www.allocine.fr/film/meilleurs_gen_filtre=bousa&critique=&annee=&tri=touslestemps&page=%s.html"%(pageId + 1)
            
        dialog = xbmcgui.DialogProgress()
        dialog.create("MyCine: Sorties", "Recherche du " + self.__titles[index], "Veuillez patienter...")
        try:
            html = urllib.urlopen(url).read()
        except:
            dialog.close()
            return ret
        try:
            exp = """\n<a href="/film/fichefilm_gen_cfilm=([0-9]*?).html"><img src="(.*?)".*?<b>(.*?)</b></a></h3>"""
            list1 = re.findall(exp,html,re.DOTALL)
            if index <= 1 or index >= 5:
                exp = """<td align="center" valign="top" style="padding-right: 10px;"><h5>(.*?)</h5></td>"""
            if index == 2 or index == 3 or index == 4:
                exp = """<br />\\((.*?)\\)</h5>"""
            list2 = re.findall(exp,html)
            if index <= 1:
                html = urllib.urlopen(url2).read()
                exp = """<a href="/film/fichefilm_gen_cfilm=\d*?.html" class="link1">(.*?)</a>.*?<h5>(.*?)</h5>.*?<h5><b>(.*?)</b></h5>.*?<h5>(.*?)</h5>"""
                list3 = re.findall(exp,html)
        except:
            list1 = []
        i = 0
        for element in list1:
            movie = ListItem()
            movie.id = element[0]
            movie.pictureFilePath = DOSSIER_TEMP + "bop" + movie.id
            movie.pictureUrl = element[1]
            if movie.pictureUrl.endswith(".jpg"):
                movie.pictureFilePath = movie.pictureFilePath + ".jpg"
            if movie.pictureUrl.endswith(".gif"):
                movie.pictureFilePath = movie.pictureFilePath + ".gif"
            movie.title = "%s - "%(i + 1 + (15 * pageId)) + element[2]
            movie.infos = list2[i].replace("&nbsp;"," ")
            if index <= 1:
                 movie.infos = movie.infos + "\nCumul: " + list3[(15 * pageId) + i][3].replace("\xa0"," ") + "\nSemaines: " + list3[(15 * pageId) + i][1]
            i += 1
            ret.append(movie)
        dialog.close()
        return ret

    def onSelect(self,movie):
        fiche = Fichefilm(numero = movie.id)
        fiche.doModal()
    

class TheaterRetriever:
    def __init__(self,theaterId):
        self.itemHeight = 150
        self.itemSpacing = 20
        self.itemsDisplayed = THEATER_ITEM_DISPLAYED_EXT_LIST
        self.__theaterId = theaterId
        self.hideInfosWhenUnselected = True
    
    def getTitles(self,index):
        return "Horaires"
    
    def getMovies(self,pageId,index):
        ret = []
        if pageId > 0:
            return ret
        #dialog = xbmcgui.DialogProgress()
        url = "http://www.allocine.fr/seance/salle_gen_csalle=%s.html"%(self.__theaterId)
        dialog = xbmcgui.DialogProgress()
        dialog.create("MyCine: ma salle", "Recherche des horaires", "Veuillez patienter...")
        try:
            html = urllib.urlopen(url).read()
        except:
            dialog.close()
            return ret
        try:
            deb=html.index("""<script type="text/JavaScript" src="/skin/seances.js">""")
            fin=html.index("""Liens sponsorisés""")
            html=html[deb:fin]
        except:
            pass

        #liste des (num,url image, titre)
        try:
            exp = re.compile("""<a class="link1" href="/film/fichefilm_gen_cfilm=([0-9]*?)\.html"><img src="(.*?)" border="0" alt="(.*?)" /></a></td>""")
            liste = exp.findall(html)
        except:
            liste=[]
        #tous les horaires
        horaires=[]
        exp = re.compile("""id="div_seance(..?)_jour(.)" [^>]*?>(.*?)</div>(?=<div|</td>)""")
        exp2 = re.compile("""<h4[^>]*?>(.*?)</h4>""")
        l = exp.findall(html)
        print l
        horaires = []
        daysNames = {"1":"Di","2":"Lu","3":"Ma","4":"Me","5":"Je","6":"Ve","7":"Sa"}
        if len(l) == len(liste) * 7:
            for i in range(0,len(liste)):
                horaires.append("")
                days = ""
                t = ""
                days = ""
                for j in range(0,7):
                    h = exp2.findall(l[i*7+j][2])
                    s = ""
                    for hh in h:
                        s = s + suppr_balises(hh)
                        if len(s) > 0 and s[len(s) - 1] != " ":
                            s = s + " "
                    if s != t:
                        if len(days) == 0:
                            days = daysNames[l[i*7+j][1]]
                        else:
                            if days != daysNames[l[i*7+j-1][1]]:
                                days = days + "-" + daysNames[l[i*7+j-1][1]]
                            horaires[i] = horaires[i] + days + ": " + t + " "
                        days = ""
                        if len(s) > 0:
                            days = daysNames[l[i*7+j][1]]
                    t = s
                if len(s) > 0:
                    if days != daysNames[l[i*7+6][1]]:
                        days = days + "-" + daysNames[l[i*7+6][1]]
                    horaires[i] = horaires[i] + days + ": " + s + " "

        listefilms=[]
        i=0
        for l in liste:
            print horaires[i]
            movie = ListItem()
            movie.id = l[0]
            movie.title = suppr_balises(l[2])
            movie.infos = suppr_balises(horaires[i].replace("<b>","\n").replace(" | "," "))
            movie.pictureUrl = l[1]
            i+=1
            movie.pictureFilePath = DOSSIER_TEMP + "mop" + movie.id        
            if movie.pictureUrl.endswith(".jpg"):
                movie.pictureFilePath = movie.pictureFilePath + ".jpg"
            if movie.pictureUrl.endswith(".gif"):
                movie.pictureFilePath = movie.pictureFilePath + ".gif"
            ret.append(movie)

        dialog.close()
        return ret
    
    def onSelect(self,movie):
        fiche = Fichefilm(numero = movie.id)
        fiche.doModal()


class SecretsRetriever:
    def __init__(self,movieId):
        self.itemHeight = 120
        self.itemSpacing = 6
        self.itemsDisplayed = SECRETS_ITEM_DISPLAYED_EXT_LIST
        self.hideInfosWhenUnselected = True
        self.date = None
        self.__movieId = movieId
    
    def getTitles(self,index):
        return "Anecdotes"
    
    def getMovies(self,pageId,index):
        ret = []
        if pageId > 1:
            return ret
        dialog = xbmcgui.DialogProgress()
        dialog.create("MyCine: Anecdotes", "Recherche des infos", "Veuillez patienter...")
        if pageId == 0:
            url = "http://www.allocine.fr/film/anecdote_gen_cfilm=%s.html"%self.__movieId
            data = None
        else:
            url = "http://www.allocine.fr/film/anecdote_gen_cfilm=%s&page=%s.html"%(self.__movieId,pageId + 1)
        try:
            html = urllib.urlopen(url).read()
        except:
            dialog.close()
            return ret
        try:
            exp = """<td colspan="3" valign="top">(<br />)*<h4><b>(.*?)</b></h4></td>.*?<div align="justify"><h4>(.*?)</h4></div>"""
            list = re.findall(exp,html,re.DOTALL)
        except:
            list = []
        for element in list:
            secret = ListItem()
            secret.title = element[1]
            infos = suppr_balises(element[2])
            secret.infos = infos
            ret.append(secret)
        dialog.close()
        return ret
   
    def onSelect(self,movie):
        textDialog = TextDialog(titre="Anecdotes",text=movie.infos)
        textDialog.show()
        textDialog.show_panel()
        textDialog.doModal()
        del textDialog


class ListItem:
    def __init__(self):
        self.id = None
        self.title = ""
        self.infos = ""
        self.info2 = ""
        self.pictureUrl = None
        self.pictureFilePath = None
    
    def getPictureFilePath(self):
        if self.pictureFilePath == None or not os.path.exists(self.pictureFilePath):
            return DOSSIER_TEMP + "A00000.gif"
        return self.pictureFilePath
        

class Trailer:
    def __init__(self,mediaId):
        self.__mediaId = mediaId
        
    def play(self,bHd = False):
        if bHd:
            selection = choix(titre="Qualité de la BA",leschoix=["Haute définition","Basse définition"]) 
            selection.show()
            selection.show_panel()
            selection.doModal()
            if selection.retour != 0:
                bHd = False
        try:
            if bHd:
                xml = urllib.urlopen("http://www.allocine.fr/video/xml/videos.asp?media=" + self.__mediaId + "&hd=1").read()
            else:
                xml = urllib.urlopen("http://www.allocine.fr/video/xml/videos.asp?media=" + self.__mediaId).read()
        except:
            return
        list = re.findall("""<video\s*?title="(.*?)".*?ld_path="(.*?)".*?md_path="(.*?)".*?hd_path="(.*?)" """, xml,re.DOTALL)
        fic = ""
        if list[0][3] != "":
            fic = list[0][3]
        else:
            if list[0][2] != "":
                fic = list[0][2]
            else:
                fic = list[0][1]
            
        url = "http://a69.g.akamai.net/n/69/32563/v1/mediaplayer.allocine.fr" + fic + ".flv"
        if fic != "":
            xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(url)
        else:
            if bHd:
                self.play(False)

    
class Listefilm0(xbmcgui.Window):
    def __init__(self, titrepage, films, horaires, HITEM, SEARCHflag=False, flagsalle=False):
        xbmcgui.Window.__init__(self)
        #self.setCoordinateResolution(6)
        self.films=films
        self.flagsalle=flagsalle
        self.horaires=horaires

        # Le fond       
        self.addControl(xbmcgui.ControlImage(WIN[0], WIN[1], WIN[2], WIN[3], FondEcran))
        # Le titre
        self.addControl(xbmcgui.ControlLabel(TLF1[0], TLF1[1], TLF1[2], TLF1[3], titrepage, alignment=6))
        # Liste des films
        self.Film = xbmcgui.ControlList(LFPList[0], LFPList[1], LFPList[2], LFPList[3], 
                                        itemHeight=HITEM, 
                                        imageWidth= int ((HITEM-5)/HRATIO), 
                                        imageHeight= HITEM-5, 
                                        selectedColor= LFselc, 
                                        textColor=LFtxtc, 
                                        buttonTexture=PICS+LFnofocus, 
                                        buttonFocusTexture=PICS+LFfocus)
        self.addControl(self.Film)
        for film in self.films:
            if not SEARCHflag:
                try:
                    thumb=film[2]
                except:
                    thumb=DOSSIER_TEMP+"A00000.gif"
                self.Film.addItem(xbmcgui.ListItem(label=film[1],thumbnailImage=thumb))
            else:
                self.Film.addItem(xbmcgui.ListItem(label=film[1]))
                
        self.setFocus(self.Film)
    
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        
    def onControl(self, control):
        if control == self.Film:
            item = self.Film.getSelectedItem()
            nb = self.Film.getSelectedPosition()
            SearchNumero = self.films[nb][0]
            SearchTitre = self.films[nb][1]
            fiche_scr = Fichefilm(numero=SearchNumero, titre=SearchTitre, Horaire=self.horaires, flagsalle=self.flagsalle)
            fiche_scr.doModal()
            del fiche_scr


##################
# FICHE DE FILMS #
##################

class Fichefilm(xbmcgui.Window):
    def __init__(self, numero, titre="", Horaire="", flagsalle=False):
        xbmcgui.Window.__init__(self)
        #self.setCoordinateResolution(6)
        self.flagg=0
        self.movieId = numero
        self.title = titre
        self.horaire=Horaire
        self.flagsalle=flagsalle

        # Le fond
        self.addControl(xbmcgui.ControlImage(WIN[0], WIN[1], WIN[2], WIN[3], PICS + FondFicheFilm))
        # Le Titre du film
        self.strTitre = xbmcgui.ControlLabel(FFPGX+FFTIT[0], FFPGY+FFTIT[1], FFTIT[2], FFTIT[3], '-', FFf_titre, FFc_titre, alignment=FFTITalign)
        self.addControl(self.strTitre)
        # Le Titre ORIGINAL du film
        self.strTitreO = xbmcgui.ControlLabel(FFPGX+FFTITO[0], FFPGY+FFTITO[1], FFTITO[2], FFTITO[3], '-', FFf_titreO, FFc_titreO, alignment=FFTITalign)
        self.addControl(self.strTitreO)
        # La date de sortie
        self.addControl(xbmcgui.ControlLabel(FFPGX+FFdat[0], FFPGY+FFdat[1], FFdat[2], FFdat[3], 'Sortie le :', FFf_label, FFc_label))
        self.strDate = xbmcgui.ControlLabel(FFPGX+FFDAT[0], FFPGY+FFDAT[1], FFDAT[2], FFDAT[3], '-', FFf_value, FFc_value)
        self.addControl(self.strDate)
        # Le réalisateur
        self.addControl(xbmcgui.ControlLabel(FFPGX+FFrea[0], FFPGY+FFrea[1], FFrea[2], FFrea[3], 'Réalisateur :', FFf_label, FFc_label))
        self.btnRea = xbmcgui.ControlButton(FFPGX+FFREA[0], FFPGY+FFREA[1], FFREA[2], FFREA[3], FFreaLbl, PICS+FOCUSbtn, PICS+NOFOCUSbtn)
        self.addControl(self.btnRea)
        # Le casting
        self.addControl(xbmcgui.ControlLabel(FFPGX+FFcast[0], FFPGY+FFcast[1], FFcast[2], FFcast[3], 'Casting :', FFf_label, FFc_label))
        self.btnCast = xbmcgui.ControlButton(FFPGX+FFCAST[0], FFPGY+FFCAST[1], FFCAST[2], FFCAST[3], FFcastLbl, PICS+FOCUSbtn, PICS+NOFOCUSbtn)
        self.addControl(self.btnCast)
        self.btnCast.setVisible(False)
        # Le genre
        self.addControl(xbmcgui.ControlLabel(FFPGX+FFgen[0], FFPGY+FFgen[1], FFgen[2], FFgen[3], 'Genre :', FFf_label, FFc_label))
        self.strGenre = xbmcgui.ControlLabel(FFPGX+FFGEN[0], FFPGY+FFGEN[1], FFGEN[2], FFGEN[3], '-', FFf_value, FFc_value)
        self.addControl(self.strGenre)
        # La durée
        self.addControl(xbmcgui.ControlLabel(FFPGX+FFdur[0], FFPGY+FFdur[1], FFdur[2], FFdur[3], 'Durée :', FFf_label, FFc_label))
        self.strDuree = xbmcgui.ControlLabel(FFPGX+FFDUR[0], FFPGY+FFDUR[1], FFDUR[2], FFDUR[3], '-', FFf_value, FFc_value)
        self.addControl(self.strDuree)
        # La note
        self.strNote = xbmcgui.ControlLabel(FFPGX+FFNOT[0], FFPGY+FFNOT[1], FFNOT[2], FFNOT[3], '-', FFf_label, FFc_label)
        self.addControl(self.strNote)
        # Box Office France
        self.addControl(xbmcgui.ControlLabel(FFPGX+FFbofrance[0], FFPGY+FFbofrance[1], FFbofrance[2], FFbofrance[3], 'BO France :', FFf_label, FFc_label))
        self.strBOfr = xbmcgui.ControlLabel(FFPGX+FFBOFRANCE[0], FFPGY+FFBOFRANCE[1], FFBOFRANCE[2], FFBOFRANCE[3], '-', FFf_value, FFc_value)
        self.addControl(self.strBOfr)
        # le textebox Synopsis
        self.txtSynHor = xbmcgui.ControlTextBox(FFPGX+FFSHT[0], FFPGY+FFSHT[1], FFSHT[2], FFSHT[3], font=FFf_synhor, textColor=FFc_synhor)
        self.addControl(self.txtSynHor)
        # Le bouton pour la BA
        self.btnBA = xbmcgui.ControlButton(FFPGX+FFBBA[0], FFPGY+FFBBA[1], FFBBA[2], FFBBA[3], FFBBALbl, PICS+FFBBAfocus, PICS+FFBBAnofocus)
        self.addControl(self.btnBA)
        self.btnBA.setVisible(False)
        # Le bouton pour les secrets
        self.btnSecrets = xbmcgui.ControlButton(FFPGX+FFBHO[0], FFPGY+FFBHO[1], FFBHO[2], FFBHO[3], FFBHOLblSec, PICS+FFBHOfocus, PICS+FFBHOnofocus)
        self.addControl(self.btnSecrets)        
        self.btnSecrets.setVisible(True)
        
        # Les déplacements
        self.btnRea.controlDown(self.btnCast)
        self.btnCast.controlDown(self.btnSecrets)
        self.btnCast.controlUp(self.btnRea)
        self.txtSynHor.controlUp(self.btnSecrets)
        self.btnSecrets.controlUp(self.btnCast)
        self.btnSecrets.controlDown(self.txtSynHor)
        self.btnBA.controlRight(self.btnSecrets)
 
        self.setFocus(self.btnRea)
        
        self.fillFields()
        
    def getMovieDetail(self):
        """
        Parse la fiche d'un film pour en renvoyer les infos
        """
        dialog = xbmcgui.DialogProgress()
        dialog.create('MyCine : Lecture de la fiche film', 'Chargement de la fiche #%s en cours'%self.movieId, 'Veuillez patienter...')
        try:
            html=urllib.urlopen('http://www.allocine.fr/film/fichefilm_gen_cfilm=%s.html'%self.movieId).read()
        except:
            print "FicheFilm : Impossible de télécharger la fiche film"
            dialog.close()
            return
        try: #Titre du film
            self.title = re.findall("""<h1 class="TitleFilm">(.*?)</h1>""", html)[0]
        except:
            pass
        try:# note de la presse
            deb="""Critiques Presse</h2>"""
            htmlinfos = html[html.index(deb):]
            tab=re.findall("""<td><img src=".*?" [^>]*? class="etoile_(.)""", htmlinfos)
            e4=tab.count('4')
            e3=tab.count('3')
            e2=tab.count('2')
            e1=tab.count('1')
            e0=tab.count('0')
            d=float(e0+e1+e2+e3+e4)
            s=e1+e2*2+e3*3+e4*4
            self.pressRating = "%1.2f"%(s/d) + "/4"
        except:
            self.pressRating = "-"
        try:#note du public
            tab=re.findall("""note=(.).html" class="link1">.*? (.*?) critique""", htmlinfos)
            s=0.0
            d=0.0
            for l in tab:
                if l[1]=="":
                    n=1
                else:
                    n=int(l[1])
                s=s+int(l[0])*n
                d=d+int(n)
            self.publicRating = "%1.2f"%(s/d) + "/4"        
        except:
            self.publicRating = "-"
        # INFOS DIVERSES
        try:
            deb="""<table cellpadding="0" cellspacing="0" border="0" width="750" style="margin: 0 0 10 0;">"""
            fin="""<h5>Tags"""
            htmlinfos = html[html.index(deb):html.index(fin)]
        except:
            htmlinfos="Pas d'informations disponibles"
        try: # Poster
            #exp="""<img src="(.*?)" border="0" alt="" class="affichette" />"""
            exp="""<img src="(.*?)" border="0" alt="[^"]*?" class="affichette" />"""
            posterUrl = re.findall(exp, htmlinfos)[0]
            ext = posterUrl[-3:]
            self.poster = DOSSIER_TEMP + "mop" + self.movieId + "." + ext
            loader = MyCineUtils.Loader(posterUrl,self.poster,self,"displayPoster")
            loader.start()
        except:
            self.poster = DOSSIER_TEMP + "A00000.gif"
        try:#date de sortie
            self.releaseDate = re.findall("""Date de sortie : <b><a [^>].*> (.*?)</a></b>""", htmlinfos)[0]
        except:
            self.releaseDate = ""
        try:#realisateur
            self.director = []  
            Reas=re.findall("""Réalisé par <a class="link1" href="/personne/fichepersonne_gen_cpersonne=([0-9]*?).html">(.*?)</a>""", htmlinfos)[0]
            self.director = [(Reas[0], suppr_balises(Reas[1]))]
        except:
            self.director = [("", "")] # TODO: cas des réalisateurs multiples
        try:#casting
            loader = MyCineUtils.Loader("http://www.allocine.fr/film/casting_gen_cfilm=%s.html"%self.movieId,None,self,"castingParsing")
            loader.start()
        except:
            self.castingList = []
        try:#genre
            self.categories = suppr_balises(re.findall("""Genre : (.*?)</h3>""", htmlinfos)[0])
        except:
            self.categories = ""
        try:#durée
            self.length = re.findall("""Durée : (.*?).&nbsp;""", htmlinfos)[0]
        except:
            self.length = ""
        try:#titre original
            self.originalTitle = suppr_balises(re.findall("""Titre original : <i>(.*?)</i>""", htmlinfos)[0])
        except:
            self.originalTitle = ""
        # SYNOPSIS
        try:
            htmlsynopsis=extrait(html,"""<div align="justify"><h4>""", "</h4>", 0)
        except:
            htmlsynopsis="-- Pas de synopsis --"
        try:
            self.synopsis = htmlsynopsis.replace("\t", "    ")
            self.synopsis = self.synopsis.replace("\n", "")
            self.synopsis = self.synopsis.replace("\r", "")
            self.synopsis = self.synopsis.replace("<br />", "\n")
            self.synopsis = suppr_balises(self.synopsis)
        except:
            self.synopsis = "- Pas de synopsis -"
        try: #BO France
            deb=html.index("""Fiche Technique</h2>""")
            htmlinfos=html[deb:]
            self.frenchBoxOffice = re.findall("""<b>Box Office France</b> : (.*?) entrées""", htmlinfos)[0]
            self.frenchBoxOffice = self.frenchBoxOffice.replace("\xa0", ".")
        except:
            self.frenchBoxOffice = "-"
        try:#bandes annonces
            self.trailers = None
            loader = MyCineUtils.Loader("http://www.allocine.fr/film/video_gen_cfilm=%s.html"%self.movieId,None,self,"trailersParsing")
            loader.start()
        except:
            self.trailers = None
        dialog.close()

    def fillFields(self):        
        try:
            self.getMovieDetail()
        except:
            pop("MyCine : ERREUR", "une erreur est survenue lors de la récupération des", "informations du film.")
            self.close()
        
        #Le titre
        self.strTitre.setLabel(self.title)
        #le titre original
        self.strTitreO.setLabel(self.originalTitle)
        #date de sortie
        self.strDate.setLabel(self.releaseDate)
        #Realisateur
        self.btnRea.setLabel(self.director[0][1])
        #Le genre
        self.strGenre.setLabel(self.categories)
        #La durée
        self.strDuree.setLabel(self.length)
        #box office
        self.strBOfr.setLabel(self.frenchBoxOffice)
        #La note presse et public
        self.strNote.setLabel('Presse : %s  | Public : %s'%(self.pressRating,self.publicRating))
        #self.strNote.setLabel(QUIZZ.question)
        #Le synopsis
        #self.strSynHor.setLabel("Synopsis :")
        self.txtSynHor.setText(self.synopsis)
 
    def displayPoster(self):
        self.addControl(xbmcgui.ControlImage(FFPGX+AFF[0], FFPGY+AFF[1], AFF[2], int(AFF[3]*HRATIO), self.poster))

    def castingParsing(self,htmlcast):
        deb = htmlcast.index("""Acteurs</h2>""")
        fin = htmlcast.index("""</table>""", deb+1)
        htmlcast = htmlcast[deb:fin]
        exp = re.compile("""<h5>(.*?)</h5></td>.*?cpersonne=([0-9]*?).html" class="link1">(.*?)</a>""", re.DOTALL)
        listecasting = re.findall(exp, htmlcast, re.DOTALL)
        self.castingList = []
        for cast in listecasting:
            self.castingList.append([cast[1], suppr_balises(cast[2]), suppr_balises(cast[0])])
        self.btnCast.setVisible(True) 
    
    def trailersParsing(self,html):
        i1 = html.index("""<div id="player""")
        i2 = html.index("""<div id="autrevideo""")
        html = html[i1:i2]
        list = re.findall("""<h5>..<a href="/video/player_gen_cmedia=(.*?)&cfilm=.*?.html" class="link1"><b>(.*?)</b>(.*?)</a>""", html, re.DOTALL)
        self.trailers = []
        for ba in list:
            if ba[2][0:3] == " - ":
                title = ba[2][3:]
            else:
                title = ba[2]
            self.trailers.append((ba[0], title))
        self.btnBA.setVisible(True)
        self.setNavigation()

    def setNavigation(self):
        self.btnBA.setVisible(True)
        self.btnSecrets.controlLeft(self.btnBA)

    def onControl(self, control):
        if control==self.btnBA:
            bachoix=[]
            for ba in self.trailers:
                bachoix.append(ba[1])
            selectBA=choix(titre="Choix de la Bande-Annonce", leschoix=bachoix)
            selectBA.show()
            selectBA.show_panel()
            selectBA.doModal()
            chba=selectBA.retour
            if chba>=0:
                try:
                    trailer = Trailer(mediaId = self.trailers[chba][0])
                    trailer.play(True)
                    #xml=urllib.urlopen("http://www.allocine.fr/video/xml/videos.asp?media=%s&ref=%s&typeref=film&hd=0&rld=1"%(self.trailers[chba][0],self.movieId)).read()
                    #list2=re.findall("""<video.*?title="(.*?)".*?ld_path="(.*?)".*?md_path="(.*?)" """, xml)
                    #if list2[0][2]=="":
                    #    url="http://a69.g.akamai.net/n/69/32563/v1/mediaplayer.allocine.fr"+list2[0][1]+".flv"
                    #else:
                    #    url="http://a69.g.akamai.net/n/69/32563/v1/mediaplayer.allocine.fr"+list2[0][2]+".flv"
                    #xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(url)
                except:
                    pop("MyCine : Bande Annonce", "La bande annonce n\'est pas disponible")
            else:
                pass

        if control==self.btnSecrets:
            retr = SecretsRetriever(self.movieId)
            secretsList = MovieList(retrievers = [retr])
            secretsList.doModal()
            del secretsList

            
        if control == self.btnRea:
            fiche=FichePerso(actid=self.director[0][0])
            fiche.doModal()
            del fiche

        if control == self.btnCast:
            lstcasting = []
            for cast in self.castingList:
                line = cast[1]
                if cast[2] != "":
                    line += " - " + cast[2]
                lstcasting.append(line)
            selection = choix(titre="Casting de %s"%self.title, leschoix=lstcasting)
            selection.show()
            selection.show_panel()
            selection.doModal()
            chp=selection.retour
            if chp>=0:
                fiche=FichePerso(actid=self.castingList[chp][0])
                fiche.doModal()
                del fiche
            
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()
            
        if action == ACTION_X:
            try:
                dialogwait=xbmcgui.DialogProgress()
                dialogwait.create("MyCine : Photos", "Récupération des photos en cours", "Veuillez patienter...")
                photos=diapos(filmID=self.movieId, lstPhotos=GaleriePhoto(self.movieId,"film"), titre=self.title, ref=1)
                photos.show()
                dialogwait.close()
                photos.show_panel(True)
                photos.doModal()
                del photos
            except:
                dialogwait.close()
                pass

           
######################
# FICHE PERSONNALITE #
######################

class FichePerso(xbmcgui.Window):
    def __init__(self, actid, nomacteur="Pas d'acteur"):
        xbmcgui.Window.__init__(self)
        #self.setCoordinateResolution(6)
        self.persoid=actid
        self.nom=nomacteur
        self.fonction=''
        self.etatcivil=''
        self.photo=DOSSIER_TEMP+"A00000.gif"
        self.bio='Pas de biographie'
        self.liste_perso=[]
        self.liste_films=[]
        
        # Le fond
        self.addControl(xbmcgui.ControlImage(WIN[0], WIN[1], WIN[2], WIN[3], PICS + FondFichePerso))

        # Le Nom de l'acteur
        self.strNom = xbmcgui.ControlFadeLabel(FPPGX+FPNOM[0], FPPGY+FPNOM[1], FPNOM[2], FPNOM[3], FPfnom, FPcnom, alignment=FPNOMalign)
        self.addControl(self.strNom)
        # L'état civil
        self.strEtatCivil = xbmcgui.ControlFadeLabel(FPPGX+FPEC[0], FPPGY+FPEC[1], FPEC[2], FPEC[3], FPflbl, FPclbl)
        self.addControl(self.strEtatCivil)
        # Les fonctions du pesonnage
        self.strFonction = xbmcgui.ControlFadeLabel(FPPGX+FPFONC[0], FPPGY+FPFONC[1], FPFONC[2], FPFONC[3], FPflbl, FPclbl)
        self.addControl(self.strFonction)
        # La biographie
        self.strBio = xbmcgui.ControlTextBox(FPPGX+FPBIO[0], FPPGY+FPBIO[1], FPBIO[2], FPBIO[3], FPfbio, FPcbio)
        self.addControl(self.strBio)
		        
        # Le bouton pour la liste des films
        self.btnfilms = xbmcgui.ControlButton(FPPGX+FPBF[0], FPPGY+FPBF[1], FPBF[2], FPBF[3], FPBFlbl, PICS+FOCUSbtn, PICS+NOFOCUSbtn)
        self.addControl(self.btnfilms)
        # Le bouton pour la liste des acteurs
        self.btnpersonnes = xbmcgui.ControlButton(FPPGX+FPBP[0], FPPGY+FPBP[1], FPBP[2], FPBP[3], FPBPlbl, PICS+FOCUSbtn, PICS+NOFOCUSbtn)
        self.addControl(self.btnpersonnes)
        
        self.btnfilms.controlRight(self.strBio)
        self.btnpersonnes.controlRight(self.strBio)
        self.strBio.controlLeft(self.btnfilms)
        self.btnfilms.controlDown(self.btnpersonnes)
        self.btnpersonnes.controlUp(self.btnfilms)
        self.setFocus(self.btnfilms)
        
        wait=xbmcgui.DialogProgress()
        wait.create("MyCine", "Récupération de la fiche personnalité #%s"%self.persoid)
        self.Ecrit()
        wait.close()
        
    def getFichePerso(self,actid, nom):
        """
        Parse la fiche d'un personnage pour en renvoyer les infos :
            -Nom
            -Fonction
            -EtatCivil
            -Photo
            -Bio
            -ListePerso
            -ListeFilms
        """
        try:
            html = urllib.urlopen("http://www.allocine.fr/personne/fichepersonne_gen_cpersonne=%s.html"%actid).read()
        except:
            html = ""
        #Le nom
        try:
            exp="""<title>(.*?)</title>"""
            Nom=re.findall(exp, html)[0]
        except:
            Nom="Inconnu"
        #les fonctions (realisateur, metteur en scène, acteur, etc etc...)
        try:
            exp="""<div><h4><b>(.*?)</b></h4></div>"""
            Fonction=re.findall(exp, html)[0]
        except:
            Fonction=""
        # état civile (né à... en 19... )
        try:
            exp="""<h4><div style="padding:10 0 0 0">(.*?)</h4>"""
            EtatCivil=re.findall(re.compile(exp, 16), html)[0].replace("\n\n", " / ")
            EtatCivil=EtatCivil.replace("\n", " ")
            EtatCivil=EtatCivil.replace("\r", "")
            EtatCivil=suppr_balises(EtatCivil)
        except:
            EtatCivil=""
        # récupération de sa photo
        try:
            exp="""<img src="(.*?)" width="120" height="160" border="0">"""
            pic=re.findall(exp, html)[0]
            if pic==[]:
                Photo=DOSSIER_TEMP+"A00000.gif"
            else:
                downloadJPG(pic, DOSSIER_TEMP+"P%s.jpg"%actid)
                Photo = DOSSIER_TEMP+"P%s.jpg"%actid
        except:
            Photo = DOSSIER_TEMP+"A00000.gif"
    
        # BIOGRAPHIE
        try:
            exp="""<div align="justify"><h4>(.*?)</h4></div></td>"""
            Biobrut=re.findall(re.compile(exp, 16), html)[0]
        except:
            Biobrut=""
        #SI on souhaite récupérer les liens films et liens personnages, il faut le faire maintenant
        #   personnages
        try:
            exp="""<a class="link1" href="/personne/fichepersonne_gen_cpersonne=([0-9]*?).html">(.*?)</a>"""
            ListePerso=re.findall(exp, Biobrut) # modifier ensuite pour extraire les doublons de la liste
        except:
            ListePerso=[]
        #   nettoyage de la biographie
        try:
            Bio = suppr_balises(Biobrut)
            Bio=Bio.replace("\r", "")
            Bio=Bio.replace("\t", "    ")
            Bio=Bio.replace("\n\n", "\n")
            if Bio=="":
                Bio="Pas de Biographie..."
        except:
            pop("biographie", "ERREUR")
            Bio = "Il n'y a pas de biographie pour cette personne."
            
        #   filmographie
        try:
            exp="""<a class="link1" href="/film/fichefilm_gen_cfilm=([0-9]*?).html"><b>(.*?)</b></a>"""
            ListeFilms=re.findall(exp, Biobrut) # modifier ensuite pour extraire les doublons de la liste
        except:
            ListeFilms=[]
           
        #voir pour ajouter ici "toute sa filmographie"
        #"http://www.allocine.fr/personne/filmographie_gen_cpersonne=%s.html"%actid
        #

        return Nom, Fonction, EtatCivil, Photo, Bio, ListePerso, ListeFilms

    def Ecrit(self):
        self.nom, self.fonction, self.etatcivil, self.photo, self.bio, self.liste_perso, self.liste_films=self.getFichePerso(self.persoid, self.nom)
        self.addControl(xbmcgui.ControlImage(FPPGX+FPPIC[0], FPPGY+FPPIC[1], FPPIC[2]/HRATIO, FPPIC[3], self.photo))
        if self.liste_perso==[]:
            self.btnpersonnes.setVisible(0)
        if self.liste_films==[]:
            self.btnfilms.setVisible(0)
        #self.strNom.setLabel(self.nom)
        self.strNom.addLabel(self.nom)
        #self.strEtatCivil.setLabel(self.etatcivil)
        self.strEtatCivil.addLabel(self.etatcivil)
        #self.strFonction.setLabel(self.fonction)
        self.strFonction.addLabel(self.fonction)
        self.strBio.setText(self.bio)

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        if action == ACTION_X:
            try:
                dialogwait=xbmcgui.DialogProgress()
                dialogwait.create("MyCine : Photos", "Récupération des photos en cours", "Veuillez patienter...")
                photos=diapos(filmID=self.persoid, lstPhotos=GaleriePhoto(self.persoid,"star"), titre=self.nom, ref=2)
                photos.show()
                dialogwait.close()
                photos.show_panel(True)
                photos.doModal()
                del photos
            except:
                dialogwait.close()
                pass

    def onControl(self, control):
        if control==self.btnpersonnes:
            Choix=[]
            for perso in self.liste_perso:
                Choix.append(perso[1])
            selection = choix(titre='Personnages cités par la biographie de %s'%self.nom, leschoix=Choix)
            selection.show()
            selection.show_panel()
            selection.doModal()
            ch=selection.retour
            if not ch==None:
                fiche=FichePerso(actid=self.liste_perso[ch][0])
                fiche.doModal()
                del fiche
        if control==self.btnfilms:
            Choix=[]
            for film in self.liste_films:
                Choix.append(film[1])
            selection = choix(titre='Films cités par la biographie de %s'%self.nom, leschoix=Choix)
            selection.show()
            selection.show_panel()
            selection.doModal()
            ch=selection.retour
            if not ch==None:
                fiche_scr = Fichefilm(numero=self.liste_films[ch][0], titre=self.liste_films[ch][1])
                fiche_scr.doModal()
                del fiche_scr


class Salle(xbmcgui.Window):
    def __init__(self, num="C0002", nom="Rex"):
        xbmcgui.Window.__init__(self)
        #self.setCoordinateResolution(6)

        self.NumSalle=num
        try:
            self.NomSalle, self.Adresse, self.films=litSalle(self.NumSalle)
        except:
            self.NomSalle="Nom de la salle non renseigné"
            self.Adresse="Adresse non renseignée"
            self.films=[]

        # Le fond       
        self.addControl(xbmcgui.ControlImage(WIN[0], WIN[1], WIN[2], WIN[3], PICS + BG_SALLE))
        # Le nom de la salle
        self.addControl(xbmcgui.ControlLabel(NSAL[0], NSAL[1], NSAL[2], NSAL[3], self.NomSalle+" ; "+ self.Adresse, alignment=6))
        # Liste des films
        self.FilmListe = xbmcgui.ControlList(SALST[0], SALST[1], SALST[2], SALST[3], 
                                        itemHeight=SALHitem, 
                                        imageWidth= int ((SALHitem-5)/HRATIO), 
                                        imageHeight= SALHitem-5, 
                                        buttonTexture=PICS+LFnofocus, 
                                        buttonFocusTexture=PICS+LFfocus)
        self.addControl(self.FilmListe)
        
        self.setFocus(self.FilmListe)

        #remplissage de la liste
        self.fill_films(self.films)
        

    def fill_films(self, lstfilms):
        #num,titre,image,diffusion,horaire
        for film in lstfilms:
            try:
                thumb=film[2]
            except:
                thumb=DOSSIER_TEMP+"A00000.gif"
                pass
            self.FilmListe.addItem(
                xbmcgui.ListItem(label=film[1], 
                                 #label2=film[3],
                                 thumbnailImage=thumb
                                 ))
    
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        
    def onControl(self, control):
        if control == self.FilmListe:
            item = self.FilmListe.getSelectedItem()
            nb = self.FilmListe.getSelectedPosition()
            Numero = self.films[nb][0]
            Titre = self.films[nb][1]
            fiche_scr = Fichefilm(numero=Numero, titre=Titre, Horaire=self.films[nb][4], flagsalle=True)
            fiche_scr.doModal()
            del fiche_scr        


#############
# I N F O S #   
#############

class Infos(xbmcgui.Window):
    def __init__(self, SHOW=True):
        xbmcgui.Window.__init__(self)
        #self.setCoordinateResolution(6)

        #fond ecran
        self.addControl(xbmcgui.ControlImage(WIN[0], WIN[1], WIN[2], WIN[3], PICS+BG_INFOS))
        #une fenêtre de texte
        self.txt1 = xbmcgui.ControlTextBox(INFTXT[0], INFTXT[1], INFTXT[2], INFTXT[3], INFTXTf, INFTXTc)
        self.addControl(self.txt1)
        try:
            f=open(HOME+'infos.txt', 'r')
            infotxt=f.read()
            f.close()
            self.txt1.setText(infotxt)
        except:
            self.txt1.setText("En cours de construction")
        self.setFocus(self.txt1)


    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()


class TextDialog(xbmcgui.WindowDialog):
    def __init__(self,titre,text):
        xbmcgui.WindowDialog.__init__(self)

        self.diff=ANIM*(720-QZBG[0])

        self.panel=xbmcgui.ControlImage(TDCOORD[0]+self.diff, TDCOORD[1], TDCOORD[2], TDCOORD[3], PICS+TDPANEL)
        self.addControl(self.panel)

        self.titre=xbmcgui.ControlLabel(TDTIT[0]+self.diff, TDTIT[1], TDTIT[2], TDTIT[3], titre, TDTITf, TDTITc, alignment=6)
        self.addControl(self.titre)

        self.libelle = xbmcgui.ControlTextBox(TDTXTBOX[0] +self.diff, TDTXTBOX[1], TDTXTBOX[2], TDTXTBOX[3], QZQfont, QZQc)
        self.addControl(self.libelle)
        self.libelle.setText(text)
        self.setFocus(self.libelle)

    def show_panel(self):
        for pos in  range(STEP, -1, -1):
            time.sleep(0.01)
            self.animation(pos)

    def animation(self, pct):
        elmt_step=float(self.diff)/float(STEP)
        
        delta = int(pct*elmt_step)
        self.panel.setPosition(TDCOORD[0]+delta, TDCOORD[1])
        self.titre.setPosition(TDTIT[0]+delta, TDTIT[1])
        self.libelle.setPosition(TDTXTBOX[0] + delta, CHLST[1])

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            if ANIM == 1:
                for pos in range(0, STEP, 1):
                    time.sleep(0.01)
                    self.animation(pos)
            self.close()


#############
# Q U I Z Z #
#############

class QUIZZ(xbmcgui.WindowDialog):
    def __init__(self):
        xbmcgui.WindowDialog.__init__(self)
        #self.setCoordinateResolution(6)

        self.diff=ANIM*(720-QZBG[0])#

        #fond ecran
        self.panel=xbmcgui.ControlImage(QZBG[0]+self.diff, QZBG[1], QZBG[2], QZBG[3], PICS+QuizzBkgnd)
        self.addControl(self.panel)
        # Un petit titre
        self.strTitre = xbmcgui.ControlLabel(QZTIT[0]+self.diff, QZTIT[1], QZTIT[2], QZTIT[3], 'Le Quizz de MyCine', QZTfont, QZTc, QZTc, 6, 0)
        self.addControl(self.strTitre)
        #question
        self.libelle = xbmcgui.ControlTextBox(QZLIB[0]+self.diff, QZLIB[1], QZLIB[2], QZLIB[3], QZQfont, QZQc)
        self.addControl(self.libelle)
        self.libelle.setText("Il n'y a pas de question disponible !")
        #bouton réponse
        self.img_btn_rep=xbmcgui.ControlImage(QZREP[0]+self.diff, QZREP[1], QZREP[2], QZREP[3], OKBUTTON)
        self.addControl(self.img_btn_rep)

        dialog = xbmcgui.DialogProgress()
        dialog.create('MyCine : Le Quizz', 'Récupération d\'une question aléatoire...', 'Veuillez patienter...')
        try:
            self.question, self.lien=quizz()
            self.libelle.setText(self.question)
            #self.setFocus(self.repondre)
        except:
            pop("QUIZZ", "Pas de question disponible")
        dialog.close()

    def show_panel(self):
        for pos in  range(STEP, -1, -1):
            time.sleep(0.01)
            self.animation(pos)

    def animation(self, pct):
        elmt_step=float(self.diff)/float(STEP)
        
        delta = int(pct*elmt_step)
        self.panel.setPosition(QZBG[0]+delta, QZBG[1])
        self.strTitre.setPosition(QZTIT[0]+delta, QZTIT[1])
        self.libelle.setPosition(QZLIB[0]+delta, QZLIB[1])
        self.img_btn_rep.setPosition(QZREP[0]+delta, QZREP[1])

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            if ANIM == 1:
                for pos in range(0, STEP, 1):
                    time.sleep(0.01)
                    self.animation(pos)
            self.close()
        if action == ACTION_SELECT_ITEM:
            exp="""http://www.allocine.fr/(.*?)=(.*?).html"""
            try:
                infos=self.lien.split("=")
                typefiche=infos[0]
                num=infos[1].split(".")[0]
                if typefiche=="http://www.allocine.fr/personne/fichepersonne_gen_cpersonne":
                    fiche=FichePerso(actid=num)
                    if ANIM == 1:
                        for pos in range(0, STEP, 1):
                            time.sleep(0.01)
                            self.animation(pos)
                    self.close()
                    fiche.doModal()
                    del fiche
                elif typefiche=="http://www.allocine.fr/film/fichefilm_gen_cfilm":
                    fiche=Fichefilm(numero=num, titre='', Horaire="", flagsalle=False)
                    if ANIM == 1:
                        for pos in range(0, STEP, 1):
                            time.sleep(0.01)
                            self.animation(pos)
                    self.close()
                    fiche.doModal()
                    del fiche
            except:
                pop("Mycine : Le Quizz", "Problème avec %s"%self.lien)


###################
# Diaporama film  #
###################

class diapos(xbmcgui.WindowDialog):
    def __init__(self, filmID, ref, lstPhotos=[], titre="Diaporama"):
        xbmcgui.WindowDialog.__init__(self)
        #self.setCoordinateResolution(6)
        self.diff=ANIM*(740-DFIMG[0])#animation initialisée

        self.filmID=filmID
        self.ref=ref
        self.lstPhotos=lstPhotos
        self.selectedpic=0
        self.maxpic=len(self.lstPhotos)

        #fond de liste
        self.panel=xbmcgui.ControlImage(DFIMG[0]+self.diff, DFIMG[1], DFIMG[2], DFIMG[3], PICS+FondDiapo)
        self.addControl(self.panel)
        #titre
        self.titre=xbmcgui.ControlLabel(DFTIT[0]+self.diff, DFTIT[1], DFTIT[2], DFTIT[3], titre, DFTITf, DFTITc, alignment=6)
        self.addControl(self.titre)
        #credit photo
        self.credit=xbmcgui.ControlFadeLabel(DFCRED[0]+self.diff, DFCRED[1], DFCRED[2], DFCRED[3], DFCREDf, DFCREDc, alignment=6)
        self.addControl(self.credit)
        #aide
        self.aide=xbmcgui.ControlLabel(DFAID[0]+self.diff, DFAID[1], DFAID[2], DFAID[3], DFAIDstr, DFAIDf, DFAIDc, alignment=6)
        self.addControl(self.aide)
        

        #télécharge la première image
        try:
            picfile = self.DL_pic(self.lstPhotos[0][0])#renvoi le chemin complet de l'image
        except:
            pop("MyCine: photos", "Photos indisponibles")
            self.close()
        
        #puis l'ajoute à l'ecran
        if picfile:
            self.change_photo(picfile)#, width , height)
        else:
            pop("MyCine : photos", "Erreur lors du dimensionnement...")
            self.close()
        try:
            s = self.lstPhotos[0][1].decode("utf-8")
            s = s.replace("\\r","")
            s = s.replace("\\n","")
            self.credit.addLabel(s)
        except:
            pass

    def DL_pic(self, relUrl):
        url = "http://a69.g.akamai.net/n/69/10688/v1/img5.allocine.fr/acmedia/rsz/434/x/x/x/medias" + relUrl
        try:
            filename = "mpi" + os.path.basename(url)
            downloadJPG(url,DOSSIER_TEMP + filename)
            return filename
        except:
            print "PHOTOS : erreur de donwloadJPG"
            return None
        
    def get_size_pic(self, picfile, maxW=DFmaxW, maxH=DFmaxH):
        #utilise les valeur max DFmaxW et DFmaxH par défaut, sinon des largeur/hauteur max peuvent être envoyées
        im = Image.open(DOSSIER_TEMP+picfile)
        width, height=im.size
        height = height * HRATIO
        #rapport des largeurs
        qw=float(width)/float(maxW)
        #rapport des hauteurs
        qh=float(height)/float(maxH)
        #retient le plus gros coeff
        coeff=max(qw, qh)
        #redimensionne l'image avec le coeff
        wpic=int(width/coeff)
        hpic=int(height/coeff)

        return wpic, hpic
        
    def change_photo(self, picfile):
        try:
            self.removeControl(self.photo)
        except:
            pass
        picW, picH=self.get_size_pic(picfile)
        self.centrX=(DFmaxW/2)-(picW/2)
        self.centrY=(DFmaxH/2)-(picH/2)
        self.photo=xbmcgui.ControlImage(DFfoto[0]+self.diff+self.centrX, DFfoto[1]+self.centrY, picW, picH, DOSSIER_TEMP+picfile)
        self.addControl(self.photo)
        
    def show_panel(self, show=True):
        if ANIM == 1:
            if show:
                for pos in  range(STEP, -1, -1):
                    time.sleep(0.01)
                    self.animation(pos)
            else:
                for pos in range(0, STEP, 1):
                    time.sleep(0.01)
                    self.animation(pos)

    def animation(self, pct):
        elmt_step=float(self.diff)/float(STEP)
        
        delta = int(pct*elmt_step)
        self.panel.setPosition(DFIMG[0]+delta, DFIMG[1])
        self.titre.setPosition(DFTIT[0]+delta, DFTIT[1])
        self.credit.setPosition(DFCRED[0]+delta, DFCRED[1])
        self.photo.setPosition(DFfoto[0]+delta+self.centrX, DFfoto[1]+self.centrY)
        self.aide.setPosition(DFAID[0]+delta, DFAID[1])

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU :
            self.show_panel(False)
            self.close()
        if action == ACTION_MOVE_LEFT:
            #masque le panel
            self.show_panel(False)
            #déplace le focus de liste
            if self.selectedpic==0:
                self.selectedpic=self.maxpic-1
            else:
                self.selectedpic-=1
            #récupère la nouvelle image
            picfile=self.DL_pic(self.lstPhotos[self.selectedpic][0])
            #met à jour le control image
            self.change_photo(picfile)
            #met à jour les crédits
            self.credit.reset()
            s = self.lstPhotos[self.selectedpic][1].decode("utf-8")
            s = s.replace("\\r","")
            s = s.replace("\\n","")
            self.credit.addLabel(s)
            #affiche le panel
            self.show_panel(True)
        if action == ACTION_MOVE_RIGHT:
            #masque le panel
            self.show_panel(False)
            #déplace le focus de liste
            if self.selectedpic==self.maxpic-1:
                self.selectedpic=0
            else:
                self.selectedpic+=1
            #récupère la nouvelle image
            picfile=self.DL_pic(self.lstPhotos[self.selectedpic][0])
            #met à jour le control image
            self.change_photo(picfile)
            #met à jour les crédits
            self.credit.reset()
            s = self.lstPhotos[self.selectedpic][1].decode("utf-8")
            s = s.replace("\\r","")
            s = s.replace("\\n","")
            self.credit.addLabel(s)
            #affiche le panel
            self.show_panel(True)
        if action == ACTION_SELECT_ITEM:
            self.show_panel(False)
            picfile=self.DL_pic(self.lstPhotos[self.selectedpic][0])
            W, H=self.get_size_pic(picfile, DFzoom[2], DFzoom[3])
            aff=Affiche(img=DOSSIER_TEMP+picfile, pos=[DFzoom[0]+(DFzoom[2]/2)-(W/2), DFzoom[1]+(DFzoom[3]/2)-(H/2), W, H])
            aff.doModal()
            del aff
            self.show_panel(True)


###################
# Dialog de choix #
###################

class choix(xbmcgui.WindowDialog):
    def __init__(self, titre="Choisir", leschoix=[], paneau=CHDEFPANEL, coord=CHDEFCOORD):
        xbmcgui.WindowDialog.__init__(self)
        #self.setCoordinateResolution(6)

        self.choix=leschoix
        self.retour=None
        self.coord=coord

        self.diff=ANIM*(720-coord[0])#
        
    
        #fond de liste
        self.panel=xbmcgui.ControlImage(self.coord[0]+self.diff, self.coord[1], self.coord[2], self.coord[3], PICS+paneau)
        self.addControl(self.panel)
        #titre
        self.titre=xbmcgui.ControlLabel(CHTIT[0]+self.diff, CHTIT[1], CHTIT[2], CHTIT[3], titre, CHTITf, CHTITc, alignment=6)
        self.addControl(self.titre)
        #liste des choix
        self.lst_choix=xbmcgui.ControlList(CHLST[0]+self.diff, CHLST[1], CHLST[2], CHLST[3], itemHeight=CHLSTh)
        self.addControl(self.lst_choix)
        #remplissage de la liste
        for ch in self.choix:
            self.lst_choix.addItem(ch)
        
        self.setFocus(self.lst_choix)

        
    def show_panel(self):
        for pos in  range(STEP, -1, -1):
            time.sleep(0.01)
            self.animation(pos)

    def animation(self, pct):
        elmt_step=float(self.diff)/float(STEP)
        
        delta = int(pct*elmt_step)
        self.panel.setPosition(self.coord[0]+delta, self.coord[1])
        self.titre.setPosition(CHTIT[0]+delta, CHTIT[1])
        self.lst_choix.setPosition(CHLST[0]+delta, CHLST[1])


    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            if ANIM == 1:
                for pos in range(0, STEP, 1):
                    time.sleep(0.01)
                    self.animation(pos)
            self.close()

    def onControl(self, control):
        if control==self.lst_choix:
            self.retour=self.lst_choix.getSelectedPosition()
            if ANIM == 1:
                for pos in range(0, STEP, 1):
                    time.sleep(0.01)
                    self.animation(pos)
            self.close()

class Affiche(xbmcgui.WindowDialog):
    def __init__(self, img, pos=AFFZOOM):
        xbmcgui.WindowDialog.__init__(self)
        #self.setCoordinateResolution(6)
        self.addControl(xbmcgui.ControlImage(WIN[0], WIN[1], WIN[2], WIN[3], PICS+AffFond))
        self.addControl(xbmcgui.ControlImage(pos[0], pos[1], pos[2], pos[3], img))        
    def onAction(self, action):
        #if action == ACTION_PREVIOUS_MENU or action == ACTION_X:
        self.close()

#######################################################################################################################    
class RssReader: # thanks to "someone" (I don't know who !) who made this class in rss.py script
    def __init__(self):
        self.news = []
    def parsexml(self, line, tag):
        result= re.search('<' + tag + '>.*' + tag + '>', line, re.DOTALL)
        try:
            if result.group(0):
                mod = string.replace(result.group(0), '<' + tag + '>', '')
                mod = string.replace(mod, '</' + tag + '>', '')
                mod = string.lstrip(mod)
                return mod
        except:
            return
    def getNews(self, url):
        try:
            data = urllib.urlopen(url)
        except:
            return ['Cannot open '+url+' URL !']
        items = string.split(data.read(), '<item>')
        for item in items:
            self.news.append(self.parsexml(item, 'title'))
        return self.news

def checkConnexion():
    dialog = xbmcgui.DialogProgress()
    dialog.create('MyCine : Test de connexion', 'Test de la résolution des noms en IP et de la résolution des IP en noms', 'Veuillez patienter...')
    pingdns=ping("www.allocine.fr")
    pingip=ping("212.73.231.111")
    dialog.close()
    if not(pingdns and pingip):
        pop("My Cine: Erreur", "Votre connexion internet est mal configurée")


#############################################################################################
#############################################################################################

def start():
    global updatingLauncher
    if updatingLauncher == 1:
        return
    
    #checkConnexion()

    verifrep(DOSSIER_TEMP)

    menu = Menu()
    menu.doModal()
    del menu

    # Nettoyage des fichiers temporaires
    removeOlder(DOSSIER_TEMP,10,"jpg")

updatingLauncher = 0
try:
    #import MyCineUpdater
    #updatingLauncher = MyCineUpdater.updateLauncher()
    pass
except:
    pass
