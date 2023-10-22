import random

from bs4 import BeautifulSoup

from pdf_generation import DataGenerator
from pdf_generation.Annotation import Annotation, DataObject
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


# TODO: Implement information extraction for annotation.
def fill_html(html, annotation_object: Annotation):
    data_generator = DataGenerator()
    provided_types = data_generator.data_types
    soup = BeautifulSoup(html, 'html.parser')
    elems = soup.findAll()

    for elem in elems:
        if 'data-type' in elem.attrs:
            data_type = elem.attrs['data-type']
            try:

                if data_type == 'logo':
                    elem['src'] = provided_types[data_type]()
                    elem['style'] = f'height:{random.randint(80, 140)}px'

                elif data_type == 'address':
                    address = provided_types[data_type]()

                    street_div = soup.new_tag("div")
                    street_span = create_tag(soup, "span", str(elem["id"]) + "_street", address.street)
                    number_span = create_tag(soup, "span", str(elem["id"]) + "_building_number", address.building_number)
                    street_div.append(street_span)
                    street_div.append(" ")
                    street_div.append(number_span)

                    city_div = soup.new_tag("div")
                    city_span = create_tag(soup, "span", str(elem["id"]) + "_city", address.city)
                    postal_span = create_tag(soup, "span", str(elem["id"]) + "_postal_code", address.postal_code)
                    city_div.append(city_span)
                    city_div.append(", ")
                    city_div.append(postal_span)

                    country_div = create_tag(soup, "div", str(elem["id"]) + "_country", address.country)
                    elem.append(street_div)
                    elem.append(city_div)
                    elem.append(country_div)

                else:
                    output = provided_types[data_type]()
                    elem.string = output

            except KeyError:
                print(f'Data type {elem.attrs["data-type"]} is unknown! This field will not be filled.')

    with open(DEFAULT_TMP_PATH + 'invoice.html', 'w', encoding="utf-8") as f:
        f.write(str(soup))


def create_tag(soup, tag, tag_id, content):
    new_tag = soup.new_tag(tag, id=tag_id)
    new_tag.string = content
    return new_tag

class HTMLFileFormatError(Exception):
    def __init__(self, message):
        super().__init__(message)
