from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import timedelta
from db.database import SessionLocal
from db.models import User, RevokedToken
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
    email: str  
    password: str  
       
class UserLogin(BaseModel):
    credential: str  # Puede ser username o email
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

@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    # Buscar el usuario en la base de datos por username o email
    db_user = db.query(User).filter(
        (User.username == user.credential) | (User.email == user.credential)
    ).first()

    # Si el usuario no existe o la contraseña es incorrecta, devolver error
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # Generar token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Revoca el token de autenticación del usuario"""
    # Verificar si el token ya está revocado
    if db.query(RevokedToken).filter(RevokedToken.token == token).first():
        raise HTTPException(status_code=400, detail="Token already revoked")

    # Guardar el token en la base de datos para marcarlo como revocado
    revoked_token = RevokedToken(token=token)
    db.add(revoked_token)
    db.commit()

    return {"message": "Logout successful. Token revoked."}

@router.get("/me")
async def users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
    }
