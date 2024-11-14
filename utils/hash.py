import bcrypt

# pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class PasswordHasher:
    @staticmethod
    def generate_hash(password: str):
        # convert password to bytes
        bytes = password.encode('utf-8')
        # hash the password
        hashed = bcrypt.hashpw(bytes, bcrypt.gensalt())

        return hashed.decode('utf-8') 
    
    @staticmethod
    def verify_password(hashed_password, plain_password):
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
