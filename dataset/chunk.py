"""
=========================================================
Knowledge Base Chunking
Author : Rose Maria
Purpose:
Convert cleaned knowledge base into semantic chunks
for Hyper-RAG.
=========================================================
"""

import re
import os
import pandas as pd

# -------------------------------------------------------
# Configuration
# -------------------------------------------------------

INPUT_FILE = r"D:\Elnino\dataset\Knowledge_Base_Final.xlsx"
OUTPUT_FILE = r"D:\Elnino\dataset\Knowledge_Base_Chunks.xlsx"

# Maximum chunk size (words)
MAX_WORDS = 120

# Minimum chunk size (words)
MIN_WORDS = 30


# -------------------------------------------------------
# Split paragraph into sentences
# -------------------------------------------------------

def split_sentences(text):

    sentences = re.split(r'(?<=[.!?])\s+', text)

    sentences = [s.strip() for s in sentences if s.strip()]

    return sentences


# -------------------------------------------------------
# Build semantic chunks
# -------------------------------------------------------

def create_chunks(text):

    sentences = split_sentences(text)

    chunks = []

    current = []

    current_words = 0

    for sentence in sentences:

        words = len(sentence.split())

        if current_words + words <= MAX_WORDS:

            current.append(sentence)

            current_words += words

        else:

            chunk = " ".join(current).strip()

            if len(chunk.split()) >= MIN_WORDS:

                chunks.append(chunk)

            current = [sentence]

            current_words = words

    if current:

        chunk = " ".join(current)

        if len(chunk.split()) >= MIN_WORDS:

            chunks.append(chunk)

    return chunks


# -------------------------------------------------------
# Main
# -------------------------------------------------------

def main():

    print("=" * 60)
    print("Chunking Knowledge Base")
    print("=" * 60)

    df = pd.read_excel(INPUT_FILE)

    output = []

    chunk_counter = 1

    for _, row in df.iterrows():

        chunks = create_chunks(str(row["Extracted_Text"]))

        for chunk in chunks:

            output.append({

                "Chunk_ID":
                f"C{chunk_counter:06d}",

                "Document_ID":
                f"{row['Source']}_{row['Year']}_P{row['Page']}",

                "Year":
                row["Year"],

                "Source":
                row["Source"],

                "Topic":
                row["Topics"],

                "Page":
                row["Page"],

                "Keywords":
                row["Keywords"],

                "Chunk_Text":
                chunk

            })

            chunk_counter += 1

    chunk_df = pd.DataFrame(output)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    chunk_df.to_excel(OUTPUT_FILE, index=False)

    print("\nChunking Complete")
    print("-------------------------")
    print("Original Paragraphs :", len(df))
    print("Total Chunks        :", len(chunk_df))
    print("\nSaved to:")
    print(OUTPUT_FILE)

    print("\nSample Chunks\n")

    print(chunk_df.head())


if __name__ == "__main__":

    main()