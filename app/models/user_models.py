from typing import Optional
from pydantic import BaseModel

class UserVM(BaseModel):
    name: str
    description: str = None
    age: int


class UserPersonaRequest(BaseModel):
    user_name: str
    email: Optional[str] = None
    educational_background: Optional[str] = None
    professional_background: Optional[str] = None
    skills: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    medium: Optional[str] = None