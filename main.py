from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas
import crud
import database
import random

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:5173"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    database.init_db()

@app.get("/")
def read_root():
    return {"message": "Mini-MMORPG Backend is running!"}

# --- Character CRUD API ---

@app.post("/characters/", response_model=schemas.CharacterOut)
def create_character(character: schemas.CharacterCreate, db: Session = Depends(get_db)):
    return crud.create_character(db, character)

@app.get("/characters/", response_model=list[schemas.CharacterOut])
def read_characters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_characters(db, skip=skip, limit=limit)

@app.get("/characters/stats")
def character_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(models.Character.id)).scalar() or 0
    avg_health = db.query(func.avg(models.Character.health)).scalar() or 0
    avg_armor = db.query(func.avg(models.Character.armor)).scalar() or 0
    avg_mana = db.query(func.avg(models.Character.mana)).scalar() or 0
    avg_kills = db.query(func.avg(models.Character.kills)).scalar() or 0
    if total == 0:
        return {
            "total": total,
            "avg_health": 0,
            "avg_armor": 0,
            "avg_mana": 0,
            "avg_kills": 0
        }
    return {
        "total": total,
        "avg_health": round(avg_health, 1) if avg_health else 0,
        "avg_armor": round(avg_armor, 1) if avg_armor else 0,
        "avg_mana": round(avg_mana, 1) if avg_mana else 0,
        "avg_kills": round(avg_kills, 1) if avg_kills else 0
    }

@app.get("/characters/{character_id}", response_model=schemas.CharacterOut)
def read_character(character_id: int, db: Session = Depends(get_db)):
    db_character = crud.get_character(db, character_id)
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return db_character

@app.put("/characters/{character_id}", response_model=schemas.CharacterOut)
def update_character(character_id: int, character: schemas.CharacterUpdate, db: Session = Depends(get_db)):
    db_character = crud.update_character(db, character_id, character)
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return db_character

@app.delete("/characters/{character_id}", response_model=schemas.CharacterOut)
def delete_character(character_id: int, db: Session = Depends(get_db)):
    db_character = crud.delete_character(db, character_id)
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return db_character

random_names = ['Valeera', 'Uther', 'Illidan', 'Sylvanas', 'Malfurion', 'Anduin', 'Guldan', 'Rexxar']
def random_image(name):
    return f"https://robohash.org/{name.lower()}?set=set2"

def random_int(min_v, max_v):
    return random.randint(min_v, max_v)

@app.post("/characters/random", response_model=schemas.CharacterOut)
def create_random_character(db: Session = Depends(get_db)):
    name = random.choice(random_names) + str(random_int(1, 99))
    image = random_image(name)
    health = random_int(60, 150)
    armor = random_int(0, 50)
    mana = random_int(0, 150)
    kills = random_int(0, 20)
    character = schemas.CharacterCreate(
        name=name,
        image=image,
        health=health,
        armor=armor,
        mana=mana,
        kills=kills
    )
    return crud.create_character(db, character)

# Character routes will be added here 