from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain.agents import AgentExecutor
from langchain.tools.tavily_search import TavilySearchResults
from typing import Any, Optional
import os

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

llm = ChatGroq(
    temperature=0.6,
    llm="llama-3.3-70b-versatile",
    api_key=groq_api_key
)
prompt = ChatPromptTemplate.from_template(
    '''
You are a document classifier and intent classifier expert.
You classify documents in three categories :
 - Email
 - PDF
 - JSON
Classify the document type only from (Email, PDF, JSON)
You classify document's intent from the following categories :
 - Complaint
 - Invoice
 - RFQ (request for quotation)
 - Generic Queries
Classify the document's intent only from (Complaint, Invoice, RFQ, Generic Queries)
Return the respose in JSON format:
{{
"format":"...",
"intent":"..."}}

Input_file:
{input_txt}
'''
)
#tools = [
    #tavily_search = TavilySearchResults(api_key=tavily_api_key)

chain = prompt | llm | StrOutputParser()

class SampleAgent :
    def __init__(self,input_txt:str):
        self.agent = AgentExecutor(
            llm = chain,
            

        )