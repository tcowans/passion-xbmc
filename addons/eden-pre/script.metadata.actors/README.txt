Parameters:
Simply add $INFO[ListItem.foo]

For example:
XBMC.RunScript(script.metadata.actors,$INFO[ListItem.foo])


Launch from Library MovieActors, MovieDirectors or TvShowActors.
Add button in DialogContextMenu.xml in main grouplist.

<control type="grouplist" id="996">
	<description>grouplist for context buttons</description>
	...
	<control type="button" id="1245">
		<description>actor/director info button (visible only container is MovieActors, MovieDirectors or TvShowActors)</description>
		...
		<label>[Infos] $INFO[ListItem.Label]</label>
		<onclick>RunScript(script.metadata.actors,$INFO[ListItem.Label])</onclick>
		<visible>System.HasAddon(script.metadata.actors) + [SubString(Container.FolderPath,videodb://1/4/) | SubString(Container.FolderPath,videodb://1/5/) | SubString(Container.FolderPath,videodb://2/4/)]</visible>
	</control>
	...
</control>


Launch from DialogVideoInfo.xml for actor infos: (create a new button and keep $INFO[Container(50).Listitem.Label] )

<control type="button" id="????">
	<description>actor info button</description>
	...
	<onclick>RunScript(script.metadata.actors,$INFO[Container(50).Listitem.Label])</onclick>
	<visible>Control.IsVisible(50) + System.HasAddon(script.metadata.actors)</visible>
</control>


Launch from DialogVideoInfo.xml for director/writer infos:

<onclick condition="System.HasAddon(script.metadata.actors)">RunScript(script.metadata.actors,$INFO[ListItem.Director])</onclick>
<onclick condition="System.HasAddon(script.metadata.actors)">RunScript(script.metadata.actors,$INFO[ListItem.Writer])</onclick>


Special Launch for Artists from DialogAlbumInfo.xml:

<control type="button" id="15">
	<description>Filmography</description>
	...
	<label>Filmography</label>
	<onclick>RunScript(script.metadata.actors,$INFO[Listitem.Artist])</onclick>
	<visible>container.content(Artists) + System.HasAddon(script.metadata.actors)</visible>
</control>


Available Property for hide DialogVideoInfo.xml / DialogAlbumInfo.xml:
Window.Property(script.metadata.actors.isactive): return 1 or empty

For example:

<animation effect="slide" start="1100,0" end="0,0" time="400" condition="!StringCompare(Window.Property(script.metadata.actors.isactive),1)">Conditional</animation>
<animation effect="slide" start="0,0" end="1100,0" time="400" condition="StringCompare(Window.Property(script.metadata.actors.isactive),1)">Conditional</animation>


-------------------------------------------------------------------------------------------------------------------------------------------------------------------


List of Built In Controls Available In script-Actors-DialogInfo.xml:

5 ----> button -----> Toggle between Biography and Known Movies
6 ----> button -----> Refresh actor information
8 ----> button -----> Browse your movies of the currently selected actor
10 ---> button -----> Get actor thumbnail
11 ---> button -----> edit (require tmdb account)
20 ---> button -----> Get actor fanart
25 ---> button -----> open add-on settings
50 ---> container --> window actor info
150 --> container --> movies list (acting / directing / writing)
250 --> container --> thumbs list of actor


Labels Available In script-Actors-DialogInfo.xml:

Labels of the currently selected actor / director / writer / artist
Listitem.Title -------------------> Name
Listitem.Label -------------------> Same as Title
ListItem.Icon --------------------> icon
ListItem.Plot --------------------> Biography
ListItem.Property(Biography) -----> Same as Plot
ListItem.Property(Biooutline) ----> (currently not used)
ListItem.Property(TotalMovies) ---> Total of Known Movies (acting / directing / writing)
ListItem.Property(Birthday) ------> Date of Birthday
ListItem.Property(Age) -----------> Age (30)
ListItem.Property(AgeLong) -------> Age long format (age 30)
ListItem.Property(Deathday) ------> Date of Deathday
ListItem.Property(Deathage) ------> Age of dead (30)
ListItem.Property(DeathageLong) --> Age of dead long format (age 30)
ListItem.Property(PlaceOfBirth) --> Place of birth
ListItem.Property(AlsoKnownAs) ---> Also Known Name
ListItem.Property(Homepage) ------> Link of homepage, you can use onclick for open web browser directly on homepage: RunScript(script.metadata.actors,homepage=$INFO[ListItem.Property(Homepage)])
ListItem.Property(Adult) ---------> Is Adult Actor (no / yes)
ListItem.Property(Fanart_Image) --> Fanart

Labels of Known Movies list
Container(150).ListItem.Label ----------------------> Title of movie (format: "year  title [name of role / director / writer / etc]")
Container(150).Listitem.Icon -----------------------> icon of movie
Container(150).ListItem.Property(LibraryHasMovie) --> return 1 or empty, if movie exists in library

Labels of thumbs list
Container(250).ListItem.Label -------------------> Image résolution (512x720)
Container(250).Listitem.Icon --------------------> Image
Container(250).ListItem.Property(aspect_ratio) --> Aspect Ratio (0.66)


-------------------------------------------------------------------------------------------------------------------------------------------------------------------

** BACKEND **

For example:
<onload condition="System.HasAddon(script.metadata.actors)">RunScript(script.metadata.actors,backend)</onload>

Labels Available from backend in video/music library.

Window.Property(current.actor.name) ----------> Name
Window.Property(current.actor.biography) -----> Same as Plot
Window.Property(current.actor.biooutline) ----> (currently not used)
Window.Property(current.actor.birthday) ------> Date of Birthday
Window.Property(current.actor.age) -----------> Age (30)
Window.Property(current.actor.agelong) -------> Age long format (age 30)
Window.Property(current.actor.deathday) ------> Date of Deathday
Window.Property(current.actor.deathage) ------> Age of dead (30)
Window.Property(current.actor.deathagelong) --> Age of dead long format (age 30)
Window.Property(current.actor.placeofbirth) --> Place of birth
Window.Property(current.actor.alsoknownas) ---> Also Known Name
Window.Property(current.actor.homepage) ------> Link of homepage, you can use onclick for open web browser directly on homepage: RunScript(script.metadata.actors,homepage=$INFO[Window.Property(current.actor.homepage)])
Window.Property(current.actor.adult) ---------> Is Adult Actor (no / yes)

Window.Property(current.actor.icon) ----------> icon
Window.Property(current.actor.fanart_image) --> Fanart
Window.Property(current.actor.extrafanart) ---> extrafanart (return empty if not exists)
Window.Property(current.actor.extrathumb) ----> extrathumb (return empty if not exists)

Window.Property(current.actor.totalmovies) ---> (currently not used) Total of Known Movies (acting / directing / writing)
