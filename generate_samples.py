from human_eval.human_eval.data import write_jsonl, read_problems
from llama_cpp import Llama
from tqdm import tqdm

problems = read_problems()

# LLM SPECIFICATIONS -------------------------------------------------------------------------------------

llm_model = "gguf/Phi-3-mini-4k-instruct-q4.gguf"
n_ctx=4096
n_gpu_layers=999
max_tokens=200
stop=None
temperature=0.8

client = Llama(model_path=llm_model, n_ctx=n_ctx, n_gpu_layers=n_gpu_layers, n_threads=4, verbose=False)

# --------------------------------------------------------------------------------------------------------

def generate_one_completion(user_prompt):
    completion= client(user_prompt,max_tokens=max_tokens, temperature=temperature, stop=stop)
    return completion["choices"][0]["text"]

num_samples_per_task = 3
samples = [
    dict(task_id=task_id, completion=generate_one_completion(problems[task_id]["prompt"]))
    for task_id in tqdm(problems)
    for _ in range(num_samples_per_task)
]


write_jsonl("samples.jsonl", samples)

print("Finished")