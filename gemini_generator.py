import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class GeminiDocumentGenerator:
    """Handles prompt construction and Gemini API calls for legal document generation."""

    def __init__(self, model_name: str = None):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it in your .env file."
            )

        genai.configure(api_key=api_key)
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.model = genai.GenerativeModel(model_name=self.model_name)

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:
        """Generate a legal document using Gemini based on user inputs."""

        prompt = f"""You are a professional legal document drafting assistant.
Generate a comprehensive, formal legal document of type: "{document_type}".

Document Details:
- Document Type: {document_type}
- Involved Parties: {parties}
- Effective Date: {dates}
- Terms and Conditions: {terms}

Requirements:
1. Use formal legal language and structure.
2. Include a clear title at the top.
3. Include sections such as: Parties, Effective Date, Terms & Conditions,
   Confidentiality, Termination, Governing Law, Entire Agreement, Severability,
   and Signature block.
4. Convert semicolon-separated terms into numbered clauses.
5. Use placeholders (e.g., [Address], [State]) where information is missing.
6. Ensure the output is clean, well-formatted plain text with numbered
   headings and proper spacing.
7. Do NOT include markdown code fences, asterisks, or emojis.
8. End with a signature block and a footer line: "LegalEase Inc. | contact@legalease.com | All Rights Reserved."

Return ONLY the document text.
"""

        try:
            response = self.model.generate_content(prompt)
            text = getattr(response, "text", None)
            if not text:
                # Fallback for safety-blocked or empty responses
                raise RuntimeError("Gemini returned an empty response.")
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"Gemini generation failed: {str(e)}")