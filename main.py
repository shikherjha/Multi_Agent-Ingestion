import os
import streamlit as st
import json
import logging
from datetime import datetime
from agent_router import AgentRouter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Multi-Agent Ingestion System", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .result-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .error-container {
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ff4444;
    }
    .success-container {
        background-color: #e6ffe6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #44ff44;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>Multi-Agent Ingestion System</h1>", unsafe_allow_html=True)

st.sidebar.header("Configuration")

groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    st.error("GROQ_API_KEY environment variable is required")
    st.info("Please set the GROQ_API_KEY environment variable and restart the application")
    st.stop()

st.sidebar.markdown("---")

model_options = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile", 
    "mixtral-8x7b-32768"
]
selected_model = st.sidebar.selectbox(
    "Select Model",
    model_options,
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Built by:** Shikher Jha")
st.sidebar.markdown("**Version:** 1.0")

try:
    if 'router' not in st.session_state:
        with st.spinner("Initializing agents..."):
            st.session_state.router = AgentRouter(groq_api_key=groq_key)
        st.success("All agents initialized successfully")
    router = st.session_state.router
except Exception as e:
    st.error(f"Failed to initialize agents: {str(e)}")
    st.stop()

st.header("Input Section")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("File Upload")
    uploaded = st.file_uploader(
        "Upload a file", 
        type=["pdf", "json", "txt", "eml"]
    )
    
    if uploaded:
        file_details = {
            "filename": uploaded.name,
            "filetype": uploaded.type,
            "filesize": uploaded.size
        }
        st.json(file_details)

with col2:
    st.subheader("Text Input")
    paste_text = st.checkbox("Enter text directly")
    raw_text_input = ""
    
    if paste_text:
        input_type = st.selectbox(
            "Content Type",
            ["Email", "JSON", "General Text"]
        )
        
        raw_text_input = st.text_area(
            f"Enter {input_type} Content",
            height=200,
            placeholder=f"Paste your {input_type.lower()} content here..."
        )

st.header("Processing")

if st.button("Process Input", type="primary"):
    if not uploaded and not (paste_text and raw_text_input.strip()):
        st.warning("Please upload a file or enter text content.")
    else:
        with st.spinner("Processing your input..."):
            try:
                if uploaded:
                    source_name = uploaded.name
                    data = uploaded.read()
                    
                    if uploaded.name.lower().endswith(".pdf"):
                        result = router.route(source_name, raw_bytes=data)
                    else:
                        try:
                            text_content = data.decode("utf-8")
                        except UnicodeDecodeError:
                            st.error("Unable to decode file. Please ensure it's a valid text file.")
                            st.stop()
                        result = router.route(source_name, raw_text=text_content)
                else:
                    source_name = f"manual_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    result = router.route(source_name, raw_text=raw_text_input)

                st.header("Results")
                
                if "error" not in result.get("result", {}):
                    st.markdown(
                        "<div class='success-container'>Processing completed successfully</div>", 
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        "<div class='error-container'>Processing completed with errors</div>", 
                        unsafe_allow_html=True
                    )

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Source", result['source'])
                with col2:
                    st.metric("Format", result['format'])
                with col3:
                    st.metric("Intent", result['intent'])

                st.subheader("Detailed Results")
                
                agent_result = result["result"]
                
                if result['format'] == 'EMAIL':
                    if 'error' not in agent_result:
                        st.markdown("**Email Analysis:**")
                        email_cols = st.columns(2)
                        with email_cols[0]:
                            st.write(f"**Sender:** {agent_result.get('sender_name', 'N/A')}")
                            st.write(f"**Email:** {agent_result.get('sender_email', 'N/A')}")
                            st.write(f"**Urgency:** {agent_result.get('urgency', 'N/A')}")
                        with email_cols[1]:
                            st.write(f"**Summary:** {agent_result.get('summary', 'N/A')}")
                            st.write(f"**Action Required:** {agent_result.get('action', 'N/A')}")
                
                elif result['format'] == 'JSON':
                    st.markdown("**JSON Validation:**")
                    if agent_result.get('valid'):
                        st.success("JSON is valid and properly structured")
                        st.json(agent_result.get('data', {}))
                    else:
                        st.error("JSON validation failed")
                        if agent_result.get('errors'):
                            st.write("**Validation Errors:**")
                            for error in agent_result['errors']:
                                st.write(f"- {error}")
                        if agent_result.get('data'):
                            st.write("**Raw Data:**")
                            st.json(agent_result['data'])
                
                elif result['format'] == 'PDF':
                    st.markdown("**PDF Analysis:**")
                    if 'raw_text' in agent_result:
                        text_preview = agent_result['raw_text'][:500]
                        st.text_area("Text Preview (first 500 chars)", value=text_preview, height=150)
                        st.write(f"**Total Characters:** {len(agent_result['raw_text'])}")

                with st.expander("Raw JSON Output"):
                    st.json(result)

            except Exception as e:
                st.error(f"Processing failed: {str(e)}")
                logger.error(f"Processing error: {e}")

st.header("System Memory & Statistics")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Processing Statistics")
    try:
        stats = router.get_memory_stats()
        if 'error' not in stats:
            st.metric("Total Processed", stats.get('total_entries', 0))
            
            if stats.get('format_counts'):
                st.write("**Format Distribution:**")
                for fmt, count in stats['format_counts'].items():
                    st.write(f"- {fmt}: {count}")
            
            if stats.get('intent_counts'):
                st.write("**Intent Distribution:**")
                for intent, count in stats['intent_counts'].items():
                    st.write(f"- {intent}: {count}")
        else:
            st.error(f"Failed to load stats: {stats['error']}")
    except Exception as e:
        st.error(f"Statistics unavailable: {str(e)}")

with col2:
    st.subheader("Recent Processing Log")
    try:
        logs = router.memory.fetch_all(limit=10)
        if logs:
            for i, entry in enumerate(logs):
                with st.expander(f"Entry {i+1}: {entry.source} ({entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"):
                    st.write(f"**Format:** {entry.format}")
                    st.write(f"**Intent:** {entry.intent}")
                    st.write(f"**Source:** {entry.source}")
                    
                    try:
                        payload_data = json.loads(entry.payload)
                        st.json(payload_data)
                    except:
                        st.text(entry.payload)
        else:
            st.info("No processing history available")
    except Exception as e:
        st.error(f"Unable to load processing history: {str(e)}")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>Multi-Agent Ingestion System v1.0 | Built with Streamlit & LangChain</p>
    <p>Supports PDF, JSON, and Email processing with intelligent routing</p>
</div>
""", unsafe_allow_html=True)

if st.sidebar.checkbox("Debug Mode"):
    st.header("Debug Information")
    
    debug_info = {
        "Groq API Key Set": bool(groq_key),
        "Selected Model": selected_model,
        "Session State Keys": list(st.session_state.keys()),
        "Environment Variables": {
            "GROQ_API_KEY": bool(os.getenv("GROQ_API_KEY")),
            "Python Path": os.environ.get("PYTHONPATH", "Not set")
        }
    }
    
    st.json(debug_info)