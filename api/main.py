import torch
import os
from datetime import datetime, timezone
import cloudinary
import cloudinary.uploader
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from typing import List

# --- Import từ các module của chúng ta ---
from model import DeepfakeDetector
from utils import transform_image
from database import user_collection, analysis_collection
from security import (
    get_password_hash, verify_password, create_access_token,
    SECRET_KEY, ALGORITHM
)
from schemas import UserCreate, Token, AnalysisRecord, TokenData, ImageAnalysisResult

# --- Cấu hình ---
app = FastAPI(
    title="Deepfake Image Detection Service",
    description="A service to detect deepfakes in images, with user accounts and history.",
    version="3.0-image-only"
)

# Cấu hình Cloudinary từ biến môi trường
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# --- Tải mô hình ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
try:
    deepfake_model = DeepfakeDetector().to(device)
    deepfake_model.load_state_dict(torch.load("140K_resnet50_model.pth", map_location=device))
    deepfake_model.eval()
    print("Deepfake detector model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    deepfake_model = None

# --- Hệ thống xác thực (Authentication) ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await user_collection.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return user


# --- Endpoints cho User và Authentication ---
@app.post("/register", tags=["Authentication"], status_code=201)
async def register_user(user: UserCreate):
    """Registers a new user."""
    existing_user = await user_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = {"email": user.email, "hashed_password": hashed_password}
    await user_collection.insert_one(new_user)
    return {"message": "User created successfully"}

@app.post("/token", response_model=Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Logs in a user and returns a JWT token."""
    user = await user_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}


# --- Endpoints Chính ---

@app.post("/analyze-image/", response_model=ImageAnalysisResult, tags=["Analysis"])
async def analyze_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Analyzes an uploaded image for deepfakes.
    Requires authentication.
    """
    if not deepfake_model:
        raise HTTPException(status_code=503, detail="Model is not available.")

    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a JPEG or PNG image.")

    contents = await file.read()
    
    try:
        upload_result = cloudinary.uploader.upload(contents, resource_type="image")
        storage_url = upload_result.get("secure_url")
        if not storage_url:
            raise HTTPException(status_code=500, detail="Could not upload file to cloud storage.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloud storage error: {e}")

    tensor = transform_image(contents)
    if tensor is None:
        raise HTTPException(status_code=400, detail="Could not process the image. It might be corrupted.")
    tensor = tensor.to(device)
    
    with torch.no_grad():
        output = deepfake_model(tensor)
        confidence_real = output.item()
        if confidence_real > 0.5:
            prediction_label, is_fake, confidence_score = "Real", False, confidence_real
        else:
            prediction_label, is_fake, confidence_score = "Fake", True, 1 - confidence_real

    result_json = {
        "prediction": prediction_label,
        "confidence": round(confidence_score, 4),
        "is_deepfake": is_fake
    }

    analysis_data = {
        "user_id": str(current_user["_id"]),
        "original_filename": file.filename,
        "storage_url": storage_url,
        "result": result_json,
        "created_at": datetime.now(timezone.utc)
    }
    await analysis_collection.insert_one(analysis_data)

    return result_json

@app.get("/history", response_model=List[AnalysisRecord], tags=["User"])
async def get_user_history(current_user: dict = Depends(get_current_user)):
    """Retrieves the analysis history for the current logged-in user."""
    user_id = str(current_user["_id"])
    cursor = analysis_collection.find({"user_id": user_id}).sort("created_at", -1).limit(100)
    
    history = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        history.append(doc)
    
    return history

@app.get("/", tags=["Status"])
def read_root():
    """Root endpoint to check if the API is running."""
    return {"status": "Deepfake Image Detection API is running."}