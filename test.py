import streamlit as st
from weasyprint import HTML
import tempfile
import base64

st.set_page_config(layout="wide")
st.title("📝 Paste Rich Text and Export to PDF")

st.markdown("""
**Instructions**  
1. Copy-paste rich text from any source (Word, Gmail, Google Docs).  
2. Make sure it includes inline images (they will be embedded as base64).  
3. Click **Preview** or **Download PDF**.
""")

# Text input for raw HTML
html_input = st.text_area("Paste HTML with formatting and inline images:", height=400)

# Optional live preview
if st.button("🔍 Preview"):
    st.components.v1.html(html_input, height=600, scrolling=True)

# Convert to PDF using WeasyPrint
if st.button("📄 Download as PDF"):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
        HTML(string=html_input).write_pdf(tmp_pdf.name)
        with open(tmp_pdf.name, "rb") as f:
            st.download_button("⬇️ Download PDF", f, file_name="richtext_output.pdf")
