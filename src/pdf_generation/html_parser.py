import json
import random

from bs4 import BeautifulSoup

from pdf_generation import DataGenerator
from util.constants import *

"""
Validates a custom config file. 
TODO: add functionality
"""


def validate_html(html):
    pass
    # TODO: implement


def parse_html(html):
    pass


def fill_html(html):
    data_generator = DataGenerator()
    provided_types = data_generator.data_types
    soup = BeautifulSoup(html, 'html.parser')
    elems = soup.findAll()

    for elem in elems:
        if 'data-type' in elem.attrs:
            data_type = elem.attrs['data-type']
            try:
                if data_type == 'logo':
                    new_tag = soup.new_tag("img", src=provided_types[data_type](), style=f'height:{random.randint(80, 140)}px')
                    elem.append(new_tag)
                else:
                    output = provided_types[data_type]()
                    elem.string = output
            except KeyError:
                print(f'Data type {elem.attrs["data-type"]} is unknown! This field will not be filled.')

    with open(DEFAULT_TMP_PATH + 'invoice.html', 'w') as f:
        f.write(str(soup))


class HTMLFileFormatError(Exception):
    def __init__(self, message):
        super().__init__(message)
