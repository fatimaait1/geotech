
from geoalchemy2 import Geometry
from sqlalchemy import DOUBLE_PRECISION, Column, Date, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'public'}
    username = Column(String, primary_key=True, unique=True, index=True)
    password = Column(String, nullable=False)
    status = Column(String, default='verified')
    role = Column(String, default='admin')



class Borehole(Base):
    __tablename__ = 'boreholes'
    __table_args__ = {'schema': 'bh'}
    id= Column(Integer, primary_key=True, index=True, autoincrement=True)
    project= Column(String, nullable=False)
    pointID = Column(String, nullable=False)
    report_id = Column(String, nullable=True)
    East = Column(DOUBLE_PRECISION, nullable=False)
    North = Column(DOUBLE_PRECISION, nullable=False)
    Elevation = Column(DOUBLE_PRECISION, nullable=False)
    geom = Column(Geometry('POINT', srid=4326), nullable=False)
    date= Column(Date, nullable=True)

class Geol(Base):
    __tablename__ = 'geol'
    __table_args__ = {'schema': 'bh'}
    id= Column(Integer, primary_key=True, index=True, autoincrement=True)
    pointID = Column(String, nullable=False)
    project= Column(String, nullable=False)
    bh_id= Column(Integer, ForeignKey('bh.boreholes.id', ondelete="CASCADE"), nullable=False)
    depth_from = Column(DOUBLE_PRECISION, nullable=False)
    depth_to = Column(DOUBLE_PRECISION, nullable=False)
    geol_value = Column(String, nullable=False)


class Bh_params(Base):
    __tablename__ = 'params'
    __table_args__ = {'schema': 'bh'}
    id= Column(Integer, primary_key=True, index=True, autoincrement=True)
    bh_id = Column(Integer, ForeignKey('bh.boreholes.id', ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=True)
    depth = Column(DOUBLE_PRECISION, nullable=True)
    value = Column(DOUBLE_PRECISION, nullable=True)
    pointID = Column(String, nullable=False)
    project = Column(String, nullable=False)
    samp_ref = Column(String, nullable=True)



from sqlalchemy import MetaData, Table, Column, Integer
from sqlalchemy.ext.automap import automap_base
from .database import engine

metadata = MetaData(schema='cpt')
project_table = Table('project', metadata, autoload_with=engine)
grid_table = Table('grid', metadata, autoload_with=engine)
info_table = Table('info', metadata, autoload_with=engine)
meas_table = Table('meas', metadata, autoload_with=engine)

class Project(Base):
    __table__ = project_table
    __mapper_args__ = {
        'primary_key': [project_table.c.id]  # Replace 'id' with the actual primary key column name
    }

class Box(Base):
    __table__ = grid_table
    __mapper_args__ = {
        'primary_key': [grid_table.c.id]  # Replace 'id' with the actual primary key column name
    }

class Cpt(Base):
    __table__ = info_table
    __mapper_args__ = {
        'primary_key': [info_table.c.id]  # Replace 'id' with the actual primary key column name
    }

class Meas(Base):
    __table__ = meas_table
    __mapper_args__ = {
        'primary_key': [meas_table.c.id]  # Replace 'id' with the actual primary key column name
    }
