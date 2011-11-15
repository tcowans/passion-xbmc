
class Score:
    def create_score(self):
        self.old_foodcoords = '0,0'
        self.score = 0

    def update_score(self, foodcoords):
        if (str(self.old_foodcoords) != str(foodcoords)):
            self.score += 1
            self.old_foodcoords = str(foodcoords)

    def get_current_score(self):
        return self.score

    def get_upload_score(self):
        return (str(self.score) + '|correct')
