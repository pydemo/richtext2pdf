from os.path import isfile
import streamlit as st, base64, pathlib

def show_pdf(path: str | pathlib.Path):
    """Display PDF using streamlit's built-in capabilities"""
    with open(path, "rb") as f:
        pdf_bytes = f.read()
    
    st.title("PDF Viewer")
    
    # Method 1: Download button (always works)
    st.download_button(
        label="📥 Download PDF",
        data=pdf_bytes,
        file_name="document.pdf",
        mime="application/pdf"
    )
    
    # Method 2: Try to display with object tag (more compatible than iframe with data URLs)
    b64 = base64.b64encode(pdf_bytes).decode()
    pdf_display = f'''
    <object data="data:application/pdf;base64,{b64}" type="application/pdf" width="100%" height="800px">
        <p>Your browser does not support PDFs. 
        <a href="data:application/pdf;base64,{b64}">Download the PDF</a> instead.</p>
    </object>
    '''
    
    st.markdown("### PDF Preview")
    st.markdown(pdf_display, unsafe_allow_html=True)
    
    # Method 3: Fallback - display as downloadable link
    st.markdown("### Alternative Access")
    st.markdown(f'<a href="data:application/pdf;base64,{b64}" target="_blank">🔗 Open PDF in new tab</a>', unsafe_allow_html=True)

assert isfile(r"C:\Users\alex_\AppData\Local\Temp\clipboard_20250606_180054.pdf")
show_pdf(r"C:\Users\alex_\AppData\Local\Temp\clipboard_20250606_180054.pdf")
