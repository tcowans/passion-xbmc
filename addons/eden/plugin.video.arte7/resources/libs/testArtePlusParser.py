from parsers import PlusParser

print "ARTE PLUS"

videos = []
link = ""

#Init
plusParser = PlusParser("fr",videos)

#List videos
plusParser.parse(1,200)
for video in videos :
	print "%s" %(video.title)
	link = video.link

#Get video rtmp link
plusParser.lang="fr"
hd, sd = plusParser.fetch_stream_links( link )
print "%s" %(hd)

#Get video infos
infos = plusParser.fetch_summary(link)
print "%s" %(infos[0])
print "%s" %(infos[1])
print "%s" %(infos[2])
