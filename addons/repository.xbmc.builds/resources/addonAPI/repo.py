
#Modules General
import os
import re
import sys
import time
import urllib
from StringIO import StringIO
from traceback import print_exc

import elementtree.ElementTree as HTB

# base url
repo_url = "http://mirrors.xbmc.org/"
# jump directly
releases_url = repo_url + "releases/"
nightlies_url = repo_url + "nightlies/"


ICONS = {
    "linux": "linux.png", "linux_x64": "linux.png",
    "live": "live.png", "iso": "live.png",
    "osx": "mac.png", "mac": "mac.png",
    "pc": "win.png", "dharma": "win.png", "pcinstaller": "win.png", "win": "win.png",
    "xbox": "xbox.png", "t3chm": "xbox.png",
    }


def get_html_source( url ):
    """ fetch the html source """
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
        return ""


def setDate( txt ):
    try:
        a = "jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"
        def b( m ): return str( a.split( "|" ).index( m.group() ) + 1 ).zfill( 2 )
        return re.sub( a, b, txt.lower() ).replace( "-", "." )
    except:
        print_exc()
        return txt


def setSize( txt ):
    if txt.isdigit(): txt += "B"
    sz = re.search( '([+-]?\\d*\\.\\d+|\\d+)(b|k|m|g|t)', txt.lower() )
    size = 0.0
    if sz:
        byte = 1.0
        if sz.group( 2 ) == "k": byte = 1024.0
        elif sz.group( 2 ) == "m": byte = 1024.0**2
        elif sz.group( 2 ) == "g": byte = 1024.0**3
        elif sz.group( 2 ) == "t": byte = 1024.0**4 # infrequent
        try: size = float( sz.group( 1 ) ) * byte
        except: print_exc()
    return size


def getListing( url ):
    source = get_html_source( url )
    regexp = '<img src="/icons/((?:[a-z][a-z\\.\\d_]+)\\.(?:[a-z\\d]{3}))(?![\\w\\.])" alt="(\\[.*?\\])"'
    regexp += ' width="16" height="16" /> <a href="(.*?)">(.*?)</a>\\s+(.*?)   [ \-|<]'
    links = re.compile( regexp ).findall( source )

    LIST = []
    #remove Parent Directory
    links = links[ 1: ]
    for icon, type, uri, title, infos in links:
        if "latest." in title: continue
        try:
            isFolder = ( type == "[DIR]" )
            type = os.path.splitext( icon )[ 0 ]
            icon = ICONS.get( type.lower(), "" )
            infos = infos.strip().replace( "   ", " " ).split() + [ "oops!" ]
            d, t, s = infos[ :3 ]
            #date modified
            date = setDate( d )
            # datetime added
            x = time.mktime( time.strptime( date+t, "%d.%m.%Y%H:%M" ) )
            lastplayed = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime( x ) )
            #size
            size = setSize( s )
            #revision
            rev = re.search( "r(\d+)", title )
            if rev: rev = rev.group( 1 )
            else: rev = ""

            link = { "title": title, "revision": rev, "date": date, "size": size, "icon": icon, "type": type,
                "isFolder": isFolder, "link": url+uri, "year": int( lastplayed[ :4 ] ), "lastplayed": lastplayed }
            LIST.append( link )
            #print link
            #print
        except:
            print_exc()
    LIST.reverse()
    return LIST


def getAvailableUpdates( platform="win32", revision=33300 ):
    LIST = []
    def _get( url ):
        for link in getListing( url ):
            #while folder
            if link[ "isFolder" ]:
                _get( link[ "link" ] )
            elif link[ "revision" ].isdigit():
                if int( link[ "revision" ] ) > revision:
                    LIST.append( link )
    for url in [ releases_url, nightlies_url ]:
        _get( "%s%s/" % ( url, platform ) )
    LIST.reverse()
    return LIST


def getUnofficialBuilds( url="http://www.sshcs.com/xbmc/" ):
    """ Unofficial Nightly Builds From SVN """
    builds = []
    src = get_html_source( url )
    for uri, title in re.compile( '<a href="(\?mode=DLC.*?)" title="(.*?)"></a>' ).findall( src ):
        uri = uri.replace( "&#38;", "&" )
        #revision
        rev = re.search( "FB\=(\d+)", uri )
        if rev: rev = rev.group( 1 )
        else: rev = ""
        #type=platform
        type = re.search( "FT\=(.*?)\&", uri )
        if type: type = type.group( 1 )
        else: type = ""
        ext = re.search( "TF\=(.*)", uri ).group( 1 )
        filename = "XBMC_%s_%s.%s" % ( type, rev, ext )

        icon = ICONS.get( type.lower(), "" )
        title = filename
        link = { "title": title, "revision": rev, "icon": icon, "type": type,  "link": url+uri,
            "filename": filename, "isFolder": False, "date": "", "size": 0, "year": 0, "lastplayed": "" }
        builds.append( link )
    return builds


def getChangelog():
    changelog = ""
    try:
        from convert_utc_time import utc_to_local
        bullet_list = "[B]\x95 [/B]" #unichar( 8226 )

        html = get_html_source( "http://trac.xbmc.org/timeline?ticket=on&changeset=on&max=500&daysback=90&format=rss" )
        #html = get_html_source( "http://trac.xbmc.org/timeline?changeset=on&max=150&daysback=90&format=rss" )

        html = html.replace( "dc:creator", "dcCreator" )
        root = HTB.parse( StringIO( html ) ).find( "channel" ).findall( "item" )
        #print len( root )
        #d = {}
        colors = [ "FFFFFFFF", "88FFFFFF" ]
        for elem in root:
            t = "\n".join( [ #elem.findtext( "category" ), 
                elem.findtext( "title" ),
                #"-"*len( elem.findtext( "title" ) ),
                utc_to_local( elem.findtext( "pubDate" ) ) + " by " + elem.findtext( "dcCreator" ), "",
                re.sub( "(?s)<[^>]*>", "", elem.findtext( "description" ) ).strip(), "",
                "_"*300,# "\n",
                ] )
            t = "[COLOR=%s]%s[/COLOR]\n" % ( colors[ 0 ], t )
            colors.reverse()
            changelog += t
            #d[ elem.findtext( "category" ) ] = 1
        #print d
    except:
        print_exc()
    return changelog.replace( "&lt;", "<" ).replace( "&gt;", ">" ).replace( "\t", "    " )


if ( __name__ == "__main__" ):
    file( "changelog.txt", "w" ).write( getChangelog().encode( "utf-8" ) )

    #for build in getUnofficialBuilds():
    #    print build
    #    print

    #l = getListing( repo_url )
    #l = getAvailableUpdates()
    #for news in l:
    #    print news
    #    print
