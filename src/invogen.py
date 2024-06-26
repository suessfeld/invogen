import codecs
import logging
import os.path
import sys

import typer
from typing import Optional

import pdf_generation

from util.constants import *

app = typer.Typer(help="Invoice Generation Tool by Elias Voill")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

"""
Generates invoices with the specified params.
Parses and validates arguments
"""


@app.command()
def generate(output: str = typer.Option(..., "--output", "-o"),
             amount: int = typer.Option(..., "--amount"),
             input_html: str = typer.Option(..., "--input-html"),
             input_css: str = typer.Option(..., "--input-css"),
             label_studio_project_root: Optional[str] = None,
             display_bounding_boxes: Optional[bool] = False,
             buffer_logos: Optional[bool] = False,
             ):
    gen_attr = pdf_generation.GenerationAttributes()

    if output is None:
        gen_attr.invoice_output_path = DEFAULT_INVOICE_OUTPUT_PATH
        gen_attr.annotation_output_path = DEFAULT_ANNOTATION_OUTPUT_PATH
        gen_attr.temp_path = DEFAULT_TMP_PATH
    else:
        gen_attr.invoice_output_path = output + "/invoices/"
        gen_attr.annotation_output_path = output + "/annotation_data/"
        gen_attr.temp_path = output + "/temp/"

    if label_studio_project_root is None:
        gen_attr.label_studio_project_root = output
    else:
        gen_attr.label_studio_project_root = label_studio_project_root

    gen_attr.display_bounding_boxes = display_bounding_boxes
    gen_attr.buffer_logos = buffer_logos
    gen_attr.input_html = input_html
    gen_attr.input_css = input_css
    gen_attr.amount = amount

    pdf_generation.generate_pdfs(gen_attr)


if __name__ == "__main__":
    app()
