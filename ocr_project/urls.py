from django.urls import path
from ocr_service.views.ocr_views import ConvertPDFToDocxAPI, DownloadOriginalDocxAPI, DownloadReplacedDocxAPI,GetTaskStatusAPI,TranslateRecordsView, SaveApplicationSettings
from ocr_service.views.memory_views import TranslationMemoryUploadAPI, MemoryListAPI, MemoryAssetListAPI, MemoryListAPIById, MemoryDeleteAPI, MemoryUpdateAPI, MemoryBulkDeleteAPI, MemoryUpdateAPIBySourceAndTargetLanguage, MemoryExportAPIById, DuplicateMemory, GetMemoryBySource

urlpatterns = [
    path('extract-text/', ConvertPDFToDocxAPI.as_view(), name='convert_pdf_to_docx'),
    path('download-generated-docx/', DownloadOriginalDocxAPI.as_view(), name='download_original_docx'),
    path('download-replaced-docx/', DownloadReplacedDocxAPI.as_view(), name='download_replaced_docx'),
    # MEMORY ASSET
    path('memory/assets/list/', MemoryAssetListAPI.as_view(), name='memory-asset-list'),
    path('memory/tasks/', GetTaskStatusAPI.as_view(), name='get-task-status'),
    # MEMORY_VIEW
    path('memory/upload/', TranslationMemoryUploadAPI.as_view(), name='upload-memory'),
    path('memory/list/', MemoryListAPI.as_view(), name='memory-list'),
    path('memory/list/<int:id>/', MemoryListAPIById.as_view(), name='memory-list'),
    path('memory/assets/export/<int:id>/', MemoryExportAPIById.as_view(), name='memory-list'),
    path('memory/assets/delete/<int:memory_asset_id>/', MemoryDeleteAPI.as_view(), name='delete_memory'),
    path('memory/update/', MemoryUpdateAPI.as_view(), name='memory-update'),
    path('memory/bulk-delete/', MemoryBulkDeleteAPI.as_view(), name='memory-bulk-delete'),
    path('memory/bulk-update/', MemoryUpdateAPIBySourceAndTargetLanguage.as_view(), name='memory-bulk-update'),
    
    path('memory/translation/', TranslateRecordsView.as_view(), name='memory-bulk-translate'),
    path('memory/duplicate/<int:memory_asset_id>/', DuplicateMemory.as_view(), name='memory-duplicate'),
    
    path('memory/get-by-source-text/', GetMemoryBySource.as_view(), name='memory-duplicate'),
    
    path('memory/settings/', SaveApplicationSettings.as_view(), name='memory-duplicate')
]
