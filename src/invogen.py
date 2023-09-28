import typer
import json
from typing import Optional

import pdf_generation

from util.constants import *

app = typer.Typer()

"""
Generates invoices with the specified params.
If the seed flag is not set, a random seed will be used.
"""
@app.command()
def generate(invoice_output_path: Optional[str] = None, annotation_output_path: Optional[str] = None, amount: int = 0, seed: Optional[str] = None):

    gen_attr = pdf_generation.GenerationAttributes()

    if invoice_output_path is None:
        gen_attr.invoice_output_path = DEFAULT_INVOICE_OUTPUT_PATH

    if annotation_output_path is None:
        gen_attr.annotation_output_path = DEFAULT_ANNOTATION_OUTPUT_PATH

    gen_attr.seed = seed
    gen_attr.amount = amount

    pdf_generation.generate_pdfs(gen_attr)


"""
Validates a html-input file
"""
@app.command()
def validate(path: str = None):

    if path:
        try:
            pdf_generation.validate_html(path)

        except FileNotFoundError:
            print(f"File not found: {path}")
            return None

        except pdf_generation.HTMLFileFormatError as e:
            print(f"Config is not in the right format: {e}")
            return None


if __name__ == "__main__":
    app()
