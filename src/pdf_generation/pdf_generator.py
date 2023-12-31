import io
import os
import re
import codecs
import sys
from contextlib import redirect_stdout

import pdfkit

import jsonpickle

from bs4 import BeautifulSoup

from pdf_generation import html_parser
from pdf_generation.Annotation import *
from util.constants import *
from pdf_generation.GenerationAttributes import GenerationAttributes, BoundingBox

"""
Generates invoice PDFs with the provided attributes and saves them to the specified output.
The output name is specified in constants.py.
"""


def generate_pdfs(gen_attr: GenerationAttributes):
    invoice_output_path = gen_attr.invoice_output_path
    annotation_output_path = gen_attr.annotation_output_path

    if not os.path.exists(gen_attr.invoice_output_path):
        os.mkdir(gen_attr.invoice_output_path)

    if not os.path.exists(gen_attr.annotation_output_path):
        os.mkdir(gen_attr.annotation_output_path)

    for i in range(gen_attr.amount):
        gen_attr.invoice_output_path = invoice_output_path
        gen_attr.invoice_output_path = invoice_output_path + DEFAULT_OUTPUT_NAME + str(i) + ".pdf"

        gen_attr.annotation_output_path = annotation_output_path
        gen_attr.annotation_output_path = annotation_output_path + DEFAULT_OUTPUT_NAME + str(i) + ".json"
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

    template_path = './sample_invoice/invoice.html'

    annotation_object = Annotation()

    with open(template_path) as html_file:
        html_parser.fill_html(html_file, annotation_object)

    if gen_attr.display_bounding_boxes:
        with open(template_path) as html_file:
            generate_bounding_boxes(html_file)
        gen_attr.display_bounding_boxes = False

    # TODO: This should be refactored
    add_js_to_html()

    template_path = DEFAULT_TMP_PATH + 'invoice.html'
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

    with open(template_path) as html_file:

        with io.StringIO() as buf, redirect_stdout(buf):
            pdf = pdfkit.from_string(html_file.read(), gen_attr.invoice_output_path, configuration=config,
                                         options={"enable-local-file-access": ""}, css="./sample_invoice/invoice.css",
                                         verbose=True)
            extract_and_save_information(buf, gen_attr.annotation_output_path, annotation_object)
            return pdf



"""
Extracts position information from the html file
TODO: Implement
"""


def extract_and_save_information(buf, annotation_output_path, annotation_object):
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


def add_js_to_html():
    with open(DEFAULT_GENERATION_SCRIPT_PATH) as script:
        soup = BeautifulSoup()
        soup.append(BeautifulSoup("<script>" + script.read() + "</script>", features="html.parser"))

    with open(DEFAULT_TMP_PATH + 'invoice.html', 'a+') as f:
        f.write(str(soup))


"""
Generates visual bounding boxes for all randomly placed Elements.
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
