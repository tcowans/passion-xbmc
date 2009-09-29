
import os
import re
import time
from traceback import print_exc

import elementtree.HTMLTreeBuilder as ET


ENCODING = ( "", "iso-8859-1", "UTF-8", )[ 0 ]


def update_nfo( filename, attr_dict={}, encoding=ENCODING ):
    try:
        # ...manipulate tree...
        import elementtree.ElementTree as etree
        tree = etree.parse( filename )
        for elem in tree.getroot():
            for key, value in attr_dict.items():
                if elem.tag == key:
                    if not value: value = ""
                    if isinstance( value, str ): elem.text = value
                    elif isinstance( value, dict ): elem.attrib = value
                    else: elem.text = repr( value )
        tree.write( filename, encoding )
        #If not error, return path filename.
        return filename
    except:
        print_exc()
        #None reponse is returned



class InfosNFO:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )
        self.infoLabels = {}
        self.isTVShow = False

    def set( self, key, value="" ):
        self.__dict__.setdefault( key, value )

    def get( self, key, default="" ):
        return self.__dict__.get( key, default )

    def parse( self, filename ):
        try:
            tree = ET.parse( filename )
            root = tree.getroot()
            self.set( "actor", [] )
            self.set( "fanart", [] )
            self.set( "thumbs", [] )
            for elem in root:
                try:
                    if elem.tag in [ "fanart", "thumbs" ]:
                        for tbn in elem.findall( "thumb" ):
                            tbn = ( tbn.text or "" ).strip( '\t\r\n ' )
                            if tbn and ( elem.tag == "fanart" ):
                                self.fanart.append( tbn )
                            elif tbn and ( elem.tag == "thumbs" ):
                                self.thumbs.append( tbn )
                    elif elem.tag == "thumb":
                        txt = ( elem.text or "" ).strip( '\t\r\n ' )
                        self.thumbs.append( txt )
                    elif elem.tag == "actor":
                        dct = {}
                        for sub_elem in elem.getiterator()[ 1: ]:
                            txt = ( sub_elem.text or "" ).strip( '\t\r\n ' )
                            dct[ sub_elem.tag ] = txt
                        self.actor.append( dct )
                    else:
                        txt = ( elem.text or "" ).strip( '\t\r\n ' )
                        self.set( elem.tag, txt )
                except:
                    print elem.tag, elem.text
                    print_exc()
        except:
            print_exc()
        self.set_info_labels()

    def set_info_labels( self ):
        """set infos for listitem.setInfo
        setInfo(type, infoLabels) -- Sets the listitem's infoLabels.

        type           : string - type of media(video/music/pictures).
        infoLabels     : dictionary - pairs of { label: value }.

        *Note, To set pictures exif info, prepend 'exif:' to the label. Exif values must be passed
               as strings, separate value pairs with a comma. (eg. {'exif:resolution': '720,480'}
               See CPictureInfoTag::TranslateString in PictureInfoTag.cpp for valid strings.

               You can use the above as keywords for arguments and skip certain optional arguments.
               Once you use a keyword, all following arguments require the keyword.

        example:
          - self.list.getSelectedItem().setInfo('video', { 'Genre': 'Comedy' })
        """

        hrsmin = re.findall( "(\d{1,4})", self.get( "runtime", "" ) ) + [ "0", "0" ]
        duration = time.strftime( "%X", time.gmtime( ( int( hrsmin[ 0 ] ) * 60 * 60 ) + ( int( hrsmin[ 1 ] ) * 60 ) ) )

        cast_and_role = []
        for actor in self.actor:
            try: cast_and_role.append( ( actor.get( "name", "" ), actor.get( "role", "" ) ) )
            except: pass

        self.infoLabels = {
            "year"        : int( self.get( "year" ) or "0" ),
            "count"       : int( self.get( "count" ) or "0" ),
            "rating"      : float( self.get( "rating" ) or "0.0" ),
            "size"        : int( self.get( "size" ) or "0" ),
            "watched"     : int( self.get( "playcount" ) or "0" ),
            "playcount"   : int( self.get( "playcount" ) or "0" ),
            "overlay"     : int( self.get( "overlay" ) or "0" ),
            "cast"        : cast_and_role,
            "genre"       : self.get( "genre", "" ),
            "director"    : self.get( "director", "" ),
            "mpaa"        : self.get( "mpaa", "" ),
            "plot"        : self.get( "plot"  "" ),
            "plotoutline" : self.get( "outline", "" ),
            "title"       : self.get( "title", "" ),
            "duration"    : duration,
            "studio"      : self.get( "studio", "" ),
            "tagline"     : self.get( "tagline", "" ),
            "writer"      : self.get( "credits", "" ),
            "premiered"   : self.get( "premiered", "" ) or self.get( "aired", "" ),
            "trailer"     : self.get( "trailer", "" ),
            "votes"       : self.get( "votes", "" ),
            "date"        : self.get( "date", "" )
            }
            #date = string, format "2009-01-12"
        if self.isTVShow:
            self.infoLabels.update( {
                "episode"     : int( self.get( "episode" ) or "0" ),
                "season"      : int( self.get( "season" ) or "0" ),
                "tvshowtitle" : self.get( "title", "" )
                } )



if ( __name__ == "__main__" ):
    import time
    t1 = time.time()
    filename = "scrapers/Passion_XBMC/29718.xml"
    nfo = InfosNFO()
    print dir( nfo )
    print
    nfo.parse( filename )
    print time.time() - t1
    print dir( nfo )
    print
    print nfo.get( "trailer", "" )
    print
    print nfo.infoLabels
    print
    print time.time() - t1
