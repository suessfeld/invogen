import codecs
import json
import logging
import os
import random
import re
import string

import jsonpickle
from bs4 import BeautifulSoup

from pdf_generation import DataGenerator
from pdf_generation.Annotation import Annotation, DataObject, Position
from util.constants import *


def fill_html(html, buffer_logos, gen_attr):
    data_generator = DataGenerator(buffer_logos)
    provided_types = data_generator.data_types
    soup = BeautifulSoup(html, 'html.parser')
    elems = soup.findAll()

    # fonts:
    set_font(soup, gen_attr)

    for elem in elems:
        if 'data-type' in elem.attrs:
            data_type = elem.attrs['data-type']
            try:

                if data_type == 'logo':

                    config = json.loads(elem['data-config'])

                    # validate options
                    viable_options = {'height'}
                    config_keys = set(config.keys())
                    extra_keys = config_keys - viable_options
                    if extra_keys:
                        logging.error(f"Table has invalid options: {extra_keys}")
                        continue

                    # Table background color:
                    heights = str(config['height']).split(';')

                    elem['src'] = provided_types[data_type]()
                    elem['style'] = f'height:{random.randint(int(heights[0]), int(heights[1]))}px'

                elif data_type == 'custom':
                    elem.string = provided_types[data_type](elem['data-list'])

                elif data_type == 'regex':
                    elem.string = provided_types[data_type](elem['data-regex'])

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

                    country_div = create_tag(soup, "span", str(elem["id"]) + "_country", address.country)
                    elem.append(street_div)
                    elem.append(city_div)
                    elem.append(country_div)

                elif data_type == 'item_list':

                    assert (elem.name == "table")

                    config = json.loads(elem['data-config'])

                    # validate options
                    viable_options = {'minWidth', 'maxWidth', 'minPadding', 'maxPadding', 'minFontSize', 'maxFontSize',
                                      'minElems', 'maxElems', 'colors'}
                    config_keys = set(config.keys())
                    extra_keys = config_keys - viable_options
                    if extra_keys:
                        logging.error(f"Table has invalid options: {extra_keys}")
                        continue

                    items = provided_types[data_type](config['minElems'], config['maxElems'])

                    first_row = soup.new_tag("tr")

                    th = soup.new_tag("th")
                    th.append(create_tag(soup, "span", f'{str(elem["id"])}_header_name', 'Product'))
                    first_row.append(th)

                    th = soup.new_tag("th")
                    th.append(create_tag(soup, "span", f'{str(elem["id"])}_header_quantity', 'Quantity'))
                    first_row.append(th)

                    th = soup.new_tag("th")
                    th.append(create_tag(soup, "span", f'{str(elem["id"])}_header_price', 'Price'))
                    first_row.append(th)

                    elem.append(first_row)

                    count = 1
                    for item in items[:-1]:
                        row = soup.new_tag("tr")
                        td = soup.new_tag("td")
                        td.append(create_tag(soup, "span", f'{str(elem["id"])}_item_{count}_name', item.name))
                        row.append(td)

                        td = soup.new_tag("td")
                        td.append(
                            create_tag(soup, "span", f'{str(elem["id"])}_item_{count}_quantity', str(item.quantity)))
                        row.append(td)

                        td = soup.new_tag("td")
                        td.append(create_tag(soup, "span", f'{str(elem["id"])}_item_{count}_price', str(item.price)))
                        row.append(td)

                        elem.append(row)
                        count += 1

                    last_row = soup.new_tag("tr")
                    last_row.append(soup.new_tag("td"))

                    td = soup.new_tag("td")
                    td.append(create_tag(soup, "span", f'{str(elem["id"])}_total_description', random.choice(
                        ["Total", "Total: ", "TOTAL", "TOTAL:", "Sum", "Sum:", "SUM", "SUM:"])))
                    last_row.append(td)

                    td = soup.new_tag("td")
                    td.append(create_tag(soup, "span", f'{str(elem["id"])}_total_value', items[len(items) - 1].price))
                    last_row.append(td)

                    elem.append(last_row)

                    with open(gen_attr.temp_path + 'invoice.css', 'a', encoding="utf-8") as f:
                        f.write(generate_table_styles(elem, config))

                else:
                    output = provided_types[data_type]()
                    elem.string = output

            except KeyError as e:
                logging.error(f'Data type {elem.attrs["data-type"]} is unknown! This field will not be filled.')
                logging.error(e)

    with open(gen_attr.temp_path + 'invoice.html', 'w', encoding="utf-8") as f:
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
    # Table background color:
    color_options = str(config['colors']).split(';')
    color = random.choice(color_options)

    padding = random.randint(int(config["minPadding"]), int(config["maxPadding"]))
    width = random.randint(int(config["minWidth"]), int(config["maxWidth"]))

    output = f'#{table["id"]} {{ width: {width}px;' \
             f'padding: {random.randint(int(config["minPadding"]), int(config["maxPadding"]))}px;' \
             f'font-size: {random.randint(config["minFontSize"], config["maxFontSize"])}px;' \
             f'text-align: right;' \
             f'box-sizing: border-box;' \
             f'border-spacing: 0px;' \
             f'table-layout: fixed;}}' \
             f'\n' \
             f'#{table["id"]} tr:nth-child(even) {{background: {color};}}' \
             f'\n' \
             f'#{table["id"]} td {{border-bottom: {padding}px solid transparent;' \
             f'border-top: {padding}px solid transparent;}}'

    return output


def set_font(soup, gen_attr):
    elem = soup.findAll("html")[0]
    font_choice = '"Courier New", Courier, monospace;'
    size_choice = 30
    background_choice = 'white'
    color_choice = 'black'

    if 'data-fonts' in elem.attrs:
        data_fonts = elem.attrs['data-fonts']
        fonts = data_fonts.split(';')
        font_choice = random.choice(fonts)

    if 'data-fontsize' in elem.attrs:
        data_fontsize = elem.attrs['data-fontsize']
        limits = data_fontsize.split(';')
        size_choice = random.randint(int(limits[0]), int(limits[1]))

    if 'data-fontsize' in elem.attrs:
        data_fontcolor = elem.attrs['data-fontcolor']
        colors = data_fontcolor.split(';')
        color_choice = random.choice(colors)

    if 'data-background' in elem.attrs:
        data_background = elem.attrs['data-background']
        backgrounds = data_background.split(';')
        background_choice = random.choice(backgrounds)

    with open(gen_attr.temp_path + 'invoice.css', 'a', encoding="utf-8") as f:

        f.write('\nhtml, table {'
                f'font-family: {font_choice};\n'
                f'font-size: {size_choice}px;\n'
                f'color: {color_choice};\n'
                f'background: {background_choice};}}')


"""
Extracts position information from the html file
"""


def extract_and_save_information(buf, annotation_output_path):
    annotation_object = Annotation()
    with codecs.open(annotation_output_path, "w", encoding="utf-8") as file:
        string = buf.getvalue()
        matches = re.findall("position-absolute;.+;[0-9]+;[0-9]+;[0-9]+;[0-9]+;.+;", string)

        for m in matches:
            string_arr = m.split(';')
            annotation_object.data[string_arr[1]] = DataObject()
            annotation_object.data[string_arr[1]].position = Position(string_arr[2], string_arr[3],
                                                                      string_arr[4], string_arr[5])
            annotation_object.data[string_arr[1]].value = string_arr[6]

        # Ensure correct utf-8 encoding
        jsonpickle.set_encoder_options('json', ensure_ascii=False)
        file.write(jsonpickle.encode(annotation_object, unpicklable=False, max_depth=10))


"""
Reads in the JS-Script file and appends the script to the html file.
"""


def add_js_to_html(gen_attr):
    with open(DEFAULT_GENERATION_SCRIPT_PATH, encoding='utf-8') as script:
        soup = BeautifulSoup()
        soup.append(BeautifulSoup("<script>" + script.read() + "</script>", features="html.parser"))

    with open(os.path.normpath(gen_attr.temp_path + 'invoice.html'), 'a+', encoding="utf-8") as f:
        f.write(str(soup))


"""
Generates visual bounding boxes for all randomly placed Elements.
"""


def generate_bounding_boxes(html, gen_attr):
    soup = BeautifulSoup(html, 'html.parser')
    output = BeautifulSoup()
    elems = soup.findAll()
    for elem in elems:
        if 'data-position' in elem.attrs:
            position_string = elem.attrs['data-position'].split(' ')
            tag = soup.new_tag("div", style=f"""
                position: absolute;
                height: {int(position_string[3]) - int(position_string[1])}px;
                width: {int(position_string[2]) - int(position_string[0])}px;
                left: {position_string[0]}px;
                bottom: {position_string[1]}px;
                border: 1px solid #f32177;
            """)
            output.append(tag)

    with open(gen_attr.temp_path + 'invoice.html', 'a+', encoding="utf-8") as f:
        f.write(str(output))


class HTMLFileFormatError(Exception):
    def __init__(self, message):
        super().__init__(message)
