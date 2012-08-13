from parsers import SearchParser

print "SEARCH ARTE PLUS"

videos = []
link = ""

#Init
searchParser = SearchParser("fr",videos)

#List videos
searchParser.parse(1, 200, "Le+grand+soir")
for video in videos :
	print "%s" %(video.title)
	link = video.link

#Get video rtmp link
searchParser.lang="fr"
hd, sd = searchParser.fetch_stream_links( link )
print "%s" %(hd)

