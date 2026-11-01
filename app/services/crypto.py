from app import extensions


def encrypt_token(plain_text):
    if isinstance(plain_text, str):
        plain_text = plain_text.encode()
    return extensions.fernet.encrypt(plain_text)


def decrypt_token(cipher_bytes):
    return extensions.fernet.decrypt(cipher_bytes).decode()
