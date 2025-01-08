document.addEventListener('DOMContentLoaded', function () {
  const questionInput = document.getElementById('questionInput');
  const askBtn = document.getElementById('askBtn');
  const clearBtn = document.getElementById('clearBtn');
  const answerContainer = document.getElementById('answerContainer');

  // Set focus to the question input field
  questionInput.focus();

  clearBtn.addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    chrome.tabs.sendMessage(tab.id, { type: 'CLEAR_HIGHLIGHTS' });
    answerContainer.classList.add('hidden');
    document.body.classList.remove('expanded');
    questionInput.value = '';
    questionInput.focus();
  });

  askBtn.addEventListener('click', async () => {
    console.log('The "Ask" button is clicked');
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    console.log('The current tab:', tab);

    const url = tab.url;
    const question = questionInput.value.trim();

    if (!question) {
      console.log('The question is not entered');
      return;
    }

    // Expand the popup
    document.body.classList.add('expanded');
    answerContainer.classList.remove('hidden');
    answerContainer.textContent = "Please wait, processing...";
    console.log('Sending a request to the server with the URL:', url, 'and the question:', question);

    try {
      const response = await fetch('http://127.0.0.1:5000/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, question }),
      });

      console.log('The response from the server is received:', response);

      if (!response.ok) {
        console.error('The server error:', response.statusText);
        answerContainer.textContent = "The server error.";
        return;
      }

      const data = await response.json();
      console.log('The data from the server:', data);

      const { answer, chunks } = data;

      answerContainer.textContent = answer;
      console.log('Sending a message to contentScript.js with chunks:', chunks);

      chrome.tabs.sendMessage(
        tab.id,
        { type: 'HIGHLIGHT_CHUNKS', chunks },
        response => {
          if (chrome.runtime.lastError) {
            console.error('The error sending a message to contentScript.js:', chrome.runtime.lastError.message);
            return;
          }
          console.log('The response from contentScript.js:', response);
        }
      );
    } catch (error) {
      console.error('The error when requesting the server:', error);
      answerContainer.textContent = `The error: ${error.message}`;
    }
  });

  // Add event listener for pressing Enter in the input field
  questionInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
      event.preventDefault(); // Prevent form submission if the input is within a form
      askBtn.click(); // Trigger the click event of the Ask button
    }
  });
});
