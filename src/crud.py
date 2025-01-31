#Este codigo es crucial ya que dentro de el tenemos una funcion que verifica si un usuario ya existe en la
#base de datos antes de crearlo

from sqlalchemy.orm import Session
from .models import User  

def get_user_by_username_or_email(db: Session, username: str, email: str):
    return db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
