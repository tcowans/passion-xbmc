# -*- coding: utf-8 -*-

#
#      rbc_lib.py -- search and retrieve music from Radio blog Club
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

__doc__ = """ Radio Blog Club library

rbc_lib is a library to search an artist and/or a music on the radio blog club site 
(http://radioblogclub.com). This library also allows to retrieve the music file.

This library can also be used as a tool.

Usage : rbc_lib -h or rbc_lib to show the history.

Example : rbc_lib -s Camille ta douleur
"""

__all__ = ['rbc_lib']

__author__   = 'nioc.bertheloneum'
__status__   = 'beta'
__version__  = '0.1.1'
__date__     = '2 June 2007'
__title__    = 'rbc_lib'


# ---------------------------------------------------------------------------------------
# libraries

import urllib
from smarturlretrieve import SmartFancyURLopener
import re
import os.path
import sys
# ---------------------------------------------------------------------------------------
class rbc_lib:
    """Class for the site Radio Blog Club"""
    
    _basePath_    = 'http://www.radioblogclub.com'
    _searchPath_  = '/search'
    _query_       = '&k=657ecb3231ac0b275497d4d6f00b61a1'
    _nresults_    = '/h3\>.*?about \<b\>(\d*?)\</b\>.*?\</div\>'
    _results_     =  'play.*?start\(\'(.*)\'\)\;.*?\>([^>]*?)\</a'
    
    _nbypage_     = 50
    
    _keepresults_ = {}
    _history_    = []
    _maxhistory_ = 10
    
    # -----------------------------------------------------------------------------------
    def __init__ ( self, encoding = 'utf-8', maxresults = 100 ):
        """Initialize the class with the encoding of the input (utf-8, windows-1252, ...)
        and optionnaly with the maximum number of results accepted in the response 
        (default sets to 100)"""
        
        self._encoding    = encoding
        self._maxresults_ = maxresults
        urllib._urlopener = SmartFancyURLopener ()
        self._cnresults   = re.compile ( self._nresults_ )
        self._cresults    = re.compile ( self._results_  )
        
    
    # -----------------------------------------------------------------------------------
    def searchArtistMusic ( self, artistMusic, update = False, report_search=None ):
        """Search an Artist and/or a music on Radio Blog Club if it's not in the 
        history or if the update parameter is True"""
        
        try:
            encArtistMusic = unicode(artistMusic, self._encoding).encode('latin-1')
        except UnicodeDecodeError:
            encArtistMusic = artistMusic
            
        if (artistMusic in self._history_) and (update == False):
            return len ( self._keepresults_ [ artistMusic ] )
        
        if report_search: report_search ( 1, 1 )
        
        page = 0
        n, result = self._searching ( encArtistMusic, page )
        
        totalsongs = min ( n, self._maxresults_ )
        
        nb = max ( totalsongs - self._nbypage_, 0 )
        
        if report_search: report_search ( nb, totalsongs )
        
        while nb > 0:
            page += 1
            result.extend ( self._searching ( artistMusic, page )[1] )
            nb -= self._nbypage_
            if report_search: report_search ( nb, totalsongs )
        
        self._add_result ( artistMusic, result )
        
        return min ( n, self._maxresults_ )
        
    
    # -----------------------------------------------------------------------------------
    def _searching ( self, artistMusic, page = 0 ):
        """Search an Artist and/or a music on Radio Blog Club by page"""
        
        search = urllib.quote ( artistMusic.strip().replace(' ', '_') )
        path = self._searchPath_ + '/%d/%s' % ( page * self._nbypage_, search )
        url  = self._basePath_ + path
        html = urllib.urlopen ( url ) . read ()
        result = self._cnresults.findall ( html )
        
        if len(result) == 0: return 0, []
        
        nbresult = int ( result[0] )
        
        return nbresult, self._cresults.findall ( html )
        
    
    # -----------------------------------------------------------------------------------
    def _add_result ( self, artistMusic, result ):
        """Adds the result to the dictionnary and add the artistMusic to the history"""
        
        self._keepresults_ [ artistMusic ] = result
        
        if artistMusic in self._history_:
            self._history_.remove ( artistMusic )
            
        elif len ( self._history_ ) == self._maxhistory_:
            last = self._history_.pop()
            if self._keepresults_.get ( last ): del self._keepresults_ [ last ]
        
        self._history_.insert ( 0, artistMusic )
        
    
    # -----------------------------------------------------------------------------------
    def get_musicNames ( self, artistMusic ):
        """Returns the list of music names found for artistMusic"""
        
        if artistMusic not in self._history_:
            return None
        else:
            return [ r[1] for r in self._keepresults_ [ artistMusic ] ]
        
    
    # -----------------------------------------------------------------------------------
    def get_musicAddress ( self, num, artistMusic ):
        """Returns the web address of the file corresponding to the indice num of the 
        list linked to artistMusic"""
        
        if artistMusic not in self._history_:
            return None
        else:
            return self._keepresults_ [ artistMusic ] [ num ] [ 0 ]
        
    
    # -----------------------------------------------------------------------------------
    def retrieve ( self, num, artistMusic, basepath, reporthook=None ):
        """Download the file specified by num and artistMusic to the basepath folder.
        the reporthook parameter is used to show information during the download"""
        
        result = self._keepresults_.get ( artistMusic, None )
        
        if not result: return None
        
        url, name = result [ num ]
        return urllib.urlretrieve ( url + self._query_, 
                                   os.path.join ( basepath, name + '.mp3' ), reporthook )
        
    
    # -----------------------------------------------------------------------------------
    def save_history ( self, path ):
        """Save the history and the results in path"""
        
        fp = open ( path, 'w' )
        fp.write ( repr ( self._history_ ) + '\n' )
        fp.write ( repr ( self._keepresults_ ) + '\n' )
        fp.close ()
        
    
    # -----------------------------------------------------------------------------------
    def load_history ( self, path ):
        """Loads the history and the results from path"""
        
        if not os.path.isfile ( path ): return
        
        fp = open ( path, 'r' )
        self._history_ = eval ( fp.readline () )
        self._keepresults_ = eval ( fp.readline () )
        fp.close()
        
    

# ---------------------------------------------------------------------------------------
def report_retrieve (blocknum, blocksize, totalsize):
    """Print a progress bar during the download"""
    
    i = float(totalsize) / blocksize
    nb = int (i)
    if nb != i: nb += 1
    p = ( float ( 100 * blocknum ) / nb )
    sys.stdout.write ( '\r\t\t[' + (int(round(p/2))*'#').ljust(50) + '] %.2f%%' % p )
    sys.stdout.flush()
    

# ---------------------------------------------------------------------------------------
def report_search ( nb, totalsongs ):
    """Print a progress bar during the research"""
    
    nb = max ( nb, 0 )
    try: p = ( float ( 100 * ( totalsongs - nb ) ) / totalsongs )
    except ZeroDivisionError: p = 100.0
    sys.stdout.write ( '\r\t\t[' + (int(round(p/2))*'#').ljust(50) + '] %.2f%%' % p )
    sys.stdout.flush()
    

# ---------------------------------------------------------------------------------------
def main ():
    from optparse import OptionParser
    
    parser = OptionParser()
    parser.set_usage ( "%prog [options] \"Artist and/or Music\"" )
    parser.add_option( "-s", "--search", dest="search", action="store_true", 
                       help="search the artist and/or the music in the history and " + \
                       "on Radio Blog Club if not found", default=False )
    parser.add_option( "-u", "--update", dest="update", action="store_true", 
                       help="search the artist and/or the music on Radio Blog Club",
                       default=False )
    parser.add_option( "-r", "--retrieve", dest="retrieve", action="store",
                       help="retrieve the music by his indice", type="int", default=-1,
                       metavar='indice')
    parser.add_option( "-m", "--maxresults", dest="max_results", action="store",
                       help="set the maximum number of results", type="int", default=100,
                       metavar="max")
    
    (options, args) = parser.parse_args()
    
    if len(args) == 0 and (options.search or options.update or options.retrieve > -1):
        print 'You must specify one artist and/or Music to process'
        print 'Use -h or --help for help'
        sys.exit(1)
    
    rbcl = rbc_lib ( sys.stdin.encoding, options.max_results )
    
    pathSave = os.path.abspath ( 'rbcl.sav' )
    
    if os.path.isfile ( pathSave ): rbcl.load_history ( pathSave )
    
    artistMusic = ' '.join ( args )
    
    if options.search or options.update:
        # Search and print the artistMusic on Radio Blog Club if necessary (update or
        # not in the history
        
        print '\nSearching \'%s\' ...' % artistMusic
        n = rbcl.searchArtistMusic ( artistMusic, options.update, report_search )
        if n:
            print '\r  %d results:' % n + 65 * ' '
            results = rbcl.get_musicNames ( artistMusic )
            for i in range ( len ( results ) ):
                print '\t%d  %s' % (i, results[i])
        else:
            print '  no song found'
        print
        
    elif options.retrieve > -1:
        # Download a file in the current path
        
        if artistMusic not in rbcl._history_:
            print 'you must search the Artist and/or Music before'
            sys.exit(1)
        print 
        print 'Downloading \'%s\'...' % \
                                 rbcl.get_musicNames ( artistMusic ) [ options.retrieve ]
        path = rbcl.retrieve ( options.retrieve, artistMusic, sys.path[0], 
                                                                     report_retrieve )[0]
        print '\r\tDownload completed' + 65 * ' ' + '\n'
        print 'File saved in %s\n' % path
        
    elif artistMusic:
        # Shows the results of the artistMusic search if they are in the history
        
        if artistMusic not in rbcl._history_:
            print 'This Artist and/or Music is not in the history'
            sys.exit(1)
        results = rbcl.get_musicNames ( artistMusic )
        for i in range ( len ( results ) ):
            print '\t%d  %s' % (i, results[i])
        
    else:
        # Shows the last research
        
        print 'history:'
        if len ( rbcl._history_ ) == 0:
            print 'No history'
            sys.exit(1)
        for h in rbcl._history_:
            print '\t%s' % h
    
    rbcl.save_history ( pathSave )
    

# ---------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
    
