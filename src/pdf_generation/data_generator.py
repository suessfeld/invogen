import calendar
import random


def generate_email(fake):
    first_name = fake.first_name()
    last_name = fake.last_name()
    return f"{first_name}.{last_name}@{fake.domain_name()}"

def generate_date(fake):
    date = fake.date_this_century()
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


def generate_address(fake):
    fake.address()


def generate_invoice_no():
    pass


def generate_logo():
    pass

