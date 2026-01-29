from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from os import environ

if "POSTGRES_PASSWORD" not in environ:
    raise EnvironmentError("POSTGRES_PASSWORD environment variable not set")

URL_DATABASE = f"postgresql+psycopg2://group_n_meet:{environ['POSTGRES_PASSWORD']}@localhost/group_n_meet"

engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()