#Codigo para la validacion de email.

#Este parte del codigo no funciona como se desea. Revisar en algun momento.

import re

def is_valid_email(email: str) -> bool:
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return re.match(email_regex, email) is not None