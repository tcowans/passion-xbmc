"""
Module de partage des fonctions et des constantes

"""

#En gros seul les fonctions et variables de __all__ vont etre importees lors du "import *"
#The public names defined by a module are determined by checking the module's namespace
#for a variable named __all__; if defined, it must be a sequence of strings which are names defined
#or imported by that module. The names given in __all__ are all considered public and are required to exist.
#If __all__ is not defined, the set of public names includes all names found in the module's namespace
#which do not begin with an underscore character ("_"). __all__ should contain the entire public API.
#It is intended to avoid accidentally exporting items that are not part of the API (such as library modules
#which were imported and used within the module).
__all__ = [
    # public names
    "PersistentDataCreator",
    "PersistentDataRetriever"
          ]

#Modules general
import os
import pickle
from traceback import print_exc




class PersistentDataCreator:
    """
    Creates persitent data
    """
    def __init__( self, data, filepath ):
        print "PersistentDataCreator: filepath = %s"%filepath
        print "PersistentDataCreator: data:"
        print data
        self._persit_data( data, filepath )

    def _persit_data( self, data, filepath ):
        f = open( filepath, 'w' )
        pickle.dump(data, f)
        f.close()

class PersistentDataRetriever:
    """
    Retrieves persitent data
    """
    import pickle
    def __init__( self, filepath ):
        self.filepath = filepath

    def get_data( self ):
        data = None
        if os.path.isfile( self.filepath ):
            f = open( self.filepath, 'r')
            try:
                data = pickle.load(f)
            except:
                pass
            f.close()
        return data
