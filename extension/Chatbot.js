import { pipeline } from './transformers.js';

let embeddingsPipeline;
let isEmbeddingsLoading = false;

export class Chatbot {
    constructor(knowledgeBase, apiKey, model, apiEndpoint, embedderModel) {
        this.knowledgeBase = knowledgeBase;
        this.apiKey = apiKey;
        this.model = model;
        this.apiEndpoint = apiEndpoint;
        this.embedderModel = embedderModel;

        // Split knowledge base into paragraphs
        this.chunks = this._splitIntoParagraphs(this.knowledgeBase);

        // Initialize messages with the system message
        this.messages = [
            {
                role: "system",
                content: (
                    "You will be given documents and a question. " +
                    "Your task is to answer the question using these documents. " +
                    "Be factual and only use information from the context to answer the questions. " +
                    "Be concise in your answers, not more than one sentence. " +
                    "Answer in the same language you were asked."
                ),
            },
        ];
    }

    async loadEmbedder() {
        if (!embeddingsPipeline && !isEmbeddingsLoading) {
            isEmbeddingsLoading = true;
            try {
                embeddingsPipeline = await pipeline('feature-extraction', this.embedderModel);
            } catch (error) {
                console.error('Error loading embedding model:', error);
                throw error;
            } finally {
                isEmbeddingsLoading = false;
            }
        }
    }

    _splitIntoParagraphs(text) {
        // Split the text into paragraphs using newlines
        const paragraphs = text.split('\n');
        // Remove any empty paragraphs
        return paragraphs.map(para => para.trim()).filter(para => para);
    }

    async retrieve(question) {
        if (!embeddingsPipeline) {
            await this.loadEmbedder();
        }

        // Embed the question
        const questionEmbedding = await embeddingsPipeline(question, {
            pooling: 'mean',
            normalize: true,
        });

        // Embed all paragraphs
        const paragraphEmbeddings = await Promise.all(
            this.chunks.map(chunk =>
                embeddingsPipeline(chunk, { pooling: 'mean', normalize: true })
            )
        );

        // Compute cosine similarities
        const cosineScores = paragraphEmbeddings.map(embedding =>
            this.cosineSimilarity(questionEmbedding.data, embedding.data)
        );

        // Get the top 6 most similar paragraphs
        const topIndices = this.getTopIndices(cosineScores, 6);
        const topScores = topIndices.map(index => cosineScores[index]);

        // Filter out paragraphs with similarity score < 0.1
        const ranked = topIndices
            .map((index, i) => ({ chunk: this.chunks[index], score: topScores[i] }))
            .filter(({ score }) => score > 0.1);

        return ranked;
    }

    cosineSimilarity(vecA, vecB) {
        const dotProduct = vecA.reduce((sum, a, i) => sum + a * vecB[i], 0);
        const magnitudeA = Math.sqrt(vecA.reduce((sum, a) => sum + a * a, 0));
        const magnitudeB = Math.sqrt(vecB.reduce((sum, b) => sum + b * b, 0));
        return dotProduct / (magnitudeA * magnitudeB);
    }

    getTopIndices(scores, k) {
        return scores
            .map((score, index) => ({ score, index }))
            .sort((a, b) => b.score - a.score)
            .slice(0, k)
            .map(({ index }) => index);
    }

    async sendQuestion(question, ranked) {
        // Create the context based on the ranked documents
        const context = ranked.map(({ chunk, score }) =>
            `Document: ${chunk}\nSimilarity: ${score.toFixed(4)}`
        ).join('\n');

        const prompt = `Context:\n${context}\n\nQuestion: ${question}`;

        // Construct the messages array for this single turn
        const messages = [
            this.messages[0], // The original system message
            { role: "user", content: prompt } // The user's current question with context
        ];

        try {
            const response = await this.queryModel(
                messages, // Use a fresh messages array for each question
                this.apiKey,
                this.model,
                this.apiEndpoint
            );
            return response.choices[0].message.content;
        } catch (error) {
            console.error("Error querying model:", error);
            return null;
        }
    }

    async queryModel(messages, apiKey, model, apiEndpoint) {
        const response = await fetch(apiEndpoint, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${apiKey}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                model: model,
                messages: messages,
            }),
        });

        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }

        return await response.json();
    }
}
