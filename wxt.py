import os, tempfile, datetime, subprocess, sys
import html

def get_clipboard_content():
    """Get clipboard content on Linux"""
    try:
        # Try xclip first (most common)
        result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                              capture_output=True, text=True, check=True)
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Try xsel as fallback
            result = subprocess.run(['xsel', '--clipboard', '--output'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: No clipboard tool found. Please install xclip or xsel:")
            print("  sudo apt-get install xclip")
            print("  # or")
            print("  sudo apt-get install xsel")
            sys.exit(1)

def text_to_html(text):
    """Convert plain text to basic HTML with preserved formatting"""
    if not text.strip():
        return "<p>No content in clipboard</p>"
    
    # Escape HTML characters
    escaped_text = html.escape(text)
    
    # Convert line breaks to paragraphs
    lines = escaped_text.split('\n')
    html_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            html_lines.append(f"<p>{line}</p>")
        else:
            html_lines.append("<br>")
    
    return '\n'.join(html_lines)

def create_pdf_from_text(text, output_file):
    """Create PDF from text using weasyprint"""
    try:
        from weasyprint import HTML
    except ImportError:
        print("Error: weasyprint not installed. Install it with:")
        print("  pip install weasyprint")
        sys.exit(1)
    
    # Convert text to HTML
    html_content = text_to_html(text)
    
    # Create styled HTML document
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                line-height: 1.6;
                color: #333;
            }}
            p {{
                margin: 0 0 10px 0;
            }}
            h1, h2, h3 {{
                color: #2C3E50;
                margin-top: 20px;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <h1>Clipboard Content</h1>
        <div class="content">
            {html_content}
        </div>
        <div style="margin-top: 30px; font-size: 10px; color: #666;">
            Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </body>
    </html>
    """
    
    # Generate PDF
    HTML(string=styled_html).write_pdf(output_file)

# Main execution
outfile = os.path.join(
    tempfile.gettempdir(),
    f"clipboard_{datetime.datetime.now():%Y%m%d_%H%M%S}.pdf"
)

try:
    # Get clipboard content
    clipboard_text = get_clipboard_content()
    
    if not clipboard_text.strip():
        print("Warning: Clipboard is empty or contains no text")
        clipboard_text = "Clipboard was empty when PDF was generated."
    
    # Create PDF
    create_pdf_from_text(clipboard_text, outfile)
    
    print("Saved:", outfile)
    print(f"Content length: {len(clipboard_text)} characters")
    
except Exception as e:
    print(f"Error: {str(e)}")
    sys.exit(1)
