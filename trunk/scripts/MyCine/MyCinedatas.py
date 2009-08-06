# -*- coding: iso-8859-1 -*-

#version = 151105
        ###########
        # S K I N #
        ###########
#Toutes les positions et dimensions des objets sont
# données pour un écran PAL 720x576.
#Elles seront automatiquement redimensionnées pour
# s'adapter à la résolution de l'ecran de l'utilisateur.

#Taille plein ecran (ne doit à priori pas être changé)
#peut être réutilisé pour donner la taille d'écran à d'autres variables
WIN     =   [0,0,720,576]

# G E N E R A L

# animation des menus popup
ANIM=1 #mettre à 0 pour désactiver l'animation
STEP=10 #nombre de pas pour faire disparaitre/apparaitre
        #  plus la valeur est faible, plus le menu appraitra/disparaitra rapidement

#   textures par défaut pour les boutons
FOCUSbtn    = 'bouton_on.png'
NOFOCUSbtn  = 'bouton_off.png'

#   arrières plans
BG_SORTIES   = 'bg1.png'# fond de liste des sorties
BG_BO        = 'bg1.png'# fond de liste des BO
BG_SEARCH    = 'bg1.png'# fond de recherche (voir si utilisé)
BG_SALLE     = 'bg1.png'# fond des salles (voir si utilisé)
BG_INFOS     = 'bg1.png'# fond de l'écran information



# H O M E   S C R E E N

## UTILISER cette variable pour indiquer le genre des boutons du HOME screen
#   USE_TEXTURE = -1  --> utilise les textures ET les labels
#   USE_TEXTURE = 0   --> utilise les labels SEULS
#   USE_TEXTURE = 1   --> utilise les textures SEULES
USE_TEXTURE=-1 
#   arrière plan
BG_HOME = 'background-mycine.png'
#   positions des boutons
FBP1    = [97, 229, 14, 14] 
FBP2    = [97, 270, 14, 14] 
FBP3    = [97, 309, 14, 14] 
FBP4    = [97, 350, 14, 14] 
FBP5    = [97, 387, 14, 14] 
FBP6    = [71, 434, 14, 14] 
FBP7    = [211, 434, 14, 14]
#   textures des boutons
#       quand FOCUS=ON
ONBP1   = 'home-focus.gif'
ONBP2   = 'home-focus.gif'
ONBP3   = 'home-focus.gif'
ONBP4   = 'home-focus.gif'
ONBP5   = 'home-focus.gif'
ONBP6   = 'home-focus.gif'
ONBP7   = 'home-focus.gif'
#       quand FOCUS=OFF
OFFBP1  = 'homebutton-small.png'
OFFBP2  = 'homebutton-small.png'
OFFBP3  = 'homebutton-small.png'
OFFBP4  = 'homebutton-small.png'
OFFBP5  = 'homebutton-small.png'
OFFBP6  = 'homebutton-small.png'
OFFBP7  = 'homebutton-small.png'
#   labels des boutons
TXTBP1  = '       Sorties au Cinéma'     
TXTBP2  = '       Les Box-Offices'     
TXTBP3  = '       Actualités'    
TXTBP4  = '       Ma salle'         
TXTBP5  = '       Infos'          
TXTBP6  = '    Le Quizz'          
TXTBP7  = '    Rechercher'
#   fonts des labels
TXTf    = "special13"
#   images contextuelles selon focus sur l'accueil
clipart = ['semaine3.png',   # bouton 1
           'bof3.png',       # bouton 2
           'hd3.png',     # bouton 3
           'masalle3.png',    # bouton 4
           'info3.png',   # bouton 5
           'quizz3.png'  ,      # bouton 6
           'search3.png']      # bouton 7
#   positions des images contextuelles
#(utiliser WIN pour prendre la taille ecran défini précédemment)
PC={} 
PC[0]   =   WIN
PC[1]   =   WIN
PC[2]   =   WIN
PC[3]   =   WIN
PC[4]   =   WIN
PC[5]   =   WIN
PC[6]   =   WIN


# L I S T E   D E   F I L M S

#   position du titre
TLF0     = [140,110,150,30]
TLF1     = [280,110,150,30]
TLF2     = [420,110,150,30]
#   positions de la liste des films
LFPList = [137,142,446,406]
#   hauteur des éléments des listes de films
LFHitem   = 125 #hauteur par défaut
LFHBO     = 50 #hauteur des items de bande annonce
LFHSearch = 30 #hauteur des items de recherches
#   texture d'un item sans focus
LFnofocus = ''
#   texture de l'item qui a le focus
LFfocus = 'select2.png'
#   couleur du texte des listes
LFselc  = '0xFF115599'
#   couleur du texte de l'item qui a le focus
LFtxtc  = '0xFFEEEEEE'

# V I D E O S   H D

#   arrière plan
BG_HD        = 'bg1.png'
#   position du titre
THD     = [240,110,240,30]
#   positions de la liste des videos
HDPList = [137,142,446,406]
#   hauteur des éléments de la liste
HDHitem = 60

# F I C H E   D E   F I L M

#   arrière plan
FondFicheFilm = 'mycine_fiche.png'
#   Fonts
FFf_titre   = 'special13'#titre du film
FFf_titreO  = 'special12'#titre original du film
FFf_label   = 'font13'#Etiquettes
FFf_value   = 'special13'#valeurs
FFf_synhor  = 'font12'#Synopsis/horaires
#   couleurs
FFc_titre   = '0xFFF2F44B'#titre du film
FFc_titreO  = '0xBBF2F44B'#titre original du film
FFc_label   = '0xFFEEEEEE'#Etiquettes
FFc_value   = '0xFFAAAAAA'#valeurs
FFc_synhor  = '0xFFFFFFFF'#Synopsis/horaires
#   position globale de l'ensemble
#     (les autres coordonnées seront relatives à cette position)
FFPGX,FFPGY = 185,122
#       positions relatives à PGX et PGY:
#   titre du film
FFTIT   = [0,-13,450,20]
#   titre Original du film
FFTITO  = [0,7,450,20]
#   alignement des titres:
        #gauche = 0
        #droite = 1
        #centréX = 2
        #centréY = 4
        #tronqué = 8
FFTITalign = 0 
#   affiche
AFF     = [0,35,120,160]
#   affiche Zoom
AFFZOOM = [160,35,263,350]
#   date de sortie
FFdat   = [130,35,100,20]#label
FFDAT   = [230,30,190,20]#valeur
#   réalisateur
FFrea   = [130,60,100,20]#label
FFREA   = [230,60,150,25]#bouton
FFreaLbl= 'Réalisateur'
#   Casting
FFcast  = [130,85,100,20]#label
FFCAST  = [230,85,150,25]#bouton
FFcastLbl = 'Voir le Casting'
#   genre
FFgen   = [130,110,100,20]#label
FFGEN   = [230,110,200,20]#valeur
#   durée
FFdur   = [130,130,100,20]#label
FFDUR   = [230,130,190,20]#valeur
#   box office France
FFbofrance  = [130,150,100,20]#label
FFBOFRANCE  = [230,150,190,20]#valeur
#   Note presse/public
FFNOT   = [130,170,250,20]
#   Synopsis / horaires
#FFSHL   = [-140,200,100,20]#label
FFSHT   = [81,250,404,160]#texte
#   Bouton de BA
FFBBA    = [130,205,100,25]
FFBBALbl    = '  Vidéos' #texte du bouton
FFBBAfocus  = 'bouton_play_on.png'
FFBBAnofocus= 'bouton_play_off.png'
#   Bouton de Synopsis/secrets
FFBHO    = [260,205,100,25]
FFBHOLblSec = 'Anecdotes' #texte du bouton pour les secrets
FFBHOLblSyn = '  Synopsis' #texte du bouton pour synopsis
FFBHOfocus  = 'bouton_on.png'
FFBHOnofocus= 'bouton_off.png'


# F I C H E   D E S   P E R S O N N A L I T E S

#   arrière plan
FondFichePerso  = "mycine_perso.png"
#   fonts
FPfnom  = 'special13'#nom du perso
FPflbl  = 'font13'#les divers infos
FPfbio  = 'font13'#la bio
#   couleurs
FPcnom  = '0xFFF2F44B'#nom du perso
FPclbl  = '0xFFAAAAAA'#les divers infos
FPcbio  = '0xFFFFFFFF'#la bio
#   position globale de l'ensemble
#     (les autres coordonnées seront relatives à cette position)
FPPGX,FPPGY = 185,122
#   photo
FPPIC   = [0,35,120,160]
#   Zoom photo
FPPICZOOM= [160,35,263,350]
#   nom du personnage
FPNOM   = [0,0,360,20]
#   alignement du titre (nom) :
        #gauche = 0
        #droite = 1
        #centré X = 2
        #centré Y = 4
        #tronqué = 8
FPNOMalign = 0
#   etat civil du personnage
FPEC    = [130,40,340,20]
#   Fonctions de la personne
FPFONC  = [130,70,340,20]
#   Biographie
FPBIO   = [81,215,404,203]
#   bouton pour les films cités
FPBF    = [150,130,170,30]
FPBFlbl = '  Films cités'
#   bouton pour les personnages cités
FPBP    = [150,165,170,30]
FPBPlbl = '  Personnages cités'


# E C R A N   M A   S A L L E

#   image de fond
#configurer plus haut dans les backgrounds
#   Nom de la salle
NSAL    = [160,115,376,20]
#   Liste des films
SALST   = [137,142,446,406]
#   hauteur des éléments de liste
SALHitem = 125



# Q U I Z Z (popup question)

#   texte question
QZLIB   = [262,220,353,187]
#   couleur question
QZQc = '0xFFFFFFFF'
#   font de la question
QZQfont = 'font13'
#   titre quizz
QZTIT   = [247,170,390,20]
#   font du titre
QZTfont = 'font13'
#   couleur du titre
QZTc = '0xFFFFFFFF'
#   image suppl
QZREP   = [338,300,90,25]
#   fichier image supplementaire
OKBUTTON    = ""
#   fichier image background
QuizzBkgnd  = "panel1.png"
#   position image background
QZBG    = [212,100,505,356]


# D I A P O R A M A

#   image de fond du diaporama
FondDiapo   = "context2.png"
#   position de l'image
DFIMG   = [185,63,425,500]
#   titre
DFTIT   = [205,87,185,30]
#   couleur du titre
DFTITc  = '0xFFF2F44B'
#   font du titre
DFTITf  = 'font13'
#   position de la photo
DFfoto  = [215,115]
#   dimensions maxi de la photo
#      (la photo sera adapté en largeur et hauteur pour ne jamais dépasser
#       ces valeurs tout en conservant le ratio original de l'image)
DFmaxW=375
DFmaxH=355
#   dimensions pour zoom photo
DFzoom = [20,20,680,536]
#   Crédits photo
DFCRED  = [210,480,395,30]
#   couleur des credits
DFCREDc = '0xFFFFFFFF'
#   font des credits
DFCREDf = 'font13'
#   Aide
DFAID   = [200,505,405,20]
#   couleur de l'aide
DFAIDc  = '0xFFB6B6B6'
#   font de l'aide
DFAIDf  = 'font13'
#   texte d'aide
DFAIDstr= "             "
#   fond d'affiche mode zoom :
AffFond = "bgphotos.png"


# C H O I X (liste d'items)

#   image du fond des choix
CHDEFPANEL  = "context.png" #image par défaut
#   position de l'image
CHDEFCOORD  = [185,63,505,405] #position par défaut 
#   titre
CHTIT   = [295,87,320,30]
#   couleur du titre
CHTITc  = '0xFFFFFFFF'
#   font du titre
CHTITf  = 'font13'
#   liste des choix
CHLST   = [206,160,472,275]
#   hauteur des items de la liste des choix
CHLSTh  = 20



# I N F O S

#   fenêtre de texte
INFTXT  = [160,150,400,390]
#   couleur de la fenetre texte
INFTXTc = '0xFFFFFFFF'
#   font de la fenêtre texte
INFTXTf = 'font13'



# LES FENETRES ACTIVES

#   position du label
ACTWIN  = [100,100,50,30]
#   image de fond
ACTBG   = ""
#   font
ACTWINf = 'font13'
#   couleur (0x00.... = invisible)
ACTWINc = '0x00FFFFFF'

# D I V E R S





# R S S

#   position du label
RSSp    = [60,500,600,30]
#   font
RSS_FONT = 'font13'
#   couleur
RSS_COLOR = '0x88FFFFFF'
#   url
#RSS_URL = "http://www.cinemovies.fr/webmaster/filmfr_rss.php"
#RSS_URL = "http://www.cinereporter.com/rss/blog_semaine_prochaine.aspx"
RSS_URL = "http://www.nord-cinema.com/rss.php"
#   titre du flux
RSS_TITLE = "Les sorties cinéma cette semaine"

##################
# END   SKINNING #
##################
#'''



# TextDialog

TDPANEL  = "context.png"
#   position de l'image
TDCOORD  = [100,63,505,405] 
#   titre
TDTIT   = [210,87,320,30]
#   couleur du titre
TDTITc  = '0xFFFFFFFF'
#   font du titre
TDTITf  = 'font13'
#   liste des choix
TDTXTBOX   = [131,160,452,275]

#	Listes etendues
MOVIE_EXTLIST = [150,145,420,100]
ADVERT_EXTLIST = [250,300,200,30]
TRAILERS_ITEM_DISPLAYED_EXT_LIST = 4
BOXOFFICE_ITEM_DISPLAYED_EXT_LIST = 5
BOXOFFICE_ITEM_SPACING_EXT_LIST = 4
FLASHES_ITEM_DISPLAYED_EXT_LIST = 7
FLASHES_ITEM_SPACING_EXT_LIST = 9
THEATER_ITEM_DISPLAYED_EXT_LIST = 3
SECRETS_ITEM_DISPLAYED_EXT_LIST = 5
