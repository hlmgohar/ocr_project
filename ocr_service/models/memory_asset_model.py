from django.db import models


class MemoryAsset(models.Model):
    name= models.CharField(max_length=100, help_text="Name of the memory asset", default='')
    source_language = models.CharField(max_length=50, help_text="Source language of the memory asset")
    target_languages = models.TextField(help_text="Comma-separated target languages")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the memory asset was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the memory asset was last updated")

    class Meta:
        db_table = 'memory_assets'

    def __str__(self):
        return f"MemoryAsset: {self.source_language} -> {self.target_languages}"