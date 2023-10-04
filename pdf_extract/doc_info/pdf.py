import json
import logging
import pandas as pd
from typing import List, Tuple
from zipfile import ZipFile

from .base import DocumentInfo

REF_SCORE_THRESHOLD = 0.85


class PDFDocumentInfo(DocumentInfo):
    def __init__(self, extr_path):
        self.source = ZipFile(extr_path)
        with self.source.open("structuredData.json") as struct_file:
            self.struct_data = json.load(struct_file)

    @property
    def title(self) -> str:
        title = ""
        for e in self.struct_data["elements"]:
            if (e["Path"] == "//Document/Title"):
                title = e["Text"]
                break

        return title

    @property
    def sections(self) -> List[dict]:
        sections = list()
        cur_section = ""
        for e in self.struct_data["elements"]:
            if ("Text" in e):
                if (e["Path"].startswith("//Document/H")):
                    cur_section = e["Text"]
                    sections.append({"title": cur_section, "content": list()})
                elif (cur_section and (e["Path"].startswith("//Document/P") or e["Path"].startswith("//Document/L"))):
                    sections[-1]["content"].append(e["Text"])

        return sections

    @property
    def tables(self) -> List[pd.DataFrame]:
        tables = list()
        for e in self.struct_data["elements"]:
            if (e["Path"].startswith("//Document/Table") and len(e["Path"].split("/")) == 4):
                with self.source.open(e["filePaths"][0]) as table_file:
                    try:
                        table = pd.read_csv(table_file, dtype=str)
                        tables.append(table)
                    except pd.errors.ParserError:
                        logging.error(f"Error parsing table {e['Path']} at {e['filePaths'][0]}")

        return tables

    @property
    def references(self) -> List[str]:
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





