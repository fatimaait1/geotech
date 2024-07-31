
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