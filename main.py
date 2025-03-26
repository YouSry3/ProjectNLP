from flask import Flask, request, jsonify
from transformers import pipeline
from PIL import Image
import os
import uuid

app = Flask(__name__)

# تحميل نموذج وصف الصور
print("🔄 جاري تحميل نموذج الذكاء الاصطناعي...")
try:
    image_describer = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
    print("✅ تم تحميل النموذج بنجاح!")
except Exception as e:
    print(f"❌ فشل تحميل النموذج: {str(e)}")
    image_describer = None

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>نظام وصف الصور</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
            .chat-container {
                height: 60vh;
                overflow-y: auto;
            }
            .message {
                margin-bottom: 1rem;
            }
            .user-message {
                background-color: #e0f2fe;
                border-radius: 1rem 1rem 0 1rem;
                padding: 0.75rem;
                margin-left: auto;
                max-width: 80%;
            }
            .bot-message {
                background-color: #f0fdf4;
                border-radius: 1rem 1rem 1rem 0;
                padding: 0.75rem;
                margin-right: auto;
                max-width: 80%;
            }
            .image-preview {
                max-width: 100%;
                max-height: 200px;
                border-radius: 0.5rem;
            }
        </style>
    </head>
    <body class="bg-gray-50">
        <div class="container mx-auto max-w-md p-4">
            <div class="bg-white rounded-xl shadow-md overflow-hidden">
                <!-- Header -->
                <div class="bg-blue-600 text-white p-4">
                    <h1 class="text-xl font-bold text-center">
                        <i class="fas fa-camera-retro mr-2"></i>نظام وصف الصور الذكي
                    </h1>
                </div>
                
                <!-- Chat Area -->
                <div id="chat-container" class="p-4 chat-container">
                    <div class="text-center text-gray-500 py-4">
                        قم برفع صورة لتحصل على وصف دقيق
                    </div>
                </div>
                
                <!-- Controls -->
                <div class="p-4 border-t">
                    <div class="mb-3">
                        <label class="block text-sm font-medium text-gray-700 mb-2">مستوى التفصيل:</label>
                        <div class="flex gap-2">
                            <button onclick="setDetail('normal')" class="flex-1 py-2 px-4 rounded-lg bg-blue-100 text-blue-800 border border-blue-300">عادي</button>
                            <button onclick="setDetail('detailed')" class="flex-1 py-2 px-4 rounded-lg bg-green-100 text-green-800 border border-green-300">مفصل</button>
                        </div>
                    </div>
                    
                    <div class="flex gap-2">
                        <label class="flex-1">
                            <input type="file" id="image-input" accept="image/*" class="hidden">
                            <div class="w-full py-2 px-4 bg-blue-600 text-white rounded-lg cursor-pointer text-center hover:bg-blue-700 transition">
                                <i class="fas fa-upload mr-2"></i>رفع صورة
                            </div>
                        </label>
                        <button id="describe-btn" class="flex-1 py-2 px-4 bg-green-600 text-white rounded-lg disabled:opacity-50" disabled>
                            <i class="fas fa-search mr-2"></i>وصف
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let currentDetail = 'normal';
            
            function setDetail(level) {
                currentDetail = level;
                document.querySelectorAll('button[onclick^="setDetail"]').forEach(btn => {
                    btn.classList.remove('bg-blue-600', 'text-white');
                    btn.classList.add(btn.classList.contains('bg-blue-100') ? 'bg-blue-100' : 'bg-green-100');
                });
                event.target.classList.add(level === 'normal' ? 'bg-blue-600' : 'bg-green-600', 'text-white');
            }
            
            document.getElementById('image-input').addEventListener('change', function(e) {
                if (e.target.files.length > 0) {
                    const file = e.target.files[0];
                    const reader = new FileReader();
                    
                    reader.onload = function(event) {
                        const chatContainer = document.getElementById('chat-container');
                        
                        // Remove welcome message
                        if (chatContainer.children.length === 1) {
                            chatContainer.innerHTML = '';
                        }
                        
                        const messageDiv = document.createElement('div');
                        messageDiv.className = 'message';
                        messageDiv.innerHTML = `
                            <div class="user-message">
                                <img src="${event.target.result}" class="image-preview mb-2">
                                <div class="text-sm text-gray-600">تم رفع الصورة بنجاح</div>
                            </div>
                        `;
                        chatContainer.appendChild(messageDiv);
                        chatContainer.scrollTop = chatContainer.scrollHeight;
                        
                        document.getElementById('describe-btn').disabled = false;
                    };
                    
                    reader.readAsDataURL(file);
                }
            });
            
            document.getElementById('describe-btn').addEventListener('click', async function() {
                const fileInput = document.getElementById('image-input');
                if (!fileInput.files[0]) return;
                
                const chatContainer = document.getElementById('chat-container');
                const describeBtn = document.getElementById('describe-btn');
                
                // Add loading indicator
                const loadingDiv = document.createElement('div');
                loadingDiv.className = 'message';
                loadingDiv.innerHTML = `
                    <div class="bot-message flex items-center gap-2">
                        <div class="flex space-x-1">
                            <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                            <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style="animation-delay: 0.2s"></div>
                            <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style="animation-delay: 0.4s"></div>
                        </div>
                        <span>جاري تحليل الصورة...</span>
                    </div>
                `;
                chatContainer.appendChild(loadingDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
                
                describeBtn.disabled = true;
                
                try {
                    const formData = new FormData();
                    formData.append('image', fileInput.files[0]);
                    formData.append('detail', currentDetail);
                    
                    const response = await fetch('/describe', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        throw new Error(await response.text());
                    }
                    
                    const data = await response.json();
                    
                    // Remove loading indicator
                    loadingDiv.remove();
                    
                    // Show result
                    const resultDiv = document.createElement('div');
                    resultDiv.className = 'message';
                    resultDiv.innerHTML = `
                        <div class="bot-message">
                            <div class="font-medium mb-1">وصف الصورة:</div>
                            <div class="mb-2">${data.caption}</div>
                            <div class="text-right">
                                <button onclick="copyText(this)" class="text-xs text-blue-600 hover:text-blue-800">
                                    <i class="far fa-copy mr-1"></i>نسخ النص
                                </button>
                            </div>
                        </div>
                    `;
                    chatContainer.appendChild(resultDiv);
                    
                    // Reset input
                    fileInput.value = '';
                    describeBtn.disabled = true;
                    
                } catch (error) {
                    console.error('Error:', error);
                    loadingDiv.remove();
                    
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'message';
                    errorDiv.innerHTML = `
                        <div class="bg-red-100 text-red-800 px-4 py-2 rounded-lg text-center">
                            <i class="fas fa-exclamation-circle mr-1"></i>
                            حدث خطأ أثناء معالجة الصورة
                        </div>
                    `;
                    chatContainer.appendChild(errorDiv);
                    
                    describeBtn.disabled = false;
                }
                
                chatContainer.scrollTop = chatContainer.scrollHeight;
            });
            
            function copyText(button) {
                const text = button.closest('.bot-message').querySelector('div:nth-child(2)').textContent;
                navigator.clipboard.writeText(text);
                
                const icon = button.querySelector('i');
                icon.classList.replace('fa-copy', 'fa-check');
                button.innerHTML = button.innerHTML.replace('نسخ النص', 'تم النسخ!');
                
                setTimeout(() => {
                    icon.classList.replace('fa-check', 'fa-copy');
                    button.innerHTML = button.innerHTML.replace('تم النسخ!', 'نسخ النص');
                }, 2000);
            }
        </script>
    </body>
    </html>
    """

@app.route("/describe", methods=["POST"])
def describe_image():
    if not image_describer:
        return jsonify({"error": "النموذج غير محمل"}), 500
    
    if "image" not in request.files:
        return jsonify({"error": "لم يتم اختيار صورة"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "ملف فارغ"}), 400

    try:
        # التحقق من أن الملف صورة
        img = Image.open(file.stream)
        img.verify()
        file.stream.seek(0)
        
        # حفظ الصورة
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # توليد الوصف الأساسي
        result = image_describer(filepath)
        caption = result[0]['generated_text']
        
        # تحسين الوصف حسب المستوى المختار
        detail_level = request.form.get('detail', 'normal')
        if detail_level == "detailed":
            # إضافة تحسينات للوصف المفصل
            if "men" in caption.lower():
                caption = "مجموعة من الرجال يلتقطون صورة معًا. " + caption
            elif "woman" in caption.lower():
                caption = "امرأة تلتقط صورة. " + caption
            else:
                caption = "صورة تحتوي على: " + caption
        
        return jsonify({"caption": caption})
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)