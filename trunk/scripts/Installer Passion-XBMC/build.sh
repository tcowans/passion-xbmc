#!/bin/bash

cleanup() {
  if [ -d "$1" ]
  then
    printf "\r  Cleaning %-60.60s" "$1"
    rm -rf "$1/.svn" &> /dev/null
    for I in "$1"/*
    do
      cleanup "${I}"
    done
  fi
}

SCRIPTNAME="${PWD##*/}"
BUILDDIR="BUILD/$SCRIPTNAME"

echo -ne "]0;$SCRIPTNAME Build Script!"

if [[ -e "$BUILDDIR" ]]
then
  echo " Removing existing $BUILDDIR"
  rm -rf "$BUILDDIR" &> /dev/null
fi

echo " Creating $BUILDDIR"
mkdir -p "$BUILDDIR"

echo " Extracting revision number"
REVISION=$(expr "$(svn info 2>&1 | grep "Revision")" : '.*: \(.*\)')

echo " Copying required files to $BUILDDIR"

for I in *
do
  if ! [[ $I == "build.sh" || $I == "build.bat" || $I == "BUILD" ]]
  then
    cp -rf "$I" "$BUILDDIR" &> /dev/null
  fi
done

echo " Performing cleanup"
cleanup "$BUILDDIR"
echo

echo " Embedding revision number in default.py"
sed -i "s/__svn_revision__\ =\ 0/__svn_revision__\ =\ $REVISION/" "$BUILDDIR/default.py" 
echo "======================================================================"
echo "Build Complete - Scroll up to check for errors."
echo "Final build is located in the \BUILD\ direcory."
echo "copy: $SCRIPTNAME folder from the \BUILD\ folder."
echo "to: /XBMC/scripts/ folder."
echo "======================================================================"

