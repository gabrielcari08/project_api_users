#Este codigo hace lo siguiente

#-Importa Base y engine desde database.py.
#-Importa los modelos para que SQLAlchemy los reconozca.
#-Llama a Base.metadata.create_all(bind=engine) para crear las tablas en la base de datos.

from database import engine, Base
import models

print("Creando las tablas en la base de datos...")

Base.metadata.create_all(bind=engine)

print("Tablas creadas exitosamente")