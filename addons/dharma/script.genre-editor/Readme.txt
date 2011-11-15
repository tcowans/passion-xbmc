Installation :
Copy script.genre-editor folder in C:\Users\Yourusername\AppData\Roaming\XBMC\addons\
or
use addon manager in xbmc

Use:
for movie: <onclick>XBMC.RunScript(script.genre-editor,"$INFO[ListItem.Title]","$INFO[ListItem.FileName]")</onclick>
for tvshow: <onclick>XBMC.RunScript(script.genre-editor,"$INFO[ListItem.TVShowTitle]","TVShow")</onclick>


Example of simple Integration in Confluence :
Edit "C:\Program Files (x86)\XBMC\addons\skin.confluence\720p\DialogVideoInfo.xml"
search <control type="button" id="5">
insert before :
<control type="button" id="103">
	<description>Edit genre</description>
	<visible>container.content(movies)</visible>
	<include>ButtonInfoDialogsCommonValues</include>
	<onclick>XBMC.RunScript(script.genre-editor,"$INFO[ListItem.Title]","$INFO[ListItem.FileName]")</onclick>
	<label>Edit genre</label>
</control>
<control type="button" id="102">
	<description>Edit genre</description>
	<visible>container.content(episodes) | container.content(TVShows) | container.content(seasons)</visible>
	<include>ButtonInfoDialogsCommonValues</include>
	<onclick>XBMC.RunScript(script.genre-editor,"$INFO[ListItem.TVShowTitle]","TVShow")</onclick>
	<label>Edit genre</label>
</control>