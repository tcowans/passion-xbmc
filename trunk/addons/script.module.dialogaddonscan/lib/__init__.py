# Dummy file to make this directory a package.

# prevent possible conflict remove old libs, if exists
import os
import glob

OLD_LIBS = [ "gui" ]

pathlib = "special://home/addons/script.module.dialogaddonscan/resources/lib/"

for old in OLD_LIBS:
    #for ext in [ ".py", ".pyo", ".pyc" ]:
    print glob.glob( pathlib + old + ".py*" )