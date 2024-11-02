# Tinyrag

A tiny lightweight CPU-optimized implementation of RAG using SLMs. It uses the amazing [WordLlama](https://github.com/dleemiller/WordLlama) library as an embedder and llama-cpp-python as the inference engine, so it would run everywhere there is a CPU and about 2.7 GB of free RAM.

## Installation

1. Create a venv:

```
python -m venv venv
```

2. Activate venv:

```
source venv/bin/activate
```

3. Run installation script, which will install llama.cpp with GPU support if available

```
bash install.sh
```

## Usage

You can start chatting with a webpage simply by passing it to the script:

```
python frontend.py https://github.com/chameleon-lizard/tinyrag
```

Additionally, you can pass the query directly, enabling automations:

```
python frontend.py https://github.com/chameleon-lizard/tinyrag --query 'Which library is used as an embedder?'
```

## Evaluations

To do evaluations, please create a `.env` file with the following structure:

```
TOKEN=<OpenAI API token>
JUDGE_API_LINK=<Link to API of the judge>

JUDGE_MODEL=openai/gpt-4o-mini
```

Sample evaluation dataset is located in `data` folder. Evaluation results for `gemma-2-2b`, `llama-3.2-3b` and `qwen-2-7b` in Q4_K_S quant:

```
Model: bartowski/gemma-2-2b-it-GGUF
Quant: Q4_K_S
Judge model: openai/gpt-4o-mini
score
5     1
4    32
3     8
2     5
1    14
0    10
Name: count, dtype: int64

Mean score: 3.0166666666666666
Median score: 4.0
Percentage: 60.33333333333333


Model: bartowski/Llama-3.2-3B-Instruct-GGUF
Quant: Q4_K_S
Judge model: openai/gpt-4o-mini
score
5     0
4    31
3    10
2     4
1    15
0    10
Name: count, dtype: int64

Mean score: 2.95
Median score: 4.0
Percentage: 59.00000000000001

Model: bartowski/Qwen2-7B-Instruct-GGUF
Quant: Q4_K_S
Judge model: openai/gpt-4o-mini
score
5     0
4    29
3    11
2     3
1    16
0    11
Name: count, dtype: int64

Mean score: 2.8983050847457625
Median score: 3.0
Percentage: 57.96610169491525
```

Just for reference, here are the results of [SkoltechChatBot's implementation of RAG](https://github.com/chameleon-lizard/SkoltechChatBot):

```
Model: qwen/qwen-2-7b-instruct
Quant: None
Judge: openai/gpt-4o-mini
score
5    27
4    26
3     7
2     2
1     4
0     4
Name: count, dtype: int64

Mean score: 4.0606060606060606
Median score: 4.0
Percentage: 81.21212121212122


Model: qwen/qwen-2-72b-instruct
Quant: None
Judge: openai/gpt-4o-mini
score
5    34
4    22
3     7
2     1
1     1
0     5
Name: count, dtype: int64

Mean score: 4.338461538461538
Median score: 5.0
Percentage: 86.76923076923076
```

Kinda bad in comparison, but since we're targeting edge, the results are good enough. The default model is `gemma-2-2b`.


## Usage tips

- The embeddings are fast, but not multilingual. Ask questions in the same language as the webpage for best results.
- There is no context in the dialogue, so keep this in mind when asking additional questions.
- Small models are kinda dumb, but they are fast. Thus, if you don't like the answer to your question -- just paraphrase and ask again :)
