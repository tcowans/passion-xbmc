
MOVIESETS INFOLABELS

Full description of labels: http://wiki.xbmc.org/?title=InfoLabels

Legend: (*) if not exists return empty

Labels Available:

 - Container(id).ListItem(offset) ----> [ first item is empty/dummy item ]

   - .Label ---->   [ Title of Set ] -> [ first item : "Movie Sets" ]
   - .Label2 --->   [ idSet ] --------> [ first item : "Total of MovieSets in your db" ]

   - .Icon -----> * [ return cached icon of set, if user has created with xbmc ]
   - .Path ----->   [ ActivateWindow(10025,videodb://1/7/[idSet]/) ]
   - .Title ---->   [ Same as .Label ]
   - .Genre ---->   [ return all genres of movies in set ]
   - .Plot ----->   [ return all plot of movies in set ]
   - .Duration ->   [ return total time in minutes of all movie in set ]
   - .Rating --->   [ return sum of rating divided by total movies in set ]( eg: 5.6 + 7.5 / 2 movies )
   - .Votes ---->   [ return sum of votes for all movie in set ]

   - .Property(HasMovieSets) ---->   [ return true or empty, if item currently selected is movieset ]
   - .Property(WatchedMovies) --->   [ Shows the number of watched movies for the currently selected movieset ]
   - .Property(UnWatchedMovies) ->   [ Shows the number of unwatched movies for the currently selected movieset ]
   - .Property(TotalMovies) ----->   [ Shows the number of total movies for the currently selected movieset ]
   - .Property(ExtraFanart) -----> * [ return first folder "../extrafanart" of movies for the currently selected movieset ]( eg: moviepath/../extrafanart )
   - .Property(Fanart_Image) ----> * [ return first fanart of movieset sorted by sortTitle tag ]

Properties of each movie for the currently selected movieset
base property "movie.ID." Possible ID ( 1 - 10 or more )

   - .Property(movie.ID.Title) ------->   [ return title of ID ]
   - .Property(movie.ID.sortTitle) --->   [ return sort title of ID ] http://wiki.xbmc.org/index.php?title=Movie_Sets#Editing_the_.NFO_file
   - .Property(movie.ID.Filename) ---->   [ return filename of ID ]
   - .Property(movie.ID.Path) -------->   [ return path of ID ]
   - .Property(movie.ID.Plot)--------->   [ return plot of ID ]
   - .Property(movie.ID.Icon) --------> * [ return cached icon of ID ]
   - .Property(movie.ID.Fanart) ------> * [ return cached fanart of ID ]
   - .Property(movie.ID.ExtraFanart) -> * [ return folder "extrafanart" of ID ]( eg: moviepath/extrafanart )


WINDOW PROPERTIES:

 - Window([id]).Property(MovieSets.IsAlive) -> [ return true or empty, if addon is running ]
 - Window([id]).Property(Content.MovieSets) -> [ return true or empty, if Container.FolderPath is videodb://1/7/ ]
