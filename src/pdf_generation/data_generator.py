import calendar
import inspect
import logging
import random
import string

import faker
import qrcode
import requests
import rstr

from faker import Faker
from faker.providers import company
from schwifty import IBAN

import pdf_generation
import util.constants
from pdf_generation.Item import Item, ItemField
from pdf_generation.Address import Address
from util.constants import LOGO_API_KEY, LOGO_API_URL


def static(method):
    method_name = method.__name__

    def wrapper(self, *args, **kwargs):

        if method_name in self.invoice_information:
            return self.invoice_information[method_name]
        else:
            self.invoice_information[method_name] = method(self, *args, **kwargs)
            return self.invoice_information[method_name]

    return wrapper

class DataGenerator:
    # singleton instance
    _instance = None

    _buffer_logos = False

    _buffered_images = []

    invoice_information = {}

    @static
    def email(self):
        return f"{self.first_name}.{self.last_name}@{self.fake.domain_name()}"

    @static
    def client_name(self):
        return self.first_name + " " + self.last_name

    def regex(self, regex):
        return rstr.xeger(regex)

    def date(self):
        date = self.fake.date_this_century()
        rand = random.randint(0, 4)
        if rand == 0:
            return f"{date.day}.{date.month}.{date.year}"
        elif rand == 1:
            return f"{date.day}/{date.month}/{str(date.year)[len(str(date.year)) - 2:]}"
        elif rand == 2:
            return f"{date.year}-{date.month}-{date.day}"
        elif rand == 3:
            return f"{calendar.month_name[date.month]} {date.day}, {date.year}"
        elif rand == 4:
            return f"{calendar.month_abbr[date.month]} {date.day}, {date.year}"

    @static
    def invoice_date(self):
        return self.fake.date_this_century()

    def invoice_date_natural(self):
        date = self.invoice_date()
        rand = random.randint(0, 4)
        if rand == 0:
            return f"{date.day}.{date.month}.{date.year}"
        elif rand == 1:
            return f"{date.day}/{date.month}/{str(date.year)[len(str(date.year)) - 2:]}"
        elif rand == 2:
            return f"{date.year}-{date.month}-{date.day}"
        elif rand == 3:
            return f"{calendar.month_name[date.month]} {date.day}, {date.year}"
        elif rand == 4:
            return f"{calendar.month_abbr[date.month]} {date.day}, {date.year}"

    def invoice_date_iso(self):
        return self.invoice_date().isoformat()

    @static
    def invoice_timestamp(self):
        return self.fake.time()

    def address(self):
        return Address(self.fake.street_name(),
                       self.fake.building_number(),
                       self.fake.city(),
                       self.fake.postcode(),
                       self.fake.country())

    @static
    def company(self):
        return self.fake.company()

    def logo(self):

        if not self._buffer_logos:
            logging.info("Sent API-request for logo fetching")
            name = ''.join(random.choice(string.ascii_lowercase) for _ in range(2))
            api_url = 'https://api.api-ninjas.com/v1/logo?name={}'.format(name)
            response = requests.get(api_url, headers={'X-Api-Key': LOGO_API_KEY})

            if response.status_code == requests.codes.ok:
                json = response.json()

                if len(json) == 0:
                    return self.logo()

                return json[0]["image"]

        if self._buffered_images:
            img = random.choice(self._buffered_images)
            self._buffered_images.remove(img)
            return img["image"]

        name = ''.join(random.choice(string.ascii_lowercase) for _ in range(2))
        api_url = f'{LOGO_API_URL}?name={name}'
        response = requests.get(api_url, headers={'X-Api-Key': LOGO_API_KEY})

        logging.info("Sent API-request for logo fetching")
        if response.status_code == requests.codes.ok:
            json = response.json()

            if len(json) == 0:
                return self.logo()

            self._buffered_images = json
            return self.logo()

        else:
            logging.error("Error:", response.status_code, response.text)

    def item_list(self, lower_bound, upper_bound, columns):

        item_list = []
        currency = random.choice(['$', ' $ ', '€', ' € ', '£', ' £ '])
        currency_in_front = random.randint(0, 1) == 0
        total = 0

        item = Item()

        for column in columns:

            if column == 'number':
                item.add_field(ItemField(column, random.choice(["No.", "No.:"])))

            if column == 'name':
                item.add_field(ItemField(column, random.choice(["Name", "Product: ", "Name:"])))

            if column == 'description':
                item.add_field(ItemField(column, random.choice(["Description", "Desc.:", "Desc.", "Description:"])))

            if column == 'article_number':
                item.add_field(ItemField(column, random.choice(["Art. No.", "No.: ", "Art. No.:"])))

            if column == 'price':
                item.add_field(ItemField(column, random.choice(["Price", "Price:"])))

            if column == 'quantity':
                item.add_field(ItemField(column, random.choice(["Qty.:", "Qty."])))

            if column == 'tax':
                item.add_field(ItemField(column, random.choice(["Tax", "Tax: "])))

        item_list.append(item)
        total = 0

        freetax = 0
        mintax = 0
        midtax = 0
        specialtax = 0
        maxtax = 0

        for i in range(random.randint(lower_bound, upper_bound)):
            item = Item()

            tax_temp = 0

            for column in columns:

                field = None

                if column == 'number':
                    field = ItemField('number', str(i + 1))

                if column == 'name':
                    field = ItemField('name', self.fake.ecommerce_name())

                if column == 'price':
                    item_price_float = float("{0:.2f}".format(random.uniform(2, 50)))
                    item_price = [f'{currency}{item_price_float}', f'{item_price_float}{currency}'][currency_in_front]

                    tax_temp = item_price_float

                    total = total + item_price_float

                    field = ItemField('price', item_price)

                if column == 'quantity':
                    field = ItemField('quantity', str(random.randint(1, 8)))

                if column == 'article_number':
                    field = ItemField('article_number', self.regex(r"\b\d{4,8}\b"))

                if column == 'description':
                    field = ItemField('description', self.fake.bs())

                if column == 'tax':
                    field = ItemField('tax', random.choice(['0%', '10%', '13%', '19%', '20%']))

                item.add_field(field)
            try:
                index = item.get_fields().index('tax');
                tax = item.get_fields()[index]

                if tax == '0%':
                    freetax += tax_temp

                if tax == '10%':
                    midtax += tax_temp

                if tax == '13%':
                    midtax += tax_temp

                if tax == '19%':
                    specialtax += tax_temp

                if tax == '20%':
                    maxtax += tax_temp

            except ValueError:
                maxtax += tax_temp

            item_list.append(item)

        self.invoice_information['invoice_total'] = total
        self.invoice_information['invoice_mintax'] = mintax
        self.invoice_information['invoice_midtax'] = midtax
        self.invoice_information['invoice_maxtax'] = maxtax
        self.invoice_information['invoice_freetax'] = freetax
        self.invoice_information['invoice_specialtax'] = specialtax

        total = "{:.2f}".format(total)
        item = Item()
        has_sum = False
        for i in range(len(columns)):
            if i < len(columns) - 3:
                item.add_field(ItemField(f"spacer{i}", ""))

            if i == len(columns) - 3:
                if random.randint(0, 100) < 50:
                    item.add_field(ItemField('total_description', random.choice(
                        ["Total", "Total: ", "TOTAL", "TOTAL:", "Sum", "Sum:", "SUM", "SUM:"])))
                    has_sum = True
                else:
                    item.add_field(ItemField(f"spacer{i}", ""))

            if i == len(columns) - 2:
                if has_sum:
                    item.add_field(ItemField(f"spacer{i}", ""))
                else:
                    item.add_field(ItemField('total_description', random.choice(
                        ["Total", "Total: ", "TOTAL", "TOTAL:", "Sum", "Sum:", "SUM", "SUM:"])))
                    has_sum = True

            if i == len(columns) - 1:
                item.add_field(
                    ItemField('total_value', [f'{currency}{total}', f'{total}{currency}'][currency_in_front]))
        item_list.append(item)
        return item_list

    def custom(self, data: str):
        strings = data.split(';')
        choice = random.choice(strings)
        return choice

    def qr_code_invoice(self, path):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        algorithm_type = random.choice(["R1-AT0", "R1-AT1", "R1-AT2"])
        register_number = self.invoice_register_number()
        invoice_number = self.invoice_number()
        invoice_timestamp = self.invoice_date_iso() + 'T' + self.invoice_timestamp()
        invoice_mintax = self.invoice_information['invoice_mintax']
        invoice_midtax = self.invoice_information['invoice_midtax']
        invoice_maxtax = self.invoice_information['invoice_maxtax']
        invoice_freetax = self.invoice_information['invoice_freetax']
        invoice_specialtax = self.invoice_information['invoice_specialtax']
        encrypted_counter = rstr.xeger(r'^[a-zA-Z0-9=\\%&]{10,20}$')
        certificate_number = rstr.xeger(r'^[a-zA-Z0-9=\\%&]{10,20}$')
        last_signature = rstr.xeger(r'^[a-zA-Z0-9=\\%&]{10,20}$')
        signature = rstr.xeger(r'^[a-zA-Z0-9=\\%&]{15,30}$')

        data = \
            '_' + algorithm_type + \
            '_' + register_number + \
            '_' + invoice_number + \
            '_' + invoice_timestamp + \
            '_' + "{:.2f}".format(invoice_mintax).replace('.', ',') + \
            '_' + "{:.2f}".format(invoice_midtax).replace('.', ',') + \
            '_' + "{:.2f}".format(invoice_maxtax).replace('.', ',') + \
            '_' + "{:.2f}".format(invoice_freetax).replace('.', ',') + \
            '_' + "{:.2f}".format(invoice_specialtax).replace('.', ',') + \
            '_' + encrypted_counter + \
            '_' + certificate_number + \
            '_' + last_signature + \
            '_' + signature

        qr.add_data(data)
        qr.make(fit=True)

        qr.make_image(fill_color="black", back_color="white").save(path + "qrcode.png")
        return path + "qrcode.png"

    @static
    def qr_code_url(self, path):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.url())
        qr.make(fit=True)

        qr.make_image(fill_color="black", back_color="white").save(path + "qrcode_url.png")
        return path + "qrcode_url.png"

    @static
    def url(self):
        return self.fake.url()

    # see https://de.wikipedia.org/wiki/Internationale_Bankkontonummer for more information
    @static
    def invoice_iban(self):
        return IBAN.random()

    @static
    def invoice_register_number(self):
        return self.regex(r'\d{4,7}')

    @static
    def invoice_number(self):
        return self.regex(r'\d{10,20}')

    @static
    def invoice_email(self):
        return self.email()

    def __init__(self, buffer_logos):
        self._buffer_logos = buffer_logos
        self.fake = Faker(["de_AT"])
        self.fake.add_provider(pdf_generation.faker_commerce.Provider)
        self.fake.add_provider(faker.providers.company)
        self.first_name = self.fake.first_name()
        self.last_name = self.fake.last_name()
        self.data_types = {}
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if not name.startswith('__') and not name.startswith('_'):
                self.data_types[name] = method

    def __new__(cls, buffer_logos=None):
        if cls._instance is None:
            # Store the init parameter before creating the instance
            cls._init_params = {'buffer_logos': buffer_logos}
            cls._instance = super(DataGenerator, cls).__new__(cls)
        return cls._instance

    country_codes = [
        'AF', 'AL', 'DZ', 'AS', 'AD', 'AO', 'AI', 'AQ', 'AG', 'AR', 'AM', 'AW', 'AU', 'AT', 'AZ',
        'BS', 'BH', 'BD', 'BB', 'BY', 'BE', 'BZ', 'BJ', 'BM', 'BT', 'BO', 'BQ', 'BA', 'BW', 'BR',
        'BN', 'BG', 'BF', 'BI', 'CV', 'KH', 'CM', 'CA', 'KY', 'CF', 'TD', 'CL', 'CN', 'CO', 'KM',
        'CG', 'CD', 'CR', 'CI', 'HR', 'CU', 'CW', 'CY', 'CZ', 'DK', 'DJ', 'DM', 'DO', 'EC', 'EG',
        'SV', 'GQ', 'ER', 'EE', 'SZ', 'ET', 'FJ', 'FI', 'FR', 'GA', 'GM', 'GE', 'DE', 'GH', 'GI',
        'GR', 'GL', 'GD', 'GU', 'GT', 'GN', 'GW', 'GY', 'HT', 'HN', 'HK', 'HU', 'IS', 'IN', 'ID',
        'IR', 'IQ', 'IE', 'IL', 'IT', 'JM', 'JP', 'JO', 'KZ', 'KE', 'KI', 'KP', 'KR', 'KW', 'KG',
        'LA', 'LV', 'LB', 'LS', 'LR', 'LY', 'LI', 'LT', 'LU', 'MO', 'MG', 'MW', 'MY', 'MV', 'ML',
        'MT', 'MH', 'MR', 'MU', 'MX', 'FM', 'MD', 'MC', 'MN', 'ME', 'MS', 'MA', 'MZ', 'MM', 'NA',
        'NR', 'NP', 'NL', 'NZ', 'NI', 'NE', 'NG', 'NU', 'NF', 'MK', 'MP', 'NO', 'OM', 'PK', 'PW',
        'PS', 'PA', 'PG', 'PY', 'PE', 'PH', 'PL', 'PT', 'PR', 'QA', 'RO', 'RU', 'RW', 'KN', 'LC',
        'VC', 'WS', 'SM', 'ST', 'SA', 'SN', 'RS', 'SC', 'SL', 'SG', 'SX', 'SK', 'SI', 'SB', 'SO',
        'ZA', 'SS', 'ES', 'LK', 'SD', 'SR', 'SE', 'CH', 'SY', 'TW', 'TJ', 'TZ', 'TH', 'TL', 'TG',
        'TO', 'TT', 'TN', 'TR', 'TM', 'TV', 'UG', 'UA', 'AE', 'GB', 'US', 'UY', 'UZ', 'VU', 'VA',
        'VE', 'VN', 'YE', 'ZM', 'ZW'
    ]

    country_codes_eu = [
        'BE', 'EL', 'LT', 'PT', 'BG', 'ES', 'LU', 'RO', 'CZ', 'FR', 'HU', 'SI', 'DK', 'HR', 'MT', 'SK', 'DE', 'IT',
        'NL',
        'FI', 'EE', 'CY', 'AT', 'SE', 'IE', 'LV', 'PL', 'IS', 'NO', 'LI', 'CH', 'BA', 'ME', 'MD', 'MK', 'GE', 'AL',
        'RS',
        'TR', 'UA']
