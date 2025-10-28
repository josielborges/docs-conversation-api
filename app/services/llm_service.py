import google.generativeai as genai
from app.core import settings


class LLMService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    def generate_response(self, context: str, question: str) -> str:
        """Generate a response based on context and question."""
        prompt = f"""Based on the following documents:

{context}

Answer the following question: {question}

If the information is not in the documents, say that you did not find the information.

IMPORTANT: Respond in Brazilian Portuguese."""
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def generate_summary(self, context: str, sources: list) -> str:
        """Generate a summary of the documents."""
        prompt = f"""Based on the following documents, create a comprehensive executive summary:

{context}

The summary should:
- Identify the main topics and themes
- Highlight the most important information
- Be structured and easy to read
- Be between 200-300 words

Sources: {', '.join(sources)}

IMPORTANT: Respond in Brazilian Portuguese."""
        
        response = self.model.generate_content(prompt)
        return response.text


llm_service = LLMService()
