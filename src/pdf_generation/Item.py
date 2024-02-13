class Item:
    name: str
    price: float
    quantity: int

    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity
