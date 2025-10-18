from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import UserCreate, UserOut
from ..database import get_db
from ..crud import get_user_or_create
from .. import models

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut)
def create_user(u: UserCreate, db: Session = Depends(get_db)):
    user = get_user_or_create(db, u.phone, u.firstname, u.surname, u.lastname)
    return user

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
