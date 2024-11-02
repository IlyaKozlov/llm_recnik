from common.kv_storage import KVStorage
from datatypes.translate_response import TranslateResponse


class Cache(KVStorage):

    def __init__(self):
        super().__init__(file_name="cache.sqlite", table_name="cache")

    def get(self, key: str, default=None) -> TranslateResponse:
        value_json = self._load(key=key)
        if value_json is None:
            return default
        else:
            return TranslateResponse.model_validate_json(value_json)

    def put(self, key: str, value: TranslateResponse):
        value_json = value.model_dump_json()
        self._save(key=key, value=value_json)
