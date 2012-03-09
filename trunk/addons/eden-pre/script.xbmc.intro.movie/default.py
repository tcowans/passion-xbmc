
import sys


if __name__ == "__main__":
    setting = "".join( sys.argv[ 1: ] )
    if setting:
        from resources.lib.settings import Main
        Main( setting )

    else:
        # play intro
        import resources.lib.intro
