# Generated by Django 4.2.16 on 2024-12-04 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ocr_service', '0003_alter_memoryasset_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_api_key', models.CharField(blank=True, max_length=255, null=True)),
                ('abby_app_id', models.CharField(blank=True, max_length=255, null=True)),
                ('abby_password', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp when the settings were created.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Timestamp when the settings were last updated.')),
            ],
            options={
                'verbose_name': 'Setting',
                'verbose_name_plural': 'Settings',
                'db_table': 'settings',
            },
        ),
    ]