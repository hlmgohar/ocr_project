from django.urls import path
from ocr_service.views.ocr_views import ConvertPDFToDocxAPI, DownloadOriginalDocxAPI, DownloadReplacedDocxAPI
from ocr_service.views.memory_views import TranslationMemoryUploadAPI, MemoryListAPI, MemoryAssetListAPI, MemoryListAPIById

urlpatterns = [
    path('extract-text/', ConvertPDFToDocxAPI.as_view(), name='convert_pdf_to_docx'),
    path('download-generated-docx/', DownloadOriginalDocxAPI.as_view(), name='download_original_docx'),
    path('download-replaced-docx/', DownloadReplacedDocxAPI.as_view(), name='download_replaced_docx'),
    
    # MEMORY ASSET
    path('memory/assets/list/', MemoryAssetListAPI.as_view(), name='memory-asset-list'),

    # MEMORY_VIEW
    path('memory/upload/', TranslationMemoryUploadAPI.as_view(), name='upload-memory'),
    path('memory/list/', MemoryListAPI.as_view(), name='memory-list'),
    path('memory/list/<int:id>/', MemoryListAPIById.as_view(), name='memory-list'),
]
