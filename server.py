
import time
import threading
import src.utils as utils
import main

from flask_cors import CORS
from flask import Flask, request, jsonify

app = Flask(__name__)
CORS(app)

chatbot_instance = None
last_request_time = None
UNLOAD_TIMEOUT = 120


def unload_model():
    """
    English: Unloads the model from memory.
    """
    global chatbot_instance
    if chatbot_instance is not None:
        chatbot_instance.shutdown()
        chatbot_instance = None
        print("[INFO] Model unloaded from memory.")

def background_unload_check():
    """
    A background thread that checks if there has been a long period of no requests.
    If so, it unloads the model from memory.
    """
    global last_request_time
    while True:
        if last_request_time and (time.time() - last_request_time > UNLOAD_TIMEOUT):
            unload_model()
            last_request_time = None
        time.sleep(30)

unload_thread = threading.Thread(target=background_unload_check, daemon=True)
unload_thread.start()


@app.route('/process', methods=['POST'])
def process_page():
    """
    Accepts JSON with fields: 'url', 'question'.
    Downloads the page, processes it, returns the answer and chunks for highlighting.
    """
    global chatbot_instance, last_request_time

    data = request.json
    url = data.get("url")
    question = data.get("question")

    if not utils.validate_url(url):
        return jsonify({"error": f"'{url}' is not a valid URL."}), 400

    last_request_time = time.time()

    if chatbot_instance is None:
        print("[INFO] Loading model...")
        html_content = utils.download_page(url)
        if html_content is None:
            return jsonify({"error": "Failed to download page"}), 500

        text = utils.extract_text(html_content)
        chatbot_instance = main.Chatbot(text)

        chatbot_instance.wait_for_load()

    ranked = chatbot_instance.retrieve(question)
    answer = chatbot_instance.send_question(question, ranked)

    chunks = [
        {"text": chunk_text, "similarity": sim}
        for chunk_text, sim in ranked
    ]

    return jsonify({
        "answer": answer,
        "chunks": chunks,
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
