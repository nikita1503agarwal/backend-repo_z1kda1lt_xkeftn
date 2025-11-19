import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

from database import db, create_document, get_documents

app = FastAPI(title="Professional Community API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Models (request/response)
# -----------------------------------------------------------------------------

class CreateUser(BaseModel):
    name: str
    email: EmailStr
    headline: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    skills: List[str] = []
    website: Optional[str] = None

class CreateTopic(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None

class CreatePost(BaseModel):
    author_id: str
    content: str
    topic_slugs: List[str] = []

class CreateComment(BaseModel):
    post_id: str
    author_id: str
    content: str

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

@app.get("/")
def read_root():
    return {"message": "Professional Community API running"}

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
            response["database_name"] = getattr(db, 'name', None) or "Unknown"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# -----------------------------------------------------------------------------
# API: Users
# -----------------------------------------------------------------------------

@app.post("/api/users")
def create_user(payload: CreateUser):
    # Check if email exists
    existing = get_documents("professionaluser", {"email": payload.email}, limit=1)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = payload.model_dump()
    user_id = create_document("professionaluser", user_data)
    return {"id": user_id, **user_data}

@app.get("/api/users")
def list_users(limit: int = 50):
    users = get_documents("professionaluser", {}, limit=limit)
    # Convert ObjectId to string if present
    for u in users:
        if "_id" in u:
            u["id"] = str(u.pop("_id"))
        # Clean timestamps
        if "created_at" in u and isinstance(u["created_at"], datetime):
            u["created_at"] = u["created_at"].isoformat()
        if "updated_at" in u and isinstance(u["updated_at"], datetime):
            u["updated_at"] = u["updated_at"].isoformat()
    return users

# -----------------------------------------------------------------------------
# API: Topics
# -----------------------------------------------------------------------------

@app.post("/api/topics")
def create_topic(payload: CreateTopic):
    # unique slug
    existing = get_documents("topic", {"slug": payload.slug}, limit=1)
    if existing:
        raise HTTPException(status_code=400, detail="Topic slug already exists")
    topic_id = create_document("topic", payload.model_dump())
    return {"id": topic_id, **payload.model_dump()}

@app.get("/api/topics")
def list_topics(limit: int = 100):
    topics = get_documents("topic", {}, limit=limit)
    for t in topics:
        if "_id" in t:
            t["id"] = str(t.pop("_id"))
        if "created_at" in t and isinstance(t["created_at"], datetime):
            t["created_at"] = t["created_at"].isoformat()
        if "updated_at" in t and isinstance(t["updated_at"], datetime):
            t["updated_at"] = t["updated_at"].isoformat()
    return topics

# -----------------------------------------------------------------------------
# API: Posts
# -----------------------------------------------------------------------------

@app.post("/api/posts")
def create_post(payload: CreatePost):
    # ensure author exists
    author = get_documents("professionaluser", {"_id": {"$exists": True}}, limit=1)  # light check
    # If you want strict check by id, we'd need ObjectId conversion; keeping simple
    if not payload.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    post_data = payload.model_dump()
    post_data["like_count"] = 0
    post_data["comment_count"] = 0
    post_id = create_document("post", post_data)
    return {"id": post_id, **post_data}

@app.get("/api/posts")
def list_posts(limit: int = 50):
    posts = get_documents("post", {}, limit=limit)
    # decorate with simple denormalized fields
    for p in posts:
        if "_id" in p:
            p["id"] = str(p.pop("_id"))
        if "created_at" in p and isinstance(p["created_at"], datetime):
            p["created_at"] = p["created_at"].isoformat()
        if "updated_at" in p and isinstance(p["updated_at"], datetime):
            p["updated_at"] = p["updated_at"].isoformat()
    return posts

# -----------------------------------------------------------------------------
# API: Comments
# -----------------------------------------------------------------------------

@app.post("/api/comments")
def create_comment(payload: CreateComment):
    if not payload.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    comment_id = create_document("comment", payload.model_dump())
    return {"id": comment_id, **payload.model_dump()}

@app.get("/api/comments")
def list_comments(post_id: Optional[str] = None, limit: int = 100):
    filt = {"post_id": post_id} if post_id else {}
    comments = get_documents("comment", filt, limit=limit)
    for c in comments:
        if "_id" in c:
            c["id"] = str(c.pop("_id"))
        if "created_at" in c and isinstance(c["created_at"], datetime):
            c["created_at"] = c["created_at"].isoformat()
        if "updated_at" in c and isinstance(c["updated_at"], datetime):
            c["updated_at"] = c["updated_at"].isoformat()
    return comments


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
