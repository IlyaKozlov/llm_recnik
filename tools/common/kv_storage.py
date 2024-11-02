import abc
import logging
import sqlite3
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class KVStorage(abc.ABC):

    def __init__(self, file_name: str, table_name: str):
        """
        from https://stackoverflow.com/questions/47237807/use-sqlite-as-a-keyvalue-store
        """
        self.table_name = table_name
        self.path = Path(__file__).parent.parent.parent.absolute() / file_name

        logger.debug(f"Save {self.table_name} "
                     f"in file {str(self.path.absolute())}, "
                     f"file {'not' if self.path.exists() else ''}exists")

        self.conn = sqlite3.connect(self.path)
        self.conn.execute(
            f"CREATE TABLE IF NOT EXISTS {self.table_name} (key text unique, value text)"
        )
        size = self.conn.execute(f"SELECT count(*) FROM {self.table_name}").fetchone()[
            0
        ]
        logger.info(f"Size of {self.table_name} dict is {size}")

    def _load(self, key: str) -> Optional[str]:
        value = self.conn.execute(
            f"SELECT value FROM {self.table_name} WHERE key = ?", (key,)
        ).fetchone()
        return value[0] if value is not None else None

    def __upload_to_db(self, key: str, value: str):
        self.conn.execute(
            f"REPLACE INTO {self.table_name} (key, value) VALUES (?,?)", (key, value)
        )

    def _save(self, key: str, value: str):
        self.__upload_to_db(key=key, value=value)
        self.conn.commit()

    def _save_all(self, keys: List[str], values: List[str]):
        for key, value in zip(keys, values):
            self.__upload_to_db(key, value)
        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()
