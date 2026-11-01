"""Turn a question plus retrieved chunks into an answer via OpenAI.

Run with: uv run python -m generation.generate "your question here"
"""

import sys

from dotenv import load_dotenv
from openai import OpenAI

from models.chunk import RetrievedChunk
from retrieval.retrieve import retrieve

load_dotenv()

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "You are an HR assistant for Pinnacle Solutions. Answer the employee's "
    "question using only the context below, drawn from the company's HR "
    "policy documents. If the context doesn't contain the answer, say you "
    "don't know - do not guess, and do not use outside knowledge."
)


def build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    context = "\n\n---\n\n".join(f"[Source: {chunk.source}]\n{chunk.content}" for chunk in chunks)
    return f"Context:\n{context}\n\nQuestion: {question}"


def generate_answer(question: str, chunks: list[RetrievedChunk]) -> str:
    client = OpenAI()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(question, chunks)},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage: uv run python -m generation.generate "your question here"')
    question = " ".join(sys.argv[1:])
    chunks = retrieve(question)
    print(generate_answer(question, chunks))
