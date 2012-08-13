from parsers import ProgrammesParser

print "ARTE Programmes"

categories = {}
videos = []
link = ""

#Init
programmesParser = ProgrammesParser("fr", categories, videos)

#List categories
programmesParser.get_categories_list()
for key,value in categories.items():
	print key.encode('utf-8')
	link = value

#List videos
nextPage = programmesParser.parse(link, 1, 25)

if nextPage:
    print "Next Page : %s" %(nextPage)
else:
    print "Pas de page suivante"

for video in videos :
    print "%s" %(video.title.encode("utf-8"))
    link = video.link

#Get video rtmp link
programmesParser.lang = "fr"
hd, sd = programmesParser.fetch_stream_links( link )
print "%s" %(hd)
