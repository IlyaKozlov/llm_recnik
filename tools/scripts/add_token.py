import sys

from token_utils import add_token

for secret in sys.argv[1:]:
    add_token(secret=secret)
