import os

from dotenv import load_dotenv

load_dotenv()

PG_USER: str = os.getenv("PG_USER")
PG_PASSWORD: str = os.getenv("PG_PASSWORD")
PG_TABLENAME: str = os.getenv("PG_TABLENAME")
PG_DATABASE_URI: str = os.getenv("PG_DATABASE_URI")

JWT_SECRET_KEY: str = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("SECRET_KEY_REFRESH")

JWT_ACCESS_TOKEN_EXPIRES_MINUTES = os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 10)
JWT_REFRESH_TOKEN_EXPIRES_MINUTES = os.getenv("JWT_REFRESH_TOKEN_EXPIRES_MINUTES", 60)

S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "xryak")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "Sergey125!")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://192.168.1.201:9002")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "lingoplay")
