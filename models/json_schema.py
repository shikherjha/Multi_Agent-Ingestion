from pydantic import BaseModel, Field, validator
from typing import Optional, List, Any

class LineItem(BaseModel):
    description : str
    quantity : int 
    unit_price : float

class InvoiceSchema(BaseModel):
    invoice_id : str
    date : str
    total_amount: float
    line_items : List[LineItem]
    discount : Optional[float]= None
    tax : Optional[float] = None
    shipping_address : Optional[str] = None

class RFQSchema(BaseModel) :
    rfq_id : str
    requester : str
    items : List[LineItem]
    deadline : Optional[str]
    
class ComplaintSchema(BaseModel):
    complaint_id : str
    customer : str
    issue : str
    severity : Optional[str]    

class GenericJSONSchema(BaseModel) :
    payload: Any = Field(..., description="Raw JSON payload if no stricter schema applies")   

schema_mapping = {
    "Invoice" : InvoiceSchema,
    "RFQ" : RFQSchema,
    "Complaint":ComplaintSchema
}