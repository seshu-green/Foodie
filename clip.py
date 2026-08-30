import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Force CPU

import torch
import open_clip
from ultralytics import YOLO
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="YOLO + CLIP Food Predictor - UNRESTRICTED")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

device = torch.device("cpu")
# Using YOLO to find specific items, but we fall back to whole image if no crops
yolo_model = YOLO("yolov8n.pt").to(device)

# Load CLIP
clip_model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k")
clip_model = clip_model.to(device).eval()

# Dataset Setup
BASE_DIR = r"C:\Users\LSESH\OneDrive\Desktop\prjs\Food\Food\fdimages"
# Dynamically load all folder names as food categories
food_names = [f.replace("_"," ").lower() for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]
text_prompts = [f"a photo of {food}" for food in food_names]

# Pre-encode text prompts for speed
with torch.no_grad():
    tokens = open_clip.tokenize(text_prompts).to(device)
    text_features = clip_model.encode_text(tokens)
    text_features /= text_features.norm(dim=-1, keepdim=True)

@app.post("/predict_food")
async def predict_food(images: List[UploadFile] = File(...)):
    results_all = []
    
    for image in images:
        try:
            img = Image.open(image.file).convert("RGB")
            detections = yolo_model(img)
            
            crops = []
            # Gather all detected boxes
            for r in detections:
                for box in r.boxes.xyxy.cpu().numpy():
                    coords = list(map(int, box)) 
                    crops.append(img.crop(coords))

            # If YOLO doesn't see specific objects, process the whole image as one "crop"
            if not crops: 
                crops = [img]

            image_predictions = []
            seen_foods = {} # Use dictionary to prevent duplicate names in the same image

            for crop in crops:
                img_tensor = preprocess(crop).unsqueeze(0).to(device)
                with torch.no_grad():
                    img_feat = clip_model.encode_image(img_tensor)
                    img_feat /= img_feat.norm(dim=-1, keepdim=True)
                    
                    # Calculate similarity against ALL food names
                    similarity = (img_feat @ text_features.T)[0]
                    
                    # Get top scores for THIS crop
                    # We take top 5 possibilities per crop to ensure "no restriction"
                    probs, indices = similarity.topk(5) 
                    
                    for i in range(len(probs)):
                        name = food_names[int(indices[i])]
                        conf = round(float(probs[i] * 100), 2)
                        
                        # Only add if confidence is decent (>10%) to avoid complete randomness
                        if conf > 10:
                            if name not in seen_foods or conf > seen_foods[name]:
                                seen_foods[name] = conf

            # Convert dictionary back to list for the response
            for food, score in seen_foods.items():
                image_predictions.append({
                    "food_name": food,
                    "confidence": f"{score}%"
                })

            # Sort final list by confidence
            image_predictions.sort(key=lambda x: float(x["confidence"].replace('%','')), reverse=True)
            results_all.append({"image": image.filename, "predictions": image_predictions})
            
        except Exception as e:
            print(f"❌ Error processing image {image.filename}: {e}")
            
    return {"results": results_all}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)