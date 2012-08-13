from parsers import LiveParser

print "ARTE LIVE"

categories = {}
videos = []
link = ""

#Init
liveParser = LiveParser("fr",categories)

#List categories
liveParser.get_categories_list()
for key,value in categories.items():
	print key.encode('utf-8')
	print value
	link = key

#List videos
liveParser.get_videos_list(link, videos)
for video in videos :
    print "%s" %(video.title)
    link = str(video.order)

#Get video rtmp link
links = liveParser.get_links(link)
hd = links['HD']
sd = links['SD'] 
live = links['Live']
if links['Live'] is not None:
	hd = links['Live']
elif links['HD'] is not None :
	hd = links['HD']
else:
	hd = links['SD']
print "%s" %(hd)
