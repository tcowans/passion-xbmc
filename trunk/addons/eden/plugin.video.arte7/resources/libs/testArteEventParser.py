from parsers import EventParser

print "ARTE EVENT"

categories = {}
videos = []
link = ""

#Init
eventParser = EventParser("fr", categories, videos)

#List categories
eventParser.get_categories_list()
for key,value in categories.items():
	print key.encode('utf-8')
	link = value

#List videos
nextPage = eventParser.parse(link, 1, 25)

if nextPage:
    print "Next Page : %s" %(nextPage)
else:
    print "Pas de page suivante"

for video in videos :
    print "%s" %(video.title.encode("utf-8"))
    link = video.link

#Get video rtmp link
eventParser.lang = "fr"
hd, sd = eventParser.fetch_stream_links( link )
print "%s" %(hd)

