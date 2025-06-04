import json
import logging
from pydantic import ValidationError
from models.json_schema import schema_mapping, GenericJSONSchema

class JSONAgent:
    def __init__(self, log_level=logging.INFO):
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger(self.__class__.__name__)

    def process(self, raw_json_str: str, intent: str) -> dict:
        """
        1. Load JSON
        2. Validate against the schema for the detected intent
        3. Flag any anomalies or missing fields
        4. Return a dict with:
         - 'valid': bool
         - 'data': the parsed model (or raw dict for fallback)
         - 'errors': validation errors, if any
        """
        if not raw_json_str or not raw_json_str.strip():
            return {
                "valid": False,
                "data": None,
                "errors": "Empty JSON string provided"
            }

        try:
            payload = json.loads(raw_json_str)
        except json.JSONDecodeError as e:
            self.logger.error("Invalid JSON: %s", e)
            return {
                "valid": False,
                "data": None,
                "errors": f"JSON decode error: {e}"
            }

        # Get the appropriate schema based on intent
        schema = schema_mapping.get(intent, GenericJSONSchema)
        
        try:
            model = schema(**payload)
            self.logger.info(f"JSON validated against {schema.__name__}")
            
            
            try:
                data = model.model_dump()  # Pydantic v2
            except AttributeError:
                data = model.dict()  # Pydantic v1
                
            return {
                "valid": True,
                "data": data,
                "errors": None
            }
            
        except ValidationError as e:
          
            errors = e.errors()
            self.logger.warning("Validation errors:\n %s", errors)
            return {
                "valid": False,
                "data": payload,  # Return raw payload for inspection
                "errors": errors
            }
        except Exception as e:
            self.logger.error(f"Unexpected error during validation: {e}")
            return {
                "valid": False,
                "data": payload,
                "errors": f"Validation error: {str(e)}"
            }