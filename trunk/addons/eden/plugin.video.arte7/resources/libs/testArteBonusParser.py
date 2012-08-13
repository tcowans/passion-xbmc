from parsers import BonusParser

print "ARTE Bonus"

categories = {}
videos = []
link = ""

#Init
bonusParser = BonusParser("fr", categories, videos)

#List categories
bonusParser.get_categories_list()
for key,value in categories.items():
	#print value.encode('utf-8')
	link = value

#List videos
nextPage = bonusParser.parse(link, 1, 25)

#if nextPage:
#    print "Next Page : %s" %(nextPage)
#else:
#    print "Pas de page suivante"

for video in videos :
    print "%s" %(video.title.encode("utf-8"))
    link = video.link

#Get video rtmp link
#bonusParser.lang = "fr"
#hd, sd = bonusParser.fetch_stream_links( link )
#print "%s" %(hd)

