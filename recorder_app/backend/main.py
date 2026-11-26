from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pathlib import Path
import sqlite3, hashlib, secrets, time, os

BASE=Path(__file__).parent; STORE=BASE/'storage'; STORE.mkdir(exist_ok=True)
DB=BASE/'records.db'; app=FastAPI(title='CaptureCloud API')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
security=HTTPBearer(auto_error=False); tokens={}
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
with db() as c:
 c.execute('CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY, name TEXT, filename TEXT, size INTEGER, created REAL)')
 c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
 # demo credentials, change before production
 if not c.execute('SELECT 1 FROM users').fetchone(): c.execute('INSERT INTO users VALUES (?,?)',('admin',hashlib.sha256('ChangeMe123!'.encode()).hexdigest()))
def auth(creds: HTTPAuthorizationCredentials=Depends(security)):
 if not creds or creds.credentials not in tokens: raise HTTPException(401,'Please sign in')
 return tokens[creds.credentials]
@app.post('/api/login')
def login(data:dict):
 username=data.get('username',''); password=data.get('password','')
 with db() as c: row=c.execute('SELECT password FROM users WHERE username=?',(username,)).fetchone()
 if not row or row['password']!=hashlib.sha256(password.encode()).hexdigest(): raise HTTPException(401,'Invalid username or password')
 token=secrets.token_urlsafe(32); tokens[token]=username; return {'token':token,'username':username}
@app.get('/api/ping')
def ping(): return {'ok':True,'time':time.time()}
@app.get('/api/videos')
def list_videos(user=Depends(auth)):
 with db() as c: rows=c.execute('SELECT id,name,size,created FROM videos ORDER BY created DESC').fetchall()
 return [dict(r) for r in rows]
@app.post('/api/videos')
def upload_video(file:UploadFile=File(...),name:str=Form('Recording'),user=Depends(auth)):
 ext=Path(file.filename or 'video.webm').suffix or '.webm'; filename=f'{secrets.token_hex(16)}{ext}'
 path=STORE/filename; size=0
 with path.open('wb') as f:
  while chunk:=file.file.read(1024*1024): f.write(chunk); size+=len(chunk)
 with db() as c: cur=c.execute('INSERT INTO videos(name,filename,size,created) VALUES(?,?,?,?)',(name,filename,size,time.time())); vid=cur.lastrowid
 return {'id':vid,'name':name,'size':size}
@app.get('/api/videos/{vid}/download')
def download(vid:int,user=Depends(auth)):
 with db() as c: row=c.execute('SELECT * FROM videos WHERE id=?',(vid,)).fetchone()
 if not row: raise HTTPException(404,'Video not found')
 path=STORE/row['filename']
 if not path.exists(): raise HTTPException(404,'File missing')
 return FileResponse(path,media_type='application/octet-stream',filename=row['name']+path.suffix)
@app.delete('/api/videos/{vid}')
def delete(vid:int,user=Depends(auth)):
 with db() as c: row=c.execute('SELECT filename FROM videos WHERE id=?',(vid,)).fetchone()
 if not row: raise HTTPException(404,'Video not found')
 try: (STORE/row['filename']).unlink()
 except FileNotFoundError: pass
 with db() as c: c.execute('DELETE FROM videos WHERE id=?',(vid,))
 return {'ok':True}
