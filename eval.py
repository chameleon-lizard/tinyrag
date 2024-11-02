import pathlib
import json
from main import Chatbot
from tqdm import tqdm
import time

import pandas as pd

import os
import dotenv
import threading
from queue import Queue

import src.prompts as prompts
import utils

dotenv.load_dotenv(".env")


def judge(item, q):
    judge_model = f"{os.environ.get('JUDGE_MODEL')}"
    judge_api_link = f"{os.environ.get('JUDGE_API_LINK')}"
    token = f"{os.environ.get('TOKEN')}"

    with sem:
        eval = utils.send_question(
            prompt=prompts.EVALUATION_PROMPT.format(
                instruction=item["question"],
                response=item["generated_answer"],
                reference_answer=item["true_answer"],
            ),
            model=judge_model,
            api_link=judge_api_link,
            token=token,
            temperature=0.1,
            max_tokens=512,
        )

    try:
        feedback, score = [i.strip() for i in eval.split("[RESULT]")]
        print(f"Score: {score}\nFeedback: {feedback}")
        item["feedback"] = feedback
        item["score"] = score

        with q_lock:
            q.put(item)
    except Exception:
        return


eval_files = ["questions_en.json"]

text = pathlib.Path("orientation.md").read_text()
c = Chatbot(text)

for idx, eval_file in enumerate(eval_files):
    data = json.loads(pathlib.Path(eval_file).read_text())

    outputs = []
    for example in tqdm(data):
        question = example["question"]
        if question in [output["question"] for output in outputs]:
            continue

        answer = c.send_question(question)

        result = {
            "question": question,
            "true_answer": example["answer"],
            "source_doc": example["context"],
            "generated_answer": answer,
        }

        outputs.append(result)
    with open(f"eval/eval_ans_{idx}.json", "w") as f:
        json.dump(outputs, f)

    flattened_data = json.loads(pathlib.Path(f"eval/eval_ans_{idx}.json").read_text())

    sem = threading.Semaphore(1)

    q_lock = threading.Lock()

    threads = []
    q = Queue()
    for item in tqdm(flattened_data):
        thread = threading.Thread(target=judge, args=(item, q))
        thread.start()
        threads.append(thread)
        time.sleep(1)

    [_.join() for _ in threads]

    res = []
    while not q.empty():
        res.append(q.get())

    with open(f"eval/eval_res_{idx}.json", "w") as f:
        json.dump(res, f, indent=4)


for idx, eval_file in enumerate(eval_files):
    df = pd.read_json(f"eval/eval_res_{idx}.json")

    print(f"Eval file: {eval_file}\n")
    print(f"Judge model: {os.environ.get('JUDGE_MODEL')}\n")
    print(df.score.value_counts(), end="\n\n")
    print("Mean score: " + str(df.score[df.score != 0].mean()))
    print("Median score: " + str(df.score[df.score != 0].median()))
    print("Percentage: " + str(df.score[df.score != 0].mean() / 5 * 100))
    print("\n\n")
