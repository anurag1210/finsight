"""Validates uploaded documents are financial filings."""
from openai import OpenAI
from src.config import OPENAI_API_KEY

def is_financial_document(first_page_text: str) -> tuple[bool, str]:
    """Check if the document is a financial filing using LLM classification."""
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=10,
        messages=[
            {
                "role": "system",
                "content": "You are a document classifier. Given the first page of a document, determine if it is a financial filing (10-K, 10-Q, annual report, earnings report, prospectus, or similar SEC/regulatory filing). Answer ONLY 'YES' or 'NO'."
            },
            {
                "role": "user",
                "content": first_page_text[:2000]
            }
        ]
    )
    
    answer = response.choices[0].message.content.strip().upper()


    if answer == "YES":
            return True, "Document accepted."
    return False, "FinSight only accepts financial filings (10-K, 10-Q, annual reports, etc.)."
    