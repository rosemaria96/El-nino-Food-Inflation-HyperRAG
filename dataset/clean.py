"""
=========================================================
Knowledge Base Cleaner
Purpose:
Automatically catch what the manual 30-60 min pass looks
for in Knowledge_Base_Clean.xlsx:

  - duplicate paragraphs (exact + near-duplicate)
  - reference / publication list paragraphs
  - author list paragraphs
  - conference / workshop / seminar name paragraphs
  - non-explanatory paragraphs (no cause/effect language)

Removed rows are NOT thrown away silently - they're saved
to a separate "review" file so you can spot-check the
automated decisions instead of trusting them blindly.
=========================================================
"""

import re
import pandas as pd

# =========================================================
# Configuration
# =========================================================

INPUT_FILE = r"D:\Elnino\dataset\Knowledge_Base_Clean.xlsx"

OUTPUT_FILE = r"D:\Elnino\dataset\Knowledge_Base_Final.xlsx"
REMOVED_FILE = r"D:\Elnino\dataset\Knowledge_Base_Removed_Review.xlsx"

TEXT_COLUMN = "Extracted_Text"

# =========================================================
# Reference / Publication Patterns
# =========================================================

REFERENCE_PATTERNS = [

    r"\bet al\.",

    r"\bpp\.\s?\d",

    r"\bvol\.\s?\d",

    r"\bissn\b",

    r"\bisbn\b",

    r"\bdoi\s?:",

    r"https?://",

    r"www\.",

    r"\bretrieved from\b",

    r"\breferences?\s*:",

    r"\bbibliography\b",

    r"\bjournal of\b",

    r"\bproceedings of\b",

    r"\d{4}\)\.\s*[A-Z]",          # "... (2015). Title..."

    r"\b(19|20)\d{2}[a-z]?\)\s"    # in-text citation like "(2015)"

]

# =========================================================
# Author List Patterns
# =========================================================
# Author lists tend to be strings of capitalized name-like
# tokens separated by commas / "and", often with initials
# ("A. Kumar, B. Sharma and C. Rao"), and very few lowercase
# connecting words relative to their length.
# =========================================================

AUTHOR_TITLE_WORDS = [

    "dr.",

    "prof.",

    "shri",

    "smt."

]

def looks_like_author_list(paragraph):

    lower = paragraph.lower()

    if any(word in lower for word in AUTHOR_TITLE_WORDS):

        return True

    # Pattern: two or more "Initial. Surname" tokens

    initials = re.findall(r"\b[A-Z]\.\s?[A-Z][a-z]+", paragraph)

    if len(initials) >= 2:

        return True

    # Pattern: long run of comma-separated capitalized words

    # e.g. "Rao, K., Sharma, P., Gupta, R., and Singh, M."

    comma_caps = re.findall(r"\b[A-Z][a-z]+,\s?[A-Z]\.", paragraph)

    if len(comma_caps) >= 2:

        return True

    return False

# =========================================================
# Conference / Workshop Patterns
# =========================================================

CONFERENCE_WORDS = [

    "conference",

    "workshop",

    "seminar",

    "symposium",

    "proceedings",

    "annual meeting",

    "training programme"

]

# =========================================================
# Explanatory (cause/effect) Words
# =========================================================
# Kept in sync with the extractor's REASON_WORDS so the
# cleaner and extractor agree on what "explanatory" means.
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
# Normalize Text (for near-duplicate detection)
# =========================================================

def normalize(paragraph):

    text = paragraph.lower()

    text = re.sub(r"[^a-z0-9\s]", "", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text

# =========================================================
# Row-Level Checks
# =========================================================

def is_reference_paragraph(paragraph):

    lower = paragraph.lower()

    return any(re.search(pattern, lower) for pattern in REFERENCE_PATTERNS)


def is_conference_paragraph(paragraph):

    lower = paragraph.lower()

    return any(word in lower for word in CONFERENCE_WORDS)


def is_non_explanatory(paragraph):

    lower = paragraph.lower()

    return not any(word in lower for word in REASON_WORDS)

# =========================================================
# Main Cleaning Function
# =========================================================

def clean_knowledge_base(input_file, output_file, removed_file):

    df = pd.read_excel(input_file)

    if TEXT_COLUMN not in df.columns:

        raise ValueError(f"Column '{TEXT_COLUMN}' not found in {input_file}")

    df["Remove_Reason"] = ""

    # -----------------------------------------
    # 1. Exact duplicate paragraphs
    # -----------------------------------------

    exact_dupe_mask = df.duplicated(subset=[TEXT_COLUMN], keep="first")

    df.loc[exact_dupe_mask, "Remove_Reason"] += "Exact duplicate; "

    # -----------------------------------------
    # 2. Near-duplicate paragraphs
    # (same text after stripping punctuation/case/whitespace)
    # -----------------------------------------

    df["_normalized"] = df[TEXT_COLUMN].astype(str).apply(normalize)

    near_dupe_mask = df.duplicated(subset=["_normalized"], keep="first") & ~exact_dupe_mask

    df.loc[near_dupe_mask, "Remove_Reason"] += "Near duplicate; "

    # -----------------------------------------
    # 3. Reference / publication list paragraphs
    # -----------------------------------------

    reference_mask = df[TEXT_COLUMN].astype(str).apply(is_reference_paragraph)

    df.loc[reference_mask, "Remove_Reason"] += "Reference/publication list; "

    # -----------------------------------------
    # 4. Author list paragraphs
    # -----------------------------------------

    author_mask = df[TEXT_COLUMN].astype(str).apply(looks_like_author_list)

    df.loc[author_mask, "Remove_Reason"] += "Author list; "

    # -----------------------------------------
    # 5. Conference / workshop / seminar paragraphs
    # -----------------------------------------

    conference_mask = df[TEXT_COLUMN].astype(str).apply(is_conference_paragraph)

    df.loc[conference_mask, "Remove_Reason"] += "Conference/workshop name; "

    # -----------------------------------------
    # 6. Non-explanatory paragraphs
    # -----------------------------------------

    non_explanatory_mask = df[TEXT_COLUMN].astype(str).apply(is_non_explanatory)

    df.loc[non_explanatory_mask, "Remove_Reason"] += "Not explanatory (no cause/effect language); "

    # -----------------------------------------
    # Split kept vs removed
    # -----------------------------------------

    remove_mask = (

        exact_dupe_mask

        | near_dupe_mask

        | reference_mask

        | author_mask

        | conference_mask

        | non_explanatory_mask

    )

    df_removed = df[remove_mask].drop(columns=["_normalized"])

    df_kept = df[~remove_mask].drop(columns=["_normalized", "Remove_Reason"])

    df_kept.reset_index(drop=True, inplace=True)

    df_removed.reset_index(drop=True, inplace=True)

    # -----------------------------------------
    # Save both files
    # -----------------------------------------

    df_kept.to_excel(output_file, index=False)

    df_removed.to_excel(removed_file, index=False)

    # -----------------------------------------
    # Summary
    # -----------------------------------------

    print("=" * 60)
    print("Knowledge Base Cleaning Complete")
    print("=" * 60)

    print(f"Original rows : {len(df)}")

    print(f"Kept rows     : {len(df_kept)}")

    print(f"Removed rows  : {len(df_removed)}")

    print("\nRemoval breakdown (rows can match more than one reason):")

    print(f"  Exact duplicates          : {exact_dupe_mask.sum()}")

    print(f"  Near duplicates           : {near_dupe_mask.sum()}")

    print(f"  Reference/publication     : {reference_mask.sum()}")

    print(f"  Author lists              : {author_mask.sum()}")

    print(f"  Conference/workshop names : {conference_mask.sum()}")

    print(f"  Non-explanatory           : {non_explanatory_mask.sum()}")

    print(f"\nCleaned file saved to : {output_file}")

    print(f"Review file saved to  : {removed_file}")

    print("\nSpot-check the review file - if the automated cutoffs")

    print("removed anything wrongly, adjust the keyword lists above")

    print("and rerun rather than hand-fixing the output.")

    return df_kept, df_removed


# =========================================================
# Entry Point
# =========================================================

if __name__ == "__main__":

    clean_knowledge_base(INPUT_FILE, OUTPUT_FILE, REMOVED_FILE)