from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List

conf = ConnectionConfig(
    MAIL_USERNAME="mikeekh666@gmail.com",
    MAIL_PASSWORD="mpasfxtjvcixwllb",
    MAIL_FROM="mikeekh666@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_SSL_TLS= False,
    MAIL_STARTTLS=True,
    # MAIL_TLS=True,
    # MAIL_SSL=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


async def send_mail(subject: str, recipient: List, message: str):
    message = MessageSchema(
        subject=subject,
        recipients=recipient,
        body=message,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
