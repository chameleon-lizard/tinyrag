import threading
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import wordllama
import gc

import src.prompts as prompts


class Chatbot:
    def __init__(
        self,
        knowledge_base: str,
        repo_id: str = 'unsloth/gemma-2-2b-it-bnb-4bit',
    ) -> None:
        self.knowledge_base = knowledge_base
        self.repo_id = repo_id
        self.wl = None
        self.llm = None
        self.tokenizer = None
        self.chunks = None
        self.is_loaded = False
        self._loading_thread = None

        if 'gemma-2-2b-it' in repo_id:
            self.messages = [
                {
                    "role": "user",
                    "content": (
                        "You will be given documents and a question. "
                        "Your task is to answer the question using these documents. "
                        "Be factual and only use information from the context to answer the questions. "
                        "Be concise in your answers, not more than one sentence."
                    ),
                },
                {
                    "role": "assistant",
                    "content": "Okay! Send me the context and the question.",
                },
            ]
        else:
            self.messages = [
                {
                    "role": "system",
                    "content": (
                        "You will be given documents and a question. "
                        "Your task is to answer the question using these documents. "
                        "Be factual and only use information from the context to answer the questions. "
                        "Be concise in your answers, not more than one sentence."
                    ),
                },
            ]

        # Start loading in a background thread
        self._loading_thread = threading.Thread(target=self._load_resources)
        self._loading_thread.start()

    def _load_resources(self) -> None:
        # Loading WordLlama embeddings
        self.wl = wordllama.WordLlama.load(trunc_dim=256)

        # Loading llm model
        self.tokenizer = AutoTokenizer.from_pretrained(self.repo_id)

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        self.llm = AutoModelForCausalLM.from_pretrained(self.repo_id, quantization_config=bnb_config)

        if torch.cuda.is_available():
            self.llm = self.llm.to("cuda")

        # Semantic chunking
        self.chunks = self.wl.split(self.knowledge_base, target_size=256)

        self.is_loaded = True

    def wait_for_load(self) -> None:
        if not self.is_loaded:
            self._loading_thread.join()

    def shutdown(self) -> None:
        if self._loading_thread and self._loading_thread.is_alive():
            print("Waiting for resources to finish loading before shutting down...")
            self._loading_thread.join()


        if self.llm is not None:
            self.llm.cpu()
            del self.llm
            self.llm = None

        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        
        if self.wl is not None:
            del self.wl
            self.wl = None
        
        if self.chunks is not None:
            del self.chunks
            self.chunks = None
            
        gc.collect()

        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        self.is_loaded = False


    def retrieve(self, question: str) -> list[tuple[str, float]]:
        self.wait_for_load()

        top_docs = self.wl.topk(question, self.chunks, k=6)
        ranked = self.wl.rank(question, top_docs, sort=True)
        return [(sent, sim) for sent, sim in ranked if sim > 0.1]

    def _create_chat_completion(self, messages):
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.llm.device) 

        print(prompt)

        output_ids = self.llm.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.7,
        )

        final_ans = self.tokenizer.decode(output_ids[0, inputs.input_ids.shape[1]:], skip_special_tokens=True)

        return {"choices": [{"message": {"content": final_ans}}]}


    def send_question(
        self,
        question: str,
        ranked: list[tuple[str, float]],
    ) -> tuple[str, list[tuple[str, float]]]:
        """
        Creates the context based on the ranked documents and sends the question to the model.
        """
        self.wait_for_load()

        context = "\n".join(
            prompts.CONTEXT_TEMPLATE.format(document_text=sent, similarity=sim)
            for sent, sim in ranked
        )

        messages_ = self.messages.copy()
        messages_.append({
            "role": "user",
            "content": prompts.QUESTION_TEMPLATE.format(context=context, question=question),
        })

        res = self._create_chat_completion(messages_)

        return res["choices"][0]["message"]["content"]
