import logging
import os.path
import json
import hashlib
from typing import Dict

import adobe.pdfservices.operation.pdf_services as adobe_pdfservices
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_renditions_element_type import ExtractRenditionsElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.table_structure_type import TableStructureType

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
        elif (os.path.exists(self.base_path + "/pdfservices-api-credentials.json")):
            with open(self.base_path + "/pdfservices-api-credentials.json") as cred_file:
                credentials = json.load(cred_file)
                client_id = credentials["client_credentials"]["client_id"]
                client_secret = credentials["client_credentials"]["client_secret"]
        else:
            client_id = os.getenv('PDF_SERVICES_CLIENT_ID')
            client_secret = os.getenv('PDF_SERVICES_CLIENT_SECRET')

        self.credentials = ServicePrincipalCredentials(client_id=client_id, client_secret=client_secret)

    def extract(self, file_path: str) -> DocumentInfo:
        with open(file_path, "rb") as input_file:
            input_hash = hashlib.md5(input_file.read()).hexdigest()
        if (not os.path.exists(self.base_path + f"/output/{input_hash}.zip")):
            try:
                pdf_services = adobe_pdfservices.PDFServices(credentials=self.credentials)
                with open(file_path, "rb") as pdf_file:
                    source = pdf_file.read()

                input_asset = pdf_services.upload(input_stream=source, mime_type=PDFServicesMediaType.PDF)
                extract_params = ExtractPDFParams(
                    elements_to_extract=[ExtractElementType.TEXT, ExtractElementType.TABLES],
                    elements_to_extract_renditions=[ExtractRenditionsElementType.TABLES,
                                                    ExtractRenditionsElementType.FIGURES],
                    table_structure_type=TableStructureType.CSV
                )
                extract_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_params)
                location = pdf_services.submit(extract_job)
                response = pdf_services.get_job_result(location, ExtractPDFResult)
                result_asset = response.get_result().get_resource()
                stream_asset = pdf_services.get_content(result_asset)

                if (not os.path.exists(self.base_path + f"/output")):
                    os.makedirs(self.base_path + f"/output", exist_ok=True)
                with open(self.base_path + f"/output/{input_hash}.zip", "wb") as output_file:
                    output_file.write(stream_asset.get_input_stream())

            except (ServiceApiException, ServiceUsageException, SdkException):
                logging.exception("Exception encountered while executing operation")
                return None

        return PDFDocumentInfo(self.base_path + f"/output/{input_hash}.zip")
