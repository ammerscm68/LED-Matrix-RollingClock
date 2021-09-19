#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

import re
import time
from datetime import datetime

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

try:
    # create matrix device
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=90, blocks_arranged_in_reverse_order=True)
    device.contrast(10)
    print("Created device")
    
    CurrentTime = datetime.now()
    MinutesStr = CurrentTime.strftime('%M') # Minute
    HoursStr = CurrentTime.strftime('%-H') # Stunde
    # HoursStr = "6"
    # 0, 4, 10, 14, 20 = -2  
    
    # Scroll in
    for i in range(35,-1,-1):
          with canvas(device) as draw:
           if int(HoursStr) < 10:
             if int(HoursStr) == 0 or int(HoursStr) == 4:
               text(draw, (i+7, 0), HoursStr, fill="white", font=proportional(CP437_FONT))
             else:  
               text(draw, (i+8, 0), HoursStr, fill="white", font=proportional(CP437_FONT))
           else:
               if int(HoursStr) == 10 or int(HoursStr) == 14 or int(HoursStr) == 20:
                  text(draw, (i, 0), HoursStr, fill="white", font=proportional(CP437_FONT))
               else:  
                  text(draw, (i+1, 0), HoursStr, fill="white", font=proportional(CP437_FONT))
                  
                  
           text(draw, (i+15, 0), ":", fill="white", font=proportional(TINY_FONT))
           text(draw, (i+17, 0), MinutesStr, fill="white", font=proportional(CP437_FONT))
           time.sleep(0.04)
    
    #for i in range(-1,35,1):
        #with canvas(device) as draw:
           #text(draw, (i, 0), "10", fill="white", font=proportional(CP437_FONT))
           #text(draw, (i+15, 0), ":", fill="white", font=proportional(TINY_FONT))
           #text(draw, (i+17, 0), "00", fill="white", font=proportional(CP437_FONT))
           #time.sleep(0.04)
           
    time.sleep(5)         
              
    # Scroll out          
    for i in range(-1,-35,-1):
          with canvas(device) as draw:
           if int(HoursStr) < 10:
             if int(HoursStr) == 0 or int(HoursStr) == 4 or int(HoursStr) == 10 or int(HoursStr) == 14 or int(HoursStr) == 20:
               text(draw, (i+7, 0), HoursStr, fill="white", font=proportional(CP437_FONT))
             else:  
               text(draw, (i+8, 0), HoursStr, fill="white", font=proportional(CP437_FONT))
           else:
               text(draw, (i, 0), HoursStr, fill="white", font=proportional(CP437_FONT))
           text(draw, (i+15, 0), ":", fill="white", font=proportional(TINY_FONT))
           text(draw, (i+17, 0), MinutesStr, fill="white", font=proportional(CP437_FONT))
           time.sleep(0.04)
           
except KeyboardInterrupt:
        pass
