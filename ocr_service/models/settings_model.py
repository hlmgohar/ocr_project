from django.db import models


class Settings(models.Model):
    chat_api_key = models.CharField(max_length=255, null=True, blank=True)
    abby_app_id = models.CharField(max_length=255, null=True, blank=True)
    abby_password = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True, 
        help_text="Timestamp when the settings were created."
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        help_text="Timestamp when the settings were last updated."
    )

    class Meta:
        db_table = 'settings'
        verbose_name = "Setting"
        verbose_name_plural = "Settings"

    def __str__(self):
        return f"Settings: GPT Key={self.gpt_key}, ABBYY App ID={self.abbyy_app_id}"
