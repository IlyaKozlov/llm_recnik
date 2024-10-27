import gzip
import json
import shutil
import sys

from tqdm import tqdm

from common.utils import wc, batch
from context_tools.inverted_dict import InvertedDict

path_in = sys.argv[1]

invert_dict = InvertedDict("inverted_dict.sqlite.part")

total = wc(path_in)
with gzip.open(path_in, "rb") as file:
    for batch in batch(tqdm(file, total=total), 100):
        items = [json.loads(item) for item in batch]
        keys = [item["key"] for item in items]
        values = [item["value"] for item in items]
        invert_dict.put_all(keys=keys, values=values)

shutil.move(invert_dict.path, str(invert_dict.path).replace(".part", ""))


