import os
import asyncio
import aiohttp
from typing import Dict, Any, Optional
import json
import time


class AzureOCRService:
    def __init__(self):
        self.endpoint = os.getenv("AZURE_CV_ENDPOINT")
        self.key = os.getenv("AZURE_CV_KEY")

        if not self.endpoint or not self.key:
            raise ValueError("Azure Computer Vision endpoint and key must be set")

    async def process_receipt(self, image_path: str) -> Dict[str, Any]:
        """Process receipt image using Azure Computer Vision Read API"""
        try:
            # Read image file
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()

            headers = {
                'Ocp-Apim-Subscription-Key': self.key,
                'Content-Type': 'application/octet-stream'
            }

            # Submit image for analysis
            analyze_url = f"{self.endpoint}/vision/v3.2/read/analyze"

            async with aiohttp.ClientSession() as session:
                # Start the analysis
                async with session.post(analyze_url, headers=headers, data=image_data) as response:
                    if response.status == 202:
                        operation_location = response.headers.get('Operation-Location')
                        if not operation_location:
                            return {"success": False, "error": "No operation location returned"}

                        operation_id = operation_location.split('/')[-1]

                        # Poll for results
                        result_url = f"{self.endpoint}/vision/v3.2/read/analyzeResults/{operation_id}"

                        max_attempts = 30
                        for attempt in range(max_attempts):
                            await asyncio.sleep(2)  # Wait 2 seconds between polls

                            async with session.get(result_url,
                                                   headers={'Ocp-Apim-Subscription-Key': self.key}) as result_response:
                                if result_response.status == 200:
                                    result_data = await result_response.json()

                                    if result_data['status'] == 'succeeded':
                                        extracted_text = self._extract_text_from_result(result_data)
                                        return {
                                            "success": True,
                                            "extracted_text": extracted_text,
                                            "confidence": 0.90,  # Azure doesn't provide overall confidence
                                            "processing_time_ms": (attempt + 1) * 2000,
                                            "raw_result": result_data
                                        }
                                    elif result_data['status'] == 'failed':
                                        return {
                                            "success": False,
                                            "error": "Azure OCR processing failed"
                                        }
                                    # If status is 'running', continue polling
                                else:
                                    return {
                                        "success": False,
                                        "error": f"Error getting results: {result_response.status}"
                                    }

                        return {
                            "success": False,
                            "error": "Timeout waiting for Azure OCR results"
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Azure API returned status {response.status}: {error_text}"
                        }

        except Exception as e:
            return {
                "success": False,
                "error": f"Exception during OCR processing: {str(e)}"
            }

    def _extract_text_from_result(self, azure_result: Dict) -> Dict[str, Any]:
        """Extract and structure text from Azure OCR result"""
        all_text = []

        # Extract all text lines
        for page in azure_result['analyzeResult']['readResults']:
            for line in page['lines']:
                all_text.append(line['text'])

        full_text = '\n'.join(all_text)

        # Basic receipt parsing (we'll improve this later)
        return {
            "full_text": full_text,
            "lines": all_text,
            "store_name": self._extract_store_name(all_text),
            "total_amount": self._extract_total_amount(all_text),
            "date": self._extract_date(all_text)
        }

    def _extract_store_name(self, text_lines: list) -> Optional[str]:
        """Extract store name (usually first line)"""
        return text_lines[0] if text_lines else None

    def _extract_total_amount(self, text_lines: list) -> Optional[str]:
        """Extract total amount"""
        import re
        amount_pattern = r'[₱P]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'

        for line in text_lines:
            if 'total' in line.lower():
                match = re.search(amount_pattern, line)
                if match:
                    return match.group(1)
        return None

    def _extract_date(self, text_lines: list) -> Optional[str]:
        """Extract date"""
        import re
        date_pattern = r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}'

        for line in text_lines:
            match = re.search(date_pattern, line)
            if match:
                return match.group()
        return None