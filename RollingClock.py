#!/usr/bin/env python3

# RollingClock by joe703 / https://www.youtube.com/channel/UChMi8gAr52_jZXIpr9WXYQQ
# Inspired by luma.led_matrix/examples/silly_clock.py by ttsiodras
# https://github.com/rm-hull/luma.led_matrix/blob/master/examples/silly_clock.py

import threading
import sys, signal
from gpiozero import CPUTemperature
import vlc  # pip3 install python-vlc
import Feiertage as bf
import time
import RPi.GPIO as GPIO
from datetime import date, datetime
from PIL import Image
from pathlib import Path
# Luma Komponenten importieren
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

# Zeitdauer des Tastendrucks für PushButton
duration = 0  # Variable Initialisieren

def signal_handler(signal, stackframe):
    Uhr.Hide()
    ClockHide= True
    ClockStop= True
    Uhr.close()
    print("Stop der Uhr angefordert")
    Uhr.join()
    print("Uhr gestoppt")
    sys.exit()

class RollingClock(threading.Thread):
   
    def __DrawNumber(self, draw, StringOld, StringNew, PosOld, PosNew, Iterator, DisplayPos):
        # Draws and animates Number - Iterator has to be increased from 0 (old String) to 8 (NewString)
       if DisplayPos == "top":  
        if Iterator > 8:
            Iterator = 8
        if Iterator < 8:
            text(draw, (PosOld, 0 - Iterator), StringOld, fill="white", font=proportional(CP437_FONT))
        if Iterator > 0:
            text(draw, (PosNew, 8 - Iterator), StringNew, fill="white", font=proportional(CP437_FONT))
       else: 
        if Iterator > 8:
            Iterator = 8
        if Iterator < 8:
            text(draw, (PosOld, 1 - Iterator), StringOld, fill="white", font=proportional(CP437_FONT))
        if Iterator > 0:
            text(draw, (PosNew, 9 - Iterator), StringNew, fill="white", font=proportional(CP437_FONT))   
           
    def __DrawSpecialText(self, draw, StringOld, StringNew, PosOld, PosNew, Iterator):
        # Draws and animates Number - Iterator has to be increased from 0 (old String) to 8 (NewString)
        if Iterator > 7:
            Iterator = 7
        if Iterator < 7:
            text(draw, (PosOld, 0 - Iterator), StringOld, fill="white", font=proportional(SINCLAIR_FONT))
        if Iterator > 0:
            text(draw, (PosNew, 7 - Iterator), StringNew, fill="white", font=proportional(SINCLAIR_FONT))      

    def __DrawColon(self, draw, StringOld, StringNew, Iterator, DisplayPos):
        # Draws and animates colon - Iterator has to be increased from 0 (old String) to 8 (NewString)
       if DisplayPos == "top": 
        if StringOld == ":":
            text(draw, (15, 0 - Iterator), ":", fill="white", font=proportional(TINY_FONT))
        if StringNew == ":":
            text(draw, (15, 8 - Iterator), ":", fill="white", font=proportional(TINY_FONT))
       else:
        if StringOld == ":":
            text(draw, (15, 1 - Iterator), ":", fill="white", font=proportional(TINY_FONT))
        if StringNew == ":":
            text(draw, (15, 9 - Iterator), ":", fill="white", font=proportional(TINY_FONT))   
            
    def __DrawIntroText(self, draw, StringOld, StringNew, PosOld, PosNew, Iterator):
        # Draws and animates Number - Iterator has to be increased from 0 (old String) to 8 (NewString)
        if Iterator > 8:
            Iterator = 8
        if Iterator < 8:
            text(draw, (PosOld, 0 - Iterator), StringOld, fill="white", font=proportional(CP437_FONT))
        if Iterator > 0: 
            text(draw, (PosNew, 7 - Iterator), StringNew, fill="white", font=proportional(CP437_FONT))

    def __GetHourPos(self, hours):
        # Returns position for hours with CP437_FONT
        if hours == 0 or hours == 4:
            return 7
        elif hours < 10:
            return 8
        elif hours == 10 or hours == 14 or hours == 20:
            return 0
        else:
            return 1

    def __init__(self):
        # Init Own Thread for Clock
        threading.Thread.__init__(self)
        # Init LED Matrix
        serial = spi(port=0, device=0, gpio=noop())
        self.device = max7219(serial, cascaded=4, block_orientation=90, blocks_arranged_in_reverse_order=True)
        self.device.contrast(5)
        self.__DisplayPosition="top"
        self.__ClockAlignment = 0 
        self.__PushbuttonEvent=""
        self.__ScrollInMode="V"
        self.__ScrollOutMode="V"

    def run(self):
        # Clock is running
        self.__RunClock = True
        self.__ShowClock = True
        self.__DisplayText= ""
        
        # Geist Bild laden wenn vorhanden
        GhostFile = Path("ghost.png")
        if GhostFile.is_file():
           self.__GhostFileExist = True
           GhostPic = Image.open(GhostFile)
           self.__GhostPix = GhostPic.load()
        else: 
           self.__GhostFileExist = False  
        
        # Toggle the second indicator every second
        toggle = False

        while self.__RunClock:
            # Init Time
            CurrentTime = datetime.now()
            MinutesStr = CurrentTime.strftime('%M')
            MinutesStrOld = MinutesStr
            HoursStr = CurrentTime.strftime('%-H')
            HoursStrOld = HoursStr
            HoursPos = self.__GetHourPos(CurrentTime.hour)
            HoursPosOld = HoursPos
            
            # Scroll in Clock 
            if self.__ScrollInMode == "V": # ScrollIn Vertical
                for i in range(0,8):
                    with canvas(self.device) as draw:
                        self.__DrawNumber(draw, "", HoursStr, HoursPos, HoursPos, i, self.__DisplayPosition)
                        self.__DrawColon(draw, "", ":", i, self.__DisplayPosition)
                        self.__DrawNumber(draw, "", MinutesStr, 17, 17, i, self.__DisplayPosition)
                    time.sleep(0.1)
            else:
               for i in range(35,-1,-1):
                  with canvas(self.device) as draw:
                   if int(HoursStr) < 10:
                     if int(HoursStr) == 0 or int(HoursStr) == 4:
                       text(draw, (i+7, self.__ClockAlignment), HoursStr, fill="white", font=proportional(CP437_FONT))
                     else:  
                       text(draw, (i+8, self.__ClockAlignment), HoursStr, fill="white", font=proportional(CP437_FONT))
                   else:
                       if int(HoursStr) == 10 or int(HoursStr) == 14 or int(HoursStr) == 20:
                          text(draw, (i, self.__ClockAlignment), HoursStr, fill="white", font=proportional(CP437_FONT))
                       else:  
                          text(draw, (i+1, self.__ClockAlignment), HoursStr, fill="white", font=proportional(CP437_FONT)) 
                   text(draw, (i+15, self.__ClockAlignment), ":", fill="white", font=proportional(TINY_FONT))
                   text(draw, (i+17, self.__ClockAlignment), MinutesStr, fill="white", font=proportional(CP437_FONT))
                   time.sleep(0.033) 

            while (self.__ShowClock==True and self.__DisplayText==""):
                # Get New Time
                CurrentTime = datetime.now()
                MinutesStr = CurrentTime.strftime('%M')
                HoursStr = CurrentTime.strftime('%-H')
                HoursPos = self.__GetHourPos(CurrentTime.hour)

                # Handle special cases for right alignemnt of hours in CP437_FONT
                HoursPos = self.__GetHourPos(CurrentTime.hour)
                if (MinutesStr != MinutesStrOld or HoursStr != HoursStrOld):
                    # Time changed
                    for i in range(0,9):
                        if i == 5:
                            # toggle colon
                            toggle = not toggle
                        if HoursStr != HoursStrOld:
                            # Animate Hours and Minutes
                            with canvas(self.device) as draw:
                                self.__DrawNumber(draw, HoursStrOld, HoursStr, HoursPosOld, HoursPos, i, self.__DisplayPosition)
                                self.__DrawColon(draw, ":" if toggle else " ", " ", 0, self.__DisplayPosition)
                                self.__DrawNumber(draw, MinutesStrOld, MinutesStr, 17, 17, i, self.__DisplayPosition)
                        elif MinutesStr[0] != MinutesStrOld[0]:
                            # Animate 2 digit Minute Update
                            with canvas(self.device) as draw:
                                self.__DrawNumber(draw, HoursStrOld, HoursStr, HoursPos, HoursPos, 0, self.__DisplayPosition)
                                self.__DrawColon(draw, ":" if toggle else " ", " ", 0, self.__DisplayPosition)
                                self.__DrawNumber(draw, MinutesStrOld, MinutesStr, 17, 17, i, self.__DisplayPosition)
                        else:
                            # Animate 1 digit Minute Update
                            with canvas(self.device) as draw:
                                self.__DrawNumber(draw, HoursStrOld, HoursStr, HoursPos, HoursPos, 0, self.__DisplayPosition)
                                self.__DrawColon(draw, ":" if toggle else " ", " ", 0, self.__DisplayPosition)
                                self.__DrawNumber(draw, MinutesStr[0],
                                                  MinutesStr[0], 17, 17, 0, self.__DisplayPosition)
                                # If we don't draw digit 1 we need to check it for the position
                                if MinutesStr[0] == "0" or MinutesStr[0] == "4":
                                    self.__DrawNumber(draw, MinutesStrOld[1], MinutesStr[1], 25, 25, i, self.__DisplayPosition)
                                else:
                                    self.__DrawNumber(draw, MinutesStrOld[1], MinutesStr[1], 24, 24, i, self.__DisplayPosition)
                        time.sleep(0.1)
                else:
                    # Redraw Time to toggle colon
                    with canvas(self.device) as draw:
                        self.__DrawNumber(draw, HoursStr, HoursStr, HoursPos, HoursPos, 0, self.__DisplayPosition)
                        self.__DrawColon(draw, ":" if toggle else " ", " ", 0, self.__DisplayPosition)
                        self.__DrawNumber(draw, MinutesStr, MinutesStr, 17, 17, 0, self.__DisplayPosition)
                    time.sleep(0.5)

                # Store Time
                MinutesStrOld = MinutesStr
                HoursStrOld = HoursStr
                HoursPosOld = HoursPos

                # toggle colon
                toggle = not toggle

            # Scroll out Clock
            if self.__ScrollOutMode == "V": # ScrollOut Vertical
                for i in range(0,9):
                    with canvas(self.device) as draw:
                        self.__DrawNumber(draw, HoursStr, "", HoursPos, HoursPos, i, self.__DisplayPosition)
                        self.__DrawColon(draw, ":", "", i, self.__DisplayPosition)
                        self.__DrawNumber(draw, MinutesStr, "", 17, 17, i, self.__DisplayPosition)
                    time.sleep(0.1)
            else: # ScrollOut horizontal
               for i in range(-1,-35,-1):
                  with canvas(self.device) as draw:
                   if int(HoursStr) < 10:
                     if int(HoursStr) == 0 or int(HoursStr) == 4:
                       text(draw, (i+7, self.__ClockAlignment), HoursStr, fill="white", font=proportional(CP437_FONT))
                     else:  
                       text(draw, (i+8, self.__ClockAlignment), HoursStr, fill="white", font=proportional(CP437_FONT))
                   else:
                       if int(HoursStr) == 10 or int(HoursStr) == 14 or int(HoursStr) == 20:
                          text(draw, (i, self.__ClockAlignment), HoursStr, fill="white", font=proportional(CP437_FONT))
                       else:  
                          text(draw, (i+1, self.__ClockAlignment), HoursStr, fill="white", font=proportional(CP437_FONT)) 
                   text(draw, (i+15, self.__ClockAlignment), ":", fill="white", font=proportional(TINY_FONT))
                   text(draw, (i+17, self.__ClockAlignment), MinutesStr, fill="white", font=proportional(CP437_FONT))
                   time.sleep(0.033) 

            # Wait and show text
            while self.__RunClock and ((self.__ShowClock==False) or (self.__DisplayText!="")):
                if self.__DisplayText!="":
                    show_message(self.device, self.__DisplayText, fill="white", font=proportional(CP437_FONT), scroll_delay=0.04)
                    self.__DisplayText=""
                time.sleep(0.5)
                
    def ClockScrollInMode(self,SMode):
            if SMode == 'H':
                self.__ScrollInMode = 'H'
            else:
                self.__ScrollInMode = 'V'
                
    def ClockScrollOutMode(self,SMode):
            if SMode == 'H':
                self.__ScrollOutMode = 'H'
            else:
                self.__ScrollOutMode = 'V'            
                
    def ClockDisplayPosition(self,CDPos):
            self.__DisplayPosition = CDPos
            # Clockposition bei Horizontal Scroll
            if self.__DisplayPosition == "top":
               self.__ClockAlignment = 0
            else:
               self.__ClockAlignment = 1
        
    def PushButtonAction(self,PORT,PushTime,PrellTime,PushButtonStatus):
        self.__GPIOPort = PORT
        self.__PUTime = PushTime
        self.__PRTime = PrellTime
        # GPIO initialisieren, BMC-Pinnummer, Pullup-Widerstand   
        if PushButtonStatus == "Active":
            print("--------------------------")
            print("PushButton-Status: : aktiv")
            print("--------------------------")
            print("")
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.__GPIOPort, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # Zeitdauer des Tastendrucks
            duration = 0
            
            def buttonISR(pin):
             global duration
             if not (GPIO.input(pin)):
              # Taste gedrueckt
              if duration == 0:
                duration = time.time()
             else:
                 # Taste losgelassen
                 if duration > 0:
                    elapsed = (time.time() - duration)
                    duration = 0
                    if elapsed >= self.__PUTime:
                      self.__PushbuttonEvent="long"
                      print("-------------------------------")
                      print("PushButton wurde lang gedrückt ")
                      print("-------------------------------")
                    elif elapsed >= self.__PRTime:
                      self.__PushbuttonEvent="short"
                      print("-------------------------------")
                      print("PushButton wurde kurz gedrückt ")
                      print("-------------------------------")
            # Interrupt fuer die Taste einschalten
            GPIO.add_event_detect(PORT, GPIO.BOTH, callback=buttonISR)
        else:
            self.__PushbuttonEvent = ""
            print("--------------------------------")
            print("PushButton-Status: : nicht aktiv")
            print("--------------------------------")
            print("")
            
    def PBEvent(self):
        if self.__PushbuttonEvent == "short":
            self.__PushbuttonEvent = ""
            PBE = "short"
            return PBE
        elif self.__PushbuttonEvent == "long":
             self.__PushbuttonEvent = "" 
             PBE = "long"
             return PBE
        elif self.__PushbuttonEvent == "":
             PBE = "wait"
             return PBE 
    
    def Show(self):
           if self.__ShowClock == False: 
              self.__ShowClock = True

    def Hide(self):
        if self.__ShowClock == True: 
           self.__ShowClock = False
        time.sleep(3)

    def ShowText(self, text):
        # Replace special characters, whch are not available in font
        chars = {'ö':'oe','ä':'ae','ü':'ue','Ö':'Oe','Ä':'Ae','Ü':'Ue','ß':'ss','–':'-',' ':' '}
        for char in chars:
            text = text.replace(char,chars[char])
        # Check if text can be displayed and request output if not busy
        if self.__DisplayText=="":
            self.__DisplayText = text
            print("Textausgabe angefordert: "+text)
            return True
        else:
            print("Textausgabe nicht moeglich: "+text)
            return False

    def close(self):
        self.__ShowClock = False
        self.__RunClock = False
        GPIO.cleanup()
    
    def ClockIntro(self,intro_text,TextPos):
    # Replace special characters, whch are not available in font
     try:
      if self.__ShowClock  == False:
        chars = {'ö':'oe','ä':'ae','ü':'ue','Ö':'Oe','Ä':'Ae','Ü':'Ue','ß':'ss','–':'-',' ':' '}
        for char in chars:
            intro_text = intro_text.replace(char,chars[char])
        if TextPos < 0:  
         show_message(self.device, intro_text, fill="white", font=proportional(CP437_FONT), scroll_delay=0.04)
         time.sleep(1) # kurz Warten ...
        else: 
         # Scroll the Text down
         for i in range(0,8): 
             with canvas(self.device) as draw:
              self.__DrawIntroText(draw, "", intro_text, 17, TextPos, i)
              time.sleep(0.1)
         time.sleep(2) # kurz Warten ...
         # Scroll the Text up
         for i in range(0,8): 
            with canvas(self.device) as draw:
             self.__DrawIntroText(draw, intro_text, "", TextPos, 17, i)
             time.sleep(0.1)
      else:
          print("")  # Leerzeile
          print("Intro nicht möglich !")
     except:
        chars = {'ö': 'oe', 'ä': 'ae', 'ü': 'ue', 'Ö': 'Oe', 'Ä': 'Ae', 'Ü': 'Ue', 'ß': 'ss', '–': '-', ' ': ' '}
        for char in chars:
            intro_text = intro_text.replace(char, chars[char])
        if TextPos < 0:
            show_message(self.device, intro_text, fill="white", font=proportional(CP437_FONT), scroll_delay=0.04)
            time.sleep(1)  # kurz Warten ...
        else:
            # Scroll the Text down
            for i in range(0, 8):
                with canvas(self.device) as draw:
                    self.__DrawIntroText(draw, "", intro_text, 17, TextPos, i)
                    time.sleep(0.1)
            time.sleep(2)  # kurz Warten ...
            # Scroll the Text up
            for i in range(0, 8):
                with canvas(self.device) as draw:
                    self.__DrawIntroText(draw, intro_text, "", TextPos, 17, i)
                    time.sleep(0.1)
                    
    def CheckHideClock(self): # Check ob Uhr noch läuft wenn Ausgeblendet
      if (self.__ShowClock==False and self.__DisplayText==""):
        print("Textausgabe angefordert: Doppelpunkt")  
        with canvas(self.device) as draw:
            text(draw, (16, 0), ":", fill="white", font=proportional(TINY_FONT))
            time.sleep(0.1)
        time.sleep(5)
        with canvas(self.device) as draw:
            #self.__DrawColon(draw, ":","",0)
            text(draw, (16, 0), "", fill="white", font=proportional(TINY_FONT))
            time.sleep(0.1)   
      else:
          print("Textausgabe nicht moeglich: Doppelpunkt")
          
    def SpecialText(self,special_text,TextPos):
     try:
       # Replace special characters, whch are not available in font
       chars = {'ö':'oe','ä':'ae','ü':'ue','Ö':'Oe','Ä':'Ae','Ü':'Ue','ß':'ss','–':'-',' ':' '}
       for char in chars:
            special_text = special_text.replace(char,chars[char])    
       if (self.__ShowClock==False and self.__DisplayText==""):
         print("Textausgabe angefordert: "+special_text)
         # with excess length scroll horizontal   
         if TextPos < 0: # CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT
          if TextPos == -9:
            show_message(self.device, special_text, fill="white", font=proportional(CP437_FONT), scroll_delay=0.04) # für z.Bsp. Datum
          else:
            show_message(self.device, special_text, fill="white", font=proportional(SINCLAIR_FONT), scroll_delay=0.04)
          time.sleep(1) # kurz Warten ...
         else: 
         # Scroll the Text down
          for i in range(0,8): 
             with canvas(self.device) as draw:
              self.__DrawSpecialText(draw, "", special_text, 17, TextPos, i)
              time.sleep(0.1)
          time.sleep(1.5) # kurz Warten ...
          # Scroll the Text up
          for i in range(0,8): 
            with canvas(self.device) as draw:
             self.__DrawSpecialText(draw, special_text, "", TextPos, 17, i)
             time.sleep(0.1)   
       else:
          print("Textausgabe nicht moeglich: "+special_text)
          
     except BaseException:
         print("Textausgabe nicht moeglich ! ")
         pass
        
    def PlayHourSound(self,SFile,Volume,Mode):
        try:   
          if Mode == "on":  
            SoundFile = Path(SFile)
            if SoundFile.is_file():
               # VLC Instanz und MediaPlayer anlegen
               instance = vlc.Instance()
               player = instance.media_player_new()
               player.audio_set_volume(Volume) # Lautstärke
               # Media setzen
               media = instance.media_new(SoundFile)
               player.set_media(media)
               # Equalizer erstellen
               equalizer = vlc.AudioEqualizer()
               # Mehrere Frequenzbänder anpassen (Beispiel)
               equalizer.set_amp_at_index(0, 10)  # 60 Hz  +5 dB - Min/Max: -20 /+20
               equalizer.set_amp_at_index(1, 10)  # 170 Hz +3 dB - Min/Max: -20 /+20
               equalizer.set_amp_at_index(2, -10) # 310 Hz -2 dB - Min/Max: -20 /+20
               equalizer.set_amp_at_index(3, -10) # 600 Hz -2 dB - Min/Max: -20 /+20
               equalizer.set_amp_at_index(4, -10) # 1 kHz -2 dB  - Min/Max: -20 /+20
               equalizer.set_amp_at_index(5, -10) # 3 kHz -2 dB  - Min/Max: -20 /+20
               equalizer.set_amp_at_index(6, -10) # 6 kHz -2 dB  - Min/Max: -20 /+20
               equalizer.set_amp_at_index(7, -10) # 12 kHz -2 dB - Min/Max: -20 /+20
               equalizer.set_amp_at_index(8, -10) # 14 kHz -2 dB - Min/Max: -20 /+20
               equalizer.set_amp_at_index(9, 20) # 16 kHz -2 dB  - Min/Max: -20 /+20
               # Equalizer auf den Player anwenden
               player.set_equalizer(equalizer)
               # Wiedergabe starten
               player.play()
               time.sleep(5) # 5 sekunden bis zur nächsten Ausgabe warten
               # Wiedergabe stoppen
               player.stop() 
               return True
            else: 
               return False
          else:
               return False
        except:
               return False
        
    def CountDown(self,EYear, EMonth, EDay, EventText):
      try:
        EDate = datetime(EYear, EMonth, EDay, 0, 0, 0) 
        difference = EDate - datetime.now()
        count_hours, rem = divmod(difference.seconds, 3600)
        count_minutes, count_seconds = divmod(rem, 60)
        if difference.days >= 0:
           if difference.days == 1:
              ViewDay = "Tag"
           else:
              ViewDay = "Tage"
           if count_hours == 1:
              ViewHour = "Stunde"
           else:
              ViewHour = "Stunden"
           if count_minutes == 1:
              ViewMinute = "Minute"
           else:
              ViewMinute = "Minuten"      
              
           return("Noch "
                  + str(difference.days) + " "+ViewDay+" "
                  + str(count_hours) + " "+ViewHour+" "
                  + str(count_minutes) + " "+ViewMinute+" "
                  + "bis "+EventText)
        else:
            return "-1"
      except:
            return "Fail"
      
    def DrawGhost(self,Mode):
         if (self.__ShowClock==False and self.__DisplayText==""):
                if Mode == "on" and self.__GhostFileExist == True:  
                  for l in range(-16,50):
                    with canvas(self.device) as draw:
                      for y in range(8):
                        for x in range(8):
                          if self.__GhostPix[x,y] == (0,0,0):
                            draw.point((l+x,y), fill="white")
                    time.sleep(0.045) 
                  for l in range(50,-16,-1):
                     with canvas(self.device) as draw:
                        for y in range(8):
                          for x in range(8):
                            if self.__GhostPix[x,y] == (0,0,0):
                               draw.point((l+x,y), fill="white")
                     time.sleep(0.045)
                else:
                  print("-----------------------------")  
                  print("Geist - Anzeige deaktiviert !")
                  print("-----------------------------")
         else:
            print("-----------------------------------------")  
            print("Geist kann nicht nicht angezeigt werden !")
            print("-----------------------------------------")          
        
def HolidayText(country_code):
        hdj = datetime.now().strftime('%Y')
        hdd = datetime.now().strftime('%Y-%m-%d')
        hl  = bf.Holidays(hdj, country_code)
        holidays = hl.get_holiday_list()
        hdt = ""
        for h in holidays:
            # print(h[0],h[1]) # Ausgabe Liste aller Feiertage zum Testen
            if hdd == h[0].strftime('%Y-%m-%d'):
               hdt = h[1]
               # print("FT: "+hdt) 
        return hdt
    
def Measure_CPU_Temp():
    cpu = CPUTemperature() # CPU-Temperatur
    return int(cpu.temperature)    
    
def time_in_range(start, end, x):
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

if __name__ == "__main__":
    Wochentag=["Sonntag ", "Montag ", "Dienstag ", "Mittwoch ", "Donnerstag ", "Freitag ", "Samstag "]
    ClockHide = False
    DayCounter = 0
    PlausiCheck = 0
    CDEventViewCounter = 0
    
    # ******************************************************************************************************
    # ************** Variablen mit den gewünschten Werten vorbelegen ***************************************
    # ******************************************************************************************************
    
    # Ausrichtung der Uhrzeitanzeige
    #----------------------------------------------------------------------------------------------------
    ClockDisplayPosition = "top" #  top = oben  -  bottom = unten  (ungleich top oder bottom = unten)
    #----------------------------------------------------------------------------------------------------
    
    # ScrollIn und ScrollOut der Anzeige festlegen
    ClockScrollIn = "H" # V = Vertical  H = Horizontal   Default ist "V"
    ClockScrollOut = "H" # V = Vertical  H = Horizontal   Default ist "V"
    
    # PushButton-Setup
    PushButtonGPIOPort= 21 # Pin-Nummer (nicht GPIO-Nummer) auf GPIO-Leiste gegen Ground
    LongPushTime= 1 # Länge in Sekunden bis Event
    PushButtonDePrell = 0.03 # Entprellzeit für den PushButton (sollte standardmäßig so bleiben) Default = 0.03
    PushButtonStatus = "Active" # PushButton aktivieren oder deaktivieren
    # wenn PushButton nicht vorhanden "NotActive" = deaktiviert  -  Wenn PushButton vorhanden "Active" = aktiviert)
    
    # weitere Einstellungen 
    HideClockTimeHour = "23" # ab hier Uhr ausblenden (Stunde Uhrzeit --> ohne führende Null)   -->  -1  = Uhr nicht Ausblenden
    ShowClockTimeHour = "6" # ab hier Uhr wieder anzeigen (Stunde Uhrzeit --> ohne führende Null)
    
    # Anzeigehelligkeit 
    DisplayContrastHigh = 16 # Voller Displaycontrast
    DisplayContrastLow = 5 # geringer Displaycontrast
    
    # Geburtstagsgruß Datum
    DateOfBirth = "27.04"
    
    HDBL = "TH" # Feiertags Bundesland --> keine Angabe gibt nur die bundeseinheitlichen Feiertage aus (Bundesländer siehe unten) 
    
    AlertMaxCPUTemp = 70 # Alarm-Anzeige bei Temperatur von X Grad oder höher der CPU
    
    NewsTrigger = 10 # Nach X sekunden (von 1 Minute) - Prüfen auf vorhandene News
    
    DateViewCount = 3 # Datum und Grüße nur alle X Minuten anzeigen
    
    GhostMode = "on" # on = Geist wird um Mitternacht angezeigt off = Geist wird nicht um Mitternacht angezeigt
    
    SoundMode = "on"  # on = beim Start und jede volle Stunde wird ein Sound ausgegeben (nur wenn Uhrzeit eingeblendet) off = kein Sound
    StartSoundFile= "sound1.mp3" # Sound-Datei beim Start der Uhr
    HourSoundFile= "sound3.mp3" # Sound-Datei zu jeder vollen Stunde
    ShowClockSoundFile= "sound4.mp3" # Sound wenn die Uhr wieder eingeblendet wird
    AlarmClockSoundFile= "sound2.mp3" # Sound-Datei für Wecker
    AlarmClockCount = -1 # Wie oft soll der Sound für den Wecker ausgegeben werden (-1 = Wecker deaktiviert)
    AlarmClockTime = "06:00" # Wecker Uhrzeit (mit führender Null bei Uhrzeiten zischen 0 und 9 Uhr)
    SoundVolume = 200    # Sound-Lautstärke anpassen (Standard = 100)
    HourSoundFrom = 5 # Stunde ab wann der Sound jede volle Stunde abgespielt werden soll (Wenn Uhrzeit eingeblendet)
    HourSoundTo = 21 # Stunde bis wann der Sound jede volle Stunde abgespielt werden soll (Wenn Uhrzeit eingeblendet)
    
    # CountDown Daten
    CDEventYear = 2033 # Jahr des Events
    CDEventMonth = 3 # Monat des Events
    CDEventDay = 17 # Tag des Events
    CDEventText = "25 Jahre" # Text für den CountDown
    CDEventViewCount = -1 # alle X Minuten wird der CountDown-Zähler angezeigt (-1 = CountDown deaktiviert)
    
    # ********************************************************************************************************
    # ********************************************************************************************************
    
    # ---- Plausi-Check ----
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
    except:
        HideClockTimeHour = "-1" # Default Ausgeschaltet
        ShowClockTimeHour = "6"  # Default
        NewsTrigger = 15 # Default
        PlausiCheck = PlausiCheck + 1   
    
    # Main
    Uhr = RollingClock() # Uhr Initialisieren
    ClockStop = False
    
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
    
    StartTimeHour = int(datetime.now().strftime('%H'))
    if StartTimeHour >= 12 and StartTimeHour < 17:
        Uhr.device.contrast(DisplayContrastHigh) # Displayhelligkeit Voreinstellen
        print("------------------")
        print("Displaystart: Hell")
        print("------------------")
    else:
        Uhr.device.contrast(DisplayContrastLow) # Displayhelligkeit Voreinstellen
        print("--------------------")
        print("Displaystart: Dunkel")
        print("--------------------")
    
    THoliDay = HolidayText(HDBL) # Ermitteln ob Feiertag beim Programmstart
    if THoliDay != "":
        print("")
        print("----------------------------------------")
        print("Heute ist Feiertag: "+THoliDay)
        print("----------------------------------------")
    
    print("")
    print("-----------------------")
    print("CPU-Temperatur: "+str(CPUTemperature)+" Grad")
    print("-----------------------")
    print("")
    
    if ClockDisplayPosition == "top":
        print("------------------------------------")
        print("Ausrichtung der Uhrzeitanzeige: oben")
        print("------------------------------------")
    else:
        print("-------------------------------------")
        print("Ausrichtung der Uhrzeitanzeige: unten")
        print("-------------------------------------")
        
    if HideClockTimeHour != "-1":
       print("")
       print("--------------------------------------------------------") 
       print("Einblenden der Uhrzeit um: "+ShowClockTimeHour+":00 Uhr (wenn ausgeblendet)")
       print("--------------------------------------------------------") 
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
    
    Uhr.start() # Uhr starten
    
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
    print("");
    
    # Geist mal Testen
    #Uhr.Hide()
    #for i in range(5):
     #Uhr.DrawGhost(GhostMode) # Geist anzeigen
     #time.sleep(1)
    #Uhr.Show()
    
    # Sound Test
    #for i in range(5):
     #Uhr.PlayHourSound("sound3.mp3", SoundVolume, SoundMode)
    
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
            print("\n")
            GN = [22,23,0,1,2,3,4] # Nacht
            if StartTimeHour in GN:
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
    
    try:
     signal.signal(signal.SIGINT, signal_handler)
     while not ClockStop:
            datum = datetime.now().strftime('%d.%m.%Y')
            SpecialDat= datetime.now().strftime('%d.%m')
            CheckTime = datetime.now().strftime('%M:%S')
            FullTime= datetime.now().strftime('%H:%M:%S')
            RepeatTime= datetime.now().strftime('%M')
            TimeHour = int(datetime.now().strftime('%H'))
            tag = datetime.now().strftime('%w')
            sekunden = datetime.now().strftime('%S')
            
            if PushButtonStatus == "Active":
                PushButtonEvent = Uhr.PBEvent() # Abfrage ob PushButton gedrückt wurde
                # Aktion wenn Taste von "PushButton" gedrückt wurde
                if PushButtonEvent == "long":
                   print("-----------------------------------------")
                   print("PushButton-Longsequenz wird ausgeführt...")
                   print("-----------------------------------------")
                   ClockHide= True # Uhr ausblenden
                   Uhr.Hide()
                if PushButtonEvent == "short":
                   print("------------------------------------------")
                   print("PushButton-Shortsequenz wird ausgeführt...")
                   print("------------------------------------------")
                   ClockHide= False # Uhr einblenden
                   Uhr.Show()
            
            if FullTime == "12:00:"+SecondTrigger: # Display Helligkeit auf "volle Leuchtstärke"
                Uhr.device.contrast(16)
            
            if FullTime == "16:00:"+SecondTrigger: # Display Helligkeit veringern
                Uhr.device.contrast(5)
                
            if SpecialDat != "31.12" and ClockHide == False and HideClockTimeHour != -1: # Silvester oder bei TimeHideClockHour = -1 die Uhr nicht abschalten 
              if FullTime == HideClockTimeHour +":00:"+SecondTrigger: # Display abschalten
                   ClockHide= True
                   Uhr.Hide() # Uhr Ausblenden
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
                 if FullTime == ShowClockTimeHour +":00:"+SecondTrigger: # Display einschalten
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
             
            if FullTime == "00:00:"+SecondTrigger: # Prüfen ob neuer Tag ein Feiertag ist
               THoliDay = HolidayText(HDBL)
               
            if CheckTime == "00:00" and ClockHide == True: # jede Stunde kurz Melden wenn Clock Hide
             if TimeHour != 0: # Mitternacht einen Geist anzeigen
                print("--------------------------------------------") 
                print("Displayausgabe - Doppelpunkt  (als Zeichen) ")
                print("--------------------------------------------") 
                Uhr.CheckHideClock()
             else:
                print("-----------------------------------------") 
                print("Displayausgabe- Ein Geist um Mitternacht ")
                print("-----------------------------------------")
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
                  
            if sekunden == str(NewsTrigger) and ClockHide == False: # Wenn Uhrzeit Eingeblendet
                
             # 3 Leerzeilen in Kommandozeile einfügen
             print("\n")
             print("Textausgabe in Kommandozeile - Neuer Durchlauf ... ("+FullTime+" Uhr)")
             print("\n")
             
             #Uhr.ShowText("+++ Das ist ein Test der LED Matrix Uhr +++")
                
             CPU_Temp = Measure_CPU_Temp()
             if CPU_Temp > AlertMaxCPUTemp:
                Uhr.ShowText(" +++ Achtung !!!  CPU-Temperatur zu hoch ("+str(CPU_Temp)+" Grad) +++") # CPU Temperatur Alarm
                
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
                    Uhr.ShowText(CountDownTextOut) # CountDown jetzt ausgeben
                 else:
                    print("-------------------------------------------------------------")
                    print("Textausgabe in Kommandozeile - Der CountDown ist abgelaufen !")
                    print("-------------------------------------------------------------") 
                    
            # Datum mit verschiedenen Grüßen
             DayCounter= DayCounter + 1
             if DayCounter == DateViewCount: # Default nur alle 3 Minuten anzeigen
                DayCounter = 0  
                if SpecialDat == DateOfBirth:
                    Uhr.Hide() # Uhr Ausblenden
                    Uhr.SpecialText(Wochentag[int(tag)] + datum,-9)
                    Uhr.SpecialText("Alles",3)
                    Uhr.SpecialText("gute",5)
                    Uhr.SpecialText("zum",8)
                    Uhr.SpecialText("Geburtstag",-1)
                    Uhr.Show() # Uhr Einblenden
                    
                elif SpecialDat == "31.12":
                    Uhr.Hide() # Uhr Ausblenden
                    Uhr.SpecialText(Wochentag[int(tag)] + datum,-9)
                    Uhr.SpecialText("Guten",2)
                    Uhr.SpecialText("Rutsch",-1)
                    Uhr.SpecialText("ins",10)
                    Uhr.SpecialText("neue",5)
                    Uhr.SpecialText("Jahr",5)
                    
                elif SpecialDat == "01.01":
                    Uhr.Hide() # Uhr Ausblenden
                    Uhr.SpecialText(Wochentag[int(tag)] + datum,-9)
                    Uhr.SpecialText("Alles",3)
                    Uhr.SpecialText("gute",5)
                    Uhr.SpecialText("im",12)
                    Uhr.SpecialText("neuen",2)
                    Uhr.SpecialText("Jahr",5)
                    Uhr.SpecialText(datetime.now().strftime('%Y'),3)
                    Uhr.Show() # Uhr Einblenden
                    
                elif SpecialDat == "01.04":
                    Uhr.Hide() # Uhr Ausblenden
                    Uhr.SpecialText(Wochentag[int(tag)] + datum,-9)
                    Uhr.SpecialText("April",4)
                    Uhr.SpecialText("April",4)
                    Uhr.Show() # Uhr Einblenden
                    
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

            time.sleep(1)
    except BaseException: #KeyboardInterrupt: 
      pass
      GPIO.cleanup()  
      sys.exit()
    
    
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
