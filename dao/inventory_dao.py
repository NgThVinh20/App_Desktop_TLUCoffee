from config.database import Database
from typing import List

class InventoryDAO:

    @staticmethod
    def get_all() -> List[dict]:
        return Database.execute_query(
            "SELECT * FROM inventory ORDER BY name",
            fetch=True
        )

    @staticmethod
    def get_low_stock() -> List[dict]:
        """Nguyên liệu dưới ngưỡng cảnh báo."""
        return Database.execute_query(
            """SELECT * FROM inventory
               WHERE quantity <= min_quantity
               ORDER BY quantity ASC""",
            fetch=True
        )

    @staticmethod
    def update_quantity(item_id: int, quantity: float) -> None:
        Database.execute_query(
            "UPDATE inventory SET quantity=%s WHERE id=%s",
            (quantity, item_id)
        )

    @staticmethod
    def create(item_code: str, name: str, unit: str,
               quantity: float, min_quantity: float) -> int:
        return Database.execute_query(
            """INSERT INTO inventory
               (item_code, name, unit, quantity, min_quantity)
               VALUES (%s,%s,%s,%s,%s)""",
            (item_code, name, unit, quantity, min_quantity)
        )