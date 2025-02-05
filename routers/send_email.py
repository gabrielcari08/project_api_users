from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, EmailStr
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

router = APIRouter(prefix="/send-email"
                   , tags=["Send Email"])

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),  # Convertir a entero
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS") == "True",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS") == "True",
    USE_CREDENTIALS=True
)

class EmailSchema(BaseModel):
    email: EmailStr
    subject: str
    message: str

async def send_email(email_data: EmailSchema):
    message = MessageSchema(
        subject=email_data.subject,
        recipients=[email_data.email],
        body=email_data.message,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)

@router.post("/")
async def send_email_endpoint(email_data: EmailSchema, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email_data)
    return {"message": "Email en proceso de envío"}
