from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:fatimazahra@localhost/DBBH"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
#engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"options": "-csearch_path=bh,public"})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)