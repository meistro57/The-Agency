"""Simple MySQL database initializer."""
import mysql.connector
from mysql.connector import Error
from config import Config


def init_database():
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE}")
        cursor.execute(f"USE {Config.MYSQL_DATABASE}")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS logs (" 
            "id INT AUTO_INCREMENT PRIMARY KEY, entry TEXT)"
        )
        conn.commit()
        print("Database initialized")
    except Error as e:
        print(f"DB init failed: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    init_database()
