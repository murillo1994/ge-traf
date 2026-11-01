import pytest
from cryptography.fernet import Fernet, InvalidToken


def test_encrypt_returns_bytes(app):
    with app.app_context():
        from app.services.crypto import encrypt_token

        result = encrypt_token("my-secret-token")
        assert isinstance(result, bytes)


def test_decrypt_recovers_original(app):
    with app.app_context():
        from app.services.crypto import decrypt_token, encrypt_token

        original = "my-secret-token-12345"
        encrypted = encrypt_token(original)
        decrypted = decrypt_token(encrypted)
        assert decrypted == original


def test_encrypted_not_equal_to_plaintext(app):
    with app.app_context():
        from app.services.crypto import encrypt_token

        original = "my-secret-token"
        encrypted = encrypt_token(original)
        assert encrypted != original.encode()


def test_decrypt_with_wrong_key_fails(app):
    with app.app_context():
        from app.services.crypto import encrypt_token

        encrypted = encrypt_token("test-token")

    wrong_fernet = Fernet(Fernet.generate_key())
    with pytest.raises(InvalidToken):
        wrong_fernet.decrypt(encrypted)
