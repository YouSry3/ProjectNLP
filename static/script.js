document.addEventListener('DOMContentLoaded', () => {
  // ... (الكود السابق)

  async function describeImage() {
      if (!imageInput.files[0]) return;
      
      const detailLevel = document.querySelector('.detail-level button.active').dataset.level;
      const loadingId = addLoadingMessage(`Processing...`);
      
      try {
          // إظهار رسالة تحميل
          addSystemMessage(`Processing ${imageInput.files[0].name}`, 'info');
          
          const formData = new FormData();
          formData.append('image', imageInput.files[0]);
          formData.append('detail', detailLevel);
          
          const response = await fetch('/describe', {
              method: 'POST',
              body: formData
          });
          
          if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
          }
          
          const data = await response.json();
          
          if (data.error) {
              throw new Error(data.error);
          }
          
          // إظهار النتيجة بنجاح
          addMessage(data.caption, 'bot');
          
      } catch (error) {
          console.error('Error:', error);
          addSystemMessage(error.message || 'Failed to process image', 'error');
      } finally {
          removeMessage(loadingId);
          resetFileInput();
      }
  }

  // ... (باقي الكود)
});