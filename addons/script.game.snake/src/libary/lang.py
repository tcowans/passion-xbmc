class Language:
	def load(self,thepath):
		import re, os, xbmc
		self.strings = {}
		tempstrings = []
		self.language = xbmc.getLanguage().lower()
		print "-----------------------------"
		if os.path.exists(thepath+self.language+"\\strings.xml"):
			self.foundlang = self.language
		else:
			self.foundlang = "english"
		self.langdoc = thepath+self.foundlang+"\\strings.xml"
		print "Loading Language: " + self.foundlang
		try:
			f=open(self.langdoc,'r')
			tempstrings=f.read()
			f.close()
		except:
			print "Error: Languagefile "+self.langdoc+" cant be opened"

		self.exp='<string id="(.*?)">(.*?)</string>'
		self.res=re.findall(self.exp,tempstrings)
		for stringdat in self.res:
			self.strings[int(stringdat[0])] = str(stringdat[1])

	def string(self,number):
		if int(number) in self.strings:
			return self.strings[int(number)]
		else:
			return "unknown string id"