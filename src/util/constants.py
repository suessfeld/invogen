"""
All globally defined constants
"""

from datetime import datetime

"""
PATHS
"""
CUSTOM_CONFIG_FILE_PATH = "./src/util/custom_config.json"
DEFAULT_CONFIG_FILE_PATH = "./src/util/default_config.json"

DEFAULT_OUTPUT_PATH = "./output/"
DEFAULT_INVOICE_OUTPUT_PATH = DEFAULT_OUTPUT_PATH + "invoices/"
DEFAULT_ANNOTATION_OUTPUT_PATH = DEFAULT_OUTPUT_PATH + "annotation_data/"
DEFAULT_OUTPUT_NAME = datetime.today().strftime('%Y_%m_%d') + "_invoice_output_"

DEFAULT_TMP_PATH = DEFAULT_OUTPUT_PATH + "tmp/"

DEFAULT_GENERATION_SCRIPT_PATH = "./src/util/position_generation_script.js"
CSS_PATH = "./sample_invoice/invoice.css"

LOGO_API_KEY = "NglW5BMfsKzOQlKS10ETzw==n33giYi70AugXKb5"

# TODO: THIS PATH IS ONLY CORRECT FOR WINDOWS MACHINES AND WILL BE CHANGED FOR DOCKER-USAGE!
DEFAULT_WKTHMLTOPDF_PATH = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
