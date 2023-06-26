import json

colors = {}
soundOn = False


def read_colors_from_file(filepath):
    global colors
    with open(filepath) as f:
        colors = json.load(f)


read_colors_from_file('GraphicalUserInterface/colors.json')


def read_args(filename='args'):
    args_dictionary = {}

    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().split(' : ')
            try:
                args_dictionary[key] = int(value)
            except:
                args_dictionary[key] = float(value)

    return args_dictionary


