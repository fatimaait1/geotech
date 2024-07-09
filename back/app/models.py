from uuid import uuid4
from geoalchemy2 import Geometry
from sqlalchemy import DOUBLE_PRECISION, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def get_uuid():
    return uuid4().hex

class User(Base):
    __tablename__ = 'users'
    #id = Column(String, primary_key=True, unique=True, default=get_uuid)
    username = Column(String, primary_key=True, unique=True, index=True) 
    password = Column(String, nullable=False)
    role = Column(String, default='admin')


class Project(Base):
    __tablename__ = 'projects'
    #id = Column(String, primary_key=True, unique=True, default=get_uuid)
    name = Column(String, unique=True, index=True, primary_key=True, nullable=False) 
    description = Column(String, nullable=True)
    East = Column(DOUBLE_PRECISION, nullable=False)
    North = Column(DOUBLE_PRECISION, nullable=False)
    Parameter1 = Column(DOUBLE_PRECISION, nullable=False)
    Parameter2 = Column(DOUBLE_PRECISION, nullable=False)
    Parameter3 = Column(DOUBLE_PRECISION, nullable=False)
    geom = Column(Geometry('POINT', srid= 32640), nullable=False)





