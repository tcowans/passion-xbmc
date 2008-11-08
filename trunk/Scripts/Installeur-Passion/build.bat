@ECHO OFF
CLS
COLOR 1B

:Begin
:: Set script name based on current directory
FOR /F "Delims=" %%D IN ('ECHO %CD%') DO SET ScriptName=%%~nD

:: Set window title
TITLE %ScriptName% Build Script!

:MakeBuildFolder
:: Create Build folder
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Creating \BUILD\%ScriptName%\ folder . . .
IF EXIST BUILD (
    RD BUILD /S /Q
)
MD BUILD
ECHO.

:GetRevision
:: Extract Revision # and SET %Revision% variable
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Extracting revision number . . .
ECHO.
FOR /F "Tokens=2* Delims=]" %%R IN ('FIND /v /n "&_&_&_&" ".svn\entries" ^| FIND "[11]"') DO SET Revision=%%R

:MakeExcludeFile
:: Create exclude file
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Creating exclude.txt file . . .
ECHO.
ECHO .svn>"BUILD\exclude.txt"
ECHO Thumbs.db>>"BUILD\exclude.txt"
ECHO Desktop.ini>>"BUILD\exclude.txt"

ECHO .pyo>>"BUILD\exclude.txt"
ECHO .pyc>>"BUILD\exclude.txt"

:MakeReleaseBuild
:: Create release build
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Copying required files to \Build\%ScriptName%\ folder . . .
XCOPY resources "BUILD\%ScriptName%\resources" /E /Q /I /Y /EXCLUDE:BUILD\exclude.txt
COPY default.tbn "BUILD\%ScriptName%\"

:: Create new default.py with __svn_revision__ embedded
ECHO # %ScriptName% script revision: %Revision% - built with build.bat version 1.0 #> "BUILD\%ScriptName%\default.py"
FOR /F "Tokens=1* Delims=]" %%L IN ('FIND /v /n "&_&_&_&" default.py') DO (
    IF /I "%%M"=="__svn_revision__ = 0" (
        ECHO __svn_revision__ = "%Revision%">> "BUILD\%ScriptName%\default.py"
    ) ELSE IF "%%M"=="" (
        ECHO.>> "BUILD\%ScriptName%\default.py"
    ) ELSE (
        ECHO %%M>> "BUILD\%ScriptName%\default.py"
        )
    )
)
ECHO.

:Cleanup
:: Delete exclude.txt file
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Cleaning up . . .
DEL "BUILD\exclude.txt"
ECHO.
ECHO.

:: XBMC is installed
SET XBMC_EXE=%ProgramFiles%\XBMC
IF EXIST "%XBMC_EXE%" (
    GOTO XBMC_EXIST
) ELSE (
    GOTO Finish
)

:XBMC_EXIST
    ECHO ----------------------------------------------------------------------
    ECHO.
    ECHO XBMC is installed on your PC!
    ECHO [1] Yes, copy a new "\Build\%ScriptName%\ to %XBMC_EXE%\scripts\%ScriptName%\"
    ECHO [2] Yes, copy a new build and run XBMC in fullscreen
    ECHO [3] No, i prefer copied manually
    ECHO.
    ECHO ----------------------------------------------------------------------
    SET /P COPY_BUILD_ANSWER=Copy a new BUILD? [1/2/3]:
    IF /I %COPY_BUILD_ANSWER% EQU 1 GOTO COPY_BUILD
    IF /I %COPY_BUILD_ANSWER% EQU 2 GOTO COPY_BUILD
    IF /I %COPY_BUILD_ANSWER% EQU 3 GOTO Finish

:COPY_BUILD
    :: Copy release build
    ECHO ----------------------------------------------------------------------
    ECHO.
    ECHO Copying "\Build\%ScriptName%\ to \XBMC\scripts\%ScriptName%\" folder . . .
    rem ren "%XBMC_EXE%\scripts\%ScriptName%\" %ScriptName%_old
    XCOPY "BUILD\%ScriptName%" "%XBMC_EXE%\scripts\%ScriptName%\" /E /Q /I /Y
    ECHO.

    :: Notify user of completion of copy
    ECHO ======================================================================
    ECHO.
    ECHO Build Complete and Copied.
    ECHO.
    ECHO ======================================================================
    ECHO.

    IF /I %COPY_BUILD_ANSWER% EQU 2 (
        ECHO Starting XBMC in fullscreen.
        ECHO.
        ECHO ======================================================================
        start /D"%XBMC_EXE%" XBMC.exe -fs -p
        )

    GOTO END

:Finish
    :: Notify user of completion
    ECHO ======================================================================
    ECHO.
    ECHO Build Complete.
    ECHO.
    ECHO Final build is located in the \BUILD\ folder.
    ECHO.
    ECHO copy: \%ScriptName%\ folder from the \BUILD\ folder.
    ECHO to: /XBMC/scripts/ folder.
    ECHO.
    ECHO ======================================================================
    ECHO.
    GOTO END

:END
    ECHO Scroll up to check for errors.
    PAUSE