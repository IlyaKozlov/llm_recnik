import hashlib
import os
from pathlib import Path
from typing import Optional

path = (Path(__file__).parent / "resources" / "tokens").absolute()


def secret2hash(secret: str) -> str:
    return str(hashlib.sha256(secret.encode()).hexdigest())


def add_token(secret: str):
    if check_access(secret):
        return
    token = secret2hash(secret)
    with open(path, "a") as f:
        f.write(f"{token}\n")


def check_access(secret: Optional[str]) -> bool:
    if os.environ.get("CHECK_ACCESS", "true").lower() == "false":
        # Don't need to check, access is not restricted.
        return True
    if secret is None:
        return False
    if not path.is_file():
        return False
    token = secret2hash(secret)
    with open(path, "r") as f:
        for line in f:
            if token == line.strip():
                return True
    return False
