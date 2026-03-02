
import os
from convert_md_to_pdf import convert_md_to_pdf

# Path to the artifact markdown file
# Note: In real usage, this path might be dynamic, but I'll hardcode the one I just created.
# Wait, I should probably copy the artifact content here or read it from the artifact path.
# The artifact path is:
# C:\Users\range\.gemini\antigravity\brain\64ead1a0-8b86-4258-93ac-2c3c9a9a79f6\project_report.md

md_path = r"C:\Users\range\.gemini\antigravity\brain\64ead1a0-8b86-4258-93ac-2c3c9a9a79f6\project_report.md"
pdf_path = "project_report.pdf"

if not os.path.exists(md_path):
    print(f"Error: Markdown file not found at {md_path}")
else:
    print(f"Converting {md_path} to {pdf_path}...")
    convert_md_to_pdf(md_path, pdf_path)
    print("Done.")
