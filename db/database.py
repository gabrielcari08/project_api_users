#Este codigo hace lo siguiente:

#-Crea la conexión con PostgreSQL usando create_engine.
#-Define una sesión para interactuar con la base de datos.
#-Define Base, que será la clase base para nuestros modelos.

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user_test:12345@localhost/api_users"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()