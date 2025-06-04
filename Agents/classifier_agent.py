from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models.prompt_templates import FORMAT_CLASSIFICATION_PROMPT, INTENT_CLASSIFICATION_PROMPT
from dotenv import load_dotenv
import os
import logging

load_dotenv()

Format_labels = ["PDF", "EMAIL", "JSON"]
Intent_labels = ["Invoice", "RFQ", "Complaint", "Regulation", "General Enquiry"]

class ClassifierAgent:
    def __init__(self, groq_api_key: str, model_name: str = "llama-3.3-70b-versatile"):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        try:
            self.llm = ChatGroq(
                temperature=0,
                model_name=model_name,
                api_key=groq_api_key
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize ChatGroq: {e}")
            raise
        
       
        self.format_parser = StrOutputParser()
        self.intent_parser = StrOutputParser()

      
        self.format_prompt = ChatPromptTemplate.from_template(FORMAT_CLASSIFICATION_PROMPT)
        self.intent_prompt = ChatPromptTemplate.from_template(INTENT_CLASSIFICATION_PROMPT)
    
    def _validate_format(self, response: str) -> str:
        """Validate and clean format response"""
        response = response.strip().upper()
        if response in Format_labels:
            return response
        # Fallback logic
        if 'PDF' in response:
            return 'PDF'
        elif 'EMAIL' in response:
            return 'EMAIL'
        elif 'JSON' in response:
            return 'JSON'
        else:
            self.logger.warning(f"Unknown format response: {response}, defaulting to EMAIL")
            return 'EMAIL'
    
    def _validate_intent(self, response: str) -> str:
        """Validate and clean intent response"""
        response = response.strip()
        for intent in Intent_labels:
            if intent.lower() in response.lower():
                return intent
        self.logger.warning(f"Unknown intent response: {response}, defaulting to General Enquiry")
        return 'General Enquiry'

    def classify_format(self, input_txt: str) -> str:
        try:
            # Create the chain properly
            chain = self.format_prompt | self.llm | self.format_parser
            response = chain.invoke({"input_content": input_txt})
            return self._validate_format(response)
        except Exception as e:
            self.logger.error(f"Format classification failed: {e}")
            return "EMAIL"  # Default fallback

    def classify_intent(self, input_txt: str) -> str:
        try:
            # Create the chain properly
            chain = self.intent_prompt | self.llm | self.intent_parser
            response = chain.invoke({"input_content": input_txt})
            return self._validate_intent(response)
        except Exception as e:
            self.logger.error(f"Intent classification failed: {e}")
            return "General Enquiry"  # Default fallback

    def classify(self, input_txt: str) -> dict:
        if not input_txt or not input_txt.strip():
            return {
                "format": "EMAIL",
                "intent": "General Enquiry"
            }
        
        format_type = self.classify_format(input_txt)
        intent_type = self.classify_intent(input_txt)

        return {
            "format": format_type,
            "intent": intent_type
        }