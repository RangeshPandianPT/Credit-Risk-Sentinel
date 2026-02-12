import markdown
from fpdf import FPDF
import os

def convert_md_to_pdf(md_file, pdf_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Sanitize text for Latin-1 (standard PDF fonts)
    replacements = {
        '\u2018': "'", '\u2019': "'",  # Smart quotes
        '\u201c': '"', '\u201d': '"',  # Smart double quotes
        '\u2013': '-', '\u2014': '--', # Dashes
        '\u2026': '...',               # Ellipsis
        '\u00A0': ' '                  # Non-breaking space
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)

    # 2. Convert to HTML
    # We use 'extra' extension to support tables which are present in the report
    html = markdown.markdown(text, extensions=['extra'])
    
    # 3. PDF Generation Class
    class PDF(FPDF):
        def header(self):
            self.set_font('helvetica', 'B', 15)
            # self.cell(0, 10, 'Pre-Delinquency Intervention Engine', border=False, ln=1, align='C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('helvetica', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', align='C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    
    # Simple styling for fpdf write_html
    # Note: fpdf2 has limited HTML support, so we keep it simple.
    # It might struggle with complex tables, but basic ones usually work or degrade gracefully.
    try:
        pdf.write_html(html)
        pdf.output(pdf_file)
        print(f"Successfully generated PDF: {pdf_file}")
    except Exception as e:
        print(f"Error generating PDF: {e}")

if __name__ == "__main__":
    # Artifact path constraints
    base_dir = r"C:\Users\range\.gemini\antigravity\brain\2a6b9559-32a7-402a-83b1-a43147c9b6d1"
    md_path = os.path.join(base_dir, "project_proposal_report.md")
    pdf_path = os.path.join(base_dir, "project_proposal_report.pdf")
    
    convert_md_to_pdf(md_path, pdf_path)
