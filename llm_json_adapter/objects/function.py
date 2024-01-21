from pydantic import BaseModel


class Function(BaseModel):
    name: str
    description: str
    parameters: dict
