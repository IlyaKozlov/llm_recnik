import json
import sqlite3
from pathlib import Path

from common.utils import to_cyrillic, is_latin, to_latin


class InvertedDict:

    def __init__(self, file_name: str = "inverted_dict.sqlite"):
        """
        from https://stackoverflow.com/questions/47237807/use-sqlite-as-a-keyvalue-store
        """
        self.path = Path(__file__).parent.parent.parent.absolute() / file_name
        self.conn = sqlite3.connect(self.path)
        self.conn.execute("CREATE TABLE IF NOT EXISTS kv (key text unique, value text)")
        size = self.conn.execute('SELECT count(*) FROM kv').fetchone()[0]
        print(f"Size of inverted dict is {size}")

    def close(self):
        self.conn.commit()
        self.conn.close()

    def get(self, key: str, default=None):
        latin = is_latin(key)
        key_cyrillic = to_cyrillic(key)
        value = self.conn.execute('SELECT value FROM kv WHERE key = ?', (key_cyrillic,)).fetchone()
        if value is None:
            return default
        else:
            value = value[0]
        value = json.loads(value)
        if latin:
            value = [to_latin(v) for v in value]
        return value

    def _put_one(self, key: str, value):
        key = to_cyrillic(key)
        value = to_cyrillic(value)
        value = json.dumps(value, ensure_ascii=False)
        self.conn.execute('REPLACE INTO kv (key, value) VALUES (?,?)', (key, value))

    def put(self, key: str, value: str):
        self._put_one(key, value)
        self.conn.commit()

    def put_all(self, keys: list, values: list):
        for key, value in zip(keys, values):
            self._put_one(key, value)
        self.conn.commit()
