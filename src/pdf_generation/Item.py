class Item:
    fields: []

    def add_field(self, field):
        self.fields.append(field)

    def get_fields(self):
        return self.fields

    def __init__(self):
        self.fields = []

class ItemField:
    attribute: str
    value: str

    def __init__(self, attribute, value):
        self.attribute = attribute
        self.value = value