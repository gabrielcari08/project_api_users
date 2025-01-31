#Este código hace lo siguiente:

#-Inicializa FastAPI.
#-Se conecta con la base de datos.
#-Incluye el router users (que crearemos en el siguiente paso).
#-Define un endpoint de prueba en /.


from fastapi import FastAPI, Depends
from src.database import engine, Base
from fastapi.security import OAuth2PasswordBearer
from src.routers import users, auth # Importaremos este módulo después

#Definir el esquema OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#Crear las tablas (en caso de que no existan)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Usuarios", version="1.0")

#Incluir los endpoints de usuarios
app.include_router(users.router)
app.include_router(auth.router)

@app.get("/")
def home():
    return {"message": "Bienvenido a la API de Usuarios"}

