# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    id: Optional[int] = None
    username: str

class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime
    class Config:
        orm_mode = True

class CommentCreate(BaseModel):
    post_id: int
    parent_id: Optional[int] = None
    author_id: int
    author_name: str
    text: str

class CommentOut(BaseModel):
    id: int
    post_id: int
    parent_id: Optional[int]
    author_id: int
    author_name: str
    text: str
    created_at: datetime
    class Config:
        orm_mode = True

class PostCreate(BaseModel):
    title: str
    description: str
    categories: List[str]
    age_segment: Optional[int] = None
    community_id: Optional[int] = None
    author_id: Optional[int] = None
    author_name: Optional[str] = None

class PostUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    categories: Optional[List[str]]
    age_segment: Optional[int]
    community_id: Optional[int]

class PostOut(BaseModel):
    id: int
    title: str
    description: str
    categories: List[str]
    age_segment: Optional[int]
    community_id: Optional[int]
    created_at: datetime
    author_id: Optional[int]
    author_name: Optional[str]
    likes_count: int
    comments: List[CommentOut] = []
    class Config:
        orm_mode = True
