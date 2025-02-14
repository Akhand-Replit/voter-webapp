import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_text_file(content):
    """Process the text file content and extract structured data."""
    records = []

    try:
        # Remove BOM and normalize newlines
        content = content.strip().replace('\ufeff', '').replace('\r\n', '\n')

        # Split into records using both Bengali and English numerals
        # This pattern looks for lines starting with numbers followed by a dot
        raw_records = re.split(r'\n\s*(?=(?:[০-৯]+|[0-9]+)\.)', content)
        logger.info(f"Initial split found {len(raw_records)} potential records")

        for record in raw_records:
            if not record.strip():
                continue

            logger.debug(f"Processing record: {record[:100]}...")
            record_dict = {}

            # Define field patterns with more flexible matching
            field_patterns = {
                'ক্রমিক_নং': (r'^([০-৯]+|[0-9]+)\.', True),  # True means take full match
                'নাম': (r'নাম:?\s*([^,\n।]+)', False),
                'ভোটার_নং': (r'ভোটার\s*নং:?\s*([^,\n।]+)', False),
                'পিতার_নাম': (r'পিতা:?\s*([^,\n।]+)', False),
                'মাতার_নাম': (r'মাতা:?\s*([^,\n।]+)', False),
                'পেশা': (r'পেশা:?\s*([^,।\n]+)', False),
                'জন্ম_তারিখ': (r'জন্ম\s*তারিখ:?\s*([^,\n।]+)', False),
                'ঠিকানা': (r'ঠিকানা:?\s*([^,\n।]+(?:[,\n।][^,\n।]+)*)', False)
            }

            # Extract each field
            for field, (pattern, full_match) in field_patterns.items():
                match = re.search(pattern, record, re.MULTILINE)
                if match:
                    # For ক্রমিক_নং, take the full match and remove the dot
                    value = match.group(0).strip() if full_match else match.group(1).strip()
                    if field == 'ক্রমিক_নং':
                        value = value.rstrip('.')
                    record_dict[field] = value.strip()

            # Only add records that have at least a few key fields
            required_fields = {'ক্রমিক_নং', 'নাম', 'ভোটার_নং'}
            if all(field in record_dict for field in required_fields):
                records.append(record_dict)
                logger.debug(f"Added record with fields: {list(record_dict.keys())}")
            else:
                logger.warning(f"Skipped incomplete record: missing required fields")

        logger.info(f"Successfully processed {len(records)} complete records")
        return records

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise Exception(f"Failed to process file: {str(e)}")