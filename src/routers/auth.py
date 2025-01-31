#Que hace este endpoint:

#-Recibe usuario y contraseña en POST /auth/login.
# Verifica si el usuario existe y la contraseña es correcta.
# Genera un JWT y lo devuelve.

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from src.routers.users import get_db
from src.models import User
from src.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.get("/protected-route")
async def protected_route(token: str = Depends(oauth2_scheme)):
    return {"message": "Tienes acceso a esta ruta", "token": token}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}
