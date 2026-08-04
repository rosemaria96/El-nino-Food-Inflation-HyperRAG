"""
=========================================================
Embedding Generator
Author : Rose Maria
Purpose:
Generate embeddings for every chunk using
all-MiniLM-L6-v2
=========================================================
"""

import pandas as pd
from sentence_transformers import SentenceTransformer

# ---------------------------------------
# Files
# ---------------------------------------

INPUT_FILE = r"D:\Elnino\dataset\Knowledge_Base_Chunks.xlsx"

OUTPUT_FILE = r"D:\Elnino\dataset\Knowledge_Base_Embeddings.xlsx"

# ---------------------------------------
# Load Model
# ---------------------------------------

print("="*60)
print("Loading Embedding Model")
print("="*60)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ---------------------------------------
# Read Chunks
# ---------------------------------------

df = pd.read_excel(INPUT_FILE)

print("Chunks :", len(df))

# ---------------------------------------
# Generate Embeddings
# ---------------------------------------

embeddings = []

for i, text in enumerate(df["Chunk_Text"]):

    vector = model.encode(
        str(text),
        normalize_embeddings=True
    )

    embeddings.append(vector.tolist())

    if (i + 1) % 25 == 0:
        print(f"{i+1} chunks completed")

# ---------------------------------------
# Save
# ---------------------------------------

df["Embedding"] = embeddings

df.to_excel(
    OUTPUT_FILE,
    index=False
)

print("\nEmbedding Generation Completed")

print("Vectors :", len(df))

print("Dimension :", len(embeddings[0]))

print("\nSaved to:")

print(OUTPUT_FILE)