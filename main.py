'''Connects to a website and reads the HTML content of the website'''

#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in13_V4
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import requests
import time

logging.basicConfig(level=logging.DEBUG)

lines = []
fut_bold = ImageFont.truetype(os.path.join("Futura Std", 'FuturaStd-Bold.otf'), 18)
fut_book = ImageFont.truetype(os.path.join("Futura Std", 'FuturaStd-Book.otf'), 18)

# Specify encoding to avoid errors
encoding = 'utf-8'

url = 'http://aiary.stefanjanisch.net'

epd = epd2in13_V4.EPD()

epd.init()
epd.Clear(0xFF)


lines_old = lines

response = requests.get(url)
html = response.content.decode(encoding)

# Make a list of all lines including "<p><b>"
lines = html.split('\n')
lines = [line for line in lines if '<p><b>' in line]

# Split the lines at "</b><br>"
lines = lines[0].split('</b><br>')
# Delete <p>, <b>, </p>, </b> and <br> tags
lines = [line.replace('<p>', '').replace('<b>', '').replace('</p>', '').replace('</b>', '').replace('<br>', '') for line in lines]
# Delete leading and trailing whitespaces
lines = [line.strip() for line in lines]

# Check if lines has changed since last time
if lines != lines_old:
    epd.Clear(0xFF)
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)

    # Draw the lines
    for i, line in enumerate(lines):
        text_width, text_height = draw.textsize(line, font=fut_bold)
        x = (epd.width - text_width) // 2 + epd.width*0.5
        y = 10 + i * 20
        if i == 0:
            draw.text((x, y), line, font=fut_book, fill=0)
        else:
            draw.text((x, y), line, font=fut_bold, fill=0)

    epd.display(epd.getbuffer(image))
    time.sleep (10)
    
#    time.sleep(60)

    

