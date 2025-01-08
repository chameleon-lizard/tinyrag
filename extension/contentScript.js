chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('contentScript.js received message:', message);
  
    if (message.type === 'HIGHLIGHT_CHUNKS') {
      const { chunks } = message;
  
      const instance = new Mark(document.body);
      instance.unmark();
  
      chunks.forEach(({ text, similarity }) => {
        if (text && similarity >= 0.1) {
          highlightTextOnPage(text);
        }
      });
  
      sendResponse({ status: "ok" });
    }
  
    if (message.type === 'CLEAR_HIGHLIGHTS') {
      const instance = new Mark(document.body);
      instance.unmark();
      sendResponse({ status: "ok" });
    }
  });
  
  function highlightTextOnPage(searchText) {
    const instance = new Mark(document.body);
    
    instance.mark(searchText, {
      accuracy: "exactly",
      separateWordSearch: false
    });
  }