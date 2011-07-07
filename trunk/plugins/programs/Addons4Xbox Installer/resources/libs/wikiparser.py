"""
   Module retrieving repositories info from XBMC Wiki
   by Temhil 
"""
__all__ = [
    # public names
    "getRepoList",
    "ListItemFromWiki"
    ]

from BeautifulSoup import SoupStrainer, BeautifulSoup
from traceback import print_exc
import re
import urllib
#
# Constants
# 
#__settings__ = sys.modules[ "__main__" ].__settings__
#__language__ = sys.modules[ "__main__" ].__language__

# Custom modules
try:
    from Item import TYPE_ADDON_REPO
except:
    print_exc()


def getRepoList(pageUrl, destination=None, addItemFunc=None, progressBar=None,  msgFunc=None ):
    """
    Retrieve Blogs list passing each item to the cb addItemFunc
    return Next page URL
    """
    #print "getRepoList"
    result = "OK"

    # Get HTML page...
    htmlSource = urllib.urlopen( pageUrl ).read()    
    #print htmlSource
    
    # Parse response...
    beautifulSoup = BeautifulSoup( htmlSource )
    itemRepoList = beautifulSoup.findAll("tr") 
    print itemRepoList
    for repo in itemRepoList:
        try:
            #print repo
            #print "----"
            repoInfo = {}
            tdList = repo.findAll("td")
            if tdList:
                repoInfo[ "name" ]        = tdList[0].a.string.strip()
                repoInfo[ "description" ] = tdList[1].string.strip()
                repoInfo[ "author" ]      = tdList[2].string.strip()
                repoInfo[ "repo_url" ]    = tdList[3].a["href"]
                repoInfo[ "version" ]     = None
                repoInfo[ "type" ]        = TYPE_ADDON_REPO
                try:
                    repoInfo["ImageUrl"] = tdList[4].a["href"]
                except:
                    repoInfo["ImageUrl"] = None
            
            #if progressBar != None:
            if addItemFunc != None:
                if repoInfo["repoUrl"].endswith("zip"):
                    addItemFunc( repoInfo )
                else:
                    print "Invalid URL for the repository %s - URL=%s"%(repoInfo["name"], repoInfo["repoUrl"])
        except:
            print "getRepoList - error parsing html - impossible to retrieve Repo info"
            print_exc()
            result = "ERROR"  
    return result



class ListItemFromWiki:
    currentParseIdx = 1
    addons = []
    def __init__( self, pageUrl ):
        try:
            if ( pageUrl ):
                # Get HTML page...
                htmlSource = urllib.urlopen( pageUrl ).read()    
                
                #print htmlSource
                
                # Parse response...
                beautifulSoup = BeautifulSoup( htmlSource )
                self.itemRepoList = beautifulSoup.findAll("tr") 
                print self.itemRepoList
                print               
        except:
            status = 'ERROR'
            print_exc()
    
        
    def _parseRepoElement(self, repoElt, repoInfo):
        status = 'OK'
        try:
            #print repo
            #print "----"
            tdList = repoElt.findAll("td")
            if tdList:
                repoInfo[ "name" ]        = tdList[0].a.string.strip()
                repoInfo[ "description" ] = tdList[1].string.strip()
                repoInfo[ "author" ]      = tdList[2].string.strip()
                repoInfo[ "repo_url" ]    = tdList[3].a[ "href" ]
                repoInfo[ "version" ]     = None
                repoInfo[ "type" ]        = TYPE_ADDON_REPO
                try:
                    repoInfo[ "ImageUrl" ] = tdList[4].a[ "href" ]
                except:
                    repoInfo[ "ImageUrl" ] = None
        except:
            print "_parseRepoElement - error parsing html - impossible to retrieve Repos info"
            print_exc()
            result = "ERROR"  
        
        return status
    
    
    def getNextItem(self):
        result = None
        if len(self.itemRepoList) > 0 and self.currentParseIdx < len(self.itemRepoList):
            itemInfo = {}
            status = self._parseRepoElement( self.itemRepoList[self.currentParseIdx], itemInfo )
            self.currentParseIdx = self.currentParseIdx + 1
            print "status = %s"%status
            if status == 'OK':
                result = itemInfo
        else:
            #result = None
            itemInfo = {}
            result = itemInfo
        print "getNextItem - result:"
        print result
        return result
    

    
if ( __name__ == "__main__" ):
    print "Wiki parser test"
    
    repoListUrl = "http://wiki.xbmc.org/index.php?title=Unofficial_Add-on_Repositories"
    print repoListUrl
    #getRepoList(repoListUrl)
    
    listRepoWiki = ListItemFromWiki(repoListUrl)
    keepParsing = True
    while (keepParsing):
        item = listRepoWiki.getNextItem()
        print item
        if item:
            print "Item OK"
        else:
            keepParsing = False


