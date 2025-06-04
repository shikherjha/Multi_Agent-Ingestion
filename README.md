# Multi-Agent Ingestion System

A Python-based multi-agent system that processes PDF, JSON, or raw email input. It uses a Groq LLM (via LangChain) to classify format and business intent, routes the input to a specialized agent, extracts structured data, and logs everything in an SQLite-based memory. A Streamlit UI wraps the entire flow for easy interaction and review.

---

## Features

- **File & Text Input:** Upload PDFs, JSON files, or paste raw text content.
- **Smart Classification:** Format and intent detection using Groq’s LLM via LangChain.
- **Specialized Agents:**  
  - **JSON Agent:** Schema validation and anomaly detection  
  - **Email Agent:** Sender, urgency, and content extraction  
  - **PDF Agent:** Text extraction via PyMuPDF (pdfplumber optional)
- **Memory Logging:** SQLite storage for all inputs, outputs, and metadata.
- **Streamlit UI:** User-friendly interface to upload, process, and view logs.

---