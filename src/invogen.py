import logging

import typer
from typing import Optional

import pdf_generation

from util.constants import *

app = typer.Typer(help="Invoice Generation Tool by Elias Voill")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

"""
Generates invoices with the specified params.
If the seed flag is not set, a random seed will be used.
"""
@app.command()
def generate(invoice_output_path: Optional[str] = None, annotation_output_path: Optional[str] = None, amount: int = 0,
             display_bounding_boxes: Optional[bool] = False):

    gen_attr = pdf_generation.GenerationAttributes()

    if invoice_output_path is None:
        gen_attr.invoice_output_path = DEFAULT_INVOICE_OUTPUT_PATH

    if annotation_output_path is None:
        gen_attr.annotation_output_path = DEFAULT_ANNOTATION_OUTPUT_PATH
    gen_attr.display_bounding_boxes = display_bounding_boxes
    gen_attr.amount = amount

    pdf_generation.generate_pdfs(gen_attr)

if __name__ == "__main__":
    app()
