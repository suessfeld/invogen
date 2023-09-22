import calendar
import random
import string
import inspect
import types
from os.path import join
import sys

import requests
from faker import Faker

import pdf_generation
from util.constants import LOGO_API_KEY


class DataGenerator:
    def email(self):
        return f"{self.first_name}.{self.last_name}@{self.fake.domain_name()}"

    def client_name(self):
        return self.first_name + " " + self.last_name

    def invoice_no(self):
        return "00-000000"

    def date(self):
        date = self.fake.date_this_century()
        rand = random.randint(0, 4)
        match rand:
            case 0:
                return f"{date.day}.{date.month}.{date.year}"
            case 1:
                return f"{date.day}/{date.month}/{date.year}"
            case 2:
                return f"{date.year}-{date.month}-{date.day}"
            case 3:
                return f"{calendar.month_name[date.month]} {date.day}, {date.year}"
            case 4:
                return f"{calendar.month_abbr[date.month]} {date.day}, {date.year}"

    def address(self):
        return self.fake.address()

    def company_name(self):
        return self.fake.company()

    def logo(self):
        name = ''.join(random.choice(string.ascii_lowercase) for _ in range(2))
        api_url = 'https://api.api-ninjas.com/v1/logo?name={}'.format(name)
        response = requests.get(api_url, headers={'X-Api-Key': LOGO_API_KEY})

        if response.status_code == requests.codes.ok:
            json = response.json()

            if len(json) == 0:
                return self.logo()

            return json[0]["image"]

        else:
            print("Error:", response.status_code, response.text)

    def __init__(self):
        # TODO: Maybe change functionality, so functions will be extracted automatically

        self.fake = Faker('de_DE')
        self.first_name = self.fake.first_name()
        self.last_name = self.fake.last_name()

        self.data_types = {
            'logo': self.logo,
            'invoice_no': self.invoice_no,
            'address': self.address,
            'date': self.date,
            'email': self.email,
            'company': self.company_name,
            'client_name': self.client_name}
