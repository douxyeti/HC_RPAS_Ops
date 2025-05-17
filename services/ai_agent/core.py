from openai import OpenAI
from PyPDF2 import PdfReader
import os

class AIAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.docs_dir = os.getenv('PDF_DIR', 'docs')

    def query(self, prompt: str, max_context: int = 3000) -> str:
        context = self._load_pdf_context()[:max_context]
        
        response = self.client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4.1-turbo'),
            messages=[
                {"role": "system", "content": f"DOCUMENTS DE RÉFÉRENCE :\n{context}"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def _load_pdf_context(self) -> str:
        context = ""
        for root, _, files in os.walk(self.docs_dir):
            for file in files:
                if file.endswith('.pdf'):
                    path = os.path.join(root, file)
                    context += f"\n\nFICHIER : {path}\nCONTENU :\n"
                    with open(path, 'rb') as f:
                        reader = PdfReader(f)
                        for page in reader.pages:
                            context += page.extract_text() + "\n"
        return context
