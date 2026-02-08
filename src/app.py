"""
JeyQwe's Intelligence - AI Career Analysis Platform
Modern Dark SaaS UI inspired by GoPidge
"""

import sys
import os
from pathlib import Path

# --- ЖЕЛЕЗНЫЙ КУПОЛ (НАЧАЛО) ---

# 1. Затыкаем рот OpenAI (чтобы CrewAI даже не думал туда стучаться)
os.environ["OPENAI_API_KEY"] = "NA"
os.environ["OPENAI_MODEL_NAME"] = "NA"

# 2. Принудительная кодировка (лечит ошибку "invalid UTF-8" из логов)
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "C.UTF-8"

# 3. Перехват вывода (чтобы Windows консоль не крашилась от эмодзи)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# --- ЖЕЛЕЗНЫЙ КУПОЛ (КОНЕЦ) ---

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

# Import the backend analysis function
from main import run_job_analysis

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="JeyQwe's Intelligence",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CUSTOM CSS - MODERN DARK AI SAAS THEME (GoPidge Style)
# ============================================================================

st.markdown("""
<style>
    /* Import Modern Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Overrides */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Force Dark Background with Gradient */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #050511 0%, #120c1e 100%);
        background-attachment: fixed;
    }
    
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    
    /* Hide Default Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main Content Container */
    .main {
        background-color: transparent;
        padding-top: 80px;
    }
    
    .block-container {
        max-width: 900px;
        padding: 3rem 2rem;
    }
    
    /* Main Headline */
    .main-headline {
        text-align: center;
        margin-bottom: 60px;
    }
    
    .headline-text {
        font-size: 4.5rem;
        font-weight: 800;
        line-height: 1.1;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .headline-normal {
        color: #FFFFFF;
    }
    
    .headline-accent {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        display: inline-block;
        text-shadow: 0 0 60px rgba(106, 17, 203, 0.5);
    }
    
    .subheadline {
        font-size: 1.25rem;
        color: #B0B0C0;
        text-align: center;
        margin-top: 20px;
        line-height: 1.6;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Input Card - Glassmorphism */
    .input-card {
        background: rgba(30, 20, 60, 0.3);
        border: 1px solid rgba(106, 17, 203, 0.3);
        border-radius: 24px;
        padding: 40px;
        margin-bottom: 30px;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Text Area Styling */
    .stTextArea label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #FFFFFF !important;
        margin-bottom: 15px !important;
    }
    
    .stTextArea textarea {
        background: rgba(10, 5, 20, 0.8) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(106, 17, 203, 0.4) !important;
        border-radius: 16px !important;
        font-size: 15px !important;
        padding: 20px !important;
        min-height: 280px !important;
        line-height: 1.6 !important;
    }
    
    .stTextArea textarea:focus {
        border: 1px solid rgba(106, 17, 203, 0.8) !important;
        box-shadow: 0 0 0 3px rgba(106, 17, 203, 0.1) !important;
        outline: none !important;
    }
    
    .stTextArea textarea::placeholder {
        color: #6a7280 !important;
    }
    
    /* Button Styling - Purple Gradient Pill */
    .stButton {
        text-align: center;
        margin-top: 30px;
    }
    
    .stButton button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%) !important;
        color: #FFFFFF !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 18px 50px !important;
        border: none !important;
        border-radius: 50px !important;
        letter-spacing: 0.3px !important;
        box-shadow: 0 10px 40px rgba(106, 17, 203, 0.4) !important;
        transition: all 0.3s ease !important;
        text-transform: none !important;
    }
    
    .stButton button:hover {
        box-shadow: 0 15px 50px rgba(106, 17, 203, 0.6) !important;
        transform: translateY(-3px) !important;
    }
    
    .stButton button:active {
        transform: translateY(-1px) !important;
    }
    
    /* Output Card - Dashboard Style */
    .output-card {
        background: rgba(30, 20, 60, 0.4);
        border: 1px solid rgba(106, 17, 203, 0.3);
        border-radius: 24px;
        padding: 35px;
        margin-top: 40px;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .output-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 25px;
        padding-bottom: 20px;
        border-bottom: 1px solid rgba(106, 17, 203, 0.2);
    }
    
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(90deg, rgba(106, 17, 203, 0.2) 0%, rgba(37, 117, 252, 0.2) 100%);
        border: 1px solid rgba(106, 17, 203, 0.4);
        padding: 8px 18px;
        border-radius: 100px;
        font-size: 0.9rem;
        font-weight: 600;
        color: #FFFFFF;
    }
    
    .error-badge {
        background: rgba(239, 68, 68, 0.2);
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #fca5a5;
    }
    
    .output-content {
        color: #E0E0E8;
        font-size: 15px;
        line-height: 1.8;
        white-space: pre-wrap;
    }
    
    /* Loading Spinner */
    .stSpinner > div {
        border-top-color: #6a11cb !important;
        border-right-color: #2575fc !important;
    }
    
    /* Loading Text */
    .loading-container {
        text-align: center;
        padding: 60px 20px;
    }
    
    .loading-text {
        color: #B0B0C0;
        font-size: 1.1rem;
        font-weight: 500;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Tooltip/Helper Text */
    .helper-text {
        color: #6a7280;
        font-size: 0.9rem;
        text-align: center;
        margin-top: 15px;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .headline-text {
            font-size: 3rem;
        }
        
        .subheadline {
            font-size: 1.1rem;
        }
        
        .input-card, .output-card {
            padding: 25px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# MAIN INTERFACE
# ============================================================================

# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False

# ============================================================================
# HEADER SECTION
# ============================================================================

st.markdown("""
<div class="main-headline">
    <h1 class="headline-text">
        <span class="headline-normal">JeyQwe's</span>
        <span class="headline-accent">Intelligence</span>
    </h1>
    <p class="subheadline">
        Advanced AI-powered career analysis that matches job requirements 
        with your unique skillset to accelerate your professional growth.
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# INPUT SECTION
# ============================================================================

st.markdown('<div class="input-card">', unsafe_allow_html=True)

# Job Description Input
job_description = st.text_area(
    "📋 Paste Job Vacancy",
    placeholder="""Paste the complete job description here...

Example:
Senior Python Developer for AI Startup

Requirements:
• 3+ years Python experience
• Experience with RAG systems
• Knowledge of LangChain/CrewAI
• Vector database expertise
• LLM integration skills

Nice to have:
• Local LLM deployment (Ollama)
• AI agent workflows
""",
    key="job_input"
)

# Analyze Button
analyze_button = st.button("🚀 Analyze Career Match", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Helper text
st.markdown('<p class="helper-text">Powered by Gemma 3 • Local AI Processing</p>', unsafe_allow_html=True)

# ============================================================================
# ANALYSIS EXECUTION
# ============================================================================

if analyze_button:
    if not job_description.strip():
        st.session_state.error_message = "Please paste a job description to analyze."
        st.session_state.analysis_result = None
    else:
        st.session_state.error_message = None
        st.session_state.analysis_result = None
        st.session_state.is_loading = True
        
        # Show loading state
        with st.spinner(''):
            st.markdown("""
            <div class="loading-container">
                <p class="loading-text">🧠 Analyzing with AI Neural Network...</p>
                <p class="loading-text">🔍 Querying Personal Memory Vectors...</p>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                # Run the analysis
                result = run_job_analysis(job_description)
                st.session_state.analysis_result = str(result)
                st.session_state.is_loading = False
                
            except Exception as e:
                st.session_state.error_message = str(e)
                st.session_state.is_loading = False

# ============================================================================
# OUTPUT DISPLAY
# ============================================================================

# Display Results
if st.session_state.analysis_result:
    st.markdown("""
    <div class="output-card">
        <div class="output-header">
            <span class="status-badge">
                ✨ Analysis Complete
            </span>
        </div>
        <div class="output-content">
    """, unsafe_allow_html=True)
    
    st.markdown(st.session_state.analysis_result)
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

# Display Errors
if st.session_state.error_message:
    st.markdown(f"""
    <div class="output-card">
        <div class="output-header">
            <span class="error-badge">
                ⚠️ System Error
            </span>
        </div>
        <div class="output-content">
            {st.session_state.error_message}
            
            <br><br>
            <strong>Troubleshooting:</strong>
            • Ensure Ollama is running (ollama serve)
            • Verify gemma3:4b model is installed
            • Check FAISS database exists (run ingest_memory.py)
        </div>
    </div>
    """, unsafe_allow_html=True)
