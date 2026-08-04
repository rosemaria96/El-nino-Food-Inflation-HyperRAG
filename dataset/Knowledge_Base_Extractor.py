"""
=========================================================
Knowledge Base Extractor
Author : Rose Maria
Purpose:
Extract useful knowledge from IMD and RBI annual reports
for Hyper-RAG 
=========================================================
"""

import fitz
import os
import re
import pandas as pd

# =========================================================
# Suppress MuPDF warnings
# =========================================================

fitz.TOOLS.mupdf_display_errors(False)
fitz.TOOLS.mupdf_display_warnings(False)

# =========================================================
# Configuration
# =========================================================

FOLDERS = {
    "IMD": r"D:\Elnino\imd",
    "RBI": r"D:\Elnino\rbi"
}

OUTPUT_FILE = r"D:\Elnino\dataset\Knowledge_Base_Clean.xlsx"

# =========================================================
# IMD Keywords
# =========================================================

IMD_KEYWORDS = [

    "el niño",
    "el nino",
    "la niña",
    "la nina",
    "enso",

    "monsoon",
    "rainfall",
    "rainfall deficit",
    "rainfall excess",

    "drought",
    "dry spell",

    "heat wave",
    "temperature anomaly",

    "agriculture",
    "crop",

    "kharif",
    "rabi"

]

# =========================================================
# RBI Keywords
# =========================================================

RBI_KEYWORDS = [

    "food inflation",

    "consumer price inflation",

    "cpi",

    "fuel inflation",

    "food prices",

    "vegetable prices",

    "inflation",

    "supply shock",

    "monsoon",

    "el niño",
    "el nino",

    "climate",

    "agriculture",

    "rainfall"

]

# =========================================================
# Skip Words
# =========================================================

SKIP_WORDS = [

    "table of contents",
    "contents",
    "appendix",
    "annex",

    "financial statements",
    "balance sheet",

    "statement",

    "schedule",

    "list of",

    "copyright",

    "photo",

    "figure",

    "table",

    "chapter",

    "index"

]

# =========================================================
# Bad Phrases
# =========================================================

BAD_PHRASES = [

    "fig.",

    "figure",

    "map of india",

    "training programme",

    "workshop",

    "seminar",

    "conference",

    "algorithm",

    "matrix",

    "equation"

    # NOTE: "forecast verification", "hazard prone", and "skill
    # score" were removed from this list - they're normal IMD
    # forecast-outlook vocabulary that legitimately co-occurs with
    # genuine El Nino/monsoon explanatory paragraphs, and were
    # causing those paragraphs to be discarded entirely.

]

# =========================================================
# Cause / Effect Words
# =========================================================

REASON_WORDS = [

    "because",

    "due to",

    "led to",

    "resulted in",

    "caused",

    "impact",

    "affected",

    "therefore",

    "contributed",

    "increase",

    "decrease",

    "higher",

    "lower",

    "rise",

    "decline"

]

# =========================================================
# ENSO-specific words (used for scoring boost)
# =========================================================

ENSO_WORDS = [

    "el niño",
    "el nino",
    "la niña",
    "la nina",
    "enso"

]

# =========================================================
# Extract Year
# =========================================================

def extract_year(filename, source):

    if source == "RBI":

        m = re.search(r"ANNUALREPORT(20\d{2})_\d{2}", filename.upper())

        if m:
            return m.group(1)

    m = re.search(r"(20\d{2})", filename)

    if m:
        return m.group(1)

    return "Unknown"

# =========================================================
# Skip Paragraph?
# =========================================================

def should_skip_paragraph(paragraph):

    paragraph = paragraph.strip()

    if len(paragraph) < 180:

        return True

    if len(paragraph.split()) < 25:

        return True

    lower = paragraph.lower()

    if any(word in lower for word in SKIP_WORDS):

        return True

    if any(word in lower for word in BAD_PHRASES):

        return True

    if re.search(r"\.{5,}", paragraph):

        return True

    if re.search(r"(table\s*\d+|figure\s*\d+)", lower):

        return True

    if re.fullmatch(r"\d+", paragraph):

        return True

    digits = len(re.findall(r"\d", paragraph))

    letters = len(re.findall(r"[A-Za-z]", paragraph))

    if letters == 0:

        return True

    if digits / letters > 0.25:

        return True

    return False

# =========================================================
# Find Keywords
# =========================================================

def find_keywords(paragraph, keywords):

    lower = paragraph.lower()

    found = []

    for keyword in keywords:

        if keyword in lower:

            found.append(keyword)

    return sorted(set(found))

# =========================================================
# Topic Classification (Improvement 1)
# =========================================================
# A paragraph can belong to MULTIPLE topics, so instead of
# returning on the first match (elif chain), we check every
# category independently and collect all that apply.
# =========================================================

def classify_topics(paragraph):

    lower = paragraph.lower()

    topics = []

    if any(k in lower for k in [

        "el niño",

        "el nino",

        "la niña",

        "la nina",

        "enso"

    ]):

        topics.append("Climate")

    if any(k in lower for k in [

        "monsoon",

        "rainfall",

        "rainfall deficit",

        "rainfall excess",

        "drought",

        "dry spell",

        "heat wave"

    ]):

        topics.append("Monsoon")

    if any(k in lower for k in [

        "crop",

        "agriculture",

        "kharif",

        "rabi"

    ]):

        topics.append("Agriculture")

    if any(k in lower for k in [

        "food inflation",

        "food prices",

        "vegetable prices"

    ]):

        topics.append("Food Inflation")

    if any(k in lower for k in [

        "fuel inflation",

        "fuel price",

        "crude oil"

    ]):

        topics.append("Fuel")

    if any(k in lower for k in [

        "consumer price inflation",

        "inflation",

        "cpi"

    ]):

        topics.append("Inflation")

    if "supply shock" in lower:

        topics.append("Supply Shock")

    return topics

# =========================================================
# Check Cause / Effect Words
# =========================================================

def has_reason_words(paragraph):

    lower = paragraph.lower()

    return any(word in lower for word in REASON_WORDS)

# =========================================================
# Relevance Score (Improvement 3)
# =========================================================
# Score = number of matched keywords
#         + 3 if the paragraph contains cause/effect language
#         + 1 if the paragraph specifically mentions El Niño /
#             La Niña / ENSO
#
# Example: 4 keywords + reason words + El Niño mention
#          = 4 + 3 + 1 = 8
# =========================================================

def calculate_relevance_score(paragraph, found_keywords):

    lower = paragraph.lower()

    score = len(found_keywords)

    if has_reason_words(paragraph):

        score += 3

    if any(word in lower for word in ENSO_WORDS):

        score += 1

    return score

# =========================================================
# Process a Single PDF
# =========================================================

def process_pdf(pdf_path, source, keywords):

    results = []

    pdf_name = os.path.basename(pdf_path)

    year = extract_year(pdf_name, source)

    print(f"   Reading: {pdf_name}")

    try:
        doc = fitz.open(pdf_path)

    except Exception as e:

        print(f"   Cannot open {pdf_name}")

        print(e)

        return results

    # ---------------------------------------------
    # Read every page
    # ---------------------------------------------

    for page_no in range(len(doc)):

        try:

            page = doc.load_page(page_no)

            blocks = page.get_text("blocks")

        except Exception:

            continue

        # -----------------------------------------
        # Chunk counter resets per page (Improvement 2)
        # -----------------------------------------

        chunk_no = 0

        # -----------------------------------------
        # Read each text block
        # -----------------------------------------

        for block in blocks:

            try:

                paragraph = block[4]

            except IndexError:

                continue

            paragraph = paragraph.replace("\n", " ")

            paragraph = re.sub(r"\s+", " ", paragraph)

            paragraph = paragraph.strip()

            # -----------------------------------------
            # Skip unwanted paragraphs
            # -----------------------------------------

            if should_skip_paragraph(paragraph):

                continue

            # -----------------------------------------
            # Find keywords
            # -----------------------------------------

            found = find_keywords(paragraph, keywords)

            # Require at least TWO keywords - UNLESS the paragraph
            # already names El Nino/La Nina/ENSO directly. That term
            # is specific enough on its own; requiring a second
            # keyword in the same text block was silently dropping
            # genuine El Nino paragraphs whenever PyMuPDF split a
            # forecast paragraph away from a nearby "monsoon"/
            # "drought" mention (common near tables and columns).

            mentions_enso = any(word in paragraph.lower() for word in ENSO_WORDS)

            if len(found) < 2 and not mentions_enso:

                continue

            # -----------------------------------------
            # Topic Classification (multi-topic)
            # -----------------------------------------

            topics = classify_topics(paragraph)

            if not topics:

                continue

            # -----------------------------------------
            # Keep explanatory paragraphs - unless the
            # paragraph already names El Nino/La Nina/ENSO,
            # in which case it's kept even without explicit
            # cause/effect language (e.g. "El Nino conditions
            # are expected to persist through the season" is
            # still useful retrieval context on its own).
            # -----------------------------------------

            if not has_reason_words(paragraph) and not mentions_enso:

                continue

            # -----------------------------------------
            # Unique Document ID (Improvement 2)
            # e.g. IMD_2012_P31_C1
            # -----------------------------------------

            chunk_no += 1

            doc_id = f"{source}_{year}_P{page_no + 1}_C{chunk_no}"

            # -----------------------------------------
            # Relevance Score (Improvement 3)
            # -----------------------------------------

            score = calculate_relevance_score(paragraph, found)

            # -----------------------------------------
            # Save Result
            # -----------------------------------------

            results.append({

                "Doc_ID": doc_id,

                "Year": year,

                "Source": source,

                "Topics": ", ".join(topics),

                "File": pdf_name,

                "Page": page_no + 1,

                "Keywords": ", ".join(found),

                "Relevance_Score": score,

                "Extracted_Text": paragraph

            })

    doc.close()

    return results


# =========================================================
# Process Folder
# =========================================================

def process_folder(source, folder):

    folder_results = []

    print("\n=========================================")
    print(f"Processing {source}")
    print("=========================================")

    if not os.path.exists(folder):

        print("Folder not found:", folder)

        return folder_results

    pdf_files = sorted([

        f for f in os.listdir(folder)

        if f.lower().endswith(".pdf")

    ])

    print("Total PDFs:", len(pdf_files))

    if source == "IMD":

        keywords = IMD_KEYWORDS

    else:

        keywords = RBI_KEYWORDS

    # -----------------------------------------
    # Process every PDF
    # -----------------------------------------

    for pdf in pdf_files:

        pdf_path = os.path.join(folder, pdf)

        pdf_results = process_pdf(

            pdf_path,

            source,

            keywords

        )

        folder_results.extend(pdf_results)

    print(f"{source} Records: {len(folder_results)}")

    return folder_results


# =========================================================
# Process All Sources
# =========================================================

def process_all_sources():

    all_results = []

    for source, folder in FOLDERS.items():

        folder_results = process_folder(

            source,

            folder

        )

        all_results.extend(folder_results)

    return all_results

# =========================================================
# Export Results
# =========================================================

def export_to_excel(results):

    if not results:

        print("\nNo records found.")

        return

    df = pd.DataFrame(results)

    # -----------------------------------------
    # Remove duplicate paragraphs
    # -----------------------------------------

    df.drop_duplicates(

        subset=[

            "Source",
            "Extracted_Text"

        ],

        inplace=True

    )

    # -----------------------------------------
    # Sort (highest relevance first within each group)
    # -----------------------------------------

    df.sort_values(

        by=[

            "Year",
            "Source",
            "Relevance_Score",
            "Page"

        ],

        ascending=[

            True,
            True,
            False,
            True

        ],

        inplace=True

    )

    # -----------------------------------------
    # Reset Index
    # -----------------------------------------

    df.reset_index(

        drop=True,

        inplace=True

    )

    # -----------------------------------------
    # Save Excel
    # -----------------------------------------

    os.makedirs(

        os.path.dirname(OUTPUT_FILE),

        exist_ok=True

    )

    df.to_excel(

        OUTPUT_FILE,

        index=False

    )

    # -----------------------------------------
    # Statistics
    # -----------------------------------------

    print("\n======================================")
    print("Knowledge Base Created Successfully")
    print("======================================")

    print(f"Total Records : {len(df)}")

    print("\nRecords by Source")

    print(df["Source"].value_counts())

    print("\nRecords by Topics")

    print(df["Topics"].value_counts())

    print("\nRecords by Year")

    print(df["Year"].value_counts().sort_index())

    print("\nAverage Relevance Score")

    print(df["Relevance_Score"].mean())

    print("\nSaved To:")

    print(OUTPUT_FILE)

    print("\nSample Records:\n")

    print(df.head(10))

    return df


# =========================================================
# Main Function
# =========================================================

def main():

    print("=" * 60)
    print("Knowledge Base Extraction Started")
    print("=" * 60)

    results = process_all_sources()

    export_to_excel(results)

    print("\nExtraction Finished Successfully.")


# =========================================================
# Entry Point
# =========================================================

if __name__ == "__main__":

    main()