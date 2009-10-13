# -*- coding: utf-8 -*-


# script constants
__script__       = "Calendar"
__plugin__       = "Calendar"
__author__       = "CinPoU"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center, [LINUX, OS X, WIN32, XBOX]"
__date__         = "26-09-2009"
__version__      = "0.0.1"


import os
import re
import sys
import xbmc, xbmcgui


# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )

#calendar modules
import datetime
import calendar

#For Xml Files
import xml.dom.minidom
import shutil

# Shared resources
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )
# append the proper libs folder to our path
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "libs" ) )
# append the proper GUI folder to our path
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "libs", "GUI" ) )
# append the proper xml folder to our path
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "libs", "xml" ) )
# append the proper gdata folder to our path
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "libs", "gdata" ) )
# append the proper atom folder to our path
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "libs", "atom" ) )


#modules custom
from specialpath import *

#Google modules
from elementtree import ElementTree
import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import atom
import getopt
import string
import time


#get actioncodes from keymap.xml
ACTION_PREVIOUS_MENU = 10


#Variable du mois
monthName = calendar.month_name


class AgendaGUI(xbmcgui.WindowXML):
    def __init__(self,strXMLname, strFallbackPath, strDefaultName ):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        pass
 
    def onInit(self):
        # Put your List Populating code/ and GUI startup stuff here
        self.list = self.getControl(150)
        self.daysname = self.getControl(250)
        self.monthname = self.getControl(602)
        self.contentpanel = self.getControl(490)
        self.contentpaneltitle = self.getControl(491)
        self.calendar_list = self.getControl(350)
        
        #Init display
        self.main_gui_state = 0
        
        
        #Init button id
        self.calendarList = 350
        self.dayNameList = 250
        self.btn_next = 130
        self.btn_prev = 131
        
        self.main_btn_add = 140
        self.main_btn_reresh = 141
        self.main_btn_view = 142
        self.main_btn_managed = 143
        self.main_btn_plugins = 144
        self.main_btn_settings = 145
        
        self.addcalendar_btn_title = 9001
        self.addcalendar_btn_decrease_color = 9021
        self.addcalendar_btn_increase_color = 9022
        self.addcalendar_btn_label_color = 9023
        self.addcalendar_btn_decrease_type = 9031
        self.addcalendar_btn_increase_type = 9032
        self.addcalendar_btn_label_type = 9033
        self.addcalendar_btn_decrease_account = 9042
        self.addcalendar_btn_increase_account = 9043
        self.addcalendar_btn_label_account = 9044
        self.addcalendar_btn_add_account = 9005
        self.addcalendar_btn_decrease_calendar = 9061
        self.addcalendar_btn_increase_calendar = 9062
        self.addcalendar_btn_label_calendar = 9063
        self.addcalendar_btn_add_calendar = 9007
        self.addcalendar_btn_write = 9008
        
        #Init the calendars xml file
        calendar_xml = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "default.xml" )
        if not os.path.isfile( calendar_xml ):
            calendar_xml_src = os.path.join( BASE_RESOURCE_PATH, "modeles" , "default.xml" )
            try :
                shutil.copy2(calendar_xml_src,calendar_xml)
            except : "Unable to write the list calendar xml file"  
        
        #Init the account xml file
        account_xml = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "account.xml" )
        if not os.path.isfile( account_xml ):
            account_xml_src = os.path.join( BASE_RESOURCE_PATH, "modeles" , "account.xml" )
            try :
                shutil.copy2(account_xml_src,account_xml)
            except : "Unable to write the list account xml file" 
            
        #Init the google calendar
        self.calendar_service = gdata.calendar.service.CalendarService()

        #self.printUserCalendars(self.calendar_service)


        #Init color var
        self.calendarColor = ["Violet" , "Rouge" , "Bleu" , "Vert" , "Jaune" , "Rose" , "Marron" , "Noir" , "Orange" , "Blanc"]
        self.calendarColorCurrent = 0 
        #Init account type var
        self.addCalendarAccountType = ["Local" , "Web" , "Google"]
        self.addCalendarAccountTypeCurrent = 0 
        #Init account title var
        self.addCalendarAccountTitle = []
        self.addCalendarAccountTitleCurrent = 0
        self.xml_google_account()
        #Init calendar title var
        self.addCalendarCalendarTitle = []
        self.addCalendarCalendarTitleCurrent = 0       
        
        #Display the Day's Name    
        for x in xrange(0,7):
          self.daysname.addItem( xbmcgui.ListItem( calendar.day_abbr[ x ] ) )
                
        #Today :
        today = datetime.date.today()
        #Break the data
        current = re.split('-', str(today))
        self.current_no = int(current[1])
        self.current_month = monthName[self.current_no]
        self.current_day = int(re.sub('\A0', '', current[2]))
        self.current_yr = int(current[0])
        #Display the today's date :
        today_text = '%s %s %s' %(self.current_day, self.current_month, self.current_yr)

        #Selected month
        self.year = self.current_yr
        self.month_no = self.current_no
        self.prev_year = 0
        self.next_year = 0
        self.prev_month_no = 0
        self.next_month_no = 0
        
        self.set_container_days (self.year, self.month_no)
        
    def show_keyboard (self, textDefault, textHead) :
        # Recuperation d'un texte via la clavier virtuel
        keyboard = xbmc.Keyboard(textDefault, textHead)
        #keyboard.setHeading('') # En tete
        #keyboard.setDefault("Title") # Texte par defaut qui sera deja affiche a la saisie
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            inputText = keyboard.getText()
            #print"Login: %s"%inputText
         
            dialogInfo = xbmcgui.Dialog()
            #dialogInfo.ok("Texte saisi", "Votre texte est:", "%s"%inputText)
        del keyboard
        return inputText
        
    ##Google def
    def googleAccountConnect(self , login , password) :
        self.calendar_service.email = login
        self.calendar_service.password = password
        self.calendar_service.source = 'Google-Calendar_Python_Sample-1.0'
        self.calendar_service.ProgrammaticLogin()
        
    def printUserCalendars(self , calendar_service):
        feed = calendar_service.GetAllCalendarsFeed()
        print feed.title.text
        for i, a_calendar in enumerate(feed.entry):
          print '\t%s. %s' % (i, a_calendar.title.text,)
    ##End of google def
        
    def increase_button (self, value, valueCurrent, labelBtn, label) :
        valueLength = len(value)
        if valueCurrent == valueLength - 1 :
             valueCurrent = 0
        else :
             valueCurrent = valueCurrent + 1
        label_colored = "[COLOR=%s]%s[/COLOR]" % ( "ff555555", value[valueCurrent] )
        self.getControl( labelBtn ).setLabel( label, label2=label_colored )
        return valueCurrent
        
    def decrease_button (self, value, valueCurrent, labelBtn, label) :
        valueLength = len(value)
        if valueCurrent == 0 :
             valueCurrent = valueLength - 1
        else :
             valueCurrent = valueCurrent - 1
        label_colored = "[COLOR=%s]%s[/COLOR]" % ( "ff555555", value[valueCurrent] )
        self.getControl( labelBtn ).setLabel( label, label2=label_colored )
        self.getControl( labelBtn ).setLabel( label, label2=label_colored )
        return valueCurrent
        
    def set_container_days (self, year, month_no) :
        self.year = year
        self.month_no = month_no
        
        self.getControl( 150 ).reset()
    
        #Find prev year
        if self.month_no == 1 :
            self.prev_year = self.year-1
        else :
            self.prev_year = self.year

        #Find prev month
        if self.month_no == 1 :
            self.prev_month_no = 12
        else :
            self.prev_month_no = self.month_no-1

        #Display the number of weeks in the prev month
        prev_month = calendar.monthcalendar(self.prev_year, self.prev_month_no)
        prev_nweeks = len(prev_month)
        

        #Find next year
        if self.month_no == 12 :
            self.next_year = self.year+1
        else :
            self.next_year = self.year

        #Find next month
        if self.month_no == 12 :
            self.next_month_no = 1
        else :
            self.next_month_no = self.month_no+1

        #Display the number of weeks in the next month
        self.next_month = calendar.monthcalendar(self.next_year, self.next_month_no)
        
        #Display the month's information
        month_text = '%s %s' % (monthName[self.month_no], self.year)
        self.monthname.setLabel(month_text)
        month = calendar.monthcalendar(self.year, self.month_no)
        nweeks = len(month)
        if nweeks < 6 :
          month.append(self.next_month[1])
        if nweeks < 5 :
          month.append(self.next_month[2])
        
        #Display the days of the current month
        item_pos = 0 
        for w in range(0,6):
            week = month[w]
            for x in xrange(0,7):
                day = week[x]
                today = ""
                if x == 5 or x == 6:
                    daytype = 'weekend'
                else:
                    daytype = 'day'
                # Previous month days      
                if day == 0 and w==0:
                    daytype = 'previous'
                    dayColor = "ccbbbbbb"
                    prev_week =  prev_month[prev_nweeks-1]
                    day = prev_week[x] 
                # Next month days then the month contain 5 weeks
                elif w == 6 and nweeks == 5:
                    daytype = 'next'
                    dayColor = "ccbbbbbb"
                    day = week[x]
                    path = "special://skin/media/button-Back.png"
                # Next month days then the month contain 4 weeks
                elif w == 5 and nweeks == 5:
                    daytype = 'next'
                    dayColor = "ccbbbbbb"
                    day = week[x]
                    path = "special://skin/media/button-Back.png"
                # Next month days        
                elif day == 0:
                    daytype = 'next'
                    dayColor = "ccbbbbbb"
                    next_week =  self.next_month[0]
                    day = next_week[x]
                    path = "special://skin/media/button-Back.png"
                # Today
                elif day == self.current_day and self.month_no == self.current_no and self.year == self.current_yr :
                    print 'Aujourdhui, type : %s, day : %s' %(daytype, day)
                    daytype = "today"
                    today = "true"
                    dayColor = "ff333333"
                    path = "special://skin/media/button-Back.png"
                # Current days
                else:
                    dayColor = "ffffffff"
                    path = "special://skin/media/button-Back.png"
                # Add the days to the list
                label_colored = "[COLOR=%s]%i[/COLOR]" % ( dayColor, day )
                listitem = xbmcgui.ListItem( label_colored )
                listitem.setProperty( "today", today )
                dayItem = self.list.addItem( listitem )
                if daytype ==  "today" :
                    self.list.selectItem(item_pos)
                
                item_pos = item_pos + 1
        
    def set_main_gui_view (self, id) :
        self.main_gui_state = id - 139
        #Define the events panel titles
        eventPanelTitles = ["" , "Add an Event" , "Refresh" , "Displayed Calendar" , "Managed Calendar" , "Managed Plugins" , "Settings"]
        #Show the event Panel
        #Add the Content Panel Title
        eventPanelTitle = eventPanelTitles[self.main_gui_state]
        self.contentpaneltitle.setLabel(eventPanelTitle)
        
    def list_calendar(self):  
        self.calendar_list.reset()    
        #read the calendars list xml
        calendar_xml = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "default.xml" )
        xml_list_calendar = xml.dom.minidom.parse(calendar_xml)
        xml_calendars = xml_list_calendar.getElementsByTagName('calendar')
        xml_calendars_len = len(xml_calendars)
        for w in range(0,xml_calendars_len):
        
            text_color = "ff000000"
            
            title = xml_calendars[w].getElementsByTagName('title')[0].firstChild.data
            type = xml_calendars[w].getElementsByTagName('type')[0].firstChild.data
            account = xml_calendars[w].getElementsByTagName('account')[0].firstChild.data
            googleid = xml_calendars[w].getElementsByTagName('googleid')[0].firstChild.data
            link = xml_calendars[w].getElementsByTagName('link')[0].firstChild.data
            activate = xml_calendars[w].getElementsByTagName('activate')[0].firstChild.data
            write = xml_calendars[w].getElementsByTagName('write')[0].firstChild.data
            color = xml_calendars[w].getElementsByTagName('color')[0].firstChild.data
            
            #Define Colors
            if activate == "false" :
                color = "ff999999"
                text_color = "ff555555"
            elif color == "" :
                color = "ff000000"
                
            #Define Thumb
            type_thumb =  { 'google':'calendar_thumb_google.png' , 'local':'calendar_thumb_local.png' , 'web':'calendar_thumb_web.png'}
            print type_thumb[type]
            calendar_thumb = type_thumb[type]
            
            # Add the calendars to the list
            label_colored = "[COLOR=%s]%s[/COLOR]" % ( text_color, title )
            listitem = xbmcgui.ListItem( label_colored )
            listitem.setProperty( "type", type )
            listitem.setThumbnailImage(calendar_thumb)
            calendar_list_item = self.calendar_list.addItem( listitem )
            #calendar_list_item.getControl(1).setColorDiffuse("0xff456dfa")
        
    def list_calendar_activate(self , item): 
        #Find the current item position
        calendar_num = self.calendar_list.getSelectedPosition()
        print calendar_num 
        self.calendar_list.reset()    
        
        #read the calendars list xml
        calendar_xml = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "default.xml" )
        xml_list_calendar = xml.dom.minidom.parse(calendar_xml)
        xml_calendars = xml_list_calendar.getElementsByTagName('calendar')
        activate = xml_calendars[calendar_num].getElementsByTagName('activate')[0].firstChild.data
        
        if activate == "true" :
            xml_calendars[calendar_num].getElementsByTagName('activate')[0].firstChild.data = "false"
        else :
            xml_calendars[calendar_num].getElementsByTagName('activate')[0].firstChild.data = "true"
    
    
        # Print our newly created XML
        print xml_list_calendar.toxml(encoding="UTF-8")
    
        outputfile = open(calendar_xml, 'wb')
        outputfile.write(xml_list_calendar.toxml(encoding="UTF-8"))
        outputfile.close()
            
        self.list_calendar()
        
    def xml_google_account(self): 
        self.addCalendarAccountTitle = []
        self.addCalendarAccountTitleCurrent = 0 
        #read the calendars list xml
        account_xml = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "account.xml" )
        xml_list_account = xml.dom.minidom.parse(account_xml)
        xml_accounts = xml_list_account.getElementsByTagName('account')
        xml_accounts_len = len(xml_accounts)
        for w in range(0,xml_accounts_len):
            
            title = xml_accounts[w].getElementsByTagName('title')[0].firstChild.data
            type = xml_accounts[w].getElementsByTagName('type')[0].firstChild.data
            login = xml_accounts[w].getElementsByTagName('login')[0].firstChild.data
            password = xml_accounts[w].getElementsByTagName('password')[0].firstChild.data
            self.addCalendarAccountTitle.append(title)
        
    def xml_google_account_id(self , pos): 
        #read the calendars list xml
        account_xml = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "account.xml" )
        xml_list_account = xml.dom.minidom.parse(account_xml)
        xml_accounts = xml_list_account.getElementsByTagName('account')
        login = xml_accounts[pos].getElementsByTagName('login')[0].firstChild.data
        password = xml_accounts[pos].getElementsByTagName('password')[0].firstChild.data
        google_account_id = [login , password]
        return google_account_id
        
    def xml_add_account(self, title, type, login, pwd): 
        
        #read the calendars list xml
        account_xml = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "account.xml" )
        xml_list_account = xml.dom.minidom.parse(account_xml)
        accounts = xml_list_account.childNodes[0]
        
        # Create a main <account> element
        xml_account = xml_list_account.createElement("account")
        xml_accountBal = accounts.appendChild(xml_account)
        
        
        # Create the account <title> element
        xml_title = xml_list_account.createElement("title")
        xml_titleBal = xml_accountBal.appendChild(xml_title)
        
        # Give the <title> element some text
        xml_titletext = xml_list_account.createTextNode(title)
        xml_titleBal.appendChild(xml_titletext)
        
        
        # Create the account <type> element
        xml_type = xml_list_account.createElement("type")
        xml_typeBal = xml_accountBal.appendChild(xml_type)
        
        # Give the <type> element some text
        xml_typetext = xml_list_account.createTextNode(type)
        xml_typeBal.appendChild(xml_typetext)
        
        
        # Create the account <login> element
        xml_login = xml_list_account.createElement("login")
        xml_loginBal = xml_accountBal.appendChild(xml_login)
        
        # Give the <login> element some text
        xml_logintext = xml_list_account.createTextNode(login)
        xml_loginBal.appendChild(xml_logintext)
        
        
        # Create the account <password> element
        xml_pwd = xml_list_account.createElement("password")
        xml_pwdBal = xml_accountBal.appendChild(xml_pwd)
        
        # Give the <password> element some text
        xml_pwdtext = xml_list_account.createTextNode(pwd)
        xml_pwdBal.appendChild(xml_pwdtext)  
        
    
        # Print our newly created XML
        print xml_list_account.toxml(encoding="UTF-8")
    
        outputfile = open(account_xml, 'wb')
        outputfile.write(xml_list_account.toxml(encoding="UTF-8"))
        outputfile.close()
        
    def list_google_calendar(self, login, pwd): 
        self.addCalendarCalendarTitle = []
        self.addCalendarCalendarTitleCurrent = 0 
        #connection to the account
        self.googleAccountConnect(login , pwd)
        feed = self.calendar_service.GetAllCalendarsFeed()
        for i, a_calendar in enumerate(feed.entry):
            print '\t%s. %s' % (i, a_calendar.title.text,)
            self.addCalendarCalendarTitle.append(a_calendar.title.text)
        
 
    def onAction(self, action):
        #Close the script
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        
    def onClick(self, controlID):
        """
            Notice: onClick not onControl
            Notice: it gives the ID of the control not the control object
        """
            
        #Calendar Buttons Click        
        if controlID == self.dayNameList: pass
        
        if controlID == self.btn_next:
            self.set_container_days( self.next_year,self.next_month_no )
        
        if controlID == self.btn_prev:
            self.set_container_days( self.prev_year,self.prev_month_no )
            
        #Main Buttons Click
        if controlID == self.main_btn_add or controlID == self.main_btn_view or controlID == self.main_btn_reresh or controlID == self.main_btn_managed or controlID == self.main_btn_plugins or controlID == self.main_btn_settings :
            self.set_main_gui_view (controlID)
        if controlID == self.main_btn_view :
            self.list_calendar()
        if controlID == self.calendarList :
            self.list_calendar_activate(self.calendar_list.getSelectedItem())
            
        #Add Calendar Buttons Click
        if controlID == self.addcalendar_btn_title :
            keyboard_text = self.show_keyboard ("TITLE", "")
            self.getControl( self.addcalendar_btn_title ).setLabel( keyboard_text )
            
        if controlID == self.addcalendar_btn_decrease_color :
            self.calendarColorCurrent = self.decrease_button (self.calendarColor, self.calendarColorCurrent, self.addcalendar_btn_label_color, "COLOR :")
            
        if controlID == self.addcalendar_btn_increase_color :
            self.calendarColorCurrent = self.increase_button (self.calendarColor, self.calendarColorCurrent, self.addcalendar_btn_label_color, "COLOR :")
            
        if controlID == self.addcalendar_btn_decrease_type :
            self.addCalendarAccountTypeCurrent = self.decrease_button (self.addCalendarAccountType, self.addCalendarAccountTypeCurrent, self.addcalendar_btn_label_type, "TYPE :")
            if self.addCalendarAccountType[self.addCalendarAccountTypeCurrent] == "Google" :
                self.getControl(self.addcalendar_btn_decrease_account).setVisible(True)
                self.getControl(self.addcalendar_btn_increase_account).setVisible(True)
                self.getControl(self.addcalendar_btn_label_account).setVisible(True)
                self.getControl(self.addcalendar_btn_add_account).setVisible(True)
                self.getControl(self.addcalendar_btn_decrease_calendar).setVisible(True)
                self.getControl(self.addcalendar_btn_increase_calendar).setVisible(True)
                self.getControl(self.addcalendar_btn_label_calendar).setVisible(True)
                self.getControl(self.addcalendar_btn_add_calendar).setVisible(True)
                self.getControl(self.addcalendar_btn_write).setVisible(True)
            elif self.addCalendarAccountType[self.addCalendarAccountTypeCurrent] == "Local" :
                self.getControl(self.addcalendar_btn_decrease_account).setVisible(False)
                self.getControl(self.addcalendar_btn_increase_account).setVisible(False)
                self.getControl(self.addcalendar_btn_label_account).setVisible(False)
                self.getControl(self.addcalendar_btn_add_account).setVisible(False)
                self.getControl(self.addcalendar_btn_decrease_calendar).setVisible(True)
                self.getControl(self.addcalendar_btn_increase_calendar).setVisible(True)
                self.getControl(self.addcalendar_btn_label_calendar).setVisible(True)
                self.getControl(self.addcalendar_btn_add_calendar).setVisible(True)
                self.getControl(self.addcalendar_btn_write).setVisible(True)
            elif self.addCalendarAccountType[self.addCalendarAccountTypeCurrent] == "Web" :
                self.getControl(self.addcalendar_btn_decrease_account).setVisible(False)
                self.getControl(self.addcalendar_btn_increase_account).setVisible(False)
                self.getControl(self.addcalendar_btn_label_account).setVisible(False)
                self.getControl(self.addcalendar_btn_add_account).setVisible(False)
                self.getControl(self.addcalendar_btn_decrease_calendar).setVisible(False)
                self.getControl(self.addcalendar_btn_increase_calendar).setVisible(False)
                self.getControl(self.addcalendar_btn_label_calendar).setVisible(False)
                self.getControl(self.addcalendar_btn_add_calendar).setVisible(False)
                self.getControl(self.addcalendar_btn_write).setVisible(False)
            
        if controlID == self.addcalendar_btn_increase_type :
            self.addCalendarAccountTypeCurrent = self.increase_button (self.addCalendarAccountType, self.addCalendarAccountTypeCurrent, self.addcalendar_btn_label_type, "TYPE :")
            if self.addCalendarAccountType[self.addCalendarAccountTypeCurrent] == "Google" :
                self.getControl(self.addcalendar_btn_decrease_account).setVisible(True)
                self.getControl(self.addcalendar_btn_increase_account).setVisible(True)
                self.getControl(self.addcalendar_btn_label_account).setVisible(True)
                self.getControl(self.addcalendar_btn_add_account).setVisible(True)
                self.getControl(self.addcalendar_btn_decrease_calendar).setVisible(True)
                self.getControl(self.addcalendar_btn_increase_calendar).setVisible(True)
                self.getControl(self.addcalendar_btn_label_calendar).setVisible(True)
                self.getControl(self.addcalendar_btn_add_calendar).setVisible(True)
                self.getControl(self.addcalendar_btn_write).setVisible(True)
            elif self.addCalendarAccountType[self.addCalendarAccountTypeCurrent] == "Local" :
                self.getControl(self.addcalendar_btn_decrease_account).setVisible(False)
                self.getControl(self.addcalendar_btn_increase_account).setVisible(False)
                self.getControl(self.addcalendar_btn_label_account).setVisible(False)
                self.getControl(self.addcalendar_btn_add_account).setVisible(False)
                self.getControl(self.addcalendar_btn_decrease_calendar).setVisible(True)
                self.getControl(self.addcalendar_btn_increase_calendar).setVisible(True)
                self.getControl(self.addcalendar_btn_label_calendar).setVisible(True)
                self.getControl(self.addcalendar_btn_add_calendar).setVisible(True)
                self.getControl(self.addcalendar_btn_write).setVisible(True)
            elif self.addCalendarAccountType[self.addCalendarAccountTypeCurrent] == "Web" :
                self.getControl(self.addcalendar_btn_decrease_account).setVisible(False)
                self.getControl(self.addcalendar_btn_increase_account).setVisible(False)
                self.getControl(self.addcalendar_btn_label_account).setVisible(False)
                self.getControl(self.addcalendar_btn_add_account).setVisible(False)
                self.getControl(self.addcalendar_btn_decrease_calendar).setVisible(False)
                self.getControl(self.addcalendar_btn_increase_calendar).setVisible(False)
                self.getControl(self.addcalendar_btn_label_calendar).setVisible(False)
                self.getControl(self.addcalendar_btn_add_calendar).setVisible(False)
                self.getControl(self.addcalendar_btn_write).setVisible(False)
            
        if controlID == self.addcalendar_btn_decrease_account :
            self.addCalendarAccountTitleCurrent = self.decrease_button (self.addCalendarAccountTitle, self.addCalendarAccountTitleCurrent, self.addcalendar_btn_label_account, "ACCOUNT :")
            if self.addCalendarAccountType[self.addCalendarAccountTypeCurrent] == "Google" :
                google_calendar_id = self.xml_google_account_id(self.addCalendarAccountTitleCurrent)
                self.list_google_calendar(google_calendar_id[0], google_calendar_id[1])
            
        if controlID == self.addcalendar_btn_increase_account :
            self.addCalendarAccountTitleCurrent = self.increase_button (self.addCalendarAccountTitle, self.addCalendarAccountTitleCurrent, self.addcalendar_btn_label_account, "ACCOUNT :")
            if self.addCalendarAccountType[self.addCalendarAccountTypeCurrent] == "Google" :
                google_calendar_id = self.xml_google_account_id(self.addCalendarAccountTitleCurrent)
                self.list_google_calendar(google_calendar_id[0], google_calendar_id[1])
            
        if controlID == self.addcalendar_btn_decrease_calendar :
            self.addCalendarCalendarTitleCurrent = self.decrease_button (self.addCalendarCalendarTitle, self.addCalendarCalendarTitleCurrent, self.addcalendar_btn_label_calendar, "CALENDAR :")
            
        if controlID == self.addcalendar_btn_increase_calendar :
            self.addCalendarCalendarTitleCurrent = self.increase_button (self.addCalendarCalendarTitle, self.addCalendarCalendarTitleCurrent, self.addcalendar_btn_label_calendar, "CALENDAR :")
        
        if controlID == self.addcalendar_btn_add_account :
            title = self.show_keyboard ("TITLE", "")
            login = self.show_keyboard ("LOGIN", "")
            pwd = self.show_keyboard ("PASSWORD", "")
            self.xml_add_account(title, "google", login, pwd)
            self.xml_google_account()
            self.decrease_button (self.addCalendarAccountTitle, 0, self.addcalendar_btn_label_account, "ACCOUNT")
        
        if controlID == self.addcalendar_btn_add_calendar :
            keyboard_text = self.show_keyboard ("CALENDAR", "")
            listLength = len(self.addCalendarCalendarTitle)
            self.addCalendarCalendarTitle.append(keyboard_text)
            self.increase_button (self.addCalendarCalendarTitle, listLength - 1, self.addcalendar_btn_label_calendar, "CALENDAR")
 
  
    def onFocus(self, controlID):
        pass

if  __name__ == "__main__":

  base_path = os.getcwd()#Frost
  
  w = AgendaGUI("agenda.xml", base_path, "DefaultSkin")
  w.doModal()
  del w