# -*- coding: utf-8 -*-

# parsers.py
# version: 1.2
# This file is part of Qarte
#    
# Author : Vincent Vande Vyvre <vincent.vandevyvre@swing.be>
# Copyright: 2011-2012 Vincent Vande Vyvre
# Licence: GPL3
# Home page : https://launchpad.net/qarte
#
# Parser for pages arte+7 and arteLiveWeb

import os, re
import time
import urllib2, xml.dom.minidom
import sys
import pickle
import copy
import logging
logger = logging.getLogger("parser")

from threading import Thread, current_thread
from threading import enumerate as enumerate_
from traceback import print_exc
from email.utils import parsedate

class PlusParser():
    ARTE_WEB_ROOT = 'http://videos.arte.tv'
    ARTE_CATEGORIES_ROOT = ''
    ARTE_CATEGORIES_LINK = ''
    ARTE_BONUS_SPECIFIQUE = ''
    RE_TITLE = re.compile('(?<=<h2><a href=")(.*?)(?=</a></h2>)', re.DOTALL)
    RE_PITCH = re.compile('(?<=<p class="teaserText">)(.*?)(?=</p>)', re.DOTALL)
    RE_DURATION = re.compile('(?<=<div class="duration_thumbnail">)'
                                        '(.*?)(?=</div>)', re.DOTALL)
    RE_DATE = re.compile('(?<=<p>)(.*?)(?=</p>)', re.DOTALL)
    RE_PICT = re.compile('(?<=class="thumbnail")(.*?)(?=/></a>)', re.DOTALL)
    RE_TIME = re.compile("^\d\d[h:]\d\d$")
    #RE_XML = re.compile("(?<=vote {ajaxUrl:')(.*?)(?=,view)", re.DOTALL)
    RE_XML = re.compile('(?<=vars_player.videorefFileUrl)(.*?)(?=";)', re.DOTALL)
    RE_XML2 = re.compile('ajaxUrl:.?.(/../do_delegate/videos/)'
                                        '([^,]+),view,commentForm.html')
    RE_STREAM = re.compile('<url quality="([^"]+)">([^<]+)<')
    RE_CONT = re.compile('(?<="recentTracksCont">)(.*?)(?="technicalSheet">)', 
                                        re.DOTALL)
    RE_DE = re.compile('(?<=<p>)(.*?)(?=</p>)', re.DOTALL)
    RE_OR = re.compile('(?<=<p style="margin-top: 0">)(.*?)(?=<br/>)', 
                                        re.DOTALL)
    MONTHS = [u"ja", u"f", u"mar", u"av", u"mai", u"juin", u"juil", 
                       u"ao", u"se", u"oc", u"no", u"d", u"Ja", 
                       u"F", u"Mä", u"Ap", u"Mai", u"Jun", u"Jul", 
                       u"Au", u"Se", u"Ok", u"No", u"De"]

    def __init__(self, lang, videos):
       #super(PlusParser, self).__init__()
        self.videos = videos
        self.lang = lang
        self.page = "/".join([self.ARTE_WEB_ROOT, lang, "videos/"])
        self.is_updating = False
        self.close_app = False
        self.is_daemon = True

    def get_categories_list(self):
	cat_re = re.compile("".join(['<li><a href="/', 
				self.lang, self.ARTE_CATEGORIES_LINK, 
				'(?P<lien>.*?)"', '',self.ARTE_BONUS_SPECIFIQUE,
				'>(?P<nom>.*?)<span id="(.*?)"></span></a></li>']), re.DOTALL)

	# Stage 1
	if self.dbg:
	    print "%s" %(u"Get page: {0}".format(self.page))
	reply = self.get_page(self.page)
	if reply[0] is None:
	    print "Stage 1 : %s" %(reply[1])
	    return

	# Stage 2
	for item in re.finditer(cat_re, reply[0]):
	    self.categories[item.group('nom').decode('utf-8', 'replace')] = item.group('lien')

    def parse(self, pageNumber, nbVideosPerPage):
        """Get arte+7 page and run parsing.

        """
        # Stage 1
        if self.is_daemon:
            self.dbg = True
        print "%s" %(u"Run arte+7 parser: {0}".format(current_thread()))
        print "%s" %(u"Get page: {0}".format(self.page))
        content, err = self.get_page_content(self.page)
        if content is None:
            print "%s" %(u"Read Error: {0}".format(err))
            return

        if not len(content):
            print "%s" %(u"Read Error: 'Page empty'")
            return

        # Stage 2
        # Here, we need to find one <script> wich contains "videowallSettings"
        # into this part we seek for a string like:
        #   "/fr/do_delegate/videos/index-1234567,view,asThumbnail.html",
        # finally, we use this string to create our url
        #   "http://videos.arte.tv/fr/do_delegate/videos/index-1234567,
        #    view,asThumbnail.html,?hash=fr/thumb///1/200/"
        # Note: the last number 200 is the maximum videos to display.
        chs = content.split('videowallSettings = {')[1]\
                            .split('coverflowXmlUrl')[0]
        found_url = 0
        for chain in chs.split():
            if "asThumbnail" in chain:
                page_url = "".join([self.ARTE_WEB_ROOT,
                        chain.replace('"',''), "?hash=",
                        self.lang, "/thumb///",str(pageNumber),"/",str(nbVideosPerPage),"/"])
                found_url = 1
                break
        if not found_url:
            print "%s" %(u"Read Error: 'URL videowall not found'")
            return

        # Stage 3
        print "%s" %(u"Get page: {0}".format(page_url))
        content, err = self.get_page_content(page_url)
        if content is None:
            print "%s" %(u"Read Error: {0}".format(err))
            return

        # Parsing for each video
        items = content.split('<div class="video">')[1:]
        self.lang = "/{0}/".format(self.lang)
        for it in items:
            vid = self.get_videos_data(it)
            if vid is not None:
                video = VideoPlusItem(vid)
                self.videos.append(video)

        print "%s" %(u"Found {0} videos".format(len(self.videos)))
	# Load summaries
        self.load_summaries() 
        if self.summaries:
		for idx, video in enumerate(self.videos):
		    if video.date in self.summaries:
		        video.summary = self.summaries[video.date][0]
		        video.orig = self.summaries[video.date][1]

	nextPage = self.getNextPage(content)
	return nextPage

    def get_videos_data(self, txt):
        try:
            ttl = self.RE_TITLE.search(txt).group(0)
            ref, title = ttl.split('html">')
            title = title.decode('utf-8', 'replace')
            title = self.html_to_utf8(title)
            ref = self.ARTE_WEB_ROOT + ref
            link = ref.replace("/fr/", self.lang)
        except Exception, why:
            return None

        try:
            dt = self.RE_DATE.search(txt).group(0)
            date = dt.decode('utf-8', 'replace')
            date = self.format_date(date)
        except Exception, why:
            date = None

        try:
            duration = self.RE_DURATION.search(txt).group(0)
        except Exception, why:
            duration = 'Unknow'

        try:
            pict = self.RE_PICT.search(txt).group(0)
            pict = pict.split('src="')[1].strip()[:-1]
            pict = self.ARTE_WEB_ROOT + pict
            pict = pict.replace("/fr/", self.lang)
        except Exception, why:
            pict = None

        try:
            ptc = self.RE_PITCH.search(txt).group(0)
            ptc = ptc.decode('utf-8', 'replace')
            pitch = self.html_to_utf8(ptc)
        except Exception, why:
            pitch = None
        if link[-1] == '.':
            link = link[:-1]
        return [title, date, duration, link, pict, pitch]

    def html_to_utf8(self, text):
        return text.replace("&#39;", "'")

    def get_page(self, url):
	try:
	    content = urllib2.urlopen(url).read()
	except IOError as why:
	    return None, why
	return self.unescape(content), None

    def unescape(self, text):
	def ent2chr( m ):
	    code = m.group( 1 )
	    if( code.isdigit() ): 
		code = int( code )
	    else:
		code = int( code[ 1 : ], 16 )
	    if( code < 256 ): 
		return chr( code )
	    else: 
		return '?'

	text = text.replace("&lt;", "<")
	text = text.replace("&gt;", ">")
	text = text.replace("&quot;", "'")
        text = text.replace("&amp;", "&")
	return text
      
    def format_date(self, dt):
        date_array = dt.split(",")
        if self.RE_TIME.search(date_array[-1].strip()) is None:
            return ""
        time_ = date_array[-1].strip()
        if date_array[0].strip() in (u"Aujourd'hui", u"Heute"):
            date_ = time.strftime("%d/%m/%Y", time.localtime(time.time()))
        elif date_array[0].strip() in (u"Hier", u"Gestern"):
            date_ = time.strftime("%d/%m/%Y", 
                                    time.localtime(time.time() - (86400)))
        else:
            array = date_array[1].split()
            day = array[0].strip(".")
            month = array[1]
            for idx, mnt in enumerate(self.MONTHS):
                if month.startswith(mnt):
                    if idx > 11:
                        idx -= 12
                    month = "%02d" % (idx+1)
                    break
            year = array[2]
            date_ = "%s/%s/%s" % (day, month, year)
        return date_ + " " + time_

    def get_page_content(self, url):
        try:
            content = urllib2.urlopen(url).read()
        except IOError as why:
            return None, why
        return content, None

    def update_all(self):
        """Called after the viewer is completed for update the video infos.

        """
        self.is_updating = True
        Thread(target=self.update_videos_infos, args=(None,)).start()

    def get_rtmp_url(self, lnk, quality):
        content = self.get_page_content(lnk)
        if content[0] is None:
            return
        match = self.RE_XML.search(content[0])

        xmlurl = 'http://videos.arte.tv%s%s,view,asPlayerXml.xml'\
                                % (match.group(1), match.group(2))
        content = self.get_page_content(xmlurl)
        urls = []
        url = None
        for line in content[0].split("\n"):
            match = self.RE_STREAM.search(line)
            if match:
                urls.append((match.group(1), match.group(2)))
        if len(urls) == 0:
            return
        if len(urls) == 1:
            return urls[0][1]
        for u in urls:
            if u[0] == 'hd':
                url = u[1]
                break
            if u[0] == 'sd':
                url = u[1]
        return url

    def update_videos_infos(self, *args):
        """Update the summary with file 'summaries'.

        """
        print "%s" %(u"Update arte+7 summaries list")
        print "%s" %(u"Threads enum: {0}".format(enumerate_()))
        begin = time.time()
        self.load_summaries() 
        if not self.summaries:
            self.get_new_infos()
            return
        for idx, video in enumerate(self.videos):
            if video.date in self.summaries:
                video.summary = self.summaries[video.date][0]
                video.orig = self.summaries[video.date][1]
        self.get_new_infos()

    def get_new_infos(self):
        for video in self.videos:
            if self.close_app:
                break
            if video.summary is None:
                infos = self.fetch_summary(video.link)
                video.summary, video.orig = infos[0], infos[1]
                self.summaries[video.date] = infos
        print "%s" %(u"arte+7 summaries updated")
        #self.main.summaries = self.summaries
        self.save_videos_infos()
        self.is_updating = False

    def fetch_summary(self, link):
        reply = self.get_page_content(link)
        if reply[0] is None:
            print "No Reply"
            return None, None, None
        content = reply[0]
        try:
            """Recuperation du Theme"""
            txt = re.compile('(?<=<ul class="tags">)(.*?)(?=</ul>)',re.DOTALL).search(content).group(0)
            temp = "%s" %re.compile('(?<=<li><a href=")(.*?)(?=</a></li>)',re.DOTALL).search(txt).group(0)
            pattern = re.compile('(?P<scheme>[^>]*)>(?P<theme>.*)',re.DOTALL)
            match = re.match(pattern, temp)
            t = match.group('theme')
            theme = t.decode('utf-8', 'replace')
        except Exception, why:
            print_exc()
            theme = "-1"
        try:
            txt = self.RE_CONT.search(content).group(0)
        except Exception, why:
            print_exc()
            return None, u""            
        try:
            d = self.RE_DE.search(txt)
            if d:
                d = d.group(0)
            else:
                d = u"No description"
            desc = d.decode('utf-8', 'replace')
        except Exception, why:
            print_exc()
            desc =u"No description"
        try:
            o = self.RE_OR.search(txt)
            if o:
                o = o.group(0)
            else:
                o = u"-1,-1,-1"
            orig = o.decode('utf-8', 'replace')
        except Exception, why:
            print_exc()
            orig =u"-1,-1,-1"
        return desc, orig, theme

    def fetch_stream_links(self, link):
        urls = []
        print "%s" %(u"Get stream URL: {0}".format(link))       
	reply = self.get_page_content(link)
        if reply[0] is None:
            print "%s" %(u"Read error: {0}".format(reply[1]))
            return None, None
        content = reply[0]
        # RE_XML: ('(?<=vote {ajaxUrl:)(.*?)(?=,view)', re.DOTALL)
        match = self.RE_XML.search(content)
        if match is not None:
            #xmlurl = "".join(["http://videos.arte.tv", match.group(0), ",view,strmVideoAsPlayerXml.xml"])
            st = match.group(0)
            # Space and other symbol may vary
            LNK = re.compile('(?<=http)(.*?)(?=xml)', re.DOTALL)
            st = LNK.search(match.group(0))
            if st is not None:
		xmlurl = "".join(['http', st.group(0), 'xml'])
		print "%s" %(u"Found: {0}".format(xmlurl))

        else:
            #RE_XML2: ('ajaxUrl:.?.(/../do_delegate/videos/)'
                                        #'([^,]+),view,commentForm.html')
	    print "RE_XML2"
            match = self.RE_XML2.search(content)
            if match is not None:
                xmlurl = 'http://videos.arte.tv%s%s,view,strmVideoAsPlayerXml.xml'\
                                        % (match.group(1), match.group(2))
            else:
                print "%s" %(u"Unable to find stream URl")
                return None, None
        print "%s" %(u"Get page: {0}".format(xmlurl))
        reply = self.get_page_content(xmlurl)
        if reply[0] is None:
            print "%s" %(u"Read error: {0}".format(reply[1]))
            return None, None
        #content = reply[0]
        #for line in content.split("\n"):

        content = reply[0].split("\n")
        lg = "".join(['<video lang="', self.lang, '" ref="'])
        lnk = ""
        for line in content:
	    if line.startswith(lg):
		lnk = line[22:].split(" ")[0][:-1]
		break

        if not lnk:
	    print "%s" %(u"Unable to find stream URl")
	    return None, None

        reply = self.get_page_content(lnk)
        if reply[0] is None:
	    print "%s" %(u"Read error: {0}".format(reply[1]))
	    return None, None

        content = reply[0].split("\n")
        for line in content:

            # RE_STREAM = re.compile('<url quality="([^"]+)">([^<]+)<')
            match = self.RE_STREAM.search(line)
            if match:
                urls.append((match.group(1), match.group(2)))

        if not urls:
            print "%s" %(u"rtmp URLs not found in: {0}".format(link))
            return (None, None)
        hd, sd = None, None
        for u in urls:
            if u[0] == 'hd':
                hd = u[1]
            elif u[0] == 'sd':
                sd = u[1]
        return hd, sd

    def save_content(self, txt):
        """debugging function"""
        with open("contentxml", "w") as objf:
            objf.write(txt)

    def load_summaries(self):
        """Summaries are saved in a dictionnary where keys are the video's dates.

        """
        try:
            with open(self.findex, "r") as objfile:
                self.summaries = pickle.load(objfile)
        except Exception as why:
            self.summaries = {}

    def save_videos_infos(self):
        try:
            with open(self.findex, 'w') as objf:
                pickle.dump(self.summaries, objf)
        except Exception as why:
            print "%s" %(u"Unable to save summaries list, reason: \n\t{0}"
                                .format(why))

    def getNextPage(self, content):
        content=content[content.find('<div class="pagination inside">'):]
        content=content[:content.find('</ul>')]
        spl=content.split('<a href=')
        for i in range(1,len(spl),1):
          entry=spl[i]
          if entry.find('"#"')>=0:
            next=""
            if self.lang[1:-1]=="de":
              next="Weiter"
            elif self.lang[1:-1]=="fr":
              next="Suivant"
            if entry.find(next)>=0:
	      match=re.compile('class="{page:\'(.+?)\'}">'+next+'</a>', re.DOTALL).findall(entry)
	      if match :
              	nextPage=match[0]
              	return nextPage
          else:
            if self.lang[1:-1]=="de":
              next="Weiter"
            elif self.lang[1:-1]=="fr":
              next="Suivant"
            if entry.find(next)>=0:
              match=re.compile('"(.+?)"', re.DOTALL).findall(entry)
              url="http://videos.arte.tv"+match[0].replace("&amp;","&")
              match=re.compile('pageNr=(.+?)&', re.DOTALL).findall(url)
	      nextPage = None
	      if match :
              	nextPage=match[0]
              	return nextPage
	return None

class LiveParser():
    def __init__(self, lang, categories):
        #super(LiveParser, self).__init__()
        self.lang = lang
	self.categories = categories
        self.dbg = True

    def get_categories_list(self):
        
        ARTE_WEB_ROOT = 'http://liveweb.arte.tv/{0}'.format(self.lang)
        cat_re = re.compile("".join(['<li><a href="http://liveweb.arte.tv/',
                                    self.lang,
                                    '/cat/(?P<lien>.*?)" class="accueil"',
                                    '>(?P<nom>.*?)</a></li>']), re.DOTALL)
        count, soup = 0, False

        # Stage 1
        if self.dbg:
            print "%s" %(u"Get page: {0}".format(ARTE_WEB_ROOT))
        reply = self.get_page(ARTE_WEB_ROOT)
        if reply[0] is None:
            print "Stage 1 : %s" %(reply[1])
            return

        # Stage 2
        for item in re.finditer(cat_re, reply[0]):
            self.categories[item.group('nom').decode('utf-8', 'replace')] \
                                                    = item.group('lien')

    def get_videos_list(self, cat, videos):
	self.get_categories_list()
        # Stage 3
        if self.dbg:
            print "%s" %(u"Get arteLiveWeb video's data in '{0}'".format(cat))
            #print "%s" %(u"Threads enum: {0}".format(enumerate_()))
        if not self.categories:
            # Stage 1 has failed
	    print "Stage 1 has failed"
            return
        ptrn = re.compile('href="(http://download.liveweb.arte.tv/o21/'
                            'liveweb/rss/home.*?\.rss)', re.DOTALL)
        ptrn_1 = re.compile("(<item>.*?</item>)", re.DOTALL)
        value = self.categories[cat]
        url = "http://liveweb.arte.tv/{0}/cat/{1}".format(self.lang, value)
        page = self.get_page(url)
	self.videos = {}
        if page[0] is None:
	    print "Stage 3 : %s" %(page[1])
            return
        if len(page[0]) > 0:
            lnk = re.search(ptrn, page[0]).group(0)
            page = self.get_page(lnk[6:])
            if page[0] is None:
		print "Stage 3 : %s" %(page[1])
                return
            if len(page[0]) > 0:
                items = re.findall(ptrn_1, page[0])
                self.videos[cat] = items
            else:
                print "Page 2 is empty!"
        else:
            print "Page 1 is empty!"

        # Stage 4
        for key, values in self.videos.iteritems():
            vids = {}
            for val in values:
                it = self.get_element(val)
                if it is None:
                    print "elem is None"
                    continue
                try:
                    rfc_date = parsedate(it['date'])
                    it['date'] = time.strftime('%c', rfc_date)\
                                            .decode('utf-8', 'ignore')
                    if time.mktime(rfc_date) - float(time.time()) > 0:
                        it['soon'] = True
                except Exception, e:
                    #print 'date error: ', e
		    it['date'] = 'Date ?'
                itm = VideoItem(key, it)
                videos.append(itm)



    def get_lll(self):
        links = self.get_links(it)
        for k, v in links.iteritems():
            it[k] = v
        self.videos[key].append(it)

    def get_element(self, chain):
        ele = {'HD': None, 'SD': None, 'Live': None, 'soon': False}
        count = 0
        tt = re.compile("(?<=<title>)(.*?)(?=</title>)", re.DOTALL)
        lk = re.compile("(?<=<link>)(http://liveweb.arte.tv/{0}/video/.*?)"
                        "(?=</link>)".format(self.lang), re.DOTALL)
        dt = re.compile("(?<=<pubDate>)(.*?)(?=</pubDate>)", re.DOTALL)
        pt = re.compile("(?<=<description>)(.*?)(?=</description>)", re.DOTALL)
        at = re.compile("(?<=<author>)(.*?)(?=</author>)", re.DOTALL)
        en = re.compile("<enclosure.*?/event/.*?/(.*?)-.*?/>", re.DOTALL)
        pix = re.compile('(?<=<enclosure url=")(.*?)(?=" type="image/)')        
        try:
            s = tt.search(chain).group(0)
            ele['title'] = s.decode('utf-8', 'replace')
        except:
            return None
        try:
            ele['link']  = lk.search(chain).group(0)
        except Exception, why:
            print "title: %s has no link %s" % (ele['title'], why)
            ele['link']  = "No link"
        try:
            s = (dt.search(chain).group(0))
            ele['date'] = s.decode('utf-8', 'replace')
        except:
            ele['date'] = "No date"
        try:
            s = (pt.search(chain).group(0))
            ele['pitch'] = s.decode('utf-8', 'replace')
        except:
            ele['pitch'] = "No description"
        try:
            s = (at.search(chain).group(0))
            ele['author'] = s.decode('utf-8', 'replace')
        except:
            ele['author'] = "Unknow"
        try:
            ele['ID'] = int(en.search(chain).group(1))
        except:
            ele['ID'] = 0
        try:
            ele['pict'] = pix.search(chain).group(0)
        except:
            ele['pict'] = None
        return ele

    def get_page(self, url):
        try:
            content = urllib2.urlopen(url).read()
        except IOError as why:
            return None, why
        return self.unescape(content), None

    def get_links(self, idx):
        page = self.get_page("http://arte.vo.llnwd.net/o21/liveweb/events"
                            "/event-{0}.xml".format(idx))
	print "%s" %("http://arte.vo.llnwd.net/o21/liveweb/events"
                            "/event-{0}.xml".format(idx))
        if page[0] is None:
            print "Get stream's URL %s"  %(page[1])
            return
        page = page[0]
        HD = re.compile("(?<=<urlHd>)(.*?)(?=</urlHd>)", re.DOTALL)
        SD = re.compile("(?<=<urlSd>)(.*?)(?=</urlSd>)", re.DOTALL)
        Live = re.compile("(?<=<liveUrl>)(.*?)(?=</liveUrl>)", re.DOTALL)
        obj = {}
        try:
            obj['HD'] = HD.search(page).group(0)
        except AttributeError:
            obj['HD'] = None
        try:
            obj['SD'] = SD.search(page).group(0)
        except AttributeError:
            obj['SD'] = None
        try:
            obj['Live'] = Live.search(page).group(0)
        except AttributeError:
            obj['Live'] = None
        return obj

    def decode_link(self, url):
	pattern = re.compile("(?P<scheme>[^:]*)://(?P<host>[^/^:]*):{0,1}(?P<port>[^/]*)/(?P<app>.*?)/(?P<playpath>\w*?\:.*)", re.DOTALL)
	match = re.match(pattern, url)
	link = "%s://%s app=%s playpath=%s" %(
			match.group('scheme'),
			match.group('host'),
			match.group('app'),
			match.group('playpath'))

	if( match.group('port') != ""):
	    port = match.group('port')
	elif(url[ :6 ] == 'rtmpte'):
	    port = '80'
	elif(url[ :5 ] == 'rtmpe'):
	    port = '1935'
	elif(url[ :5 ] == 'rtmps'):
	    port = '443'
	elif(url[ :5 ] == 'rtmpt'):
	    port = '80'
	else:
	    port = '1935'

	downloadParams = { "url" : url,
			   "host" : match.group('host'),
			   "port" : port,
			   "app"  : match.group('app'),
			   "playpath" : match.group('playpath')
			}

	return link, downloadParams

    def unescape(self, text):
        def ent2chr( m ):
            code = m.group( 1 )
            if( code.isdigit() ): 
                code = int( code )
            else:
                code = int( code[ 1 : ], 16 )
            if( code < 256 ): 
                return chr( code )
            else: 
                return '?'

        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
	text = text.replace("&quot;", "'")
        text = text.replace("&amp;", "&")
        return text

class EventParser(PlusParser):

    ARTE_CATEGORIES_ROOT = 'videos/events'
    ARTE_CATEGORIES_LINK = '/videos/events/'

    def __init__(self, lang, categories, videos):
	self.categories = categories
	self.videos = videos
	self.lang = lang
	PlusParser.__init__(self, self.lang, self.videos)
	self.dbg = True
	self.is_updating = False
	self.close_app = False
	self.is_daemon = True
	self.page = "/".join([self.ARTE_WEB_ROOT, self.lang, self.ARTE_CATEGORIES_ROOT, "index-3188672.html" ])
	
    def parse(self, url, pageNumber, nbVideosPerPage):
	self.get_categories_list()
	self.page = "/".join([self.ARTE_WEB_ROOT, self.lang, self.ARTE_CATEGORIES_ROOT , url])+"#/tv/list///"+str(pageNumber)+"/"+str(nbVideosPerPage)+"/"
	nextPage = PlusParser.parse(self, pageNumber, nbVideosPerPage)
	return nextPage

class ProgrammesParser(EventParser): 
    ARTE_BONUS_SPECIFIQUE = ''
    def __init__(self, lang, categories, videos):
	self.categories = categories
	self.videos = videos
	self.lang = lang	
	EventParser.__init__(self, self.lang, self.categories, self.videos)
	self.dbg = True
	self.is_updating = False
	self.close_app = False
	self.is_daemon = True

    def initArteRoot(self):
	if self.lang == "fr":
		self.ARTE_CATEGORIES_ROOT = "videos/programmes"
		self.ARTE_CATEGORIES_LINK = "/videos/programmes/" 	
	elif self.lang == "de":
		self.ARTE_CATEGORIES_ROOT = "videos/sendungen"
		self.ARTE_CATEGORIES_LINK = "/videos/sendungen/"

    def get_categories_list(self):
	self.initArteRoot()
	self.page = "/".join([self.ARTE_WEB_ROOT, self.lang, self.ARTE_CATEGORIES_ROOT])+"#/tv/list///1/200/"
	EventParser.get_categories_list(self)

class BonusParser(ProgrammesParser):
    ARTE_BONUS_SPECIFIQUE = ' class="(.*?)"'
    def __init__(self, lang, categories, videos):
	self.categories = categories
	self.videos = videos
	self.lang = lang	
	ProgrammesParser.__init__(self, self.lang, self.categories, self.videos)
	self.dbg = True
	self.is_updating = False
	self.close_app = False
	self.is_daemon = True

    def initArteRoot(self):
	if self.lang == "fr":
		self.ARTE_CATEGORIES_ROOT = "videos/toutesLesVideos"
		self.ARTE_CATEGORIES_LINK = "/videos/toutes_les_videos/" 	
	elif self.lang == "de":
		self.ARTE_CATEGORIES_ROOT = "videos/alleVideos"
		self.ARTE_CATEGORIES_LINK = "/videos/alle_videos/"

    def parse(self, url, pageNumber, nbVideosPerPage):
        print "BonusParser 25 videos/page max"
        ProgrammesParser.parse(self, url, pageNumber, 25)

class SearchParser(PlusParser):
    def __init__(self, lang, videos):
	self.videos = videos
	self.lang = lang	
	PlusParser.__init__(self, self.lang, self.videos)
	self.dbg = True
	self.is_updating = False
	self.close_app = False
	self.is_daemon = True

    def initArteRoot(self):
	if self.lang == "fr":
		self.ARTE_CATEGORIES_ROOT = "do_search/videos/recherche?q="+self.search 	
	elif self.lang == "de":
		self.ARTE_CATEGORIES_ROOT = "do_search/videos/suche?q="+self.search

    def parse(self, pageNumber, nbVideosPerPage, search):
	self.search = search
	self.initArteRoot()
	self.page = "/".join([self.ARTE_WEB_ROOT, self.lang, self.ARTE_CATEGORIES_ROOT])
        page_url = self.page

        print "%s" %(u"Get page: {0}".format(page_url))
        content, err = self.get_page_content(page_url)
        if content is None:
            print "%s" %(u"Read Error: {0}".format(err))
            return

        items = content.split('<div class="video">')[1:]
        self.lang = "/{0}/".format(self.lang)
        for it in items:
            vid = self.get_videos_data(it)
            if vid is not None:
                video = VideoPlusItem(vid)
                self.videos.append(video)

        print "%s" %(u"Found {0} videos".format(len(self.videos)))
	# Load summaries
        self.load_summaries() 
        if self.summaries:
		for idx, video in enumerate(self.videos):
		    if video.date in self.summaries:
		        video.summary = self.summaries[video.date][0]
		        video.orig = self.summaries[video.date][1]

	nextPage = self.getNextPage(content)
	return nextPage

class VideoPlusItem(object):
    def __init__(self, data):
        """Item video in arte+7.

        Args:
        data -- values provided by the parser
        """
        d = dict(title = data[0],
                date = data[1],
                duration = data[2],
                link = data[3],
                pix = data[4],
                pitch = data[5],
                HD = None,
                SD = None,
                outfile = None,
                preview = None,
                summary = None,
		author = None,
                orig = None)
        for key, value in d.iteritems():
            setattr(self, key, value)


class VideoItem(object):
    def __init__(self, cat, item):
        """Item video in arteLiveWeb.

        Args:
        cat -- category
        item -- values provided by the parser
        """
        d = dict(category = cat,
                order = item['ID'],
                title = item['title'],
                date = item['date'],
                pitch = item['pitch'],
                link = item['link'],
                pix = item['pict'],
                soon = item['soon'],
                preview = None,
                HD = None,
                SD = None,
                Live = None,
                outfile = None,
                quality = None,
		duration = None,
		summary = None,
		orig = None,
                author = item['author'])

        for key, value in d.iteritems():
            setattr(self, key, value)
        if self.pix is not None:
            self.preview = os.path.basename(self.pix)

    def get_stream_links(self, page):
        tt = re.compile("(?<=<nameDe>)(.*?)(?=</nameDe>)", re.DOTALL)
        HD = re.compile("(?<=<urlHd>)(.*?)(?=</urlHd>)", re.DOTALL)
        SD = re.compile("(?<=<urlSd>)(.*?)(?=</urlSd>)", re.DOTALL)
        Live = re.compile("(?<=<liveUrl>)(.*?)(?=</liveUrl>)", re.DOTALL)
        try:
            self.local_name = tt.search(page).group(0)
        except AttributeError:
            self.local_name = None
        try:
            self.HD = HD.search(page).group(0)
        except AttributeError:
            self.HD = None
        try:
            self.SD = SD.search(page).group(0)
        except AttributeError:
            self.SD = None
        try:
            self.Live = Live.search(page).group(0)
        except AttributeError:
            self.Live = None

    def get_image(self):
        if self.preview is not None:
            try:
                img = urllib2.urlopen(self.pix).read()
            except Exception, why:
                return None
            else:
                return img
        else:
            return None
