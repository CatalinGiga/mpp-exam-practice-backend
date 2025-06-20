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

class PositionBase(BaseModel):
    character_id: int
    x: int
    y: int

class PositionCreate(PositionBase):
    pass

class PositionOut(PositionBase):
    id: int
    class Config:
        orm_mode = True

class EnemyBase(BaseModel):
    x: int
    y: int
    health: int = 100

class EnemyCreate(EnemyBase):
    pass

class EnemyOut(EnemyBase):
    id: int
    class Config:
        orm_mode = True 