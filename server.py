from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from uuid import uuid4
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# FastAPI uygulaması
app = FastAPI()

# CORS middleware ayarı
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MySQL veritabanı bağlantısı ayarı
DATABASE_URL = "mysql+pymysql://root:123456@localhost/blogdb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Veritabanı modelleri
class UserDB(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    surname = Column(String(100))
    email = Column(String(100), unique=True)
    password = Column(String(100))
    city = Column(String(100), nullable=True)

class BlogDB(Base):
    __tablename__ = 'blogs'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    content = Column(Text)
    author = Column(String(100))
    image = Column(String(255), nullable=True)
    created_at = Column(String(100), nullable=True)

# Veritabanı tablolarını oluşturma
Base.metadata.create_all(bind=engine)

# Dependency - veritabanı oturumunu alır
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modeller
class User(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str
    city: Optional[str] = None

class LoginRequest(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str

class Blog(BaseModel):
    title: str
    content: str
    author: str
    image: Optional[str] = None
    created_at: Optional[str] = None

# Kullanıcı kaydı
@app.post("/register/")
async def register_user(user: User, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = UserDB(**user.dict())
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully", "user": user.dict()}

# Kullanıcı girişi
@app.post("/login/")
async def login_user(login_request: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(
        UserDB.name == login_request.name,
        UserDB.surname == login_request.surname,
        UserDB.email == login_request.email,
        UserDB.password == login_request.password
    ).first()
    if db_user:
        session_id = str(uuid4())
        return {"success": True, "message": "Login successful", "session_id": session_id}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Kullanıcı çıkışı
@app.post("/logout/")
async def logout_user(request: Request):
    authorization: str = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        session_id = authorization.split(" ")[1]
        # Gerekirse session_id ile oturum sonlandırma işlemi yapılabilir.
        return {"message": "Logout successful"}
    raise HTTPException(status_code=401, detail="Invalid session")

# Tüm kullanıcıları alma
@app.get("/users/")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(UserDB).all()
    return {"users": [user.__dict__ for user in users]}

# Blog oluşturma
@app.post("/blogs/")
async def create_blog(blog: Blog, db: Session = Depends(get_db)):
    new_blog = BlogDB(**blog.dict())
    db.add(new_blog)
    db.commit()
    return {"message": "Blog created successfully", "blog": blog.dict()}

# Tüm blogları alma
@app.get("/blogs/")
async def get_blogs(db: Session = Depends(get_db)):
    blogs = db.query(BlogDB).all()
    return {"blogs": [blog.__dict__ for blog in blogs]}

# Blog detaylarını alma
@app.get("/blogs/{id}")
async def get_blog(id: int, db: Session = Depends(get_db)):
    blog = db.query(BlogDB).filter(BlogDB.id == id).first()
    if blog:
        return {"blog": blog.__dict__}
    raise HTTPException(status_code=404, detail="Blog not found")

# Blog güncelleme
@app.put("/blogs/{id}")
async def update_blog(id: int, updated_blog: Blog, db: Session = Depends(get_db)):
    blog = db.query(BlogDB).filter(BlogDB.id == id).first()
    if blog:
        for key, value in updated_blog.dict().items():
            setattr(blog, key, value)
        db.commit()
        return {"message": "Blog updated successfully", "blog": blog.__dict__}
    raise HTTPException(status_code=404, detail="Blog not found")

# Blog silme
@app.delete("/blogs/{id}")
async def delete_blog(id: int, db: Session = Depends(get_db)):
    blog = db.query(BlogDB).filter(BlogDB.id == id).first()
    if blog:
        db.delete(blog)
        db.commit()
        return {"message": "Blog deleted successfully"}
    raise HTTPException(status_code=404, detail="Blog not found")

# Öne çıkan bloglar
@app.get("/featured-blogs/")
async def get_featured_blogs(db: Session = Depends(get_db)):
    blogs = db.query(BlogDB).all()
    if len(blogs) < 3:
        raise HTTPException(status_code=404, detail="Not enough blogs to display")
    from random import sample
    featured_blogs = sample(blogs, 3)
    return {"featured_blogs": [blog.__dict__ for blog in featured_blogs]}
