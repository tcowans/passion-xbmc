@ECHO OFF
CLS
COLOR 1B

:Begin
:: Set Addon name based on current directory fullname
FOR /F "Delims=" %%D IN ("%CD%") DO SET AddonName=%%~nxD

:: Set window title
TITLE %AddonName% Build Addon!

:MakeBuildFolder
:: Create Build folder
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Creating \BUILD\addons\%AddonName%\ folder . . .
IF EXIST BUILD (
    RD BUILD /S /Q
)
MD BUILD
ECHO.

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
ECHO .bak>>"BUILD\exclude.txt"

:MakeReleaseBuild
:: Create release build
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Copying required files to \Build\addons\%AddonName%\ folder . . .
XCOPY lib "BUILD\addons\%AddonName%\lib" /E /Q /I /Y /EXCLUDE:BUILD\exclude.txt
XCOPY media "BUILD\addons\%AddonName%\media" /E /Q /I /Y /EXCLUDE:BUILD\exclude.txt
XCOPY sounds "BUILD\addons\%AddonName%\sounds" /E /Q /I /Y /EXCLUDE:BUILD\exclude.txt
COPY default.py "BUILD\addons\%AddonName%\"
COPY addon.xml "BUILD\addons\%AddonName%\"
ECHO.
ECHO Copying optional files to \Build\addons\%AddonName%\ folder . . .
IF EXIST "icon.png" COPY icon.png "BUILD\addons\%AddonName%\"
IF EXIST "fanart.jpg" COPY fanart.jpg "BUILD\addons\%AddonName%\"
IF EXIST "changelog.txt" COPY changelog.txt "BUILD\addons\%AddonName%\"

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
    ECHO [1] Yes, copy a new "\Build\addons\%AddonName%\ to %XBMC_EXE%\addons\%AddonName%\"
    ECHO [2] Yes, copy a new build and run XBMC...
    ECHO [3] No, i prefer copied manually
    ECHO [4] Create ZIP "BUILD\addons\%AddonName%.zip"
    ECHO.
    ECHO ----------------------------------------------------------------------
    SET /P COPY_BUILD_ANSWER=Copy a new BUILD? [1/2/3/4]:
    IF /I %COPY_BUILD_ANSWER% EQU 1 GOTO COPY_BUILD
    IF /I %COPY_BUILD_ANSWER% EQU 2 GOTO COPY_BUILD
    IF /I %COPY_BUILD_ANSWER% EQU 3 GOTO Finish
    IF /I %COPY_BUILD_ANSWER% EQU 4 GOTO ZIP_BUILD

:COPY_BUILD
    :: Copy release build
    ECHO ----------------------------------------------------------------------
    ECHO.
    ECHO Copying "\Build\addons\%AddonName%\ to \XBMC\addons\%AddonName%\" folder . . .
    rem ren "%XBMC_EXE%\addons\%AddonName%\" %AddonName%_old
    XCOPY "BUILD\addons\%AddonName%" "%XBMC_EXE%\addons\%AddonName%\" /E /Q /I /Y
    ECHO.

    :: Notify user of completion of copy
    ECHO ======================================================================
    ECHO.
    ECHO Build Complete and Copied.
    ECHO.
    ECHO ======================================================================
    ECHO.

    IF /I %COPY_BUILD_ANSWER% EQU 2 (
        ECHO Starting XBMC ...
        ECHO.
        ECHO ======================================================================
        start /D"%XBMC_EXE%" XBMC.exe -p
        )

    GOTO END

:ZIP_BUILD
    set ZIP="%ProgramFiles%\7-Zip\7z.exe"
    set ZIP_ROOT=7z.exe
    set ZIPOPS_EXE=a -tzip "%AddonName%.zip" "%AddonName%"
    ECHO IF EXIST %ZIP% ( %ZIP% %ZIPOPS_EXE%>>"BUILD\addons\zip_build.bat"
    ECHO   ) ELSE (>>"BUILD\addons\zip_build.bat"
    ECHO   IF EXIST %ZIP_ROOT% ( %ZIP_ROOT% %ZIPOPS_EXE%>>"BUILD\addons\zip_build.bat"
    ECHO     ) ELSE (>>"BUILD\addons\zip_build.bat"
    ECHO     ECHO  not installed!  Skipping .zip compression...>>"BUILD\addons\zip_build.bat"
    ECHO     )>>"BUILD\addons\zip_build.bat"
    ECHO   )>>"BUILD\addons\zip_build.bat"
    cd BUILD\addons\
    ECHO Compressing "BUILD\addons\%AddonName%.zip"...
    CALL zip_build.bat
    ::cd ..
    ::DEL "BUILD\zip_build.bat"
    DEL zip_build.bat
    GOTO Finish

:Finish
    :: Notify user of completion
    ECHO ======================================================================
    ECHO.
    ECHO Build Complete.
    ECHO.
    ECHO Final build is located in the \BUILD\addons\ folder.
    ECHO.
    ECHO copy: \addons\%AddonName%\ folder from the \BUILD\addons\ folder
    ECHO to: /XBMC/addons/ folder.
    ECHO.
    ECHO ======================================================================
    ECHO.
    GOTO END

:END
    ECHO Scroll up to check for errors.
    PAUSE