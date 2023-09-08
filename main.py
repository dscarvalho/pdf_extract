import sys
import json
from pdf_extract.pdfservices import PDFServices


def main(argv):
    pdfserv = PDFServices()
    doc_info = pdfserv.extract(argv[1])

    with open("references.json", "w") as res_file:
        json.dump(doc_info.get_references(), res_file, indent=2)

    with open("sections.json", "w") as res_file:
        json.dump(doc_info.get_sections(), res_file, indent=2)

    print(doc_info.get_tables()[1])


if __name__ == '__main__':
    main(sys.argv)

