# Tinyrag
A Chrome extension implementation of TinyRAG - a lightweight RAG (Retrieval-Augmented Generation) system. This is a fork of the original [Tinyrag project](https://github.com/chameleon-lizard/tinyrag), modified to work as a browser extension and using Transformers instead of llama.cpp.

## Installation

### Chrome Extension

1. Clone the repository
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" in the top right corner
4. Click "Load unpacked" and select the `extension` directory from the cloned repository

### Backend Server

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate  # For Linux/MacOS
# or
venv\Scripts\activate  # For Windows
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file for setup:
```
echo 'API_KEY=sk-or-v1-xxxxxx
MODEL=google/gemini-flash-1.5-8b
API_LINK=https://openrouter.ai/api/v1
EMBEDDER_MODEL=intfloat/multilingual-e5-small' > .env
```

## Usage

1. Start the backend server:
```bash
python server.py
```

2. Click the extension icon in Chrome to open the popup interface
3. Enter your question about the current webpage
4. Click "Ask" to get an answer
5. Relevant text passages on the webpage will be highlighted
6. Use "Clear" to remove highlights and reset the interface
