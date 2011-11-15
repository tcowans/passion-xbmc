class Level:
    def load(self,path):
        import os, xml.dom.minidom

        self.level = {}
        self.walls = {}
        print path
        self.levelfile = path
        self.word = path.split("\\")[-1]
        print "loading level... " + self.word
        if os.path.exists(self.levelfile):
            try:
                doc = xml.dom.minidom.parse(self.levelfile)
                error = "no"
            except:
                print "cant read Levelfile"
                print "Levelfile is probably damaged!"
                error = "yes"

        if error != "yes":
            parent = doc.getElementsByTagName("level")[0]
            for child in parent.childNodes:
                if str(child.nodeName) != "#text":
                    self.level[str(child.nodeName)] = str(child.childNodes[0].nodeValue).replace("%SKIN_DIR%",path)
                    #print str(child.nodeName) + " loaded"
                    
            print "loading level successfull"
        print "-----------------------------"

    def get(self,toget):
        try:
            return self.level[toget]
        except:
            return "error"


