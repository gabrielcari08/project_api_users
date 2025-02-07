#Este codigo hace lo siguiente

#-Define un modelo User, que representa la tabla users en PostgreSQL.
#-Crea columnas como id, username, email, hashed_password y is_active.

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    
class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)  # Guardamos el token revocado
    created_at = Column(DateTime, default=datetime.utcnow)  # Fecha en que se revocó el token