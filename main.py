import sys
import json
from pdf_extract.pdfservices import PDFServices


def main(argv):
    pdfserv = PDFServices()
    doc_info = pdfserv.extract(argv[1])

    with open("references.json", "w") as res_file:
        json.dump(doc_info.references, res_file, indent=2)

    with open("sections.json", "w") as res_file:
        json.dump(doc_info.sections, res_file, indent=2)

    print(doc_info.tables[1])

    with open("docinfo.json", "w") as res_file:
        json.dump({"title": doc_info.title,
                   "sections": doc_info.sections,
                   "tables": [t.astype("str").to_dict("records") for t in doc_info.tables],
                   "references": doc_info.references}, res_file, indent=2)


if __name__ == '__main__':
    main(sys.argv)

