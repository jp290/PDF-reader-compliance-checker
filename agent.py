import os
import json
from datetime import datetime
from google import genai
from pdf2image import convert_from_path
from PIL import Image
from dotenv import load_dotenv

# Automatically load the GOOGLE_API_KEY from the .env file in the same directory
load_dotenv()

class BioGeminiAgent:
    def __init__(self, api_key=None):
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env or environment.")
        
        # Initialize the NEW Client from google-genai SDK
        self.client = genai.Client(api_key=api_key)
        # Using the state-of-the-art gemini-2.5-flash for maximum speed and accuracy
        self.model_id = 'gemini-2.5-flash'

    def _pdf_to_pil_image(self, pdf_path):
        """Converts the first page of a PDF to a PIL Image."""
        print(f"Converting PDF: {pdf_path} to image...")
        try:
            pages = convert_from_path(pdf_path, first_page=1, last_page=1)
            if not pages:
                raise ValueError("Could not convert PDF to image.")
            return pages[0]
        except Exception as e:
            raise RuntimeError(f"Failed to convert PDF. Is 'poppler' installed? Error: {e}")

    def check_compliance(self, pdf_path, target_product="Organic Chia Seeds"):
        # Convert PDF to Image
        image = self._pdf_to_pil_image(pdf_path)

        prompt = f"""
        You are an expert Quality Assurance (QA) Manager for a German Bio-Food Importer.
        Look at the attached image of an Organic Certificate and extract the following data.

        TARGET PRODUCT TO VERIFY: "{target_product}"
        TODAY'S DATE: {datetime.now().strftime('%d.%m.%Y')}

        RETURN ONLY A JSON OBJECT with these keys:
        - "cert_number": string (Found on the document)
        - "expiry_date": string (DD.MM.YYYY - Locate the 'Valid until' or 'Expiry' date)
        - "is_expired": boolean (Compare expiry_date with TODAY'S DATE)
        - "product_found": boolean (Is the target product listed in the certificate's scope?)
        - "compliance_status": "PASS" | "FAIL" (PASS only if NOT expired AND product found)
        - "summary": A 1-sentence explanation based on visual evidence.
        """

        print(f"Sending image to {self.model_id} via New GenAI SDK...")
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=[prompt, image]
        )
        
        # Extract JSON from response
        content = response.text
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        
        return json.loads(content)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python agent.py <path_to_pdf> [target_product]")
        sys.exit(1)

    pdf_file = sys.argv[1]
    product = sys.argv[2] if len(sys.argv) > 2 else "Organic Chia Seeds"

    try:
        agent = BioGeminiAgent()
        print(f"--- [Bio-Gemini Pro Agent Prototype v2.5] ---")
        
        result = agent.check_compliance(pdf_file, product)
        print("\n[VISUAL COMPLIANCE REPORT]")
        print(json.dumps(result, indent=4))
        
        if result["compliance_status"] == "PASS":
            print(f"\n✅ PASS: {product} is cleared for import.")
        else:
            print(f"\n❌ FAIL: {result['summary']}")
    except Exception as e:
        print(f"\nError: {e}")
