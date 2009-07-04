from elementtree import ElementTree 

ET = ElementTree.ElementTree()
doc = ET.parse('advancedsettings.xml')
root = ElementTree.Element(doc)
screensaver = ElementTree.SubElement(root,'truc')
tree = ElementTree.ElementTree(root)
tree.write('test.xml')



 ##

##xml = 
##ast = xml.getroot()
##ast.append('truc')
##root.append('truc')

#screensaver = ET.SubElement(root,'truc')
#tree = ET.ElementTree(root)
#tree.write('advancedsettings.xml')


#screensaver =  manage('roo')

#screensaver = xml.find('screensaver')
#ast.append('truc')


#mode = screensaver.find('mode')
#print mode.text
#mode.text = 'baba'
#print mode.text
#_setroot(element)
#ET.write('guisettings.xml',)

#screensaver = ET.element('screensaver')
#dimlevel = ET.subelement(screensaver,'dimlevel')
#mode = ET.subelement(screensaver,'mode')
#slideshowpath = 
#slideshowshuffle
#time
#usedimonpause
#uselock
#usemusicvisinstead
#ss =  screensaver.getchildren()
#ss2 = screensaver.keys()
#print ss2
#print ss2.attrib
#print ss.attrib
#print screensaver.items()


#print at.get('mode')

