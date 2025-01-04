chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {


  console.log('background.js received message:', message);

  if (message.type === 'FETCH_FROM_SERVER') {
    const { url, question } = message;

    fetch('http://127.0.0.1:5000/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, question }),
    })
      .then(response => response.json())
      .then(data => {
        sendResponse({ success: true, data });
      })
      .catch(error => {
        console.error('Error when accessing the server:', error);
        sendResponse({ success: false, error: error.message });
      });

    return true;
  }
});
