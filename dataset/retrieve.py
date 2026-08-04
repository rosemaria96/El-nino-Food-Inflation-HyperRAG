"""
=========================================================
Hybrid Retrieval
Purpose:
All retrieval logic for Hyper-RAG lives here:
  1. Embed the question (local MiniLM - must match the
     model used to build the FAISS index)
  2. Vector search via FAISS
  3. Hypergraph expansion from the vector-search seeds
     (pull in chunks sharing a Topic/Keyword with what
     was already found)
  4. NEW - keyword/topic-based retrieval: match the
     question's own words directly against hyperedge
     names, so a chunk gets pulled in because it's
     tagged with the right subject even if the vector
     search ranked it low (e.g. a question naming
     "El Nino" pulls in Keyword::el niño chunks even
     when they're phrased very differently from RBI's
     inflation-report language).

llm_answer.py imports retrieve() from this file - it
should not need to know how retrieval works internally.
=========================================================
"""

import faiss
import pickle
import numpy as np

from sentence_transformers import SentenceTransformer

# -------------------------------------------------
# Config
# -------------------------------------------------

INDEX_FILE = r"D:\Elnino\dataset\knowledge_index.faiss"
META_FILE = r"D:\Elnino\dataset\knowledge_metadata.pkl"
HYPERGRAPH_FILE = r"D:\Elnino\dataset\hypergraph.pkl"

EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

TOP_K = 5

# How many sibling chunks to pull per seed edge during
# hypergraph expansion (step 3).
SEED_EXPAND_PER_EDGE = 3

# How many extra chunks the keyword/topic pass (step 4)
# is allowed to add on top of everything else.
MAX_KEYWORD_EXTRA = 5

# Hard ceiling on total chunks returned, across all three
# retrieval mechanisms combined - keeps the LLM prompt from
# growing unbounded on a question that matches many edges.
MAX_TOTAL_CHUNKS = 15

# Skip hyperedge names shorter than this when doing the
# keyword/topic text match - avoids noisy short-word hits.
MIN_EDGE_VALUE_LENGTH = 4

# -------------------------------------------------
# Load model, FAISS index, metadata, hypergraph
# (once, at import time - both retrieve.py run directly
# and llm_answer.py importing it share this load)
# -------------------------------------------------

print("=" * 60)
print("Loading Retrieval Components")
print("=" * 60)

model = SentenceTransformer(EMBED_MODEL_NAME)

index = faiss.read_index(INDEX_FILE)

with open(META_FILE, "rb") as f:
    metadata = pickle.load(f)

with open(HYPERGRAPH_FILE, "rb") as f:
    hypergraph = pickle.load(f)

# Chunk_ID -> full record, for O(1) lookup (the original
# script re-scanned all of metadata per chunk, which is
# O(n*m) - this trades a bit of memory for speed).
chunk_lookup = {record["Chunk_ID"]: record for record in metadata}

# Chunk_ID -> list of edge names it belongs to, so seed
# expansion doesn't have to scan every hyperedge per chunk.
chunk_to_edges = {}

for edge, nodes in hypergraph.items():

    for chunk_id in nodes:

        chunk_to_edges.setdefault(chunk_id, []).append(edge)

print("Vectors in index  :", index.ntotal)
print("Metadata records  :", len(metadata))
print("Hyperedges loaded :", len(hypergraph))


# -------------------------------------------------
# Step 1 - Embed the question
# -------------------------------------------------

def embed_question(question):

    vector = model.encode(
        [question],
        normalize_embeddings=True
    )

    return np.array(vector, dtype="float32")


# -------------------------------------------------
# Step 2 - Vector search
# -------------------------------------------------

def vector_search(question, top_k=TOP_K):

    query_vector = embed_question(question)

    distances, indices = index.search(query_vector, top_k)

    matches = []

    for rank, idx in enumerate(indices[0]):

        if idx == -1:

            continue

        record = metadata[idx]

        matches.append({
            "chunk_id": record.get("Chunk_ID", "Unknown"),
            "doc_id": record.get("Document_ID", "Unknown"),
            "text": record.get("Chunk_Text", ""),
            "distance": float(distances[0][rank]),
            "via": "vector"
        })

    return matches


# -------------------------------------------------
# Step 3 - Hypergraph expansion from seed chunks
# -------------------------------------------------
# Only expands via Topic:: and Keyword:: edges - Source::
# and Year:: edges are excluded because they're too broad
# (e.g. Source::RBI has 185 chunks) and would just flood
# the context with same-source noise instead of genuinely
# related material.
# -------------------------------------------------

def expand_from_seeds(seed_chunk_ids, per_edge=SEED_EXPAND_PER_EDGE):

    extra_chunk_ids = []

    for chunk_id in seed_chunk_ids:

        for edge in chunk_to_edges.get(chunk_id, []):

            if not (edge.startswith("Topic::") or edge.startswith("Keyword::")):

                continue

            for sibling_id in hypergraph[edge][:per_edge]:

                if sibling_id not in extra_chunk_ids:

                    extra_chunk_ids.append(sibling_id)

    return extra_chunk_ids


# -------------------------------------------------
# Step 4 (NEW) - Keyword/topic-based retrieval
# -------------------------------------------------
# Matches the question's own words against every Topic::
# and Keyword:: hyperedge name directly - independent of
# what the vector search found. This is what catches an
# entity like "El Nino" that vector search under-ranks
# because the matching chunks are phrased very differently
# from the question (meteorological vs. economic language).
# -------------------------------------------------

def keyword_topic_matches(question, max_extra=MAX_KEYWORD_EXTRA):

    q_lower = question.lower()

    candidate_edges = []

    for edge, nodes in hypergraph.items():

        if not (edge.startswith("Topic::") or edge.startswith("Keyword::")):

            continue

        value = edge.split("::", 1)[1].lower()

        if len(value) < MIN_EDGE_VALUE_LENGTH:

            continue

        if value in q_lower:

            candidate_edges.append((edge, nodes))

    # Smaller (more specific) edges first - a narrow match
    # like "el niño" naming a handful of chunks is a stronger
    # signal than "inflation" naming 135 of them.

    candidate_edges.sort(key=lambda pair: len(pair[1]))

    extra_chunk_ids = []

    for edge, nodes in candidate_edges:

        for chunk_id in nodes:

            if chunk_id not in extra_chunk_ids:

                extra_chunk_ids.append(chunk_id)

            if len(extra_chunk_ids) >= max_extra:

                return extra_chunk_ids

    return extra_chunk_ids


# -------------------------------------------------
# Combined retrieval - this is what llm_answer.py calls
# -------------------------------------------------

def retrieve(question, top_k=TOP_K):

    matches = vector_search(question, top_k)

    seen_chunk_ids = {m["chunk_id"] for m in matches}

    # Step 3: expand from what vector search already found

    for chunk_id in expand_from_seeds(list(seen_chunk_ids)):

        if chunk_id in seen_chunk_ids or len(matches) >= MAX_TOTAL_CHUNKS:

            continue

        record = chunk_lookup.get(chunk_id)

        if record is None:

            continue

        matches.append({
            "chunk_id": chunk_id,
            "doc_id": record.get("Document_ID", "Unknown"),
            "text": record.get("Chunk_Text", ""),
            "distance": None,
            "via": "hypergraph_expand"
        })

        seen_chunk_ids.add(chunk_id)

    # Step 4: pull in chunks matching the question's own terms

    for chunk_id in keyword_topic_matches(question):

        if chunk_id in seen_chunk_ids or len(matches) >= MAX_TOTAL_CHUNKS:

            continue

        record = chunk_lookup.get(chunk_id)

        if record is None:

            continue

        matches.append({
            "chunk_id": chunk_id,
            "doc_id": record.get("Document_ID", "Unknown"),
            "text": record.get("Chunk_Text", ""),
            "distance": None,
            "via": "hypergraph_keyword"
        })

        seen_chunk_ids.add(chunk_id)

    return matches


# -------------------------------------------------
# Standalone CLI - lets you test retrieval alone,
# without spending an LLM call, same as before.
# -------------------------------------------------

def main():

    query = input("\nAsk Question : ")

    matches = retrieve(query)

    print(f"\nRetrieved {len(matches)} chunk(s):\n")

    for match in matches:

        print("-" * 60)

        if match["distance"] is not None:

            print(f"{match['chunk_id']}  ({match['doc_id']})  distance={match['distance']:.4f}")

        else:

            print(f"{match['chunk_id']}  ({match['doc_id']})  via={match['via']}")

        print(match["text"])


if __name__ == "__main__":

    main()