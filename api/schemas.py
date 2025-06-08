# api/schemas.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, timezone

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserInDB(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr
    hashed_password: str
    
    class Config:
        populate_by_name = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ImageAnalysisResult(BaseModel):
    prediction: str
    confidence: float
    is_deepfake: bool

class AnalysisRecord(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    original_filename: str
    storage_url: str
    result: ImageAnalysisResult 
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }