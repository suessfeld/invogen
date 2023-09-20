import calendar
import os
import random

from faker import Faker

import jinja2
import pdfkit

import jsonpickle

from bs4 import BeautifulSoup

from pdf_generation.data_generator import generate_email, generate_date
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
    if os.path.exists(DEFAULT_TMP_PATH + "invoice.css"):
        os.remove(DEFAULT_TMP_PATH + "invoice.css")
    if os.path.exists(DEFAULT_TMP_PATH + "invoice.html"):
        os.remove(DEFAULT_TMP_PATH + "invoice.html")

    template_loader = jinja2.FileSystemLoader('./')
    template_env = jinja2.Environment(loader=template_loader)

    template_path = './sample_invoice/invoice.html'
    context = generate_context()

    with open(template_path) as html_file:
        add_js_to_html(html_file)

    with open(template_path) as html_file:
        generate_bounding_boxes(html_file)
    template_path = DEFAULT_TMP_PATH + 'invoice.html'
    template = template_env.get_template(template_path)

    # TODO: Fix this line
    output_text = template.render(jsonpickle.decode(jsonpickle.encode(context, unpicklable=False)))

    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

    pdf = pdfkit.from_string(output_text, gen_attr.output_path, configuration=config)
    return pdf


"""
Extracts the needed config information from the html-document.
TODO: Change functionality to extract position for JSON generation.
"""


def extract_html_information(html) -> dict:
    element_dict = dict()

    soup = BeautifulSoup(html, 'html.parser')
    elems = soup.findAll()

    for elem in elems:
        if 'data-position' in elem.attrs:
            position_string = elem.attrs['data-position'].split(' ')
            element_dict[elem.attrs['class'][0]] = vars(BoundingBox(int(position_string[0]), int(position_string[1]),
                                                                    int(position_string[2]), int(position_string[3])))

    return element_dict


"""
Reads in the JS-Script file and appends the script to the html file.
"""


def add_js_to_html(html):
    with open(DEFAULT_GENERATION_SCRIPT_PATH) as script:
        soup = BeautifulSoup(html, 'html.parser')
        soup.append(BeautifulSoup("<script>" + script.read() + "</script>", features="html.parser"))

    with open(DEFAULT_TMP_PATH + 'invoice.html', 'a+') as f:
        f.write(str(soup))


"""
Generates visual bounding boxes for all randomly placed Elements.
TODO: Make this feature an option
"""


def generate_bounding_boxes(html):
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

    with open(DEFAULT_TMP_PATH + 'invoice.html', 'a+') as f:
        f.write(str(output))


"""
TODO:implement
Generates a random context.
"""


def generate_context() -> {}:

    fake = Faker('de_DE')
    address = Address(fake.address())

    context = Context()
    context.company = Company()
    context.company.address = address
    context.company.name = fake.company()
    context.company.email = generate_email(fake)
    print(generate_date(fake))
    return context


class Context:
    pass


class Company:
    pass


class Address:

    def __init__(self, address):
        self.address = address


