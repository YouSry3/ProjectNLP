from flask import Flask, request, jsonify
from transformers import pipeline
from PIL import Image
import os
import uuid
from datetime import datetime

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
    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>نظام وصف الصور</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
            @keyframes typing {{
                from {{ width: 0 }}
                to {{ width: 100% }}
            }}

            .typing-animation::after {{
                content: "|";
                animation: blink 1s infinite;
            }}

            @keyframes blink {{
                50% {{ opacity: 0; }}
            }}
        </style>
    </head>
    <body class="bg-gray-100">
        <div class="max-w-2xl mx-auto h-screen flex flex-col">
            <!-- Header -->
            <div class="bg-gradient-to-r from-blue-500 to-purple-600 p-4 shadow-lg">
                <div class="flex items-center gap-3 text-white">
                    <div class="bg-white/20 p-2 rounded-full">
                        <i class="fas fa-robot text-xl"></i>
                    </div>
                    <div>
                        <h1 class="text-xl font-bold">مساعد وصف الصور</h1>
                        <p class="text-sm opacity-90">الذكاء الاصطناعي لتحليل الصور</p>
                    </div>
                </div>
            </div>

            <!-- Chat Area -->
            <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                <div class="text-center text-gray-500 py-4">
                    ارفع صورة لتحصل على وصف مفصل
                </div>

                <div id="chat-container"></div>
            </div>

            <!-- Controls -->
            <div class="bg-white border-t p-4 shadow-lg">
                <div class="mb-4 flex gap-2">
                    <button onclick="setDetail('normal')" class="flex-1 px-4 py-2 rounded-full border transition-all"
                            id="normal-btn">
                        وصف عادي
                    </button>
                    <button onclick="setDetail('detailed')" class="flex-1 px-4 py-2 rounded-full border transition-all"
                            id="detailed-btn">
                        وصف مفصل
                    </button>
                </div>

                <div class="flex gap-2">
                    <label class="flex-1 relative">
                        <input type="file" id="image-input" accept="image/*" class="hidden">
                        <div class="w-full p-2 bg-white border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-blue-500 transition-colors text-center">
                            <div class="py-4">
                                <i class="fas fa-cloud-upload-alt text-3xl text-gray-400 mb-2"></i>
                                <p class="text-gray-600">اسحب وأفلت الصورة هنا أو انقر للرفع</p>
                            </div>
                        </div>
                    </label>
                    
                    <button id="describe-btn" class="px-6 py-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition disabled:opacity-50" disabled>
                        <i class="fas fa-paper-plane mr-2"></i>إرسال
                    </button>
                </div>
            </div>
        </div>

        <script>
            let currentDetail = 'normal';
            document.getElementById('normal-btn').classList.add('bg-blue-500', 'text-white', 'border-blue-600');
            
            function setDetail(level) {{
                currentDetail = level;
                document.querySelectorAll('#normal-btn, #detailed-btn').forEach(btn => {{
                    btn.classList.remove('bg-blue-500', 'bg-green-500', 'text-white', 'border-blue-600', 'border-green-600');
                    btn.classList.add('bg-gray-100', 'border-gray-300');
                }});
                
                if(level === 'normal') {{
                    document.getElementById('normal-btn').classList.add('bg-blue-500', 'text-white', 'border-blue-600');
                }} else {{
                    document.getElementById('detailed-btn').classList.add('bg-green-500', 'text-white', 'border-green-600');
                }}
            }}
            
            document.getElementById('image-input').addEventListener('change', function(e) {{
                if (e.target.files.length > 0) {{
                    const file = e.target.files[0];
                    const reader = new FileReader();
                    
                    reader.onload = function(event) {{
                        const chatContainer = document.getElementById('chat-container');
                        
                        if (chatContainer.children.length === 1) {{
                            chatContainer.innerHTML = '';
                        }}
                        
                        const time = new Date().toLocaleTimeString('ar-EG', {{ hour: 'numeric', minute: 'numeric' }});
                        
                        const messageDiv = document.createElement('div');
                        messageDiv.className = 'flex items-start gap-3 mb-4';
                        messageDiv.innerHTML = `
                            <div class="ml-auto max-w-[85%]">
                                <div class="bg-blue-500 text-white p-3 rounded-xl rounded-tr-none shadow">
                                    <img src="${{event.target.result}}" class="mb-2 rounded-lg w-full h-48 object-cover">
                                    <div class="text-xs text-blue-100">تم الرفع: ${{time}}</div>
                                </div>
                            </div>
                        `;
                        chatContainer.appendChild(messageDiv);
                        chatContainer.scrollTop = chatContainer.scrollHeight;
                        
                        document.getElementById('describe-btn').disabled = false;
                    }};
                    
                    reader.readAsDataURL(file);
                }}
            }});
            
            document.getElementById('describe-btn').addEventListener('click', async function() {{
                const fileInput = document.getElementById('image-input');
                if (!fileInput.files[0]) return;
                
                const chatContainer = document.getElementById('chat-container');
                const describeBtn = document.getElementById('describe-btn');
                
                // Add loading indicator
                const loadingDiv = document.createElement('div');
                loadingDiv.className = 'flex items-center gap-2 text-gray-500 mb-4';
                loadingDiv.innerHTML = `
                    <div class="bg-white p-3 rounded-xl shadow">
                        <div class="typing-animation">جاري التحليل</div>
                    </div>
                    <div class="bg-gray-100 p-2 rounded-full">
                        <i class="fas fa-robot"></i>
                    </div>
                `;
                chatContainer.appendChild(loadingDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
                
                describeBtn.disabled = true;
                
                try {{
                    const formData = new FormData();
                    formData.append('image', fileInput.files[0]);
                    formData.append('detail', currentDetail);
                    
                    const response = await fetch('/describe', {{
                        method: 'POST',
                        body: formData
                    }});
                    
                    if (!response.ok) {{
                        throw new Error(await response.text());
                    }}
                    
                    const data = await response.json();
                    const time = new Date().toLocaleTimeString('ar-EG', {{ hour: 'numeric', minute: 'numeric' }});
                    
                    // Remove loading indicator
                    loadingDiv.remove();
                    
                    // Show result
                    const resultDiv = document.createElement('div');
                    resultDiv.className = 'flex items-start gap-3 mb-4';
                    resultDiv.innerHTML = `
                        <div class="bg-white p-3 rounded-xl rounded-tl-none shadow">
                            <div class="font-medium mb-2">وصف الصورة:</div>
                            <p class="text-gray-700">${{data.caption}}</p>
                            <div class="mt-2 text-xs text-gray-500">${{time}}</div>
                        </div>
                        <div class="bg-gray-100 p-2 rounded-full">
                            <i class="fas fa-robot text-gray-500"></i>
                        </div>
                    `;
                    chatContainer.appendChild(resultDiv);
                    
                    // Reset input
                    fileInput.value = '';
                    describeBtn.disabled = true;
                    
                }} catch (error) {{
                    console.error('Error:', error);
                    loadingDiv.remove();
                    
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'bg-red-100 text-red-800 px-4 py-2 rounded-lg text-center mb-4';
                    errorDiv.innerHTML = `
                        <i class="fas fa-exclamation-circle mr-1"></i>
                        حدث خطأ أثناء معالجة الصورة
                    `;
                    chatContainer.appendChild(errorDiv);
                    
                    describeBtn.disabled = false;
                }}
                
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }});
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
        img = Image.open(file.stream)
        img.verify()
        file.stream.seek(0)
        
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        result = image_describer(filepath)
        caption = result[0]['generated_text']
        
        detail_level = request.form.get('detail', 'normal')
        if detail_level == "detailed":
            caption = f"وصف مفصل: {caption} (تحليل إضافي باستخدام الذكاء الاصطناعي)"
        
        return jsonify({"caption": caption})
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)