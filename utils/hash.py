from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class PasswordHasher:
    @staticmethod
    def generate_hash(password: str):
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(hashed_password, plain_password):
        return pwd_context.verify(plain_password, hashed_password)
