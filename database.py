import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

USER = os.getenv("POSTGRES_USER", "postgres")
PASSWORD = os.getenv("POSTGRES_PASSWORD", "Omkar@31415")
HOST = os.getenv("POSTGRES_SERVER", "localhost")
PORT = os.getenv("POSTGRES_PORT", "5432")
DB = os.getenv("POSTGRES_DB", "postgres")

# URL encode password as it contains special characters (@)
encoded_password = quote_plus(PASSWORD)
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{USER}:{encoded_password}@{HOST}:{PORT}/{DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    meta_info = Column(JSONB, default={})

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
