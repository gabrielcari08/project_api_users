#Codigo para la validacion de email.

#Este parte del codigo no funciona como se desea. Revisar en algun momento.

import re

def is_valid_email(email: str) -> bool:
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None