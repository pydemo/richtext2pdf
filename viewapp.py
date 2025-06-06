from os.path import isfile
import streamlit as st, base64, pathlib

def create_pdf():

    import os, tempfile, datetime, win32com.client  # pip install pywin32

    wdFormatPDF = 17                       # constant for PDF export
    outfile = os.path.join(
        tempfile.gettempdir(),
        f"clipboard_{datetime.datetime.now():%Y%m%d_%H%M%S}.pdf"
    )

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False                   # keep UI hidden
    doc   = word.Documents.Add()           # blank document
    doc.Content.Paste()                    # paste *as Word sees it* (text + pictures)
    doc.ExportAsFixedFormat(outfile, wdFormatPDF)  # same API Word’s UI uses
    doc.Close(False)
    word.Quit()

    print("Saved:", outfile)
    return outfile


def show_pdf(path: str | pathlib.Path):
    """Display PDF using streamlit's built-in capabilities"""
    with open(path, "rb") as f:
        pdf_bytes = f.read()
    
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

# Main application logic
st.title("PDF Viewer")

# Initialize session state
if 'pdf_path' not in st.session_state:
    st.session_state.pdf_path = None

# JavaScript for keyboard shortcut detection
keyboard_js = """
<script>
document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'v') {
        event.preventDefault();
        // Trigger button click
        const button = document.querySelector('button[data-testid="baseButton-secondary"]');
        if (button && button.textContent.includes('Create PDF from Clipboard')) {
            button.click();
        }
    }
});
</script>
"""

st.markdown(keyboard_js, unsafe_allow_html=True)

# Button to create PDF from clipboard (also triggered by Ctrl+V)
if st.button("📋 Create PDF from Clipboard (Ctrl+V)", key="create_pdf_btn"):
    try:
        with st.spinner("Creating PDF from clipboard..."):
            pdf_path = create_pdf()
            st.session_state.pdf_path = pdf_path
        st.success(f"PDF created successfully: {os.path.basename(pdf_path)}")
        st.rerun()
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")

# Display PDF if one exists
if st.session_state.pdf_path and isfile(st.session_state.pdf_path):
    show_pdf(st.session_state.pdf_path)
else:
    # Show empty PDF viewer
    st.markdown("### PDF Preview")
    st.info("📄 No PDF loaded. Press **Ctrl+V** or click the button above to create a PDF from your clipboard content.")
    
    # Empty PDF viewer placeholder
    empty_viewer = '''
    <div style="border: 2px dashed #ccc; height: 400px; display: flex; align-items: center; justify-content: center; background-color: #f9f9f9;">
        <div style="text-align: center; color: #666;">
            <h3>PDF Viewer</h3>
            <p>Your PDF will appear here</p>
        </div>
    </div>
    '''
    st.markdown(empty_viewer, unsafe_allow_html=True)
