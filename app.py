import streamlit as st
from pathlib import Path
import json

from src import read_pdf_with_verbx, translate_text, SUPPORTED_LANGUAGES

st.set_page_config(
    page_title="Indian Document Agent",
    page_icon="🇮🇳",
    layout="wide",
)

st.title("🇮🇳 Indian Document Agent")
st.caption("AI-powered Document Analysis, OCR extraction & Multilingual Translation using VerbX")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ OCR & Translation Settings")
    hard_ocr = st.checkbox(
        "Hard OCR Mode",
        value=False,
        help="Use this for scanned, low-contrast, or handwritten documents.",
    )
    
    st.divider()
    st.subheader("🌐 Default Translation")
    default_lang_code = st.selectbox(
        "Default Target Language",
        options=list(SUPPORTED_LANGUAGES.keys()),
        format_func=lambda code: SUPPORTED_LANGUAGES[code],
        index=0,  # Default to Hindi
        help="Select the default language to translate extracted text into.",
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
                # Reset previous translation when a new OCR is run
                st.session_state.pop("translation_result", None)
                st.success("✅ Document processed successfully!")
            except Exception as e:
                st.error(f"❌ OCR extraction failed: {e}")

# Display OCR & Translation Results if present in session state
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

    # Action Row
    col_dl, _ = st.columns([3, 4])
    with col_dl:
        st.download_button(
            label="📥 Download Extracted Text (.txt)",
            data=full_text,
            file_name=f"{Path(file_name).stem}_extracted.txt",
            mime="text/plain",
            use_container_width=True,
        )

    tab_full, tab_translate, tab_pages, tab_raw = st.tabs([
        "📄 Full Extracted Text",
        "🌐 Translate to Indian Languages",
        "📑 Page-by-Page",
        "🔍 Raw JSON",
    ])

    with tab_full:
        st.text_area(
            "Extracted Text Content",
            value=full_text,
            height=450,
            help="Complete document text transcribed by VerbX OCR.",
        )

    with tab_translate:
        st.subheader("🌐 Multilingual Document Translation (VerbX)")
        st.caption("Translate the extracted document text into Indian languages in real time.")

        col_t1, col_t2, col_t3 = st.columns([3, 3, 2])
        with col_t1:
            source_options = {"auto": "Auto-Detect"}
            source_options.update(SUPPORTED_LANGUAGES)
            source_lang = st.selectbox(
                "Source Language",
                options=list(source_options.keys()),
                format_func=lambda k: source_options[k],
                index=0,
            )

        with col_t2:
            target_lang = st.selectbox(
                "Target Indian Language",
                options=list(SUPPORTED_LANGUAGES.keys()),
                format_func=lambda k: SUPPORTED_LANGUAGES[k],
                index=list(SUPPORTED_LANGUAGES.keys()).index(default_lang_code),
            )

        with col_t3:
            st.write("")
            st.write("")
            do_translate = st.button("✨ Translate Now", type="primary", use_container_width=True)

        if do_translate:
            if not full_text.strip():
                st.warning("⚠️ No text available in the document to translate.")
            else:
                with st.spinner(f"Translating to {SUPPORTED_LANGUAGES[target_lang]} using VerbX..."):
                    try:
                        trans_res = translate_text(
                            full_text,
                            target_lang=target_lang,
                            source_lang=source_lang,
                        )
                        st.session_state["translation_result"] = trans_res
                        st.session_state["trans_target_lang"] = target_lang
                        st.success(f"✅ Translated successfully into {SUPPORTED_LANGUAGES[target_lang]}!")
                    except Exception as te:
                        st.error(f"❌ Translation failed: {te}")

        # Display Translation if available
        if "translation_result" in st.session_state:
            t_res = st.session_state["translation_result"]
            translated_txt = t_res.get("text", "")
            t_target = st.session_state.get("trans_target_lang", target_lang)
            confidence = t_res.get("confidence")

            col_tm1, col_tm2 = st.columns(2)
            if confidence is not None:
                col_tm1.metric("Translation Confidence", f"{confidence * 100:.1f}%")
            col_tm2.metric("Translated Characters", len(translated_txt))

            # Side-by-side comparison
            c_orig, c_trans = st.columns(2)
            with c_orig:
                st.markdown("**Original Text (Extracted)**")
                st.text_area("Original", value=full_text, height=380, label_visibility="collapsed")
            with c_trans:
                st.markdown(f"**Translated ({SUPPORTED_LANGUAGES.get(t_target, t_target)})**")
                st.text_area("Translated", value=translated_txt, height=380, label_visibility="collapsed")

            st.download_button(
                label=f"📥 Download Translated Text ({SUPPORTED_LANGUAGES.get(t_target, t_target)}) (.txt)",
                data=translated_txt,
                file_name=f"{Path(file_name).stem}_{t_target}_translated.txt",
                mime="text/plain",
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
