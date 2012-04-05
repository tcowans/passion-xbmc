
How to use media of weather.fanart.pda.style

Install weather.fanart.pda.style to special://home/addons/weather.fanart.pda.style
Or create weather.fanart.pda.style-1.0.0.zip and install from zip with xbmc addons manager

<control type="multiimage">
    ...
    <imagepath>special://home/addons/weather.fanart.pda.style/media/$INFO[Window(Weather).Property(Current.FanartCode)]</imagepath>
    <timeperimage>100</timeperimage>
    <randomize>false</randomize>
    <fadetime>0</fadetime>
</control>

<control type="multiimage">
    ...
    <imagepath>special://home/addons/weather.fanart.pda.style/media/$INFO[Window(Weather).Property(Day[0-3].FanartCode)]</imagepath>
    <timeperimage>100</timeperimage>
    <randomize>false</randomize>
    <fadetime>0</fadetime>
</control>
