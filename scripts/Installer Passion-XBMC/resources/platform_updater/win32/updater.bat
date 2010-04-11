@ECHO OFF
CLS
COLOR 1B




::SET WINDOW TITLE
TITLE XBMC Updater 1.0 by Team Passion-XBMC

::FORCE XBMC TO CLOSE
ECHO Closing XBMC...
TaskKill /IM:XBMC.exe /F
IF "%ErrorLevel:~0,1%"=="0" (
  ECHO XBMC has been closed!
) ELSE (
  ECHO WRANING: It is better to close if XBMC is still running!
  ECHO Please close XBMC and/or press any key to continue ...
  pause > NUL
)

::POUR UNE RAISON X, XBMC CHANGE LE %CD% DU BAT POUR LA RACINE D'XBMC!!!!
SET InfoPaths="%CD%\paths.txt"

IF NOT EXIST %InfoPaths% (
  ECHO ------------------------------------------------------------------------
  ECHO.
  ECHO Error: %InfoPaths% not found!
  ECHO.
  GOTO NoUpdate
)

::CHECK IF CURRENT FOLDER IS SAME AS %CD%, SET THIS IS NOT SAME or FORCE 
SET /A line=0
FOR /F "tokens=2 delims==" %%a IN ('more/E +%%line%% ^< %InfoPaths%') DO (
  IF NOT DEFINED cd_real SET "cd_real=%%a"
)
::FORCE %CD%
CD %cd_real%
SET cd_real=

::SET UPDATER NAME BASED ON CURRENT PLATFORM DIRECTORY
FOR /F "Delims=" %%D IN ('ECHO %CD%') DO SET UpdaterName=%%~nD
::CHECK IF UPDATER NAME IS SAME AS win32, IS NOT SAME ERROR GOTO NOUPDATE :(
IF NOT "%UpdaterName%"=="win32" (
  ECHO ------------------------------------------------------------------------
  ECHO.
  ECHO Error: The working directory should be win32!
  ECHO [%UpdaterName%]: %CD%
  ECHO.
  ECHO ------------------------------------------------------------------------
  GOTO NoUpdate
)


:Begin
::CHANGE WINDOW TITLE
TITLE XBMC %UpdaterName% Updater 1.0 by Team Passion-XBMC

ECHO ------------------------------------------------------------------------
ECHO  ____   __    ___  ___  ____  _____  _  _      _  _  ____  __  __  ___ 
ECHO (  _ \ /__\  / __)/ __)(_  _)(  _  )( \( ) __ ( \/ )(  _ \(  \/  )/ __)
ECHO  )___//(__)\ \__ \\__ \ _)(_  )(_)(  )  ( (__) )  (  ) _ ( )    (( (__ 
ECHO (__) (__)(__)(___/(___/(____)(_____)(_)\_)    (_/\_)(____/(_/\/\_)\___)
ECHO  _    _  ____  __   _      __  __  ____  ____    __   ____  ____  ____ 
ECHO ( \/\/ )(_  _)(  \ ( ) __ (  )(  )(  _ \(  _ \  /__\ (_  _)( ___)(  _ \
ECHO  )    (  _)(_  ))\\(( (__) )(__)(  )___/ )(_) )/(__)\  )(   )__)  )   /
ECHO (__/\__)(____)(_) \__)    (______)(__)  (____/(__)(__)(__) (____)(_)\_)
ECHO.


::GET AND SET XBMC_INSTALL_PATH
SET /A line=1
FOR /F "tokens=2 delims==" %%a IN ('more/E +%%line%% ^< %InfoPaths%') DO (
  IF NOT DEFINED xbmc_install_path SET "xbmc_install_path=%%a"
)

::GET AND SET XBMC_BUILD
SET /A line=2
FOR /F "tokens=2 delims==" %%a IN ('more/E +%%line%% ^< %InfoPaths%') DO (
  IF NOT DEFINED xbmc_build SET "xbmc_build=%%a"
)

::OPTIONAL GET AND SET EXCLUDE_TXT 
SET exclude_txt=exclude.txt
rem SET /A line=3
rem FOR /F "tokens=2 delims==" %%a IN ('more/E +%%line%% ^< %InfoPaths%') DO (
rem   IF NOT DEFINED exclude_txt SET "exclude_txt=%%a"
rem )

:: GET XBMC IS ON PORTABLE MODE OR NOT
SET /A line=5
FOR /F "tokens=2 delims==" %%a IN ('more/E +%%line%% ^< %InfoPaths%') DO (
IF NOT DEFINED xbmc_is_portable SET "xbmc_is_portable=%%a"
)


::CHECK IF XBMC OR BUILD EXIST, IF NOT EXISTS GOTO NOUPDATE
ECHO ------------------------------------------------------------------------
ECHO.
IF EXIST %xbmc_install_path% (
  ECHO XBMC path found: %xbmc_install_path%
) ELSE (
  ECHO Error: XBMC path not found! %xbmc_install_path%
  ECHO.
  GOTO NoUpdate
)

IF EXIST %xbmc_build% (
  ECHO Build found: %xbmc_build%
) ELSE (
  ECHO Error: Build not found! %xbmc_build%
  ECHO.
  GOTO NoUpdate
)

::OPTIONAL FILE
IF EXIST %exclude_txt% (
  ECHO use exclude file: %exclude_txt%
  ::CONVERT IN WINDOWS FORMAT, BECAUSE XBMC WRITE FILE IN UNIX FORMAT AND XCOPY NOT WORK
  FOR /F "Delims=" %%D IN ('type %exclude_txt%') DO ECHO %%D >> "%CD%\exclude.tmp"
  DEL %exclude_txt% & REN "%CD%\exclude.tmp" exclude.txt
  SET exclude_txt=exclude.txt
) ELSE (
  ECHO Not use exclude file!
)
ECHO.


:MakeXBMCTempFolder
::CREATE XBMC TEMP FOLDER IN TEMP DIR
ECHO ------------------------------------------------------------------------
ECHO.
ECHO Creating XBMC temp folder...

Set XBMCTemp=%TEMP%\XBMC_TEMP

IF EXIST %XBMCTemp% (
  RD %XBMCTemp% /S /Q
)
MD %XBMCTemp%

IF EXIST "%CD%\LOGS" (
  RD "%CD%\LOGS" /S /Q
)
MD "%CD%\LOGS"
ECHO.
GOTO UnrarBuild


:UnrarBuild
  ::http://www.win-rar.com/index.php?id=24&kb_category_id=50
  ::WINRAR INSTALLED
  IF NOT EXIST "%ProgramFiles%\WinRAR\" (
    ECHO ------------------------------------------------------------------------
    ECHO.
    ECHO WinRAR not installed!  Skipping decompression...
    ECHO Visit and download WinRAR : http://www.rarlab.com/download.htm
    start http://www.rarlab.com/download.htm
    pause
    IF NOT EXIST "%ProgramFiles%\WinRAR\" ( GOTO NoUpdate )
    ECHO.
  )
  ::INSERT WINRAR TO APPLICATION PATH
  SET path="%ProgramFiles%\WinRAR\";%path%

  ECHO ------------------------------------------------------------------------
  ECHO.
  SET /P testbuild=Want to test the build before anything? [Y/N]:
  IF "%testbuild:~0,1%"=="y" (
    ECHO Testing build: %xbmc_build%
    ECHO Please wait...
    RAR t %xbmc_build%
    IF NOT "%ErrorLevel:~0,1%"=="0" (
      ECHO Error: %ErrorLevel%
      )
  )
  SET testbuild=
  ECHO.

  ::UNRAR BUILD
  ECHO ------------------------------------------------------------------------
  ECHO.
  ECHO Extracting build: %xbmc_build%
  ECHO Please wait...
  UNRAR x -o+ %xbmc_build% %XBMCTemp% > "%CD%\LOGS\unrar.log"
  rem ECHO Erreur numero %ErrorLevel%
  ECHO.
  ::METTRE ICI UNE FONCTION POUR LES ERREURS SI PAS D'ERREUR UPDATE
  IF NOT "%ErrorLevel:~0,1%"=="0" (
    GOTO NoUpdate
  ) ELSE (
    GOTO XBMCBackup
  )


:XBMCBackup
  ::CREATE BACKUP IF USER WANT, FULL XBMC DIR OR XBMC.EXE ONLY
  ECHO ----------------------------------------------------------------------
  ECHO.
  ::GET XBMC REVISION
  SET /A line=4
  FOR /F "tokens=2 delims==" %%a IN ('more/E +%%line%% ^< %InfoPaths%') DO (
    IF NOT DEFINED backup_revision SET "backup_revision=%%a"
  )
  SET BackupName=XBMC_Backup_%backup_revision%
  SET BackupPath=%xbmc_install_path:~1,3%%BackupName%
  ECHO XBMC Backup %backup_revision%!
  ECHO Backup Path: %BackupPath%
  ECHO.

  ECHO [1] Make a backup of the executable "XBMC.exe" only.
  ECHO [2] Make a full backup of the folder to installed XBMC.
  ECHO [Enter] Do nothing.
  ECHO.
  SET /P BackupMode=Enter the number of the desired method! [1/2/Enter]:
  IF "%BackupMode:~0,1%"=="1" (
    ECHO.
    ECHO Creating Backup:
    ECHO %xbmc_install_path:~1,-1%xbmc.exe -} %BackupPath%\xbmc.exe...
    ECHO Please wait...
    IF NOT EXIST %BackupPath% (
      MD %BackupPath%
    )
    COPY %xbmc_install_path%xbmc.exe %BackupPath%\xbmc.exe /B /V
    IF NOT "%ErrorLevel:~0,1%"=="0" (
      ECHO Error: The file were not backed up!
      )
  )
  IF "%BackupMode:~0,1%"=="2" (
    ::write exclude file for full backup, add non essential folder to exclude.txt
    ECHO cache > "%CD%\backup_exclude.txt"
    ECHO plugin >> "%CD%\backup_exclude.txt"
    ECHO scripts >> "%CD%\backup_exclude.txt"
    ECHO.
    ECHO Creating Full Backup:
    ECHO %xbmc_install_path:~1,-1% -} %BackupPath%...
    ECHO Please wait...
    IF NOT EXIST %BackupPath% (
      MD %BackupPath%
    )
    SET BackupExclude = "%CD%\backup_exclude.txt"
    XCOPY "%xbmc_install_path:~1,-2%" %BackupPath%\ /E /I /Y /F /V /EXCLUDE:%BackupExclude% > "%CD%\LOGS\backup.log"
    IF NOT "%ErrorLevel:~0,1%"=="0" (
      ECHO Error: The files were not backed up or have been part of it!
      )
  )
  ECHO.
  SET BackupName=
  SET BackupPath=
  SET BackupMode=
  GOTO Update


:Update
  ECHO ------------------------------------------------------------------------
  ECHO.
  ::GET BUILD NAME
  FOR /F %%a IN ('DIR /B %XBMCTemp%') DO SET BuildName=%%~na

  SET /P updatexbmc=Confirm to update your XBMC.? [Y/N]:
  IF NOT "%updatexbmc:~0,1%"=="y" (
    GOTO END
  )
  SET updatexbmc=
  ECHO.

  IF "%BuildName%"=="Setup" GOTO PCInstaller
  IF "%BuildName:~4,5%"=="Setup" GOTO PCInstaller

  ECHO Updating XBMC from %BuildName%...
  ECHO Please wait...

  SET copy_tempdir=
  IF EXIST %XBMCTemp%\%BuildName%\xbmc\XBMC.exe (
    SET copy_tempdir=%XBMCTemp%\%BuildName%\xbmc
  )
  IF EXIST %XBMCTemp%\%BuildName%\XBMC.exe (
    SET copy_tempdir=%XBMCTemp%\%BuildName%
  )

  IF EXIST %exclude_txt% (
      XCOPY %copy_tempdir% %xbmc_install_path% /E /I /Y /F /V /EXCLUDE:%exclude_txt% > "%CD%\LOGS\update.log"
      rem XCOPY %copy_tempdir% xbmc /E /I /Y /F /V /EXCLUDE:%exclude_txt% > "%CD%\LOGS\update.log"
  ) ELSE (
      XCOPY %copy_tempdir% %xbmc_install_path% /E /I /Y /F /V > "%CD%\LOGS\update.log"
      rem XCOPY %copy_tempdir% xbmc /E /I /Y /F /V > "%CD%\LOGS\update.log"
  )
  IF NOT "%ErrorLevel:~0,1%"=="0" (
    ECHO He seems to have been an unexpected error!
    SET /P showlog=Do you see the log of the update? [Y/N]:
    IF NOT "%showlog:~0,1%"=="Y" (
      NOTEPAD "%CD%\LOGS\update.log"
    )
    SET showlog=
    GOTO NoUpdate
  )
  ECHO.
  ECHO Update Done!
  ECHO.
  ECHO ------------------------------------------------------------------------
  ECHO                    ___  _   _  ____  ____  ____  ___ 
  ECHO                   / __)( )_( )( ___)( ___)(  _ \/ __)
  ECHO                  ( (__  ) _ (  )__)  )__)  )   /\__ \
  ECHO                   \___)(_) (_)(____)(____)(_)\_)(___/
  ECHO.
  ECHO ------------------------------------------------------------------------
  DEL %InfoPaths%
  GOTO LaunchXBMC


:LaunchXBMC
  ECHO.
  SET LaunchMode=
  SET YesNo=

  IF %xbmc_is_portable%=="" (
    ECHO Would you launch XBMC?
    ECHO.
    ECHO [1] To run in normal mode.
    ECHO [2] To run in portable mode.
    ECHO [Enter] Do nothing.
    ECHO.
    SET /P LaunchMode=Enter number! [1/2/Enter]:
  )

  IF NOT %xbmc_is_portable%=="" (
    SET /P YesNo=Would you launch XBMC? [Y/N]:
  )

  IF "%YesNo:~0,1%"=="y" (
    IF %xbmc_is_portable%=="false" SET LaunchMode=1 
    IF %xbmc_is_portable%=="true" SET LaunchMode=2
  )

  IF "%LaunchMode:~0,1%"=="1" (
    START /D%xbmc_install_path% XBMC.exe
    EXIT
  ) 
  IF "%LaunchMode:~0,1%"=="2" (
    START /D%xbmc_install_path% XBMC.exe -p
    EXIT
  )
  ECHO.
  ECHO ------------------------------------------------------------------------
  GOTO END


:PCInstaller
  DEL %InfoPaths%
  IF EXIST "%XBMCTemp%\%BuildName%.exe" (
    START %XBMCTemp%\%BuildName%.exe
    EXIT
  ) ELSE (
    ECHO Impossible to launch Windows Installer!
    ECHO.
    ECHO ------------------------------------------------------------------------
    GOTO END
    )


:NoUpdate
  DEL %InfoPaths%
  ECHO ------------------------------------------------------------------------
  ECHO.
  ECHO Impossible to update XBMC!
  ECHO.
  ECHO ------------------------------------------------------------------------
  GOTO END


:END
  ECHO Scroll up to check for errors.
  PAUSE
