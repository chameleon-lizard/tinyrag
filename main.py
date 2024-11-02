import llama_cpp
import pathlib
import wordllama


class Chatbot:
    def __init__(
        self,
        knowledge_base: str,
        repo_id: str = "bartowski/gemma-2-2b-it-GGUF",
        quant: str = "*Q4_K_S.gguf",
    ) -> None:
        # Loading WordLlama embeddings
        self.wl = wordllama.WordLlama.load(trunc_dim=256)

        # Loading model
        self.llm = llama_cpp.Llama.from_pretrained(
            repo_id=repo_id,
            filename=quant,
            n_ctx=1024,
            n_gpu_layers=256,
            verbose=False,
        )

        # Semantic chunking
        self.chunks = self.wl.split(knowledge_base, target_size=256)

        if repo_id != "bartowski/gemma-2-2b-it-GGUF":
            self.messages = [
                {
                    "role": "system",
                    "content": "You will be given documents and a question. Your task is to answer the question using these documents. Be factual and only use information from the context to answer the questions. Be concise in your answers, not more than one sentence.",
                },
            ]
        else:
            self.messages = [
                {
                    "role": "user",
                    "content": "You will be given documents and a question. Your task is to answer the question using these documents. Be factual and only use information from the context to answer the questions. Be concise in your answers, not more than one sentence.",
                },
                {
                    "role": "assistant",
                    "content": "Okay! Send me the context and the question.",
                },
            ]

    def send_question(self, question: str) -> tuple[str, list[tuple[str, float]]]:
        top_docs = self.wl.topk(question, self.chunks, k=6)
        ranked = [
            (sent, sim)
            for sent, sim in self.wl.rank(question, top_docs, sort=True)
            if sim > 0.25
        ]
        context = "\n".join(
            f"""DOCUMENT SIMILARITY: 

    {sim:.2f}

    DOCUMENT TEXT:

    {sent}
    """
            for sent, sim in ranked
        )
        messages_ = self.messages.copy()
        messages_.append(
            {
                "role": "user",
                "content": f"""CONTEXT:

        {context}

        QUESTION:

        {question}""",
            }
        )

        res = self.llm.create_chat_completion(messages_)

        return res["choices"][0]["message"]["content"], ranked


if __name__ == "__main__":
    text = pathlib.Path("file.txt").read_text()
    c = Chatbot(text)

    print("Q: Who is Farah?")
    print("A: " + c.send_question("Who is Farah?")[0])

    print("Q: Who is Price?")
    print("A: " + c.send_question("Who is Price?")[0])

    print("Q: Who is the game's composer?")
    print("A: " + c.send_question("Who is the game's composer?")[0])
