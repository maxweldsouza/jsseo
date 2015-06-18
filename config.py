import json

with open('config.json') as f:
    config_text = f.read()
config = json.loads(config_text)
