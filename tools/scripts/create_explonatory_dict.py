import gzip
import json
import sys

from tqdm import tqdm

from common.utils import wc, get_batch
from context_tools.context_dict import ContextDict

path_in = sys.argv[1]

invert_dict = ContextDict("explanatory_dict")

total = wc(path_in)
with gzip.open(path_in, "rb") as file:
    for batch in get_batch(tqdm(file, total=total), 100):
        items = [json.loads(item) for item in batch]
        keys = [item["key"] for item in items]
        values = [[item["value"]] for item in items]
        invert_dict.put_all(keys=keys, values=values)

