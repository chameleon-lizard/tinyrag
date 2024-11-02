import llama_cpp
import pathlib
import wordllama


# Loading WordLlama embeddings
wl = wordllama.WordLlama.load(trunc_dim=256)

model_id = "./gemma-2-2b-it-Q4_K_M.gguf"

# Loading model
llm = llama_cpp.Llama(model_path=model_id, n_ctx=1024, verbose=False)

# Loading knowledge_base
knowledge_base = pathlib.Path('file.txt').read_text()

# Semantic chunking
chunks = wl.split(knowledge_base, target_size=256)

if model_id != './gemma-2-2b-it-Q4_K_M.gguf':
    messages = [
        {
            'role': 'system',
            'content': 'You will be given documents and a question. Your task is to answer the question using these documents. Be factual and only use information from the context to answer the questions. Be concise in your answers, not more than one sentence.',
        },
    ]
else:
     messages = [
        {
            'role': 'user',
            'content': 'You will be given documents and a question. Your task is to answer the question using these documents. Be factual and only use information from the context to answer the questions. Be concise in your answers, not more than one sentence.',
        },
        {
            'role': 'assistant',
            'content': 'Okay! Send me the context and the question.',
        },
    ]


while True:
    question = input('Q: ')

    top_docs = wl.topk(question, chunks, k=6)
    context = '\n'.join(
        f'''DOCUMENT SIMILARITY: 

{sim}

DOCUMENT TEXT:

{sent}
'''
        for sent, sim in wl.rank(question, top_docs, sort=True)
    )
    messages_ = messages.copy()
    messages_.append(
       {
            'role': 'user',
            'content': f'''CONTEXT:

    {context}

    QUESTION:

    {question}''',
        }
    )

    print('A: ' + llm.create_chat_completion(messages_)['choices'][0]['message']['content'])
