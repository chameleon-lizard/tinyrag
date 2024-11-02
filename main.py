import llama_cpp
import pathlib
import wordllama


# Loading WordLlama embeddings
wl = wordllama.WordLlama.load(trunc_dim=256)

repo_id = 'bartowski/gemma-2-2b-it-GGUF'
quant = '*Q4_K_S.gguf'
# Loading model
llm = llama_cpp.Llama.from_pretrained(
    repo_id=repo_id, 
    filename=quant,
    n_ctx=1024, 
    verbose=False, 
)

# Loading knowledge_base
knowledge_base = pathlib.Path('file.txt').read_text()

# Semantic chunking
chunks = wl.split(knowledge_base, target_size=256)

if repo_id != 'bartowski/gemma-2-2b-it-GGUF':
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
    ranked =  [(sent, sim) for sent, sim in wl.rank(question, top_docs, sort=True) if sim > 0.25]
    context = '\n'.join(
        f'''DOCUMENT SIMILARITY: 

{sim:.2f}

DOCUMENT TEXT:

{sent}
'''
        for sent, sim in ranked
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

    res = llm.create_chat_completion(messages_)

    print('A: ' + res['choices'][0]['message']['content'], end='')
    print('References: ' + '\n'.join(f'Doc {idx}, sim {doc[1]:.2f}: {doc[0][:50]}...' for idx, doc in enumerate(ranked)))
    print()
