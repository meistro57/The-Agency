# memory.py

import os
import threading
import logging
import mysql.connector
from mysql.connector import Error


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class MemoryManager:
    """
    Handles in-memory and optional MySQL-backed key-value storage.
    Automatically falls back to memory-only mode if DB connection fails.
    """

    def __init__(self, config=None):
        self.config = config
        self.cache = {}
        self.lock = threading.Lock()
        self.conn = None
        self.search_index = {}

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
                logging.info("✅ MemoryManager connected to MySQL.")
            except Error as e:
                logging.error(f"❌ MemoryManager DB connection failed: {e}")
                self.conn = None

    def _init_table(self, table_name="memory"):
        """
        Initializes the MySQL table if it doesn't exist.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    keyname VARCHAR(255) UNIQUE,
                    value TEXT
                )
            """)
            self.conn.commit()
        except Error as e:
            logging.error(f"❌ Failed to create memory table: {e}")

    def save(self, key: str, value: str):
        """
        Saves a key-value pair to memory and optionally to MySQL.
        """
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Key must be a non-empty string.")

        with self.lock:
            self.cache[key] = value
            self.search_index[key] = str(value).lower()

        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    "REPLACE INTO memory (keyname, value) VALUES (%s, %s)",
                    (key, value)
                )
                self.conn.commit()
            except Error as e:
                logging.error(f"❌ DB write error for '{key}': {e}")

    def get(self, key: str, default=None):
        """
        Retrieves a value by key from memory or database.
        """
        with self.lock:
            if key in self.cache:
                return self.cache[key]

        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT value FROM memory WHERE keyname=%s", (key,))
                result = cursor.fetchone()
                if result:
                    with self.lock:
                        self.cache[key] = result[0]
                    return result[0]
            except Error as e:
                logging.error(f"❌ DB read error for '{key}': {e}")

        return default

    def close_connection(self):
        """
        Closes the MySQL connection cleanly.
        """
        if self.conn:
            try:
                self.conn.close()
                logging.info("🛑 MemoryManager DB connection closed.")
            except Error as e:
                logging.error(f"❌ Error closing DB connection: {e}")

    def semantic_search(self, query: str, top_k: int = 5):
        """Return keys that semantically match the query."""
        results = []
        q = query.lower()
        with self.lock:
            for key, text in self.search_index.items():
                score = self._similarity(q, text)
                results.append((score, key))
        results.sort(reverse=True)
        return [k for _, k in results[:top_k]]

    def _similarity(self, a: str, b: str) -> float:
        from difflib import SequenceMatcher
        return SequenceMatcher(None, a, b).ratio()

    def __del__(self):
        self.close_connection()
