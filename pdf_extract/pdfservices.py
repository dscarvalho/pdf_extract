import logging
import os.path
import json
import hashlib
from typing import Dict

from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_pdf_options import ExtractPDFOptions
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_renditions_element_type import ExtractRenditionsElementType
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfops.options.extractpdf.table_structure_type import TableStructureType
from adobe.pdfservices.operation.execution_context import ExecutionContext
from adobe.pdfservices.operation.io.file_ref import FileRef
from adobe.pdfservices.operation.pdfops.extract_pdf_operation import ExtractPDFOperation

from .doc_info.base import DocumentInfo
from .doc_info.pdf import PDFDocumentInfo


logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class PDFServices:
    def __init__(self, base_path: str = None, credentials: Dict[str, str] = None):
        if (base_path):
            self.base_path = base_path
        else:
            self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Initial setup, create credentials instance.
        if (credentials):
            client_id = credentials["client_id"]
            client_secret = credentials["client_secret"]
        elif (os.path.exists("pdfservices-api-credentials.json")):
            with open(self.base_path + "/pdfservices-api-credentials.json") as cred_file:
                credentials = json.load(cred_file)
                client_id = credentials["client_credentials"]["client_id"]
                client_secret = credentials["client_credentials"]["client_secret"]
        else:
            client_id = os.getenv('PDF_SERVICES_CLIENT_ID')
            client_secret = os.getenv('PDF_SERVICES_CLIENT_SECRET')

        self.credentials = Credentials.service_principal_credentials_builder(). \
            with_client_id(client_id). \
            with_client_secret(client_secret). \
            build()

    def extract(self, file_path: str) -> DocumentInfo:
        with open(file_path, "rb") as input_file:
            input_hash = hashlib.md5(input_file.read()).hexdigest()
        if (not os.path.exists(self.base_path + f"/output/{input_hash}.zip")):
            try:
                # Create an ExecutionContext using credentials and create a new operation instance.
                execution_context = ExecutionContext.create(self.credentials)
                extract_pdf_operation = ExtractPDFOperation.create_new()

                # Set operation input from a source file.
                source = FileRef.create_from_local_file(file_path)
                extract_pdf_operation.set_input(source)

                # Build ExtractPDF options and set them into the operation
                extract_pdf_options: ExtractPDFOptions = ExtractPDFOptions.builder() \
                    .with_elements_to_extract([ExtractElementType.TEXT, ExtractElementType.TABLES]) \
                    .with_elements_to_extract_renditions([ExtractRenditionsElementType.TABLES,
                                                          ExtractRenditionsElementType.FIGURES]) \
                    .with_get_char_info(True) \
                    .with_table_structure_format(TableStructureType.CSV) \
                    .build()
                extract_pdf_operation.set_options(extract_pdf_options)

                # Execute the operation.
                result: FileRef = extract_pdf_operation.execute(execution_context)

                # Save the result to the specified location.
                result.save_as(self.base_path + f"/output/{input_hash}.zip")

            except (ServiceApiException, ServiceUsageException, SdkException):
                logging.exception("Exception encountered while executing operation")

        return PDFDocumentInfo(self.base_path + f"/output/{input_hash}.zip")
