from django.db import models
from .memory_asset_model import MemoryAsset

class Memory(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the memory")
    source_language = models.CharField(max_length=50, help_text="Source language of the text")
    target_language = models.CharField(max_length=50, help_text="Target language of the text")
    source_text = models.TextField(help_text="Original text in the source language")
    target_text = models.TextField(help_text="Translated text in the target language")
    memory_asset = models.ForeignKey(
        MemoryAsset,
        related_name="memories",
        on_delete=models.CASCADE,
        help_text="The memory asset to which this memory belongs"
    )

    class Meta:
        db_table = 'translation_memory'

    def __str__(self):
        return f"Memory: {self.name} ({self.source_language} -> {self.target_language})"