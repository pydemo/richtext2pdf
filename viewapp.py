from os.path import isfile
import streamlit as st, base64, pathlib, os

def create_pdf(prefix="clipboard"):

    import os, tempfile, datetime, win32com.client, pythoncom  # pip install pywin32

    # Initialize COM
    pythoncom.CoInitialize()
    
    try:
        wdFormatPDF = 17                       # constant for PDF export
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.pdf"
        outfile = os.path.join(tempfile.gettempdir(), filename)

        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False                   # keep UI hidden
        doc   = word.Documents.Add()           # blank document
        doc.Content.Paste()                    # paste *as Word sees it* (text + pictures)
        doc.ExportAsFixedFormat(outfile, wdFormatPDF)  # same API Word's UI uses
        doc.Close(False)
        word.Quit()

        print("Saved:", outfile)
        return outfile
    finally:
        # Clean up COM
        pythoncom.CoUninitialize()


def show_pdf(path: str | pathlib.Path):
    """Display PDF using streamlit's built-in capabilities"""
    with open(path, "rb") as f:
        pdf_bytes = f.read()
    
    # Extract filename from path
    filename = os.path.basename(path)
    
    # Method 1: Download button (always works)
    st.download_button(
        label="📥 Download PDF",
        data=pdf_bytes,
        file_name=filename,
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
        
        // Add query parameter and reload page
        const url = new URL(window.location);
        url.searchParams.set('ctrl_v', 'true');
        window.location.href = url.toString();
    }
});
</script>
"""

st.markdown(keyboard_js, unsafe_allow_html=True)

# Check if Ctrl+V was pressed (using query params)
query_params = st.query_params
ctrl_v_triggered = 'ctrl_v' in query_params and query_params['ctrl_v'] == 'true'

if ctrl_v_triggered:
    # Clear the query parameter to avoid retriggering
    st.query_params.clear()

# Create columns for text input and button
col1, col2 = st.columns([2, 1])

with col1:
    # Text input for PDF filename prefix
    pdf_prefix = st.text_input(
        "PDF filename prefix:",
        value="document",
        placeholder="Enter filename prefix",
        help="The PDF will be saved as: prefix_timestamp.pdf"
    )

with col2:
    # Add some spacing to align button with text input
    st.write("")  # Empty line for spacing
    # Button to create PDF from clipboard (also triggered by Ctrl+V)
    create_pdf_clicked = st.button("📋 Create PDF from Clipboard (Ctrl+V)", key="create_pdf_btn")

if create_pdf_clicked or ctrl_v_triggered:
    # Use the prefix from the text input, or default if empty
    prefix = pdf_prefix.strip() if pdf_prefix.strip() else "document"
    try:
        with st.spinner("Creating PDF from clipboard..."):
            pdf_path = create_pdf(prefix)
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
