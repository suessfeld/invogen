import io
import logging
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
from pdf_generation.html_parser import *
from util.constants import *
from pdf_generation.GenerationAttributes import GenerationAttributes, BoundingBox

"""
Generates invoice PDFs with the provided attributes and saves them to the specified output.
The output name is specified in constants.py.
"""


def generate_pdfs(gen_attr: GenerationAttributes):
    invoice_output_path = gen_attr.invoice_output_path
    annotation_output_path = gen_attr.annotation_output_path
    temp_path = gen_attr.temp_path

    if not os.path.exists(invoice_output_path):
        os.mkdir(invoice_output_path)

    if not os.path.exists(annotation_output_path):
        os.mkdir(annotation_output_path)

    if not os.path.exists(temp_path):
        os.mkdir(temp_path)

    for i in range(gen_attr.amount):
        start = time.time()
        gen_attr.invoice_output_path = invoice_output_path
        gen_attr.invoice_output_path = invoice_output_path + DEFAULT_OUTPUT_NAME + str(i) + ".pdf"

        gen_attr.annotation_output_path = annotation_output_path
        gen_attr.annotation_output_path = annotation_output_path + DEFAULT_OUTPUT_NAME + str(i) + ".json"
        render(gen_attr)
        end = time.time()
        logging.info(f'Generated {gen_attr.invoice_output_path} in {round(end - start, 2)} seconds')


"""
Renders a single PDF document from html and css templates. 
"""


def render(gen_attr: GenerationAttributes):

    if os.path.exists(DEFAULT_TMP_PATH + "invoice.css"):
        os.remove(DEFAULT_TMP_PATH + "invoice.css")
    if os.path.exists(DEFAULT_TMP_PATH + "invoice.html"):
        os.remove(DEFAULT_TMP_PATH + "invoice.html")

    template_path = '../sample_invoice/invoice_example2.html'
    template_css = '../sample_invoice/invoice_example2.css'

    with open(DEFAULT_TMP_PATH + 'invoice.css', 'w', encoding="utf-8") as css_file, open(template_css, 'r') as input_file:
        for line in input_file:
            css_file.write(line)

    with open(template_path, encoding="utf-8") as html_file:
        html_parser.fill_html(html_file, gen_attr.buffer_logos)

    if gen_attr.display_bounding_boxes:
        with open(template_path, encoding="utf-8") as html_file:
            generate_bounding_boxes(html_file)
        gen_attr.display_bounding_boxes = False

    add_js_to_html()

    template_path = DEFAULT_TMP_PATH + 'invoice.html'
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

    with open(template_path, encoding="utf-8") as html_file:

        #with io.StringIO() as buf, redirect_stdout(buf):
        pdf = pdfkit.from_string(html_file.read(), gen_attr.invoice_output_path, configuration=config,
                                     options={"enable-local-file-access": ""}, css=DEFAULT_TMP_PATH + "invoice.css",
                                     verbose=True)
            #extract_and_save_information(buf, gen_attr.annotation_output_path)

        return pdf
