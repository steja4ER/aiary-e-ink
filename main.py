#!/home/pi/aiary-e-ink/venv/bin/python

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
font_std_name = 'DejaVuSans.ttf'
font_bold_name = 'DejaVuSans-Bold.ttf'
font_bold_size = 22
font_std_size = 18
encoding = 'utf-8'
url = 'http://aiary.stefanjanisch.net'

epd_width = 250
epd_height = 122

# FUNCTIONS
def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

# Function to automatically split text into multiple lines if it exceeds a certain width
def split_text_into_lines(text, font, max_width, draw):
    # Split the text by space to get words, then further split each word by hyphen if necessary,
    # treating the hyphen as a separate word for potential line breaking.
    words = []
    for word in text.split(' '):
        subwords = word.split('-')
        for i, subword in enumerate(subwords[:-1]):  # Don't process the last one the same way because it doesn't end in a hyphen
            words.append(subword)
            words.append('-')  # Treat hyphen as a separate word for potential line breaking
        words.append(subwords[-1])

    lines = []
    current_line = ''
    for word in words:
        if word == '-':
            test_line = f"{current_line}{word}"  # Don't add a space before hyphen
        else:
            test_line = f'{current_line} {word}' if current_line else word
        text_width, _ = get_text_dimensions(test_line.strip(), font=font)  # Use strip to remove leading/trailing spaces
        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word if word != '-' else ''  # Start new line; if word is a hyphen, start with an empty line
    if current_line:  # Add the last line if it's not empty
        lines.append(current_line)
    lines = [line.strip() for line in lines if line]  # Remove leading/trailing spaces and empty strings
    return lines


epd = epd2in13_V4.EPD()

epd.init()
epd.Clear(0xFF)


# class epd:
#     width = 250
#     height = 122

#     @staticmethod
#     def display(image):
#         print(image)

#     @staticmethod
#     def getbuffer(image):
#         return image
    
        
got_data = False

while not got_data:
    try:
        response = requests.get(url)
        html = response.content.decode(encoding)
        got_data = True
    except Exception as e:
        logging.error(e)
        time.sleep(10)
        continue

# Extract lines including "<p><b>" and process them
lines = html.split('\n')
lines = [line for line in lines if '<p><b>' in line]
lines = lines[0].split('</b><br>')
lines = [line.replace('<p>', '').replace('<b>', '').replace('</p>', '').replace('</b>', '').replace('<br>', '').strip().replace('"', '') for line in lines]


font_std_size_current = font_std_size
font_bold_size_current = font_bold_size
fits = False

while not fits:
    total_text_height = 0
    max_line_width = 0
    line_spacing = 5

    if centering:
        max_width = epd_width
    else:
        max_width = epd_width - 20

    font_bold = ImageFont.truetype(os.path.join(fontdir, font_bold_name), font_bold_size_current)
    font_std = ImageFont.truetype(os.path.join(fontdir, font_std_name), font_std_size_current)

    # Calculate the total height of the text block and check if it fits
    for i, line in enumerate(lines):
        font = font_bold if i == 0 else font_std
        temp_image = Image.new('1', (epd.height, epd.width), 255)
        temp_draw = ImageDraw.Draw(temp_image)
        processed_lines = split_text_into_lines(line, font, max_width, temp_draw)
        for j, pline in enumerate(processed_lines):
            _, text_height = get_text_dimensions(pline, font)
            total_text_height += text_height + line_spacing
            if i == 0 and j == 0:
                total_text_height -= 5
        total_text_height += line_spacing  # Add spacing between lines

    total_text_height -= line_spacing  # Adjust because there's no spacing after the last line

    # Check if text is outside the screen and adjust font size if necessary
    if total_text_height > epd_height:
        font_std_size_current -= 1
        font_bold_size_current -= 1
        if font_std_size_current < 10 or font_bold_size_current < 10:  # Prevent fonts from becoming too small
            logging.error("Text too large and font size too small. Cannot fit text.")
            break
    else:
        fits = True

# After determining the correct font size, calculate start_y for vertical centering
start_y = max((epd_height - total_text_height) // 2, 0)

# Draw the image with centered text
image = Image.new('1', (epd.height, epd.width), 255)
draw = ImageDraw.Draw(image)
y = start_y

for i, line in enumerate(lines):
    font = font_bold if i == 0 else font_std
    processed_lines = split_text_into_lines(line, font, max_width, draw)

    for j,pline in enumerate(processed_lines):
        text_width, text_height = get_text_dimensions(pline, font)
        if centering:
            x = (epd_width - text_width) // 2  # Center horizontally
        else:
            x = 10
        draw.text((x, y), pline, font=font, fill=0)
        y += text_height + line_spacing
        if i == 0 and j == 0:
            y -= 5
    y += line_spacing


# Display the image
image = image.rotate(180)
displayed_image = False
while not displayed_image: 
    try:
        epd.display(epd.getbuffer(image))
        displayed_image = True
    except Exception as e:
        logging.error(e)
        time.sleep(10)
        continue