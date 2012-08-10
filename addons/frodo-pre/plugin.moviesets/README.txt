
MOVIESETS INFOLABELS FOR SKINNERS

Legend: (*) if not exists return empty

AVAILABLE LABELS:
 - Container.Property(Content) ---> MovieSets
 - Container.Property(TotalSets) -> Total Sets in container
 
 - ListItem.Label ---->   [ Title of Set ]
 - ListItem.Label2 --->   [ idSet ]

 - ListItem.Icon -----> * [ return cached icon of set, if user has created with xbmc ]
 - ListItem.Path ----->   [ return all path in stack format ] ( eg: stackset://$INFO[movie.[1-10].FilenameAndPath] ; $INFO[movie.[1-10].FilenameAndPath] ; ... )
 - ListItem.Title ---->   [ Title of Set ]
 - ListItem.Genre ---->   [ return all genres of movies in set ]
 - ListItem.Plot ----->   [ return all plot of movies in set ]
 - ListItem.Duration ->   [ return total time in minutes of all movie in set ]
 - ListItem.Rating --->   [ return sum of rating divided by total movies in set ]( eg: 5.6 + 7.5 / 2 movies )
 - ListItem.Votes ---->   [ return sum of votes for all movie in set ]
 - ListItem.mpaa ----->   [ return mpaa for all movie in set ]
 - ListItem.trailer --> * [ return stack://trailer1 , trailer2 , ... ]

 - ListItem.Property(WatchedMovies) --->   [ Shows the number of watched movies for the currently selected movieset ]
 - ListItem.Property(UnWatchedMovies) ->   [ Shows the number of unwatched movies for the currently selected movieset ]
 - ListItem.Property(TotalMovies) ----->   [ Shows the number of total movies for the currently selected movieset ]
 - ListItem.Property(ExtraFanart) -----> * [ return first folder "../extrafanart" of movies for the currently selected movieset ]( eg: moviepath/../extrafanart )
 - ListItem.Property(Fanart_Image) ----> * [ return first fanart of movieset sorted by sortTitle tag ]
 - ListItem.Property(Countries) ------->   [ return country for all movie in set ]
 - ListItem.Property(StarRating) ------>   [ return image "rating[0-5].png" same value ListItem.Rating ]
 - ListItem.Property(Years) ----------->   [ return year for all movie in set ]
 - ListItem.Property(VideoResolution) ->   [ return moyen of all movie in set ] ( not really exact value, for friendly only )
 - ListItem.Property(VideoAspect) ----->   [ return moyen of all movie in set ] ( not really exact value, for friendly only )

   this Property is used for conditional visibility
 - ListItem.Property(IsSet) ----------->   [ return true or empty, if item currently selected is movieset ]

Available properties of each movie in the currently selected movieset
base property "movie.ID." Possible ID ( 1 - 10 or more )

 - ListItem.Property(movie.[1-10].Title) ------->   [ return title of ID ]
 - ListItem.Property(movie.[1-10].sortTitle) --->   [ return sort title of ID ] http://wiki.xbmc.org/index.php?title=Movie_Sets#Editing_the_.NFO_file
 - ListItem.Property(movie.[1-10].Filename) ---->   [ return filename of ID ]
 - ListItem.Property(movie.[1-10].Path) -------->   [ return path of ID ]
 - ListItem.Property(movie.[1-10].Plot) -------->   [ return plot of ID ]
 - ListItem.Property(movie.[1-10].Year) -------->   [ return year of ID ]
 - ListItem.Property(movie.[1-10].Trailer) -----> * [ return trailer of ID ]
 - ListItem.Property(movie.[1-10].Icon) --------> * [ return cached icon of ID ]
 - ListItem.Property(movie.[1-10].Fanart) ------> * [ return cached fanart of ID ]
 - ListItem.Property(movie.[1-10].ExtraFanart) -> * [ return folder "extrafanart" of ID ]( eg: moviepath/extrafanart )


For more description of labels: http://wiki.xbmc.org/?title=InfoLabels
