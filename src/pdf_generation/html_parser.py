import json

from util.constants import *


"""
Validates a custom config file. 
TODO: add functionality
"""
def validate_html(html):
    pass
    #TODO: implement

def parse_html(html):
    pass

class HTMLFileFormatError(Exception):
    def __init__(self, message):
        super().__init__(message)
