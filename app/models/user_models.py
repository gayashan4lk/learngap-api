from pydantic import BaseModel

class UserVM(BaseModel):
    name: str
    description: str = None
    age: int