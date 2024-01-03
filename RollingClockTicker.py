#!/usr/bin/env python3

# RollingClockTicker by joe703 / https://www.youtube.com/channel/UChMi8gAr52_jZXIpr9WXYQQ
# Verbesserungen und Erweiterungen von Mario

import time
import socket
import feedparser
import requests
import RollingClock
import sys, signal
import imaplib
from fritzconnection.lib.fritzcall import FritzCall # pip3 install fritzconnection
import json, urllib.request
from re import sub
from datetime import date, datetime
import RPi.GPIO as GPIO

global OFFSET, WeatherNewsAPIKey, TelegramAPIKey, WheatherNewsCity
OFFSET = 0

def time_in_range(start, end, x):
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def signal_handler(signal, stackframe):
    Uhr.Hide()
    ClockHide= True
    ClockStop= True
    Uhr.close()
    print("Stop der Uhr angefordert")
    Uhr.join()
    print("Uhr gestoppt")
    sys.exit()    

def ReadYoutubeSubscriberCounter():
    try:
        url = "https://www.googleapis.com/youtube/v3/channels?part=statistics&id=___YOUTUBE-KANAL-ID___&key=___GOOGLE-API-KEY___"
        res = urllib.request.urlopen(url).read().decode('utf-8')
        data = json.loads(res)
        SubscriberText = data['items'][0]['statistics']['subscriberCount']
    except:
        SubscriberText = "???"
    return "Mario's YouTube-Kanal: " + SubscriberText + " Abonnenten"

def ReadNews():
    try:
        NewsFeed = feedparser.parse("https://www.tagesschau.de/infoservices/alle-meldungen-100~rss2.xml")
        NewsText = NewsFeed.entries[0].title+": "+NewsFeed.entries[0].description
        chars = {'ö':'oe','ä':'ae','ü':'ue','Ö':'Oe','Ä':'Ae','Ü':'Ue','ß':'ss','–':'-',' ':' ','§':'Paragraph'}
        for char in chars:
            NewsText = NewsText.replace(char,chars[char])
    except:
        NewsText = "Keine Tagesschau News ???"
    return sub('[^abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890()?=/.%&:!, -]', ' ', NewsText)

def ITNews():
    try:
        ITFeed = feedparser.parse("https://www.heise.de/rss/heise-Rubrik-IT.rdf")
        ITText = ITFeed.entries[0].title+": "+ITFeed.entries[0].description
        chars = {'ö':'oe','ä':'ae','ü':'ue','Ö':'Oe','Ä':'Ae','Ü':'Ue','ß':'ss','–':'-',' ':' ','§':'Paragraph'}
        for char in chars:
            ITText = ITText.replace(char,chars[char])
    except:
        ITText = "Keine Heise IT News ???"
    return sub('[^abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890()?=/.%&:!, -]', ' ', ITText)

def MobileNews():
    try:
        MobileFeed = feedparser.parse("https://www.heise.de/rss/heise-Rubrik-Mobiles.rdf")
        MobileText = MobileFeed.entries[0].title+": "+MobileFeed.entries[0].description
        chars = {'ö':'oe','ä':'ae','ü':'ue','Ö':'Oe','Ä':'Ae','Ü':'Ue','ß':'ss','–':'-',' ':' ','§':'Paragraph'}
        for char in chars:
            MobileText = MobileText.replace(char,chars[char])
    except:
        MobileText = "Keine Heise Mobile News ???"
    return sub('[^abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890()?=/.%&:!, -]', ' ', MobileText)

def BoersenNews():
    try:
        BoersenFeed = feedparser.parse("https://www.finanztreff.de/rdf_news_category-marktberichte.rss")
        BoersenText = BoersenFeed.entries[0].title
        chars = {'ö':'oe','ä':'ae','ü':'ue','Ö':'Oe','Ä':'Ae','Ü':'Ue','ß':'ss','–':'-',' ':' ','§':'Paragraph'}
        for char in chars:
            BoersenText = BoersenText.replace(char,chars[char])
    except:
        BoersenText = "Keine Boersennews ???"
    return sub('[^abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890()?=/.%&:!, -]', '', BoersenText)

def WetterNews(): # Daten von OpenWeatherMAP holen
    try:
        API_KEY = WeatherNewsAPIKey # API Key von OpenWheaterMAP
        city = WheatherNewsCity # gewünschte Stadt
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
        data = requests.get(url).json()
        temp = int(float(data['main']['temp'])) # aktuelle Temperatur
        humidity = data['main']['humidity'] # aktuelle Luftfeuchtigkeit
        wspeed = int(float(data['wind']['speed'])*3.6) # aktuelle Windgeschwindigkeit in km/h
        airpress = int(float(data['main']['pressure'])) # aktueller Luftdruck
        sunrise = data['sys']['sunrise'] # Sonnenaufgang
        sunset = data['sys']['sunset'] # Sonnenuntergang
        sunrise = datetime.fromtimestamp(sunrise).strftime('%H:%M') # Sonnenaufgang formatiert (locale Time)
        sunset = datetime.fromtimestamp(sunset).strftime('%H:%M') # Sonnenuntergang formatiert (locale Time)
        #sunrise = datetime.utcfromtimestamp(sunrise).strftime('%H:%M')+ " Uhr" # Sonnenaufgang formatiert (UTC Time)
        #sunset = datetime.utcfromtimestamp(sunset).strftime('%H:%M')+ " Uhr" # Sonnenuntergang formatiert (UTC Time)
        for i in data['weather']:
            dsky = i['description'] # aktuelle Situaltion (z.Bsp. Regen, Nebel, Wolken)
            wid =  i['id'] # aktuelle Wetter ID
            if dsky != "mist" and wid != "701":
             break # nach 1. Description abbrechen falls mehrere vorhanden sind
        if dsky == "scattered clouds" or dsky == "clear sky":     
            mc = "high" # LED-Matrix Kontrast hoch
        else:
            mc = "low"  # LED-Matrix Kontrast niedrig    
        WetterText = f'Aktuelle Wetterdaten fuer {city}: Temperatur: {dsky} bei {temp} Grad - Luftfeuchte: {humidity} % - Luftdruck: {airpress} hPa - Wind: {wspeed} km/h - Sonnenaufgang: {sunrise} Uhr - Sonnenuntergang: {sunset} Uhr'
        chars = {'broken clouds':'aufgelockert bewoelkt',
                 'few clouds':'leicht bewoelkt',
                 'clear sky':'klarer Himmel',
                 'light rain':'leichter Regen',
                 'overcast clouds':'bedeckter Himmel',
                 'fog':'Nebel',
                 'rain':'Regen',
                 'heavy intensity rain':'starker Regen',
                 'moderate rain':'leichter Regen',
                 'scattered clouds':'vereinzelt Wolken'} # Englische Angaben ins deutsche Übersetzen (eventuell noch erweitern)
        for char in chars:
            WetterText = WetterText.replace(char,chars[char])       
    except:
        WetterText = "Wetterdaten deaktiviert!"
        mc = "low"  # LED-Matrix Kontrast niedrig
        sunrise = "06:00"  # Sonnenaufgang im Fehlerfall oder wenn Wetterdaten deaktiviert
    return sub('[^abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890()?=/.%&:!, -]', ' ', WetterText), mc, sunrise

def BadWeatherNews(URL): # https://wettwarn.de/wettwarn_wetterwarnungen/warnregion_waehlen/ 
    try:  
        BadWeatherNewsFeed = feedparser.parse(URL)
        BadWeatherNewsText = BadWeatherNewsFeed.entries[0].title
        chars = {'ö':'oe','ä':'ae','ü':'ue','Ö':'Oe','Ä':'Ae','Ü':'Ue','ß':'ss','–':'-',' ':' ','§':'Paragraph'}
        for char in chars:
            BadWeatherNewsText = BadWeatherNewsText.replace(char,chars[char])
        #print('----------------------')    
        #print(BadWeatherNewsText)
        #print('----------------------')
        if BadWeatherNewsText.startswith("DWD WETTERWARNUNG:"):
           BadWeatherNewsText = BadWeatherNewsText.replace("DWD WETTERWARNUNG:", "Achtung Unwetterwarnung:")   
    except:
        BadWeatherNewsText = "Keine Unwetterwarnungen ???"
    return sub('[^abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890()?=/.%&:!, -]', '', BadWeatherNewsText)

def FritzBoxMissedCallCount(IP,FB_Password):
    try:
        fc = FritzCall(address=IP, password=FB_Password)
        calls = fc.get_missed_calls(update=True, num=None, days=1) # Liste der verpassten Anrufe von heute und gestern
        # calls = fc.get_missed_calls(update=True, num=None, days=None) # Liste aller verpassten Anrufe
        CallCount = 0
        for call in calls:
           CallCount = CallCount +1
    except:
        CallCount = -1 
    return CallCount

def UnreadMailCount(Servername, UserName, Password):
 try:
    mail = imaplib.IMAP4_SSL(Servername)
    mail.login(UserName, Password)
    mail.select("inbox", True) # connect to inbox.
    return_code, mail_ids = mail.search(None, 'UnSeen')
    count = len(mail_ids[0].split())
 except:
    count = -1
 return count   

def TelegramNews(): # Daten von Chat-App "Telegram" holen und Anzeigen
   try:
    botToken = TelegramAPIKey # "BOT-Token" des erstellten BOT's
    url = f'http://api.telegram.org/bot' + botToken + '/getUpdates'
    update_raw = requests.get(url + "?offset=" + str(OFFSET))
    update = update_raw.json()
    num_updates = len(update["result"])
    last_update = num_updates - 1
    TelegramText = update['result'][last_update]['message']['text']
   except:
       TelegramText = "Telegram Nachrichten deaktiviert!"
   return sub('[^abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890()?=/.%&:!, -]', ' ', TelegramText) # Telegramtext zurückgeben
       
def IsOnline():
        mem1 = 0
        try:
         host = socket.gethostbyname("www.google.com")  # Change to personal choice of site
         s = socket.create_connection((host, 80), 2)
         s.close()
         mem2 = 1
         if mem2 == mem1:
            pass  # Add commands to be executed on every check
         else:
            mem1 = mem2
            #IsOnlineText = "Internet is working"  # Will be executed on state change
         return True    

        except Exception as e:
            mem2 = 0
        if mem2 == mem1:
            pass
        else:
            mem1 = mem2
            # IsOnlineText = "Internet is down"
        return False
    
if __name__ == "__main__":
    Wochentag =["Sonntag ", "Montag ", "Dienstag ", "Mittwoch ", "Donnerstag ", "Freitag ", "Samstag "]
    
    # ******************************************************************************************************
    # ************** Variablen mit den gewünschten Werten vorbelegen ***************************************
    # ******************************************************************************************************
    
    #----------------------------------------------------------------------------------------------------
    # Ausrichtung der Uhrzeitanzeige
    ClockDisplayPosition = "top" #  top = oben  -  bottom = unten  (ungleich top oder bottom = unten)
    #----------------------------------------------------------------------------------------------------
    
    # ScrollIn und ScrollOut der Anzeige festlegen
    ClockScrollIn = "H" # V = Vertical  H = Horizontal   Default ist "V"
    ClockScrollOut = "H" # V = Vertical  H = Horizontal   Default ist "V"
    
    # PushButton-Setup
    PushButtonGPIOPort= 21 # Pin-Nummer (nicht GPIO-Nummer) auf GPIO-Leiste gegen Ground
    LongPushTime= 1 # Länge in Sekunden bis Event
    PushButtonDePrell = 0.03 # Entprellzeit für den PushButton (sollte standardmäßig so bleiben) - Default = 0.03
    PushButtonStatus = "Active" # PushButton aktivieren oder deaktivieren
    # wenn PushButton nicht vorhanden "NotActive" = deaktiviert  -  Wenn PushButton vorhanden "Active" = aktiviert)
    
    # Wetternews und Telegram API Schlüssel
    WeatherNewsAPIKey = "4e9f18945af4d0c5769e1620arr1059a" # Hier den eigenen API Key von OpenWheaterMAP eigeben
    TelegramAPIKey= "1844486426:AAG5cwqqgZ3zJl7a-IKDd2unvs7FEPPptk0" # Hier den "BOT-Token" des erstellten BOT's eingeben
    
    # Stadt für WetterNews
    WheatherNewsCity= "Berlin" # Hier die gewünschte Stadt eingeben
    
    # RSS Feed URL für Unwetterwarnung --> hier als Beispiel Berlin
    BadWeatherURL = "https://wettwarn.de/rss/efx.rss" # hier findet Ihr eure Region oder Stadt : --> https://wettwarn.de/wettwarn_wetterwarnungen/warnregion_waehlen/
    BadWeatherMode = "on" # on = Anzeige von Unwetterwarnung  off = keine Anzeige von Unwetterwarnungen
    
    # weitere Einstellungen 
    HideClockTimeHour = "21" # ab hier Uhr ausblenden (Stunde Uhrzeit --> ohne führende Null)   -->  -1  = Uhr nicht Ausblenden
    ShowClockTimeHour = "6"  # ab hier Uhr wieder anzeigen (Stunde Uhrzeit --> ohne führende Null)
    AutoShowClock = "on"     # on = Uhr Einblenden bei Sonnenaufgang   - off = Uhr nur Einblenden nach bestimmter Zeit (ShowClockTimeHour)
    # (Wenn "WetterNews" deaktiviert ist , dann ist AutoShowClock = "off")
    
    DisplayContrastHigh = 16 # Voller Displaycontrast
    DisplayContrastLow = 5 # geringer Displaycontrast
    FullDisplayContrastHour = 12 # Ab hier vollen Displaykontrast (Stunde Uhrzeit) --> je nach Wetter wenn Wetternews aktiviert
    MinDisplayContrastHourWinter = 15 # Ab hier niedriger Displaycontrast (Stunde Uhrzeit - im Winter)
    MinDisplayContrastHourSummer = 19 # Ab hier niedriger Displaycontrast (Stunde Uhrzeit - im Sommer)
    
    # Geburtstagsgruß Datum
    DateOfBirth = "28.02"
    
    HDBL = "TH" # Feiertags Bundesland --> keine Angabe gibt nur die bundeseinheitlichen Feiertage aus (Bundesländer siehe unten) 
    
    AlertMaxCPUTemp = 70 # Alarm-Anzeige bei Temperatur von X Grad oder höher der CPU
    
    NewsTrigger = 15 # Nach X sekunden (von 1 Minute) - Prüfen auf vorhandene News
    
    TriggerWeatherData = 5 # nur alle X Minuten die Wetterdaten anzeigen wenn keine Änderung
    
    CurrentDateTimeCounter = 3 # aktuelles Datum nur alle X Minuten anzeigen
    
    WaitTimeforOnline = 8 # Alle X sekunden "Internetstatus: Offline" anzeigen wenn keine Internetverbindung
    
    GhostMode = "on" # on = Geist wird um Mitternacht angezeigt off = Geist wird nicht um Mitternacht angezeigt
    
    SoundMode = "on"  # on = beim Start und jede volle Stunde wird ein Sound ausgegeben (nur wenn Uhrzeit eingeblendet) off = kein Sound
    StartSoundFile= "sound1.mp3" # Sound-Datei beim Start der Uhr
    HourSoundFile= "sound3.mp3" # Sound-Datei zu jeder vollen Stunde
    ShowClockSoundFile= "sound4.mp3" # Sound wenn die Uhr wieder eingeblendet wird
    AlarmClockSoundFile= "sound2.mp3" # Sound-Datei für Wecker
    AlarmClockCount = -1 # Wie oft soll der Sound für den Wecker ausgegeben werden (-1 = Wecker deaktiviert)
    AlarmClockTime = "06:00" # Wecker Uhrzeit (mit führender Null bei Uhrzeiten zischen 0 und 9 Uhr)
    SoundVolume = 40    # Sound-Lautstärke anpassen  (Standard = 40)
    HourSoundFrom = 5 # Stunde ab wann der Sound jede volle Stunde abgespielt werden soll (Wenn Uhrzeit eingeblendet)
    HourSoundTo = 21 # Stunde bis wann der Sound jede volle Stunde abgespielt werden soll (Wenn Uhrzeit eingeblendet)
    
    # CountDown Daten
    CDEventYear = 2043 # Jahr des Events
    CDEventMonth = 9 # Monat des Events
    CDEventDay = 1 # Tag des Events
    CDEventText = "zur Rente" # Text für den CountDown
    CDEventViewCount = 10 # alle X Minuten wird der CountDown-Zähler angezeigt (-1 = CountDown deaktiviert)
    
    # **** Prüfung auf ungelesene E-Mail Nachrichten ****
    CurrentMailCheckInterval = 16 # Prüfung alle X Minuten  -1 = Prüfung aller Konten deaktiviert - Empfehlung: 15
    # 1. Konto
    CheckMode1 = "on" # on = aktiviert  off = deaktiviert
    MailAccountName1 = "" # Dient nur zur Anzeige damit man weis welches Konto gemeint ist - Name ist frei wählbar - z.Bsp. Info-Konto (kein @-Zeichen verwenden)
    MailServername1 = "" # IMAP Servername
    MailUserName1 = "" # Benutzername Konto 1
    MailPassword1 = "" # Passwort Konto 1
    # 2. Konto
    CheckMode2 = "on" # on = aktiviert  off = deaktiviert
    MailAccountName2 = "" # Dient nur zur Anzeige damit man weis welches Konto gemeint ist - Name ist frei wählbar z.Bsp. Kontakt-Konto (kein @-Zeichen verwenden)
    MailServername2 = "" # IMAP Servername
    MailUserName2 = "" # Benutzername Konto 2
    MailPassword2 = "" # Passwort Konto 2
    # 3. Konto
    CheckMode3 = "on" # on = aktiviert  off = deaktiviert
    MailAccountName3 = "" # Dient nur zur Anzeige damit man weis welches Konto gemeint ist - Name ist frei wählbar z.Bsp. Bestellung-Konto (kein @-Zeichen verwenden)
    MailServername3 = "" # IMAP Servername
    MailUserName3 = "" # Benutzername Konto 3
    MailPassword3 = "" # Passwort Konto 3
    
    # Anzahl verpasster Anrufe über eine FritzBox
    CheckMissedFBCalls = "on" # on = aktiviert  off = deaktiviert
    FritzBoxIP = "192.168.178.1" # Default ist "192.168.178.1"
    FritzBoxPassword = "" # Fritzbox Passwort
    CurrentFBCheckInterval = 8 # Prüfung auf verpasste Anrufe alle X Minuten 
    
    # ********************************************************************************************************
    # ********************************************************************************************************
    
    # Hilfsvariablen initialisieren
    OldNewsText = ""
    OldBoersenText = ""
    #OldSubscriberText = ""
    OldITText = ""
    OldMobileText = ""
    OldWetterText = ""
    OldTelegramText = ""
    LMC = ""
    SRT = ""
    ShowClockTime = ""
    MailText = ""
    ClockHide = False
    AlertCPUTemp = False
    WetterCounter = TriggerWeatherData + 1
    DayCounter = CurrentDateTimeCounter + 1
    MailCheckInterval = CurrentMailCheckInterval + 1
    FBCheckInterval = CurrentFBCheckInterval + 1
    PlausiCheck = 0
    GetWeatherData = False
    CDEventViewCounter = 0
    MailCount1 = 0
    MailCount2 = 0
    MailCount3 = 0
    MissedCallCount = 0
    
    # Plausi-Check
    try: 
     if NewsTrigger <= 0 or NewsTrigger > 59:
        NewsTrigger = 15 # Default
        PlausiCheck = PlausiCheck + 1
     if HourSoundFrom <= 0 or HourSoundFrom > 23:
        HourSoundFrom = 5 # Default
        PlausiCheck = PlausiCheck + 1
     if HourSoundTo <= 0 or HourSoundTo > 23:
        HourSoundTo = 21 # Default
        PlausiCheck = PlausiCheck + 1      
     SecondTrigger = NewsTrigger-5
     if SecondTrigger <= 0:
        SecondTrigger = 5
     if SecondTrigger < 10:
        SecondTrigger = "0"+str(SecondTrigger)
     else:
        SecondTrigger = str(SecondTrigger) 
     CPUCheckTrigger = NewsTrigger - 10
     if CPUCheckTrigger < 0 or CPUCheckTrigger > 59 or CPUCheckTrigger == NewsTrigger:
        CPUCheckTrigger = 59 # Default
        PlausiCheck = PlausiCheck + 1
     if HideClockTimeHour != "-1":   
        if int(HideClockTimeHour) < 0 or int(HideClockTimeHour) > 23:
           HideClockTimeHour = "23" # Default
           PlausiCheck = PlausiCheck + 1
        if int(HideClockTimeHour) < 10:
           HideClockTimeHour = "0"+ HideClockTimeHour   
     if int(ShowClockTimeHour) < 0 or int(ShowClockTimeHour) > 23:
        ShowClockTimeHour = "6" # Default
        PlausiCheck = PlausiCheck + 1
     if int(ShowClockTimeHour) < 10:
        ShowClockTimeHour = "0"+ ShowClockTimeHour
     if int(ShowClockTimeHour) == int(HideClockTimeHour):
        ShowClockTimeHour = "6" # Default
        HideClockTimeHour = "23" # Default
        PlausiCheck = PlausiCheck + 1
     # E-Mail Unread MessageCount Check   
     if MailCheckInterval > -1:   
         if (CheckMode1 == "on") and (MailServername1 == "" or MailUserName1 == "" or MailPassword1 == ""):
             CheckMode1 = "off"
         if (CheckMode2 == "on") and (MailServername2 == "" or MailUserName2 == "" or MailPassword2 == ""):
             CheckMode2 = "off"
         if (CheckMode3 == "on") and (MailServername3 == "" or MailUserName3 == "" or MailPassword3 == ""):
             CheckMode3 = "off"
         if MailAccountName1 == "":
            MailAccountName1 = "E-Mail Konto 1"
         if MailAccountName2 == "":
            MailAccountName2 = "E-Mail Konto 2"
         if MailAccountName3 == "":
            MailAccountName3 = "E-Mail Konto 3"
     else:
         CheckMode1 = "off"
         CheckMode2 = "off"
         CheckMode3 = "off"
     # Fritzbox verpasste Anrufe    
     if CurrentFBCheckInterval < 1:
        CheckMissedFBCalls = "off"    
    except:
        HideClockTimeHour = "-1" # Default Ausgeschaltet
        ShowClockTimeHour = "6"  # Default
        CPUCheckTrigger = 59 # Default
        NewsTrigger = 15 # Default
        PlausiCheck = PlausiCheck + 1
        MailCheckInterval = -1 # E-Mail Unread MessageCount Check deaktiviert
        CheckMissedFBCalls = "off" # Prüfung auf verpasste Anrufe deaktiviert
        
    # Main
    ClockStop= False
    Uhr = RollingClock.RollingClock() # Uhr Initialisieren
    print("")
    
    # *************************************
    # Uhrzeit ScrollIn Modus
    Uhr.ClockScrollInMode(ClockScrollIn) 
    
    # Uhrzeit ScrollOut Modus
    Uhr.ClockScrollOutMode(ClockScrollOut) 
    # *************************************
    
    # Start Clock-Intro
    print("---------------------")
    print("Start Clock-Intro ...")
    print("---------------------")
    Uhr.ClockIntro("LED",5)
    Uhr.ClockIntro("MATRIX",-1) # Value less than 0 --> Scroll horizontal
    Uhr.ClockIntro("UHR",6)
    print("")
    
    # Auf Onlineverbindung warten
    while IsOnline() == False:
        Uhr.ClockIntro("*** Internetstatus: Offline ***",-1)
        time.sleep(1)
        Uhr.ClockIntro("Uhrzeit kann nicht synchronisiert werden !",-1)
        time.sleep(1)
        Uhr.ClockIntro("Uhr wartet auf Internetverbindung ...",-1)
        print("-------------------------------")
        print("*** Internetstatus: Offline ***")
        print("-------------------------------")
        time.sleep(WaitTimeforOnline)
        
    print("")
    print("------------------------------")
    print("*** Internetstatus: Online ***")
    print("------------------------------")
    print("")
    WetterText,LMC,SRT = WetterNews() # WetterNews abfragen
    if WetterText == "Wetterdaten deaktiviert!":
       if HideClockTimeHour != "-1": 
          ShowClockTime = ShowClockTimeHour +":00"
       else:
          ShowClockTime = SRT # Default Uhrzeit: 06:00 Uhr (wenn Uhrzeit per PushButton ausgeblendet wurde)
       AutoShowClock = "off"   
       print("-----------------------------------")
       print("Status - Wetter News: deaktiviert !")
       print("-----------------------------------")
    else:
       print("-------------------------------")
       print("Status - Wetter News: aktiviert")
       print("-------------------------------")
       if HideClockTimeHour != "-1": 
           if AutoShowClock == "on":
             ShowClockTime = SRT  # Uhrzeit Sonnenaufgang
           else:
             ShowClockTime = ShowClockTimeHour +":00"
       else:
          ShowClockTime = SRT # Uhrzeit Sonnenaufgang (wenn Uhrzeit per PushButton ausgeblendet wurde)  
             
    if HideClockTimeHour != "-1":
       print("")
       print("--------------------------------------------------------")  
       print("Einblenden der Uhrzeit um: "+ShowClockTime+" Uhr (wenn ausgeblendet)")
       print("--------------------------------------------------------") 
       print("")
     
    TelegramText = TelegramNews() # Telegram News abfragen
    if TelegramText == "Telegram Nachrichten deaktiviert!":
      print("-------------------------------------------------------------")  
      print("Telegram Nachrichren deaktiviert oder keine neuen Nachrichten")
      print("-------------------------------------------------------------")
    
    print("")
    StartTimeHour = int(datetime.now().strftime('%H'))
    StartTimeSeason = int(datetime.now().strftime('%m'))
    StartTimeHide = datetime.now().strftime('%H:%M')
    if StartTimeHour >= FullDisplayContrastHour and StartTimeHour < MinDisplayContrastHourSummer and LMC == "high":
     if (StartTimeSeason == 5 or StartTimeSeason == 6 or StartTimeSeason == 7 or StartTimeSeason== 8):
        Uhr.device.contrast(DisplayContrastHigh) # Displayhelligkeit Voreinstellen je nach Jahreszeit
        print("------------------------------------")
        print("Displaystart: Hell - Frühling/Sommer")
        print("------------------------------------")
     else:
        if StartTimeHour >= FullDisplayContrastHour and StartTimeHour < MinDisplayContrastHourWinter:
            Uhr.device.contrast(DisplayContrastHigh) # Displayhelligkeit Voreinstellen je nach Jahreszeit
            print("----------------------------------")
            print("Displaystart: Hell - Herbst/Winter")
            print("----------------------------------")
        else:    
            Uhr.device.contrast(DisplayContrastLow) # Displayhelligkeit Voreinstellen je nach Jahreszeit
            print("------------------------------------")
            print("Displaystart: Dunkel - Herbst/Winter")
            print("------------------------------------") 
    else:
        Uhr.device.contrast(DisplayContrastLow) # Displayhelligkeit Voreinstellen
        print("--------------------")
        print("Displaystart: Dunkel")
        print("--------------------")
         
    THoliDay = RollingClock.HolidayText(HDBL) # Ermitteln ob Feiertag beim Programmstart
    if THoliDay != "":
        print("")
        print("--------------------------------------")
        print("Heute ist Feiertag: "+THoliDay)
        print("--------------------------------------")
    
    print("")
    print("-----------------------")
    print("CPU-Temperatur: "+str(RollingClock.Measure_CPU_Temp())+" Grad")
    print("-----------------------")
    print("")
    
    if ClockDisplayPosition == "top":
        print("------------------------------------")
        print("Ausrichtung der Uhrzeitanzeige: oben")
        print("------------------------------------")
        print("")
    else:
        print("-------------------------------------")
        print("Ausrichtung der Uhrzeitanzeige: unten")
        print("-------------------------------------")
        print("")
        
    # Einstellungen überprüfen
    if PlausiCheck > 0:
       print("")
       print("------------------------------------") 
       print("Bitte die Einstellungen überprüfen !")
       print("------------------------------------") 
       print("")  
       for i in range(0,3):  
           Uhr.ClockIntro("+++ Bitte die Einstellungen überprüfen ! +++",-1) # Value less than 0 --> Scroll horizontal
           time.sleep(2) # 2 sekunden warten
        
    Uhr.ClockDisplayPosition(ClockDisplayPosition) # Ausrichtung der Uhrzeitanzeige
    
    Uhr.start() # ********** Start Clock  ************
    
    # PushButton initialisieren
    Uhr.PushButtonAction(PushButtonGPIOPort,LongPushTime,PushButtonDePrell,PushButtonStatus)
    
    # Sound beim Starten der Uhr ausgeben wenn in Uhrzeitbereich
    if time_in_range(HourSoundFrom,HourSoundTo,StartTimeHour) == True:
        if Uhr.PlayHourSound(StartSoundFile, SoundVolume, SoundMode) == True:
            print("-------------------------------------------") 
            print("Soundausgabe- Start-Sound wurde ausgegeben ")
            print("-------------------------------------------")
        else:
            print("------------------------------------------------") 
            print("Soundausgabe- Start-Sound wird nicht ausgegeben ")
            print("------------------------------------------------")  
    else:
            print("------------------------------------------------") 
            print("Soundausgabe- Start-Sound wird nicht ausgegeben ")
            print("------------------------------------------------")
    
    print("");
    print("Uhr gestartet")
    print("Press Ctrl-C to quit.")
    print("")
    
    # Geist mal Testen
    #Uhr.Hide()
    #for i in range(5):
     #Uhr.DrawGhost(GhostMode) # Geist anzeigen
     #time.sleep(1)
    #Uhr.Show() 
    
    # Sound Testen
    #for i in range(5):
     #Uhr.PlayHourSound("sound2.mp3", SoundVolume, SoundMode)
    
    # Test Spezial und Intro Text mal Testen
    #Uhr.Hide()
    #time.sleep(1)
    #Uhr.CheckHideClock()
    #Uhr.SpecialText("Gute",4)
    #Uhr.SpecialText("Nacht",2)
    #Uhr.ClockIntro("UHR",6)
    #Uhr.Show()
    
    # Vorschau CountDown Zähler wenn aktiviert
    if CDEventViewCount != -1:   
       VCountDownTextOut = Uhr.CountDown(CDEventYear, CDEventMonth, CDEventDay, CDEventText)
       if VCountDownTextOut != "-1":
        if VCountDownTextOut == "Fail":
          print("")  
          print("-------------------------------------------------------------------------")
          print("Textausgabe in Kommandozeile - ungültige Datumsangabe im CountDown Zähler")
          print("-------------------------------------------------------------------------")
          print("")
        else:  
          print("")
          print("------------------------------------------------------------------------------------")
          print("CountDown: "+VCountDownTextOut)
          print("------------------------------------------------------------------------------------")
          print("")
       else:
          print("") 
          print("-------------------------------------------------------------")
          print("Textausgabe in Kommandozeile - Der CountDown ist abgelaufen !")
          print("-------------------------------------------------------------")
          print("")
    
    # Uhr Ausblenden oder nicht
    if HideClockTimeHour != "-1": 
        if time_in_range(int(HideClockTimeHour),int(ShowClockTimeHour),StartTimeHour) == True: # Display abschalten
            ClockHide= True
            Uhr.Hide()
            time.sleep(1) # kurz warten
            GN = [22,23,0,1,2,3,4] # Nacht
            if StartTimeHour in GN:
                Uhr.SpecialText("Gute",4)
                Uhr.SpecialText("Nacht",2)
            else:
                Uhr.SpecialText("Bis",4)
                Uhr.SpecialText("Bald...",1)
               
    #try:
    signal.signal(signal.SIGINT, signal_handler)
    while not ClockStop:
            datum = datetime.now().strftime('%d.%m.%Y')
            SpecialDat = datetime.now().strftime('%d.%m')
            FullTime = datetime.now().strftime('%H:%M:%S')
            CheckTime = datetime.now().strftime('%M:%S')
            season = int(datetime.now().strftime('%m'))
            TimeHour = int(datetime.now().strftime('%H'))
            RepeatTime= datetime.now().strftime('%M')
            tag = datetime.now().strftime('%w')
            sekunden = datetime.now().strftime('%S')
            
            if FullTime == "00:00:"+SecondTrigger: # Prüfen ob neuer Tag ein Feiertag ist
               THoliDay = RollingClock.HolidayText(HDBL)
               
            # Uhrzeit Sonnenaufgang für den neuen Tag
            if FullTime == "00:15:"+SecondTrigger and GetWeatherData == False:
                WetterText,LMC,SRT = WetterNews()
                ShowClockTime = SRT  # Uhrzeit Sonnenaufgang (bei deaktivierten WetterNews = Default: 06:00 Uhr)
                print("")
                print("------------------------------------------------------")
                print("Uhrzeit - Sonnenaufgang für den neuen Tag  : "+SRT+" Uhr")
                print("------------------------------------------------------")
                print("")
            
            if PushButtonStatus == "Active":
                PushButtonEvent = Uhr.PBEvent() # Abfrage ob PushButton gedrückt wurde
                # Aktion wenn Taste von "PushButton" gedrückt wurde
                if PushButtonEvent == "long":
                   print("-----------------------------------------")
                   print("PushButton-Longsequenz wird ausgeführt...")
                   print("-----------------------------------------")  
                   PushButtonEvent = "" # Variable zurücksetzen
                   ClockHide= True # Uhr ausblenden
                   Uhr.Hide()
                if PushButtonEvent == "short":
                   print("------------------------------------------")
                   print("PushButton-Shortsequenz wird ausgeführt...")
                   print("------------------------------------------") 
                   PushButtonEvent = "" # Variable zurücksetzen
                   OldNewsText = "" # Tagesschau-News zurücksetzen
                   OldBoersenText = "" # Börsen-News zurücksetzen
                   OldITText = "" # IT-News zurücksetzen
                   OldMobileText = "" # Mobile-News zurücksetzen
                   OldWetterText = "" # Wetter-News Zurücksetzen
                   ClockHide= False # Uhr einblenden
                   Uhr.Show()
            
            if SpecialDat != "31.12" and ClockHide == False and HideClockTimeHour != -1: # Silvester oder bei TimeHideClockHour = -1 die Uhr nicht abschalten 
              if FullTime == HideClockTimeHour +":00:"+SecondTrigger: # Display abschalten
                   ClockHide= True
                   Uhr.Hide()
                   print("\n")
                   GN = [22,23,0,1,2,3,4] # Nacht
                   if TimeHour in GN:
                        print("------------------------------------------------------------------")
                        print("Textausgabe in Kommandozeile - *** Gute Nacht *** (Uhr Ausblenden)")
                        print("------------------------------------------------------------------")
                        print("\n")   
                        Uhr.SpecialText("Gute",4)
                        Uhr.SpecialText("Nacht",2)
                   else:
                        print("--------------------------------------------------------------------")
                        print("Textausgabe in Kommandozeile - *** Bis Bald ... *** (Uhr Ausblenden)")
                        print("--------------------------------------------------------------------")
                        print("\n")   
                        Uhr.SpecialText("Bis",4)
                        Uhr.SpecialText("Bald...",1)     
              
            if ClockHide == True:
                 if FullTime == ShowClockTime+":"+SecondTrigger: # Display einschalten
                   print("\n")
                   print("---------------------------------------------")
                   print("Textausgabe in Kommandozeile - Uhr Einblenden")
                   print("---------------------------------------------")
                   print("\n")
                   print("------------------------------------------------------------------")  
                   if Uhr.PlayHourSound(ShowClockSoundFile, SoundVolume, SoundMode) == True:
                      print("-------------------------------------") 
                      print("Soundausgabe- Sound wurde ausgegeben ")
                      print("-------------------------------------")
                   else:
                      print("------------------------------------------") 
                      print("Soundausgabe- Sound wird nicht ausgegeben ")
                      print("------------------------------------------")
                   Uhr.ClockIntro("LED",5)
                   Uhr.ClockIntro("MATRIX",-1) # Value less than 0 --> Scroll horizontal
                   Uhr.ClockIntro("UHR",6)
                   GM = [5,6,7,8,9,10] # früher Morgen
                   if TimeHour in GM:
                       time.sleep(2) # 2 sekunden warten
                       Uhr.SpecialText("Guten",2)
                       Uhr.SpecialText("Morgen",-1)
                   time.sleep(1) # 1 sekunden warten
                   Uhr.Show() # Uhr Einblenden
                   ClockHide = False
             
            if sekunden == str(CPUCheckTrigger):
             CPU_Temp = RollingClock.Measure_CPU_Temp()   
             if CPU_Temp > AlertMaxCPUTemp:
                AlertCPUTemp = True
                print("--------------------------------------------------") 
                print("Textausgabe - Achtung !!!  CPU-Temperatur zu hoch ")
                print("--------------------------------------------------")
                Uhr.ShowText(" +++ Achtung !!!  CPU-Temperatur zu hoch ("+str(CPU_Temp)+" Grad) +++") # CPU Temperatur Alarm
             else:
                AlertCPUTemp = False 
            
            if CheckTime == "00:00" and ClockHide == True and AlertCPUTemp == False: # jede Stunde kurz Melden wenn Clock Hide
              if TimeHour != 0: # Mitternacht einen Geist anzeigen    
                print("--------------------------------------------") 
                print("Displayausgabe - Doppelpunkt  (als Zeichen) ")
                print("--------------------------------------------")
                Uhr.CheckHideClock()  # Doppelpunkt für 5 sek. Anzeigen wenn Uhr ausgeblendet
              else:
                print("------------------------------------------") 
                print("Displayausgabe - Ein Geist um Mitternacht ")
                print("------------------------------------------")
                for i in range(2):
                 Uhr.DrawGhost(GhostMode) # Geist anzeigen 2x
                 
            if CheckTime == "00:00" and ClockHide == False: # jede Stunde einen Sound ausgeben (Wenn Uhrzeit Eingeblendet)
              if time_in_range(HourSoundFrom,HourSoundTo,TimeHour) == True:
                   print("------------------------------------------------------------------") 
                   if Uhr.PlayHourSound(HourSoundFile, SoundVolume, SoundMode) == True:
                      print("-------------------------------------") 
                      print("Soundausgabe- Sound wurde ausgegeben ")
                      print("-------------------------------------")
                   else:
                      print("------------------------------------------") 
                      print("Soundausgabe- Sound wird nicht ausgegeben ")
                      print("------------------------------------------")
              else:
                     print("------------------------------------------") 
                     print("Soundausgabe- Sound wird nicht ausgegeben ")
                     print("------------------------------------------")
                     
            if FullTime == AlarmClockTime+":10": # Wecker
               if AlarmClockCount != -1:
                for i in range (AlarmClockCount):   
                   print("------------------------------------------------------------------")
                   if Uhr.PlayHourSound(AlarmClockSoundFile, SoundVolume, SoundMode) == True:
                      print("--------------------------------------------") 
                      print("Soundausgabe- Wecker-Sound wurde ausgegeben ")
                      print("--------------------------------------------")
                   else:
                      print("-------------------------------------------------") 
                      print("Soundausgabe- Wecker-Sound wird nicht ausgegeben ")
                      print("-------------------------------------------------")          
             
            if sekunden == str(NewsTrigger) and ClockHide == False and AlertCPUTemp == False: # NewTrigger: 15 ist Standard
              
             if IsOnline() == True: # Check ob Internetverbindung besteht
                
                # 3 Leerzeilen in Kommandozeile einfügen
                print("\n")
                print("-----------------------------------------------------------------")
                print("Textausgabe in Kommandozeile - Neuer Durchlauf ... ("+FullTime+" Uhr)")
                print("-----------------------------------------------------------------")
                print("\n")
                
                # show Youtube Subscriber Counter if changed
                #SubscriberText = ReadYoutubeSubscriberCounter()
                #if SubscriberText != OldSubscriberText:
                  #print("Textausgabe - Anzeige Abonennten ")
                    #if Uhr.ShowText(SubscriberText):
                        #OldSubscriberText=SubscriberText
                #else:
                    #print("---------------------------------------------------------------------------")
                    #print("Textausgabe in Kommandozeile - Abonennten-Counter (keine neuen Abonennten) ") # Anzeige auf Kommandozeile zu Kontrolle
                    #print("---------------------------------------------------------------------------")   

                # Testlauf
                #Uhr.ShowText("Testanzeige")
                
                # show feed if changed (Tagesschau News)
                NewsText = ReadNews()
                if (RepeatTime == "00") and NewsText == OldNewsText:
                    OldNewsText = "" # Tagesschau-News alle 60 Minuten anzeigen, auch wenn schon gelaufen
                
                # show feed if changed (Tagesschau News)
                if NewsText != OldNewsText:
                    print("Textausgabe - *** Tagesschau-News *** ")
                    if Uhr.ShowText("+++ "+ NewsText +" +++"):
                        OldNewsText=NewsText
                else:
                    print("-------------------------------------------------------------------")
                    print("Textausgabe in Kommandozeile - *** keine neuen Tagesschau-News *** ") # Anzeige auf Kommandozeile zu Kontrolle
                    print("-------------------------------------------------------------------")
                    
                # show feed if changed (Börsen News)
                BoersenText = BoersenNews()
                if BoersenText != OldBoersenText:
                    print("Textausgabe - *** Börsen-News *** ")
                    if Uhr.ShowText("+++ " + BoersenText + " +++"):
                        OldBoersenText=BoersenText    
                else:
                    print("---------------------------------------------------------------")
                    print("Textausgabe in Kommandozeile - *** keine neuen Börsen-News *** ") # Anzeige auf Kommandozeile zu Kontrolle
                    print("---------------------------------------------------------------")       
                        
                # show feed if changed (IT-News)
                ITText = ITNews()
                if ITText != OldITText:
                  print("Textausgabe - *** IT-News *** ")  
                  if Uhr.ShowText("+++ " + ITText + " +++"):
                       OldITText=ITText
                else:
                    print("-----------------------------------------------------------")
                    print("Textausgabe in Kommandozeile - *** keine neuen IT-News *** ") # Anzeige auf Kommandozeile zu Kontrolle
                    print("-----------------------------------------------------------")        
                       
                # show feed if changed (Mobile News)
                MobileText = MobileNews()
                if MobileText != OldMobileText:
                  print("Textausgabe - *** Mobile-News *** ")  
                  if Uhr.ShowText("+++ " + MobileText + " +++"):
                       OldMobileText=MobileText
                else:
                    print("---------------------------------------------------------------")
                    print("Textausgabe in Kommandozeile - *** keine neuen Mobile-News *** ") # Anzeige auf Kommandozeile zu Kontrolle
                    print("---------------------------------------------------------------")
                    
                # show feed if changed (Telegram News)
                if RepeatTime == "10" or RepeatTime == "20" or RepeatTime == "30" or RepeatTime == "40" or RepeatTime == "50":
                  # Telegram Nachricht alle 10 Minuten (außer volle Stunde) anzeigen
                  TelegramText = TelegramNews()
                  if TelegramText != "Telegram Nachrichten deaktiviert!":
                    print("Textausgabe - *** Telegram-Nachricht *** ")
                    Uhr.ShowText("+++ Telegram Nachricht: " + TelegramText + " +++")
                  else:
                    print("------------------------------------------------------------------")
                    print("Textausgabe in Kommandozeile - *** keine Telegram-Nachrichten *** ") # Anzeige auf Kommandozeile zu Kontrolle
                    print("------------------------------------------------------------------")  
                
                # show feed (Unwetter News)
                if BadWeatherMode == 'on' : # on = Unwetterwarnung wird angezeigt
                    BadWeatherText = BadWeatherNews(BadWeatherURL)
                    #print("-----------------------------------------------------------------")
                    #print("Unwettertext: "+BadWeatherText) # Test-Anzeige auf Kommandozeile zu Kontrolle
                    #print("-----------------------------------------------------------------")   
                    if (BadWeatherText.find("Keine Warnungen") != -1) or \
                       (BadWeatherText.find("FROST") != -1) or \
                       (BadWeatherText.find("STURMBOeEN") != -1) or \
                       (BadWeatherText.find("LEICHTER") != -1) : # bei diesen Strings keine Unwetterwarnung
                      print("-----------------------------------------------------------------")
                      print("Textausgabe in Kommandozeile - *** keine neuen Unwetter-News *** ") # Anzeige auf Kommandozeile zu Kontrolle
                      print("-----------------------------------------------------------------")     
                    else:
                      print("------------------------------------")  
                      print("Textausgabe - *** Unwetter-News *** ")
                      print("------------------------------------")
                      Uhr.ShowText("+++ " + BadWeatherText + " +++")   
                
                # show feed if changed (Wetter News)
                WetterCounter = WetterCounter  - 1
                print("------------------------------------------------------------------------------")
                print("Textausgabe in Kommandozeile - Anzeige aktuelle Wetterdaten in "+str(WetterCounter)+" Minute(n)") # Anzeige auf Kommandozeile zu Kontrolle
                print("------------------------------------------------------------------------------")
                if WetterCounter == 0:
                 WetterCounter = TriggerWeatherData + 1
                 GetWeatherData == True # Wetterdaten holen Anfang
                 WetterText,LMC,SRT = WetterNews()
                 if season == 5 or season == 6 or season == 7 or season == 8:
                   if TimeHour >= FullDisplayContrastHour and TimeHour < MinDisplayContrastHourSummer and LMC == "high":
                    Uhr.device.contrast(DisplayContrastHigh) # Displayhelligkeit Voreinstellen je nach Jahreszeit
                    print("---------------------------------------")
                    print("Displaykontrast: Hell - Frühling/Sommer")
                    print("Sonnenaufgang  : "+SRT+" Uhr")
                    print("---------------------------------------")
                   else:    
                    Uhr.device.contrast(DisplayContrastLow) # Displayhelligkeit Voreinstellen je nach Jahreszeit
                    print("-----------------------------------------")
                    print("Displaykontrast: Dunkel - Frühling/Sommer")
                    print("Sonnenaufgang  : "+SRT+" Uhr")
                    print("-----------------------------------------")
                 else:
                    if TimeHour >= FullDisplayContrastHour and TimeHour < MinDisplayContrastHourWinter and LMC == "high":
                     Uhr.device.contrast(DisplayContrastHigh) # Displayhelligkeit Voreinstellen je nach Jahreszeit
                     print("-------------------------------------")
                     print("Displaykontrast: Hell - Herbst/Winter")
                     print("Sonnenaufgang  : "+SRT+" Uhr")
                     print("-------------------------------------")
                    else:    
                     Uhr.device.contrast(DisplayContrastLow) # Displayhelligkeit Voreinstellen je nach Jahreszeit
                     print("---------------------------------------")
                     print("Displaykontrast: Dunkel - Herbst/Winter")
                     print("Sonnenaufgang  : "+SRT+" Uhr")
                     print("---------------------------------------") 
                    
                 if WetterText != "Wetterdaten deaktiviert!":   
                   if WetterText != OldWetterText: 
                    print("Textausgabe - Wetter-News ")
                    if Uhr.ShowText("+++ " + WetterText + " +++"):
                      OldWetterText=WetterText   
                   else:
                    print("--------------------------------------------------------------")
                    print("Textausgabe in Kommandozeile - *** keine neuen Wetter-News ***") # Anzeige auf Kommandozeile zu Kontrolle
                    print("--------------------------------------------------------------")
                 else:
                   print("---------------------------------------------------------------")
                   print("Textausgabe in Kommandozeile - *** Wetter-News deaktiviert! ***") # Anzeige auf Kommandozeile zu Kontrolle
                   print("---------------------------------------------------------------") 
                 GetWeatherData == False # Wetterdaten holen Ende
                 
                # CountDown Zähler anzeigen wenn aktiviert
                if CDEventViewCount != -1:
                    CDEventViewCounter = CDEventViewCounter + 1
                    print("------------------------------------------------------------------------------")
                    print("Textausgabe in Kommandozeile - Anzeige des CountDown Zählers in "+str(CDEventViewCount-CDEventViewCounter)+" Minute(n)") # Anzeige auf Kommandozeile zu Kontrolle
                    print("------------------------------------------------------------------------------")
                    if CDEventViewCounter == CDEventViewCount:
                     CDEventViewCounter = 0
                     CountDownTextOut = Uhr.CountDown(CDEventYear, CDEventMonth, CDEventDay, CDEventText)
                     if CountDownTextOut != "-1":
                      if CountDownTextOut == "Fail":
                        print("-------------------------------------------------------------------------")
                        print("Textausgabe in Kommandozeile - ungültige Datumsangabe im CountDown Zähler")
                        print("-------------------------------------------------------------------------")
                      else:  
                        Uhr.ShowText("+++ "+CountDownTextOut+" +++") # CountDown jetzt ausgeben
                     else:
                        print("-------------------------------------------------------------")
                        print("Textausgabe in Kommandozeile - Der CountDown ist abgelaufen !")
                        print("-------------------------------------------------------------") 
                 
               # Ausgabe des Datum's    
                DayCounter= DayCounter - 1
                print("------------------------------------------------------------------------------")
                print("Textausgabe in Kommandozeile - Anzeige des aktuellen Datums in "+str(DayCounter)+" Minute(n)") # Anzeige auf Kommandozeile zu Kontrolle
                print("------------------------------------------------------------------------------")
                if DayCounter == 0:
                 DayCounter = CurrentDateTimeCounter + 1
                 print("") # Leerzeile
                
                 # Datum mit verschiedenen Grüßen
                 if SpecialDat == DateOfBirth:
                    print("-------------------------------------------------------")
                    print("Textausgabe (Spezialdatum) -  Alles gute zum Geburtstag")
                    print("-------------------------------------------------------")
                    Uhr.Hide() # Uhr Ausblenden
                    ClockHide= True
                    Uhr.SpecialText("+++ Heute ist " + Wochentag[int(tag)] + "der "+ datum + " +++",-9)
                    Uhr.SpecialText("Alles",3)
                    Uhr.SpecialText("gute",5)
                    Uhr.SpecialText("zum",8)
                    Uhr.SpecialText("Geburtstag",-1)
                    Uhr.Show() # Uhr Einblenden
                    ClockHide= False
                    
                 elif SpecialDat == "31.12":
                    print("--------------------------------------------------------")
                    print("Textausgabe (Spezialdatum) -  Guten Rutsch ins neue Jahr")
                    print("--------------------------------------------------------")
                    Uhr.Hide() # Uhr Ausblenden
                    ClockHide= True
                    Uhr.SpecialText("+++ Heute ist " + Wochentag[int(tag)] + "der "+ datum + " +++",-9)
                    Uhr.SpecialText("Guten",2)
                    Uhr.SpecialText("Rutsch",-1)
                    Uhr.SpecialText("ins",10)
                    Uhr.SpecialText("neue",5)
                    Uhr.SpecialText("Jahr",5)
                    Uhr.Show() # Uhr Einblenden
                    ClockHide= False
                    
                 elif SpecialDat == "01.01":
                    print("------------------------------------------------------")
                    print("Textausgabe (Spezialdatum) -  Alles gute im neuen Jahr")
                    print("------------------------------------------------------")
                    Uhr.Hide() # Uhr Ausblenden
                    ClockHide= True
                    Uhr.SpecialText("+++ Heute ist " + Wochentag[int(tag)] + "der "+ datum + " +++",-9)
                    Uhr.SpecialText("Alles",3)
                    Uhr.SpecialText("gute",5)
                    Uhr.SpecialText("im",12)
                    Uhr.SpecialText("neuen",2)
                    Uhr.SpecialText("Jahr",5)
                    Uhr.SpecialText(datetime.now().strftime('%Y'),3)
                    Uhr.Show() # Uhr Einblenden
                    ClockHide= False
                    
                 elif SpecialDat == "01.04":
                    print("------------------------------------------")
                    print("Textausgabe (Spezialdatum) -  April, April")
                    print("------------------------------------------")
                    Uhr.Hide() # Uhr Ausblenden
                    ClockHide= True
                    Uhr.SpecialText("+++ Heute ist " + Wochentag[int(tag)] + "der "+ datum + " +++",-9)
                    Uhr.SpecialText("April",4)
                    Uhr.SpecialText("April",4)
                    Uhr.Show() # Uhr Einblenden
                    ClockHide= False
                 else:
                    if THoliDay == "":
                        print("Textausgabe - *** Wochentag und Datum (kein Feiertag) *** ")
                        Uhr.ShowText("+++ Heute ist " + Wochentag[int(tag)] + "der "+ datum + " in der "+str(date.today().isocalendar()[1])+". Kalenderwoche  +++") # Datum anzeigen (wenn kein Feiertag)
                    else:
                        print("Textausgabe - *** Wochentag und Datum (mit Feiertag) *** ")
                        Uhr.Hide() # Uhr Ausblenden
                        ClockHide= True
                        Uhr.SpecialText("+++ Heute ist " + Wochentag[int(tag)] + "der "+ datum + " in der "+str(date.today().isocalendar()[1])+". Kalenderwoche  +++",-9)
                        Uhr.SpecialText("+++ "+THoliDay+" +++ ",-1)
                        Uhr.Show() # Uhr Einblenden
                        ClockHide= False
                        
                # Prüfung auf ungelesene E-Mails
                if CurrentMailCheckInterval > -1:
                  MailCheckInterval = MailCheckInterval - 1
                  print("--------------------------------------------------------------------------------------")
                  print("Textausgabe in Kommandozeile - Anzeige der Anzahl ungelesener E-Mails in "+str(MailCheckInterval)+" Minute(n)") # Anzeige auf Kommandozeile zu Kontrolle
                  print("--------------------------------------------------------------------------------------")
                  if MailCheckInterval == 0:
                      MailCheckInterval = CurrentMailCheckInterval + 1
                      if CheckMode1 == "on":
                         MailCount1 = UnreadMailCount(MailServername1, MailUserName1, MailPassword1)
                         MailText
                      else:
                         MailCount1 = -1 
                      if CheckMode2 == "on":
                         MailCount2 = UnreadMailCount(MailServername2, MailUserName2, MailPassword2)
                      else:
                         MailCount2 = -1  
                      if CheckMode3 == "on":
                         MailCount3 = UnreadMailCount(MailServername3, MailUserName3, MailPassword3)
                      else:
                         MailCount3 = -1
                         
                      if MailCount1 > 0 or MailCount2 > 0 or MailCount3 > 0:
                       MailText = "+++ Anzahl ungelesener E-Mail Nachrichten:  "   
                       if MailCount1 > -1:
                        MailText = MailText+MailAccountName1+" = "+str(MailCount1)
                       if MailCount2 > -1:
                        MailText = MailText+"     "+MailAccountName2+" = "+str(MailCount2)
                       if MailCount3 > -1:
                        MailText = MailText+"     "+MailAccountName3+" = "+str(MailCount3)
                       Uhr.ShowText(MailText+" +++") 
                      else:
                         print("")
                         print("------------------------------------------------------------------------------")
                         print("Textausgabe in Kommandozeile - Keine ungelesenen E-Mail Nachrichten vorhanden ") # Anzeige auf Kommandozeile zu Kontrolle
                         print("------------------------------------------------------------------------------")
                         print("")
                       # Uhr.ShowText("+++ Keine ungelesenen E-Mail Nachrichten vorhanden. +++") # (Optional)
                       
                # Check FritzBox auf Anzahl verpasste Anrufe (gestern und Heute)
                if CheckMissedFBCalls == "on": 
                  FBCheckInterval = FBCheckInterval - 1
                  print("--------------------------------------------------------------------------------------")
                  print("Textausgabe in Kommandozeile - Anzeige der Anzahl verpasster Anrufe in "+str(FBCheckInterval)+" Minute(n)") # Anzeige auf Kommandozeile zu Kontrolle
                  print("--------------------------------------------------------------------------------------")
                  if FBCheckInterval == 0:
                      FBCheckInterval = CurrentFBCheckInterval + 1
                      MissedCallCount = FritzBoxMissedCallCount(FritzBoxIP,FritzBoxPassword)
                      if MissedCallCount > 0:
                         Uhr.ShowText("+++ Anzahl verpasster Anrufe: "+str(MissedCallCount)+" +++")
                      else:
                         print("")
                         print("-----------------------------------------------------------------")
                         print("Textausgabe in Kommandozeile - Keine verpassten Anrufe vorhanden ") # Anzeige auf Kommandozeile zu Kontrolle
                         print("-----------------------------------------------------------------")
                         print("") 
                         # Uhr.ShowText("Keine verpassten Anrufe vorhanden") # (Optional)
                         
                # weitere Aktionen
                
             else:
               print("Textausgabe - *** Internetstatus: Offline *** ")  
               Uhr.ShowText("+++ Internetstatus: Offline +++")
            
            time.sleep(1)
    #except BaseException:#KeyboardInterrupt:
        #pass
        #GPIO.cleanup()  
        #sys.exit()
    
# +++ Feiertage +++   
#"""Bundesländer Deutschland"""
#            'Baden-Württemberg'='BW'
#            'Bayern'='BY'
#            'Berlin'='BE'
#            'Brandenburg'='BB'
#            'Bremen'='HB'
#            'Hamburg'='HH'
#            'Hessen'='HE'
#            'Mecklenburg-Vorpommern'='MV'
#            'Niedersachsen'='NI'
#            'Nordrhein-Westfalen'='NW'
#            'Rheinland-Pfalz'='RP'
#            'Saarland'='SL'
#            'Sachsen'='SN'
#            'Sachsen-Anhalt'='SA'
#            'Schleswig-Holstein'='SH'
#            'Thüringen'='TH'

#"""Bundesländer Oesterreich"""
#            'Burgenland'='B'
#            'Kärnten'='K'
#            'Niederösterreich'='N'
#            'Oberösterreich'='O'
#            'Land Salzburg'='S'
#            'Steiermark'='ST'
#            'Tirol'='T'
#            'Vorarlberg'='V'
#            'Wien'='W'

#"""Kantone Schweiz"""
#            'Kanton Zürich'='KZH'
#            'Kanton Bern'='KBE'
#            'Kanton Luzern'='KLU'
#            'Kanton Uri'='KUR'
#            'Kanton Schwyz'='KSZ'
#            'Kanton Obwalden'='KOW'
#            'Kanton Nidwalden'='KNW'
#            'Kanton Glaraus'='KGL'
#            'Kanton Zug'='KZG'
#            'Kanton Freiburg'='KFR'
#            'Kanton Solothurn'='KSO'
#            'Kanton Basel Stadt'='KBS'
#            'Kanton Basel Landschaft'='KBL'
#            'Kanton Schaffhausen'='KSH'
#            'Kanton Appenzell Ausserhoden'='KAR'
#            'Kanton Appenzell Innerhoden'='KAL'
#            'Kanton St.Gallen'='KSG'
#            'Kanton Graubünden'='KGR'
#            'Kanton Aargau'='KAG'
#            'Kanton Thurgau'='KTG'
#            'Kanton Tessin'='KTI'
#            'Kanton Waadt'='KVD'
#            'Kanton Wallis'='KVS'
#            'Kanton Neuenburg'='KNE'
#            'Kanton Genf'='KGE'
#            'Kanton Jura'='KJU'          
    
