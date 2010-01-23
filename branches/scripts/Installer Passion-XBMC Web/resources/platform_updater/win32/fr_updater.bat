@ECHO OFF
CLS
COLOR 1B
::Special note for French only, don't edit fr_updater.bat but fr_updater.txt and use
::this tuto http://blogmotion.fr/programmation/batch/convertir-au-formatage-dos-96
::for convert French character, DOS a recognized text.

::SET WINDOW TITLE
TITLE XBMC Updater 1.0 by Team Passion-XBMC

::FORCE XBMC TO CLOSE
ECHO Fermeture d'XBMC...
TaskKill /IM:XBMC.exe /F
IF "%ErrorLevel:~0,1%"=="0" (
  ECHO XBMC a ‚t‚ ferm‚!
) ELSE (
  ECHO ATTENTION: Il est pr‚f‚rable de fermer XBMC s'il est encore en marche!
  ECHO Veuillez fermer XBMC et/ou appuyez sur une touche pour continuer...
  pause > NUL
)

::POUR UNE RAISON X, XBMC CHANGE LE %CD% DU BAT POUR LA RACINE D'XBMC!!!!
SET InfoPaths="%CD%\paths.txt"

IF NOT EXIST %InfoPaths% (
  ECHO ------------------------------------------------------------------------
  ECHO.
  ECHO Erreur: %InfoPaths% non trouv‚!
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
  ECHO Erreur: Le r‚pertoire de travail doit ˆtre win32!
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
  ECHO Chemin XBMC trouv‚: %xbmc_install_path%
) ELSE (
  ECHO Erreur: Chemin XBMC non trouv‚! %xbmc_install_path%
  ECHO.
  GOTO NoUpdate
)

IF EXIST %xbmc_build% (
  ECHO Build trouv‚e: %xbmc_build%
) ELSE (
  ECHO Erreur: Build non trouv‚e! %xbmc_build%
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
ECHO Cr‚ation du r‚pertoire temporaire d'XBMC...

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
    ECHO WinRAR n'est pas install‚!  D‚compression annul‚e...
    ECHO Visiter et t‚l‚charger WinRAR : http://www.rarlab.com/download.htm
    start http://www.rarlab.com/download.htm
    pause
    IF NOT EXIST "%ProgramFiles%\WinRAR\" ( GOTO NoUpdate )
    ECHO.
  )
  ::INSERT WINRAR TO APPLICATION PATH
  SET path="%ProgramFiles%\WinRAR\";%path%

  ECHO ------------------------------------------------------------------------
  ECHO.
  SET /P testbuild=Voulez-vous tester la build avant toute chose? [O/N]:
  IF "%testbuild:~0,1%"=="o" (
    ECHO Analyse de la build: %xbmc_build%
    ECHO Veuillez patienter...
    RAR t %xbmc_build%
    IF NOT "%ErrorLevel:~0,1%"=="0" (
      ECHO Erreur: %ErrorLevel%
      )
  )
  SET testbuild=
  ECHO.

  ::UNRAR BUILD
  ECHO ------------------------------------------------------------------------
  ECHO.
  ECHO Extraction de la build: %xbmc_build%
  ECHO Veuillez patienter...
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
  ECHO Chemin de la sauvegarde: %BackupPath%
  ECHO.

  ECHO [1] Effectuer une sauvegarde de l'ex‚cutable "XBMC.exe" seulement.
  ECHO [2] Effectuer une sauvegarde complŠte du dossier d'installation d'XBMC.
  ECHO [Enter] Ne rien faire.
  ECHO.
  SET /P BackupMode=Entr‚e le num‚ro de la m‚thode d‚sir‚e! [1/2/Enter]:
  IF "%BackupMode:~0,1%"=="1" (
    ECHO.
    ECHO Cr‚ation de la sauvegarde:
    ECHO %xbmc_install_path:~1,-1%xbmc.exe -} %BackupPath%\xbmc.exe...
    ECHO Veuillez patienter...
    IF NOT EXIST %BackupPath% (
      MD %BackupPath%
    )
    COPY %xbmc_install_path%xbmc.exe %BackupPath%\xbmc.exe /B /V
    IF NOT "%ErrorLevel:~0,1%"=="0" (
      ECHO Erreur: Le fichier n'ont pas ‚t‚ sauvegard‚!
      )
  )
  IF "%BackupMode:~0,1%"=="2" (
    ::WRITE EXCLUDE FILE FOR FULL BACKUP, ADD NON ESSENTIAL FOLDER TO exclude.txt
    ECHO cache > "%CD%\backup_exclude.txt"
    ECHO plugin >> "%CD%\backup_exclude.txt"
    ECHO scripts >> "%CD%\backup_exclude.txt"
    ECHO.
    ECHO Cr‚ation de la sauvegarde complŠte:
    ECHO %xbmc_install_path:~1,-1% -} %BackupPath%...
    ECHO Veuillez patienter...
    IF NOT EXIST %BackupPath% (
      MD %BackupPath%
    )
    XCOPY "%xbmc_install_path:~1,-2%" %BackupPath%\ /E /I /Y /F /V /EXCLUDE:"%CD%\backup_exclude.txt" > "%CD%\LOGS\backup.log"
    IF NOT "%ErrorLevel:~0,1%"=="0" (
      ECHO Erreur: Les fichiers n'ont pas ‚t‚ sauvegard‚s ou l'ont ‚t‚ en partie!
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

  SET /P updatexbmc=Confirmer la mise … jour de votre XBMC? [O/N]:
  IF NOT "%updatexbmc:~0,1%"=="o" (
    GOTO END
  )
  SET updatexbmc=
  ECHO.

  IF "%BuildName%"=="Setup" GOTO PCInstaller

  ECHO Mise … jour d'XBMC depuis %BuildName%...
  ECHO Veuillez patienter...

  IF EXIST %exclude_txt% (
      XCOPY %XBMCTemp%\%BuildName%\xbmc %xbmc_install_path% /E /I /Y /F /V /EXCLUDE:%exclude_txt% > "%CD%\LOGS\update.log"
      rem XCOPY %XBMCTemp%\%BuildName%\xbmc xbmc /E /I /Y /F /V /EXCLUDE:%exclude_txt% > "%CD%\LOGS\update.log"
  ) ELSE (
      XCOPY %XBMCTemp%\%BuildName%\xbmc %xbmc_install_path% /E /I /Y /F /V > "%CD%\LOGS\update.log"
      rem XCOPY %XBMCTemp%\%BuildName%\xbmc xbmc /E /I /Y /F /V > "%CD%\LOGS\update.log"
  )
  IF NOT "%ErrorLevel:~0,1%"=="0" (
    ECHO Il semble avoir eu une erreur impr‚vue!
    SET /P showlog=Voulez-vous voir le log de la MAJ? [O/N]:
    IF NOT "%showlog:~0,1%"=="o" (
      NOTEPAD "%CD%\LOGS\update.log"
    )
    SET showlog=
  )
  ECHO.
  ECHO Mise … jour effectu‚e!
  ECHO.
  ECHO ------------------------------------------------------------------------
  ECHO                    ___  _   _  ____  ____  ____  ___ 
  ECHO                   / __)( )_( )( ___)( ___)(  _ \/ __)
  ECHO                  ( (__  ) _ (  )__)  )__)  )   /\__ \
  ECHO                   \___)(_) (_)(____)(____)(_)\_)(___/
  ECHO.
  ECHO ------------------------------------------------------------------------
  DEL paths.txt
  GOTO LaunchXBMC


:LaunchXBMC
  ECHO.

  SET /A line=5
  FOR /F "tokens=2 delims==" %%a IN ('more/E +%%line%% ^< %InfoPaths%') DO (
    IF NOT DEFINED xbmc_is_portable SET "xbmc_is_portable=%%a"
  )

  SET LaunchMode=
  SET YesNo=

  IF %xbmc_is_portable%=="" (
    ECHO D‚sirez-vous lancer XBMC?
    ECHO.
    ECHO [1] Pour le lancer en mode normal.
    ECHO [2] Pour le lancer en mode portable.
    ECHO [Enter] Ne rien faire.
    ECHO.
    SET /P LaunchMode=Entr‚e le num‚ro! [1/2/Enter]:
  )

  IF NOT %xbmc_is_portable%=="" (
    SET /P YesNo=D‚sirez-vous lancer XBMC? [O/N]:
  )

  IF "%YesNo:~0,1%"=="o" (
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
  DEL paths.txt
  IF EXIST "%XBMCTemp%\Setup.exe" (
    START %XBMCTemp%\Setup.exe
    EXIT
  ) ELSE (
    ECHO Impossible de lancer Windows Installer!
    ECHO.
    ECHO ------------------------------------------------------------------------
    GOTO END
    )


:NoUpdate
  DEL paths.txt
  ECHO ------------------------------------------------------------------------
  ECHO.
  ECHO Impossible de mettre … jour XBMC!
  ECHO.
  ECHO ------------------------------------------------------------------------
  GOTO END


:END
  ECHO D‚filer vers le haut pour v‚rifier les erreurs.
  PAUSE
