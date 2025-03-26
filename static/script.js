document.addEventListener('DOMContentLoaded', () => {
  const chatContainer = document.getElementById('chat-container');
  const imageInput = document.getElementById('image-input');
  const sendBtn = document.getElementById('send-btn');
  const previewContainer = document.getElementById('preview-container');
  const previewImage = document.getElementById('preview-image');
  const fileName = document.getElementById('file-name');
  const cancelUpload = document.getElementById('cancel-upload');

  // عند اختيار صورة
  imageInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
          const file = e.target.files[0];
          const reader = new FileReader();
          
          reader.onload = (event) => {
              // عرض المعاينة
              previewImage.src = event.target.result;
              fileName.textContent = file.name;
              previewContainer.classList.remove('hidden');
              sendBtn.disabled = false;
              
              // عرض الصورة في الشات
              addMessage(event.target.result, 'user');
          };
          
          reader.readAsDataURL(file);
      }
  });

  // إلغاء التحميل
  cancelUpload.addEventListener('click', () => {
      imageInput.value = '';
      previewContainer.classList.add('hidden');
      sendBtn.disabled = true;
  });

  // عند الضغط على زر الوصف
  sendBtn.addEventListener('click', async () => {
      if (!imageInput.files[0]) return;
      
      // إضافة مؤشر تحميل
      const loadingId = addLoadingIndicator();
      
      const formData = new FormData();
      formData.append('image', imageInput.files[0]);
      
      try {
          // إرسال الصورة للمخدم
          const response = await fetch('/describe', {
              method: 'POST',
              body: formData
          });
          
          const data = await response.json();
          
          // إزالة مؤشر التحميل
          removeLoadingIndicator(loadingId);
          
          if (data.error) {
              addMessage(data.error, 'error');
          } else {
              // عرض الوصف في الشات
              addMessage(data.caption, 'bot');
          }
          
          // إعادة تعيين الحقل
          imageInput.value = '';
          previewContainer.classList.add('hidden');
          sendBtn.disabled = true;
      } catch (error) {
          removeLoadingIndicator(loadingId);
          addMessage('Error processing image', 'error');
      }
  });
  
  // دالة لإضافة رسالة للشات
  function addMessage(content, sender) {
      const messageDiv = document.createElement('div');
      messageDiv.className = `flex ${sender === 'user' ? 'justify-end' : 'justify-start'}`;
      
      const bubbleDiv = document.createElement('div');
      bubbleDiv.className = `p-3 rounded-lg max-w-xs ${
          sender === 'user' ? 'bg-indigo-100 text-indigo-900' : 
          sender === 'bot' ? 'bg-gray-200 text-gray-900' : 
          'bg-red-100 text-red-900'
      }`;
      
      if (content.startsWith('data:image')) {
          bubbleDiv.innerHTML = `
              <img src="${content}" class="max-w-full h-auto rounded mb-1">
              <div class="text-xs text-gray-500 mt-1">Image uploaded</div>
          `;
      } else {
          bubbleDiv.innerHTML = content;
          
          if (sender === 'bot') {
              bubbleDiv.innerHTML += `
                  <div class="flex justify-end mt-2">
                      <button class="copy-btn text-xs text-indigo-600 hover:text-indigo-800">
                          <i class="far fa-copy mr-1"></i>Copy
                      </button>
                  </div>
              `;
          }
      }
      
      messageDiv.appendChild(bubbleDiv);
      chatContainer.appendChild(messageDiv);
      chatContainer.scrollTop = chatContainer.scrollHeight;
      
      // إضافة حدث نسخ للنص
      if (sender === 'bot') {
          const copyBtn = messageDiv.querySelector('.copy-btn');
          copyBtn.addEventListener('click', () => {
              navigator.clipboard.writeText(content);
              copyBtn.innerHTML = '<i class="fas fa-check mr-1"></i>Copied!';
              setTimeout(() => {
                  copyBtn.innerHTML = '<i class="far fa-copy mr-1"></i>Copy';
              }, 2000);
          });
      }
  }
  
  // دالة لإضافة مؤشر تحميل
  function addLoadingIndicator() {
      const id = 'loading-' + Date.now();
      const loadingDiv = document.createElement('div');
      loadingDiv.className = 'flex justify-start';
      loadingDiv.id = id;
      
      const bubbleDiv = document.createElement('div');
      bubbleDiv.className = 'bg-gray-200 text-gray-900 p-3 rounded-lg max-w-xs';
      bubbleDiv.innerHTML = `
          <div class="flex space-x-2">
              <div class="w-2 h-2 bg-gray-500 rounded-full pulse-animation"></div>
              <div class="w-2 h-2 bg-gray-500 rounded-full pulse-animation" style="animation-delay: 0.2s"></div>
              <div class="w-2 h-2 bg-gray-500 rounded-full pulse-animation" style="animation-delay: 0.4s"></div>
          </div>
      `;
      
      loadingDiv.appendChild(bubbleDiv);
      chatContainer.appendChild(loadingDiv);
      chatContainer.scrollTop = chatContainer.scrollHeight;
      
      return id;
  }
  
  // دالة لإزالة مؤشر تحميل
  function removeLoadingIndicator(id) {
      const element = document.getElementById(id);
      if (element) {
          element.remove();
      }
  }
});