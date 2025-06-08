import torch
import torchvision.transforms as transforms
from PIL import Image
import io

IMAGE_SIZE = (256, 256)

transform = transforms.Compose([
    transforms.Resize(IMAGE_SIZE),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def transform_image(image_bytes: bytes) -> torch.Tensor:
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        tensor = transform(image)
        return tensor.unsqueeze(0)
    except Exception as e:
        print(f"Error transforming image: {e}")
        return None