import codecs
import json
import logging
import os
import platform
import random
import re

import jsonpickle
from bs4 import BeautifulSoup

from pdf_generation import DataGenerator
from pdf_generation.Annotation import Annotation, AnnotationObject, AnnotationValue, AnnotationResult
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
                    viable_options = {'width'}
                    config_keys = set(config.keys())
                    extra_keys = config_keys - viable_options
                    if extra_keys:
                        logging.error(f"Table has invalid options: {extra_keys}")
                        continue

                    # Table background color:
                    heights = str(config['width']).split(';')

                    elem['src'] = provided_types[data_type]()
                    elem['style'] = f'width:{random.randint(int(heights[0]), int(heights[1]))}px'

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
                                      'minElems', 'maxElems', 'colors', 'columns'}
                    config_keys = set(config.keys())
                    extra_keys = config_keys - viable_options
                    if extra_keys:
                        logging.error(f"Table has invalid options: {extra_keys}")
                        continue

                    items = provided_types[data_type](config['minElems'], config['maxElems'],
                                                      str(config['columns']).split(';'))

                    first_row = soup.new_tag("tr")

                    col_widths = calc_widths(items)

                    for index, field in enumerate(items[0].get_fields()):
                        th = soup.new_tag("th")
                        th['style'] = f'width: {round(col_widths[index])}%'
                        th.append(create_tag(soup, "span", f'{str(elem["id"])}_header_{field.attribute}', field.value))
                        first_row.append(th)

                    elem.append(first_row)

                    count = 1
                    for item in items[1:]:
                        row = soup.new_tag("tr")
                        for field in item.get_fields():
                            td = soup.new_tag("td")
                            td.append(create_tag(
                                soup,
                                "span", f'{str(elem["id"])}_item_{count}_{field.attribute}', field.value))

                            row.append(td)

                        elem.append(row)
                        count += 1

                    with open(gen_attr.temp_path + 'invoice.css', 'a', encoding="utf-8") as f:
                        f.write(generate_table_styles(elem, config))

                elif data_type == 'qr_code_invoice':
                    config = json.loads(elem['data-config'])

                    # validate options
                    viable_options = {'height'}
                    config_keys = set(config.keys())
                    extra_keys = config_keys - viable_options
                    if extra_keys:
                        logging.error(f"Table has invalid options: {extra_keys}")
                        continue

                    # Table heights
                    heights = str(config['height']).split(';')

                    elem['src'] = provided_types[data_type](gen_attr.temp_path)
                    elem['style'] = f'height:{random.randint(int(heights[0]), int(heights[1]))}px'

                elif data_type == 'qr_code_url':
                    config = json.loads(elem['data-config'])

                    # validate options
                    viable_options = {'height'}
                    config_keys = set(config.keys())
                    extra_keys = config_keys - viable_options
                    if extra_keys:
                        logging.error(f"Table has invalid options: {extra_keys}")
                        continue

                    # Table heights
                    heights = str(config['height']).split(';')

                    elem['src'] = provided_types[data_type](gen_attr.temp_path)
                    elem['style'] = f'height:{random.randint(int(heights[0]), int(heights[1]))}px'

                else:
                    output = provided_types[data_type]()
                    elem.string = output

            except KeyError as e:
                logging.error(f'Generation of type {elem.attrs["data-type"]} failed!'
                              f'Check if this type is correctly defined.'
                              f'[error: {e}]')

    with open(gen_attr.temp_path + 'invoice.html', 'w', encoding="utf-8") as f:
        f.write(str(soup))

    data_generator.invoice_information = {}

def create_tag(soup, tag, tag_id, content):
    if tag_id is None:
        new_tag = soup.new_tag(tag)
        new_tag.string = content
        return new_tag
    else:
        new_tag = soup.new_tag(tag, id=tag_id)
        new_tag.string = content
        return new_tag


def calc_widths(items):
    counter = [0] * len(items[0].get_fields())
    for item in items:
        for index, field in enumerate(item.get_fields()):
            if len(field.value) > 3:
                counter[index] += len(field.value)
            else:
                counter[index] += 3

    total = 0
    counter = list(map(lambda c: c / len(items), counter))
    total = sum(counter)

    output = [0] * len(items[0].get_fields())
    for index, c in enumerate(counter):
        output[index] = c / total * 100

    return counter


def generate_table_styles(table, config):
    # Table background color:
    color_options = str(config['colors']).split(';')
    color = random.choice(color_options)

    padding = random.randint(int(config["minPadding"]), int(config["maxPadding"]))
    width = random.randint(int(config["minWidth"]), int(config["maxWidth"]))
    font_size = random.randint(config["minFontSize"], config["maxFontSize"])

    output = f'#{table["id"]} {{ width: {width}px;' \
             f'padding: {random.randint(int(config["minPadding"]), int(config["maxPadding"]))}px;' \
             f'font-size: {font_size}px;' \
             f'text-align: center;' \
             f'box-sizing: border-box;' \
             f'border-spacing: 0px;' \
             f'table-layout: fixed;}}' \
             f'\n' \
             f'#{table["id"]} tr:nth-child(even) {{background: {color};}}' \
             f'\n' \
             f'#{table["id"]} tr {{height: {font_size + padding}px;}}'

    return output


def set_font(soup, gen_attr):
    elem = soup.findAll("html")[0]
    font_choice = '"Courier New", Courier, monospace;'
    size_choice = 30
    background_choice = 'white'
    color_choice = 'black'
    selected = False

    if 'data-fonts' in elem.attrs:
        data_fonts = elem.attrs['data-fonts']
        fonts = data_fonts.split(';')
        font_choice = random.choice(fonts)
        selected = True

    if 'data-fontsize' in elem.attrs:
        data_fontsize = elem.attrs['data-fontsize']
        limits = data_fontsize.split(';')
        size_choice = random.randint(int(limits[0]), int(limits[1]))
        selected = True

    if 'data-fontsize' in elem.attrs:
        data_fontcolor = elem.attrs['data-fontcolor']
        colors = data_fontcolor.split(';')
        color_choice = random.choice(colors)
        selected = True

    if 'data-background' in elem.attrs:
        data_background = elem.attrs['data-background']
        backgrounds = data_background.split(';')
        background_choice = random.choice(backgrounds)
        selected = True

    if selected:
        with open(gen_attr.temp_path + 'invoice.css', 'a', encoding="utf-8") as f:
            f.write('\nhtml, table {'
                    f'font-family: {font_choice};\n'
                    f'font-size: {size_choice}px;\n'
                    f'color: {color_choice};\n'
                    f'background: {background_choice};}}')
            f.close()


"""
Extracts position information from the html file
"""


def to_percentage(small, big, invert):
    percentage = (float(small) / float(big)) * 100

    if invert:
        return 100 - percentage
    else:
        return percentage


def extract_and_save_information(buf, gen_attr, global_annotation_object: [], html):
    soup = BeautifulSoup(html, 'html.parser')
    height = soup.find('meta', attrs={'name': 'pdfkit-page-height'})['content']
    width = soup.find('meta', attrs={'name': 'pdfkit-page-width'})['content']

    # Remove the 'px' suffix and convert to integers
    height = int(height.replace('px', ''))
    width = int(width.replace('px', ''))

    annotation = Annotation()

    path = gen_attr.label_studio_project_root.replace("\\", "\\\\")

    annotation.data['image'] = \
        "/data/local-files/?d=" + path.replace("pdf", "jpg")

    with codecs.open(os.path.normpath(gen_attr.annotation_output_path), "w", encoding="utf-8") as file:
        line = buf.getvalue()
        matches = re.findall(
            'position-absolute;[^;]*;[0-9]+(?:\.[0-9]+)?;[0-9]+(?:\.[0-9]+)?;[0-9]+(?:\.[0-9]+)?;[0-9]+(?:\.[0-9]+)?;[^;]*;',
            line)

        annotation_object = AnnotationObject()
        annotation_object.ground_truth = False
        annotation_object.result = []

        for m in matches:
            string_arr = m.split(';')

            annotation_result = AnnotationResult()
            annotation_value = AnnotationValue()

            annotation_result.type = "textarea"
            annotation_result.id = string_arr[1]
            annotation_result.to_name = "image"
            annotation_result.from_name = "transcription"
            annotation_result.image_rotation = 0
            annotation_result.original_width = width
            annotation_result.original_height = height

            annotation_value.x = to_percentage(string_arr[2], width, False)
            annotation_value.y = to_percentage(string_arr[5], height, True)
            annotation_value.width = to_percentage(abs(float(string_arr[4]) - float(string_arr[2])), width, False)
            annotation_value.height = to_percentage(abs(float(string_arr[5]) - float(string_arr[3])), height, False)
            annotation_value.rotation = 0
            annotation_value.text = [string_arr[6]]

            annotation_result.value = annotation_value
            annotation_object.result.append(annotation_result)

        annotation.annotations.append(annotation_object)
        global_annotation_object.append(annotation)
        # Ensure correct utf-8 encoding
        jsonpickle.set_encoder_options('json', ensure_ascii=False)
        file.write(jsonpickle.encode(annotation, unpicklable=False, max_depth=10))


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
