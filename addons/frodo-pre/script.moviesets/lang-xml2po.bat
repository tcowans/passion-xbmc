@ECHO OFF
CLS
COLOR 1B

:: Set our project name
FOR /F "Delims=" %%D IN ("%CD%") DO SET projectname=%%~nxD
:: Set our xml2po
SET xml2po=..\tools\xbmc-xml2po\xbmc-xml2po

:: Set our window title
TITLE %projectname%-%projectversion% Build PO Strings!

ECHO ----------------------------------------
ECHO Creating PO Strings...
ECHO ----------------------------------------

START /B /WAIT %xml2po% -s "%CD%"

ECHO ----------------------------------------
ECHO PO Strings Created...
ECHO ----------------------------------------

pause
