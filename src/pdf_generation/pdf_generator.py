import os
import jinja2
import pdfkit

from util.constants import *
from pdf_generation.GenerationAttributes import GenerationAttributes


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
    context = {}
    output_text = template.render(context)

    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdf = pdfkit.from_string(output_text, gen_attr.output_path, configuration=config,
                             css='./src/pdf_generation/sample_invoice/invoice.css')
    return pdf
