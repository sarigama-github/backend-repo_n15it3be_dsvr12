import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from bson import ObjectId

from database import db
from schemas import Event, Place

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Helpers ----------

def to_str_id(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not doc:
        return doc
    doc = dict(doc)
    _id = doc.get("_id")
    if isinstance(_id, ObjectId):
        doc["id"] = str(_id)
        del doc["_id"]
    return doc

# ---------- Health ----------
@app.get("/")
def read_root():
    return {"message": "Wedding backend running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# ---------- Event Endpoints ----------

DEFAULT_EVENT = Event(
    couple_names="Brigitte & Salvatore",
    date="2026-05-10",
    city="Montoro (AV)",
    church_name="Chiesa di San Giovanni Battista",
    church_address="Piazza Michele Pironti, Montoro (AV)",
    venue_name="Tenuta Leone - Villa per Eventi",
    venue_address="Via Roma, 19, 84080 Calvanico (SA)",
    notes="Benvenuti! Qui trovate tutte le informazioni utili per vivere al meglio il nostro grande giorno."
)

@app.get("/api/event")
def get_event():
    coll = db["event"]
    doc = coll.find_one({})
    if not doc:
        # seed default
        data = DEFAULT_EVENT.model_dump()
        coll.replace_one({}, data, upsert=True)
        doc = coll.find_one({})
    return to_str_id(doc)

class EventUpdate(Event):
    pass

@app.put("/api/event")
def update_event(payload: EventUpdate):
    coll = db["event"]
    res = coll.replace_one({}, payload.model_dump(), upsert=True)
    doc = coll.find_one({})
    return to_str_id(doc)

# ---------- Places Endpoints ----------

@app.get("/api/places")
def list_places(category: Optional[str] = Query(None, description="Filter by category")):
    coll = db["place"]
    query: Dict[str, Any] = {}
    if category:
        query["category"] = category
    items = [to_str_id(d) for d in coll.find(query).sort("name", 1)]
    return items

class PlaceCreate(Place):
    pass

@app.post("/api/places", status_code=201)
def create_place(payload: PlaceCreate):
    coll = db["place"]
    result = coll.insert_one(payload.model_dump())
    doc = coll.find_one({"_id": result.inserted_id})
    return to_str_id(doc)

class PlaceUpdate(BaseModel):
    category: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    maps_url: Optional[str] = None
    tags: Optional[list] = None

@app.put("/api/places/{place_id}")
def update_place(place_id: str, payload: PlaceUpdate):
    coll = db["place"]
    try:
        _id = ObjectId(place_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    res = coll.update_one({"_id": _id}, {"$set": update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Place not found")
    doc = coll.find_one({"_id": _id})
    return to_str_id(doc)

@app.delete("/api/places/{place_id}", status_code=204)
def delete_place(place_id: str):
    coll = db["place"]
    try:
        _id = ObjectId(place_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")
    res = coll.delete_one({"_id": _id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Place not found")
    return

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
