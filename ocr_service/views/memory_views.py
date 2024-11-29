from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from lxml import etree
import pandas as pd
from ocr_service.models.memory_models import Memory, MemoryAsset
from xlsx2csv import Xlsx2csv
from django.http import HttpResponse
from io import StringIO
import csv

LANGUAGE_CODES = {
    "French": "fr",
    "Arabic": "ar",
    "Turkish": "tr",
    "English": "en",
}

class TranslationMemoryUploadAPI(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        source_language = request.data.get('source_language')
        name = request.data.get('name')
        target_languages = request.data.get('target_language')  # Comma-separated target languages
        file = request.FILES.get('file')

        # Validate payload
        if not source_language or not target_languages or not name:
            return Response(
                {"error": "name, source_language, and target_language are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parse target languages
        target_languages = [lang.strip() for lang in target_languages.split(',')]

        # Check if MemoryAsset already exists
        memory_asset, created = MemoryAsset.objects.get_or_create(
            source_language=source_language,
            target_languages=",".join(target_languages),
            defaults={'name': name}
        )

        if not created:
            # Update the name of the existing MemoryAsset
            memory_asset.name = name
            memory_asset.save()

        # If no file is provided, only update the MemoryAsset name and return the response
        if not file:
            return Response(
                {"message": "MemoryAsset updated successfully!", "memory_asset_id": memory_asset.id},
                status=status.HTTP_200_OK
            )

        # If a file is provided, validate and process it
        file_type = file.name.split('.')[-1].lower()
        if file_type not in ['tmx', 'xlsx']:
            return Response(
                {"error": "Unsupported file type. Only TMX and XLSX are allowed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Process file
        try:
            if file_type == 'tmx':
                self.process_tmx(file, source_language, target_languages, name, memory_asset)
            elif file_type == 'xlsx':
                self.process_xlsx(file, source_language, target_languages, name, memory_asset)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {"message": "Translations saved successfully!", "memory_asset_id": memory_asset.id},
            status=status.HTTP_201_CREATED
        )


    def process_tmx(self, file, source_language, target_languages, name, memory_asset):
        """Process TMX file and update or save translations for multiple target languages."""
        try:
            tree = etree.parse(file)
            root = tree.getroot()

            # TMX namespace
            namespace = {'xml': 'http://www.w3.org/XML/1998/namespace'}

            for tu_number, tu in enumerate(root.findall('.//tu'), start=1):  # Iterate through translation units
                source_text = None
                target_texts = {lang: None for lang in target_languages}

                for tuv_number, tuv in enumerate(tu.findall('./tuv'), start=1):  # Translation unit variants
                    lang = tuv.attrib.get(f'{{{namespace["xml"]}}}lang')
                    seg = tuv.find('./seg')

                    if seg is not None:
                        # Clean the text content
                        cleaned_text = etree.tostring(seg, encoding='unicode', method='text').strip()

                        if lang == source_language:
                            source_text = cleaned_text
                        elif lang in target_languages:
                            target_texts[lang] = cleaned_text

                # Save or update translations for each target language
                for lang, target_text in target_texts.items():
                    if source_text and target_text:
                        try:
                            Memory.objects.update_or_create(
                                name=name,
                                source_language=source_language,
                                target_language=lang,
                                source_text=source_text,
                                defaults={
                                    'target_text': target_text,
                                    'memory_asset': memory_asset
                                }
                            )
                        except Exception as db_error:
                            print(f"Error saving TU #{tu_number} for target language {lang}: {db_error}")
                    else:
                        print(f"Skipping TU #{tu_number} for target language {lang}: Missing source or target text")

        except Exception as e:
            print(f"Error processing TMX file: {e}")
            raise ValueError(f"Error processing TMX file: {e}")

    def process_xlsx(self, file, source_language, target_languages, name, memory_asset):
        """Process XLSX file and update or save translations for multiple target languages."""
        try:
            # Convert XLSX to CSV
            csv_output = StringIO()
            Xlsx2csv(file, outputencoding="utf-8").convert(csv_output)

            # Load CSV into Pandas DataFrame
            csv_output.seek(0)
            df = pd.read_csv(csv_output)

            # Verify columns
            if source_language not in df.columns:
                raise ValueError(f"Source language column '{source_language}' not found in the file.")
            for lang in target_languages:
                if lang not in df.columns:
                    raise ValueError(f"Target language column '{lang}' not found in the file.")

            # Process rows
            for index, row in df.iterrows():
                source_text = row.get(source_language)
                target_texts = {lang: row.get(lang) for lang in target_languages}

                source_text = str(source_text).strip() if pd.notna(source_text) else None
                if source_text:
                    for lang, target_text in target_texts.items():
                        target_text = str(target_text).strip() if pd.notna(target_text) else None
                        if target_text:
                            try:
                                Memory.objects.update_or_create(
                                    name=name,
                                    source_language=source_language,
                                    target_language=lang,
                                    source_text=source_text,
                                    defaults={
                                        'target_text': target_text,
                                        'memory_asset': memory_asset,
                                    }
                                )
                                print(f"Saved or updated Row #{index + 1} for target language '{lang}'")
                            except Exception as db_error:
                                print(f"Error saving or updating row #{index + 1} for target language '{lang}': {db_error}")
                        else:
                            print(f"Skipping Row #{index + 1} for target language '{lang}': Missing target text")
                else:
                    print(f"Skipping Row #{index + 1}: Missing source text")
        except Exception as e:
            print(f"Error processing XLSX file: {e}")
            raise ValueError(f"Error processing XLSX file: {e}")

class MemoryListAPI(APIView):
    def get(self, request, *args, **kwargs):
        # Fetch all memory records
        memories = Memory.objects.all().values(
            'id', 'source_language', 'target_language', 
        )

        return Response(
            {"data": list(memories)},
            status=status.HTTP_200_OK
        )

class MemoryListAPIById(APIView):
    def get(self, request, *args, **kwargs):
        # Get the 'id' parameter from the URL
        memory_id = kwargs.get('id')

        if not memory_id:
            return Response(
                {"error": "Memory ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch memory record by ID
        try:
            memory = Memory.objects.filter(memory_asset_id=memory_id).values(
                'id', 'name', 'source_language', 'target_language', 'source_text', 'target_text'
            )

            if not memory:
                return Response(
                    {"data": []},
                    status=status.HTTP_200_OK
                )

            return Response({"data": memory}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MemoryAssetListAPI(APIView):
    def get(self, request, *args, **kwargs):
        # Fetch all memory records
        memories = MemoryAsset.objects.all().values(
            'id', 'source_language', 'target_languages', 'name', 'created_at'
        )

        return Response(
            {"data": list(memories)},
            status=status.HTTP_200_OK
        )


class MemoryDeleteAPI(APIView):
    def delete(self, request, *args, **kwargs):
        # Get the memory_asset_id from the URL parameters
        memory_asset_id = kwargs.get('memory_asset_id')

        if not memory_asset_id:
            return Response(
                {"error": "Memory asset ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Delete all related memories
            deleted_memories_count, _ = Memory.objects.filter(memory_asset_id=memory_asset_id).delete()

            # Delete the memory asset
            deleted_memory_asset_count, _ = MemoryAsset.objects.filter(id=memory_asset_id).delete()

            if deleted_memories_count == 0 and deleted_memory_asset_count == 0:
                return Response(
                    {"message": "No records found for the provided memory asset ID."},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {
                    "message": "Memory and memory asset deleted successfully.",
                    "deleted_memories_count": deleted_memories_count,
                    "deleted_memory_asset_count": deleted_memory_asset_count,
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MemoryUpdateAPI(APIView):
    def put(self, request, *args, **kwargs):
        # Retrieve updated rows from the request body
        updated_rows = request.data.get('updated_rows', [])

        if not updated_rows:
            return Response(
                {"error": "No rows provided for update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_count = 0
        errors = []

        # Iterate through each row and update the database
        for row in updated_rows:
            memory_id = row.get('id')
            source_text = row.get('source_text')
            target_text = row.get('target_text')

            if not memory_id or not source_text or not target_text:
                errors.append(
                    {"id": memory_id, "error": "Missing required fields (id, source_text, target_text)."}
                )
                continue

            try:
                # Update the Memory record
                Memory.objects.filter(id=memory_id).update(
                    source_text=source_text,
                    target_text=target_text
                )
                updated_count += 1
            except Exception as e:
                errors.append({"id": memory_id, "error": str(e)})

        response_data = {
            "message": f"{updated_count} rows updated successfully.",
            "errors": errors,
        }

        return Response(response_data, status=status.HTTP_200_OK if updated_count > 0 else status.HTTP_400_BAD_REQUEST)

class MemoryUpdateAPIBySourceAndTargetLanguage(APIView):
    def put(self, request, *args, **kwargs):
        # Retrieve `source_language` and `target_language` from the body
        source_language = request.data.get('source_language')
        target_language = request.data.get('target_language')
        updated_rows = request.data.get('updated_rows', [])

        # Validate required fields
        if not source_language or not target_language:
            return Response(
                {"error": "source_language and target_language are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not updated_rows:
            return Response(
                {"error": "No rows provided for update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_count = 0
        errors = []

        # Iterate through each row and update the database
        for row in updated_rows:
            original_text = row.get('originalText')
            translated_text = row.get('translatedText')

            # Validate required fields in each row
            if not original_text or not translated_text:
                errors.append(
                    {"error": "Missing required fields (originalText, translatedText).", "row": row}
                )
                continue

            try:
                # Update the Memory record
                updated_rows_count = Memory.objects.filter(
                    source_language=LANGUAGE_CODES.get(source_language, 'en'),
                    target_language=LANGUAGE_CODES.get(target_language, 'fr'),
                    source_text=original_text
                ).update(
                    target_text=translated_text
                )

                if updated_rows_count > 0:
                    updated_count += updated_rows_count
                else:
                    errors.append(
                        {"error": "No matching record found for the provided source_language, target_language, and originalText.", "row": row}
                    )
            except Exception as e:
                errors.append({"error": str(e), "row": row})

        response_data = {
            "message": f"{updated_count} rows updated successfully.",
            "errors": errors,
        }

        return Response(
            response_data,
            status=status.HTTP_200_OK if updated_count > 0 else status.HTTP_400_BAD_REQUEST
        )


class MemoryExportAPIById(APIView):
    def get(self, request, *args, **kwargs):
        # Get the 'id' parameter from the URL
        memory_id = kwargs.get('id')

        if not memory_id:
            return Response(
                {"error": "Memory ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch memory records by memory_asset_id
        try:
            memory = Memory.objects.filter(memory_asset_id=memory_id).values(
                'id', 'name', 'source_language', 'target_language', 'source_text', 'target_text'
            )

            if not memory:
                return Response(
                    {"data": []},
                    status=status.HTTP_200_OK
                )

            # Check if the request is for export
            export = request.query_params.get('export', '').lower() == 'true'

            if export:
                return self.export_to_csv(memory)

            return Response({"data": list(memory)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def export_to_csv(self, memory):
        """Helper method to export memory data to a CSV file."""
        # Create an in-memory buffer for the CSV
        buffer = StringIO()
        writer = csv.writer(buffer)
        
        # Write the header row
        writer.writerow(['ID', 'Name', 'Source Language', 'Target Language', 'Source Text', 'Target Text'])

        # Write the data rows
        for record in memory:
            writer.writerow([
                record['id'],
                record['name'],
                record['source_language'],
                record['target_language'],
                record['source_text'],
                record['target_text'],
            ])

        # Generate the HTTP response with the CSV file
        response = HttpResponse(buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="memory_export.csv"'
        buffer.close()

        return response
    
class MemoryBulkDeleteAPI(APIView):
    def delete(self, request, *args, **kwargs):
        # Retrieve the list of IDs to delete from the request body
        memory_ids = request.data.get('memory_ids', [])

        if not memory_ids or not isinstance(memory_ids, list):
            return Response(
                {"error": "A list of memory IDs is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Delete the specified Memory records
            deleted_count, _ = Memory.objects.filter(id__in=memory_ids).delete()

            if deleted_count == 0:
                return Response(
                    {"message": "No records found for the provided IDs."},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {"message": f"{deleted_count} memory records deleted successfully."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )