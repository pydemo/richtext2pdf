import wx
import wx.html2
import wx.richtext
import tempfile
import os
import threading
import time
from weasyprint import HTML
import base64
import io
import html

class RichTextToPDFFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Rich Text to PDF Converter", size=(1200, 800))
        
        # Initialize variables
        self.last_content = ""
        self.conversion_timer = None
        self.temp_pdf_path = None
        
        # Create the main panel
        main_panel = wx.Panel(self)
        
        # Create splitter window
        splitter = wx.SplitterWindow(main_panel)
        splitter.SetSashGravity(0.5)  # Equal split
        splitter.SetMinimumPaneSize(200)
        
        # Create left panel for rich text input
        left_panel = wx.Panel(splitter)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add label for left panel
        left_label = wx.StaticText(left_panel, label="Rich Text Input (Paste your formatted text here)")
        left_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        left_sizer.Add(left_label, 0, wx.ALL | wx.EXPAND, 5)
        
        # Create RichTextCtrl for better formatting support
        self.rich_text_ctrl = wx.richtext.RichTextCtrl(
            left_panel, 
            style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER,
            size=(-1, -1)
        )
        
        # Set up some basic styling
        self.rich_text_ctrl.GetBuffer().SetFontTable(wx.richtext.RichTextFontTable())
        self.rich_text_ctrl.GetBuffer().SetStyleSheet(wx.richtext.RichTextStyleSheet())
        
        # Create formatting toolbar
        toolbar = wx.Panel(left_panel)
        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Bold button
        bold_btn = wx.Button(toolbar, label="B", size=(30, 25))
        bold_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        bold_btn.Bind(wx.EVT_BUTTON, self.on_bold)
        toolbar_sizer.Add(bold_btn, 0, wx.ALL, 2)
        
        # Italic button
        italic_btn = wx.Button(toolbar, label="I", size=(30, 25))
        italic_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        italic_btn.Bind(wx.EVT_BUTTON, self.on_italic)
        toolbar_sizer.Add(italic_btn, 0, wx.ALL, 2)
        
        # Underline button
        underline_btn = wx.Button(toolbar, label="U", size=(30, 25))
        underline_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, True))
        underline_btn.Bind(wx.EVT_BUTTON, self.on_underline)
        toolbar_sizer.Add(underline_btn, 0, wx.ALL, 2)
        
        toolbar.SetSizer(toolbar_sizer)
        left_sizer.Add(toolbar, 0, wx.ALL | wx.EXPAND, 5)
        
        # Set initial text with some examples
        self.rich_text_ctrl.WriteText("Welcome to Rich Text to PDF Converter!\n\n")
        
        # Add some formatted example text
        self.rich_text_ctrl.BeginBold()
        self.rich_text_ctrl.WriteText("Try pasting formatted text here. Supported features:\n")
        self.rich_text_ctrl.EndBold()
        
        self.rich_text_ctrl.WriteText("1. ")
        self.rich_text_ctrl.BeginBold()
        self.rich_text_ctrl.WriteText("Bold")
        self.rich_text_ctrl.EndBold()
        self.rich_text_ctrl.WriteText(" and ")
        self.rich_text_ctrl.BeginItalic()
        self.rich_text_ctrl.WriteText("italic")
        self.rich_text_ctrl.EndItalic()
        self.rich_text_ctrl.WriteText(" text (paste from Word/Google Docs)\n")
        
        self.rich_text_ctrl.WriteText("2. Different font sizes and colors\n")
        self.rich_text_ctrl.WriteText("3. Lists and bullet points\n")
        self.rich_text_ctrl.WriteText("4. Live PDF conversion as you type!\n\n")
        
        self.rich_text_ctrl.BeginItalic()
        self.rich_text_ctrl.WriteText("You can paste rich text from:\n")
        self.rich_text_ctrl.EndItalic()
        
        self.rich_text_ctrl.WriteText("• Microsoft Word\n")
        self.rich_text_ctrl.WriteText("• Google Docs\n")
        self.rich_text_ctrl.WriteText("• Web pages\n")
        self.rich_text_ctrl.WriteText("• Email clients\n\n")
        
        self.rich_text_ctrl.WriteText("The text will be converted to HTML and then to PDF automatically.")
        
        # Bind events for live conversion
        self.rich_text_ctrl.Bind(wx.EVT_TEXT, self.on_text_changed)
        self.rich_text_ctrl.Bind(wx.EVT_KEY_UP, self.on_key_up)
        
        left_sizer.Add(self.rich_text_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        
        # Add conversion status
        self.status_text = wx.StaticText(left_panel, label="Status: Ready")
        self.status_text.SetForegroundColour(wx.Colour(0, 128, 0))
        left_sizer.Add(self.status_text, 0, wx.ALL | wx.EXPAND, 5)
        
        left_panel.SetSizer(left_sizer)
        
        # Create right panel for PDF display
        right_panel = wx.Panel(splitter)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add label for right panel
        right_label = wx.StaticText(right_panel, label="PDF Preview (Auto-updates)")
        right_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        right_sizer.Add(right_label, 0, wx.ALL | wx.EXPAND, 5)
        
        # Create text control for PDF status (since WebView might not be available)
        try:
            self.pdf_viewer = wx.html2.WebView.New(right_panel)
            self.pdf_viewer_type = "webview"
            right_sizer.Add(self.pdf_viewer, 1, wx.ALL | wx.EXPAND, 5)
        except Exception as e:
            # Fallback to text control for status display
            self.pdf_viewer = wx.TextCtrl(
                right_panel,
                style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP,
                size=(-1, -1)
            )
            self.pdf_viewer_type = "text"
            self.pdf_viewer.SetValue("PDF Preview:\n\nWebView component not available on this system.\nPDF files will be generated in the background.\nUse 'Save PDF' from the File menu to save the converted PDF.\n\nThe application will show conversion status here.")
            right_sizer.Add(self.pdf_viewer, 1, wx.ALL | wx.EXPAND, 5)
        
        right_panel.SetSizer(right_sizer)
        
        # Split the window
        splitter.SplitVertically(left_panel, right_panel)
        
        # Create main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(splitter, 1, wx.EXPAND)
        main_panel.SetSizer(main_sizer)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.CreateStatusBar()
        self.SetStatusText("Ready - Start typing or paste rich text to see live PDF conversion")
        
        # Center the window
        self.Center()
        
        # Initial conversion
        wx.CallAfter(self.convert_to_pdf)
    
    def create_menu_bar(self):
        menubar = wx.MenuBar()
        
        # File menu
        file_menu = wx.Menu()
        
        new_item = file_menu.Append(wx.ID_NEW, '&New\tCtrl+N', 'Create new document')
        open_item = file_menu.Append(wx.ID_OPEN, '&Open\tCtrl+O', 'Open rich text file')
        save_item = file_menu.Append(wx.ID_SAVE, '&Save RTF\tCtrl+S', 'Save as rich text file')
        file_menu.AppendSeparator()
        save_pdf_item = file_menu.Append(wx.ID_SAVEAS, 'Save &PDF\tCtrl+Shift+S', 'Save as PDF file')
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, 'E&xit\tCtrl+Q', 'Exit application')
        
        # Edit menu
        edit_menu = wx.Menu()
        copy_item = edit_menu.Append(wx.ID_COPY, '&Copy\tCtrl+C', 'Copy selection')
        paste_item = edit_menu.Append(wx.ID_PASTE, '&Paste\tCtrl+V', 'Paste from clipboard')
        edit_menu.AppendSeparator()
        clear_item = edit_menu.Append(wx.ID_CLEAR, 'C&lear', 'Clear all content')
        
        # Help menu
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, '&About', 'About this application')
        
        menubar.Append(file_menu, '&File')
        menubar.Append(edit_menu, '&Edit')
        menubar.Append(help_menu, '&Help')
        
        self.SetMenuBar(menubar)
        
        # Bind menu events
        self.Bind(wx.EVT_MENU, self.on_new, new_item)
        self.Bind(wx.EVT_MENU, self.on_open, open_item)
        self.Bind(wx.EVT_MENU, self.on_save, save_item)
        self.Bind(wx.EVT_MENU, self.on_save_pdf, save_pdf_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_copy, copy_item)
        self.Bind(wx.EVT_MENU, self.on_paste, paste_item)
        self.Bind(wx.EVT_MENU, self.on_clear, clear_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)
    
    def on_text_changed(self, event):
        """Handle text changes for live conversion"""
        self.schedule_conversion()
        event.Skip()
    
    def on_key_up(self, event):
        """Handle key up events for live conversion"""
        self.schedule_conversion()
        event.Skip()
    
    def schedule_conversion(self):
        """Schedule PDF conversion with a small delay to avoid too frequent updates"""
        if self.conversion_timer:
            self.conversion_timer.Stop()
        
        self.conversion_timer = wx.CallLater(500, self.convert_to_pdf)  # 500ms delay
    
    def convert_to_pdf(self):
        """Convert rich text content to PDF"""
        try:
            # Get rich text as HTML
            html_content = self.rich_text_to_html()
            
            # Check if content has changed
            if html_content == self.last_content:
                return
            
            self.last_content = html_content
            
            # Update status
            self.status_text.SetLabel("Status: Converting to PDF...")
            self.status_text.SetForegroundColour(wx.Colour(255, 165, 0))  # Orange
            
            # Perform conversion in a separate thread to avoid blocking UI
            thread = threading.Thread(target=self.convert_to_pdf_worker, args=(html_content,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            wx.CallAfter(self.show_error, f"Conversion error: {str(e)}")
    
    def convert_to_pdf_worker(self, html_content):
        """Worker thread for PDF conversion"""
        try:
            # Create styled HTML with CSS
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
                    }}
                    h1, h2, h3 {{ color: #2C3E50; }}
                    img {{ max-width: 100%; height: auto; }}
                    .highlight {{ background-color: #FFFFCC; padding: 2px 5px; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # Create temporary PDF file
            if self.temp_pdf_path and os.path.exists(self.temp_pdf_path):
                os.unlink(self.temp_pdf_path)
            
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
                self.temp_pdf_path = tmp_pdf.name
                HTML(string=styled_html).write_pdf(tmp_pdf.name)
            
            # Update UI in main thread
            wx.CallAfter(self.update_pdf_viewer)
            
        except Exception as e:
            wx.CallAfter(self.show_error, f"PDF generation error: {str(e)}")
    
    def update_pdf_viewer(self):
        """Update the PDF viewer with the new PDF"""
        try:
            if self.temp_pdf_path and os.path.exists(self.temp_pdf_path):
                # Get file size for display
                file_size = os.path.getsize(self.temp_pdf_path)
                file_size_kb = file_size / 1024
                
                # Load PDF in viewer
                if self.pdf_viewer_type == "webview":
                    # For WebView
                    file_url = f"file://{self.temp_pdf_path}"
                    self.pdf_viewer.LoadURL(file_url)
                else:
                    # For text control fallback
                    status_message = f"""PDF Generated Successfully!

File: {self.temp_pdf_path}
Size: {file_size_kb:.1f} KB
Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}

The PDF has been created and is ready for saving.
Use 'Save PDF' from the File menu to save it to your desired location.

Live conversion is active - the PDF will update automatically as you type or paste new content."""
                    
                    self.pdf_viewer.SetValue(status_message)
                
                # Update status
                self.status_text.SetLabel("Status: PDF updated successfully")
                self.status_text.SetForegroundColour(wx.Colour(0, 128, 0))  # Green
                
                self.SetStatusText("PDF converted successfully - Live preview updated")
            
        except Exception as e:
            self.show_error(f"PDF viewer update error: {str(e)}")
    
    def rich_text_to_html(self):
        """Convert RichTextCtrl content to HTML with proper formatting"""
        try:
            # Use the built-in HTML handler to get properly formatted HTML
            handler = wx.richtext.RichTextHTMLHandler()
            stream = io.StringIO()
            
            # Export to HTML
            handler.SaveStream(self.rich_text_ctrl.GetBuffer(), stream)
            html_content = stream.getvalue()
            
            # Clean up the HTML - remove unnecessary parts
            if '<body>' in html_content and '</body>' in html_content:
                start = html_content.find('<body>') + 6
                end = html_content.find('</body>')
                html_content = html_content[start:end].strip()
            
            return html_content
            
        except Exception:
            # Fallback to simple conversion
            try:
                plain_text = self.rich_text_ctrl.GetValue()
                escaped_text = html.escape(plain_text)
                lines = escaped_text.split('\n')
                html_lines = []
                
                for line in lines:
                    if line.strip():
                        html_lines.append(f"<p>{line}</p>")
                    else:
                        html_lines.append("<br>")
                
                return '\n'.join(html_lines)
            except Exception:
                # Ultimate fallback
                plain_text = self.rich_text_ctrl.GetValue()
                escaped_text = html.escape(plain_text)
                return f"<pre>{escaped_text}</pre>"
    
    def show_error(self, message):
        """Show error message"""
        self.status_text.SetLabel(f"Status: Error - {message}")
        self.status_text.SetForegroundColour(wx.Colour(255, 0, 0))  # Red
        self.SetStatusText(f"Error: {message}")
        
        wx.MessageBox(message, "Error", wx.OK | wx.ICON_ERROR)
    
    # Formatting event handlers
    def on_bold(self, event):
        """Toggle bold formatting for selected text"""
        if self.rich_text_ctrl.HasSelection():
            # Apply bold to selection
            self.rich_text_ctrl.ApplyBoldToSelection()
        else:
            # Toggle bold for current typing position
            attr = self.rich_text_ctrl.GetDefaultStyle()
            if attr.GetFontWeight() == wx.FONTWEIGHT_BOLD:
                attr.SetFontWeight(wx.FONTWEIGHT_NORMAL)
            else:
                attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
            self.rich_text_ctrl.SetDefaultStyle(attr)
        
        self.rich_text_ctrl.SetFocus()
        self.schedule_conversion()
    
    def on_italic(self, event):
        """Toggle italic formatting for selected text"""
        if self.rich_text_ctrl.HasSelection():
            # Apply italic to selection
            self.rich_text_ctrl.ApplyItalicToSelection()
        else:
            # Toggle italic for current typing position
            attr = self.rich_text_ctrl.GetDefaultStyle()
            if attr.GetFontStyle() == wx.FONTSTYLE_ITALIC:
                attr.SetFontStyle(wx.FONTSTYLE_NORMAL)
            else:
                attr.SetFontStyle(wx.FONTSTYLE_ITALIC)
            self.rich_text_ctrl.SetDefaultStyle(attr)
        
        self.rich_text_ctrl.SetFocus()
        self.schedule_conversion()
    
    def on_underline(self, event):
        """Toggle underline formatting for selected text"""
        if self.rich_text_ctrl.HasSelection():
            # Apply underline to selection
            self.rich_text_ctrl.ApplyUnderlineToSelection()
        else:
            # Toggle underline for current typing position
            attr = self.rich_text_ctrl.GetDefaultStyle()
            attr.SetFontUnderlined(not attr.GetFontUnderlined())
            self.rich_text_ctrl.SetDefaultStyle(attr)
        
        self.rich_text_ctrl.SetFocus()
        self.schedule_conversion()
    
    # Menu event handlers
    def on_new(self, event):
        self.rich_text_ctrl.Clear()
        self.convert_to_pdf()
    
    def on_open(self, event):
        with wx.FileDialog(self, "Open RTF file", 
                          wildcard="RTF files (*.rtf)|*.rtf|Text files (*.txt)|*.txt",
                          style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.rich_text_ctrl.SetValue(content)
                    self.convert_to_pdf()
            except Exception as e:
                wx.MessageBox(f"Cannot open file: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
    
    def on_save(self, event):
        with wx.FileDialog(self, "Save text file",
                          wildcard="Text files (*.txt)|*.txt|RTF files (*.rtf)|*.rtf",
                          style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            
            pathname = fileDialog.GetPath()
            try:
                # Save as text file
                content = self.rich_text_ctrl.GetValue()
                with open(pathname, 'w', encoding='utf-8') as file:
                    file.write(content)
                wx.MessageBox("File saved successfully!", "Success", wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f"Cannot save file: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
    
    def on_save_pdf(self, event):
        with wx.FileDialog(self, "Save PDF file",
                          wildcard="PDF files (*.pdf)|*.pdf",
                          style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            
            pathname = fileDialog.GetPath()
            try:
                if self.temp_pdf_path and os.path.exists(self.temp_pdf_path):
                    # Copy temporary PDF to desired location
                    import shutil
                    shutil.copy2(self.temp_pdf_path, pathname)
                    wx.MessageBox("PDF saved successfully!", "Success", wx.OK | wx.ICON_INFORMATION)
                else:
                    wx.MessageBox("No PDF available to save. Please wait for conversion to complete.", "Error", wx.OK | wx.ICON_ERROR)
            except Exception as e:
                wx.MessageBox(f"Cannot save PDF: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
    
    def on_copy(self, event):
        self.rich_text_ctrl.Copy()
    
    def on_paste(self, event):
        self.rich_text_ctrl.Paste()
        self.convert_to_pdf()
    
    def on_clear(self, event):
        self.rich_text_ctrl.Clear()
        self.convert_to_pdf()
    
    def on_exit(self, event):
        self.cleanup()
        self.Destroy()
    
    def on_about(self, event):
        info = wx.adv.AboutDialogInfo()
        info.SetName("Rich Text to PDF Converter")
        info.SetVersion("1.0")
        info.SetDescription("A wxPython application that converts rich text to PDF with live preview.\n\nFeatures:\n- Live PDF conversion as you type\n- Rich text formatting support\n- Split-pane interface\n- Save as RTF or PDF formats")
        info.SetCopyright("(C) 2025")
        info.AddDeveloper("Created with wxPython and WeasyPrint")
        
        wx.adv.AboutBox(info)
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_pdf_path and os.path.exists(self.temp_pdf_path):
            try:
                os.unlink(self.temp_pdf_path)
            except:
                pass

class RichTextToPDFApp(wx.App):
    def OnInit(self):
        frame = RichTextToPDFFrame()
        frame.Show()
        return True

def main():
    """Main entry point"""
    try:
        app = RichTextToPDFApp()
        app.MainLoop()
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        print("Please make sure you have wxPython and weasyprint installed:")
        print("pip install wxpython weasyprint")

if __name__ == '__main__':
    main()
