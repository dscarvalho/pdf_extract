import json
import pandas
from typing import List
from zipfile import ZipFile
from collections import OrderedDict

from .base import DocumentInfo


class HTMLDocumentInfo(DocumentInfo):
    def __init__(self, extr_path):
        self.source = ZipFile(extr_path)
        with self.source.open("structuredData.json") as struct_file:
            self.struct_data = json.load(struct_file)

    def get_sections(self) -> OrderedDict[str, List[str]]:
        pass

    def get_tables(self) -> List[pandas.DataFrame]:
        pass

    def get_references(self) -> List[str]:
        pass