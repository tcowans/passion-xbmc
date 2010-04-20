
import os
import re
import sys
import urllib
import urllib2
from traceback import print_exc


base_url = "http://www.sshcs.com/xbmc/"
builds_url = base_url + "?mode=Builds"
dl_url = base_url + "/binaries/builds/"

try:
    #FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
    _ = sys.modules[ "__main__" ].__language__
except:
    lang = { 32900: "Use this package to over-write your current installed application.",
        32901: "Use this package to install a fresh copy using the latest SVN release.",
        32902: "Use this package to install a full version on your deb based Linux.",
        32903: "Use this package for a clean install or upgrade on your XBMC.",
        32904: "Use this package to install a full version on your OS X Bases Systems." }
    def _( id ): return lang[ id ]

# temporaire les labels vont dans le strings.xml
build_text = {
    "PCDX":  ( "Windows DirectX", _( 32900 ), "nightlyDX.png" ),
    "PCI":   ( "Windows Installer", _( 32901 ), "nightlyWin.png" ),
    "Linux": ( "Linux x86 Debian File", _( 32902 ), "nightlyLinux.png" ),
    "Linux64": ( "Linux x64 Debian File", _( 32902 ), "nightlyLinux.png" ),
    "XBOX":  ( "XBOX", _( 32903 ), "nightlyXBox.png" ),
    "PCO":   ( "Windows OpenGL", _( 32900 ), "nightlyGL.png" ),
    "OSX":   ( "OSX 10.5/10.4/ATV", _( 32904 ), "nightlyOSX.png" ),
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


def get_changelog( new_rev, current_rev="0" ):
    changelog = ""
    try:
        bullet_list = "[B]\x95 [/B]" #unichar( 8226 )

        sock = urllib.urlopen( "http://trac.xbmc.org/timeline?changeset=on&max=300&daysback=90&format=rss" )
        html = sock.read()
        sock.close()

        regex_items = re.compile( '<item>(.*?)</item>', re.DOTALL )
        regex_revision = re.compile( '<title>Changeset \[([0-9]+)\]: ([^<]+)?</title>' )
        regex_date = re.compile( '<pubDate>(.*?)</pubDate>' )
        items = regex_items.findall( html )
        getAll = ( int( current_rev ) >= int( new_rev ) )
        for item in items:
            try:
                revision = regex_revision.findall( item )[ 0 ]
                if ( not getAll ) and ( int( revision[ 0 ] ) > int( new_rev ) ): continue
                date = regex_date.findall( item )[ 0 ]
                day, month, year = date.split()[ 1:4 ]
                month = str( "jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec".split( "|" ).index( month.lower() ) + 1 )
                line = "[%s] %s/%s/%s, %s\n" % ( revision[ 0 ], day, month.zfill( 2 ), year, revision[ 1 ], )
                changelog += bullet_list + line
                if ( not getAll ) and ( int( revision[ 0 ] ) <= int( current_rev ) ): break
            except:
                print_exc()
    except:
        print_exc()

    return changelog


def get_nightly_builds( current_rev="0" ):
    try:
        bullet_list = "[B]\x95 [/B]" #unichar( 8226 )

        html = download_html( base_url )

        box = re.compile( '<\!-- The News Box -->(.*?)<\!--roller over image box-->', re.S ).findall( html )[ 0 ]
        rev = re.findall( '<div style=".*?">Build r(.*?)</div>', box, re.S )[ 0 ]
        builddate = re.findall( '<div style=".*?">Uploaded (.*?)</div>', box, re.S )[ 0 ]
        notebox = re.search( '<div style=".*?">(.*?)</div>', box, re.S ).group( 1 ).replace( "<hr />", "[B] - [/B]" ).replace( "\r", "" ).replace( "&nbsp;", " " ).strip( os.linesep ).replace( "\n", "  " ).strip()

        heading = "Unofficial Nightly Builds: XBMC SVN r%s" % rev
        info = "[B]%s:[/B] %s" % ( builddate, notebox )

        builds = []
        available_builds = []
        #('PCDX', 'PC', 'Windows DirectX')
        for ID, mode, title in re.findall( '<div class="(.*?)"><a href=".*?P=(.*?)\&.*?" title="(.*?)" ></a></div>', box ):
            #print ID, mode, title
            ID = ID.strip( "b" )
            ext = ( ( "rar", "tgz" )[ ID == "OSX" ], "zip" )[ ID == "XBOX" ]
            build_url = dl_url + "XBMC_%s_%s.%s" % ( mode, rev, ext )
            name, desc, icon = build_text.get( ID )
            builds.append( [ title, desc, icon, name, build_url ] )
            available_builds.append( bullet_list + name )

        available_builds = "[CR]".join( available_builds )

        if not current_rev.isdigit(): current_rev = "0"
        changelog = get_changelog( rev, current_rev )

        # types returned: str, str, str, str, list
        return heading, info, changelog, available_builds, builds
    except:
        print_exc()

    return "", "", "", "", []



if ( __name__ == "__main__" ):
    import time
    t1 = time.time()
    for object in get_nightly_builds():
        print object
        print
    print time.time()-t1
