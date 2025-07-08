"""Simple SQLite database initializer."""
import sqlite3
from config import Config


def init_database():
    try:
        conn = sqlite3.connect(Config.SQLITE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, entry TEXT)"
        )
        conn.commit()
        print("Database initialized")
    except sqlite3.Error as e:
        print(f"DB init failed: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    init_database()
