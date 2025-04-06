from flask import Flask, request, render_template
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import os

app = Flask(__name__)

# Load CLIP model and processor
clip_model = CLIPModel.from_pretrained("laion/CLIP-ViT-B-32-laion2B-s34B-b79K")
clip_processor = CLIPProcessor.from_pretrained("laion/CLIP-ViT-B-32-laion2B-s34B-b79K")

# Hardcoded application data
applications = {
    "APP123": {"scheme_name": "Rajiv Yuvvikas Scheme", "business_name": "Royal Kirana Store"},
    "APP456": {"scheme_name": "Rajiv Yuvvikas Scheme", "business_name": "GreenTech Solutions"},
    "APP789": {"scheme_name": "Rajiv Yuvvikas Scheme", "business_name": "Shivam Electronics"}
}

# Function to compare image with business name using CLIP
def match_business_with_image(business_name, image):
    inputs = clip_processor(text=[business_name], images=image, return_tensors="pt", padding=True)
    outputs = clip_model(**inputs)
    probs = outputs.logits_per_image.softmax(dim=1)
    return probs[0][0].item()

# Home page
@app.route('/')
def index():
    return render_template("index.html")

# Verification route
@app.route('/verify', methods=['POST'])
def verify():
    app_number = request.form['app_number'].strip()
    file = request.files['business_image']

    if app_number not in applications:
        return render_template("verify_result.html", error="❌ Application number not found.")

    try:
        image = Image.open(file).convert("RGB")
    except Exception:
        return render_template("verify_result.html", error="❌ Invalid image file.")

    app_data = applications[app_number]
    business_name = app_data['business_name']
    scheme_name = app_data['scheme_name']

    score = match_business_with_image(business_name, image)
    digital_verified = score > 0.5

    return render_template("verify_result.html",
                           app_number=app_number,
                           scheme_name=scheme_name,
                           business_name=business_name,
                           score=round(score, 2),
                           digital_verified=digital_verified)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
