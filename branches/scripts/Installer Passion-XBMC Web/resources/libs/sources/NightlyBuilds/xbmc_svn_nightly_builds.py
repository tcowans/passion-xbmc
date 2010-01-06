
import os
import re
import urllib
import urllib2
from traceback import print_exc


base_url = "http://www.sshcs.com/xbmc/"
builds_url = base_url + "?mode=Builds"
dl_url = base_url + "/binaries/builds/"

# temporaire les labels vont dans le strings.xml
build_text = {
    "btnback1": ( "Windows DirectX", "Use this package to over-write your current installed application.", "windows.png" ),
    "btnback2": ( "Windows Installer", "Use this package to install a fresh copy using the latest SVN release.", "windows.png" ),
    "btnback3": ( "Linux Debian File", "Use this package to install a full version on your deb based Linux.", "ubuntu.png" ),
    "btnback4": ( "XBOX", "Use this package for a clean install or upgrade on your XBMC.", "xbox.png" ),
    "btnback5": ( "Windows OpenGL", "Use this package to over-write your current installed application.", "windows.png" ),
    "btnback6": ( "OSX 10.5/10.4/ATV", "Use this package to install a full version on your OS X Bases Systems.", "mac.png" ),
    }


def download_html( url ):
    try:
        args = { "User-agent": 'Mozilla/5.0 ( Windows; U; Windows NT 5.1; fr; rv:1.9.1.3 ) Gecko/20090824 Firefox/3.5.3 ( .NET CLR 3.5.30729 )' }
        req = urllib2.Request( url, urllib.urlencode( {} ), args )
        sock = urllib2.urlopen( req )
        html = sock.read()
        sock.close()
    except:
        print_exc()
        html = "Not found!"

    return html


def get_nightly_builds():
    try:
        bullet_list = "[B]\x95 [/B]" #unichar( 8226 )

        html = download_html( base_url )

        available_builds = []
        not_available_builds = []
        for available in re.compile( '(r.*?Available).*?<img src="/xbmc/img/(.*?).png"' ).findall( html ):
            build = bullet_list + available[ 0 ].strip()
            if available[ 1 ] == "yes": available_builds.append( build )
            else: not_available_builds.append( "[COLOR=FF990000]%s[/COLOR]" % build  )
        available_builds = "\n".join( available_builds + not_available_builds )

        changelog = re.compile( '<div class="NotesBox">(.*?)</div>', re.S ).findall( html )[ 0 ].replace( "<br />", "\n" )
        changelog = bullet_list + changelog.strip( os.linesep ).replace( "\n", "\n" + bullet_list ).replace( "&nbsp;", " " ).strip()

        html = download_html( builds_url )

        heading = "Unofficial Nightly Builds: %s" % re.compile( '<div class="xbmcrevtxt">(.*?)</div>' ).findall( html )[ 0 ].strip()
        info = re.compile( '<div class="NewsData">(.*?)</div>', re.S ).findall( html )[ 0 ].replace( "<hr />", "[B] - [/B]" ).replace( "\r", "" ).replace( "&nbsp;", " " ).strip( os.linesep ).replace( "\n", "  " ).strip()

        builds = []
        for items in re.compile( '<a href="\?mode=BuildsDownloadCounter\&FN=(.*?)\&BN=(.*?)" class="(btnback.*?)">.*?id="(xbmcimg.*?)".*?</a><span class=".*?">(.*?)</span>' ).findall( html ):
            #print items
            build_url = dl_url + "XBMC_%s_%s.%s" % ( items[ 0 ], items[ 1 ], ( "rar", "tgz" )[ items[ 0 ] == "OSX" ] )
            #print build_url
            title, desc, icon = build_text.get( items[ 2 ] )
            dl_times = items[ 4 ].replace( "   ", " " ).strip()
            builds.append( [ title, desc, icon, dl_times, build_url ] )

        # types returned: str, str, str, str, list
        return heading, info, changelog, available_builds, builds
    except:
        print_exc()

    return "", "", "", "", []



if ( __name__ == "__main__" ):
    import time
    t1 = time.time()
    print get_nightly_builds()
    print time.time()-t1
