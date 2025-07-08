# memory.py

import os
import threading
import logging
import sqlite3


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class MemoryManager:
    """
    Handles in-memory and optional SQLite-backed key-value storage.
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
                db_path = getattr(self.config, "SQLITE_PATH", "the_agency.db")
                self.conn = sqlite3.connect(db_path, check_same_thread=False)
                self._init_table()
                logging.info(f"✅ MemoryManager connected to SQLite at {db_path}.")
            except sqlite3.Error as e:
                logging.error(f"❌ MemoryManager DB connection failed: {e}")
                self.conn = None

    def _init_table(self, table_name="memory"):
        """
        Initializes the SQLite table if it doesn't exist.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} (keyname TEXT PRIMARY KEY, value TEXT)"
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"❌ Failed to create memory table: {e}")

    def save(self, key: str, value: str):
        """
        Saves a key-value pair to memory and optionally to SQLite.
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
                    "INSERT OR REPLACE INTO memory (keyname, value) VALUES (?, ?)",
                    (key, value)
                )
                self.conn.commit()
            except sqlite3.Error as e:
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
                cursor.execute("SELECT value FROM memory WHERE keyname=?", (key,))
                result = cursor.fetchone()
                if result:
                    with self.lock:
                        self.cache[key] = result[0]
                    return result[0]
            except sqlite3.Error as e:
                logging.error(f"❌ DB read error for '{key}': {e}")

        return default

    def close_connection(self):
        """
        Closes the SQLite connection cleanly.
        """
        if self.conn:
            try:
                self.conn.close()
                logging.info("🛑 MemoryManager DB connection closed.")
            except sqlite3.Error as e:
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
