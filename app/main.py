from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import session# Database connection string
from fastapi import FastAPI, Depends , HTTPException
from pydantic import BaseModel
from typing import List , Optional

app = FastAPI()
DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()   

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None 

@app.post("/users/",response_model=UserResponse)
def create_user(user: UserCreate, db: session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#get operation to retrieve all users

@app.get("/users/", response_model=list[UserResponse])
def read_users(skip: int = 0, limit: int = 10, name: str ="", db: session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

#get operation to retrieve a user by ID
from fastapi import HTTPException

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")  
    return db_user


#put operation to update a user by ID
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.name is not None:
        db_user.name = user.name
    if user.email is not None:
        db_user.email = user.email
    
    db.commit()
    db.refresh(db_user)
    return db_user

#delete operation to delete a user by ID
@app.delete("/users/{user_id}", response_model=UserResponse)
def delete_user(user_id: int, db: session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return db_user