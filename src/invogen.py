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
def generate(output_path: Optional[str] = None, amount: int = 0, seed: Optional[str] = None):

    gen_attr = pdf_generation.GenerationAttributes()

    if output_path is None:
        gen_attr.output_path = DEFAULT_OUTPUT_DIR_PATH

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
