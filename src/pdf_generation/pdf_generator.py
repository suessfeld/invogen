import json
import os
import random

import jinja2
import pdfkit


import jsonpickle

from bs4 import BeautifulSoup
from util.constants import *
from pdf_generation.GenerationAttributes import GenerationAttributes, BoundingBox

"""
Generates invoice PDFs with the provided attributes and saves them to the specified output.
The output name is specified in constants.py.
"""
def generate_pdfs(gen_attr: GenerationAttributes):
    output_path = gen_attr.output_path

    if not os.path.exists(gen_attr.output_path):
        os.mkdir(gen_attr.output_path)

    for i in range(gen_attr.amount):
        gen_attr.output_path = output_path
        gen_attr.output_path = output_path + DEFAULT_OUTPUT_NAME + str(i) + ".pdf"
        render(gen_attr)


"""
Renders a single PDF document from html and css templates. 
TODO: complete functionality with config and random values.
"""
def render(gen_attr: GenerationAttributes):
    template_loader = jinja2.FileSystemLoader('./')
    template_env = jinja2.Environment(loader=template_loader)

    html_template = './src/pdf_generation/sample_invoice/invoice.html'
    template = template_env.get_template(html_template)
    context = generate_context()
    # TODO: Fix this line
    output_text = template.render(jsonpickle.decode(jsonpickle.encode(context, unpicklable=False)))

    bounding_box = BoundingBox(0, 0, 1000, 1000)
    position = generate_position(bounding_box)
    extract_html_information(open(html_template))
    html_info = extract_html_information(open(html_template))
    generate_css(html_info)

    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdf = pdfkit.from_string(output_text, gen_attr.output_path, configuration=config,
                             css='./src/pdf_generation/tmp/invoice.css')
    os.remove("./src/pdf_generation/tmp/invoice.css")
    return pdf


"""
TODO:implement
Generates a random context.
"""
def generate_context() -> {}:
    context = Context()
    context.company = Company()
    context.company.address = Address()
    context.company.name = "test company"
    context.company.address.street = "Gumpendorfer Strasse"
    context.company.address.city = "Wien"
    context.company.address.postal = "1060"
    context.company.email = "a.b@c.d"
    return context


"""
Generates a random position in the provided bounding box.
"""
def generate_position(bounding_box: BoundingBox) -> {}:
    return {
        'x': random.randrange(bounding_box.x1, bounding_box.x2),
        'y': random.randrange(bounding_box.y1, bounding_box.y2)
    }


"""
Generates a temporary css file for positioning of the elements.
Params: element_dic is a dictionary with the structure
    <element_name>: {
        position_x
        position_y
        }
        element_name represents class of the css element, position the absolute position of the element
"""
def generate_css(element_dict: dict):
    css_template = '''.{element_name} {{
    position:absolute;
    bottom:{position_x}px;
    left:{position_y}px;}}
    '''
    css_template = css_template.replace("\n", "")
    f = open("./src/pdf_generation/tmp/invoice.css", "a+")
    for element, attributes in element_dict.items():
        bounding_box = BoundingBox(attributes['x1'], attributes['y1'], attributes['x2'], attributes['y2'])

        position = generate_position(bounding_box)
        f.write(css_template.format(element_name=element, position_x=position['x'], position_y=position['y']))


"""
Extracts the needed config information from the html-document.
"""
def extract_html_information(html) -> dict:
    element_dict = dict()

    soup = BeautifulSoup(html, 'html.parser')
    elems = soup.findAll()

    for elem in elems:
        if 'data-position' in elem.attrs:
            position_string = elem.attrs['data-position'].split(' ')
            element_dict[elem.attrs['class'][0]]=vars(BoundingBox(int(position_string[0]), int(position_string[1]), int(position_string[2]), int(position_string[3])))

    return element_dict

class Context:
    pass


class Company:
    pass


class Address:
    pass
