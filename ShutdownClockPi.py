#!/usr/bin/python
# shutdown/reboot Raspberry Pi mittels Taste

import RPi.GPIO as GPIO
import time, sys, syslog, os

# GPIO-Port, an dem die Taste gegen GND angeschlossen ist
# GPIO 5
PORT = 21 # Standard ist 5   GPIO Number --> not GPIO PIN

# Schwelle fuer ShutDown (in Sekunden), wird die Taste kuerzer
# gedruckt, erfolgt ein Reboot
T_SHUT = 2

# Entprellzeit fuer die Taste
T_PRELL = 0.05

# GPIO initialisieren, BMC-Pinnummer, Pullup-Widerstand
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PORT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Zeitdauer des Tastendrucks
duration = 0

# Interrupt-Routine fuer die Taste
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
      if elapsed >= T_SHUT:
        syslog.syslog('Shutdown: System halted');
        os.system("sudo pkill -SIGINT -f RollingClockTicker.py")
        time.sleep(3)
        os.system("sudo systemctl poweroff") 
      elif elapsed >= T_PRELL: 
        syslog.syslog('Shutdown: System rebooted');
        os.system("sudo pkill -SIGINT -f RollingClockTicker.py")
        time.sleep(3)
        os.system("sudo systemctl reboot")

# Interrupt fuer die Taste einschalten
GPIO.add_event_detect(PORT, GPIO.BOTH, callback=buttonISR)

syslog.syslog('Shutdown Script started');
print('Shutdown Script started');
while True:
  try:
    time.sleep(1)
  except BaseException:
    pass  
    syslog.syslog('Shutdown Script exception');
    sys.exit(0)

