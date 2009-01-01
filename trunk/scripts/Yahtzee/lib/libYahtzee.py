# -*- coding: utf-8 -*-

#####################################################################################################
''' Module: import '''
#####################################################################################################
import os
import random

#####################################################################################################
''' Class: Yahtzee Score '''
#####################################################################################################
class DICE:
    def __init__(self):
        self.d1 = "1"
        self.d2 = "2"
        self.d3 = "3"
        self.d4 = "4"
        self.d5 = "5"
        self.ex = "6"

    def choiceDice(self, numdice=6):
        try:
            shuffle = random.shuffle
        except AttributeError:
            def shuffle(x):
                for i in xrange(len(x)-1, 0, -1):
                    j = int(random.random() * (i+1))
                    x[i], x[j] = x[j], x[i]
        dice = numdice * range(1, 7)
        shuffle(dice)
        return dice

    def changeColorDice(self, colorlist):
        try:
            shuffle = random.shuffle
        except AttributeError:
            def shuffle(x):
                for i in xrange(len(x)-1, 0, -1):
                    j = int(random.random() * (i+1))
                    x[i], x[j] = x[j], x[i]
        shuffle(colorlist)
        return colorlist

class SCORE:
    def __init__(self):
        self.default = {
            "uppersection": {"Aces": "", "Twos": "", "Threes": "", "Fours": "", "Fives": "",
                             "Sixes": "", "SubTotal": "0", "Bonus": "0", "Total Upper": "0"},
            "lowersection": {"3 of kind": "", "4 of kind": "", "Full House": "", "Sm. Straight": "",
                             "Lg. Straight": "", "Yahtzee": "", "Chance": "", "Yahtzee Bonus": "[ ] [ ] [ ]",
                             "Total Lower": "0", "Grand Total": "0"}
            }
        self.current = {"uppersection": {}, "lowersection": {}}
        self.maxRolling = 16

        #self.reset()

    def reset(self):
        self.maxRolling = 16
        for up in self.default["uppersection"].keys():
            self.current["uppersection"][up] = self.default["uppersection"][up]
        for low in self.default["lowersection"].keys():
            self.current["lowersection"][low] = self.default["lowersection"][low]

    def isSameDict(self):
        return (self.current == self.default)

    def decreaseMaxRolling(self):
        self.maxRolling -= 1
        if self.maxRolling <= 0: pass

    # CALCULATE SCRORE FOR UPPER SECTION
    def singleXDice(self, dice, alldice):
        return str(alldice.count(dice) * int(dice))

    def subTotal(self):
        temp = [self.current["uppersection"]["Aces"], self.current["uppersection"]["Twos"],
                self.current["uppersection"]["Threes"], self.current["uppersection"]["Fours"],
                self.current["uppersection"]["Fives"], self.current["uppersection"]["Sixes"]]
        while "" in temp: temp.remove("")
        self.current["uppersection"]["SubTotal"] = str(sum(int(d) for d in temp))
        return self.current["uppersection"]["SubTotal"]

    def bonusDice(self):
        if int(self.subTotal()) >= 63: self.current["uppersection"]["Bonus"] = str(35)
        return self.current["uppersection"]["Bonus"]

    def totalUpper(self):
        temp = [self.bonusDice(), self.subTotal()]
        while "" in temp: temp.remove("")
        self.current["uppersection"]["Total Upper"] = str(sum(int(d) for d in temp))
        return self.current["uppersection"]["Total Upper"]

    # CALCULATE SCRORE FOR LOWER SECTION
    def ofKind(self, dice, alldice):
        if alldice.count("6") >= dice: return self.chance(alldice)
        if alldice.count("5") >= dice: return self.chance(alldice)
        if alldice.count("4") >= dice: return self.chance(alldice)
        if alldice.count("3") >= dice: return self.chance(alldice)
        if alldice.count("2") >= dice: return self.chance(alldice)
        if alldice.count("1") >= dice: return self.chance(alldice)
        return str(0)

    def fullHouse(self, alldice):
        temp = alldice
        temp.sort()
        hasTriple = False
        if temp.count("6") >= 3:
            while str(6) in temp: temp.remove(str(6))
            hasTriple = True
        elif temp.count("5") >= 3:
            while str(5) in temp: temp.remove(str(5))
            hasTriple = True
        elif temp.count("4") >= 3:
            while str(4) in temp: temp.remove(str(4))
            hasTriple = True 
        elif temp.count("3") >= 3:
            while str(3) in temp: temp.remove(str(3))
            hasTriple = True
        elif temp.count("2") >= 3:
            while str(2) in temp: temp.remove(str(2))
            hasTriple = True
        elif temp.count("1") >= 3:
            while str(1) in temp: temp.remove(str(1))
            hasTriple = True
        hasDouble = False
        if   temp.count("6") >= 2: hasDouble = True
        elif temp.count("5") >= 2: hasDouble = True
        elif temp.count("4") >= 2: hasDouble = True
        elif temp.count("3") >= 2: hasDouble = True
        elif temp.count("2") >= 2: hasDouble = True
        elif temp.count("1") >= 2: hasDouble = True

        if (hasDouble)&(hasTriple): return str(25)
        return str(0)

    def smStraight(self, alldice):
        temp = alldice
        if ("1" in temp)&("2" in temp)&("3" in temp)&("4" in temp): return str(30)
        if ("3" in temp)&("4" in temp)&("5" in temp)&("6" in temp): return str(30)
        return str(0)

    def lgStraight(self, alldice):
        temp = alldice
        if ("1" in temp)&("2" in temp)&("3" in temp)&("4" in temp)&("5" in temp): return str(40)
        if ("2" in temp)&("3" in temp)&("4" in temp)&("5" in temp)&("6" in temp): return str(40)
        return str(0)

    def yahtzee(self, alldice):
        pts = str(0)
        if alldice.count("6") >= 5: pts = str(50)
        if alldice.count("5") >= 5: pts = str(50)
        if alldice.count("4") >= 5: pts = str(50)
        if alldice.count("3") >= 5: pts = str(50)
        if alldice.count("2") >= 5: pts = str(50)
        if alldice.count("1") >= 5: pts = str(50)
        if pts == str(50):
            return self.yahtzeeBonus()
        if self.current["lowersection"]["Yahtzee"] != self.default["lowersection"]["Yahtzee"]:
            pts = self.current["lowersection"]["Yahtzee"]
        return pts

    def chance(self, alldice):
        return str(sum(int(d) for d in alldice))

    def yahtzeeBonus(self):
        pts = str(50)
        if self.current["lowersection"]["Yahtzee"] != self.default["lowersection"]["Yahtzee"]:
            pts = self.current["lowersection"]["Yahtzee"]
        if self.current["lowersection"]["Yahtzee"] == str(50):
            pts = str(150)
        elif self.current["lowersection"]["Yahtzee"] == str(150):
            pts = str(250)
        elif (self.current["lowersection"]["Yahtzee"] == str(250))|(self.current["lowersection"]["Yahtzee"] == str(350)):
            pts = str(350)
        return pts

    def markYahtzeeBonus(self):
        if self.current["lowersection"]["Yahtzee"] == str(150):
            self.current["lowersection"]["Yahtzee Bonus"] = str("[X] [ ] [ ]")
        elif self.current["lowersection"]["Yahtzee"] == str(250):
            self.current["lowersection"]["Yahtzee Bonus"] = str("[X] [X] [ ]")
        elif (self.current["lowersection"]["Yahtzee"] == str(350))|(self.current["lowersection"]["Yahtzee"] == str(350)):
            self.current["lowersection"]["Yahtzee Bonus"] = str("[X] [X] [X]")


    def lossYahtzeeBonus(self):
        if self.current["lowersection"]["Yahtzee Bonus"] == str("[ ] [ ] [ ]"):
            self.current["lowersection"]["Yahtzee Bonus"] = str("[0] [0] [0]")
            self.maxRolling -= 2
        elif self.current["lowersection"]["Yahtzee Bonus"] == str("[X] [ ] [ ]"):
            self.current["lowersection"]["Yahtzee Bonus"] = str("[X] [0] [0]")
            self.maxRolling -= 1
        elif self.current["lowersection"]["Yahtzee Bonus"] == str("[X] [X] [ ]"):
            self.current["lowersection"]["Yahtzee Bonus"] = str("[X] [X] [0]")


    def totalLower(self):
        temp = [self.current["lowersection"]["3 of kind"], self.current["lowersection"]["4 of kind"],
                self.current["lowersection"]["Full House"], self.current["lowersection"]["Sm. Straight"],
                self.current["lowersection"]["Lg. Straight"], self.current["lowersection"]["Yahtzee"],
                self.current["lowersection"]["Chance"]]
        while "" in temp: temp.remove("")
        self.current["lowersection"]["Total Lower"] = str(sum(int(d) for d in temp))
        return self.current["lowersection"]["Total Lower"]

    def grandTotal(self):
        temp = [self.current["uppersection"]["Total Upper"], self.current["lowersection"]["Total Lower"]]
        while "" in temp: temp.remove("")
        self.current["lowersection"]["Grand Total"] = str(sum(int(d) for d in temp))
        return self.current["lowersection"]["Grand Total"]

    def endScore(self):
        if self.isSameDict(): return False
        defList = [self.default["uppersection"]["Aces"], self.default["uppersection"]["Twos"],
                   self.default["uppersection"]["Threes"], self.default["uppersection"]["Fours"],
                   self.default["uppersection"]["Fives"], self.default["uppersection"]["Sixes"],
                   self.default["lowersection"]["3 of kind"], self.default["lowersection"]["4 of kind"],
                   self.default["lowersection"]["Full House"], self.default["lowersection"]["Sm. Straight"],
                   self.default["lowersection"]["Lg. Straight"], self.default["lowersection"]["Yahtzee"],
                   self.default["lowersection"]["Chance"], self.default["lowersection"]["Yahtzee Bonus"]]
        curList = [self.current["uppersection"]["Aces"], self.current["uppersection"]["Twos"],
                   self.current["uppersection"]["Threes"], self.current["uppersection"]["Fours"],
                   self.current["uppersection"]["Fives"], self.current["uppersection"]["Sixes"],
                   self.current["lowersection"]["3 of kind"], self.current["lowersection"]["4 of kind"],
                   self.current["lowersection"]["Full House"], self.current["lowersection"]["Sm. Straight"],
                   self.current["lowersection"]["Lg. Straight"], self.current["lowersection"]["Yahtzee"],
                   self.current["lowersection"]["Chance"], self.current["lowersection"]["Yahtzee Bonus"]]
        list = zip(defList, curList)
        allItem = len(list)
        for defItem, curItem in list:
            if defItem == "[ ] [ ] [ ]":
                if "[X]" in curItem: allItem -= 1
            else:
                if defItem != curItem: allItem -= 1
        if allItem <= 0: return True
        return False
