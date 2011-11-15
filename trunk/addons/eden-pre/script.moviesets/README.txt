
MOVIESETS INFOLABELS FOR SKINNERS

Legend: (*) if not exists return empty

AVAILABLE LABELS:
 Exemple: Container(ID) = 7000

 - Container(7000).ListItem(offset) ---->   [ first item is empty/dummy item ]

   - Container(7000).ListItem.Label ---->   [ Title of Set ]
   - Container(7000).ListItem.Label2 --->   [ idSet ]

   - Container(7000).ListItem.Icon -----> * [ return cached icon of set, if user has created with xbmc ]
   - Container(7000).ListItem.Path ----->   [ return all path in stack format ] ( eg: stackset://$INFO[movie.[1-10].FilenameAndPath] ; $INFO[movie.[1-10].FilenameAndPath] ; ... )
   - Container(7000).ListItem.Title ---->   [ Title of Set ]
   - Container(7000).ListItem.Genre ---->   [ return all genres of movies in set ]
   - Container(7000).ListItem.Plot ----->   [ return all plot of movies in set ]
   - Container(7000).ListItem.Duration ->   [ return total time in minutes of all movie in set ]
   - Container(7000).ListItem.Rating --->   [ return sum of rating divided by total movies in set ]( eg: 5.6 + 7.5 / 2 movies )
   - Container(7000).ListItem.Votes ---->   [ return sum of votes for all movie in set ]
   - Container(7000).ListItem.mpaa ----->   [ return mpaa for all movie in set ]
   - Container(7000).ListItem.trailer --> * [ return stack://trailer1 , trailer2 , ... ]

   - Container(7000).ListItem.Property(WatchedMovies) --->   [ Shows the number of watched movies for the currently selected movieset ]
   - Container(7000).ListItem.Property(UnWatchedMovies) ->   [ Shows the number of unwatched movies for the currently selected movieset ]
   - Container(7000).ListItem.Property(TotalMovies) ----->   [ Shows the number of total movies for the currently selected movieset ]
   - Container(7000).ListItem.Property(ExtraFanart) -----> * [ return first folder "../extrafanart" of movies for the currently selected movieset ]( eg: moviepath/../extrafanart )
   - Container(7000).ListItem.Property(Fanart_Image) ----> * [ return first fanart of movieset sorted by sortTitle tag ]
   - Container(7000).ListItem.Property(Countries) ------->   [ return country for all movie in set ]
   - Container(7000).ListItem.Property(StarRating) ------>   [ return image "rating[0-5].png" same value ListItem.Rating ]
   - Container(7000).ListItem.Property(Years) ----------->   [ return year for all movie in set ]
   - Container(7000).ListItem.Property(VideoResolution) ->   [ return moyen of all movie in set ] ( not really exact value, for friendly only )
   - Container(7000).ListItem.Property(VideoAspect) ----->   [ return moyen of all movie in set ] ( not really exact value, for friendly only )

   this Property is used for conditional visibility
   - Container(7000).ListItem.Property(HasMovieSets) ---->   [ return true or empty, if item currently selected is movieset ]

Available properties of each movie in the currently selected movieset
base property "movie.ID." Possible ID ( 1 - 10 or more )

   - Container(7000).ListItem.Property(movie.[1-10].Title) ------->   [ return title of ID ]
   - Container(7000).ListItem.Property(movie.[1-10].sortTitle) --->   [ return sort title of ID ] http://wiki.xbmc.org/index.php?title=Movie_Sets#Editing_the_.NFO_file
   - Container(7000).ListItem.Property(movie.[1-10].Filename) ---->   [ return filename of ID ]
   - Container(7000).ListItem.Property(movie.[1-10].Path) -------->   [ return path of ID ]
   - Container(7000).ListItem.Property(movie.[1-10].Plot) -------->   [ return plot of ID ]
   - Container(7000).ListItem.Property(movie.[1-10].Year) -------->   [ return year of ID ]
   - Container(7000).ListItem.Property(movie.[1-10].Trailer) -----> * [ return trailer of ID ]
   - Container(7000).ListItem.Property(movie.[1-10].Icon) --------> * [ return cached icon of ID ]
   - Container(7000).ListItem.Property(movie.[1-10].Fanart) ------> * [ return cached fanart of ID ]
   - Container(7000).ListItem.Property(movie.[1-10].ExtraFanart) -> * [ return folder "extrafanart" of ID ]( eg: moviepath/extrafanart )


WINDOW PROPERTIES USED FOR CONDITIONAL VISIBILITY:

 - Window([id]).Property(MovieSets.IsAlive) -> [ return true or empty, if addon is running ]
 - Window([id]).Property(Content.MovieSets) -> [ return true or empty, if Container.FolderPath is videodb://1/7/ ]

 
For more description of labels: http://wiki.xbmc.org/?title=InfoLabels
