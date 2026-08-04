import pandas as pd
import numpy as np
import faiss
import pickle
import re

print("=" * 60)
print("Creating FAISS Vector Database")
print("=" * 60)

# -----------------------------
# Load embeddings
# -----------------------------

INPUT_FILE = r"D:\Elnino\dataset\Knowledge_Base_Embeddings.xlsx"

df = pd.read_excel(INPUT_FILE)

print("Embeddings Loaded :", len(df))

# -----------------------------
# Convert embedding strings
# -----------------------------
# The "Embedding" column can come out looking like:
#   "-0.0573,0.123,0.881,..."          (plain CSV)
#   "[-0.0573, 0.123, 0.881, ...]"     (numpy/list repr, brackets + spaces)
#   "[-0.0573\n 0.123\n 0.881 ...]"    (numpy repr, newline-wrapped, no commas)
#
# Splitting on "," alone breaks on the second and third forms, which is
# exactly what produced "could not convert string to float: '[-0.0573...'".
#
# A regex that just pulls out every float-looking token handles all three
# formats the same way, regardless of brackets, commas, or line wraps.
# -----------------------------

NUMBER_PATTERN = re.compile(r"-?\d+\.?\d*(?:[eE][-+]?\d+)?")

def parse_embedding(raw):

    if isinstance(raw, (list, tuple, np.ndarray)):

        return np.array(raw, dtype="float32")

    text = str(raw)

    tokens = NUMBER_PATTERN.findall(text)

    return np.array(tokens, dtype="float32")


embeddings = []

bad_rows = []

expected_dim = None

for row_idx, emb in enumerate(df["Embedding"]):

    vector = parse_embedding(emb)

    if expected_dim is None:

        expected_dim = len(vector)

    if len(vector) != expected_dim:

        bad_rows.append((row_idx, len(vector)))

        continue

    embeddings.append(vector)

if bad_rows:

    print(f"\nSkipped {len(bad_rows)} row(s) with the wrong embedding length "
          f"(expected {expected_dim}):")

    for row_idx, length in bad_rows[:10]:

        print(f"  Row {row_idx}: got {length} values")

    if len(bad_rows) > 10:

        print(f"  ... and {len(bad_rows) - 10} more")

embeddings = np.vstack(embeddings)

print("Embedding Shape :", embeddings.shape)

# -----------------------------
# Create FAISS Index
# -----------------------------

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

print("Vectors Indexed :", index.ntotal)

# -----------------------------
# Save Index
# -----------------------------

INDEX_FILE = r"D:\Elnino\dataset\knowledge_index.faiss"

faiss.write_index(index, INDEX_FILE)

# -----------------------------
# Save metadata
# -----------------------------
# If any rows were skipped above, drop them from the metadata too so
# row N in the FAISS index still lines up with row N in the metadata.
# -----------------------------

if bad_rows:

    skip_idx = {row_idx for row_idx, _ in bad_rows}

    df = df.drop(index=list(skip_idx)).reset_index(drop=True)

META_FILE = r"D:\Elnino\dataset\knowledge_metadata.pkl"

metadata = df.to_dict("records")

with open(META_FILE, "wb") as f:
    pickle.dump(metadata, f)

print("\nFAISS Index Saved")

print(INDEX_FILE)

print(META_FILE)