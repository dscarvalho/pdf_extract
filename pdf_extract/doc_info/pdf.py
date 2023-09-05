import json
import pandas
from typing import List
from zipfile import ZipFile
from collections import OrderedDict

from .base import DocumentInfo


class PDFDocumentInfo(DocumentInfo):
    def __init__(self, extr_path):
        self.source = ZipFile(extr_path)
        with self.source.open("structuredData.json") as struct_file:
            self.struct_data = json.load(struct_file)

    def get_sections(self) -> OrderedDict[str, List[str]]:
        sections = OrderedDict()
        cur_section = ""
        for e in self.struct_data["elements"]:
            if ("Text" in e):
                if (e["Path"].startswith("//Document/H")):
                    cur_section = e["Text"]
                    sections[cur_section] = list()
                elif (cur_section and e["Path"].startswith("//Document/P")):
                    sections[cur_section].append(e["Text"])

        return sections

    def get_tables(self) -> List[pandas.DataFrame]:
        tables = list()
        for e in self.struct_data["elements"]:
            if (e["Path"].startswith("//Document/Table") and len(e["Path"].split("/")) == 4):
                with self.source.open(e["filePaths"][0]) as table_file:
                    table = pandas.read_csv(table_file)
                    tables.append(table)

        return tables

    def get_references(self) -> List[str]:
        capture = False
        labels = ["references", "bibliography"]
        refs = []
        for e in self.struct_data["elements"]:
            if ("Text" in e):
                if (e["Path"].startswith("//Document/H") and sum([e["Text"].lower().startswith(l) for l in labels])):
                    capture = True
                elif (capture):
                    if (e["Path"].startswith("//Document/H")):
                        capture = False
                    elif (len(e["Text"]) > DocumentInfo.MINIMUM_REF_LEN):
                        refs.append(e["Text"].strip())

        return refs





