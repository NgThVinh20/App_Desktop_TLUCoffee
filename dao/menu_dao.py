from config.database import Database
from typing import Optional, List

class MenuDAO:

    @staticmethod
    def get_all(category_id: int = None) -> List[dict]:
        if category_id:
            return Database.execute_query(
                """SELECT m.*, c.name as category_name
                   FROM menu_items m
                   JOIN categories c ON m.category_id = c.id
                   WHERE m.category_id = %s
                   ORDER BY m.name""",
                (category_id,), fetch=True
            )
        return Database.execute_query(
            """SELECT m.*, c.name as category_name
               FROM menu_items m
               JOIN categories c ON m.category_id = c.id
               ORDER BY c.sort_order, m.name""",
            fetch=True
        )

    @staticmethod
    # lấy món đang bán cho POS
    def get_available() -> List[dict]:
        return Database.execute_query(
            """SELECT m.*, c.name as category_name
               FROM menu_items m
               JOIN categories c ON m.category_id = c.id
               WHERE m.is_available = 1
               ORDER BY c.sort_order, m.name""",
            fetch=True
        )
    # lấy món theo id
    @staticmethod
    def get_by_id(item_id: int) -> Optional[dict]:
        rows = Database.execute_query(
            """SELECT m.*, c.name as category_name
               FROM menu_items m
               JOIN categories c ON m.category_id = c.id
               WHERE m.id = %s""",
            (item_id,), fetch=True
        )
        return rows[0] if rows else None
    # tìm kiếm món
    @staticmethod
    def search(keyword: str) -> List[dict]:
        kw = f"%{keyword}%"
        return Database.execute_query(
            """SELECT m.*, c.name as category_name
               FROM menu_items m
               JOIN categories c ON m.category_id = c.id
               WHERE m.name LIKE %s OR m.description LIKE %s""",
            (kw, kw), fetch=True
        )
    # thêm món
    @staticmethod
    def create(category_id: int, name: str, description: str,
               base_price: float, image_path: str = None) -> int:
        return Database.execute_query(
            """INSERT INTO menu_items
               (category_id, name, description, base_price, image_path)
               VALUES (%s, %s, %s, %s, %s)""",
            (category_id, name, description, base_price, image_path)
        )
    # sửa món
    @staticmethod
    def update(item_id: int, category_id: int, name: str,
               description: str, base_price: float,
               is_available: int, is_featured: int) -> None:
        Database.execute_query(
            """UPDATE menu_items
               SET category_id=%s, name=%s, description=%s,
                   base_price=%s, is_available=%s, is_featured=%s
               WHERE id=%s""",
            (category_id, name, description,
             base_price, is_available, is_featured, item_id)
        )
    # xóa món
    @staticmethod
    def delete(item_id: int) -> None:
        Database.execute_query(
            "DELETE FROM menu_items WHERE id = %s", (item_id,)
        )
    # danh sách danh mục
    @staticmethod
    def get_categories() -> List[dict]:
        return Database.execute_query(
            "SELECT * FROM categories ORDER BY sort_order",
            fetch=True
        )
    # món bán chạy
    @staticmethod
    def get_top_selling(limit: int = 5) -> List[dict]:
        return Database.execute_query(
            """SELECT oi.item_name, SUM(oi.quantity) as total_sold,
                      SUM(oi.subtotal) as total_revenue
               FROM order_items oi
               JOIN orders o ON oi.order_id = o.id
               WHERE o.status = 'completed'
               GROUP BY oi.item_name
               ORDER BY total_sold DESC
               LIMIT %s""",
            (limit,), fetch=True
        )