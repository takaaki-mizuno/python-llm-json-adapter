from pydantic import BaseModel


class Response(BaseModel):
    name: str
    description: str
    parameters: dict
