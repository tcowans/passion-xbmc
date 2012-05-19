@ECHO OFF
CLS
COLOR 1B

:: Set our project name
FOR /F "Delims=" %%D IN ("%CD%") DO SET projectname=%%~nxD
:: Set our project version
SET projectversion=Frodo
:: Set our source of language
SET sourcelang=resources\language
:: Set our window title
SET xml2po=..\tools\xbmc-xml2po\xbmc-xml2po_v091

:: Set our window title
TITLE %projectname%-%projectversion% Build PO Strings!

ECHO ----------------------------------------
ECHO Creating PO Strings...
ECHO ----------------------------------------

START /B /WAIT %xml2po% -s %sourcelang% -p %projectname% -v %projectversion%

ECHO ----------------------------------------
ECHO PO Strings Created...
ECHO ----------------------------------------

pause
