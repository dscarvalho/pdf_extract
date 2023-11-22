import sys
import os
import json
from pdf_extract.pdfservices import PDFServices


def main(argv):
    pdfserv = PDFServices()
    filepaths = argv[1:]
    for path in filepaths:
        if (path.endswith(".pdf")):
            doc_info = pdfserv.extract(path)
            fname = path.split(os.path.sep)[-1].replace(".pdf", "")
            with open(fname + ".json", "w") as res_file:
                json.dump({"title": doc_info.title,
                           "sections": doc_info.sections,
                           "tables": [t.astype("str").to_dict("records") for t in doc_info.tables],
                           "references": doc_info.references}, res_file, indent=2)


if __name__ == '__main__':
    main(sys.argv)

