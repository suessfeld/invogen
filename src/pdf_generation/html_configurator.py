import json

from util.constants import *


"""
Validates a custom config file. 
TODO: add functionality
"""
def validate_config(config):
    print(config)
    if config is None:
        raise(ConfigFileFormatError("did not work"))


"""
Persists a custom config. File path is defined at constants.py.
"""
def save_config(data):

    try:
        with open(CUSTOM_CONFIG_FILE_PATH, 'w') as output_file:
            json.dump(data, output_file, indent=4)

    except FileNotFoundError:
        print(f"File not found: {CUSTOM_CONFIG_FILE_PATH}, this should not happen")
        return None


"""
Exception which gets thrown, when a provided config file is not the in the right format
or has missing fields.
"""
class ConfigFileFormatError(Exception):
    def __init__(self, message):
        super().__init__(message)
