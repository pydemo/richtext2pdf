# 📝 Streamlit Rich Text + Image to PDF Converter

This Streamlit app lets you **paste rich text (HTML with formatting and inline images)** into a text area, **preview it**, and **export it as a PDF** — all without uploading images separately.

## 🚀 Features

- Paste HTML from Word, Gmail, Google Docs, etc.
- Supports inline **Base64-encoded images**
- Live HTML preview in browser
- One-click **PDF export** using `WeasyPrint`

## 📸 What Works

✅ Bold / Italics / Paragraphs  
✅ Lists  
✅ Inline `<img>` with Base64 source  
✅ Most standard HTML & inline CSS styles  

## 🛠️ Installation

### Requirements

Python 3.8+  
Install dependencies:

```bash
pip install streamlit weasyprint
