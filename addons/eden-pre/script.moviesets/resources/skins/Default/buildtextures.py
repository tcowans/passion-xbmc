
import os
import shutil

# get xml content
str_xml = ""
for root, dirs, files in os.walk( "720p" ):
    for file in files:
        str_xml += open( os.path.join( root, file ) ).read()

# media source
media = r"E:\coding\Windows\xbmc\addons\skin.confluence\media"

for root, dirs, files in os.walk( media ):#, topdown=False ):
    for file in files:
        fpath = os.path.join( root, file )
        img = fpath.replace( media, "" ).replace( "\\", "/" ).strip( "/" )
        if img in str_xml:
            print img
            dst = "media/sets-" + img
            if not os.path.exists( os.path.dirname( dst ) ):
                os.makedirs( os.path.dirname( dst ) )
            shutil.copy( fpath, dst )

# backgrounds source
backgrounds = r"E:\coding\Windows\xbmc\addons\skin.confluence\backgrounds"

for root, dirs, files in os.walk( backgrounds ):#, topdown=False ):
    for file in files:
        fpath = os.path.join( root, file )
        img = fpath.replace( backgrounds, "" ).replace( "\\", "/" ).strip( "/" )
        if img in str_xml:
            print img
            dst = "backgrounds/sets-" + img
            if not os.path.exists( os.path.dirname( dst ) ):
                os.makedirs( os.path.dirname( dst ) )
            shutil.copy( fpath, dst )
