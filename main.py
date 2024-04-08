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
import textwrap

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

# Function to automatically split text into multiple lines if it exceeds a certain width
def split_text_into_lines(text, font, max_width, draw):
    lines = textwrap.wrap(text, width=20)  # Adjust width according to your font and display size
    return lines

# Initialize drawing on the image
epd.init()
epd.Clear(0xFF)
image = Image.new('1', (epd.height, epd.width), 255)
draw = ImageDraw.Draw(image)

max_width = epd.width - 20  # Adjust padding if needed

# Use a sample text to calculate text height with the given font
_, text_height = draw.textsize("Sample", font=fut_bold)

processed_lines = []
for line in lines:
    processed_lines.extend(split_text_into_lines(line, fut_bold, max_width, draw))

# Calculate the total height of the text block to center it vertically
total_text_height = len(processed_lines) * (text_height + 5)  # Adjust spacing between lines if needed

# Calculate starting Y position to vertically center the text block
start_y = (epd.height - total_text_height) // 2

# Draw each line, centered
for i, line in enumerate(processed_lines):
    text_width, _ = draw.textsize(line, font=fut_bold)
    x = (epd.width - text_width) // 2  # Calculate X position to horizontally center the text
    y = start_y + i * (text_height + 5)  # Calculate Y position
    draw.text((x, y), line, font=fut_bold, fill=0)

# Display the image
epd.display(epd.getbuffer(image))
time.sleep(10)

