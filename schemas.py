from pydantic import BaseModel

class CharacterBase(BaseModel):
    name: str
    image: str
    health: int = 100
    armor: int = 0
    mana: int = 0
    kills: int = 0

class CharacterCreate(CharacterBase):
    pass

class CharacterUpdate(BaseModel):
    name: str | None = None
    image: str | None = None
    health: int | None = None
    armor: int | None = None
    mana: int | None = None
    kills: int | None = None

class CharacterOut(CharacterBase):
    id: int

    class Config:
        orm_mode = True 