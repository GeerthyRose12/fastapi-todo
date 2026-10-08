from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, TokenResponse, RefreshTokenRequest
from app.utils import hash_password, verify_password, create_access_token, create_refresh_token, verify_refresh_token

router = APIRouter(tags=["Users"])


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(email=user.email, password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"user_id": db_user.id})
    refresh_token = create_refresh_token({"user_id": db_user.id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        payload = verify_refresh_token(request.refresh_token)
        user_id = payload.get("user_id")
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=401, detail="User not found")
        access_token = create_access_token({"user_id": db_user.id})
        refresh_token = create_refresh_token({"user_id": db_user.id})
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
