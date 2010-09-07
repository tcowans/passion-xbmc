
import urllib

url_base = ""

class highscore:
    def get_game_id(self, game):
        if not url_base: return ""
        game = game.replace(' ', '%20')
        testurl = urllib.urlopen(((url_base + 'get_game_id.php?game=') + game))
        temp = testurl.read()
        testurl.close()
        return str(temp)

    def get_level_id(self, gameid, levelname):
        if not url_base: return ""
        levelname = levelname.replace(' ', '%20')
        testurl = urllib.urlopen(((((url_base + 'get_level_id.php?gameid=') + gameid) + '&levelname=') + levelname))
        temp = testurl.read()
        testurl.close()
        return str(temp)

    def get_user_id(self, username, password):
        if not url_base: return ""
        username = username.replace(' ', '%20')
        testurl = urllib.urlopen(((((url_base + 'get_user_id.php?username=') + username) + '&pass=') + password))
        temp = testurl.read()
        testurl.close()
        return str(temp)

    def get_level_list(self, gameid):
        if not url_base: return ""
        testurl = urllib.urlopen(((url_base + 'get_levellist.php?gameid=') + gameid))
        temp = testurl.read()
        testurl.close()
        temp += ' '
        temp = temp.strip()
        return str(temp)

    def create_new_game(self, gamename):
        if not url_base: return ""
        gamename = gamename.replace(' ', '%20')
        testurl = urllib.urlopen(((url_base + 'create_new_game.php?gamename=') + gamename))
        temp = testurl.read()
        testurl.close()
        return str(temp)

    def create_new_level(self, levelname, gameid):
        if not url_base: return ""
        levelname = levelname.replace(' ', '%20')
        testurl = urllib.urlopen(((((url_base + 'create_new_level.php?levelname=') + levelname) + '&gameid=') + gameid))
        temp = testurl.read()
        testurl.close()
        return str(temp)

    def create_new_user(self, username, password):
        if not url_base: return ""
        username = username.replace(' ', '%20')
        testurl = urllib.urlopen(((((url_base + 'create_new_user.php?username=') + username) + '&pass=') + password))
        temp = testurl.read()
        testurl.close()
        return str(temp)

    def get_highscore(self, gameid, levelid = '', quantity = ''):
        if not url_base: return ""
        theurl = ((url_base + 'get_highscore.php?gameid=') + gameid)
        if (levelid != ''):
            theurl += ('&levelid=' + levelid)
        if (quantity != ''):
            theurl += ('&quantity=' + quantity)
        testurl = urllib.urlopen(theurl)
        temp = testurl.read()
        testurl.close()
        return str(temp)

    def insert_new_highscore(self, gameid, userid, score, levelid = ''):
        if not url_base: return ""
        theurl = ((((((url_base + 'insert_new_highscore.php?gameid=') + gameid) + '&userid=') + userid) + '&score=') + score)
        if (levelid != ''):
            theurl += ('&levelid=' + levelid)
        testurl = urllib.urlopen(theurl)
        temp = testurl.read()
        testurl.close()
        return str(temp)

    def get_picture_url(self, userid):
        if not url_base: return ""
        userid = userid.replace(' ', '%20')
        testurl = urllib.urlopen(((url_base + 'get_picture_url.php?userid=') + userid))
        temp = testurl.read()
        testurl.close()
        return str(temp)
