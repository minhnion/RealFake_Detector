import torch
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import logging
from pydantic import BaseModel

from model import DeepfakeDetector
from utils import transform_image


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Deepfake Detection API",
    description="An API to detect whether an image is real or a deepfake.",
    version="1.0.0"
)

#Tải mô hình 
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")

MODEL_PATH = "140K_resnet50_model.pth"

try:
    model = DeepfakeDetector().to(device)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.eval()  
    logger.info("Model loaded successfully!")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model = None

class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    is_deepfake: bool

@app.post("/predict/", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    if not model:
        raise HTTPException(status_code=500, detail="Model is not loaded. Cannot perform prediction.")

    image_bytes = await file.read()

    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a JPEG or PNG image.")

    try:
        tensor = transform_image(image_bytes)
        if tensor is None:
            raise HTTPException(status_code=400, detail="Could not process the image. It might be corrupted.")
        tensor = tensor.to(device)
    except Exception as e:
        logger.error(f"Error during image transformation: {e}")
        raise HTTPException(status_code=500, detail="Error processing the image.")

    with torch.no_grad():
        output = model(tensor)
        
        confidence_real = output.item()
        
        if confidence_real > 0.5:
            prediction_label = "Real"
            is_fake = False
            confidence_score = confidence_real
        else:
            prediction_label = "Fake"
            is_fake = True
            confidence_score = 1 - confidence_real

    response_data = {
        "prediction": prediction_label,
        "confidence": round(confidence_score, 4), # Làm tròn cho đẹp
        "is_deepfake": is_fake
    }

    return JSONResponse(content=response_data)

@app.get("/")
def read_root():
    return {"status": "Deepfake Detection API is running"}