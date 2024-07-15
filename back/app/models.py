from uuid import uuid4
from geoalchemy2 import Geometry
from sqlalchemy import DOUBLE_PRECISION, Column, Date, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def get_uuid():
    return uuid4().hex

class User(Base):
    __tablename__ = 'users'
    #id = Column(String, primary_key=True, unique=True, default=get_uuid)
    username = Column(String, primary_key=True, unique=True, index=True) 
    password = Column(String, nullable=False)
    status = Column(String, default='verified')
    role = Column(String, default='admin')


class Project(Base):
    __tablename__ = 'projects'
    name = Column(String, unique=True, index=True, primary_key=True, nullable=False) 
    project_id = Column(String, index=True, nullable=False) 
    East = Column(DOUBLE_PRECISION, nullable=False)
    North = Column(DOUBLE_PRECISION, nullable=False)
    geom = Column(Geometry('POINT', srid= 4326), nullable=False)
    date= Column(Date, nullable=True)


class BH(Base):
    __tablename__ = 'bh'
    pointID = Column(String, nullable=False)
    project_name = Column(String, ForeignKey('projects.name', ondelete="CASCADE"), nullable=False)
    report_id = Column(String, nullable=True)
    East = Column(DOUBLE_PRECISION, nullable=False)
    North = Column(DOUBLE_PRECISION, nullable=False)
    Elevation = Column(DOUBLE_PRECISION, nullable=False)
    geom = Column(Geometry('POINT', srid= 4326), nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('project_name', 'pointID', name='pk_project_name_pointID'),
        {'extend_existing': True}
    )

class geol(Base):
    __tablename__ = 'geol'
    
    depth_from = Column(DOUBLE_PRECISION, nullable=False)
    depth_to = Column(DOUBLE_PRECISION, nullable=False)
    geol_value = Column(String, nullable=False)
    pointID = Column(String, nullable=False)
    project_name = Column(String, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ['pointID', 'project_name'], 
            ['bh.pointID', 'bh.project_name']
        ),
        PrimaryKeyConstraint('pointID', 'project_name', 'depth_from', 'depth_to', name='pk_geol')
    )


class bhparams(Base):
    __tablename__ = 'bhparams'
    id = Column(Text, primary_key=True, unique=True, default=get_uuid)
    name = Column(String, nullable=True) #name of parameter
    depth = Column(DOUBLE_PRECISION, nullable=True)
    value = Column(DOUBLE_PRECISION, nullable=True)
    pointID = Column(String, nullable=False)
    project_name = Column(String, nullable=False)
    samp_ref = Column(String, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(
            ['pointID', 'project_name'], 
            ['bh.pointID', 'bh.project_name']
        ),
        #PrimaryKeyConstraint('pointID', 'project_name', 'name', 'samp_ref', 'depth', name='pk_bhparams')
    )

    







