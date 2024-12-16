from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from lxml import etree
import pandas as pd
from ocr_service.models.memory_models import Memory, MemoryAsset
from xlsx2csv import Xlsx2csv
from django.http import HttpResponse
import csv
from io import BytesIO, StringIO
import xml.etree.ElementTree as ET
from openpyxl import Workbook
from django.db.models.query import QuerySet
import os
from django.conf import settings


LANGUAGE_CODES = {
    "Abkhaz": "ab",
    "Adyghe": "ady",
    "Afrikaans": "af",
    "Agul": "ag",
    "Albanian": "sq",
    "Altaic": "alt",
    "Arabic": "ar",
    "Armenian (Eastern)": "hy_e",
    "Armenian (Grabar)": "hy_g",
    "Armenian (Western)": "hy_w",
    "Avar": "av",
    "Aymara": "ay",
    "Azerbaijani (Cyrillic)": "az_c",
    "Azerbaijani (Latin)": "az_l",
    "Bashkir": "ba",
    "Basque": "eu",
    "Belarussian": "be",
    "Bemba": "bem",
    "Blackfoot": "bf",
    "Breton": "br",
    "Bugotu": "bu",
    "Bulgarian": "bg",
    "Buryat": "bxr",
    "Catalan": "ca",
    "Chamorro": "ch",
    "Chechen": "ce",
    "Chinese Simplified": "zh_cn",
    "Chinese Traditional": "zh_tw",
    "Chukcha": "chuk",
    "Chuvash": "cv",
    "For MICR CMC-7 text type": "cmc7",
    "Corsican": "co",
    "Crimean Tatar": "crh",
    "Croatian": "hr",
    "Crow": "crw",
    "Czech": "cs",
    "Danish": "da",
    "Dargwa": "dar",
    "Numbers*": "num",
    "Dungan": "dng",
    "Dutch (Netherlands)": "nl",
    "Dutch (Belgium)": "nl_be",
    "For MICR (E-13B) text type": "e13b",
    "English": "en",
    "Eskimo (Cyrillic)": "esk_c",
    "Eskimo (Latin)": "esk_l",
    "Esperanto": "eo",
    "Estonian": "et",
    "Even": "evn",
    "Evenki": "evt",
    "Farsi": "fa",
    "Faeroese": "fo",
    "Fijian": "fj",
    "Finnish": "fi",
    "French": "fr",
    "Frisian": "fy",
    "Friulian": "fur",
    "Scottish Gaelic": "gd",
    "Gagauz": "gag",
    "Galician": "gl",
    "Ganda": "lg",
    "German": "de",
    "German (Luxembourg)": "de_lu",
    "German (new spelling)": "de_new",
    "Greek": "el",
    "Guarani": "gn",
    "Hani": "hn",
    "Hausa": "ha",
    "Hawaiian": "haw",
    "Hebrew": "he",
    "Hungarian": "hu",
    "Icelandic": "is",
    "Ido": "io",
    "Indonesian": "id",
    "Ingush": "inh",
    "Interlingua": "ia",
    "Irish": "ga",
    "Italian": "it",
    "Japanese": "ja",
    "Kabardian": "kbd",
    "Kalmyk": "xal",
    "Karachay-Balkar": "kbd_kb",
    "Karakalpak": "kaa",
    "Kasub": "csb",
    "Kazakh": "kk",
    "Khakas": "kha",
    "Khanty": "kca",
    "Kikuyu": "ki",
    "Kirgiz": "ky",
    "Kongo": "kg",
    "Korean": "ko",
    "Korean (Hangul)": "ko_h",
    "Koryak": "kpy",
    "Kpelle": "kpe",
    "Kumyk": "kum",
    "Kurdish": "ku",
    "Lak": "lbe",
    "Sami (Lappish)": "sme",
    "Latin": "la",
    "Latvian": "lv",
    "Latvian language written in Gothic script": "lv_goth",
    "Lezgin": "lez",
    "Lithuanian": "lt",
    "Luba": "lua",
    "Macedonian": "mk",
    "Malagasy": "mg",
    "Malay": "ms",
    "Malinke": "mln",
    "Maltese": "mt",
    "Mansi": "mns",
    "Maori": "mi",
    "Mari": "chm",
    "Maya": "myn",
    "Miao": "hmn",
    "Minangkabau": "min",
    "Mohawk": "moh",
    "Mongol": "mn",
    "Mordvin": "mdf",
    "Nahuatl": "nah",
    "Nenets": "yrk",
    "Nivkh": "niv",
    "Nogay": "nog",
    "Norwegian Nynorsk + Bokmal": "no",
    "Norwegian (Bokmal)": "nb",
    "Norwegian (Nynorsk)": "nn",
    "Nyanja": "ny",
    "Occidental": "oc",
    "Ojibway": "oj",
    "Old English": "ang",
    "Old French": "fro",
    "Old German": "goh",
    "Old Italian": "ita_old",
    "Old Slavonic": "cu",
    "Old Spanish": "osp",
    "Ossetian": "os",
    "Papiamento": "pap",
    "Tok Pisin": "tpi",
    "Polish": "pl",
    "Portuguese (Brazil)": "pt_br",
    "Portuguese (Portugal)": "pt_pt",
    "Provencal": "prv",
    "Quechua": "qu",
    "Rhaeto-Romanic": "rm",
    "Romanian": "ro",
    "Romanian (Moldavia)": "ro_md",
    "Romany": "rom",
    "Ruanda": "rw",
    "Rundi": "rn",
    "Russian (old spelling)": "ru_old",
    "Russian": "ru",
    "Samoan": "sm",
    "Selkup": "sel",
    "Serbian (Cyrillic)": "sr_c",
    "Serbian (Latin)": "sr_l",
    "Shona": "sn",
    "Sioux (Dakota)": "dak",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Somali": "so",
    "Sorbian": "wen",
    "Sotho": "st",
    "Spanish": "es",
    "Sunda": "su",
    "Swahili": "sw",
    "Swazi": "ss",
    "Swedish": "sv",
    "Tabassaran": "tab",
    "Tagalog": "tl",
    "Tahitian": "ty",
    "Tajik": "tg",
    "Tatar": "tt",
    "Thai": "th",
    "Jingpo": "kac",
    "Tongan": "to",
    "Tswana": "tn",
    "Tun": "tun",
    "Turkish": "tr",
    "Turkmen": "tk",
    "Tuvan": "tyv",
    "Udmurt": "udm",
    "Uighur (Cyrillic)": "ug_c",
    "Uighur (Latin)": "ug_l",
    "Ukrainian": "uk",
    "Uzbek (Cyrillic)": "uz_c",
    "Uzbek (Latin)": "uz_l",
    "Vietnamese": "vi",
    "Cebuano": "ceb",
    "Welsh": "cy",
    "Wolof": "wo",
    "Xhosa": "xh",
    "Yakut": "sah",
    "Yiddish": "yi",
    "Zapotec": "zap",
    "Zulu": "zu"
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

                for tuv in tu.findall('./tuv'):  # Translation unit variants
                    lang = tuv.attrib.get(f'{{{namespace["xml"]}}}lang')
                    seg = tuv.find('./seg')

                    if seg is not None:
                        # Clean the text content
                        cleaned_text = etree.tostring(seg, encoding='unicode', method='text').strip()

                        if lang == source_language:
                            source_text = cleaned_text
                        elif lang in target_languages:
                            target_texts[lang] = cleaned_text

                # Process source and target text
                if source_text:
                    for lang, target_text in target_texts.items():
                        target_text = target_text.strip() if target_text else None

                        # Ensure no duplicate records; update if existing, otherwise create
                        if target_text:
                            existing_record = Memory.objects.filter(
                                source_language=source_language,
                                target_language=lang,
                                source_text=source_text
                            ).first()

                            if existing_record:
                                # Update existing record
                                existing_record.target_text = target_text
                                existing_record.memory_asset = memory_asset
                                existing_record.name = name
                                existing_record.save()
                                print(f"Updated TU #{tu_number} for target language '{lang}'")
                            else:
                                # Create a new record
                                Memory.objects.create(
                                    name=name,
                                    source_language=source_language,
                                    target_language=lang,
                                    source_text=source_text,
                                    target_text=target_text,
                                    memory_asset=memory_asset,
                                )
                                print(f"Added TU #{tu_number} for target language '{lang}'")
                        else:
                            print(f"Skipping TU #{tu_number} for target language '{lang}': Missing target text")
                else:
                    print(f"Skipping TU #{tu_number}: Missing source text")

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

                        # Check for existing record
                        existing_record = Memory.objects.filter(
                            source_language=source_language,
                            target_language=lang,
                            source_text=source_text,
                        ).first()

                        if existing_record:
                            # Update existing record
                            if target_text:
                                existing_record.target_text = target_text
                            existing_record.memory_asset = memory_asset
                            existing_record.name = name
                            existing_record.save()
                            print(f"Updated Row #{index + 1} for target language '{lang}'")
                        else:
                            # Only create a new record if target_text is provided
                            if target_text:
                                Memory.objects.create(
                                    name=name,
                                    source_language=source_language,
                                    target_language=lang,
                                    source_text=source_text,
                                    target_text=target_text,
                                    memory_asset=memory_asset,
                                )
                                print(f"Added Row #{index + 1} for target language '{lang}'")
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

class GetMemoryBySource(APIView):
    def put(self, request, *args, **kwargs):
        # Retrieve the payload directly from the request body
        source_text = request.data.get('source_text')
        target_language = request.data.get('target_language')
        source_language = request.data.get('source_language')

        # Validate that all required fields are present
        if not source_text or not target_language or not source_language:
            return Response(
                {"error": "Missing required fields (source_text, target_language, source_language)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        errors = []

        try:
            # Find the first matching memory record
            matched_memory = Memory.objects.filter(
                source_text=source_text,
                source_language=LANGUAGE_CODES.get(source_language, 'en'),
                target_language=LANGUAGE_CODES.get(target_language, 'en')
            ).first()

            # If no record is found, return an empty response (204 No Content)
            if not matched_memory:
                return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            errors.append({"error": str(e)})

        # Construct response data if a matched record is found
        response_data = {
            "errors": errors,
            "data": {
                "id": matched_memory.id if matched_memory else None,
                "source_text": matched_memory.source_text if matched_memory else None,
                "target_text": matched_memory.target_text if matched_memory else None,
                "source_language": matched_memory.source_language if matched_memory else None,
                "target_language": matched_memory.target_language if matched_memory else None,
            }
        }

        # Return a response
        return Response(response_data, status=status.HTTP_200_OK)

class MemoryUpdateAPIBySourceAndTargetLanguage(APIView):
    def put(self, request, *args, **kwargs):
        # Retrieve `source_language`, `target_language`, and rows to update
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

        # Retrieve the MemoryAsset for the given languages
        memory_asset = MemoryAsset.objects.filter(
            source_language=LANGUAGE_CODES.get(source_language, 'en'),
            target_languages=LANGUAGE_CODES.get(target_language, 'fr'),
        ).first()

        if not memory_asset:
            return Response(
                {"error": "No memory asset found for the provided source_language and target_language."},
                status=status.HTTP_404_NOT_FOUND
            )

        processed_records = []
        errors = []

        # Process each row
        for row in updated_rows:
            original_text = row.get('originalText')
            translated_text = row.get('translatedText')

            if not original_text or not translated_text:
                errors.append(
                    {"error": "Missing required fields (originalText, translatedText).", "row": row}
                )
                continue

            try:
                memory, created = Memory.objects.update_or_create(
                    source_language=LANGUAGE_CODES.get(source_language, 'en'),
                    target_language=LANGUAGE_CODES.get(target_language, 'fr'),
                    source_text=original_text,
                    defaults={
                        "target_text": translated_text,
                        "memory_asset": memory_asset,
                    },
                )
                processed_records.append({
                    "id": memory.id,
                    "source_language": memory.source_language,
                    "target_language": memory.target_language,
                    "source_text": memory.source_text,
                    "target_text": memory.target_text,
                    "status": "created" if created else "updated"
                })
            except Exception as e:
                errors.append({"error": str(e), "row": row})

        # Prepare the response
        response_data = {
            "message": f"{len([r for r in processed_records if r['status'] == 'updated'])} rows updated and "
                       f"{len([r for r in processed_records if r['status'] == 'created'])} rows created successfully.",
            "processed_records": processed_records,
            "errors": errors,
        }

        return Response(
            response_data,
            status=status.HTTP_200_OK if processed_records else status.HTTP_400_BAD_REQUEST
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
            export_format = request.query_params.get('type', '').lower()  # 'csv', 'xlsx', or 'tmx'

            if export_format == 'xlsx':
                return self.export_to_xlsx(memory)
            elif export_format == 'tmx':
                return self.export_to_tmx(memory)
            else:  # Default to CSV
                return self.export_to_csv(memory)

        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def export_to_csv(self, memory):
        """Export data to CSV format."""
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        # Write header
        writer.writerow(['ID', 'Name', 'Source Language', 'Target Language', 'Source Text', 'Target Text'])
        # Write rows
        for record in memory:
            writer.writerow([
                record['id'],
                record['name'],
                record['source_language'],
                record['target_language'],
                record['source_text'],
                record['target_text']
            ])
        # Create response
        response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="memory_export.csv"'
        return response

    def export_to_xlsx(self, memory):
        """Export data to XLSX format and save the file to the server before returning it."""
        # Define the directory to save the file (you can change the path as needed)
        directory = os.path.join(settings.BASE_DIR, 'exports')  # You can change this to any directory
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Create the workbook
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Memory Data"

        # Write header
        headers = ['ID', 'Name', 'Source Language', 'Target Language', 'Source Text', 'Target Text']
        sheet.append(headers)

        # Write rows
        for record in memory:
            row = [
                record['id'],
                record['name'],
                record['source_language'],
                record['target_language'],
                record['source_text'],
                record['target_text']
            ]
            print("Writing row:", row)  # Debug: Ensure rows are correct
            sheet.append(row)

        # Save workbook to a file in the specified directory
        file_path = os.path.join(directory, 'memory_export.xlsx')
        workbook.save(file_path)

        # Open and send the file as a response
        with open(file_path, 'rb') as f:
            # Prepare the response to download the file
            response = HttpResponse(
                f.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="memory_export.xlsx"'

        return response
    def export_to_tmx(self, memory):
        """Export data to TMX format."""
        # Create TMX XML structure
        root = ET.Element("tmx", version="1.4")
        header = ET.SubElement(root, "header", attrib={
            "creationtool": "MemoryExportAPI",
            "creationtoolversion": "1.0",
            "datatype": "plaintext",
            "segtype": "sentence",
            "adminlang": "en-us",
            "srclang": memory[0]['source_language'] if memory else "en",
        })
        body = ET.SubElement(root, "body")

        for record in memory:
            tu = ET.SubElement(body, "tu")
            ET.SubElement(tu, "tuv", attrib={"xml:lang": record['source_language']}).append(
                ET.Element("seg", text=record['source_text'])
            )
            ET.SubElement(tu, "tuv", attrib={"xml:lang": record['target_language']}).append(
                ET.Element("seg", text=record['target_text'])
            )

        # Convert XML to string
        tmx_buffer = BytesIO()
        tree = ET.ElementTree(root)
        tree.write(tmx_buffer, encoding="utf-8", xml_declaration=True)
        tmx_buffer.seek(0)

        response = HttpResponse(tmx_buffer.getvalue(), content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="memory_export.tmx"'
        return response
class DuplicateMemory(APIView):
    def post(self, request, memory_asset_id):
        """
        Duplicate a memory asset and its associated memory records with a new target language.
        """
        try:
            target_languages_str = request.data.get("target_languages", "")

            # Fetch the original memory asset
            original_memory_asset = MemoryAsset.objects.filter(id=memory_asset_id).first()
            if not original_memory_asset:
                return Response(
                    {"error": "Memory asset not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Extract and parse target languages from the request
            if not target_languages_str:
                return Response(
                    {"error": "Target languages are required as a comma-separated string"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Convert comma-separated string to a list of target languages
            target_languages = [lang.strip() for lang in target_languages_str.split(",") if lang.strip()]
            if not target_languages:
                return Response(
                    {"error": "Invalid target languages provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if a MemoryAsset already exists with the same source_language and target_languages
            existing_memory_asset = MemoryAsset.objects.filter(
                source_language=original_memory_asset.source_language,
                target_languages=target_languages_str,
            ).first()

            # Use the existing memory asset or create a new one
            if existing_memory_asset:
                new_memory_asset = existing_memory_asset
            else:
                new_memory_asset = MemoryAsset.objects.create(
                    name=f"duplicate_{original_memory_asset.name}",
                    source_language=original_memory_asset.source_language,
                    target_languages=target_languages_str,
                )

            # Fetch memory records for the original memory asset
            memories = Memory.objects.filter(memory_asset=original_memory_asset)

            # Duplicate memory records
            for memory in memories:
                for target_language in target_languages:
                    # Check if a memory record with the same source_text exists
                    existing_memory = Memory.objects.filter(
                        memory_asset=new_memory_asset,
                        source_language=memory.source_language,
                        target_language=target_language,
                        source_text=memory.source_text,
                    ).exists()

                    if not existing_memory:
                        Memory.objects.create(
                            memory_asset=new_memory_asset,
                            source_language=memory.source_language,
                            target_language=target_language,
                            source_text=memory.source_text,
                        )

            return Response(
                {"message": "Memory asset duplicated successfully"},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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