"""
Diagnostic: search the raw IMD (and RBI) PDFs directly for any
El Nino / La Nina / ENSO mention, bypassing the extraction
pipeline entirely. This tells us whether the term is genuinely
in the source PDFs and getting lost somewhere downstream
(encoding corruption, keyword mismatch, or the paragraph-level
filters), versus just not being there in the first place.
"""

import fitz
import re
import os

fitz.TOOLS.mupdf_display_errors(False)
fitz.TOOLS.mupdf_display_warnings(False)

FOLDERS = {
    "IMD": r"D:\Elnino\imd",
    "RBI": r"D:\Elnino\rbi"
}

# Matches "El Nino" with ANY single character (or none) standing
# in for the "n~o" - catches "Niño", "Nino", "Ni?o", "Nifio",
# "Niiio" and similar encoding-mangled variants. Also plain ASCII.
PATTERN = re.compile(
    r"el\s*ni.?o|la\s*ni.?a|\benso\b",
    re.IGNORECASE
)

for source, folder in FOLDERS.items():

    print("=" * 60)
    print(f"Scanning {source}: {folder}")
    print("=" * 60)

    if not os.path.exists(folder):

        print("  Folder not found.")

        continue

    pdf_files = sorted(f for f in os.listdir(folder) if f.lower().endswith(".pdf"))

    total_hits = 0

    for pdf_name in pdf_files:

        pdf_path = os.path.join(folder, pdf_name)

        try:

            doc = fitz.open(pdf_path)

        except Exception as e:

            print(f"  Cannot open {pdf_name}: {e}")

            continue

        file_hits = 0

        for page_no in range(len(doc)):

            text = doc.load_page(page_no).get_text()

            matches = PATTERN.findall(text)

            if matches:

                file_hits += len(matches)

                total_hits += len(matches)

                # Show a snippet around the first match on this page

                m = PATTERN.search(text)

                start = max(0, m.start() - 60)

                end = min(len(text), m.end() + 60)

                snippet = text[start:end].replace("\n", " ")

                print(f"  {pdf_name}  page {page_no + 1}  match='{m.group()}'")

                print(f"    ...{snippet}...")

        doc.close()

    print(f"\n  {source} total raw matches: {total_hits}\n")