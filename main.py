import openai
import torch
import gc
import src.prompts as prompts
from sentence_transformers import SentenceTransformer, util

class Chatbot:
    def __init__(
        self,
        knowledge_base: str,
        api_key: str,
        model: str,
        api_link: str,
        embedder_model: str,
    ) -> None:
        self.knowledge_base = knowledge_base
        self.api_key = api_key
        self.model = model
        self.api_link = api_link
        self.embedder_model = embedder_model

        # Load the sentence-transformers model
        self.embedder = SentenceTransformer(self.embedder_model)

        # Split knowledge base into paragraphs
        self.chunks = self._split_into_paragraphs(self.knowledge_base)

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

    def _split_into_paragraphs(self, text: str) -> list[str]:
        # Split the text into paragraphs using newlines
        paragraphs = text.split('\n\n')
        # Remove any empty paragraphs
        paragraphs = [para.strip() for para in paragraphs if para.strip()]
        return paragraphs

    def retrieve(self, question: str) -> list[tuple[str, float]]:
        # Embed the question
        question_embedding = self.embedder.encode(question, convert_to_tensor=True)

        # Embed all paragraphs
        paragraph_embeddings = self.embedder.encode(self.chunks, convert_to_tensor=True)

        # Compute cosine similarities
        cosine_scores = util.cos_sim(question_embedding, paragraph_embeddings)[0]

        # Get the top 6 most similar paragraphs
        top_indices = torch.topk(cosine_scores, k=6).indices
        top_scores = cosine_scores[top_indices]

        # Filter out paragraphs with similarity score < 0.1
        ranked = [(self.chunks[i], score.item()) for i, score in zip(top_indices, top_scores) if score.item() > 0.1]

        return ranked

    def send_question(
        self,
        question: str,
        ranked: list[tuple[str, float]],
    ) -> str:
        """
        Creates the context based on the ranked documents and sends the question to the model.
        """
        context = "\n".join(
            prompts.CONTEXT_TEMPLATE.format(document_text=sent, similarity=sim)
            for sent, sim in ranked
        )

        prompt = prompts.QUESTION_TEMPLATE.format(context=context, question=question)

        client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.api_link,
        )

        messages = self.messages.copy()
        messages.append({"role": "user", "content": prompt})

        response_big = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=150,
            n=1,
        )

        response = response_big.choices[0].message.content

        return response
