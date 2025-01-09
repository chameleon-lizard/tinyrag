import { Chatbot } from './Chatbot.js';

document.addEventListener('DOMContentLoaded', function () {
  const questionInput = document.getElementById('questionInput');
  const askBtn = document.getElementById('askBtn');
  const clearBtn = document.getElementById('clearBtn');
  const answerContainer = document.getElementById('answerContainer');
  const settingsBtn = document.getElementById('settingsBtn');
  const settingsContent = document.getElementById('settingsContent');
  const apiKeyInput = document.getElementById('apiKeyInput');
  const modelInput = document.getElementById('modelInput');
  const apiLinkInput = document.getElementById('apiLinkInput');
  const embedderModelInput = document.getElementById('embedderModelInput');
  const saveSettingsBtn = document.getElementById('saveSettingsBtn');

  // Default configuration values
  const defaultConfig = {
    API_KEY: 'sk-or-v1-xxxxxx',
    MODEL: 'google/gemma-2-9b-it:free',
    API_LINK: 'https://openrouter.ai/api/v1/chat/completions',
    EMBEDDER_MODEL: 'Xenova/all-MiniLM-L6-v2',
  };

  let chatbotInstance = null;
  let lastRequestTime = null;

  // Load saved settings or use defaults
  chrome.storage.sync.get(['settings'], function (result) {
    const settings = result.settings || defaultConfig;
    apiKeyInput.value = settings.API_KEY;
    modelInput.value = settings.MODEL;
    apiLinkInput.value = settings.API_LINK;
    embedderModelInput.value = settings.EMBEDDER_MODEL;
  });

  // Set focus to the question input field
  questionInput.focus();

  // Toggle settings visibility
  settingsBtn.addEventListener('click', () => {
    settingsContent.classList.toggle('hidden');
  });

  // Save settings
  saveSettingsBtn.addEventListener('click', () => {
    const settings = {
      API_KEY: apiKeyInput.value,
      MODEL: modelInput.value,
      API_LINK: apiLinkInput.value,
      EMBEDDER_MODEL: embedderModelInput.value,
    };
    chrome.storage.sync.set({ settings }, () => {
      console.log('Settings saved');
      settingsContent.classList.add('hidden');
    });
  });

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
    answerContainer.textContent = 'Please wait, processing...';

    try {
      // Load settings
      const settings = await new Promise((resolve) => {
        chrome.storage.sync.get(['settings'], (result) => {
          resolve(result.settings || defaultConfig);
        });
      });

      // Download and clean the webpage content
      const htmlContent = await fetch(url).then((response) => response.text());
      const text = extractTextFromHtml(htmlContent);

      if (!text) {
        throw new Error('Failed to extract text from the webpage.');
      }

      // Initialize or reuse the chatbot instance
      if (!chatbotInstance) {
        console.log('[INFO] Loading model...');
        chatbotInstance = new Chatbot(
          text, // Use the cleaned text as the knowledge base
          settings.API_KEY,
          settings.MODEL,
          settings.API_LINK,
          settings.EMBEDDER_MODEL
        );
        await chatbotInstance.loadEmbedder();
      }

      // Retrieve relevant chunks and get the answer
      const ranked = await chatbotInstance.retrieve(question);
      const answer = await chatbotInstance.sendQuestion(question, ranked);

      // Display the answer
      answerContainer.textContent = answer;

      // Send chunks to content script for highlighting
      const chunks = ranked.map(({ chunk, score }) => ({
        text: chunk,
        similarity: score,
      }));
      console.log('Sending a message to contentScript.js with chunks:', chunks);

      chrome.tabs.sendMessage(
        tab.id,
        { type: 'HIGHLIGHT_CHUNKS', chunks },
        (response) => {
          if (chrome.runtime.lastError) {
            console.error(
              'The error sending a message to contentScript.js:',
              chrome.runtime.lastError.message
            );
            return;
          }
          console.log('The response from contentScript.js:', response);
        }
      );
    } catch (error) {
      console.error('The error when processing the question:', error);
      answerContainer.textContent = `The error: ${error.message}`;
    }
  });

  // Add event listener for pressing Enter in the input field
  questionInput.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
      event.preventDefault(); // Prevent form submission if the input is within a form
      askBtn.click(); // Trigger the click event of the Ask button
    }
  });
});

/**
 * Extracts and cleans text from HTML content.
 * @param {string} htmlContent - The HTML content of the webpage.
 * @returns {string} - The cleaned text.
 */
function extractTextFromHtml(htmlContent) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlContent, 'text/html');

  // Remove script and style elements
  doc.querySelectorAll('script, style').forEach((element) => element.remove());

  // Extract text content
  const text = doc.body.textContent || '';

  // Clean up the text (remove extra spaces, newlines, etc.)
  return text;
}
