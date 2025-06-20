from fastapi import FastAPI, Depends, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas
import crud
import database
import random
from fastapi.responses import JSONResponse
import threading
import time

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

def move_enemies_background():
    while True:
        db = database.SessionLocal()
        try:
            # Get all character positions
            positions = db.query(models.Position).all()
            if not positions or len(positions) < 2:
                db.close()
                time.sleep(3)
                continue
            # Pick 3 random enemies (not the player)
            char_ids = [p.character_id for p in positions]
            # For demo, just pick 3 random (if more than 3)
            random.shuffle(char_ids)
            enemies = char_ids[:3]
            # Get all taken positions
            taken = set((p.x, p.y) for p in positions)
            for enemy_id in enemies:
                pos = db.query(models.Position).filter(models.Position.character_id == enemy_id).first()
                if not pos:
                    continue
                # Try to move to a random adjacent tile (up, down, left, right only)
                moves = [(-1,0),(1,0),(0,-1),(0,1)]
                random.shuffle(moves)
                moved = False
                for dx, dy in moves:
                    nx, ny = pos.x + dx, pos.y + dy
                    if 0 <= nx < 10 and 0 <= ny < 10 and (nx, ny) not in taken:
                        taken.remove((pos.x, pos.y))
                        pos.x, pos.y = nx, ny
                        db.commit()
                        taken.add((nx, ny))
                        moved = True
                        break
                # If all moves are blocked, stay in place
                if not moved:
                    db.commit()
        finally:
            db.close()
        time.sleep(3)

@app.on_event("startup")
def on_startup():
    database.init_db()
    threading.Thread(target=move_enemies_background, daemon=True).start()

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

@app.post("/spawn/{character_id}", response_model=schemas.PositionOut)
def spawn_character(character_id: int, db: Session = Depends(get_db)):
    # Check if character exists
    character = crud.get_character(db, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    # Get random free position
    x, y = crud.get_random_free_position(db, grid_size=10)
    # Create or update position
    position_in = schemas.PositionCreate(character_id=character_id, x=x, y=y)
    position = crud.create_or_update_position(db, position_in)
    return position

@app.post("/move/{character_id}", response_model=schemas.PositionOut)
def move_character(character_id: int, direction: str = Body(..., embed=True), db: Session = Depends(get_db)):
    # Get current position
    pos = crud.get_position_by_character_id(db, character_id)
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found")
    x, y = pos.x, pos.y
    if direction == "up":
        y = max(0, y - 1)
    elif direction == "down":
        y = min(9, y + 1)
    elif direction == "left":
        x = max(0, x - 1)
    elif direction == "right":
        x = min(9, x + 1)
    else:
        raise HTTPException(status_code=400, detail="Invalid direction")
    # Update position
    position_in = schemas.PositionCreate(character_id=character_id, x=x, y=y)
    position = crud.create_or_update_position(db, position_in)
    return position

@app.get("/enemies/", response_model=list[schemas.EnemyOut])
def get_enemies(db: Session = Depends(get_db)):
    return crud.get_enemies(db)

@app.get("/positions/")
def get_all_positions(db: Session = Depends(get_db)):
    positions = db.query(models.Position).all()
    result = []
    for pos in positions:
        char = db.query(models.Character).filter(models.Character.id == pos.character_id).first()
        if char:
            result.append({
                "id": char.id,
                "name": char.name,
                "image": char.image,
                "x": pos.x,
                "y": pos.y
            })
    return JSONResponse(content=result)

@app.post("/attack/")
def attack(request: Request, db: Session = Depends(get_db)):
    data = request.json() if hasattr(request, 'json') else None
    import asyncio
    if asyncio.iscoroutine(data):
        import asyncio
        data = asyncio.run(data)
    attacker_id = data.get('attacker_id')
    target_id = data.get('target_id')
    session_hp = data.get('session_hp')  # frontend sends current session HP
    # Get positions
    attacker_pos = crud.get_position_by_character_id(db, attacker_id)
    target_pos = crud.get_position_by_character_id(db, target_id)
    if not attacker_pos or not target_pos:
        return JSONResponse(content={"error": "Attacker or target not found"}, status_code=404)
    # Check range (1-tile, including diagonals)
    dx = abs(attacker_pos.x - target_pos.x)
    dy = abs(attacker_pos.y - target_pos.y)
    if max(dx, dy) > 1:
        return JSONResponse(content={"error": "Target not in range"}, status_code=400)
    # Get characters
    attacker = crud.get_character(db, attacker_id)
    target = crud.get_character(db, target_id)
    if not attacker or not target:
        return JSONResponse(content={"error": "Attacker or target not found"}, status_code=404)
    # Damage formula
    damage = int(attacker.mana * 0.35)
    killed = False
    new_session_hp = session_hp - damage if session_hp is not None else None
    if new_session_hp is not None and new_session_hp <= 0:
        attacker.kills += 1
        killed = True
        db.commit()
    return JSONResponse(content={
        "attacker_id": attacker_id,
        "target_id": target_id,
        "damage": damage,
        "target_health": max(0, new_session_hp) if new_session_hp is not None else None,
        "killed": killed
    })

# Character routes will be added here 