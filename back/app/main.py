import io
import random
import re
import traceback
from typing import Annotated, List, Optional
from fastapi import FastAPI, Depends, File, HTTPException, Header, Request, UploadFile, status, Query
import numpy as np
import pandas as pd
import json
from sqlalchemy import and_, exists, or_
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models, schemas
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from .schemas import UserCreate, UserUpdate, UserUpdate2
from .models import Borehole, Box, Cpt, Meas, Project, User, Bh_params, Geol
#, Project, Box, Cpt,  Meas
from fastapi.middleware.cors import CORSMiddleware
from shapely import wkb
from shapely.geometry import Point
from pyproj import Proj, transform
from geoalchemy2.shape import from_shape
from scipy.interpolate import griddata, LinearNDInterpolator
import plotly.graph_objects as go
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from sqlalchemy.orm import aliased
from .geo_codes import geo 
SECRET_KEY = "nmdcsecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480 #8H
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

origins = [
    "http://localhost:4200",
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
        new_user = User(username=username, password=hashed_password, role='admin', status='verified') 
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
        return {"access_token": access_token, "role": user.role, "username": user.username}
    return {'message': 'Incorrect username or password or unverified status.'}, 404


@app.post("/bh")
async def addBHs(Files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    for bh_file in Files:
        if bh_file:
            try:    
                    bhs= []
                    bhsdict= {}
                    boreholes= None
                    filename = bh_file.filename.lower()
                    fl= bh_file.filename
                    print(filename)
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
                            if ISTPs['ISPT_REP'].isna().all() and not ISTPs['ISPT_TYPE'].isna().all():
                               ISTPs['ISPT_REP'] = ISTPs['ISPT_TYPE']
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
                           GEOLs = GEOLs.dropna(subset=['PointID', 'Depth', 'GEOL_BASE', 'GEOL_LEG'])
                        

                        if BHs is not None and not BHs.empty:
                            boreholes = BHs.iloc[:, 0].tolist()
                            project_name= filename[: filename.index('.xls')]
                            for _, row in BHs.iterrows():
                                pointID= row['PointID']
                                if ('Report' in BHs.columns):
                                    report_id= str(row['Report'])
                                else:
                                    report_id= ''
                                Elevation = row['Elevation']
                                East= float(row['East'])
                                North= float(row['North'])
                                X3857, Y3857 = transform(proj_in, proj_out, East, North)  
                                point = Point(X3857, Y3857)
                                geom = from_shape(point)
                                new_entry = Borehole(
                                pointID=pointID,
                                project= project_name,
                                report_id= report_id,
                                Elevation= Elevation,
                                East=East,
                                North=North,
                                filename= fl,
                                geom=geom)
                                db.add(new_entry)
                                bhs.append(new_entry)
                            db.commit()
                            for bh in bhs: 
                                bhsdict[bh.pointID]= bh.id
                            #print(bhsdict)
                    elif filename.endswith('.ags'):
                        frames_data = {}
                        ags_content0 = await bh_file.read()
                        ags_content= ags_content0.decode('utf-8')
                        frame_pattern = re.compile(r'"\*\*(.*?)\"', re.MULTILINE)
                        matches = re.finditer(frame_pattern, ags_content)
                        frames_to_extract= ['PROJ', 'HOLE', 'GEOL', 'CORE', 'ISPT']
                        matches = list(frame_pattern.finditer(ags_content))
                        for i, match in enumerate(matches):
                            frame_name = match.group(1).strip()
                            if frame_name in frames_to_extract:
                               start_index = match.end()
                               end_index = matches[i + 1].start() if i + 1 < len(matches) else len(ags_content)
                               # Slice the content for the current frame
                               frame_content = ags_content[start_index:end_index]
                               columns_str= frame_content[: frame_content.find('"<UNITS>"')]
                                #print(columns_str)
                               all_columns= columns_str.strip('"').split(',')
                               cleaned_columns = [col.strip('\r\n"*') for col in all_columns]
                                #print(cleaned_columns)                    
                                # Find data for the current frame
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
                            project_name= first_row0['PROJ_NAME']
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

                            for _, row in BHs.iterrows():
                                pointID= row['PointID']
                                Elevation = row['Elevation']
                                East= float(row['East'])
                                North= float(row['North'])
                                X3857, Y3857 = transform(proj_in, proj_out, East, North)  
                                point = Point(X3857, Y3857)
                                geom = from_shape(point)
                                new_entry = Borehole(
                                pointID=pointID,
                                filename= fl,
                                date= project_date,
                                project= project_name,
                                Elevation= Elevation,
                                East=East,
                                North=North,
                                geom=geom)

                                db.add(new_entry)
                                bhs.append(new_entry)
                            db.commit()
                            for bh in bhs: 
                                bhsdict[bh.pointID]= bh.id
                            print(bhsdict)
                        GEOLs = frames_data.get('GEOL')
                        if  GEOLs is not None and not GEOLs.empty:
                            GEOLs= GEOLs[['HOLE_ID', 'GEOL_TOP', 'GEOL_BASE', 'GEOL_LEG']]
                            #GEOLs['GEOL_LEG'] = GEOLs['GEOL_LEG'].replace(result_dict)
                            GEOLs.rename(columns={'HOLE_ID': 'PointID', 'GEOL_TOP': 'Depth'}, inplace=True)
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
                               if (str(row['GEOL_LEG']) in geo.keys()):
                                   geol_desc = geo[str(row['GEOL_LEG'])]
                               else:
                                   continue
                               depthFrom= row['Depth']
                               depthTo = row['GEOL_BASE']
                               #print(bhsdict[pointID])
                               new_entry= Geol(pointID= pointID, bh_id= bhsdict[pointID], project=project_name, depth_from=depthFrom, depth_to= depthTo, geol_value=geol_desc)
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
                                    new_entry= Bh_params(name= 'ISPT', bh_id= bhsdict[pointID], pointID= pointID, project=project_name, depth=depth, value=istp_value)
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
                                        new_entry1= Bh_params(name= 'CORE_PREC', bh_id= bhsdict[pointID], pointID= pointID, project=project_name, depth=depth, value=core_prec)
                                        db.add(new_entry1)
                                    if (core_srec.isdigit()):
                                        new_entry2= Bh_params(name= 'CORE_SREC', bh_id= bhsdict[pointID], pointID= pointID, project=project_name, depth=depth, value=core_srec)
                                        db.add(new_entry2)
                                    if (core_rqd.isdigit()):
                                        new_entry3= Bh_params(name= 'CORE_RQD', bh_id= bhsdict[pointID], pointID= pointID, project=project_name, depth=depth, value=core_rqd)
                                        db.add(new_entry3)
                                #print(core_prec.isdigit())
                                #print(type(core_prec))
                                #print(isinstance(core_srec, (float)) or isinstance(core_srec, (int)))
                                else: 
                                    if (isinstance(core_prec, (float)) or isinstance(core_prec, (int))):
                                        new_entry1= Bh_params(name= 'CORE_PREC', bh_id= bhsdict[pointID], pointID= pointID, project=project_name, depth=depth, value=core_prec)
                                        db.add(new_entry1)
                                    if (isinstance(core_srec, (float)) or isinstance(core_srec, (int))):
                                        new_entry2= Bh_params(name= 'CORE_SREC', bh_id= bhsdict[pointID], pointID= pointID, project=project_name, depth=depth, value=core_srec)
                                        db.add(new_entry2)
                                    if (isinstance(core_rqd, (float)) or isinstance(core_rqd, (int))):
                                        new_entry3= Bh_params(name= 'CORE_RQD', bh_id= bhsdict[pointID], pointID= pointID, project=project_name, depth=depth, value=core_rqd)
                                        db.add(new_entry3)
                        db.commit()
                    if boreholes is not None and UCSs is not None and not UCSs.empty:  
                       for _, row in UCSs.iterrows():
                        pointID= row['PointID']
                        if (pointID in boreholes):
                            depth= row['Depth']
                            strength = row['Strength']
                            samp_ref= row['SAMP_REF']
                            new_entry= Bh_params(samp_ref= samp_ref, name= 'UCS', bh_id= bhsdict[pointID], pointID= pointID, project=project_name, depth=depth, value=strength)
                            db.add(new_entry)
                       db.commit()

            except Exception as e:
                traceback.print_exc()
                print ('An error is detected:', e)

    return {'message': 'BH created.'}, 200
            

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


@app.get("/bh")
def getBHs(db: Session = Depends(get_db)):
    BHs= db.query(Borehole).all()
    #print(BHs)
    data= []
    for bh in BHs:
        geometry = wkb.loads(bytes(bh.geom.data))
        data.append({'id': bh.id, 'name': bh.pointID, 'x': geometry.x, 'y': geometry.y})
    return {'data': data}


@app.get("/bhparams")
def getData(id: int = Query(...), parameter: str = Query(...), db: Session = Depends(get_db)): 
    print(id, parameter)
    data= []
    bh= db.query(Borehole).filter(Borehole.id == id).first()
    print('hoooooo', bh.pointID)
    para_names= {'SCR':'CORE_PREC', 'TCR':'CORE_SREC', 'RQD':'CORE_RQD', 'SPT': 'ISPT', 'UCS': 'UCS'}
    values = db.query(Bh_params).filter(Bh_params.bh_id == id, Bh_params.name == para_names[parameter]).all()

    for v in values:
        print(v)
        data.append({
                    'elev': bh.Elevation - float(v.depth),
                    'value': v.value})
    print(data)
    return {'data': data}
     
@app.get("/bhgeol")
def getGeol(id: int, db: Session = Depends(get_db)):
    geols = db.query(Geol).filter(Geol.bh_id == id).all()
    data = []
    
    for v in geols: 
        bh = db.query(Borehole).filter(Borehole.id == id).first()
        if not bh or pd.isna(bh.Elevation):
            continue
        geometry = wkb.loads(bytes(bh.geom.data))
        if pd.isna(geometry.y) or pd.isna(geometry.x):
            continue
        data.append({
            'id': bh.id,
            'name': bh.pointID,
            'x': bh.East,
            'y': bh.North,
            'Elev': bh.Elevation,
            'depthFrom': v.depth_from,
            'depthTo': v.depth_to,
            'geol_desc': v.geol_value,
        })
    return {'data': data}

#CPT SECTION
@app.get("/projects")
def getprojects(db: Session = Depends(get_db)):
    projects= db.query(Project).all()
    data= []
    for p in projects:
        data.append({
            'id': p.id, 'name': p.name, 'lat': p.loclat, 'lon': p.loclon
        })
    return {'data': data}

#get only boxes WITH associated CPT data WITH measurements
@app.get("/grid")
def getGrid(id: int, db: Session = Depends(get_db)):
    data= []
    # Aliases for clarity
    CptAlias = aliased(Cpt)
    MeasAlias = aliased(Meas)

# Subquery for EXISTS
    exists_subquery = (
    exists()
    .where(
        CptAlias.box_id == Box.box_name,
        CptAlias.id == MeasAlias.info_id,
        MeasAlias.info_id == CptAlias.id,
        Box.project_id == id
    )
)

# Query with EXISTS filter
    boxes = db.query(Box).filter(exists_subquery).distinct().all()
    for b in boxes:
        geom = to_shape(b.polygon)
        data.append({'id': b.id, 'box_name': b.box_name, 'geom': mapping(geom)})
    return {'data': data}


@app.get("/cptdata")
def getcptdata(id: str, type: str, db: Session = Depends(get_db)):
    print(type)
    if type == 'POST':
        cpts = db.query(Cpt).filter(Cpt.box_id == id, or_(Cpt.type == 'POST', Cpt.type == 'PO')).all()
    elif type == 'PRE and POST':
        cpts = db.query(Cpt).filter(Cpt.box_id == id, or_(Cpt.type == 'POST', Cpt.type == 'PO', Cpt.type == 'PRE')).all()
    else:
        cpts = db.query(Cpt).filter(Cpt.box_id == id, Cpt.type == type).all()

    cpt_data = []
    for cpt in cpts:
        measurements = db.query(Meas).filter(Meas.info_id == cpt.id).all()
        meas_data = []
        for m in measurements:
            meas_data.append({
                'depth': m.depth,
                'fs': m.fs,
                'qc': m.qc
            })

        cpt_data.append({
            'cpt_id': cpt.id,
            'grid_id': cpt.grid_id,
            'box_name': cpt.box_id,
            'type': cpt.type,
            'measurements': meas_data
        })
    #print(cpt_data)
    return {'cpt_data': cpt_data}
