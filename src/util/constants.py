"""
All globally defined constants
"""

from datetime import datetime

"""
PATHS
"""
CUSTOM_CONFIG_FILE_PATH = "./src/util/custom_config.json"
DEFAULT_CONFIG_FILE_PATH = "./src/util/default_config.json"
DEFAULT_OUTPUT_DIR_PATH = "./output/"
DEFAULT_OUTPUT_NAME = datetime.today().strftime('%Y_%m_%d') + "_invoice_output_"
DEFAULT_TMP_PATH = DEFAULT_OUTPUT_DIR_PATH + "tmp/"
DEFAULT_GENERATION_SCRIPT_PATH = "./src/util/position_generation_script.js"
