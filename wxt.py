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
