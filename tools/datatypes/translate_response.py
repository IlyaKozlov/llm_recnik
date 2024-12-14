import logging
from typing import Optional, Any, Dict

from pydantic import BaseModel

current_version = "1"

logger = logging.getLogger(__name__)


class TranslateResponse(BaseModel):
    """
    Store previous responses from the LLM, newer versions can change
    the structure, but evert cache must
    1. Be a json serializable
    2. Has a version (str) field
    """

    html: str
    version: str  # this field should be represented in every new version.

    @staticmethod
    def parse(cache: Dict[str, Any]) -> Optional["TranslateResponse"]:
        version = cache.get("version")
        if version is None:
            logging.warning("Version is not found, probably it is a bug")
            return None
        if version == current_version:
            return TranslateResponse.model_validate(cache)
        # here you can add older version parsing, don't forget about unittests then
        else:
            logger.info(f"Version {current_version} does not supported")
            return None
