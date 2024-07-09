from sqlalchemy.orm import Session
from . import models, schemas

def get_project(db: Session, project_name: str):
    return db.query(models.Project).filter(models.Project.name == project_name).first()

def get_projects(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(
        name=project.name,
        description=project.description,
        East=project.East,
        North=project.North,
        geom=f'SRID=32640;POINT({project.East} {project.North})'
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project