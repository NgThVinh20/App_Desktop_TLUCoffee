import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    _instance = None

    @classmethod
    def get_connection(cls):
        if cls._instance is None or not cls._instance.is_connected():
            try:
                cls._instance = mysql.connector.connect(
                    host=os.getenv("DB_HOST", "localhost"),
                    port=int(os.getenv("DB_PORT", 3306)),
                    user=os.getenv("DB_USER", "root"),
                    password=os.getenv("DB_PASSWORD", ""),
                    database=os.getenv("DB_NAME", "cafe_tlu"),
                    charset="utf8mb4"
                )
            except Error as e:
                print(f"Lỗi kết nối MySQL: {e}")
                raise e
        return cls._instance

    @classmethod
    def execute_query(cls, query, params=None, fetch=False):
        """ fetch=True nếu muốn lấy kết quả."""
        conn = cls.get_connection()
        cursor = conn.cursor(dictionary=True)  
        try:
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                conn.commit()
                return cursor.lastrowid  # Trả về id vừa insert
        except Error as e:
            conn.rollback()
            print(f"Lỗi SQL: {e}")
            raise e
        finally:
            cursor.close()

    @classmethod
    def execute_many(cls, query, data_list):
        """Chèn nhiều dòng cùng lúc."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        try:
            cursor.executemany(query, data_list)
            conn.commit()
        except Error as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    @classmethod
    def close(cls):
        if cls._instance and cls._instance.is_connected():
            cls._instance.close()
            cls._instance = None