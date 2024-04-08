import sys
import os
import logging

import time
from PIL import Image, ImageDraw, ImageFont
import requests

logging.basicConfig(level=logging.DEBUG)

# Function to automatically split text into multiple lines if it exceeds a certain width
def split_text_into_lines(text, font, max_width, draw):
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        # Check if adding the next word would exceed the max width
        test_line = f'{current_line} {word}' if current_line else word
        text_width, _ = draw.textsize(test_line, font=font)
        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)  # Add the last line
    return lines

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd2in13_V4

fut_bold = ImageFont.truetype(os.path.join("Futura Std", 'FuturaStd-Bold.otf'), 18)
fut_book = ImageFont.truetype(os.path.join("Futura Std", 'FuturaStd-Medium.otf'), 18)

# Specify encoding to avoid errors
encoding = 'utf-8'

url = 'http://aiary.stefanjanisch.net'

epd = epd2in13_V4.EPD()

epd.init()
epd.Clear(0xFF)

lines = []
while True:
    old_lines = lines
    response = requests.get(url)
    html = response.content.decode(encoding)

    # Extract lines including "<p><b>" and process them
    lines = html.split('\n')
    lines = [line for line in lines if '<p><b>' in line]
    lines = lines[0].split('</b><br>')
    lines = [line.replace('<p>', '').replace('<b>', '').replace('</p>', '').replace('</b>', '').replace('<br>', '').strip().replace('"', '') for line in lines]

    if lines == old_lines:
        time.sleep(60)
        continue

    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    max_width = epd.width - 20
    y = 10

    # Iterate over lines to apply different fonts and processing
    for i, line in enumerate(lines):
        font = fut_bold if i == 0 else fut_book
        processed_lines = split_text_into_lines(line, font, max_width, draw)

        for pline in processed_lines:
            text_width, text_height = draw.textsize(pline, font=font)
            x = (epd.width - text_width) // 2 + epd.width // 2
            draw.text((x, y), pline, font=font, fill=0)
            y += text_height + 5  # Adjust spacing between lines if necessary

    epd.display(epd.getbuffer(image))
