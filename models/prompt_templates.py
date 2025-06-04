FORMAT_CLASSIFICATION_PROMPT ="""
You are file format classifier.
Given the content of a file, determine whether it is a 
- PDF
- JSON
- EMAIL

Respond only with one of: "PDF", "JSON", "EMAIL".

Content:
{input_content}
"""

INTENT_CLASSIFICATION_PROMPT = """
You are an intent classifier.
Given the following, classify a user's intent.

Possible intents include:
- Invoice
- RFQ (Request for Quotation)
- Complaint
- Regulation
- General Enquiry


Respond only with only the intent label.

Content:
{input_content}
"""

EMAIL_EXTRACTION_PROMPT="""
You are an Email Parsing assistant. Given the email body below extract:
 - Sender's name and email
 - Urgency level (High, Medium, Low)
 - Summary in 1-2 sentences
 - Any action requested

 Respond in JSON:
 {{
 "sender_name":"....",
 "sender_email":"...",
 "urgency":"...",
 "summary":"...",
 "action":"..."
 }}

 Email:
 {email_content}

""" 