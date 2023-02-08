import os


class Product:
    def __init__(
        self,
        event_time: str,
        product_id: str,
        category: str,
        item: str,
        size: str,
        cogs: float,
        price: float,
        inventory_level: int,
        contains_fruit: bool,
        contains_veggies: bool,
        contains_nuts: bool,
        contains_caffeine: bool,
        propensity_to_buy: int,
    ):
        self.event_time = str(event_time)
        self.product_id = str(product_id)
        self.category = str(category)
        self.item = str(item)
        self.size = str(size)
        self.cogs = float(cogs)
        self.price = float(price)
        self.inventory_level = int(inventory_level)
        self.contains_fruit = bool(contains_fruit)
        self.contains_veggies = bool(contains_veggies)
        self.contains_nuts = bool(contains_nuts)
        self.contains_caffeine = bool(contains_caffeine)
        self.propensity_to_buy = int(propensity_to_buy)

    def __str__(self):
        return (
            "Product: event_time: {0}, Product: product_id: {1}, category: {2}, item: {3}, size: {4}, "
            "cogs: ${5:.2f}, price: ${6:.2f}, inventory_level: {7:.0f}, contains_fruit: {8}, contains_veggies: {9}, "
            "contains_nuts: {10}, contains_caffeine: {10}".format(
                self.event_time,
                self.product_id,
                self.category,
                self.item,
                self.size,
                self.cogs,
                self.price,
                self.inventory_level,
                self.contains_fruit,
                self.contains_veggies,
                self.contains_nuts,
                self.contains_caffeine,
            )
        )

    def __repr__(self):
        return str(self)

    def schema_name(self):
        return "product"

    # return dictionary of the object
    def to_dict(self):
        return {
            "event_time": self.event_time,
            "product_id": self.product_id,
            "category": self.category,
            "item": self.item,
            "size": self.size,
            "cogs": self.cogs,
            "price": self.price,
            "inventory_level": self.inventory_level,
            "contains_fruit": self.contains_fruit,
            "contains_veggies": self.contains_veggies,
            "contains_nuts": self.contains_nuts,
            "contains_caffeine": self.contains_caffeine,
            "propensity_to_buy": self.propensity_to_buy,
        }

    # Get the schema for the Product class in Avro format
    def get_schema(self):
        schema = {
            "namespace": "com.example.models",
            "type": "record",
            "name": "Product",
            "fields": [
                {"name": "event_time", "type": "string"},
                {"name": "product_id", "type": "string"},
                {"name": "category", "type": "string"},
                {"name": "item", "type": "string"},
                {"name": "size", "type": "string"},
                {"name": "cogs", "type": "float"},
                {"name": "price", "type": "float"},
                {"name": "inventory_level", "type": "int"},
                {"name": "contains_fruit", "type": "boolean"},
                {"name": "contains_veggies", "type": "boolean"},
                {"name": "contains_nuts", "type": "boolean"},
                {"name": "contains_caffeine", "type": "boolean"},
                {"name": "propensity_to_buy", "type": "int"},
            ],
        }
        return schema

    def load_schema(self):
        # load schema from file
        path = os.path.realpath(os.path.dirname(
            __file__)).replace("models", "schema")
        with open(f"{path}/product.avsc") as f:
            schema = f.read()
        return schema

    def schema_path(self):
        path = os.path.realpath(os.path.dirname(
            __file__)).replace("models", "schema")
        return f"{path}/product.avsc"
