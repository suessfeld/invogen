import calendar
import inspect
import logging
import random
import string

import faker
import requests
import rstr

import faker_commerce
from faker import Faker

import pdf_generation
from pdf_generation.Item import Item
from pdf_generation.Address import Address
from util.constants import LOGO_API_KEY, LOGO_API_URL


class DataGenerator:

    # singleton instance
    _instance = None

    _buffer_logos = False

    _buffered_images = []

    def email(self):
        return f"{self.first_name}.{self.last_name}@{self.fake.domain_name()}"

    def client_name(self):
        return self.first_name + " " + self.last_name

    def regex(self, regex):
        return rstr.xeger(regex)

    def date(self):
        date = self.fake.date_this_century()
        rand = random.randint(0, 4)
        match rand:
            case 0:
                return f"{date.day}.{date.month}.{date.year}"
            case 1:
                return f"{date.day}/{date.month}/{str(date.year)[len(str(date.year)) - 2:]}"
            case 2:
                return f"{date.year}-{date.month}-{date.day}"
            case 3:
                return f"{calendar.month_name[date.month]} {date.day}, {date.year}"
            case 4:
                return f"{calendar.month_abbr[date.month]} {date.day}, {date.year}"

    def address(self):
        return Address(self.fake.street_name(),
                       self.fake.building_number(),
                       self.fake.city(),
                       self.fake.postcode(),
                       self.fake.country())

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

    def item_list(self, lower_bound, upper_bound):

        item_list = []
        currency = random.choice(['$', ' $ ', '€', ' € ', '£', ' £ '])
        currency_in_front = random.randint(0, 1) == 0
        total = 0

        for _ in range(random.randint(lower_bound, upper_bound)):
            item_name = self.fake.ecommerce_name()

            item_price_float = float("{0:.2f}".format(random.uniform(2, 600)))
            item_price = [f'{currency}{item_price_float}', f'{item_price_float}{currency}'][currency_in_front]
            total = total + item_price_float

            item_quantity = random.randint(1, 4)
            item = Item(item_name, item_price, item_quantity)
            item_list.append(item)

        total = "{:.2f}".format(total)
        item_list.append(Item('total', [f'{currency}{total}', f'{total}{currency}'][currency_in_front], 0))
        return item_list

    def custom(self, data: str):
        strings = data.split(';')
        choice = random.choice(strings)
        return choice

    def __init__(self, buffer_logos):
        self._buffer_logos = buffer_logos
        self.fake = Faker('en_US')
        self.fake.add_provider(faker_commerce.Provider)
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