[B]Property -> TvTunesIsAlive[/B]:
 return TRUE if tvtunes is currently playing a theme.mp3
 You can also use this visible condition to prevent activating visualisation or music background fanart.

<visible>!SubString(Window(10025).Property(TvTunesIsAlive),True)</visible>
OR
<visible>IsEmpty(Window(10025).Property(TvTunesIsAlive))</visible>


[B]Property -> TvTunesIsRunning[/B]:
 return TRUE if tvtunes is running in background/backend
 You can also use this visible condition to launch tvtunes is not started.

<window id="25">
    ...
    <onload condition="IsEmpty(Window(10025).Property(TvTunesIsRunning))">
RunScript(script.tvtunes,backend=true)</onload>
    ...
</window>
