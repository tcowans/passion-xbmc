
import os

class Secure:
    def check_level(self, path):
        self.all_walls = 0
        self.the_speed = 0
        if os.path.exists(path):
            self.aefile = path
        else:
            return -1
        f = open(self.aefile, 'r')
        self.xmldata = f.read()
        f.close()
        self.walldata = self.xmldata.split('<walls>')[1].split('</walls>')[0].split('\n')
        for wall in self.walldata:
            if (wall.strip() != ''):
                wallx = (int(wall.split('<x>')[1].split('</x>')[0]) - 1)
                wally = (int(wall.split('<y>')[1].split('</y>')[0]) - 1)
                self.all_walls += wallx
                self.all_walls += wallx

        self.speeddata = self.xmldata.split('<speed>')[1].split('</speed>')[0].split('\n')
        self.the_speed = int(self.speeddata[0])
        try:
            self.keydata = self.xmldata.split('<key>')[1].split('</key>')[0].split('\n')
            self.the_key = int(self.keydata[0])
        except:
            return -2
        self.value = ((self.all_walls * self.the_speed) / 17)
        if (self.value == self.the_key):
            return 1
        else:
            return 0

    def get_key(self, path):
        self.all_walls = 0
        self.the_speed = 0
        if os.path.exists(path):
            self.aefile = path
        else:
            return -1
        f = open(self.aefile, 'r')
        self.xmldata = f.read()
        f.close()
        self.walldata = self.xmldata.split('<walls>')[1].split('</walls>')[0].split('\n')
        for wall in self.walldata:
            if (wall.strip() != ''):
                wallx = (int(wall.split('<x>')[1].split('</x>')[0]) - 1)
                wally = (int(wall.split('<y>')[1].split('</y>')[0]) - 1)
                self.all_walls += wallx
                self.all_walls += wallx

        self.speeddata = self.xmldata.split('<speed>')[1].split('</speed>')[0].split('\n')
        self.the_speed = int(self.speeddata[0])
        self.value = ((self.all_walls * self.the_speed) / 17)
        return self.value
