from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import schemas, crud, models
from ..database import get_db

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=schemas.PostOut)
def create_post(post_in: schemas.PostCreate, db: Session = Depends(get_db)):
    post = crud.create_post(db, post_in)
    likes_count = db.query(models.Like).filter(models.Like.post_id == post.id).count()
    return schemas.PostOut(
        id=post.id,
        title=post.title,
        description=post.description,
        categories=post.categories,
        age_segment=post.age_segment,
        community_id=post.community_id,
        created_at=post.created_at,
        author_id=post.author_id,
        author_name=post.author_name,
        likes_count=likes_count,
        comments=[]
    )

@router.get("/", response_model=List[schemas.PostOut])
def list_posts(category: Optional[str] = Query(None), skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    posts = crud.list_posts(db, category, skip, limit)
    out = []
    for p in posts:
        likes_count = db.query(models.Like).filter(models.Like.post_id == p.id).count()
        comments = db.query(models.Comment).filter(models.Comment.post_id == p.id).all()
        out.append(schemas.PostOut(
            id=p.id, title=p.title, description=p.description, categories=p.categories,
            age_segment=p.age_segment, community_id=p.community_id, created_at=p.created_at,
            author_id=p.author_id, author_name=p.author_name, likes_count=likes_count,
            comments=[schemas.CommentOut.from_orm(c) for c in comments]
        ))
    return out

@router.get("/{post_id}", response_model=schemas.PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    p = crud.get_post(db, post_id)
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    likes_count = db.query(models.Like).filter(models.Like.post_id == p.id).count()
    comments = db.query(models.Comment).filter(models.Comment.post_id == p.id).all()
    return schemas.PostOut(
        id=p.id, title=p.title, description=p.description, categories=p.categories,
        age_segment=p.age_segment, community_id=p.community_id, created_at=p.created_at,
        author_id=p.author_id, author_name=p.author_name, likes_count=likes_count,
        comments=[schemas.CommentOut.from_orm(c) for c in comments]
    )

@router.put("/{post_id}", response_model=schemas.PostOut)
def update_post(post_id: int, upd: schemas.PostUpdate, db: Session = Depends(get_db)):
    p = crud.get_post(db, post_id)
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    p = crud.update_post(db, p, upd)
    likes_count = db.query(models.Like).filter(models.Like.post_id == p.id).count()
    comments = db.query(models.Comment).filter(models.Comment.post_id == p.id).all()
    return schemas.PostOut(
        id=p.id, title=p.title, description=p.description, categories=p.categories,
        age_segment=p.age_segment, community_id=p.community_id, created_at=p.created_at,
        author_id=p.author_id, author_name=p.author_name, likes_count=likes_count,
        comments=[schemas.CommentOut.from_orm(c) for c in comments]
    )

@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    p = crud.get_post(db, post_id)
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    crud.delete_post(db, p)
    return {"status": "deleted"}

@router.post("/{post_id}/like")
def like_toggle(
    post_id: int,
    phone: str,
    firstname: Optional[str] = None,
    surname: Optional[str] = None,
    lastname: Optional[str] = None,
    db: Session = Depends(get_db)
):
    p = crud.get_post(db, post_id)
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    res = crud.toggle_like(db, p, phone, firstname, surname, lastname)
    return res

@router.post("/{post_id}/comments", response_model=schemas.CommentOut)
def add_comment(post_id: int, comment_in: schemas.CommentCreate, db: Session = Depends(get_db)):
    # ensure post_id matches
    if comment_in.post_id != post_id:
        raise HTTPException(status_code=400, detail="post_id mismatch")
    c = crud.add_comment(db, comment_in)
    return schemas.CommentOut.from_orm(c)
