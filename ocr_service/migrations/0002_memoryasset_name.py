# Generated by Django 4.2.16 on 2024-11-19 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ocr_service', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='memoryasset',
            name='name',
            field=models.CharField(default='', help_text='Name of the memory asset', max_length=100),
            preserve_default=False,
        ),
    ]
