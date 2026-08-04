"""
=========================================================
Hypergraph Builder
Author : Rose Maria
Purpose:
Create Hypergraph for Hyper-RAG
=========================================================
"""

import pandas as pd
import pickle
from collections import defaultdict

print("=" * 60)
print("Building Hypergraph")
print("=" * 60)

# =====================================================
# Configuration
# =====================================================

INPUT_FILE = r"D:\Elnino\dataset\Knowledge_Base_Chunks.xlsx"

OUTPUT_FILE = r"D:\Elnino\dataset\hypergraph.pkl"

# =====================================================
# Load Chunks
# =====================================================

df = pd.read_excel(INPUT_FILE)

print("Chunks Loaded :", len(df))

# =====================================================
# Hypergraph Structure
# =====================================================

hypergraph = defaultdict(set)

# =====================================================
# Build Hyperedges
# =====================================================

for _, row in df.iterrows():

    chunk = row["Chunk_ID"]

    # ---------------------------
    # Source
    # ---------------------------

    source = str(row["Source"]).strip()

    hypergraph[f"Source::{source}"].add(chunk)

    # ---------------------------
    # Year
    # ---------------------------

    year = str(row["Year"]).strip()

    hypergraph[f"Year::{year}"].add(chunk)

    # ---------------------------
    # Topic
    # ---------------------------

    topics = str(row["Topic"]).split(",")

    for topic in topics:

        topic = topic.strip()

        if topic:

            hypergraph[f"Topic::{topic}"].add(chunk)

    # ---------------------------
    # Keywords
    # ---------------------------

    keywords = str(row["Keywords"]).split(",")

    for keyword in keywords:

        keyword = keyword.strip().lower()

        if keyword:

            hypergraph[f"Keyword::{keyword}"].add(chunk)

# =====================================================
# Convert sets to lists
# =====================================================

hypergraph = {

    edge: sorted(list(nodes))

    for edge, nodes in hypergraph.items()

}

# =====================================================
# Save
# =====================================================

with open(OUTPUT_FILE, "wb") as f:

    pickle.dump(hypergraph, f)

# =====================================================
# Statistics
# =====================================================

print("\nHypergraph Created Successfully")

print("-" * 40)

print("Total Hyperedges :", len(hypergraph))

print()

print("Sample Hyperedges\n")

count = 0

for edge, nodes in hypergraph.items():

    print(edge)

    print("Chunks :", len(nodes))

    print(nodes[:8])

    print()

    count += 1

    if count == 10:

        break

print("Saved To:")

print(OUTPUT_FILE)