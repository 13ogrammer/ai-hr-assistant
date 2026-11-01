from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    user_id: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str]


class UserResponse(BaseModel):
    id: str
    name: str
    title: str
    role: str
