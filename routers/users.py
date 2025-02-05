from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import timedelta
from db.database import SessionLocal
from db.models import User
from utils import is_valid_email
from security import (
    oauth2_scheme, 
    get_current_user, 
    verify_password, 
    get_password_hash, 
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/users", tags=["Users"])

# Esquema del usuario
class UserCreate(BaseModel):
    username: str
    email: EmailStr  # Verifica automáticamente que el email tenga un formato válido
    password: str  
       
class UserLogin(BaseModel):
    username: str
    password: str

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")  # Obtener todos los usuarios (solo para pruebas)
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.post("/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Validar el formato del email
    if not is_valid_email(user.email):
        raise HTTPException(status_code=400, detail="Formato de email inválido")

    # Verificar si el usuario o email ya existen
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="El username o email ya está en uso")

    # Validar la longitud mínima de la contraseña
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres")

    # Hashear la contraseña
    hashed_password = get_password_hash(user.password)

    # Crear el nuevo usuario
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "User registered successfully", "username": db_user.username, "email": db_user.email}

@router.post("/token")
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
    }
