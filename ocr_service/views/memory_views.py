from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from lxml import etree
import pandas as pd
from ocr_service.models.memory_models import Memory, MemoryAsset
from xlsx2csv import Xlsx2csv
from io import StringIO

class TranslationMemoryUploadAPI(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        source_language = request.data.get('source_language')
        name = request.data.get('name')
        target_languages = request.data.get('target_language')  # Comma-separated target languages
        file = request.FILES.get('file')

        # Validate payload
        if not source_language or not target_languages or not file or not name:
            return Response(
                {"error": "name, source_language, target_language, and file are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parse target languages
        target_languages = [lang.strip() for lang in target_languages.split(',')]

        # Create a MemoryAsset
        memory_asset = MemoryAsset.objects.create(
            source_language=source_language,
            name=name,
            target_languages=",".join(target_languages)
        )
        
        # memory_asset=9

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

        return Response({"message": "Translations saved successfully!", "memory_asset_id": memory_asset.id}, status=status.HTTP_201_CREATED)

    def process_tmx(self, file, source_language, target_languages, name, memory_asset):
        """Process TMX file and save translations for multiple target languages."""
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

                # Save translations for each target language
                for lang, target_text in target_texts.items():
                    if source_text and target_text:
                        try:
                            Memory.objects.create(
                                name=name,
                                source_language=source_language,
                                target_language=lang,
                                source_text=source_text,
                                target_text=target_text,
                                memory_asset=memory_asset
                            )
                        except Exception as db_error:
                            print(f"Error saving TU #{tu_number} for target language {lang}: {db_error}")
                    else:
                        print(f"Skipping TU #{tu_number} for target language {lang}: Missing source or target text")

        except Exception as e:
            print(f"Error processing TMX file: {e}")
            raise ValueError(f"Error processing TMX file: {e}")

    def process_xlsx(self, file, source_language, target_languages, name, memory_asset):
        """Process XLSX file using xlsx2csv and save translations for multiple target languages."""
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
                                Memory.objects.create(
                                    name=name,
                                    source_language=source_language,
                                    target_language=lang,
                                    source_text=source_text,
                                    target_text=target_text,
                                    memory_asset=memory_asset,
                                )
                                print(f"Saved Row #{index + 1} for target language '{lang}'")
                            except Exception as db_error:
                                print(f"Error saving row #{index + 1} for target language '{lang}': {db_error}")
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