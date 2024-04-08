'''Connects to a website and reads the HTML content of the website'''

#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import logging
import epd2in13_V4
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import requests

logging.basicConfig(level=logging.DEBUG)




# Specifay encoding to avoid errors
encoding = 'utf-8'

url = 'http://aiary.stefanjanisch.net'
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

print(lines)