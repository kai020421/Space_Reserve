"""Environment-based application settings."""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "").strip()
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480")
        )
        self.bcrypt_rounds = int(os.getenv("BCRYPT_ROUNDS", "12"))
        if self.bcrypt_rounds < 12:
            raise RuntimeError("BCRYPT_ROUNDS must be at least 12.")

settings = Settings()
