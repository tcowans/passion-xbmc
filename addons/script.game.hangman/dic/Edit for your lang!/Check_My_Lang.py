from xbmc import getLanguage , executebuiltin

My_Lang = getLanguage().lower()

print "My language is : *",My_Lang,"*"
print "Rename folder *Edit for your lang!* ->in-> *",My_Lang,"*"
print "Rename file *Edit me!.xml* ->in-> *strings.xml*"
print "And finally edit files *Hard.wrd, Normal.wrd and strings.xml*"
print "Enjoy!\nFrost"

executebuiltin('XBMC.ActivateWindow(ScriptsDebugInfo)')
