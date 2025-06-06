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

**🆕 Enhanced Word Document Support:**
- Automatically detects and processes images from Word documents
- Handles multiple clipboard formats (HTML, RTF, direct images)
- Shows helpful placeholders when images can't be auto-converted
- Provides manual image insertion tools as backup
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
            
            // Enhanced paste event handler for Word documents with images
            editor.addEventListener('paste', function(e) {
                // Prevent the default paste action
                e.preventDefault();
                
                statusBar.textContent = "Processing paste...";
                
                // Get clipboard data
                const clipboardData = e.clipboardData || window.clipboardData;
                
                // Debug: Log available clipboard types
                console.log('Available clipboard types:', Array.from(clipboardData.types));
                
                // Process paste with enhanced Word support
                processPasteData(clipboardData, e);
            });
            
            // Enhanced paste processing function
            async function processPasteData(clipboardData, originalEvent) {
                let processedContent = false;
                
                // Enhanced debugging - show info in status bar
                const types = Array.from(clipboardData.types);
                const itemsCount = clipboardData.items ? clipboardData.items.length : 0;
                
                statusBar.textContent = `Debug: Found ${types.length} types, ${itemsCount} items. Types: ${types.join(', ')}`;
                
                // Note: Debug popup removed for better user experience
                // The issue is that Word only provides text/plain data for complex content
                
                // Enhanced debugging - log all available data types
                console.log('=== CLIPBOARD DEBUG INFO ===');
                console.log('Available types:', types);
                console.log('Items count:', itemsCount);
                
                // Log all available data
                for (let type of types) {
                    try {
                        const data = clipboardData.getData(type);
                        console.log(`Type "${type}" length:`, data.length);
                        if (data.length < 500) {
                            console.log(`Type "${type}" content:`, data);
                        } else {
                            console.log(`Type "${type}" content (first 200 chars):`, data.substring(0, 200) + '...');
                        }
                    } catch (e) {
                        console.log(`Error getting data for type "${type}":`, e);
                    }
                }
                
                // Check clipboard items in detail
                if (clipboardData.items) {
                    console.log('=== CLIPBOARD ITEMS DEBUG ===');
                    for (let i = 0; i < clipboardData.items.length; i++) {
                        const item = clipboardData.items[i];
                        console.log(`Item ${i}:`, {
                            type: item.type,
                            kind: item.kind
                        });
                    }
                }
                
                // Process images FIRST (higher priority)
                if (clipboardData.items) {
                    const success = await processImageItems(clipboardData.items);
                    if (success) {
                        processedContent = true;
                        console.log('Successfully processed direct image items');
                    }
                }
                
                // Check for HTML content (Word often provides this)
                if (!processedContent && clipboardData.types.includes('text/html')) {
                    const html = clipboardData.getData('text/html');
                    console.log('Processing HTML content...');
                    
                    // Enhanced HTML processing for Word content
                    const success = await processHTMLContent(html);
                    if (success) {
                        processedContent = true;
                        console.log('Successfully processed HTML content');
                    }
                }
                
                // Check for RTF content (Word's rich text format)
                if (!processedContent && clipboardData.types.includes('text/rtf')) {
                    const rtf = clipboardData.getData('text/rtf');
                    console.log('Processing RTF content...');
                    statusBar.textContent = "Processing RTF content...";
                    
                    const success = await processRTFContent(rtf);
                    if (success) {
                        processedContent = true;
                        console.log('Successfully processed RTF content');
                    }
                }
                
                // Try alternative image formats
                if (!processedContent) {
                    const imageSuccess = await tryAlternativeImageFormats(clipboardData, originalEvent);
                    if (imageSuccess) {
                        processedContent = true;
                        console.log('Successfully processed alternative image formats');
                    }
                }
                
                // Fallback to plain text if nothing else worked
                if (!processedContent) {
                    const text = clipboardData.getData('text/plain');
                    if (text) {
                        document.execCommand('insertText', false, text);
                        
                        // Add helpful message for Word users
                        const helpDiv = document.createElement('div');
                        helpDiv.innerHTML = '<br><div style="background-color: #e6f3ff; border: 1px solid #0066cc; padding: 10px; margin: 10px 0; border-radius: 5px; font-size: 12px;"><strong>💡 Note:</strong> Only text was detected in your paste. If your Word document contains images, please use the <strong>"Insert Image"</strong> button above to add them manually.</div>';
                        
                        const selection = window.getSelection();
                        if (selection.rangeCount > 0) {
                            const range = selection.getRangeAt(0);
                            range.insertNode(helpDiv);
                            
                            // Move cursor after the help message
                            range.setStartAfter(helpDiv);
                            range.setEndAfter(helpDiv);
                            selection.removeAllRanges();
                            selection.addRange(range);
                        }
                        
                        statusBar.textContent = "Text pasted - use 'Insert Image' button for images";
                        console.log('Fallback to plain text');
                    } else {
                        statusBar.textContent = "No pasteable content detected";
                        console.log('No content could be processed');
                    }
                }
            }
            
            // Try alternative image detection methods
            async function tryAlternativeImageFormats(clipboardData, originalEvent) {
                try {
                    // Try to get Files array (newer API)
                    if (clipboardData.files && clipboardData.files.length > 0) {
                        console.log('Found files in clipboard:', clipboardData.files.length);
                        for (let file of clipboardData.files) {
                            console.log('File type:', file.type, 'Size:', file.size);
                            if (file.type.startsWith('image/')) {
                                const success = await processFileAsImage(file);
                                if (success) return true;
                            }
                        }
                    }
                    
                    // Try DataTransfer API approach
                    const dt = originalEvent.clipboardData || originalEvent.dataTransfer;
                    if (dt && dt.files && dt.files.length > 0) {
                        console.log('Found files in DataTransfer:', dt.files.length);
                        for (let file of dt.files) {
                            console.log('DT File type:', file.type, 'Size:', file.size);
                            if (file.type.startsWith('image/')) {
                                const success = await processFileAsImage(file);
                                if (success) return true;
                            }
                        }
                    }
                    
                    return false;
                } catch (error) {
                    console.error('Error in tryAlternativeImageFormats:', error);
                    return false;
                }
            }
            
            // Process a file as an image
            async function processFileAsImage(file) {
                return new Promise((resolve) => {
                    const reader = new FileReader();
                    reader.onload = function(event) {
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
                        
                        statusBar.textContent = "Image pasted successfully";
                        resolve(true);
                    };
                    reader.onerror = () => resolve(false);
                    reader.readAsDataURL(file);
                });
            }
            
            // Enhanced HTML content processing
            async function processHTMLContent(html) {
                try {
                    // Create a temporary div to hold the HTML
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = html;
                    
                    // Find all images in the pasted content
                    const images = tempDiv.querySelectorAll('img');
                    const imageProcessingPromises = [];
                    
                    images.forEach((img, index) => {
                        img.classList.add('pasted-image');
                        
                        // Handle different types of image sources
                        if (img.src) {
                            const promise = processImageSource(img, index);
                            imageProcessingPromises.push(promise);
                        }
                        // Handle Word-specific image formats
                        else if (img.getAttribute('v:shapes') || img.parentElement.tagName === 'V:IMAGEDATA') {
                            // Word uses VML (Vector Markup Language) for images
                            const vmlPromise = processVMLImage(img, index);
                            imageProcessingPromises.push(vmlPromise);
                        }
                    });
                    
                    // Process all images
                    if (imageProcessingPromises.length > 0) {
                        statusBar.textContent = `Processing ${imageProcessingPromises.length} images...`;
                        await Promise.allSettled(imageProcessingPromises);
                    }
                    
                    // Insert the processed content
                    const selection = window.getSelection();
                    if (selection.rangeCount > 0) {
                        const range = selection.getRangeAt(0);
                        range.deleteContents();
                        
                        // Insert all content from tempDiv
                        while (tempDiv.firstChild) {
                            range.insertNode(tempDiv.lastChild);
                        }
                        
                        statusBar.textContent = `Content pasted with ${images.length} image(s)`;
                        return true;
                    }
                } catch (error) {
                    console.error('Error processing HTML content:', error);
                    statusBar.textContent = "Error processing pasted content";
                }
                return false;
            }
            
            // Process individual image sources
            async function processImageSource(img, index) {
                return new Promise((resolve) => {
                    const originalSrc = img.src;
                    
                    // If it's already a data URL, we're good
                    if (originalSrc.startsWith('data:')) {
                        resolve();
                        return;
                    }
                    
                    // If it's a file:// URL (common with Word), try to handle it
                    if (originalSrc.startsWith('file://')) {
                        // We can't directly access file:// URLs from web context
                        // Replace with a placeholder and add to a list for manual handling
                        img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIiBzdHJva2U9IiNjY2MiIHN0cm9rZS13aWR0aD0iMiIvPgogIDx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM2NjYiPkltYWdlIFBsYWNlaG9sZGVyPC90ZXh0Pgo8L3N2Zz4K';
                        img.alt = `Image from Word document (${originalSrc})`;
                        img.title = 'Click "Insert Image" button to manually add this image';
                        img.style.border = '2px dashed #ccc';
                        resolve();
                        return;
                    }
                    
                    // For other URLs, try to load them
                    const tempImg = new Image();
                    tempImg.crossOrigin = 'anonymous';
                    
                    tempImg.onload = function() {
                        try {
                            // Convert to base64
                            const canvas = document.createElement('canvas');
                            canvas.width = this.naturalWidth;
                            canvas.height = this.naturalHeight;
                            const ctx = canvas.getContext('2d');
                            ctx.drawImage(this, 0, 0);
                            
                            const dataURL = canvas.toDataURL('image/png');
                            img.src = dataURL;
                            resolve();
                        } catch (error) {
                            console.error('Error converting image to base64:', error);
                            // Use placeholder
                            img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIiBzdHJva2U9IiNjY2MiIHN0cm9rZS13aWR0aD0iMiIvPgogIDx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM2NjYiPkltYWdlIE5vdCBBdmFpbGFibGU8L3RleHQ+Cjwvc3ZnPgo=';
                            resolve();
                        }
                    };
                    
                    tempImg.onerror = function() {
                        console.warn('Failed to load image:', originalSrc);
                        // Use placeholder for failed images
                        img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIiBzdHJva2U9IiNjY2MiIHN0cm9rZS13aWR0aD0iMiIvPgogIDx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM2NjYiPkltYWdlIE5vdCBBdmFpbGFibGU8L3RleHQ+Cjwvc3ZnPgo=';
                        img.alt = `Failed to load: ${originalSrc}`;
                        resolve();
                    };
                    
                    tempImg.src = originalSrc;
                });
            }
            
            // Process VML images from Word
            async function processVMLImage(img, index) {
                return new Promise((resolve) => {
                    // Word VML images are complex - for now, add a placeholder
                    img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZTZmMmZmIiBzdHJva2U9IiM0Q0FGNTAUCB2w+KCAgPHRleHQgeD0iNTAlIiB5PSI1MCUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzMzNyI+V29yZCBJbWFnZTwvdGV4dD4KPC9zdmc+Cg==';
                    img.alt = 'Image from Word document (VML format)';
                    img.title = 'Use "Insert Image" button to manually add this image';
                    img.style.border = '2px dashed #4CAF50';
                    resolve();
                });
            }
            
            // Process RTF content
            async function processRTFContent(rtf) {
                try {
                    // Extract any base64 image data from RTF
                    // RTF images are often embedded as hexadecimal data
                    const hexImageRegex = /\\\\pict[\\s\\S]*?([0-9a-fA-F\\s]+)(?=\\\\par|\\})/g;
                    const matches = Array.from(rtf.matchAll(hexImageRegex));
                    
                    if (matches.length > 0) {
                        statusBar.textContent = `Found ${matches.length} embedded image(s) in RTF`;
                        
                        // For now, we'll insert a placeholder and the text content
                        // Converting RTF hex to proper images is complex
                        const textContent = rtf.replace(/\\{[^}]*\\}/g, '').replace(/\\\\[a-z]+\\s?/g, '');
                        document.execCommand('insertText', false, textContent);
                        
                        // Add a note about images
                        const imageNote = document.createElement('div');
                        imageNote.innerHTML = '<br><em>Note: Images detected in RTF format. Please use "Insert Image" button to add them manually.</em><br>';
                        imageNote.style.color = '#666';
                        imageNote.style.fontStyle = 'italic';
                        
                        const selection = window.getSelection();
                        if (selection.rangeCount > 0) {
                            const range = selection.getRangeAt(0);
                            range.insertNode(imageNote);
                        }
                        
                        return true;
                    }
                } catch (error) {
                    console.error('Error processing RTF content:', error);
                }
                return false;
            }
            
            // Process direct image items from clipboard
            async function processImageItems(items) {
                let imageInserted = false;
                const imagePromises = [];
                
                Array.from(items).forEach(item => {
                    if (item.type.indexOf('image') !== -1) {
                        const promise = new Promise((resolve) => {
                            const blob = item.getAsFile();
                            
                            const reader = new FileReader();
                            reader.onload = function(event) {
                                const img = document.createElement('img');
                                img.src = event.target.result;
                                img.classList.add('pasted-image');
                                
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
                                resolve();
                            };
                            reader.readAsDataURL(blob);
                        });
                        imagePromises.push(promise);
                    }
                });
                
                if (imagePromises.length > 0) {
                    await Promise.all(imagePromises);
                    statusBar.textContent = `${imagePromises.length} image(s) pasted successfully`;
                    return true;
                }
                
                return false;
            }
            
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
    - **Enhanced Word document paste** with automatic image detection
    
    **📋 Pasting from Word Documents:**
    - The app automatically detects multiple clipboard formats (HTML, RTF, images)
    - Images are processed and converted to base64 for PDF compatibility
    - When images can't be auto-converted, placeholders are shown with dashed borders
    - Use the "Insert Image" button to manually add images that couldn't be processed
    
    **🔧 Troubleshooting Image Issues:**
    - If you see gray "Image Placeholder" boxes, the original image couldn't be accessed
    - Try copying images individually using Ctrl+C then pasting them directly
    - Use the "Insert Image" button to manually upload image files
    - Make sure images are saved in your Word document (not just linked externally)
    
    **💡 Tips for best results:**
    - Copy content directly from Word rather than from email or other sources
    - Check the browser console (F12) for detailed processing information
    - Use the Preview button to verify images display correctly before generating PDF
    - For complex documents, consider saving as HTML from Word first, then uploading
    """)
