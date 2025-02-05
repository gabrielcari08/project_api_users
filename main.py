from fastapi import FastAPI, BackgroundTasks, Depends
from routers import send_email, users

app = FastAPI(title="API de Usuarios", version="1.0")

app.include_router(send_email.router)
app.include_router(users.router)

@app.get("/")
def home():
    return {"message": "Bienvenido a la API de Usuarios"}
