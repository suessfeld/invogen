
class Address:
    street: str
    building_number: str
    city: str
    postal_code: str
    country: str

    def __init__(self, street, building_number, city, postal_code, country):
        self.street = street
        self.building_number = building_number
        self.city = city
        self.postal_code = postal_code
        self.country = country
