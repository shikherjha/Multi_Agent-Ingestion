from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models.prompt_templates import EMAIL_EXTRACTION_PROMPT
from dotenv import load_dotenv
import os
import json
import logging

load_dotenv()

class EmailAgent:
    def __init__(self, groq_api_key: str, model_name: str = "llama-3.3-70b-versatile"):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        try:
            self.llm = ChatGroq(
                temperature=0,
                api_key=groq_api_key,
                model_name=model_name
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize ChatGroq: {e}")
            raise
            
        self.output_parser = StrOutputParser()
        self.prompt = ChatPromptTemplate.from_template(EMAIL_EXTRACTION_PROMPT)

    def parse_email(self, email_txt: str) -> dict:
        if not email_txt or not email_txt.strip():
            return {
                "error": "Empty email content provided",
                "sender_name": "",
                "sender_email": "",
                "urgency": "Low",
                "summary": "",
                "action": ""
            }

        try:
            
            chain = self.prompt | self.llm | self.output_parser
            result = chain.invoke({"email_content": email_txt})
            
            # Try to parse as JSON
            try:
                parsed_result = json.loads(result)
                # Ensure all required fields are present
                required_fields = ["sender_name", "sender_email", "urgency", "summary", "action"]
                for field in required_fields:
                    if field not in parsed_result:
                        parsed_result[field] = ""
                
                return parsed_result
            except json.JSONDecodeError as e:
                self.logger.warning(f"JSON parsing failed: {e}")
                # Return structured fallback
                return {
                    "error": "LLM returned unstructured output",
                    "raw_response": result,
                    "sender_name": "",
                    "sender_email": "",
                    "urgency": "Medium",
                    "summary": result[:200] if result else "",
                    "action": ""
                }
                
        except Exception as e:
            self.logger.error(f"Email parsing failed: {e}")
            return {
                "error": f"Email parsing failed: {str(e)}",
                "sender_name": "",
                "sender_email": "",
                "urgency": "Low",
                "summary": "",
                "action": ""
            }