# memory_manager.py

import logging
import threading
import mysql.connector
from mysql.connector import Error
from typing import Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class MemoryManager:
    """
    Hybrid memory interface with in-memory caching and optional MySQL persistence.
    """

    def __init__(self, config=None, table_name="memory"):
        """
        Initializes the memory manager.

        Args:
            config: Configuration object with MySQL connection details.
            table_name (str): Name of the table to store memory in MySQL.
        """
        self.config = config
        self.conn = None
        self.table = table_name
        self.cache = {}
        self.lock = threading.Lock()

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
                logger.info("✅ MemoryManager connected to MySQL.")
            except Error as e:
                logger.error(f"❌ MemoryManager DB connection failed: {e}")
                self.conn = None

    def _init_table(self):
        """
        Creates the memory table if it doesn't exist.
        """
        if not self.conn:
            return
        try:
            query = f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                keyname VARCHAR(255) UNIQUE,
                value TEXT
            )
            """
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()
            logger.info(f"📦 Memory table '{self.table}' ensured.")
        except Error as e:
            logger.error(f"❌ Failed to initialize memory table: {e}")

    def save(self, key: str, value: str):
        """
        Stores a key-value pair in memory and optionally in MySQL.

        Args:
            key (str): The memory key.
            value (str): The data to store.
        """
        with self.lock:
            self.cache[key] = value

        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    f"REPLACE INTO {self.table} (keyname, value) VALUES (%s, %s)",
                    (key, value)
                )
                self.conn.commit()
            except Error as e:
                logger.error(f"❌ DB write error for key '{key}': {e}")

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieves a value by key, first from cache, then MySQL.

        Args:
            key (str): The key to look up.
            default (str): Value to return if key is not found.

        Returns:
            str | None: Value if found, else default.
        """
        with self.lock:
            if key in self.cache:
                return self.cache[key]

        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute(f"SELECT value FROM {self.table} WHERE keyname = %s", (key,))
                result = cursor.fetchone()
                if result:
                    value = result[0]
                    with self.lock:
                        self.cache[key] = value
                    return value
            except Error as e:
                logger.error(f"❌ DB read error for key '{key}': {e}")

        return default

    def close(self):
        """
        Closes the database connection.
        """
        if self.conn:
            self.conn.close()
            logger.info("🛑 MySQL connection closed.")

    def __del__(self):
        self.close()