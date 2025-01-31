#Este código hace lo siguiente:

#-Define el router /users.
#-Conecta a la base de datos.
#-Crea un modelo UserCreate para recibir datos del usuario.
#-Crea los endpoints:
#-GET /users/: Obtener todos los usuarios.
#-POST /users/: Crear un usuario en la base de datos.


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import User
from src.security import hash_password
from pydantic import BaseModel, EmailStr
from fastapi.security import OAuth2PasswordBearer
from src.security import decode_access_token
from src.utils import is_valid_email  # Asegúrate de tener esta función en utils.py
from src.security import generate_reset_token, send_reset_email
from jose import JWTError, jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/users", 
                   tags=["Users"])

SECRET_KEY = "super_secret_key"  # Cámbiala por una clave segura
ALGORITHM = "HS256"

# Conexión con la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    return payload

# Esquema de usuario
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr
    
class PasswordReset(BaseModel):
    token: str
    new_password: str

#Endpoint para obtener todos los usuarios
@router.get("/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

#Endpoint que devuelve el nombre del usuario tras inngresar su token generado
@router.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["sub"]}

#Endpoint para crear un usuario con validaciones
@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    #Validar si el email es correcto
    if not is_valid_email(user.email):
        raise HTTPException(status_code=400, detail="El email no es válido")

    #Verificar si el usuario o email ya existen
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="El username o email ya está en uso")

    #Validar la longitud mínima de la contraseña
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres")

    #Hashear la contraseña antes de guardarla
    hashed_pw = hash_password(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_pw)
    
    # Guardar en la base de datos
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "Usuario creado exitosamente"}

#Endpoint que simula el envio de un correo para reestablecer una contraseña
@router.post("/password-reset/")
def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="No existe una cuenta con ese email")

    reset_token = generate_reset_token(user.email)  # Generar un token de recuperación
    send_reset_email(user.email, reset_token)  # Simulación de envío de email (debes implementarlo)

    return {"message": "Se ha enviado un correo con instrucciones para restablecer la contraseña"}

#Endpoint para actualizar la contraseña
@router.post("/password-reset/confirm/")
def reset_password(data: PasswordReset, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="El token ha expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Token inválido")

    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 8 caracteres")

    user.hashed_password = hash_password(data.new_password)
    db.commit()

    return {"message": "Contraseña actualizada correctamente"}
