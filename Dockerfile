# BUILD IMAGE WITH
# docker build -t invogen-app .
#
# RUN CONTAINER WITH
# docker run -v "C:/Users/evoil/PycharmProjects/invogen/sample_invoice:/input" -v "C:/Users/evoil/Documents/output:/output"
# invogen-app python ./src/invogen.py --input-html /input/invoice_example2.html --input-css /input/invoice_example2.css --output /output --amount 10

FROM python:3.9-buster

WORKDIR /usr/src/app

# Install dependencies and wkhtmltopdf
RUN apt-get update && apt-get install -y \
    wget \
    xfonts-base \
    xfonts-75dpi \
    fontconfig \
    libjpeg62-turbo \
    libxrender1 \
    && wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb \
    && apt install -y ./wkhtmltox_0.12.6-1.buster_amd64.deb \
    && rm ./wkhtmltox_0.12.6-1.buster_amd64.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./src/invogen.py"]




