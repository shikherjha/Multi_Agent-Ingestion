import logging
import fitz


class PDFAgent:
    def __init__(self,log_level:int=logging.INFO):
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract_text(self,pdf_bytes:bytes) -> str:
        '''
        uses PyMuPDF  to pull text from the PDF
        '''
        try:
            doc = fitz.open(stream=pdf_bytes,filetype="pdf")
            text = []
            for page in doc:
                text.append(page.get_text())
            full_text = "\n".join(text)
            self.logger.info(f"Extracted {len(text)} pages of text.")

            return full_text 
        except Exception as e :
            self.logger.error(f"PDF  text extraction failed: {e}")
            raise    
    def process(self,pdf_bytes:bytes,intent:str=None) ->dict:
        '''
        1. Extract the PDF text.
        2. (Optionally) could re-run for intent detection here.
        3. Return dict with the raw  text and  metadata
        '''       
        raw_text = self.extract_text(pdf_bytes)

        return {
            "raw_text":raw_text,
            "intent":intent
        }
