from fastapi import APIRouter

from generation.generate import generate_answer
from models.qa import AskRequest, AskResponse
from retrieval.retrieve import retrieve

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "healthy"}


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    chunks = retrieve(request.question)
    answer = generate_answer(request.question, chunks)
    sources = sorted({chunk.source for chunk in chunks})
    return AskResponse(answer=answer, sources=sources)
