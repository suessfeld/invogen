"""
All globally defined constants
"""

from datetime import datetime

CUSTOM_CONFIG_FILE_PATH = "./src/util/custom_config.json"
DEFAULT_CONFIG_FILE_PATH = "./src/util/default_config.json"
DEFAULT_OUTPUT_DIR_PATH = "./src/output/"
DEFAULT_OUTPUT_NAME = datetime.today().strftime('%Y_%m_%d') + "_invoice_output_"
