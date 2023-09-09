import typer
import json
from typing import Optional
from pdf_generation.pdf_generator import generate_pdfs
from pdf_generation.GenerationAttributes import GenerationAttributes
from pdf_generation.html_configurator import validate_config, save_config, ConfigFileFormatError
from util.constants import *

app = typer.Typer()

"""
Sets and loads a custom config.
TODO: This command might be unnecessary and might be removed
"""
@app.command()
def config(path: str = None):
    save_and_validate_config(path)
    typer.echo("Config loaded successfully!")


"""
Generates invoices with the specified params.
If the config_path flag is not set, the default config will be used.
If the seed flag is not set, a random seed will be generated.
"""
@app.command()
def generate(config_path: Optional[str] = None, output_path: str = None, amount: int = 0, seed: Optional[str] = None):

    gen_attr = GenerationAttributes()

    if config_path is None:
        gen_attr.config = DEFAULT_CONFIG_FILE_PATH
    else:
        save_and_validate_config(config_path)
        gen_attr.config = CUSTOM_CONFIG_FILE_PATH

    if output_path is None:
        gen_attr.output_path = DEFAULT_OUTPUT_DIR_PATH

    gen_attr.seed = seed
    gen_attr.amount = amount

    generate_pdfs(gen_attr)


"""
Reads in an validates config. TODO: implement
"""
def save_and_validate_config(path: str = None):

    if path:
        try:
            with open(path, 'r') as file:
                data = json.load(file)
                validate_config(data)
                save_config(data)

        except FileNotFoundError:
            print(f"File not found: {path}")
            return None

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None

        except ConfigFileFormatError as e:
            print(f"Config is not in the right format: {e}")
            return None


if __name__ == "__main__":
    app()
