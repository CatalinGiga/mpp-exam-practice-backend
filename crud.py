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

def get_position_by_character_id(db: Session, character_id: int):
    return db.query(models.Position).filter(models.Position.character_id == character_id).first()

def create_or_update_position(db: Session, position: schemas.PositionCreate):
    db_position = get_position_by_character_id(db, position.character_id)
    if db_position:
        db_position.x = position.x
        db_position.y = position.y
    else:
        db_position = models.Position(**position.dict())
        db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position

def get_random_free_position(db: Session, grid_size: int = 10):
    import random
    taken = set((p.x, p.y) for p in db.query(models.Position).all())
    while True:
        x = random.randint(0, grid_size - 1)
        y = random.randint(0, grid_size - 1)
        if (x, y) not in taken:
            return x, y

def get_enemies(db: Session):
    return db.query(models.Enemy).all()

def create_enemy(db: Session, enemy: schemas.EnemyCreate):
    db_enemy = models.Enemy(**enemy.dict())
    db.add(db_enemy)
    db.commit()
    db.refresh(db_enemy)
    return db_enemy

def get_enemy_by_id(db: Session, enemy_id: int):
    return db.query(models.Enemy).filter(models.Enemy.id == enemy_id).first() 