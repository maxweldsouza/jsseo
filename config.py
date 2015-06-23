import json

try:
    f = open('config.json', 'r')
    config_text = f.read()
except IOError:
    print 'Check whether config.json exists'
config = json.loads(config_text)
