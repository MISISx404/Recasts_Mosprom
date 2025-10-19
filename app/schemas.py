from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    phone: str
    firstname: Optional[str] = None
    surname: Optional[str] = None
    lastname: Optional[str] = None
    age: Optional[int] = None

    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 150):
            raise ValueError('Age must be between 0 and 150')
        return v

class UserOut(BaseModel):
    id: int
    phone: str
    firstname: Optional[str] = None
    surname: Optional[str] = None
    lastname: Optional[str] = None
    age: Optional[int] = None
    total_points: float = 0.0
    created_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2

class CommentCreate(BaseModel):
    post_id: int
    parent_id: Optional[int] = None
    author_phone: str
    author_firstname: Optional[str] = None
    author_surname: Optional[str] = None
    author_lastname: Optional[str] = None
    author_age: Optional[int] = None
    text: str

class CommentOut(BaseModel):
    id: int
    post_id: int
    parent_id: Optional[int] = None
    author_id: int
    author_name: str
    text: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2

class PostCreate(BaseModel):
    title: str
    description: str
    categories: List[str]
    age_segment: Optional[int] = None
    age_restriction: int = 0  # 0, 6, 12, 16, 18
    community_id: Optional[int] = None
    author_phone: Optional[str] = None
    author_firstname: Optional[str] = None
    author_surname: Optional[str] = None
    author_lastname: Optional[str] = None
    author_age: Optional[int] = None

    @field_validator('age_restriction')
    @classmethod
    def validate_age_restriction(cls, v):
        if v not in [0, 6, 12, 16, 18]:
            raise ValueError('Age restriction must be one of: 0, 6, 12, 16, 18')
        return v

class PostUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    categories: Optional[List[str]] = None
    age_segment: Optional[int] = None
    age_restriction: Optional[int] = None
    community_id: Optional[int] = None

    @field_validator('age_restriction')
    @classmethod
    def validate_age_restriction(cls, v):
        if v is not None and v not in [0, 6, 12, 16, 18]:
            raise ValueError('Age restriction must be one of: 0, 6, 12, 16, 18')
        return v

class PostOut(BaseModel):
    id: int
    title: str
    description: str
    categories: List[str]
    age_segment: Optional[int] = None
    age_restriction: int = 0
    community_id: Optional[int] = None
    quality_score: Optional[float] = None
    points_awarded: Optional[float] = None
    created_at: datetime
    author_id: Optional[int] = None
    author_name: Optional[str] = None
    likes_count: int = 0
    comments: List[CommentOut] = []
    
    class Config:
        from_attributes = True  # Pydantic v2 (вместо orm_mode)