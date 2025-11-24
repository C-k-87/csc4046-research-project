from human_eval.human_eval.data import write_jsonl, stream_jsonl, read_problems
from human_eval.human_eval.execution import check_correctness
from tqdm import tqdm

from utils.logger import get_logger

MAX_TRIALS=3

log = get_logger()
problems = read_problems()
samples_file = stream_jsonl("samples/samples.jsonl")

def vanilla_run(llm, num_samples_per_task=MAX_TRIALS):
    log.info("initiating vanilla run with llm %s (num samples = %s ", llm, num_samples_per_task)
    
    samples = [
        dict(task_id=task_id, completion=llm.generate_one_completion(problems[task_id]["prompt"]))
        for task_id in tqdm(problems)
        for _ in range(num_samples_per_task)
    ]

    write_jsonl("samples.jsonl", samples)

    log.info("VANILLA RUN | finished generation")

    evaluate_samples(samples)

def evaluate_samples(samples=samples_file):
    log.info("SAMPLE EVALUATION | Initiating...")

    samples_check = []
    passed, failed = 0,0

    for sample in samples:
        task_id = sample["task_id"]
        task_data = problems[task_id]
        completion = sample["completion"]

        check = check_correctness(
            task_data,
            completion,
            timeout=10
        )

        if check["passed"]:
            log.info("SUCCESS! Problem %s solved",task_id)
            samples_check.append({'task_id':task_id, 'completion':completion, 'passed':True})
            passed += 1
        else:
            error = check.get("result", "Tests failed with an unknown error.")
            log.warning("FAILED! Problem %s failed with error %s...",task_id, error[:200])
            samples_check.append({'task_id':task_id, 'last_completion':completion, 'passed':False})
            failed +=1
    
    log.info("EVALUATION | Finished sample evaluation\n")
    log.info("Passed: %s \tFailed:%s\n",passed,failed)
    write_jsonl("samples_results.jsonl", samples_check)