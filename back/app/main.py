from typing import Annotated, Optional
from fastapi import FastAPI, Depends, HTTPException, Header, Request, status
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models, schemas
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from .schemas import ProjectCreate, ProjectUpdate, UserCreate, UserUpdate
from .models import User, Project
from fastapi.middleware.cors import CORSMiddleware
from shapely import wkb
from shapely.geometry import Point, Polygon
from pyproj import Proj, transform
from geoalchemy2.shape import from_shape

SECRET_KEY = "nmdcsecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480 #8H
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    username = user.username
    password = user.password
    isExist = db.query(User).filter(User.username == username).first()
    if isExist:
        return {'message': 'User already exists'}, 200    
    else:
        hashed_password = pwd_context.hash(password)
        new_user = User(username=username, password=hashed_password, role='admin') 
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {'message': 'Account created.'}, 200
    

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    username = user.username
    password = user.password
    user = db.query(User).filter(User.username==username).first()
    if user and pwd_context.verify(password, user.password):
        access_token = create_access_token(data={"user": user.username})
        return {"access_token": access_token, "role": user.role}
    return {'message': 'Incorrect username or password'}, 404

    
@app.get("/projects")
def getProjects(Authorization: Annotated[str | None, Header()] = None, db: Session = Depends(get_db)):
    print(Authorization)
    try:
        payload = jwt.decode(Authorization, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload["user"])
        prjs= db.query(Project).all()
        data=[]
        proj_in = Proj(init='epsg:32640') #utm zone 40 northing/easting
        proj_out = Proj(init='epsg:4326') #wgs84 long/lat
        for bh in prjs:
            lon, lat = transform(proj_in, proj_out, bh.East, bh.North)
            point = Point(lon, lat)
            geom = from_shape(point)
            geometry = wkb.loads(bytes(geom.data))
            #print(geometry.x)
            data.append({'name': bh.name, 'parameter1': bh.Parameter1, 'parameter2': bh.Parameter2 , 'parameter3': bh.Parameter3, 'x': bh.East, 'y': bh.North})
        return {'data': data}
    except JWTError:
        return {'error': 'invalid token'}, 401
         


@app.post("/projects")
def createProject(project: ProjectCreate, db: Session = Depends(get_db)):
    try:
        new_project= Project(name=project.name, description= project.description, Parameter1= project.parameter1, Parameter2= project.parameter2, Parameter3= project.parameter3, East= project.longitude, North= project.latitude, geom= from_shape(Point(project.longitude, project.latitude)))
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        return {'message': 'Project created.'}, 200
    except:
        return {'message': 'error creation.'}, 401


@app.put("/projects/{project_name}/modify")
def modify_project(project_name: str, project_update: ProjectUpdate, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.name == project_name).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    updated_data = project_update.dict(exclude_unset=True)
    print(updated_data)
    for field, value in updated_data.items():
        setattr(db_project, field, value)
    db.commit()
    db.refresh(db_project)
    return {'message': 'Project modified.'}, 200


@app.delete("/projects/{project_name}", status_code=204)
def delete_project(project_name: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.name == project_name).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}


@app.get("/users")
def getUsers(Authorization: Annotated[str | None, Header()] = None, db: Session = Depends(get_db)):
    print(Authorization)
    try:
        payload = jwt.decode(Authorization, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload["user"])
        users= db.query(User).all()
        data=[]
        for bh in users:
            data.append({'name': bh.username, 'role': bh.role})
        return {'data': data}
    except JWTError:
        return {'error': 'invalid token'}, 401
         


@app.post("/users")
def createUser(project: ProjectCreate, db: Session = Depends(get_db)):
    try:
        new_project= Project(name=project.name, description= project.description, Parameter1= project.parameter1, Parameter2= project.parameter2, Parameter3= project.parameter3, East= project.longitude, North= project.latitude, geom= from_shape(Point(project.longitude, project.latitude)))
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        return {'message': 'Project created.'}, 200
    except:
        return {'message': 'error creation.'}, 401


@app.put("/users/{username}/modify")
def modify_user(username: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Project not found")
    updated_data = user_update.dict(exclude_unset=True)
    print(updated_data)
    for field, value in updated_data.items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return {'message': 'User modified.'}, 200


@app.delete("/users/{username}", status_code=204)
def delete_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}