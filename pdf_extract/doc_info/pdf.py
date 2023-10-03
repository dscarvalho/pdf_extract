import json
import pandas as pd
from typing import List
from zipfile import ZipFile
from collections import OrderedDict

from .base import DocumentInfo

REF_SCORE_THRESHOLD = 0.85


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
                elif (cur_section and (e["Path"].startswith("//Document/P") or e["Path"].startswith("//Document/L"))):
                    sections[cur_section].append(e["Text"])

        return sections

    def get_tables(self) -> List[pd.DataFrame]:
        tables = list()
        for e in self.struct_data["elements"]:
            if (e["Path"].startswith("//Document/Table") and len(e["Path"].split("/")) == 4):
                with self.source.open(e["filePaths"][0]) as table_file:
                    table = pd.read_csv(table_file, dtype=str)
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

        if (not refs):
            doc_lists = dict()
            for e in self.struct_data["elements"]:
                if ("Text" in e and e["Path"].startswith("//Document/L")):
                    if (e["Path"].split("/")[3] not in doc_lists):
                        doc_lists[e["Path"].split("/")[3]] = list()
                    if (len(e["Text"]) > DocumentInfo.MINIMUM_REF_LEN):
                        doc_lists[e["Path"].split("/")[3]].append(e["Text"].strip())

            ref_scores = {lt: sum([txt[-5:].strip().replace(".", "").isnumeric() for txt in doc_lists[lt]]) / len(doc_lists[lt])
                          for lt in doc_lists}
            if (len(ref_scores.items()) > 0):
                max_score = max(ref_scores.items(), key=lambda x: x[1])
                if (max_score[1] > REF_SCORE_THRESHOLD):
                    refs = doc_lists[max_score[0]]

        return refs





