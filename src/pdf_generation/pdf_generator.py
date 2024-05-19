import io
import logging
import os
import platform
import re
import codecs
import sys
import time
from contextlib import redirect_stdout

import pdfkit

import jsonpickle

from bs4 import BeautifulSoup
from fitz_new import fitz

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
        try:
            os.mkdir(invoice_output_path)
        except FileNotFoundError:
            logging.error("Output path is invalid!")
            sys.exit(-1)

    if not os.path.exists(annotation_output_path):
        os.mkdir(annotation_output_path)

    if not os.path.exists(temp_path):
        os.mkdir(temp_path)

    global_annotation_object = []
    try:
        for i in range(gen_attr.amount):
            start = time.time()
            gen_attr.invoice_output_path = invoice_output_path
            gen_attr.invoice_output_path = invoice_output_path + DEFAULT_OUTPUT_NAME + str(i) + ".pdf"

            gen_attr.annotation_output_path = annotation_output_path
            gen_attr.annotation_output_path = annotation_output_path + DEFAULT_OUTPUT_NAME + str(i) + ".json"
            render(gen_attr, global_annotation_object)
            start_conversion = time.time()
            pdf_to_jpg(gen_attr.invoice_output_path)
            end_conversion = time.time()
            end = time.time()
            logging.info(f'Generated {gen_attr.invoice_output_path} in {round(end - start, 2)}seconds'
                         f' (jpg conversion took {round(end_conversion - start_conversion, 2)}s).')

    except Exception as e:
        logging.error("An exception was encountered during generation. Progress is saved.")
        logging.info(e)

    finally:
        with codecs.open(annotation_output_path + "~label-studio-import.json", "w", encoding="utf-8") as file:
            jsonpickle.set_encoder_options('json', ensure_ascii=False)
            file.write(jsonpickle.encode(global_annotation_object, unpicklable=False, max_depth=10))


"""
Renders a single PDF document from html and css templates. 
"""


def render(gen_attr: GenerationAttributes, global_annotation_object: []):
    if os.path.exists(gen_attr.temp_path + "invoice.css"):
        os.remove(gen_attr.temp_path + "invoice.css")
    if os.path.exists(gen_attr.temp_path + "invoice.html"):
        os.remove(gen_attr.temp_path + "invoice.html")

    try:
        with open(gen_attr.temp_path + 'invoice.css', 'w', encoding="utf-8") as css_file, open(gen_attr.input_css,
                                                                                               'r') as input_file:
            for line in input_file:
                css_file.write(line)
    except FileNotFoundError:
        print("The specified CSS file does not exist.")
        sys.exit(-1)

    try:
        with open(gen_attr.input_html, encoding="utf-8") as html_file:
            html_parser.fill_html(html_file, gen_attr.buffer_logos, gen_attr)
    except FileNotFoundError:
        print("The specified HTML file does not exist.")
        sys.exit(-1)

    if gen_attr.display_bounding_boxes:
        with open(gen_attr.input_html, encoding="utf-8") as html_file:
            generate_bounding_boxes(html_file, gen_attr)
        gen_attr.display_bounding_boxes = False

    add_js_to_html(gen_attr)

    template_path = gen_attr.temp_path + 'invoice.html'

    config = None
    if platform.system() == 'Windows':
        config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    else:
        config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')

    with open(template_path, encoding="utf-8") as html_file:

        with io.StringIO() as buf, redirect_stdout(buf):
            pdf = pdfkit.from_string(html_file.read(), gen_attr.invoice_output_path, configuration=config,
                                     options={"enable-local-file-access": ""}, css=gen_attr.temp_path + "invoice.css",
                                     verbose=True)

            with open(gen_attr.input_html, encoding="utf-8") as input_html:
                extract_and_save_information(buf, gen_attr, global_annotation_object, input_html)

        return pdf

def pdf_to_jpg(pdf):
    document = fitz.open(pdf)
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        pix = page.get_pixmap()
        pix.save(pdf.replace("pdf", "jpg"))
