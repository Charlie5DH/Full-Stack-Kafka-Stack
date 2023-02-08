import os


class Inventory:
    def __init__(
        self,
        event_time: str,
        product_id: str,
        existing_level: int,
        stock_quantity: int,
        new_level: int,
    ):
        self.event_time = str(event_time)
        self.product_id = str(product_id)
        self.existing_level = int(existing_level)
        self.stock_quantity = int(stock_quantity)
        self.new_level = int(new_level)

    def __str__(self):
        return (
            "Inventory: event_time: {0}, product_id: {1}, existing_level: {2:.0f}, stock_quantity: {3:.0f}, "
            "new_level: {4:.0f}".format(
                self.event_time,
                self.product_id,
                self.existing_level,
                self.stock_quantity,
                self.new_level,
            )
        )

    def to_dict(self):
        return {
            "event_time": self.event_time,
            "product_id": self.product_id,
            "existing_level": self.existing_level,
            "stock_quantity": self.stock_quantity,
            "new_level": self.new_level,
        }

    def get_schema(self):
        schema = {
            "namespace": "com.example.models",
            "type": "record",
            "name": "Inventory",
            "fields": [
                {"name": "event_time", "type": "string"},
                {"name": "product_id", "type": "string"},
                {"name": "existing_level", "type": "int"},
                {"name": "stock_quantity", "type": "int"},
                {"name": "new_level", "type": "int"},
            ],
        }
        return schema

    def load_schema(self):
        # load schema from file
        path = os.path.realpath(os.path.dirname(
            __file__)).replace("models", "schema")
        with open(f"{path}/inventory.avsc") as f:
            schema = f.read()
        return schema

    def schema_name(self):
        return "inventory"

    def schema_path(self):
        # load schema from file
        path = os.path.realpath(os.path.dirname(
            __file__)).replace("models", "schema")
        return f"{path}/inventory.avsc"
