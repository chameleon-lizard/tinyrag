# Tinyrag

A tiny chrome extension, using which you can chat with your webpages.

## Installation

### Chrome Extension

1. Clone the repository
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" in the top right corner
4. Click "Load unpacked" and select the `extension` directory from the cloned repository
5. Click the extension icon in Chrome to open the popup interface
6. Set up your models and API keys in the Settings section

### About models and API keys

By default, an free tier of Gemma-2-9b model on OpenRouter is selected. To use it, create your own API key and paste it into the field. You can use any OpenAI-compatible API endpoint, even a self hosted one. If the endpoint does not implement keys, put anything into the key field.

Embedding model to do search through the webpage is inferenced locally, on the CPU of your computer, thus, it might be slow. On Intel Core i5-5250U it takes about 30 seconds to index a medium sized Wikipedia page using Xenova/multilingual-e5-small model and about 8-10 seconds using Xenova/all-MiniLM-L6-v2.

You can experiment with different models by checking out [ONNX converted models on HuggingFace](https://huggingface.co/Xenova).

## Usage

1. Click the extension icon in Chrome to open the popup interface
2. Enter your question about the current webpage
3. Click "Ask" to get an answer
4. Relevant text passages on the webpage will be highlighted
5. Use "Clear" to remove highlights and reset the interface
