
DEBUG = 0

import os
import sys
import urllib
import urllib2
from traceback import print_exc

try:
    import json
except:
    import simplejson as json


USER_AGENT = "XBMC Metadata Actors/Dev"
try:
    from xbmcaddon import Addon
    from xbmc import getInfoLabel
    USER_AGENT = USER_AGENT.replace( "Dev", Addon( "script.metadata.actors" ).getAddonInfo( "version" ), 1 )
    USER_AGENT += " (XBMC for %s %s; %s" % ( sys.platform, getInfoLabel( "System.BuildVersion" ), getInfoLabel( "System.BuildDate" ) )
except ImportError:
    USER_AGENT += " (Python %s on %s" % ( sys.version, sys.platform )
USER_AGENT += ")"
#USER_AGENT = "Mozilla/5.0 (Windows NT 5.1; rv:10.0.2) Gecko/20100101 Firefox/10.0.2"


class _urlopener( urllib.FancyURLopener ):
    version = os.environ.get( "HTTP_USER_AGENT" ) or USER_AGENT
urllib._urlopener = _urlopener()


# http://help.themoviedb.org/kb/api/about-3 and/or http://api.themoviedb.org/2.1/
# The API key we supplied you with for your account.
APIKEY  = "d12bf766b6df5b909eedeaf2ba0d3429"
# basic Authentication
HEADERS = { "Accept": "application/json", "User-Agent": USER_AGENT }


# Retrieve JSON data from site
def _get_json_new( url, params={} ):
    parsed_json = {}
    try:
        params.update( { "api_key": APIKEY } )
        url += "?" + urllib.urlencode( params )
        request = urllib2.Request( url, headers=HEADERS )

        req = urllib2.urlopen( request )
        json_string = req.read()
        req.close()

        json_string = unicode( json_string, 'utf-8', errors='ignore' )
        parsed_json = json.loads( json_string )
    except:
        print_exc()
    return parsed_json


def search_person( person="", page=1 ):
    """ This is a good starting point to start finding peoples on TMDb.
        The idea is to be a quick and light method so you can iterate through peoples quickly.
        This method is purposefully lighter than the 2.1 search. It searches. That’s all.
    """
    if not person: return {}
    url = "http://api.themoviedb.org/3/search/person"
    js  = _get_json_new( url, { "query": person, "page": str( page ) } )
    if DEBUG:
        #print js
        print json.dumps( js, sort_keys=True, indent=2 )
    return js


def person_info( person_id=19429 ):
    """ This method is used to retrieve all of the basic person information.
        It will return the single highest rated profile image.
    """
    url = "http://api.themoviedb.org/3/person/" + str( person_id )
    js  = _get_json_new( url )
    if DEBUG:
        #print js
        print json.dumps( js, sort_keys=True, indent=2 )
    return js


def person_credits( person_id=19429, language="en" ):
    """ This method is used to retrieve all of the cast & crew information for the person.
        It will return the single highest rated poster for each movie record.

        language : "da|fi|nl|de|it|es|fr|pl|hu|el|tr|ru|he|ja|pt|zh|cs|sl|hr|ko|en|sv|no"
    """
    url = "http://api.themoviedb.org/3/person/%s/credits" % str( person_id )
    js  = _get_json_new( url, { "language": language } )
    if DEBUG:
        #print js
        print json.dumps( js, sort_keys=True, indent=2 )
    return js


def person_images( person_id=19429 ):
    """ This method is used to retrieve all of the profile images for a person.
    """
    url = "http://api.themoviedb.org/3/person/%s/images" % str( person_id )
    js  = _get_json_new( url )
    if DEBUG:
        #print js
        print json.dumps( js, sort_keys=True, indent=2 )
    return js


def full_person_info( person_id=19429, language="en" ):
    infos = {}
    infos.update( person_info( person_id ) )
    infos.update( person_credits( person_id, language ) )
    infos.update( person_images( person_id ) )

    if DEBUG:
        print json.dumps( infos, sort_keys=True, indent=2 )

    return infos


def configuration( refresh=False ):
    """ Some elements of the API require some knowledge of the configuration data which can be found here.
        The purpose of this is to try and keep the actual API responses as light as possible.
        That is, by not repeating a bunch of data like image URLs or sizes.
    """
    js = {u'images': {u'poster_sizes': [u'w92', u'w154', u'w185', u'w342', u'w500', u'original'], u'profile_sizes': [u'w45', u'w185', u'h632', u'original'], u'backdrop_sizes': [u'w300', u'w780', u'w1280', u'original'], u'base_url': u'http://cf2.imgobject.com/t/p/'}}
    if refresh: js = _get_json_new( "http://api.themoviedb.org/3/configuration" )
    if DEBUG:
        #print js
        print json.dumps( js, sort_keys=True, indent=2 )
    return js[ 'images' ]

    
    
try: import xbmcvfs
except: pass
def download( url, destination ):
    OK, dl_path = False, ""
    try:
        destination = destination + os.path.basename( url )
        try:
            fp, h = urllib.urlretrieve( url, destination )
            #try:
            #    print "%r" % fp
            #    print str( h ).replace( "\r", "" )
            #except:
            #    pass
            OK = xbmcvfs.exists( destination )
            dl_path = destination
        except:
            xbmcvfs.delete( destination )
            print "%r xbmcvfs.delete(%r)" % ( not xbmcvfs.exists( destination ), destination )
    except:
        print_exc()
    return OK and dl_path



if __name__=="__main__":
    import time
    t1 = time.time()

    #js = configuration()
    #print "-"*100
    DEBUG = 1
    js = search_person( "Bruce Lee" )
    #print "-"*100

    #js = full_person_info( 19429, "fr" )
    #print "-"*100

    print time.time() - t1





def getPerson21( where, method=0, language="en" ):
    # for testing diff with v3
    method = ( "search", "getInfo" )[ method ]
    TYPE   = "json" # Type can be xml, yaml or json.
    url = "http://api.themoviedb.org/2.1/Person.%s/%s/%s/%s/%s" % ( method, language, TYPE, APIKEY, where )

    sock = urllib.urlopen( url )
    html = sock.read()
    sock.close()

    js = json.loads( unicode( html, 'utf-8', errors='ignore' ) )
    if DEBUG: print json.dumps( js, sort_keys=True, indent=2 )
    return js
#getPerson21( "bruce lee" )
#getPerson21( "19429", 1 )
