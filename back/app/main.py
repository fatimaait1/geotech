import io
import random
import re
import traceback
from typing import Annotated, List, Optional
from fastapi import FastAPI, Depends, File, HTTPException, Header, Request, UploadFile, status, Query
import numpy as np
import pandas as pd
import json
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models, schemas
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from .schemas import ProjectCreate, ProjectUpdate, UserCreate, UserUpdate, UserUpdate2
from .models import BH, User, Project, bhparams, geol
from fastapi.middleware.cors import CORSMiddleware
from shapely import wkb
from shapely.geometry import Point, Polygon
from pyproj import Proj, transform
from geoalchemy2.shape import from_shape
from scipy.interpolate import griddata, LinearNDInterpolator
from scipy.spatial import ConvexHull, Delaunay
import plotly.graph_objects as go

SECRET_KEY = "nmdcsecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480 #8H
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

origins = [
    "http://localhost:4200",
      "http://localhost:4200/home",  # Frontend URL
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
        new_user = User(username=username, password=hashed_password, role='nonadmin', status='unverified') 
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
    if user and pwd_context.verify(password, user.password) and user.status == 'verified':
        access_token = create_access_token(data={"user": user.username})
        return {"access_token": access_token, "role": user.role}
    return {'message': 'Incorrect username or password or unverified status.'}, 404

    
@app.get("/projects")
def getProjects(Authorization: Annotated[str | None, Header()] = None, db: Session = Depends(get_db)):
    #print(Authorization)
    try:
        payload = jwt.decode(Authorization, SECRET_KEY, algorithms=[ALGORITHM])
        #print(payload["user"])
        prjs= db.query(Project).all()
        data=[]
        for bh in prjs:
            geometry = wkb.loads(bytes(bh.geom.data))
            data.append({'name': bh.name, 'date': bh.date, 'x': geometry.x, 'y': geometry.y})
        return {'data': data, 'user': payload["user"]}
    except JWTError:
        return {'error': 'invalid token'}, 401
         

@app.post("/projects")
async def createProject(Files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    for bh_file in Files:
        if bh_file:
            try:
                    boreholes= None
                    filename = bh_file.filename.lower()
                    proj_in = Proj(init='epsg:32640') #utm zone 40 northing/easting
                    proj_out = Proj(init='epsg:4326') #wgs84 long/lat
                    if filename.endswith('.xls') or filename.endswith('.xlsx') or filename.endswith('.xlsm'):
                        ff=  await bh_file.read()
                        test= pd.ExcelFile(ff)
                        sheet_names= test.sheet_names
                        BHs = None
                        ISTPs = None
                        COREs = None
                        UCSs = None
                        GEOLs = None
                        if ('POINT' in sheet_names):
                            BHs = pd.read_excel(io.BytesIO(ff), sheet_name='POINT') 
                            if ('HOLE_NATE' in BHs.columns and 'HOLE_NATN' in BHs.columns and not BHs['HOLE_NATE'].isnull().all()):
                                BHs['East'] = BHs['HOLE_NATE']
                                BHs['North'] = BHs['HOLE_NATN']
                            BHs = BHs.dropna(subset=['PointID', 'East', 'North', 'Elevation'])

                        if ('ISPT' in sheet_names):
                            ISTPs = pd.read_excel(io.BytesIO(ff), sheet_name='ISPT') 
                            ISTPs = ISTPs.dropna(subset=['PointID', 'Depth', 'ISPT_REP'])
                        
                        if ('CORE' in sheet_names):
                            COREs = pd.read_excel(io.BytesIO(ff), sheet_name='CORE')
                            COREs = COREs.dropna(subset=['PointID', 'Depth', 'CORE_PREC', 'CORE_SREC', 'CORE_RQD']) 
                            #print(COREs)

                        if ('UNCONF COMPR' in sheet_names):
                           UCSs = pd.read_excel(io.BytesIO(ff), sheet_name='UNCONF COMPR') 
                           UCSs = UCSs.dropna(subset=['PointID', 'Depth', 'Strength'])

                        if ('GEOL' in sheet_names):
                           GEOLs = pd.read_excel(io.BytesIO(ff), sheet_name='GEOL')
                           GEOLs = GEOLs.dropna(subset=['PointID', 'Depth', 'GEOL_BASE', 'GEOL_LEG', 'GEOL_DESC'])


                        if BHs is not None and not BHs.empty:
                            project_name= filename[: filename.index('.xls')]
                            boreholes = BHs.iloc[:, 0].tolist()
                            print(boreholes)
                            first_row = BHs.iloc[0]
                            project_East = float(first_row['East'])
                            project_North = float(first_row['North'])
                            new_project= Project(name= project_name, project_id= project_name, East= project_East, North= project_North, geom= from_shape(Point(transform(proj_in, proj_out, project_East, project_North))))
                            db.add(new_project)
                            db.commit()
                            db.refresh(new_project)
                            for _, row in BHs.iterrows():
                                pointID= row['PointID']
                                if ('Report' in BHs.columns):
                                    report_id= row['Report']
                                else:
                                    report_id= ''
                                Elevation = row['Elevation']
                                East= float(row['East'])
                                North= float(row['North'])
                                X3857, Y3857 = transform(proj_in, proj_out, East, North)  
                                point = Point(X3857, Y3857)
                                geom = from_shape(point)
                                new_entry = BH(
                                pointID=pointID,
                                project_name= project_name,
                                report_id= report_id,
                                Elevation= Elevation,
                                East=East,
                                North=North,
                                geom=geom)
                                db.add(new_entry)
                            db.commit()
                    elif filename.endswith('.ags'):
                        frames_data = {}
                        ags_content0 = await bh_file.read()
                        ags_content= ags_content0.decode('utf-8')
                        frame_pattern = re.compile(r'"\*\*(.*?)\"', re.MULTILINE)
                        matches = re.finditer(frame_pattern, ags_content)
                        frames_to_extract= ['PROJ', 'HOLE', 'GEOL', 'CORE', 'ISPT', 'ABBR']
                        matches = list(frame_pattern.finditer(ags_content))
                        for i, match in enumerate(matches):
                            frame_name = match.group(1).strip()
                            if frame_name in frames_to_extract:
                               start_index = match.end()
                               end_index = matches[i + 1].start() if i + 1 < len(matches) else len(ags_content)
                               # Slice the content for the current frame
                               frame_content = ags_content[start_index:end_index]
                              # Find columns for the current frame
                               if frame_name == 'ABBR':
                                   result_dict = {}
                                   lines = frame_content.strip().split('\n')
                                   for line in lines[1:]:
                                    # Check if the line starts with '"GEOL_LEG"'
                                       if line.startswith('"GEOL_LEG"'):
                                       # Split the line by commas
                                           parts = line.split(',')
                                         # Get the second and third elements, stripping the surrounding quotes
                                           key = parts[1].strip('\r"\n')
                                           value = parts[2].strip('\r"\n')
                                            # Store the key-value pair in the dictionary
                                           result_dict[key] = value
                                   #print(result_dict)
                               if frame_name != 'ABBR':
                                    columns_str= frame_content[: frame_content.find('"<UNITS>"')]
                                    #print(columns_str)
                                    all_columns= columns_str.strip('"').split(',')
                                    cleaned_columns = [col.strip('\r\n"*') for col in all_columns]
                                    #print(cleaned_columns)                    
                                    # Find data for the current frame
                                    rows= []
                                    data_lines = frame_content[frame_content.find('"<UNITS>"'):].split('\r\n')
                                    #print(data_lines)
                                    processed_lines = []
                                    # Initialize a dictionary to hold the most recent non-empty values for each column
                                    last_values = {}
                                    # Convert the data_lines to an iterator to allow skipping
                                    j=0
                                    data_lines_iter = data_lines[1:]
                                    while j < len(data_lines_iter):
                                            values = [val.strip('"') for val in data_lines_iter[j].split('","')]  
                                            # If current line is not <CONT>
                                            if values[0] != '<CONT>':
                                                # Check if there are empty values to fill
                                                has_empty = any(val == '' for val in values)
                                                k = j + 1
                                                while has_empty and k < len(data_lines_iter):
                                                    cont_values = [val.strip('"') for val in data_lines_iter[k].split('","')]
                                                    if cont_values[0] == '<CONT>':
                                                        # Fill the empty values from the subsequent <CONT> line
                                                        for i in range(len(values)):
                                                            if values[i] == '' and cont_values[i] != '':
                                                                values[i] = cont_values[i]
                                                        has_empty = any(val == '' for val in values)
                                                        k += 1
                                                    else:
                                                        break  
                                                processed_lines.append(values)
                                            else:
                                                # If current line is <CONT>, just update the last_values and skip
                                                for i, val in enumerate(values):
                                                    if val:
                                                        last_values[i] = val
                                            j += 1 
                                    frames_data[frame_name] = pd.DataFrame(processed_lines, columns=cleaned_columns)
  

                        project= frames_data.get('PROJ')
                        BHs = frames_data.get('HOLE')   
                        if BHs is not None and project is not None and not BHs.empty:
                            first_row0 = project.iloc[0]
                            project_id= first_row0['PROJ_ID']
                            project_name= first_row0['PROJ_NAME']
                            #print(project_name)
                            date= first_row0['PROJ_DATE']
                            if (date.strip()):
                                project_date= datetime.strptime(date, "%d/%m/%Y").date()
                            else:
                                project_date= None
                            if ('HOLE_LOCX' in BHs.columns and 'HOLE_LOCY' in BHs.columns and 'HOLE_LOCZ' in BHs.columns):
                                BHs= BHs.rename(columns={'HOLE_ID': 'PointID', 'HOLE_LOCY': 'North', 'HOLE_LOCX': 'East', 'HOLE_LOCZ':'Elevation' })
                            else:
                                BHs=BHs.rename(columns={'HOLE_ID': 'PointID', 'HOLE_NATN': 'North', 'HOLE_NATE': 'East', 'HOLE_GL':'Elevation' })
                            BHs = BHs[['PointID', 'East', 'North', 'Elevation']]
                            BHs = BHs.dropna(subset=['PointID','East', 'North'])
                            boreholes = BHs.iloc[:, 0].tolist()
                            first_row = BHs.iloc[0]
                            project_East = float(first_row['East'])
                            project_North = float(first_row['North'])
                            new_project= Project(name= project_name, project_id= project_id, date=project_date, East= project_East, North= project_North, geom= from_shape(Point(transform(proj_in, proj_out, project_East, project_North))))
                            db.add(new_project)
                            db.commit()
                            db.refresh(new_project)
                            for _, row in BHs.iterrows():
                                pointID= row['PointID']
                                Elevation = row['Elevation']
                                East= float(row['East'])
                                North= float(row['North'])
                                X3857, Y3857 = transform(proj_in, proj_out, East, North)  
                                point = Point(X3857, Y3857)
                                geom = from_shape(point)
                                new_entry = BH(
                                pointID=pointID,
                                project_name= project_name,
                                Elevation= Elevation,
                                East=East,
                                North=North,
                                geom=geom,
                            )
                                db.add(new_entry)

                            db.commit()

                        GEOLs = frames_data.get('GEOL')
                        if  GEOLs is not None and not GEOLs.empty:
                            GEOLs= GEOLs[['HOLE_ID', 'GEOL_TOP', 'GEOL_BASE', 'GEOL_LEG']]
                            GEOLs['GEOL_LEG'] = GEOLs['GEOL_LEG'].replace(result_dict)
                            GEOLs.rename(columns={'HOLE_ID': 'PointID', 'GEOL_TOP': 'Depth','GEOL_LEG': 'GEOL_DESC'}, inplace=True)
                            GEOLs.dropna(how='any', inplace=True)



                        COREs = frames_data.get('CORE')
                        if  COREs is not None and not COREs.empty:
                            COREs= COREs[['HOLE_ID', 'CORE_TOP', 'CORE_PREC', 'CORE_SREC', 'CORE_RQD']]
                            COREs.rename(columns={'HOLE_ID': 'PointID', 'CORE_TOP': 'Depth'}, inplace=True)
                            COREs.dropna(how='any', inplace=True)


                        ISTPs = frames_data.get('ISPT') 
                        if  ISTPs is not None and not ISTPs.empty:
                            if 'ISPT_REP' in ISTPs.columns and ISTPs['ISPT_REP'][0] != '':
                           #ISTPs= ISTPs[['HOLE_ID', 'ISPT_TOP', 'ISPT_NVAL', 'ISPT_REP']]
                               ISTPs['ISPT_NVAL'] = ISTPs['ISPT_REP']
                            ISTPs= ISTPs[['HOLE_ID', 'ISPT_TOP', 'ISPT_NVAL']]
                            ISTPs.rename(columns={'HOLE_ID': 'PointID', 'ISPT_TOP': 'Depth','ISPT_NVAL': 'ISPT_REP'} , inplace=True)
                            ISTPs= ISTPs.dropna(subset=['ISPT_REP'])
                        UCSs = None
                    

                    
                    if boreholes is not None and GEOLs is not None and not GEOLs.empty:
                        for _, row in GEOLs.iterrows():
                            pointID= row['PointID']
                            if (pointID in boreholes):
                               if (filename.endswith('.xls') or filename.endswith('.xlsx') or filename.endswith('.xlsm')):
                                    if (isinstance(row['GEOL_LEG'], (int))):
                                        if (len(row['GEOL_DESC'].split(',')) > 1): #if geol is a long text, we take the 1st upper word
                                            match = re.search(r'\b[A-Z]{2,}\b', row['GEOL_DESC'])
                                            if match:
                                                geol_desc= match.group(0)
                                            else:
                                                geol_desc = row['GEOL_DESC']
                                        else:
                                            geol_desc = row['GEOL_DESC']

                                    else:
                                        geol_desc = row['GEOL_LEG']
                               else:
                                   geol_desc = row['GEOL_DESC']
                               depthFrom= row['Depth']
                               depthTo = row['GEOL_BASE']
                               new_entry= geol(pointID= pointID, project_name=project_name, depth_from=depthFrom, depth_to= depthTo, geol_value=geol_desc)
                               db.add(new_entry)
                        db.commit()
                    if boreholes is not None and ISTPs is not None and not ISTPs.empty:
                        for _, row in ISTPs.iterrows():
                            pointID= row['PointID']
                            if (pointID in boreholes):
                                depth= row['Depth']
                                if ('/' in str(row['ISPT_REP'])):
                                    istp_value = str(row['ISPT_REP']).split('/')[0]
                                elif ('>' in str(row['ISPT_REP'])):
                                    istp_value = str(row['ISPT_REP']).split('>')[1]
                                elif ('<' in str(row['ISPT_REP'])):
                                    istp_value = str(row['ISPT_REP']).split('<')[1]
                                else:  
                                    istp_value = str(row['ISPT_REP'])
                                if(istp_value.isdigit()):
                                    new_entry= bhparams(name= 'ISPT', pointID= pointID, project_name=project_name, depth=depth, value=istp_value)
                                    db.add(new_entry)
                        db.commit()
                    if boreholes is not None and COREs is not None and not COREs.empty:
                        for _, row in COREs.iterrows():
                            pointID= row['PointID']
                            if (pointID in boreholes):
                                #print(pointID, 'yes core pointid is in boreholes')
                                depth= row['Depth']
                                #core_bot = row['CORE_BOT']
                                core_prec= row['CORE_PREC']
                                core_srec= row['CORE_SREC']
                                core_rqd= row['CORE_RQD']
                                if(filename.endswith('.ags')):
                                    if (core_prec.isdigit()):
                                        new_entry1= bhparams(name= 'CORE_PREC', pointID= pointID, project_name=project_name, depth=depth, value=core_prec)
                                        db.add(new_entry1)
                                    if (core_srec.isdigit()):
                                        new_entry2= bhparams(name= 'CORE_SREC', pointID= pointID, project_name=project_name, depth=depth, value=core_srec)
                                        db.add(new_entry2)
                                    if (core_rqd.isdigit()):
                                        new_entry3= bhparams(name= 'CORE_RQD', pointID= pointID, project_name=project_name, depth=depth, value=core_rqd)
                                        db.add(new_entry3)
                                #print(core_prec.isdigit())
                                #print(type(core_prec))
                                #print(isinstance(core_srec, (float)) or isinstance(core_srec, (int)))
                                else: 
                                    if (isinstance(core_prec, (float)) or isinstance(core_prec, (int))):
                                        new_entry1= bhparams(name= 'CORE_PREC', pointID= pointID, project_name=project_name, depth=depth, value=core_prec)
                                        db.add(new_entry1)
                                    if (isinstance(core_srec, (float)) or isinstance(core_srec, (int))):
                                        new_entry2= bhparams(name= 'CORE_SREC', pointID= pointID, project_name=project_name, depth=depth, value=core_srec)
                                        db.add(new_entry2)
                                    if (isinstance(core_rqd, (float)) or isinstance(core_rqd, (int))):
                                        new_entry3= bhparams(name= 'CORE_RQD', pointID= pointID, project_name=project_name, depth=depth, value=core_rqd)
                                        db.add(new_entry3)
                        db.commit()
                    if boreholes is not None and UCSs is not None and not UCSs.empty:  
                       for _, row in UCSs.iterrows():
                        pointID= row['PointID']
                        if (pointID in boreholes):
                            depth= row['Depth']
                            strength = row['Strength']
                            samp_ref= row['SAMP_REF']
                            new_entry= bhparams(samp_ref= samp_ref, name= 'UCS', pointID= pointID, project_name=project_name, depth=depth, value=strength)
                            db.add(new_entry)
                       db.commit()

            except Exception as e:
                traceback.print_exc()
                print ('An error is detected:', e)

    return {'message': 'Project created.'}, 200
            


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
    
    
    db.query(geol).filter(geol.project_name == project_name).delete()
    db.query(bhparams).filter(bhparams.project_name == project_name).delete()
    db.query(BH).filter(BH.project_name == project_name).delete()
    db.delete(project)
    db.commit()
    return {"message": f"Project {project_name} and related data deleted successfully"}


@app.get("/users")
def getUsers(Authorization: Annotated[str | None, Header()] = None, db: Session = Depends(get_db)):
    print(Authorization)
    try:
        payload = jwt.decode(Authorization, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload["user"])
        users= db.query(User).all()
        data=[]
        for bh in users:
            data.append({'name': bh.username, 'role': bh.role, 'status': bh.status})
        return {'data': data}
    except JWTError:
        return {'error': 'invalid token'}, 401
         
#admin updates role, status of user
@app.put("/users/{username}/modify")
def modify_user(username: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    updated_data = user_update.dict(exclude_unset=True)
    print(updated_data)
    for field, value in updated_data.items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return {'message': 'User modified.'}, 200


#user updates password, phone number etc
@app.put("/users/{username}/update")
def modify_user(username: str, user_update: UserUpdate2, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    updated_data = user_update.dict(exclude_unset=True)
    print(updated_data)
    for field, value in updated_data.items():
        if (field == 'password'):
           print(value)
           value= pwd_context.hash(value)
           print(value)
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


@app.get("/data/{project_name}")
def getBHs(project_name: str, db: Session = Depends(get_db)):
    BHs= db.query(BH).filter(BH.project_name==project_name).all()
    print(BHs)
    data= []
    for bh in BHs:
        geometry = wkb.loads(bytes(bh.geom.data))
        data.append({'name': bh.pointID, 'x': geometry.x, 'y': geometry.y})
    return {'data': data}


@app.get("/params")
def getData(project: str = Query(...), bhh: str = Query(...), parameter: str = Query(...), db: Session = Depends(get_db)): 
    print(project, bhh, parameter)
    data= []
    bh= db.query(BH).filter(BH.pointID== bhh, BH.project_name == project).first()
    print('hoooooo', bh.pointID)
    values = db.query(bhparams).filter(bhparams.project_name == project, bhparams.pointID == bhh, bhparams.name == parameter).all()
    for v in values:
        data.append({
                    'elev': bh.Elevation - float(v.depth),
                    'value': v.value})
    return {'data': data}
     
@app.get("/geol/{project_name}")
def getGeol(project_name: str, db: Session = Depends(get_db)):
    geols = db.query(geol).filter(geol.project_name == project_name).all()
    data = []
    
    for v in geols: 
        bh = db.query(BH).filter(BH.pointID == v.pointID, BH.project_name == project_name).first()
        if not bh or pd.isna(bh.Elevation):
            continue
        geometry = wkb.loads(bytes(bh.geom.data))
        if pd.isna(geometry.y) or pd.isna(geometry.x):
            continue
        val = v.geol_value.lower()
        data.append({
            'name': bh.pointID,
            'x': geometry.x,
            'y': geometry.y,
            'Elev': bh.Elevation,
            'depthFrom': v.depth_from,
            'depthTo': v.depth_to,
            'geol_desc': val,
        })
    return {'data': data}

@app.get("/interpo/{project_name}")
def getInterpo(project_name: str, db: Session = Depends(get_db)):
    geols = db.query(geol).filter(geol.project_name == project_name).all()
    unique_geol_desc = set()
    all_points = []
    all_values = []
    fig = go.Figure()
    num= db.query(BH).filter(BH.project_name == project_name).count()
    print(num)
    if (num < 2):
        raise ValueError("At least 2 boreholes are required to compute the interpolation")
  
    for v in geols: 
        bh = db.query(BH).filter(BH.pointID == v.pointID, BH.project_name == project_name).first()
        if not bh or pd.isna(bh.Elevation):
            continue
        geometry = wkb.loads(bytes(bh.geom.data))
        val = v.geol_value.lower()
        unique_geol_desc.add(val)
        if pd.isna(geometry.y) or pd.isna(geometry.x):
            continue

        z_start = bh.Elevation - v.depth_from
        z_end = bh.Elevation - v.depth_to
        z_values = np.linspace(z_start, z_end, 20)
        points = np.array([[geometry.x, geometry.y, z] for z in z_values])
        all_points.extend(points)
        all_values.extend([val] * len(points))

    all_points = np.array(all_points)
    all_values = np.array(all_values)

    # Convert geological descriptions to numerical values
    geol_desc_to_num = {desc: i for i, desc in enumerate(unique_geol_desc)}
    num_to_geol_desc = {i: desc for desc, i in geol_desc_to_num.items()}
    print(num_to_geol_desc)
    all_values_numeric = np.array([geol_desc_to_num[val] for val in all_values])

    # Compute convex hull
    #hull = ConvexHull(all_points)

    # Extract the vertices of the convex hull
    #hull_points = all_points[hull.vertices]

    # Create a Delaunay triangulation within the convex hull to generate grid points
    #tri = Delaunay(hull_points)

    # Find min and max coordinates
    #x_min, x_max = np.min(hull_points[:, 0]), np.max(hull_points[:, 0])
    #y_min, y_max = np.min(hull_points[:, 1]), np.max(hull_points[:, 1])
    #z_min, z_max = np.min(hull_points[:, 2]), np.max(hull_points[:, 2])



    x_min, x_max = np.min(all_points[:, 0]), np.max(all_points[:, 0])
    y_min, y_max = np.min(all_points[:, 1]), np.max(all_points[:, 1])
    z_min, z_max = np.min(all_points[:, 2]), np.max(all_points[:, 2])
    # Generate points within the convex hull
    grid_points = np.array([[x, y, z] for x in np.linspace(x_min, x_max, 60)
                            for y in np.linspace(y_min, y_max, 60)
                            for z in np.linspace(z_min, z_max, 30)
                            #if tri.find_simplex([x, y, z]) >= 0
                            ])
    # Interpolate values across the grid
    interpolator = LinearNDInterpolator(all_points, all_values_numeric)
    interpolated_values = interpolator(grid_points)

    # Remove NaN values from interpolated values and their corresponding grid points
    valid_indices = ~np.isnan(interpolated_values)
    interpolated_values = interpolated_values[valid_indices]
    grid_points = grid_points[valid_indices]

    # Map numerical interpolated values back to categories
    interpolated_values = [num_to_geol_desc[int(round(val))] for val in interpolated_values]
    unique_values = list(set(interpolated_values))
    interpolated_colors={}
    for cat in unique_values:
        interpolated_colors[cat] = get_random_color()

    data= go.Scatter3d(
        x=grid_points[:, 0],
        y=grid_points[:, 1],
        z=grid_points[:, 2],
        mode='markers',
        marker=dict(
            symbol= 'square',
            color=[interpolated_colors[category] for category in interpolated_values],
            size=10,
        ),
        name='Interpolated Values',
        showlegend=False
    )  
    fig.add_trace(data)

    for category, color in interpolated_colors.items():
        legend_entry = go.Scatter3d(
            x=[None],
            y=[None],
            z=[None],
            mode='markers',
            marker=dict(
                size=10,
                symbol= 'square',
                color=color,
                opacity=1
            ),
            name=category,
            showlegend= True
        )
        fig.add_trace(legend_entry)

    fig.update_layout(
    scene=dict(
        xaxis=dict(title='X', showticklabels=False),
        yaxis=dict(title='Y', showticklabels=False),
        zaxis=dict(title='Z'),
        aspectratio=dict(x=2, y=1, z=1)
    ),
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0
    ),
    width=930,
    height=500,
    showlegend=True,
    #title='3D Geological Interpolation'
)



    return {'fig': json.loads(fig.to_json())}

def get_random_color():
    r = random.randint(210, 255)  # Red: 210-255
    g = random.randint(180, 230)  # Green: 180-230
    b = random.randint(150, 200)  # Blue: 150-200
    return f'rgb({r},{g},{b})'


