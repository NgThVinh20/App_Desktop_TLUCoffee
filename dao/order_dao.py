from config.database import Database
from typing import Optional, List
from datetime import date

class OrderDAO:

    @staticmethod
    def get_recent(limit: int = 10) -> List[dict]:
        """Đơn gần đây — dùng cho Dashboard."""
        return Database.execute_query(
            """SELECT o.*, u.full_name as staff_name
               FROM orders o
               JOIN users u ON o.user_id = u.id
               ORDER BY o.created_at DESC
               LIMIT %s""",
            (limit,), fetch=True
        )

    @staticmethod
    def get_all(status: str = None, from_date: str = None,
                to_date: str = None) -> List[dict]:
        """Lịch sử đơn hàng có filter."""
        query = """SELECT o.*, u.full_name as staff_name
                   FROM orders o
                   JOIN users u ON o.user_id = u.id
                   WHERE 1=1"""
        params = []
        if status:
            query += " AND o.status = %s"
            params.append(status)
        if from_date:
            query += " AND DATE(o.created_at) >= %s"
            params.append(from_date)
        if to_date:
            query += " AND DATE(o.created_at) <= %s"
            params.append(to_date)
        query += " ORDER BY o.created_at DESC"
        return Database.execute_query(query, params, fetch=True)

    @staticmethod
    def get_by_id(order_id: int) -> Optional[dict]:
        rows = Database.execute_query(
            """SELECT o.*, u.full_name as staff_name
               FROM orders o JOIN users u ON o.user_id = u.id
               WHERE o.id = %s""",
            (order_id,), fetch=True
        )
        return rows[0] if rows else None

    @staticmethod
    def get_items(order_id: int) -> List[dict]:
        """Lấy danh sách món của 1 đơn."""
        return Database.execute_query(
            "SELECT * FROM order_items WHERE order_id = %s",
            (order_id,), fetch=True
        )

    @staticmethod
    def get_revenue_today() -> float:
        """Doanh thu hôm nay — Dashboard."""
        rows = Database.execute_query(
            """SELECT COALESCE(SUM(total_amount), 0) as revenue
               FROM orders
               WHERE DATE(created_at) = CURDATE()
               AND status = 'completed'""",
            fetch=True
        )
        return float(rows[0]['revenue']) if rows else 0.0

    @staticmethod
    def get_revenue_7days() -> List[dict]:
        """Doanh thu 7 ngày qua — biểu đồ Dashboard."""
        return Database.execute_query(
            """SELECT DATE(created_at) as ngay,
                      COALESCE(SUM(total_amount), 0) as doanh_thu
               FROM orders
               WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
               AND status = 'completed'
               GROUP BY DATE(created_at)
               ORDER BY ngay""",
            fetch=True
        )

    @staticmethod
    def get_count_today() -> dict:
        """Số đơn hôm nay theo trạng thái."""
        rows = Database.execute_query(
            """SELECT
                COUNT(*) as total,
                SUM(status='completed')  as completed,
                SUM(status='processing') as processing,
                SUM(status='cancelled')  as cancelled
               FROM orders
               WHERE DATE(created_at) = CURDATE()""",
            fetch=True
        )
        return rows[0] if rows else {}

    @staticmethod
    def create(user_id: int, subtotal: float, total_amount: float,
               payment_method: str, table_number: int = None,
               discount: float = 0, note: str = None) -> int:
        """Tạo đơn hàng mới, tự sinh order_code."""
        # Sinh mã đơn: TLU-2024-XXXX
        rows = Database.execute_query(
            "SELECT COUNT(*)+1 as next_id FROM orders", fetch=True
        )
        next_id = rows[0]['next_id']
        from datetime import datetime
        order_code = f"TLU-{datetime.now().year}-{next_id:04d}"

        return Database.execute_query(
            """INSERT INTO orders
               (order_code, user_id, table_number, subtotal,
                discount, total_amount, payment_method, status, note)
               VALUES (%s,%s,%s,%s,%s,%s,%s,'completed',%s)""",
            (order_code, user_id, table_number, subtotal,
             discount, total_amount, payment_method, note)
        )

    @staticmethod
    def add_items(order_id: int, items: list) -> None:
        """Thêm các món vào đơn — items là list of dict."""
        data = [
            (order_id, i['item_id'], i['item_name'],
             i['unit_price'], i['quantity'], i['subtotal'])
            for i in items
        ]
        Database.execute_many(
            """INSERT INTO order_items
               (order_id, item_id, item_name, unit_price, quantity, subtotal)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            data
        )