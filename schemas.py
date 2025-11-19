"""
Database Schemas for Professional Community App

Each Pydantic model represents a MongoDB collection. The collection name is the lowercase
of the class name.

These schemas are used by the built-in database tools for validation and by our API.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# -----------------------------------------------------------------------------
# Core app schemas
# -----------------------------------------------------------------------------

class Professionaluser(BaseModel):
    """
    Professionals (users) in the community
    Collection: "professionaluser"
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Unique email")
    headline: Optional[str] = Field(None, description="Short professional headline")
    bio: Optional[str] = Field(None, description="About section")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    location: Optional[str] = Field(None, description="City, Country")
    company: Optional[str] = Field(None, description="Current company")
    role: Optional[str] = Field(None, description="Current role/title")
    skills: List[str] = Field(default_factory=list, description="List of skills")
    website: Optional[str] = Field(None, description="Personal/portfolio website")
    is_active: bool = Field(default=True)

class Topic(BaseModel):
    """
    Discussion topics/tags users can post under
    Collection: "topic"
    """
    name: str = Field(..., description="Topic name, e.g., 'Product Management'")
    slug: str = Field(..., description="URL-friendly unique slug")
    description: Optional[str] = Field(None, description="Short description")

class Post(BaseModel):
    """
    Posts created by professionals
    Collection: "post"
    """
    author_id: str = Field(..., description="ID of Professionaluser")
    content: str = Field(..., description="Text content of the post")
    topic_slugs: List[str] = Field(default_factory=list, description="Associated topics by slug")
    like_count: int = Field(default=0)
    comment_count: int = Field(default=0)

class Comment(BaseModel):
    """
    Comments on posts
    Collection: "comment"
    """
    post_id: str = Field(..., description="ID of the post")
    author_id: str = Field(..., description="ID of Professionaluser")
    content: str = Field(..., description="Comment text")

# -----------------------------------------------------------------------------
# Example additional schemas kept for reference (not used directly by app UI)
# -----------------------------------------------------------------------------

class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
