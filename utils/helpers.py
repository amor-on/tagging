# utils/helpers.py
import json

def load_labels_info(path):
    with open(path, 'r') as file:
        return json.load(file)
