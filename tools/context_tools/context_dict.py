import json

from common.kv_storage import KVStorage
from common.utils import to_cyrillic, is_latin, to_latin


class ContextDict(KVStorage):

    def __init__(self, table_name: str = "inverted_dict"):
        file_name = f"{table_name}.sqlite"
        super().__init__(file_name=file_name, table_name=table_name)

    def get(self, key: str, default=None):
        latin = is_latin(key)
        key_cyrillic = to_cyrillic(key)
        value = self._load(key_cyrillic)
        if value is None:
            return default
        value = json.loads(value)
        if latin:
            value = [to_latin(v) for v in value]
        return value

    @staticmethod
    def _transform(key: str, value: list):
        key = to_cyrillic(key)
        value = [to_cyrillic(v) for v in value]
        value = json.dumps(value, ensure_ascii=False)
        return key, value

    def put(self, key: str, value: list):
        key, value = self._transform(key, value)
        self._save(key, value)

    def put_all(self, keys: list, values: list):
        transformed_keys = []
        transformed_values = []
        for k, v in zip(keys, values):
            transformed_key, transformed_value = self._transform(k, v)
            transformed_keys.append(transformed_key)
            transformed_values.append(transformed_value)
        self._save_all(transformed_keys, transformed_values)
