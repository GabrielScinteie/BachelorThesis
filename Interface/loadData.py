import json

colors = {}
microphoneOn = False
soundOn = True

def read_colors_from_file(filepath):
    global colors
    with open(filepath) as f:
        colors = json.load(f)


read_colors_from_file('colors.json')

