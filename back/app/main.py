import io
import re
import traceback
from typing import Annotated, List, Optional
from fastapi import FastAPI, Depends, File, HTTPException, Header, Request, UploadFile, status, Query
import pandas as pd
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
                    filename = bh_file.filename.lower()
                    proj_in = Proj(init='epsg:32640') #utm zone 40 northing/easting
                    proj_out = Proj(init='epsg:4326') #wgs84 long/lat
                    if filename.endswith('.xls') or filename.endswith('.xlsx') or filename.endswith('.xlsm'):
                        ff=  await bh_file.read()
                        BHs = pd.read_excel(io.BytesIO(ff), sheet_name='POINT') 
                        ISTPs = pd.read_excel(io.BytesIO(ff), sheet_name='ISPT') 
                        COREs = pd.read_excel(io.BytesIO(ff), sheet_name='CORE') 
                        UCSs = pd.read_excel(io.BytesIO(ff), sheet_name='UNCONF COMPR') 
                        GEOLs = pd.read_excel(io.BytesIO(ff), sheet_name='GEOL')
                        filename = bh_file.filename.lower()
                        project_name= filename.split('.')[0]
                        print(project_name)
                        first_row = BHs.iloc[0]
                        project_East = float(first_row['East'])
                        project_North = float(first_row['North'])
                        new_project= Project(name= project_name, project_id= project_name, East= project_East, North= project_North, geom= from_shape(Point(transform(proj_in, proj_out, project_East, project_North))))
                        db.add(new_project)
                        db.commit()
                        if BHs is not None and not BHs.empty:
                            for _, row in BHs.iterrows():
                                pointID= row['PointID']
                                report_id= row['Report']
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
                        first_row0 = project.iloc[0]
                        project_id= first_row0['PROJ_ID']
                        project_name= first_row0['PROJ_NAME']
                        print(project_name)
                        date= first_row0['PROJ_DATE']
                        project_date= datetime.strptime(date, "%d/%m/%Y").date()
                        BHs = frames_data.get('HOLE')   
                        if BHs is not None and not BHs.empty:
                            if ('HOLE_LOCX' in BHs.columns and 'HOLE_LOCY' in BHs.columns and 'HOLE_LOCZ' in BHs.columns):
                                BHs= BHs.rename(columns={'HOLE_ID': 'PointID', 'HOLE_LOCY': 'North', 'HOLE_LOCX': 'East', 'HOLE_LOCZ':'Elevation' })
                            else:
                                BHs=BHs.rename(columns={'HOLE_ID': 'PointID', 'HOLE_NATN': 'North', 'HOLE_NATE': 'East', 'HOLE_GL':'Elevation' })
                            BHs = BHs[['PointID', 'East', 'North', 'Elevation']]
                            BHs = BHs.dropna(subset=['East', 'North'])
                            
                        first_row = BHs.iloc[0]
                        project_East = float(first_row['East'])
                        project_North = float(first_row['North'])
                        new_project= Project(name= project_name, project_id= project_id, date=project_date, East= project_East, North= project_North, geom= from_shape(Point(transform(proj_in, proj_out, project_East, project_North))))
                        db.add(new_project)
                        db.commit()
                        if BHs is not None and not BHs.empty:
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


                        GEOLs = frames_data.get('GEOL')
                        if GEOLs is not None and not GEOLs.empty:
                            GEOLs= GEOLs[['HOLE_ID', 'GEOL_TOP', 'GEOL_BASE', 'GEOL_LEG']]
                            GEOLs['GEOL_LEG'] = GEOLs['GEOL_LEG'].replace(result_dict)
                            GEOLs.rename(columns={'HOLE_ID': 'PointID', 'GEOL_TOP': 'Depth','GEOL_LEG': 'GEOL_DESC'}, inplace=True)
                            GEOLs.dropna(how='any', inplace=True)



                        COREs = frames_data.get('CORE')
                        if COREs is not None and not COREs.empty:
                            COREs= COREs[['HOLE_ID', 'CORE_TOP', 'CORE_BOT', 'CORE_PREC', 'CORE_SREC', 'CORE_RQD']]
                            COREs.rename(columns={'HOLE_ID': 'PointID', 'CORE_TOP': 'Depth'}, inplace=True)
                            COREs.dropna(how='any', inplace=True)


                        ISTPs = frames_data.get('ISPT') 
                        if ISTPs is not None and not ISTPs.empty:
                            if 'ISPT_REP' in ISTPs.columns and ISTPs['ISPT_REP'][0] != '':
                           #ISTPs= ISTPs[['HOLE_ID', 'ISPT_TOP', 'ISPT_NVAL', 'ISPT_REP']]
                               ISTPs['ISPT_NVAL'] = ISTPs['ISPT_REP']
                            ISTPs= ISTPs[['HOLE_ID', 'ISPT_TOP', 'ISPT_NVAL']]
                            ISTPs.rename(columns={'HOLE_ID': 'PointID', 'ISPT_TOP': 'Depth','ISPT_NVAL': 'ISPT_REP'} , inplace=True)
                            ISTPs= ISTPs.dropna(subset=['ISPT_REP'])
                        UCSs = None
                    


                    if GEOLs is not None and not GEOLs.empty:
                        for _, row in GEOLs.iterrows():
                            pointID= row['PointID']
                            geol_desc = row['GEOL_DESC']
                            depthFrom= row['Depth']
                            depthTo = row['GEOL_BASE']
                            new_entry= geol(pointID= pointID, project_name=project_name, depth_from=depthFrom, depth_to= depthTo, geol_value=geol_desc)
                            db.add(new_entry)
                        
                    #do the same for core, istp, ucs
                    if ISTPs is not None and not ISTPs.empty:
                        for _, row in ISTPs.iterrows():
                            pointID= row['PointID']
                            depth= row['Depth']
                            if ('/' in str(row['ISPT_REP'])):
                                istp_value = str(row['ISPT_REP']).split('/')[0]
                            elif ('>' in str(row['ISPT_REP'])):
                                istp_value = str(row['ISPT_REP']).split('>')[1]
                            elif ('<' in str(row['ISPT_REP'])):
                                istp_value = str(row['ISPT_REP']).split('<')[1]
                            else:
                                istp_value = str(row['ISPT_REP'])
                            new_entry= bhparams(name= 'ISPT', pointID= pointID, project_name=project_name, depth=depth, value=istp_value)
                            db.add(new_entry)
                        
                    if COREs is not None and not COREs.empty:
                        for _, row in COREs.iterrows():
                            pointID= row['PointID']
                            depth= row['Depth']
                            #core_bot = row['CORE_BOT']
                            core_prec= row['CORE_PREC']
                            core_srec= row['CORE_SREC']
                            core_rqd= row['CORE_RQD']
                            new_entry1= bhparams(name= 'CORE_PREC', pointID= pointID, project_name=project_name, depth=depth, value=core_prec)
                            db.add(new_entry1)
                            new_entry2= bhparams(name= 'CORE_SREC', pointID= pointID, project_name=project_name, depth=depth, value=core_srec)
                            db.add(new_entry2)
                            new_entry3= bhparams(name= 'CORE_RQD', pointID= pointID, project_name=project_name, depth=depth, value=core_rqd)
                            db.add(new_entry3)
                        
                    if UCSs is not None and not UCSs.empty:  
                       for _, row in UCSs.iterrows():
                        pointID= row['PointID']
                        depth= row['Depth']
                        strength = row['Strength']
                        new_entry= bhparams(name= 'UCS', pointID= pointID, project_name=project_name, depth=depth, value=strength)
                        db.add(new_entry)
                    
                    db.commit()
            except Exception as e:
                traceback.print_exc()
                print ('errrrrrrrrrrror', e)

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
    geols= db.query(geol).filter(geol.project_name == project_name).all()
    data=[]
    for v in geols: 
        bh= db.query(BH).filter(BH.pointID== v.pointID, BH.project_name== project_name).first()
        geometry = wkb.loads(bytes(bh.geom.data))
        data.append({
                'name': bh.pointID,
                'x': geometry.x,
                'y': geometry.y,
                'Elev': bh.Elevation,
                'depthFrom': v.depth_from,
                'depthTo': v.depth_to,
                'geol_desc': v.geol_value.lower(),
            })
    return {'data': data}