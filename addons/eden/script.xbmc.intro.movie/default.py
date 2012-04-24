
import sys


if __name__ == "__main__":
    setting = "".join( sys.argv[ 1: ] )
    if setting:
        from resources.lib.settings import Main
        Main( setting.lower() )

    else:
        # play intro
        import resources.lib.intro
