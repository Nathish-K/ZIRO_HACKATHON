import streamlit as st
from pathlib import Path
import json

from src import read_pdf_with_verbx

st.set_page_config(
    page_title="Indian Document Agent",
    page_icon="🇮🇳",
    layout="wide",
)

st.title("🇮🇳 Indian Document Agent")
st.caption("AI-powered Document Analysis & OCR extraction using VerbX")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ OCR Settings")
    hard_ocr = st.checkbox(
        "Hard OCR Mode",
        value=False,
        help="Use this for scanned, low-contrast, or handwritten documents.",
    )
    
    st.divider()
    st.subheader("📁 Sample Documents")
    sample_files = [
        Path(r"C:\Users\nathi\Downloads\Agentic AI Problem Statement.pdf"),
        Path("indian_document_agent_test.pdf"),
    ]
    available_samples = [p for p in sample_files if p.exists()]
    
    selected_sample = None
    if available_samples:
        use_sample = st.checkbox("Use a detected local file", value=False)
        if use_sample:
            sample_options = {p.name: p for p in available_samples}
            choice = st.selectbox("Choose file:", list(sample_options.keys()))
            selected_sample = sample_options[choice]

# File Upload Section
uploaded_file = st.file_uploader(
    "Upload a document (PDF)",
    type=["pdf"],
    help="Upload your Indian government, legal, or business document for OCR.",
)

pdf_bytes = None
file_name = None

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    file_name = uploaded_file.name
elif selected_sample is not None and selected_sample.exists():
    pdf_bytes = selected_sample.read_bytes()
    file_name = selected_sample.name
    st.info(f"Loaded local document: `{file_name}`")

if not pdf_bytes:
    st.info("👆 Please upload a PDF document above to get started.")
else:
    col_action, _ = st.columns([2, 5])
    with col_action:
        run_btn = st.button("🚀 Run OCR & Extract Content", type="primary", use_container_width=True)

    if run_btn:
        with st.spinner("Processing document with VerbX OCR... This may take a few seconds."):
            try:
                result = read_pdf_with_verbx(pdf_bytes, hard=hard_ocr)
                st.session_state["ocr_result"] = result
                st.session_state["processed_file"] = file_name
                st.success("✅ Document processed successfully!")
            except Exception as e:
                st.error(f"❌ OCR extraction failed: {e}")

# Display OCR Results if present in session state
if "ocr_result" in st.session_state and st.session_state.get("processed_file") == file_name:
    result = st.session_state["ocr_result"]
    full_text = result.get("text", "")
    pages = result.get("pages", [])

    st.divider()

    # Metrics Row
    m1, m2, m3 = st.columns(3)
    m1.metric("Pages Extracted", len(pages) if pages else 1)
    m2.metric("Character Count", len(full_text))
    m3.metric("Word Count", len(full_text.split()))

    # Download Button
    st.download_button(
        label="📥 Download Extracted Text (.txt)",
        data=full_text,
        file_name=f"{Path(file_name).stem}_extracted.txt",
        mime="text/plain",
    )

    tab_full, tab_pages, tab_raw = st.tabs(["📄 Full Extracted Text", "📑 Page-by-Page", "🔍 Raw JSON"])

    with tab_full:
        st.text_area(
            "Extracted Text Content",
            value=full_text,
            height=450,
            help="Complete document text transcribed by VerbX OCR.",
        )

    with tab_pages:
        if pages:
            for page in pages:
                page_num = page.get("page", 1)
                page_text = page.get("text", "")
                with st.expander(f"📖 Page {page_num}", expanded=(page_num == 1)):
                    st.write(page_text if page_text else "_No text detected on this page._")
        else:
            st.write(full_text if full_text else "_No pages data returned._")

    with tab_raw:
        st.json(result)
