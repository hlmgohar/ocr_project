from django.urls import path
from ocr_service.views import ConvertPDFToDocxAPI, DownloadOriginalDocxAPI, DownloadReplacedDocxAPI

urlpatterns = [
    path('extract-text/', ConvertPDFToDocxAPI.as_view(), name='convert_pdf_to_docx'),
    path('download-generated-docx/', DownloadOriginalDocxAPI.as_view(), name='download_original_docx'),
    path('download-replaced-docx/', DownloadReplacedDocxAPI.as_view(), name='download_replaced_docx'),
]
