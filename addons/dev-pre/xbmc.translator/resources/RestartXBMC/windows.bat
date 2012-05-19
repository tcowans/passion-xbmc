@ECHO OFF
CLS
COLOR 1B

::SET WINDOW TITLE
TITLE Restarting XBMC ...

ECHO ---------------------------------------------------------------------------
echo                         :                                                  
echo                        :::                                                 
echo                        ::::                                                
echo                        ::::                                                
echo    :::::::       :::::::::::::::::        ::::::      ::::::        :::::::
echo    :::::::::   ::::::::::::::::::::     ::::::::::  ::::::::::    :::::::::
echo     ::::::::: ::::::::::::::::::::::   ::::::::::::::::::::::::  ::::::::: 
echo          :::::::::     :::      ::::: :::::    ::::::::    :::: :::::      
echo           ::::::      ::::       :::: ::::      :::::       :::::::        
echo           :::::       ::::        :::::::       :::::       ::::::         
echo           :::::       :::         ::::::         :::        ::::::         
echo           ::::        :::         ::::::        ::::        ::::::         
echo           ::::        :::        :::::::        ::::        ::::::         
echo          :::::        ::::       :::::::        ::::        ::::::         
echo         :::::::       ::::      ::::::::        :::         :::::::        
echo     :::::::::::::::    :::::  ::::: :::         :::         :::::::::      
echo  :::::::::  :::::::::  :::::::::::  :::         :::         ::: :::::::::  
echo  ::::::::    :::::::::  :::::::::   :::         :::         :::  ::::::::  
echo ::::::         :::::::    :::::     :            ::          ::    ::::::  

ECHO ---------------------------------------------------------------------------
::FORCE XBMC TO CLOSE
::tasklist /fi "Imagename eq XBMC.exe"
ECHO Closing XBMC ...
TaskKill /IM:XBMC.exe /F

::XBMC CHANGE LE %CD% DU BAT POUR LA RACINE D'XBMC.
SET xbmcPath=%CD%
IF NOT EXIST "%xbmcPath%\XBMC.exe" (
    SET xbmcPath=C:\Program Files\XBMC
)

ECHO ---------------------------------------------------------------------------
ECHO Starting XBMC ...
:: SLEEP 7 SECONDE
PING -n 7 localhost > NUL
:: START XBMC
START /D"%xbmcPath%" XBMC.exe

::PAUSE > NUL
