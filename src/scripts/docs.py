import os
from pydoc import doc
from langchain_docling import DoclingLoader
import constants
from pprint import pp
import json as json_lib

FILE_PATH = [
    os.path.join(
        constants.storage_path,
        "Manual_livreto-CENTRAL_FIT_CONNECT_portugues_espanhol_rev00-1.pdf",
    )
]

loader = DoclingLoader(file_path=FILE_PATH)

docs = loader.load()

json = {"data": [doc.model_dump() for doc in docs]}
path = os.path.join(constants.tmp_path, "output.json")
with open(path, "w") as f:
    json_lib.dump(json, f, indent=4)
