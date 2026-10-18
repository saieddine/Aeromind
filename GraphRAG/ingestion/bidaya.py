import pdfplumber
from pathlib import Path


def text_extractor(input_pdf):
    pdf_path = Path(input_pdf)

    if pdf_path.exists():
        with pdfplumber.open(pdf_path) as pdf:
            pages = []

            for number, page in enumerate(pdf.pages, start = 1):
             text = page.extract_text() 

             if text:
                text_and_page = {
                   "text" :text,
                   "page" :number
                }

                pages.append(text_and_page)

        return pages
                

    else :
        print("file not found")
        return None



             
             

        