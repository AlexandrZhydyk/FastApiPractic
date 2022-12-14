import os
# from starlette.config import Config
#
# config = Config(".env")

class Config:
    if os.environ.get("TESTING"):
        DB_USER = "postgres"
        DB_PASSWORD = "admin"
        DB_NAME = "test_fastapi"
        DB_HOST = "localhost"
        DB_PORT = "5432"
    else:
        DB_USER = os.getenv("POSTGRES_USER", "postgres")
        DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
        DB_NAME = os.getenv("POSTGRES_NAME", "fastapi")
        DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
        DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DB_CONFIG = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SECRET_KEY = os.getenv("SECRET_KEY", "44f4c1953195bdcbdaad74b399171c3a48a9c56c8f9738352502ce4a261f4149")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15)
    REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 2880)
    JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "1e3c5b421af30b2495e0af81bc71af012a369bd0ce6a1315833c4810f3fae500")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
