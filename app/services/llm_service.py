import google.generativeai as genai
from app.core import settings


class LLMService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def generate_response(self, context: str, question: str) -> str:
        """
        [Original RAG Prompt]
        Generates a response based only on the context. Less conversational.
        """
        prompt = f"""Based on the following documents:

{context}

Answer the following question: {question}

If the information is not in the documents, say that you did not find the information.

IMPORTANT: Your final answer **must** be in Brazilian Portuguese."""

        response = self.model.generate_content(prompt)
        return response.text

    def generate_chat_response(self, context: str, question: str) -> str:
        """
        [Advanced Chat Prompt]
        Generates a chat response that can handle RAG, casual conversation, and
        out-of-scope questions, always replying in Brazilian Portuguese.
        """
        prompt = f"""You are a helpful and friendly virtual assistant. Your primary job is to answer questions using **only** the documents provided.

**Behavioral Instructions:**
1.  **Top Priority (Document-based Questions):** First, check if the user's question can be answered using the provided documents. If it can, provide an answer based **strictly** on the information within them.
2.  **Casual Conversation:** If the question is a greeting, farewell, or general small talk (e.g., "Hi", "How are you?", "Thank you", "Who are you?"), **DO NOT** search the documents. Instead, respond politely and conversationally as an assistant.
3.  **Out-of-Scope Questions:** If the user asks about a topic that is clearly not covered in the documents (e.g., "What is the capital of France?", "How to bake a cake?"), politely state that you can only answer questions based on the provided content.

**Documents for Context:**
---
{context}
---

**User's Question:**
{question}

**IMPORTANT:** Your final answer **must** be in Brazilian Portuguese.
"""

        response = self.model.generate_content(prompt)
        return response.text

    def generate_summary(self, context: str, sources: list) -> str:
        """
        [Summary Prompt]
        Generates a summary from the context, outputting in Brazilian Portuguese.
        """
        prompt = f"""Based on the following documents, create a comprehensive executive summary.

**Documents:**
{context}

**Sources:**
{', '.join(sources)}

**The summary must:**
- Identify the main topics and themes.
- Highlight the most important information.
- Be structured and easy to read.
- Be between 200-300 words.

**IMPORTANT:** The final summary **must** be written in Brazilian Portuguese."""

        response = self.model.generate_content(prompt)
        return response.text


llm_service = LLMService()