# InvoGen
This is an invoice generator tool made for generating annotated training data for Key Information Extraction. The project was
implemented as part of Elias Voill's bachelor's thesis.

## Usage

```sh
invogen --output <OUTPUT> --amount <AMOUNT> --input-html <INPUT_HTML> --input-css <INPUT_CSS>
```

| Option                       | Description                                                                                                                                                                                                                                                                             | Required | Default Value   |
|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|-----------------|
| `-o, --output <OUTPUT>`      | Specifies the output file or directory.                                                                                                                                                                                                                                                 | Yes | N/A             |
| `--amount <AMOUNT>`          | Number of documents to generate                                                                                                                                                                                                                                                         | Yes | N/A             |
| `--input-html <INPUT_HTML>`  | Path of the input HTML file.                                                                                                                                                                                                                                                            | Yes | N/A             |
| `--input-css <INPUT_CSS>`    | Path of the input CSS file.                                                                                                                                                                                                                                                             | Yes | N/A             |
| `--display-bounding-boxes`   | Optional flag to display bounding boxes on the first generated invoice.                                                                                                                                                                                                                 | No | `False`         |
| `--buffer-logos`             | Optional flag to buffer logos.This will improve performance but reduces logo variation of consecutive invoices. Consider randomizing the output order to  mitigate this effect.                                                                                                                | No | `False`         |
| `--label-studio-project-root` | Optional flag to define the absolute path of the desired output root. This path will be used to define the image location of an invoice for an annotation. Use this if you cannot directly generate data into the target Label Studio folder. ([see more](#use-invogen-with-docker)) | No | path from `--output` |

## Documentation

### Input

#### HTML Header

Every document has to start with a html tag containing the attributes data-fonts, data-fontsize, data-fontcolor, and data-background.
The data-fonts attribute defines which fonts should be randomly used in the generation process. Note that in order to use the provided fonts,
they have to be included in the HTML file with a link element. Secondly, the data-fontsize attribute defines a range of sizes that will randomly
be used for the provided fonts. data-fontcolor and data-background define a palette of colors from which the respective attributes are chosen.

Following that, the head element requires various meta attributes to configure PDFKit for PDF rendering.
The following options are customizable:

```pdfkit-page-height``` and ```pdfkit-page-width``` define the fixed size of the produced document.
Note that these measures influence the positioning step of randomly placed elements later.
```pdfkit-margin-*``` is recommended to be set to 0 for all directions as this option could lead to positioning problems.
The following options are mandatory and should not be changed to ensure proper PDF output:
``` html
    <meta charset="UTF-8">
    <meta name="pdfkit-disable-smart-shrinking" content=""/>
    <meta name="pdfkit-debug-javascript" content=""/>
```
Combined, the start of an input HTML file should look like this:
```html
<html data-fonts="<font1>;<font2>;...;<fontN>"
      data-fontsize="<min>;<max>"
      data-fontcolor="<color1>;<color2>;...;<colorN>"
      data-background="<color1>;<color2>;...;<colorN>">
<link href="..." rel="stylesheet">
<link href="..." rel="stylesheet">
<link href="..." rel="stylesheet">

<head>
    <meta charset="UTF-8">
    <meta name="pdfkit-page-height" content="<height>px"/>
    <meta name="pdfkit-page-width" content="<width>px"/>
    <meta name="pdfkit-margin-top" content="0px"/>
    <meta name="pdfkit-margin-right" content="0px"/>
    <meta name="pdfkit-margin-left" content="0px"/>
    <meta name="pdfkit-margin-bottom" content="0px"/>
    <meta name="pdfkit-disable-smart-shrinking" content=""/>
    <meta name="pdfkit-debug-javascript" content=""/>
</head>
```

### HTML Body

For InvoGen all HTML elements can be used. Only elements that have the `id` attribute will be included in the annotation data.

InvoGen provides following predefined HTML generation rules:

- `data-position="<x1> <y1> <x2> <y2>"`: Defines the bounding box in which the element will be places
- `data-type="<type>"`: Defines how this element will be filled. Following types are already defined:
  - `regex`: Generates random regex.
    - Requires attribute `data-regex="<regex>"` to be filled with a valid regular expression.
  - `date`: Generates random date
  - `address`: Generates random address
  - `logo`: Generates random logo
    - `item_list`: Generates a list of items.
      - Requires `id` attribute
      - Requires attribute `data-config=""` to be set the following way:
        ```
          data-config='
            {
                "minWidth": <minimal width>,
                "maxWidth": <maximal width>,
                "minElems": <minimal count of elements>,
                "maxElems": <maximal count of elements>,
                "minFontSize": <minimal fontsize>,
                "maxFontSize": <maximal fontsize>,
                "minPadding": <minimal padding>,
                "maxPadding": <maximal padding>,
                "colors": "<color1>;<color2>;...;<colorN>"
            }'
          '```
  - `custom`: Generates a random element of the provided list
    - Requires attribute `data-list="<text1>;<text2>;...;<textN>` to be set.
  - `email` *static*: Generates email for this invoice
  - `client_name` *static*: Generates name for this invoice
  - `company` *static*: Generates company name for this invoice
  - `url` *static*: Generates url for this invoice
  - `qr_code_invoice` *static*: Generates QR Code for this invoice
  - `qr_code_url` *static*: Generates QR Code of the static invoice URL
  - `invoice_date_natural` *static*: Generates date for this invoice in random natural format
  - `invoice_date_iso` *static*: Generates date for this invoice in ISO format
  - `invoice_timestamp` *static*: Generates timestamp for this invoice in ISO format
  - `invoice_register_number` *static*: Generates register number for this invoice
  - `invoice_number` *static*: Generates invoice number for this invoice
  - `invoice_email` *static*: Generates email for this invoice
  - `invoice_iban` *static*: Generates iban for this invoice

Note that all *static* attributes only generate values once per invoice to guarantee consistency. Thus, reusing those functions will return the same values as
previous calls.

Helpful examples can be found at `/sample_invoices`.

#### CSS
Every element can additionally be formatted by the user with a supplementary CSS file. Note that some CSS properties might be overwritten if defined otherwise in generation elements.

### Output
Results of the generation process consist of two components, PDF documents, and annotation data.

#### PDFs
Generated invoices will be saved in the PDF format in the specified output folder in the directory /invoices. The documents will be named in the format:
```
<YYYY>_<MM>_<DD>_invoice_output_<index>.pdf
```
#### Annotation Data
Annotation data will be generated and stored in the ```/annotation_data``` directory, again with the latter defined naming convention but as a .json file.
It is stored in the [Label Studio import format](https://labelstud.io/guide/tasks.html)  and is thus directly importable in Label Studio.

To support batch import, once per job a file named ```~label_studio_import.json``` will be generated. This file contains annotation data of all invoices
and can be used to import the entire job at once.

### Use InvoGen with Label Studio (Windows)
1. Setup Label Studio on your machine and run it in a terminal.
2. Setup your Label Studio environment variables to support local file access (`LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED = true`, `LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT = <path>`,
[see more](https://labelstud.io/guide/start#Run-Label-Studio-on-Docker-and-use-local-storage))
3. Generate invoices with InvoGen in a subdirectory of the Label Studio root (as defined in step 2). (example `C:\Users\user\Documents\LabelStudio\myjob\output`, with root set to `C:\Users\user\Documents\LabelStudio`
  Note: Data *has* to be directly generated into this directory to ensure relative paths are set correctly during the generation process.
4. Create a new Label Studio project and define a desired labeling interface
5. Under Settings -> Cloud Storage -> Add Source Storage -> Local Files: Define the *parent* path of the output folder as 'absolute local path'. (in our example `C:\Users\user\Documents\LabelStudio\myjob\`)
6. Import the `~label_studio_import.json` file which should be located at `C:\Users\user\Documents\LabelStudio\myjob\output\annotation_data`

### Use InvoGen with Docker 
A public InvoGen image is available [here](https://hub.docker.com/repository/docker/suessfeld/invogen/general). 
Because Docker uses a mounted file system it is advised to use the option `--label-studio-output-root` to define the
final output path.


## Example
Lets try out to generate a sample invoices with Docker
1. Build (`docker build -t invogen .`) or pull your image of InvoGen
2. Run the container with correct options
   ```sh
   docker run
       -v "C:/Users/<user>/PycharmProjects/invogen/sample_invoice:/input"
       -v "C:/Users/<user>/Documents/LabelStudio/myjob/invogen:/output"
       invogen python ./src/invogen.py
           --input-html /input/invoice_example3.html
           --input-css /input/invoice_example3_docker.css
           --output /output
           --label-studio-project-root C:\Users\<user>\Documents\LabelStudio\myjob\invogen
           --amount 100
   ```
   Explanation:
   This command will generate 100 invoices into the `"C:/Users/<user>/Documents/LabelStudio/myjob/invogen/` directory and can be directly imported into Label Studio from exactly this location.
   - `-v "C:/Users/<user>/PycharmProjects/invogen/sample_invoice:/input"` mounts the input directory
   - `-v "C:/Users/<user>/Documents/LabelStudio/myjob/invogen:/output"` mounts the ouput directory
   - `--input-html /input/invoice_example3.html` defines input html of mounted directory
   - `--input-css /input/invoice_example3_docker.css` defines the input css of the mounted directory
   - `--output /output` defines the ouput directory of the mounted ouput directory
   - `--label-studio-project-root C:\Users\<user>\Documents\LabelStudio\myjob\invogen` defines the target output destination. Only if this path is correctly set, Label Studio will recognize the image paths when importing
   - `--amount 100` generate 100 invoices

## Extendability
Invogen was designed in a way to make defining new generation rules easily. 
Adding functions in the ```data_generator``` module will automatically be recognized as ```data-type``` for the input html and thus
fill the element as defined.

### Adding IBAN generation functionality (example):
For adding a new rule ```invoice_iban``` define the function ```invoice_iban(self)```

```python
...
from schwifty import IBAN
...

class DataGenerator:
    ...
    # see https://en.wikipedia.org/wiki/International_Bank_Account_Number for more information
    @static
    def invoice_iban(self):
            return IBAN.random()

    def __init__(self, buffer_logos):
        ...
```
in the DataGenerator class. If functions are annotated with ```@static``` the value will only be generated once per invoice and reused on subsequent calls. This can be useful to ensure consistent
information throughout a document. For this example it is assumed that IBANs stay consistent if occurring multiple times in a document.

After defining this function, the type ```invoice_iban``` can be used in input html files

```html
...
<span style="text-align: center" data-type="invoice_iban"></span>
...
```

Adding more complex rules that include html modification will require modifying
```fill_html()``` function defined in the `html_parser` module.
