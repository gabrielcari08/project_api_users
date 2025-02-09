#Que hace este código

#hash_password(password): Convierte la contraseña en un hash seguro.
#verify_password(plain_password, hashed_password): Compara una contraseña ingresada con su versión hasheada.

import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Clave secreta para firmar los tokens
SECRET_KEY = "super_secret_key"  # Cámbiala por una clave segura
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Cargar variables de entorno
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def generate_reset_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=15)  # Token válido por 15 minutos
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def send_reset_email(email: str, token: str):
    reset_url = f"http://localhost:8000/reset-password?token={token}"
    
    # Configurar el correo
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = email
    msg["Subject"] = "Recuperación de contraseña"

    body = f"""Restablecer contraseña

    Haz clic en el siguiente enlace para restablecer tu contraseña:
    {reset_url}

    Este enlace expirará en 15 minutos.
    """
    msg.attach(MIMEText(body, "plain"))

    try:
        # Conectar al servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Habilitar seguridad
        server.login(SMTP_USER, SMTP_PASS)  # Autenticación
        server.sendmail(SMTP_USER, email, msg.as_string())  # Enviar email
        server.quit()
        print(f"Correo enviado a {email}")
    except Exception as e:
        print(f"Error enviando correo: {e}")