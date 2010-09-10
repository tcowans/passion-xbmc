@ECHO OFF
CLS
COLOR 1B

rem based on Script by chadoe
rem http://xbmc.svn.sourceforge.net/viewvc/xbmc/trunk/project/Win32BuildSetup/buildscripts.bat

rem Set window title
TITLE Build All Addons!

SET SCRIPT_PATH="%1"
SET CUR_PATH=%CD%
ECHO ----------------------------------------------------------------------
ECHO Compiling addons...

:MakeBuildFolder
rem Create Build folder
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Creating \BUILD_ADDONS\ folder . . .
IF EXIST "%CUR_PATH%\BUILD_ADDONS" (
    RD "%CUR_PATH%\BUILD_ADDONS" /S /Q
)
MD "%CUR_PATH%\BUILD_ADDONS"
ECHO.

:MakeExcludeFile
rem Create exclude file
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Creating exclude.txt file . . .
ECHO.
ECHO .svn>"exclude.txt"
ECHO Thumbs.db>>"exclude.txt"
ECHO Desktop.ini>>"exclude.txt"

ECHO .pyo>>"exclude.txt"
ECHO .pyc>>"exclude.txt"
ECHO .bak>>"exclude.txt"

del error.log > NUL

ECHO ----------------------------------------------------------------------
ECHO.
SET /P zipaddon=Do you want create a zip for each Add-on.? [y/n]:
IF "%zipaddon:~0,1%"=="y" (
    SET zipaddons=y
) ELSE (
    SET zipaddons=n
)

rem optional plugins
SETLOCAL ENABLEDELAYEDEXPANSION

SET _BAT=""
FOR /F "tokens=*" %%S IN ('dir /B /AD "%SCRIPT_PATH%"') DO (
  IF "%%S" NEQ ".svn" (
    SET _BAT=""
    CD "%%S"
    ECHO ----------------------------------------------------------------------
    IF EXIST "build.bat" (
      ECHO Found build.bat for %%S
      SET _BAT=build.bat
    )
    IF !_BAT! NEQ "" (
      IF EXIST _btmp.bat del _btmp.bat > NUL
      rem create temp bat file without the pause statements in the original bat file.
      for /f "tokens=*" %%a in ('findstr /v /i /c:"pause" "!_BAT!"') do (
        IF "%%a" == "SET /P zipaddon=Do you want create a zip of the Add-on.? [Y/N]:" (
            echo SET zipaddon=%zipaddons%>> _btmp.bat
        ) else (
            IF NOT "%%a" == "ECHO Scroll up to check for errors." echo %%a>> _btmp.bat
        )
      )
      ECHO Building plugin %%S
      call _btmp.bat
      del "%CUR_PATH%\%%S\_btmp.bat" > NUL
      CD "%CUR_PATH%"
      if EXIST "%%S\BUILD\addons\%%S\addon.xml" (
        ECHO Copying build...
        ECHO "%%S\BUILD" "BUILD_ADDONS\%%S"
        xcopy "%%S\BUILD\addons" "%CUR_PATH%\BUILD_ADDONS" /E /Q /I /Y /EXCLUDE:exclude.txt > NUL
      ) ELSE (
        ECHO "%%S\BUILD\%%S\addon.xml not found, not including in build." >> error.log
      )
    ) ELSE (
      CD "%CUR_PATH%"
      IF EXIST "%%S\addon.xml" (
        ECHO Copying files...
        ECHO "%%S" "BUILD_ADDONS\%%S"
        xcopy "%%S" "%CUR_PATH%\BUILD_ADDONS\%%S" /E /Q /I /Y /EXCLUDE:exclude.txt > NUL
      ) ELSE (
        ECHO "No build.bat or addon.xml found for directory %%S, not including in build." >> error.log
      )
    )
  )
)

del exclude.txt > NUL
ENDLOCAL

:DONE
CD "%CUR_PATH%"
ECHO ======================================================================
pause