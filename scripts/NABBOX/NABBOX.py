# -*- coding: cp1252 -*-
"""
Nabbox core
09-10-08 Version 1.0 by temhil
    - Added cp1252 encoding
    - Saved file to UNIX(LF) format
    - Change default parameter for saving page as false (it was true) and 
      added to few functions this parameter in order user of API can decide if he wants to cache or not file  
21-06-08 Version Beta5 by Alexsolex
    - Creation: this module provide an API to retrieve, extract and format data form the Webiste site 'www.nabbox.com'
"""
import urllib,urllib2,re,os.path
import htmllib
import cookielib

cookiejar = cookielib.CookieJar()

HTMLFOLDER = ""
#HEADERS = { 'User-Agent': 'Mozilla/5.0 (iPhone; U; XXXXX like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/241 Safari/419.3' }
#une autre solution pour le header, celui de firefox 3



class ConnectError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
        
        
class SearchError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
        
        
def unescape(s):
    """
    remplace les séquences d'échappement par leurs caractères équivalent
    """
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()
    
    
def parse_params(url):
    """
    parse l'url fournie pour recréer le dictionnaire des paramètres POST
    Retourne :
        - path : le chemin de l'url
        - params : un dictionnaire[cle]=valeur des paramètres
        ex: http://www.nabbox.com/index.php?showtopic=10861&st=60&start=60
        donne : path = http://www.nabbox.com/index.php
        et params = {"showtopic"="10861","st"="60","start"="60"}
    """
    url=url.replace("&amp;","&")
    
    path,paramstring=url.split("?")
    params={}
    for parametre in paramstring.split("&"):
        try:
            cle,valeur=parametre.split("=")
            params[cle]=valeur
        except:
            pass
    return path,params
    
    
def is_connected(html):
    """
    Renvoi l'état de connexion au forum
    """
    if html.find('<input type="hidden" name="act" value="Login" />')>0:
        return False
    else:
        return True
        
        
def connexion(login,password,savehtml=True):
    """
    Procède Ã  l'authentification et renvoi un ID de session
    """
    print "connexion - savehtml = "
    print savehtml
    #A FAIRE : réaliser un test afin de ne pas se reconnecter inutilement
    if not(login):
        raise ConnectError,"Veuillez configurer votre login NABBOX"
    if not(password):
        raise ConnectError,"Veuillez configurer votre mot de passe NABBOX"
    #téléchargement de la page d'accueil pour la session
    #urllib2.urlopen("http://www.nabbox.com/").read()
    indexHTML = get_page({}, savehtml, filename="index.html",check_connexion=False)
    
    #récupération de l'url du formulaire de connexion
    exp=re.compile(r'<form action="(.*?act=Login.*?)".*?>(?:\s|.)*?</form>')
    formulaires = exp.findall(indexHTML)
    urlform=formulaires[0]
    #mise en forme correcte de l'URL : on remplace les &amp; par leurs équivalents : &
    #urlform=urlform.replace("&amp;","&")
    
    #maintenant on 'découpe' l'url du formulaire pour en extraire les paramètres
    #ces paramètres sont alors stockés dans un dictionnaire
    path,params = parse_params(urlform)
    
    #on ajoute aux paramètres les login et password
    params["UserName"]=login
    params["PassWord"]=password
    
    #maintenant on effectue une requête POST valide pour se connecter
    #html = urllib2.urlopen(path,urllib.urlencode(params)).read()
    html = get_page(params, savehtml, filename="connexion.html",check_connexion=False)
    
    #on trouve le lien de redirection
    #(a voir si c'est utile)
    exp=re.compile(r'\(<a href="(.*?)">Ou cliquez ici si vous ne souhaitez pas attendre</a>\)')
    urlredirect = exp.findall(html)
    if urlredirect==[]:
        raise ConnectError,"L'authentification a échouée (redirection non trouvée)"
    urlredirect = urlredirect[0].replace("&amp;","&")
    #on traite les paramètres du lien
    path,params=parse_params(urlredirect)
    
    #on suis la redirection en téléchargeant la nouvelle page
    html = get_page(params, savehtml, filename="redirection post-connexion.html")
    
    #print "Vous êtes connecté au forums NABBOX sour l'ID de session '%s'"%params["s"]
    return params["s"] #on retourne l'ID de session
    
    
def make_answer(sessionID,forumID,topicID,message="Merci pour tout !", savehtml=True):
    """
    Envoie le message de remerciement 'message'
        sur le topic 'topicID'
        du forum 'forumID'
        sous la session 'sessionID'
    Retourne le code html du topic après remerciement
    """
    params={} #init du dictionnaire
    #on recréé le dictionnaire
    params["s"]=sessionID
    params["act"]="post"
    params["do"]="reply_post"
    params["f"]=forumID#params["f"]="54"
    params["t"]=topicID#params["t"]="10919"
    #on télécharge la page :
    html = get_page(params, savehtml)    #voilÃ , nous avons la page de réponse,
    #maintenant on parse le formulaire de message
    #on le récupère
    exp=re.compile(r"(?s)<form id='postingform'.*?>(.*?)</form>")
    formdata = exp.findall(html)[0]
    #formdata contient maintenant le contenu du formulaire
    #on parse les input hidden du formulaire
    #   (je ne sais pas si c'est utile mais au moins, ca marche et c'est fait !)
    exp=re.compile(r"<input type='hidden' name='(.*?)' value='(.*?)' />")
    inputHidden=exp.findall(formdata)
    #on ajoute les input hidden au dictionnaire
    params={}
    for cle,valeur in inputHidden:
        params[cle]=valeur
    #on ajoute ces quelques valeurs d'input supplémentaires
    params["iconid"]="0" #certainement pour mettre une icone (7 choix apriori)
    params["Post"]=message #on met notre message de remerciement ici
    params["s"]=sessionID #NON TESTE !!!! on ajoute l'ID de session
    # on envoie le formulaire en téléchargeant la page de la requête
    html = get_page(params, savehtml, filename="réponse envoyée topic %s.html"%topicID)
    return html
    
    
def hook(blockscount,blocksize,totalsize):
    #print (blockscount*blocksize)
    pass
    
    
def get_page(params,savehtml=True,filename="defaut.html",check_connexion=True):
    """
    télécharge la page index avec les paramètres fournis :
        params : dictionnaire de paramètres
    Renvoi le code html de la page
    """
    h=urllib2.HTTPHandler(debuglevel=0)
    #h=urllib2.HTTPCookieProcessor(cookiejar)
    request = urllib2.Request("http://www.nabbox.com/index.php",urllib.urlencode(params))
    request.add_header('Referer', 'http://www.nabbox.com')
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9) Gecko/2008052906 Firefox/3.0')
    request.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    request.add_header('Accept-Language','fr,fr-fr;q=0.8,en-us;q=0.5,en;q=0.3')
    request.add_header('Accept-Charset','ISO-8859-1,utf-8;q=0.7,*;q=0.7')
    request.add_header('Keep-Alive','300')
    request.add_header('Connection','keep-alive')
    
    opener = urllib2.build_opener(h)
    urllib2.install_opener(opener)
    html = opener.open(request).read()
    if savehtml == True:
        open(os.path.join(HTMLFOLDER, filename),"w").write(html)
##    F,H=urllib.urlretrieve( "http://www.nabbox.com/index.php", os.path.join(HTMLFOLDER, filename), hook , urllib.urlencode(params)) #F : filename et H: headers
##    html = open(F).read()
##    #html = open(os.path.join(HTMLFOLDER, filename)).read()
    if check_connexion and not(is_connected(html)):
        return ""
    else:
        return html
        
        
def get_liens(html,ext="avi|mpg|flv|mov|mp4|mpeg|divx|wmv|mkv|zip|rar"):
    """
    Recherche les liens dans un topic. Utilise les extensions fournis pour trouver les urls
        - renvoi -1 si le topic ne contient aucun lien
        - renvoi -2 si le topic présente des liens cachés
        - renvoi les liens si le topic présente des liens activés
    """
    if len(html)==0:
        return ["Vous n'êtes pas connecté."]
    if html.count("<img src='style_images/nabbox-v3/hidden.gif'border='0'  alt='Contenu caché' />")>0:
        #print "Des liens sont cachés dans le topic"
        return -2
    else:
        #exp=re.compile(r'(?i)<a href="(http://[\-._%%/a-zA-Z0-9]*[.](?:%s))" target="_blank">.*?</a>'%ext)
        exp=re.compile(r'(?i)<a href="(http://[\-._%%/a-zA-Z0-9]*[.](?:%s))" target="_blank">.*?</a>'%ext)
        liens=exp.findall(html)
        if len(liens)==0:
            print "Le Topic ne contient aucun lien"
            return -1
        else:
            return liens
            
            
def SearchContentTopics(sessionID, savehtml=True):
    """effectue une recherche des topics avec contenu"""
    params={}
    params["s"]=sessionID
    params["act"]="Search"
    params["CODE"]="01"
    params["keywords"]="\"contenu caché\""
    params["namesearch"]=""
    params["exactname"]=""
    params["searchsubs"]="1"
    params["prune_type"]="newer"  # older
    params["prune"]="0" # 1 , 7 , 30 , 60 , 90 , 180 , 365
    params["sort_order"]="desc" # asc
    params["sort_key"]="" #last_post , posts , starter_name , forum_id
    params["search_in"]="posts" # titles
    params["result_type"]="posts" # topics
    params["forums[]"]="46" # id du forum
    
    html = get_page(params, savehtml, filename="recherche_redirection.html")
    
    exp=re.compile(r'\(<a href="(.*?)">Ou cliquez ici si vous ne souhaitez pas attendre</a>\)')
    urlredirect = exp.findall(html)
    if urlredirect==[]:
        raise SearchError,"La recherche a échouée (redirection non trouvée)"
    urlredirect = urlredirect[0].replace("&amp;","&")
    #on traite les paramètres du lien
    path,params=parse_params(urlredirect)
    
    #on suis la redirection en téléchargeant la nouvelle page
    html = get_page(params, savehtml, filename="redirection post-recherche.html")
    return html
    
    
def get_topics(html):
    """
    liste les sujets d'un forum
    renvoi une liste de tuple pour chaque topic : (urlTopic,titretopic)
    """
    if len(html)==0:
        return [(None,"Vous n'êtes pas connecté.")]
    #exp=re.compile(r'<a id="tid-link-\d*?" href="http://www\.nabbox\.com/index\.php\?s=.*?showtopic=(\d*?)" title=".*?">(.*?)</a>')
    exp=re.compile(r"""<a (?:id=["']{1}tid-link-\d*?["']{1})??\s??href=["']{1}http://www\.nabbox\.com/index\.php\?s=[a-f0-9]*?&amp;showtopic=(\d*?)(?:&amp;view=getnewpost)??(?:&amp;hl=)??["']{1}(?:\s??title=["']{1}.*?["']{1})??>([^<]*?)</a>""")
    
    
    topics = exp.findall(html)
    Topics=[]
    for IDtopic,intitule in topics:
        Topics.append((IDtopic,unescape(intitule)))
    return Topics #[ IDTopic , intitulé) , ...]
    
    
def get_forums(html):
    """
    Recherche les forums dans la page fournie
        -renvoi une liste de tuple (forumID,titre,description)
    """
    if len(html)==0:
        return [(None,"Vous n'êtes pas connecté.","Il est nécessaire de se connecter pour parcourir les forums")]
    exp=re.compile(r'<b><a href="http://www\.nabbox\.com/index\.php\?s=.*?showforum=(\d*?)">(.*?)</a></b>\s*?<br />\s*?<span class="forumdesc">(.*?)\s*?<')
    forums = exp.findall(html)
    Forums = []
    for forumID,titre,description in forums:
        Forums.append((forumID,unescape(titre),unescape(description)))
    return Forums
    
    
def get_page_courante(html):
    """
    retourne le numéro de page courante dans un topic
    """
    if len(html)==0:
        return "Vous n'êtes pas connecté."
    exp=re.compile(r'<span class="pagecurrent">(\d*?)</span>')
    pagecourante = exp.findall(html)
    try:
        return pagecourante[0]
    except:
        return None
    
    
def get_next_page(html):
    """
    récupère le lien de la page suivante dans la page fournie
    """
    if len(html)==0:
        return "Vous n'êtes pas connecté."
    exp=re.compile(r'<a href="(http://www\.nabbox\.com/index\.php\?s=\w*?&amp;showforum=\d*?&amp;prune_day=\d*&amp;sort_by=Z-A&amp;sort_key=last_post&amp;topicfilter=all&amp;st=\d*|http://www\.nabbox\.com/index\.php\?s=\w*?&amp;showtopic=\d*?&amp;st=\d*?)" title="Page suivante">&gt;</a>')
    nextpageURL=exp.findall(html)
    try:
        return nextpageURL[0].replace("&amp;","&")
    except:
        return None
    
    
def get_prev_page(html):
    """
    récupère le lien de la page précédente dans la page fournie
    """
    if len(html)==0:
        return "Vous n'êtes pas connecté."
    exp=re.compile(r'<a href="(http://www\.nabbox\.com/index\.php\?s=\w*?&amp;showtopic=\d*?&amp;st=\d*?|http://www\.nabbox\.com/index\.php\?s=\w*?&amp;showforum=\d*?&amp;prune_day=\d*?&amp;sort_by=Z-A&amp;sort_key=last_post&amp;topicfilter=all&amp;st=0)" title="Page pr&eacute;c&eacute;dente">&lt;</a>')
    nextpageURL=exp.findall(html)
    try:
        return nextpageURL[0].replace("&amp;","&")
    except:
        return None
    
def get_total_page(html):
    """
    récupère dans la page le nombre total de page.
    Soit : le nombre de pages de topic pour un forum
    ou : le nombre de pages de réponses pour un topic
    """
    if len(html)==0:
        return "Vous n'êtes pas connecté."
    exp=re.compile(r"""<span class="pagelink" id='page-jump'>(\d*?) Pages <img src='style_images/nabbox-v3/menu_action_down\.gif' alt='V' title='Ouvrir le menu' border='0' />""")
    nbpage = exp.findall(html)
    try :
        return nbpage[0]
    except :
        return "1"
        
        
def get_title(html):
    """
    retourne le titre de la page (balise html title dans le head de la page)
    """
    exp=re.compile(r'<title>(.*?)</title>')
    title=exp.findall(html)
    try:
        #return title[0].replace("NABBOX FORUM ->","")
        rawTitle = title[0].replace("NABBOX FORUM ->","").replace("- NABBOX FORUM","")
        return unescape(rawTitle.strip())
    except:
        return ""
        
        
def get_param_answer(html):
    """
    retourne l'ID du forum et l'ID du topic pour envoyer un message dans un topic
    """
    if len(html)==0:
        return "Vous n'êtes pas connecté."
    exp=re.compile(r'do=reply_post&amp;f=([0-9]*?)&amp;t=([0-9]*?)"')
    forumID,topicID = exp.findall(html)
    try:
        return forumID[0],topicID[0]
    except:
        return None
        
        
if __name__ == "__main__":
    #ici on pourrait faire des action si le script était lancé en tant que programme
    pass
else:
    #ici on est en mode librairie importée depuis un programme
    pass
    


