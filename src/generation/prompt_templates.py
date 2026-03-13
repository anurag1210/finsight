from src.retrieval.retriever import retrieve_vectordb

# System prompt with your specific constraints
SYSTEM_PROMPT = """
You are a Financial Analyst Sysadmin. Adhere to the following rules:
1. SOURCE RESTRICTION: Do NOT make up information. Use ONLY the provided context chunks from source PDFs to answer.
2. CITATIONS: You MUST cite the source for every claim. Use the format: (Source: [Filename], Page: [Number]).
3. MISSING DATA: If the answer is not contained within the provided documents, say exactly: "Information not found in financial records."
4. STYLE: Provide detailed, analytical responses that break down technical or financial figures clearly.
"""

def get_user_content(context, query):
    return f"""<context>
    {context}
    </context>
    <question>
    {query} 
    </question>"""
        
#Function to fetch the result from the retrieval and formats it 
def formatting_retrieval(query):
    results = retrieve_vectordb(query)
    return format_context(results)

def format_context(results):
    if not results:
        return ""
    lines = []
    seen = set()
    for doc, score in results:
        source_file = doc.metadata.get("source_file") or doc.metadata.get("source") or "Unknown"
        page = doc.metadata.get("page")
        chunk_id = doc.metadata.get("chunk_id")
        dedupe_key = (source_file, page, chunk_id, doc.page_content[:200])
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        lines.append(
            f"[Source: {source_file}, Page: {page}, Score: {score:.3f}] {doc.page_content}"
        )
    return "\n\n".join(lines)


if __name__ == "__main__":
     print("This is the code for prompt template for a chat for a financial analyst")
     query=input("Input a financial query: ")
     context_result = formatting_retrieval(query)
     user_content = get_user_content(context_result, query)
     print(user_content)
     
