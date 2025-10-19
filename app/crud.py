from sqlalchemy.orm import Session
from app import models, schemas
from app.toxic_analis import is_toxic_by_model
from app.quality_rating import rate_text_quality, calculate_points
from fastapi import HTTPException
from typing import List, Optional

def _format_author_name(user: models.User) -> str:
    parts = [user.firstname, user.surname, user.lastname]
    parts = [p for p in parts if p]
    if parts:
        return " ".join(parts)
    return user.phone

def get_user_or_create(db: Session, phone: str, firstname: Optional[str] = None,
                       surname: Optional[str] = None, lastname: Optional[str] = None,
                       age: Optional[int] = None) -> models.User:
    """
    Find user by phone, create if not exists. Update fields if provided and different.
    """
    user = db.query(models.User).filter(models.User.phone == phone).first()
    if user:
        updated = False
        if firstname and user.firstname != firstname:
            user.firstname = firstname
            updated = True
        if surname and user.surname != surname:
            user.surname = surname
            updated = True
        if lastname and user.lastname != lastname:
            user.lastname = lastname
            updated = True
        if age is not None and user.age != age:
            user.age = age
            updated = True
        if updated:
            db.commit()
            db.refresh(user)
        return user
    new = models.User(phone=phone, firstname=firstname, surname=surname, lastname=lastname, age=age)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

def create_post(db: Session, post_in: schemas.PostCreate):
    
    toxic = is_toxic_by_model(post_in.description)
    print(f"Toxic check result: {toxic}")
    if toxic:
        raise HTTPException(status_code=400, detail="Post contains toxic content")

    author_id = None
    author_name = None
    author_user = None
    
    if post_in.author_phone:
        author_user = get_user_or_create(
            db,
            phone=post_in.author_phone,
            firstname=post_in.author_firstname,
            surname=post_in.author_surname,
            lastname=post_in.author_lastname,
            age=post_in.author_age
        )
        author_id = author_user.id
        author_name = _format_author_name(author_user)

    combined_text = f"{post_in.title}\n{post_in.description}"
    quality_score = rate_text_quality(combined_text)
    points_awarded = calculate_points(quality_score)

    db_post = models.Post(
        title=post_in.title,
        description=post_in.description,
        categories=post_in.categories,
        age_segment=post_in.age_segment,
        age_restriction=post_in.age_restriction,
        community_id=post_in.community_id,
        author_id=author_id,
        author_name=author_name,
        quality_score=quality_score,
        points_awarded=points_awarded
    )
    db.add(db_post)
    
    if author_user:
        author_user.total_points += points_awarded
    
    db.commit()
    db.refresh(db_post)
    return db_post

def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def list_posts(db: Session, category: str = None, skip: int = 0, limit: int = 50,
               user_age: Optional[int] = None) -> List[models.Post]:
    """
    Список постов с фильтрацией по категории и возрастным ограничениям.
    """
    q = db.query(models.Post)
    
    if category:
        q = q.filter(models.Post.categories.contains([category]))
    
    # фильтрация по возрасту пользователя
    if user_age is not None:
        q = q.filter(models.Post.age_restriction <= user_age)
    
    return q.order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()

def update_post(db: Session, post: models.Post, update: schemas.PostUpdate):
    for field, val in update.dict(exclude_unset=True).items():
        setattr(post, field, val)
    db.commit()
    db.refresh(post)
    return post

def delete_post(db: Session, post: models.Post):
    db.delete(post)
    db.commit()

def add_comment(db: Session, c: schemas.CommentCreate):
    post = get_post(db, c.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    user = get_user_or_create(
        db, c.author_phone, c.author_firstname, 
        c.author_surname, c.author_lastname, c.author_age
    )
    
    if user.age is not None and post.age_restriction > user.age:
        raise HTTPException(
            status_code=403, 
            detail=f"Age restriction: post requires age {post.age_restriction}+"
        )
    
    comment = models.Comment(
        post_id=c.post_id,
        parent_id=c.parent_id,
        author_id=user.id,
        author_name=_format_author_name(user),
        text=c.text
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def toggle_like(db: Session, post: models.Post, phone: str,
                firstname: Optional[str] = None, surname: Optional[str] = None, 
                lastname: Optional[str] = None, age: Optional[int] = None):
    """
    Toggle like by user's phone. Return dict {"action": "added"/"removed", "likes_count": N}
    """
    user = get_user_or_create(db, phone, firstname, surname, lastname, age)
    
    if user.age is not None and post.age_restriction > user.age:
        raise HTTPException(
            status_code=403, 
            detail=f"Age restriction: post requires age {post.age_restriction}+"
        )
    
    existing = (
        db.query(models.Like)
        .filter(models.Like.post_id == post.id)
        .filter(models.Like.user_id == user.id)
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        likes_count = db.query(models.Like).filter(models.Like.post_id == post.id).count()
        return {"action": "removed", "likes_count": likes_count}
    
    like = models.Like(user_id=user.id, post_id=post.id)
    db.add(like)
    db.commit()
    likes_count = db.query(models.Like).filter(models.Like.post_id == post.id).count()
    return {"action": "added", "likes_count": likes_count}