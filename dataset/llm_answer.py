"""
=========================================================
LLM Answer
Purpose:
This file does NOT contain retrieval logic - that all
lives in retrieve.py. This file only:
  1. Calls retrieve.py for the relevant chunks
  2. Formats them into a prompt
  3. Sends the prompt to Gemini
  4. Prints the answer
=========================================================
"""

from google import genai

from retrieve import retrieve

client = genai.Client()  # reads the key automatically from the GEMINI_API_KEY env var

CHAT_MODEL = "gemini-3.5-flash"

# -----------------------------
# Build prompt from retrieved chunks only
# -----------------------------

def build_prompt(question, matches):

    context_blocks = []

    for match in matches:

        context_blocks.append(
            f"[{match['doc_id']}] {match['text']}"
        )

    context = "\n\n".join(context_blocks)

    prompt = f"""You are an expert on India's economy.

Context
{context}

Question
{question}

Answer only from the context above. If the context does not
contain the answer, say so explicitly instead of guessing.
Cite the [Document_ID] tags you relied on.
"""

    return prompt


# -----------------------------
# Main
# -----------------------------

def main():

    question = input("Question : ")

    matches = retrieve(question)

    if not matches:

        print("No relevant context found in the index.")

        return

    print(f"\nRetrieved {len(matches)} chunk(s):")

    for match in matches:

        if match["distance"] is not None:

            print(f"  [{match['chunk_id']}] {match['doc_id']}  distance={match['distance']:.4f}")

        else:

            print(f"  [{match['chunk_id']}] {match['doc_id']}  (via {match['via']})")

    prompt = build_prompt(question, matches)

    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt
    )

    print("\nAnswer:\n")

    print(response.text)


if __name__ == "__main__":

    main()