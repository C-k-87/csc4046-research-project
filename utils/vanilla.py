from human_eval.human_eval.data import write_jsonl, read_problems
from tqdm import tqdm

from utils.logger import get_logger

MAX_TRIALS=3

log = get_logger()
problems = read_problems()

def vanilla_run(llm, num_samples_per_task=MAX_TRIALS):
    log.info("initiating vanilla run with llm %s (num samples = %s ", llm, num_samples_per_task)
    
    samples = [
        dict(task_id=task_id, completion=llm.generate_one_completion(problems[task_id]["prompt"]))
        for task_id in tqdm(problems)
        for _ in range(num_samples_per_task)
    ]

    write_jsonl("samples.jsonl", samples)

    log.info("vanilla run | finished generation")