import os
import sys
import requests
import streamlit as st

# Make project root importable when running `streamlit run frontend/app.py`
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config import BACKEND_URL, LOGO_PATH, INVERSE_LOGO_PATH
from frontend.sanitizer import sanitize_text
from frontend.formatters import format_docx, format_pdf, format_html_preview

# ---------- Page Config ----------
st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="centered",
)

# ---------- Session State ----------
if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""
if "show_edit" not in st.session_state:
    st.session_state.show_edit = False
if "doc_type" not in st.session_state:
    st.session_state.doc_type = "Legal Document"

# ---------- Header / Logo ----------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    logo_shown = False
    if os.path.exists(LOGO_PATH):
        try:
            st.image(LOGO_PATH, use_container_width=True)
            logo_shown = True
        except Exception:
            pass
    if not logo_shown:
        st.markdown(
            "<h1 style='text-align:center;'>⚖️ LegalEase</h1>",
            unsafe_allow_html=True,
        )

st.markdown(
    "<h2 style='text-align: center; color: #7dd3fc;'>AI Legal Document Generator</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#94a3b8;'>"
    "Generate professional legal documents in seconds with Gemini 3.8 Flash."
    "</p>",
    unsafe_allow_html=True,
)
st.divider()

# ---------- Input Form ----------
with st.form("legal_form"):
    document_type = st.text_input(
        "Document Type",
        placeholder="e.g., Freelance Work Contract, NDA, Lease Agreement",
    )
    parties = st.text_area(
        "Parties Involved",
        placeholder="e.g., Jane Doe (Service Provider), TechNova Inc. (Client)",
        height=100,
    )
    terms = st.text_area(
        "Terms & Conditions (Use semicolons for bullet points)",
        placeholder="Payment within 30 days; Deliverables by deadline; "
        "Confidentiality maintained; 15-day termination notice",
        height=140,
    )
    dates = st.text_input(
        "Effective Date",
        placeholder="e.g., April 15, 2025",
    )

    submitted = st.form_submit_button("🚀 Generate Document", use_container_width=True)

# ---------- Generate ----------
if submitted:
    if not document_type or not parties or not terms or not dates:
        st.warning("Please fill in all fields before generating.")
    else:
        with st.spinner("Generating your legal document with Gemini 3.8 Flash..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json={
                        "document_type": document_type,
                        "parties": parties,
                        "terms": terms,
                        "dates": dates,
                    },
                    timeout=300,
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.generated_text = sanitize_text(data["document"])
                    st.session_state.doc_type = document_type
                    st.session_state.show_edit = False
                    st.success("✅ Document Generated Successfully!")
                else:
                    st.error(
                        f"Backend error {response.status_code}: {response.text}"
                    )
            except requests.exceptions.ConnectionError:
                st.error(
                    f"❌ Could not connect to backend at {BACKEND_URL}. "
                    "Make sure FastAPI (uvicorn) is running."
                )
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ---------- Preview ----------
if st.session_state.generated_text:
    st.divider()
    st.markdown("### 📄 Document Preview")

    styled_html = format_html_preview(st.session_state.generated_text)
    st.markdown(
        f"""
        <div style="
            background-color:#0f172a;
            border:1px solid #1e293b;
            border-radius:10px;
            padding:22px;
            max-height:520px;
            overflow-y:auto;
            font-family:'Times New Roman', serif;
        ">
            {styled_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- Edit ----------
    if st.button("✏️ Click to Edit Document"):
        st.session_state.show_edit = not st.session_state.show_edit

    if st.session_state.show_edit:
        edited_text = st.text_area(
            "Edit Document Below:",
            value=st.session_state.generated_text,
            height=300,
            key="edit_area",
        )
        st.session_state.generated_text = edited_text

    # ---------- Downloads ----------
    st.markdown("### 📥 Download Options")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.download_button(
            label="⬇️ Download as .TXT",
            data=st.session_state.generated_text.encode("utf-8"),
            file_name=f"{st.session_state.doc_type.replace(' ', '_').lower()}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with col_b:
        try:
            docx_bytes = format_docx(
                st.session_state.generated_text, st.session_state.doc_type
            )
            st.download_button(
                label="⬇️ Download as .DOCX",
                data=docx_bytes,
                file_name=f"{st.session_state.doc_type.replace(' ', '_').lower()}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"DOCX error: {e}")

    with col_c:
        try:
            pdf_bytes = format_pdf(
                st.session_state.generated_text, st.session_state.doc_type
            )
            st.download_button(
                label="⬇️ Download as .PDF",
                data=pdf_bytes,
                file_name=f"{st.session_state.doc_type.replace(' ', '_').lower()}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"PDF error: {e}")

# ---------- Footer ----------
st.divider()
st.markdown(
    "<p style='text-align:center; color:#64748b; font-size:12px;'>"
    "LegalEase Inc. | contact@legalease.com | All Rights Reserved."
    "</p>",
    unsafe_allow_html=True,
)