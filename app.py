import streamlit as st
from weasyprint import HTML
import tempfile
import base64
import os
import io
from streamlit.components.v1 import html as html_component
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(layout="wide", page_title="Rich Text to PDF Converter", page_icon="📝")

# CSS customization
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    h1 {
        color: #2C3E50;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E6F0FF;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("📝 Rich Text to PDF Converter")

st.markdown("""
**Convert formatted text and images to PDF with just a few clicks**  
This app lets you paste rich text from sources like Word, Gmail, or Google Docs and convert it to PDF with all formatting and images preserved.
""")

# Sample HTML template
sample_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #2C3E50; }
        .highlight { background-color: #FFFFCC; padding: 2px 5px; }
        img { max-width: 100%; }
    </style>
</head>
<body>
    <h1>Sample Document with Formatting</h1>
    <p>This is a <strong>bold text</strong> and this is an <em>italic text</em>.</p>
    <p>You can also have <span class="highlight">highlighted text</span> using inline CSS.</p>
    <h2>Lists Example</h2>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3 with <strong>bold</strong> text</li>
    </ul>
    <p>Below is a base64 encoded image example:</p>
    <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAKElEQVQ4jWNgYGD4Twzu6FhFFGYYNXDUwGFpIAk2E4dHDRw1cDgaCAASFOffhEIO3gAAAABJRU5ErkJggg==" alt="Sample colored box">
    <p>The above is just a simple colored box as an example.</p>
</body>
</html>
"""

# Create tabs for different input methods
tab1, tab2, tab3 = st.tabs(["📝 Paste HTML", "📎 Upload HTML File", "🧩 Use Template"])

with tab1:
    st.markdown("### Paste formatted content below:")
    
    # Initialize session state for rich text content if it doesn't exist
    if 'rich_text_content' not in st.session_state:
        st.session_state.rich_text_content = ""
    
    # Create an enhanced rich text editor component with better image handling
    rich_text_editor = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .editor-container {
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-bottom: 10px;
                background-color: white;
            }
            #rich-editor {
                min-height: 300px;
                padding: 10px;
                overflow-y: auto;
                font-family: Arial, sans-serif;
            }
            #rich-editor:focus {
                outline: none;
            }
            img {
                max-width: 100%;
                height: auto;
                display: block;
                margin: 10px 0;
            }
            .toolbar {
                background-color: #f5f5f5;
                padding: 5px;
                border-bottom: 1px solid #ddd;
                display: flex;
                flex-wrap: wrap;
                gap: 5px;
            }
            .toolbar button {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px 10px;
                cursor: pointer;
                font-size: 14px;
            }
            .toolbar button:hover {
                background-color: #f0f0f0;
            }
            .capture-btn {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                margin-top: 10px;
                font-weight: bold;
            }
            .capture-btn:hover {
                background-color: #45a049;
            }
            .status-bar {
                font-size: 12px;
                color: #666;
                padding: 5px;
                text-align: right;
                background-color: #f9f9f9;
                border-top: 1px solid #ddd;
            }
            .image-upload-input {
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="editor-container">
            <div class="toolbar">
                <button onclick="execCommand('bold')"><b>B</b></button>
                <button onclick="execCommand('italic')"><i>I</i></button>
                <button onclick="execCommand('underline')"><u>U</u></button>
                <button onclick="execCommand('insertOrderedList')">1.</button>
                <button onclick="execCommand('insertUnorderedList')">•</button>
                <label for="image-upload">
                    <button onclick="document.getElementById('image-upload').click(); return false;">Insert Image</button>
                </label>
                <input type="file" id="image-upload" class="image-upload-input" accept="image/*">
            </div>
            <div id="rich-editor" contenteditable="true">
                <p>Paste your formatted text and images here...</p>
            </div>
            <div class="status-bar" id="status-bar">Ready</div>
        </div>
        <button id="capture-btn" class="capture-btn">Capture Content</button>
        
        <script>
            const editor = document.getElementById('rich-editor');
            const statusBar = document.getElementById('status-bar');
            
            // Execute command function for toolbar buttons
            function execCommand(command, value = null) {
                document.execCommand(command, false, value);
                editor.focus();
            }
            
            // Clear default text on first click
            editor.addEventListener('focus', function(e) {
                if (this.textContent.trim() === 'Paste your formatted text and images here...') {
                    this.innerHTML = '';
                }
            }, {once: true});
            
            // Fill editor with existing content if available
            const initialContent = """ + (f"'{st.session_state.rich_text_content}'" if st.session_state.rich_text_content else "''") + """;
            if (initialContent && initialContent.trim() !== '') {
                editor.innerHTML = initialContent;
            }
            
            // Handle paste event to properly handle images
            editor.addEventListener('paste', function(e) {
                // Prevent the default paste action
                e.preventDefault();
                
                statusBar.textContent = "Processing paste...";
                
                // Get clipboard data
                const clipboardData = e.clipboardData || window.clipboardData;
                
                // Check for HTML content
                if (clipboardData.types.includes('text/html')) {
                    // Get HTML from clipboard
                    const html = clipboardData.getData('text/html');
                    
                    // Insert at cursor position
                    const selection = window.getSelection();
                    if (selection.rangeCount > 0) {
                        const range = selection.getRangeAt(0);
                        range.deleteContents();
                        
                        // Create a temporary div to hold the HTML
                        const tempDiv = document.createElement('div');
                        tempDiv.innerHTML = html;
                        
                        // Process images in the pasted content to ensure they're properly loaded
                        const images = tempDiv.querySelectorAll('img');
                        let imageLoadPromises = [];
                        
                        images.forEach(img => {
                            // Add a class to identify pasted images
                            img.classList.add('pasted-image');
                            
                            // Create a promise that resolves when the image loads
                            if (img.src) {
                                const promise = new Promise((resolve) => {
                                    const tempImg = new Image();
                                    tempImg.onload = () => {
                                        resolve();
                                    };
                                    tempImg.onerror = () => {
                                        // If loading fails, we still resolve to continue
                                        resolve();
                                    };
                                    tempImg.src = img.src;
                                });
                                imageLoadPromises.push(promise);
                            }
                        });
                        
                        // Wait for all images to load (or fail)
                        Promise.all(imageLoadPromises)
                            .then(() => {
                                // Now insert the content
                                while (tempDiv.firstChild) {
                                    range.insertNode(tempDiv.lastChild);
                                }
                                statusBar.textContent = "Paste completed";
                            })
                            .catch(err => {
                                statusBar.textContent = "Error processing images: " + err;
                            });
                    }
                } 
                // If no HTML, try to get images directly
                else if (clipboardData.items) {
                    let imageInserted = false;
                    
                    Array.from(clipboardData.items).forEach(item => {
                        if (item.type.indexOf('image') !== -1) {
                            // Get the image as a blob
                            const blob = item.getAsFile();
                            
                            // Convert blob to base64
                            const reader = new FileReader();
                            reader.onload = function(event) {
                                // Create an image element
                                const img = document.createElement('img');
                                img.src = event.target.result;
                                img.classList.add('pasted-image');
                                
                                // Insert at cursor position
                                const selection = window.getSelection();
                                if (selection.rangeCount > 0) {
                                    const range = selection.getRangeAt(0);
                                    range.deleteContents();
                                    range.insertNode(img);
                                    
                                    // Move cursor after the image
                                    range.setStartAfter(img);
                                    range.setEndAfter(img);
                                    selection.removeAllRanges();
                                    selection.addRange(range);
                                }
                                
                                imageInserted = true;
                                statusBar.textContent = "Image pasted successfully";
                            };
                            reader.readAsDataURL(blob);
                        }
                    });
                    
                    // If no image was found, insert as plain text
                    if (!imageInserted) {
                        const text = clipboardData.getData('text/plain');
                        document.execCommand('insertText', false, text);
                        statusBar.textContent = "Text pasted";
                    }
                } 
                // Fallback to plain text paste
                else {
                    const text = clipboardData.getData('text/plain');
                    document.execCommand('insertText', false, text);
                    statusBar.textContent = "Text pasted";
                }
            });
            
            // Handle image upload from toolbar
            document.getElementById('image-upload').addEventListener('change', function(e) {
                if (this.files && this.files[0]) {
                    const file = this.files[0];
                    const reader = new FileReader();
                    
                    reader.onload = function(event) {
                        const img = document.createElement('img');
                        img.src = event.target.result;
                        img.classList.add('uploaded-image');
                        
                        // Insert at cursor position
                        const selection = window.getSelection();
                        if (selection.rangeCount > 0) {
                            const range = selection.getRangeAt(0);
                            range.deleteContents();
                            range.insertNode(img);
                            
                            // Move cursor after the image
                            range.setStartAfter(img);
                            range.setEndAfter(img);
                            selection.removeAllRanges();
                            selection.addRange(range);
                        }
                        
                        statusBar.textContent = "Image uploaded successfully";
                    };
                    
                    reader.readAsDataURL(file);
                    
                    // Reset the file input
                    this.value = '';
                }
            });
            
            // Drag and drop handling for images
            editor.addEventListener('dragover', function(e) {
                e.preventDefault();
                statusBar.textContent = "Drop to insert image";
            });
            
            editor.addEventListener('drop', function(e) {
                e.preventDefault();
                
                if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                    const file = e.dataTransfer.files[0];
                    
                    // Check if the file is an image
                    if (file.type.match(/image.*/)) {
                        const reader = new FileReader();
                        
                        reader.onload = function(event) {
                            const img = document.createElement('img');
                            img.src = event.target.result;
                            img.classList.add('dropped-image');
                            
                            // Insert at drop position
                            const range = document.caretRangeFromPoint(e.clientX, e.clientY);
                            if (range) {
                                range.deleteContents();
                                range.insertNode(img);
                            }
                            
                            statusBar.textContent = "Image inserted successfully";
                        };
                        
                        reader.readAsDataURL(file);
                    }
                }
            });
            
            // Capture button click
            document.getElementById('capture-btn').addEventListener('click', function() {
                const htmlContent = editor.innerHTML;
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: htmlContent
                }, '*');
                
                statusBar.textContent = "Content captured";
            });
        </script>
    </body>
    </html>
    """
    
    # Custom component for rich text editor with callback
    component_value = components.html(rich_text_editor, height=370, scrolling=True)
    
    # Handle the component value change
    if component_value:
        st.session_state.rich_text_content = component_value
        st.session_state.html_input = component_value
        st.success("Content captured! You can now preview or generate PDF.")
    
    # Text area for showing and editing the raw HTML (hidden by default)
    show_html = st.checkbox("Show/Edit Raw HTML")
    if show_html:
        html_input = st.text_area(
            "HTML Source:", 
            value=st.session_state.get('rich_text_content', ""),
            height=300, 
            key="html_source_editor"
        )
        # Update session state if edited
        if html_input != st.session_state.get('rich_text_content', ""):
            st.session_state.html_input = html_input
            st.session_state.rich_text_content = html_input
    
with tab2:
    uploaded_file = st.file_uploader("Upload an HTML file:", type=["html", "htm"])
    if uploaded_file is not None:
        html_input = uploaded_file.read().decode("utf-8")
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        
with tab3:
    st.markdown("**Use this sample template as a starting point:**")
    if st.button("Load Sample Template"):
        # Store in session state so the rich text editor can access it
        st.session_state.html_input = sample_html
        st.session_state.rich_text_content = sample_html
        st.success("Sample template loaded! Switch to the 'Paste HTML' tab to see it.")
        # Switch to the first tab
        st.experimental_set_query_params(tab="paste-html")
        # Add a rerun to apply changes immediately
        st.experimental_rerun()

# Initialize session state for html input if it doesn't exist
if 'html_input' not in st.session_state:
    st.session_state.html_input = ""

# Determine which HTML content to use
if 'html_input' in locals() or 'html_input' in st.session_state:
    # Get HTML content from either locals or session state
    html_content = html_input if 'html_input' in locals() else st.session_state.get('html_input', "")
    
    # Add CSS to make the preview responsive
    styled_html = f"""
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
    {html_content}
    """
    
    # Preview button with error handling
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔍 Preview Content"):
            html_content = html_input if 'html_input' in locals() else st.session_state.get('html_input', "")
            if html_content and len(html_content.strip()) > 0:
                st.subheader("Preview:")
                try:
                    html_component(styled_html, height=500, scrolling=True)
                except Exception as e:
                    st.error(f"Error rendering HTML preview: {str(e)}")
            else:
                st.warning("Please enter or upload some HTML content first.")
    
    # Convert to PDF with error handling
    with col2:
        if st.button("📄 Generate PDF"):
            html_content = html_input if 'html_input' in locals() else st.session_state.get('html_input', "")
            if html_content and len(html_content.strip()) > 0:
                try:
                    with st.spinner("Generating PDF..."):
                        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
                            HTML(string=styled_html).write_pdf(tmp_pdf.name)
                            with open(tmp_pdf.name, "rb") as f:
                                pdf_data = f.read()
                            os.unlink(tmp_pdf.name)  # Clean up the temp file
                            
                            st.success("PDF generated successfully!")
                            st.download_button(
                                "⬇️ Download PDF", 
                                pdf_data, 
                                file_name="richtext_output.pdf",
                                mime="application/pdf"
                            )
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
                    st.info("Tip: Make sure your HTML is well-formed and all image sources are valid.")
            else:
                st.warning("Please enter or upload some HTML content first.")

# Footer with helpful information
st.markdown("---")
with st.expander("ℹ️ About this app"):
    st.markdown("""
    This app converts rich text to PDF while preserving formatting and images. 
    
    **Supported features:**
    - Text formatting (bold, italic, underline)
    - Lists (ordered and unordered)
    - Tables
    - Inline images (base64 encoded)
    - CSS styling
    
    **Tips for best results:**
    - Make sure all images are properly embedded as base64
    - Use standard HTML tags for formatting
    - Check the preview before generating the PDF
    """)
