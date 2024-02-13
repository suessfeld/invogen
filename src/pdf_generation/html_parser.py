import json
import logging
import random
import string

from bs4 import BeautifulSoup

from pdf_generation import DataGenerator
from pdf_generation.Annotation import Annotation, DataObject
from util.constants import *

def fill_html(html):
    data_generator = DataGenerator()
    provided_types = data_generator.data_types
    soup = BeautifulSoup(html, 'html.parser')
    elems = soup.findAll()

    # fonts:
    set_font(soup)

    for elem in elems:
        if 'data-type' in elem.attrs:
            data_type = elem.attrs['data-type']
            try:

                if data_type == 'logo':
                    elem['src'] = provided_types[data_type]()
                    elem['style'] = f'height:{random.randint(20, 60)}px'

                elif data_type == 'custom':
                    elem.string = provided_types[data_type](elem['data-list'])

                elif data_type == 'address':
                    address = provided_types[data_type]()

                    street_div = soup.new_tag("div")
                    street_span = create_tag(soup, "span", str(elem["id"]) + "_street", address.street)
                    number_span = create_tag(soup, "span", str(elem["id"]) + "_building_number",
                                             address.building_number)
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

                elif data_type == 'item_list':

                    assert (elem.name == "table")

                    config = json.loads(elem['data-config'])

                    # validate options
                    viable_options = {'width', 'minBorderSpacing', 'maxBorderSpacing', 'minFontSize', 'maxFontSize',
                                      'minElems', 'maxElems'}
                    config_keys = set(config.keys())
                    extra_keys = config_keys - viable_options
                    if extra_keys:
                        logging.error(f"Table has invalid options: {extra_keys}")
                        continue

                    items = provided_types[data_type](config['minElems'], config['maxElems'])

                    first_row = soup.new_tag("tr")
                    first_row.append(create_tag(soup, "th", f'{str(elem["id"])}_header_name', 'Product'))
                    first_row.append(create_tag(soup, "th", f'{str(elem["id"])}_header_quantity', 'Quantity'))
                    first_row.append(create_tag(soup, "th", f'{str(elem["id"])}_header_price', 'Price'))
                    elem.append(first_row)

                    count = 1
                    for item in items[:-1]:
                        row = soup.new_tag("tr")
                        row.append(create_tag(soup, "td", f'{str(elem["id"])}_item_{count}_name', item.name))
                        row.append(
                            create_tag(soup, "td", f'{str(elem["id"])}_item_{count}_quantity', str(item.quantity)))
                        row.append(create_tag(soup, "td", f'{str(elem["id"])}_item_{count}_price', str(item.price)))
                        elem.append(row)
                        count += 1

                    last_row = soup.new_tag("tr")
                    last_row.append(soup.new_tag("th"))
                    last_row.append(create_tag(soup, "th", None, random.choice(
                        ["Total", "Total: ", "TOTAL", "TOTAL:", "Sum", "Sum:", "SUM", "SUM:"])))
                    last_row.append(create_tag(soup, "th", f'{str(elem["id"])}_total', items[len(items) - 1].price))
                    elem.append(last_row)

                    with open(DEFAULT_TMP_PATH + 'invoice.css', 'a', encoding="utf-8") as f:
                        f.write(generate_table_styles(elem, config))

                else:
                    output = provided_types[data_type]()
                    elem.string = output

            except KeyError:
                logging.error(f'Data type {elem.attrs["data-type"]} is unknown! This field will not be filled.')

    with open(DEFAULT_TMP_PATH + 'invoice.html', 'w', encoding="utf-8") as f:
        f.write(str(soup))


def create_tag(soup, tag, tag_id, content):
    if tag_id is None:
        new_tag = soup.new_tag(tag)
        new_tag.string = content
        return new_tag
    else:
        new_tag = soup.new_tag(tag, id=tag_id)
        new_tag.string = content
        return new_tag


def generate_table_styles(table, config):
    return f'#{table["id"]} {{ width: {config["width"]}px;' \
           f'border-spacing: {random.randint(config["minBorderSpacing"], config["maxBorderSpacing"])}px;' \
           f'font-size: {random.randint(config["minFontSize"], config["maxFontSize"])}px;' \
           f'text-align: right;' \
           f'box-sizing: border-box;' \
           f'table-layout: fixed;}}'


def set_font(soup):
    elem = soup.findAll("html")[0]
    font_choice = '"Courier New", Courier, monospace;'
    size_choice = 30
    if 'data-fonts' in elem.attrs:
        data_fonts = elem.attrs['data-fonts']
        fonts = data_fonts.split(';')
        font_choice = random.choice(fonts)

    if 'data-fontsize' in elem.attrs:
        data_fontsize = elem.attrs['data-fontsize']
        limits = data_fontsize.split(';')
        size_choice = random.randint(int(limits[0]), int(limits[1]))

    with open(DEFAULT_TMP_PATH + 'invoice.css', 'a', encoding="utf-8") as f:

        f.write('\nhtml {'
                f'font-family: {font_choice};\n'
                f'font-size: {size_choice}px\n'
                '}')


class HTMLFileFormatError(Exception):
    def __init__(self, message):
        super().__init__(message)
