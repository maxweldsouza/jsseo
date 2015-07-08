import json
import os

try:
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    f = open(config_path, 'r')
    config_text = f.read()
except IOError:
    print 'Check whether config.json exists'
config = json.loads(config_text)
