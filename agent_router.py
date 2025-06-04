import os
import logging
from Agents.classifier_agent import ClassifierAgent
from Agents.json_agent import JSONAgent
from Agents.email_agent import EmailAgent
from Agents.pdf_agent import PDFAgent
from memory.memory import MemoryLogger

class AgentRouter:
    def __init__(self, groq_api_key: str = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if not groq_api_key:
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY is required")
        
        try:
            self.classifier = ClassifierAgent(groq_api_key=groq_api_key)
            self.json_agent = JSONAgent()
            self.email_agent = EmailAgent(groq_api_key=groq_api_key)
            self.pdf_agent = PDFAgent()
            self.memory = MemoryLogger()
            self.logger.info("All agents initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            raise

    def _detect_format_from_content(self, text: str, source_name: str = "") -> str:
        """Helper method to detect format from content characteristics"""
        if not text or not text.strip():
            return "EMAIL"
            
        text_lower = text.lower().strip()
        
        # JSON detection
        if (text.strip().startswith('{') and text.strip().endswith('}')) or \
           (text.strip().startswith('[') and text.strip().endswith(']')):
            return "JSON"
        
        # Email detection patterns
        email_indicators = ['from:', 'to:', 'subject:', '@', 'dear', 'sincerely', 'regards']
        if any(indicator in text_lower for indicator in email_indicators):
            return "EMAIL"
            
        # File extension based detection
        if source_name:
            if source_name.lower().endswith('.json'):
                return "JSON"
            elif source_name.lower().endswith('.pdf'):
                return "PDF"
            elif source_name.lower().endswith(('.txt', '.eml')):
                return "EMAIL"
        
        return "EMAIL"  # Default fallback

    def route(self, source_name: str, raw_bytes: bytes = None, raw_text: str = None):
        """
        Main routing method:
        - If raw_bytes is provided, assume PDF
        - Else use raw_text for JSON or Email
        """
        try:
            # Input validation
            if not raw_bytes and not raw_text:
                raise ValueError("Either raw_bytes or raw_text must be provided")
            
            if raw_bytes:
                # PDF path - extract text first
                try:
                    text = self.pdf_agent.extract_text(raw_bytes)
                except Exception as e:
                    self.logger.error(f"PDF text extraction failed: {e}")
                    return {
                        "source": source_name,
                        "format": "PDF",
                        "intent": "Unknown",
                        "result": {"error": f"PDF processing failed: {str(e)}"}
                    }
            else:
                text = raw_text

            # Classify format and intent
            try:
                classification = self.classifier.classify(text)
                fmt = classification["format"]
                intent = classification["intent"]
            except Exception as e:
                self.logger.warning(f"Classification failed, using fallback: {e}")
                # Fallback classification
                fmt = self._detect_format_from_content(text, source_name)
                intent = "General Enquiry"
                classification = {"format": fmt, "intent": intent}

            # Route to appropriate agent
            try:
                if fmt == "JSON":
                    result = self.json_agent.process(text, intent)
                elif fmt == "EMAIL":
                    result = self.email_agent.parse_email(text)
                elif fmt == "PDF":
                    # We already extracted text; pass bytes and intent
                    result = self.pdf_agent.process(raw_bytes, intent)
                else:
                    result = {"error": f"Unknown format: {fmt}"}
            except Exception as e:
                self.logger.error(f"Agent processing failed: {e}")
                result = {"error": f"Processing failed: {str(e)}"}

            # Log to memory
            try:
                self.memory.log_entry(
                    source=source_name,
                    format_type=fmt,
                    intent=intent,
                    payload={"classification": classification, "result": result}
                )
            except Exception as e:
                self.logger.warning(f"Memory logging failed: {e}")

            # Return result
            return {
                "source": source_name,
                "format": fmt,
                "intent": intent,
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Routing failed: {e}")
            return {
                "source": source_name,
                "format": "Unknown",
                "intent": "Unknown",
                "result": {"error": f"Routing failed: {str(e)}"}
            }

    def get_memory_stats(self):
        """Get memory statistics"""
        try:
            recent_entries = self.memory.fetch_all(limit=100)
            if not recent_entries:
                return {"total_entries": 0, "format_counts": {}, "intent_counts": {}}
            
            format_counts = {}
            intent_counts = {}
            
            for entry in recent_entries:
                format_counts[entry.format] = format_counts.get(entry.format, 0) + 1
                intent_counts[entry.intent] = intent_counts.get(entry.intent, 0) + 1
            
            return {
                "total_entries": len(recent_entries),
                "format_counts": format_counts,
                "intent_counts": intent_counts
            }
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    import json
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        router = AgentRouter(groq_api_key=os.getenv("GROQ_API_KEY"))

        # Test with sample files if they exist
        sample_files = [
            ("data/samples/sample_invoice.json", "text"),
            ("data/samples/sample_doc.pdf", "binary")
        ]
        
        for filepath, file_type in sample_files:
            if os.path.exists(filepath):
                try:
                    if file_type == "binary":
                        with open(filepath, "rb") as f:
                            pdf_bytes = f.read()
                        out = router.route(source_name=os.path.basename(filepath), raw_bytes=pdf_bytes)
                    else:
                        with open(filepath, "r") as f:
                            raw_text = f.read()
                        out = router.route(source_name=os.path.basename(filepath), raw_text=raw_text)
                    
                    print(f"\n=== {filepath} ===")
                    print(json.dumps(out, indent=2, default=str))
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
            else:
                print(f"Sample file not found: {filepath}")
                
    except Exception as e:
        print(f"Failed to initialize router: {e}")