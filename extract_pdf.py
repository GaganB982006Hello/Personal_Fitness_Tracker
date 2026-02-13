import pypdf
import os

pdf_path = 'Fitness_Tracker_AICTE_Report by Gagan B.pdf'
output_path = 'report_extraction.txt'

if os.path.exists(pdf_path):
    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ''
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + '\n'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Successfully extracted text to {output_path}")
    except Exception as e:
        print(f"Error extracting PDF: {e}")
else:
    print(f"File not found: {pdf_path}")
