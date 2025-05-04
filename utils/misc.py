from random import choices
from string import ascii_letters, digits

def create_id(length=6):
    return ''.join(choices(ascii_letters + digits, k=length))