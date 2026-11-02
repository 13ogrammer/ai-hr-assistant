from fastapi import APIRouter, HTTPException

from generation.generate import generate_answer
from models.qa import AskRequest, AskResponse, UserResponse
from shared.users import FAKE_USERS, get_user

router = APIRouter()


@router.get("/users", response_model=list[UserResponse])
def list_users() -> list[UserResponse]:
    return [UserResponse(id=u.id, name=u.name, title=u.title, role=u.role) for u in FAKE_USERS]


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    user = get_user(request.user_id)
    if user is None:
        raise HTTPException(status_code=400, detail="Unknown user_id")

    answer, sources = generate_answer(request.question, user)
    return AskResponse(answer=answer, sources=sources)
