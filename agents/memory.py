# memory.py

import mysql.connector
from mysql.connector import Error

class MemoryManager:
    def __init__(self, config=None):
        self.config = config
        self.cache = {}

        if self.config:
            try:
                self.conn = mysql.connector.connect(
                    host=self.config.MYSQL_HOST,
                    port=self.config.MYSQL_PORT,
                    user=self.config.MYSQL_USER,
                    password=self.config.MYSQL_PASSWORD,
                    database=self.config.MYSQL_DATABASE
                )
                self._init_table()
            except Error as e:
                print(f"❌ MemoryManager DB connection failed: {e}")
                self.conn = None
        else:
            self.conn = None

    def _init_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS memory (
            id INT AUTO_INCREMENT PRIMARY KEY,
            keyname VARCHAR(255) UNIQUE,
            value TEXT
        )
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()

    def save(self, key: str, value: str):
        self.cache[key] = value
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    "REPLACE INTO memory (keyname, value) VALUES (%s, %s)",
                    (key, value)
                )
                self.conn.commit()
            except Error as e:
                print(f"❌ DB write error: {e}")

    def get(self, key: str, default=None):
        if key in self.cache:
            return self.cache[key]

        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT value FROM memory WHERE keyname=%s", (key,))
                result = cursor.fetchone()
                if result:
                    self.cache[key] = result[0]
                    return result[0]
            except Error as e:
                print(f"❌ DB read error: {e}")

        return default
