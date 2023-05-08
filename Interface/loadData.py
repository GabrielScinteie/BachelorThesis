import json
import sys
import os

colors = {}
microphoneOn = False
soundOn = False

def read_colors_from_file(filepath):
    global colors
    with open(filepath) as f:
        colors = json.load(f)


read_colors_from_file('./Interface/colors.json')

