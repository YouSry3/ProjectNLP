from flask import Flask, request, jsonify, render_template
from transformers import pipeline
import os
import uuid

app = Flask(__name__)

# تحميل نموذج وصف الصور
model = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")

# مجلد لتحميل الصور
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/describe", methods=["POST"])
def describe_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No image selected"}), 400
    
    # حفظ الصورة بمعرف فريد
    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # توليد الوصف
    result = model(filepath)
    caption = result[0]['generated_text']
    
    return jsonify({
        "image_url": f"/{filepath}",
        "caption": caption
    })

if __name__ == "__main__":
    app.run(debug=True)