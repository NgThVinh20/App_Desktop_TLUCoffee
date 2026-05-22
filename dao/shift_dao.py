from config.database import Database
from typing import List
from datetime import date, timedelta


class ShiftDAO:

    @staticmethod
    def get_by_week(week_start: date) -> List[dict]:
        week_end = week_start + timedelta(days=6)
        return Database.execute_query(
            """SELECT s.*, u.full_name, u.role
               FROM shifts s
               JOIN users u ON s.user_id = u.id
               WHERE s.shift_date BETWEEN %s AND %s
               ORDER BY s.shift_date, s.shift_type, u.full_name""",
            (week_start, week_end), fetch=True
        )

    @staticmethod
    def create(user_id: int, shift_date: date, shift_type: str,
               start_time: str, end_time: str, task_note: str = None) -> int:
        return Database.execute_query(
            """INSERT INTO shifts
               (user_id, shift_date, shift_type, start_time, end_time, task_note)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (user_id, shift_date, shift_type,
             start_time, end_time, task_note)
        )

    @staticmethod
    def delete(shift_id: int) -> None:
        Database.execute_query(
            "DELETE FROM shifts WHERE id = %s", (shift_id,)
        )

    @staticmethod
    def check_conflict(user_id: int, shift_date: date,
                       shift_type: str) -> bool:
        rows = Database.execute_query(
            """SELECT COUNT(*) as cnt FROM shifts
               WHERE user_id=%s AND shift_date=%s AND shift_type=%s""",
            (user_id, shift_date, shift_type), fetch=True
        )
        return rows[0]['cnt'] > 0 if rows else False

    @staticmethod
    def get_all_staff() -> List[dict]:
        return Database.execute_query(
            "SELECT * FROM users WHERE is_active=1 ORDER BY full_name",
            fetch=True
        )