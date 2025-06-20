from sqlalchemy.orm import Session
import models
import schemas

# Create

def create_character(db: Session, character: schemas.CharacterCreate):
    db_character = models.Character(**character.dict())
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

# Read all

def get_characters(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Character).offset(skip).limit(limit).all()

# Read one

def get_character(db: Session, character_id: int):
    return db.query(models.Character).filter(models.Character.id == character_id).first()

# Update

def update_character(db: Session, character_id: int, character: schemas.CharacterUpdate):
    db_character = get_character(db, character_id)
    if not db_character:
        return None
    for field, value in character.dict(exclude_unset=True).items():
        setattr(db_character, field, value)
    db.commit()
    db.refresh(db_character)
    return db_character

# Delete

def delete_character(db: Session, character_id: int):
    db_character = get_character(db, character_id)
    if not db_character:
        return None
    db.delete(db_character)
    db.commit()
    return db_character 