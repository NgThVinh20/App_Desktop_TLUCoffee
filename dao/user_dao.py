import bcrypt
from config.database import Database
from typing import Optional, List

class UserDAO:

    @staticmethod
    def get_by_email(email: str) -> Optional[dict]:
        rows = Database.execute_query(
            "SELECT * FROM users WHERE email = %s AND is_active = 1",
            (email,), fetch=True
        )
        return rows[0] if rows else None

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    @staticmethod
    def get_all() -> List[dict]:
        return Database.execute_query(
            """SELECT u.*,
                      CASE u.role
                          WHEN 'admin'   THEN 'Admin'
                          WHEN 'manager' THEN 'Quản lý'
                          WHEN 'cashier' THEN 'Thu ngân'
                          WHEN 'barista' THEN 'Barista'
                          WHEN 'server'  THEN 'Phục vụ'
                          WHEN 'kitchen' THEN 'Bếp'
                      END as role_display
               FROM users u
               ORDER BY u.full_name""",
            fetch=True
        )

    @staticmethod
    def get_by_id(user_id: int) -> Optional[dict]:
        rows = Database.execute_query(
            "SELECT * FROM users WHERE id = %s", (user_id,), fetch=True
        )
        return rows[0] if rows else None

    @staticmethod
    def create(full_name: str, email: str, password: str,
               role: str, phone: str = None) -> int:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        return Database.execute_query(
            """INSERT INTO users (full_name, email, password_hash, role, phone)
               VALUES (%s, %s, %s, %s, %s)""",
            (full_name, email, hashed, role, phone)
        )

    @staticmethod
    def update(user_id: int, full_name: str, role: str,
               phone: str = None, is_active: int = 1) -> None:
        Database.execute_query(
            """UPDATE users SET full_name=%s, role=%s, phone=%s, is_active=%s
               WHERE id=%s""",
            (full_name, role, phone, is_active, user_id)
        )

    @staticmethod
    def update_last_login(user_id: int) -> None:
        Database.execute_query(
            "UPDATE users SET last_login = NOW() WHERE id = %s",
            (user_id,)
        )

    @staticmethod
    def search(keyword: str) -> List[dict]:
        kw = f"%{keyword}%"
        return Database.execute_query(
            """SELECT * FROM users
               WHERE full_name LIKE %s OR email LIKE %s OR role LIKE %s""",
            (kw, kw, kw), fetch=True
        )