
#####################################################################################################
''' Module: import '''
#####################################################################################################
import os
import re


#####################################################################################################
''' Function: DirWalker '''
#####################################################################################################
class DirWalker:
    def __init__(self, directory):
        self.stack = [directory]
        self.files = []
        self.index = 0

    def __getitem__(self, index):
        while 1:
            try:
                file = self.files[self.index]
                self.index = self.index + 1
            except IndexError:
                self.directory = self.stack.pop()
                self.files = os.listdir(self.directory)
                self.index = 0
            else:
                fullname = os.path.join(self.directory, file)
                if os.path.isdir(fullname) and not os.path.islink(fullname):
                    self.stack.append(fullname)
                return fullname

#####################################################################################################
''' Function: Language '''
#####################################################################################################
class pyLanguage:
    def __init__(self):
        self.CWD = os.getcwd().rstrip( ";" )
        from xbmc import getLanguage
        self.curLanguage = getLanguage().lower()
        del getLanguage
        self.testlanguageList = {}
        self.languageList = {}
        self.isFound = False
        try:
            for file in DirWalker(self.CWD):
                if file.endswith(".py"):
                    f = open(file,"r")
                    calLabel = f.read()
                    f.close()
                    existingLabel = re.compile("label[[](.*?)]", re.IGNORECASE).findall(calLabel)
                    for test in existingLabel:
                        self.testlanguageList[int(test)] = u'no label'
        except:
            for test in range(0, 1001):
                self.testlanguageList[test] = u'no label'

    def parser(self):
        altLanguage = os.path.join(self.CWD, "language", "english", "strings.xml")
        setLanguage = os.path.join(self.CWD, "language", self.curLanguage, "strings.xml")
        try:
            f = open(setLanguage, "r")
            readLanguage = f.readlines()
            f.close()
        except:
            try:
                f = open(altLanguage, "r")
                readLanguage = f.readlines()
                f.close()
            except:
                from xbmcgui import Dialog
                Dialog().ok("Error","The %s language file was not found!" % self.curLanguage,
                    "And not alt english language file!", "Please contact %s for this probleme." % __author__)
                return self.testlanguageList
            else: self.isFound = True
        else: self.isFound = True
        if self.isFound:
            regexp = """<string id=(.*?)>(.*?)</string>"""
            for lines in readLanguage:
                try:
                    word = re.findall(regexp, lines)[0]
                except: pass
                else:
                    try: uLabel = unicode(word[1],"utf-8")
                    except UnicodeError: uLabel = word[1]
                    self.languageList[int(word[0].replace('"',''))] = uLabel
            if self.testlanguageList != {}:
                for k in self.testlanguageList.keys():
                    if not self.languageList.has_key(k):
                        self.languageList[k] = self.testlanguageList[k]
            return self.languageList
