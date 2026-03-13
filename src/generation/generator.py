#Adding generator part to generate the output of the RAG
from langchain_openai import ChatOpenAI
from src.config import LLM_MODEL,OPENAI_API_KEY,MAX_TOKENS,LLM_TEMPERATURE
from src.generation.prompt_templates import SYSTEM_PROMPT,formatting_retrieval,get_user_content

#Function to generate the output response from the LLM
def generate_response(query:str)-> str:
    llm=ChatOpenAI(
    model=LLM_MODEL,
    api_key=OPENAI_API_KEY,
    temperature=LLM_TEMPERATURE,
    max_tokens=MAX_TOKENS,
    )

    context = formatting_retrieval(query)
    user_content=get_user_content(context, query)
    
    messages=[
          ("system", SYSTEM_PROMPT),
          ("human", user_content),
    ]
    response=llm.invoke(messages)
    return response.content



if __name__ == "__main__":
      query = input("Input a financial query: ")
      answer = generate_response(query)
      print(answer)
   