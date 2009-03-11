# -*- coding: utf-8 -*-

#
#      smarturlretrieve.py -- modify the redirection treatment of FancyURLopener
#
#      Copyright 2007 nioc.bertheloneum <nioc.bertheloneum@gmail.com>
#
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation; either version 2 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program; if not, write to the Free Software
#      Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#

__doc__ = """
Modify the FancyURLopener to alterate the address passed in the header using quote 
function. A special function smarturlretrieve is set to replace urlretrieve.

Usage:
\timport urllib
\tfrom smarturlretrieve import SmartFancyURLopener

\turllib._urlopener = SmartFancyURLopener ()
"""

__all__ = ['SmartFancyURLOpener', 'smarturlretrieve']

__author__   = 'nioc.bertheloneum'
__status__   = 'beta'
__version__  = '0.1.0'
__date__     = '2 June 2007'
__title__    = 'smarturlretrieve'

# ---------------------------------------------------------------------------------------
# libraries

from urllib import FancyURLopener, quote, basejoin, splittype



# ---------------------------------------------------------------------------------------
class SmartFancyURLopener ( FancyURLopener ):
    """Alteration of the redirection treatment. Replace any special character by its
    associated code"""
    
    # -----------------------------------------------------------------------------------
    def redirect_internal(self, url, fp, errcode, errmsg, headers, data):
        if 'location' in headers:
            newurl = headers['location']
        elif 'uri' in headers:
            newurl = headers['uri']
        else:
            return
        type, tempurl = splittype (newurl)
        newurl = type + ':' + quote(tempurl)
        void = fp.read()
        fp.close()
        # In case the server sent a relative URL, join with original:
        newurl = basejoin(self.type + ":" + url, newurl)
        return self.open(newurl)
        
    

# ---------------------------------------------------------------------------------------
def smarturlretrieve(url, filename=None, reporthook=None, data=None):
    return SmartFancyURLopener().retrieve(url, filename, reporthook, data)
    

