"""
   Module retrieving video info from www.8artcity.com
   by Temhil 
"""

from BeautifulSoup import SoupStrainer
from BeautifulSoup import BeautifulSoup
from traceback import print_exc
import re

# Modules custom
from utils import HTTPCommunicator, set_xbmc_carriage_return, strip_off

#
# Constants
# 
#__settings__ = sys.modules[ "__main__" ].__settings__
#__language__ = sys.modules[ "__main__" ].__language__



def getBlogsList(pageUrl, addItemFunc=None, progressBar=None,  msgFunc=None ):
    """
    Retrieve Blogs list passing each item to the cb addItemFunc
    return Next page URL
    """
    print "getBlogsList"
    # Get HTML page...
    httpCommunicator = HTTPCommunicator()
    htmlSource       = httpCommunicator.get( pageUrl )                
    
    # Parse response...
    # <div style="text-align: center;">
    beautifulSoup = BeautifulSoup( htmlSource )
    itemBlogList = beautifulSoup.findAll("img", {"src" : re.compile( "images/stories/alaincarrazeblog/.*?" )} ) 
    for img in itemBlogList:
        try:
            item =  img.findParent().findParent()
            
            itemInfo = {}
            itemInfo["title"] = item.a["title"]
            itemInfo["url"] = item.a["href"]
            itemInfo["image"] = item.img["src"]
            itemInfo["description"] = ""
        
            print itemInfo
            #if progressBar != None:
            if addItemFunc != None:
                addItemFunc( itemInfo )
        except:
            print "getBlogsList - error parsing html - impossible to retrieve Blog info"
            print_exc()
    

def getVideoList(pageUrl, addItemFunc=None, progressBar=None,  msgFunc=None ):
    """
    Retrieve Video list passing each item to the cb addItemFunc
    return Next page URL
    """
    print "getVideoList"
    # Get HTML page...
    httpCommunicator = HTTPCommunicator()
    htmlSource       = httpCommunicator.get( pageUrl )                
    
    # Parse response...
    # <div class="content-item-block">
    #soupStrainer  = SoupStrainer( "div", { "class" : "content-item-block" } )
    #beautifulSoup = BeautifulSoup( htmlSource, soupStrainer )
    beautifulSoup = BeautifulSoup( htmlSource )
    
    
    # Parse video entries...
    # Looking for <script type="text/javascript">
    itemInfoList = beautifulSoup.findAll ("div", { "class" : "content-item-block" } ) 
    for item in itemInfoList:
        try:
            itemInfo = {}
            # Get Title
            # Looking for <h2 class="contentheading">
            contentheading = item.find ("h2", { "class" : "contentheading" } )
            if contentheading:
                itemInfo["title"]         = contentheading.a.string.strip()
                itemInfo["url_page_info"] = contentheading.a["href"]
            else:
                itemInfo["title"]         = ""
                itemInfo["url_page_info"] = None
                
            # Get Creation date
            # Looking for<span class="createdate">
            create_date = item.find ("span", { "class" : "createdate" } )
            if item.find ("span", { "class" : "createdate" } ):
                itemInfo["create_date"] = create_date.string.strip()
            else:
                itemInfo["create_date"] = ""
                
            # Get URL
            video_info = item.find ("script", { "type" : "text/javascript" } )
            if video_info:
                # <div style="text-align: justify;">
                #info = itemInfo.find ("style", { "type" : "text/javascript"} )
                re_descript = re.compile(r"</p>(.*?)</div>", re.DOTALL)
                #print video_info.findParent().findParent()
                try:
                    itemInfo["description"] = strip_off( set_xbmc_carriage_return( re_descript.findall(str(video_info.findParent().findParent()))[0].replace("\n<br />", "") ) )
                except:
                    itemInfo["description"] = ""
                    print "Error while retrieving Item info: %s"%itemInfo["title"]
                    print_exc()
                
                #video_info = info.p.script
                re_video_url = re.compile(r"'file=(.*?)['|&]", re.DOTALL) 
                re_image_url = re.compile(r"image=(.*?)'", re.DOTALL) 
                
                #TODO: manage case where nothing is found (will happen for image)
                itemInfo["url_video"] = re_video_url.findall(str(video_info))[0]
                raw_url_image = re_image_url.findall(str(video_info))
                if raw_url_image:
                    itemInfo["url_image"] = raw_url_image[0]
                else:
                    itemInfo["url_image"] = None
                
                
                print itemInfo
                #if progressBar != None:
                if addItemFunc != None:
                    addItemFunc( itemInfo )
            print itemInfo
        except:
            print "getVideoList - error parsing html - impossible to retrieve Video info"
            print_exc()

    # Get next page URL
    suivantInfo = beautifulSoup.find("a", { "title" : "Suivant" } )
    if suivantInfo:
        print suivantInfo
        next_url = suivantInfo["href"]
        print next_url
    else:
        next_url = None
    
    return next_url
    
if ( __name__ == "__main__" ):
    print "8artcity.py test"
    
    urlStart = "http://www.8artcity.com/le-videoblog-dalain-carraze"
    print urlStart
    getBlogsList(urlStart)
    
    
    #url              = "http://www.8artcity.com/le-videoblog-dalain-carraze/le-videoblog-dalain-carraze"
    #url              = "http://www.8artcity.com/index.php?option=com_content&amp;view=category&amp;layout=blog&amp;id=51&amp;Itemid=92"
    #url = "http://www.8artcity.com/component/content/category/51?layout=blog&amp;start=5"
    url = "http://www.8artcity.com/index.php?option=com_content&amp;view=category&amp;layout=blog&amp;id=51&amp;Itemid=92"
    print url
    
    getVideoList(url)