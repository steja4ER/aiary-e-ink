import sys
import os
import logging

import time
from PIL import Image, ImageDraw, ImageFont
import requests

logging.basicConfig(level=logging.DEBUG)

fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Fonts')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd2in13_V4

# OPTIONS
centering = False
font_bold = ImageFont.truetype(os.path.join(fontdir, 'DejaVuSans-Bold.ttf'), 22)
font_std = ImageFont.truetype(os.path.join(fontdir, 'DejaVuSans.ttf'), 18)
encoding = 'utf-8'
url = 'http://aiary.stefanjanisch.net'

# FUNCTIONS
def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

# Function to automatically split text into multiple lines if it exceeds a certain width
def split_text_into_lines(text, font, max_width, draw):
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        # Check if adding the next word would exceed the max width
        test_line = f'{current_line} {word}' if current_line else word
        text_width, _ = get_text_dimensions(test_line, font=font)
        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)  # Add the last line
    return lines

epd = epd2in13_V4.EPD()

epd.init()
epd.Clear(0xFF)

lines = []
while True:

    old_lines = lines
    try:
        response = requests.get(url)
        html = response.content.decode(encoding)
    except Exception as e:
        logging.error(e)
        time.sleep(10)
        continue

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
    max_width = epd.width
    y = 10

    # Iterate over lines to apply different fonts and processing
    for i, line in enumerate(lines):
        font = font_bold if i == 0 else font_std
        processed_lines = split_text_into_lines(line, font, max_width, draw)

        for pline in processed_lines:
            text_width, text_height = get_text_dimensions(pline, font=font)
            if centering:
                x = (epd.width - text_width) // 2 + epd.width // 2
            else:
                x = 10
            draw.text((x, y), pline, font=font, fill=0)
            y += text_height + 5  # Adjust spacing between lines if necessary

    image = image.rotate(180)
    try:
        epd.display(epd.getbuffer(image))
    except Exception as e:
        logging.error(e)
        time.sleep(10)
        continue
